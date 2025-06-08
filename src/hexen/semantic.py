"""
Semantic analyzer for Hexen

Performs semantic analysis on the AST including:
- Symbol table management and scope tracking
- Type checking and type inference
- Mutability enforcement (val vs mut)
- Use-before-definition validation
- undef handling and validation

This module implements the second phase of the Hexen compiler pipeline:
1. Parser creates AST from source code
2. SemanticAnalyzer validates semantics and types
3. (Future) Code generator produces LLVM IR

Design Philosophy:
- Error recovery: Collect all errors before stopping (batch error reporting)
- Explicit over implicit: Clear error messages
- Type safety: Prevent runtime type errors
- Immutable-by-default: val vs mut distinction enforced
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class HexenType(Enum):
    """
    Hexen's type system with explicit support for type inference and uninitialized states.

    Design decisions:
    - I32 as default integer type (following Rust conventions)
    - UNKNOWN for type inference failures (not user-facing)
    - UNINITIALIZED for explicit undef values (different from null/None)

    Future extensions:
    - User-defined types (structs, enums)
    - Generic types
    - Function types
    """

    I32 = "i32"
    I64 = "i64"
    F64 = "f64"
    STRING = "string"
    UNKNOWN = "unknown"  # For type inference failures - internal use only
    UNINITIALIZED = "undef"  # For explicit undef values - different from null


class Mutability(Enum):
    """
    Variable mutability levels following Rust's ownership model.

    IMMUTABLE (val):
    - Cannot be reassigned after initialization
    - Prevents accidental mutation bugs
    - Default choice encourages functional programming style

    MUTABLE (mut):
    - Can be reassigned multiple times
    - Requires explicit opt-in for clarity
    - Used when mutation is genuinely needed
    """

    IMMUTABLE = "val"  # val variables - cannot be reassigned
    MUTABLE = "mut"  # mut variables - can be reassigned


@dataclass
class Symbol:
    """
    Represents a symbol in the symbol table with full metadata.

    Tracks everything needed for semantic analysis:
    - Type information for type checking
    - Mutability for assignment validation
    - Initialization state for use-before-def checking
    - Usage tracking for dead code elimination

    Design note: Using dataclass for clean syntax while maintaining
    the ability to add computed properties later.
    """

    name: str
    type: HexenType
    mutability: Mutability
    declared_line: Optional[int] = None  # For better error reporting (future)
    initialized: bool = True  # False for undef variables - prevents use-before-init
    used: bool = False  # Track usage for dead code warnings


class SymbolTable:
    """
    Manages symbols and scopes using a scope stack.

    Implementation details:
    - Stack-based scope management (LIFO)
    - Inner scopes shadow outer scopes
    - Lexical scoping rules (can access outer scope variables)

    Scope lifecycle:
    1. enter_scope() - push new scope (function entry, block entry)
    2. declare_symbol() - add symbols to current scope
    3. lookup_symbol() - search from inner to outer scopes
    4. exit_scope() - pop current scope (function/block exit)

    Future extensions:
    - Nested function support
    - Module-level scopes
    - Import/export handling
    """

    def __init__(self):
        # Stack of scopes - each scope is a dict of name -> Symbol
        # Index 0 is global scope, higher indices are inner scopes
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Start with global scope
        self.current_function: Optional[str] = None  # Track current function context

    def enter_scope(self):
        """
        Enter a new scope (e.g., function body, block).

        Called when entering:
        - Function bodies
        - Block statements (future)
        - Loop bodies (future)
        """
        self.scopes.append({})

    def exit_scope(self):
        """
        Exit current scope and return to parent scope.

        Note: Never pop the global scope (index 0) to prevent stack underflow.
        This is a safety measure against malformed ASTs.
        """
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare_symbol(self, symbol: Symbol) -> bool:
        """
        Declare a symbol in the current scope.

        Returns False if symbol already exists in current scope.
        This prevents variable redeclaration within the same scope.

        Design decision: Shadowing is allowed across scopes but not within
        the same scope for clarity.
        """
        current_scope = self.scopes[-1]
        if symbol.name in current_scope:
            return False  # Already declared in this scope
        current_scope[symbol.name] = symbol
        return True

    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """
        Look up symbol in all scopes from innermost to outermost.

        Implements lexical scoping:
        - Search current scope first
        - Then parent scopes in reverse order
        - Return first match found
        - Return None if not found in any scope

        This allows inner scopes to shadow outer scopes naturally.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def mark_used(self, name: str) -> bool:
        """
        Mark a symbol as used for dead code analysis.

        Returns False if symbol not found.
        Used when analyzing identifier references to track which
        variables are actually used vs. just declared.
        """
        symbol = self.lookup_symbol(name)
        if symbol:
            symbol.used = True
            return True
        return False


