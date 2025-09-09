"""
Shared test utilities for Hexen parser tests.

This module provides common helper functions and utilities used across
multiple parser test files to eliminate code duplication and ensure
consistent testing patterns.
"""

import pytest

from src.hexen.ast_nodes import NodeType
from src.hexen.parser import HexenParser


def verify_binary_operation_ast(ast, expected_operator, expected_left, expected_right):
    """
    Helper to verify binary operation AST structure.

    Args:
        ast: The AST node to verify
        expected_operator: Expected operator string (e.g., "+", "-", "&&")
        expected_left: Expected left operand AST structure
        expected_right: Expected right operand AST structure
    """
    assert ast["type"] == NodeType.BINARY_OPERATION.value
    assert ast["operator"] == expected_operator
    assert ast["left"] == expected_left
    assert ast["right"] == expected_right


def verify_unary_operation_ast(node, expected_operator, expected_operand):
    """
    Helper function to verify unary operation AST structure.

    Args:
        node: The AST node to verify
        expected_operator: Expected operator string (e.g., "-", "!")
        expected_operand: Expected operand AST structure
    """
    assert node["type"] == NodeType.UNARY_OPERATION.value
    assert node["operator"] == expected_operator
    assert node["operand"] == expected_operand


def verify_variable_declaration_ast(
    ast, expected_name, expected_type, expected_mutability, expected_value=None
):
    """
    Helper to verify variable declaration AST structure.

    Args:
        ast: The AST node to verify
        expected_name: Expected variable name
        expected_type: Expected type annotation (or None for inferred)
        expected_mutability: Expected mutability ("val" or "mut")
        expected_value: Expected initial value AST structure (optional)
    """
    assert ast["type"] == NodeType.VARIABLE_DECLARATION.value
    assert ast["name"] == expected_name
    assert ast["type_annotation"] == expected_type
    assert ast["mutability"] == expected_mutability
    if expected_value is not None:
        assert ast["value"] == expected_value


def verify_function_declaration_ast(
    ast, expected_name, expected_params, expected_return_type, expected_body=None
):
    """
    Helper to verify function declaration AST structure.

    Args:
        ast: The AST node to verify
        expected_name: Expected function name
        expected_params: Expected parameter list
        expected_return_type: Expected return type annotation
        expected_body: Expected function body AST structure (optional)
    """
    assert ast["type"] == NodeType.FUNCTION_DECLARATION.value
    assert ast["name"] == expected_name
    assert ast["parameters"] == expected_params
    assert ast["return_type"] == expected_return_type
    if expected_body is not None:
        assert ast["body"] == expected_body


def verify_literal_ast(ast, expected_node_type, expected_value):
    """
    Helper to verify literal AST structure.

    Args:
        ast: The AST node to verify
        expected_node_type: Expected NodeType value
        expected_value: Expected literal value
    """
    assert ast["type"] == expected_node_type.value
    assert ast["value"] == expected_value


def verify_explicit_conversion_ast(ast, expected_target_type, expected_value):
    """
    Helper to verify explicit conversion AST structure.

    Args:
        ast: The AST node to verify
        expected_target_type: Expected target type string
        expected_value: Expected value AST structure
    """
    assert ast["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
    assert ast["target_type"] == expected_target_type
    assert ast["value"] == expected_value


def assert_parse_error(source_code, expected_error_pattern=None):
    """
    Standardized error testing helper.

    Args:
        source_code: Source code that should cause a parse error
        expected_error_pattern: Optional regex pattern to match in error message
    """
    parser = HexenParser()

    with pytest.raises(SyntaxError) as exc_info:
        parser.parse(source_code)

    # Always check for "Parse error" in the message
    assert "Parse error" in str(exc_info.value)

    # If specific pattern provided, check for it
    if expected_error_pattern:
        import re

        assert re.search(expected_error_pattern, str(exc_info.value))


def get_function_statements(ast, function_index=0):
    """
    Helper to extract statements from a function body.

    Args:
        ast: The program AST
        function_index: Index of the function in the functions list

    Returns:
        List of statements from the function body
    """
    return ast["functions"][function_index]["body"]["statements"]


def get_first_function_first_statement(ast):
    """
    Helper to get the first statement of the first function.

    Args:
        ast: The program AST

    Returns:
        First statement from the first function
    """
    return get_function_statements(ast)[0]


def create_comptime_int_ast(value):
    """
    Helper to create a comptime integer AST node.

    Args:
        value: Integer value

    Returns:
        AST node for comptime integer literal
    """
    return {
        "type": NodeType.COMPTIME_INT.value,
        "value": value,
        "source_text": str(value),
    }


def create_comptime_float_ast(value):
    """
    Helper to create a comptime float AST node.

    Args:
        value: Float value

    Returns:
        AST node for comptime float literal
    """
    return {
        "type": NodeType.COMPTIME_FLOAT.value,
        "value": value,
        "source_text": str(value),
    }


def create_bool_ast(value):
    """
    Helper to create a boolean AST node.

    Args:
        value: Boolean value

    Returns:
        AST node for boolean literal
    """
    return {"type": NodeType.LITERAL.value, "value": value}


def create_string_ast(value):
    """
    Helper to create a string AST node.

    Args:
        value: String value

    Returns:
        AST node for string literal
    """
    return {"type": NodeType.LITERAL.value, "value": value}


def create_undef_ast():
    """
    Helper to create an undef AST node.

    Returns:
        AST node for undef literal
    """
    return {"type": NodeType.IDENTIFIER.value, "name": "undef"}


class BaseParserTest:
    """
    Base test class providing common setup and utilities.

    All parser test classes can inherit from this to get standard setup.
    """

    def setup_method(self):
        """Standard setup method for parser tests."""
        self.parser = HexenParser()

    def parse_and_verify(self, source_code):
        """
        Parse source code and verify it's a valid program.

        Args:
            source_code: Source code to parse

        Returns:
            Parsed AST
        """
        ast = self.parser.parse(source_code)
        assert ast["type"] == NodeType.PROGRAM.value
        return ast

    def parse_single_function(self, source_code):
        """
        Parse source code and return the first function.

        Args:
            source_code: Source code to parse

        Returns:
            First function AST node
        """
        ast = self.parse_and_verify(source_code)
        assert len(ast["functions"]) >= 1
        return ast["functions"][0]

    def parse_function_statements(self, source_code):
        """
        Parse source code and return the statements from the first function.

        Args:
            source_code: Source code to parse

        Returns:
            List of statements from the first function
        """
        func = self.parse_single_function(source_code)
        return func["body"]["statements"]
