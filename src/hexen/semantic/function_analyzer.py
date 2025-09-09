"""
Function Call Analysis for Hexen Language

Handles function call resolution and parameter type checking including:
- Function name lookup and validation
- Argument-parameter matching and validation
- Parameter type context for comptime type resolution
- TYPE_SYSTEM.md rule application to function arguments
- Function call return type inference

Implements the unified type resolution strategy from FUNCTION_SYSTEM.md.
"""

from typing import Dict, Optional, Callable, Union

from .type_util import can_coerce
from .types import HexenType, ConcreteArrayType


class FunctionAnalyzer:
    """
    Specialized analyzer for function call analysis.

    Implements function call resolution following FUNCTION_SYSTEM.md:
    - Function name lookup and validation
    - Parameter type context for argument resolution
    - Comptime type preservation until parameter context forces resolution
    - TYPE_SYSTEM.md conversion rules for all arguments
    - Clear error messages for function call issues

    Design follows the callback pattern for main analyzer integration.
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[
            [Dict, Optional[Union[HexenType, ConcreteArrayType]]], HexenType
        ],
        lookup_function_callback: Callable[[str], Optional[object]],
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._lookup_function = lookup_function_callback

    def analyze_function_call(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a function call and return its type.

        Args:
            node: Function call AST node
            target_type: Optional target type (currently unused for function calls)

        Returns:
            Function return type, or HexenType.UNKNOWN for invalid calls

        Implementation follows FUNCTION_SYSTEM.md parameter-guided resolution:
        1. Function name lookup and validation
        2. Argument count validation
        3. Argument-parameter type resolution using TYPE_SYSTEM.md rules
        4. Return function's return type
        """
        function_name = node.get("function_name")
        if not function_name:
            self._error("Function call missing function name", node)
            return HexenType.UNKNOWN

        # Look up function signature
        function_signature = self._lookup_function(function_name)
        if not function_signature:
            self._error(f"Undefined function: '{function_name}'", node)
            return HexenType.UNKNOWN

        # Validate argument count
        arguments = node.get("arguments", [])
        expected_count = len(function_signature.parameters)
        actual_count = len(arguments)

        if actual_count != expected_count:
            self._error(
                f"Function '{function_name}' expects {expected_count} argument{'s' if expected_count != 1 else ''}, "
                f"but {actual_count} provided",
                node,
            )
            return HexenType.UNKNOWN

        # Analyze each argument against its corresponding parameter
        for i, (argument, parameter) in enumerate(
            zip(arguments, function_signature.parameters)
        ):
            self._analyze_argument_against_parameter(
                argument, parameter, function_name, i + 1
            )

        # Return the function's return type
        return function_signature.return_type

    def _analyze_argument_against_parameter(
        self, argument: Dict, parameter, function_name: str, position: int
    ):
        """
        Analyze a single argument against its corresponding parameter.

        Args:
            argument: Argument expression AST node
            parameter: Parameter object with type and mutability info
            function_name: Function name for error messages
            position: Argument position (1-based) for error messages

        Implementation follows FUNCTION_SYSTEM.md type resolution:
        - Parameter type provides context for argument resolution
        - Comptime types adapt seamlessly to parameter types
        - Mixed concrete types require explicit conversions
        - Same TYPE_SYSTEM.md rules as variable assignments
        """
        # Analyze argument expression with parameter type as context
        # This enables comptime type adaptation and enforces TYPE_SYSTEM.md rules
        argument_type = self._analyze_expression(argument, parameter.param_type)

        # Validate type compatibility using TYPE_SYSTEM.md conversion rules
        if not can_coerce(argument_type, parameter.param_type):
            # Handle error message for both HexenType and ConcreteArrayType
            param_type_str = (
                parameter.param_type.value
                if hasattr(parameter.param_type, "value")
                else str(parameter.param_type)
            )
            arg_type_str = (
                argument_type.value
                if hasattr(argument_type, "value")
                else str(argument_type)
            )

            self._error(
                f"Function '{function_name}' argument {position}: "
                f"Cannot assign {arg_type_str} to parameter '{parameter.name}' of type {param_type_str}. "
                f"Use explicit conversion: 'expression:{param_type_str}'",
                argument,
            )
