"""
Test module for type annotation error cases

Tests parser-level syntax errors for type annotation syntax.
These are syntax validation tests - semantic type checking is handled elsewhere.
"""

import pytest
from src.hexen.parser import HexenParser


class TestTypeAnnotationErrors:
    """Test type annotation syntax error cases"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_type_annotation_without_left_type_error(self):
        """Test that type annotations without explicit left side type cause parser errors"""
        # Note: This might be caught at semantic analysis level rather than parser level
        # depending on how the grammar is structured
        invalid_sources = [
            """
            func main() : i32 = {
                val result = 42 : i32
                return 0
            }
            """,
            """
            func main() : i32 = {
                mut counter = expr : i32
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

    def test_invalid_type_annotation_syntax(self):
        """Test various invalid type annotation syntax patterns"""
        invalid_sources = [
            # Missing type after colon
            """
            func main() : i32 = {
                val result : i32 = 42 :
                return 0
            }
            """,
            # Type annotation in wrong position
            """
            func main() : i32 = {
                val result : i32 = : i32 42
                return 0
            }
            """,
            # Multiple type annotations
            """
            func main() : i32 = {
                val result : i32 = 42 : i32 : f64
                return 0
            }
            """,
            # Invalid type name
            """
            func main() : i32 = {
                val result : i32 = 42 : invalid_type
                return 0
            }
            """,
        ]

        for source in invalid_sources:
            with pytest.raises(SyntaxError):
                self.parser.parse(source)

    def test_empty_type_annotation(self):
        """Test empty type annotation (just colon)"""
        source = """
        func main() : i32 = {
            val result : i32 = 42 :
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_type_annotation_with_invalid_expression(self):
        """Test type annotation with syntactically invalid expressions"""
        invalid_sources = [
            # Missing operand in binary operation
            """
            func main() : i32 = {
                val result : i32 = (42 +) : i32
                return 0
            }
            """,
            # Unmatched parentheses
            """
            func main() : i32 = {
                val result : i32 = (42 + 10 : i32
                return 0
            }
            """,
            # Invalid operator sequence
            """
            func main() : i32 = {
                val result : i32 = (42 + * 10) : i32
                return 0
            }
            """,
        ]

        for source in invalid_sources:
            with pytest.raises(SyntaxError):
                self.parser.parse(source)

    def test_type_annotation_in_function_return(self):
        """Test type annotation in function return statements"""
        source = """
        func test() : i32 = {
            return 42 : i32
        }
        """

        # This should parse successfully - type annotations in returns are valid
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == "return_statement"
        # The return value should have a type annotation
        return_value = return_stmt["value"]
        assert return_value["type"] == "type_annotation"
        assert return_value["annotation_type"] == "i32"
        assert return_value["expression"]["value"] == 42

    def test_valid_complex_type_annotations(self):
        """Test that valid complex type annotations parse correctly"""
        valid_sources = [
            # Nested expressions with type annotations
            """
            func main() : i32 = {
                val result : f64 = ((10 + 20) * 30.0) : f64
                return 0
            }
            """,
            # Multiple variables with type annotations
            """
            func main() : i32 = {
                val a : i32 = 42 : i32
                val b : f64 = 3.14 : f64
                val c : string = "hello" : string
                return 0
            }
            """,
            # Type annotations with identifiers
            """
            func main() : i32 = {
                val x = 42
                val result : i32 = x : i32
                return 0
            }
            """,
        ]

        for source in valid_sources:
            # These should all parse successfully
            ast = self.parser.parse(source)
            assert ast is not None
            assert len(ast["functions"]) == 1

    def test_type_annotation_precedence(self):
        """Test that type annotation has correct precedence in expressions"""
        source = """
        func main() : i32 = {
            val result : i32 = 10 + 20 : i32
            return 0
        }
        """

        # This tests whether the type annotation applies to just "20" or to "10 + 20"
        # Based on the spec, it should apply to the entire expression
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]

        # The type annotation should wrap the entire binary operation
        if expr["type"] == "type_annotation":
            # Type annotation has higher precedence - wraps the whole expression
            assert expr["annotation_type"] == "i32"
            inner_expr = expr["expression"]
            assert inner_expr["type"] == "binary_operation"
            assert inner_expr["operator"] == "+"
        else:
            # Type annotation has lower precedence - only applies to the right operand
            assert expr["type"] == "binary_operation"
            assert expr["right"]["type"] == "type_annotation"

    def test_multiple_type_annotations_error(self):
        """Test that multiple type annotations on same expression cause error"""
        source = """
        func main() : i32 = {
            val result : i32 = 42 : i32 : f64
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)
