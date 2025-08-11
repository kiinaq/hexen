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
from .types import HexenType, BlockEvaluability
from .symbol_table import SymbolTable
from .comptime_analyzer import ComptimeAnalyzer


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
        Analyze statements with context-specific assign/return validation.

        NEW UNIFIED_BLOCK_SYSTEM.md semantics:
        - Expression blocks: Must end with 'assign' OR 'return' (dual capability)
        - Statement blocks: Allow 'return' for function exits, no 'assign' statements
        - Function blocks: Returns allowed anywhere, type validation applied
        """
        is_expression_block = context == "expression"
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
            # Classify block evaluability while still in scope
            # CRITICAL: Must happen before scope exit so variables are accessible
            evaluability = self.comptime_analyzer.classify_block_evaluability(statements)
            return self._finalize_expression_block_with_evaluability(
                has_assign, has_return, last_statement, node, evaluability
            )

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
        Finalize expression block analysis following NEW UNIFIED_BLOCK_SYSTEM.md rules.

        Expression blocks must end with EITHER:
        - 'assign expression' (produces block value)
        - 'return expression' (early function exit with value)

        Dual capability: assign = block value, return = function exit
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

    def _finalize_expression_block_with_evaluability(
        self,
        has_assign: bool,
        has_return: bool,
        last_statement: Optional[Dict],
        node: Dict,
        evaluability: BlockEvaluability,
    ) -> HexenType:
        """
        Finalize expression block analysis with evaluability-aware type resolution.
        
        Comptime Type Preservation Logic
                This implements the enhanced unified block system functionality:
        - COMPILE_TIME blocks: Preserve comptime types for maximum flexibility
        - RUNTIME blocks: Require explicit context validation and immediate resolution
        
        Args:
            has_assign: Whether block has assign statement
            has_return: Whether block has return statement  
            last_statement: The final statement in the block
            node: Block node for error reporting
            evaluability: Block evaluability classification
            
        Returns:
            Type of the expression block result
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
                # Evaluability-aware type resolution
                if evaluability == BlockEvaluability.COMPILE_TIME:
                    # Compile-time evaluable blocks: Preserve comptime types for maximum flexibility
                    return self._analyze_expression_preserve_comptime(assign_value)
                else:
                    # Runtime blocks: Use explicit context (function return type)
                    # This provides concrete context for immediate type resolution
                    return self._analyze_expression_with_context(
                        assign_value, self._get_current_function_return_type()
                    )
            else:
                self._error("'assign' statement requires an expression", last_statement)
                return HexenType.UNKNOWN

        # Handle return statement (function exit)
        elif has_return and last_statement.get("type") == "return_statement":
            # Return statements in expression blocks exit the function
            # Always use function return type as context (both compile-time and runtime)
            return_value = last_statement.get("value")
            if return_value:
                # Return statements always use function context for type resolution
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
    # COMPTIME TYPE PRESERVATION LOGIC
    # =========================================================================

    def _analyze_expression_preserve_comptime(self, expression: Dict) -> HexenType:
        """
        Analyze expression while preserving comptime types for maximum flexibility.
        
        This is used for compile-time evaluable expression blocks to enable the 
        "one computation, multiple uses" pattern from UNIFIED_BLOCK_SYSTEM.md.
        
        Key behavior:
        - Comptime types (COMPTIME_INT, COMPTIME_FLOAT) are preserved as-is
        - No target type context provided (preserves flexibility)
        - All operations remain in comptime space until explicit context forces resolution
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            Expression type with comptime types preserved for later context-driven resolution
        """
        # No target type context provided - this preserves comptime type flexibility
        return self._analyze_expression(expression, None)

    def _analyze_expression_with_context(self, expression: Dict, target_type: Optional[HexenType]) -> HexenType:
        """
        Analyze expression with explicit target context for immediate resolution.
        
        This is used for runtime blocks that require explicit context due to
        runtime operations (function calls, conditionals, concrete variables).
        
        Key behavior:
        - Target type provides explicit context for type resolution
        - Comptime types resolve immediately to concrete types
        - All conversions happen with explicit context guidance
        
        Args:
            expression: Expression AST node to analyze
            target_type: Target type providing explicit context for resolution
            
        Returns:
            Expression type with immediate context-driven resolution
        """
        # Target type context provided - this forces immediate resolution
        return self._analyze_expression(expression, target_type)

    def _validate_runtime_block_context_requirement(self, evaluability: BlockEvaluability, node: Dict) -> bool:
        """
        Validate that runtime blocks have the required explicit type context.
        
        This enforces the specification requirement:
        "Runtime blocks require explicit type context due to runtime operations"
        
        The validation logic provides foundation for comprehensive error messages
        and suggestions for proper usage patterns.
        
        Args:
            evaluability: Block evaluability classification
            node: Block node for error reporting context
            
        Returns:
            True if validation passes, False if context is required but missing
        """
        if evaluability == BlockEvaluability.COMPILE_TIME:
            # Compile-time blocks don't require explicit context
            return True
            
        # Runtime blocks validation logic
        if evaluability == BlockEvaluability.RUNTIME:
            # Runtime blocks in expression context need explicit type context
            # This validation provides foundation for detailed error messages
            
            # Currently, we assume function return type provides adequate context
            # Future enhancements will add comprehensive context validation for variable declarations
            function_return_type = self._get_current_function_return_type()
            if function_return_type is None:
                # No function context - this would be an error condition
                return False
                
            # Function provides explicit type context
            return True
            
        # Unknown evaluability - assume validation fails for safety
        return False

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
    
    def _validate_runtime_block_context(self, statements: List[Dict], evaluability: BlockEvaluability) -> Optional[str]:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.validate_runtime_block_context(statements, evaluability)
    
    def _get_runtime_operation_reason(self, statements: List[Dict]) -> str:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.get_runtime_operation_reason(statements)
    
    def _statement_has_comptime_only_operations(self, statement: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.statement_has_comptime_only_operations(statement)
    
    def _expression_has_comptime_only_operations(self, expression: Dict) -> bool:
        """Delegate to comptime analyzer for backward compatibility."""
        return self.comptime_analyzer.expression_has_comptime_only_operations(expression)
    
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


