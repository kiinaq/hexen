"""
Array-Specific Type Utilities

Core data structures and utilities for array type information.
Provides array dimension specification and type metadata that integrates
with the existing comptime type system.

This module defines the fundamental structures used throughout the array
semantic analysis pipeline.
"""

from dataclasses import dataclass
from typing import List, Union
from ..types import HexenType


@dataclass
class ArrayDimension:
    """Single array dimension specification"""
    size: Union[int, str]  # Integer or "_" for inferred
    
    def is_inferred(self) -> bool:
        """Check if this dimension has inferred size"""
        return self.size == "_"
    
    def get_size(self) -> int:
        """Get size, raising error if inferred"""
        if self.is_inferred():
            raise ValueError("Cannot get size of inferred dimension")
        return int(self.size)


@dataclass  
class ArrayTypeInfo:
    """Complete array type information"""
    element_type: HexenType
    dimensions: List[ArrayDimension]
    
    def is_comptime_array(self) -> bool:
        """Check if this is a comptime array type"""
        return self.element_type in {HexenType.COMPTIME_ARRAY_INT, HexenType.COMPTIME_ARRAY_FLOAT}
    
    def get_element_count(self) -> int:
        """Calculate total element count for concrete arrays"""
        if any(dim.is_inferred() for dim in self.dimensions):
            raise ValueError("Cannot calculate size with inferred dimensions")
        
        count = 1
        for dim in self.dimensions:
            count *= dim.get_size()
        return count
    
    def can_flatten_to_1d(self) -> bool:
        """Check if array can be safely flattened to 1D"""
        return not any(dim.is_inferred() for dim in self.dimensions)
    
    def get_dimensionality(self) -> int:
        """Get the number of dimensions"""
        return len(self.dimensions)
    
    def is_multidimensional(self) -> bool:
        """Check if this is a multidimensional array (2D+)"""
        return len(self.dimensions) > 1
    
    def to_type_string(self) -> str:
        """Convert to type string representation for display"""
        dimension_str = ""
        for dim in self.dimensions:
            if dim.is_inferred():
                dimension_str += "[_]"
            else:
                dimension_str += f"[{dim.size}]"
        
        if self.element_type == HexenType.COMPTIME_ARRAY_INT:
            return dimension_str + "comptime_int"
        elif self.element_type == HexenType.COMPTIME_ARRAY_FLOAT:
            return dimension_str + "comptime_float"
        else:
            return dimension_str + self.element_type.value