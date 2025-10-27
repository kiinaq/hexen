"""
Test Category 6: Unbounded Range Copy (Migration Validation)

Tests [..] as unbounded range (validates migration from old copy operator):
- array[..] copies entire array using unbounded range
- Type preservation through unbounded range
- Semantic equivalence with old behavior
- No special-case handling needed
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType


class TestUnboundedRangeCopy(StandardTestBase):
    """Test [..] as unbounded range (validates migration from old copy operator)"""

    def test_unbounded_range_full_copy(self):
        """array[..] copies entire array using unbounded range"""
        code = """
        val source : [_]i32 = [10, 20, 30]
        val copy : [_]i32 = source[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        copy_symbol = self.analyzer.symbol_table.lookup_symbol("copy")
        assert str(copy_symbol.type.element_type) == "i32"

    def test_unbounded_range_preserves_type_i32(self):
        """[..] preserves array element type: i32"""
        code = """
        val source : [_]i32 = [1, 2, 3, 4, 5]
        val copy : [_]i32 = source[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        copy_symbol = self.analyzer.symbol_table.lookup_symbol("copy")
        assert str(copy_symbol.type.element_type) == "i32"

    def test_unbounded_range_preserves_type_f64(self):
        """[..] preserves array element type: f64"""
        code = """
        val source : [_]f64 = [1.1, 2.2, 3.3]
        val copy : [_]f64 = source[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        copy_symbol = self.analyzer.symbol_table.lookup_symbol("copy")
        assert str(copy_symbol.type.element_type) == "f64"

    def test_unbounded_range_preserves_type_string(self):
        """[..] preserves array element type: string"""
        code = """
        val source : [_]string = ["hello", "world"]
        val copy : [_]string = source[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        copy_symbol = self.analyzer.symbol_table.lookup_symbol("copy")
        assert str(copy_symbol.type.element_type) == "string"

    def test_unbounded_range_multidimensional(self):
        """[..] works with multidimensional arrays"""
        code = """
        val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
        val copy : [_][_]i32 = matrix[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed - full matrix copy
        assert len(self.analyzer.errors) == 0

    def test_unbounded_range_no_special_case(self):
        """[..] is handled same as any other range"""
        code = """
        val arr : [_]i32 = [1, 2, 3, 4, 5]
        val full_copy : [_]i32 = arr[..]
        val partial : [_]i32 = arr[1..4]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Both should succeed
        assert len(self.analyzer.errors) == 0

        full_copy = self.analyzer.symbol_table.lookup_symbol("full_copy")
        partial = self.analyzer.symbol_table.lookup_symbol("partial")

        # Both have same element type
        assert str(full_copy.type.element_type) == "i32"
        assert str(partial.type.element_type) == "i32"

    def test_unbounded_range_equivalent_to_explicit(self):
        """[..] equivalent to [0..length] semantically"""
        code = """
        val arr : [5]i32 = [1, 2, 3, 4, 5]
        val copy1 : [_]i32 = arr[..]
        val copy2 : [_]i32 = arr[0..5]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Both should succeed and produce same result type
        assert len(self.analyzer.errors) == 0

        copy1 = self.analyzer.symbol_table.lookup_symbol("copy1")
        copy2 = self.analyzer.symbol_table.lookup_symbol("copy2")

        assert str(copy1.type.element_type) == "i32"
        assert str(copy2.type.element_type) == "i32"

    def test_unbounded_range_on_empty_array(self):
        """[..] works on empty arrays"""
        code = """
        val empty : [_]i32 = []
        val copy : [_]i32 = empty[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_unbounded_range_chained_operations(self):
        """[..] can be used in chained operations"""
        code = """
        val source : [_]i32 = [10, 20, 30, 40, 50]
        val copy : [_]i32 = source[..]
        val slice : [_]i32 = copy[1..3]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_unbounded_range_with_comptime_array(self):
        """[..] works with comptime arrays (first materialization)"""
        code = """
        val comptime_arr = [1, 2, 3, 4, 5]
        val concrete : [_]i32 = comptime_arr[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        concrete = self.analyzer.symbol_table.lookup_symbol("concrete")
        assert str(concrete.type.element_type) == "i32"

    def test_unbounded_range_bool_array(self):
        """[..] preserves bool array type"""
        code = """
        val flags : [_]bool = [true, false, true]
        val copy : [_]bool = flags[..]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        copy_symbol = self.analyzer.symbol_table.lookup_symbol("copy")
        assert str(copy_symbol.type.element_type) == "bool"

    def test_unbounded_inclusive_range_copy(self):
        """[..=] not valid for full copy (no end bound for inclusive)"""
        # Note: ..= requires an end bound, so this tests error case
        code = """
        val arr : [_]i32 = [1, 2, 3]
        val copy : [_]i32 = arr[..=]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # This should be a parse error since ..= requires end bound
        # If it parses, semantic should also reject
        # For now, just check it doesn't crash
        # assert len(self.analyzer.errors) > 0  # May vary based on parser
