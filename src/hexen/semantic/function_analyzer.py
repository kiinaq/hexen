"""
Function Call Analysis for Hexen Language

Handles function call resolution and parameter type checking including:
- Function name lookup and validation
- Argument-parameter matching and validation
- Parameter type context for comptime type resolution
- TYPE_SYSTEM.md rule application to function arguments
- Function call return type inference
- Pass-by-value semantics validation

Implements the unified type resolution strategy from FUNCTION_SYSTEM.md.

## Pass-by-Value Semantics

All Hexen parameters follow **pass-by-value semantics**:
- Parameters are copied to the function's stack frame
- Modifications to parameters affect only the local copy
- Caller's values remain unchanged
- `mut` parameters allow local reassignment for multi-step computations
- Side effects must be communicated through return values

This design maintains Hexen's stack-only memory model and ensures predictable,
safe behavior without requiring reference semantics or borrow checking.

**Implementation Status**: ✅ Task 7 Complete (Week 2)
- Semantic analysis validates pass-by-value correctness
- All parameter types (scalars, arrays, strings, bools) follow pass-by-value
- Test coverage: 23 comprehensive tests in test_pass_by_value.py
- Caller isolation guaranteed through type system constraints
"""

from typing import Dict, Optional, Callable, Union

from .type_util import can_coerce
from .types import HexenType, ConcreteArrayType, ComptimeArrayType


