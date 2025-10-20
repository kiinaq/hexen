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

from .symbol_table import (
    Symbol,
    SymbolTable,
    create_function_signature_from_ast,
    validate_function_parameters,
)
from .type_util import (
    parse_type,
)
from .types import HexenType, Mutability, ConcreteArrayType
from .arrays.multidim_analyzer import MultidimensionalArrayAnalyzer
from ..ast_nodes import NodeType


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
        get_modified_parameters_callback: Optional[Callable[[], set]] = None,
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
            get_modified_parameters_callback: Function to get modified mut parameters (Week 2 Task 8)
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
        self._get_modified_parameters = get_modified_parameters_callback

        # Initialize multidimensional array analyzer for flattening operations
        self.multidim_analyzer = MultidimensionalArrayAnalyzer(
            error_callback=error_callback, comptime_analyzer=comptime_analyzer
        )

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
            # Use enhanced type parsing to handle both simple and complex return types
            return_type = self._parse_type_annotation(return_type_str)
            self._set_function_context(name, return_type)

            # Analyze function body - block handles scope + return requirements
            if body:
                self._analyze_block(body, node)

            # Validate mut parameter enforcement (Week 2 Task 8)
            self._validate_mut_parameter_enforcement(signature, return_type, node)

            # Clean up function context and exit scope
            self._clear_function_context()
            self.symbol_table.exit_function_scope()

        except (KeyError, ValueError) as e:
            self._error(f"Invalid function declaration: {e}", node)

    def _validate_mut_parameter_enforcement(
        self, signature, return_type: HexenType, node: Dict
    ) -> None:
        """
        Validate mut parameter enforcement rule (Week 2 Task 8).

        Rule: Functions that modify mut parameters MUST return the modified value.
        This makes pass-by-value semantics explicit and prevents developer confusion.

        Error condition:
        - Function modifies one or more mut parameters
        - AND function returns void

        Rationale:
        - Pass-by-value means modifications affect LOCAL COPIES only
        - Modifications are lost unless returned to caller
        - Enforcement prevents "silent confusion" where developers expect side effects
        """
        if not self._get_modified_parameters:
            return  # Callback not available, skip validation

        # Get set of modified parameters
        modified_params = self._get_modified_parameters()
        if not modified_params:
            return  # No parameters were modified, all good

        # Check if function returns void
        if return_type == HexenType.VOID:
            # Get parameter info for better error messages
            modified_param_names = ", ".join(sorted(modified_params))

            self._error(
                f"Function '{signature.name}' modifies mutable parameter(s) '{modified_param_names}' "
                f"but returns void. Modified mut parameters affect local copies only (pass-by-value). "
                f"Return the modified value to communicate changes to caller. "
                f"Suggestion: Change return type from 'void' to parameter type and return modified value",
                node,
            )

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
            var_type = self._parse_type_annotation(type_annotation)

            # Check for explicit undef initialization
            if (
                value
                and value.get("type") == NodeType.IDENTIFIER.value
                and value.get("name") == "undef"
            ):
                is_initialized = False

                # Validate val + undef prohibition
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

                    # Check for array flattening before type compatibility validation
                    flattening_handled = False
                    if self._is_flattening_assignment(var_type, value_type):
                        if self._handle_flattening_assignment(
                            node, var_type, value_type, name, value
                        ):
                            # Flattening successful - skip regular type compatibility check
                            flattening_handled = True
                        else:
                            # Flattening failed - error already reported
                            return

                    # Use centralized declaration type compatibility validation only if not flattening
                    if not flattening_handled:
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

            # Special handling for undef without explicit type
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

            # NEW RULE: Function call return values require explicit type annotation
            # Functions always return concrete types (never comptime types)
            # This makes the concrete type explicit and visible at the call site
            # Improves code clarity and aligns with "Transparent Costs" philosophy
            if value.get("type") == NodeType.FUNCTION_CALL.value:
                function_name = value.get("name", "<unknown>")
                self._error(
                    f"Function call return values require explicit type annotation. "
                    f"Variable '{name}' is assigned result of function '{function_name}()' without explicit type. "
                    f"Functions always return concrete types (never comptime types). "
                    f"Use explicit type annotation: 'val {name} : type = {function_name}(...)' "
                    f"(see CLAUDE.md: Function System - Function Call Return Value Type Annotations)",
                    node,
                )
                return

            # NEW RULE: Conditional expression return values require explicit type annotation
            # Conditional expressions are runtime operations that form a "type barrier"
            # where comptime types can flow IN but concrete types flow OUT.
            # This makes the concrete type explicit and visible at the declaration site.
            # Follows same pattern as function calls (runtime operations require type context).
            if value.get("type") == NodeType.CONDITIONAL_STATEMENT.value:
                self._error(
                    f"Conditional expressions require explicit type annotation (runtime operation). "
                    f"Variable '{name}' is assigned result of conditional expression without explicit type. "
                    f"Conditional expressions are runtime operations (like function calls) that form a 'type barrier'. "
                    f"Use explicit type annotation: 'val {name} : type = if condition {{ ... }}' "
                    f"(see CONDITIONAL_SYSTEM.md: Runtime Barrier Semantics)",
                    node,
                )
                return

            inferred_type = self._analyze_expression(value)

            # Runtime blocks without explicit type annotation should trigger enhanced error
            if value and value.get("type") == "block":
                # Classify block evaluability to determine if explicit context is required
                block_statements = value.get("statements", [])
                evaluability = self.comptime_analyzer.classify_block_evaluability(
                    block_statements
                )

                # If block is runtime evaluable, it requires explicit type context
                from .types import BlockEvaluability

                if evaluability == BlockEvaluability.RUNTIME:
                    # REFINED: Only flag blocks that actually produce values with assign statements
                    # Blocks with only return statements (early exits) don't need explicit context
                    has_assign_statement = any(
                        stmt.get("type") == "assign_statement"
                        for stmt in block_statements
                    )

                    if has_assign_statement:
                        # Generate enhanced error message with actionable guidance
                        runtime_reason = (
                            self.comptime_analyzer.get_runtime_operation_reason(
                                block_statements
                            )
                        )
                        self._error(
                            f"Explicit type annotation REQUIRED! Runtime block requires explicit type annotation because it {runtime_reason.lower()}. "
                            f"Suggestion: val {name} : <type> = {{ ... }}",
                            node,
                        )
                        return

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

    def _parse_type_annotation(self, type_annotation):
        """
        Parse a type annotation that can be either a simple string or complex AST node.

        Args:
            type_annotation: Either a string (like "i32") or AST node (like array types)

        Returns:
            HexenType enum or ConcreteArrayType representing the type
        """
        # Handle simple string types
        if isinstance(type_annotation, str):
            return parse_type(type_annotation)

        # Handle complex AST node types (like array types)
        if isinstance(type_annotation, dict):
            node_type = type_annotation.get("type")

            if node_type == "array_type":
                return self._parse_array_type_annotation(type_annotation)
            else:
                # Unknown complex type - return unknown for graceful degradation
                return HexenType.UNKNOWN

        # Fallback for unexpected type annotation format
        return HexenType.UNKNOWN

    def _parse_array_type_annotation(self, array_type_node: Dict) -> ConcreteArrayType:
        """
        Parse array type AST node into ConcreteArrayType.

        Creates proper ConcreteArrayType instances for
        explicit array type contexts like [3]i32, [2][4]f64.

        Args:
            array_type_node: AST node with "dimensions" and "element_type" fields

        Returns:
            ConcreteArrayType instance representing the explicit array type
        """
        # Extract element type
        element_type_str = array_type_node.get("element_type", "unknown")
        element_type = parse_type(element_type_str)

        # Validate that the element type is valid and concrete
        if element_type == HexenType.UNKNOWN:
            self._error(
                f"Invalid element type in array annotation: {element_type_str}",
                array_type_node,
            )
            return HexenType.UNKNOWN

        # Validate element type is concrete (not comptime)
        from .types import ComptimeArrayType

        if isinstance(element_type, ComptimeArrayType):
            self._error(
                f"Array type annotation cannot use ComptimeArrayType as element",
                array_type_node,
            )
            return HexenType.UNKNOWN
        if element_type in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        }:
            self._error(
                f"Array type annotation must use concrete element type, got {element_type_str}",
                array_type_node,
            )
            return HexenType.UNKNOWN

        # Extract dimensions
        dimensions = []
        dimension_nodes = array_type_node.get("dimensions", [])

        for dim_node in dimension_nodes:
            size = dim_node.get("size")
            if size == "_":
                # Allow [_] dimensions - they will be resolved during flattening or other inference contexts
                dimensions.append("_")
            else:
                try:
                    dim_size = int(size)
                    if dim_size < 0:
                        self._error(
                            f"Array dimension must be non-negative, got {dim_size}",
                            array_type_node,
                        )
                        return HexenType.UNKNOWN
                    dimensions.append(dim_size)
                except (ValueError, TypeError):
                    self._error(
                        f"Invalid array dimension size: {size}", array_type_node
                    )
                    return HexenType.UNKNOWN

        if not dimensions:
            self._error(
                "Array type annotation must have at least one dimension",
                array_type_node,
            )
            return HexenType.UNKNOWN

        # Create and return concrete array type
        try:
            return ConcreteArrayType(element_type, dimensions)
        except ValueError as e:
            self._error(f"Invalid array type: {e}", array_type_node)
            return HexenType.UNKNOWN

    def _is_flattening_assignment(
        self, target_type: HexenType, source_type: HexenType
    ) -> bool:
        """
        Detect if assignment is array flattening operation.

        Flattening occurs when:
        - Both target and source are array types
        - Target is 1D array
        - Source is multidimensional array (2D+)
        - Element types are compatible
        """
        return (
            isinstance(target_type, ConcreteArrayType)
            and isinstance(source_type, ConcreteArrayType)
            and len(target_type.dimensions) == 1  # Target is 1D
            and len(source_type.dimensions) > 1  # Source is multidimensional
        )

    def _handle_flattening_assignment(
        self,
        node: Dict,
        target_type: ConcreteArrayType,
        source_type: ConcreteArrayType,
        var_name: str,
        value_node: Dict,
    ) -> bool:
        """
        Handle array flattening assignment with proper validation.

        Args:
            node: AST node for error reporting
            target_type: Target 1D array type
            source_type: Source multidimensional array type
            var_name: Variable name for error messages
            value_node: Value AST node to check for explicit copy operator

        Returns:
            True if flattening is valid and processed, False if error occurred
        """
        # 0. Explicit copy operator AND type conversion check - flattening requires BOTH!
        value_type = value_node.get("type")

        # Comptime array literals can flatten without [..] (first materialization)
        if value_type == "array_literal":
            # Comptime array - first materialization, no copy needed
            pass
        # Array copy operator [..] is explicitly present
        elif value_type == "array_copy":
            # Explicit copy present, but for dimension changes we also need :type!
            # This enforces that BOTH [..] AND :type are required for flattening
            self._error(
                f"Missing explicit type conversion syntax for array flattening\n"
                f"Variable '{var_name}' expects flattened array\n"
                f"Array dimension changes require BOTH [..] (copy) AND :type (conversion) operators\n"
                f"The [..] operator alone is not sufficient for dimension conversion\n"
                f"Suggestion: use combined syntax: value[..]:[type]\n"
                f"Example: val {var_name} : {self._format_array_type(target_type)} = {self._get_value_hint(value_node)}[..]:{self._format_array_type(target_type)}",
                node,
            )
            return False
        # Everything else requires explicit [..]
        else:
            # Most common case: identifier (variable reference to existing array)
            if value_type == "identifier":
                array_name = value_node.get("name", "<unknown>")
                target_type_str = f"[{target_type.dimensions[0]}]{target_type.element_type.name.lower()}"

                self._error(
                    f"Missing explicit copy syntax for array flattening\n"
                    f"Variable '{var_name}' expects type {target_type_str}\n"
                    f"Concrete array '{array_name}' requires explicit copy operator [..] for flattening\n"
                    f"Array flattening is a copy operation and requires explicit syntax to make performance costs visible\n"
                    f"Suggestion: val {var_name} : {target_type_str} = {array_name}[..]",
                    node,
                )
                return False

            # Other expression types also need explicit copy
            self._error(
                f"Array flattening requires explicit copy operator [..]\n"
                f"Variable '{var_name}' expects flattened array\n"
                f"Complex array expressions must use explicit [..] to make copy costs visible\n"
                f"Suggestion: wrap expression in array copy: (<expression>)[..]",
                node,
            )
            return False

        # 1. Element type compatibility check
        if source_type.element_type != target_type.element_type:
            self._error(
                f"Array flattening type mismatch for variable '{var_name}': "
                f"cannot flatten {source_type.element_type} array to {target_type.element_type} array. "
                f"Element types must match exactly",
                node,
            )
            return False

        # 2. Calculate source array total element count
        source_element_count = 1
        for dim_size in source_type.dimensions:
            if dim_size == "_":
                self._error(
                    f"Cannot flatten array with inferred source dimensions for variable '{var_name}'. "
                    f"Source array must have explicit dimensions",
                    node,
                )
                return False
            source_element_count *= dim_size

        # 3. Handle size inference for [_] targets
        if target_type.dimensions[0] == "_":
            # Infer the size from source array element count
            target_type.dimensions[0] = source_element_count
            # Size inference complete - no need for further validation
        else:
            # 4. Explicit target size - validate against source
            target_size = target_type.dimensions[0]
            if source_element_count != target_size:
                self._error(
                    f"Array flattening element count mismatch for variable '{var_name}': "
                    f"source array has {source_element_count} elements "
                    f"({' × '.join(map(str, source_type.dimensions))}) "
                    f"but target array expects {target_size} elements. "
                    f"Element counts must match exactly for safe flattening",
                    node,
                )
                return False

        # All validation passed - flattening is valid
        return True

    def _extract_array_type_info(self, array_type: ConcreteArrayType) -> Dict:
        """
        Extract array type information for multidim analyzer.

        Converts ConcreteArrayType to the format expected by MultidimensionalArrayAnalyzer.
        """
        return {
            "element_type": array_type.element_type,
            "dimensions": array_type.dimensions,
            "is_concrete": True,
        }

    def _format_array_type(self, array_type: ConcreteArrayType) -> str:
        """Format array type for error messages."""
        dims_str = "".join(f"[{dim}]" for dim in array_type.dimensions)
        return f"{dims_str}{array_type.element_type.name.lower()}"

    def _get_value_hint(self, value_node: Dict) -> str:
        """Get a hint string for the value in error messages."""
        value_type = value_node.get("type")
        if value_type == "identifier":
            return value_node.get("name", "value")
        elif value_type == "array_copy":
            inner_array = value_node.get("array", {})
            if inner_array.get("type") == "identifier":
                return inner_array.get("name", "value")
            return "value"
        return "value"
