"""
Test parentheses support in expressions

Phase 1 Parser Tests - Parentheses
Tests the basic parentheses functionality added to expressions.
"""

import pytest
from src.hexen.parser import HexenParser


class TestBasicParentheses:
    """Test basic parentheses functionality"""

    def setup_method(self):
        self.parser = HexenParser()

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
        assert expr["type"] == "literal"
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
        assert expr["type"] == "literal"
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
        assert expr["type"] == "literal"
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
        assert expr["type"] == "identifier"
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
        assert return_stmt["type"] == "return_statement"
        assert return_stmt["value"]["type"] == "literal"
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
        assert expr["type"] == "literal"
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
        assert expr["type"] == "literal"
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
        assert expr["type"] == "identifier"
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
        assert block["type"] == "block"

        temp_expr = block["statements"][0]["value"]
        assert temp_expr["type"] == "literal"
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
        assert block["type"] == "block"

        # Check first variable
        first_expr = block["statements"][0]["value"]
        assert first_expr["type"] == "literal"
        assert first_expr["value"] == 3.14

        # Check second variable
        second_expr = block["statements"][1]["value"]
        assert second_expr["type"] == "literal"
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

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == "block"
        assert len(expr["statements"]) == 2


class TestParenthesesWithTypes:
    """Test parentheses work correctly with all types"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_parentheses_with_all_numeric_types(self):
        """Test parentheses with all numeric literals"""
        source = """
        func test() : void = {
            val int_val = (42)
            val float_val = (3.14)
            val negative_int = (-10)
            val negative_float = (-2.5)
        }
        """
        ast = self.parser.parse(source)

        statements = ast["functions"][0]["body"]["statements"]

        # Check integer
        assert statements[0]["value"]["type"] == "literal"
        assert statements[0]["value"]["value"] == 42

        # Check float
        assert statements[1]["value"]["type"] == "literal"
        assert statements[1]["value"]["value"] == 3.14

        # Check negative integer (as unary operation)
        assert statements[2]["value"]["type"] == "unary_operation"
        assert statements[2]["value"]["operator"] == "-"
        assert statements[2]["value"]["operand"]["type"] == "literal"
        assert statements[2]["value"]["operand"]["value"] == 10

        # Check negative float (as unary operation)
        assert statements[3]["value"]["type"] == "unary_operation"
        assert statements[3]["value"]["operator"] == "-"
        assert statements[3]["value"]["operand"]["type"] == "literal"
        assert statements[3]["value"]["operand"]["value"] == 2.5

    def test_parentheses_preserve_type_annotations(self):
        """Test that parentheses work with explicit type annotations"""
        source = """
        func test() : void = {
            val explicit_i32 : i32 = (42)
            val explicit_f64 : f64 = (3.14)
            val explicit_bool : bool = (true)
            val explicit_string : string = ("hello")
        }
        """
        ast = self.parser.parse(source)

        statements = ast["functions"][0]["body"]["statements"]

        # Verify all have correct type annotations
        assert statements[0]["type_annotation"] == "i32"
        assert statements[1]["type_annotation"] == "f64"
        assert statements[2]["type_annotation"] == "bool"
        assert statements[3]["type_annotation"] == "string"


class TestParenthesesEdgeCases:
    """Test edge cases and error conditions"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_empty_parentheses_error(self):
        """Test that empty parentheses cause a parse error"""
        source = """
        func test() : i32 = {
            val result = ()
            return result
        }
        """
        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_unmatched_opening_parenthesis_error(self):
        """Test unmatched opening parenthesis causes error"""
        source = """
        func test() : i32 = {
            val result = (42
            return result
        }
        """
        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_unmatched_closing_parenthesis_error(self):
        """Test unmatched closing parenthesis causes error"""
        source = """
        func test() : i32 = {
            val result = 42)
            return result
        }
        """
        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_whitespace_in_parentheses(self):
        """Test that whitespace inside parentheses is handled correctly"""
        source = """
        func test() : i32 = {
            val result = ( 42 )
            return result
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == "literal"
        assert expr["value"] == 42

    def test_comments_around_parentheses(self):
        """Test comments around parentheses"""
        source = """
        func test() : i32 = {
            // before parentheses
            val result = ( 42 ) // after parentheses
            return result
        }
        """
        ast = self.parser.parse(source)

        expr = ast["functions"][0]["body"]["statements"][0]["value"]
        assert expr["type"] == "literal"
        assert expr["value"] == 42
