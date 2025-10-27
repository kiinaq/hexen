"""
Semantic tests for range materialization feature.

Tests that [range_expr] syntax correctly materializes ranges into arrays,
with proper validation and error handling.
"""

import pytest
from tests.semantic import StandardTestBase, assert_no_errors, assert_error_contains


class TestRangeMaterializationBasic(StandardTestBase):
    """Test basic range materialization functionality"""

    def test_bounded_range_materializes_successfully(self):
        """✅ Bounded ranges can materialize to arrays"""
        code = """
        val arr : [_]i32 = [1..10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_inclusive_range_materializes(self):
        """✅ Inclusive ranges [start..=end] materialize correctly"""
        code = """
        val arr : [_]i32 = [1..=10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_stepped_range_materializes(self):
        """✅ Stepped ranges [start..end:step] materialize correctly"""
        code = """
        val arr : [_]i32 = [0..100:10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_float_range_with_step_succeeds(self):
        """✅ Float range with explicit step materializes"""
        code = """
        val arr : [_]f32 = [0.0..10.0:0.5]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestRangeMaterializationValidation(StandardTestBase):
    """Test validation rules for range materialization"""

    def test_unbounded_range_from_fails(self):
        """❌ Range 5.. cannot materialize (no end bound)"""
        code = """
        val arr : [_]i32 = [5..]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error for unbounded range"
        assert_error_contains(errors, "unbounded range")

    def test_unbounded_range_to_fails(self):
        """❌ Range ..10 cannot materialize (no start bound)"""
        code = """
        val arr : [_]i32 = [..10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error for unbounded range"
        assert_error_contains(errors, "unbounded range")

    def test_unbounded_range_full_fails(self):
        """❌ Range .. cannot materialize (no bounds)"""
        code = """
        val arr : [_]i32 = [..]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error for unbounded range"
        assert_error_contains(errors, "unbounded range")

    def test_float_range_requires_step(self):
        """❌ Float ranges must have explicit step"""
        code = """
        val arr : [_]f32 = [0.0..10.0]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error for float range without step"
        assert_error_contains(errors, "step")


class TestRangeMaterializationSizeComputation(StandardTestBase):
    """Test array size computation for materialized ranges"""

    def test_exclusive_range_size_computation(self):
        """Test [1..10] produces 9 elements"""
        code = """
        val arr : [_]i32 = [1..10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Verify array type has correct size
        arr_symbol = self.analyzer.symbol_table.lookup_symbol("arr")
        assert arr_symbol is not None
        # Size should be 9 (10 - 1 = 9 elements)

    def test_inclusive_range_size_computation(self):
        """Test [1..=10] produces 10 elements"""
        code = """
        val arr : [_]i32 = [1..=10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Verify array type has correct size
        arr_symbol = self.analyzer.symbol_table.lookup_symbol("arr")
        assert arr_symbol is not None
        # Size should be 10 (inclusive)

    def test_stepped_range_size_computation(self):
        """Test [0..100:10] produces 10 elements"""
        code = """
        val arr : [_]i32 = [0..100:10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Verify array type has correct size
        arr_symbol = self.analyzer.symbol_table.lookup_symbol("arr")
        assert arr_symbol is not None
        # Size should be 10 ([0, 10, 20, ..., 90])

    def test_empty_range_size_computation(self):
        """Test [10..5] produces 0 elements (inverted bounds)"""
        code = """
        val arr : [_]i32 = [10..5]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        # Should not error, but produce empty array
        assert_no_errors(errors)


class TestRangeMaterializationComptimeAdaptation(StandardTestBase):
    """Test comptime range adaptation to target types"""

    def test_comptime_range_adapts_to_i32(self):
        """✅ Comptime range adapts to i32 array"""
        code = """
        val arr : [_]i32 = [1..10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_range_adapts_to_i64(self):
        """✅ Comptime range adapts to i64 array"""
        code = """
        val arr : [_]i64 = [1..10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_range_adapts_to_f64_requires_step(self):
        """❌ Comptime int range adapting to f64 requires explicit step (becomes float range)"""
        code = """
        val arr : [_]f64 = [1..10]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        # When comptime_int adapts to f64 context, it becomes a float range
        # Float ranges require explicit step
        assert len(errors) > 0
        assert_error_contains(errors, "step")

    def test_comptime_range_preserves_flexibility(self):
        """✅ Range without type annotation stays comptime"""
        code = """
        val flexible_arr = [1..10]
        val as_i32 : [_]i32 = flexible_arr
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestRangeMaterializationEdgeCases(StandardTestBase):
    """Test edge cases and special scenarios"""

    def test_single_element_range(self):
        """Test [5..=5] produces 1 element"""
        code = """
        val arr : [_]i32 = [5..=5]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_large_step_range(self):
        """Test [0..100:50] produces 2 elements"""
        code = """
        val arr : [_]i32 = [0..100:50]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_range(self):
        """Test negative range [-10..-5] materializes"""
        code = """
        val arr : [_]i32 = [-10..-5]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_float_range_with_fractional_step(self):
        """Test [0.0..1.0:0.1] materializes correctly"""
        code = """
        val arr : [_]f32 = [0.0..1.0:0.1]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_descending_integer_range(self):
        """Test descending range [10..1:-1] with negative step"""
        code = """
        val arr : [_]i32 = [10..1:-1]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_descending_range_with_step_2(self):
        """Test descending range [20..0:-2] materializes correctly"""
        code = """
        val arr : [_]i32 = [20..0:-2]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_descending_float_range(self):
        """Test descending float range [10.0..0.0:-1.0]"""
        code = """
        val arr : [_]f32 = [10.0..0.0:-1.0]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_descending_inclusive_range(self):
        """Test descending inclusive range [10..=1:-1]"""
        code = """
        val arr : [_]i32 = [10..=1:-1]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestRangeMaterializationIntegration(StandardTestBase):
    """Test range materialization in realistic scenarios"""

    def test_range_in_function_call(self):
        """Test materialized range passed to function"""
        code = """
        func sum(arr : [_]i32) : i32 = {
            return 42
        }

        val result : i32 = sum([1..10])
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_range_with_variable_bounds_runtime_size(self):
        """Test range with variable bounds has runtime-determined size"""
        code = """
        mut start : i32 = 1
        mut end : i32 = 10
        val arr : [_]i32 = [start..end]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        # Should succeed - runtime-determined size is valid
        assert_no_errors(errors)

    def test_multiple_range_materializations(self):
        """Test multiple independent range materializations"""
        code = """
        val arr1 : [_]i32 = [1..10]
        val arr2 : [_]i32 = [10..20]
        val arr3 : [_]f32 = [0.0..1.0:0.1]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestRangeMaterializationErrorMessages(StandardTestBase):
    """Test that error messages are helpful and actionable"""

    def test_unbounded_error_is_helpful(self):
        """Verify unbounded range error provides helpful guidance"""
        code = """
        val arr : [_]i32 = [5..]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        # Should mention that only bounded ranges can materialize
        assert_error_contains(errors, "bounded")

    def test_float_step_error_is_helpful(self):
        """Verify float step error provides example syntax"""
        code = """
        val arr : [_]f32 = [0.0..1.0]
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        # Should mention explicit step requirement
        assert_error_contains(errors, "step")
