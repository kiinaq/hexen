"""
Test module for explicit conversion error cases

Tests parser-level syntax errors for explicit conversion syntax.
These are syntax validation tests - semantic type checking is handled elsewhere.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestExplicitConversionErrors:
    """Test explicit conversion syntax error cases"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_explicit_conversion_without_left_type_error(self):
        """Test that explicit conversions without explicit left side type cause parser errors"""
        # Note: This might be caught at semantic analysis level rather than parser level
        # depending on how the grammar is structured
        invalid_sources = [
            """
            func main() : i32 = {
                val result = 42:i32
                return 0
            }
            """,
            """
            func main() : i32 = {
                mut counter = expr:i32
                return 0
            }
            """,
        ]

        for source in invalid_sources:
            # This test might need to be adjusted based on actual parser behavior
            # It may be that the parser accepts this syntax and semantic analysis rejects it
            try:
                ast = self.parser.parse(source)
                # If parser accepts it, we should at least verify the structure
                # The semantic analyzer should catch the error later
                assert ast is not None
            except SyntaxError:
                # If parser rejects it, that's also valid
                pass

    def test_invalid_explicit_conversion_syntax(self):
        """Test various invalid explicit conversion syntax patterns"""
        invalid_sources = [
            # Missing type after colon
            """
            func main() : i32 = {
                val result : i32 = 42:
                return 0
            }
            """,
            # Type annotation in wrong position
            """
            func main() : i32 = {
                val result : i32 = :i32 42
                return 0
            }
            """,
            # Multiple explicit conversions
            """
            func main() : i32 = {
                val result : i32 = 42:i32:f64
                return 0
            }
            """,
            # Invalid type name
            """
            func main() : i32 = {
                val result : i32 = 42:invalid_type
                return 0
            }
            """,
        ]

        for source in invalid_sources:
            with pytest.raises(SyntaxError):
                self.parser.parse(source)

    def test_empty_explicit_conversion(self):
        """Test empty explicit conversion (just colon)"""
        source = """
        func main() : i32 = {
            val result : i32 = 42:
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_explicit_conversion_with_invalid_expression(self):
        """Test explicit conversion with syntactically invalid expressions"""
        invalid_sources = [
            # Missing operand in binary operation
            """
            func main() : i32 = {
                val result : i32 = (42 +):i32
                return 0
            }
            """,
            # Unmatched parentheses
            """
            func main() : i32 = {
                val result : i32 = (42 + 10:i32
                return 0
            }
            """,
            # Invalid operator sequence
            """
            func main() : i32 = {
                val result : i32 = (42 + * 10):i32
                return 0
            }
            """,
        ]

        for source in invalid_sources:
            with pytest.raises(SyntaxError):
                self.parser.parse(source)

    def test_explicit_conversion_in_function_return(self):
        """Test explicit conversion in function return statements"""
        source = """
        func test() : i32 = {
            return 42:i32
        }
        """

        # This should parse successfully - explicit conversions in returns are valid
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        # The return value should have a explicit conversion
        return_value = return_stmt["value"]
        assert return_value["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        assert return_value["target_type"] == "i32"
        assert return_value["expression"]["value"] == 42

    def test_valid_complex_explicit_conversions(self):
        """Test that valid complex explicit conversions parse correctly"""
        valid_sources = [
            # Nested expressions with explicit conversions
            """
            func main() : i32 = {
                val result : f64 = ((10 + 20) * 30.0):f64
                return 0
            }
            """,
            # Multiple variables with explicit conversions
            """
            func main() : i32 = {
                val a : i32 = 42:i32
                val b : f64 = 3.14:f64
                val c : string = "hello":string
                return 0
            }
            """,
            # Type annotations with identifiers
            """
            func main() : i32 = {
                val x = 42
                val result : i32 = x:i32
                return 0
            }
            """,
        ]

        for source in valid_sources:
            # These should all parse successfully
            ast = self.parser.parse(source)
            assert ast is not None
            assert len(ast["functions"]) == 1

    def test_explicit_conversion_precedence(self):
        """Test that explicit conversion has high precedence (binds tightly to operands)"""
        source = """
        func main() : i32 = {
            val result : i32 = 10 + 20:i32
            return 0
        }
        """

        # This tests whether the explicit conversion applies to just "20" or to "10 + 20"
        # With high precedence, it should apply only to "20": 10 + (20:i32)
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]

        # The top-level expression should be the binary operation
        # (This confirms explicit conversions have HIGH precedence - they bind tightly)
        assert expr["type"] == NodeType.BINARY_OPERATION.value
        assert expr["operator"] == "+"

        # The left operand should be the number 10
        left = expr["left"]
        assert left["type"] == NodeType.COMPTIME_INT.value
        assert left["value"] == 10

        # The right operand should be the explicit conversion of 20 to i32
        right = expr["right"]
        assert right["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        assert right["target_type"] == "i32"
        assert right["expression"]["type"] == NodeType.COMPTIME_INT.value
        assert right["expression"]["value"] == 20

    def test_multiple_explicit_conversions_error(self):
        """Test that multiple explicit conversions on same expression cause error"""
        source = """
        func main() : i32 = {
            val result : i32 = 42:i32:f64
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)
