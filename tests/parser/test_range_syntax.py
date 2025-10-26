"""
Parser tests for range system syntax.

Tests ONLY syntax parsing and AST generation for ranges.
Semantic validation (type checking) tested separately in tests/semantic/ranges/.

Test Coverage:
- Range literal expressions (bounded, unbounded, stepped)
- Range type annotations (range[T])
- Array indexing with ranges (unified [..] model)
- Range expressions in various contexts
- Operator precedence
- Edge cases
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestRangeLiteralSyntax:
    """Test parsing of range literal expressions."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_bounded_exclusive(self):
        """Test exclusive bounded range: 1..10"""
        code = "val r = 1..10"
        ast = self.parser.parse(code)

        # Verify AST structure
        decl = ast["statements"][0]
        assert decl["type"] == NodeType.VAL_DECLARATION.value

        range_expr = decl["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["start"]["type"] == NodeType.COMPTIME_INT.value
        assert range_expr["start"]["value"] == 1
        assert range_expr["end"]["type"] == NodeType.COMPTIME_INT.value
        assert range_expr["end"]["value"] == 10
        assert range_expr["step"] is None
        assert range_expr["inclusive"] is False

    def test_bounded_inclusive(self):
        """Test inclusive bounded range: 1..=10"""
        code = "val r = 1..=10"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["inclusive"] is True
        assert range_expr["start"]["value"] == 1
        assert range_expr["end"]["value"] == 10

    def test_bounded_with_step_exclusive(self):
        """Test exclusive bounded range with step: 0..100:2"""
        code = "val r = 0..100:2"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["start"]["value"] == 0
        assert range_expr["end"]["value"] == 100
        assert range_expr["step"]["type"] == NodeType.COMPTIME_INT.value
        assert range_expr["step"]["value"] == 2
        assert range_expr["inclusive"] is False

    def test_bounded_with_step_inclusive(self):
        """Test inclusive bounded range with step: 0..=100:2"""
        code = "val r = 0..=100:2"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["step"]["value"] == 2
        assert range_expr["inclusive"] is True

    def test_negative_step(self):
        """Test range with negative step: 10..0:-1"""
        code = "val r = 10..0:-1"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["start"]["value"] == 10
        assert range_expr["end"]["value"] == 0

        # -1 is parsed as unary operation
        step = range_expr["step"]
        assert step["type"] == NodeType.UNARY_OPERATION.value
        assert step["operator"] == "-"
        assert step["operand"]["value"] == 1


class TestUnboundedRangeSyntax:
    """Test parsing of unbounded range expressions."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_range_from(self):
        """Test unbounded from range: 5.."""
        code = "val r = 5.."
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["start"]["value"] == 5
        assert range_expr["end"] is None
        assert range_expr["step"] is None
        assert range_expr["inclusive"] is False

    def test_range_from_with_step(self):
        """Test unbounded from range with step: 5..:2"""
        code = "val r = 5..:2"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["start"]["value"] == 5
        assert range_expr["end"] is None
        assert range_expr["step"]["value"] == 2

    def test_range_to_exclusive(self):
        """Test unbounded to range (exclusive): ..10"""
        code = "val r = ..10"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["start"] is None
        assert range_expr["end"]["value"] == 10
        assert range_expr["step"] is None
        assert range_expr["inclusive"] is False

    def test_range_to_inclusive(self):
        """Test unbounded to range (inclusive): ..=10"""
        code = "val r = ..=10"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["start"] is None
        assert range_expr["end"]["value"] == 10
        assert range_expr["inclusive"] is True

    def test_range_full(self):
        """Test full unbounded range: .."""
        code = "val r = .."
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["type"] == NodeType.RANGE_EXPR.value
        assert range_expr["start"] is None
        assert range_expr["end"] is None
        assert range_expr["step"] is None
        assert range_expr["inclusive"] is False


class TestRangeTypeAnnotations:
    """Test parsing of range type annotations."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_range_type_i32(self):
        """Test range[i32] type annotation"""
        code = "val r : range[i32] = 1..10"
        ast = self.parser.parse(code)

        decl = ast["statements"][0]
        assert decl["type_annotation"]["type"] == NodeType.RANGE_TYPE.value
        assert decl["type_annotation"]["element_type"] == "i32"

    def test_range_type_usize(self):
        """Test range[usize] type annotation"""
        code = "val r : range[usize] = 0..100"
        ast = self.parser.parse(code)

        type_ann = ast["statements"][0]["type_annotation"]
        assert type_ann["type"] == NodeType.RANGE_TYPE.value
        assert type_ann["element_type"] == "usize"

    def test_range_type_f64(self):
        """Test range[f64] type annotation"""
        code = "val r : range[f64] = 0.0..1.0:0.01"
        ast = self.parser.parse(code)

        type_ann = ast["statements"][0]["type_annotation"]
        assert type_ann["element_type"] == "f64"

    def test_range_type_in_function_parameter(self):
        """Test range type as function parameter"""
        code = """
        func process(r : range[i32]) : void = {
            return
        }
        """
        ast = self.parser.parse(code)

        func = ast["functions"][0]
        param = func["parameters"][0]
        param_type = param["param_type"]

        assert param_type["type"] == NodeType.RANGE_TYPE.value
        assert param_type["element_type"] == "i32"

    def test_range_type_as_return_type(self):
        """Test range type as function return type"""
        code = """
        func get_range() : range[usize] = {
            return 0..10
        }
        """
        ast = self.parser.parse(code)

        func = ast["functions"][0]
        return_type = func["return_type"]

        assert return_type["type"] == NodeType.RANGE_TYPE.value
        assert return_type["element_type"] == "usize"


class TestArrayIndexingWithRanges:
    """Test parsing of array indexing using range expressions."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_array_slice_exclusive(self):
        """Test array slice with exclusive range: arr[1..4]"""
        code = """
        val arr = [10, 20, 30, 40, 50]
        val slice = arr[1..4]
        """
        ast = self.parser.parse(code)

        slice_expr = ast["statements"][1]["value"]
        assert slice_expr["type"] == NodeType.ARRAY_ACCESS.value

        range_idx = slice_expr["index"]
        assert range_idx["type"] == NodeType.RANGE_EXPR.value
        assert range_idx["start"]["value"] == 1
        assert range_idx["end"]["value"] == 4
        assert range_idx["inclusive"] is False

    def test_array_slice_inclusive(self):
        """Test array slice with inclusive range: arr[1..=4]"""
        code = "val slice = arr[1..=4]"
        ast = self.parser.parse(code)

        slice_expr = ast["statements"][0]["value"]
        assert slice_expr["index"]["inclusive"] is True

    def test_array_slice_from(self):
        """Test array slice from index: arr[2..]"""
        code = "val slice = arr[2..]"
        ast = self.parser.parse(code)

        range_idx = ast["statements"][0]["value"]["index"]
        assert range_idx["start"]["value"] == 2
        assert range_idx["end"] is None

    def test_array_slice_to(self):
        """Test array slice to index: arr[..5]"""
        code = "val slice = arr[..5]"
        ast = self.parser.parse(code)

        range_idx = ast["statements"][0]["value"]["index"]
        assert range_idx["start"] is None
        assert range_idx["end"]["value"] == 5

    def test_array_slice_full(self):
        """Test full array slice: arr[..] (unified range model!)"""
        code = "val copy = arr[..]"
        ast = self.parser.parse(code)

        access_expr = ast["statements"][0]["value"]
        assert access_expr["type"] == NodeType.ARRAY_ACCESS.value

        range_idx = access_expr["index"]
        assert range_idx["type"] == NodeType.RANGE_EXPR.value
        assert range_idx["start"] is None
        assert range_idx["end"] is None

    def test_array_slice_with_step(self):
        """Test array slice with step: arr[0..10:2]"""
        code = "val evens = arr[0..10:2]"
        ast = self.parser.parse(code)

        range_idx = ast["statements"][0]["value"]["index"]
        assert range_idx["step"]["value"] == 2

    def test_array_reverse_slice(self):
        """Test reverse array slice: arr[9..0:-1]"""
        code = "val reversed = arr[9..0:-1]"
        ast = self.parser.parse(code)

        range_idx = ast["statements"][0]["value"]["index"]
        assert range_idx["start"]["value"] == 9
        assert range_idx["end"]["value"] == 0

        # -1 is parsed as unary operation
        step = range_idx["step"]
        assert step["type"] == NodeType.UNARY_OPERATION.value
        assert step["operator"] == "-"
        assert step["operand"]["value"] == 1


class TestRangeExpressionContext:
    """Test range expressions in various contexts."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_range_in_variable_declaration(self):
        """Test range as variable initializer"""
        code = "val r : range[i32] = 1..100"
        ast = self.parser.parse(code)

        assert ast["statements"][0]["value"]["type"] == NodeType.RANGE_EXPR.value

    def test_range_with_variable_bounds(self):
        """Test range with variable bounds: start..end"""
        code = """
        val start = 5
        val end = 10
        val r = start..end
        """
        ast = self.parser.parse(code)

        range_expr = ast["statements"][2]["value"]
        assert range_expr["start"]["type"] == NodeType.IDENTIFIER.value
        assert range_expr["start"]["name"] == "start"
        assert range_expr["end"]["type"] == NodeType.IDENTIFIER.value
        assert range_expr["end"]["name"] == "end"

    def test_range_with_expression_bounds(self):
        """Test range with expression bounds: (x+1)..(y*2)"""
        code = "val r = (x + 1)..(y * 2)"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["start"]["type"] == NodeType.BINARY_OPERATION.value
        assert range_expr["end"]["type"] == NodeType.BINARY_OPERATION.value

    def test_range_as_function_argument(self):
        """Test range as function call argument"""
        code = """
        func process(r : range[i32]) : void = {
            return
        }
        val result = process(1..10)
        """
        ast = self.parser.parse(code)

        call_expr = ast["statements"][0]["value"]
        arg = call_expr["arguments"][0]
        assert arg["type"] == NodeType.RANGE_EXPR.value


class TestComplexRangeSyntax:
    """Test complex range syntax combinations."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_nested_array_range_indexing(self):
        """Test range indexing on multidimensional arrays: matrix[0][1..3]"""
        code = "val row_slice = matrix[0][1..3]"
        ast = self.parser.parse(code)

        # Outer access: matrix[0][...]
        outer = ast["statements"][0]["value"]
        assert outer["type"] == NodeType.ARRAY_ACCESS.value

        # Inner access: matrix[0]
        inner = outer["array"]
        assert inner["type"] == NodeType.ARRAY_ACCESS.value
        assert inner["index"]["value"] == 0

        # Range index: [1..3]
        range_idx = outer["index"]
        assert range_idx["type"] == NodeType.RANGE_EXPR.value
        assert range_idx["start"]["value"] == 1
        assert range_idx["end"]["value"] == 3

    def test_range_in_return_statement(self):
        """Test range in function return"""
        code = """
        func get_range() : range[i32] = {
            return 1..10
        }
        """
        ast = self.parser.parse(code)

        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]
        range_expr = return_stmt["value"]

        assert range_expr["type"] == NodeType.RANGE_EXPR.value


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_empty_range(self):
        """Test empty range: 5..5"""
        code = "val empty = 5..5"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["start"]["value"] == 5
        assert range_expr["end"]["value"] == 5

    def test_reversed_range(self):
        """Test reversed range (semantic error, but should parse): 10..1"""
        code = "val reversed = 10..1"
        ast = self.parser.parse(code)

        # Parser allows this, semantic analyzer will validate
        range_expr = ast["statements"][0]["value"]
        assert range_expr["start"]["value"] == 10
        assert range_expr["end"]["value"] == 1

    def test_large_range_values(self):
        """Test ranges with large literal values"""
        code = "val large = 0..1000000"
        ast = self.parser.parse(code)

        range_expr = ast["statements"][0]["value"]
        assert range_expr["end"]["value"] == 1000000

    def test_zero_step(self):
        """Test zero step (semantic error, but should parse): 1..10:0"""
        code = "val zero_step = 1..10:0"
        ast = self.parser.parse(code)

        # Parser allows this, semantic analyzer will reject
        range_expr = ast["statements"][0]["value"]
        assert range_expr["step"]["value"] == 0
