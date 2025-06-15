"""
Hexen Semantic Analyzer

Main semantic analysis implementation for Hexen language.
Performs semantic analysis on the AST including type checking,
symbol table management, and validation.
"""

from typing import Dict, List, Optional

from .types import HexenType, Mutability
from .symbol_table import SymbolTable
from .errors import SemanticError
from .binary_ops import BinaryOpsAnalyzer
from .declaration_analyzer import DeclarationAnalyzer
from .type_util import (
    is_numeric_type,
    can_coerce,
    parse_type,
    infer_type_from_value,
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

        # Initialize binary operations analyzer with callbacks
        self.binary_ops = BinaryOpsAnalyzer(
            error_callback=self._error,
            analyze_expression_callback=self._analyze_expression,
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
        if node.get("type") != "program":
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
        Smart unified block analysis - ALL blocks manage scope, context determines return rules.

        ALL blocks:
        - Manage their own scope (complete unification)
        - Validate return types

        Context determines return statement rules:
        - "expression": Requires return as final statement (value computation)
        - "statement": No return statements required (statement execution)
        - Default + non-void function: Allows returns anywhere, expects some return
        - Default + void function: No return statements required (statement execution)

        This balances unification (scope) with context-specific needs (return rules).
        """
        if body.get("type") != "block":
            self._error(f"Expected block node, got {body.get('type')}")
            return HexenType.UNKNOWN if context == "expression" else None

        # ALL blocks manage their own scope (unified)
        self.symbol_table.enter_scope()

        # Track context for return handling
        is_expression_block = context == "expression"
        is_statement_block = context == "statement"
        is_void_function = self.current_function_return_type == HexenType.VOID

        if is_expression_block:
            self.block_context.append("expression")

        # Analyze all statements with context-specific return rules
        statements = body.get("statements", [])
        last_return_stmt = None
        block_return_type = None

        for i, stmt in enumerate(statements):
            if stmt.get("type") == "return_statement":
                if is_void_function:
                    # Let _analyze_return_statement handle void function validation
                    # to avoid duplicate error reporting
                    pass
                elif is_statement_block:
                    # Statement blocks can have returns that match function signature
                    # This allows returning from the function within a statement block
                    pass  # Will be validated by _analyze_return_statement
                elif is_expression_block:
                    # Expression blocks: return must be last
                    if i == len(statements) - 1:
                        last_return_stmt = stmt
                    else:
                        self._error(
                            "Return statement must be the last statement in expression block",
                            stmt,
                        )
                # Non-void function blocks: returns allowed anywhere (no restriction)

            self._analyze_statement(stmt)

        # Context-specific return validation
        if is_expression_block:
            # Expression blocks must end with return statement
            if not last_return_stmt:
                self._error("Expression block must end with a return statement", node)
                block_return_type = HexenType.UNKNOWN
            else:
                # Get the type from the return statement's value
                return_value = last_return_stmt.get("value")
                if return_value:
                    block_return_type = self._analyze_expression(
                        return_value, self.current_function_return_type
                    )
                else:
                    block_return_type = HexenType.UNKNOWN

        # ALL blocks clean up their own scope (unified)
        self.symbol_table.exit_scope()

        # Expression context cleanup
        if is_expression_block:
            self.block_context.pop()

        # Context determines what to do with computed type
        return block_return_type if is_expression_block else None

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

        if stmt_type in ["val_declaration", "mut_declaration"]:
            self.declaration_analyzer.analyze_declaration(node)
        elif stmt_type == "return_statement":
            self._analyze_return_statement(node)
        elif stmt_type == "assignment_statement":
            self._analyze_assignment_statement(node)
        elif stmt_type == "block":
            # Statement block - standalone execution (like void functions)
            self._analyze_block(node, node, context="statement")
        else:
            self._error(f"Unknown statement type: {stmt_type}", node)

    def _analyze_return_statement(self, node: Dict):
        """
        Analyze a return statement with support for bare returns.

        Context-aware validation:
        - Default context: Return type must match function return type
        - Expression context: Return determines block's type (must have value)
        - Bare returns: Only allowed in void functions or statement blocks
        - No valid context: Error - return statements need context
        """
        value = node.get("value")

        # Handle bare return (return;)
        if value is None:
            # Bare returns are only valid in void functions or statement blocks
            if self.block_context and self.block_context[-1] == "expression":
                # Expression blocks must return a value
                self._error("Expression block return statement must have a value", node)
                return
            elif self.current_function_return_type == HexenType.VOID:
                # Void functions can have bare returns
                return
            elif self.current_function_return_type:
                # Non-void functions cannot have bare returns
                self._error(
                    f"Function returning {self.current_function_return_type.value} "
                    f"cannot have bare return statement",
                    node,
                )
                return
            else:
                # No valid context for return statement
                self._error("Return statement outside valid context", node)
                return

        # Handle return with value (return expression;)
        # Analyze the return value expression
        return_type = self._analyze_expression(value, self.current_function_return_type)

        # Simplified context-aware validation
        if self.block_context and self.block_context[-1] == "expression":
            # We're in an expression block context - return type determines block type
            # No additional validation needed here, the block will handle it
            pass
        elif self.current_function_return_type:
            # We're in default context (function body) - validate against function signature
            if self.current_function_return_type == HexenType.VOID:
                # Void functions cannot have return values
                self._error("Void function cannot return a value", node)
            elif return_type != HexenType.UNKNOWN:
                # Use coercion for return type checking
                if not can_coerce(return_type, self.current_function_return_type):
                    self._error(
                        f"Return type mismatch: expected {self.current_function_return_type.value}, "
                        f"got {return_type.value}",
                        node,
                    )
        else:
            # No valid context for return statement
            self._error("Return statement outside valid context", node)

    def _analyze_assignment_statement(self, node: Dict):
        """
        Analyze an assignment statement with comprehensive validation and coercion.

        Assignment rules:
        - Target must be a declared variable
        - Target must be mutable (mut, not val)
        - Value type must be coercible to target type (using coercion)
        - Supports self-assignment (x = x)
        - No chained assignment (a = b = c)

        This validates our mutability system and type checking robustness with elegant coercion.
        """
        target_name = node.get("target")
        value = node.get("value")

        if not target_name:
            self._error("Assignment target missing", node)
            return

        if not value:
            self._error("Assignment value missing", node)
            return

        # Look up target variable in symbol table
        symbol = self.symbol_table.lookup_symbol(target_name)
        if not symbol:
            self._error(f"Undefined variable: '{target_name}'", node)
            return

        # Check mutability - only mut variables can be assigned to
        if symbol.mutability == Mutability.IMMUTABLE:
            self._error(f"Cannot assign to immutable variable '{target_name}'", node)
            return

        # Analyze the value expression
        value_type = self._analyze_expression(value, symbol.type)

        # Check type compatibility with coercion
        if value_type != HexenType.UNKNOWN:
            if not can_coerce(value_type, symbol.type):
                self._error(
                    f"Type mismatch in assignment: variable '{target_name}' is {symbol.type.value}, "
                    f"but assigned value is {value_type.value}",
                    node,
                )
                return

        # Mark the symbol as used (assignment counts as usage)
        symbol.used = True

        # Mark the symbol as initialized (assignment initializes uninitialized variables)
        symbol.initialized = True

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

        if expr_type == "type_annotated_expression":
            # Handle type annotated expressions
            expr = node.get("expression")
            type_annotation = node.get("type_annotation")
            annotated_type = parse_type(type_annotation)

            # Analyze the expression with the annotated type as target
            expr_type = self._analyze_expression(expr, annotated_type)

            # Validate that the expression type can be coerced to the annotated type
            if expr_type != HexenType.UNKNOWN and not can_coerce(
                expr_type, annotated_type
            ):
                self._error(
                    f"Type mismatch: expression of type {expr_type.value} cannot be coerced to {annotated_type.value}",
                    node,
                )
                return HexenType.UNKNOWN

            return annotated_type
        elif expr_type == "literal":
            return infer_type_from_value(node)
        elif expr_type == "identifier":
            return self._analyze_identifier(node)
        elif expr_type == "block":
            return self._analyze_block(node, node, context="expression")
        elif expr_type == "binary_operation":
            return self._analyze_binary_operation(node, target_type)
        elif expr_type == "unary_operation":
            return self._analyze_unary_operation(node, target_type)
        else:
            self._error(f"Unknown expression type: {expr_type}", node)
            return HexenType.UNKNOWN

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
        Analyze a unary operation with context-guided type resolution.

        Handles:
        - Unary minus (-): Negates numeric values
        - Logical not (!): Negates boolean values
        """
        operator = node.get("operator")
        operand = node.get("operand")

        if not operator or not operand:
            self._error("Invalid unary operation", node)
            return HexenType.UNKNOWN

        # Analyze operand with context
        operand_type = self._analyze_expression(operand, target_type)

        if operand_type == HexenType.UNKNOWN:
            return HexenType.UNKNOWN

        # Handle unary minus (-)
        if operator == "-":
            # Only allow unary minus on numeric types
            if not is_numeric_type(operand_type):
                self._error(
                    f"Unary minus (-) requires numeric operand, got {operand_type.value}",
                    node,
                )
                return HexenType.UNKNOWN

            # For comptime types, preserve them
            if operand_type == HexenType.COMPTIME_INT:
                return HexenType.COMPTIME_INT
            if operand_type == HexenType.COMPTIME_FLOAT:
                return HexenType.COMPTIME_FLOAT

            # For concrete types, return the same type
            return operand_type

        # Handle logical not (!)
        elif operator == "!":
            if operand_type != HexenType.BOOL:
                self._error(
                    f"Logical not (!) requires boolean operand, got {operand_type.value}",
                    node,
                )
                return HexenType.UNKNOWN
            return HexenType.BOOL

        else:
            self._error(f"Unknown unary operator: {operator}", node)
            return HexenType.UNKNOWN

    def _set_function_context(self, name: str, return_type: HexenType) -> None:
        """Set the current function context for return type validation."""
        self.symbol_table.current_function = name
        self.current_function_return_type = return_type

    def _clear_function_context(self) -> None:
        """Clear the current function context."""
        self.symbol_table.current_function = None
        self.current_function_return_type = None

    def _get_current_scope(self):
        """Return the current (innermost) scope dictionary from the symbol table."""
        return self.symbol_table.scopes[-1]
