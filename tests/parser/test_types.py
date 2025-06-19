"""
Test module for type annotations

Tests type annotation parsing and type system functionality.
"""

from src.hexen.parser import HexenParser


class TestTypeAnnotations:
    """Test type annotation parsing (fixed TODO investigation)"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_function_return_type_i32(self):
        """Test i32 return type annotation"""
        source = """
        func test() : i32  = {
            return 42
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "i32"

    def test_function_return_type_i64(self):
        """Test i64 return type annotation"""
        source = """
        func test() : i64  = {
            return 42
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "i64"

    def test_function_return_type_f64(self):
        """Test f64 return type annotation"""
        source = """
        func test() : f64  = {
            return 42
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "f64"

    def test_function_return_type_string(self):
        """Test string return type annotation"""
        source = """
        func test() : string  = {
            val greeting = "Hello!"
            return greeting
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "string"

    def test_function_return_type_bool(self):
        """Test bool return type annotation"""
        source = """
        func test() : bool  = {
            return true
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "bool"

    def test_function_return_type_f32(self):
        """Test f32 return type annotation"""
        source = """
        func test() : f32  = {
            return 42.0
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "f32"

    def test_function_return_type_void(self):
        """Test void return type annotation"""
        source = """
        func test() : void  = {
            return
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        assert func["return_type"] == "void"

    def test_all_type_annotations_work(self):
        """Test that all type annotations parse correctly (regression test for TODO fix)"""
        test_cases = [
            ("i32", "i32"),
            ("i64", "i64"),
            ("f32", "f32"),
            ("f64", "f64"),
            ("string", "string"),
            ("bool", "bool"),
            ("void", "void"),
        ]

        for type_name, expected in test_cases:
            source = f"""
            func test() : {type_name} = {{
                return 0
            }}
            """

            ast = self.parser.parse(source)
            actual = ast["functions"][0]["return_type"]
            assert actual == expected, (
                f"Expected {expected}, got {actual} for type {type_name}"
            )
