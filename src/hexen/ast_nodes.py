"""
AST Node Type Definitions for Hexen Language

This module defines the NodeType enum used throughout the Hexen language
implementation to provide type-safe node type checking and creation.
"""

from enum import Enum


class NodeType(Enum):
    """AST Node Type Enumeration for Hexen Language

    This enum centralizes all AST node type definitions, providing:
    - Type safety for node type checking
    - IDE autocomplete support
    - Prevention of typos in node type strings
    - Centralized location for all node type definitions

    Usage:
        Creating nodes: {"type": NodeType.LITERAL.value, "value": 42}
        Checking types: node.get("type") == NodeType.LITERAL.value
    """

    # Core AST Structure
    PROGRAM = "program"
    FUNCTION = "function"
    BLOCK = "block"

    # Declarations
    VAL_DECLARATION = "val_declaration"
    MUT_DECLARATION = "mut_declaration"

    # Statements
    RETURN_STATEMENT = "return_statement"
    ASSIGNMENT_STATEMENT = "assignment_statement"

    # Expressions
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    BINARY_OPERATION = "binary_operation"
    UNARY_OPERATION = "unary_operation"
    TYPE_ANNOTATED_EXPRESSION = "type_annotated_expression"

    # Comptime Types (Literals that adapt to context)
    COMPTIME_INT = "comptime_int"
    COMPTIME_FLOAT = "comptime_float"

    def __str__(self):
        """Return the string value for convenient usage"""
        return self.value
