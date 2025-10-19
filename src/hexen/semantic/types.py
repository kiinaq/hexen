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
    - ComptimeArrayType class: Array literals with preserved dimensional information
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
    # Removed: COMPTIME_ARRAY_INT and COMPTIME_ARRAY_FLOAT
    # Use ComptimeArrayType class instead for dimensional information preservation
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


class ComptimeArrayType:
    """
    Comptime array type with preserved dimensional information.

    Represents array literals like [1, 2, 3] (comptime_array_int with size 3)
    before they materialize to concrete types like [3]i32.

    Key Properties:
    - Preserves exact dimensions for validation against fixed-size parameters
    - Supports multidimensional arrays (e.g., [[1, 2], [3, 4]] has dimensions [2, 2])
    - Materializes to ConcreteArrayType when assigned explicit type or passed to function
    - Element types are COMPTIME_INT or COMPTIME_FLOAT (not concrete types)

    Design Philosophy:
    - Comptime arrays are "flexible" - same array can materialize to different types
    - But they're not "shapeless" - dimensions must match target requirements
    - This balances ergonomics (no type annotations needed) with safety (no silent truncation)

    Examples:
        [1, 2, 3]           → ComptimeArrayType(COMPTIME_INT, [3])
        [1.5, 2.5]          → ComptimeArrayType(COMPTIME_FLOAT, [2])
        [[1, 2], [3, 4]]    → ComptimeArrayType(COMPTIME_INT, [2, 2])
        [[[1]], [[2]]]      → ComptimeArrayType(COMPTIME_INT, [2, 1, 1])
    """

    def __init__(self, element_comptime_type: HexenType, dimensions: list[int]):
        """
        Create a comptime array type.

        Args:
            element_comptime_type: COMPTIME_INT or COMPTIME_FLOAT
            dimensions: List of dimension sizes (e.g., [5] or [2, 3])

        Raises:
            ValueError: If element type is not comptime or dimensions invalid
        """
        # Validate element type is comptime
        if element_comptime_type not in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            raise ValueError(
                f"ComptimeArrayType element must be COMPTIME_INT or COMPTIME_FLOAT, "
                f"got {element_comptime_type}"
            )

        # Validate dimensions are non-negative integers
        # Note: Dimension 0 is valid for empty arrays (e.g., [0]i32, [[], []])
        if not dimensions:
            raise ValueError("ComptimeArrayType must have at least one dimension")

        for dim in dimensions:
            if not isinstance(dim, int) or dim < 0:
                raise ValueError(f"All dimensions must be non-negative integers, got {dim}")

        self.element_comptime_type = element_comptime_type
        self.dimensions = dimensions

    def __str__(self) -> str:
        """Human-readable string representation"""
        dims_str = "".join(f"[{d}]" for d in self.dimensions)
        elem_str = "int" if self.element_comptime_type == HexenType.COMPTIME_INT else "float"
        return f"comptime_{dims_str}{elem_str}"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"ComptimeArrayType({self.element_comptime_type!r}, {self.dimensions!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ComptimeArrayType):
            return False
        return (
            self.element_comptime_type == other.element_comptime_type
            and self.dimensions == other.dimensions
        )

    def __hash__(self) -> int:
        return hash((self.element_comptime_type, tuple(self.dimensions)))

    def total_elements(self) -> int:
        """
        Calculate total number of elements across all dimensions.

        Examples:
            [3] → 3
            [2, 3] → 6
            [2, 3, 4] → 24
        """
        result = 1
        for dim in self.dimensions:
            result *= dim
        return result

    def ndim(self) -> int:
        """Return number of dimensions (1 for 1D, 2 for 2D, etc.)"""
        return len(self.dimensions)

    def is_1d(self) -> bool:
        """Check if this is a 1D array"""
        return len(self.dimensions) == 1

    def is_multidimensional(self) -> bool:
        """Check if this is a multidimensional array (2D or higher)"""
        return len(self.dimensions) > 1

    def can_materialize_to(self, target: 'ConcreteArrayType') -> bool:
        """
        Check if this comptime array can materialize to target concrete type.

        Rules:
        1. Dimension count must match
        2. Each dimension must be compatible:
           - Fixed dimension (int) must match exactly
           - Inferred dimension ("_") accepts any size
        3. Element type compatibility checked elsewhere

        Args:
            target: ConcreteArrayType to check compatibility against

        Returns:
            True if dimensions are compatible, False otherwise

        Examples:
            comptime_[3]int can materialize to:
            - [3]i32 ✅ (exact match)
            - [3]i64 ✅ (exact match, different element type OK)
            - [_]i32 ✅ (inferred accepts any size)

            comptime_[3]int CANNOT materialize to:
            - [4]i32 ❌ (size mismatch)
            - [2]i32 ❌ (size mismatch)
        """
        # Check dimension count
        if len(self.dimensions) != len(target.dimensions):
            return False

        # Check each dimension
        for comptime_dim, concrete_dim in zip(self.dimensions, target.dimensions):
            if concrete_dim == "_":
                # Inferred dimension accepts any size
                continue
            if comptime_dim != concrete_dim:
                # Fixed dimension must match exactly
                return False

        return True

    def dimension_mismatch_details(self, target: 'ConcreteArrayType') -> str:
        """
        Generate detailed error message for dimension mismatches.

        Used by function analyzer to provide helpful error messages.

        Returns:
            Human-readable string describing the mismatch
        """
        if len(self.dimensions) != len(target.dimensions):
            return (
                f"Dimension count mismatch: "
                f"comptime array has {len(self.dimensions)} dimension(s), "
                f"parameter expects {len(target.dimensions)} dimension(s)"
            )

        mismatches = []
        for i, (comptime_dim, concrete_dim) in enumerate(zip(self.dimensions, target.dimensions)):
            if concrete_dim != "_" and comptime_dim != concrete_dim:
                mismatches.append(
                    f"dimension {i}: expected {concrete_dim}, got {comptime_dim}"
                )

        if mismatches:
            return "; ".join(mismatches)

        return "dimensions compatible"


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
        # Check for ComptimeArrayType instances first (cannot be used as element type)
        if isinstance(element_type, ComptimeArrayType):
            raise ValueError(
                f"ConcreteArrayType cannot use ComptimeArrayType as element: {element_type}"
            )
        # Check for comptime scalar types
        if element_type in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
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

    def is_compatible_with(self, comptime_array: ComptimeArrayType) -> bool:
        """Check if this concrete array type is compatible with a comptime array type"""
        if comptime_array.element_comptime_type == HexenType.COMPTIME_INT:
            # comptime_array_int can coerce to any numeric element types (following comptime_int rules)
            return self.element_type in {
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
            }
        elif comptime_array.element_comptime_type == HexenType.COMPTIME_FLOAT:
            # comptime_array_float can coerce to float element types only (following comptime_float rules)
            return self.element_type in {HexenType.F32, HexenType.F64}
        return False
