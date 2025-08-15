"""
Comptime Binary Operations Module

Handles all binary operation comptime logic including mixed-type operations,
arithmetic resolution, and comparison operations.

Responsibilities:
- BINARY_OPS.md pattern implementation (Patterns 1-4)
- Mixed type operation handling
- Context-guided arithmetic resolution
- Comparison operation logic  
- Error message generation for mixed types
- Binary operation operand analysis

This module centralizes all the binary operation logic that was extracted
from BinaryOpsAnalyzer during the centralization effort.
"""

from typing import Dict, List, Optional, Any, Union
from ...ast_nodes import NodeType
from ..types import HexenType
from .type_operations import TypeOperations


class BinaryOperations:
    """
    Comptime binary operation handling and analysis.
    
    Implements the four patterns from BINARY_OPS.md:
    - Pattern 1: Comptime + Comptime → Comptime
    - Pattern 2: Comptime + Concrete → Concrete (adapts)
    - Pattern 3: Mixed Concrete → Explicit Required
    - Pattern 4: Same Concrete → Same Concrete
    """
    
    def __init__(self, type_ops: TypeOperations):
        """
        Initialize binary operations with type operations dependency.
        
        Args:
            type_ops: TypeOperations instance for basic type utilities
        """
        self.type_ops = type_ops
    
    # =========================================================================
    # OPERAND ANALYSIS
    # =========================================================================
    
    def has_comptime_operands(self, expression: Dict) -> bool:
        """
        Check if expression contains any comptime operands.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression contains comptime operands
        """
        expr_type = expression.get("type")
        
        # Direct comptime literals
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value]:
            return True
            
        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and self.has_comptime_operands(left):
                return True
            if right and self.has_comptime_operands(right):
                return True
                
        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand and self.has_comptime_operands(operand):
                return True
                
        # Variable references: check if variable has comptime type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.type_ops.symbol_table.lookup_symbol(var_name)
                if symbol_info and self.type_ops.is_comptime_type(symbol_info.type):
                    return True
                    
        return False
    
    # =========================================================================
    # MIXED TYPE OPERATION HANDLING
    # =========================================================================
    
    def handle_mixed_type_binary_operation(
        self, 
        left_type: HexenType, 
        right_type: HexenType, 
        operator: str, 
        target_type: Optional[HexenType],
        error_callback,
        node: Dict
    ) -> Optional[HexenType]:
        """
        Handle mixed type binary operations with BINARY_OPS.md patterns.
        
        Implements Pattern 2 (Comptime + Concrete) and Pattern 3 (Mixed Concrete) logic
        that was previously scattered across BinaryOpsAnalyzer.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            operator: Binary operator
            target_type: Optional target type for context
            error_callback: Function to call for error reporting
            node: AST node for error reporting
            
        Returns:
            None to continue with normal processing, or HexenType.UNKNOWN if error occurred
        """
        if not self.type_ops.is_mixed_type_operation(left_type, right_type):
            return None  # Not a mixed type operation, continue normal processing
            
        # Pattern 2: Comptime + Concrete → Concrete (comptime adapts)
        # Pattern 3: Mixed Concrete → Requires explicit conversions

        # Check if either operand is comptime (Pattern 2 - should work with target context)
        has_comptime = self.type_ops.is_comptime_type(left_type) or self.type_ops.is_comptime_type(right_type)

        if has_comptime and target_type is not None:
            # Pattern 2: Comptime adapts to concrete type with target context
            # This should work - let the resolve function handle it
            return None  # Continue with normal processing
            
        elif not has_comptime:
            # Pattern 3: Mixed concrete types ALWAYS require explicit conversions
            # This enforces transparent costs and explicit conversion philosophy
            from ..errors import BlockAnalysisError
            target_type_name = target_type.value if target_type else "target_type"
            error_callback(
                BlockAnalysisError.mixed_types_need_conversion(
                    left_type.value,
                    right_type.value,
                    f"arithmetic operation '{operator}'"
                ) + f" Example: left_val:{target_type_name} {operator} right_val:{target_type_name}",
                node,
            )
            return HexenType.UNKNOWN
            
        elif target_type is None:
            # Comptime types without target context - check if it's a valid comptime operation
            if self.type_ops.is_comptime_type(left_type) and self.type_ops.is_comptime_type(right_type):
                # This is Pattern 1: comptime + comptime - let resolve function handle
                return None  # Continue with normal processing
            else:
                # Use enhanced error message for ambiguous operations
                from ..errors import BlockAnalysisError
                error_callback(
                    BlockAnalysisError.ambiguity_resolution_guidance(
                        f"operation '{left_type.value} {operator} {right_type.value}'",
                        ["explicit target type annotation", "explicit type conversions"]
                    ) + " Example: val result : target_type = expression",
                    node,
                )
                return HexenType.UNKNOWN
                
        return None  # Continue with normal processing
    
    def handle_mixed_type_comparison(
        self,
        operator: str,
        left_type: HexenType,
        right_type: HexenType,
        error_callback,
        node: Dict
    ) -> Optional[HexenType]:
        """
        Handle mixed type comparison operations following BINARY_OPS.md rules.
        
        Args:
            operator: Comparison operator (==, !=, <, >, <=, >=)
            left_type: Left operand type
            right_type: Right operand type
            error_callback: Function to call for error reporting
            node: AST node for error reporting
            
        Returns:
            HexenType.BOOL if valid, HexenType.UNKNOWN if error, None for normal processing
        """
        from ..type_util import is_numeric_type
        
        if not self.type_ops.is_mixed_type_operation(left_type, right_type):
            return None  # Not mixed type, continue normal processing
            
        # For numeric types, apply same rules as arithmetic operations
        if is_numeric_type(left_type) and is_numeric_type(right_type):
            # Check if both are comptime types (should work naturally)
            both_comptime = (self.type_ops.is_comptime_type(left_type) and 
                           self.type_ops.is_comptime_type(right_type))

            if not both_comptime:
                # Mixed concrete types require explicit conversions (BINARY_OPS.md rule)
                # Use enhanced error message with better guidance
                from ..errors import BlockAnalysisError
                error_callback(
                    BlockAnalysisError.mixed_types_need_conversion(
                        left_type.value,
                        right_type.value,
                        f"comparison operation '{operator}'"
                    ),
                    node,
                )
                return HexenType.UNKNOWN
                
        return None  # Continue normal processing
    
    # =========================================================================
    # ARITHMETIC OPERATION RESOLUTION
    # =========================================================================
    
    def resolve_arithmetic_operation_type(
        self,
        operator: str,
        left_type: HexenType,
        right_type: HexenType,
        target_type: Optional[HexenType]
    ) -> Optional[HexenType]:
        """
        Resolve comptime-specific arithmetic operation types.
        
        Handles the comptime type promotion logic that was in BinaryOpsAnalyzer.
        Returns None if not a comptime-specific case (caller should handle normally).
        
        Args:
            operator: Arithmetic operator (+, -, *)
            left_type: Left operand type
            right_type: Right operand type
            target_type: Optional target type for context
            
        Returns:
            Resolved type for comptime operations, None for non-comptime cases
        """
        if operator not in ["+", "-", "*"]:
            return None  # Not an arithmetic operator we handle
            
        # Handle comptime type promotion first (Pattern 1)
        # BINARY_OPS.md Pattern 1: comptime_int + comptime_float → comptime_float
        if ((left_type == HexenType.COMPTIME_INT and right_type == HexenType.COMPTIME_FLOAT) or
            (left_type == HexenType.COMPTIME_FLOAT and right_type == HexenType.COMPTIME_INT)):
            return HexenType.COMPTIME_FLOAT

        # BINARY_OPS.md Pattern 1: comptime_int + comptime_int → comptime_int
        if left_type == HexenType.COMPTIME_INT and right_type == HexenType.COMPTIME_INT:
            return HexenType.COMPTIME_INT

        # BINARY_OPS.md Pattern 1: comptime_float + comptime_float → comptime_float
        if left_type == HexenType.COMPTIME_FLOAT and right_type == HexenType.COMPTIME_FLOAT:
            return HexenType.COMPTIME_FLOAT
            
        # For mixed comptime + concrete with target context, let caller handle
        if target_type and (self.type_ops.is_comptime_type(left_type) or self.type_ops.is_comptime_type(right_type)):
            return None  # Caller should handle context-guided resolution
            
        return None  # Not a comptime-specific case
    
    def resolve_context_guided_arithmetic(
        self,
        left_type: HexenType,
        right_type: HexenType,
        target_type: HexenType
    ) -> Optional[HexenType]:
        """
        Resolve arithmetic operation with context guidance for comptime types.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            target_type: Target type for context guidance
            
        Returns:
            Resolved type or None if normal resolution should be used
        """
        from ..type_util import is_float_type, is_integer_type, can_coerce, get_wider_type
        
        # Only handle if target is numeric
        if not (is_float_type(target_type) or is_integer_type(target_type)):
            return None
            
        # Resolve comptime types to target type for context guidance
        left_resolved = self.type_ops.resolve_comptime_type(left_type, target_type)
        right_resolved = self.type_ops.resolve_comptime_type(right_type, target_type)

        # Check if both operands can coerce to target type
        if can_coerce(left_resolved, target_type) and can_coerce(right_resolved, target_type):
            return target_type

        # If coercion is not possible, fall back to standard resolution
        return get_wider_type(left_resolved, right_resolved)
    
    # =========================================================================
    # BINARY OPERATION RESOLUTION
    # =========================================================================
    
    def resolve_comptime_binary_operation(self, left_type: HexenType, right_type: HexenType, operator: str) -> HexenType:
        """
        Resolve result type for comptime binary operations.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            operator: Binary operator
            
        Returns:
            Result type for comptime binary operation
        """
        # Only handle if both are comptime types
        if not (self.type_ops.is_comptime_type(left_type) and self.type_ops.is_comptime_type(right_type)):
            return HexenType.UNKNOWN
            
        # Comparison operators always produce bool
        if operator in {"<", ">", "<=", ">=", "==", "!="}:
            return HexenType.BOOL
            
        # Logical operators always produce bool  
        if operator in {"&&", "||"}:
            return HexenType.BOOL
            
        # Arithmetic operators follow promotion rules
        if operator in {"+", "-", "*", "/", "\\"}:
            return self.type_ops.get_comptime_promotion_result(left_type, right_type)
            
        return HexenType.UNKNOWN
    
    # =========================================================================
    # UNARY OPERATIONS (related to binary operations)
    # =========================================================================
    
    def preserve_comptime_type_in_unary_op(self, operand_type: HexenType, operator: str) -> HexenType:
        """
        Preserve comptime type through unary operations.
        
        Args:
            operand_type: Operand type
            operator: Unary operator
            
        Returns:
            Result type preserving comptime nature where appropriate
        """
        # For comptime types with unary minus, preserve the comptime type
        if operator == "-":
            if operand_type == HexenType.COMPTIME_INT:
                return HexenType.COMPTIME_INT
            elif operand_type == HexenType.COMPTIME_FLOAT:
                return HexenType.COMPTIME_FLOAT
                
        # For logical not, always return bool
        if operator == "!":
            return HexenType.BOOL
            
        # Default: return operand type unchanged
        return operand_type
    
    # =========================================================================
    # ASSIGNMENT CONTEXT ANALYSIS
    # =========================================================================
    
    def can_safely_adapt_comptime_types(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool:
        """
        Check if comptime types in a binary operation can safely adapt to the target type.
        
        Centralizes the comptime adaptation logic from AssignmentAnalyzer lines 144-153.
        This determines if a binary operation with comptime operands can safely resolve
        without requiring precision loss checks.
        
        Args:
            left_type: Left operand type  
            right_type: Right operand type
            target_type: Target type for the assignment
            
        Returns:
            True if comptime operands can safely adapt, skipping precision loss checks
        """
        from ..type_util import can_coerce
        
        # Check if either operand is a comptime type
        has_comptime_operand = self.type_ops.is_comptime_type(left_type) or self.type_ops.is_comptime_type(right_type)
        
        if not has_comptime_operand:
            # No comptime operands - cannot adapt
            return False
            
        # Check if comptime operands can coerce to target type
        left_can_coerce = self.type_ops.is_comptime_type(left_type) and can_coerce(left_type, target_type)
        right_can_coerce = self.type_ops.is_comptime_type(right_type) and can_coerce(right_type, target_type)
        
        # If we have comptime operands that can coerce to target type, adaptation is safe
        return left_can_coerce or right_can_coerce
    
    def should_skip_precision_loss_check_for_mixed_concrete(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool:
        """
        Check if precision loss check should be skipped for mixed concrete types.
        
        Centralizes logic from AssignmentAnalyzer lines 160-164 for handling mixed
        concrete operations that are safe despite not having comptime operands.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type  
            target_type: Target type for the assignment
            
        Returns:
            True if precision loss check should be skipped for safe concrete operations
        """
        from ..type_util import can_coerce
        
        # Both operand types must be able to coerce to target type for safety
        return can_coerce(left_type, target_type) and can_coerce(right_type, target_type)
    
    def analyze_assignment_comptime_operands(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool:
        """
        Analyze if comptime operands in assignment binary operation make precision loss check unnecessary.
        
        Centralizes the complete comptime operand analysis logic from AssignmentAnalyzer 
        lines 135-153, combining both comptime adaptation and mixed concrete safety checks.
        
        Args:
            left_type: Left operand type in binary operation
            right_type: Right operand type in binary operation  
            target_type: Target type for the assignment
            
        Returns:
            True if precision loss check should be skipped due to safe comptime/concrete mixing
        """
        # First check: Can comptime operands safely adapt?
        if self.can_safely_adapt_comptime_types(left_type, right_type, target_type):
            return True
            
        # Second check: Are mixed concrete types safe?
        if not (self.type_ops.is_comptime_type(left_type) or self.type_ops.is_comptime_type(right_type)):
            # No comptime operands, check if concrete types are safe
            return self.should_skip_precision_loss_check_for_mixed_concrete(left_type, right_type, target_type)
            
        return False