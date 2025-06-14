"""
Hexen Binary Operations Analyzer

Handles analysis of binary operations including:
- Arithmetic operations (+, -, *, /, \)
- Type coercion and comptime type adaptation
- Division operator specific rules (/ vs \)
- Mixed type operations with explicit type requirements
"""

from typing import Dict, Optional

from .types import HexenType


class BinaryOpsAnalyzer:
    """
    Analyzes binary operations with context-guided type resolution.

    Implements the "Pedantic to write, but really easy to read" philosophy:
    - Explicit type requirements for mixed operations
    - Clear division operator semantics (/ vs \)
    - Transparent cost model through result types
    - Comptime type adaptation with context guidance
    """

    def __init__(self, error_callback):
        """
        Initialize the binary operations analyzer.

        Args:
            error_callback: Function to call when semantic errors are found
                          (typically SemanticAnalyzer._error)
        """
        self._error = error_callback

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
        if self._is_mixed_type_operation(left_type, right_type):
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
        if not self._is_numeric_type(left_type) or not self._is_numeric_type(
            right_type
        ):
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
        left_float = self._to_float_type(left_type)
        right_float = self._to_float_type(right_type)

        # Result is the wider of the two float types
        return (
            HexenType.F64
            if HexenType.F64 in {left_float, right_float}
            else HexenType.F32
        )

    def _analyze_integer_division(
        self, left_type: HexenType, right_type: HexenType, node: Dict
    ) -> HexenType:
        """Analyze integer division operation."""
        # Check for float operands
        if self._is_float_type(left_type) or self._is_float_type(right_type):
            self._error(
                "Integer division (\\\\) cannot be used with float operands", node
            )
            return HexenType.UNKNOWN

        # Convert comptime types to concrete integer types
        left_int = self._to_integer_type(left_type)
        right_int = self._to_integer_type(right_type)

        # Result is the wider of the two integer types
        return (
            HexenType.I64 if HexenType.I64 in {left_int, right_int} else HexenType.I32
        )

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
        left_type = self._resolve_comptime_type(left_type, target_type)
        right_type = self._resolve_comptime_type(right_type, target_type)

        # For non-comptime types, use standard type resolution
        if operator in ["+", "-", "*"]:
            # Arithmetic operations
            if self._is_float_type(left_type) or self._is_float_type(right_type):
                # If either operand is float, result is float
                return (
                    HexenType.F64
                    if HexenType.F64 in {left_type, right_type}
                    else HexenType.F32
                )
            else:
                # Both operands are integers
                return (
                    HexenType.I64
                    if HexenType.I64 in {left_type, right_type}
                    else HexenType.I32
                )

        return HexenType.UNKNOWN

    def _resolve_comptime_type(
        self, comptime_type: HexenType, target_type: Optional[HexenType]
    ) -> HexenType:
        """
        Resolve a comptime type to a concrete type based on context.

        Used when we have a comptime_int or comptime_float that needs to become
        a concrete type. Falls back to default types if no target is provided.
        """
        if comptime_type == HexenType.COMPTIME_INT:
            if target_type and self._is_numeric_type(target_type):
                return target_type
            else:
                return HexenType.I32  # Default integer type

        elif comptime_type == HexenType.COMPTIME_FLOAT:
            if target_type and self._is_float_type(target_type):
                return target_type
            else:
                return HexenType.F64  # Default float type

        else:
            return comptime_type  # Not a comptime type, return as-is

    def _is_mixed_type_operation(
        self, left_type: HexenType, right_type: HexenType
    ) -> bool:
        """Check if an operation involves mixed types that require explicit handling."""
        return (
            (
                left_type == HexenType.COMPTIME_INT
                and right_type == HexenType.COMPTIME_FLOAT
            )
            or (
                left_type == HexenType.COMPTIME_FLOAT
                and right_type == HexenType.COMPTIME_INT
            )
            or (self._is_float_type(left_type) and not self._is_float_type(right_type))
            or (not self._is_float_type(left_type) and self._is_float_type(right_type))
        )

    def _is_numeric_type(self, type_: HexenType) -> bool:
        """Check if a type is numeric (integer or float)."""
        return type_ in {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }

    def _is_float_type(self, type_: HexenType) -> bool:
        """Check if a type is a float type."""
        return type_ in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}

    def _to_float_type(self, type_: HexenType) -> HexenType:
        """Convert a type to its float equivalent."""
        if type_ == HexenType.COMPTIME_INT:
            return HexenType.F64
        elif type_ == HexenType.COMPTIME_FLOAT:
            return HexenType.F64
        elif type_ in {HexenType.I32, HexenType.I64}:
            return HexenType.F64
        else:
            return type_

    def _to_integer_type(self, type_: HexenType) -> HexenType:
        """Convert a type to its integer equivalent."""
        if type_ == HexenType.COMPTIME_INT:
            return HexenType.I32
        else:
            return type_

    def _analyze_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze an expression and return its type.

        This is a placeholder that should be implemented by the main analyzer.
        The BinaryOpsAnalyzer will receive this method from the main analyzer.
        """
        raise NotImplementedError(
            "BinaryOpsAnalyzer requires _analyze_expression to be provided by the main analyzer"
        )
