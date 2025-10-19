"""
Hexen Symbol Table Management

Symbol table implementation for managing variable declarations, scoping,
and symbol lookup during semantic analysis.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union

from .type_util import parse_type
from .types import HexenType, Mutability, ConcreteArrayType, ComptimeArrayType


@dataclass
class Parameter:
    """
    Represents a function parameter with type and mutability information.

    Used in function signatures to track parameter metadata:
    - Type information for type checking function calls
    - Mutability for parameter reassignment validation within function body
    """

    name: str
    param_type: Union[HexenType, ConcreteArrayType]
    is_mutable: bool


@dataclass
class FunctionSignature:
    """
    Represents a function signature for symbol table storage.

    Tracks everything needed for function call resolution:
    - Parameter types and mutability for argument validation
    - Return type for result type checking
    - Parameter names for scope management within function body

    Design note: Separate from Symbol to distinguish functions from variables.
    Functions and variables live in different namespaces in many languages.
    """

    name: str
    parameters: List[Parameter]
    return_type: Union[HexenType, ConcreteArrayType]
    declared_line: Optional[int] = None  # For better error reporting (future)


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

    CHANGE (Phase 2): Extended type field to support ComptimeArrayType
    for preserving dimensional information in comptime arrays.
    """

    name: str
    type: Union[HexenType, ConcreteArrayType, ComptimeArrayType]  # Phase 2: Added ComptimeArrayType
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

        # Function signature storage (global namespace)
        # Functions exist in a separate namespace from variables
        self.functions: Dict[str, FunctionSignature] = {}

        # Current function context for analysis
        self.current_function: Optional[str] = None  # Track current function context
        self.current_function_signature: Optional[FunctionSignature] = None

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

    # =============================================================================
    # Function Management
    # =============================================================================

    def declare_function(self, signature: FunctionSignature) -> bool:
        """
        Declare a function signature in the global function namespace.

        Returns False if function already exists (prevents redeclaration).
        Functions exist in a separate namespace from variables, so function
        names don't conflict with variable names.

        Args:
            signature: Complete function signature with parameters and return type

        Returns:
            True if successfully declared, False if already exists
        """
        if signature.name in self.functions:
            return False  # Function already declared
        self.functions[signature.name] = signature
        return True

    def lookup_function(self, name: str) -> Optional[FunctionSignature]:
        """
        Look up function signature by name.

        Returns function signature if found, None otherwise.
        Used for function call resolution and type checking.
        """
        return self.functions.get(name)

    def enter_function_scope(self, function_name: str) -> bool:
        """
        Enter function scope with parameter declarations.

        Sets up function context and declares all parameters as local symbols
        in the new function scope. This enables parameter access throughout
        the function body and enforces parameter mutability rules.

        Args:
            function_name: Name of function being entered

        Returns:
            True if successful, False if function not found
        """
        signature = self.lookup_function(function_name)
        if not signature:
            return False

        # Set current function context
        self.current_function = function_name
        self.current_function_signature = signature

        # Enter new scope for function body
        self.enter_scope()

        # Declare all parameters as symbols in the function scope
        for param in signature.parameters:
            mutability = (
                Mutability.MUTABLE if param.is_mutable else Mutability.IMMUTABLE
            )
            param_symbol = Symbol(
                name=param.name,
                type=param.param_type,
                mutability=mutability,
                initialized=True,  # Parameters are always initialized by caller
            )
            # Note: Parameter declaration should always succeed since we control parameter names
            self.declare_symbol(param_symbol)

        return True

    def exit_function_scope(self) -> None:
        """
        Exit function scope and clear function context.

        Cleans up function context and exits the function's local scope.
        Should be called when function analysis is complete.
        """
        # Exit function scope
        self.exit_scope()

        # Clear function context
        self.current_function = None
        self.current_function_signature = None

    def get_current_function_signature(self) -> Optional[FunctionSignature]:
        """
        Get the signature of the currently analyzing function.

        Returns None if not currently analyzing a function.
        Used for return type validation and parameter access checking.
        """
        return self.current_function_signature

    def is_parameter(self, name: str) -> bool:
        """
        Check if a symbol is a parameter of the current function.

        Returns True if the symbol exists and is a parameter of the current
        function, False otherwise. Used for parameter-specific validation.
        """
        if not self.current_function_signature:
            return False

        for param in self.current_function_signature.parameters:
            if param.name == name:
                return True
        return False

    def get_parameter_info(self, name: str) -> Optional[Parameter]:
        """
        Get parameter information for the given name in current function.

        Returns Parameter object if name is a parameter of current function,
        None otherwise. Used for parameter mutability checking.
        """
        if not self.current_function_signature:
            return None

        for param in self.current_function_signature.parameters:
            if param.name == name:
                return param
        return None


