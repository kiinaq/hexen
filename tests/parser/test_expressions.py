"""
Unified expression parsing tests for Hexen parser.

Consolidates:
- Basic expression parsing
- Parentheses handling
- Complex nested expressions
- Expression precedence validation
- Expression error cases

Moved from:
- test_parentheses.py (complete file)
- test_binary_ops.py (precedence & complex expressions)
- test_unary_ops.py (unary precedence)
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType
from .test_utils import verify_binary_operation_ast, BaseParserTest


class TestBasicParentheses(BaseParserTest):
    """Test basic parentheses functionality"""

    def test_simple_parenthesized_number(self):
        """Test simple parenthesized number literal"""
        source = """
        func test() : i32 = {
            val result = (42)
            return result
        }
        """
        ast = self.parser.parse(source)

        # Verify the parentheses are correctly parsed and removed
        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.COMPTIME_INT.value
        assert expr["value"] == 42

    def test_parenthesized_string(self):
        """Test parenthesized string literal"""
        source = """
        func test() : string = {
            val message = ("hello")
            return message
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.LITERAL.value
        assert expr["value"] == "hello"

    def test_parenthesized_boolean(self):
        """Test parenthesized boolean literal"""
        source = """
        func test() : bool = {
            val flag = (true)
            return flag
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.LITERAL.value
        assert expr["value"]

    def test_parenthesized_identifier(self):
        """Test parenthesized identifier"""
        source = """
        func test() : i32 = {
            val x = 42
            val result = (x)
            return result
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][1]["value"]
        assert expr["type"] == NodeType.IDENTIFIER.value
        assert expr["name"] == "x"

    def test_parenthesized_in_return(self):
        """Test parentheses in return statements"""
        source = """
        func test() : i32 = {
            return (42)
        }
        """
        ast = self.parser.parse(source)

        return_stmt = ast["functions"][0]["body"]["statements"][0]
        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.COMPTIME_INT.value
        assert return_stmt["value"]["value"] == 42


class TestNestedParentheses:
    """Test nested parentheses"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_double_parentheses(self):
        """Test double nested parentheses"""
        source = """
        func test() : i32 = {
            val result = ((42))
            return result
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.COMPTIME_INT.value
        assert expr["value"] == 42

    def test_triple_parentheses(self):
        """Test triple nested parentheses"""
        source = """
        func test() : string = {
            val message = ((("nested")))
            return message
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.LITERAL.value
        assert expr["value"] == "nested"

    def test_nested_parentheses_with_identifiers(self):
        """Test nested parentheses with identifiers"""
        source = """
        func test() : i32 = {
            val x = 10
            val y = 20
            val result = (((x)))
            return result
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][2]["value"]
        assert expr["type"] == NodeType.IDENTIFIER.value
        assert expr["name"] == "x"


class TestParenthesesInBlocks:
    """Test parentheses in various block contexts"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_parentheses_in_expression_block(self):
        """Test parentheses within expression blocks"""
        source = """
        func test() : i32 = {
            val result = {
                val temp = (100)
                return temp
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        block = ast["functions"][0]["body"]["statements"][0]["value"]
        assert block["type"] == NodeType.BLOCK.value

        temp_expr = block["statements"][0]["value"]
        assert temp_expr["type"] == NodeType.COMPTIME_INT.value
        assert temp_expr["value"] == 100

    def test_parentheses_in_statement_block(self):
        """Test parentheses in statement blocks"""
        source = """
        func test() : void = {
            {
                val wrapped = (3.14)
                val another = ("test")
            }
        }
        """
        ast = self.parser.parse(source)

        block = ast["functions"][0]["body"]["statements"][0]
        assert block["type"] == NodeType.BLOCK.value

        # Check first variable
        first_expr = block["statements"][0]["value"]
        assert first_expr["type"] == NodeType.COMPTIME_FLOAT.value
        assert first_expr["value"] == 3.14

        # Check second variable
        second_expr = block["statements"][1]["value"]
        assert second_expr["type"] == NodeType.LITERAL.value
        assert second_expr["value"] == "test"

    def test_parenthesized_block_expression(self):
        """Test parentheses around entire block expressions"""
        source = """
        func test() : i32 = {
            val result = ({
                val computed = 50
                return computed
            })
            return result
        }
        """
        ast = self.parser.parse(source)

        # The parentheses around the block should be parsed correctly
        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.BLOCK.value

        # Check the inner computation
        inner_expr = expr["statements"][0]["value"]
        assert inner_expr["type"] == NodeType.COMPTIME_INT.value
        assert inner_expr["value"] == 50


class TestParenthesesWithTypes:
    """Test parentheses with different type combinations"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_parentheses_with_all_numeric_types(self):
        """Test parentheses work with all numeric types"""
        source = """
        func test() : void = {
            val int_val = (42)
            val float_val = (3.14)
            val double_val = (2.718)
            val single_val = (1.5)
        }
        """
        ast = self.parser.parse(source)

        statements = ast["functions"][0]["body"]["statements"]

        # Check integer
        assert statements[0]["value"]["type"] == NodeType.COMPTIME_INT.value
        assert statements[0]["value"]["value"] == 42

        # Check float values
        assert statements[1]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[1]["value"]["value"] == 3.14

        assert statements[2]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[2]["value"]["value"] == 2.718

        assert statements[3]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[3]["value"]["value"] == 1.5

    def test_parentheses_preserve_type_annotations(self):
        """Test that parentheses don't interfere with type annotations"""
        source = """
        func test() : void = {
            val typed : i32 = (42)
            val another : string = ("hello")
            val flag : bool = (true)
        }
        """
        ast = self.parser.parse(source)

        statements = ast["functions"][0]["body"]["statements"]

        # Verify type annotations are preserved
        assert statements[0]["type_annotation"] == "i32"
        assert statements[1]["type_annotation"] == "string"
        assert statements[2]["type_annotation"] == "bool"

        # Verify values are correct
        assert statements[0]["value"]["value"] == 42
        assert statements[1]["value"]["value"] == "hello"
        assert statements[2]["value"]["value"] is True


class TestOperatorPrecedence:
    """Test operator precedence in expressions"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_binary_operator_precedence(self):
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
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # x = 10 + 20 * 2
        # Should be: 10 + (20 * 2)
        mul_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "*",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 20},
            "right": {"type": NodeType.COMPTIME_INT.value, "value": 2},
        }
        verify_binary_operation_ast(
            statements[0]["value"],
            "+",
            {"type": NodeType.COMPTIME_INT.value, "value": 10},
            mul_op,
        )

        # y = (10 + 20) * 2
        # Should be: (10 + 20) * 2
        add_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "+",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 10},
            "right": {"type": NodeType.COMPTIME_INT.value, "value": 20},
        }
        verify_binary_operation_ast(
            statements[1]["value"],
            "*",
            add_op,
            {"type": NodeType.COMPTIME_INT.value, "value": 2},
        )

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
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": {"type": NodeType.COMPTIME_INT.value, "value": 2},
        }
        verify_binary_operation_ast(
            statements[0]["value"],
            "*",
            neg_two,
            {"type": NodeType.COMPTIME_INT.value, "value": 3},
        )

        # Test 2 * -3
        neg_three = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": {"type": NodeType.COMPTIME_INT.value, "value": 3},
        }
        verify_binary_operation_ast(
            statements[1]["value"],
            "*",
            {"type": NodeType.COMPTIME_INT.value, "value": 2},
            neg_three,
        )

        # Test -2 + -3
        neg_two = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": {"type": NodeType.COMPTIME_INT.value, "value": 2},
        }
        neg_three = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "-",
            "operand": {"type": NodeType.COMPTIME_INT.value, "value": 3},
        }
        verify_binary_operation_ast(statements[2]["value"], "+", neg_two, neg_three)


class TestComplexExpressions:
    """Test complex nested expressions"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_parenthesized_binary_expressions(self):
        """Test parsing of parenthesized expressions."""
        source = """
        func main(): i32 = {
            val x = (10 + 20) * (30 - 40)
            val y = ((10 + 20) * 30) - 40
            val z = 10 + (20 * (30 - 40))
            return 0
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # x = (10 + 20) * (30 - 40)
        add_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "+",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 10},
            "right": {"type": NodeType.COMPTIME_INT.value, "value": 20},
        }
        sub_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "-",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 30},
            "right": {"type": NodeType.COMPTIME_INT.value, "value": 40},
        }
        verify_binary_operation_ast(statements[0]["value"], "*", add_op, sub_op)

    def test_complex_nested_expressions(self):
        """Test parsing of complex nested expressions."""
        source = """
        func main(): i32 = {
            val x = 10 + 20 * 30 - 40 / 50
            val y = (10 + 20) * (30 - 40) / 50
            val z = ((10 + 20) * 30) - (40 / 50)
            return 0
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Verify AST structure for complex expressions
        # x = 10 + 20 * 30 - 40 / 50
        # Should be: (10 + (20 * 30)) - (40 / 50)
        mul_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "*",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 20},
            "right": {"type": NodeType.COMPTIME_INT.value, "value": 30},
        }
        first_add = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "+",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 10},
            "right": mul_op,
        }
        div_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "/",
            "left": {"type": NodeType.COMPTIME_INT.value, "value": 40},
            "right": {"type": NodeType.COMPTIME_INT.value, "value": 50},
        }
        verify_binary_operation_ast(statements[0]["value"], "-", first_add, div_op)


class TestExpressionErrors:
    """Test expression syntax errors"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_empty_parentheses_error(self):
        """Test that empty parentheses cause syntax error"""
        source = """
        func test() : i32 = {
            val result = ()
            return result
        }
        """
        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_unmatched_opening_parenthesis_error(self):
        """Test unmatched opening parenthesis"""
        source = """
        func test() : i32 = {
            val result = (42
            return result
        }
        """
        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_unmatched_closing_parenthesis_error(self):
        """Test unmatched closing parenthesis"""
        source = """
        func test() : i32 = {
            val result = 42)
            return result
        }
        """
        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_whitespace_in_parentheses(self):
        """Test that whitespace in parentheses works correctly"""
        source = """
        func test() : i32 = {
            val result = (   42   )
            val another = ( "hello world" )
            return result
        }
        """
        ast = self.parser.parse(source)

        statements = ast["functions"][0]["body"]["statements"]
        assert statements[0]["value"]["value"] == 42
        assert statements[1]["value"]["value"] == "hello world"

    def test_comments_around_parentheses(self):
        """Test comments around parentheses"""
        source = """
        func test() : string = {
            // comment before
            val message = ("test") // comment after
            return message
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == NodeType.LITERAL.value
        assert expr["value"] == "test"
