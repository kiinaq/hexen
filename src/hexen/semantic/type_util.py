"""
Hexen Type Utilities

Centralized type utility functions for the semantic analyzer.
Provides type checking, coercion, and resolution utilities used across
the semantic analysis phase.
"""

from typing import Optional, Dict, FrozenSet, Union

from .types import HexenType, ArrayType, ComptimeArrayType, RangeType, ComptimeRangeType

# Module-level constants for type sets and maps
NUMERIC_TYPES: FrozenSet[HexenType] = frozenset(
    {
        HexenType.I32,
        HexenType.I64,
        HexenType.F32,
        HexenType.F64,
        HexenType.USIZE,
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
        HexenType.USIZE,  # comptime_int can coerce to usize (ergonomic for indexing)
    }
)

COMPTIME_FLOAT_TARGETS: FrozenSet[HexenType] = frozenset(
    {
        HexenType.F32,
        HexenType.F64,
    }
)

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
    "usize": HexenType.USIZE,  # Platform-dependent unsigned integer for array indexing
    "string": HexenType.STRING,
    "bool": HexenType.BOOL,
    "void": HexenType.VOID,
    "comptime_int": HexenType.COMPTIME_INT,
    "comptime_float": HexenType.COMPTIME_FLOAT,
}

# Inverse mapping for error messages - automatically derived from TYPE_STRING_TO_HEXEN_TYPE
HEXEN_TYPE_TO_STRING: Dict[HexenType, str] = {
    v: k for k, v in TYPE_STRING_TO_HEXEN_TYPE.items()
}

