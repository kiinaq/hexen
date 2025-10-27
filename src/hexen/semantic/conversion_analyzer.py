"""
Explicit Conversion Analysis for Hexen Language

Implements semantic analysis for explicit type conversions (`value:type` syntax)
following the TYPE_SYSTEM.md conversion rules.

This analyzer handles:
- Validation of conversion compatibility per TYPE_SYSTEM.md Quick Reference Table
- Clear error messages for invalid conversions
- Integration with the comptime type system
- Cost transparency for all concrete type conversions
"""

from typing import Dict, Optional, Callable, Union

from .type_util import parse_type
from .types import HexenType, ArrayType, RangeType, ComptimeRangeType


class ConversionAnalyzer:
    """
    Specialized analyzer for explicit conversion expressions (`value:type`).

    Implements the TYPE_SYSTEM.md conversion rules:
    - ✅ Preserved: Comptime types stay flexible
    - ✅ Implicit: Comptime → compatible concrete (ergonomic)
    - 🔧 Explicit: All concrete conversions (transparent costs)
    - ❌ Forbidden: Invalid conversions (with clear guidance)
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
        parse_array_type_callback: Optional[Callable[[Dict], ArrayType]] = None,
        parse_range_type_callback: Optional[Callable[[Dict], RangeType]] = None,
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._parse_array_type = parse_array_type_callback
        self._parse_range_type = parse_range_type_callback

    def analyze_conversion(
        self, node: Dict, context: Optional[HexenType] = None
    ) -> Union[HexenType, ArrayType, RangeType]:
        """
        Analyze explicit conversion expressions following TYPE_SYSTEM.md rules.

        Args:
            node: EXPLICIT_CONVERSION_EXPRESSION AST node with 'expression' and 'target_type'
            context: Optional context type (not used for conversions - they specify their own target)

        Returns:
            Target type if conversion is valid, HexenType.UNKNOWN if invalid

        Implementation follows TYPE_SYSTEM.md Quick Reference Table exactly.
        Extends to handle:
        - Array type conversions per ARRAY_IMPLEMENTATION_PLAN.md
        - Range type conversions per RANGE_SYSTEM_SEMANTIC_IMPLEMENTATION_PLAN.md
        """
        # Extract source expression and target type
        source_expr = node.get("expression")
        target_type_spec = node.get("target_type")

        if not source_expr or not target_type_spec:
            self._error(
                "Invalid conversion expression: missing expression or target type", node
            )
            return HexenType.UNKNOWN

        # Parse target type - can be string (scalar), dict (array type), or range type
        target_type = self._parse_target_type(target_type_spec, node)
        if target_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Analyze source expression (no context - conversions are explicit about their intent)
        source_type = self._analyze_expression(source_expr, target_type=None)
        if source_type == HexenType.UNKNOWN:
            # Source expression analysis failed - propagate error
            return HexenType.UNKNOWN

        # Validate conversion per TYPE_SYSTEM.md rules (scalars), ARRAY_IMPLEMENTATION_PLAN.md (arrays),
        # or RANGE_SYSTEM_SEMANTIC_IMPLEMENTATION_PLAN.md (ranges)
        if isinstance(target_type, ArrayType) and isinstance(
            source_type, ArrayType
        ):
            # Array-to-array conversion
            if self._is_valid_array_conversion(source_type, target_type, node):
                return target_type
            else:
                # Error already reported in _is_valid_array_conversion
                return HexenType.UNKNOWN
        elif isinstance(target_type, RangeType) and isinstance(
            source_type, (RangeType, ComptimeRangeType)
        ):
            # Range-to-range conversion
            if self._is_valid_range_conversion(source_type, target_type, node):
                return target_type
            else:
                # Error already reported in _is_valid_range_conversion
                return HexenType.UNKNOWN
        elif self._is_valid_conversion(source_type, target_type):
            # Scalar conversion
            return target_type
        else:
            self._report_conversion_error(source_type, target_type, node)
            return HexenType.UNKNOWN

    def _is_valid_conversion(self, source: HexenType, target: HexenType) -> bool:
        """
        Check if conversion is valid per TYPE_SYSTEM.md Quick Reference Table.

        Conversion Rules:
        ✅ Comptime Types (Ergonomic Literals):
        - comptime_int → i32, i64, f32, f64, usize (implicit, no cost)
        - comptime_float → f32, f64 (implicit, no cost)
        - comptime_float → i32, i64 (explicit conversion required - this function)

        🔧 Concrete Types (All Explicit):
        - Any concrete → any other concrete type (explicit conversion - this function)
        - i32, i64 → usize (explicit conversion required)
        - usize → i32, i64, f32, f64 (explicit conversion required)

        ❌ Forbidden Conversions:
        - Any numeric → bool (use explicit comparison: (value != 0))
        - Any numeric → string (use string formatting functions)
        - bool → Any numeric (use conditional expression)
        - string → Any numeric (use parsing functions)
        - f32, f64, comptime_float → usize (float indices forbidden)
        """
        # Identity conversion always valid
        if source == target:
            return True

        # Comptime type conversions (following TYPE_SYSTEM.md table)
        if source == HexenType.COMPTIME_INT:
            # comptime_int can convert to any numeric type (including usize)
            return target in [
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
                HexenType.USIZE,  # NEW: comptime_int → usize (ergonomic!)
            ]
        elif source == HexenType.COMPTIME_FLOAT:
            # comptime_float can convert to numeric types EXCEPT usize
            return target in [
                HexenType.I32,  # Explicit conversion (data loss)
                HexenType.I64,  # Explicit conversion (data loss)
                HexenType.F32,
                HexenType.F64,
                # NOTE: usize NOT included - float → usize forbidden
            ]

        # Concrete type conversions (all explicit per TYPE_SYSTEM.md)
        numeric_types = {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.USIZE,  # NEW: usize in numeric types
        }

        if source in numeric_types and target in numeric_types:
            # VALIDATION: Float → usize conversion forbidden
            if source in {HexenType.F32, HexenType.F64} and target == HexenType.USIZE:
                return False  # Forbidden: float → usize
            # All other numeric → numeric conversions valid with explicit syntax
            return True

        # Forbidden conversions per TYPE_SYSTEM.md
        return False

    def _report_conversion_error(
        self, source: HexenType, target: HexenType, node: Dict
    ) -> None:
        """
        Report conversion error with clear guidance following TYPE_SYSTEM.md patterns.

        Provides specific guidance for different error types:
        - Forbidden conversions suggest alternative approaches
        - Invalid comptime conversions clarify which are allowed
        """
        # NEW: Float → usize conversion (forbidden)
        if target == HexenType.USIZE and source in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}:
            self._error(
                f"Cannot convert {source.value} to usize. "
                f"Float types cannot be used for array indexing (fractional indices are meaningless). "
                f"Use integer types for indexing instead",
                node,
            )
        # Forbidden conversion patterns with guidance
        elif target == HexenType.BOOL:
            self._error(
                f"Cannot convert {source.value} to bool. "
                f"Use explicit comparison instead: (value != 0) for numeric types, "
                f'(value != "") for strings',
                node,
            )
        elif target == HexenType.STRING:
            self._error(
                f"Cannot convert {source.value} to string. "
                f"Use string formatting functions instead",
                node,
            )
        elif source == HexenType.BOOL and target != HexenType.BOOL:
            self._error(
                f"Cannot convert bool to {target.value}. "
                f"Use conditional expression instead: bool_val ? 1 : 0",
                node,
            )
        elif source == HexenType.STRING:
            if target == HexenType.BOOL:
                self._error(
                    "Cannot convert string to bool. "
                    'Use explicit comparison instead: (value != "")',
                    node,
                )
            else:
                self._error(
                    f"Cannot convert string to {target.value}. "
                    f"Use parsing functions instead",
                    node,
                )
        else:
            # Generic conversion error
            self._error(
                f"Invalid conversion from {source.value} to {target.value}. "
                f"Check TYPE_SYSTEM.md for supported conversions",
                node,
            )

    def _parse_target_type(
        self, target_type_spec: Union[str, Dict], node: Dict
    ) -> Union[HexenType, ArrayType, RangeType]:
        """
        Parse target type specification - handles scalar strings, array types, and range types.

        Args:
            target_type_spec: Either string ("i32") or dict (array/range type AST node)
            node: AST node for error reporting

        Returns:
            Parsed type (HexenType, ConcreteArrayType, or RangeType), or HexenType.UNKNOWN if invalid
        """
        # Handle scalar types (string)
        if isinstance(target_type_spec, str):
            target_type = parse_type(target_type_spec)
            if target_type == HexenType.UNKNOWN:
                self._error(f"Invalid target type: {target_type_spec}", node)
            return target_type

        # Handle dict types (array or range)
        if isinstance(target_type_spec, dict):
            # Check if it's a range type
            if target_type_spec.get("type") == "range_type" and self._parse_range_type:
                return self._parse_range_type(target_type_spec)
            # Otherwise try array type
            elif self._parse_array_type:
                return self._parse_array_type(target_type_spec)

        # Unknown format
        self._error(f"Invalid target type specification format", node)
        return HexenType.UNKNOWN

    def _is_valid_array_conversion(
        self, source: ArrayType, target: ArrayType, node: Dict
    ) -> bool:
        """
        Validate array-to-array conversion per ARRAY_IMPLEMENTATION_PLAN.md.

        Conversion Rules:
        1. Dimension count must match exactly (no dimension transformations)
        2. Size compatibility (fixed sizes must match exactly, inferred accepts any)
        3. Element type conversion (can change with explicit :type)

        Args:
            source: Source array type
            target: Target array type
            node: AST node for error reporting

        Returns:
            True if conversion is valid, False otherwise (with error reported)
        """
        # Step 1: Size Compatibility Validation
        if not self._validate_array_size_compatibility(source, target, node):
            return False

        # Step 2: Element Type Compatibility
        # Element types must be compatible (same or convertible)
        if source.element_type != target.element_type:
            # Check if element type conversion is valid
            if not self._is_valid_conversion(source.element_type, target.element_type):
                self._error(
                    f"Invalid element type conversion in array conversion\n"
                    f"Cannot convert element type {source.element_type.name.lower()} "
                    f"to {target.element_type.name.lower()}\n"
                    f"Element type conversion must be valid per TYPE_SYSTEM.md rules",
                    node,
                )
                return False

        # All validations passed
        return True

    def _validate_array_size_compatibility(
        self, source: ArrayType, target: ArrayType, node: Dict
    ) -> bool:
        """
        Validate array size compatibility per ARRAY_IMPLEMENTATION_PLAN.md.

        Rules:
        - Dimension count must match exactly (source and target must have same number of dimensions)
        - Inferred-size target [_]T: Always accepts any size (wildcard match)
        - Fixed-size target [N]T: Source size must match exactly

        Args:
            source: Source array type
            target: Target array type
            node: AST node for error reporting

        Returns:
            True if sizes are compatible, False otherwise (with error reported)
        """
        # Require exact dimension match for array conversions
        if len(source.dimensions) != len(target.dimensions):
            self._error(
                f"Array dimension mismatch: cannot convert {self._format_array_type(source)} to {self._format_array_type(target)}\n"
                f"Array conversions require matching dimensions\n"
                f"For dimension transformations, use the standard library",
                node,
            )
            return False

        # Validate source dimensions are concrete
        for dim in source.dimensions:
            if dim == "_":
                self._error(
                    f"Cannot perform explicit conversion on array with inferred source dimensions\n"
                    f"Source array must have concrete dimensions for explicit type conversion\n"
                    f"Inferred dimensions are only valid as conversion targets",
                    node,
                )
                return False

        # Validate each dimension matches (with [_] inference support)
        for i, (src_dim, tgt_dim) in enumerate(
            zip(source.dimensions, target.dimensions)
        ):
            if tgt_dim == "_":  # Inferred dimension [_]
                # Accept any source dimension size and infer target size
                target.dimensions[i] = src_dim
                continue
            if src_dim != tgt_dim:
                self._error(
                    f"Array dimension size mismatch: expected [{tgt_dim}], got [{src_dim}]",
                    node,
                )
                return False

        return True

    def _format_array_type(self, array_type: ArrayType) -> str:
        """Format array type for error messages."""
        dims_str = "".join(f"[{dim}]" for dim in array_type.dimensions)
        return f"{dims_str}{array_type.element_type.name.lower()}"

    def _is_valid_range_conversion(
        self,
        source: Union[RangeType, ComptimeRangeType],
        target: RangeType,
        node: Dict,
    ) -> bool:
        """
        Validate range type conversion per RANGE_SYSTEM_SEMANTIC_IMPLEMENTATION_PLAN.md.

        Conversion Rules:
        1. Comptime range adaptation:
           - comptime_int range → any integer range type (implicit)
           - comptime_float range → float range types only (NOT usize)

        2. Concrete range conversions:
           - i32/i64 range → usize range (explicit :range[usize])
           - float range → usize range (FORBIDDEN)

        3. Element type conversion must be valid per _is_valid_conversion rules

        Args:
            source: Source range type (RangeType or ComptimeRangeType)
            target: Target range type
            node: AST node for error reporting

        Returns:
            True if conversion is valid, False otherwise (with error reported)
        """
        from_elem = source.element_type
        to_elem = target.element_type

        # Comptime range adaptation
        if isinstance(source, ComptimeRangeType):
            if source.can_adapt_to(to_elem):
                return True

            # Comptime float trying to convert to usize
            if from_elem == HexenType.COMPTIME_FLOAT and to_elem == HexenType.USIZE:
                self._error(
                    "Cannot convert range[comptime_float] to range[usize]\n"
                    "Float ranges cannot be used for array indexing\n"
                    "Use integer range for indexing",
                    node,
                )
                return False

        # Concrete range conversions
        # Integer ranges can convert to usize
        if from_elem in {HexenType.I32, HexenType.I64} and to_elem == HexenType.USIZE:
            return True  # Explicit :range[usize] required

        # Float ranges CANNOT convert to usize
        if from_elem in {HexenType.F32, HexenType.F64} and to_elem == HexenType.USIZE:
            self._error(
                f"Cannot convert range[{from_elem.value}] to range[usize]\n"
                f"Float types cannot convert to usize (fractional indices meaningless)\n"
                f"Float ranges are for iteration only, not array indexing",
                node,
            )
            return False

        # All other conversions follow standard type conversion rules
        return self._is_valid_conversion(from_elem, to_elem)
