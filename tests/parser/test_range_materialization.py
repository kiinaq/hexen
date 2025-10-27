"""
Parser tests for range materialization syntax.

Tests that [range_expr] parses correctly as ARRAY_LITERAL,
and is distinguished from array access with range index.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestRangeMaterializationParsing:
    """Test that range materialization syntax parses correctly."""

    @pytest.fixture
    def parser(self):
        return HexenParser()

    def test_basic_range_materialization(self, parser):
        """Test [1..10] parses as array_literal with range element."""
        code = "val arr : [_]i32 = [1..10]"
        ast = parser.parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == NodeType.ARRAY_LITERAL.value
        assert len(value["elements"]) == 1
        assert value["elements"][0]["type"] == NodeType.RANGE_EXPR.value

    def test_inclusive_range_materialization(self, parser):
        """Test [1..=10] parses as array_literal with inclusive range."""
        code = "val arr : [_]i32 = [1..=10]"
        ast = parser.parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == NodeType.ARRAY_LITERAL.value
        assert len(value["elements"]) == 1

        range_elem = value["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value
        assert range_elem["inclusive"] is True

    def test_range_with_step_materialization(self, parser):
        """Test [0..100:10] parses correctly."""
        code = "val arr : [_]i32 = [0..100:10]"
        ast = parser.parse(code)

        range_elem = ast["statements"][0]["value"]["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value
        assert range_elem["step"] is not None

    def test_float_range_materialization(self, parser):
        """Test [0.0..1.0:0.1] parses correctly."""
        code = "val arr : [_]f32 = [0.0..1.0:0.1]"
        ast = parser.parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == NodeType.ARRAY_LITERAL.value

        range_elem = value["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value

    def test_distinguishes_array_access_from_materialization(self, parser):
        """Ensure source[1..10] is array_access, not array_literal."""
        code = "val slice : [_]i32 = source[1..10]"
        ast = parser.parse(code)

        value = ast["statements"][0]["value"]
        # This should be ARRAY_ACCESS, not ARRAY_LITERAL!
        assert value["type"] == NodeType.ARRAY_ACCESS.value
        assert value["index"]["type"] == NodeType.RANGE_EXPR.value

    def test_nested_range_materialization_syntax(self, parser):
        """Test [[1..5], [10..15]] parses (will be semantic error later)."""
        code = "val arr = [[1..5], [10..15]]"
        ast = parser.parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == NodeType.ARRAY_LITERAL.value
        assert len(value["elements"]) == 2

        # Each element should be an array literal containing a range
        assert value["elements"][0]["type"] == NodeType.ARRAY_LITERAL.value
        assert value["elements"][1]["type"] == NodeType.ARRAY_LITERAL.value

    def test_range_bounds_captured_correctly(self, parser):
        """Test that range bounds are properly captured in AST."""
        code = "val arr : [_]i32 = [5..15]"
        ast = parser.parse(code)

        range_elem = ast["statements"][0]["value"]["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value
        assert range_elem["start"] is not None  # Bounded range has start
        assert range_elem["end"] is not None    # Bounded range has end
        assert range_elem["inclusive"] is False

    def test_unbounded_range_from_syntax(self, parser):
        """Test [5..] parses (will be semantic error later)."""
        code = "val arr : [_]i32 = [5..]"
        ast = parser.parse(code)

        range_elem = ast["statements"][0]["value"]["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value
        # Range "from" has start but no end
        assert range_elem["start"] is not None
        assert range_elem["end"] is None

    def test_unbounded_range_to_syntax(self, parser):
        """Test [..10] parses (will be semantic error later)."""
        code = "val arr : [_]i32 = [..10]"
        ast = parser.parse(code)

        range_elem = ast["statements"][0]["value"]["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value
        # Range "to" has end but no start
        assert range_elem["start"] is None
        assert range_elem["end"] is not None

    def test_unbounded_range_full_syntax(self, parser):
        """Test [..] parses (will be semantic error later)."""
        code = "val arr : [_]i32 = [..]"
        ast = parser.parse(code)

        range_elem = ast["statements"][0]["value"]["elements"][0]
        assert range_elem["type"] == NodeType.RANGE_EXPR.value
        # Range "full" has neither start nor end
        assert range_elem["start"] is None
        assert range_elem["end"] is None

    def test_mixed_array_literal_syntax(self, parser):
        """Test [1..5, 10, 20] parses (will be semantic error later)."""
        code = "val arr : [_]i32 = [1..5, 10, 20]"
        ast = parser.parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == NodeType.ARRAY_LITERAL.value
        assert len(value["elements"]) == 3

        # First element is range
        assert value["elements"][0]["type"] == NodeType.RANGE_EXPR.value
        # Other elements are literals (comptime_int)
        assert value["elements"][1]["type"] == NodeType.COMPTIME_INT.value
        assert value["elements"][2]["type"] == NodeType.COMPTIME_INT.value
