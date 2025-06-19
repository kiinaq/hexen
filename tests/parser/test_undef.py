"""
Test module for undef declarations

Tests uninitialized variable declarations with undef keyword.
"""

from src.hexen.parser import HexenParser


class TestUndefDeclarations:
    """Test uninitialized variable declarations with undef keyword."""

    def setup_method(self):
        self.parser = HexenParser()

    def test_val_undef_explicit_type(self):
        """Test val declaration with undef requires explicit type."""
        code = """
        func test() : i32  = {
            val x: i32 = undef
            return 0
        }
        """
        result = self.parser.parse(code)
        assert (
            result["functions"][0]["body"]["statements"][0]["type"] == "val_declaration"
        )
        assert result["functions"][0]["body"]["statements"][0]["name"] == "x"
        assert (
            result["functions"][0]["body"]["statements"][0]["type_annotation"] == "i32"
        )
        assert (
            result["functions"][0]["body"]["statements"][0]["value"]["type"]
            == "identifier"
        )
        assert (
            result["functions"][0]["body"]["statements"][0]["value"]["name"] == "undef"
        )

    def test_mut_undef_explicit_type(self):
        """Test mut declaration with undef requires explicit type."""
        code = """
        func test() : i32  = {
            mut y: string = undef
            return 0
        }
        """
        result = self.parser.parse(code)
        stmt = result["functions"][0]["body"]["statements"][0]
        assert stmt["type"] == "mut_declaration"
        assert stmt["name"] == "y"
        assert stmt["type_annotation"] == "string"
        assert stmt["value"]["name"] == "undef"

    def test_type_inference_still_works(self):
        """Test that type inference works without explicit types."""
        code = """
        func test() : i32  = {
            val inferred_int = 42
            val inferred_string = "hello"
            mut mutable_int = 123
            return inferred_int
        }
        """
        result = self.parser.parse(code)
        statements = result["functions"][0]["body"]["statements"]

        # val inferred_int = 42
        assert statements[0]["type"] == "val_declaration"
        assert statements[0]["name"] == "inferred_int"
        assert statements[0]["type_annotation"] is None
        assert statements[0]["value"]["value"] == 42

        # val inferred_string = "hello"
        assert statements[1]["type"] == "val_declaration"
        assert statements[1]["name"] == "inferred_string"
        assert statements[1]["type_annotation"] is None
        assert statements[1]["value"]["value"] == "hello"

        # mut mutable_int = 123
        assert statements[2]["type"] == "mut_declaration"
        assert statements[2]["name"] == "mutable_int"
        assert statements[2]["type_annotation"] is None
        assert statements[2]["value"]["value"] == 123

    def test_mixed_declarations_in_same_function(self):
        """Test mixing inferred and explicit undef declarations."""
        code = """
        func test() : i32  = {
            val a = 42
            val b: i64 = undef
            mut c = "test"
            mut d: f64 = undef
            return a
        }
        """
        result = self.parser.parse(code)
        statements = result["functions"][0]["body"]["statements"]

        # val a = 42 (inferred)
        assert statements[0]["type_annotation"] is None
        assert statements[0]["value"]["value"] == 42

        # val b: i64 = undef (explicit)
        assert statements[1]["type_annotation"] == "i64"
        assert statements[1]["value"]["name"] == "undef"

        # mut c = "test" (inferred)
        assert statements[2]["type_annotation"] is None
        assert statements[2]["value"]["value"] == "test"

        # mut d: f64 = undef (explicit)
        assert statements[3]["type_annotation"] == "f64"
        assert statements[3]["value"]["name"] == "undef"

    def test_all_types_with_undef(self):
        """Test undef works with all supported types."""
        code = """
        func test() : i32  = {
            val a: i32 = undef
            val b: i64 = undef
            val c: f32 = undef
            val d: f64 = undef
            val e: string = undef
            val f: bool = undef
            return 0
        }
        """
        result = self.parser.parse(code)
        statements = result["functions"][0]["body"]["statements"]

        expected_types = ["i32", "i64", "f32", "f64", "string", "bool"]
        for i, expected_type in enumerate(expected_types):
            assert statements[i]["type_annotation"] == expected_type
            assert statements[i]["value"]["name"] == "undef"

    def test_undef_with_f32_specifically(self):
        """Test undef works specifically with f32 type"""
        code = """
        func test() : i32  = {
            mut precise : f32 = undef
            return 0
        }
        """
        result = self.parser.parse(code)
        stmt = result["functions"][0]["body"]["statements"][0]
        assert stmt["type"] == "mut_declaration"
        assert stmt["name"] == "precise"
        assert stmt["type_annotation"] == "f32"
        assert stmt["value"]["name"] == "undef"

    def test_undef_with_bool_specifically(self):
        """Test undef works specifically with bool type"""
        code = """
        func test() : i32  = {
            val flag : bool = undef
            return 0
        }
        """
        result = self.parser.parse(code)
        stmt = result["functions"][0]["body"]["statements"][0]
        assert stmt["type"] == "val_declaration"
        assert stmt["name"] == "flag"
        assert stmt["type_annotation"] == "bool"
        assert stmt["value"]["name"] == "undef"
