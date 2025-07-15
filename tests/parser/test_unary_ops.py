"""
Test suite for unary operations in Hexen parser.

Tests parsing of:
- Unary minus (-) for numeric values
- Logical not (!) for boolean values
- Operator precedence with unary operators
- Parentheses with unary operators
"""

from src.hexen.ast_nodes import NodeType
from .test_utils import (
    verify_unary_operation_ast,
    verify_binary_operation_ast,
    create_comptime_int_ast,
    create_comptime_float_ast,
    create_bool_ast,
    BaseParserTest,
)


class TestUnaryMinus(BaseParserTest):
    """Test parsing of unary minus operator (-)"""

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
            create_comptime_int_ast(42),
        )

        # Test negation of zero
        verify_unary_operation_ast(
            statements[1]["value"],
            "-",
            create_comptime_int_ast(0),
        )

        # Test double negation
        inner_neg = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": create_comptime_int_ast(42),
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
            create_comptime_float_ast(3.14),
        )

        # Test negation of zero
        verify_unary_operation_ast(
            statements[1]["value"],
            "-",
            create_comptime_float_ast(0.0),
        )

        # Test double negation
        inner_neg = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": create_comptime_float_ast(3.14),
        }
        verify_unary_operation_ast(statements[2]["value"], "-", inner_neg)


class TestLogicalNot(BaseParserTest):
    """Test parsing of logical NOT operator (!)"""

    def test_logical_not_with_boolean_literals(self):
        """Test logical NOT with boolean literals"""
        source = """
        func main(): bool = {
            val x = !true
            val y = !false
            val z = !(!true)  // Double negation
            return false
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test NOT true
        verify_unary_operation_ast(
            statements[0]["value"],
            "!",
            create_bool_ast(True),
        )

        # Test NOT false
        verify_unary_operation_ast(
            statements[1]["value"],
            "!",
            create_bool_ast(False),
        )

        # Test double negation
        inner_not = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "!",
            "operand": create_bool_ast(True),
        }
        verify_unary_operation_ast(statements[2]["value"], "!", inner_not)

    def test_logical_not_with_variables(self):
        """Test logical NOT with boolean variables"""
        source = """
        func main(): bool = {
            val flag : bool = true
            val result = !flag
            return result
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test NOT with variable
        expected_var = {"type": NodeType.IDENTIFIER.value, "name": "flag"}
        verify_unary_operation_ast(
            statements[1]["value"],
            "!",
            expected_var,
        )

    def test_logical_not_precedence(self):
        """Test logical NOT operator precedence"""
        source = """
        func main(): bool = {
            val result = !true && false
            return result
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Should parse as (!true) && false
        not_true = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "!",
            "operand": create_bool_ast(True),
        }
        verify_binary_operation_ast(
            statements[0]["value"],
            "&&",
            not_true,
            create_bool_ast(False),
        )

    def test_nested_logical_not(self):
        """Test nested logical NOT operations"""
        source = """
        func main(): bool = {
            val a : bool = true
            val b : bool = false
            val result = !(a && !b)
            return result
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Build expected AST structure
        var_a = {"type": NodeType.IDENTIFIER.value, "name": "a"}
        var_b = {"type": NodeType.IDENTIFIER.value, "name": "b"}

        not_b = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "!",
            "operand": var_b,
        }

        a_and_not_b = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "&&",
            "left": var_a,
            "right": not_b,
        }

        verify_unary_operation_ast(
            statements[2]["value"],
            "!",
            a_and_not_b,
        )


class TestUnaryOperatorPrecedence(BaseParserTest):
    """Test operator precedence with unary operators"""

    def test_unary_minus_with_multiplication(self):
        """Test unary minus precedence with multiplication"""
        source = """
        func main(): i32 = {
            val result = -2 * 3
            return result
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Should parse as (-2) * 3
        neg_two = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": create_comptime_int_ast(2),
        }
        verify_binary_operation_ast(
            statements[0]["value"],
            "*",
            neg_two,
            create_comptime_int_ast(3),
        )

    def test_unary_minus_with_addition(self):
        """Test unary minus precedence with addition"""
        source = """
        func main(): i32 = {
            val result = -2 + 3
            return result
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Should parse as (-2) + 3
        neg_two = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": create_comptime_int_ast(2),
        }
        verify_binary_operation_ast(
            statements[0]["value"],
            "+",
            neg_two,
            create_comptime_int_ast(3),
        )

    def test_unary_operators_with_parentheses(self):
        """Test unary operators with parentheses"""
        source = """
        func main(): i32 = {
            val result = -(2 + 3)
            return result
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Should parse as -(2 + 3)
        two_plus_three = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "+",
            "left": create_comptime_int_ast(2),
            "right": create_comptime_int_ast(3),
        }
        verify_unary_operation_ast(
            statements[0]["value"],
            "-",
            two_plus_three,
        )
