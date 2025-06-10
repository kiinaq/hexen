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
    Hexen's type system with Zig-style comptime types for elegant numeric handling.

    Design decisions:
    - I32 as default integer type (following Rust conventions)
    - F32/F64 for single/double precision floats
    - COMPTIME_INT for integer literals (arbitrary precision, context-dependent coercion)
    - COMPTIME_FLOAT for float literals (arbitrary precision, context-dependent coercion)
    - VOID for functions/blocks that don't return values
    - UNKNOWN for type inference failures (not user-facing)
    - UNINITIALIZED for explicit undef values (different from null/None)

    Zig-inspired comptime types:
    - comptime_int: Integer literals that can coerce to any integer or float type
    - comptime_float: Float literals that can coerce to any float type
    - Context-dependent coercion eliminates need for literal suffixes

    Future extensions:
    - User-defined types (structs, enums)
    - Generic types
    - Function types
    """

    I32 = "i32"
    I64 = "i64"
    F32 = "f32"  # New: 32-bit float
    F64 = "f64"
    STRING = "string"
    BOOL = "bool"
    VOID = "void"  # For functions/blocks that don't return values
    COMPTIME_INT = "comptime_int"  # New: Zig-style integer literals
    COMPTIME_FLOAT = "comptime_float"  # New: Zig-style float literals
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
            "f32": HexenType.F32,
            "f64": HexenType.F64,
            "string": HexenType.STRING,
            "bool": HexenType.BOOL,
            "void": HexenType.VOID,
            "comptime_int": HexenType.COMPTIME_INT,
            "comptime_float": HexenType.COMPTIME_FLOAT,
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

        This implements the unified declaration syntax philosophy:
        - val name : type = value
        - mut name : type = value
        - func name() : type = value

        All follow the same pattern with type-specific handling.
        """
        # 1. Determine declaration type
        decl_type = self._get_declaration_type(node)

        # 2. Extract common components
        name, type_annotation, value = self._extract_declaration_components(node)

        # 3. Unified validation - skip type-specific analysis if validation fails
        self._validate_declaration_name(name, node)
        if not self._validate_no_redeclaration(name, node):
            return  # Skip analysis if redeclaration detected

        # 4. Type-specific analysis
        if decl_type == "function":
            self._analyze_function_declaration(name, type_annotation, value, node)
        elif decl_type == "val_declaration":
            self._analyze_variable_declaration_unified(
                name, type_annotation, value, Mutability.IMMUTABLE, node
            )
        elif decl_type == "mut_declaration":
            self._analyze_variable_declaration_unified(
                name, type_annotation, value, Mutability.MUTABLE, node
            )
        else:
            self._error(f"Unknown declaration type: {decl_type}", node)

    def _get_declaration_type(self, node: Dict) -> str:
        """Determine the type of declaration from AST node."""
        return node.get("type", "unknown")

    def _extract_declaration_components(self, node: Dict) -> tuple[str, str, Dict]:
        """
        Extract name, type annotation, and value from any declaration type.

        Returns unified components regardless of declaration type:
        - Functions: name, return_type, body
        - Variables: name, type_annotation, value
        """
        decl_type = node.get("type")

        if decl_type == "function":
            # Function: func name() : return_type = body
            name = node.get("name")
            type_annotation = node.get("return_type")
            value = node.get("body")
        elif decl_type in ["val_declaration", "mut_declaration"]:
            # Variable: val/mut name : type_annotation = value
            name = node.get("name")
            type_annotation = node.get("type_annotation")
            value = node.get("value")
        else:
            # Unknown type - return empty values
            name = None
            type_annotation = None
            value = None

        return name, type_annotation, value

    def _validate_declaration_name(self, name: str, node: Dict) -> None:
        """Validate that declaration has a valid name."""
        if not name:
            decl_type = self._get_declaration_type(node)
            self._error(f"{decl_type.replace('_', ' ').title()} missing name", node)

    def _validate_no_redeclaration(self, name: str, node: Dict) -> bool:
        """Check for redeclaration in current scope."""
        if not name:
            return True  # Skip if name validation already failed

        # Check for redeclaration in current scope
        # Note: Shadowing across scopes is allowed, but not within same scope
        if name in self.symbol_table.scopes[-1]:
            decl_type = self._get_declaration_type(node)
            self._error(
                f"{decl_type.replace('_', ' ').title()} '{name}' already declared in this scope",
                node,
            )
            return False
        return True

    # =============================================================================
    # TYPE-SPECIFIC DECLARATION HANDLERS
    # =============================================================================

    def _analyze_function_declaration(
        self, name: str, return_type_str: str, body: Dict, node: Dict
    ) -> None:
        """
        Analyze function declaration with truly unified block behavior.

        Handles function-specific logic:
        - Function context setup for return type validation
        - Block analysis (block manages its own scope and requires final return)
        - No symbol table registration (functions are not variables)

        Complete unification: Function bodies are just regular blocks that
        validate their return type against the function signature.
        """
        # Set up function analysis context for return type validation
        self.symbol_table.current_function = name
        self.current_function_return_type = self._parse_type(return_type_str)

        # Analyze function body - block handles scope + return requirements
        if body:
            self._analyze_block(body, node)  # Block manages everything now!

        # Clean up function context
        self.symbol_table.current_function = None
        self.current_function_return_type = None

    def _analyze_variable_declaration_unified(
        self,
        name: str,
        type_annotation: str,
        value: Dict,
        mutability: Mutability,
        node: Dict,
    ) -> None:
        """
        Analyze variable declaration using unified framework with Zig-style coercion.

        Handles variable-specific logic:
        - Type inference and validation with comptime type coercion
        - undef handling
        - Symbol table registration
        """
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
                # Type annotation + value: validate compatibility with Zig-style coercion
                value_type = self._analyze_expression(value)
                if value_type != HexenType.UNKNOWN:
                    if self._can_coerce(value_type, var_type):
                        # Coercion is allowed - resolve comptime types to concrete types
                        if value_type in {
                            HexenType.COMPTIME_INT,
                            HexenType.COMPTIME_FLOAT,
                        }:
                            # The comptime type becomes the target type through coercion
                            pass
                        # else: regular coercion (e.g., i32 -> i64), also fine
                    else:
                        # Cannot coerce - this is a type error
                        self._error(
                            f"Type mismatch: variable '{name}' declared as {var_type.value} "
                            f"but assigned value of type {value_type.value}",
                            node,
                        )
        else:
            # Type inference path - must have value
            if not value:
                self._error(
                    f"Variable '{name}' must have either explicit type or value",
                    node,
                )
                return

            inferred_type = self._analyze_expression(value)
            if inferred_type == HexenType.UNKNOWN:
                self._error(f"Cannot infer type for variable '{name}'", node)
                return

            # Resolve comptime types to their default concrete types for inference
            var_type = self._resolve_comptime_type(inferred_type, HexenType.UNKNOWN)

        # Create and register symbol
        symbol = Symbol(
            name=name,
            type=var_type,
            mutability=mutability,
            initialized=is_initialized,
        )

        if not self.symbol_table.declare_symbol(symbol):
            self._error(f"Failed to declare variable '{name}'", node)

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
                    block_return_type = self._analyze_expression(return_value)
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

        Future statement types:
        - assignment: Variable assignment
        - if_statement: Conditional execution
        - while_statement: Loop execution
        - expression_statement: Expression evaluation
        """
        stmt_type = node.get("type")

        if stmt_type in ["val_declaration", "mut_declaration"]:
            self._analyze_declaration(node)
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

        This implements the unified block philosophy where return statements
        work consistently but context determines their validation rules.
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
        return_type = self._analyze_expression(value)

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
                # Use Zig-style coercion for return type checking
                if not self._can_coerce(return_type, self.current_function_return_type):
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
        Analyze an assignment statement with comprehensive validation and Zig-style coercion.

        Assignment rules:
        - Target must be a declared variable
        - Target must be mutable (mut, not val)
        - Value type must be coercible to target type (using Zig-style coercion)
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
        value_type = self._analyze_expression(value)

        # Check type compatibility with Zig-style coercion
        if value_type != HexenType.UNKNOWN:
            if not self._can_coerce(value_type, symbol.type):
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
            return self._analyze_block(node, node, context="expression")
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

    def _infer_type_from_value(self, value: Dict) -> HexenType:
        """
        Infer type from a literal value using Zig-style comptime types.

        Zig-inspired type inference rules:
        - Integer literals have type comptime_int (arbitrary precision, context-dependent)
        - Float literals have type comptime_float (arbitrary precision, context-dependent)
        - String literals are string type
        - Boolean literals are bool type
        - comptime types can coerce to any compatible concrete type

        This eliminates the need for literal suffixes and provides elegant type coercion.
        """
        if value.get("type") != "literal":
            return HexenType.UNKNOWN

        val = value.get("value")

        if isinstance(val, bool):
            return HexenType.BOOL
        elif isinstance(val, int):
            return (
                HexenType.COMPTIME_INT
            )  # Zig-style: context will determine final type
        elif isinstance(val, float):
            return (
                HexenType.COMPTIME_FLOAT
            )  # Zig-style: context will determine final type
        elif isinstance(val, str):
            return HexenType.STRING
        else:
            return HexenType.UNKNOWN

    def _can_coerce(self, from_type: HexenType, to_type: HexenType) -> bool:
        """
        Check if from_type can be automatically coerced to to_type.

        Implements Zig-style context-dependent coercion rules:

        1. Comptime types (the magic sauce):
           - comptime_int can coerce to any integer or float type
           - comptime_float can coerce to any float type

        2. Regular widening coercion:
           - i32 can widen to i64 and f64/f32
           - i64 can widen to f64/f32
           - f32 can widen to f64

        3. Identity coercion:
           - Any type can coerce to itself

        This approach eliminates the need for explicit casting in most cases
        while maintaining type safety.
        """
        # Identity coercion - type can always coerce to itself
        if from_type == to_type:
            return True

        # Zig-style comptime type coercion (the elegant part!)
        if from_type == HexenType.COMPTIME_INT:
            # comptime_int can become numeric types, but NOT bool (that would be unsafe)
            return to_type in {
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
            }

        if from_type == HexenType.COMPTIME_FLOAT:
            # comptime_float can become any float type, but NOT bool (that would be unsafe)
            return to_type in {HexenType.F32, HexenType.F64}

        # Regular numeric widening coercion (for when we have concrete types)
        widening_rules = {
            HexenType.I32: {HexenType.I64, HexenType.F32, HexenType.F64},
            HexenType.I64: {HexenType.F32, HexenType.F64},  # Note: may lose precision
            HexenType.F32: {HexenType.F64},
        }

        return to_type in widening_rules.get(from_type, set())

    def _resolve_comptime_type(
        self, comptime_type: HexenType, target_type: HexenType
    ) -> HexenType:
        """
        Resolve a comptime type to a concrete type based on context.

        Used when we have a comptime_int or comptime_float that needs to become
        a concrete type. Falls back to default types if no target is provided.
        """
        if comptime_type == HexenType.COMPTIME_INT:
            if target_type in {
                HexenType.I32,
                HexenType.I64,
                HexenType.F32,
                HexenType.F64,
            }:
                return target_type
            else:
                return HexenType.I32  # Default integer type

        elif comptime_type == HexenType.COMPTIME_FLOAT:
            if target_type in {HexenType.F32, HexenType.F64}:
                return target_type
            else:
                return HexenType.F64  # Default float type

        else:
            return comptime_type  # Not a comptime type, return as-is

    def _parse_type(self, type_str: str) -> HexenType:
        """
        Parse a type string to HexenType enum.

        Handles conversion from string representation (from parser)
        to internal enum representation using the instance type_map.

        Returns HexenType.UNKNOWN for unrecognized types.
        This allows for graceful handling of future type additions.
        """
        return self.type_map.get(type_str, HexenType.UNKNOWN)
