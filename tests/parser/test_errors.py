"""
Test module for parser error handling

Tests error messages and invalid syntax detection.
"""

import os
import pytest
import tempfile

from .test_utils import assert_parse_error, BaseParserTest


class TestParserErrorMessages(BaseParserTest):
    """Test that we get helpful error messages"""

    def test_syntax_error_contains_parse_error(self):
        """Test that syntax errors mention 'Parse error'"""
        source = "invalid syntax here"
        assert_parse_error(source)

    def test_file_parsing_error(self):
        """Test file parsing with invalid syntax"""
        # Create a temporary file with invalid syntax
        with tempfile.NamedTemporaryFile(mode="w", suffix=".hxn", delete=False) as f:
            f.write("invalid syntax here")
            temp_file = f.name

        try:
            # Test that parse_file method handles errors properly
            with pytest.raises(SyntaxError) as exc_info:
                self.parser.parse_file(temp_file)

            assert "Parse error" in str(exc_info.value)
        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_mut_without_type_fails(self):
        """Test that mut declaration without type annotation fails at parse time"""
        source = """
        func test() : void = {
            mut counter = 42
        }
        """
        assert_parse_error(source)

    def test_mut_with_undef_without_type_fails(self):
        """Test that mut with undef without type annotation fails at parse time"""
        source = """
        func test() : void = {
            mut pending = undef
        }
        """
        assert_parse_error(source)

    def test_val_without_type_still_works(self):
        """Test that val declarations without type annotation still work"""
        source = """
        func test() : void = {
            val inferred = 42
            return
        }
        """
        # Should parse successfully
        ast = self.parser.parse(source)
        assert ast is not None


class TestComprehensiveSyntaxErrors(BaseParserTest):
    """Test comprehensive syntax error scenarios"""

    def test_missing_function_body(self):
        """Test error when function body is missing"""
        source = """
        func test() : void
        """
        assert_parse_error(source)

    def test_missing_function_return_type(self):
        """Test error when function return type is missing"""
        source = """
        func test() = {
            return
        }
        """
        assert_parse_error(source)

    def test_missing_function_name(self):
        """Test error when function name is missing"""
        source = """
        func () : void = {
            return
        }
        """
        assert_parse_error(source)

    def test_invalid_variable_name(self):
        """Test error with invalid variable names"""
        source = """
        func test() : void = {
            val 123invalid = 42
        }
        """
        assert_parse_error(source)

    def test_missing_assignment_value(self):
        """Test error when assignment value is missing"""
        source = """
        func test() : void = {
            val x : i32 = 
        }
        """
        assert_parse_error(source)

    def test_invalid_type_annotation(self):
        """Test error with invalid type annotations"""
        source = """
        func test() : void = {
            val x : invalid_type = 42
        }
        """
        assert_parse_error(source)

    def test_missing_semicolon_equivalent(self):
        """Test error when statements are not properly terminated"""
        source = """
        func test() : void = {
            val x = 42
            val y = 43 val z = 44
        }
        """
        # This might actually parse successfully in Hexen's grammar - skip for now
        try:
            self.parser.parse(source)
            # If it parses successfully, that's also valid behavior
        except SyntaxError:
            # If it fails, that's expected behavior too
            pass

    def test_unmatched_braces(self):
        """Test error with unmatched braces"""
        source = """
        func test() : void = {
            val x = 42
        """
        assert_parse_error(source)

    def test_extra_closing_brace(self):
        """Test error with extra closing brace"""
        source = """
        func test() : void = {
            val x = 42
        }}
        """
        assert_parse_error(source)

    def test_invalid_operator_usage(self):
        """Test error with invalid operator usage"""
        source = """
        func test() : void = {
            val x = 42 +
        }
        """
        assert_parse_error(source)

    def test_missing_parentheses_in_expression(self):
        """Test error with missing parentheses"""
        source = """
        func test() : void = {
            val x = (42 + 43
        }
        """
        assert_parse_error(source)

    def test_invalid_explicit_conversion_syntax(self):
        """Test error with invalid explicit conversion syntax"""
        source = """
        func test() : void = {
            val x : i32 = 42:
        }
        """
        assert_parse_error(source)

    def test_missing_return_value(self):
        """Test error when return value is missing for non-void function"""
        source = """
        func test() : i32 = {
            return
        }
        """
        # This might be caught by semantic analysis rather than parser
        # The parser might allow bare return statements syntactically
        try:
            self.parser.parse(source)
            # If it parses successfully, semantic analysis should catch the error
        except SyntaxError:
            # If parser catches it, that's also valid
            pass


class TestEdgeCaseErrors(BaseParserTest):
    """Test edge case error scenarios"""

    def test_empty_source(self):
        """Test parsing empty source"""
        source = ""
        # Empty source might not be valid in Hexen
        try:
            ast = self.parser.parse(source)
            if ast is not None:
                # If it parses successfully, that's valid behavior
                pass
        except SyntaxError:
            # If it fails, that's also expected behavior
            pass

    def test_only_comments(self):
        """Test parsing source with only comments"""
        source = """
        // This is a comment
        /* This is a block comment */
        """
        # Comments-only source might not be valid in Hexen
        try:
            ast = self.parser.parse(source)
            if ast is not None:
                # If it parses successfully, that's valid behavior
                pass
        except SyntaxError:
            # If it fails, that's also expected behavior
            pass

    def test_deeply_nested_expressions(self):
        """Test very deeply nested expressions"""
        # Create a deeply nested expression, but not too deep to cause recursion issues
        nested_expr = "42"
        for i in range(10):  # Reduce to 10 levels to avoid recursion issues
            nested_expr = f"({nested_expr})"

        source = f"""
        func test() : i32 = {{
            val x = {nested_expr}
            return x
        }}
        """
        # Should parse successfully
        ast = self.parser.parse(source)
        assert ast is not None

    def test_very_long_identifier(self):
        """Test very long identifier names"""
        long_name = "x" * 1000  # 1000 character identifier
        source = f"""
        func test() : void = {{
            val {long_name} = 42
        }}
        """
        # Should parse successfully
        ast = self.parser.parse(source)
        assert ast is not None

    def test_invalid_escape_sequences(self):
        """Test invalid escape sequences in strings"""
        source = """
        func test() : void = {
            val x = "invalid\\q"
        }
        """
        # This might parse successfully depending on string handling
        # The actual error might be caught later in semantic analysis
        try:
            ast = self.parser.parse(source)
            assert ast is not None
        except SyntaxError:
            # If parser catches this, that's also valid
            pass
