"""
Test Category 8: Range Type Conversions

Tests range type conversions:
- User type → index type (range[i32]:range[usize])
- Comptime → concrete (implicit adaptation)
- Float → usize (forbidden)
- Explicit conversion syntax
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType


class TestRangeConversions(StandardTestBase):
    """Test range type conversions"""

    def test_user_range_to_index_range_i32_to_usize(self):
        """User type range can convert to index type: i32 → usize"""
        code = """
        val r_i32 : range[i32] = 1..10
        val r_usize : range[usize] = r_i32:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed (explicit conversion)
        assert len(self.analyzer.errors) == 0

        r_usize = self.analyzer.symbol_table.lookup_symbol("r_usize")
        assert r_usize.type.element_type == HexenType.USIZE

    def test_user_range_to_index_range_i64_to_usize(self):
        """User type range can convert to index type: i64 → usize"""
        code = """
        val r_i64 : range[i64] = 0..1000
        val r_usize : range[usize] = r_i64:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_usize = self.analyzer.symbol_table.lookup_symbol("r_usize")
        assert r_usize.type.element_type == HexenType.USIZE

    def test_index_range_to_user_range_usize_to_i32(self):
        """Index type range can convert to user type: usize → i32"""
        code = """
        val r_usize : range[usize] = 1..10
        val r_i32 : range[i32] = r_usize:range[i32]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_i32 = self.analyzer.symbol_table.lookup_symbol("r_i32")
        assert r_i32.type.element_type == HexenType.I32

    def test_index_range_to_user_range_usize_to_i64(self):
        """Index type range can convert to user type: usize → i64"""
        code = """
        val r_usize : range[usize] = 0..100
        val r_i64 : range[i64] = r_usize:range[i64]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_i64 = self.analyzer.symbol_table.lookup_symbol("r_i64")
        assert r_i64.type.element_type == HexenType.I64

    def test_float_range_to_usize_forbidden_f32(self):
        """Float range cannot convert to usize: f32"""
        code = """
        val r_f32 : range[f32] = 1.0..10.0:0.1
        val r_usize : range[usize] = r_f32:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: float range cannot convert to usize
        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() and "usize" in err.lower()
                   for err in self.analyzer.errors)

    def test_float_range_to_usize_forbidden_f64(self):
        """Float range cannot convert to usize: f64"""
        code = """
        val r_f64 : range[f64] = 0.0..100.0:1.0
        val r_usize : range[usize] = r_f64:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() and "usize" in err.lower()
                   for err in self.analyzer.errors)

    def test_range_i32_to_i64_conversion(self):
        """Range type conversion: i32 → i64"""
        code = """
        val r_i32 : range[i32] = 1..10
        val r_i64 : range[i64] = r_i32:range[i64]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_i64 = self.analyzer.symbol_table.lookup_symbol("r_i64")
        assert r_i64.type.element_type == HexenType.I64

    def test_range_i64_to_i32_conversion(self):
        """Range type conversion: i64 → i32"""
        code = """
        val r_i64 : range[i64] = 0..50
        val r_i32 : range[i32] = r_i64:range[i32]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_i32 = self.analyzer.symbol_table.lookup_symbol("r_i32")
        assert r_i32.type.element_type == HexenType.I32

    def test_range_f32_to_f64_conversion(self):
        """Range type conversion: f32 → f64"""
        code = """
        val r_f32 : range[f32] = 0.0..10.0:0.1
        val r_f64 : range[f64] = r_f32:range[f64]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_f64 = self.analyzer.symbol_table.lookup_symbol("r_f64")
        assert r_f64.type.element_type == HexenType.F64

    def test_range_f64_to_f32_conversion(self):
        """Range type conversion: f64 → f32"""
        code = """
        val r_f64 : range[f64] = 1.0..5.0:0.5
        val r_f32 : range[f32] = r_f64:range[f32]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_f32 = self.analyzer.symbol_table.lookup_symbol("r_f32")
        assert r_f32.type.element_type == HexenType.F32

    def test_comptime_implicit_adaptation_no_conversion(self):
        """Comptime range adapts implicitly (no explicit conversion needed)"""
        code = """
        val flexible = 1..10
        val as_i32 : range[i32] = flexible
        val as_i64 : range[i64] = flexible
        val as_usize : range[usize] = flexible
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # All should succeed without explicit conversion
        assert len(self.analyzer.errors) == 0

    def test_explicit_conversion_preserves_bounds(self):
        """Explicit conversion preserves range bounds"""
        code = """
        val r_i32 : range[i32] = 10..20
        val r_usize : range[usize] = r_i32:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_usize = self.analyzer.symbol_table.lookup_symbol("r_usize")
        assert r_usize.type.has_start is True
        assert r_usize.type.has_end is True

    def test_explicit_conversion_preserves_step(self):
        """Explicit conversion preserves step information"""
        code = """
        val r_i32 : range[i32] = 0..100:10
        val r_usize : range[usize] = r_i32:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_usize = self.analyzer.symbol_table.lookup_symbol("r_usize")
        assert r_usize.type.has_step is True

    def test_explicit_conversion_preserves_inclusive(self):
        """Explicit conversion preserves inclusive flag"""
        code = """
        val r_i32 : range[i32] = 1..=10
        val r_i64 : range[i64] = r_i32:range[i64]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_i64 = self.analyzer.symbol_table.lookup_symbol("r_i64")
        assert r_i64.type.inclusive is True

    def test_unbounded_range_conversion(self):
        """Unbounded ranges can be converted"""
        code = """
        val r_i32 : range[i32] = 5..
        val r_usize : range[usize] = r_i32:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_usize = self.analyzer.symbol_table.lookup_symbol("r_usize")
        assert r_usize.type.element_type == HexenType.USIZE
        assert r_usize.type.has_start is True
        assert r_usize.type.has_end is False

    def test_full_unbounded_range_conversion(self):
        """Full unbounded ranges can be converted"""
        code = """
        val r_i32 : range[i32] = ..
        val r_usize : range[usize] = r_i32:range[usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_usize = self.analyzer.symbol_table.lookup_symbol("r_usize")
        assert r_usize.type.element_type == HexenType.USIZE
