"""
Multidimensional Array Semantic Analysis

Implements semantic analysis for multidimensional arrays and flattening operations.
Supports N-dimensional arrays with row-major layout and safe flattening (no reshaping).

Key Features:
- Multidimensional array literal validation
- Array structure consistency checking
- Safe array flattening with element count validation
- Integration with existing comptime type system
"""

from typing import Dict, List, Any, Optional, Callable, Union

from .array_types import ArrayTypeInfo
from .error_messages import ArrayErrorMessages
from ..types import HexenType, ComptimeArrayType


class MultidimensionalArrayAnalyzer:
    """Semantic analysis for multidimensional arrays"""

    def __init__(
        self, error_callback: Callable[[str, Optional[Dict]], None], comptime_analyzer
    ):
        """
        Initialize with callback pattern for integration.

        Args:
            error_callback: Error reporting callback to main analyzer
            comptime_analyzer: Existing ComptimeAnalyzer instance
        """
        self._error = error_callback
        self.comptime_analyzer = comptime_analyzer

    def analyze_multidimensional_literal(
        self, node: Dict[str, Any], target_type: Optional[Union[HexenType, ComptimeArrayType]] = None
    ) -> Union[HexenType, ComptimeArrayType]:
        """
        Analyze multidimensional array literal for structure consistency.

        Returns ComptimeArrayType with full dimensional information to preserve size metadata.

        Args:
            node: Array literal AST node with nested structure
            target_type: Optional target type for context-guided resolution

        Returns:
            ComptimeArrayType with preserved dimensions, or HexenType.UNKNOWN on error
        """
        elements = node.get("elements", [])

        if not elements:
            if target_type is None:
                self._error(ArrayErrorMessages.empty_array_type_annotation_required(), node)
                return HexenType.UNKNOWN
            return target_type

        # Check if this is actually multidimensional (first element is array)
        first_element = elements[0]
        if not self._is_array_literal(first_element):
            # This is actually a 1D array, delegate back to regular analysis
            # CHANGE: Return ComptimeArrayType with 1D dimensions
            return ComptimeArrayType(
                element_comptime_type=HexenType.COMPTIME_INT,
                dimensions=[len(elements)]
            )

        # Validate multidimensional structure consistency
        try:
            self._validate_multidim_structure(elements)
        except ValueError as e:
            self._error(
                f"Multidimensional array structure validation error: {str(e)}", node
            )
            return HexenType.UNKNOWN

        # CHANGE: Calculate dimensions and return ComptimeArrayType
        dimensions = self._calculate_dimensions(elements)
        element_type = self._determine_element_type(elements)

        return ComptimeArrayType(
            element_comptime_type=element_type,
            dimensions=dimensions
        )

    def analyze_array_flattening(
        self, array_node: Dict[str, Any], target_type_str: str
    ) -> Dict[str, Any]:
        """
        Analyze array flattening operation: multidim_array → 1D array

        Implements safe array flattening from ARRAY_TYPE_SYSTEM.md:
        - Row-major memory layout enables zero-cost flattening
        - Compile-time element count validation
        - Comptime type preservation when possible

        Args:
            array_node: Source multidimensional array AST node
            target_type_str: Target 1D array type string (e.g., "[6]i32")

        Returns:
            Analysis result dictionary with flattening validation
        """
        # For now, this is a simplified implementation
        # Full implementation would:
        # 1. Extract source array type information
        # 2. Parse target type string
        # 3. Validate element count compatibility
        # 4. Check element type compatibility

        # Simplified validation
        if not array_node:
            self._error("Invalid array flattening: missing source array", None)
            return {"type": "array_flattening", "valid": False}

        return {
            "type": "array_flattening",
            "source": array_node,
            "target_type": target_type_str,
            "valid": True,
            "zero_cost": True,  # Row-major layout enables zero-cost flattening
            "element_count_validated": False,  # Would be True in full implementation
        }

    def _validate_multidim_structure(self, elements: List[Dict[str, Any]]) -> None:
        """
        Validate multidimensional array literal for consistent structure.

        Ensures:
        1. All rows have same number of columns
        2. Proper nesting structure
        3. Element types are compatible

        Raises:
            ValueError: If structure is inconsistent
        """
        if not elements:
            raise ValueError("Empty multidimensional array literal")

        # Check first element to establish pattern
        first_element = elements[0]
        if not self._is_array_literal(first_element):
            raise ValueError("Multidimensional array must contain sub-arrays")

        first_row_elements = first_element.get("elements", [])
        first_row_length = len(first_row_elements)

        # Validate all rows have same length
        for i, element in enumerate(elements):
            if not self._is_array_literal(element):
                raise ValueError(
                    f"Row {i} is not an array in multidimensional array literal"
                )

            row_elements = element.get("elements", [])
            row_length = len(row_elements)

            if row_length != first_row_length:
                raise ValueError(
                    f"Inconsistent inner array dimensions: expected {first_row_length} elements, "
                    f"got {row_length} at row {i}"
                )

        # Recursively validate nested structures (for 3D, 4D, etc.)
        self._validate_nested_structure_consistency(elements)

        # Structure is consistent

    def _validate_nested_structure_consistency(
        self, elements: List[Dict[str, Any]]
    ) -> None:
        """
        Recursively validate deep nested structure consistency for 3D, 4D, etc. arrays.

        This method validates that if the array has multiple dimensions,
        all sub-arrays at each level have consistent internal structure.
        """
        if not elements:
            return

        # Check if the first element is itself a multidimensional array
        first_element = elements[0]
        if not self._is_array_literal(first_element):
            return  # Not multidimensional, no nested validation needed

        first_sub_elements = first_element.get("elements", [])
        if not first_sub_elements or not self._is_array_literal(first_sub_elements[0]):
            return  # Not 3D or deeper, no nested validation needed

        # This is a 3D+ array, validate each 2D slice independently
        for i, element in enumerate(elements):
            try:
                # Recursively validate each 2D slice
                self._validate_multidim_structure(element.get("elements", []))
            except ValueError as e:
                # Convert ValueError to proper error reporting
                raise ValueError(
                    f"Inconsistent inner array dimensions in dimension {i}: {str(e)}"
                )

    def _is_array_literal(self, node: Dict[str, Any]) -> bool:
        """Check if a node represents an array literal"""
        return node.get("type") == "array_literal"

    def _calculate_dimensions(self, elements: List[Dict[str, Any]]) -> List[int]:
        """
        Calculate dimensions for multidimensional array literal.

        For [[1, 2], [3, 4], [5, 6]] returns [3, 2] (3 rows, 2 columns)

        Args:
            elements: Top-level elements of the array literal

        Returns:
            List of dimension sizes [outer_dim, inner_dim, ...]
        """
        if not elements:
            return []

        # Outer dimension is number of elements
        outer_dim = len(elements)

        # Check if first element is array to determine inner dimensions
        first_element = elements[0]
        if not self._is_array_literal(first_element):
            # 1D array (shouldn't reach here, but handle safely)
            return [outer_dim]

        # Get inner dimensions recursively
        inner_elements = first_element.get("elements", [])
        if not inner_elements:
            return [outer_dim, 0]

        # Check if this is 2D or deeper
        first_inner = inner_elements[0]
        if not self._is_array_literal(first_inner):
            # 2D array: [outer][inner]
            return [outer_dim, len(inner_elements)]
        else:
            # 3D+ array: recurse
            inner_dims = self._calculate_dimensions(inner_elements)
            return [outer_dim] + inner_dims

    def _determine_element_type(self, elements: List[Dict[str, Any]]) -> HexenType:
        """
        Determine the comptime element type for multidimensional array.

        Recursively finds the leaf element type.

        Args:
            elements: Array elements (may be nested)

        Returns:
            HexenType.COMPTIME_INT or HexenType.COMPTIME_FLOAT
        """
        if not elements:
            return HexenType.COMPTIME_INT  # Default for empty

        first_element = elements[0]

        # If first element is array, recurse deeper
        if self._is_array_literal(first_element):
            inner_elements = first_element.get("elements", [])
            return self._determine_element_type(inner_elements)

        # Reached leaf level - check element type
        element_type = first_element.get("type")

        if element_type == "comptime_int":
            # Check all elements - if any float, promote to float
            for elem in elements:
                if elem.get("type") == "comptime_float":
                    return HexenType.COMPTIME_FLOAT
            return HexenType.COMPTIME_INT
        elif element_type == "comptime_float":
            return HexenType.COMPTIME_FLOAT
        else:
            # Default to int for other types
            return HexenType.COMPTIME_INT

    def _calculate_total_elements(self, elements: List[Dict[str, Any]]) -> int:
        """Calculate total number of leaf elements in multidimensional array"""
        if not elements:
            return 0

        # For 2D arrays: rows * columns
        num_rows = len(elements)
        if num_rows == 0:
            return 0

        first_row = elements[0]
        if not self._is_array_literal(first_row):
            # This is actually 1D
            return num_rows

        num_cols = len(first_row.get("elements", []))
        return num_rows * num_cols

    def validate_array_access_chain(
        self, access_chain: List[Dict[str, Any]], base_array_info: ArrayTypeInfo
    ) -> Dict[str, Any]:
        """
        Validate chained array access for multidimensional arrays.

        Args:
            access_chain: List of access operations [arr[0][1][2]]
            base_array_info: Type information for the base array

        Returns:
            Validation result with remaining dimensions and element type
        """
        # Simplified implementation for Task 7
        # Full implementation would validate each access level against array dimensions

        remaining_dimensions = len(base_array_info.dimensions) - len(access_chain)

        if remaining_dimensions < 0:
            return {
                "valid": False,
                "error": f"Too many indices: array has {len(base_array_info.dimensions)} dimensions, "
                f"got {len(access_chain)} indices",
            }

        if remaining_dimensions == 0:
            # Full access - returns element type
            result_type = base_array_info.element_type
        else:
            # Partial access - returns sub-array type (simplified)
            result_type = (
                f"{remaining_dimensions}D_array_of_{base_array_info.element_type}"
            )

        return {
            "valid": True,
            "remaining_dimensions": remaining_dimensions,
            "result_type": result_type,
            "bounds_validated": False,  # Would be True with constant index checking
        }


class ArrayFlattening:
    """Utility class for array flattening operations"""

    @staticmethod
    def can_flatten(source_info: ArrayTypeInfo, target_info: ArrayTypeInfo) -> bool:
        """
        Check if source multidimensional array can be flattened to target 1D array.

        Args:
            source_info: Source array type information
            target_info: Target 1D array type information

        Returns:
            True if flattening is safe and valid, False otherwise
        """
        # Source must be multidimensional
        if len(source_info.dimensions) < 2:
            return False

        # Target must be 1D
        if len(target_info.dimensions) != 1:
            return False

        # Element types must be compatible
        # (Simplified - full implementation would check type compatibility)
        return True

    @staticmethod
    def calculate_flattened_size(source_info: ArrayTypeInfo) -> int:
        """
        Calculate total element count when flattening multidimensional array.

        Args:
            source_info: Source array type information

        Returns:
            Total number of elements after flattening
        """
        if not source_info.can_flatten_to_1d():
            raise ValueError("Cannot calculate size for array with inferred dimensions")

        return source_info.get_element_count()