# Type range constants for overflow detection per LITERAL_OVERFLOW_BEHAVIOR.md
TYPE_RANGES: Dict[HexenType, tuple[Union[int, float], Union[int, float]]] = {
    HexenType.I32: (-2147483648, 2147483647),
    HexenType.I64: (-9223372036854775808, 9223372036854775807),
    HexenType.F32: (-3.4028235e38, 3.4028235e38),
    HexenType.F64: (-1.7976931348623157e308, 1.7976931348623157e308),
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


def can_coerce(
    from_type: Union[HexenType, ArrayType, ComptimeArrayType, RangeType, ComptimeRangeType],
    to_type: Union[HexenType, ArrayType, ComptimeArrayType, RangeType, ComptimeRangeType],
) -> bool:
    """
    Check if from_type can be automatically coerced to to_type.

    Implements TYPE_SYSTEM.md coercion rules:

    1. Comptime types (ergonomic literals):
       - comptime_int can coerce to any integer or float type
       - comptime_float can coerce to any float type
       - comptime_array types can coerce to compatible concrete array types

    2. Identity coercion:
       - Any type can coerce to itself

    3. NO automatic widening for concrete types:
       - All concrete type conversions require explicit syntax per TYPE_SYSTEM.md

    4. Array type coercion:
       - ComptimeArrayType can coerce to compatible ConcreteArrayType (PHASE 2)
       - Comptime array enum types can coerce to compatible ConcreteArrayType (legacy)
       - ConcreteArrayType only coerces to identical ConcreteArrayType

    Args:
        from_type: The source type (HexenType, ConcreteArrayType, or ComptimeArrayType)
        to_type: The target type (HexenType, ConcreteArrayType, or ComptimeArrayType)

    Returns:
        True if coercion is allowed
    """
    # Identity coercion - type can always coerce to itself
    if from_type == to_type:
        return True

    if isinstance(from_type, ComptimeArrayType) and isinstance(
        to_type, ArrayType
    ):
        # Array coercion requires exact dimension count match
        if len(from_type.dimensions) != len(to_type.dimensions):
            return False

        # Check each dimension (allow [_] inference)
        for from_dim, to_dim in zip(from_type.dimensions, to_type.dimensions):
            if to_dim == "_":
                # Inferred dimension - accepts any size
                continue
            if from_dim != to_dim:
                # Concrete dimensions must match exactly
                return False

        # Check element type compatibility
        if from_type.element_comptime_type == HexenType.COMPTIME_INT:
            # comptime_int can coerce to any numeric type
            return to_type.element_type in {
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
            }
        elif from_type.element_comptime_type == HexenType.COMPTIME_FLOAT:
            # comptime_float can coerce to float types only
            return to_type.element_type in {HexenType.F32, HexenType.F64}
        return False

    # PHASE 5 ADDITION: Handle ComptimeArrayType → ComptimeArrayType coercion
    if isinstance(from_type, ComptimeArrayType) and isinstance(
        to_type, ComptimeArrayType
    ):
        # Both comptime arrays - check if dimensions and element types match exactly
        return (
            from_type.dimensions == to_type.dimensions
            and from_type.element_comptime_type == to_type.element_comptime_type
        )

    # PHASE 5 ADDITION: Handle ComptimeArrayType → HexenType (invalid coercion)
    if isinstance(from_type, ComptimeArrayType) and isinstance(to_type, HexenType):
        # Cannot coerce array to scalar type
        return False

    # RANGE SYSTEM ADDITION: Handle ComptimeRangeType → RangeType coercion
    if isinstance(from_type, ComptimeRangeType) and isinstance(to_type, RangeType):
        # Comptime range can coerce to any compatible concrete range type
        # Check element type compatibility: comptime_int → i32/i64/usize, comptime_float → f32/f64
        if from_type.element_type == HexenType.COMPTIME_INT:
            # comptime_int ranges can coerce to any integer or usize range types
            if to_type.element_type not in {
                HexenType.I32,
                HexenType.I64,
                HexenType.USIZE,
            }:
                return False
        elif from_type.element_type == HexenType.COMPTIME_FLOAT:
            # comptime_float ranges can coerce to float range types
            if to_type.element_type not in {HexenType.F32, HexenType.F64}:
                return False
        else:
            # Other types (bool, string) must match exactly
            if from_type.element_type != to_type.element_type:
                return False

        # Comptime ranges can coerce to concrete ranges regardless of structure
        # (Type annotations like `range[f32]` accept any range structure)
        # Specific validation (e.g., float ranges requiring steps) happens elsewhere
        return True

    # RANGE SYSTEM ADDITION: Handle ComptimeRangeType → ComptimeRangeType coercion
    if isinstance(from_type, ComptimeRangeType) and isinstance(
        to_type, ComptimeRangeType
    ):
        # Both comptime ranges - they must have the same element type and structure
        return from_type.element_type == to_type.element_type

    # RANGE SYSTEM ADDITION: Handle RangeType → RangeType coercion
    if isinstance(from_type, RangeType) and isinstance(to_type, RangeType):
        # Concrete range to concrete range coercion
        # Allow coercion if element types match (type annotations are flexible about structure)
        # Only require exact match if both are from non-annotation contexts
        if from_type.element_type == to_type.element_type:
            # Same element type: allow coercion (type annotations don't enforce structure)
            return True
        # Different element types: require explicit conversion :type syntax
        return False

    # RANGE SYSTEM ADDITION: Invalid range coercions
    if isinstance(from_type, (RangeType, ComptimeRangeType)) or isinstance(
        to_type, (RangeType, ComptimeRangeType)
    ):
        # Cannot coerce range to/from non-range types
        return False

    # Handle ConcreteArrayType cases
    if isinstance(to_type, ArrayType):
        # Handle inferred-size parameter matching: [N]T can coerce to [_]T
        if isinstance(from_type, ArrayType):
            # Element types must match
            if from_type.element_type != to_type.element_type:
                return False

            # Dimension count must match
            if len(from_type.dimensions) != len(to_type.dimensions):
                return False

            # Check each dimension: either exact match or target has inferred (_)
            for from_dim, to_dim in zip(from_type.dimensions, to_type.dimensions):
                if to_dim == "_":
                    # Inferred dimension accepts any size
                    continue
                elif from_dim == "_":
                    # Source has inferred dimension - cannot coerce to fixed
                    return False
                elif from_dim != to_dim:
                    # Fixed dimensions must match exactly
                    return False

            # All checks passed - coercion allowed
            return True

        # ConcreteArrayType only coerces to identical ConcreteArrayType (handled by identity above)
        return False

    # ConcreteArrayType cannot coerce to HexenType
    if isinstance(from_type, ArrayType):
        return False

    # Standard HexenType coercion rules
    if not isinstance(from_type, HexenType) or not isinstance(to_type, HexenType):
        return False

    # comptime type coercion (ergonomic literals)
    if from_type == HexenType.COMPTIME_INT:
        return to_type in COMPTIME_INT_TARGETS

    if from_type == HexenType.COMPTIME_FLOAT:
        return to_type in COMPTIME_FLOAT_TARGETS

    # NO automatic widening for concrete types per TYPE_SYSTEM.md
    # All concrete conversions require explicit syntax: value:type
    return False


# resolve_comptime_type moved to ComptimeAnalyzer


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
    # Handle usize: usize + usize = usize (no implicit mixing with signed types)
    if left_type == HexenType.USIZE and right_type == HexenType.USIZE:
        return HexenType.USIZE
    # For signed integers, use standard widening
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


# is_mixed_type_operation moved to ComptimeAnalyzer


def is_string_type(type_: HexenType) -> bool:
    """Check if a type is a string type."""
    return type_ == HexenType.STRING


def is_boolean_type(type_: HexenType) -> bool:
    """Check if a type is a boolean type."""
    return type_ == HexenType.BOOL


def is_concrete_type(type_annotation: str) -> bool:
    """
    Check if a type annotation represents a concrete (non-comptime) type.

    Used in block evaluability detection to determine if variables with
    explicit type annotations should trigger runtime classification.

    Args:
        type_annotation: Type annotation string (e.g., "i32", "f64", "string")

    Returns:
        True if type is concrete, False if it's comptime
    """
    concrete_types = {"i32", "i64", "f32", "f64", "string", "bool", "void"}
    return type_annotation in concrete_types


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


def validate_literal_range(
    value: Union[int, float], target_type: HexenType, source_text: str = None
) -> None:
    """
    Validate literal fits in target type range per LITERAL_OVERFLOW_BEHAVIOR.md.

    Raises TypeError with detailed message if literal overflows target type range.
    This implements the compile-time safety guarantees specified in the documentation.

    Args:
        value: The literal value to check
        target_type: The target type to validate against
        source_text: Original literal text for error messages (e.g., "0xFF", "1e6")

    Raises:
        TypeError: If literal overflows target type range with detailed error message

    Returns:
        None if validation passes
    """
    if target_type not in TYPE_RANGES:
        return  # Unknown type, let other validation handle it

    min_val, max_val = TYPE_RANGES[target_type]

    if not (min_val <= value <= max_val):
        display_text = source_text or str(value)
        type_name = target_type.value

        # Format error message per LITERAL_OVERFLOW_BEHAVIOR.md specification
        if target_type in {HexenType.F32, HexenType.F64}:
            error_msg = (
                f"Literal {display_text} overflows {type_name} range\n"
                f"  Expected: approximately ±{max_val}\n"
                f"  Suggestion: Use explicit conversion if truncation is intended: {display_text}:{type_name}"
            )
        else:
            error_msg = (
                f"Literal {display_text} overflows {type_name} range\n"
                f"  Expected: {min_val} to {max_val}\n"
                f"  Suggestion: Use explicit conversion if truncation is intended: {display_text}:{type_name}"
            )

        raise TypeError(error_msg)


# validate_comptime_literal_coercion moved to ComptimeAnalyzer
# extract_literal_info moved to ComptimeAnalyzer


# =============================================================================
# ARRAY TYPE UTILITIES - Added for Task 5
# =============================================================================


def is_array_type(
    type_: Union[HexenType, ArrayType, ComptimeArrayType],
) -> bool:
    """
    Check if type represents an array (comptime or concrete).

    CHANGE (Phase 2): Extended to handle ComptimeArrayType instances.
    """
    # Handle ConcreteArrayType instances
    if isinstance(type_, ArrayType):
        return True
    # Handle ComptimeArrayType instances
    if isinstance(type_, ComptimeArrayType):
        return True
    # No old enum values - only class-based array types supported
    return False


# Legacy comptime array helper functions removed - use ComptimeArrayType class instead


def get_type_name_for_error(
    type_obj: Union[HexenType, ArrayType, ComptimeArrayType, RangeType, ComptimeRangeType],
) -> str:
    """
    Get a human-readable type name for error messages.

    CHANGE (Phase 2): Extended to handle ComptimeArrayType instances.
    CHANGE (Range System): Extended to handle RangeType and ComptimeRangeType.
    """
    if isinstance(type_obj, ArrayType):
        # ConcreteArrayType.dimensions is a list of integers, not ArrayDimension objects
        # Build dimension string: [2][3]i32 for 2D array
        dim_str = "".join(f"[{dim}]" for dim in type_obj.dimensions)
        return f"{dim_str}{type_obj.element_type.name.lower()}"

    # PHASE 2 ADDITION: Handle ComptimeArrayType
    if isinstance(type_obj, ComptimeArrayType):
        # Use ComptimeArrayType's __str__ method: comptime_[5]int
        return str(type_obj)

    # RANGE SYSTEM: Handle RangeType and ComptimeRangeType
    if isinstance(type_obj, (RangeType, ComptimeRangeType)):
        # Use RangeType's __str__ method for consistent formatting
        return str(type_obj)

    # Use the inverse mapping from TYPE_STRING_TO_HEXEN_TYPE for consistency
    return HEXEN_TYPE_TO_STRING.get(type_obj, "unknown")


# ============================================================================
# Range Type Utilities
# ============================================================================


def is_range_type(type_obj) -> bool:
    """Check if a type is a range type (concrete or comptime)"""
    return isinstance(type_obj, (RangeType, ComptimeRangeType))


def is_comptime_range(type_obj) -> bool:
    """Check if a type is a comptime range type"""
    return isinstance(type_obj, ComptimeRangeType)


def is_numeric_type(type_obj) -> bool:
    """
    Check if type is numeric (for range bounds/steps).

    Includes:
    - Concrete numeric types: i32, i64, f32, f64, usize
    - Comptime types: comptime_int, comptime_float
    """
    if isinstance(type_obj, HexenType):
        return type_obj in {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.USIZE,
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }
    return False


def can_convert_to_usize(type_obj) -> bool:
    """
    Check if type can convert to usize (for array indexing).

    Rules:
    - comptime_int → usize (implicit, ergonomic)
    - i32, i64 → usize (explicit conversion required)
    - f32, f64, comptime_float → NEVER (float indices forbidden)
    """
    if isinstance(type_obj, HexenType):
        # Comptime int adapts implicitly
        if type_obj == HexenType.COMPTIME_INT:
            return True

        # Integer types require explicit conversion
        if type_obj in {HexenType.I32, HexenType.I64}:
            return True

        # Float types CANNOT convert to usize
        if type_obj in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}:
            return False

    return False


