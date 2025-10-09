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
    - comptime_array_int: Integer array literals with flexible element adaptation
    - comptime_array_float: Float array literals with flexible element adaptation
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
    COMPTIME_ARRAY_INT = "comptime_array_int"  # New: flexible integer arrays
    COMPTIME_ARRAY_FLOAT = "comptime_array_float"  # New: flexible float arrays
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


class BlockEvaluability(Enum):
    """
    Classification of block evaluability for type preservation in the unified block system.

    This classification determines how expression blocks interact with the comptime type system:

    COMPILE_TIME:
    - Block contains only comptime operations (literals, arithmetic on comptime types)
    - Can preserve comptime types for maximum flexibility
    - Enables "one computation, multiple uses" pattern
    - No runtime operations (function calls, conditionals, concrete variables)

    RUNTIME:
    - Block contains runtime operations requiring explicit type context
    - Includes function calls (functions always return concrete types)
    - Includes conditionals (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
    - Includes concrete variable usage
    - Requires explicit type annotation on target variable

    Design rationale:
    - Binary classification simplifies logic (no MIXED enum needed)
    - Aligns with unified block system philosophy
    - Supports both comptime flexibility and explicit runtime costs
    """

    COMPILE_TIME = "compile_time"  # Can preserve comptime types
    RUNTIME = "runtime"  # Requires explicit context (includes mixed operations)


class ConcreteArrayType:
    """
    Represents explicit concrete array types like [3]i32, [2][4]f64, [_]i32.

    Unlike comptime array types (which are flexible), concrete array types have:
    - Fixed dimensions with specific sizes OR inferred dimensions ([_])
    - Concrete element types
    - Explicit type annotation requirements

    Inferred dimensions ([_]) are used for:
    - Function parameters that accept any array size
    - Array flattening with size inference
    """

    def __init__(self, element_type: HexenType, dimensions: list[int | str]):
        """
        Create a concrete array type.

        Args:
            element_type: The concrete element type (I32, F64, etc.)
            dimensions: List of dimension sizes or "_" for inferred
                       e.g., [3] for [3]i32, [2, 4] for [2][4]f64, ["_"] for [_]i32
        """
        if element_type in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
            HexenType.COMPTIME_ARRAY_INT,
            HexenType.COMPTIME_ARRAY_FLOAT,
        }:
            raise ValueError(
                f"ConcreteArrayType cannot use comptime element type: {element_type}"
            )

        self.element_type = element_type
        self.dimensions = dimensions

    def __str__(self) -> str:
        """String representation: [3]i32, [2][4]f64"""
        dim_str = "".join(f"[{dim}]" for dim in self.dimensions)
        return f"{dim_str}{self.element_type.value}"

    def __repr__(self) -> str:
        return f"ConcreteArrayType({self.element_type!r}, {self.dimensions!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ConcreteArrayType):
            return False
        return (
            self.element_type == other.element_type
            and self.dimensions == other.dimensions
        )

    def __hash__(self) -> int:
        return hash((self.element_type, tuple(self.dimensions)))

    def has_inferred_dimensions(self) -> bool:
        """Check if this type has any inferred dimensions ([_])"""
        return any(dim == "_" for dim in self.dimensions)

    def total_elements(self) -> int:
        """
        Calculate total number of elements (product of all dimensions).

        Raises:
            ValueError: If any dimension is inferred ([_])
        """
        if self.has_inferred_dimensions():
            raise ValueError("Cannot calculate total elements with inferred dimensions")

        result = 1
        for dim in self.dimensions:
            result *= dim  # type: ignore - checked above that all are int
        return result

    def is_compatible_with(self, comptime_array_type: HexenType) -> bool:
        """Check if this concrete array type is compatible with a comptime array type"""
        if comptime_array_type == HexenType.COMPTIME_ARRAY_INT:
            # comptime_array_int can coerce to any numeric element types (following comptime_int rules)
            return self.element_type in {
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
            }
        elif comptime_array_type == HexenType.COMPTIME_ARRAY_FLOAT:
            # comptime_array_float can coerce to float element types only (following comptime_float rules)
            return self.element_type in {HexenType.F32, HexenType.F64}
        return False
