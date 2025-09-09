"""
Test module for comptime type parsing

Tests that numeric literals generate correct comptime AST nodes.
This validates parser implementation: parser generates comptime_int
and comptime_float nodes for the semantic analyzer's type system.
"""

from src.hexen.ast_nodes import NodeType
from src.hexen.parser import HexenParser


class TestComptimeParsing:
    """Test comptime type AST node generation"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_integer_generates_comptime_int(self):
        """Test integer literals generate COMPTIME_INT nodes"""
        source = """
        func test() : void = {
            val x = 42
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        assert val_decl["value"]["type"] == NodeType.COMPTIME_INT.value
        assert val_decl["value"]["value"] == 42

    def test_float_generates_comptime_float(self):
        """Test float literals generate COMPTIME_FLOAT nodes"""
        source = """
        func test() : void = {
            val x = 3.14
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        assert val_decl["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert val_decl["value"]["value"] == 3.14

    def test_negative_integer_generates_comptime_int(self):
        """Test negative integer literals generate COMPTIME_INT nodes"""
        source = """
        func test() : void = {
            val x = -100
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        # Negative numbers are unary operations on comptime_int literals
        assert val_decl["value"]["type"] == NodeType.UNARY_OPERATION.value
        assert val_decl["value"]["operator"] == "-"
        assert val_decl["value"]["operand"]["type"] == NodeType.COMPTIME_INT.value
        assert val_decl["value"]["operand"]["value"] == 100

    def test_negative_float_generates_comptime_float(self):
        """Test negative float literals generate COMPTIME_FLOAT nodes"""
        source = """
        func test() : void = {
            val x = -2.5
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        # Negative numbers are unary operations on comptime_float literals
        assert val_decl["value"]["type"] == NodeType.UNARY_OPERATION.value
        assert val_decl["value"]["operator"] == "-"
        assert val_decl["value"]["operand"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert val_decl["value"]["operand"]["value"] == 2.5

    def test_multiple_comptime_literals(self):
        """Test multiple comptime literals in same function"""
        source = """
        func test() : void = {
            val integer = 42
            val float = 3.14
            val zero = 0
            val small_float = 0.5
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check each declaration
        assert statements[0]["value"]["type"] == NodeType.COMPTIME_INT.value
        assert statements[0]["value"]["value"] == 42

        assert statements[1]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[1]["value"]["value"] == 3.14

        assert statements[2]["value"]["type"] == NodeType.COMPTIME_INT.value
        assert statements[2]["value"]["value"] == 0

        assert statements[3]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[3]["value"]["value"] == 0.5

    def test_comptime_in_binary_operations(self):
        """Test comptime literals in binary operations"""
        source = """
        func test() : void = {
            val result = 42 + 100
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        binary_op = val_decl["value"]

        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == "+"
        assert binary_op["left"]["type"] == NodeType.COMPTIME_INT.value
        assert binary_op["left"]["value"] == 42
        assert binary_op["right"]["type"] == NodeType.COMPTIME_INT.value
        assert binary_op["right"]["value"] == 100

    def test_comptime_in_mixed_binary_operations(self):
        """Test comptime literals in mixed int/float operations"""
        source = """
        func test() : void = {
            val result = 42 + 3.14
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        binary_op = val_decl["value"]

        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == "+"
        assert binary_op["left"]["type"] == NodeType.COMPTIME_INT.value
        assert binary_op["left"]["value"] == 42
        assert binary_op["right"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert binary_op["right"]["value"] == 3.14

    def test_comptime_in_return_statements(self):
        """Test comptime literals in return statements"""
        source = """
        func test() : i32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        return_stmt = ast["functions"][0]["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.COMPTIME_INT.value
        assert return_stmt["value"]["value"] == 42

    def test_string_remains_literal(self):
        """Test string literals remain LITERAL nodes (not comptime)"""
        source = """
        func test() : void = {
            val x = "hello"
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        assert val_decl["value"]["type"] == NodeType.LITERAL.value
        assert val_decl["value"]["value"] == "hello"

    def test_boolean_remains_literal(self):
        """Test boolean literals remain LITERAL nodes (not comptime)"""
        source = """
        func test() : void = {
            val x = true
            val y = false
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        assert statements[0]["value"]["type"] == NodeType.LITERAL.value
        assert statements[0]["value"]["value"] is True

        assert statements[1]["value"]["type"] == NodeType.LITERAL.value
        assert statements[1]["value"]["value"] is False

    def test_comptime_with_type_annotations(self):
        """Test comptime literals with type annotations work correctly"""
        source = """
        func test() : void = {
            val result = 42:i32
        }
        """
        ast = self.parser.parse(source)
        val_decl = ast["functions"][0]["body"]["statements"][0]
        type_annotated_expr = val_decl["value"]

        assert (
            type_annotated_expr["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        )
        assert type_annotated_expr["expression"]["type"] == NodeType.COMPTIME_INT.value
        assert type_annotated_expr["expression"]["value"] == 42
        assert type_annotated_expr["target_type"] == "i32"

    def test_comptime_edge_case_values(self):
        """Test comptime literals with edge case values"""
        source = """
        func test() : void = {
            val large = 9223372036854775807
            val precise = 3.141592653589793
            val tiny = 0.0001
            val whole_float = 5.0
        }
        """
        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Large integer
        assert statements[0]["value"]["type"] == NodeType.COMPTIME_INT.value
        assert statements[0]["value"]["value"] == 9223372036854775807

        # High precision float
        assert statements[1]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[1]["value"]["value"] == 3.141592653589793

        # Small float
        assert statements[2]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[2]["value"]["value"] == 0.0001

        # Whole number float
        assert statements[3]["value"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert statements[3]["value"]["value"] == 5.0
