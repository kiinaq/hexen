"""
Comptime Literal Validation Module

Handles literal coercion and validation for comptime types including
overflow detection and range checking.

Responsibilities:
- Literal overflow detection
- Comptime literal coercion validation
- Range checking for target types
- Literal-specific error messages
- Assignment context validation

This module centralizes all the literal validation logic that was moved
from type_util.py during the centralization effort.
"""

from typing import Dict, Optional, Union, Tuple
from ...ast_nodes import NodeType
from ..types import HexenType


class LiteralValidation:
    """
    Comptime literal validation and coercion checking.
    
    Handles overflow detection and range validation for comptime literals
    being coerced to concrete types.
    """
    
    def __init__(self):
        """Initialize literal validation (no dependencies)."""
        pass
    
    # =========================================================================
    # LITERAL EXTRACTION
    # =========================================================================
    
    def extract_literal_info(self, node: Dict) -> Tuple[Union[int, float], str]:
        """
        Extract literal value and source text from AST node.

        Args:
            node: AST node representing a literal (comptime_int, comptime_float, etc.)

        Returns:
            Tuple of (value, source_text) or (None, None) if not a literal
        """
        if node.get("type") in {NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value}:
            value = node.get("value")
            source_text = node.get("source_text", str(value) if value is not None else None)
            return value, source_text
        return None, None
    
    # =========================================================================
    # COMPTIME LITERAL COERCION VALIDATION
    # =========================================================================
    
    def validate_comptime_literal_coercion(
        self,
        value: Union[int, float],
        from_type: HexenType,
        to_type: HexenType,
        source_text: str = None,
    ) -> None:
        """
        Validate comptime literal can be safely coerced to target type.

        This function implements the overflow detection during comptime type coercion
        as specified in LITERAL_OVERFLOW_BEHAVIOR.md. It should be called when
        comptime_int or comptime_float literals are being coerced to concrete types.

        Args:
            value: The literal value from the AST node
            from_type: The source comptime type (COMPTIME_INT or COMPTIME_FLOAT)
            to_type: The target concrete type
            source_text: Original literal text for error messages

        Raises:
            TypeError: If literal overflows target type range

        Returns:
            None if coercion is safe
        """
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
    
    # =========================================================================
    # ASSIGNMENT CONTEXT VALIDATION
    # =========================================================================
    
    def validate_assignment_comptime_literal(self, value_node: Dict, value_type: HexenType, target_type: HexenType) -> Optional[str]:
        """
        Validate comptime literal coercion in assignment context.
        
        Centralizes the comptime literal validation logic from AssignmentAnalyzer
        lines 177-186, providing comprehensive literal overflow checking.
        
        Args:
            value_node: AST node for the assigned value
            value_type: Inferred type of the value  
            target_type: Target type for the assignment
            
        Returns:
            Error message string if validation fails, None if validation passes
        """
        # Only validate comptime literals
        if value_type not in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            return None
            
        # Extract literal information
        literal_value, source_text = self.extract_literal_info(value_node)
        if literal_value is None:
            return None
            
        # Validate literal coercion
        try:
            self.validate_comptime_literal_coercion(literal_value, value_type, target_type, source_text)
            return None  # Validation passed
        except TypeError as e:
            return str(e)  # Return error message