"""
Hexen Semantic Analysis Package

Public API for semantic analysis components.
Provides clean imports for the main semantic analyzer and supporting types.
"""

# Main semantic analyzer
from .analyzer import SemanticAnalyzer

# Specialized analyzers (for advanced use cases)
from .block_analyzer import BlockAnalyzer

# Error handling
from .errors import SemanticError

# Symbol table components
from .symbol_table import Symbol, SymbolTable

# Core types and enums
from .types import HexenType, Mutability

# Public API
__all__ = [
    "SemanticAnalyzer",
    "HexenType",
    "Mutability",
    "Symbol",
    "SymbolTable",
    "SemanticError",
    "BlockAnalyzer",
]
