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
    USIZE = "usize"  # Platform-dependent unsigned integer for array indexing
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
        if element_comptime_type not in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }:
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
                raise ValueError(
                    f"All dimensions must be non-negative integers, got {dim}"
                )

        self.element_comptime_type = element_comptime_type
        self.dimensions = dimensions

    def __str__(self) -> str:
        """Human-readable string representation"""
        dims_str = "".join(f"[{d}]" for d in self.dimensions)
        elem_str = (
            "int" if self.element_comptime_type == HexenType.COMPTIME_INT else "float"
        )
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

    def can_materialize_to(self, target: "ArrayType") -> bool:
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

    def dimension_mismatch_details(self, target: "ArrayType") -> str:
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
        for i, (comptime_dim, concrete_dim) in enumerate(
            zip(self.dimensions, target.dimensions)
        ):
            if concrete_dim != "_" and comptime_dim != concrete_dim:
                mismatches.append(
                    f"dimension {i}: expected {concrete_dim}, got {comptime_dim}"
                )

        if mismatches:
            return "; ".join(mismatches)

        return "dimensions compatible"


class ArrayType:
    """
    Represents explicit concrete array types like [3]i32, [2][4]f64, [_]i32.

    Unlike comptime array types (which are flexible), concrete array types have:
    - Fixed dimensions with specific sizes OR inferred dimensions ([_])
    - Concrete element types
    - Explicit type annotation requirements

    Inferred dimensions ([_]) are used for:
    - Function parameters that accept any array size
    - Size inference in array type conversions
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
        if not isinstance(other, ArrayType):
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


class RangeType:
    """
    Represents a range type (e.g., range[i32], range[usize], range[f64]).

    Ranges are lazy sequences that describe numeric sequences without storing elements.
    They serve two distinct purposes:

    1. **User Type Ranges** (i32, i64, f32, f64):
       - For materialization to arrays: [range]
       - For iteration (future): for x in range { }

    2. **Index Type Ranges** (usize only):
       - For array slicing: array[range]
       - Works with any array element type

    Key Properties:
    - Immutable: Ranges cannot be modified after creation
    - Lazy: No storage cost (O(1) space regardless of size)
    - Typed: Element type determines valid operations

    Design Rules:
    - User types → materialization & iteration
    - Index type (usize) → array indexing only
    - Float types cannot convert to usize (no indexing)

    Attributes:
        element_type: Type of elements the range produces
        has_start: Whether range has start bound (False for ..end and ..)
        has_end: Whether range has end bound (False for start.. and ..)
        has_step: Whether range has explicit step
        inclusive: True for ..=, False for ..

    Examples:
        range[i32]   → User type range (materialization/iteration)
        range[usize] → Index type range (array slicing)
        range[f64]   → User type range (iteration only, step required)
    """

    def __init__(
        self,
        element_type: HexenType,
        has_start: bool,
        has_end: bool,
        has_step: bool,
        inclusive: bool,
    ):
        """
        Create a range type.

        Args:
            element_type: Type of elements (i32, i64, f32, f64, usize)
            has_start: Whether range has start bound
            has_end: Whether range has end bound
            has_step: Whether range has explicit step
            inclusive: True for ..=, False for ..

        Raises:
            ValueError: If element type is invalid for ranges
        """
        # Validate element type is numeric
        valid_types = {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.USIZE,
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }

        if element_type not in valid_types:
            raise ValueError(
                f"Range element type must be numeric, got {element_type}"
            )

        self.element_type = element_type
        self.has_start = has_start
        self.has_end = has_end
        self.has_step = has_step
        self.inclusive = inclusive

    def is_bounded(self) -> bool:
        """Check if range has both start and end bounds"""
        return self.has_start and self.has_end

    def is_unbounded(self) -> bool:
        """Check if range has neither start nor end bound"""
        return not self.has_start and not self.has_end

    def can_materialize(self) -> bool:
        """Check if range can be materialized to array (requires both bounds)"""
        return self.is_bounded()

    def can_iterate(self) -> bool:
        """Check if range can be iterated (requires start bound)"""
        return self.has_start

    def can_slice(self) -> bool:
        """Check if range can be used for array slicing (any bounds OK)"""
        return True  # All ranges can slice (even unbounded)

    def requires_step(self) -> bool:
        """Check if range element type requires explicit step (floats only)"""
        return self.element_type in {
            HexenType.F32,
            HexenType.F64,
            HexenType.COMPTIME_FLOAT,
        }

    def is_user_type(self) -> bool:
        """Check if this is a user type range (i32, i64, f32, f64)"""
        return self.element_type in {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }

    def is_index_type(self) -> bool:
        """Check if this is an index type range (usize only)"""
        return self.element_type == HexenType.USIZE

    def is_comptime(self) -> bool:
        """Check if this is a comptime range (flexible adaptation)"""
        return self.element_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}

    def __str__(self) -> str:
        """Human-readable string representation"""
        elem_str = self.element_type.value
        bounds = []
        if self.has_start:
            bounds.append("start")
        if self.has_end:
            bounds.append("end")
        if self.has_step:
            bounds.append("step")

        bounds_str = ",".join(bounds) if bounds else "unbounded"
        inclusive_str = "inclusive" if self.inclusive else "exclusive"

        return f"range[{elem_str}]({bounds_str},{inclusive_str})"

    def __repr__(self) -> str:
        """Debug representation"""
        return (
            f"RangeType(element_type={self.element_type!r}, "
            f"has_start={self.has_start}, has_end={self.has_end}, "
            f"has_step={self.has_step}, inclusive={self.inclusive})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, RangeType):
            return False
        return (
            self.element_type == other.element_type
            and self.has_start == other.has_start
            and self.has_end == other.has_end
            and self.has_step == other.has_step
            and self.inclusive == other.inclusive
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.element_type,
                self.has_start,
                self.has_end,
                self.has_step,
                self.inclusive,
            )
        )


class ComptimeRangeType(RangeType):
    """
    Comptime range type that preserves flexibility for context-dependent adaptation.

    Comptime ranges (e.g., 1..10, 0.0..1.0:0.1) can adapt to different concrete types:
    - range[comptime_int] → range[i32], range[i64], range[f32], range[f64], range[usize]
    - range[comptime_float] → range[f32], range[f64] (NOT usize - floats can't index!)

    This enables ergonomic range literals without type annotations while maintaining
    type safety through context-driven resolution.

    Examples:
        val r = 1..10                    # ComptimeRangeType(COMPTIME_INT)
        val idx : range[usize] = r       # Adapts to range[usize] for indexing
        val vals : range[i32] = r        # Adapts to range[i32] for materialization
    """

    def __init__(
        self,
        element_comptime_type: HexenType,
        has_start: bool,
        has_end: bool,
        has_step: bool,
        inclusive: bool,
    ):
        """
        Create a comptime range type.

        Args:
            element_comptime_type: COMPTIME_INT or COMPTIME_FLOAT
            has_start: Whether range has start bound
            has_end: Whether range has end bound
            has_step: Whether range has explicit step
            inclusive: True for ..=, False for ..

        Raises:
            ValueError: If element type is not comptime
        """
        if element_comptime_type not in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }:
            raise ValueError(
                f"ComptimeRangeType element must be COMPTIME_INT or COMPTIME_FLOAT, "
                f"got {element_comptime_type}"
            )

        super().__init__(
            element_type=element_comptime_type,
            has_start=has_start,
            has_end=has_end,
            has_step=has_step,
            inclusive=inclusive,
        )

    def can_adapt_to(self, target_type: HexenType) -> bool:
        """
        Check if this comptime range can adapt to target concrete type.

        Rules (following comptime type system):
        - comptime_int → i32, i64, f32, f64, usize (any numeric)
        - comptime_float → f32, f64 ONLY (NOT usize - float indices forbidden)

        Args:
            target_type: Target element type to adapt to

        Returns:
            True if adaptation is safe, False otherwise
        """
        if self.element_type == HexenType.COMPTIME_INT:
            # comptime_int can adapt to any numeric type
            return target_type in {
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
                HexenType.USIZE,
            }
        elif self.element_type == HexenType.COMPTIME_FLOAT:
            # comptime_float CANNOT adapt to usize (float indices forbidden)
            return target_type in {HexenType.F32, HexenType.F64}

        return False

    def __str__(self) -> str:
        """Human-readable string representation"""
        elem_str = "int" if self.element_type == HexenType.COMPTIME_INT else "float"
        bounds = []
        if self.has_start:
            bounds.append("start")
        if self.has_end:
            bounds.append("end")
        if self.has_step:
            bounds.append("step")

        bounds_str = ",".join(bounds) if bounds else "unbounded"
        inclusive_str = "inclusive" if self.inclusive else "exclusive"

        return f"comptime_range[{elem_str}]({bounds_str},{inclusive_str})"
