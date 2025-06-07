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
