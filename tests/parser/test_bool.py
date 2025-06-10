"""
Test bool type parsing functionality in Hexen
"""

from src.hexen.parser import HexenParser
import pytest


class TestBoolTypeParsing:
    """Test parsing of bool type annotations and boolean literals"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_bool_type_annotation(self):
        """Test parsing function with bool return type"""
        source = """
        func test() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        assert ast["type"] == "program"
        assert len(ast["functions"]) == 1

        func = ast["functions"][0]
        assert func["return_type"] == "bool"

    def test_boolean_literal_true(self):
        """Test parsing true literal"""
        source = """
        func test() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == "return_statement"
        assert return_stmt["value"]["type"] == "literal"
        assert return_stmt["value"]["value"] is True

    def test_boolean_literal_false(self):
        """Test parsing false literal"""
        source = """
        func test() : bool = {
            return false
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == "return_statement"
        assert return_stmt["value"]["type"] == "literal"
        assert return_stmt["value"]["value"] is False

    def test_bool_variable_declaration_with_type(self):
        """Test bool variable declaration with explicit type"""
        source = """
        func test() : bool = {
            val flag : bool = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        assert val_decl["type"] == "val_declaration"
        assert val_decl["name"] == "flag"
        assert val_decl["type_annotation"] == "bool"
        assert val_decl["value"]["type"] == "literal"
        assert val_decl["value"]["value"] is True

    def test_bool_variable_declaration_without_type(self):
        """Test bool variable declaration with type inference"""
        source = """
        func test() : bool = {
            val flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        assert val_decl["type"] == "val_declaration"
        assert val_decl["name"] == "flag"
        assert val_decl["type_annotation"] is None
        assert val_decl["value"]["type"] == "literal"
        assert val_decl["value"]["value"] is True

    def test_mut_bool_variable(self):
        """Test mutable bool variable declaration"""
        source = """
        func test() : bool = {
            mut flag : bool = false
            flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        statements = func["body"]["statements"]

        # Check mut declaration
        mut_decl = statements[0]
        assert mut_decl["type"] == "mut_declaration"
        assert mut_decl["name"] == "flag"
        assert mut_decl["type_annotation"] == "bool"
        assert mut_decl["value"]["value"] is False

        # Check assignment
        assignment = statements[1]
        assert assignment["type"] == "assignment_statement"
        assert assignment["target"] == "flag"
        assert assignment["value"]["value"] is True

    def test_multiple_bool_variables(self):
        """Test multiple boolean variables in one function"""
        source = """
        func test() : bool = {
            val ready = true
            val done = false
            mut active : bool = true
            return ready
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        statements = func["body"]["statements"]

        assert len(statements) == 4  # 3 declarations + 1 return

        # Check each declaration
        assert statements[0]["value"]["value"] is True
        assert statements[1]["value"]["value"] is False
        assert statements[2]["value"]["value"] is True

    def test_bool_undef_declaration(self):
        """Test bool variable with undef value"""
        source = """
        func test() : bool = {
            val flag : bool = undef
            return true
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        assert val_decl["type"] == "val_declaration"
        assert val_decl["type_annotation"] == "bool"
        assert val_decl["value"]["type"] == "identifier"
        assert val_decl["value"]["name"] == "undef"


class TestBoolTypeEdgeCases:
    """Test edge cases for bool type parsing"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_bool_keywords_not_identifiers(self):
        """Test that 'true' and 'false' cannot be used as identifiers"""
        # This should fail because 'true' is a reserved keyword
        with pytest.raises(Exception):
            source = """
            func test() : i32 = {
                val true = 42
                return true
            }
            """
            self.parser.parse(source)

    def test_mixed_types_with_bool(self):
        """Test function with multiple types including bool"""
        source = """
        func test() : bool = {
            val number = 42
            val text = "hello"
            val flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        statements = func["body"]["statements"]

        assert statements[0]["value"]["value"] == 42
        assert statements[1]["value"]["value"] == "hello"
        assert statements[2]["value"]["value"] is True

    def test_bool_in_expression_block(self):
        """Test bool type in expression blocks"""
        source = """
        func test() : bool = {
            val result = {
                val flag = true
                return flag
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]

        # Check the expression block
        expr_block = val_decl["value"]
        assert expr_block["type"] == "block"
        inner_decl = expr_block["statements"][0]
        assert inner_decl["value"]["value"] is True
