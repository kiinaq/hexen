"""
Test Category 1: Range Type Inference

Tests basic range type inference for:
- Bounded ranges (start..end)
- Unbounded from (start..)
- Unbounded to (..end)
- Full unbounded (..)
- Float ranges with step
- Inclusive vs exclusive ranges
- Explicit type annotations
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType, RangeType, ComptimeRangeType


class TestRangeTypeInference(StandardTestBase):
    """Test basic range type inference"""

    def test_bounded_integer_range(self):
        """Bounded range 1..10 infers to range[comptime_int]"""
        code = "val r = 1..10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should have no errors
        assert len(self.analyzer.errors) == 0

        # Check that r has comptime range type
        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert r_symbol is not None
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_start is True
        assert r_symbol.type.has_end is True
        assert r_symbol.type.has_step is False
        assert r_symbol.type.inclusive is False

    def test_bounded_integer_range_inclusive(self):
        """Inclusive range 1..=10 infers to range[comptime_int]"""
        code = "val r = 1..=10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.inclusive is True

    def test_unbounded_from_range(self):
        """Unbounded from 5.. infers to range[comptime_int]"""
        code = "val r = 5.."
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_start is True
        assert r_symbol.type.has_end is False
        assert r_symbol.type.has_step is False

    def test_unbounded_to_range(self):
        """Unbounded to ..10 infers to range[comptime_int]"""
        code = "val r = ..10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_start is False
        assert r_symbol.type.has_end is True
        assert r_symbol.type.has_step is False

    def test_full_unbounded_range(self):
        """Full unbounded .. infers to range[comptime_int]"""
        code = "val r = .."
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_start is False
        assert r_symbol.type.has_end is False
        assert r_symbol.type.has_step is False

    def test_float_range_with_step(self):
        """Float range 0.0..1.0:0.1 infers to range[comptime_float]"""
        code = "val r = 0.0..1.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_FLOAT
        assert r_symbol.type.has_start is True
        assert r_symbol.type.has_end is True
        assert r_symbol.type.has_step is True

    def test_integer_range_with_step(self):
        """Integer range 1..10:2 infers to range[comptime_int]"""
        code = "val r = 1..10:2"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_step is True

    def test_explicit_range_type_i32(self):
        """Explicit type: val r : range[i32] = 1..10"""
        code = "val r : range[i32] = 1..10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32
        assert not isinstance(r_symbol.type, ComptimeRangeType)

    def test_explicit_range_type_usize(self):
        """Explicit type: val r : range[usize] = 0..5"""
        code = "val r : range[usize] = 0..5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE

    def test_explicit_range_type_f64(self):
        """Explicit type: val r : range[f64] = 0.0..1.0:0.1"""
        code = "val r : range[f64] = 0.0..1.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F64

    def test_negative_bounds(self):
        """Range with negative bounds: -10..10"""
        code = "val r = -10..10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT

    def test_zero_based_range(self):
        """Zero-based range: 0..100"""
        code = "val r = 0..100"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT

    def test_single_element_range(self):
        """Single element range: 5..6"""
        code = "val r = 5..6"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)

    def test_large_range(self):
        """Large range: 0..1000000"""
        code = "val r = 0..1000000"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
