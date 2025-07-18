"""
Hexen Type Utilities

Centralized type utility functions for the semantic analyzer.
Provides type checking, coercion, and resolution utilities used across
the semantic analysis phase.
"""

from typing import Optional, Dict, FrozenSet
from .types import HexenType


# Module-level constants for type sets and maps
NUMERIC_TYPES: FrozenSet[HexenType] = frozenset(
    {
        HexenType.I32,
        HexenType.I64,
        HexenType.F32,
        HexenType.F64,
        HexenType.COMPTIME_INT,
        HexenType.COMPTIME_FLOAT,
    }
)

FLOAT_TYPES: FrozenSet[HexenType] = frozenset(
    {
        HexenType.F32,
        HexenType.F64,
        HexenType.COMPTIME_FLOAT,
    }
)

INTEGER_TYPES: FrozenSet[HexenType] = frozenset(
    {
        HexenType.I32,
        HexenType.I64,
        HexenType.COMPTIME_INT,
    }
)

# Comptime type coercion targets
COMPTIME_INT_TARGETS: FrozenSet[HexenType] = frozenset(
    {
        HexenType.I32,
        HexenType.I64,
        HexenType.F32,
        HexenType.F64,
    }
)

COMPTIME_FLOAT_TARGETS: FrozenSet[HexenType] = frozenset(
    {
        HexenType.F32,
        HexenType.F64,
    }
)

# Regular numeric widening coercion rules
WIDENING_RULES: Dict[HexenType, FrozenSet[HexenType]] = {
    HexenType.I32: frozenset({HexenType.I64, HexenType.F32, HexenType.F64}),
    HexenType.I64: frozenset(
        {HexenType.F32, HexenType.F64}
    ),  # Note: may lose precision
    HexenType.F32: frozenset({HexenType.F64}),
}

# Type conversion maps
TO_FLOAT_TYPE_MAP: Dict[HexenType, HexenType] = {
    HexenType.COMPTIME_INT: HexenType.F64,
    HexenType.COMPTIME_FLOAT: HexenType.F64,
    HexenType.I32: HexenType.F64,
    HexenType.I64: HexenType.F64,
}

TO_INTEGER_TYPE_MAP: Dict[HexenType, HexenType] = {
    HexenType.COMPTIME_INT: HexenType.I32,
}

TYPE_STRING_TO_HEXEN_TYPE: Dict[str, HexenType] = {
    "i32": HexenType.I32,
    "i64": HexenType.I64,
    "f32": HexenType.F32,
    "f64": HexenType.F64,
    "string": HexenType.STRING,
    "bool": HexenType.BOOL,
    "void": HexenType.VOID,
    "comptime_int": HexenType.COMPTIME_INT,
    "comptime_float": HexenType.COMPTIME_FLOAT,
}


def parse_type(type_str: str) -> HexenType:
    """
    Parse a type string to HexenType enum.

    Handles conversion from string representation (from parser)
    to internal enum representation using the module-level map.

    Returns HexenType.UNKNOWN for unrecognized types.
    This allows for graceful handling of future type additions.
    """
    return TYPE_STRING_TO_HEXEN_TYPE.get(type_str, HexenType.UNKNOWN)


def is_numeric_type(type_: HexenType) -> bool:
    """
    Check if a type is numeric (integer or float).

    Args:
        type_: The type to check

    Returns:
        True if the type is numeric (I32, I64, F32, F64, COMPTIME_INT, COMPTIME_FLOAT)
    """
    return type_ in NUMERIC_TYPES


def is_float_type(type_: HexenType) -> bool:
    """
    Check if a type is a float type.

    Args:
        type_: The type to check

    Returns:
        True if the type is a float type (F32, F64, COMPTIME_FLOAT)
    """
    return type_ in FLOAT_TYPES


def is_integer_type(type_: HexenType) -> bool:
    """
    Check if a type is an integer type.

    Args:
        type_: The type to check

    Returns:
        True if the type is an integer type (I32, I64, COMPTIME_INT)
    """
    return type_ in INTEGER_TYPES


