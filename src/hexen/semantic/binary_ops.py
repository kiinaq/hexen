"""
Hexen Binary Operations Analyzer

Handles analysis of binary operations including:
- Arithmetic operations (+, -, *, /, \)
- Type coercion and comptime type adaptation
- Division operator specific rules (/ vs \)
- Mixed type operations with explicit type requirements
"""

from typing import Dict, Optional, Callable

from .types import HexenType
from .type_util import (
    is_numeric_type,
    is_float_type,
    resolve_comptime_type,
    to_float_type,
    to_integer_type,
    get_wider_type,
    is_mixed_type_operation,
)


class BinaryOpsAnalyzer:
    """
    Analyzes binary operations with context-guided type resolution.

    Implements the "Pedantic to write, but really easy to read" philosophy:
    - Explicit type requirements for mixed operations
    - Clear division operator semantics (/ vs \)
    - Transparent cost model through result types
    - Comptime type adaptation with context guidance
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
    ):
        """
        Initialize the binary operations analyzer.

        Args:
            error_callback: Function to call when semantic errors are found
                          (typically SemanticAnalyzer._error)
            analyze_expression_callback: Function to analyze expressions
                                      (typically SemanticAnalyzer._analyze_expression)
        """
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback

    def analyze_binary_operation(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a binary operation with context-guided type resolution.

        Args:
            node: Binary operation AST node
            target_type: Optional target type for context-guided resolution

        Returns:
            The resolved type of the operation
        """
        operator = node.get("operator")
        left = node.get("left")
        right = node.get("right")

        if not operator or not left or not right:
            self._error("Invalid binary operation", node)
            return HexenType.UNKNOWN

        # Analyze operands with context
        left_type = self._analyze_expression(left, target_type)
        right_type = self._analyze_expression(right, target_type)

        if left_type == HexenType.UNKNOWN or right_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Handle division operators specifically
        if operator in ["/", "\\"]:
            return self._analyze_division_operation(
                operator, left_type, right_type, node
            )

        # For mixed type operations, require explicit type annotation
        if is_mixed_type_operation(left_type, right_type):
            if not target_type:
                self._error(
                    "Mixed type operations require explicit type annotation", node
                )
                return HexenType.UNKNOWN

        # For other arithmetic operations, use standard type resolution
        return self._resolve_binary_operation_type(
            operator, left_type, right_type, target_type
        )

    def _analyze_division_operation(
        self, operator: str, left_type: HexenType, right_type: HexenType, node: Dict
    ) -> HexenType:
        """
        Analyze division operations with specific rules for / and \.

        Rules:
        - / (float division): Always produces float result
        - \ (integer division): Always produces integer result
        - Both require numeric operands
        - Both support comptime type adaptation
        """
        # Check for non-numeric operands
        if not is_numeric_type(left_type) or not is_numeric_type(right_type):
            self._error(
                f"Division operator '{operator}' requires numeric operands, got {left_type.value} and {right_type.value}",
                node,
            )
            return HexenType.UNKNOWN

        # Handle float division (/)
        if operator == "/":
            return self._analyze_float_division(left_type, right_type)

        # Handle integer division (\)
        else:  # operator == "\\"
            return self._analyze_integer_division(left_type, right_type, node)

    def _analyze_float_division(
        self, left_type: HexenType, right_type: HexenType
    ) -> HexenType:
        """Analyze float division operation."""
        # Convert operands to float types
        left_float = to_float_type(left_type)
        right_float = to_float_type(right_type)

        # Result is the wider of the two float types
        return get_wider_type(left_float, right_float)

    def _analyze_integer_division(
        self, left_type: HexenType, right_type: HexenType, node: Dict
    ) -> HexenType:
        """Analyze integer division operation."""
        # Check for float operands
        if is_float_type(left_type) or is_float_type(right_type):
            self._error(
                "Integer division (\\\\) cannot be used with float operands", node
            )
            return HexenType.UNKNOWN

        # Convert comptime types to concrete integer types
        left_int = to_integer_type(left_type)
        right_int = to_integer_type(right_type)

        # Result is the wider of the two integer types
        return get_wider_type(left_int, right_int)

    def _resolve_binary_operation_type(
        self,
        operator: str,
        left_type: HexenType,
        right_type: HexenType,
        target_type: Optional[HexenType],
    ) -> HexenType:
        """
        Resolve the result type of a binary operation with context guidance.

        Handles:
        - Type coercion and widening
        - Comptime type adaptation
        - Context-guided resolution
        """
        # Handle comptime types first
        left_type = resolve_comptime_type(left_type, target_type)
        right_type = resolve_comptime_type(right_type, target_type)

        # For non-comptime types, use standard type resolution
        if operator in ["+", "-", "*"]:
            # Arithmetic operations
            return get_wider_type(left_type, right_type)

        return HexenType.UNKNOWN

    def _analyze_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze an expression by delegating to the provided callback.

        This is a wrapper around the main analyzer's _analyze_expression method.
        """
        return self._analyze_expression(node, target_type)
