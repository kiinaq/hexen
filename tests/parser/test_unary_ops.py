"""
Test suite for unary operations in Hexen parser.

Tests parsing of:
- Unary minus (-) for numeric values
- Logical not (!) for boolean values
- Operator precedence with unary operators
- Parentheses with unary operators
"""

from hexen.parser import HexenParser


def verify_unary_operation_ast(node, expected_operator, expected_operand):
    """Helper function to verify unary operation AST structure."""
    assert node["type"] == "unary_operation"
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
            statements[0]["value"], "-", {"type": "literal", "value": 42}
        )

        # Test negation of zero
        verify_unary_operation_ast(
            statements[1]["value"], "-", {"type": "literal", "value": 0}
        )

        # Test double negation
        inner_neg = {
            "type": "unary_operation",
            "operator": "-",
            "operand": {"type": "literal", "value": 42},
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
            statements[0]["value"], "-", {"type": "literal", "value": 3.14}
        )

        # Test negation of zero
        verify_unary_operation_ast(
            statements[1]["value"], "-", {"type": "literal", "value": 0.0}
        )

        # Test double negation
        inner_neg = {
            "type": "unary_operation",
            "operator": "-",
            "operand": {"type": "literal", "value": 3.14},
        }
        verify_unary_operation_ast(statements[2]["value"], "-", inner_neg)


class TestLogicalNot:
    """Test parsing of logical not operator (!)"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_logical_not_with_booleans(self):
        """Test logical not with boolean literals"""
        source = """
        func main(): bool = {
            val a : bool = true
            val b : bool = false
            val x = !a
            val y = !b
            val z = !(a && b)  // Logical not with expression
            return true
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test single negation of variable
        verify_unary_operation_ast(
            statements[2]["value"], "!", {"type": "identifier", "name": "a"}
        )

        # Test negation of false variable
        verify_unary_operation_ast(
            statements[3]["value"], "!", {"type": "identifier", "name": "b"}
        )

        # Test negation of expression
        inner_expr = {
            "type": "binary_operation",
            "operator": "&&",
            "left": {"type": "identifier", "name": "a"},
            "right": {"type": "identifier", "name": "b"},
        }
        verify_unary_operation_ast(statements[4]["value"], "!", inner_expr)


class TestUnaryOperatorPrecedence:
    """Test operator precedence with unary operators"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_unary_minus_precedence(self):
        """Test precedence of unary minus with other operators"""
        source = """
        func main(): i32 = {
            val x = -2 * 3      // (-2) * 3
            val y = 2 * -3      // 2 * (-3)
            val z = -2 + -3     // (-2) + (-3)
            return 0
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test -2 * 3
        neg_two = {
            "type": "unary_operation",
            "operator": "-",
            "operand": {"type": "literal", "value": 2},
        }
        verify_binary_operation_ast(
            statements[0]["value"], "*", neg_two, {"type": "literal", "value": 3}
        )

        # Test 2 * -3
        neg_three = {
            "type": "unary_operation",
            "operator": "-",
            "operand": {"type": "literal", "value": 3},
        }
        verify_binary_operation_ast(
            statements[1]["value"], "*", {"type": "literal", "value": 2}, neg_three
        )

        # Test -2 + -3
        neg_two = {
            "type": "unary_operation",
            "operator": "-",
            "operand": {"type": "literal", "value": 2},
        }
        neg_three = {
            "type": "unary_operation",
            "operator": "-",
            "operand": {"type": "literal", "value": 3},
        }
        verify_binary_operation_ast(statements[2]["value"], "+", neg_two, neg_three)

    def test_logical_not_precedence(self):
        """Test precedence of logical not with other operators"""
        source = """
        func main(): bool = {
            val a : bool = true
            val b : bool = false
            val x = !a && b     // (!a) && b
            val y = !(a && b)   // !(a && b)
            val z = !!a         // !(!a)
            return true
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test !a && b
        not_a = {
            "type": "unary_operation",
            "operator": "!",
            "operand": {"type": "identifier", "name": "a"},
        }
        verify_binary_operation_ast(
            statements[2]["value"], "&&", not_a, {"type": "identifier", "name": "b"}
        )

        # Test !(a && b)
        inner_and = {
            "type": "binary_operation",
            "operator": "&&",
            "left": {"type": "identifier", "name": "a"},
            "right": {"type": "identifier", "name": "b"},
        }
        verify_unary_operation_ast(statements[3]["value"], "!", inner_and)

        # Test !!a
        inner_not = {
            "type": "unary_operation",
            "operator": "!",
            "operand": {"type": "identifier", "name": "a"},
        }
        verify_unary_operation_ast(statements[4]["value"], "!", inner_not)


def verify_binary_operation_ast(node, expected_operator, expected_left, expected_right):
    """Helper function to verify binary operation AST structure."""
    assert node["type"] == "binary_operation"
    assert node["operator"] == expected_operator
    assert node["left"] == expected_left
    assert node["right"] == expected_right