class SemanticError(Exception):
    """
    Represents a semantic analysis error with optional AST node context.

    Design philosophy:
    - Collect all errors before failing (don't stop at first error)
    - Provide context when available for better error messages
    - Separate from syntax errors (which are caught by parser)

    Future enhancements:
    - Line/column information
    - Error severity levels
    - Suggested fixes
    """

    def __init__(self, message: str, node: Optional[Dict] = None):
        self.message = message
        self.node = node  # AST node where error occurred (for future line/col info)
        super().__init__(message)


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
        self.current_function_return_type: Optional[HexenType] = (
            None  # For return type checking
        )

        # Context tracking for unified block concept
        self.block_context: List[str] = []  # Track: "function", "expression", etc.

        # Type mapping from string representation (parser) to internal enum (semantic analyzer)
        # Centralized as instance field for easy access and potential future customization
        self.type_map = {
            "i32": HexenType.I32,
            "i64": HexenType.I64,
            "f64": HexenType.F64,
            "string": HexenType.STRING,
        }

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
        Future: May contain imports, type definitions, etc.

        Validates:
        - Node type is correct
        - All functions are valid
        """
        if node.get("type") != "program":
            self._error(f"Expected program node, got {node.get('type')}")
            return

        # Analyze all functions in the program
        for func in node.get("functions", []):
            self._analyze_function(func)

    def _analyze_function(self, node: Dict):
        """
        Analyze a function definition.

        Function analysis involves:
        1. Set up function context (name, return type)
        2. Enter new scope for function body
        3. Analyze function body statements
        4. Validate return type consistency
        5. Clean up function context

        Future enhancements:
        - Parameter analysis
        - Multiple return statements
        - Function overloading
        """
        if node.get("type") != "function":
            self._error(f"Expected function node, got {node.get('type')}")
            return

        func_name = node.get("name")
        return_type_str = node.get("return_type")

        # Set up function analysis context
        self.symbol_table.current_function = func_name
        self.current_function_return_type = self._parse_type(return_type_str)
        self.block_context.append("function")

        # Enter function scope - function body gets its own scope
        self.symbol_table.enter_scope()

        # Analyze function body
        body = node.get("body")
        if body:
            self._analyze_block(body)

        # Clean up function context
        self.symbol_table.exit_scope()
        self.block_context.pop()
        self.symbol_table.current_function = None
        self.current_function_return_type = None

    def _analyze_block(self, node: Dict):
        """
        Analyze a block of statements.

        Blocks contain ordered statements that execute sequentially.
        Each statement is analyzed independently.

        Future: May need to handle control flow analysis
        (unreachable code after return, etc.)
        """
        if node.get("type") != "block":
            self._error(f"Expected block node, got {node.get('type')}")
            return

        statements = node.get("statements", [])
        for stmt in statements:
            self._analyze_statement(stmt)

    def _analyze_statement(self, node: Dict):
        """
        Dispatch statement analysis to appropriate handler.

        Currently supported statement types:
        - val_declaration: Immutable variable declaration
        - mut_declaration: Mutable variable declaration
        - return_statement: Function return

        Future statement types:
        - assignment: Variable assignment
        - if_statement: Conditional execution
        - while_statement: Loop execution
        - expression_statement: Expression evaluation
        """
        stmt_type = node.get("type")

        if stmt_type == "val_declaration":
            self._analyze_val_declaration(node)
        elif stmt_type == "mut_declaration":
            self._analyze_mut_declaration(node)
        elif stmt_type == "return_statement":
            self._analyze_return_statement(node)
        else:
            self._error(f"Unknown statement type: {stmt_type}", node)

    def _analyze_val_declaration(self, node: Dict):
        """
        Analyze an immutable variable declaration (val).

        Delegates to generic variable declaration analysis
        with IMMUTABLE mutability.
        """
        self._analyze_variable_declaration(node, Mutability.IMMUTABLE)

    def _analyze_mut_declaration(self, node: Dict):
        """
        Analyze a mutable variable declaration (mut).

        Delegates to generic variable declaration analysis
        with MUTABLE mutability.
        """
        self._analyze_variable_declaration(node, Mutability.MUTABLE)

    def _analyze_variable_declaration(self, node: Dict, mutability: Mutability):
        """
        Analyze a variable declaration (val or mut).

        Handles both explicit and inferred typing:
        - val x: i32 = 42      (explicit type)
        - val x = 42           (inferred type)
        - val x: i32 = undef   (explicit type, uninitialized)
        - mut y: i32 = 42      (mutable, explicit type)

        Validation steps:
        1. Check variable name is provided
        2. Check for redeclaration in current scope
        3. Handle type annotation vs inference
        4. Handle undef values
        5. Validate type compatibility
        6. Register symbol in symbol table
        """
        var_name = node.get("name")
        type_annotation = node.get("type_annotation")
        value = node.get("value")

        if not var_name:
            self._error("Variable declaration missing name", node)
            return

        # Check for redeclaration in current scope
        # Note: Shadowing across scopes is allowed, but not within same scope
        if var_name in self.symbol_table.scopes[-1]:
            self._error(f"Variable '{var_name}' already declared in this scope", node)
            return

        # Type determination logic
        var_type = None
        is_initialized = True

        if type_annotation:
            # Explicit type annotation path
            var_type = self._parse_type(type_annotation)

            # Check for explicit undef initialization
            if (
                value
                and value.get("type") == "identifier"
                and value.get("name") == "undef"
            ):
                is_initialized = False
            elif value:
                # Type annotation + value: validate compatibility
                value_type = self._analyze_expression(value)
                if value_type != HexenType.UNKNOWN and value_type != var_type:
                    self._error(
                        f"Type mismatch: variable '{var_name}' declared as {var_type.value} "
                        f"but assigned value of type {value_type.value}",
                        node,
                    )
        else:
            # Type inference path - must have value
            if not value:
                self._error(
                    f"Variable '{var_name}' must have either explicit type or value",
                    node,
                )
                return

            var_type = self._analyze_expression(value)
            if var_type == HexenType.UNKNOWN:
                self._error(f"Cannot infer type for variable '{var_name}'", node)
                return

        # Create and register symbol
        symbol = Symbol(
            name=var_name,
            type=var_type,
            mutability=mutability,
            initialized=is_initialized,
        )

        if not self.symbol_table.declare_symbol(symbol):
            self._error(f"Failed to declare variable '{var_name}'", node)

    def _analyze_return_statement(self, node: Dict):
        """
        Analyze a return statement in context.

        Context-aware validation:
        - Function context: Return type must match function return type
        - Block expression context: Return determines block's type
        - No context: Error - return statements need context

        This implements the unified block philosophy where return statements
        work consistently but context determines their validation rules.
        """
        value = node.get("value")
        if not value:
            self._error("Return statement missing value", node)
            return

        # Analyze the return value expression
        return_type = self._analyze_expression(value)

        # Context-aware validation
        if self.block_context and self.block_context[-1] == "expression":
            # We're in a block expression context - return type determines block type
            # No additional validation needed here, the block will handle it
            pass
        elif self.current_function_return_type:
            # We're in a function context - validate against function signature
            if (
                return_type != HexenType.UNKNOWN
                and return_type != self.current_function_return_type
            ):
                self._error(
                    f"Return type mismatch: expected {self.current_function_return_type.value}, "
                    f"got {return_type.value}",
                    node,
                )
        else:
            # No valid context for return statement
            self._error("Return statement outside valid context", node)

    def _analyze_expression(self, node: Dict) -> HexenType:
        """
        Analyze an expression and return its type.

        Currently supported expressions:
        - Literals: numbers, strings
        - Identifiers: variable references
        - Blocks: unified block expressions

        Future expression types:
        - Binary operations: +, -, *, /
        - Function calls
        - Member access
        - Array indexing

        Returns HexenType.UNKNOWN for invalid expressions.
        """
        expr_type = node.get("type")

        if expr_type == "literal":
            return self._infer_type_from_value(node)
        elif expr_type == "identifier":
            return self._analyze_identifier(node)
        elif expr_type == "block":
            return self._analyze_block_as_expression(node)
        else:
            self._error(f"Unknown expression type: {expr_type}", node)
            return HexenType.UNKNOWN

    def _analyze_block_as_expression(self, node: Dict) -> HexenType:
        """
        Analyze a block used as an expression.

        Expression blocks must:
        1. End with a return statement (explicit returns philosophy)
        2. Create a new scope for their variables
        3. Return the type of their final return statement

        This implements the unified block concept where context determines requirements.
        """
        if node.get("type") != "block":
            self._error(f"Expected block node, got {node.get('type')}")
            return HexenType.UNKNOWN

        # Enter block expression context
        self.block_context.append("expression")
        self.symbol_table.enter_scope()

        statements = node.get("statements", [])
        block_return_type = HexenType.UNKNOWN

        # Find the last return statement to determine block's type
        last_return_stmt = None

        # Analyze all statements
        for i, stmt in enumerate(statements):
            if stmt.get("type") == "return_statement":
                if i == len(statements) - 1:
                    # This is the final statement - good!
                    last_return_stmt = stmt
                else:
                    self._error(
                        "Return statement must be the last statement in expression block",
                        stmt,
                    )

            self._analyze_statement(stmt)

        # Validate that block ends with return statement
        if not last_return_stmt:
            self._error("Expression block must end with a return statement", node)
        else:
            # Get the type from the return statement's value
            return_value = last_return_stmt.get("value")
            if return_value:
                block_return_type = self._analyze_expression(return_value)

        # Exit block expression context
        self.symbol_table.exit_scope()
        self.block_context.pop()

        return block_return_type

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

    def _infer_type_from_value(self, value: Dict) -> HexenType:
        """
        Infer type from a literal value.

        Type inference rules:
        - Integers default to i32 (following Rust)
        - Floats default to f64
        - Strings are string type
        - Unknown for non-literals

        Future enhancements:
        - Integer literal suffixes (42i64)
        - Float literal suffixes (3.14f32)
        - Character literals
        - Boolean literals
        """
        if value.get("type") != "literal":
            return HexenType.UNKNOWN

        val = value.get("value")

        if isinstance(val, int):
            return HexenType.I32  # Default integer type
        elif isinstance(val, float):
            return HexenType.F64  # Default float type
        elif isinstance(val, str):
            return HexenType.STRING
        else:
            return HexenType.UNKNOWN

    def _parse_type(self, type_str: str) -> HexenType:
        """
        Parse a type string to HexenType enum.

        Handles conversion from string representation (from parser)
        to internal enum representation using the instance type_map.

        Returns HexenType.UNKNOWN for unrecognized types.
        This allows for graceful handling of future type additions.
        """
        return self.type_map.get(type_str, HexenType.UNKNOWN)
