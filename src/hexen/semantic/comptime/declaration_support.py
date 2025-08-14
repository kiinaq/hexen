"""
Comptime Declaration Support Module

Handles all variable declaration comptime logic including type preservation,
compatibility validation, and error analysis.

Responsibilities:
- val vs mut comptime preservation rules
- Declaration type compatibility validation
- Precision loss detection and reporting
- Type inference error handling
- Declaration-specific error messages

This module centralizes all the declaration logic that was extracted
from DeclarationAnalyzer during the centralization effort.
"""

from typing import Dict, Optional, Union, Tuple
from ..types import HexenType, Mutability
from .type_operations import TypeOperations


class DeclarationSupport:
    """
    Comptime variable declaration support and validation.
    
    Implements the declaration-specific comptime logic including:
    - Type preservation rules for val vs mut
    - Compatibility validation
    - Error analysis and reporting
    """
    
    def __init__(self, type_ops: TypeOperations):
        """
        Initialize declaration support with type operations dependency.
        
        Args:
            type_ops: TypeOperations instance for basic type utilities
        """
        self.type_ops = type_ops
    
    # =========================================================================
    # TYPE PRESERVATION RULES
    # =========================================================================
    
    def should_preserve_comptime_type_in_declaration(self, mutability: Mutability, inferred_type: HexenType) -> bool:
        """
        Determine if comptime type should be preserved in variable declaration.
        
        Args:
            mutability: Variable mutability (val vs mut)
            inferred_type: Inferred type from expression
            
        Returns:
            True if comptime type should be preserved for flexibility
        """
        # Only preserve comptime types for immutable (val) declarations
        # Per TYPE_SYSTEM.md: val declarations preserve comptime types for later adaptation
        if mutability == Mutability.IMMUTABLE and self.type_ops.is_comptime_type(inferred_type):
            return True
            
        return False
    
    def should_preserve_comptime_for_declaration(
        self,
        mutability: Mutability,
        inferred_type: HexenType
    ) -> HexenType:
        """
        Determine final variable type considering comptime type preservation rules.
        
        Per TYPE_SYSTEM.md: val declarations preserve comptime types for later adaptation,
        while mut declarations require concrete types for safety.
        
        Args:
            mutability: Variable mutability (val vs mut)
            inferred_type: Type inferred from the value expression
            
        Returns:
            Final type to use for the variable declaration
        """
        # Preserve comptime types for val declarations (flexibility)
        # Per TYPE_SYSTEM.md: val declarations preserve comptime types for later adaptation
        if mutability == Mutability.IMMUTABLE and self.type_ops.is_comptime_type(inferred_type):
            return inferred_type  # ✅ PRESERVE comptime types for maximum flexibility
        
        # For mut declarations, comptime types should be resolved to concrete types
        # This is already handled by the requirement for explicit type annotations on mut
        return inferred_type
    
    # =========================================================================
    # TYPE COMPATIBILITY VALIDATION
    # =========================================================================
    
    def validate_variable_declaration_type_compatibility(
        self,
        value_type: HexenType,
        var_type: HexenType,
        value_node: Dict,
        variable_name: str,
        error_callback,
        node: Dict
    ) -> bool:
        """
        Validate type compatibility for variable declarations with comptime awareness.
        
        Centralizes the declaration-specific type validation logic including:
        - Precision loss detection
        - Comptime literal overflow validation
        - Type coercion validation
        
        Args:
            value_type: Type of the assigned value
            var_type: Type of the variable being declared
            value_node: AST node of the value expression
            variable_name: Name of the variable being declared
            error_callback: Function to call for error reporting
            node: Declaration AST node for error reporting
            
        Returns:
            True if types are compatible, False if error was reported
        """
        from ..type_util import is_precision_loss_operation, can_coerce
        
        # Check for precision loss operations that require explicit conversion
        if is_precision_loss_operation(value_type, var_type):
            self._generate_declaration_precision_loss_error(value_type, var_type, error_callback, node)
            return False

        # Check for literal overflow before type coercion
        if self.type_ops.is_comptime_type(value_type):
            literal_value, source_text = self._extract_literal_info(value_node)
            if literal_value is not None:
                try:
                    self._validate_comptime_literal_coercion(
                        literal_value, value_type, var_type, source_text
                    )
                except TypeError as e:
                    error_callback(str(e), node)
                    return False

        # Check for remaining type compatibility
        if not can_coerce(value_type, var_type):
            error_callback(
                f"Type mismatch: variable '{variable_name}' declared as {var_type.value} "
                f"but assigned value of type {value_type.value}",
                node,
            )
            return False
            
        return True
    
    # =========================================================================
    # ERROR ANALYSIS AND REPORTING
    # =========================================================================
    
    def analyze_declaration_type_inference_error(
        self,
        value_node: Dict,
        inferred_type: HexenType,
        variable_name: str,
        error_callback,
        node: Dict
    ) -> bool:
        """
        Analyze type inference errors with comptime awareness.
        
        Provides specific error handling for mixed-type operations vs generic inference failures.
        
        Args:
            value_node: AST node of the value expression
            inferred_type: The inferred type (typically HexenType.UNKNOWN)
            variable_name: Name of the variable being declared
            error_callback: Function to call for error reporting
            node: Declaration AST node for error reporting
            
        Returns:
            True if specific error was reported, False if generic error should be used
        """
        if inferred_type == HexenType.UNKNOWN:
            # Check if this is likely a mixed-type operation that already reported a specific error
            if value_node.get("type") == "binary_operation":
                # Binary operation analyzer already provided a specific error about mixed types
                # Don't add a generic "Cannot infer type" error - just return
                return True
            else:
                # For other cases, provide a generic type inference error
                error_callback(f"Cannot infer type for variable '{variable_name}'", node)
                return True
                
        return False
    
    def _generate_declaration_precision_loss_error(
        self, 
        from_type: HexenType, 
        to_type: HexenType, 
        error_callback,
        node: Dict
    ) -> None:
        """Generate appropriate precision loss error message for declarations."""
        if from_type == HexenType.I64 and to_type == HexenType.I32:
            error_callback(
                "Potential truncation. Use explicit conversion: 'value:i32'",
                node,
            )
        elif from_type == HexenType.F64 and to_type == HexenType.F32:
            error_callback(
                "Potential precision loss. Use explicit conversion: 'value:f32'",
                node,
            )
        elif from_type in {
            HexenType.F32,
            HexenType.F64,
            HexenType.COMPTIME_FLOAT,
        } and to_type in {HexenType.I32, HexenType.I64}:
            # Float to integer conversion - use "truncation" terminology
            error_callback(
                f"Potential truncation. Use explicit conversion: 'value:{to_type.value}'",
                node,
            )
        elif from_type == HexenType.I64 and to_type == HexenType.F32:
            error_callback(
                "Potential precision loss. Use explicit conversion: 'value:f32'",
                node,
            )
        else:
            # Generic precision loss message
            error_callback(
                f"Potential precision loss. Use explicit conversion: 'value:{to_type.value}'",
                node,
            )
    
    # =========================================================================
    # HELPER METHODS (delegated to appropriate modules)
    # =========================================================================
    
    def _extract_literal_info(self, node: Dict) -> Tuple[Optional[Union[int, float]], Optional[str]]:
        """
        Extract literal value and source text from AST node.
        
        This delegates to the LiteralValidation module in the actual implementation.
        """
        # TODO: During migration, this should delegate to LiteralValidation module
        # For now, implement basic functionality
        from ...ast_nodes import NodeType
        
        if node.get("type") in {NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value}:
            value = node.get("value")
            source_text = node.get("source_text", str(value) if value is not None else None)
            return value, source_text
        return None, None
    
    def _validate_comptime_literal_coercion(self, value, from_type, to_type, source_text):
        """
        Validate comptime literal coercion.
        
        This delegates to the LiteralValidation module in the actual implementation.
        """
        # TODO: During migration, this should delegate to LiteralValidation module
        # For now, implement basic functionality
        from ..type_util import validate_literal_range, TYPE_RANGES
        
        # Only validate comptime type coercions to concrete types
        if from_type not in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            return

        if to_type not in TYPE_RANGES:
            return

        # Special handling for comptime_float → integer coercion
        if from_type == HexenType.COMPTIME_FLOAT and to_type in {
            HexenType.I32,
            HexenType.I64,
        }:
            # This should require explicit conversion per TYPE_SYSTEM.md
            # But if we get here, validate the conversion is at least in range
            validate_literal_range(int(value), to_type, source_text)
        else:
            # Standard range validation
            validate_literal_range(value, to_type, source_text)