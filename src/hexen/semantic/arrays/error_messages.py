"""
Comprehensive error handling and message formatting for array operations.

This module provides centralized error handling for the array type system,
following the patterns established in the main semantic analyzer.
"""

from typing import Dict, Any, Optional


class ArraySemanticError(Exception):
    """Specialized exception for array semantic errors."""

    def __init__(
        self,
        message: str,
        node: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.node = node
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self) -> str:
        result = self.message
        if self.suggestion:
            result += f"\nSuggestion: {self.suggestion}"
        return result


class ArrayErrorMessages:
    """Centralized error message formatting for array operations."""

    @staticmethod
    def size_mismatch(expected: int, actual: int, context: str) -> str:
        """Generate error message for array size mismatches."""
        return (
            f"Array size mismatch in {context}: expected {expected} elements, got {actual}\n"
            f"Array sizes must match exactly (size-as-type principle)"
        )

    @staticmethod
    def dimension_mismatch(expected_dims: int, actual_dims: int, operation: str) -> str:
        """Generate error message for dimension mismatches."""
        return (
            f"Dimension mismatch in {operation}: expected {expected_dims}D array, got {actual_dims}D\n"
            f"All arrays in operation must have same dimensionality"
        )

    @staticmethod
    def index_out_of_bounds(index: int, array_size: int) -> str:
        """Generate error message for array index out of bounds."""
        return (
            f"Array index {index} out of bounds for array of size {array_size}\n"
            f"Valid indices: 0 to {array_size - 1}"
        )

    @staticmethod
    def comptime_conversion_required(from_type: str, to_type: str) -> str:
        """Generate error message for required comptime conversions."""
        return (
            f"Cannot assign {from_type} to {to_type} without explicit conversion\n"
            f"Use explicit conversion: array:{to_type}"
        )

    @staticmethod
    def mixed_concrete_types(left_type: str, right_type: str, context: str) -> str:
        """Generate error message for mixed concrete types."""
        return (
            f"Mixed concrete array types in {context}: {left_type} and {right_type}\n"
            f"Transparent costs principle requires explicit conversion\n"
            f"Use explicit type conversions for compatibility"
        )

    @staticmethod
    def empty_array_type_annotation_required() -> str:
        """Generate error message for empty arrays without explicit type annotation."""
        return (
            "Empty array literal requires explicit type annotation\n"
            "Use: val array : [N]T = [] or val array : [_]T = []"
        )

    @staticmethod
    def inconsistent_multidim_structure(
        row: int, expected_cols: int, actual_cols: int
    ) -> str:
        """Generate error message for inconsistent multidimensional array structure."""
        return (
            f"Inconsistent multidimensional array structure:\n"
            f"Row 0 has {expected_cols} elements, row {row} has {actual_cols} elements\n"
            f"All rows must have the same number of columns"
        )

    @staticmethod
    def flattening_element_count_mismatch(source_count: int, target_count: int) -> str:
        """Generate error message for array flattening element count mismatches."""
        return (
            f"Array flattening element count mismatch:\n"
            f"Source array has {source_count} elements, target requires {target_count}\n"
            f"Element counts must match exactly for safe flattening"
        )

    @staticmethod
    def invalid_index_type(index_type: str) -> str:
        """Generate error message for invalid array index types."""
        return (
            f"Array index must be integer type, got {index_type}\n"
            f"Valid index types: i32, i64, comptime_int"
        )

    @staticmethod
    def non_array_indexing(type_name: str) -> str:
        """Generate error message for indexing non-array types."""
        return (
            f"Cannot index non-array type: {type_name}\n"
            f"Only array types support indexing operations"
        )

    @staticmethod
    def too_many_indices(array_dims: int, access_dims: int) -> str:
        """Generate error message for too many access indices."""
        return (
            f"Too many indices: array has {array_dims} dimensions, got {access_dims} indices\n"
            f"Number of indices cannot exceed array dimensionality"
        )

    @staticmethod
    def inferred_dimension_bounds_check() -> str:
        """Generate error message for bounds checking on inferred dimensions."""
        return (
            "Cannot perform bounds checking on arrays with inferred dimensions\n"
            "Use explicit array sizes for compile-time bounds validation"
        )

    @staticmethod
    def element_type_incompatible(
        source_type: str, target_type: str, context: str
    ) -> str:
        """Generate error message for incompatible element types."""
        return (
            f"Element type incompatible in {context}: cannot assign {source_type} to {target_type}\n"
            f"Use explicit conversion if intended: element:{target_type}"
        )

    @staticmethod
    def multidim_array_must_contain_arrays() -> str:
        """Generate error message for invalid multidimensional structure."""
        return (
            "Multidimensional array must contain sub-arrays\n"
            "Example: [[1, 2], [3, 4]] for 2D array"
        )

    @staticmethod
    def cannot_flatten_inferred_dimensions() -> str:
        """Generate error message for flattening arrays with inferred dimensions."""
        return (
            "Cannot flatten array with inferred dimensions to fixed-size array\n"
            "Use explicit array dimensions for flattening operations"
        )

    @staticmethod
    def explicit_type_annotation_required_for_mixed_types() -> str:
        """Generate error message for mixed types requiring explicit type annotation."""
        return (
            "Mixed concrete/comptime element types require explicit array type annotation\n"
            "Type mismatch: incompatible element types in array literal\n"
            "Provide explicit type annotation: val array : [N]T = [elements...]"
        )


class ArrayErrorFactory:
    """Factory for creating array-specific semantic errors."""

    @staticmethod
    def create_size_mismatch_error(
        expected: int, actual: int, context: str, node: Optional[Dict[str, Any]] = None
    ) -> ArraySemanticError:
        """Create a size mismatch error."""
        message = ArrayErrorMessages.size_mismatch(expected, actual, context)
        suggestion = f"Ensure array has exactly {expected} elements"
        return ArraySemanticError(message, node, suggestion)

    @staticmethod
    def create_bounds_error(
        index: int, array_size: int, node: Optional[Dict[str, Any]] = None
    ) -> ArraySemanticError:
        """Create an index out of bounds error."""
        message = ArrayErrorMessages.index_out_of_bounds(index, array_size)
        suggestion = f"Use index in range 0..{array_size - 1}"
        return ArraySemanticError(message, node, suggestion)

    @staticmethod
    def create_empty_array_type_annotation_error(
        node: Optional[Dict[str, Any]] = None,
    ) -> ArraySemanticError:
        """Create an empty array type annotation required error."""
        message = ArrayErrorMessages.empty_array_type_annotation_required()
        suggestion = "Add explicit type annotation: val array : [N]T = []"
        return ArraySemanticError(message, node, suggestion)

    @staticmethod
    def create_inconsistent_structure_error(
        row: int,
        expected_cols: int,
        actual_cols: int,
        node: Optional[Dict[str, Any]] = None,
    ) -> ArraySemanticError:
        """Create an inconsistent multidimensional structure error."""
        message = ArrayErrorMessages.inconsistent_multidim_structure(
            row, expected_cols, actual_cols
        )
        suggestion = f"Ensure all rows have exactly {expected_cols} elements"
        return ArraySemanticError(message, node, suggestion)

    @staticmethod
    def create_invalid_index_type_error(
        index_type: str, node: Optional[Dict[str, Any]] = None
    ) -> ArraySemanticError:
        """Create an invalid index type error."""
        message = ArrayErrorMessages.invalid_index_type(index_type)
        suggestion = "Use integer types (i32, i64, comptime_int) for array indices"
        return ArraySemanticError(message, node, suggestion)