# =============================================================================
# Function Signature Creation Utilities
# =============================================================================


def create_function_signature_from_ast(
    function_node: Dict[str, Any],
) -> FunctionSignature:
    """
    Create a FunctionSignature from a function AST node.

    Parses function declaration node to extract:
    - Function name
    - Parameter list with types and mutability
    - Return type

    Args:
        function_node: AST node for function declaration

    Returns:
        FunctionSignature object ready for symbol table storage

    Raises:
        KeyError: If function node is malformed
        ValueError: If types cannot be parsed
    """
    name = function_node["name"]
    # Use enhanced type parsing for return types to handle array types
    return_type_raw = function_node["return_type"]
    return_type = _parse_parameter_type(return_type_raw)

    # Parse parameters
    parameters = []
    for param_node in function_node.get("parameters", []):
        param_name = param_node["name"]
        param_type_raw = param_node["param_type"]

        # Use enhanced type parsing for parameters to handle array types
        param_type = _parse_parameter_type(param_type_raw)
        is_mutable = param_node.get("is_mutable", False)

        parameter = Parameter(
            name=param_name, param_type=param_type, is_mutable=is_mutable
        )
        parameters.append(parameter)

    return FunctionSignature(name=name, parameters=parameters, return_type=return_type)


def _parse_parameter_type(param_type_raw):
    """
    Parse parameter type that can be either a simple string or complex AST node.

    This is similar to DeclarationAnalyzer._parse_type_annotation but in the
    symbol_table module for function signature creation.

    Args:
        param_type_raw: Either a string (like "i32") or AST node (like array types)

    Returns:
        HexenType enum or ConcreteArrayType representing the parameter type
    """
    # Handle simple string types
    if isinstance(param_type_raw, str):
        return parse_type(param_type_raw)

    # Handle complex AST node types (like array types)
    if isinstance(param_type_raw, dict):
        node_type = param_type_raw.get("type")

        if node_type == "array_type":
            return _parse_array_parameter_type(param_type_raw)
        else:
            # Unknown complex type - return unknown for graceful degradation
            return HexenType.UNKNOWN

    # Fallback for unexpected parameter type format
    return HexenType.UNKNOWN


def _parse_array_parameter_type(array_type_node: Dict) -> ConcreteArrayType:
    """
    Parse array type AST node for function parameters into ConcreteArrayType.

    Similar to DeclarationAnalyzer._parse_array_type_annotation but without error reporting.
    """
    from .types import ConcreteArrayType  # Import here to avoid circular imports

    # Extract element type
    element_type_str = array_type_node.get("element_type", "unknown")
    element_type = parse_type(element_type_str)

    # Validate that the element type is valid and concrete
    if element_type == HexenType.UNKNOWN:
        return HexenType.UNKNOWN

    # Validate element type is concrete (not comptime)
    from .types import ComptimeArrayType
    if isinstance(element_type, ComptimeArrayType):
        return HexenType.UNKNOWN
    if element_type in {
        HexenType.COMPTIME_INT,
        HexenType.COMPTIME_FLOAT,
    }:
        return HexenType.UNKNOWN

    # Extract dimensions
    dimensions = []
    dimension_nodes = array_type_node.get("dimensions", [])

    for dim_node in dimension_nodes:
        size = dim_node.get("size")
        if size == "_":
            # Inferred dimension - accept any size ([_]T parameters)
            dimensions.append("_")
        else:
            try:
                dim_size = int(size)
                if dim_size < 0:
                    return HexenType.UNKNOWN
                dimensions.append(dim_size)
            except (ValueError, TypeError):
                return HexenType.UNKNOWN

    if not dimensions:
        return HexenType.UNKNOWN

    # Create and return concrete array type
    try:
        return ConcreteArrayType(element_type, dimensions)
    except ValueError:
        return HexenType.UNKNOWN


def validate_function_parameters(parameters: List[Parameter]) -> List[str]:
    """
    Validate function parameters for common issues.

    Checks for:
    - Duplicate parameter names
    - Invalid parameter types

    Args:
        parameters: List of Parameter objects to validate

    Returns:
        List of error messages (empty if no errors)
    """
    errors = []
    seen_names = set()

    for param in parameters:
        # Check for duplicate parameter names
        if param.name in seen_names:
            errors.append(f"Duplicate parameter name: '{param.name}'")
        seen_names.add(param.name)

        # Check for invalid parameter types (void parameters not allowed)
        if param.param_type == HexenType.VOID:
            errors.append(f"Parameter '{param.name}' cannot have void type")

    return errors
