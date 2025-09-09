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
from ..types import HexenType, ConcreteArrayType
from .array_types import ArrayTypeInfo, ArrayDimension
from .multidim_analyzer import MultidimensionalArrayAnalyzer
from .error_messages import ArrayErrorFactory, ArrayErrorMessages


class ArrayLiteralAnalyzer:
    """Analyzes array literal expressions integrated with expression framework"""
    
    def __init__(self, error_callback: Callable[[str, Optional[Dict]], None], comptime_analyzer, analyze_expression_callback: Optional[Callable[[Dict, Optional[Union[HexenType, ConcreteArrayType]]], HexenType]] = None):
        """
        Initialize with callback pattern for integration.
        
        Args:
            error_callback: Error reporting callback to main analyzer
            comptime_analyzer: Existing ComptimeAnalyzer instance
            analyze_expression_callback: Callback to analyze individual expressions
        """
        self._error = error_callback
        self.comptime_analyzer = comptime_analyzer
        self._analyze_expression = analyze_expression_callback
        
        # Initialize multidimensional analyzer
        self.multidim_analyzer = MultidimensionalArrayAnalyzer(error_callback, comptime_analyzer)
    
    def analyze_array_literal(self, node: Dict[str, Any], target_type: Optional[Union[HexenType, ConcreteArrayType]] = None) -> HexenType:
        """
        Analyze array literal and return inferred HexenType.
        
        Args:
            node: Array literal AST node
            target_type: Optional target type for context-guided resolution (HexenType or ConcreteArrayType)
            
        Returns:
            HexenType enum representing the array literal's type
        """
        elements = node.get("elements", [])
        
        # Handle empty arrays - require explicit context
        if not elements:
            if target_type is None:
                self._error(ArrayErrorMessages.empty_array_context_required(), node)
                return HexenType.UNKNOWN
            
            # For ConcreteArrayType, return the concrete type (no longer comptime)
            if isinstance(target_type, ConcreteArrayType):
                # For empty arrays with concrete context, we create a concrete array
                # This prevents empty arrays from staying comptime
                return HexenType.UNKNOWN  # Will be handled by proper concrete type system later
            
            return target_type
        
        # Check if this is a multidimensional array (first element is array literal)
        first_element = elements[0]
        if first_element.get("type") == "array_literal":
            # Delegate to multidimensional analyzer
            return self.multidim_analyzer.analyze_multidimensional_literal(node, target_type)
        
        # Handle ConcreteArrayType context
        if isinstance(target_type, ConcreteArrayType):
            return self._analyze_with_concrete_context(node, target_type)
        
        # If we have an expression analyzer callback, use it to analyze each element
        if self._analyze_expression is not None:
            element_types = []
            for element in elements:
                element_type = self._analyze_expression(element, None)
                element_types.append(element_type)
            
            # Use comptime analyzer to unify element types
            unified_type = self._unify_element_types(element_types, node)
            return unified_type
        
        # Fallback to legacy analysis for backwards compatibility
        element_type_str = first_element.get("type")
        
        if element_type_str == "comptime_int":
            # Check if all elements are integers
            if self._all_elements_are_integers(elements):
                return HexenType.COMPTIME_ARRAY_INT
            else:
                # Mixed integer/float -> promote to float array
                return HexenType.COMPTIME_ARRAY_FLOAT
        elif element_type_str == "comptime_float":
            return HexenType.COMPTIME_ARRAY_FLOAT
        elif element_type_str == "literal":
            # Check if it's a string literal
            first_value = first_element.get("value")
            if isinstance(first_value, str):
                self._error("String arrays not yet supported in current implementation", node)
                return HexenType.UNKNOWN
        
        # For other types or mixed types, require explicit context
        if target_type is None:
            if len(set(elem.get("type") for elem in elements)) > 1:
                self._error(ArrayErrorMessages.comptime_context_required_for_mixed_types(), node)
            else:
                self._error("Array literal type inference not yet implemented for this element type", node)
            return HexenType.UNKNOWN
        
        return target_type
    
    def _unify_element_types(self, element_types: List[HexenType], node: Dict[str, Any]) -> HexenType:
        """
        Unify element types to determine the array's overall type.
        
        Args:
            element_types: List of HexenType for each element
            node: Array literal AST node for error reporting
            
        Returns:
            HexenType representing the unified array type
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
                return HexenType.COMPTIME_ARRAY_INT
            elif element_type == HexenType.COMPTIME_FLOAT:
                return HexenType.COMPTIME_ARRAY_FLOAT
            else:
                # Non-comptime types require explicit context
                self._error("Array with concrete element types requires explicit array type context", node)
                return HexenType.UNKNOWN
        
        # Mixed types - check for comptime int/float promotion
        if unique_types <= {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            # Mixed comptime int/float -> promote to comptime array float
            return HexenType.COMPTIME_ARRAY_FLOAT
        
        # Other mixed types require explicit context
        self._error("Mixed concrete/comptime element types require explicit array context", node)
        return HexenType.UNKNOWN
    
    def _analyze_with_concrete_context(self, node: Dict[str, Any], target_type: ConcreteArrayType) -> HexenType:
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
        
        if expected_count != actual_count:
            self._error(
                f"Array size mismatch: expected {expected_count} elements, got {actual_count}",
                node
            )
            return HexenType.UNKNOWN
        
        # For multidimensional arrays, validate structure recursively
        if len(target_type.dimensions) > 1:
            return self._analyze_multidim_concrete_context(node, target_type)
        
        # Single dimension array - validate each element against target element type
        if self._analyze_expression is not None:
            for i, element in enumerate(elements):
                element_type = self._analyze_expression(element, target_type.element_type)
                
                # Check if element can coerce to target element type
                if element_type == HexenType.UNKNOWN:
                    # Error already reported by expression analyzer
                    continue
                
                if not self._can_coerce_to_concrete_element(element_type, target_type.element_type):
                    # Handle both HexenType and ConcreteArrayType for error messages
                    from_type_str = element_type.value if hasattr(element_type, 'value') else str(element_type)
                    to_type_str = target_type.element_type.value if hasattr(target_type.element_type, 'value') else str(target_type.element_type)
                    
                    self._error(
                        f"Element {i} type mismatch: cannot coerce {from_type_str} to {to_type_str}",
                        element
                    )
        
        # Return a type that represents successful concrete array validation
        # Since the array literal validated successfully against the concrete type context,
        # we can return a comptime array type that represents the successful validation
        # This allows the function call system to proceed with successful type matching
        if target_type.element_type in {HexenType.I32, HexenType.I64}:
            return HexenType.COMPTIME_ARRAY_INT
        elif target_type.element_type in {HexenType.F32, HexenType.F64}:
            return HexenType.COMPTIME_ARRAY_FLOAT
        else:
            # For other element types, return a compatible comptime array
            return HexenType.COMPTIME_ARRAY_INT  # Default fallback
    
    def _analyze_multidim_concrete_context(self, node: Dict[str, Any], target_type: ConcreteArrayType) -> HexenType:
        """
        Analyze multidimensional array literal with concrete context.
        
        For arrays like: val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
        """
        elements = node.get("elements", [])
        
        # Each element should be an array literal matching the inner dimensions
        inner_target_type = ConcreteArrayType(
            target_type.element_type,
            target_type.dimensions[1:]  # Remove first dimension
        )
        
        for i, element in enumerate(elements):
            if element.get("type") != "array_literal":
                self._error(
                    f"Element {i} is not an array in multidimensional array literal",
                    element
                )
                continue
            
            # Recursively validate inner array
            self._analyze_with_concrete_context(element, inner_target_type)
        
        # Return appropriate comptime array type for successful multidimensional validation
        if target_type.element_type in {HexenType.I32, HexenType.I64}:
            return HexenType.COMPTIME_ARRAY_INT
        elif target_type.element_type in {HexenType.F32, HexenType.F64}:
            return HexenType.COMPTIME_ARRAY_FLOAT
        else:
            return HexenType.COMPTIME_ARRAY_INT  # Default fallback
    
    def _can_coerce_to_concrete_element(self, from_type: HexenType, to_type: HexenType) -> bool:
        """
        Check if from_type can coerce to to_type for concrete array elements.
        
        Rules:
        1. Same type: always OK
        2. Comptime types can coerce to compatible concrete types
        3. Concrete types require explicit conversion (not handled here)
        """
        if from_type == to_type:
            return True
        
        # Comptime int can coerce to any integer type
        if from_type == HexenType.COMPTIME_INT and to_type in {HexenType.I32, HexenType.I64}:
            return True
        
        # Comptime float can coerce to any numeric type  
        if from_type == HexenType.COMPTIME_FLOAT and to_type in {HexenType.I32, HexenType.I64, HexenType.F32, HexenType.F64}:
            return True
        
        # All other combinations require explicit conversion
        return False
    
    def analyze_array_access(self, node: Dict[str, Any], target_type: Optional[HexenType] = None) -> HexenType:
        """
        Analyze array access expression and return element type.
        
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
        
        # For now, implement basic array access validation
        # In a full implementation, this would:
        # 1. Analyze the array expression to get its type
        # 2. Validate the index is an integer type
        # 3. Perform bounds checking if possible
        # 4. Return the element type
        
        # Check index type - must be integer
        index_type_str = index_expr.get("type")
        if index_type_str not in ["comptime_int", "i32", "i64"]:
            self._error(ArrayErrorMessages.invalid_index_type(index_type_str), node)
            return HexenType.UNKNOWN
        
        # For now, assume array access of comptime arrays returns comptime element type
        # This is a simplified implementation that will be enhanced
        array_type_str = array_expr.get("type")
        if array_type_str == "identifier":
            # This would normally involve symbol table lookup to get the array's type
            # For now, return COMPTIME_INT as a placeholder
            return HexenType.COMPTIME_INT
        
        self._error("Array access type inference not yet fully implemented", node)
        return HexenType.UNKNOWN
    
    def _all_elements_are_integers(self, elements: List[Dict]) -> bool:
        """Check if all elements are integer literals"""
        for element in elements:
            if element.get("type") != "comptime_int":
                return False
        return True