class FunctionAnalyzer:
    """
    Specialized analyzer for function call analysis.

    Implements function call resolution following FUNCTION_SYSTEM.md:
    - Function name lookup and validation
    - Parameter type context for argument resolution
    - Comptime type preservation until parameter context forces resolution
    - TYPE_SYSTEM.md conversion rules for all arguments
    - Clear error messages for function call issues

    Design follows the callback pattern for main analyzer integration.
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[
            [Dict, Optional[Union[HexenType, ConcreteArrayType, ComptimeArrayType]]],
            Union[HexenType, ConcreteArrayType, ComptimeArrayType],
        ],
        lookup_function_callback: Callable[[str], Optional[object]],
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._lookup_function = lookup_function_callback

    def analyze_function_call(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze a function call and return its type.

        Args:
            node: Function call AST node
            target_type: Optional target type (currently unused for function calls)

        Returns:
            Function return type, or HexenType.UNKNOWN for invalid calls

        Implementation follows FUNCTION_SYSTEM.md parameter-guided resolution:
        1. Function name lookup and validation
        2. Argument count validation
        3. Argument-parameter type resolution using TYPE_SYSTEM.md rules
        4. Return function's return type
        """
        function_name = node.get("function_name")
        if not function_name:
            self._error("Function call missing function name", node)
            return HexenType.UNKNOWN

        # Look up function signature
        function_signature = self._lookup_function(function_name)
        if not function_signature:
            self._error(f"Undefined function: '{function_name}'", node)
            return HexenType.UNKNOWN

        # Validate argument count
        arguments = node.get("arguments", [])
        expected_count = len(function_signature.parameters)
        actual_count = len(arguments)

        if actual_count != expected_count:
            self._error(
                f"Function '{function_name}' expects {expected_count} argument{'s' if expected_count != 1 else ''}, "
                f"but {actual_count} provided",
                node,
            )
            return HexenType.UNKNOWN

        # Analyze each argument against its corresponding parameter
        for i, (argument, parameter) in enumerate(
            zip(arguments, function_signature.parameters)
        ):
            self._analyze_argument_against_parameter(
                argument, parameter, function_name, i + 1
            )

        # Return the function's return type
        return function_signature.return_type

    def _analyze_argument_against_parameter(
        self, argument: Dict, parameter, function_name: str, position: int
    ):
        """
        Analyze a single argument against its corresponding parameter.

        Args:
            argument: Argument expression AST node
            parameter: Parameter object with type and mutability info
            function_name: Function name for error messages
            position: Argument position (1-based) for error messages

        Implementation follows FUNCTION_SYSTEM.md type resolution:
        - Parameter type provides context for argument resolution
        - Comptime types adapt seamlessly to parameter types
        - Mixed concrete types require explicit conversions
        - Same TYPE_SYSTEM.md rules as variable assignments
        - Arrays require explicit [..] for concrete array arguments
        """
        # Check for explicit copy requirement on array parameters
        self._check_array_argument_copy_requirement(
            argument, parameter, function_name, position
        )

        # OPTIMIZATION: Only perform double-analysis for array parameters
        # This avoids spurious errors from contextless analysis of non-array expressions
        # (e.g., conditional expressions with mixed comptime types that would resolve with context)
        if isinstance(parameter.param_type, ConcreteArrayType):
            # FIRST: Analyze argument WITHOUT context to preserve ComptimeArrayType for size validation
            argument_type_without_context = self._analyze_expression(argument, None)

            # NEW: Validate comptime array size compatibility BEFORE materialization (Issue #1 fix)
            if isinstance(argument_type_without_context, ComptimeArrayType):
                if not self._validate_comptime_array_size(
                    argument_type_without_context,
                    parameter.param_type,
                    function_name,
                    position,
                    argument,
                ):
                    # Error already reported, skip further validation
                    return

        # Analyze with parameter type as context for materialization and coercion
        # This enables comptime type adaptation and enforces TYPE_SYSTEM.md rules
        argument_type = self._analyze_expression(argument, parameter.param_type)

        # Validate type compatibility using TYPE_SYSTEM.md conversion rules
        if not can_coerce(argument_type, parameter.param_type):
            # Check if this is an array size mismatch for better error message
            if isinstance(argument_type, ConcreteArrayType) and isinstance(
                parameter.param_type, ConcreteArrayType
            ):
                # Array size mismatch - provide array-specific error
                self._error_array_size_mismatch(
                    function_name, position, parameter, argument_type, argument
                )
            else:
                # Regular type mismatch - use standard error message
                # Handle error message for both HexenType and ConcreteArrayType
                param_type_str = (
                    parameter.param_type.value
                    if hasattr(parameter.param_type, "value")
                    else str(parameter.param_type)
                )
                arg_type_str = (
                    argument_type.value
                    if hasattr(argument_type, "value")
                    else str(argument_type)
                )

                self._error(
                    f"Function '{function_name}' argument {position}: "
                    f"Cannot assign {arg_type_str} to parameter '{parameter.name}' of type {param_type_str}. "
                    f"Use explicit conversion: 'expression:{param_type_str}'",
                    argument,
                )

    def _check_array_argument_copy_requirement(
        self, argument: Dict, parameter, function_name: str, position: int
    ):
        """
        Validate that concrete array arguments use explicit [..] copy operator.

        Args:
            argument: Argument expression AST node
            parameter: Parameter object with type and mutability info
            function_name: Function name for error messages
            position: Argument position (1-based) for error messages

        Implementation of "Explicit Danger, Implicit Safety" principle:
        - Comptime arrays (literals): No [..] needed (first materialization)
        - Concrete arrays (variables): Require explicit [..] copy operator
        - This makes array copy performance costs visible
        """
        from .type_util import is_array_type
        from .arrays.error_messages import ArrayErrorMessages

        # Only check if parameter is an array type
        if not is_array_type(parameter.param_type):
            return

        # Check argument type
        arg_type = argument.get("type")

        # Allowed without explicit copy: array literals (comptime arrays)
        if arg_type == "array_literal":
            # Comptime array - first materialization, no copy needed
            return

        # Allowed without explicit copy: already has [..] operator
        if arg_type == "array_copy":
            # Explicit copy present - this is correct!
            return

        # NEW: After range system migration, arr[..] is now array_access with range index
        # Check if this is array_access with an unbounded range (which is equivalent to [..])
        if arg_type == "array_access":
            index_expr = argument.get("index", {})
            # Check if index is an unbounded range expression (..)
            if index_expr.get("type") == "range_expr":
                start = index_expr.get("start")
                end = index_expr.get("end")
                step = index_expr.get("step")
                # Unbounded range (..) has no start, end, or step
                if start is None and end is None and step is None:
                    # This is arr[..] - explicit copy present!
                    return
            # Other array_access expressions (with specific indices or bounded ranges)
            # fall through to require wrapping in [..]

        # Allowed without explicit copy: function calls (return fresh arrays)
        if arg_type == "function_call":
            # Function returns fresh array - no copy needed
            return

        # Allowed without explicit copy: expression blocks (build fresh arrays)
        if arg_type == "block":
            # Expression block builds fresh array - no copy needed
            return

        # Allowed without explicit copy: type conversion expressions that include [..]
        # Example: matrix[..]:[6]i32 already has explicit copy, produces fresh array
        if arg_type == "explicit_conversion_expression":
            # Check if the inner expression is an array_copy operation (old parser)
            # or array_access with unbounded range (new parser)
            inner_expr = argument.get("expression", {})
            inner_type = inner_expr.get("type")

            if inner_type == "array_copy":
                # Old parser: Type conversion with [..] produces fresh array
                return

            if inner_type == "array_access":
                # New parser: Check if this is array[..] pattern
                index_expr = inner_expr.get("index", {})
                if index_expr.get("type") == "range_expr":
                    start = index_expr.get("start")
                    end = index_expr.get("end")
                    step = index_expr.get("step")
                    # Unbounded range (..) means explicit copy
                    if start is None and end is None and step is None:
                        return
            # Otherwise, fall through to require explicit copy

        # Everything else requires explicit [..]
        # Most common case: identifier (variable reference to existing array)
        if arg_type == "identifier":
            # Check if this identifier refers to a comptime array (val + array literal)
            # or a concrete array (val + explicit type annotation)
            argument_type_without_context = self._analyze_expression(argument, None)

            # If it's a comptime array, no copy needed (first materialization)
            if isinstance(argument_type_without_context, ComptimeArrayType):
                return

            # Concrete array variable - requires explicit copy
            argument_name = argument.get("name", "<unknown>")
            param_type_str = (
                parameter.param_type.value
                if hasattr(parameter.param_type, "value")
                else str(parameter.param_type)
            )

            self._error(
                ArrayErrorMessages.missing_explicit_copy_for_array_argument(
                    function_name, parameter.name, param_type_str, argument_name
                ),
                argument,
            )
            return

        # Other expression types also need explicit copy
        # (array access, property access, binary operations, etc.)
        param_type_str = (
            parameter.param_type.value
            if hasattr(parameter.param_type, "value")
            else str(parameter.param_type)
        )

        self._error(
            f"Array argument to function '{function_name}' requires explicit copy operator [..]\n"
            f"Parameter '{parameter.name}' expects type {param_type_str}\n"
            f"Complex array expressions must use explicit [..] to make copy costs visible\n"
            f"Suggestion: wrap expression in array copy: (<expression>)[..]",
            argument,
        )

    def _error_array_size_mismatch(
        self,
        function_name: str,
        position: int,
        parameter,
        argument_type: ConcreteArrayType,
        argument: Dict,
    ):
        """
        Generate array-specific error message for size mismatches.

        Args:
            function_name: Function name for error messages
            position: Argument position (1-based)
            parameter: Parameter object with type info
            argument_type: Actual argument type (ConcreteArrayType)
            argument: Argument AST node for error reporting
        """
        param_array_type = parameter.param_type
        arg_type_str = str(argument_type)
        param_type_str = str(param_array_type)

        # Check if this is a size mismatch vs element type mismatch
        if argument_type.element_type != param_array_type.element_type:
            # Element type mismatch
            self._error(
                f"Function '{function_name}' argument {position}: Array element type mismatch\n"
                f"Parameter '{parameter.name}' expects {param_type_str}\n"
                f"Argument has type {arg_type_str}\n"
                f"Cannot convert {argument_type.element_type.value} array to {param_array_type.element_type.value} array\n"
                f"Arrays must have matching element types",
                argument,
            )
        elif len(argument_type.dimensions) != len(param_array_type.dimensions):
            # Dimension count mismatch
            self._error(
                f"Function '{function_name}' argument {position}: Array dimension mismatch\n"
                f"Parameter '{parameter.name}' expects {param_type_str} ({len(param_array_type.dimensions)}D array)\n"
                f"Argument has type {arg_type_str} ({len(argument_type.dimensions)}D array)\n"
                f"Cannot pass {len(argument_type.dimensions)}D array to {len(param_array_type.dimensions)}D parameter",
                argument,
            )
        else:
            # Size mismatch in at least one dimension
            # Find which dimension(s) mismatch
            mismatched_dims = []
            for i, (arg_dim, param_dim) in enumerate(
                zip(argument_type.dimensions, param_array_type.dimensions)
            ):
                if arg_dim != param_dim:
                    mismatched_dims.append((i, arg_dim, param_dim))

            if len(mismatched_dims) == 1:
                dim_idx, arg_size, param_size = mismatched_dims[0]
                dim_name = (
                    f"dimension {dim_idx}"
                    if len(argument_type.dimensions) > 1
                    else "size"
                )

                self._error(
                    f"Function '{function_name}' argument {position}: Array size mismatch\n"
                    f"Parameter '{parameter.name}' expects {param_type_str}\n"
                    f"Argument has type {arg_type_str}\n"
                    f"Array {dim_name} mismatch: expected {param_size}, got {arg_size}\n"
                    f"Array sizes must match exactly for fixed-size parameters",
                    argument,
                )
            else:
                # Multiple dimension mismatches
                self._error(
                    f"Function '{function_name}' argument {position}: Array size mismatch\n"
                    f"Parameter '{parameter.name}' expects {param_type_str}\n"
                    f"Argument has type {arg_type_str}\n"
                    f"Array sizes must match exactly for fixed-size parameters",
                    argument,
                )

    def _validate_comptime_array_size(
        self,
        comptime_type: ComptimeArrayType,
        target_type: ConcreteArrayType,
        function_name: str,
        position: int,
        argument_node: Dict
    ) -> bool:
        """
        Validate that comptime array dimensions match target parameter dimensions.

        This is the CORE FIX for Issue #1. It prevents:
        - Silent truncation (comptime [5] → parameter [3])
        - Silent padding (comptime [2] → parameter [3])
        - Dimension mismatches (comptime [2][3] → parameter [6])

        Rules:
        1. Dimension count must match
        2. Each dimension checked individually:
           - Inferred dimension ("_") accepts any size
           - Fixed dimension (int) requires exact match
        3. Clear error messages guide user to fix

        Args:
            comptime_type: ComptimeArrayType from argument expression
            target_type: ConcreteArrayType from parameter definition
            function_name: Function name for error messages
            position: Argument position (1-based) for error messages
            argument_node: AST node for error reporting

        Returns:
            True if dimensions compatible, False if mismatch (error already reported)
        """
        # Check dimension count
        if len(comptime_type.dimensions) != len(target_type.dimensions):
            # Report dimension mismatch error
            self._error_comptime_array_dimension_count_mismatch(
                comptime_type, target_type, function_name, position, argument_node
            )
            return False

        # Check each dimension for compatibility
        mismatched_dims = []
        for i, (comptime_dim, target_dim) in enumerate(
            zip(comptime_type.dimensions, target_type.dimensions)
        ):
            if target_dim == "_":
                # Inferred dimension - accepts any size
                continue

            if comptime_dim != target_dim:
                # Fixed dimension mismatch
                mismatched_dims.append((i, comptime_dim, target_dim))

        if mismatched_dims:
            self._error_comptime_array_size_mismatch(
                comptime_type,
                target_type,
                function_name,
                position,
                mismatched_dims,
                argument_node,
            )
            return False

        # All dimensions compatible
        return True

    def _error_comptime_array_dimension_count_mismatch(
        self,
        comptime_type: ComptimeArrayType,
        target_type: ConcreteArrayType,
        function_name: str,
        position: int,
        argument_node: Dict
    ):
        """Generate error for dimension count mismatch"""
        comptime_str = str(comptime_type)
        target_str = str(target_type)

        self._error(
            f"Comptime array dimension count mismatch in function call\n"
            f"  Function: {function_name}(...)\n"
            f"  Argument {position}: comptime array type {comptime_str}\n"
            f"  Parameter expects: {target_str}\n"
            f"\n"
            f"  Comptime array has {len(comptime_type.dimensions)} dimension(s)\n"
            f"  Parameter expects {len(target_type.dimensions)} dimension(s)\n"
            f"\n"
            f"  Cannot materialize {len(comptime_type.dimensions)}D array to "
            f"{len(target_type.dimensions)}D parameter",
            argument_node,
        )

    def _error_comptime_array_size_mismatch(
        self,
        comptime_type: ComptimeArrayType,
        target_type: ConcreteArrayType,
        function_name: str,
        position: int,
        mismatched_dims: list,
        argument_node: Dict
    ):
        """
        Generate detailed error message for size mismatches.

        Provides actionable guidance:
        - Shows exact size mismatch
        - Suggests using inferred-size parameter [_]T
        - Explains that truncation/padding not allowed
        """
        comptime_str = str(comptime_type)
        target_str = str(target_type)

        # Build dimension mismatch details
        if len(mismatched_dims) == 1:
            dim_idx, comptime_size, target_size = mismatched_dims[0]
            dim_detail = (
                f"  Dimension {dim_idx}: comptime size {comptime_size}, "
                f"parameter expects {target_size}\n"
            )
        else:
            dim_lines = []
            for dim_idx, comptime_size, target_size in mismatched_dims:
                dim_lines.append(
                    f"    - Dimension {dim_idx}: {comptime_size} ≠ {target_size}"
                )
            dim_detail = (
                "  Multiple dimension mismatches:\n" + "\n".join(dim_lines) + "\n"
            )

        self._error(
            f"Comptime array size mismatch in function call\n"
            f"  Function: {function_name}(...)\n"
            f"  Argument {position}: comptime array type {comptime_str}\n"
            f"  Parameter expects: {target_str}\n"
            f"\n"
            f"{dim_detail}"
            f"\n"
            f"  Fixed-size parameters require exact size match.\n"
            f"  Cannot truncate or pad comptime arrays.\n"
            f"\n"
            f"  Suggestions:\n"
            f"    - Use inferred-size parameter to accept any size: [_]T\n"
            f"    - Adjust array literal to match parameter size\n"
            f"    - Use slice operation (when implemented) for intentional truncation",
            argument_node
        )
