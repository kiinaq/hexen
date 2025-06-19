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
from hexen.parser import HexenParser


def verify_binary_operation_ast(ast, expected_operator, expected_left, expected_right):
    """Helper to verify binary operation AST structure."""
    assert ast["type"] == "binary_operation"
    assert ast["operator"] == expected_operator
    assert ast["left"] == expected_left
    assert ast["right"] == expected_right


def test_basic_arithmetic_operators():
    """Test parsing of basic arithmetic operators (+, -, *, /, \)."""
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
        {"type": "literal", "value": 10},
        {"type": "literal", "value": 20},
    )

    verify_binary_operation_ast(
        statements[1]["value"],
        "-",
        {"type": "literal", "value": 10},
        {"type": "literal", "value": 20},
    )

    verify_binary_operation_ast(
        statements[2]["value"],
        "*",
        {"type": "literal", "value": 10},
        {"type": "literal", "value": 20},
    )

    verify_binary_operation_ast(
        statements[3]["value"],
        "/",
        {"type": "literal", "value": 10},
        {"type": "literal", "value": 20},
    )

    verify_binary_operation_ast(
        statements[4]["value"],
        "\\",
        {"type": "literal", "value": 10},
        {"type": "literal", "value": 20},
    )


def test_operator_precedence():
    """Test operator precedence in AST construction."""
    source = """
    func main(): i32 = {
        val x = 10 + 20 * 2
        val y = (10 + 20) * 2
        val z = 10 * 2 + 20
        val w = 10 + 20 / 2
        return 0
    }
    """
    parser = HexenParser()
    ast = parser.parse(source)
    statements = ast["functions"][0]["body"]["statements"]

    # x = 10 + 20 * 2
    # Should be: 10 + (20 * 2)
    mul_op = {
        "type": "binary_operation",
        "operator": "*",
        "left": {"type": "literal", "value": 20},
        "right": {"type": "literal", "value": 2},
    }
    verify_binary_operation_ast(
        statements[0]["value"], "+", {"type": "literal", "value": 10}, mul_op
    )

    # y = (10 + 20) * 2
    # Should be: (10 + 20) * 2
    add_op = {
        "type": "binary_operation",
        "operator": "+",
        "left": {"type": "literal", "value": 10},
        "right": {"type": "literal", "value": 20},
    }
    verify_binary_operation_ast(
        statements[1]["value"], "*", add_op, {"type": "literal", "value": 2}
    )


def test_parenthesized_expressions():
    """Test parsing of parenthesized expressions."""
    source = """
    func main(): i32 = {
        val x = (10 + 20) * (30 - 40)
        val y = ((10 + 20) * 30) - 40
        val z = 10 + (20 * (30 - 40))
        return 0
    }
    """
    parser = HexenParser()
    ast = parser.parse(source)
    statements = ast["functions"][0]["body"]["statements"]

    # x = (10 + 20) * (30 - 40)
    add_op = {
        "type": "binary_operation",
        "operator": "+",
        "left": {"type": "literal", "value": 10},
        "right": {"type": "literal", "value": 20},
    }
    sub_op = {
        "type": "binary_operation",
        "operator": "-",
        "left": {"type": "literal", "value": 30},
        "right": {"type": "literal", "value": 40},
    }
    verify_binary_operation_ast(statements[0]["value"], "*", add_op, sub_op)


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


def test_complex_expressions():
    """Test parsing of complex nested expressions."""
    source = """
    func main(): i32 = {
        val x = 10 + 20 * 30 - 40 / 50
        val y = (10 + 20) * (30 - 40) / 50
        val z = ((10 + 20) * 30) - (40 / 50)
        return 0
    }
    """
    parser = HexenParser()
    ast = parser.parse(source)
    statements = ast["functions"][0]["body"]["statements"]

    # Verify AST structure for complex expressions
    # x = 10 + 20 * 30 - 40 / 50
    # Should be: (10 + (20 * 30)) - (40 / 50)
    mul_op = {
        "type": "binary_operation",
        "operator": "*",
        "left": {"type": "literal", "value": 20},
        "right": {"type": "literal", "value": 30},
    }
    first_add = {
        "type": "binary_operation",
        "operator": "+",
        "left": {"type": "literal", "value": 10},
        "right": mul_op,
    }
    div_op = {
        "type": "binary_operation",
        "operator": "/",
        "left": {"type": "literal", "value": 40},
        "right": {"type": "literal", "value": 50},
    }
    verify_binary_operation_ast(statements[0]["value"], "-", first_add, div_op)


def test_logical_operators():
    """Test parsing of logical operators (&&, ||)."""
    source = """
    func main(): i32 = {
        val and_op = true && false
        val or_op = true || false
        val complex = (true && false) || (false && true)
        val nested = true && (false || true) && false
        return 0
    }
    """
    parser = HexenParser()
    ast = parser.parse(source)
    statements = ast["functions"][0]["body"]["statements"]

    # Test basic AND operation
    verify_binary_operation_ast(
        statements[0]["value"],
        "&&",
        {"type": "literal", "value": True},
        {"type": "literal", "value": False},
    )

    # Test basic OR operation
    verify_binary_operation_ast(
        statements[1]["value"],
        "||",
        {"type": "literal", "value": True},
        {"type": "literal", "value": False},
    )

    # Test complex logical expression: (true && false) || (false && true)
    and_op1 = {
        "type": "binary_operation",
        "operator": "&&",
        "left": {"type": "literal", "value": True},
        "right": {"type": "literal", "value": False},
    }
    and_op2 = {
        "type": "binary_operation",
        "operator": "&&",
        "left": {"type": "literal", "value": False},
        "right": {"type": "literal", "value": True},
    }
    verify_binary_operation_ast(statements[2]["value"], "||", and_op1, and_op2)

    # Test nested logical expression: true && (false || true) && false
    or_op = {
        "type": "binary_operation",
        "operator": "||",
        "left": {"type": "literal", "value": False},
        "right": {"type": "literal", "value": True},
    }
    and_op1 = {
        "type": "binary_operation",
        "operator": "&&",
        "left": {"type": "literal", "value": True},
        "right": or_op,
    }
    verify_binary_operation_ast(
        statements[3]["value"],
        "&&",
        and_op1,
        {"type": "literal", "value": False},
    )


def test_logical_operator_syntax_errors():
    """Test syntax errors in logical operations."""
    invalid_sources = [
        # Missing operands
        "val x = true &&",  # Missing right operand
        "val x = && true",  # Missing left operand
        "val x = &&",  # Missing both operands
        # Invalid operator sequences
        "val x = true && && false",  # Double operator
        "val x = true && || false",  # Invalid operator sequence
        "val x = true || && false",  # Invalid operator sequence
        # Invalid parentheses
        "val x = (true && false",  # Unclosed parenthesis
        "val x = true && false)",  # Extra closing parenthesis
        "val x = ((true && false)",  # Mismatched parentheses
        # Invalid expressions
        "val x = true &&",  # Incomplete expression
        "val x = &&",  # Just operator
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
        assert stmt["type"] in ["val_declaration"]
        expr = stmt["value"]
        assert expr["type"] == "type_annotation"
        # The expression inside should be a binary operation
        assert expr["expression"]["type"] == "binary_operation"
