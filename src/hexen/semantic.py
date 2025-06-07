"""
Semantic analyzer for Hexen

Performs semantic analysis on the AST including:
- Symbol table management and scope tracking
- Type checking and type inference
- Mutability enforcement (val vs mut)
- Use-before-definition validation
- undef handling and validation
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class HexenType(Enum):
    """Hexen type system"""

    I32 = "i32"
    I64 = "i64"
    F64 = "f64"
    STRING = "string"
    UNKNOWN = "unknown"  # For type inference
    UNINITIALIZED = "undef"  # For undef values


class Mutability(Enum):
    """Variable mutability"""

    IMMUTABLE = "val"  # val variables
    MUTABLE = "mut"  # mut variables


@dataclass
class Symbol:
    """Represents a symbol in the symbol table"""

    name: str
    type: HexenType
    mutability: Mutability
    declared_line: Optional[int] = None
    initialized: bool = True  # False for undef variables
    used: bool = False


class SymbolTable:
    """Manages symbols and scopes"""

    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.current_function: Optional[str] = None

    def enter_scope(self):
        """Enter a new scope (e.g., function body)"""
        self.scopes.append({})

    def exit_scope(self):
        """Exit current scope"""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare_symbol(self, symbol: Symbol) -> bool:
        """Declare a symbol in current scope. Returns False if already declared."""
        current_scope = self.scopes[-1]
        if symbol.name in current_scope:
            return False
        current_scope[symbol.name] = symbol
        return True

    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """Look up symbol in all scopes (inner to outer)"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def mark_used(self, name: str) -> bool:
        """Mark a symbol as used. Returns False if not found."""
        symbol = self.lookup_symbol(name)
        if symbol:
            symbol.used = True
            return True
        return False


class SemanticError(Exception):
    """Represents a semantic analysis error"""

    def __init__(self, message: str, node: Optional[Dict] = None):
        self.message = message
        self.node = node
        super().__init__(message)


