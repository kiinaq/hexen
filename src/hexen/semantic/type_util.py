"""
Hexen Type Utilities

Centralized type utility functions for the semantic analyzer.
Provides type checking, coercion, and resolution utilities used across
the semantic analysis phase.
"""

from typing import Optional
from .types import HexenType


def is_numeric_type(type_: HexenType) -> bool:
    """
    Check if a type is numeric (integer or float).

    Args:
        type_: The type to check

    Returns:
        True if the type is numeric (I32, I64, F32, F64, COMPTIME_INT, COMPTIME_FLOAT)
    """
    return type_ in {
        HexenType.I32,
        HexenType.I64,
        HexenType.F32,
        HexenType.F64,
        HexenType.COMPTIME_INT,
        HexenType.COMPTIME_FLOAT,
    }


def is_float_type(type_: HexenType) -> bool:
    """
    Check if a type is a float type.

    Args:
        type_: The type to check

    Returns:
        True if the type is a float type (F32, F64, COMPTIME_FLOAT)
    """
    return type_ in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}


def is_integer_type(type_: HexenType) -> bool:
    """
    Check if a type is an integer type.

    Args:
        type_: The type to check

    Returns:
        True if the type is an integer type (I32, I64, COMPTIME_INT)
    """
    return type_ in {HexenType.I32, HexenType.I64, HexenType.COMPTIME_INT}


def can_coerce(from_type: HexenType, to_type: HexenType) -> bool:
    """
    Check if from_type can be automatically coerced to to_type.

    Implements context-dependent coercion rules:

    1. Comptime types:
       - comptime_int can coerce to any integer or float type
       - comptime_float can coerce to any float type

    2. Regular widening coercion:
       - i32 can widen to i64 and f64/f32
       - i64 can widen to f64/f32
       - f32 can widen to f64

    3. Identity coercion:
       - Any type can coerce to itself

    Args:
        from_type: The source type
        to_type: The target type

    Returns:
        True if coercion is allowed
    """
    # Identity coercion - type can always coerce to itself
    if from_type == to_type:
        return True

    # comptime type coercion
    if from_type == HexenType.COMPTIME_INT:
        # comptime_int can become numeric types, but NOT bool
        return to_type in {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
        }

    if from_type == HexenType.COMPTIME_FLOAT:
        # comptime_float can become any float type, but NOT bool
        return to_type in {HexenType.F32, HexenType.F64}

    # Regular numeric widening coercion
    widening_rules = {
        HexenType.I32: {HexenType.I64, HexenType.F32, HexenType.F64},
        HexenType.I64: {HexenType.F32, HexenType.F64},  # Note: may lose precision
        HexenType.F32: {HexenType.F64},
    }

    return to_type in widening_rules.get(from_type, set())


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
        else:
            return HexenType.I32  # Default integer type

    elif comptime_type == HexenType.COMPTIME_FLOAT:
        if target_type and is_float_type(target_type):
            return target_type
        else:
            return HexenType.F64  # Default float type

    else:
        return comptime_type  # Not a comptime type, return as-is


def to_float_type(type_: HexenType) -> HexenType:
    """
    Convert a type to its float equivalent.

    Args:
        type_: The type to convert

    Returns:
        The float equivalent type (F32 or F64)
    """
    if type_ == HexenType.COMPTIME_INT:
        return HexenType.F64
    elif type_ == HexenType.COMPTIME_FLOAT:
        return HexenType.F64
    elif type_ in {HexenType.I32, HexenType.I64}:
        return HexenType.F64
    else:
        return type_


def to_integer_type(type_: HexenType) -> HexenType:
    """
    Convert a type to its integer equivalent.

    Args:
        type_: The type to convert

    Returns:
        The integer equivalent type (I32 or I64)
    """
    if type_ == HexenType.COMPTIME_INT:
        return HexenType.I32
    else:
        return type_


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
    else:
        # Both are integers
        return (
            HexenType.I64 if HexenType.I64 in {left_type, right_type} else HexenType.I32
        )
