"""
Tests for Hexen Parser

Testing our language design and grammar correctness, not Lark itself.
"""

import pytest
from hexen.parser import HexenParser


class TestMinimalHexen:
    """Test our ultra-minimal Hexen grammar"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = HexenParser()

    def test_valid_main_function(self):
        """Test our target minimal function parses correctly"""
        source = """
        func main() -> i32 {
            return 0
        }
        """

        ast = self.parser.parse(source)

        # Test top-level structure
        assert ast["type"] == "program"
        assert len(ast["functions"]) == 1

        # Test function structure
        func = ast["functions"][0]
        assert func["type"] == "function"
        assert func["name"] == "main"
        assert func["return_type"] == "i32"

        # Test function body
        assert func["body"]["type"] == "return_statement"
        assert func["body"]["value"]["type"] == "literal"
        assert func["body"]["value"]["value"] == 0

    def test_different_function_names(self):
        """Test functions with different valid names"""
        valid_names = ["main", "test_func", "myFunction", "_private", "func123"]

        for name in valid_names:
            source = f"""
            func {name}() -> i32 {{
                return 42
            }}
            """

            ast = self.parser.parse(source)
            assert ast["functions"][0]["name"] == name

    def test_different_return_values(self):
        """Test different integer return values"""
        test_values = [0, 1, 42, 123, 999]

        for value in test_values:
            source = f"""
            func main() -> i32 {{
                return {value}
            }}
            """

            ast = self.parser.parse(source)
            returned_value = ast["functions"][0]["body"]["value"]["value"]
            assert returned_value == value

    def test_whitespace_handling(self):
        """Test that extra whitespace doesn't break parsing"""
        # Extra whitespace everywhere
        source = """
        
        func   main  (  )  ->  i32  {
            return   0
        }
        
        """

        ast = self.parser.parse(source)
        assert ast["functions"][0]["name"] == "main"
        assert ast["functions"][0]["return_type"] == "i32"

    def test_minimal_whitespace(self):
        """Test minimal whitespace still parses"""
        source = "func main()->i32{return 0}"

        ast = self.parser.parse(source)
        assert ast["functions"][0]["name"] == "main"

    def test_invalid_syntax_missing_return_type(self):
        """Test missing return type is rejected"""
        source = """
        func main() {
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_syntax_missing_function_name(self):
        """Test missing function name is rejected"""
        source = """
        func () -> i32 {
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_syntax_missing_braces(self):
        """Test missing braces are rejected"""
        source = "func main() -> i32 return 0"

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_syntax_missing_return_keyword(self):
        """Test missing return keyword is rejected"""
        source = """
        func main() -> i32 {
            0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_syntax_wrong_arrow(self):
        """Test wrong arrow syntax is rejected"""
        source = """
        func main() : i32 {
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_syntax_missing_parentheses(self):
        """Test missing parentheses are rejected"""
        source = """
        func main -> i32 {
            return 0
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_function_names(self):
        """Test invalid function names are rejected"""
        # Only test names that should actually be rejected by our current grammar
        # Note: Our IDENTIFIER regex /[a-zA-Z_][a-zA-Z0-9_]*/ is quite permissive
        invalid_names = ["123func"]  # Only numbers-first is invalid with our regex

        for name in invalid_names:
            source = f"""
            func {name}() -> i32 {{
                return 0
            }}
            """

            with pytest.raises(SyntaxError):
                self.parser.parse(source)

    def test_invalid_return_values(self):
        """Test invalid return values are rejected"""
        invalid_values = ['"string"', "true", "null", "3.14"]

        for value in invalid_values:
            source = f"""
            func main() -> i32 {{
                return {value}
            }}
            """

            with pytest.raises(SyntaxError):
                self.parser.parse(source)

    def test_empty_program(self):
        """Test empty program is rejected"""
        source = ""

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_multiple_statements_not_supported(self):
        """Test that multiple statements are not yet supported"""
        source = """
        func main() -> i32 {
            return 0
            return 1
        }
        """

        # This should fail because our grammar only supports one statement
        with pytest.raises(SyntaxError):
            self.parser.parse(source)


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