class SemanticAnalyzer:
    """Main semantic analyzer"""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_function_return_type: Optional[HexenType] = None

    def analyze(self, ast: Dict) -> List[SemanticError]:
        """Analyze the AST and return any semantic errors"""
        self.errors.clear()
        try:
            self._analyze_program(ast)
        except Exception as e:
            # Convert unexpected errors to semantic errors
            self.errors.append(SemanticError(f"Internal analysis error: {e}"))

        return self.errors

    def _error(self, message: str, node: Optional[Dict] = None):
        """Record a semantic error"""
        self.errors.append(SemanticError(message, node))

    def _analyze_program(self, node: Dict):
        """Analyze the program node"""
        if node.get("type") != "program":
            self._error(f"Expected program node, got {node.get('type')}")
            return

        # Analyze all functions
        for func in node.get("functions", []):
            self._analyze_function(func)

    def _analyze_function(self, node: Dict):
        """Analyze a function definition"""
        if node.get("type") != "function":
            self._error(f"Expected function node, got {node.get('type')}")
            return

        func_name = node.get("name")
        return_type_str = node.get("return_type")

        # Set up function context
        self.symbol_table.current_function = func_name
        self.current_function_return_type = self._parse_type(return_type_str)

        # Enter function scope
        self.symbol_table.enter_scope()

        # Analyze function body
        body = node.get("body")
        if body:
            self._analyze_block(body)

        # Exit function scope
        self.symbol_table.exit_scope()
        self.symbol_table.current_function = None
        self.current_function_return_type = None

    def _analyze_block(self, node: Dict):
        """Analyze a block of statements"""
        if node.get("type") != "block":
            self._error(f"Expected block node, got {node.get('type')}")
            return

        statements = node.get("statements", [])
        for stmt in statements:
            self._analyze_statement(stmt)

    def _analyze_statement(self, node: Dict):
        """Analyze a statement"""
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
        """Analyze a val (immutable) variable declaration"""
        self._analyze_variable_declaration(node, Mutability.IMMUTABLE)

    def _analyze_mut_declaration(self, node: Dict):
        """Analyze a mut (mutable) variable declaration"""
        self._analyze_variable_declaration(node, Mutability.MUTABLE)

    def _analyze_variable_declaration(self, node: Dict, mutability: Mutability):
        """Analyze a variable declaration (val or mut)"""
        var_name = node.get("name")
        type_annotation = node.get("type_annotation")
        value = node.get("value")

        if not var_name:
            self._error("Variable declaration missing name", node)
            return

        # Check if already declared in current scope
        if var_name in self.symbol_table.scopes[-1]:
            self._error(f"Variable '{var_name}' already declared in this scope", node)
            return

        # Determine type
        var_type = None
        is_initialized = True

        if type_annotation:
            # Explicit type annotation
            var_type = self._parse_type(type_annotation)

            # Check if value is undef
            if (
                value
                and value.get("type") == "identifier"
                and value.get("name") == "undef"
            ):
                is_initialized = False
            elif value:
                # Validate value type matches annotation
                value_type = self._infer_type_from_value(value)
                if value_type != HexenType.UNKNOWN and value_type != var_type:
                    self._error(
                        f"Type mismatch: variable '{var_name}' declared as {var_type.value} "
                        f"but assigned value of type {value_type.value}",
                        node,
                    )
        else:
            # Type inference from value
            if not value:
                self._error(
                    f"Variable '{var_name}' must have either explicit type or value",
                    node,
                )
                return

            var_type = self._infer_type_from_value(value)
            if var_type == HexenType.UNKNOWN:
                self._error(f"Cannot infer type for variable '{var_name}'", node)
                return

        # Create and declare symbol
        symbol = Symbol(
            name=var_name,
            type=var_type,
            mutability=mutability,
            initialized=is_initialized,
        )

        if not self.symbol_table.declare_symbol(symbol):
            self._error(f"Failed to declare variable '{var_name}'", node)

    def _analyze_return_statement(self, node: Dict):
        """Analyze a return statement"""
        value = node.get("value")
        if not value:
            self._error("Return statement missing value", node)
            return

        # Check if we're in a function
        if not self.current_function_return_type:
            self._error("Return statement outside function", node)
            return

        # Analyze the return value
        return_type = self._analyze_expression(value)

        # Check type compatibility
        if (
            return_type != HexenType.UNKNOWN
            and return_type != self.current_function_return_type
        ):
            self._error(
                f"Return type mismatch: expected {self.current_function_return_type.value}, "
                f"got {return_type.value}",
                node,
            )

    def _analyze_expression(self, node: Dict) -> HexenType:
        """Analyze an expression and return its type"""
        expr_type = node.get("type")

        if expr_type == "literal":
            return self._infer_type_from_value(node)
        elif expr_type == "identifier":
            return self._analyze_identifier(node)
        else:
            self._error(f"Unknown expression type: {expr_type}", node)
            return HexenType.UNKNOWN

    def _analyze_identifier(self, node: Dict) -> HexenType:
        """Analyze an identifier reference"""
        name = node.get("name")
        if not name:
            self._error("Identifier missing name", node)
            return HexenType.UNKNOWN

        # Special case for undef
        if name == "undef":
            return HexenType.UNINITIALIZED

        # Look up symbol
        symbol = self.symbol_table.lookup_symbol(name)
        if not symbol:
            self._error(f"Undefined variable: '{name}'", node)
            return HexenType.UNKNOWN

        # Check if variable is initialized
        if not symbol.initialized:
            self._error(f"Use of uninitialized variable: '{name}'", node)
            return HexenType.UNKNOWN

        # Mark as used
        symbol.used = True
        return symbol.type

    def _infer_type_from_value(self, value: Dict) -> HexenType:
        """Infer type from a literal value"""
        if value.get("type") != "literal":
            return HexenType.UNKNOWN

        val = value.get("value")

        if isinstance(val, int):
            return HexenType.I32  # Default integer type
        elif isinstance(val, float):
            return HexenType.F64
        elif isinstance(val, str):
            return HexenType.STRING
        else:
            return HexenType.UNKNOWN

    def _parse_type(self, type_str: str) -> HexenType:
        """Parse a type string to HexenType"""
        type_map = {
            "i32": HexenType.I32,
            "i64": HexenType.I64,
            "f64": HexenType.F64,
            "string": HexenType.STRING,
        }
        return type_map.get(type_str, HexenType.UNKNOWN)
