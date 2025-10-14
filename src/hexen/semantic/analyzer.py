"""
Hexen Semantic Analyzer

Main semantic analysis implementation for Hexen language.
Performs semantic analysis on the AST including type checking,
symbol table management, and validation.
"""

from typing import Dict, List, Optional, Union

from .assignment_analyzer import AssignmentAnalyzer
from .binary_ops_analyzer import BinaryOpsAnalyzer
from .block_analyzer import BlockAnalyzer
from .comptime import ComptimeAnalyzer
from .conversion_analyzer import ConversionAnalyzer
from .declaration_analyzer import DeclarationAnalyzer
from .errors import SemanticError
from .expression_analyzer import ExpressionAnalyzer
from .function_analyzer import FunctionAnalyzer
from .return_analyzer import ReturnAnalyzer
from .symbol_table import SymbolTable
from .types import HexenType, ConcreteArrayType
from .unary_ops_analyzer import UnaryOpsAnalyzer
from ..ast_nodes import NodeType


class SemanticAnalyzer:
    """
    Main semantic analyzer that validates AST semantics.

    Analysis phases:
    1. Symbol table construction (declarations)
    2. Type checking and inference
    3. Use-before-definition validation
    4. Mutability enforcement
    5. Return type validation

    Design principles:
    - Error recovery: Collect all errors before stopping (batch error reporting)
    - Comprehensive: Check all semantic rules
    - Extensible: Easy to add new checks
    - Informative: Provide helpful error messages
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []  # Collect all errors for batch reporting
        self.current_function_return_type: Optional[
            Union[HexenType, ConcreteArrayType]
        ] = None

        # Context tracking for unified block concept
        self.block_context: List[str] = []  # Track: "function", "expression", etc.

        # Parameter modification tracking for mut parameter enforcement (Week 2 Task 8)
        self.modified_mut_parameters: set = set()  # Track which mut parameters were modified in current function

        # Initialize comptime analyzer first (needed by other analyzers)
        self.comptime_analyzer = ComptimeAnalyzer(self.symbol_table)

        # Initialize all specialized analyzers
        self._initialize_analyzers()

    def _initialize_analyzers(self):
        """Initialize all specialized analyzers with callbacks."""
        # Initialize binary operations analyzer with callbacks
        self.binary_ops = BinaryOpsAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            comptime_analyzer=self.comptime_analyzer,
        )

        # Initialize unary operations analyzer with callbacks
        self.unary_ops = UnaryOpsAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            comptime_analyzer=self.comptime_analyzer,
        )

        # Initialize block analyzer with callbacks
        self.block_analyzer = BlockAnalyzer(
            error_callback=self._error,
            analyze_statement_callback=self._analyze_statement,
            analyze_expression_callback=self._analyze_expression,
            symbol_table=self.symbol_table,
            get_current_function_return_type_callback=lambda: self.current_function_return_type,
            block_context_stack=self.block_context,
        )

        # Initialize declaration analyzer with callbacks
        self.declaration_analyzer = DeclarationAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            symbol_table_callback=self.symbol_table.declare_symbol,
            lookup_symbol_callback=self.symbol_table.lookup_symbol,
            analyze_block_callback=self._analyze_block,
            set_function_context_callback=self._set_function_context,
            clear_function_context_callback=self._clear_function_context,
            get_current_scope_callback=self._get_current_scope,
            symbol_table=self.symbol_table,
            comptime_analyzer=self.comptime_analyzer,
            get_modified_parameters_callback=lambda: self.modified_mut_parameters,
        )

        # Initialize assignment analyzer with callbacks
        self.assignment_analyzer = AssignmentAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            lookup_symbol_callback=self.symbol_table.lookup_symbol,
            comptime_analyzer=self.comptime_analyzer,
            is_parameter_callback=self.symbol_table.is_parameter,
            get_parameter_info_callback=self.symbol_table.get_parameter_info,
            track_parameter_modification_callback=self._track_parameter_modification,
        )

        # Initialize return analyzer with callbacks
        self.return_analyzer = ReturnAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            get_block_context_callback=lambda: self.block_context,
            get_current_function_return_type_callback=lambda: self.current_function_return_type,
            comptime_analyzer=self.comptime_analyzer,
        )

        # Initialize conversion analyzer with callbacks
        self.conversion_analyzer = ConversionAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            parse_array_type_callback=self.declaration_analyzer._parse_array_type_annotation,
        )

        # Initialize function analyzer with callbacks
        self.function_analyzer = FunctionAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            lookup_function_callback=self.symbol_table.lookup_function,
        )

        # Initialize expression analyzer with callbacks
        self.expression_analyzer = ExpressionAnalyzer(
            error_callback=self._error,
            analyze_block_callback=self._analyze_block,
            analyze_binary_operation_callback=self._analyze_binary_operation,
            analyze_unary_operation_callback=self._analyze_unary_operation,
            lookup_symbol_callback=self.symbol_table.lookup_symbol,
            analyze_function_call_callback=self._analyze_function_call,
            conversion_analyzer=self.conversion_analyzer,
            comptime_analyzer=self.comptime_analyzer,
        )

    def analyze(self, ast: Dict) -> List[SemanticError]:
        """
        Main entry point for semantic analysis.

        Returns list of all semantic errors found.
        Empty list means no errors (analysis successful).

        Error handling strategy:
        - Catch and convert unexpected exceptions to semantic errors
        - Continue analysis after errors to find as many issues as possible
        - Reset error list for fresh analysis
        """
        self.errors.clear()
        try:
            self._analyze_program(ast)
        except Exception as e:
            # Convert unexpected errors to semantic errors for consistent error handling
            self.errors.append(SemanticError(f"Internal analysis error: {e}"))

        return self.errors

    def _error(self, message: str, node: Optional[Dict] = None):
        """
        Record a semantic error for later reporting.

        Centralized error collection allows:
        - Batch error reporting
        - Continued analysis after errors
        - Consistent error formatting
        """
        self.errors.append(SemanticError(message, node))

    def _analyze_program(self, node: Dict):
        """
        Analyze the root program node.

        Current structure: program contains list of functions and top-level statements
        Future: May contain imports, type definitions, etc.

        Validates:
        - Node type is correct
        - All declarations are valid (unified analysis)
        """
        if node.get("type") != NodeType.PROGRAM.value:
            self._error(f"Expected program node, got {node.get('type')}")
            return

        # Analyze all functions in the program using unified declaration analysis
        for func in node.get("functions", []):
            self._analyze_declaration(func)

        # Analyze top-level statements (val/mut declarations, etc.)
        for stmt in node.get("statements", []):
            self._analyze_statement(stmt)

    # =============================================================================
    # UNIFIED DECLARATION ANALYSIS FRAMEWORK
    # =============================================================================

    def _analyze_declaration(self, node: Dict) -> None:
        """
        Unified declaration analysis for functions, val, and mut declarations.
        Delegates to DeclarationAnalyzer.
        """
        self.declaration_analyzer.analyze_declaration(node)

    def _analyze_block(
        self, body: Dict, node: Dict, context: str = None
    ) -> Optional[HexenType]:
        """
        Unified block analysis - delegates to BlockAnalyzer.

        Implements the unified block system (UNIFIED_BLOCK_SYSTEM.md):
        - ALL blocks manage scope uniformly
        - Context determines return statement rules
        - Expression blocks produce values, statement blocks execute code
        """
        return self.block_analyzer.analyze_block(body, node, context)

    def _analyze_statement(self, node: Dict):
        """
        Dispatch statement analysis to appropriate handler.

        Currently supported statement types:
        - val_declaration: Immutable variable declaration (unified analysis)
        - mut_declaration: Mutable variable declaration (unified analysis)
        - return_statement: Function return
        - block: Statement block (standalone execution, like void functions)
        - assignment: Variable assignment

        Future statement types:
        - if_statement: Conditional execution
        - while_statement: Loop execution
        - function_call_statement: Function call evaluation
        """
        stmt_type = node.get("type")

        if stmt_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
            self.declaration_analyzer.analyze_declaration(node)
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            self.return_analyzer.analyze_return_statement(node)
        elif stmt_type == NodeType.ASSIGN_STATEMENT.value:
            self._analyze_assign_statement(node)
        elif stmt_type == NodeType.ASSIGNMENT_STATEMENT.value:
            self.assignment_analyzer.analyze_assignment_statement(node)
        elif stmt_type == NodeType.BLOCK.value:
            # Statement block - standalone execution (like void functions)
            self._analyze_block(node, node, context="statement")
        elif stmt_type == NodeType.CONDITIONAL_STATEMENT.value:
            self._analyze_conditional_statement(node)
        elif stmt_type == NodeType.FUNCTION_CALL_STATEMENT.value:
            self._analyze_function_call_statement(node)
        else:
            self._error(f"Unknown statement type: {stmt_type}", node)

    def _analyze_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze an expression and return its type by delegating to ExpressionAnalyzer.

        Args:
            node: Expression AST node
            target_type: Optional target type for context-guided resolution

        Returns HexenType.UNKNOWN for invalid expressions.
        """
        return self.expression_analyzer.analyze_expression(node, target_type)

    def _analyze_binary_operation(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a binary operation by delegating to BinaryOpsAnalyzer.
        """
        return self.binary_ops.analyze_binary_operation(node, target_type)

    def _analyze_unary_operation(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a unary operation by delegating to UnaryOpsAnalyzer.
        """
        return self.unary_ops.analyze_unary_operation(node, target_type)

    def _analyze_function_call(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a function call by delegating to FunctionAnalyzer.
        """
        return self.function_analyzer.analyze_function_call(node, target_type)

    def _analyze_assign_statement(self, node: Dict) -> None:
        """
        Analyze assign statement - validates context and expression type.

        Assign statements are only valid in expression blocks and assign
        the expression value to the block's target.
        """
        # Check if we're in an expression block context
        if not self.block_context or self.block_context[-1] != "expression":
            self._error("'assign' statement only valid in expression blocks", node)
            return

        # Analyze the expression being assigned
        value = node.get("value")
        if value:
            # No specific target type since expression blocks adapt to context
            self._analyze_expression(value)
        else:
            self._error("'assign' statement requires an expression", node)

    def _set_function_context(
        self, name: str, return_type: Union[HexenType, ConcreteArrayType]
    ) -> None:
        """Set the current function context for return type validation."""
        self.symbol_table.current_function = name
        self.current_function_return_type = return_type
        # Clear parameter modification tracking for new function (Week 2 Task 8)
        self.modified_mut_parameters.clear()

    def _clear_function_context(self) -> None:
        """Clear function context."""
        self.current_function = None
        # Clear parameter modification tracking (Week 2 Task 8)
        self.modified_mut_parameters.clear()

    def _track_parameter_modification(self, parameter_name: str) -> None:
        """
        Track that a mut parameter has been modified (Week 2 Task 8).

        This is used to enforce the rule that functions modifying mut parameters
        must return the modified value to make pass-by-value semantics explicit.
        """
        self.modified_mut_parameters.add(parameter_name)

    def _get_current_scope(self):
        """Return the current (innermost) scope dictionary from the symbol table."""
        return self.symbol_table.scopes[-1]

    def _analyze_conditional_statement(self, node: Dict) -> None:
        """
        Analyze conditional statement (if/else if/else) in statement context.

        Statement context analysis:
        1. Validate condition is boolean type
        2. Analyze each branch as statement block with scope isolation
        3. Support early returns within branches
        """
        # 1. Analyze condition - must be bool type
        condition = node.get("condition")
        if not condition:
            self._error("Conditional statement missing condition", node)
            return

        condition_type = self._analyze_expression(condition)
        if condition_type != HexenType.BOOL:
            self._error(
                f"Condition must be of type bool, got {condition_type.name.lower()}",
                condition,
            )

        # 2. Analyze if branch as statement block
        if_branch = node.get("if_branch")
        if if_branch:
            self.symbol_table.enter_scope()
            try:
                self._analyze_block(if_branch, node, context="statement")
            finally:
                self.symbol_table.exit_scope()

        # 3. Analyze each else clause
        else_clauses = node.get("else_clauses", [])
        for else_clause in else_clauses:
            # Analyze else-if condition if present
            clause_condition = else_clause.get("condition")
            if clause_condition:
                clause_condition_type = self._analyze_expression(clause_condition)
                if clause_condition_type != HexenType.BOOL:
                    self._error(
                        f"Condition must be of type bool, got {clause_condition_type.name.lower()}",
                        clause_condition,
                    )

            # Analyze else clause branch as statement block
            clause_branch = else_clause.get("branch")
            if clause_branch:
                self.symbol_table.enter_scope()
                try:
                    self._analyze_block(clause_branch, node, context="statement")
                finally:
                    self.symbol_table.exit_scope()

    def _analyze_function_call_statement(self, node: Dict) -> None:
        """
        Analyze function call statement - validates function call in statement context.

        Function call statements are used for side effects like calling void functions
        or functions where the return value is intentionally discarded.
        The result type is discarded since it's used in statement context.
        """
        function_call = node.get("function_call")
        if function_call:
            # Analyze the function call - no specific target type needed
            self._analyze_expression(function_call)
        else:
            self._error("Function call statement requires a function call", node)