def resolve_range_element_type(
    start_type,
    end_type,
    step_type,
    target_type=None,
) -> HexenType:
    """
    Resolve the element type of a range expression.

    Rules:
    1. All bounds (start, end, step) must have same type (after comptime adaptation)
    2. If target_type provided, comptime bounds adapt to it
    3. If no target, comptime types preserved (maximum flexibility)
    4. Concrete types must match exactly (no automatic conversion)

    Args:
        start_type: Type of start bound (None if unbounded)
        end_type: Type of end bound (None if unbounded)
        step_type: Type of step (None if no step)
        target_type: Optional target range type for context

    Returns:
        Resolved element type

    Raises:
        TypeError: If types are incompatible
    """
    # Collect all present bound types
    bound_types = []
    if start_type is not None:
        bound_types.append(("start", start_type))
    if end_type is not None:
        bound_types.append(("end", end_type))
    if step_type is not None:
        bound_types.append(("step", step_type))

    if not bound_types:
        # Fully unbounded range (..) - use target type if provided, otherwise default to comptime_int
        # This is valid for array slicing where context determines the type
        if target_type is not None:
            return target_type
        # Default to comptime_int for maximum flexibility
        return HexenType.COMPTIME_INT

    # If target type provided, use it for comptime adaptation
    if target_type is not None:
        # Verify all bounds can adapt to target
        for name, bound_type in bound_types:
            if not can_coerce(bound_type, target_type):
                raise TypeError(
                    f"Range {name} bound type {bound_type} cannot adapt to target {target_type}"
                )
        return target_type

    # No target type - resolve from bounds
    # If all bounds are comptime, preserve comptime flexibility
    all_comptime = all(
        bound_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}
        for _, bound_type in bound_types
    )

    if all_comptime:
        # Check for mixed comptime types
        has_int = any(bt == HexenType.COMPTIME_INT for _, bt in bound_types)
        has_float = any(bt == HexenType.COMPTIME_FLOAT for _, bt in bound_types)

        if has_int and has_float:
            # Mixed comptime_int + comptime_float → comptime_float
            return HexenType.COMPTIME_FLOAT
        elif has_float:
            return HexenType.COMPTIME_FLOAT
        else:
            return HexenType.COMPTIME_INT

    # At least one concrete type - all must match
    concrete_types = [
        bt
        for _, bt in bound_types
        if bt not in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}
    ]

    if not concrete_types:
        # Should be caught by all_comptime above
        raise ValueError("Unexpected: no concrete types but not all comptime")

    # Check all concrete types match
    first_concrete = concrete_types[0]
    if not all(ct == first_concrete for ct in concrete_types):
        raise TypeError(
            f"Range bounds have incompatible types: {[bt for _, bt in bound_types]}"
        )

    # Verify comptime bounds can adapt to concrete type
    for name, bound_type in bound_types:
        if bound_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            if not can_coerce(bound_type, first_concrete):
                raise TypeError(
                    f"Range {name} bound (comptime) cannot adapt to {first_concrete}"
                )

    return first_concrete
