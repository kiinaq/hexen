"""
Tests for assign statement parsing in Hexen

Tests the new -> token functionality according to UNIFIED_BLOCK_SYSTEM.md:
- -> statements produce values in expression blocks
- -> token syntax parsing
- -> with various expressions
"""

from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestAssignStatementParsing:
    """Test assign statement parsing functionality"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_basic_assign_statement(self):
        """Test basic assign statement parsing"""
        source = """
        func test() : i32 = {
            val result = {
                -> 42
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        # Check the assign statement in the expression block
        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.COMPTIME_INT.value
        assert assign_stmt["value"]["value"] == 42

    def test_assign_with_identifier(self):
        """Test assign statement with identifier"""
        source = """
        func test() : i32 = {
            val result = {
                val temp = 100
                -> temp
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][
            1
        ]  # Second statement after val declaration

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.IDENTIFIER.value
        assert assign_stmt["value"]["name"] == "temp"

    def test_assign_with_binary_expression(self):
        """Test assign statement with binary expression"""
        source = """
        func test() : i32 = {
            val result = {
                val a = 10
                val b = 20
                -> a + b
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][2]  # Third statement

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.BINARY_OPERATION.value
        assert assign_stmt["value"]["operator"] == "+"

    def test_assign_with_parenthesized_expression(self):
        """Test assign statement with parenthesized expression"""
        source = """
        func test() : i32 = {
            val result = {
                -> (42 + 8)
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.BINARY_OPERATION.value
        assert assign_stmt["value"]["operator"] == "+"

    def test_assign_with_explicit_conversion(self):
        """Test assign statement with explicit type conversion"""
        source = """
        func test() : i32 = {
            val result = {
                -> 42:i32
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert (
            assign_stmt["value"]["type"]
            == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        )
        assert assign_stmt["value"]["target_type"] == "i32"

    def test_assign_with_complex_expression(self):
        """Test assign statement with complex nested expression"""
        source = """
        func test() : f64 = {
            val result = {
                val base = 10
                val multiplier = 2.5
                -> base * multiplier + 1.0
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][2]  # Third statement

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.BINARY_OPERATION.value
        # Should be parsed as: (base * multiplier) + 1.0

    def test_assign_with_string_literal(self):
        """Test assign statement with string literal"""
        source = """
        func test() : string = {
            val result = {
                -> "hello world"
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.LITERAL.value
        assert assign_stmt["value"]["value"] == "hello world"

    def test_assign_with_boolean_literal(self):
        """Test assign statement with boolean literal"""
        source = """
        func test() : bool = {
            val result = {
                -> true
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["type"] == NodeType.LITERAL.value
        assert assign_stmt["value"]["value"] is True

    def test_multiple_assign_blocks(self):
        """Test multiple expression blocks with assign statements"""
        source = """
        func test() : i32 = {
            val first = {
                -> 10
            }
            
            val second = {
                val temp = first
                -> temp * 2
            }
            
            return second
        }
        """
        ast = self.parser.parse(source)

        # Check first block
        first_block = ast["functions"][0]["body"]["statements"][0]["value"]
        first_assign = first_block["statements"][0]
        assert first_assign["type"] == NodeType.ASSIGN_STATEMENT.value
        assert first_assign["value"]["value"] == 10

        # Check second block
        second_block = ast["functions"][0]["body"]["statements"][1]["value"]
        second_assign = second_block["statements"][1]  # After val declaration
        assert second_assign["type"] == NodeType.ASSIGN_STATEMENT.value
        assert second_assign["value"]["type"] == NodeType.BINARY_OPERATION.value


class TestAssignStatementValidation:
    """Test assign statement parsing validation and edge cases"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_assign_keyword_not_identifier(self):
        """Test that 'assign' is treated as a keyword, not identifier"""
        source = """
        func test() : i32 = {
            // This should parse 'assign' as keyword, not identifier
            val result = {
                -> 42
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        # Should be assign_statement, not identifier reference
        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert "name" not in assign_stmt  # Should not have identifier properties

    def test_whitespace_handling_in_assign(self):
        """Test assign statement parsing with various whitespace"""
        source = """
        func test() : i32 = {
            val result = {
                ->    42
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["value"] == 42

    def test_assign_with_comments(self):
        """Test assign statement with comments"""
        source = """
        func test() : i32 = {
            val result = {
                // This assigns a value
                -> 42  // The value 42
            }
            return result
        }
        """
        ast = self.parser.parse(source)

        result_block = ast["functions"][0]["body"]["statements"][0]["value"]
        assign_stmt = result_block["statements"][0]

        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value
        assert assign_stmt["value"]["value"] == 42
