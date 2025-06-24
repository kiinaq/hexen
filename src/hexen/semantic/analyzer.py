"""
Hexen Semantic Analyzer

Main semantic analysis implementation for Hexen language.
Performs semantic analysis on the AST including type checking,
symbol table management, and validation.
"""

from typing import Dict, List, Optional

from ..ast_nodes import NodeType
from .types import HexenType
from .symbol_table import SymbolTable
from .errors import SemanticError
from .binary_ops_analyzer import BinaryOpsAnalyzer
from .unary_ops_analyzer import UnaryOpsAnalyzer
from .declaration_analyzer import DeclarationAnalyzer
from .assignment_analyzer import AssignmentAnalyzer
from .return_analyzer import ReturnAnalyzer
from .block_analyzer import BlockAnalyzer
from .type_util import (
    parse_type,
    infer_type_from_value,
    can_coerce,
    is_precision_loss_operation,
)


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
        self.current_function_return_type: Optional[HexenType] = None

        # Context tracking for unified block concept
        self.block_context: List[str] = []  # Track: "function", "expression", etc.

        # Initialize all specialized analyzers
        self._initialize_analyzers()

    def _initialize_analyzers(self):
        """Initialize all specialized analyzers with callbacks."""
        # Initialize binary operations analyzer with callbacks
        self.binary_ops = BinaryOpsAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
        )

        # Initialize unary operations analyzer with callbacks
        self.unary_ops = UnaryOpsAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
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
        )

        # Initialize assignment analyzer with callbacks
        self.assignment_analyzer = AssignmentAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            lookup_symbol_callback=self.symbol_table.lookup_symbol,
        )

        # Initialize return analyzer with callbacks
        self.return_analyzer = ReturnAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
            get_block_context_callback=lambda: self.block_context,
            get_current_function_return_type_callback=lambda: self.current_function_return_type,
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

        Current structure: program contains list of functions
        Future: May contain global variables, imports, type definitions, etc.

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
        - expression_statement: Expression evaluation
        """
        stmt_type = node.get("type")

        if stmt_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
            self.declaration_analyzer.analyze_declaration(node)
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            self.return_analyzer.analyze_return_statement(node)
        elif stmt_type == NodeType.ASSIGNMENT_STATEMENT.value:
            self.assignment_analyzer.analyze_assignment_statement(node)
        elif stmt_type == NodeType.BLOCK.value:
            # Statement block - standalone execution (like void functions)
            self._analyze_block(node, node, context="statement")
        else:
            self._error(f"Unknown statement type: {stmt_type}", node)

    def _analyze_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze an expression and return its type.

        Args:
            node: Expression AST node
            target_type: Optional target type for context-guided resolution

        Returns HexenType.UNKNOWN for invalid expressions.
        """
        expr_type = node.get("type")
        return self._dispatch_expression_analysis(expr_type, node, target_type)

    def _dispatch_expression_analysis(
        self, expr_type: str, node: Dict, target_type: Optional[HexenType]
    ) -> HexenType:
        """Simple expression type dispatcher."""
        if expr_type == NodeType.TYPE_ANNOTATED_EXPRESSION.value:
            # Handle type annotated expressions - Phase 1 implementation
            return self._analyze_type_annotated_expression(node, target_type)
        elif expr_type == NodeType.LITERAL.value:
            return infer_type_from_value(node)
        elif expr_type == NodeType.IDENTIFIER.value:
            return self._analyze_identifier(node)
        elif expr_type == NodeType.BLOCK.value:
            return self._analyze_block(node, node, context="expression")
        elif expr_type == NodeType.BINARY_OPERATION.value:
            return self._analyze_binary_operation(node, target_type)
        elif expr_type == NodeType.UNARY_OPERATION.value:
            return self._analyze_unary_operation(node, target_type)
        else:
            self._error(f"Unknown expression type: {expr_type}", node)
            return HexenType.UNKNOWN

    def _analyze_type_annotated_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze type annotated expressions implementing "Explicit Danger, Implicit Safety".

        Key rules:
        1. Type annotation must match the target type exactly (left-hand side)
        2. Type annotations require explicit left-side types
        3. Type annotations enable precision loss operations (acknowledgment)
        4. Type annotations are NOT conversions, they're acknowledgments
        """
        expr = node.get("expression")
        type_annotation = node.get("type_annotation")
        annotated_type = parse_type(type_annotation)

        # Rule: Type annotations require explicit left-side types
        if target_type is None:
            self._error(
                "Type annotation requires explicit left side type. "
                f"Add explicit type: 'val result : {annotated_type.value} = ...'",
                node,
            )
            return HexenType.UNKNOWN

        # Rule: Type annotation must match target type exactly
        if annotated_type != target_type:
            self._error(
                f"Type annotation must match variable's declared type: "
                f"expected {target_type.value}, got {annotated_type.value}",
                node,
            )
            return HexenType.UNKNOWN

        # Analyze the expression with the annotated type as target
        expr_type = self._analyze_expression(expr, annotated_type)

        # Type annotation enables precision loss operations (acknowledgment)
        # This means we allow operations that would normally be rejected
        if expr_type != HexenType.UNKNOWN:
            # Check if this is a precision loss operation that needs acknowledgment
            if is_precision_loss_operation(expr_type, annotated_type):
                # Type annotation acknowledged - allow the operation
                return annotated_type

            # For safe operations, still check coercion
            if not can_coerce(expr_type, annotated_type):
                self._error(
                    f"Type mismatch: expression of type {expr_type.value} cannot be coerced to {annotated_type.value}",
                    node,
                )
                return HexenType.UNKNOWN
        else:
            # If expression analysis failed (e.g., due to undefined variables),
            # the type annotation structure is still valid - return the annotated type
            # This allows type annotation validation to work even when expressions have errors
            pass

        return annotated_type

    def _analyze_identifier(self, node: Dict) -> HexenType:
        """
        Analyze an identifier reference (variable usage).

        Validation steps:
        1. Check identifier has name
        2. Handle special case: undef keyword
        3. Look up symbol in symbol table
        4. Check if variable is initialized
        5. Mark symbol as used
        6. Return symbol type

        This prevents use-before-definition and tracks variable usage.
        """
        name = node.get("name")
        if not name:
            self._error("Identifier missing name", node)
            return HexenType.UNKNOWN

        # Special case: undef is a keyword, not a variable
        if name == "undef":
            return HexenType.UNINITIALIZED

        # Look up symbol in symbol table
        symbol = self.symbol_table.lookup_symbol(name)
        if not symbol:
            self._error(f"Undefined variable: '{name}'", node)
            return HexenType.UNKNOWN

        # Check if variable is initialized (prevents use of undef variables)
        if not symbol.initialized:
            self._error(f"Use of uninitialized variable: '{name}'", node)
            return HexenType.UNKNOWN

        # Mark symbol as used for dead code analysis
        symbol.used = True
        return symbol.type

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

    def _set_function_context(self, name: str, return_type: HexenType) -> None:
        """Set the current function context for return type validation."""
        self.symbol_table.current_function = name
        self.current_function_return_type = return_type

    def _clear_function_context(self) -> None:
        """Clear function context."""
        self.current_function = None

    def _get_current_scope(self):
        """Return the current (innermost) scope dictionary from the symbol table."""
        return self.symbol_table.scopes[-1]
