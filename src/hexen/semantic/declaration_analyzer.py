"""
Hexen Declaration Analyzer

Handles analysis of declarations including:
- Function declarations
- Variable declarations (val and mut)
- Type inference and validation
- Symbol table integration
- Mutability enforcement
"""

from typing import Dict, Optional, Callable, Tuple

from ..ast_nodes import NodeType
from .types import HexenType, Mutability
from .symbol_table import (
    Symbol,
    SymbolTable,
    create_function_signature_from_ast,
    validate_function_parameters,
)
from .type_util import (
    parse_type,
    can_coerce,
    is_precision_loss_operation,
)


class DeclarationAnalyzer:
    """
    Analyzes declarations with unified framework and type-specific handling.

    Implements the unified declaration syntax philosophy:
    - val name : type = value
    - mut name : type = value
    - func name() : type = value

    All follow the same pattern with type-specific handling.
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
        symbol_table_callback: Callable[[Symbol], bool],
        lookup_symbol_callback: Callable[[str], Optional[Symbol]],
        analyze_block_callback: Callable[
            [Dict, Dict, Optional[str]], Optional[HexenType]
        ],
        set_function_context_callback: Callable[[str, HexenType], None],
        clear_function_context_callback: Callable[[], None],
        get_current_scope_callback: Callable[[], dict],
        symbol_table: SymbolTable,
        comptime_analyzer,
    ):
        """
        Initialize the declaration analyzer.

        Args:
            error_callback: Function to call when semantic errors are found
            analyze_expression_callback: Function to analyze expressions
            symbol_table_callback: Function to declare symbols
            lookup_symbol_callback: Function to lookup symbols
            analyze_block_callback: Function to analyze blocks
            set_function_context_callback: Function to set function context
            clear_function_context_callback: Function to clear function context
            get_current_scope_callback: Function to get current scope
            symbol_table: Direct access to symbol table for function management
            comptime_analyzer: ComptimeAnalyzer instance for comptime type operations
        """
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._declare_symbol = symbol_table_callback
        self._lookup_symbol = lookup_symbol_callback
        self._analyze_block = analyze_block_callback
        self._set_function_context = set_function_context_callback
        self._clear_function_context = clear_function_context_callback
        self._get_current_scope = get_current_scope_callback
        self.symbol_table = symbol_table
        self.comptime_analyzer = comptime_analyzer

    def analyze_declaration(self, node: Dict) -> None:
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
        if decl_type == NodeType.FUNCTION.value:
            self._analyze_function_declaration(name, type_annotation, value, node)
        elif decl_type == NodeType.VAL_DECLARATION.value:
            self._analyze_variable_declaration_unified(
                name, type_annotation, value, Mutability.IMMUTABLE, node
            )
        elif decl_type == NodeType.MUT_DECLARATION.value:
            self._analyze_variable_declaration_unified(
                name, type_annotation, value, Mutability.MUTABLE, node
            )
        else:
            self._error(f"Unknown declaration type: {decl_type}", node)

    def _get_declaration_type(self, node: Dict) -> str:
        """Determine the type of declaration from AST node."""
        return node.get("type", "unknown")

    def _extract_declaration_components(self, node: Dict) -> Tuple[str, str, Dict]:
        """
        Extract name, type annotation, and value from any declaration type.

        Returns unified components regardless of declaration type:
        - Functions: name, return_type, body
        - Variables: name, type_annotation, value
        """
        decl_type = node.get("type")

        if decl_type == NodeType.FUNCTION.value:
            # Function: func name() : return_type = body
            name = node.get("name")
            type_annotation = node.get("return_type")
            value = node.get("body")
        elif decl_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
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
        """Check for redeclaration in current scope only (allow shadowing)."""
        if not name:
            return True  # Skip if name validation already failed

        current_scope = self._get_current_scope()
        if name in current_scope:
            decl_type = self._get_declaration_type(node)
            self._error(
                f"{decl_type.replace('_', ' ').title()} '{name}' already declared in this scope",
                node,
            )
            return False
        return True

    def _analyze_function_declaration(
        self, name: str, return_type_str: str, body: Dict, node: Dict
    ) -> None:
        """
        Analyze function declaration with symbol table registration and scope management.

        Handles function-specific logic:
        1. Create and validate function signature
        2. Register function in symbol table
        3. Enter function scope with parameter declarations
        4. Analyze function body with proper context
        5. Exit function scope and clean up context
        """
        try:
            # Create function signature from AST node
            signature = create_function_signature_from_ast(node)

            # Validate function parameters
            param_errors = validate_function_parameters(signature.parameters)
            for error_msg in param_errors:
                self._error(error_msg, node)
                return

            # Register function in symbol table
            if not self.symbol_table.declare_function(signature):
                self._error(f"Function '{name}' is already declared", node)
                return

            # Enter function scope with parameter declarations
            if not self.symbol_table.enter_function_scope(name):
                self._error(f"Failed to enter scope for function '{name}'", node)
                return

            # Set up function analysis context for return type validation
            return_type = parse_type(return_type_str)
            self._set_function_context(name, return_type)

            # Analyze function body - block handles scope + return requirements
            if body:
                self._analyze_block(body, node)

            # Clean up function context and exit scope
            self._clear_function_context()
            self.symbol_table.exit_function_scope()

        except (KeyError, ValueError) as e:
            self._error(f"Invalid function declaration: {e}", node)

    def _analyze_variable_declaration_unified(
        self,
        name: str,
        type_annotation: str,
        value: Dict,
        mutability: Mutability,
        node: Dict,
    ) -> None:
        """
        Analyze variable declaration using unified framework with coercion.

        Handles variable-specific logic:
        - Type inference and validation with comptime type coercion
        - undef handling with val/mut validation
        - Symbol table registration
        """
        var_type = None
        is_initialized = True

        if type_annotation:
            # Explicit type annotation path
            var_type = parse_type(type_annotation)

            # Check for explicit undef initialization
            if (
                value
                and value.get("type") == NodeType.IDENTIFIER.value
                and value.get("name") == "undef"
            ):
                is_initialized = False

                # PHASE 3: Validate val + undef prohibition
                if mutability == Mutability.IMMUTABLE:
                    self._error(
                        f"Invalid usage: val variable '{name}' declared with undef creates unusable variable. "
                        f"val variables cannot be assigned later. "
                        f"Consider using 'mut' for deferred initialization "
                        f"or expression blocks for complex initialization (see UNIFIED_BLOCK_SYSTEM.md)",
                        node,
                    )
                    return

            elif value:
                # Type annotation + value: validate compatibility with coercion
                # Pass var_type as target_type for context-guided analysis
                value_type = self._analyze_expression(value, var_type)
                if value_type != HexenType.UNKNOWN:
                    # Explicit conversions are handled in _analyze_expression using value:type syntax
                    # If we get here without errors, the operation was either safe or explicitly converted

                    # Use centralized declaration type compatibility validation
                    # Don't return early to avoid cascading errors - still create the symbol
                    self.comptime_analyzer.validate_variable_declaration_type_compatibility(
                        value_type, var_type, value, name, self._error, node
                    )
        else:
            # Type inference path - must have value
            if not value:
                self._error(
                    f"Variable '{name}' must have either explicit type or value",
                    node,
                )
                return

            # NEW RULE: mut variables require explicit type annotation
            if mutability == Mutability.MUTABLE:
                self._error(
                    f"Mutable variable '{name}' requires explicit type annotation to prevent action-at-a-distance issues. "
                    f"Use 'mut {name} : type = value' instead of 'mut {name} = value'",
                    node,
                )
                return

            # PHASE 3: Special handling for undef without explicit type
            if (
                value.get("type") == NodeType.IDENTIFIER.value
                and value.get("name") == "undef"
            ):
                self._error(
                    f"Cannot infer type for variable '{name}': undef requires explicit type annotation. "
                    f"Use 'mut {name} : type = undef' or 'val {name} : type = value'",
                    node,
                )
                return

            inferred_type = self._analyze_expression(value)
            
            # Use centralized type inference error analysis
            if self.comptime_analyzer.analyze_declaration_type_inference_error(
                value, inferred_type, name, self._error, node
            ):
                return

            # Use centralized comptime type preservation logic
            var_type = self.comptime_analyzer.should_preserve_comptime_for_declaration(
                mutability, inferred_type
            )

        # Create and register symbol
        symbol = Symbol(
            name=name,
            type=var_type,
            mutability=mutability,
            initialized=is_initialized,
        )

        if not self._declare_symbol(symbol):
            self._error(f"Failed to declare variable '{name}'", node)

