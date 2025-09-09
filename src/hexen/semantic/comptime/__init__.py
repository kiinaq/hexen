"""
Hexen Comptime Analysis Module

Modular organization of comptime type analysis functionality.
This module provides a centralized ComptimeAnalyzer interface while organizing
functionality into focused, maintainable modules.

Architecture:
- ComptimeAnalyzer: Main facade providing unified interface
- TypeOperations: Core type classification and unification
- BinaryOperations: Binary operation comptime handling
- DeclarationSupport: Variable declaration comptime logic
- BlockEvaluation: Block evaluability classification
- LiteralValidation: Literal coercion and validation

Usage:
    from .comptime import ComptimeAnalyzer

    analyzer = ComptimeAnalyzer(symbol_table)
    is_comptime = analyzer.is_comptime_type(some_type)
"""

from typing import Dict, List, Optional, Union, Any

from .binary_operations import BinaryOperations
from .block_evaluation import BlockEvaluation
from .declaration_support import DeclarationSupport
from .literal_validation import LiteralValidation

# Import all modules for facade pattern
from .type_operations import TypeOperations
from ..symbol_table import SymbolTable
from ..types import HexenType, BlockEvaluability


class ComptimeAnalyzer:
    """
    Centralized comptime type analyzer - single entry point for all comptime operations.

    This facade maintains the centralized interface while delegating to specialized modules.
    All existing method signatures are preserved for backward compatibility.

    The modular architecture enables:
    - Focused development on specific comptime aspects
    - Independent testing of functionality areas
    - Clear separation of concerns
    - Easier navigation and maintenance

    While preserving:
    - Single source of truth for comptime behavior
    - Consistent API for all analyzers
    - Centralized comptime logic
    """

    def __init__(self, symbol_table: SymbolTable):
        """
        Initialize the comptime analyzer with all specialized modules.

        Args:
            symbol_table: Symbol table for variable type lookups
        """
        # Initialize all specialized modules
        self.type_ops = TypeOperations(symbol_table)
        self.binary_ops = BinaryOperations(self.type_ops)
        self.declarations = DeclarationSupport(self.type_ops)
        self.block_eval = BlockEvaluation(symbol_table, self.type_ops)
        self.literals = LiteralValidation()

        # Store symbol table for direct access if needed
        self.symbol_table = symbol_table

    # =========================================================================
    # TYPE OPERATIONS DELEGATION
    # =========================================================================

    def is_comptime_type(self, type_: HexenType) -> bool:
        """Check if type is a comptime type (COMPTIME_INT or COMPTIME_FLOAT)."""
        return self.type_ops.is_comptime_type(type_)

    def is_mixed_comptime_operation(
        self, left_type: HexenType, right_type: HexenType
    ) -> bool:
        """Detect operations mixing comptime and concrete types."""
        return self.type_ops.is_mixed_comptime_operation(left_type, right_type)

    def unify_comptime_types(self, types: List[HexenType]) -> Optional[HexenType]:
        """Unify multiple comptime types following promotion rules."""
        return self.type_ops.unify_comptime_types(types)

    def get_comptime_promotion_result(
        self, left_type: HexenType, right_type: HexenType
    ) -> HexenType:
        """Get promotion result for comptime types (int + float = float)."""
        return self.type_ops.get_comptime_promotion_result(left_type, right_type)

    def can_comptime_types_mix_safely(
        self,
        left_type: HexenType,
        right_type: HexenType,
        target_type: Optional[HexenType],
    ) -> bool:
        """Check if comptime types can mix safely with given target context."""
        return self.type_ops.can_comptime_types_mix_safely(
            left_type, right_type, target_type
        )

    def are_all_comptime_compatible(self, types: List[HexenType]) -> bool:
        """Check if all types are comptime-compatible for unification."""
        return self.type_ops.are_all_comptime_compatible(types)

    def resolve_comptime_type(
        self, comptime_type: HexenType, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """Resolve a comptime type to a concrete type based on context."""
        return self.type_ops.resolve_comptime_type(comptime_type, target_type)

    def is_mixed_type_operation(
        self, left_type: HexenType, right_type: HexenType
    ) -> bool:
        """Check if an operation involves mixed types that require explicit handling."""
        return self.type_ops.is_mixed_type_operation(left_type, right_type)

    # =========================================================================
    # BINARY OPERATIONS DELEGATION
    # =========================================================================

    def handle_mixed_type_binary_operation(
        self, left_type, right_type, operator, target_type, error_callback, node
    ) -> Optional[HexenType]:
        """Handle mixed type binary operations with BINARY_OPS.md patterns."""
        return self.binary_ops.handle_mixed_type_binary_operation(
            left_type, right_type, operator, target_type, error_callback, node
        )

    def resolve_arithmetic_operation_type(
        self, operator, left_type, right_type, target_type
    ) -> Optional[HexenType]:
        """Resolve comptime-specific arithmetic operation types."""
        return self.binary_ops.resolve_arithmetic_operation_type(
            operator, left_type, right_type, target_type
        )

    def resolve_context_guided_arithmetic(
        self, left_type, right_type, target_type
    ) -> Optional[HexenType]:
        """Resolve arithmetic operation with context guidance for comptime types."""
        return self.binary_ops.resolve_context_guided_arithmetic(
            left_type, right_type, target_type
        )

    def handle_mixed_type_comparison(
        self, operator, left_type, right_type, error_callback, node
    ) -> Optional[HexenType]:
        """Handle mixed type comparison operations following BINARY_OPS.md rules."""
        return self.binary_ops.handle_mixed_type_comparison(
            operator, left_type, right_type, error_callback, node
        )

    def resolve_comptime_binary_operation(
        self, left_type, right_type, operator
    ) -> HexenType:
        """Resolve result type for comptime binary operations."""
        return self.binary_ops.resolve_comptime_binary_operation(
            left_type, right_type, operator
        )

    def has_comptime_operands(self, expression: Dict) -> bool:
        """Check if expression contains any comptime operands."""
        return self.binary_ops.has_comptime_operands(expression)

    # =========================================================================
    # DECLARATION SUPPORT DELEGATION
    # =========================================================================

    def validate_variable_declaration_type_compatibility(
        self, value_type, var_type, value_node, variable_name, error_callback, node
    ) -> bool:
        """Validate type compatibility for variable declarations with comptime awareness."""
        return self.declarations.validate_variable_declaration_type_compatibility(
            value_type, var_type, value_node, variable_name, error_callback, node
        )

    def should_preserve_comptime_for_declaration(
        self, mutability, inferred_type
    ) -> HexenType:
        """Determine final variable type considering comptime type preservation rules."""
        return self.declarations.should_preserve_comptime_for_declaration(
            mutability, inferred_type
        )

    def analyze_declaration_type_inference_error(
        self, value_node, inferred_type, variable_name, error_callback, node
    ) -> bool:
        """Analyze type inference errors with comptime awareness."""
        return self.declarations.analyze_declaration_type_inference_error(
            value_node, inferred_type, variable_name, error_callback, node
        )

    def should_preserve_comptime_type_in_declaration(
        self, mutability, inferred_type
    ) -> bool:
        """Determine if comptime type should be preserved in variable declaration."""
        return self.declarations.should_preserve_comptime_type_in_declaration(
            mutability, inferred_type
        )

    # =========================================================================
    # BLOCK EVALUATION DELEGATION
    # =========================================================================

    def classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
        """Classify block as compile-time or runtime evaluable."""
        return self.block_eval.classify_block_evaluability(statements)

    def should_preserve_comptime_types(self, evaluability: BlockEvaluability) -> bool:
        """Determine if comptime types should be preserved based on evaluability."""
        return self.block_eval.should_preserve_comptime_types(evaluability)

    def requires_explicit_context(self, evaluability: BlockEvaluability) -> bool:
        """Determine if explicit type context is required for runtime blocks."""
        return self.block_eval.requires_explicit_context(evaluability)

    def has_comptime_only_operations(self, statements: List[Dict]) -> bool:
        """Check if all operations in the block use only comptime types."""
        return self.block_eval.has_comptime_only_operations(statements)

    def has_runtime_variables(self, statements: List[Dict]) -> bool:
        """Check if the block uses variables with concrete (runtime) types."""
        return self.block_eval.has_runtime_variables(statements)

    def validate_runtime_block_context(self, statements, evaluability) -> Optional[str]:
        """Validate that runtime blocks have appropriate context and generate helpful error messages."""
        return self.block_eval.validate_runtime_block_context(statements, evaluability)

    def get_runtime_operation_reason(self, statements: List[Dict]) -> str:
        """Get a detailed reason why the block is classified as runtime."""
        return self.block_eval.get_runtime_operation_reason(statements)

    def requires_explicit_comptime_context(self, expression: Dict) -> bool:
        """Determine if expression requires explicit context for comptime resolution."""
        return self.block_eval.requires_explicit_comptime_context(expression)

    # =========================================================================
    # LITERAL VALIDATION DELEGATION
    # =========================================================================

    def validate_comptime_literal_coercion(
        self, value, from_type, to_type, source_text=None
    ) -> None:
        """Validate comptime literal can be safely coerced to target type."""
        return self.literals.validate_comptime_literal_coercion(
            value, from_type, to_type, source_text
        )

    def extract_literal_info(self, node: Dict) -> tuple:
        """Extract literal value and source text from AST node."""
        return self.literals.extract_literal_info(node)

    def validate_assignment_comptime_literal(
        self, value_node, value_type, target_type
    ) -> Optional[str]:
        """Validate comptime literal coercion in assignment context."""
        return self.literals.validate_assignment_comptime_literal(
            value_node, value_type, target_type
        )

    # =========================================================================
    # REMAINING SPECIALIZED METHODS (to be distributed to appropriate modules)
    # =========================================================================

    # These methods need to be moved to appropriate modules during migration:

    def resolve_conditional_comptime_types(
        self, branch_types, target_type
    ) -> HexenType:
        """Resolve comptime types across conditional branches."""
        return self.type_ops.resolve_conditional_comptime_types(
            branch_types, target_type
        )

    def analyze_comptime_operands_in_binary_op(
        self, left_type, right_type, target_type
    ) -> bool:
        """Analyze if comptime operands in binary operation make it safe."""
        return self.binary_ops.analyze_assignment_comptime_operands(
            left_type, right_type, target_type
        )

    def preserve_comptime_type_in_unary_op(self, operand_type, operator) -> HexenType:
        """Preserve comptime type through unary operations."""
        return self.binary_ops.preserve_comptime_type_in_unary_op(
            operand_type, operator
        )

    def validate_conditional_branch_compatibility(
        self, branch_types, target_type, error_callback, node
    ) -> Optional[HexenType]:
        """Validate type compatibility across conditional branches and return unified type."""
        return self.block_eval.validate_conditional_branch_compatibility(
            branch_types, target_type, error_callback, node
        )

    def analyze_conditional_branch_with_target_context(
        self, branch_node, target_type, analyze_expression_callback
    ) -> Optional[HexenType]:
        """Analyze conditional branch with target type context for assign statements."""
        return self.block_eval.analyze_conditional_branch_with_target_context(
            branch_node, target_type, analyze_expression_callback
        )

    def check_branch_uses_assign(self, branch_node) -> bool:
        """Check if a branch (block) uses assign statement instead of return statement."""
        return self.block_eval.check_branch_uses_assign(branch_node)

    def can_safely_adapt_comptime_types(
        self, left_type, right_type, target_type
    ) -> bool:
        """Check if comptime types in a binary operation can safely adapt to the target type."""
        return self.binary_ops.can_safely_adapt_comptime_types(
            left_type, right_type, target_type
        )

    def should_skip_precision_loss_check_for_mixed_concrete(
        self, left_type, right_type, target_type
    ) -> bool:
        """Check if precision loss check should be skipped for mixed concrete types."""
        return self.binary_ops.should_skip_precision_loss_check_for_mixed_concrete(
            left_type, right_type, target_type
        )

    def analyze_assignment_comptime_operands(
        self, left_type, right_type, target_type
    ) -> bool:
        """Analyze if comptime operands in assignment binary operation make precision loss check unnecessary."""
        return self.binary_ops.analyze_assignment_comptime_operands(
            left_type, right_type, target_type
        )

    # =========================================================================
    # ARRAY TYPE OPERATIONS DELEGATION (NEW)
    # =========================================================================

    def is_comptime_array_type(self, type_: HexenType) -> bool:
        """Check if type is a comptime array type."""
        return self.type_ops.is_comptime_array_type(type_)

    def is_array_type(self, type_: HexenType) -> bool:
        """Check if type represents an array (comptime or concrete)."""
        return self.type_ops.is_array_type(type_)

    def unify_comptime_array_types(
        self, element_types: List[HexenType]
    ) -> Optional[HexenType]:
        """Unify array element types into comptime array types."""
        return self.type_ops.unify_comptime_array_types(element_types)


# Expose main class for import
__all__ = ["ComptimeAnalyzer"]
