"""
Test module for parser error handling

Tests error messages and invalid syntax detection.
"""

import pytest
from src.hexen.parser import HexenParser


class TestParserErrorMessages:
    """Test that we get helpful error messages"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_syntax_error_contains_parse_error(self):
        """Test that syntax errors mention 'Parse error'"""
        source = "invalid syntax here"

        with pytest.raises(SyntaxError) as exc_info:
            self.parser.parse(source)

        assert "Parse error" in str(exc_info.value)

    def test_file_parsing_error(self):
        """Test file parsing with invalid syntax"""
        # This tests the error handling in parse_file method
        # We'll create a temporary file in a later iteration
        pass

    def test_mut_without_type_fails(self):
        """Test that mut declaration without type annotation fails at parse time"""
        source = """
        func test() : void = {
            mut counter = 42
        }
        """
        with pytest.raises(SyntaxError) as exc_info:
            self.parser.parse(source)
        assert "Parse error" in str(exc_info.value)

    def test_mut_with_undef_without_type_fails(self):
        """Test that mut with undef without type annotation fails at parse time"""
        source = """
        func test() : void = {
            mut pending = undef
        }
        """
        with pytest.raises(SyntaxError) as exc_info:
            self.parser.parse(source)
        assert "Parse error" in str(exc_info.value)

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
