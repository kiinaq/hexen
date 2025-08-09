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
from .type_util import is_concrete_type


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
            # NEW Session 1: Classify block evaluability while still in scope
            # CRITICAL: Must happen before scope exit so variables are accessible
            evaluability = self._classify_block_evaluability(statements)
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
        
        This is the foundation for the enhanced unified block system. In Session 1,
        we implement the classification but maintain existing behavior. Sessions 2-3
        will add the full comptime type preservation and runtime context validation.
        
        Args:
            has_assign: Whether block has assign statement
            has_return: Whether block has return statement  
            last_statement: The final statement in the block
            node: Block node for error reporting
            evaluability: Block evaluability classification
            
        Returns:
            Type of the expression block result
        """
        # Session 1: Foundation with existing behavior
        # TODO Session 2: Add function call and conditional detection
        # TODO Session 3: Add comptime type preservation for COMPILE_TIME blocks
        # TODO Session 3: Add explicit context validation for RUNTIME blocks
        
        # For now, maintain existing behavior while logging evaluability classification
        # This ensures no regressions while building the foundation
        
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
                # Session 1: Use existing behavior (current function return type as context)
                # Session 3 will enhance this with evaluability-aware type resolution
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
    # BLOCK EVALUABILITY DETECTION INFRASTRUCTURE (Session 1)
    # =========================================================================

    def _classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
        """
        Classify block as compile-time or runtime evaluable.
        
        This is the foundation for the enhanced unified block system that determines
        whether expression blocks can preserve comptime types or require explicit context.
        
        Compile-time evaluable criteria:
        - All operations involve only comptime literals
        - NO conditional expressions (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
        - No runtime function calls (will be added in Session 2)
        - No runtime variable usage
        - All computations can be evaluated at compile-time
        
        Args:
            statements: List of statements in the block
            
        Returns:
            BlockEvaluability.COMPILE_TIME if block can preserve comptime types
            BlockEvaluability.RUNTIME if block requires explicit context
        """
        # Session 1: Basic detection (function calls and conditionals will be added in Session 2)
        
        # Check for concrete variable usage (mixing comptime + concrete = runtime)
        if self._has_runtime_variables(statements):
            return BlockEvaluability.RUNTIME
            
        # If all operations are comptime-only, block is compile-time evaluable
        if self._has_comptime_only_operations(statements):
            return BlockEvaluability.COMPILE_TIME
            
        # Default to runtime for safety (unknown cases should require explicit context)
        return BlockEvaluability.RUNTIME

    def _has_comptime_only_operations(self, statements: List[Dict]) -> bool:
        """
        Check if all operations in the block use only comptime types.
        
        Comptime operations include:
        - Literal values (42, 3.14, "string", true/false)
        - Arithmetic on comptime types (42 + 100, 3.14 * 2.0)
        - Variable declarations with comptime initializers
        - Variable references to other comptime-only variables
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if all operations are comptime-only, False otherwise
        """
        for statement in statements:
            if not self._statement_has_comptime_only_operations(statement):
                return False
        return True

    def _statement_has_comptime_only_operations(self, statement: Dict) -> bool:
        """
        Check if a single statement contains only comptime operations.
        
        Args:
            statement: Statement AST node to analyze
            
        Returns:
            True if statement uses only comptime operations, False otherwise
        """
        stmt_type = statement.get("type")
        
        # Variable declarations: check initializer
        if stmt_type in [NodeType.VAL_DECLARATION.value, NodeType.MUT_DECLARATION.value]:
            value = statement.get("value")
            if value and value != "undef":
                return self._expression_has_comptime_only_operations(value)
            return True  # undef is considered comptime
            
        # Assign statements: check the assigned expression  
        elif stmt_type == NodeType.ASSIGN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_has_comptime_only_operations(value)
            return False
            
        # Assignment statements: check the assigned expression
        elif stmt_type == NodeType.ASSIGNMENT_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_has_comptime_only_operations(value)
            return False
            
        # Return statements: check the returned expression
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_has_comptime_only_operations(value)
            return True  # bare return is comptime
            
        # Other statement types will be handled in Session 2 (function calls, conditionals, etc.)
        # For now, assume they're runtime to be safe
        return False

    def _expression_has_comptime_only_operations(self, expression: Dict) -> bool:
        """
        Check if an expression contains only comptime operations.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression is comptime-only, False otherwise
        """
        expr_type = expression.get("type")
        
        # Comptime literals
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value]:
            return True
            
        # Other literals (string, bool) are concrete but considered comptime for this analysis
        if expr_type == NodeType.LITERAL.value:
            return True
            
        # Variable references: check if variable has comptime type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info:
                    # If variable has comptime type, it's comptime-only
                    var_type = symbol_info.type
                    return var_type in [HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT]
            return False
            
        # Binary operations: both operands must be comptime-only
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                return (self._expression_has_comptime_only_operations(left) and
                       self._expression_has_comptime_only_operations(right))
            return False
            
        # Unary operations: operand must be comptime-only
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand:
                return self._expression_has_comptime_only_operations(operand)
            return False
            
        # Explicit conversions: operand must be comptime-only (though result becomes concrete)
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand:
                return self._expression_has_comptime_only_operations(operand)
            return False
            
        # Block expressions: recursively analyze (this enables nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self._has_comptime_only_operations(statements)
            
        # Function calls and conditionals will be handled in Session 2
        # For now, assume they're runtime
        return False

    def _has_runtime_variables(self, statements: List[Dict]) -> bool:
        """
        Check if the block uses variables with concrete (runtime) types.
        
        This detects mixing of comptime and concrete types, which requires
        explicit type context for proper resolution.
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if block uses concrete variables, False if only comptime variables
        """
        for statement in statements:
            if self._statement_has_runtime_variables(statement):
                return True
        return False

    def _statement_has_runtime_variables(self, statement: Dict) -> bool:
        """
        Check if a statement uses concrete (runtime) variables.
        
        Args:
            statement: Statement AST node to analyze
            
        Returns:
            True if statement uses concrete variables, False otherwise  
        """
        stmt_type = statement.get("type")
        
        # Variable declarations: check if explicitly typed with concrete type
        if stmt_type in [NodeType.VAL_DECLARATION.value, NodeType.MUT_DECLARATION.value]:
            # If explicit type annotation is concrete, it's runtime
            type_annotation = statement.get("type_annotation")
            if type_annotation:
                # Parse type annotation to check if it's concrete
                return is_concrete_type(type_annotation)
                
            # Check initializer expression for concrete variable usage
            value = statement.get("value")
            if value and value != "undef":
                return self._expression_has_runtime_variables(value)
            return False
            
        # Assign and assignment statements: check expressions
        elif stmt_type in [NodeType.ASSIGN_STATEMENT.value, NodeType.ASSIGNMENT_STATEMENT.value]:
            value = statement.get("value")
            if value:
                return self._expression_has_runtime_variables(value)
            return False
            
        # Return statements: check expression
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_has_runtime_variables(value)
            return False
            
        return False

    def _expression_has_runtime_variables(self, expression: Dict) -> bool:
        """
        Check if an expression uses concrete (runtime) variables.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression uses concrete variables, False otherwise
        """
        expr_type = expression.get("type")
        
        # Literals are not runtime variables
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value, 
                        NodeType.LITERAL.value]:
            return False
            
        # Variable references: check if variable has concrete type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info:
                    var_type = symbol_info.type
                    # Concrete types indicate runtime variables
                    return var_type not in [HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT]
            return False
            
        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                return (self._expression_has_runtime_variables(left) or
                       self._expression_has_runtime_variables(right))
            return False
            
        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand:
                return self._expression_has_runtime_variables(operand)
            return False
            
        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand:
                return self._expression_has_runtime_variables(operand)
            return False
            
        # Block expressions: recursively analyze
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self._has_runtime_variables(statements)
            
        return False
