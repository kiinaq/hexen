"""
Hexen Type System

Core type definitions and enums for the Hexen semantic analyzer.
Defines the fundamental types and mutability concepts used throughout
the semantic analysis phase.
"""

from enum import Enum


class HexenType(Enum):
    """
    Hexen's type system with comptime types for elegant numeric handling.

    Design decisions:
    - I32 as default integer type (following Rust conventions)
    - F32/F64 for single/double precision floats
    - COMPTIME_INT for integer literals (arbitrary precision, context-dependent coercion)
    - COMPTIME_FLOAT for float literals (arbitrary precision, context-dependent coercion)
    - VOID for functions/blocks that don't return values
    - UNKNOWN for type inference failures (not user-facing)
    - UNINITIALIZED for explicit undef values (different from null/None)

    Zig-inspired comptime types:
    - comptime_int: Integer literals that can coerce to any integer or float type
    - comptime_float: Float literals that can coerce to any float type
    - Context-dependent coercion eliminates need for literal suffixes

    Future extensions:
    - User-defined types (structs, enums)
    - Generic types
    - Function types
    """

    I32 = "i32"
    I64 = "i64"
    F32 = "f32"  # New: 32-bit float
    F64 = "f64"
    STRING = "string"
    BOOL = "bool"
    VOID = "void"  # For functions/blocks that don't return values
    COMPTIME_INT = "comptime_int"  # New: integer literals
    COMPTIME_FLOAT = "comptime_float"  # New: float literals
    UNKNOWN = "unknown"  # For type inference failures - internal use only
    UNINITIALIZED = "undef"  # For explicit undef values - different from null


class Mutability(Enum):
    """
    Variable mutability levels following Rust's ownership model.

    IMMUTABLE (val):
    - Cannot be reassigned after initialization
    - Prevents accidental mutation bugs
    - Default choice encourages functional programming style

    MUTABLE (mut):
    - Can be reassigned multiple times
    - Requires explicit opt-in for clarity
    - Used when mutation is genuinely needed
    """

    IMMUTABLE = "val"  # val variables - cannot be reassigned
    MUTABLE = "mut"  # mut variables - can be reassigned
