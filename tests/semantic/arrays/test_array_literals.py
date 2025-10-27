"""
Test Array Literal Semantic Analysis

Tests for array literal type inference, validation, and integration
with the existing comptime type system using end-to-end Hexen source code.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestArrayLiteralSemantics:
    """Test semantic analysis of array literals with real Hexen source code"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_array_int_inference(self):
        """Test comptime_array_int inference from integer literals"""
        source = """
        func test() : void = {
            val numbers = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with comptime array int inference
        assert_no_errors(errors)

    def test_comptime_array_float_inference(self):
        """Test comptime_array_float inference from mixed numeric literals"""
        source = """
        func test() : void = {
            val mixed = [42, 3.14]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with comptime array float promotion
        assert_no_errors(errors)

    def test_comptime_array_flexibility(self):
        """Test comptime arrays adapt to different contexts"""
        source = """
        func test() : void = {
            val flexible = [1, 2, 3]
            val as_i32 : [3]i32 = flexible
            val as_i64 : [3]i64 = flexible
            val as_f32 : [3]f32 = flexible
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Comptime arrays should adapt to all numeric contexts
        assert_no_errors(errors)

    def test_empty_array_type_annotation_requirement(self):
        """Test empty array literal requires explicit type annotation"""
        source = """
        func test() : void = {
            val empty = []
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Empty arrays should require explicit type annotation
        assert_error_contains(
            errors, "Empty array literal requires explicit type annotation"
        )

    def test_empty_array_with_type_annotation(self):
        """Test empty array literal with explicit type annotation works"""
        source = """
        func test() : void = {
            val empty : [0]i32 = []
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with explicit type annotation
        assert_no_errors(errors)

    def test_type_annotation_driven_resolution(self):
        """Test array literal resolution with explicit type annotation"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Type annotation-driven resolution should work
        assert_no_errors(errors)

    def test_array_size_mismatch_error(self):
        """Test error when array size doesn't match type annotation"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect size mismatch
        assert_error_contains(errors, "Array size mismatch: expected 3 elements, got 2")

    def test_mixed_concrete_types_error(self):
        """Test error for mixed concrete/comptime types without type annotation"""
        source = """
        func test(x: i32) : void = {
            val mixed = [1, x]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should require explicit type annotation for mixed types
        assert_error_contains(
            errors,
            "Mixed concrete/comptime element types require explicit array type annotation",
        )

    def test_mixed_concrete_types_with_type_annotation(self):
        """Test mixed concrete/comptime types work with explicit type annotation"""
        source = """
        func test(x: i32) : void = {
            val mixed : [2]i32 = [1, x]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with explicit type annotation
        assert_no_errors(errors)

    def test_array_literals_in_function_parameters(self):
        """Test array literals in function call parameters"""
        source = """
        func process(arr: [3]i32) : void = {
            return
        }
        
        func test() : void = {
            process([1, 2, 3])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Function parameter context should work
        assert_no_errors(errors)

    def test_array_literals_in_return_statements(self):
        """Test array literals in return statements"""
        source = """
        func create_array() : [3]i32 = {
            return [1, 2, 3]
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Return type context should work
        assert_no_errors(errors)

    def test_array_literals_with_expressions(self):
        """Test array literals containing expressions"""
        source = """
        func test() : void = {
            val computed = [1 + 2, 3 * 4, 5 / 2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Expression elements should work
        assert_no_errors(errors)

    def test_large_array_literals(self):
        """Test arrays with many elements"""
        source = """
        func test() : void = {
            val many = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Large arrays should work
        assert_no_errors(errors)

    def test_type_mismatch_with_explicit_type_annotation(self):
        """Test type mismatch with explicit type annotation"""
        source = """
        func test() : void = {
            val strings : [2]i32 = ["hello", "world"]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect type mismatch
        assert_error_contains(errors, "type mismatch")

    def test_comptime_array_type_adaptation(self):
        """Test comptime arrays adapt to different explicit type contexts"""
        source = """
        func test() : void = {
            val flexible = [1, 2, 3]
            val as_i32 : [3]i32 = flexible
            val as_i64 : [3]i64 = flexible
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Comptime arrays should adapt to all numeric contexts
        assert_no_errors(errors)

    def test_array_function_parameters(self):
        """Test array literals as function parameters"""
        source = """
        func process(arr: [3]i32) : void = {
            return
        }

        func test() : void = {
            process([1, 2, 3])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Function parameter context should work
        assert_no_errors(errors)


class TestRangeMaterializationInArrayContext:
    """
    Test range materialization from the array literal perspective.

    Focus: How range expressions [start..end] integrate with array literal
    type inference and comptime array semantics.

    Complementary to tests/semantic/ranges/test_range_materialization.py which
    tests ranges from the range system perspective.
    """

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_range_materialization_comptime_preservation(self):
        """Test range materialization preserves comptime flexibility like array literals"""
        source = """
        func test() : void = {
            val flexible = [1..5]
            val as_i32 : [_]i32 = flexible
            val as_i64 : [_]i64 = flexible
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range should materialize to comptime array, then adapt to both types
        assert_no_errors(errors)

    def test_range_materialization_immediate_concrete(self):
        """Test range materialization with immediate type annotation"""
        source = """
        func test() : void = {
            val concrete : [_]i32 = [1..10]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range should materialize directly to [N]i32
        assert_no_errors(errors)

    def test_range_materialization_mixed_with_literals(self):
        """Test error when mixing range materialization with regular literals"""
        source = """
        func test() : void = {
            val mixed = [1, 2, [3..5]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should error: nested array syntax not allowed
        assert len(errors) > 0

    def test_range_materialization_to_different_sizes(self):
        """Test multiple range materializations with different sizes"""
        source = """
        func test() : void = {
            val small : [_]i32 = [1..5]
            val large : [_]i32 = [1..100]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Both should materialize successfully with inferred sizes
        assert_no_errors(errors)

    def test_range_materialization_inclusive_vs_exclusive(self):
        """Test inclusive and exclusive range materialization in array context"""
        source = """
        func test() : void = {
            val exclusive : [_]i32 = [1..10]
            val inclusive : [_]i32 = [1..=10]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Both should materialize (different sizes: 9 vs 10 elements)
        assert_no_errors(errors)

    def test_range_materialization_with_step(self):
        """Test stepped range materialization in array literal context"""
        source = """
        func test() : void = {
            val stepped : [_]i32 = [0..100:10]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should materialize to array with step values
        assert_no_errors(errors)

    def test_range_materialization_float_requires_step(self):
        """Test float range materialization requires explicit step"""
        source = """
        func test() : void = {
            val floats : [_]f32 = [0.0..10.0]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should error: float range requires step
        assert_error_contains(errors, "step")

    def test_range_materialization_float_with_step_succeeds(self):
        """Test float range materialization with step succeeds"""
        source = """
        func test() : void = {
            val floats : [_]f32 = [0.0..10.0:0.5]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should succeed
        assert_no_errors(errors)

    def test_range_materialization_unbounded_error(self):
        """Test unbounded range cannot materialize in array literal context"""
        source = """
        func test() : void = {
            val unbounded : [_]i32 = [5..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should error: unbounded range cannot materialize
        assert_error_contains(errors, "unbounded")

    def test_range_materialization_as_function_argument(self):
        """Test range materialization in function parameter context"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func test() : void = {
            process([1..10])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range should materialize to match parameter type
        assert_no_errors(errors)

    def test_range_materialization_in_return(self):
        """Test range materialization in return statement"""
        source = """
        func create_sequence() : [_]i32 = {
            return [1..10]
        }

        func test() : void = {
            val seq : [_]i32 = create_sequence()
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range should materialize to match return type
        assert_no_errors(errors)

    def test_range_materialization_comptime_to_multiple_contexts(self):
        """Test same comptime range materializes to different array types"""
        source = """
        func test() : void = {
            val range_source = [1..5]
            val as_i32 : [_]i32 = range_source
            val as_i64 : [_]i64 = range_source
            val as_f64 : [_]f64 = range_source
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Comptime range array should adapt to all numeric types
        assert_no_errors(errors)

    def test_range_materialization_negative_range(self):
        """Test negative range materialization"""
        source = """
        func test() : void = {
            val negatives : [_]i32 = [-10..-5]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Negative ranges should materialize correctly
        assert_no_errors(errors)

    def test_range_materialization_descending_with_negative_step(self):
        """Test descending range with negative step"""
        source = """
        func test() : void = {
            val descending : [_]i32 = [10..1:-1]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Descending range should materialize
        assert_no_errors(errors)


if __name__ == "__main__":
    pytest.main([__file__])
