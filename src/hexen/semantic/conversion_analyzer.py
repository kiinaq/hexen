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

from typing import Dict, Optional, Callable

from .types import HexenType
from .type_util import parse_type


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
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback

    def analyze_conversion(
        self, node: Dict, context: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze explicit conversion expressions following TYPE_SYSTEM.md rules.

        Args:
            node: EXPLICIT_CONVERSION_EXPRESSION AST node with 'expression' and 'target_type'
            context: Optional context type (not used for conversions - they specify their own target)

        Returns:
            Target type if conversion is valid, HexenType.UNKNOWN if invalid

        Implementation follows TYPE_SYSTEM.md Quick Reference Table exactly.
        """
        # Extract source expression and target type
        source_expr = node.get("expression")
        target_type_str = node.get("target_type")

        if not source_expr or not target_type_str:
            self._error(
                "Invalid conversion expression: missing expression or target type", node
            )
            return HexenType.UNKNOWN

        # Parse target type
        target_type = parse_type(target_type_str)
        if target_type == HexenType.UNKNOWN:
            self._error(f"Invalid target type: {target_type_str}", node)
            return HexenType.UNKNOWN

        # Analyze source expression (no context - conversions are explicit about their intent)
        source_type = self._analyze_expression(source_expr, target_type=None)
        if source_type == HexenType.UNKNOWN:
            # Source expression analysis failed - propagate error
            return HexenType.UNKNOWN

        # Validate conversion per TYPE_SYSTEM.md rules
        if self._is_valid_conversion(source_type, target_type):
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
