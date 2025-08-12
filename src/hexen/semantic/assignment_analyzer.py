"""
Hexen Assignment Analyzer

Handles analysis of assignment statements including:
- Mutable variable assignment validation
- Type compatibility checking with coercion
- Precision loss detection and explicit conversion
- Symbol table integration (lookup, usage tracking, initialization)
- Explicit conversion support for precision loss operations
"""

from typing import Dict, Optional, Callable

from .types import HexenType, Mutability
from .type_util import (
    can_coerce,
    is_precision_loss_operation,
)


class AssignmentAnalyzer:
    """
    Analyzes assignment statements with comprehensive validation and coercion.

    Implements the "Explicit Danger, Implicit Safety" philosophy:
    - Safe assignments work seamlessly with implicit coercion
    - Dangerous assignments (precision loss) require explicit conversion
    - Clear error messages guide developers to correct syntax
    - Integration with symbol table for mutability and initialization tracking
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
        lookup_symbol_callback: Callable[[str], Optional[object]],
        comptime_analyzer,
        is_parameter_callback: Optional[Callable[[str], bool]] = None,
        get_parameter_info_callback: Optional[Callable[[str], Optional[object]]] = None,
    ):
        """
        Initialize the assignment analyzer.

        Args:
            error_callback: Function to call when semantic errors are found
            analyze_expression_callback: Function to analyze expressions
            lookup_symbol_callback: Function to lookup symbols in symbol table
            comptime_analyzer: ComptimeAnalyzer instance for comptime type operations
            is_parameter_callback: Function to check if a name is a parameter
            get_parameter_info_callback: Function to get parameter info
        """
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._lookup_symbol = lookup_symbol_callback
        self.comptime_analyzer = comptime_analyzer
        self._is_parameter = is_parameter_callback
        self._get_parameter_info = get_parameter_info_callback

    def analyze_assignment_statement(self, node: Dict) -> None:
        """
        Analyze an assignment statement with comprehensive validation and coercion.

        Assignment rules:
        - Target must be a declared variable
        - Target must be mutable (mut, not val)
        - Value type must be coercible to target type (using coercion)
        - Explicit conversions enable precision loss operations (value:type syntax)
        - Supports self-assignment (x = x)
        - No chained assignment (a = b = c)

        This validates our mutability system and type checking robustness with elegant coercion.
        """
        target_name = node.get("target")
        value = node.get("value")

        if not target_name:
            self._error("Assignment target missing", node)
            return

        if not value:
            self._error("Assignment value missing", node)
            return

        # Look up target variable in symbol table
        symbol = self._lookup_symbol(target_name)
        if not symbol:
            self._error(f"Undefined variable: '{target_name}'", node)
            return

        # Check mutability - only mut variables/parameters can be assigned to
        if symbol.mutability == Mutability.IMMUTABLE:
            # Check if this is a parameter for more specific error message
            if self._is_parameter and self._is_parameter(target_name):
                self._error(
                    f"Cannot reassign immutable parameter '{target_name}'. "
                    f"Parameters are immutable by default. Use 'mut {target_name}: {symbol.type.value}' for mutable parameters",
                    node,
                )
            else:
                self._error(
                    f"Cannot assign to immutable variable '{target_name}'. "
                    f"val variables can only be assigned once at declaration",
                    node,
                )
            return

        # Analyze the value expression with target type context
        value_type = self._analyze_expression(value, symbol.type)

        # Check type compatibility with coercion
        if value_type != HexenType.UNKNOWN:
            # Explicit conversions are handled in _analyze_expression using value:type syntax
            # If we get here without errors, either it's a safe operation or it was explicitly converted
            # For complex expressions (like binary operations), check what the natural type would be
            # without target type influence to detect precision loss scenarios
            if value.get("type") == "binary_operation":
                # Check if this might involve comptime types that could safely resolve
                # If so, skip the precision loss check to avoid false positives
                left = value.get("left", {})
                right = value.get("right", {})

                # Get operand types
                left_type = (
                    self._analyze_expression(left, symbol.type)
                    if left
                    else HexenType.UNKNOWN
                )
                right_type = (
                    self._analyze_expression(right, symbol.type)
                    if right
                    else HexenType.UNKNOWN
                )

                # If either operand is a comptime type that can coerce to target, this is likely safe
                has_comptime_operand = left_type in {
                    HexenType.COMPTIME_INT,
                    HexenType.COMPTIME_FLOAT,
                } or right_type in {
                    HexenType.COMPTIME_INT,
                    HexenType.COMPTIME_FLOAT,
                }

                # If we have comptime operands that can coerce to target type, skip precision loss check
                if has_comptime_operand:
                    if (
                        left_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}
                        and can_coerce(left_type, symbol.type)
                    ) or (
                        right_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}
                        and can_coerce(right_type, symbol.type)
                    ):
                        # Skip precision loss check - comptime types can safely adapt
                        pass
                    else:
                        # Proceed with precision loss check
                        self._check_precision_loss_in_binary_op(value, symbol, node)
                else:
                    # No comptime operands, but check if this is a safe mixed concrete operation
                    # If both operand types can coerce to target type, it's safe - skip precision loss check
                    if can_coerce(left_type, symbol.type) and can_coerce(
                        right_type, symbol.type
                    ):
                        # Both types can safely coerce to target - no precision loss check needed
                        pass
                    else:
                        # Proceed with precision loss check for truly problematic cases
                        self._check_precision_loss_in_binary_op(value, symbol, node)
            else:
                # For non-binary operations, use the existing logic
                # Check for precision loss operations that require explicit conversion
                if is_precision_loss_operation(value_type, symbol.type):
                    # Generate appropriate error message based on operation type
                    self._generate_precision_loss_error(value_type, symbol.type, node)
                    return

            # Check for literal overflow before type coercion
            if value_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
                literal_value, source_text = self.comptime_analyzer.extract_literal_info(value)
                if literal_value is not None:
                    try:
                        self.comptime_analyzer.validate_comptime_literal_coercion(
                            literal_value, value_type, symbol.type, source_text
                        )
                    except TypeError as e:
                        self._error(str(e), node)
                        return

            # Check type compatibility with coercion for non-precision-loss cases
            if not can_coerce(value_type, symbol.type):
                # Resolve comptime types for better error messages
                display_value_type = self.comptime_analyzer.resolve_comptime_type(
                    value_type, HexenType.UNKNOWN
                )
                self._error(
                    f"Type mismatch in assignment: variable '{target_name}' is {symbol.type.value}, "
                    f"but assigned value is {display_value_type.value}",
                    node,
                )
                return

        # Mark the symbol as used (assignment counts as usage)
        symbol.used = True

        # Mark the symbol as initialized (assignment initializes uninitialized variables)
        symbol.initialized = True

    def _check_precision_loss_in_binary_op(self, value, symbol, node):
        """Helper method to check precision loss in binary operations."""
        # Analyze the expression without target context to get its natural type
        natural_type = self._analyze_expression(value, None)

        # If the natural type is different and would cause precision loss, require explicit conversion
        if (
            natural_type != HexenType.UNKNOWN
            and natural_type != symbol.type
            and is_precision_loss_operation(natural_type, symbol.type)
        ):
            # Generate appropriate error message based on operation type
            self._generate_precision_loss_error(natural_type, symbol.type, node)
            return

    def _generate_precision_loss_error(
        self, from_type: HexenType, to_type: HexenType, node: Dict
    ):
        """Generate appropriate precision loss error message based on operation type."""
        if from_type == HexenType.I64 and to_type == HexenType.I32:
            self._error(
                "Potential truncation. Use explicit conversion: 'value:i32'",
                node,
            )
        elif from_type == HexenType.F64 and to_type == HexenType.F32:
            self._error(
                "Potential precision loss. Use explicit conversion: 'value:f32'",
                node,
            )
        elif from_type in {
            HexenType.F32,
            HexenType.F64,
            HexenType.COMPTIME_FLOAT,
        } and to_type in {HexenType.I32, HexenType.I64}:
            # Float to integer conversion - use "truncation" terminology
            self._error(
                f"Potential truncation. Use explicit conversion: 'value:{to_type.value}'",
                node,
            )
        elif from_type == HexenType.I64 and to_type == HexenType.F32:
            self._error(
                "Potential precision loss. Use explicit conversion: 'value:f32'",
                node,
            )
        else:
            # Generic precision loss message
            self._error(
                f"Potential precision loss. Use explicit conversion: 'value:{to_type.value}'",
                node,
            )
