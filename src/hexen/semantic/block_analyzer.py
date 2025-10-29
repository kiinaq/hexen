"""
Hexen Block Analyzer

Handles analysis of blocks following the unified block system (UNIFIED_BLOCK_SYSTEM.md).

Analyzes all block types:
- Expression blocks: Produce values, require final return statement
- Statement blocks: Execute code, allow function returns, no value production
- Function bodies: Unified with other blocks, context provides return type validation
- Universal scope management for all block types
"""

from typing import Dict, List, Optional, Callable

from .comptime import ComptimeAnalyzer
from .symbol_table import SymbolTable
from .types import HexenType, BlockEvaluability
from ..ast_nodes import NodeType


class BlockAnalyzer:
    """
    Analyzes blocks following the unified block system (UNIFIED_BLOCK_SYSTEM.md).

    Implements the core Hexen principle: "One Syntax, Context-Driven Behavior"
    - All blocks use same `{}` syntax
    - Context determines specific behavior (expression vs statement vs function)
    - Universal scope management regardless of context
    - Return statement validation based on context

    Block Types:
    - Expression blocks: Must end with return, produce values
    - Statement blocks: Execute code, allow function returns
    - Function blocks: Unified with other blocks, type validation from function signature
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_statement_callback: Callable[[Dict], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
        symbol_table: SymbolTable,
        get_current_function_return_type_callback: Callable[[], Optional[HexenType]],
        block_context_stack: List[str],
    ):
        """
        Initialize the block analyzer.

        Args:
            error_callback: Function to report semantic errors
            analyze_statement_callback: Function to analyze individual statements
            analyze_expression_callback: Function to analyze expressions
            symbol_table: Symbol table for scope management
            get_current_function_return_type_callback: Function to get current function's return type
            block_context_stack: Reference to main analyzer's block context stack
        """
        self._error = error_callback
        self._analyze_statement = analyze_statement_callback
        self._analyze_expression = analyze_expression_callback
        self.symbol_table = symbol_table
        self._get_current_function_return_type = (
            get_current_function_return_type_callback
        )
        self.block_context_stack = block_context_stack

        # Initialize comptime analyzer for block evaluability detection
        self.comptime_analyzer = ComptimeAnalyzer(symbol_table)

    def analyze_block(
        self, body: Dict, node: Dict, context: str = None
    ) -> Optional[HexenType]:
        """
        Unified block analysis implementing UNIFIED_BLOCK_SYSTEM.md principles.

        ALL blocks:
        - Manage their own scope (complete unification)
        - Follow same scope creation/destruction pattern

        Context determines return statement rules:
        - "expression": Requires return as final statement (value computation)
        - "statement": No return statements required (statement execution)
        - None (function): Allows returns anywhere, type validation from function signature

        Args:
            body: Block AST node containing statements
            node: Parent node (for error reporting context)
            context: Block context ("expression", "statement", or None for function)

        Returns:
            HexenType for expression blocks (the computed value type)
            None for statement blocks and function blocks (no value production)
        """
        if body.get("type") != NodeType.BLOCK.value:
            self._error(f"Expected block node, got {body.get('type')}")
            return HexenType.UNKNOWN if context == "expression" else None

        # Universal scope management (UNIFIED_BLOCK_SYSTEM.md principle)
        # ALL blocks manage their own scope regardless of context
        self.symbol_table.enter_scope()

        # Context tracking for expression blocks
        if context == "expression":
            self.block_context_stack.append("expression")
        elif context == "loop_expression":
            self.block_context_stack.append("loop_expression")

        try:
            statements = body.get("statements", [])
            return self._analyze_statements_with_context(statements, context, node)
        finally:
            # Universal scope cleanup (UNIFIED_BLOCK_SYSTEM.md principle)
            # ALL blocks clean up their own scope regardless of context
            self.symbol_table.exit_scope()

            # Expression context cleanup
            if context == "expression":
                self.block_context_stack.pop()
            elif context == "loop_expression":
                self.block_context_stack.pop()

    def _analyze_statements_with_context(
        self, statements: List[Dict], context: str, node: Dict
    ) -> Optional[HexenType]:
        """
        Analyze statements with context-specific assign/return validation.

        NEW UNIFIED_BLOCK_SYSTEM.md semantics:
        - Expression blocks: Must end with 'assign' OR 'return' (dual capability)
        - Statement blocks: Allow 'return' for function exits, no 'assign' statements
        - Function blocks: Returns allowed anywhere, type validation applied
        """
        is_expression_block = context == "expression"
        is_loop_expression_block = context == "loop_expression"
        is_statement_block = context == "statement"
        last_statement = None
        has_assign = False
        has_return = False

        # Analyze all statements with context-specific rules
        for i, stmt in enumerate(statements):
            stmt_type = stmt.get("type")
            is_last_statement = i == len(statements) - 1

            if stmt_type == "assign_statement":
                if is_expression_block:
                    # Expression blocks: assign must be last statement
                    if is_last_statement:
                        has_assign = True
                        last_statement = stmt
                    else:
                        self._error(
                            "'assign' statement must be the last statement in expression block",
                            stmt,
                        )
                elif is_loop_expression_block:
                    # Loop expression blocks: assign statements (-> statements) allowed anywhere
                    # They don't need to be last because of flexible control flow (filtering, break, etc.)
                    # The loop analyzer handles the actual analysis of these statements
                    pass  # Allow -> statements anywhere in loop body
                elif is_statement_block:
                    # Statement blocks: assign statements not allowed
                    self._error(
                        "'assign' statement only valid in expression blocks",
                        stmt,
                    )
                # Function blocks: assign statements not allowed
                elif context is None:
                    self._error(
                        "'assign' statement only valid in expression blocks",
                        stmt,
                    )

            elif stmt_type == "return_statement":
                if is_expression_block:
                    # Expression blocks: return must be last statement (alternative to assign)
                    if is_last_statement:
                        has_return = True
                        last_statement = stmt
                    else:
                        self._error(
                            "'return' statement must be the last statement in expression block",
                            stmt,
                        )
                # Statement blocks and function blocks: returns allowed anywhere
                # (will be validated by return_analyzer)

            # Delegate to main analyzer for statement analysis
            self._analyze_statement(stmt)

        # Context-specific final validation and type computation
        if is_expression_block:
            # Expression blocks always use explicit type context
            # No evaluability classification needed - all expression blocks require explicit types
            return self._finalize_expression_block(
                has_assign, has_return, last_statement, node
            )

        if is_loop_expression_block:
            # Loop expression blocks allow flexible control flow
            # They don't require strict ending statements because:
            # - Filtering: some iterations may not yield values
            # - Break/continue: control flow can bypass yield statements
            # - Conditional yields: only some branches may produce values
            # The loop analyzer handles validation of -> statements directly
            return None

        # Statement blocks and function blocks don't produce values
        return None

    def _finalize_expression_block(
        self,
        has_assign: bool,
        has_return: bool,
        last_statement: Optional[Dict],
        node: Dict,
    ) -> HexenType:
        """
        Finalize expression block analysis with explicit type context.

        Expression blocks behave like inline functions and ALWAYS use explicit
        type context for type resolution (no comptime type preservation).

        Expression blocks must end with EITHER:
        - 'assign expression' (produces block value)
        - 'return expression' (early function exit with value)

        Type Resolution:
        - Always uses function return type as explicit context
        - Comptime types resolve immediately to concrete types
        - Consistent with function and conditional type requirements

        Args:
            has_assign: Whether block has assign statement
            has_return: Whether block has return statement
            last_statement: The final statement in the block
            node: Block node for error reporting

        Returns:
            Type of the expression block result (with explicit context)
        """
        if not (has_assign or has_return):
            self._error(
                "Expression block must end with 'assign' statement or 'return' statement",
                node,
            )
            return HexenType.UNKNOWN

        if not last_statement:
            self._error("Expression block is empty", node)
            return HexenType.UNKNOWN

        # Handle assign statement (block value production)
        if has_assign and last_statement.get("type") == "assign_statement":
            assign_value = last_statement.get("value")
            if assign_value:
                # Use current function return type as context for expression analysis
                # This implements context-guided type resolution for comptime types
                return self._analyze_expression(
                    assign_value, self._get_current_function_return_type()
                )
            else:
                self._error("'assign' statement requires an expression", last_statement)
                return HexenType.UNKNOWN

        # Handle return statement (function exit)
        elif has_return and last_statement.get("type") == "return_statement":
            # Return statements in expression blocks exit the function
            # The return_analyzer will handle type validation
            return_value = last_statement.get("value")
            if return_value:
                # Analyze the expression being returned
                return self._analyze_expression(
                    return_value, self._get_current_function_return_type()
                )
            else:
                # Bare return in expression block - error (should have been caught earlier)
                self._error(
                    "Expression block 'return' statement must have a value",
                    last_statement,
                )
                return HexenType.UNKNOWN

        # Should not reach here
        return HexenType.UNKNOWN


    # =========================================================================
    # BACKWARD COMPATIBILITY METHODS FOR TESTS
    # =========================================================================

    def _classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.classify_block_evaluability(statements)

    def _contains_runtime_operations(self, statements: List[Dict]) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._contains_runtime_operations(statements)

    def _contains_function_calls(self, statements: List[Dict]) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._contains_function_calls(statements)

    def _contains_conditionals(self, statements: List[Dict]) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._contains_conditionals(statements)

    def _has_comptime_only_operations(self, statements: List[Dict]) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.has_comptime_only_operations(statements)

    def _has_runtime_variables(self, statements: List[Dict]) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.has_runtime_variables(statements)

    def _validate_runtime_block_context(
        self, statements: List[Dict], evaluability: BlockEvaluability
    ) -> Optional[str]:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.validate_runtime_block_context(
            statements, evaluability
        )

    def _get_runtime_operation_reason(self, statements: List[Dict]) -> str:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.get_runtime_operation_reason(statements)

    def _statement_has_comptime_only_operations(self, statement: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.statement_has_comptime_only_operations(statement)

    def _expression_has_comptime_only_operations(self, expression: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.expression_has_comptime_only_operations(
            expression
        )

    def _statement_has_runtime_variables(self, statement: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.statement_has_runtime_variables(statement)

    def _expression_has_runtime_variables(self, expression: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.expression_has_runtime_variables(expression)

    def _statement_contains_function_calls(self, statement: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._statement_contains_function_calls(statement)

    def _statement_contains_conditionals(self, statement: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._statement_contains_conditionals(statement)

    def _expression_contains_function_calls(self, expression: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._expression_contains_function_calls(expression)

    def _expression_contains_conditionals(self, expression: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer._expression_contains_conditionals(expression)
