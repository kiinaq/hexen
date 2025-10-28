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
        # Step 1: Determine loop mode (statement vs expression)
        is_expression_mode = expected_type is not None

        # Step 2: Analyze iterable expression
        variable_name = node.get("variable")
        iterable = node.get("iterable")
        iterable_type = self._analyze_expression(iterable, None)

        # Step 3: Infer loop variable type from iterable
        loop_var_type = self._infer_loop_variable_type(
            iterable_type, node.get("variable_type")
        )

        # Step 4: Validate unbounded range safety (expression mode)
        if is_expression_mode:
            self._validate_bounded_iterable(iterable_type, node)

        # Step 5: Create loop context and push to stack
        loop_context = LoopContext(
            loop_type="for-in",
            label=None,  # Labels handled by labeled_statement
            is_expression_mode=is_expression_mode,
            iterable_type=iterable_type,
            variable_name=variable_name,
            variable_type=loop_var_type,
        )
        self.loop_stack.append(loop_context)

        # Step 6: Enter new scope and declare loop variable (immutable!)
        self.symbol_table.enter_scope()
        self.symbol_table.declare_symbol(
            variable_name, loop_var_type, mutable=False, node=node
        )

        try:
            # Step 7: Analyze loop body
            body = node.get("body")
            self._analyze_loop_body(body, is_expression_mode, expected_type)

            # Step 8: Validate expression mode requirements
            if is_expression_mode:
                return self._validate_loop_expression(body, expected_type, node)
            else:
                return None
        finally:
            # Step 9: Cleanup (scope and loop context)
            self.symbol_table.exit_scope()
            self.loop_stack.pop()

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
        # Step 1: Validate condition type (must be bool)
        condition = node.get("condition")
        condition_type = self._analyze_expression(condition, HexenType.BOOL)

        if condition_type != HexenType.BOOL:
            self._error(
                f"While condition must be of type bool, got {condition_type}\n"
                f"Help: Use explicit comparison: while count > 0",
                condition,
            )

        # Step 2: Create loop context
        loop_context = LoopContext(
            loop_type="while",
            label=None,
            is_expression_mode=False,  # Always statement mode
            iterable_type=None,
            variable_name=None,
            variable_type=None,
        )
        self.loop_stack.append(loop_context)

        # Step 3: Enter scope for body
        self.symbol_table.enter_scope()

        try:
            # Step 4: Analyze body statements
            body = node.get("body")
            self._analyze_loop_body(body, is_expression_mode=False, expected_type=None)
        finally:
            # Step 5: Cleanup
            self.symbol_table.exit_scope()
            self.loop_stack.pop()

    def analyze_break_statement(self, node: Dict) -> None:
        """
        Validate break statement.

        Rules:
        - Must be inside a loop
        - Label (if present) must refer to enclosing loop

        Args:
            node: BreakStatement AST node
        """
        # Check if inside any loop
        if not self.loop_stack:
            self._error(
                "break statement outside loop\n"
                "Note: break can only be used inside for-in or while loops",
                node,
            )
            return

        # Check label (if present)
        label = node.get("label")
        if label:
            if label not in self.label_stack:
                self._error(
                    f"Label '{label}' not found\n"
                    f"Note: Labels must be defined on enclosing loops",
                    node,
                )
            # Label found - break will target that loop
        # No label - break targets innermost loop (already validated via loop_stack check)

    def analyze_continue_statement(self, node: Dict) -> None:
        """
        Validate continue statement.

        Rules:
        - Must be inside a loop
        - Label (if present) must refer to enclosing loop

        Args:
            node: ContinueStatement AST node
        """
        # Check if inside any loop
        if not self.loop_stack:
            self._error(
                "continue statement outside loop\n"
                "Note: continue can only be used inside for-in or while loops",
                node,
            )
            return

        # Check label (if present)
        label = node.get("label")
        if label:
            if label not in self.label_stack:
                self._error(
                    f"Label '{label}' not found\n"
                    f"Note: Labels must be defined on enclosing loops",
                    node,
                )
            # Label found - continue will target that loop
        # No label - continue targets innermost loop (already validated via loop_stack check)

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
        label = node.get("label")
        statement = node.get("statement")
        stmt_type = statement.get("type")

        # Validate label is on a loop
        if stmt_type not in [NodeType.FOR_IN_LOOP.value, NodeType.WHILE_LOOP.value]:
            self._error(
                "Labels can only be applied to loops\n"
                f"  {label}: ...\n"
                "Help: Remove label or apply to for-in/while loop",
                node,
            )
            return

        # Check for duplicate label
        if label in self.label_stack:
            self._error(
                f"Label '{label}' already defined in this scope\n"
                "Help: Use different label name for inner loop",
                node,
            )
            return

        # Add label to stack before analyzing loop
        # (so break/continue inside can reference it)
        loop_context = LoopContext(
            loop_type="for-in" if stmt_type == NodeType.FOR_IN_LOOP.value else "while",
            label=label,
            is_expression_mode=False,  # Will be updated by loop analysis
            iterable_type=None,
            variable_name=None,
            variable_type=None,
        )
        self.label_stack[label] = loop_context

        try:
            # Analyze the loop statement
            if stmt_type == NodeType.FOR_IN_LOOP.value:
                self.analyze_for_in_loop(statement)
            else:
                self.analyze_while_loop(statement)
        finally:
            # Remove label from scope
            del self.label_stack[label]

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
        # If explicit type annotation, validate and use it
        if explicit_type_annotation:
            # Parse the type annotation
            from .expression_analyzer import ExpressionAnalyzer

            explicit_type = ExpressionAnalyzer._parse_type_string(
                explicit_type_annotation
            )
            # TODO: Validate compatibility with iterable type
            return explicit_type

        # Infer from iterable type
        if isinstance(iterable_type, ComptimeRangeType):
            # Comptime range returns element comptime type
            return iterable_type.element_comptime_type

        if isinstance(iterable_type, RangeType):
            # Concrete range returns element type
            return iterable_type.element_type

        if isinstance(iterable_type, ArrayType):
            # Array slice returns element type
            return iterable_type.element_type

        if iterable_type == HexenType.COMPTIME_INT:
            # Comptime range (old enum form)
            return HexenType.COMPTIME_INT

        # Unknown or invalid iterable
        # Error will be reported elsewhere
        return HexenType.UNKNOWN

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
        # Check if iterable is a range type
        if isinstance(iterable_type, (RangeType, ComptimeRangeType)):
            # Check if range is unbounded from start
            if not iterable_type.has_end:
                self._error(
                    "Unbounded loop cannot produce array\n"
                    f"  Range has no end bound\n"
                    "Help: Use bounded range for array generation: for i in start..end\n"
                    "Note: Unbounded ranges (start..) can iterate infinitely but cannot\n"
                    "      materialize to arrays (infinite allocation risk)",
                    node,
                )
        # Arrays are always bounded - no check needed

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
        if body.get("type") != NodeType.BLOCK.value:
            self._error(f"Expected block for loop body", body)
            return

        statements = body.get("statements", [])

        # Analyze each statement in loop body
        for stmt in statements:
            # Delegate to statement analyzer
            self._analyze_statement(stmt)

        # TODO: In expression mode, validate that -> statements exist and match expected type
        # This will be enhanced in Phase 3 (Loop Expression Validation)

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
        if not isinstance(expected_type, ArrayType):
            self._error(
                f"Loop expression must have array type annotation, got {expected_type}",
                node,
            )
            return ArrayType(HexenType.UNKNOWN, None)

        # Loop expressions produce arrays
        # TODO: Validate that -> statements exist and produce correct element type
        # This will be enhanced in Phase 3 (Loop Expression Validation)
        return expected_type
