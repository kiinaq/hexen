"""
Test module for variable declarations

Tests val/mut variable declaration system with type inference.
"""

from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestVariableDeclarations:
    """Test the val/mut variable declaration system (Phase 3 features)"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_val_declaration_without_type(self):
        """Test val declaration without type annotation"""
        source = """
        func main() : i32  = {
            val x = 42
            return x
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check val declaration
        val_decl = statements[0]
        assert val_decl["type"] == NodeType.VAL_DECLARATION.value
        assert val_decl["name"] == "x"
        assert val_decl["type_annotation"] is None
        assert val_decl["value"]["type"] == NodeType.LITERAL.value
        assert val_decl["value"]["value"] == 42

    def test_mut_declaration_with_explicit_type(self):
        """Test mut declaration requires explicit type annotation"""
        source = """
        func main() : i32  = {
            mut counter : i32 = 0
            return counter
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check mut declaration
        mut_decl = statements[0]
        assert mut_decl["type"] == NodeType.MUT_DECLARATION.value
        assert mut_decl["name"] == "counter"
        assert mut_decl["type_annotation"] == "i32"
        assert mut_decl["value"]["type"] == NodeType.LITERAL.value
        assert mut_decl["value"]["value"] == 0

    def test_val_declaration_with_string(self):
        """Test val declaration with string literal"""
        source = """
        func main() : i32  = {
            val message = "Hello, Hexen!"
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check val declaration with string
        val_decl = statements[0]
        assert val_decl["type"] == NodeType.VAL_DECLARATION.value
        assert val_decl["name"] == "message"
        assert val_decl["value"]["type"] == NodeType.LITERAL.value
        assert val_decl["value"]["value"] == "Hello, Hexen!"

    def test_variable_reference_in_return(self):
        """Test using declared variables in return statements"""
        source = """
        func main() : i32  = {
            val result = 123
            return result
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check return statement references variable
        return_stmt = statements[1]
        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.IDENTIFIER.value
        assert return_stmt["value"]["name"] == "result"

    def test_multiple_variable_declarations(self):
        """Test multiple val/mut declarations in same function"""
        source = """
        func main() : i32  = {
            val name = "Hexen"
            mut count : i32 = 1
            val flag = 0
            return count
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Should have 4 statements: 3 declarations + 1 return
        assert len(statements) == 4

        # Check first declaration (val)
        assert statements[0]["type"] == NodeType.VAL_DECLARATION.value
        assert statements[0]["name"] == "name"

        # Check second declaration (mut)
        assert statements[1]["type"] == NodeType.MUT_DECLARATION.value
        assert statements[1]["name"] == "count"

        # Check third declaration (val)
        assert statements[2]["type"] == NodeType.VAL_DECLARATION.value
        assert statements[2]["name"] == "flag"

    def test_val_vs_mut_distinction(self):
        """Test that val and mut are properly distinguished in AST"""
        source = """
        func main() : i32  = {
            val immutable = 42
            mut mutable : i32 = 42
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check that types are different
        assert statements[0]["type"] == NodeType.VAL_DECLARATION.value
        assert statements[1]["type"] == NodeType.MUT_DECLARATION.value

        # But both have same structure otherwise
        for decl in statements[:2]:
            assert "name" in decl
            assert "type_annotation" in decl
            assert "value" in decl

    def test_val_with_explicit_type_annotations(self):
        """Test val declarations with explicit type annotations"""
        source = """
        func main() : i32  = {
            val integer : i32 = 42
            val long_int : i64 = 123
            val single : f32 = 3.14
            val double : f64 = 2.718
            val text : string = "hello"
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        expected_types = ["i32", "i64", "f32", "f64", "string"]
        expected_names = ["integer", "long_int", "single", "double", "text"]
        expected_values = [42, 123, 3.14, 2.718, "hello"]

        for i, (expected_type, expected_name, expected_value) in enumerate(
            zip(expected_types, expected_names, expected_values)
        ):
            decl = statements[i]
            assert decl["type"] == NodeType.VAL_DECLARATION.value
            assert decl["name"] == expected_name
            assert decl["type_annotation"] == expected_type
            assert decl["value"]["value"] == expected_value

    def test_mut_with_explicit_type_annotations(self):
        """Test mut declarations with explicit type annotations"""
        source = """
        func main() : i32  = {
            mut counter : i32 = 0
            mut big_counter : i64 = 1000
            mut precise : f32 = 0.0
            mut very_precise : f64 = 0.0
            mut message : string = ""
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        expected_types = ["i32", "i64", "f32", "f64", "string"]
        expected_names = [
            "counter",
            "big_counter",
            "precise",
            "very_precise",
            "message",
        ]
        expected_values = [0, 1000, 0.0, 0.0, ""]

        for i, (expected_type, expected_name, expected_value) in enumerate(
            zip(expected_types, expected_names, expected_values)
        ):
            decl = statements[i]
            assert decl["type"] == NodeType.MUT_DECLARATION.value
            assert decl["name"] == expected_name
            assert decl["type_annotation"] == expected_type
            assert decl["value"]["value"] == expected_value

    def test_mixed_explicit_and_inferred_types(self):
        """Test mixing explicit type annotations with type inference (val only)"""
        source = """
        func main() : i32  = {
            val inferred_int = 42
            val explicit_int : i32 = 42
            mut explicit_string1 : string = "hello"
            mut explicit_string2 : string = "world"
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check val inferred type has None annotation
        assert statements[0]["type_annotation"] is None

        # Check all explicit types have proper annotation
        assert statements[1]["type_annotation"] == "i32"
        assert (
            statements[2]["type_annotation"] == "string"
        )  # mut requires explicit type
        assert (
            statements[3]["type_annotation"] == "string"
        )  # mut requires explicit type
