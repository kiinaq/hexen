"""
Test module for variable declarations

Tests val/mut variable declaration system with type inference.
"""

from src.hexen.parser import HexenParser


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
        assert val_decl["type"] == "val_declaration"
        assert val_decl["name"] == "x"
        assert val_decl["type_annotation"] is None
        assert val_decl["value"]["type"] == "literal"
        assert val_decl["value"]["value"] == 42

    def test_mut_declaration_without_type(self):
        """Test mut declaration without type annotation"""
        source = """
        func main() : i32  = {
            mut counter = 0
            return counter
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check mut declaration
        mut_decl = statements[0]
        assert mut_decl["type"] == "mut_declaration"
        assert mut_decl["name"] == "counter"
        assert mut_decl["type_annotation"] is None
        assert mut_decl["value"]["type"] == "literal"
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
        assert val_decl["type"] == "val_declaration"
        assert val_decl["name"] == "message"
        assert val_decl["value"]["type"] == "literal"
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
        assert return_stmt["type"] == "return_statement"
        assert return_stmt["value"]["type"] == "identifier"
        assert return_stmt["value"]["name"] == "result"

    def test_multiple_variable_declarations(self):
        """Test multiple val/mut declarations in same function"""
        source = """
        func main() : i32  = {
            val name = "Hexen"
            mut count = 1
            val flag = 0
            return count
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Should have 4 statements: 3 declarations + 1 return
        assert len(statements) == 4

        # Check first declaration (val)
        assert statements[0]["type"] == "val_declaration"
        assert statements[0]["name"] == "name"

        # Check second declaration (mut)
        assert statements[1]["type"] == "mut_declaration"
        assert statements[1]["name"] == "count"

        # Check third declaration (val)
        assert statements[2]["type"] == "val_declaration"
        assert statements[2]["name"] == "flag"

    def test_val_vs_mut_distinction(self):
        """Test that val and mut are properly distinguished in AST"""
        source = """
        func main() : i32  = {
            val immutable = 42
            mut mutable = 42
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check that types are different
        assert statements[0]["type"] == "val_declaration"
        assert statements[1]["type"] == "mut_declaration"

        # But both have same structure otherwise
        for decl in statements[:2]:
            assert "name" in decl
            assert "type_annotation" in decl
            assert "value" in decl
