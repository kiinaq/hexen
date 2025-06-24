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

from ..ast_nodes import NodeType
from .types import HexenType
from .symbol_table import SymbolTable


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

    def _analyze_statements_with_context(
        self, statements: List[Dict], context: str, node: Dict
    ) -> Optional[HexenType]:
        """
        Analyze statements with context-specific return validation.

        Implements context-driven behavior from UNIFIED_BLOCK_SYSTEM.md:
        - Expression blocks: Return must be last statement
        - Statement blocks: Function returns allowed anywhere
        - Function blocks: Returns allowed anywhere, type validation applied
        """
        is_expression_block = context == "expression"
        is_statement_block = context == "statement"
        is_void_function = self._get_current_function_return_type() == HexenType.VOID
        last_return_stmt = None

        # Analyze all statements with context-specific return rules
        for i, stmt in enumerate(statements):
            if stmt.get("type") == "return_statement":
                if is_void_function:
                    # Let return_analyzer handle void function validation
                    # to avoid duplicate error reporting
                    pass
                elif is_statement_block:
                    # Statement blocks can have returns that match function signature
                    # This allows returning from the function within a statement block
                    pass  # Will be validated by return_analyzer
                elif is_expression_block:
                    # Expression blocks: return must be last statement
                    if i == len(statements) - 1:
                        last_return_stmt = stmt
                    else:
                        self._error(
                            "Return statement must be the last statement in expression block",
                            stmt,
                        )
                # Non-void function blocks: returns allowed anywhere (no restriction)

            # Delegate to main analyzer for statement analysis
            self._analyze_statement(stmt)

        # Context-specific return validation and type computation
        if is_expression_block:
            return self._finalize_expression_block(last_return_stmt, node)

        # Statement blocks and function blocks don't produce values
        return None

    def _finalize_expression_block(
        self, last_return_stmt: Optional[Dict], node: Dict
    ) -> HexenType:
        """
        Finalize expression block analysis following UNIFIED_BLOCK_SYSTEM.md rules.

        Expression blocks must:
        - End with a return statement (required for value production)
        - Return type matches the expression type
        - Context provides type validation (function return type)
        """
        if not last_return_stmt:
            self._error("Expression block must end with a return statement", node)
            return HexenType.UNKNOWN

        # Get the type from the return statement's value
        return_value = last_return_stmt.get("value")
        if return_value:
            # Use current function return type as context for expression analysis
            # This implements context-guided type resolution
            return self._analyze_expression(
                return_value, self._get_current_function_return_type()
            )
        else:
            # Bare return in expression block (shouldn't happen, but handle gracefully)
            return HexenType.UNKNOWN
