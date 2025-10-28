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

    # Function System
    PARAMETER = "parameter"
    PARAMETER_LIST = "parameter_list"
    FUNCTION_CALL = "function_call"
    ARGUMENT_LIST = "argument_list"

    # Declarations
    VAL_DECLARATION = "val_declaration"
    MUT_DECLARATION = "mut_declaration"

    # Statements
    RETURN_STATEMENT = "return_statement"
    ASSIGN_STATEMENT = "assign_statement"
    ASSIGNMENT_STATEMENT = "assignment_statement"
    CONDITIONAL_STATEMENT = "conditional_statement"
    ELSE_CLAUSE = "else_clause"
    FUNCTION_CALL_STATEMENT = "function_call_statement"

    # Expressions
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    BINARY_OPERATION = "binary_operation"
    UNARY_OPERATION = "unary_operation"
    EXPLICIT_CONVERSION_EXPRESSION = "explicit_conversion_expression"

    # Comptime Types (Literals that adapt to context)
    COMPTIME_INT = "comptime_int"
    COMPTIME_FLOAT = "comptime_float"

    # Array System
    ARRAY_TYPE = "array_type"
    ARRAY_DIMENSION = "array_dimension"
    ARRAY_LITERAL = "array_literal"
    ARRAY_ACCESS = "array_access"
    ARRAY_COPY = "array_copy"
    PROPERTY_ACCESS = "property_access"

    # Range System
    RANGE_EXPR = "range_expr"
    RANGE_TYPE = "range_type"

    # Loop System
    FOR_IN_LOOP = "for_in_loop"
    WHILE_LOOP = "while_loop"
    BREAK_STATEMENT = "break_statement"
    CONTINUE_STATEMENT = "continue_statement"
    LABELED_STATEMENT = "labeled_statement"

    def __str__(self):
        """Return the string value for convenient usage"""
        return self.value
