"""
Test Category 4: Comptime Range Adaptation

Tests comptime range flexibility:
- comptime_int → i32, i64, f32, f64, usize
- comptime_float → f32, f64 (NOT usize)
- Same source, multiple targets
- Context-driven resolution
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType, RangeType, ComptimeRangeType


class TestComptimeRangeAdaptation(StandardTestBase):
    """Test comptime range flexibility and adaptation"""

    def test_comptime_range_adapts_to_i32(self):
        """Comptime range adapts to range[i32]"""
        code = """
        val flexible = 1..10
        val r : range[i32] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32

    def test_comptime_range_adapts_to_i64(self):
        """Comptime range adapts to range[i64]"""
        code = """
        val flexible = 0..1000
        val r : range[i64] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I64

    def test_comptime_range_adapts_to_f32(self):
        """Comptime int range adapts to range[f32]"""
        code = """
        val flexible = 1..10
        val r : range[f32] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F32

    def test_comptime_range_adapts_to_f64(self):
        """Comptime int range adapts to range[f64]"""
        code = """
        val flexible = 0..100
        val r : range[f64] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F64

    def test_comptime_range_adapts_to_usize(self):
        """Comptime int range adapts to range[usize] for indexing"""
        code = """
        val flexible = 1..10
        val r : range[usize] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE

    def test_comptime_float_adapts_to_f32(self):
        """Comptime float range adapts to range[f32]"""
        code = """
        val flexible = 0.0..1.0:0.1
        val r : range[f32] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F32

    def test_comptime_float_adapts_to_f64(self):
        """Comptime float range adapts to range[f64]"""
        code = """
        val flexible = 0.0..10.0:0.5
        val r : range[f64] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F64

    def test_comptime_float_cannot_adapt_to_usize(self):
        """Comptime float range cannot adapt to usize"""
        code = """
        val float_r = 1.0..10.0:0.1
        val r : range[usize] = float_r
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: comptime_float cannot adapt to usize
        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() and "usize" in err.lower()
                   for err in self.analyzer.errors)

    def test_comptime_float_cannot_adapt_to_i32(self):
        """Comptime float range cannot adapt to integer types"""
        code = """
        val float_r = 0.0..1.0:0.1
        val r : range[i32] = float_r
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: comptime_float requires explicit conversion to int types
        assert len(self.analyzer.errors) > 0

    def test_same_source_multiple_targets(self):
        """Same comptime range can adapt to multiple targets"""
        code = """
        val flexible = 1..100
        val as_i32 : range[i32] = flexible
        val as_i64 : range[i64] = flexible
        val as_usize : range[usize] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        # Check all adaptations worked
        as_i32 = self.analyzer.symbol_table.lookup_symbol("as_i32")
        as_i64 = self.analyzer.symbol_table.lookup_symbol("as_i64")
        as_usize = self.analyzer.symbol_table.lookup_symbol("as_usize")

        assert as_i32.type.element_type == HexenType.I32
        assert as_i64.type.element_type == HexenType.I64
        assert as_usize.type.element_type == HexenType.USIZE

    def test_inline_comptime_adaptation_i32(self):
        """Inline comptime range adapts in context"""
        code = """
        val r : range[i32] = 0..50
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32

    def test_inline_comptime_adaptation_usize(self):
        """Inline comptime range adapts to usize"""
        code = """
        val r : range[usize] = 0..10
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE

    def test_comptime_preserves_flexibility_without_annotation(self):
        """Without type annotation, comptime range stays flexible"""
        code = """
        val flexible = 1..10
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        flexible_symbol = self.analyzer.symbol_table.lookup_symbol("flexible")
        # Should still be comptime
        assert isinstance(flexible_symbol.type, ComptimeRangeType)
        assert flexible_symbol.type.element_type == HexenType.COMPTIME_INT

    def test_unbounded_comptime_range_adaptation(self):
        """Unbounded comptime range also adapts"""
        code = """
        val unbounded = 5..
        val r : range[i32] = unbounded
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32

    def test_full_unbounded_comptime_adaptation(self):
        """Full unbounded comptime range adapts"""
        code = """
        val unbounded = ..
        val r : range[usize] = unbounded
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE

    def test_comptime_range_with_step_adapts(self):
        """Comptime range with step also adapts"""
        code = """
        val flexible = 0..100:10
        val r : range[i64] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I64
        assert r_symbol.type.has_step is True
