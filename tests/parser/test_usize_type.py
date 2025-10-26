"""
Parser tests for usize platform index type.

Tests ONLY syntax parsing and AST generation for usize type.
Semantic validation (type checking, conversion rules) tested separately.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestUsizeVariableDeclarations:
    """Test parsing of variable declarations with usize type."""

    def test_val_with_usize_type(self):
        """Test val variable with usize type annotation"""
        parser = HexenParser()
        code = "val index : usize = 0"
        ast = parser.parse(code)

        # Verify program structure
        assert ast["type"] == NodeType.PROGRAM.value
        assert "statements" in ast
        assert len(ast["statements"]) == 1

        # Verify variable declaration
        decl = ast["statements"][0]
        assert decl["type"] == NodeType.VAL_DECLARATION.value
        assert decl["name"] == "index"
        assert decl["type_annotation"] == "usize"

        # Verify value
        assert decl["value"]["type"] == NodeType.COMPTIME_INT.value
        assert decl["value"]["value"] == 0

    def test_mut_with_usize_type(self):
        """Test mut variable with usize type annotation"""
        parser = HexenParser()
        code = "mut counter : usize = 42"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type"] == NodeType.MUT_DECLARATION.value
        assert decl["name"] == "counter"
        assert decl["type_annotation"] == "usize"
        assert decl["value"]["value"] == 42

    def test_usize_with_comptime_int(self):
        """Test usize variable with comptime_int literal"""
        parser = HexenParser()
        code = "val size : usize = 1024"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "usize"
        assert decl["value"]["type"] == NodeType.COMPTIME_INT.value
        assert decl["value"]["value"] == 1024

    def test_usize_with_undef(self):
        """Test usize variable initialized with undef"""
        parser = HexenParser()
        code = "mut idx : usize = undef"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type"] == NodeType.MUT_DECLARATION.value
        assert decl["type_annotation"] == "usize"
        # undef is parsed as an identifier
        assert decl["value"]["type"] == NodeType.IDENTIFIER.value
        assert decl["value"]["name"] == "undef"


class TestUsizeFunctionParameters:
    """Test parsing of function parameters with usize type."""

    def test_single_usize_parameter(self):
        """Test function with single usize parameter"""
        parser = HexenParser()
        code = """
        func get_element(index : usize) : i32 = {
            return 0
        }
        """
        ast = parser.parse(code)

        # Verify function structure
        func = ast["functions"][0]
        assert func["type"] == NodeType.FUNCTION.value
        assert func["name"] == "get_element"

        # Verify parameter
        params = func["parameters"]
        assert len(params) == 1
        assert params[0]["name"] == "index"
        assert params[0]["param_type"] == "usize"
        assert params[0]["is_mutable"] is False

    def test_multiple_parameters_with_usize(self):
        """Test function with multiple parameters including usize"""
        parser = HexenParser()
        code = """
        func slice_array(start : usize, end : usize, step : i32) : void = {
            return
        }
        """
        ast = parser.parse(code)

        func = ast["functions"][0]
        params = func["parameters"]

        assert len(params) == 3
        assert params[0]["name"] == "start"
        assert params[0]["param_type"] == "usize"
        assert params[1]["name"] == "end"
        assert params[1]["param_type"] == "usize"
        assert params[2]["name"] == "step"
        assert params[2]["param_type"] == "i32"

    def test_mut_usize_parameter(self):
        """Test mutable usize parameter"""
        parser = HexenParser()
        code = """
        func increment_index(mut idx : usize) : usize = {
            return idx
        }
        """
        ast = parser.parse(code)

        func = ast["functions"][0]
        params = func["parameters"]

        assert len(params) == 1
        assert params[0]["name"] == "idx"
        assert params[0]["param_type"] == "usize"
        assert params[0]["is_mutable"] is True


class TestUsizeFunctionReturnTypes:
    """Test parsing of function return types with usize."""

    def test_usize_return_type(self):
        """Test function returning usize"""
        parser = HexenParser()
        code = """
        func get_length() : usize = {
            return 42
        }
        """
        ast = parser.parse(code)

        func = ast["functions"][0]
        assert func["type"] == NodeType.FUNCTION.value
        assert func["name"] == "get_length"
        assert func["return_type"] == "usize"

    def test_function_usize_param_and_return(self):
        """Test function with usize parameter and return type"""
        parser = HexenParser()
        code = """
        func double_index(idx : usize) : usize = {
            return idx
        }
        """
        ast = parser.parse(code)

        func = ast["functions"][0]
        params = func["parameters"]

        assert params[0]["param_type"] == "usize"
        assert func["return_type"] == "usize"


class TestUsizeConversionSyntax:
    """Test parsing of usize in explicit conversion expressions."""

    def test_conversion_to_usize(self):
        """Test explicit conversion to usize: value:usize"""
        parser = HexenParser()
        code = "val idx : usize = some_value:usize"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "usize"

        # Verify conversion expression
        conv_expr = decl["value"]
        assert conv_expr["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        assert conv_expr["target_type"] == "usize"

        # Inner value is identifier (field is "expression" not "value")
        assert conv_expr["expression"]["type"] == NodeType.IDENTIFIER.value
        assert conv_expr["expression"]["name"] == "some_value"

    def test_i32_to_usize_conversion(self):
        """Test explicit i32 to usize conversion"""
        parser = HexenParser()
        code = "val idx : usize = i32_val:usize"
        ast = parser.parse(code)

        conv_expr = ast["statements"][0]["value"]
        assert conv_expr["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        assert conv_expr["target_type"] == "usize"

    def test_usize_to_i64_conversion(self):
        """Test explicit usize to i64 conversion"""
        parser = HexenParser()
        code = "val big : i64 = usize_val:i64"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "i64"

        conv_expr = decl["value"]
        assert conv_expr["target_type"] == "i64"


class TestUsizeArrayTypes:
    """Test parsing of arrays with usize dimensions or types."""

    def test_array_with_usize_element_type(self):
        """Test array of usize elements: [_]usize"""
        parser = HexenParser()
        code = "val indices : [_]usize = [0, 1, 2]"
        ast = parser.parse(code)

        decl = ast["statements"][0]

        # Verify array type
        array_type = decl["type_annotation"]
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert array_type["element_type"] == "usize"

        # Verify dimension
        dimensions = array_type["dimensions"]
        assert len(dimensions) == 1
        assert dimensions[0]["size"] == "_"

    def test_fixed_size_usize_array(self):
        """Test fixed-size array of usize: [5]usize"""
        parser = HexenParser()
        code = "val buffer : [5]usize = [0, 0, 0, 0, 0]"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        array_type = decl["type_annotation"]

        assert array_type["element_type"] == "usize"
        assert array_type["dimensions"][0]["size"] == 5


class TestUsizeComplexExpressions:
    """Test usize in complex expressions and contexts."""

    def test_usize_in_binary_operation(self):
        """Test usize value in binary operation"""
        parser = HexenParser()
        code = """
        val start : usize = 5
        val offset : usize = start
        """
        ast = parser.parse(code)

        # First declaration
        decl1 = ast["statements"][0]
        assert decl1["type_annotation"] == "usize"
        assert decl1["value"]["value"] == 5

        # Second declaration (identifier reference)
        decl2 = ast["statements"][1]
        assert decl2["type_annotation"] == "usize"
        assert decl2["value"]["type"] == NodeType.IDENTIFIER.value
        assert decl2["value"]["name"] == "start"

    def test_usize_function_call_argument(self):
        """Test usize as function call argument"""
        parser = HexenParser()
        code = """
        func process(idx : usize) : void = {
            return
        }
        val result = process(42)
        """
        ast = parser.parse(code)

        # Verify function
        func = ast["functions"][0]
        assert func["parameters"][0]["param_type"] == "usize"

        # Verify function call
        call_stmt = ast["statements"][0]
        call_expr = call_stmt["value"]
        assert call_expr["type"] == NodeType.FUNCTION_CALL.value

        # Argument is comptime_int (will adapt to usize semantically)
        args = call_expr["arguments"]
        assert len(args) == 1
        assert args[0]["type"] == NodeType.COMPTIME_INT.value
        assert args[0]["value"] == 42


class TestUsizeEdgeCases:
    """Test edge cases and boundary conditions for usize parsing."""

    def test_usize_with_zero(self):
        """Test usize with zero value"""
        parser = HexenParser()
        code = "val zero : usize = 0"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "usize"
        assert decl["value"]["value"] == 0

    def test_usize_with_large_literal(self):
        """Test usize with large comptime_int literal"""
        parser = HexenParser()
        code = "val large : usize = 4294967295"  # Max 32-bit unsigned
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "usize"
        assert decl["value"]["type"] == NodeType.COMPTIME_INT.value
        assert decl["value"]["value"] == 4294967295

    def test_usize_with_hexadecimal(self):
        """Test usize with hexadecimal literal"""
        parser = HexenParser()
        code = "val hex : usize = 0xFF"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "usize"
        assert decl["value"]["type"] == NodeType.COMPTIME_INT.value
        assert decl["value"]["value"] == 255

    def test_usize_with_binary(self):
        """Test usize with binary literal"""
        parser = HexenParser()
        code = "val bin : usize = 0b1010"
        ast = parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"] == "usize"
        assert decl["value"]["value"] == 10


class TestUsizeMultipleContexts:
    """Test usize appearing in multiple contexts in same program."""

    def test_usize_multiple_contexts(self):
        """Test usize in variables, parameters, and return types"""
        parser = HexenParser()
        code = """
        func calculate_index(start : usize, offset : usize) : usize = {
            val result : usize = start
            return result
        }
        val idx : usize = 42
        """
        ast = parser.parse(code)

        # Verify function
        func = ast["functions"][0]
        assert func["parameters"][0]["param_type"] == "usize"
        assert func["parameters"][1]["param_type"] == "usize"
        assert func["return_type"] == "usize"

        # Verify internal variable
        body_statements = func["body"]["statements"]
        internal_decl = body_statements[0]
        assert internal_decl["type_annotation"] == "usize"

        # Verify external variable
        external_decl = ast["statements"][0]
        assert external_decl["type_annotation"] == "usize"
