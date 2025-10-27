"""
Test Category 3: Range Step Validation

Tests step requirement enforcement:
- Float ranges require step
- Integer ranges step optional
- Unbounded to forbids step
- Full unbounded forbids step
- Step type matches bounds
"""

import pytest
from tests.semantic import StandardTestBase

from src.hexen.semantic.types import HexenType, RangeType, ComptimeRangeType


class TestRangeStepValidation(StandardTestBase):
    """Test range step requirement enforcement"""

    def test_float_range_requires_step_f32(self):
        """Float range without step is error: f32"""
        code = "val r : range[f32] = 0.0..10.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: float range requires explicit step
        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() and "float" in err.lower()
                   for err in self.analyzer.errors)

    def test_float_range_requires_step_f64(self):
        """Float range without step is error: f64"""
        code = "val r : range[f64] = 1.5..100.5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() and "float" in err.lower()
                   for err in self.analyzer.errors)

    def test_comptime_float_range_requires_step(self):
        """Comptime float range without step is error"""
        code = "val r = 0.0..10.0"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() for err in self.analyzer.errors)

    def test_float_range_with_step_ok_f32(self):
        """Float range with step is valid: f32"""
        code = "val r : range[f32] = 0.0..10.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F32
        assert r_symbol.type.has_step is True

    def test_float_range_with_step_ok_f64(self):
        """Float range with step is valid: f64"""
        code = "val r : range[f64] = -1.0..1.0:0.01"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.F64
        assert r_symbol.type.has_step is True

    def test_comptime_float_range_with_step_ok(self):
        """Comptime float range with step is valid"""
        code = "val r = 0.0..1.0:0.1"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_FLOAT
        assert r_symbol.type.has_step is True

    def test_integer_range_step_optional_i32(self):
        """Integer range step is optional: i32"""
        code = "val r : range[i32] = 1..10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should succeed without step
        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32
        assert r_symbol.type.has_step is False

    def test_integer_range_with_step_ok_i32(self):
        """Integer range with step is also valid: i32"""
        code = "val r : range[i32] = 1..10:2"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I32
        assert r_symbol.type.has_step is True

    def test_integer_range_with_step_ok_i64(self):
        """Integer range with step is valid: i64"""
        code = "val r : range[i64] = 0..1000:100"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.I64
        assert r_symbol.type.has_step is True

    def test_comptime_int_range_step_optional(self):
        """Comptime int range step is optional"""
        code = "val r = 1..100"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_step is False

    def test_comptime_int_range_with_step_ok(self):
        """Comptime int range with step is valid"""
        code = "val r = 1..100:5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.element_type == HexenType.COMPTIME_INT
        assert r_symbol.type.has_step is True

    def test_unbounded_from_with_step_ok(self):
        """Unbounded from with step is valid: start..:step"""
        code = "val r = 10..:5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # This should be OK - has start bound
        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, ComptimeRangeType)
        assert r_symbol.type.has_start is True
        assert r_symbol.type.has_end is False
        assert r_symbol.type.has_step is True

    def test_unbounded_to_forbids_step(self):
        """Unbounded to forbids step: ..end:step"""
        code = "val r = ..10:2"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: step not allowed on unbounded to
        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() and "unbounded" in err.lower()
                   for err in self.analyzer.errors)

    def test_full_unbounded_forbids_step(self):
        """Full unbounded forbids step: ..:step"""
        code = "val r = ..:5"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        # Should error: step not allowed on fully unbounded
        assert len(self.analyzer.errors) > 0
        assert any("step" in err.lower() and "unbounded" in err.lower()
                   for err in self.analyzer.errors)

    def test_unbounded_to_without_step_ok(self):
        """Unbounded to without step is valid"""
        code = "val r = ..100"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert r_symbol.type.has_start is False
        assert r_symbol.type.has_end is True
        assert r_symbol.type.has_step is False

    def test_full_unbounded_without_step_ok(self):
        """Full unbounded without step is valid"""
        code = "val r = .."
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert r_symbol.type.has_start is False
        assert r_symbol.type.has_end is False
        assert r_symbol.type.has_step is False

    def test_usize_range_step_optional(self):
        """usize range step is optional"""
        code = "val r : range[usize] = 0..10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE
        assert r_symbol.type.has_step is False

    def test_usize_range_with_step_ok(self):
        """usize range with step is valid"""
        code = "val r : range[usize] = 0..100:10"
        ast = self.parser.parse(code)
        self.analyzer.analyze(ast)

        assert len(self.analyzer.errors) == 0

        r_symbol = self.analyzer.symbol_table.lookup_symbol("r")
        assert isinstance(r_symbol.type, RangeType)
        assert r_symbol.type.element_type == HexenType.USIZE
        assert r_symbol.type.has_step is True
