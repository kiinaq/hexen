"""
Tests for for-in loop semantic analysis.

These tests verify for-in loop validation:
- Loop variable type inference from iterables
- Loop variable immutability
- Unbounded range restrictions
- Array iteration
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


class TestLoopVariableTypeInference:
    """Test loop variable type inference from iterables."""

    def test_loop_variable_from_comptime_range(self):
        """Test: for i in 1..10 → i is comptime_int (adapts to context)"""
        code = """
        for i in 1..10 {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_from_concrete_range_i32(self):
        """Test: for i in range[i32] → i is i32"""
        code = """
        val r : range[i32] = 1..10
        for i in r {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_from_concrete_range_i64(self):
        """Test: for i in range[i64] → i is i64"""
        code = """
        val r : range[i64] = 1..10
        for i in r {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_explicit_type_annotation(self):
        """Test: for i : i64 in 1..10 → i is i64"""
        code = """
        for i : i64 in 1..10 {
            val x : i64 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_comptime_range_adapts_to_loop_variable(self):
        """Test: Comptime range adapts to explicit type"""
        code = """
        for i : i32 in 1..10 {
            val x : i32 = i
        }
        for j : i64 in 1..10 {
            val y : i64 = j
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_from_array_slice(self):
        """Test: for elem in array[..] → elem type = array element type"""
        code = """
        val data : [_]f64 = [1.0, 2.0, 3.0]
        for elem in data[..] {
            val x : f64 = elem
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_variable_from_array_i32(self):
        """Test: for elem in [_]i32 array → elem is i32"""
        code = """
        val numbers : [_]i32 = [10, 20, 30]
        for num in numbers[..] {
            val doubled : i32 = num * 2
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableImmutability:
    """Test that loop variables are immutable."""

    def test_loop_variable_immutable(self):
        """Test: Loop variables cannot be reassigned"""
        code = """
        for i in 1..10 {
            i = 42
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) > 0
        assert any("immutable" in err.message.lower() for err in errors)

    def test_loop_variable_cannot_increment(self):
        """Test: Loop variable cannot be incremented"""
        code = """
        for i in 1..10 {
            i = i + 1
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) > 0
        assert any("immutable" in err.message.lower() for err in errors)

    def test_loop_variable_read_only(self):
        """Test: Loop variable can be read but not written"""
        code = """
        for i in 1..10 {
            val copy : i32 = i
            val doubled : i32 = i * 2
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestUnboundedRangeRestrictions:
    """Test unbounded range handling in loops."""

    def test_unbounded_range_allowed_in_statement_mode(self):
        """Test: Unbounded range OK in statement mode"""
        code = """
        for i in 5.. {
            if i > 100 {
                break
            }
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_unbounded_from_range_statement(self):
        """Test: start.. range in statement mode"""
        code = """
        for i in 10.. {
            if i > 20 {
                break
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_unbounded_range_forbidden_in_expression_mode(self):
        """Test: Unbounded range cannot produce array"""
        code = """
        val infinite : [_]i32 = for i in 5.. {
            if i > 100 {
                break
            }
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) > 0
        assert any("unbounded" in err.message.lower() for err in errors)

    def test_bounded_range_allowed_in_expression(self):
        """Test: Bounded range OK in expression mode"""
        code = """
        val bounded : [_]i32 = for i in 5..100 {
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestForInLoopBody:
    """Test for-in loop body validation."""

    def test_for_in_with_empty_body(self):
        """Test: Empty for-in body is valid"""
        code = """
        for i in 1..10 {
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_with_variable_declarations(self):
        """Test: Variable declarations in loop body"""
        code = """
        for i in 1..10 {
            val squared : i32 = i * i
            val doubled : i32 = i * 2
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_with_conditionals(self):
        """Test: Conditionals in loop body"""
        code = """
        for i in 1..20 {
            if i > 10 {
                val big : i32 = i
            } else {
                val small : i32 = i
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_with_nested_loops(self):
        """Test: Nested for-in loops"""
        code = """
        for i in 1..5 {
            for j in 1..5 {
                val product : i32 = i * j
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestForInWithRanges:
    """Test for-in loops with various range types."""

    def test_for_in_inclusive_range(self):
        """Test: Inclusive range 1..=10"""
        code = """
        for i in 1..=10 {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_stepped_range(self):
        """Test: Stepped range 0..100:10"""
        code = """
        for i in 0..100:10 {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_float_range(self):
        """Test: Float range requires step"""
        code = """
        for x in 0.0..10.0:0.5 {
            val y : f64 = x
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_reverse_range(self):
        """Test: Reverse range 10..1:-1"""
        code = """
        for i in 10..1:-1 {
            val countdown : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestForInWithArrays:
    """Test for-in loops with array iteration."""

    def test_for_in_array_full_slice(self):
        """Test: Iterate over full array"""
        code = """
        val data : [_]i32 = [1, 2, 3, 4, 5]
        for elem in data[..] {
            val squared : i32 = elem * elem
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_array_partial_slice(self):
        """Test: Iterate over array slice"""
        code = """
        val data : [_]i32 = [1, 2, 3, 4, 5]
        for elem in data[1..4] {
            val x : i32 = elem
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_float_array(self):
        """Test: Iterate over float array"""
        code = """
        val floats : [_]f64 = [1.0, 2.0, 3.0]
        for f in floats[..] {
            val doubled : f64 = f * 2.0
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_comptime_array(self):
        """Test: Iterate over comptime array"""
        code = """
        val comptime_arr = [1, 2, 3, 4]
        for elem in comptime_arr[..] {
            val x : i32 = elem
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestForInStatementMode:
    """Test for-in loops in statement mode (not producing values)."""

    def test_for_in_statement_basic(self):
        """Test: Basic for-in statement"""
        code = """
        for i in 1..10 {
            val x : i32 = i * 2
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_statement_with_side_effects(self):
        """Test: For-in with variable modifications"""
        code = """
        mut sum : i32 = 0
        for i in 1..10 {
            sum = sum + i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_for_in_statement_no_return_value(self):
        """Test: Statement-mode loops don't produce values"""
        code = """
        for i in 1..5 {
            val x : i32 = i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopVariableScope:
    """Test loop variable scope management."""

    def test_loop_variable_not_visible_after_loop(self):
        """Test: Loop variable goes out of scope"""
        code = """
        for i in 1..10 {
            val x : i32 = i
        }
        val y : i32 = i
        """
        errors = parse_and_analyze(code)
        assert len(errors) > 0
        assert any("undefined" in err.message.lower() or "not found" in err.message.lower() for err in errors)

    def test_loop_variable_shadows_outer(self):
        """Test: Loop variable can shadow outer variable"""
        code = """
        val i : i32 = 42
        for i in 1..10 {
            val x : i32 = i
        }
        val y : i32 = i
        """
        errors = parse_and_analyze(code)
        # Should work: loop variable shadows outer, outer restored after
        assert len(errors) == 0

    def test_nested_loop_variables_independent(self):
        """Test: Nested loop variables are independent"""
        code = """
        for i in 1..5 {
            for i in 1..3 {
                val x : i32 = i
            }
        }
        """
        errors = parse_and_analyze(code)
        # Inner 'i' shadows outer 'i' - should be valid
        assert len(errors) == 0
