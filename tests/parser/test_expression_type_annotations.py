"""
Test module for expression type annotations

Tests the parsing of type annotations on expressions (`: type` syntax).
This is critical for the Hexen type system's "explicit acknowledgment" pattern.
"""

from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestExpressionTypeAnnotations:
    """Test expression type annotation parsing (: type syntax)"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_simple_literal_type_annotation(self):
        """Test basic literal with type annotation"""
        source = """
        func main() : i32  = {
            val result : i32 = 42 : i32
            return result
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        # Check variable declaration
        val_decl = statements[0]
        assert val_decl["type"] == NodeType.VAL_DECLARATION.value
        assert val_decl["name"] == "result"
        assert val_decl["type_annotation"] == "i32"

        # Check the expression has type annotation
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["expression"]["type"] == NodeType.COMPTIME_INT.value
        assert expr["expression"]["value"] == 42
        assert expr["type_annotation"] == "i32"

    def test_float_literal_type_annotation(self):
        """Test float literal with type annotation"""
        source = """
        func main() : i32  = {
            val precise : f32 = 3.14 : f32
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["expression"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert expr["expression"]["value"] == 3.14
        assert expr["type_annotation"] == "f32"

    def test_binary_operation_type_annotation(self):
        """Test binary operation with type annotation"""
        source = """
        func main() : i32  = {
            val mixed : f64 = (42 + 3.14) : f64
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["type_annotation"] == "f64"

        # Check the inner binary operation
        binary_op = expr["expression"]
        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == "+"
        assert binary_op["left"]["type"] == NodeType.COMPTIME_INT.value
        assert binary_op["left"]["value"] == 42
        assert binary_op["right"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert binary_op["right"]["value"] == 3.14

    def test_complex_expression_type_annotation(self):
        """Test complex nested expression with type annotation"""
        source = """
        func main() : i32  = {
            val complex : i32 = (10 + 20 * 30) : i32
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["type_annotation"] == "i32"

        # Check the inner complex expression
        binary_op = expr["expression"]
        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == "+"

    def test_identifier_type_annotation(self):
        """Test identifier (variable reference) with type annotation"""
        source = """
        func main() : i32  = {
            val x = 42
            val result : i32 = x : i32
            return result
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[1]
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["type_annotation"] == "i32"

        # Check the identifier
        identifier = expr["expression"]
        assert identifier["type"] == NodeType.IDENTIFIER.value
        assert identifier["name"] == "x"

    def test_all_types_in_annotations(self):
        """Test all concrete types work in type annotations"""
        source = """
        func main() : i32  = {
            val a : i32 = 42 : i32
            val b : i64 = 123 : i64
            val c : f32 = 3.14 : f32
            val d : f64 = 2.718 : f64
            val e : string = "hello" : string
            val f : bool = true : bool
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        expected_types = ["i32", "i64", "f32", "f64", "string", "bool"]
        expected_values = [42, 123, 3.14, 2.718, "hello", True]
        expected_node_types = [
            NodeType.COMPTIME_INT.value,
            NodeType.COMPTIME_INT.value,
            NodeType.COMPTIME_FLOAT.value,
            NodeType.COMPTIME_FLOAT.value,
            NodeType.LITERAL.value,
            NodeType.LITERAL.value,
        ]

        for i, (expected_type, expected_value, expected_node_type) in enumerate(
            zip(expected_types, expected_values, expected_node_types)
        ):
            val_decl = statements[i]
            expr = val_decl["value"]
            assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
            assert expr["type_annotation"] == expected_type
            assert expr["expression"]["type"] == expected_node_type
            assert expr["expression"]["value"] == expected_value

    def test_mut_variable_with_type_annotation(self):
        """Test mut variable with type annotation"""
        source = """
        func main() : i32  = {
            mut result : f64 = 42.0 : f64
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        mut_decl = statements[0]
        assert mut_decl["type"] == NodeType.MUT_DECLARATION.value
        assert mut_decl["type_annotation"] == "f64"

        expr = mut_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["expression"]["type"] == NodeType.COMPTIME_FLOAT.value
        assert expr["expression"]["value"] == 42.0
        assert expr["type_annotation"] == "f64"

    def test_parenthesized_expression_type_annotation(self):
        """Test parenthesized expression with type annotation"""
        source = """
        func main() : i32  = {
            val result : i32 = ((10 + 20) * 30) : i32
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["type_annotation"] == "i32"

        # The expression should be the parenthesized content
        inner_expr = expr["expression"]
        assert inner_expr["type"] == NodeType.BINARY_OPERATION.value
        assert inner_expr["operator"] == "*"

    def test_nested_binary_operations_type_annotation(self):
        """Test nested binary operations with type annotation"""
        source = """
        func main() : i32  = {
            val calc : f64 = (10.0 + 20.0 * 30.0 - 40.0 / 50.0) : f64
            return 0
        }
        """

        ast = self.parser.parse(source)
        statements = ast["functions"][0]["body"]["statements"]

        val_decl = statements[0]
        expr = val_decl["value"]
        assert expr["type"] == NodeType.TYPE_ANNOTATED_EXPRESSION.value
        assert expr["type_annotation"] == "f64"

        # Check that the inner expression is properly parsed
        inner_expr = expr["expression"]
        assert inner_expr["type"] == NodeType.BINARY_OPERATION.value
