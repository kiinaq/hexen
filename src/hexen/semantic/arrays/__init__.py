"""
Hexen Array Semantic Analysis Module

This module provides semantic analysis for Hexen's array type system,
integrating with the existing comptime infrastructure for flexible
type handling.

Core Components:
- ArrayTypeInfo: Type metadata for array declarations
- ArrayDimension: Individual dimension specification
- Array literal analysis with comptime type inference
- Array access bounds checking and type validation
- Multidimensional array support with flattening

The module follows the established pattern of extending rather than
duplicating the existing comptime type system.
"""

from .array_types import ArrayTypeInfo, ArrayDimension
from .literal_analyzer import ArrayLiteralAnalyzer
from .error_messages import ArraySemanticError, ArrayErrorMessages, ArrayErrorFactory

__all__ = [
    'ArrayTypeInfo', 
    'ArrayDimension', 
    'ArrayLiteralAnalyzer',
    'ArraySemanticError',
    'ArrayErrorMessages', 
    'ArrayErrorFactory'
]