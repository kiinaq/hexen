"""
Array Literal Semantic Analysis - Integrated Version

Implements array literal analysis that integrates seamlessly with the existing
expression analysis framework. Returns HexenType enums and follows established
patterns for type inference and error reporting.

Key Integration Points:
- Returns HexenType enums (not Dict structures)
- Uses ComptimeAnalyzer for element type unification
- Integrates with expression analyzer callback pattern
- Follows established error reporting patterns
"""

from typing import Dict, List, Any, Optional, Callable, Union

from .error_messages import ArrayErrorMessages
from .multidim_analyzer import MultidimensionalArrayAnalyzer
from ..type_util import is_array_type, get_type_name_for_error, is_range_type
from ..types import HexenType, ArrayType, ComptimeArrayType, RangeType, ComptimeRangeType


class ArrayLiteralAnalyzer:
    """Analyzes array literal expressions integrated with expression framework"""

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        comptime_analyzer,
        analyze_expression_callback: Optional[
            Callable[[Dict, Optional[Union[HexenType, ArrayType]]], HexenType]
        ] = None,
        range_analyzer=None,
    ):
        """
        Initialize with callback pattern for integration.

        Args:
            error_callback: Error reporting callback to main analyzer
            comptime_analyzer: Existing ComptimeAnalyzer instance
            analyze_expression_callback: Callback to analyze individual expressions
            range_analyzer: Range analyzer for validating range-based indexing
        """
        self._error = error_callback
        self.comptime_analyzer = comptime_analyzer
        self._analyze_expression = analyze_expression_callback
        self.range_analyzer = range_analyzer

        # Initialize multidimensional analyzer
        self.multidim_analyzer = MultidimensionalArrayAnalyzer(
            error_callback, comptime_analyzer
        )

    def analyze_array_literal(
        self,
        node: Dict[str, Any],
        target_type: Optional[Union[HexenType, ArrayType, ComptimeArrayType]] = None,
    ) -> Union[HexenType, ComptimeArrayType]:
        """
        Analyze array literal and return type WITH FULL DIMENSIONAL INFORMATION.

        Returns ComptimeArrayType with full dimensional information instead of legacy enum values
        to preserve size information throughout semantic analysis.

        Args:
            node: Array literal AST node
            target_type: Optional target type for context-guided resolution

        Returns:
            ComptimeArrayType with preserved dimensions, or ConcreteArrayType if
            explicit context provided, or HexenType.UNKNOWN on error
        """
        elements = node.get("elements", [])

        # Handle empty arrays - require explicit context
        if not elements:
            if target_type is None:
                self._error(ArrayErrorMessages.empty_array_type_annotation_required(), node)
                return HexenType.UNKNOWN

            # For ConcreteArrayType, return the concrete type (no longer comptime)
            if isinstance(target_type, ArrayType):
                # For empty arrays with concrete context, we create a concrete array
                # This prevents empty arrays from staying comptime
                return (
                    HexenType.UNKNOWN
                )  # Will be handled by proper concrete type system later

            return target_type

        # Check if this is a multidimensional array (first element is array literal)
        first_element = elements[0]
        if first_element.get("type") == "array_literal":
            # Delegate to multidimensional analyzer
            return self.multidim_analyzer.analyze_multidimensional_literal(
                node, target_type
            )

        # Handle ConcreteArrayType context
        if isinstance(target_type, ArrayType):
            return self._analyze_with_concrete_context(node, target_type)

        # If we have an expression analyzer callback, use it to analyze each element
        if self._analyze_expression is not None:
            element_types = []
            for element in elements:
                element_type = self._analyze_expression(element, None)
                element_types.append(element_type)

            # Use comptime analyzer to unify element types
            # CHANGE: Now returns ComptimeArrayType with size information
            unified_type = self._unify_element_types(element_types, node, len(elements))
            return unified_type

        # If we reach here, _analyze_expression callback was not set (should never happen)
        self._error(
            "Internal error: Array literal analyzer not properly initialized", node
        )
        return HexenType.UNKNOWN

    def _unify_element_types(
        self, element_types: List[HexenType], node: Dict[str, Any], array_size: int
    ) -> Union[ComptimeArrayType, HexenType]:
        """
        Unify element types to determine the array's overall type.

        CHANGE (Phase 2): Now returns ComptimeArrayType with size information.

        Args:
            element_types: List of HexenType for each element
            node: Array literal AST node for error reporting
            array_size: Number of elements in the array (size of first dimension)

        Returns:
            ComptimeArrayType with preserved dimensions, or HexenType.UNKNOWN on error
        """
        if not element_types:
            return HexenType.UNKNOWN

        # Filter out UNKNOWN types (errors in individual elements)
        valid_types = [t for t in element_types if t != HexenType.UNKNOWN]
        if not valid_types:
            return HexenType.UNKNOWN

        # If all elements are the same type, use that type as base
        unique_types = set(valid_types)
        if len(unique_types) == 1:
            element_type = list(unique_types)[0]
            if element_type == HexenType.COMPTIME_INT:
                # CHANGE: Return ComptimeArrayType with size information
                return ComptimeArrayType(
                    element_comptime_type=HexenType.COMPTIME_INT,
                    dimensions=[array_size]
                )
            elif element_type == HexenType.COMPTIME_FLOAT:
                # CHANGE: Return ComptimeArrayType with size information
                return ComptimeArrayType(
                    element_comptime_type=HexenType.COMPTIME_FLOAT,
                    dimensions=[array_size]
                )
            else:
                # Non-comptime types require explicit context
                self._error(
                    "Array with concrete element types requires explicit array type context",
                    node,
                )
                return HexenType.UNKNOWN

        # Mixed types - check for comptime int/float promotion
        if unique_types <= {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            # Mixed comptime int/float -> promote to comptime array float
            # CHANGE: Return ComptimeArrayType with size information
            return ComptimeArrayType(
                element_comptime_type=HexenType.COMPTIME_FLOAT,
                dimensions=[array_size]
            )

        # Other mixed types require explicit context
        self._error(
            ArrayErrorMessages.explicit_type_annotation_required_for_mixed_types(), node
        )
        return HexenType.UNKNOWN

    def _analyze_with_concrete_context(
        self, node: Dict[str, Any], target_type: ArrayType
    ) -> ArrayType:
        """
        Analyze array literal with explicit concrete array type context.

        Implementation for explicit array type contexts like:
        val arr : [3]i32 = [1, 2, 3]

        Args:
            node: Array literal AST node
            target_type: ConcreteArrayType specifying expected dimensions and element type

        Returns:
            HexenType representing the resolved type (usually the concrete type)
        """
        elements = node.get("elements", [])

        # Validate element count matches first dimension
        expected_count = target_type.dimensions[0]
        actual_count = len(elements)

        # Inferred dimensions ([_]) accept any size - skip size validation
        if expected_count != "_" and expected_count != actual_count:
            self._error(
                f"Array size mismatch: expected {expected_count} elements, got {actual_count}",
                node,
            )
            return HexenType.UNKNOWN

        # For multidimensional arrays, validate structure recursively
        if len(target_type.dimensions) > 1:
            return self._analyze_multidim_concrete_context(node, target_type)

        # Single dimension array - validate each element against target element type
        if self._analyze_expression is not None:
            for i, element in enumerate(elements):
                element_type = self._analyze_expression(
                    element, target_type.element_type
                )

                # Check if element can coerce to target element type
                if element_type == HexenType.UNKNOWN:
                    # Error already reported by expression analyzer
                    continue

                if not self._can_coerce_to_concrete_element(
                    element_type, target_type.element_type
                ):
                    # Handle both HexenType and ConcreteArrayType for error messages
                    from_type_str = (
                        element_type.value
                        if hasattr(element_type, "value")
                        else str(element_type)
                    )
                    to_type_str = (
                        target_type.element_type.value
                        if hasattr(target_type.element_type, "value")
                        else str(target_type.element_type)
                    )

                    self._error(
                        f"Element {i} type mismatch: cannot coerce {from_type_str} to {to_type_str}",
                        element,
                    )

        # Return the concrete type after successful validation
        # The array literal, once validated against concrete context, IS that concrete type
        return target_type

    def _analyze_multidim_concrete_context(
        self, node: Dict[str, Any], target_type: ArrayType
    ) -> ArrayType:
        """
        Analyze multidimensional array literal with concrete context.

        For arrays like: val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
        """
        elements = node.get("elements", [])

        # Each element should be an array literal matching the inner dimensions
        inner_target_type = ArrayType(
            target_type.element_type,
            target_type.dimensions[1:],  # Remove first dimension
        )

        for i, element in enumerate(elements):
            if element.get("type") != "array_literal":
                self._error(
                    f"Element {i} is not an array in multidimensional array literal",
                    element,
                )
                continue

            # Recursively validate inner array
            self._analyze_with_concrete_context(element, inner_target_type)

        # Return the concrete type after successful validation
        return target_type

    def _can_coerce_to_concrete_element(
        self, from_type: HexenType, to_type: HexenType
    ) -> bool:
        """
        Check if from_type can coerce to to_type for concrete array elements.

        Rules:
        1. Same type: always OK
        2. Comptime types can coerce to compatible concrete types
        3. Concrete types require explicit conversion (not handled here)
        """
        if from_type == to_type:
            return True

        # Comptime int can coerce to any numeric type (follows comptime_int rules)
        if from_type == HexenType.COMPTIME_INT and to_type in {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
        }:
            return True

        # Comptime float can coerce to float types only (truncation to int requires explicit conversion)
        if from_type == HexenType.COMPTIME_FLOAT and to_type in {
            HexenType.F32,
            HexenType.F64,
        }:
            return True

        # All other combinations require explicit conversion
        return False

    def analyze_array_access(
        self, node: Dict[str, Any], target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze array access expression and return element type.
        Handles both single and multidimensional array access.

        Args:
            node: Array access AST node with 'array' and 'index' fields
            target_type: Optional target type for context-guided resolution

        Returns:
            HexenType enum representing the accessed element's type
        """
        array_expr = node.get("array")
        index_expr = node.get("index")

        if not array_expr or not index_expr:
            self._error("Invalid array access: missing array or index expression", node)
            return HexenType.UNKNOWN

        # 1. Analyze the array expression to get its type
        array_type = self._analyze_array_expression(array_expr)
        if array_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # 1.1. Validate that the expression is actually an array type
        # Special case: Allow array access expressions (they might be multidimensional)
        if not is_array_type(array_type) and array_expr.get("type") != "array_access":
            type_name = get_type_name_for_error(array_type)
            self._error(ArrayErrorMessages.non_array_indexing(type_name), node)
            return HexenType.UNKNOWN

        # 2. Analyze the index expression
        index_type = self._get_index_semantic_type(index_expr)

        # 2.1. Check if index is a range (for array slicing)
        if is_range_type(index_type):
            # Range-based slicing - validate and return array type
            # Validate that the range type is valid for indexing (usize or comptime_int)
            if self.range_analyzer:
                is_valid = self.range_analyzer.validate_range_indexing(
                    array_type, index_type, index_expr
                )
                if not is_valid:
                    return HexenType.UNKNOWN
            # Range slicing returns same array type (element type preserved)
            return array_type

        # 2.2. Otherwise, index must be an integer type
        if index_type not in {HexenType.COMPTIME_INT, HexenType.I32, HexenType.I64}:
            index_type_name = get_type_name_for_error(index_type)
            self._error(ArrayErrorMessages.invalid_index_type(index_type_name), node)
            return HexenType.UNKNOWN

        # 3. Determine element type based on array type (single element access)
        return self._get_element_type_from_array_access(array_type, target_type)

    def _analyze_array_expression(self, array_expr: Dict) -> HexenType:
        """
        Analyze the array part of an array access to determine its type.
        Handles identifiers, nested array access, array literals, array copy, and property access.
        """
        expr_type = array_expr.get("type")

        if expr_type == "identifier":
            # Symbol table lookup - delegate to expression analyzer callback
            if self._analyze_expression:
                return self._analyze_expression(array_expr)
            else:
                # Should never happen - callback should always be set
                return HexenType.UNKNOWN

        elif expr_type == "array_access":
            # Nested array access (e.g., matrix[0] in matrix[0][1])
            return self.analyze_array_access(array_expr)

        elif expr_type == "array_literal":
            # Direct array literal access (e.g., [1,2,3][0])
            return self.analyze_array_literal(array_expr)

        elif expr_type == "array_copy":
            # Array copy operation (e.g., arr[..])
            return self.analyze_array_copy(array_expr)

        elif expr_type == "property_access":
            # Property access (e.g., arr.length)
            return self.analyze_property_access(array_expr)

        elif expr_type == "function_call":
            # Function call that returns an array
            if self._analyze_expression:
                return self._analyze_expression(array_expr)
            else:
                return HexenType.UNKNOWN

        else:
            self._error(f"Invalid array expression type: {expr_type}", array_expr)
            return HexenType.UNKNOWN

    def _get_element_type_from_array_access(
        self, array_type: HexenType, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Determine the element type when accessing an array.
        Handles dimension reduction for multidimensional arrays.
        """
        # Handle ComptimeArrayType instances
        if isinstance(array_type, ComptimeArrayType):
            # For comptime arrays, reduce dimensionality
            if len(array_type.dimensions) == 1:
                # 1D comptime array access returns comptime element type
                return array_type.element_comptime_type
            else:
                # Multidimensional comptime array access reduces by one dimension
                new_dimensions = array_type.dimensions[1:]
                return ComptimeArrayType(array_type.element_comptime_type, new_dimensions)

        # Handle concrete array types (ConcreteArrayType instances)
        elif hasattr(array_type, "element_type") and hasattr(array_type, "dimensions"):
            # This is a ConcreteArrayType - access reduces dimensionality
            if len(array_type.dimensions) == 1:
                # 1D array access returns element type
                return array_type.element_type
            else:
                # Multidimensional array access reduces by one dimension
                # ConcreteArrayType already imported at top of file
                new_dimensions = array_type.dimensions[1:]  # Remove first dimension
                return ArrayType(array_type.element_type, new_dimensions)

        # Handle basic HexenType array access
        elif array_type in [
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.STRING,
            HexenType.BOOL,
        ]:
            # Direct element type access
            return array_type

        else:
            # Fallback for unknown types
            if target_type:
                return target_type
            return HexenType.COMPTIME_INT

    def _all_elements_are_integers(self, elements: List[Dict]) -> bool:
        """Check if all elements are integer literals"""
        for element in elements:
            if element.get("type") != "comptime_int":
                return False
        return True

    def _get_index_semantic_type(self, index_expr: Dict) -> HexenType:
        """Get the semantic type of an index expression."""
        expr_type = index_expr.get("type")

        # Handle literals directly
        if expr_type == "comptime_int":
            return HexenType.COMPTIME_INT
        elif expr_type == "comptime_float":
            return HexenType.COMPTIME_FLOAT

        # For identifiers and other expressions, delegate to expression analyzer
        if self._analyze_expression:
            return self._analyze_expression(index_expr)

        # Fallback - assume it's valid if we can't analyze it
        return HexenType.COMPTIME_INT

    def analyze_array_copy(
        self, node: Dict[str, Any], target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze array copy operation ([..]) and return the array type.

        Array copy creates a new array with the same type as the source.
        This is a semantic copy that will be optimized in codegen.

        Args:
            node: Array copy AST node with 'array' field
            target_type: Optional target type for context-guided resolution

        Returns:
            HexenType representing the copied array type
        """
        array_expr = node.get("array")

        if not array_expr:
            self._error("Invalid array copy: missing array expression", node)
            return HexenType.UNKNOWN

        # Analyze the array expression to get its type
        array_type = self._analyze_array_expression(array_expr)
        if array_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Validate that the expression is actually an array type
        if not is_array_type(array_type):
            type_name = get_type_name_for_error(array_type)
            self._error(ArrayErrorMessages.non_array_copy_operation(type_name), node)
            return HexenType.UNKNOWN

        # Copy preserves the exact type
        return array_type

    def analyze_property_access(
        self, node: Dict[str, Any], target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze property access (.property) and return the property type.

        Currently supports:
        - .length on array types (returns compile-time constant i32)

        Args:
            node: Property access AST node with 'object' and 'property' fields
            target_type: Optional target type for context-guided resolution

        Returns:
            HexenType representing the property's type
        """
        object_expr = node.get("object")
        property_name = node.get("property")

        if not object_expr or not property_name:
            self._error("Invalid property access: missing object or property name", node)
            return HexenType.UNKNOWN

        # Analyze the object expression to get its type
        object_type = self._analyze_array_expression(object_expr)
        if object_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Handle .length property
        if property_name == "length":
            # Validate that object is an array type
            if not is_array_type(object_type):
                type_name = get_type_name_for_error(object_type)
                self._error(
                    ArrayErrorMessages.length_property_only_on_arrays(type_name),
                    node
                )
                return HexenType.UNKNOWN

            # .length returns a compile-time constant integer
            # This will be i32 in the final implementation
            return HexenType.COMPTIME_INT
        else:
            # Unknown property
            type_name = get_type_name_for_error(object_type)
            self._error(
                ArrayErrorMessages.property_not_found(type_name, property_name),
                node
            )
            return HexenType.UNKNOWN
