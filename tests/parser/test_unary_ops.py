"""
Test suite for unary operations in Hexen parser.

Tests parsing of:
- Unary minus (-) for numeric values
- Logical not (!) for boolean values
- Operator precedence with unary operators
- Parentheses with unary operators
"""

from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


def verify_unary_operation_ast(node, expected_operator, expected_operand):
    """Helper function to verify unary operation AST structure."""
    assert node["type"] == NodeType.UNARY_OPERATION.value
    assert node["operator"] == expected_operator
    assert node["operand"] == expected_operand


class TestUnaryMinus:
    """Test parsing of unary minus operator (-)"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_unary_minus_with_integers(self):
        """Test unary minus with integer literals"""
        source = """
        func main(): i32 = {
            val x = -42
            val y = -0
            val z = -(-42)  // Double negation
            return 0
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test single negation
        verify_unary_operation_ast(
            statements[0]["value"],
            "-",
            {"type": NodeType.COMPTIME_INT.value, "value": 42},
        )

        # Test negation of zero
        verify_unary_operation_ast(
            statements[1]["value"],
            "-",
            {"type": NodeType.COMPTIME_INT.value, "value": 0},
        )

        # Test double negation
        inner_neg = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": {"type": NodeType.COMPTIME_INT.value, "value": 42},
        }
        verify_unary_operation_ast(statements[2]["value"], "-", inner_neg)

    def test_unary_minus_with_floats(self):
        """Test unary minus with float literals"""
        source = """
        func main(): f64 = {
            val x = -3.14
            val y = -0.0
            val z = -(-3.14)  // Double negation
            return 0.0
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test single negation
        verify_unary_operation_ast(
            statements[0]["value"],
            "-",
            {"type": NodeType.COMPTIME_FLOAT.value, "value": 3.14},
        )

        # Test negation of zero
        verify_unary_operation_ast(
            statements[1]["value"],
            "-",
            {"type": NodeType.COMPTIME_FLOAT.value, "value": 0.0},
        )

        # Test double negation
        inner_neg = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": {"type": NodeType.COMPTIME_FLOAT.value, "value": 3.14},
        }
        verify_unary_operation_ast(statements[2]["value"], "-", inner_neg)


class TestUnaryOperatorPrecedence:
    """Test operator precedence with unary operators"""

    def setup_method(self):
        self.parser = HexenParser()


def verify_binary_operation_ast(node, expected_operator, expected_left, expected_right):
    """Helper function to verify binary operation AST structure."""
    assert node["type"] == NodeType.BINARY_OPERATION.value
    assert node["operator"] == expected_operator
    assert node["left"] == expected_left
    assert node["right"] == expected_right