def can_coerce(from_type: HexenType, to_type: HexenType) -> bool:
    """
    Check if from_type can be automatically coerced to to_type.

    Implements TYPE_SYSTEM.md coercion rules:

    1. Comptime types (ergonomic literals):
       - comptime_int can coerce to any integer or float type
       - comptime_float can coerce to any float type

    2. Identity coercion:
       - Any type can coerce to itself

    3. NO automatic widening for concrete types:
       - All concrete type conversions require explicit syntax per TYPE_SYSTEM.md

    Args:
        from_type: The source type
        to_type: The target type

    Returns:
        True if coercion is allowed
    """
    # Identity coercion - type can always coerce to itself
    if from_type == to_type:
        return True

    # comptime type coercion (ergonomic literals)
    if from_type == HexenType.COMPTIME_INT:
        return to_type in COMPTIME_INT_TARGETS

    if from_type == HexenType.COMPTIME_FLOAT:
        return to_type in COMPTIME_FLOAT_TARGETS

    # NO automatic widening for concrete types per TYPE_SYSTEM.md
    # All concrete conversions require explicit syntax: value:type
    return False


def resolve_comptime_type(
    comptime_type: HexenType, target_type: Optional[HexenType] = None
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


def to_float_type(type_: HexenType) -> HexenType:
    """
    Convert a type to its float equivalent.

    Args:
        type_: The type to convert

    Returns:
        The float equivalent type (F32 or F64)
    """
    return TO_FLOAT_TYPE_MAP.get(type_, type_)


def to_integer_type(type_: HexenType) -> HexenType:
    """
    Convert a type to its integer equivalent.

    Args:
        type_: The type to convert

    Returns:
        The integer equivalent type (I32 or I64)
    """
    return TO_INTEGER_TYPE_MAP.get(type_, type_)


def get_wider_type(left_type: HexenType, right_type: HexenType) -> HexenType:
    """
    Get the wider of two numeric types.

    Args:
        left_type: First type
        right_type: Second type

    Returns:
        The wider of the two types
    """
    if is_float_type(left_type) or is_float_type(right_type):
        # If either is float, result is float
        return (
            HexenType.F64 if HexenType.F64 in {left_type, right_type} else HexenType.F32
        )
    # Both are integers
    return HexenType.I64 if HexenType.I64 in {left_type, right_type} else HexenType.I32


def infer_type_from_value(value: Dict) -> HexenType:
    """
    Infer a HexenType from a literal value (using comptime types).

    Zig-inspired type inference rules:
    - Integer literals have type comptime_int (arbitrary precision, context-dependent)
    - Float literals have type comptime_float (arbitrary precision, context-dependent)
    - String literals are string type
    - Boolean literals are bool type
    - comptime types can coerce to any compatible concrete type

    This eliminates the need for literal suffixes and provides elegant type coercion.

    Args:
        value: A dict (AST node) representing a literal (e.g. { "type": "literal", "value": 42 })

    Returns:
        The inferred HexenType (e.g. HexenType.COMPTIME_INT, HexenType.STRING, etc.) or HexenType.UNKNOWN if the node is not a literal.
    """
    if value.get("type") != "literal":
        return HexenType.UNKNOWN

    val = value.get("value")
    if isinstance(val, bool):
        return HexenType.BOOL
    elif isinstance(val, int):
        return HexenType.COMPTIME_INT  # Zig-style: context will determine final type
    elif isinstance(val, float):
        return HexenType.COMPTIME_FLOAT  # Zig-style: context will determine final type
    elif isinstance(val, str):
        return HexenType.STRING
    else:
        return HexenType.UNKNOWN


def is_mixed_type_operation(left_type: HexenType, right_type: HexenType) -> bool:
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


def is_string_type(type_: HexenType) -> bool:
    """Check if a type is a string type."""
    return type_ == HexenType.STRING


def is_boolean_type(type_: HexenType) -> bool:
    """Check if a type is a boolean type."""
    return type_ == HexenType.BOOL


def is_precision_loss_operation(from_type: HexenType, to_type: HexenType) -> bool:
    """
    Check if an operation represents precision loss that requires explicit conversion.

    These are the "dangerous" operations that require explicit conversion:
    - i64 → i32 (truncation)
    - f64 → f32 (precision loss)
    - float → integer (truncation + precision loss)
    - comptime_float → integer (truncation)

    This function implements the "Explicit Danger, Implicit Safety" principle
    by identifying operations that could lose data or precision.

    Args:
        from_type: The source type
        to_type: The target type

    Returns:
        True if the operation could lose precision and requires explicit conversion
    """
    return (
        # Integer truncation
        (from_type == HexenType.I64 and to_type == HexenType.I32)
        or
        # Float precision loss
        (from_type == HexenType.F64 and to_type == HexenType.F32)
        or
        # Float to integer conversion (any combination)
        (
            from_type in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}
            and to_type in {HexenType.I32, HexenType.I64}
        )
        or
        # Mixed precision loss (i64 → f32, f64 → i32)
        (from_type == HexenType.I64 and to_type == HexenType.F32)
        or (from_type == HexenType.F64 and to_type == HexenType.I32)
    )
