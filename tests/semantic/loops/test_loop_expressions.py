"""
Tests for loop expression semantic analysis (Phase 3).

These tests verify loop expression mode validation:
- Type annotation requirements (runtime operation)
- Value type matching with element types
- Filtering support (conditional -> statements)
- Break/continue in loop expressions
- Nested loop expressions (2D, 3D arrays)
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


class TestLoopExpressionTypeAnnotation:
    """Test type annotation requirements for loop expressions."""

    def test_loop_expression_requires_type_annotation(self):
        """Test: Loop expression must have explicit type"""
        code = """
        val result = for i in 1..10 { -> i }
        """
        errors = parse_and_analyze(code)
        # Should error: missing type annotation
        assert len(errors) > 0
        assert any("type annotation" in err.message.lower() for err in errors)

    def test_loop_expression_with_type_annotation(self):
        """Test: Loop expression with type annotation works"""
        code = """
        val result : [_]i32 = for i in 1..10 {
            -> i * i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_with_inferred_size(self):
        """Test: Loop expression with [_] size inference"""
        code = """
        val squares : [_]i32 = for i in 1..5 {
            -> i * i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_with_fixed_size(self):
        """Test: Loop expression with fixed size [N]T"""
        code = """
        val fixed : [10]i32 = for i in 1..=10 {
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_comptime_to_concrete(self):
        """Test: Comptime literals adapt to concrete array element type"""
        code = """
        val numbers : [_]i64 = for i in 1..5 {
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopExpressionValueTypes:
    """Test value type matching in loop expressions."""

    def test_loop_expression_value_type_mismatch(self):
        """Test: Loop expression value must match element type"""
        code = """
        val result : [_]i32 = for i in 1..10 {
            -> i:f64
        }
        """
        errors = parse_and_analyze(code)
        # Should error: f64 doesn't match i32
        assert len(errors) > 0

    def test_loop_expression_mixed_comptime_types(self):
        """Test: Mixed comptime types in loop expression"""
        code = """
        val mixed : [_]f64 = for i in 1..5 {
            -> i:f64 * 3.14
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_with_function_call(self):
        """Test: Loop expression with function call"""
        code = """
        func square(x: i32) : i32 = {
            return x * x
        }

        val squares : [_]i32 = for i in 1..5 {
            -> square(i)
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_complex_expression(self):
        """Test: Loop expression with complex value expression"""
        code = """
        val complex : [_]i32 = for i in 1..10 {
            -> (i * 2 + 1) * 3
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopExpressionFiltering:
    """Test filtering in loop expressions."""

    def test_loop_expression_conditional_yield(self):
        """Test: Conditional -> in loop expression"""
        code = """
        val evens : [_]i32 = for i in 1..20 {
            val is_even : bool = i % 2 == 0
            if is_even {
                -> i
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_filter_with_continue(self):
        """Test: Using continue to skip values"""
        code = """
        val filtered : [_]i32 = for i in 1..10 {
            val is_even : bool = i % 2 == 0
            if is_even {
                continue
            }
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_multiple_conditionals(self):
        """Test: Multiple filtering conditions"""
        code = """
        val special : [_]i32 = for i in 1..100 {
            val div_by_2 : bool = i % 2 == 0
            if div_by_2 {
                val div_by_3 : bool = i % 3 == 0
                if div_by_3 {
                    -> i
                }
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopExpressionControlFlow:
    """Test break/continue in loop expressions."""

    def test_loop_expression_with_break(self):
        """Test: Break in loop expression returns partial array"""
        code = """
        val partial : [_]i32 = for i in 1..100 {
            if i > 50 {
                break
            }
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_conditional_break(self):
        """Test: Conditional break in loop expression"""
        code = """
        val limited : [_]i32 = for i in 1..1000 {
            if i * i > 100 {
                break
            }
            -> i * i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_with_early_termination(self):
        """Test: Early termination with break"""
        code = """
        val search : [_]i32 = for i in 0..100 {
            -> i
            if i == 42 {
                break
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestNestedLoopExpressions:
    """Test nested loop expressions (2D, 3D arrays)."""

    def test_nested_loop_expression_2d(self):
        """Test: 2D array generation with nested loops"""
        code = """
        val matrix : [_][_]i32 = for i in 1..3 {
            -> for j in 1..4 {
                -> i * j
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_nested_loop_expression_3d(self):
        """Test: 3D tensor generation"""
        code = """
        val tensor : [_][_][_]i32 = for i in 1..2 {
            -> for j in 1..3 {
                -> for k in 1..4 {
                    -> i * j * k
                }
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_nested_loop_type_mismatch(self):
        """Test: Inner loop type must match outer element type"""
        code = """
        val bad : [_][_]i32 = for i in 1..3 {
            -> for j in 1..4 {
                -> j:f64
            }
        }
        """
        errors = parse_and_analyze(code)
        # Should error: f64 doesn't match i32
        assert len(errors) > 0

    def test_nested_loop_dimension_mismatch(self):
        """Test: Nesting level must match type"""
        code = """
        val bad : [_][_]i32 = for i in 1..3 {
            -> i
        }
        """
        errors = parse_and_analyze(code)
        # Should error: expected [_]i32, got i32
        assert len(errors) > 0

    def test_identity_matrix_generation(self):
        """Test: Identity matrix with conditionals"""
        code = """
        val identity : [_][_]i32 = for i in 0..5 {
            -> for j in 0..5 {
                if i == j {
                    -> 1
                } else {
                    -> 0
                }
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_filtered_outer_loop(self):
        """Test: Filtering outer loop (skip rows)"""
        code = """
        val filtered : [_][_]i32 = for i in 1..10 {
            if i % 2 == 0 {
                -> for j in 1..5 {
                    -> i * j
                }
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_filtered_inner_loop(self):
        """Test: Filtering inner loop (skip columns)"""
        code = """
        val sparse : [_][_]i32 = for i in 1..5 {
            -> for j in 1..10 {
                if j % 2 == 0 {
                    -> i * j
                }
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_nested_loop_with_break_outer(self):
        """Test: Break in outer loop of nested expression"""
        code = """
        val partial : [_][_]i32 = for i in 1..10 {
            if i > 5 {
                break
            }
            -> for j in 1..5 {
                -> i * j
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_nested_loop_with_break_inner(self):
        """Test: Break in inner loop of nested expression"""
        code = """
        val jagged : [_][_]i32 = for i in 1..5 {
            -> for j in 1..10 {
                if j > i {
                    break
                }
                -> i * j
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


class TestLoopExpressionRangeRestrictions:
    """Test unbounded range restrictions in expression mode."""

    def test_unbounded_range_forbidden_in_expression(self):
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
        # Should error: unbounded range in expression mode
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

    def test_unbounded_range_allowed_in_statement(self):
        """Test: Unbounded range OK in statement mode (not expression)"""
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


class TestLoopExpressionEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_loop_expression(self):
        """Test: Loop expression with no iterations"""
        code = """
        val empty : [_]i32 = for i in 1..1 {
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_single_iteration(self):
        """Test: Loop expression with single iteration"""
        code = """
        val single : [_]i32 = for i in 1..2 {
            -> i * 10
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_all_filtered(self):
        """Test: Loop expression where all values filtered out"""
        code = """
        val none : [_]i32 = for i in 1..10 {
            if false {
                -> i
            }
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_immediate_break(self):
        """Test: Loop expression that breaks immediately"""
        code = """
        val immediate : [_]i32 = for i in 1..100 {
            break
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0

    def test_loop_expression_with_complex_range(self):
        """Test: Loop expression with stepped range"""
        code = """
        val stepped : [_]i32 = for i in 0..100:10 {
            -> i
        }
        """
        errors = parse_and_analyze(code)
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
