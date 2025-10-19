"""
Comptime Block Evaluation Module

Handles block evaluability classification and analysis to determine whether
blocks can preserve comptime types or require explicit context.

Responsibilities:
- Compile-time vs runtime block classification
- Function call and conditional detection
- Runtime variable usage analysis
- Block context validation
- Detailed error messages for runtime requirements

This module centralizes all the block evaluation logic that was extracted
during the centralization effort.
"""

from typing import Dict, List, Optional

from .type_operations import TypeOperations
from ..symbol_table import SymbolTable
from ..types import HexenType, BlockEvaluability
from ...ast_nodes import NodeType


class BlockEvaluation:
    """
    Block evaluability classification and comptime context analysis.

    Determines whether expression blocks can preserve comptime types or
    require explicit context for immediate resolution based on the
    enhanced unified block system.
    """

    def __init__(self, symbol_table: SymbolTable, type_ops: TypeOperations):
        """
        Initialize block evaluation with dependencies.

        Args:
            symbol_table: Symbol table for variable type lookups
            type_ops: TypeOperations instance for type utilities
        """
        self.symbol_table = symbol_table
        self.type_ops = type_ops

    # =========================================================================
    # COMPTIME TYPE PRESERVATION LOGIC
    # =========================================================================

    def should_preserve_comptime_types(self, evaluability: BlockEvaluability) -> bool:
        """
        Determine if comptime types should be preserved based on evaluability.

        Args:
            evaluability: Block evaluability classification

        Returns:
            True if comptime types should be preserved for flexibility
        """
        return evaluability == BlockEvaluability.COMPILE_TIME

    def requires_explicit_context(self, evaluability: BlockEvaluability) -> bool:
        """
        Determine if explicit type context is required for runtime blocks.

        Args:
            evaluability: Block evaluability classification

        Returns:
            True if explicit context is required for immediate resolution
        """
        return evaluability == BlockEvaluability.RUNTIME

    def requires_explicit_comptime_context(self, expression: Dict) -> bool:
        """
        Determine if expression requires explicit context for comptime resolution.

        Args:
            expression: Expression AST node

        Returns:
            True if expression requires explicit context
        """
        # Mixed comptime operations typically require context
        expr_type = expression.get("type")

        if expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                # This is a simplified check - would need full type analysis
                return True  # Conservative: assume binary ops need context

        return False

    # =========================================================================
    # BLOCK EVALUABILITY CLASSIFICATION
    # =========================================================================

    def classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
        """
        Classify block as compile-time or runtime evaluable.

        This is the foundation for the enhanced unified block system that determines
        whether expression blocks can preserve comptime types or require explicit context.

        Compile-time evaluable criteria (ALL must be true):
        - All operations involve only comptime literals
        - NO conditional expressions (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
        - NO runtime function calls (functions always return concrete types)
        - NO runtime variable usage (concrete types)
        - All computations can be evaluated at compile-time

        Runtime evaluable triggers (ANY triggers runtime):
        - Function calls: Functions always return concrete types
        - Conditionals: All conditionals are runtime per specification
        - Concrete variable usage: Mixing comptime + concrete types

        Args:
            statements: List of statements in the block

        Returns:
            BlockEvaluability.COMPILE_TIME if block can preserve comptime types
            BlockEvaluability.RUNTIME if block requires explicit context
        """
        # Enhanced detection with function calls and conditionals

        # Priority 1: Check for runtime operations (function calls, conditionals)
        if self._contains_runtime_operations(statements):
            return BlockEvaluability.RUNTIME

        # Priority 2: Check for concrete variable usage (mixing comptime + concrete = runtime)
        if self.has_runtime_variables(statements):
            return BlockEvaluability.RUNTIME

        # Priority 3: If all operations are comptime-only, block is compile-time evaluable
        if self.has_comptime_only_operations(statements):
            return BlockEvaluability.COMPILE_TIME

        # Default to runtime for safety (unknown cases should require explicit context)
        return BlockEvaluability.RUNTIME

    # =========================================================================
    # RUNTIME OPERATION DETECTION
    # =========================================================================

    def _contains_runtime_operations(self, statements: List[Dict]) -> bool:
        """
        Detect runtime operations that trigger runtime classification.

        Runtime operations include:
        - Function calls (functions always return concrete types)
        - Conditional expressions (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
        - Runtime variable usage (concrete types) - handled by existing logic

        This enhances the block evaluability system with comprehensive runtime detection.

        Args:
            statements: List of statements to analyze

        Returns:
            True if any runtime operations found, False if all operations are comptime
        """
        return self._contains_function_calls(statements) or self._contains_conditionals(
            statements
        )

    def _contains_function_calls(self, statements: List[Dict]) -> bool:
        """
        Recursively detect function calls in block statements.

        Function calls always trigger runtime classification because:
        1. Functions always return concrete types (never comptime types)
        2. Function execution happens at runtime
        3. Results cannot be computed at compile-time

        Args:
            statements: List of statements to analyze

        Returns:
            True if any function calls found in statements or sub-expressions
        """
        for statement in statements:
            if self._statement_contains_function_calls(statement):
                return True
        return False

    def _contains_conditionals(self, statements: List[Dict]) -> bool:
        """
        Recursively detect conditional expressions in block statements.

        Conditionals always trigger runtime classification per CONDITIONAL_SYSTEM.md:
        1. All conditionals are runtime (specification requirement)
        2. Condition evaluation happens at runtime
        3. Branch selection cannot be determined at compile-time

        Args:
            statements: List of statements to analyze

        Returns:
            True if any conditionals found in statements or sub-expressions
        """
        for statement in statements:
            if self._statement_contains_conditionals(statement):
                return True
        return False

    def _statement_contains_function_calls(self, statement: Dict) -> bool:
        """
        Check if a single statement contains function calls.

        Args:
            statement: Statement AST node to analyze

        Returns:
            True if statement contains function calls, False otherwise
        """
        stmt_type = statement.get("type")

        # Function call statements are direct function calls
        if stmt_type == NodeType.FUNCTION_CALL_STATEMENT.value:
            return True

        # Check expressions in declaration statements
        if stmt_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
            value = statement.get("value")
            if value and value != "undef":
                return self._expression_contains_function_calls(value)

        # Check expressions in assign/assignment statements
        elif stmt_type in [
            NodeType.ASSIGN_STATEMENT.value,
            NodeType.ASSIGNMENT_STATEMENT.value,
        ]:
            value = statement.get("value")
            if value:
                return self._expression_contains_function_calls(value)

        # Check expressions in return statements
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_contains_function_calls(value)

        return False

    def _statement_contains_conditionals(self, statement: Dict) -> bool:
        """
        Check if a single statement contains conditionals.

        Args:
            statement: Statement AST node to analyze

        Returns:
            True if statement contains conditionals, False otherwise
        """
        stmt_type = statement.get("type")

        # Direct conditional statements
        if stmt_type == NodeType.CONDITIONAL_STATEMENT.value:
            return True

        # Check expressions in declaration statements
        if stmt_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
            value = statement.get("value")
            if value and value != "undef":
                return self._expression_contains_conditionals(value)

        # Check expressions in assign/assignment statements
        elif stmt_type in [
            NodeType.ASSIGN_STATEMENT.value,
            NodeType.ASSIGNMENT_STATEMENT.value,
        ]:
            value = statement.get("value")
            if value:
                return self._expression_contains_conditionals(value)

        # Check expressions in return statements
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_contains_conditionals(value)

        return False

    def _expression_contains_function_calls(self, expression: Dict) -> bool:
        """
        Recursively analyze expression for function calls.

        This performs deep analysis of expression trees to find any nested
        function calls that would trigger runtime classification.

        Args:
            expression: Expression AST node to analyze

        Returns:
            True if expression contains function calls, False otherwise
        """
        expr_type = expression.get("type")

        # Direct function call expression
        if expr_type == NodeType.FUNCTION_CALL.value:
            return True

        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and self._expression_contains_function_calls(left):
                return True
            if right and self._expression_contains_function_calls(right):
                return True

        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand and self._expression_contains_function_calls(operand):
                return True

        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand and self._expression_contains_function_calls(operand):
                return True

        # Block expressions: recursively analyze (nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self._contains_function_calls(statements)

        return False

    def _expression_contains_conditionals(self, expression: Dict) -> bool:
        """
        Recursively analyze expression for conditionals.

        This performs deep analysis of expression trees to find any nested
        conditionals that would trigger runtime classification.

        Args:
            expression: Expression AST node to analyze

        Returns:
            True if expression contains conditionals, False otherwise
        """
        expr_type = expression.get("type")

        # Direct conditional expression (if-expressions used as values)
        # Per CONDITIONAL_SYSTEM.md: All conditionals are runtime, even with comptime branches
        if expr_type == NodeType.CONDITIONAL_STATEMENT.value:
            return True

        # Binary operations: check both operands
        if expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and self._expression_contains_conditionals(left):
                return True
            if right and self._expression_contains_conditionals(right):
                return True

        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand and self._expression_contains_conditionals(operand):
                return True

        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand and self._expression_contains_conditionals(operand):
                return True

        # Block expressions: recursively analyze (nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self._contains_conditionals(statements)

        return False

    # =========================================================================
    # COMPTIME-ONLY OPERATION DETECTION
    # =========================================================================

    def has_comptime_only_operations(self, statements: List[Dict]) -> bool:
        """
        Check if all operations in the block use only comptime types.

        Comptime operations include:
        - Literal values (42, 3.14, "string", true/false)
        - Arithmetic on comptime types (42 + 100, 3.14 * 2.0)
        - Variable declarations with comptime initializers
        - Variable references to other comptime-only variables

        Args:
            statements: List of statements to analyze

        Returns:
            True if all operations are comptime-only, False otherwise
        """
        for statement in statements:
            if not self.statement_has_comptime_only_operations(statement):
                return False
        return True

    def statement_has_comptime_only_operations(self, statement: Dict) -> bool:
        """
        Check if a single statement contains only comptime operations.

        Args:
            statement: Statement AST node to analyze

        Returns:
            True if statement uses only comptime operations, False otherwise
        """
        stmt_type = statement.get("type")

        # Variable declarations: check initializer
        if stmt_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
            value = statement.get("value")
            if value and value != "undef":
                return self.expression_has_comptime_only_operations(value)
            return True  # undef is considered comptime

        # Assign statements: check the assigned expression
        elif stmt_type == NodeType.ASSIGN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_comptime_only_operations(value)
            return False

        # Assignment statements: check the assigned expression
        elif stmt_type == NodeType.ASSIGNMENT_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_comptime_only_operations(value)
            return False

        # Return statements: check the returned expression
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_comptime_only_operations(value)
            return True  # bare return is comptime

        # Other statement types are handled by runtime operation detection
        # For safety, assume they're runtime if not explicitly comptime
        return False

    def expression_has_comptime_only_operations(self, expression: Dict) -> bool:
        """
        Check if an expression contains only comptime operations.

        Args:
            expression: Expression AST node to analyze

        Returns:
            True if expression is comptime-only, False otherwise
        """
        expr_type = expression.get("type")

        # Comptime literals
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value]:
            return True

        # Other literals (string, bool) are concrete but considered comptime for this analysis
        if expr_type == NodeType.LITERAL.value:
            return True

        # Variable references: check if variable has comptime type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info:
                    # If variable has comptime type (including ComptimeArrayType instances), it's comptime-only
                    var_type = symbol_info.type
                    # Check for ComptimeArrayType instances
                    from ..types import ComptimeArrayType
                    if isinstance(var_type, ComptimeArrayType):
                        return True  # ComptimeArrayType is comptime-only
                    return var_type in [
                        HexenType.COMPTIME_INT,
                        HexenType.COMPTIME_FLOAT,
                    ]
                else:
                    # FORWARD REFERENCE FIX: If symbol not found, assume it's comptime
                    # This handles cases where variables are referenced within the same block
                    # before they're declared in the symbol table during classification
                    # Better to be conservative and allow these through classification,
                    # then catch real errors during actual analysis
                    return True
            return False

        # Binary operations: both operands must be comptime-only
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                return self.expression_has_comptime_only_operations(
                    left
                ) and self.expression_has_comptime_only_operations(right)
            return False

        # Unary operations: operand must be comptime-only
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand:
                return self.expression_has_comptime_only_operations(operand)
            return False

        # Array literals: elements must all be comptime-only
        elif expr_type == NodeType.ARRAY_LITERAL.value:
            elements = expression.get("elements", [])
            # Empty arrays are considered comptime (will require explicit context anyway)
            if not elements:
                return True
            # All elements must be comptime-only
            return all(
                self.expression_has_comptime_only_operations(elem) for elem in elements
            )

        # Array access: both array and index must be comptime-only
        elif expr_type == NodeType.ARRAY_ACCESS.value:
            array_expr = expression.get("array")
            index_expr = expression.get("index")
            if array_expr and index_expr:
                return self.expression_has_comptime_only_operations(
                    array_expr
                ) and self.expression_has_comptime_only_operations(index_expr)
            return False

        # Array copy: array expression must be comptime-only
        elif expr_type == NodeType.ARRAY_COPY.value:
            array_expr = expression.get("array")
            if array_expr:
                return self.expression_has_comptime_only_operations(array_expr)
            return False

        # Property access: object expression must be comptime-only
        elif expr_type == NodeType.PROPERTY_ACCESS.value:
            object_expr = expression.get("object")
            if object_expr:
                return self.expression_has_comptime_only_operations(object_expr)
            return False

        # Explicit conversions: operand must be comptime-only (though result becomes concrete)
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand:
                return self.expression_has_comptime_only_operations(operand)
            return False

        # Block expressions: recursively analyze (this enables nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self.has_comptime_only_operations(statements)

        # Function calls and conditionals are handled by runtime operation detection
        # For safety, assume they're runtime if not explicitly comptime
        return False

    # =========================================================================
    # RUNTIME VARIABLE DETECTION
    # =========================================================================

    def has_runtime_variables(self, statements: List[Dict]) -> bool:
        """
        Check if the block uses variables with concrete (runtime) types.

        This detects mixing of comptime and concrete types, which requires
        explicit type context for proper resolution.

        Args:
            statements: List of statements to analyze

        Returns:
            True if block uses concrete variables, False if only comptime variables
        """
        for statement in statements:
            if self.statement_has_runtime_variables(statement):
                return True
        return False

    def statement_has_runtime_variables(self, statement: Dict) -> bool:
        """
        Check if a statement uses concrete (runtime) variables.

        Args:
            statement: Statement AST node to analyze

        Returns:
            True if statement uses concrete variables, False otherwise
        """
        stmt_type = statement.get("type")

        # Variable declarations: check if explicitly typed with concrete type
        if stmt_type in [
            NodeType.VAL_DECLARATION.value,
            NodeType.MUT_DECLARATION.value,
        ]:
            # If explicit type annotation is concrete, it's runtime
            type_annotation = statement.get("type_annotation")
            if type_annotation:
                # Parse type annotation to check if it's concrete
                from ..type_util import is_concrete_type

                return is_concrete_type(type_annotation)

            # Check initializer expression for concrete variable usage
            value = statement.get("value")
            if value and value != "undef":
                return self.expression_has_runtime_variables(value)
            return False

        # Assign and assignment statements: check expressions
        elif stmt_type in [
            NodeType.ASSIGN_STATEMENT.value,
            NodeType.ASSIGNMENT_STATEMENT.value,
        ]:
            value = statement.get("value")
            if value:
                return self.expression_has_runtime_variables(value)
            return False

        # Return statements: check expression
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_runtime_variables(value)
            return False

        return False

    def expression_has_runtime_variables(self, expression: Dict) -> bool:
        """
        Check if an expression uses concrete (runtime) variables.

        Args:
            expression: Expression AST node to analyze

        Returns:
            True if expression uses concrete variables, False otherwise
        """
        expr_type = expression.get("type")

        # Literals are not runtime variables
        if expr_type in [
            NodeType.COMPTIME_INT.value,
            NodeType.COMPTIME_FLOAT.value,
            NodeType.LITERAL.value,
        ]:
            return False

        # Variable references: check if variable has concrete type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info:
                    var_type = symbol_info.type
                    # Comptime types (including ComptimeArrayType instances) are not runtime variables
                    from ..types import ComptimeArrayType
                    if isinstance(var_type, ComptimeArrayType):
                        return False  # ComptimeArrayType is not a runtime variable
                    comptime_types = {
                        HexenType.COMPTIME_INT,
                        HexenType.COMPTIME_FLOAT,
                    }
                    return var_type not in comptime_types
            return False

        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                return self.expression_has_runtime_variables(
                    left
                ) or self.expression_has_runtime_variables(right)
            return False

        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand:
                return self.expression_has_runtime_variables(operand)
            return False

        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand:
                return self.expression_has_runtime_variables(operand)
            return False

        # Block expressions: recursively analyze
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self.has_runtime_variables(statements)

        # Array literals: check all elements for runtime variables
        elif expr_type == NodeType.ARRAY_LITERAL.value:
            elements = expression.get("elements", [])
            return any(self.expression_has_runtime_variables(elem) for elem in elements)

        # Array access: check both array and index for runtime variables
        elif expr_type == NodeType.ARRAY_ACCESS.value:
            array_expr = expression.get("array")
            index_expr = expression.get("index")
            if array_expr and index_expr:
                return self.expression_has_runtime_variables(
                    array_expr
                ) or self.expression_has_runtime_variables(index_expr)
            return False

        # Array copy: check array expression for runtime variables
        elif expr_type == NodeType.ARRAY_COPY.value:
            array_expr = expression.get("array")
            if array_expr:
                return self.expression_has_runtime_variables(array_expr)
            return False

        # Property access: check object expression for runtime variables
        elif expr_type == NodeType.PROPERTY_ACCESS.value:
            object_expr = expression.get("object")
            if object_expr:
                return self.expression_has_runtime_variables(object_expr)
            return False

        return False

    # =========================================================================
    # RUNTIME OPERATION CONTEXT VALIDATION
    # =========================================================================

    def validate_runtime_block_context(
        self, statements: List[Dict], evaluability: BlockEvaluability
    ) -> Optional[str]:
        """
        Validate that runtime blocks have appropriate context and generate enhanced error messages.

        Enhanced in Session 4 with context-specific error messages and actionable guidance.
        Provides detailed error messages explaining why blocks require runtime context
        when they contain function calls or conditionals.

        Args:
            statements: List of statements in the block
            evaluability: Block evaluability classification

        Returns:
            Enhanced error message string if validation fails, None if validation passes
        """
        if evaluability != BlockEvaluability.RUNTIME:
            return None  # Compile-time blocks don't need validation

        # Generate enhanced error messages with actionable guidance
        reasons = []

        # Check for function calls with enhanced messaging
        if self._contains_function_calls(statements):
            reasons.append(
                "contains function calls (functions always return concrete types)"
            )

        # Check for conditionals with enhanced messaging
        if self._contains_conditionals(statements):
            reasons.append(
                "contains conditional expressions (all conditionals are runtime per specification)"
            )

        # Check for concrete variable usage with enhanced messaging
        if self.has_runtime_variables(statements):
            reasons.append("uses concrete type variables")

        if reasons:
            # Use enhanced error message generation from Session 4
            from ..errors import BlockAnalysisError

            return BlockAnalysisError.explicit_type_annotation_required(
                reasons, "type annotation"
            )

        return None

    def get_runtime_operation_reason(self, statements: List[Dict]) -> str:
        """
        Get a detailed reason why the block is classified as runtime with enhanced explanations.

        Enhanced in Session 4 to provide educational explanations and specification references.
        This helps generate specific error messages for different types of runtime operations.

        Args:
            statements: List of statements in the block

        Returns:
            Enhanced human-readable string explaining the runtime classification reason
        """
        reasons = []
        explanations = []

        # Check for function calls with enhanced explanations
        if self._contains_function_calls(statements):
            reasons.append(
                "Function calls detected (functions always return concrete types)"
            )
            from ..errors import BlockAnalysisError

            explanations.append(BlockAnalysisError.function_call_runtime_explanation())

        # Check for conditionals with enhanced explanations
        if self._contains_conditionals(statements):
            reasons.append(
                "Conditional expressions detected (all conditionals are runtime per CONDITIONAL_SYSTEM.md)"
            )
            from ..errors import BlockAnalysisError

            explanations.append(BlockAnalysisError.conditional_runtime_explanation())

        # Check for concrete variable usage with enhanced explanations
        if self.has_runtime_variables(statements):
            reasons.append(
                "Concrete type variables detected (mixing comptime and concrete types)"
            )

        if not reasons:
            return "Unknown runtime operations detected"

        # Provide enhanced explanation with actionable guidance
        basic_reason = ". ".join(reasons) + "."
        if explanations:
            # Include first explanation for educational purposes
            return f"{basic_reason}\n\n{explanations[0]}"

        return basic_reason

    # =========================================================================
    # CONDITIONAL BRANCH ANALYSIS
    # =========================================================================

    def validate_conditional_branch_compatibility(
        self,
        branch_types: List[HexenType],
        target_type: Optional[HexenType],
        error_callback,
        node: Dict,
    ) -> Optional[HexenType]:
        """
        Validate type compatibility across conditional branches and return unified type.

        Implements the conditional type unification logic from ExpressionAnalyzer.

        Args:
            branch_types: Types from conditional branches that use assign
            target_type: Optional target type for context-guided resolution
            error_callback: Function to call for error reporting
            node: AST node for error reporting

        Returns:
            Unified type or HexenType.UNKNOWN if incompatible
        """
        if not branch_types:
            # If no branches contribute types (all return early), use target_type if available
            return target_type if target_type else HexenType.UNKNOWN

        # If we have a target type, use it for context-guided resolution
        if target_type:
            # All assign branches should be compatible with the target type
            # Comptime types will adapt automatically
            for branch_type in branch_types:
                if self.type_ops.is_comptime_type(branch_type):
                    # Comptime types adapt to target context - this is handled by the system
                    continue
                elif branch_type != target_type:
                    # Require exact type match for concrete types (transparent costs principle)
                    # Use enhanced error message with explicit conversion suggestions
                    from ..errors import BlockAnalysisError

                    error_callback(
                        BlockAnalysisError.branch_type_mismatch(
                            branch_type.name.lower(),
                            target_type.name.lower(),
                            "conditional branch",
                        ),
                        node,
                    )
                    return HexenType.UNKNOWN
            return target_type

        # Without target context, implement basic type unification
        return self._unify_branch_types_without_context(
            branch_types, error_callback, node
        )

    def _unify_branch_types_without_context(
        self, branch_types: List[HexenType], error_callback, node: Dict
    ) -> HexenType:
        """
        Unify branch types without target context using comptime promotion rules.

        Args:
            branch_types: Types from conditional branches
            error_callback: Function to call for error reporting
            node: AST node for error reporting

        Returns:
            Unified type or HexenType.UNKNOWN if incompatible
        """
        if not branch_types:
            return HexenType.UNKNOWN

        unified_type = branch_types[0]

        # Check if all types are the same or comptime-compatible
        all_comptime_int = all(t == HexenType.COMPTIME_INT for t in branch_types)
        all_comptime_float = all(t == HexenType.COMPTIME_FLOAT for t in branch_types)
        all_same_concrete = all(t == unified_type for t in branch_types)

        if all_comptime_int:
            return HexenType.COMPTIME_INT
        elif all_comptime_float:
            return HexenType.COMPTIME_FLOAT
        elif all_same_concrete:
            return unified_type
        else:
            # Mixed types require explicit target context for resolution
            # Use enhanced error message with actionable guidance
            from ..errors import BlockAnalysisError

            type_names = [bt.name.lower() for bt in branch_types]
            error_callback(
                BlockAnalysisError.ambiguity_resolution_guidance(
                    f"conditional branches with types: {', '.join(type_names)}",
                    [
                        "explicit target type annotation",
                        "explicit type conversions in branches",
                    ],
                ),
                node,
            )
            return HexenType.UNKNOWN

    def analyze_conditional_branch_with_target_context(
        self, branch_node: Dict, target_type: HexenType, analyze_expression_callback
    ) -> Optional[HexenType]:
        """
        Analyze conditional branch with target type context for assign statements.

        Extracts the comptime-specific logic for analyzing conditional branches
        with target type propagation from ExpressionAnalyzer.

        Args:
            branch_node: Block AST node (the branch)
            target_type: Target type for context-guided resolution
            analyze_expression_callback: Function to analyze expressions

        Returns:
            Type from the assign statement or None if not applicable
        """
        if not branch_node or branch_node.get("type") != "block":
            return None

        statements = branch_node.get("statements", [])
        if not statements:
            return None

        # The last statement should be an assign statement
        last_statement = statements[-1]
        if last_statement.get("type") != "assign_statement":
            return None

        # Analyze the assign statement with target type propagation
        assign_value = last_statement.get("value")
        if assign_value:
            # Use the target type for context-guided resolution
            return analyze_expression_callback(assign_value, target_type)
        else:
            return None

    def check_branch_uses_assign(self, branch_node: Dict) -> bool:
        """
        Check if a branch (block) uses assign statement instead of return statement.

        Centralizes the branch analysis logic from ExpressionAnalyzer.

        Args:
            branch_node: Block AST node

        Returns:
            True if branch ends with assign statement, False if it ends with return
        """
        if not branch_node or branch_node.get("type") != "block":
            return False

        statements = branch_node.get("statements", [])
        if not statements:
            return False

        # Check the last statement type
        last_statement = statements[-1]
        last_stmt_type = last_statement.get("type")

        if last_stmt_type == "assign_statement":
            return True
        elif last_stmt_type == "return_statement":
            return False
        else:
            # If last statement is neither assign nor return, this is an error
            # but we'll let the block analyzer handle that error
            return False
