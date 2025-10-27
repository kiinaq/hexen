"""
Test Category 2: Range Bound Type Consistency

Tests range bound type consistency rules:
- Same concrete types allowed
- Mixed concrete types rejected
- Comptime + concrete adaptation
- Mixed comptime types resolution
- Step type matching with bounds
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType, RangeType, ComptimeRangeType


class TestRangeBoundConsistency(StandardTestBase):
    """Test range bound type consistency rules"""

    def test_same_concrete_bounds_i32(self):
        """Same concrete types allowed: i32..i32"""
        code = """
        val start : i32 = 5
        val end : i32 = 10
        val r : range[i32] = start..end
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32

    def test_same_concrete_bounds_i64(self):
        """Same concrete types allowed: i64..i64"""
        code = """
        val start : i64 = 100
        val end : i64 = 200
        val r : range[i64] = start..end
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I64

    def test_same_concrete_bounds_f32(self):
        """Same concrete types allowed: f32..f32 with step"""
        code = """
        val start : f32 = 0.0
        val end : f32 = 10.0
        val step : f32 = 0.5
        val r : range[f32] = start..end:step
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F32

    def test_mixed_concrete_bounds_error(self):
        """Mixed concrete types rejected: i32..i64"""
        code = """
        val start : i32 = 5
        val end : i64 = 10
        val r = start..end
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should have type mismatch error
        assert len(self.analyzer.errors) > 0
        assert any("incompatible" in err.lower() or "mismatch" in err.lower()
                   for err in self.analyzer.errors)

    def test_mixed_i32_f32_error(self):
        """Mixed concrete types rejected: i32..f32"""
        code = """
        val start : i32 = 0
        val end : f32 = 10.0
        val r = start..end
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("incompatible" in err.lower() or "mismatch" in err.lower()
                   for err in self.analyzer.errors)

    def test_comptime_adapts_to_concrete_i32(self):
        """Comptime bounds adapt to concrete type: i32..comptime"""
        code = """
        val start : i32 = 5
        val r : range[i32] = start..10
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # 10 should adapt to i32
        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32

    def test_comptime_adapts_to_concrete_f64(self):
        """Comptime bounds adapt to concrete type: comptime..f64 with step"""
        code = """
        val end : f64 = 100.0
        val step : f64 = 0.1
        val r : range[f64] = 0.0..end:step
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F64

    def test_both_comptime_bounds(self):
        """Both comptime bounds preserve flexibility"""
        code = """
        val r = 1..100
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT

    def test_mixed_comptime_int_float_becomes_float(self):
        """Mixed comptime_int + comptime_float → comptime_float"""
        code = """
        val r = 42..3.14:0.1
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        # Mixed comptime should promote to float
        assert r_symbol.type.element_type == HexenType.COMPTIME_FLOAT

    def test_step_type_matches_bounds_i32(self):
        """Step type must match bound types: i32"""
        code = """
        val start : i32 = 0
        val end : i32 = 100
        val step : i32 = 5
        val r : range[i32] = start..end:step
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32
        assert r_symbol.type.has_step is True

    def test_step_type_mismatch_error(self):
        """Step type mismatch causes error"""
        code = """
        val start : i32 = 0
        val end : i32 = 100
        val step : i64 = 5
        val r = start..end:step
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should have type mismatch error
        assert len(self.analyzer.errors) > 0

    def test_comptime_step_adapts(self):
        """Comptime step adapts to concrete bounds"""
        code = """
        val start : i32 = 0
        val end : i32 = 100
        val r : range[i32] = start..end:5
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Comptime 5 should adapt to i32
        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32

    def test_all_comptime_with_step(self):
        """All comptime (start, end, step) preserves flexibility"""
        code = """
        val r = 0..100:10
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT

    def test_usize_bounds_consistent(self):
        """usize bounds work consistently"""
        code = """
        val start : usize = 0
        val end : usize = 10
        val r : range[usize] = start..end
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE

    def test_expression_bounds_same_type(self):
        """Expression bounds with same result type"""
        code = """
        val base : i32 = 10
        val r : range[i32] = (base * 2)..(base * 10)
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32
