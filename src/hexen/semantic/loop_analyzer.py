"""
Hexen Loop Analyzer

Handles semantic analysis of loop constructs following LOOP_SYSTEM.md.

Responsibilities:
- Loop variable type inference and validation
- Break/continue validation (must be inside loops)
- Label resolution and scope management
- Loop expression mode detection (statement vs expression)
- Unbounded range safety checking (no unbounded in expression mode)
- While loop restrictions (no expression mode)
- Nested loop expression validation
"""

from typing import Dict, Optional, Callable, List, Union

from .types import HexenType, ArrayType, RangeType, LoopContext, ComptimeRangeType
from .symbol_table import SymbolTable
from .comptime import ComptimeAnalyzer
from ..ast_nodes import NodeType


class LoopAnalyzer:
    """
    Analyzes loop constructs (for-in, while, break, continue, labels).

    Key responsibilities:
    1. Type inference for loop variables from iterables
    2. Immutability enforcement for loop variables
    3. Break/continue validation (inside loop check)
    4. Label resolution and validation
    5. Loop expression mode detection
    6. Unbounded range safety (no unbounded in expression mode)
    7. While loop restrictions (no expression mode)

    Design principles:
    - Follow existing analyzer patterns (callback-based)
    - Comprehensive error messages with helpful hints
    - Support for nested loops and labels
    - Expression vs statement mode detection
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[
            [Dict, Optional[Union[HexenType, ArrayType]]], Union[HexenType, ArrayType]
        ],
        analyze_statement_callback: Callable[[Dict], None],
        symbol_table: SymbolTable,
        loop_stack: List[LoopContext],
        label_stack: Dict[str, LoopContext],
        get_current_function_return_type_callback: Callable[
            [], Optional[Union[HexenType, ArrayType]]
        ],
        comptime_analyzer: ComptimeAnalyzer,
    ):
        """
        Initialize loop analyzer with callbacks.

        Args:
            error_callback: Function to report semantic errors
            analyze_expression_callback: Function to analyze expressions
            analyze_statement_callback: Function to analyze statements
            symbol_table: Symbol table for variable scope management
            loop_stack: Reference to main analyzer's loop stack
            label_stack: Reference to main analyzer's label stack
            get_current_function_return_type_callback: Get current function return type
            comptime_analyzer: Comptime analyzer for type adaptation
        """
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._analyze_statement = analyze_statement_callback
        self.symbol_table = symbol_table
        self.loop_stack = loop_stack
        self.label_stack = label_stack
        self._get_current_function_return_type = get_current_function_return_type_callback
        self.comptime_analyzer = comptime_analyzer

    def analyze_for_in_loop(
        self, node: Dict, expected_type: Optional[Union[HexenType, ArrayType]] = None
    ) -> Optional[Union[HexenType, ArrayType]]:
        """
        Analyze for-in loop (both statement and expression modes).

        Statement mode: for i in 1..10 { print(i) }
        Expression mode: val arr : [_]i32 = for i in 1..10 { -> i }

        Validation rules:
        - Infer loop variable type from iterable
        - Loop variable is always immutable
        - Unbounded ranges forbidden in expression mode
        - Type annotation required for expression mode

        Args:
            node: ForInLoop AST node
            expected_type: Expected type (None for statement mode, ArrayType for expression mode)

        Returns:
            None for statement mode
            ArrayType for expression mode
        """
        # TODO: Implementation in Phase 2
        pass

    def analyze_while_loop(self, node: Dict) -> None:
        """
        Analyze while loop (statement mode only).

        While loops cannot be expressions (unbounded iteration risk).

        Validation rules:
        - Condition must be bool type
        - While loops are always statements (no expression mode)
        - Break/continue allowed inside

        Args:
            node: WhileLoop AST node
        """
        # TODO: Implementation in Phase 2
        pass

    def analyze_break_statement(self, node: Dict) -> None:
        """
        Validate break statement.

        Rules:
        - Must be inside a loop
        - Label (if present) must refer to enclosing loop

        Args:
            node: BreakStatement AST node
        """
        # TODO: Implementation in Phase 2
        pass

    def analyze_continue_statement(self, node: Dict) -> None:
        """
        Validate continue statement.

        Rules:
        - Must be inside a loop
        - Label (if present) must refer to enclosing loop

        Args:
            node: ContinueStatement AST node
        """
        # TODO: Implementation in Phase 2
        pass

    def analyze_labeled_statement(self, node: Dict) -> None:
        """
        Analyze labeled statement.

        Rules:
        - Label must be on a loop (for-in or while)
        - No duplicate labels in same scope
        - Label becomes available for break/continue

        Args:
            node: LabeledStatement AST node
        """
        # TODO: Implementation in Phase 2
        pass

    # Helper methods (to be implemented in Phase 2)

    def _infer_loop_variable_type(
        self,
        iterable_type: Union[HexenType, ArrayType, RangeType],
        explicit_type_annotation: Optional[str],
    ) -> HexenType:
        """
        Infer loop variable type from iterable.

        Rules (LOOP_SYSTEM.md):
        - Comptime range → comptime_int or comptime_float
        - Concrete range[T] → T
        - Array [N]T slice → T
        - Explicit annotation → use annotation (with validation)

        Args:
            iterable_type: Type of the iterable expression
            explicit_type_annotation: Optional explicit type annotation

        Returns:
            Inferred or validated loop variable type
        """
        # TODO: Implementation in Phase 2
        pass

    def _validate_bounded_iterable(
        self, iterable_type: Union[HexenType, ArrayType, RangeType], node: Dict
    ) -> None:
        """
        Validate that iterable is bounded (for expression mode safety).

        Rule: Unbounded ranges cannot produce arrays (infinite allocation risk).

        Args:
            iterable_type: Type of the iterable
            node: AST node for error reporting
        """
        # TODO: Implementation in Phase 2
        pass

    def _analyze_loop_body(
        self,
        body: Dict,
        is_expression_mode: bool,
        expected_type: Optional[Union[HexenType, ArrayType]],
    ) -> None:
        """
        Analyze loop body with mode-specific validation.

        Statement mode: No special requirements
        Expression mode: Must contain -> statements (value production)

        Args:
            body: Loop body block
            is_expression_mode: True if loop produces array
            expected_type: Expected type (for expression mode)
        """
        # TODO: Implementation in Phase 2
        pass

    def _validate_loop_expression(
        self, body: Dict, expected_type: Optional[Union[HexenType, ArrayType]], node: Dict
    ) -> Union[HexenType, ArrayType]:
        """
        Validate loop expression produces correct array type.

        Args:
            body: Loop body
            expected_type: Expected array type
            node: AST node for error reporting

        Returns:
            The array type produced by loop expression
        """
        # TODO: Implementation in Phase 2
        pass
