"""
Expression Analysis for Hexen Language

Handles all expression analysis including:
- Type annotated expressions (implementing "Explicit Danger, Implicit Safety")
- Identifier resolution and validation
- Literal type inference
- Expression blocks
- Delegated binary and unary operations

Implements the context-guided resolution strategy from TYPE_SYSTEM.md and BINARY_OPS.md.
"""

from typing import Dict, Optional, Callable, List

from .arrays.literal_analyzer import ArrayLiteralAnalyzer
from .type_util import (
    infer_type_from_value,
)
from .types import HexenType
from ..ast_nodes import NodeType


class ExpressionAnalyzer:
    """
    Specialized analyzer for expression analysis.

    Implements the "Explicit Danger, Implicit Safety" principle for:
    - Explicit conversion expressions with precision loss handling
    - Context-guided type resolution
    - Symbol lookup and validation
    - Comptime type inference

    Design follows the callback pattern for main analyzer integration.
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_block_callback: Callable[[Dict, Dict, str], Optional[HexenType]],
        analyze_binary_operation_callback: Callable[
            [Dict, Optional[HexenType]], HexenType
        ],
        analyze_unary_operation_callback: Callable[
            [Dict, Optional[HexenType]], HexenType
        ],
        lookup_symbol_callback: Callable[[str], Optional[object]],
        analyze_function_call_callback: Callable[
            [Dict, Optional[HexenType]], HexenType
        ],
        conversion_analyzer,
        comptime_analyzer=None,
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_block = analyze_block_callback
        self._analyze_binary_operation = analyze_binary_operation_callback
        self._analyze_unary_operation = analyze_unary_operation_callback
        self._lookup_symbol = lookup_symbol_callback
        self._analyze_function_call = analyze_function_call_callback
        self._conversion_analyzer = conversion_analyzer
        self.comptime_analyzer = comptime_analyzer

        # Initialize array literal analyzer (callback set after init to avoid circular dependency)
        self.array_literal_analyzer = ArrayLiteralAnalyzer(
            error_callback=error_callback,
            comptime_analyzer=comptime_analyzer,
            analyze_expression_callback=None,  # Set after initialization
        )
        # Set the expression analysis callback after initialization
        self.array_literal_analyzer._analyze_expression = self.analyze_expression

    def analyze_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze an expression and return its type.

        Args:
            node: Expression AST node
            target_type: Optional target type for context-guided resolution

        Returns HexenType.UNKNOWN for invalid expressions.

        Implements context-guided resolution strategy from TYPE_SYSTEM.md.
        """
        expr_type = node.get("type")
        return self._dispatch_expression_analysis(expr_type, node, target_type)

    def _dispatch_expression_analysis(
        self, expr_type: str, node: Dict, target_type: Optional[HexenType]
    ) -> HexenType:
        """
        Dispatch expression analysis to appropriate handler.

        Expression types handled:
        - EXPLICIT_CONVERSION_EXPRESSION: Explicit conversion
        - LITERAL: Non-numeric literals (string, bool)
        - COMPTIME_INT: Comptime integer literals with adaptive resolution
        - COMPTIME_FLOAT: Comptime float literals with adaptive resolution
        - IDENTIFIER: Symbol lookup and validation
        - BLOCK: Expression blocks (delegate to block analyzer)
        - BINARY_OPERATION: Delegate to binary ops analyzer
        - UNARY_OPERATION: Delegate to unary ops analyzer
        - FUNCTION_CALL: Delegate to function call analyzer
        - ARRAY_LITERAL: Delegate to array literal analyzer
        - ARRAY_ACCESS: Delegate to array access analyzer
        """
        if expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            # Handle explicit conversion expressions - implements TYPE_SYSTEM.md rules
            return self._conversion_analyzer.analyze_conversion(node, target_type)
        elif expr_type == NodeType.LITERAL.value:
            # Non-numeric literals (string, bool) - delegates to type_util
            return infer_type_from_value(node)
        elif expr_type == NodeType.COMPTIME_INT.value:
            # Comptime integer literals - adaptive type resolution
            return HexenType.COMPTIME_INT
        elif expr_type == NodeType.COMPTIME_FLOAT.value:
            # Comptime float literals - adaptive type resolution
            return HexenType.COMPTIME_FLOAT
        elif expr_type == NodeType.IDENTIFIER.value:
            # Symbol lookup and validation
            return self._analyze_identifier(node)
        elif expr_type == NodeType.BLOCK.value:
            # Expression blocks - delegate to block analyzer
            return self._analyze_block(node, node, context="expression")
        elif expr_type == NodeType.BINARY_OPERATION.value:
            # Binary operations - delegate to binary ops analyzer
            return self._analyze_binary_operation(node, target_type)
        elif expr_type == NodeType.UNARY_OPERATION.value:
            # Unary operations - delegate to unary ops analyzer
            return self._analyze_unary_operation(node, target_type)
        elif expr_type == NodeType.FUNCTION_CALL.value:
            # Function calls - delegate to function call analyzer
            return self._analyze_function_call(node, target_type)
        elif expr_type == NodeType.CONDITIONAL_STATEMENT.value:
            # Conditional expressions - analyze as expression context
            return self._analyze_conditional_expression(node, target_type)
        elif expr_type == NodeType.ARRAY_LITERAL.value:
            # Array literals - delegate to array literal analyzer
            return self.array_literal_analyzer.analyze_array_literal(node, target_type)
        elif expr_type == NodeType.ARRAY_ACCESS.value:
            # Array access expressions - delegate to array access analyzer
            return self.array_literal_analyzer.analyze_array_access(node, target_type)
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
        Follows the symbol table design from the main analyzer.
        """
        name = node.get("name")
        if not name:
            self._error("Identifier missing name", node)
            return HexenType.UNKNOWN

        # Special case: undef is a keyword, not a variable
        if name == "undef":
            return HexenType.UNINITIALIZED

        # Look up symbol in symbol table
        symbol = self._lookup_symbol(name)
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

    def _analyze_conditional_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze conditional expression (if/else if/else) in expression context.

        Expression context analysis:
        1. Validate condition is boolean type
        2. Analyze each branch as expression block
        3. Validate all branches assign or return
        4. Check type compatibility across branches
        5. Return unified type

        Args:
            node: Conditional AST node
            target_type: Optional target type for context-guided resolution

        Returns:
            Unified type from all branches
        """
        # 1. Analyze condition - must be bool type
        condition = node.get("condition")
        if not condition:
            self._error("Conditional expression missing condition", node)
            return HexenType.UNKNOWN

        condition_type = self.analyze_expression(condition)
        if condition_type != HexenType.BOOL:
            self._error(
                f"Condition must be of type bool, got {condition_type.name.lower()}",
                condition,
            )

        # 2. Analyze if branch as expression block
        if_branch = node.get("if_branch")
        if not if_branch:
            self._error("Conditional expression missing if branch", node)
            return HexenType.UNKNOWN

        # Analyze if branch in expression context with target type propagation
        if_type = self._analyze_conditional_branch(if_branch, node, target_type)

        # 3. Collect types from branches that actually assign (not return)
        assign_branch_types = []

        # Check if the if branch uses assign or return by examining its structure
        if self.comptime_analyzer and self.comptime_analyzer.check_branch_uses_assign(
            if_branch
        ):
            if if_type != HexenType.UNKNOWN:
                assign_branch_types.append(if_type)
        elif not self.comptime_analyzer and self._branch_uses_assign(if_branch):
            if if_type != HexenType.UNKNOWN:
                assign_branch_types.append(if_type)

        else_clauses = node.get("else_clauses", [])

        for else_clause in else_clauses:
            # Analyze else-if condition if present
            clause_condition = else_clause.get("condition")
            if clause_condition:
                clause_condition_type = self.analyze_expression(clause_condition)
                if clause_condition_type != HexenType.BOOL:
                    self._error(
                        f"Condition must be of type bool, got {clause_condition_type.name.lower()}",
                        clause_condition,
                    )

            # Analyze else clause branch as expression block with target type propagation
            clause_branch = else_clause.get("branch")
            if clause_branch:
                clause_type = self._analyze_conditional_branch(
                    clause_branch, node, target_type
                )
                # Only collect types from branches that use assign (not return)
                uses_assign = (
                    self.comptime_analyzer.check_branch_uses_assign(clause_branch)
                    if self.comptime_analyzer
                    else self._branch_uses_assign(clause_branch)
                )
                if uses_assign:
                    if clause_type != HexenType.UNKNOWN:
                        assign_branch_types.append(clause_type)

        # 4. Validate branch coverage for expression context
        # Expression blocks with conditionals follow the same rules as unified blocks:
        # - All branches must either assign or return (dual capability)
        # - If any branch returns (early function exit), other branches don't need full coverage
        # - If no branches return, all execution paths must be covered (final else required)

        has_final_else = False
        has_any_returns = False

        if else_clauses:
            # Check if the last clause is a final else (no condition)
            last_clause = else_clauses[-1]
            if not last_clause.get("condition"):
                has_final_else = True

        # Check if any branch uses return statements (this would be detected by block analyzer)
        # For now, we'll assume branches are properly validated by the block analyzer

        # If there's no final else, we need to check if this is acceptable
        # (i.e., some branches may return early, making incomplete coverage valid)
        if not has_final_else:
            # This is acceptable if branches use return statements for early exits
            # The block analyzer will validate individual branch compliance
            pass

        # 5. Check type compatibility across assign branches and return unified type
        if self.comptime_analyzer:
            return self.comptime_analyzer.validate_conditional_branch_compatibility(
                assign_branch_types, target_type, self._error, node
            )
        else:
            # Fallback to original logic if no comptime analyzer available
            return self._fallback_branch_type_unification(
                assign_branch_types, target_type, node
            )

    def _branch_uses_assign(self, branch_node: Dict) -> bool:
        """
        Check if a branch (block) uses assign statement instead of return statement.

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

    def _analyze_conditional_branch(
        self,
        branch_node: Dict,
        conditional_node: Dict,
        target_type: Optional[HexenType] = None,
    ) -> HexenType:
        """
        Analyze a conditional branch with proper target type propagation.

        This method provides specialized branch analysis for conditional expressions,
        enabling target type context propagation to assign statements within branches.

        Args:
            branch_node: Block AST node (the branch)
            conditional_node: Conditional AST node (for error reporting)
            target_type: Target type for context-guided resolution

        Returns:
            Type of the branch (from assign statement or return statement)
        """
        # Check if this branch uses assign or return first
        uses_assign = (
            self.comptime_analyzer.check_branch_uses_assign(branch_node)
            if self.comptime_analyzer
            else self._branch_uses_assign(branch_node)
        )

        if uses_assign and target_type:
            # Use centralized logic if available
            if self.comptime_analyzer:
                result = self.comptime_analyzer.analyze_conditional_branch_with_target_context(
                    branch_node, target_type, self.analyze_expression
                )
                if result is not None:
                    return result

            # Fallback to original logic
            if not branch_node or branch_node.get("type") != "block":
                return HexenType.UNKNOWN

            statements = branch_node.get("statements", [])
            if not statements:
                return HexenType.UNKNOWN

            # The last statement should be an assign statement
            last_statement = statements[-1]
            if last_statement.get("type") != "assign_statement":
                return HexenType.UNKNOWN

            # Analyze the assign statement with target type propagation
            assign_value = last_statement.get("value")
            if assign_value:
                # Use the target type for context-guided resolution
                return self.analyze_expression(assign_value, target_type)
            else:
                return HexenType.UNKNOWN
        else:
            # For return branches or branches without target type, use standard block analysis
            block_type = self._analyze_block(
                branch_node, conditional_node, context="expression"
            )
            return block_type

    def _fallback_branch_type_unification(
        self,
        assign_branch_types: List[HexenType],
        target_type: Optional[HexenType],
        node: Dict,
    ) -> HexenType:
        """
        Fallback implementation of branch type unification.

        Used when no comptime_analyzer is available.
        """
        if not assign_branch_types:
            # If no branches contribute types (all return early), use target_type if available
            return target_type if target_type else HexenType.UNKNOWN

        # If we have a target type, use it for context-guided resolution
        if target_type:
            # All assign branches should be compatible with the target type
            # Comptime types will adapt automatically
            for branch_type in assign_branch_types:
                if branch_type in [HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT]:
                    # Comptime types adapt to target context - this is handled by the system
                    continue
                elif branch_type != target_type:
                    # Require exact type match for concrete types (transparent costs principle)
                    # Suggest explicit conversion for mixed concrete types
                    self._error(
                        f"Branch type {branch_type.name.lower()} incompatible with target type {target_type.name.lower()}. "
                        f"Use explicit conversion: value:{target_type.name.lower()}",
                        node,
                    )
                    return HexenType.UNKNOWN
            return target_type

        # Without target context, implement basic type unification
        unified_type = assign_branch_types[0]

        # Check if all types are the same or comptime-compatible
        all_comptime_int = all(t == HexenType.COMPTIME_INT for t in assign_branch_types)
        all_comptime_float = all(
            t == HexenType.COMPTIME_FLOAT for t in assign_branch_types
        )
        all_same_concrete = all(t == unified_type for t in assign_branch_types)

        if all_comptime_int:
            return HexenType.COMPTIME_INT
        elif all_comptime_float:
            return HexenType.COMPTIME_FLOAT
        elif all_same_concrete:
            return unified_type
        else:
            # Mixed types require explicit target context for resolution
            self._error(
                f"Mixed types across conditional branches require explicit target type context",
                node,
            )
            return HexenType.UNKNOWN
