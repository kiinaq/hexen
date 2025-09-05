"""
Hexen Return Statement Analyzer - UNIFIED SEMANTICS

Implements UNIFIED_BLOCK_SYSTEM.md return semantics:
- return ALWAYS means "exit the function" (consistent everywhere)
- Expression blocks: return exits function (alternative to assign)
- Statement blocks: return exits function
- Function blocks: return exits function
- Bare return statement handling for void functions
- Return value type checking and coercion
- Precision loss detection for return values
"""

from typing import Dict, List, Optional, Callable, Union

from .types import HexenType, ConcreteArrayType
from .type_util import is_precision_loss_operation


class ReturnAnalyzer:
    """
    Analyzes return statements with UNIFIED semantics (UNIFIED_BLOCK_SYSTEM.md).

    NEW unified return semantics:
    - return ALWAYS means "exit the function" (consistent meaning everywhere)
    - Expression blocks: return exits function (alternative to assign, dual capability)
    - Statement blocks: return exits function
    - Function blocks: return exits function
    - Bare returns: Only allowed in void functions
    - Type checking: Return values must be coercible to function return type
    - Precision loss: Dangerous conversions require explicit conversion
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[Union[HexenType, ConcreteArrayType]]], HexenType],
        get_block_context_callback: Callable[[], List[str]],
        get_current_function_return_type_callback: Callable[[], Optional[Union[HexenType, ConcreteArrayType]]],
        comptime_analyzer,
    ):
        """
        Initialize the return analyzer.

        Args:
            error_callback: Function to call when semantic errors are found
            analyze_expression_callback: Function to analyze expressions
            get_block_context_callback: Function to get current block context stack
            get_current_function_return_type_callback: Function to get current function return type
            comptime_analyzer: ComptimeAnalyzer instance for comptime type operations
        """
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._get_block_context = get_block_context_callback
        self._get_current_function_return_type = (
            get_current_function_return_type_callback
        )
        self.comptime_analyzer = comptime_analyzer

    def analyze_return_statement(self, node: Dict) -> None:
        """
        Analyze a return statement with support for bare returns.

        Context-aware validation:
        - Default context: Return type must match function return type
        - Expression context: Return determines block's type (must have value)
        - Bare returns: Only allowed in void functions or statement blocks
        - No valid context: Error - return statements need context
        """
        value = node.get("value")
        current_function_return_type = self._get_current_function_return_type()
        block_context = self._get_block_context()

        # Handle bare return (return;)
        if value is None:
            self._analyze_bare_return(node, current_function_return_type, block_context)
            return

        # Handle return with value (return expression;)
        self._analyze_value_return(
            node, value, current_function_return_type, block_context
        )

    def _analyze_bare_return(
        self,
        node: Dict,
        current_function_return_type: Optional[Union[HexenType, ConcreteArrayType]],
        block_context: List[str],
    ) -> None:
        """
        Analyze bare return statements (return;) with UNIFIED semantics.

        NEW UNIFIED_BLOCK_SYSTEM.md semantics:
        - return ALWAYS means "exit the function" (consistent everywhere)
        - Expression blocks: bare return not allowed (must have value for function exit)
        - Statement blocks: bare return allowed for void functions only
        - Function blocks: bare return allowed for void functions only
        """
        # Expression blocks cannot have bare returns (need value for function exit)
        if block_context and block_context[-1] == "expression":
            self._error(
                "Expression block 'return' statement must have a value for function exit",
                node,
            )
            return

        # All other contexts: bare return only valid for void functions
        if current_function_return_type == HexenType.VOID:
            # Void functions can have bare returns
            return
        elif current_function_return_type:
            # Non-void functions cannot have bare returns
            self._error(
                f"Function returning {current_function_return_type.value} "
                f"cannot have bare return statement",
                node,
            )
            return
        else:
            # No valid context for return statement
            self._error("Return statement outside valid context", node)
            return

    def _analyze_value_return(
        self,
        node: Dict,
        value: Dict,
        current_function_return_type: Optional[Union[HexenType, ConcreteArrayType]],
        block_context: List[str],
    ) -> None:
        """
        Analyze return statements with values (return expression;) with UNIFIED semantics.

        NEW UNIFIED_BLOCK_SYSTEM.md semantics:
        - return ALWAYS means "exit the function with value" (consistent everywhere)
        - All contexts: validate return value against function signature
        - Expression blocks: return exits function (skips assign, dual capability)
        - Statement blocks: return exits function
        - Function blocks: return exits function
        """
        # Analyze the return value expression
        return_type = self._analyze_expression(value, current_function_return_type)

        # UNIFIED validation: return always exits function, so validate against function signature
        if current_function_return_type:
            self._validate_function_return(
                node, value, return_type, current_function_return_type
            )
        else:
            # No valid context for return statement
            self._error("Return statement outside valid context", node)

    def _validate_function_return(
        self,
        node: Dict,
        value: Dict,
        return_type: HexenType,
        expected_return_type: Union[HexenType, ConcreteArrayType],
    ) -> None:
        """Validate return statement against function signature."""
        if expected_return_type == HexenType.VOID:
            # Void functions cannot have return values
            self._error("Void function cannot return a value", node)
        elif return_type != HexenType.UNKNOWN:
            # Check for precision loss operations that require explicit conversion
            # Skip precision loss check for ConcreteArrayType (not applicable)
            if (isinstance(expected_return_type, HexenType) and 
                is_precision_loss_operation(return_type, expected_return_type)):
                # For non-explicit-conversion expressions, require explicit conversion
                if value.get("type") != "explicit_conversion_expression":
                    self._generate_precision_loss_error(
                        return_type, expected_return_type, node
                    )
                    return

            # Check for literal overflow before type coercion (only for simple types)
            if (return_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT} and
                isinstance(expected_return_type, HexenType)):
                literal_value, source_text = self.comptime_analyzer.extract_literal_info(value)
                if literal_value is not None:
                    try:
                        self.comptime_analyzer.validate_comptime_literal_coercion(
                            literal_value,
                            return_type,
                            expected_return_type,
                            source_text,
                        )
                    except TypeError as e:
                        self._error(str(e), node)
                        return

            # Use coercion for return type checking
            from .type_util import can_coerce

            if not can_coerce(return_type, expected_return_type):
                # Handle error message for both HexenType and ConcreteArrayType
                expected_str = expected_return_type.value if hasattr(expected_return_type, 'value') else str(expected_return_type)
                return_str = return_type.value if hasattr(return_type, 'value') else str(return_type)
                
                self._error(
                    f"Return type mismatch: expected {expected_str}, got {return_str}",
                    node,
                )

    def _generate_precision_loss_error(
        self, return_type: HexenType, expected_return_type: HexenType, node: Dict
    ) -> None:
        """Generate appropriate precision loss error message for return statements."""
        if return_type == HexenType.I64 and expected_return_type == HexenType.I32:
            self._error(
                "Potential truncation. Use explicit conversion: 'value:i32'",
                node,
            )
        elif return_type == HexenType.F64 and expected_return_type == HexenType.F32:
            self._error(
                "Potential precision loss. Use explicit conversion: 'value:f32'",
                node,
            )
        elif return_type in {
            HexenType.F32,
            HexenType.F64,
            HexenType.COMPTIME_FLOAT,
        } and expected_return_type in {HexenType.I32, HexenType.I64}:
            # Float to integer conversion - use "truncation" terminology
            self._error(
                f"Potential truncation. Use explicit conversion: 'value:{expected_return_type.value}'",
                node,
            )
        elif return_type == HexenType.I64 and expected_return_type == HexenType.F32:
            self._error(
                "Potential precision loss. Use explicit conversion: 'value:f32'",
                node,
            )
        else:
            # Generic precision loss message
            self._error(
                f"Potential precision loss. Use explicit conversion: 'value:{expected_return_type.value}'",
                node,
            )
