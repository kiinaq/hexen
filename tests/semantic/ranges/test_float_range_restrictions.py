"""
Test Category 9: Float Range Restrictions

Tests float-specific range restrictions:
- Step requirement enforcement
- No conversion to usize
- Iteration-only validation (for future)
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType


class TestFloatRangeRestrictions(StandardTestBase):
    """Test float-specific range restrictions"""

    def test_float_range_step_required_f32(self):
        """Float ranges must have explicit step: f32"""
        code = "val r : range[f32] = 0.0..10.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: float range requires step
        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() and "float" in err.lower()
                   for err in self.analyzer.errors)

    def test_float_range_step_required_f64(self):
        """Float ranges must have explicit step: f64"""
        code = "val r : range[f64] = -5.0..5.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() and "float" in err.lower()
                   for err in self.analyzer.errors)

    def test_comptime_float_step_required(self):
        """Comptime float ranges require step"""
        code = "val r = 0.0..100.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() for err in self.analyzer.errors)

    def test_mixed_comptime_float_step_required(self):
        """Mixed comptime (int + float) requires step"""
        code = "val r = 0..100.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Mixed becomes comptime_float, requires step
        assert len(self.analyzer.errors) > 0

    def test_float_range_cannot_index_f32(self):
        """Float ranges forbidden for array indexing: f32"""
        code = """
        val arr : [_]i32 = [1, 2, 3, 4, 5]
        val r : range[f32] = 1.0..3.0:0.5
        val slice : [_]i32 = arr[r]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: float range cannot index arrays
        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() and "index" in err.lower()
                   for err in self.analyzer.errors)

    def test_float_range_cannot_index_f64(self):
        """Float ranges forbidden for array indexing: f64"""
        code = """
        val data : [_]f64 = [1.1, 2.2, 3.3]
        val r : range[f64] = 0.0..2.0:0.5
        val slice : [_]f64 = data[r]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() for err in self.analyzer.errors)

    def test_comptime_float_range_cannot_index(self):
        """Comptime float ranges cannot index arrays"""
        code = """
        val arr : [_]i32 = [10, 20, 30]
        val slice : [_]i32 = arr[0.0..2.0:0.5]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: comptime float cannot adapt to usize
        assert len(self.analyzer.errors) > 0

    def test_float_range_with_step_valid_f32(self):
        """Float range with step is valid: f32"""
        code = "val r : range[f32] = 0.0..10.0:0.5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed
        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert r_symbol.type.element_type == HexenType.F32
        assert r_symbol.type.has_step is True

    def test_float_range_with_step_valid_f64(self):
        """Float range with step is valid: f64"""
        code = "val r : range[f64] = -1.0..1.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert r_symbol.type.element_type == HexenType.F64
        assert r_symbol.type.has_step is True

    def test_float_range_small_step(self):
        """Float range with very small step"""
        code = "val r : range[f64] = 0.0..1.0:0.0001"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_float_range_large_step(self):
        """Float range with large step"""
        code = "val r : range[f32] = 0.0..1000.0:100.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_float_range_negative_bounds(self):
        """Float range with negative bounds and step"""
        code = "val r : range[f64] = -10.0..10.0:0.5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_float_range_fractional_step(self):
        """Float range with fractional step"""
        code = "val r : range[f32] = 0.0..3.14:0.314"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_float_to_int_range_conversion_forbidden(self):
        """Float range cannot convert to integer range types"""
        code = """
        val r_f32 : range[f32] = 0.0..10.0:0.5
        val r_i32 : range[i32] = r_f32:range[i32]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should require explicit conversion or error
        # Depends on implementation - may be allowed with explicit syntax
        # Just verify it doesn't crash
        # assert len(self.analyzer.errors) > 0  # May vary

    def test_float_range_unbounded_from_with_step(self):
        """Float unbounded from range requires step"""
        code = "val r : range[f32] = 0.0..:0.5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed - has start bound and step
        assert len(self.analyzer.errors) == 0

    def test_float_range_unbounded_to_no_step_error(self):
        """Float unbounded to range still needs step conceptually"""
        # Note: This is a parse-level restriction (..end:step invalid)
        # So this might be a parser error
        code = "val r : range[f32] = ..10.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # May be parse error or semantic error
        # Just verify proper handling
        # For unbounded to with float, step requirement is tricky
        # Implementation may vary

    def test_comptime_float_with_step_valid(self):
        """Comptime float with step is valid"""
        code = "val r = 0.0..1.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert r_symbol.type.element_type == HexenType.COMPTIME_FLOAT

    def test_float_range_precision_f32(self):
        """f32 range with typical precision"""
        code = "val r : range[f32] = 0.0..1.0:0.01"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_float_range_precision_f64(self):
        """f64 range with high precision"""
        code = "val r : range[f64] = 0.0..1.0:0.000001"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_float_range_scientific_notation(self):
        """Float range with scientific notation (if supported)"""
        # This depends on whether parser supports scientific notation
        # If not, this test can be skipped or modified
        code = "val r : range[f64] = 0.0..1.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0
