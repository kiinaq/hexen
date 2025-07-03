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

from typing import Dict, Optional, Callable

from ..ast_nodes import NodeType
from .types import HexenType
from .type_util import (
    parse_type,
    infer_type_from_value,
    can_coerce,
    is_precision_loss_operation,
)


class ExpressionAnalyzer:
    """
    Specialized analyzer for expression analysis.

    Implements the "Explicit Danger, Implicit Safety" principle for:
    - Type annotated expressions with precision loss acknowledgment
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
    ):
        """Initialize with callbacks to main analyzer functionality."""
        self._error = error_callback
        self._analyze_block = analyze_block_callback
        self._analyze_binary_operation = analyze_binary_operation_callback
        self._analyze_unary_operation = analyze_unary_operation_callback
        self._lookup_symbol = lookup_symbol_callback

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
        - TYPE_ANNOTATED_EXPRESSION: Explicit acknowledgment of precision loss
        - LITERAL: Non-numeric literals (string, bool)
        - COMPTIME_INT: Comptime integer literals with adaptive resolution
        - COMPTIME_FLOAT: Comptime float literals with adaptive resolution
        - IDENTIFIER: Symbol lookup and validation
        - BLOCK: Expression blocks (delegate to block analyzer)
        - BINARY_OPERATION: Delegate to binary ops analyzer
        - UNARY_OPERATION: Delegate to unary ops analyzer
        """
        if expr_type == NodeType.TYPE_ANNOTATED_EXPRESSION.value:
            # Handle type annotated expressions - implements TYPE_SYSTEM.md rules
            return self._analyze_type_annotated_expression(node, target_type)
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
        else:
            self._error(f"Unknown expression type: {expr_type}", node)
            return HexenType.UNKNOWN

    def _analyze_type_annotated_expression(
        self, node: Dict, target_type: Optional[HexenType] = None
    ) -> HexenType:
        """
        Analyze type annotated expressions implementing "Explicit Danger, Implicit Safety".

        From TYPE_SYSTEM.md, key rules:
        1. Type annotation must match the target type exactly (left-hand side)
        2. Type annotations require explicit left-side types
        3. Type annotations enable precision loss operations (acknowledgment)
        4. Type annotations are NOT conversions, they're acknowledgments

        Pattern: val variable : target_type = expression : SAME_target_type
        """
        expr = node.get("expression")
        type_annotation = node.get("type_annotation")
        annotated_type = parse_type(type_annotation)

        # Rule: Type annotations require explicit left-side types
        if target_type is None:
            self._error(
                "Type annotation requires explicit left side type. "
                f"Add explicit type: 'val result : {annotated_type.value} = ...'",
                node,
            )
            return HexenType.UNKNOWN

        # Rule: Type annotation must match target type exactly
        if annotated_type != target_type:
            self._error(
                f"Type annotation must match variable's declared type: "
                f"expected {target_type.value}, got {annotated_type.value}",
                node,
            )
            return HexenType.UNKNOWN

        # Analyze the expression with the annotated type as target
        expr_type = self.analyze_expression(expr, annotated_type)

        # Type annotation enables precision loss operations (acknowledgment)
        # This means we allow operations that would normally be rejected
        if expr_type != HexenType.UNKNOWN:
            # Check if this is a precision loss operation that needs acknowledgment
            if is_precision_loss_operation(expr_type, annotated_type):
                # Type annotation acknowledged - allow the operation
                return annotated_type

            # For safe operations, still check coercion
            if not can_coerce(expr_type, annotated_type):
                self._error(
                    f"Type mismatch: expression of type {expr_type.value} cannot be coerced to {annotated_type.value}",
                    node,
                )
                return HexenType.UNKNOWN
        else:
            # If expression analysis failed (e.g., due to undefined variables),
            # the type annotation structure is still valid - return the annotated type
            # This allows type annotation validation to work even when expressions have errors
            pass

        return annotated_type

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
