"""
Test Category 7: usize Type

Tests platform index type semantics:
- Variable declarations
- Function parameters
- Conversion from comptime_int (implicit)
- Conversion from i32/i64 (explicit)
- Conversion from float (forbidden)
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType


class TestUsizeType(StandardTestBase):
    """Test platform index type semantics"""

    def test_usize_variable_declaration_with_comptime(self):
        """usize variable with comptime_int (implicit adaptation)"""
        code = "val idx : usize = 42"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed (comptime_int → usize implicit)
        assert len(self.analyzer.errors) == 0

        idx_symbol = self.analyzer.symbol_table.lookup_symbol("idx")
        assert idx_symbol.type == HexenType.USIZE

    def test_usize_variable_declaration_zero(self):
        """usize variable with zero"""
        code = "val idx : usize = 0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        idx_symbol = self.analyzer.symbol_table.lookup_symbol("idx")
        assert idx_symbol.type == HexenType.USIZE

    def test_usize_variable_large_value(self):
        """usize variable with large comptime value"""
        code = "val idx : usize = 1000000"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        idx_symbol = self.analyzer.symbol_table.lookup_symbol("idx")
        assert idx_symbol.type == HexenType.USIZE

    def test_i32_to_usize_requires_conversion(self):
        """i32 → usize requires explicit conversion"""
        code = """
        val i : i32 = 10
        val idx : usize = i:usize
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed (explicit conversion)
        assert len(self.analyzer.errors) == 0

        idx_symbol = self.analyzer.symbol_table.lookup_symbol("idx")
        assert idx_symbol.type == HexenType.USIZE

    def test_i64_to_usize_requires_conversion(self):
        """i64 → usize requires explicit conversion"""
        code = """
        val i : i64 = 100
        val idx : usize = i:usize
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        idx_symbol = self.analyzer.symbol_table.lookup_symbol("idx")
        assert idx_symbol.type == HexenType.USIZE

    def test_i32_to_usize_implicit_error(self):
        """i32 → usize implicit conversion not allowed"""
        code = """
        val i : i32 = 10
        val idx : usize = i
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: requires explicit conversion
        assert len(self.analyzer.errors) > 0

    def test_float_to_usize_forbidden_f32(self):
        """f32 → usize conversion forbidden"""
        code = """
        val f : f32 = 2.5
        val idx : usize = f:usize
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: float cannot convert to usize
        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() or "f32" in err.lower()
                   for err in self.analyzer.errors)

    def test_float_to_usize_forbidden_f64(self):
        """f64 → usize conversion forbidden"""
        code = """
        val f : f64 = 10.0
        val idx : usize = f:usize
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("float" in err.lower() or "f64" in err.lower()
                   for err in self.analyzer.errors)

    def test_comptime_float_to_usize_forbidden(self):
        """comptime_float → usize forbidden"""
        code = """
        val idx : usize = 5.5
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: float literal cannot adapt to usize
        assert len(self.analyzer.errors) > 0

    def test_usize_function_parameter(self):
        """usize as function parameter"""
        code = """
        func get_element(index: usize) : i32 = {
            return 0
        }
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_usize_function_return(self):
        """usize as function return type"""
        code = """
        func get_index() : usize = {
            return 42
        }
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # 42 adapts to usize in return context
        assert len(self.analyzer.errors) == 0

    def test_usize_to_i32_conversion(self):
        """usize → i32 explicit conversion"""
        code = """
        val idx : usize = 100
        val i : i32 = idx:i32
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed (explicit conversion)
        assert len(self.analyzer.errors) == 0

    def test_usize_to_i64_conversion(self):
        """usize → i64 explicit conversion"""
        code = """
        val idx : usize = 1000
        val i : i64 = idx:i64
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_usize_to_float_conversion_f32(self):
        """usize → f32 explicit conversion"""
        code = """
        val idx : usize = 50
        val f : f32 = idx:f32
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_usize_to_float_conversion_f64(self):
        """usize → f64 explicit conversion"""
        code = """
        val idx : usize = 100
        val f : f64 = idx:f64
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_usize_arithmetic_same_type(self):
        """usize arithmetic with same type"""
        code = """
        val a : usize = 10
        val b : usize = 5
        val sum : usize = a + b
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_usize_comparison(self):
        """usize comparison operations"""
        code = """
        val a : usize = 10
        val b : usize = 5
        val is_greater : bool = a > b
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_mut_usize_variable(self):
        """Mutable usize variable"""
        code = """
        mut idx : usize = 0
        idx = 10
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

    def test_usize_in_array_indexing(self):
        """usize for single element array indexing"""
        code = """
        val arr : [_]i32 = [10, 20, 30]
        val idx : usize = 1
        val elem : i32 = arr[idx]
        """
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0
