"""
Hexen Semantic Error Handling

Error classes and utilities for semantic analysis error reporting.
Provides structured error handling with optional AST node context.
"""

from typing import Dict, Optional


class SemanticError(Exception):
    """
    Represents a semantic analysis error with optional AST node context.

    Design philosophy:
    - Collect all errors before failing (don't stop at first error)
    - Provide context when available for better error messages
    - Separate from syntax errors (which are caught by parser)

    Future enhancements:
    - Line/column information
    - Error severity levels
    - Suggested fixes
    """

    def __init__(self, message: str, node: Optional[Dict] = None):
        self.message = message
        self.node = node  # AST node where error occurred (for future line/col info)
        super().__init__(message)
