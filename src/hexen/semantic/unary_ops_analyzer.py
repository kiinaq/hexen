"""
Hexen Unary Operations Analyzer

Handles analysis of unary operations including:
- Unary minus (-) for numeric values
- Logical not (!) for boolean values
- Type coercion and comptime type adaptation
"""

from typing import Dict, Optional, Callable

from .types import HexenType
from .type_util import (
    is_numeric_type,
)


class UnaryOpsAnalyzer:
    """
    Analyzes unary operations with context-guided type resolution.

    Implements the "Pedantic to write, but really easy to read" philosophy:
    - Explicit type requirements for mixed operations
    - Transparent cost model through result types
    - Comptime type adaptation with context guidance
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
    ):
        """
        Initialize the unary operations analyzer.

        Args:
            error_callback: Function to call when semantic errors are found
                          (typically SemanticAnalyzer._error)
            analyze_expression_callback: Function to analyze expressions
                                      (typically SemanticAnalyzer._analyze_expression)
        """
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback

    def analyze_unary_operation(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a unary operation with context-guided type resolution.

        Args:
            node: Unary operation AST node
            target_type: Optional target type for context-guided resolution

        Returns:
            The resolved type of the operation
        """
        operator = node.get("operator")
        operand = node.get("operand")

        if not operator or not operand:
            self._error("Invalid unary operation", node)
            return HexenType.UNKNOWN

        # Analyze operand with context
        operand_type = self._analyze_expression(operand, target_type)

        if operand_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Handle unary minus (-)
        if operator == "-":
            # Only allow unary minus on numeric types
            if not is_numeric_type(operand_type):
                self._error(
                    f"Unary minus (-) requires numeric operand, got {operand_type.value}",
                    node,
                )
                return HexenType.UNKNOWN

            # For comptime types, preserve them
            if operand_type == HexenType.COMPTIME_INT:
                return HexenType.COMPTIME_INT
            if operand_type == HexenType.COMPTIME_FLOAT:
                return HexenType.COMPTIME_FLOAT

            # For concrete types, return the same type
            return operand_type

        # Handle logical not (!)
        elif operator == "!":
            if operand_type != HexenType.BOOL:
                self._error(
                    f"Logical not (!) requires boolean operand, got {operand_type.value}",
                    node,
                )
                return HexenType.UNKNOWN
            return HexenType.BOOL

        else:
            self._error(f"Unknown unary operator: {operator}", node)
            return HexenType.UNKNOWN
