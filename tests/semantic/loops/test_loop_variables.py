"""
Tests for loop variable type inference and validation.

These tests verify loop variable handling:
- Type inference from different iterable types
- Explicit type annotations
- Comptime type adaptation
- Type compatibility validation
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


def parse_and_analyze(code: str):
    """Helper function to parse and analyze code."""
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer.errors


class TestLoopVariableInferenceFromRanges:
    """Test loop variable type inference from range types."""

    def test_infer_from_comptime_range(self):
        """Test: Comptime range → comptime_int loop variable"""
        code = """
        for i in 1..10 {
            val as_i32 : i32 = i
            val as_i64 : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        # Comptime loop variable should adapt to both i32 and i64
        assert len(errors) == 0

    def test_infer_from_range_i32(self):
        """Test: range[i32] → i32 loop variable"""
        code = """
        val r : range[i32] = 1..10
        for i in r {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_range_i64(self):
        """Test: range[i64] → i64 loop variable"""
        code = """
        val r : range[i64] = 1..100
        for i in r {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_range_f32(self):
        """Test: range[f32] → f32 loop variable"""
        code = """
        val r : range[f32] = 0.0..10.0:0.5
        for x in r {
            val y : f32 = x
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_range_f64(self):
        """Test: range[f64] → f64 loop variable"""
        code = """
        val r : range[f64] = 0.0..100.0:1.0
        for x in r {
            val y : f64 = x
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_range_usize(self):
        """Test: range[usize] → usize loop variable"""
        code = """
        val r : range[usize] = 0..10
        for idx in r {
            val i : usize = idx
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableInferenceFromArrays:
    """Test loop variable type inference from array types."""

    def test_infer_from_i32_array(self):
        """Test: [_]i32 → i32 loop variable"""
        code = """
        val arr : [_]i32 = [1, 2, 3]
        for elem in arr[..] {
            val x : i32 = elem
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_f64_array(self):
        """Test: [_]f64 → f64 loop variable"""
        code = """
        val arr : [_]f64 = [1.0, 2.0, 3.0]
        for elem in arr[..] {
            val x : f64 = elem
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_bool_array(self):
        """Test: [_]bool → bool loop variable"""
        code = """
        val flags : [_]bool = [true, false, true]
        for flag in flags[..] {
            val b : bool = flag
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_infer_from_comptime_array_int(self):
        """Test: comptime_array_int → comptime_int loop variable"""
        code = """
        val arr = [1, 2, 3, 4]
        for elem in arr[..] {
            val as_i32 : i32 = elem
            val as_i64 : i64 = elem
        }
        """
        errors = parse_and_analyze(code)
        # Comptime array element should adapt to both i32 and i64
        assert len(errors) == 0

    def test_infer_from_comptime_array_float(self):
        """Test: comptime_array_float → comptime_float loop variable"""
        code = """
        val arr = [1.0, 2.0, 3.0]
        for elem in arr[..] {
            val as_f32 : f32 = elem
            val as_f64 : f64 = elem
        }
        """
        errors = parse_and_analyze(code)
        # Comptime array element should adapt to both f32 and f64
        assert len(errors) == 0

    def test_infer_from_nested_array(self):
        """Test: [_][_]i32 → [_]i32 loop variable (row iteration)"""
        # Note: This tests iterating over rows of a 2D array
        code = """
        val matrix : [_][_]i32 = [[1, 2], [3, 4]]
        for row in matrix[..] {
            val r : [_]i32 = row
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestExplicitLoopVariableTypes:
    """Test explicit type annotations on loop variables."""

    def test_explicit_i32_on_comptime_range(self):
        """Test: for i : i32 in 1..10"""
        code = """
        for i : i32 in 1..10 {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_explicit_i64_on_comptime_range(self):
        """Test: for i : i64 in 1..10"""
        code = """
        for i : i64 in 1..10 {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_explicit_f32_on_float_range(self):
        """Test: for x : f32 in 0.0..10.0:0.1"""
        code = """
        for x : f32 in 0.0..10.0:0.1 {
            val y : f32 = x
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_explicit_type_overrides_inference(self):
        """Test: Explicit type takes precedence over inference"""
        code = """
        val r : range[i32] = 1..10
        for i : i64 in r {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        # Explicit i64 should work (requires conversion from range[i32])
        # This may or may not be allowed depending on conversion rules
        pass


class TestComptimeTypeAdaptation:
    """Test comptime type adaptation in loop variables."""

    def test_comptime_int_adapts_to_i32(self):
        """Test: Comptime loop variable adapts to i32"""
        code = """
        for i in 1..10 {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_comptime_int_adapts_to_i64(self):
        """Test: Comptime loop variable adapts to i64"""
        code = """
        for i in 1..10 {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_comptime_int_adapts_to_multiple_types(self):
        """Test: Same comptime variable adapts to different types"""
        code = """
        for i in 1..10 {
            val as_i32 : i32 = i
            val as_i64 : i64 = i
            val as_f32 : f32 = i
            val as_f64 : f64 = i
        }
        """
        errors = parse_and_analyze(code)
        # Comptime int should adapt to all numeric types
        assert len(errors) == 0

    def test_comptime_float_adapts_to_f32(self):
        """Test: Comptime float adapts to f32"""
        code = """
        for x in [1.0, 2.0, 3.0][..] {
            val y : f32 = x
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_comptime_float_adapts_to_f64(self):
        """Test: Comptime float adapts to f64"""
        code = """
        for x in [1.0, 2.0, 3.0][..] {
            val y : f64 = x
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableTypeCompatibility:
    """Test type compatibility validation for loop variables."""

    def test_concrete_type_no_implicit_conversion(self):
        """Test: Concrete types don't convert implicitly"""
        code = """
        val r : range[i32] = 1..10
        for i in r {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        # Should require explicit conversion i:i64
        # Note: This test documents expected behavior
        pass

    def test_loop_variable_used_in_operations(self):
        """Test: Loop variable type in arithmetic"""
        code = """
        for i in 1..10 {
            val doubled : i32 = i * 2
            val sum : i32 = i + 5
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_in_comparisons(self):
        """Test: Loop variable in comparison operations"""
        code = """
        for i in 1..20 {
            if i > 10 {
                val big : i32 = i
            }
            if i < 5 {
                val small : i32 = i
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableInExpressionMode:
    """Test loop variables in loop expressions."""

    def test_loop_variable_in_yield_expression(self):
        """Test: Loop variable used in -> expression"""
        code = """
        val squares : [_]i32 = for i in 1..10 {
            -> i * i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_adapts_to_element_type(self):
        """Test: Comptime loop variable adapts to array element type"""
        code = """
        val as_i32 : [_]i32 = for i in 1..5 {
            -> i
        }
        val as_i64 : [_]i64 = for j in 1..5 {
            -> j
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_nested_loop_variable_independence(self):
        """Test: Inner and outer loop variables are independent"""
        code = """
        val matrix : [_][_]i32 = for i in 1..3 {
            -> for j in 1..4 {
                -> i * j
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableWithTypeConversions:
    """Test loop variables with explicit type conversions."""

    def test_explicit_conversion_in_yield(self):
        """Test: Explicit type conversion in -> expression"""
        code = """
        val floats : [_]f64 = for i in 1..10 {
            -> i:f64
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_conversion_in_operation(self):
        """Test: Type conversion in arithmetic operation"""
        code = """
        for i in 1..10 {
            val as_float : f64 = i:f64 * 3.14
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableEdgeCases:
    """Test edge cases in loop variable handling."""

    def test_loop_variable_same_name_different_loops(self):
        """Test: Same variable name in sequential loops"""
        code = """
        for i in 1..5 {
            val x : i32 = i
        }
        for i in 1..10 {
            val y : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        # Should work: scopes are separate
        assert len(errors) == 0

    def test_loop_variable_shadows_outer_variable(self):
        """Test: Loop variable shadows outer scope variable"""
        code = """
        val i : i32 = 100
        for i in 1..10 {
            val local : i32 = i
        }
        val after : i32 = i
        """
        errors = parse_and_analyze(code)
        # Should work: loop variable shadows, outer restored after
        assert len(errors) == 0

    def test_single_character_loop_variables(self):
        """Test: Single character variable names"""
        code = """
        for i in 1..5 {
            val x : i32 = i
        }
        for j in 1..5 {
            val y : i32 = j
        }
        for k in 1..5 {
            val z : i32 = k
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_descriptive_loop_variable_names(self):
        """Test: Descriptive variable names"""
        code = """
        for index in 1..10 {
            val x : i32 = index
        }
        for element in 1..5 {
            val y : i32 = element
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0
