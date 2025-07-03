"""
Tests for binary operations parsing in Hexen.

Focuses on:
1. Basic operator syntax parsing
2. Expression structure and AST construction
3. Operator precedence in AST
4. Parenthesized expressions
5. Syntax error cases
6. Logical operations (&&, ||)
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


def verify_binary_operation_ast(ast, expected_operator, expected_left, expected_right):
    """Helper to verify binary operation AST structure."""
    assert ast["type"] == NodeType.BINARY_OPERATION.value
    assert ast["operator"] == expected_operator
    assert ast["left"] == expected_left
    assert ast["right"] == expected_right


def test_basic_arithmetic_operators():
    """Test parsing of basic arithmetic operators (+, -, *, /, \\)."""
    source = """
    func main(): i32 = {
        val add = 10 + 20
        val sub = 10 - 20
        val mul = 10 * 20
        val fdiv = 10 / 20
        val idiv = 10 \\ 20
        return 0
    }
    """
    parser = HexenParser()
    ast = parser.parse(source)

    # Get the variable declarations from the function body
    statements = ast["functions"][0]["body"]["statements"]

    # Verify each binary operation AST
    verify_binary_operation_ast(
        statements[0]["value"],
        "+",
        {"type": NodeType.COMPTIME_INT.value, "value": 10},
        {"type": NodeType.COMPTIME_INT.value, "value": 20},
    )

    verify_binary_operation_ast(
        statements[1]["value"],
        "-",
        {"type": NodeType.COMPTIME_INT.value, "value": 10},
        {"type": NodeType.COMPTIME_INT.value, "value": 20},
    )

    verify_binary_operation_ast(
        statements[2]["value"],
        "*",
        {"type": NodeType.COMPTIME_INT.value, "value": 10},
        {"type": NodeType.COMPTIME_INT.value, "value": 20},
    )

    verify_binary_operation_ast(
        statements[3]["value"],
        "/",
        {"type": NodeType.COMPTIME_INT.value, "value": 10},
        {"type": NodeType.COMPTIME_INT.value, "value": 20},
    )

    verify_binary_operation_ast(
        statements[4]["value"],
        "\\",
        {"type": NodeType.COMPTIME_INT.value, "value": 10},
        {"type": NodeType.COMPTIME_INT.value, "value": 20},
    )


def test_binary_operator_syntax_errors():
    """Test syntax errors in binary operations."""
    invalid_sources = [
        # Missing operands
        "val x = 10 +",  # Missing right operand
        "val x = + 10",  # Missing left operand
        "val x = +",  # Missing both operands
        # Invalid operator sequences
        "val x = 10 + + 20",  # Double operator
        "val x = 10 + * 20",  # Invalid operator sequence
        "val x = 10 * / 20",  # Invalid operator sequence
        # Invalid parentheses
        "val x = (10 + 20",  # Unclosed parenthesis
        "val x = 10 + 20)",  # Extra closing parenthesis
        "val x = ((10 + 20)",  # Mismatched parentheses
        # Invalid expressions
        "val x = 10 +",  # Incomplete expression
        "val x = +",  # Just operator
        "val x = ()",  # Empty parentheses
    ]

    parser = HexenParser()
    for source in invalid_sources:
        with pytest.raises(SyntaxError):
            parser.parse(source)


def test_binary_operations_with_type_annotations():
    """Test binary operations combined with type annotations"""
    source = """
    func main(): i32 = {
        val mixed : f64 = (42 + 3.14) : f64
        val complex : i32 = (10 * 20 + 30) : i32
        val logical : bool = (true && false) : bool
        return 0
    }
    """
    parser = HexenParser()
    ast = parser.parse(source)

    # Get the variable declarations from the function body
    statements = ast["functions"][0]["body"]["statements"]

    # Check that type annotations are properly parsed with binary operations
    for i, stmt in enumerate(statements[:3]):  # Skip return statement
        assert stmt["type"] in [NodeType.VAL_DECLARATION.value]
        expr = stmt["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        # The expression inside should be a binary operation
        assert expr["expression"]["type"] == NodeType.BINARY_OPERATION.value
