"""
Test module for boolean type parsing in Hexen

Part of the consolidated Hexen parser test suite.
Tests: Boolean literals, logical operators, precedence, and error cases.
"""

from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType
import pytest
from .test_utils import (
    verify_binary_operation_ast,
    verify_unary_operation_ast,
    BaseParserTest,
)


class TestBoolTypeParsing(BaseParserTest):
    """Test parsing of bool type annotations and boolean literals"""

    def test_bool_type_annotation(self):
        """Test parsing function with bool return type"""
        source = """
        func test() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        assert ast["type"] == NodeType.PROGRAM.value
        assert len(ast["functions"]) == 1

        func = ast["functions"][0]
        assert func["return_type"] == "bool"

    def test_boolean_literal_true(self):
        """Test parsing true literal"""
        source = """
        func test() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.LITERAL.value
        assert return_stmt["value"]["value"] is True

    def test_boolean_literal_false(self):
        """Test parsing false literal"""
        source = """
        func test() : bool = {
            return false
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.LITERAL.value
        assert return_stmt["value"]["value"] is False

    def test_bool_variable_declaration_with_type(self):
        """Test bool variable declaration with explicit type"""
        source = """
        func test() : bool = {
            val flag : bool = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        assert val_decl["type"] == NodeType.VAL_DECLARATION.value
        assert val_decl["name"] == "flag"
        assert val_decl["type_annotation"] == "bool"
        assert val_decl["value"]["type"] == NodeType.LITERAL.value
        assert val_decl["value"]["value"] is True

    def test_bool_variable_declaration_without_type(self):
        """Test bool variable declaration with type inference"""
        source = """
        func test() : bool = {
            val flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        assert val_decl["type"] == NodeType.VAL_DECLARATION.value
        assert val_decl["name"] == "flag"
        assert val_decl["type_annotation"] is None
        assert val_decl["value"]["type"] == NodeType.LITERAL.value
        assert val_decl["value"]["value"] is True

    def test_mut_bool_variable(self):
        """Test mutable bool variable declaration"""
        source = """
        func test() : bool = {
            mut flag : bool = false
            flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        statements = func["body"]["statements"]

        # Check mut declaration
        mut_decl = statements[0]
        assert mut_decl["type"] == NodeType.MUT_DECLARATION.value
        assert mut_decl["name"] == "flag"
        assert mut_decl["type_annotation"] == "bool"
        assert mut_decl["value"]["value"] is False

        # Check assignment
        assignment = statements[1]
        assert assignment["type"] == NodeType.ASSIGNMENT_STATEMENT.value
        assert assignment["target"] == "flag"
        assert assignment["value"]["value"] is True

    def test_multiple_bool_variables(self):
        """Test multiple boolean variables in one function"""
        source = """
        func test() : bool = {
            val ready = true
            val done = false
            mut active : bool = true
            return ready
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        statements = func["body"]["statements"]

        assert len(statements) == 4  # 3 declarations + 1 return

        # Check each declaration
        assert statements[0]["value"]["value"] is True
        assert statements[1]["value"]["value"] is False
        assert statements[2]["value"]["value"] is True

    def test_bool_undef_declaration(self):
        """Test bool variable with undef value"""
        source = """
        func test() : bool = {
            val flag : bool = undef
            return true
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        assert val_decl["type"] == NodeType.VAL_DECLARATION.value
        assert val_decl["type_annotation"] == "bool"
        assert val_decl["value"]["type"] == NodeType.IDENTIFIER.value
        assert val_decl["value"]["name"] == "undef"


class TestBoolTypeEdgeCases:
    """Test edge cases for bool type parsing"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_bool_keywords_not_identifiers(self):
        """Test that 'true' and 'false' cannot be used as identifiers"""
        # This should fail because 'true' is a reserved keyword
        with pytest.raises(Exception):
            source = """
            func test() : i32 = {
                val true = 42
                return true
            }
            """
            self.parser.parse(source)

    def test_mixed_types_with_bool(self):
        """Test function with multiple types including bool"""
        source = """
        func test() : bool = {
            val number = 42
            val text = "hello"
            val flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        statements = func["body"]["statements"]

        assert statements[0]["value"]["value"] == 42
        assert statements[1]["value"]["value"] == "hello"
        assert statements[2]["value"]["value"] is True

    def test_bool_in_expression_block(self):
        """Test bool type in expression blocks"""
        source = """
        func test() : bool = {
            val result = {
                val flag = true
                return flag
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        # Check the expression block
        expr_block = val_decl["value"]
        assert expr_block["type"] == NodeType.BLOCK.value
        inner_decl = expr_block["statements"][0]
        assert inner_decl["value"]["value"] is True


class TestBooleanOperators:
    """Test boolean logical operators (&&, ||, !)"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_logical_operators(self):
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
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Test basic AND operation
        verify_binary_operation_ast(
            statements[0]["value"],
            "&&",
            {"type": NodeType.LITERAL.value, "value": True},
            {"type": NodeType.LITERAL.value, "value": False},
        )

        # Test basic OR operation
        verify_binary_operation_ast(
            statements[1]["value"],
            "||",
            {"type": NodeType.LITERAL.value, "value": True},
            {"type": NodeType.LITERAL.value, "value": False},
        )

        # Test complex logical expression: (true && false) || (false && true)
        and_op1 = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "&&",
            "left": {"type": NodeType.LITERAL.value, "value": True},
            "right": {"type": NodeType.LITERAL.value, "value": False},
        }
        and_op2 = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "&&",
            "left": {"type": NodeType.LITERAL.value, "value": False},
            "right": {"type": NodeType.LITERAL.value, "value": True},
        }
        verify_binary_operation_ast(statements[2]["value"], "||", and_op1, and_op2)

        # Test nested logical expression: true && (false || true) && false
        or_op = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "||",
            "left": {"type": NodeType.LITERAL.value, "value": False},
            "right": {"type": NodeType.LITERAL.value, "value": True},
        }
        and_op1 = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "&&",
            "left": {"type": NodeType.LITERAL.value, "value": True},
            "right": or_op,
        }
        verify_binary_operation_ast(
            statements[3]["value"],
            "&&",
            and_op1,
            {"type": NodeType.LITERAL.value, "value": False},
        )

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
            statements[2]["value"],
            "!",
            {"type": NodeType.IDENTIFIER.value, "name": "a"},
        )

        # Test negation of false variable
        verify_unary_operation_ast(
            statements[3]["value"],
            "!",
            {"type": NodeType.IDENTIFIER.value, "name": "b"},
        )

        # Test negation of expression
        inner_expr = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "&&",
            "left": {"type": NodeType.IDENTIFIER.value, "name": "a"},
            "right": {"type": NodeType.IDENTIFIER.value, "name": "b"},
        }
        verify_unary_operation_ast(statements[4]["value"], "!", inner_expr)


class TestBooleanPrecedence:
    """Test operator precedence with boolean operators"""

    def setup_method(self):
        self.parser = HexenParser()

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
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "!",
            "operand": {"type": NodeType.IDENTIFIER.value, "name": "a"},
        }
        verify_binary_operation_ast(
            statements[2]["value"],
            "&&",
            not_a,
            {"type": NodeType.IDENTIFIER.value, "name": "b"},
        )

        # Test !(a && b)
        inner_and = {
            "type": NodeType.BINARY_OPERATION.value,
            "operator": "&&",
            "left": {"type": NodeType.IDENTIFIER.value, "name": "a"},
            "right": {"type": NodeType.IDENTIFIER.value, "name": "b"},
        }
        verify_unary_operation_ast(statements[3]["value"], "!", inner_and)

        # Test !!a
        inner_not = {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": "!",
            "operand": {"type": NodeType.IDENTIFIER.value, "name": "a"},
        }
        verify_unary_operation_ast(statements[4]["value"], "!", inner_not)


class TestBooleanErrors:
    """Test error cases for boolean operations"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_logical_operator_syntax_errors(self):
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

        for source in invalid_sources:
            with pytest.raises(SyntaxError):
                self.parser.parse(source)
