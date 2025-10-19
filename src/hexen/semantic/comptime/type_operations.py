"""
Comptime Type Operations Module

Core comptime type classification, unification, and basic operations.
This module provides the foundation for all other comptime modules.

Responsibilities:
- Comptime vs concrete type classification
- Type promotion rules (int + float = float)
- Type unification across expressions
- Basic safety and compatibility checks
- Context-guided type resolution

This module serves as the base dependency for other comptime modules.
"""

from typing import Dict, List, Optional, Union

from ..symbol_table import SymbolTable
from ..type_util import is_numeric_type, is_float_type, is_integer_type
from ..types import HexenType


class TypeOperations:
    """
    Core comptime type operations and classification.

    Provides fundamental type classification and unification methods
    that serve as the foundation for other comptime modules.
    """

    def __init__(self, symbol_table: SymbolTable):
        """
        Initialize type operations with symbol table access.

        Args:
            symbol_table: Symbol table for variable type lookups
        """
        self.symbol_table = symbol_table

    # =========================================================================
    # CORE TYPE CLASSIFICATION
    # =========================================================================

    def is_comptime_type(self, type_: HexenType) -> bool:
        """
        Check if type is a comptime type (COMPTIME_INT or COMPTIME_FLOAT).

        Args:
            type_: The type to check

        Returns:
            True if type is comptime (COMPTIME_INT or COMPTIME_FLOAT)
        """
        return type_ in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}

    def is_mixed_comptime_operation(
        self, left_type: HexenType, right_type: HexenType
    ) -> bool:
        """
        Detect operations mixing comptime and concrete types.

        Args:
            left_type: Left operand type
            right_type: Right operand type

        Returns:
            True if operation mixes comptime and concrete types
        """
        left_is_comptime = self.is_comptime_type(left_type)
        right_is_comptime = self.is_comptime_type(right_type)

        # Mixed if exactly one operand is comptime
        return left_is_comptime != right_is_comptime

    def is_mixed_type_operation(
        self, left_type: HexenType, right_type: HexenType
    ) -> bool:
        """
        Check if an operation involves mixed types that require explicit handling.

        Returns True ONLY for Pattern 3 (Mixed Concrete → Explicit Required):
        - Operation between different concrete integer types (e.g. i32 + i64)
        - Operation between different concrete float types (e.g. f32 + f64)
        - Operation between concrete float and concrete integer types

        Returns False for all other patterns:
        - Pattern 1: Comptime + Comptime → Comptime (e.g. comptime_int + comptime_float)
        - Pattern 2: Comptime + Concrete → Concrete (e.g. i64 + comptime_int, f32 + comptime_float)
        - Pattern 4: Same Concrete → Same Concrete (e.g. i32 + i32)
        """
        # Pattern 1 & 2: Any operation involving comptime types should be handled elsewhere (not mixed)
        if left_type in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        } or right_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            return False

        # Pattern 4: Same concrete types are not mixed
        if left_type == right_type:
            return False

        # Pattern 3: Mixed concrete types - require explicit conversions
        return (
            # Different concrete integer types
            (is_integer_type(left_type) and is_integer_type(right_type))
            or
            # Different concrete float types
            (is_float_type(left_type) and is_float_type(right_type))
            or
            # Concrete float + concrete integer (either direction)
            (is_float_type(left_type) and is_integer_type(right_type))
            or (is_integer_type(left_type) and is_float_type(right_type))
        )

    # =========================================================================
    # TYPE UNIFICATION & PROMOTION
    # =========================================================================

    def unify_comptime_types(self, types: List[HexenType]) -> Optional[HexenType]:
        """
        Unify multiple comptime types following promotion rules.

        Args:
            types: List of types to unify

        Returns:
            Unified comptime type or None if unification not possible
        """
        if not types:
            return None

        # Filter to only comptime types
        comptime_types = [t for t in types if self.is_comptime_type(t)]

        if not comptime_types:
            return None

        # All comptime_int -> comptime_int
        if all(t == HexenType.COMPTIME_INT for t in comptime_types):
            return HexenType.COMPTIME_INT

        # All comptime_float -> comptime_float
        if all(t == HexenType.COMPTIME_FLOAT for t in comptime_types):
            return HexenType.COMPTIME_FLOAT

        # Mixed comptime types -> comptime_float (promotion rule)
        if (
            HexenType.COMPTIME_INT in comptime_types
            and HexenType.COMPTIME_FLOAT in comptime_types
        ):
            return HexenType.COMPTIME_FLOAT

        return None

    def get_comptime_promotion_result(
        self, left_type: HexenType, right_type: HexenType
    ) -> HexenType:
        """
        Get promotion result for comptime types (int + float = float).

        Args:
            left_type: Left operand type
            right_type: Right operand type

        Returns:
            Promoted comptime type
        """
        # Both comptime_int -> comptime_int
        if left_type == HexenType.COMPTIME_INT and right_type == HexenType.COMPTIME_INT:
            return HexenType.COMPTIME_INT

        # Both comptime_float -> comptime_float
        if (
            left_type == HexenType.COMPTIME_FLOAT
            and right_type == HexenType.COMPTIME_FLOAT
        ):
            return HexenType.COMPTIME_FLOAT

        # Mixed comptime types -> comptime_float (promotion)
        if (
            left_type == HexenType.COMPTIME_INT
            and right_type == HexenType.COMPTIME_FLOAT
        ) or (
            left_type == HexenType.COMPTIME_FLOAT
            and right_type == HexenType.COMPTIME_INT
        ):
            return HexenType.COMPTIME_FLOAT

        # Default fallback
        return left_type

    # =========================================================================
    # SAFETY & COMPATIBILITY CHECKS
    # =========================================================================

    def can_comptime_types_mix_safely(
        self,
        left_type: HexenType,
        right_type: HexenType,
        target_type: Optional[HexenType],
    ) -> bool:
        """
        Check if comptime types can mix safely with given target context.

        Args:
            left_type: Left operand type
            right_type: Right operand type
            target_type: Target type providing context

        Returns:
            True if comptime types can mix safely
        """
        # If both are comptime, they can always mix
        if self.is_comptime_type(left_type) and self.is_comptime_type(right_type):
            return True

        # If one is comptime and we have target context
        if target_type is not None:
            # Comptime type can adapt to concrete type with context
            if (
                self.is_comptime_type(left_type)
                and not self.is_comptime_type(right_type)
            ) or (
                not self.is_comptime_type(left_type)
                and self.is_comptime_type(right_type)
            ):
                return True

        return False

    def are_all_comptime_compatible(self, types: List[HexenType]) -> bool:
        """
        Check if all types are comptime-compatible for unification.

        Args:
            types: List of types to check

        Returns:
            True if all types are comptime-compatible
        """
        if not types:
            return True

        # All types must be comptime types for compatibility
        return all(self.is_comptime_type(t) for t in types)

    # =========================================================================
    # CONTEXT-GUIDED RESOLUTION
    # =========================================================================

    def resolve_comptime_type(
        self, comptime_type: HexenType, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Resolve a comptime type to a concrete type based on context.

        Used when we have a comptime_int or comptime_float that needs to become
        a concrete type. Falls back to default types if no target is provided.

        Args:
            comptime_type: The comptime type to resolve
            target_type: Optional target type for context-guided resolution

        Returns:
            The resolved concrete type
        """
        if comptime_type == HexenType.COMPTIME_INT:
            if target_type and is_numeric_type(target_type):
                return target_type
            return HexenType.I32  # Default integer type

        if comptime_type == HexenType.COMPTIME_FLOAT:
            if target_type and is_float_type(target_type):
                return target_type
            return HexenType.F64  # Default float type

        return comptime_type  # Not a comptime type, return as-is

    # =========================================================================
    # CONDITIONAL COMPTIME TYPE RESOLUTION
    # =========================================================================

    def resolve_conditional_comptime_types(
        self, branch_types: List[HexenType], target_type: Optional[HexenType]
    ) -> HexenType:
        """
        Resolve comptime types across conditional branches.

        Args:
            branch_types: Types from all conditional branches
            target_type: Target type for context-guided resolution

        Returns:
            Unified type for conditional expression
        """
        if not branch_types:
            return HexenType.UNKNOWN

        # If we have target context, use it for resolution
        if target_type:
            # Check if all branches are comptime-compatible with target
            all_compatible = True
            for branch_type in branch_types:
                if self.is_comptime_type(branch_type):
                    # Comptime types adapt to target context
                    continue
                elif branch_type != target_type:
                    all_compatible = False
                    break

            if all_compatible:
                return target_type

        # Without target context, try to unify comptime types
        unified = self.unify_comptime_types(branch_types)
        if unified:
            return unified

        # Check if all branches have same type
        first_type = branch_types[0]
        if all(t == first_type for t in branch_types):
            return first_type

        return HexenType.UNKNOWN

    # =========================================================================
    # ARRAY TYPE OPERATIONS (NEW)
    # =========================================================================

    def is_comptime_array_type(self, type_: Union[HexenType, 'ComptimeArrayType']) -> bool:
        """Check if type is a comptime array type."""
        from ..types import ComptimeArrayType
        return isinstance(type_, ComptimeArrayType)

    def is_array_type(self, type_: HexenType) -> bool:
        """Check if type represents an array (comptime or concrete)."""
        return (
            self.is_comptime_array_type(type_)
            or isinstance(type_, str)
            and type_.startswith("[")
        )

    def unify_comptime_array_types(
        self, element_types: List[HexenType], num_elements: int = 0
    ) -> Optional['ComptimeArrayType']:
        """
        Unify array element types into comptime array types.

        Rules from ARRAY_TYPE_SYSTEM.md:
        - All COMPTIME_INT → ComptimeArrayType(COMPTIME_INT, [num_elements])
        - All COMPTIME_FLOAT → ComptimeArrayType(COMPTIME_FLOAT, [num_elements])
        - Mixed comptime int/float → ComptimeArrayType(COMPTIME_FLOAT, [num_elements])
        - Any concrete types → None (requires explicit context)
        """
        from ..types import ComptimeArrayType

        if not element_types:
            return None

        # Check for all comptime_int
        if all(t == HexenType.COMPTIME_INT for t in element_types):
            return ComptimeArrayType(HexenType.COMPTIME_INT, [num_elements or len(element_types)])

        # Check for all comptime_float
        if all(t == HexenType.COMPTIME_FLOAT for t in element_types):
            return ComptimeArrayType(HexenType.COMPTIME_FLOAT, [num_elements or len(element_types)])

        # Mixed comptime types → comptime_float (promotion)
        comptime_types = {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}
        if all(t in comptime_types for t in element_types):
            return ComptimeArrayType(HexenType.COMPTIME_FLOAT, [num_elements or len(element_types)])

        return None  # Mixed concrete/comptime requires explicit context
