"""
Array Literal Semantic Analysis - Integrated Version

Implements array literal analysis that integrates seamlessly with the existing
expression analysis framework. Returns HexenType enums and follows established
patterns for type inference and error reporting.

Key Integration Points:
- Returns HexenType enums (not Dict structures)
- Uses ComptimeAnalyzer for element type unification  
- Integrates with expression analyzer callback pattern
- Follows established error reporting patterns
"""

from typing import Dict, List, Any, Optional, Callable
from ..types import HexenType
from .array_types import ArrayTypeInfo, ArrayDimension


class ArrayLiteralAnalyzer:
    """Analyzes array literal expressions integrated with expression framework"""
    
    def __init__(self, error_callback: Callable[[str, Optional[Dict]], None], comptime_analyzer):
        """
        Initialize with callback pattern for integration.
        
        Args:
            error_callback: Error reporting callback to main analyzer
            comptime_analyzer: Existing ComptimeAnalyzer instance
        """
        self._error = error_callback
        self.comptime_analyzer = comptime_analyzer
    
    def analyze_array_literal(self, node: Dict[str, Any], target_type: Optional[HexenType] = None) -> HexenType:
        """
        Analyze array literal and return inferred HexenType.
        
        Args:
            node: Array literal AST node
            target_type: Optional target type for context-guided resolution
            
        Returns:
            HexenType enum representing the array literal's type
        """
        elements = node.get("elements", [])
        
        # Handle empty arrays - require explicit context
        if not elements:
            if target_type is None:
                self._error("Empty array literal requires explicit type context", node)
                return HexenType.UNKNOWN
            return target_type
        
        # For now, return comptime array types for non-empty arrays
        # This is a simplified implementation that will be enhanced in later tasks
        
        # Analyze first element to determine base type
        # In a full implementation, we'd analyze all elements and unify types
        first_element = elements[0]
        element_type_str = first_element.get("type")
        
        if element_type_str == "comptime_int":
            # Check if all elements are integers
            if self._all_elements_are_integers(elements):
                return HexenType.COMPTIME_ARRAY_INT
            else:
                # Mixed integer/float -> promote to float array
                return HexenType.COMPTIME_ARRAY_FLOAT
        elif element_type_str == "comptime_float":
            return HexenType.COMPTIME_ARRAY_FLOAT
        elif element_type_str == "literal":
            # Check if it's a string literal
            first_value = first_element.get("value")
            if isinstance(first_value, str):
                self._error("String arrays not yet supported", node)
                return HexenType.UNKNOWN
        
        # For other types or mixed types, require explicit context
        if target_type is None:
            if len(set(elem.get("type") for elem in elements)) > 1:
                self._error("Mixed concrete/comptime element types require explicit array context", node)
            else:
                self._error("Array literal type inference not yet implemented for this element type", node)
            return HexenType.UNKNOWN
        
        return target_type
    
    def analyze_array_access(self, node: Dict[str, Any], target_type: Optional[HexenType] = None) -> HexenType:
        """
        Analyze array access expression and return element type.
        
        Args:
            node: Array access AST node with 'array' and 'index' fields
            target_type: Optional target type for context-guided resolution
            
        Returns:
            HexenType enum representing the accessed element's type
        """
        array_expr = node.get("array")
        index_expr = node.get("index")
        
        if not array_expr or not index_expr:
            self._error("Invalid array access: missing array or index", node)
            return HexenType.UNKNOWN
        
        # For now, implement basic array access validation
        # In a full implementation, this would:
        # 1. Analyze the array expression to get its type
        # 2. Validate the index is an integer type
        # 3. Perform bounds checking if possible
        # 4. Return the element type
        
        # Check index type - must be integer
        index_type_str = index_expr.get("type")
        if index_type_str not in ["comptime_int", "i32", "i64"]:
            self._error("Array index must be an integer type", node)
            return HexenType.UNKNOWN
        
        # For now, assume array access of comptime arrays returns comptime element type
        # This is a simplified implementation that will be enhanced
        array_type_str = array_expr.get("type")
        if array_type_str == "identifier":
            # This would normally involve symbol table lookup to get the array's type
            # For now, return COMPTIME_INT as a placeholder
            return HexenType.COMPTIME_INT
        
        self._error("Array access type inference not yet fully implemented", node)
        return HexenType.UNKNOWN
    
    def _all_elements_are_integers(self, elements: List[Dict]) -> bool:
        """Check if all elements are integer literals"""
        for element in elements:
            if element.get("type") != "comptime_int":
                return False
        return True