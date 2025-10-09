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
from .types import HexenType, ConcreteArrayType


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
        parse_array_type_callback: Optional[Callable[[Dict], ConcreteArrayType]] = None,
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._parse_array_type = parse_array_type_callback

    def analyze_conversion(
        self, node: Dict, context: Optional[HexenType] = None
    ) -> Union[HexenType, ConcreteArrayType]:
        """
        Analyze explicit conversion expressions following TYPE_SYSTEM.md rules.

        Args:
            node: EXPLICIT_CONVERSION_EXPRESSION AST node with 'expression' and 'target_type'
            context: Optional context type (not used for conversions - they specify their own target)

        Returns:
            Target type if conversion is valid, HexenType.UNKNOWN if invalid

        Implementation follows TYPE_SYSTEM.md Quick Reference Table exactly.
        Extends to handle array type conversions per ARRAY_IMPLEMENTATION_PLAN.md.
        """
        # Extract source expression and target type
        source_expr = node.get("expression")
        target_type_spec = node.get("target_type")

        if not source_expr or not target_type_spec:
            self._error(
                "Invalid conversion expression: missing expression or target type", node
            )
            return HexenType.UNKNOWN

        # Parse target type - can be string (scalar) or dict (array type)
        target_type = self._parse_target_type(target_type_spec, node)
        if target_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Analyze source expression (no context - conversions are explicit about their intent)
        source_type = self._analyze_expression(source_expr, target_type=None)
        if source_type == HexenType.UNKNOWN:
            # Source expression analysis failed - propagate error
            return HexenType.UNKNOWN

        # Validate conversion per TYPE_SYSTEM.md rules (scalars) or ARRAY_IMPLEMENTATION_PLAN.md (arrays)
        if isinstance(target_type, ConcreteArrayType) and isinstance(source_type, ConcreteArrayType):
            # Array-to-array conversion
            if self._is_valid_array_conversion(source_type, target_type, node):
                return target_type
            else:
                # Error already reported in _is_valid_array_conversion
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
        - comptime_int → i32, i64, f32, f64 (implicit, no cost)
        - comptime_float → f32, f64 (implicit, no cost)
        - comptime_float → i32, i64 (explicit conversion required - this function)

        🔧 Concrete Types (All Explicit):
        - Any concrete → any other concrete type (explicit conversion - this function)

        ❌ Forbidden Conversions:
        - Any numeric → bool (use explicit comparison: (value != 0))
        - Any numeric → string (use string formatting functions)
        - bool → Any numeric (use conditional expression)
        - string → Any numeric (use parsing functions)
        """
        # Identity conversion always valid
        if source == target:
            return True

        # Comptime type conversions (following TYPE_SYSTEM.md table)
        if source == HexenType.COMPTIME_INT:
            # comptime_int can convert to any numeric type
            return target in [
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
            ]
        elif source == HexenType.COMPTIME_FLOAT:
            # comptime_float can convert to any numeric type
            return target in [
                HexenType.I32,  # Explicit conversion (data loss)
                HexenType.I64,  # Explicit conversion (data loss)
                HexenType.F32,
                HexenType.F64,
            ]

        # Concrete type conversions (all explicit per TYPE_SYSTEM.md)
        numeric_types = {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
        }

        if source in numeric_types and target in numeric_types:
            # All numeric → numeric conversions are valid with explicit syntax
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
        # Forbidden conversion patterns with guidance
        if target == HexenType.BOOL:
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
    ) -> Union[HexenType, ConcreteArrayType]:
        """
        Parse target type specification - handles both scalar strings and array type dicts.

        Args:
            target_type_spec: Either string ("i32") or dict (array type AST node)
            node: AST node for error reporting

        Returns:
            Parsed type (HexenType or ConcreteArrayType), or HexenType.UNKNOWN if invalid
        """
        # Handle scalar types (string)
        if isinstance(target_type_spec, str):
            target_type = parse_type(target_type_spec)
            if target_type == HexenType.UNKNOWN:
                self._error(f"Invalid target type: {target_type_spec}", node)
            return target_type

        # Handle array types (dict)
        if isinstance(target_type_spec, dict) and self._parse_array_type:
            return self._parse_array_type(target_type_spec)

        # Unknown format
        self._error(f"Invalid target type specification format", node)
        return HexenType.UNKNOWN

    def _is_valid_array_conversion(
        self, source: ConcreteArrayType, target: ConcreteArrayType, node: Dict
    ) -> bool:
        """
        Validate array-to-array conversion per ARRAY_IMPLEMENTATION_PLAN.md.

        Conversion Rules:
        1. Size compatibility FIRST (fixed sizes must match exactly, inferred accepts any)
        2. Element type conversion (can change with explicit :type)
        3. Dimension conversion/flattening (can flatten with size match)

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
        self, source: ConcreteArrayType, target: ConcreteArrayType, node: Dict
    ) -> bool:
        """
        Validate array size compatibility per ARRAY_IMPLEMENTATION_PLAN.md.

        Rules:
        - Inferred-size target [_]T: Always accepts any size (wildcard match)
        - Fixed-size target [N]T: Source size must match exactly

        For flattening (dimension count change):
        - Calculate total element count and verify match

        Args:
            source: Source array type
            target: Target array type
            node: AST node for error reporting

        Returns:
            True if sizes are compatible, False otherwise (with error reported)
        """
        # Calculate source total element count
        source_total_size = 1
        for dim in source.dimensions:
            if dim == "_":
                self._error(
                    f"Cannot perform explicit conversion on array with inferred source dimensions\n"
                    f"Source array must have concrete dimensions for explicit type conversion\n"
                    f"Inferred dimensions are only valid as conversion targets",
                    node,
                )
                return False
            source_total_size *= dim

        # Check each target dimension
        target_total_size = 1
        for i, target_dim in enumerate(target.dimensions):
            if target_dim == "_":
                # Inferred dimension - wildcard accepts any size
                # Infer the size from source (for this dimension)
                if i < len(source.dimensions):
                    # Use source dimension size
                    target.dimensions[i] = source.dimensions[i]
                    target_total_size *= source.dimensions[i]
                else:
                    # Flattening case - calculate remaining size
                    remaining_source_dims = source.dimensions[i:]
                    remaining_size = 1
                    for dim in remaining_source_dims:
                        remaining_size *= dim
                    target.dimensions[i] = remaining_size
                    target_total_size *= remaining_size
            else:
                # Fixed dimension - must match exactly (after flattening)
                target_total_size *= target_dim

        # For dimension changes (flattening), verify calculated sizes match
        if len(source.dimensions) != len(target.dimensions):
            # Flattening or expansion - sizes must match
            if source_total_size != target_total_size:
                self._error(
                    f"Array size mismatch in dimension conversion\n"
                    f"Source: {self._format_array_type(source)} ({source_total_size} elements total: {' × '.join(map(str, source.dimensions))})\n"
                    f"Target: {self._format_array_type(target)} ({target_total_size} elements)\n"
                    f"Dimension conversion requires exact size match (cannot resize arrays)\n"
                    f"For flattening: calculated size must match (e.g., [2][3] → [6])",
                    node,
                )
                return False
        else:
            # Same dimension count - each dimension must match (or be inferred)
            for i, (source_dim, target_dim) in enumerate(
                zip(source.dimensions, target.dimensions)
            ):
                if target_dim != "_" and source_dim != target_dim:
                    self._error(
                        f"Array size mismatch in type conversion\n"
                        f"Source: {self._format_array_type(source)}\n"
                        f"Target: {self._format_array_type(target)}\n"
                        f"Dimension {i} mismatch: source has size {source_dim}, target expects {target_dim}\n"
                        f"Fixed-size dimensions must match exactly (cannot resize arrays through conversion)",
                        node,
                    )
                    return False

        return True

    def _format_array_type(self, array_type: ConcreteArrayType) -> str:
        """Format array type for error messages."""
        dims_str = "".join(f"[{dim}]" for dim in array_type.dimensions)
        return f"{dims_str}{array_type.element_type.name.lower()}"
