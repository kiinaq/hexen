"""
Hexen Binary Operations Analyzer

Handles analysis of binary operations including:
- Arithmetic operations (+, -, *, /, \)
- Logical operations (&&, ||)
- Comparison operations (<, >, <=, >=, ==, !=)
- Type coercion and comptime type adaptation
- Division operator specific rules (/ vs \)
- Mixed type operations with explicit type requirements
"""

from typing import Dict, Optional, Callable, Set

from .types import HexenType
from .type_util import (
    is_numeric_type,
    is_float_type,
    resolve_comptime_type,
    to_float_type,
    to_integer_type,
    get_wider_type,
    is_mixed_type_operation,
    is_integer_type,
    can_coerce,
)

# Set of comparison operators
COMPARISON_OPERATORS: Set[str] = {"<", ">", "<=", ">=", "==", "!="}

# Set of equality operators (subset of comparison operators)
EQUALITY_OPERATORS: Set[str] = {"==", "!="}


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

        # Analyze operands (with context if provided)
        left_type = self._analyze_expression(left, target_type)
        right_type = self._analyze_expression(right, target_type)

        if left_type == HexenType.UNKNOWN or right_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Handle comparison operators
        if operator in COMPARISON_OPERATORS:
            return self._analyze_comparison_operation(
                operator, left_type, right_type, node, target_type
            )

        # Handle logical operators
        if operator in ["&&", "||"]:
            # Logical operations require boolean operands
            if left_type != HexenType.BOOL or right_type != HexenType.BOOL:
                self._error(
                    f"Logical operator '{operator}' requires boolean operands, got {left_type.value} and {right_type.value}",
                    node,
                )
                return HexenType.UNKNOWN
            # Logical operations always produce boolean results
            return HexenType.BOOL

        # Handle division operators next
        if operator in ["/", "\\"]:
            return self._analyze_division_operation(
                operator, left_type, right_type, node, target_type
            )

        # Handle mixed type operations and float operations
        if target_type is None:
            if is_mixed_type_operation(left_type, right_type):
                self._error("Mixed types require explicit result type", node)
                return HexenType.UNKNOWN
            if is_float_type(left_type) and is_float_type(right_type):
                self._error(
                    "comptime_float operations require explicit result type", node
                )
                return HexenType.UNKNOWN
        else:
            # When target_type is provided, check if mixed types can be safely resolved
            if is_mixed_type_operation(left_type, right_type):
                # Check if the target type can safely accommodate both operand types
                if not (
                    can_coerce(left_type, target_type)
                    and can_coerce(right_type, target_type)
                ):
                    self._error("Mixed types require explicit result type", node)
                    return HexenType.UNKNOWN
                # If both types can coerce to target, allow the operation to proceed

            # For float operations with target context, allow if target can accommodate
            if is_float_type(left_type) and is_float_type(right_type):
                if not is_float_type(target_type):
                    self._error(
                        "comptime_float operations require explicit result type", node
                    )
                    return HexenType.UNKNOWN
                # If target is also float type, allow the operation to proceed

        # Handle remaining arithmetic operations
        return self._resolve_binary_operation_type(
            operator, left_type, right_type, target_type
        )

    def _analyze_comparison_operation(
        self,
        operator: str,
        left_type: HexenType,
        right_type: HexenType,
        node: Dict,
        target_type: Optional[HexenType] = None,
    ) -> HexenType:
        """
        Analyze comparison operations with type safety rules.

        Rules:
        1. All comparison operations produce boolean results
        2. Only comparable types can be compared:
           - Numeric types can be compared with each other
           - Strings can only be compared with strings
           - Booleans can only be compared with booleans
        3. Mixed numeric types follow comptime promotion rules
        4. No implicit coercion to boolean
        5. Equality operators (==, !=) have stricter type rules than relational operators

        Args:
            operator: The comparison operator (<, >, <=, >=, ==, !=)
            left_type: Type of left operand
            right_type: Type of right operand
            node: AST node for error reporting
            target_type: Optional target type for context guidance

        Returns:
            HexenType.BOOL if comparison is valid, HexenType.UNKNOWN otherwise
        """
        # All comparison operations produce boolean results
        if target_type is not None and target_type != HexenType.BOOL:
            self._error(
                f"Comparison operation '{operator}' always produces boolean result, got target type {target_type.value}",
                node,
            )
            return HexenType.UNKNOWN

        # Handle equality operators (==, !=) first
        if operator in EQUALITY_OPERATORS:
            # For equality, types must be exactly the same
            if left_type != right_type:
                # Special case: comptime types can be compared if they're both numeric
                if is_numeric_type(left_type) and is_numeric_type(right_type):
                    # Allow comparison but warn about potential precision loss
                    self._error(
                        f"Comparison between different numeric types may have unexpected results: {left_type.value} {operator} {right_type.value}",
                        node,
                    )
                else:
                    self._error(
                        f"Cannot compare different types with {operator}: {left_type.value} and {right_type.value}",
                        node,
                    )
                    return HexenType.UNKNOWN
            return HexenType.BOOL

        # Handle relational operators (<, >, <=, >=)
        # These can only be used with numeric types
        if not is_numeric_type(left_type) or not is_numeric_type(right_type):
            self._error(
                f"Relational operator '{operator}' can only be used with numeric types, got {left_type.value} and {right_type.value}",
                node,
            )
            return HexenType.UNKNOWN

        # For numeric comparisons, apply comptime promotion rules
        if is_mixed_type_operation(left_type, right_type):
            # Emit a warning about mixed numeric type comparison
            self._error(
                f"Comparison between different numeric types may have unexpected results: {left_type.value} {operator} {right_type.value}",
                node,
            )
            # Always return boolean for comparison operations
            return HexenType.BOOL

        # For same-type numeric comparisons, result is boolean
        return HexenType.BOOL

    def _analyze_division_operation(
        self,
        operator: str,
        left_type: HexenType,
        right_type: HexenType,
        node: Dict,
        target_type: Optional[HexenType] = None,
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
            return self._analyze_float_division(
                left_type, right_type, target_type, node
            )

        # Handle integer division (\)
        else:  # operator == "\\"
            return self._analyze_integer_division(left_type, right_type, node)

    def _analyze_float_division(
        self,
        left_type: HexenType,
        right_type: HexenType,
        target_type: Optional[HexenType] = None,
        node: Optional[Dict] = None,
    ) -> HexenType:
        """Analyze float division operation."""
        # If no target type is provided, emit error about requiring explicit type
        if target_type is None and node is not None:
            self._error("Float division requires explicit result type", node)
            return HexenType.UNKNOWN

        # Convert operands to float types
        left_float = to_float_type(left_type)
        right_float = to_float_type(right_type)

        # If target type is provided and it's a float type, use it
        if target_type and is_float_type(target_type):
            return target_type

        # Otherwise, result is the wider of the two float types
        return get_wider_type(left_float, right_float)

    def _analyze_integer_division(
        self, left_type: HexenType, right_type: HexenType, node: Dict
    ) -> HexenType:
        """Analyze integer division operation."""
        # Check for float operands
        if is_float_type(left_type) or is_float_type(right_type):
            self._error(
                "Integer division (\\) cannot be used with float operands", node
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
        - Logical operations (&&, ||)
        """
        # Handle comptime types first
        left_type = resolve_comptime_type(left_type, target_type)
        right_type = resolve_comptime_type(right_type, target_type)

        # Handle logical operators
        if operator in ["&&", "||"]:
            # Logical operations always produce boolean results
            # Note: Operand type validation is done in analyze_binary_operation
            return HexenType.BOOL

        # For non-comptime types, use standard type resolution
        if operator in ["+", "-", "*"]:
            # Handle string concatenation for + operator
            if (
                operator == "+"
                and left_type == HexenType.STRING
                and right_type == HexenType.STRING
            ):
                return HexenType.STRING

            # If target_type is provided and is a float or integer type, use it
            if target_type and (
                is_float_type(target_type) or is_integer_type(target_type)
            ):
                return target_type
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
