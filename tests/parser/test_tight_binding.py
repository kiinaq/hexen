"""
Test tight binding syntax for explicit type conversions.

This test ensures that the grammar enforces tight binding for conversion syntax:
- `42:i32` should work (tight binding)
- `42 : i32` should fail (spaced syntax not allowed)
"""

import pytest
from src.hexen.parser import HexenParser


class TestTightBinding:
    """Test cases for tight binding conversion syntax"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_tight_conversion_works(self):
        """Test that tight binding syntax works correctly"""
        valid_cases = [
            "func test() : i32 = { return 42:i32 }",
            "func test() : void = { val x = (10 + 20):f64 }",
            "func test() : void = { val y = variable:i64 }",
            "func test() : f32 = { return 3.14:f32 }",
            "func test() : void = { val z = true:bool }",
            "func test() : string = { return text:string }",
        ]

        for case in valid_cases:
            # Should parse successfully without exceptions
            result = self.parser.parse(case)
            assert result is not None
            assert "functions" in result
            assert len(result["functions"]) == 1

    def test_spaced_conversion_fails(self):
        """Test that spaced syntax fails with parse errors"""
        invalid_cases = [
            "func test() : i32 = { return 42 : i32 }",  # Spaces not allowed
            "func test() : void = { val x = (10 + 20) : f64 }",  # Spaces not allowed
            "func test() : void = { val y = variable : i64 }",  # Spaces not allowed
            "func test() : f32 = { return 3.14 : f32 }",  # Spaces not allowed
            "func test() : void = { val z = true : bool }",  # Spaces not allowed
        ]

        for case in invalid_cases:
            with pytest.raises(Exception):
                # Should raise ParseError due to spaced syntax
                self.parser.parse(case)

    def test_complex_expressions_with_tight_binding(self):
        """Test complex expressions with tight binding conversions"""
        complex_cases = [
            "func test() : void = { val result = (a + b):f64 }",
            "func test() : void = { val calc = (x + y):i32 }",
        ]

        for case in complex_cases:
            # Should parse successfully
            result = self.parser.parse(case)
            assert result is not None
            assert "functions" in result

    def test_multiple_conversions_in_same_function(self):
        """Test multiple conversions in the same function"""
        source = """
        func test() : void = {
            val a = 42:i32
            val b = 3.14:f64
            val c = a:i64
            val d = (b + 1.0):f32
        }
        """

        result = self.parser.parse(source)
        assert result is not None
        assert len(result["functions"]) == 1

        # Check that all conversions are properly parsed
        statements = result["functions"][0]["body"]["statements"]
        assert len(statements) == 4

        for stmt in statements:
            assert stmt["type"] == "val_declaration"
            assert stmt["value"]["type"] == "explicit_conversion_expression"
            assert "target_type" in stmt["value"]

    def test_all_type_conversions_work(self):
        """Test that tight binding works with all supported types"""
        type_cases = [
            ("42:i32", "i32"),
            ("42:i64", "i64"),
            ("3.14:f32", "f32"),
            ("3.14:f64", "f64"),
            ("text:string", "string"),
            ("flag:bool", "bool"),
        ]

        for expr, expected_type in type_cases:
            source = f"func test() : void = {{ val x = {expr} }}"
            result = self.parser.parse(source)

            # Verify the conversion is parsed with correct target type
            conversion = result["functions"][0]["body"]["statements"][0]["value"]
            assert conversion["type"] == "explicit_conversion_expression"
            assert conversion["target_type"] == expected_type
