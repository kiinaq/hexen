"""
Test Category 5: Array Indexing Validation

Tests range-based array indexing:
- Valid indexing with usize ranges
- Comptime int range indexing (adapts to usize)
- User type range errors
- Float range indexing errors
- Explicit conversion syntax
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType


class TestRangeIndexing(StandardTestBase):
    """Test range-based array indexing validation"""

    def test_usize_range_indexing(self):
        """usize range can index arrays"""
        code = """
        val arr : [_]i32 = [10, 20, 30, 40, 50]
        val idx : range[usize] = 1..4
        val slice : [_]i32 = arr[idx]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        slice_symbol = self.analyzer.symbol_table.lookup_symbol("slice")
        # Result should be i32 array
        assert str(slice_symbol.type.element_type) == "i32"

    def test_comptime_range_indexing_adapts_to_usize(self):
        """Comptime range adapts to usize for indexing"""
        code = """
        val arr : [_]i32 = [10, 20, 30, 40, 50]
        val slice : [_]i32 = arr[1..4]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # 1..4 should adapt to range[usize]
        assert len(self.analyzer.errors) == 0

        slice_symbol = self.analyzer.symbol_table.lookup_symbol("slice")
        assert str(slice_symbol.type.element_type) == "i32"

    def test_unbounded_from_range_indexing(self):
        """Unbounded from range works for indexing: arr[5..]"""
        code = """
        val arr : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8]
        val slice : [_]i32 = arr[5..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_unbounded_to_range_indexing(self):
        """Unbounded to range works for indexing: arr[..3]"""
        code = """
        val arr : [_]i32 = [1, 2, 3, 4, 5]
        val slice : [_]i32 = arr[..3]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_full_unbounded_range_indexing(self):
        """Full unbounded range works for indexing (array copy): arr[..]"""
        code = """
        val arr : [_]i32 = [1, 2, 3, 4, 5]
        val copy : [_]i32 = arr[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        copy_symbol = self.analyzer.symbol_table.lookup_symbol("copy")
        assert str(copy_symbol.type.element_type) == "i32"

    def test_range_with_step_indexing(self):
        """Range with step can index arrays"""
        code = """
        val arr : [_]i32 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        val slice : [_]i32 = arr[0..10:2]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_user_type_range_indexing_error_i32(self):
        """User type range[i32] cannot index without conversion"""
        code = """
        val arr : [_]i32 = [10, 20, 30, 40, 50]
        val r : range[i32] = 1..4
        val slice : [_]i32 = arr[r]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: range[i32] not valid for indexing
        assert len(self.analyzer.errors) > 0
        assert any("usize" in err.lower() and "i32" in err.lower()
                   for err in self.analyzer.errors)

    def test_user_type_range_indexing_error_i64(self):
        """User type range[i64] cannot index without conversion"""
        code = """
        val arr : [_]f64 = [1.1, 2.2, 3.3]
        val r : range[i64] = 0..2
        val slice : [_]f64 = arr[r]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("usize" in err.lower() for err in self.analyzer.errors)

    def test_float_range_indexing_error_f32(self):
        """Float range cannot index arrays: f32"""
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

    def test_float_range_indexing_error_f64(self):
        """Float range cannot index arrays: f64"""
        code = """
        val arr : [_]string = ["a", "b", "c"]
        val r : range[f64] = 0.0..2.0:0.5
        val slice : [_]string = arr[r]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() for err in self.analyzer.errors)

    def test_explicit_conversion_to_usize_for_indexing(self):
        """Explicit conversion allows user range to index"""
        code = """
        val arr : [_]i32 = [10, 20, 30, 40, 50]
        val r_i32 : range[i32] = 1..4
        val r_usize : range[usize] = r_i32:range[usize]
        val slice : [_]i32 = arr[r_usize]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed with explicit conversion
        assert len(self.analyzer.errors) == 0

    def test_multidimensional_array_range_indexing(self):
        """Range indexing on multidimensional arrays"""
        code = """
        val matrix : [_][_]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        val rows : [_][_]i32 = matrix[0..2]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_range_indexing_preserves_element_type(self):
        """Range indexing preserves array element type"""
        code = """
        val floats : [_]f64 = [1.1, 2.2, 3.3, 4.4, 5.5]
        val slice : [_]f64 = floats[1..4]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        slice_symbol = self.analyzer.symbol_table.lookup_symbol("slice")
        assert str(slice_symbol.type.element_type) == "f64"

    def test_inline_range_literal_indexing(self):
        """Inline range literal for indexing"""
        code = """
        val numbers : [_]i32 = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        val subset : [_]i32 = numbers[2..8:2]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_zero_based_range_indexing(self):
        """Zero-based range indexing"""
        code = """
        val arr : [_]i32 = [100, 200, 300]
        val slice : [_]i32 = arr[0..2]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0
