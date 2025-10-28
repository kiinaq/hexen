"""
Comprehensive tests for for-in loop parsing.

Tests cover:
- Basic for-in loops
- Type annotations
- Range iteration (bounded, inclusive, stepped)
- Array iteration and slicing
- Float ranges
- Nested loops (2D, 3D, 4D)
- Loop expressions producing arrays
- Filtering patterns
- Early termination with break
- Expression mode vs statement mode
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


@pytest.fixture
def parser():
    """Create parser instance for testing."""
    return HexenParser()


class TestBasicForInLoops:
    """Test basic for-in loop parsing."""

    def test_basic_for_in_with_range(self, parser):
        """Test: for i in 1..10 { }"""
        code = """
        for i in 1..10 {
            print(i)
        }
        """
        ast = parser.parse(code)
        assert len(ast["statements"]) == 1
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "i"
        assert loop["variable_type"] is None
        assert loop["iterable"]["type"] == NodeType.RANGE_EXPR.value

    def test_for_in_with_inclusive_range(self, parser):
        """Test: for i in 1..=10 { }"""
        code = """
        for i in 1..=10 {
            print(i)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["iterable"]["inclusive"] is True

    def test_for_in_with_stepped_range(self, parser):
        """Test: for i in 0..100:10 { }"""
        code = """
        for i in 0..100:10 {
            print(i)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["iterable"]["step"] is not None

    def test_for_in_with_empty_body(self, parser):
        """Test: for i in 1..10 { }"""
        code = """
        for i in 1..10 {
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert len(loop["body"]["statements"]) == 0

    def test_for_in_with_multiple_statements(self, parser):
        """Test: for i in 1..10 { stmt1; stmt2; stmt3 }"""
        code = """
        for i in 1..10 {
            val x : i32 = i
            val y : i32 = x * 2
            print(y)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert len(loop["body"]["statements"]) == 3


class TestForInWithTypeAnnotations:
    """Test for-in loops with type annotations."""

    def test_for_in_with_i32_type(self, parser):
        """Test: for i : i32 in 1..10 { }"""
        code = """
        for i : i32 in 1..10 {
            print(i)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "i"
        assert loop["variable_type"] == "i32"

    def test_for_in_with_i64_type(self, parser):
        """Test: for i : i64 in 1..100 { }"""
        code = """
        for i : i64 in 1..100 {
            print(i)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable_type"] == "i64"

    def test_for_in_with_f32_type(self, parser):
        """Test: for x : f32 in 0.0..10.0:0.5 { }"""
        code = """
        for x : f32 in 0.0..10.0:0.5 {
            print(x)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable_type"] == "f32"

    def test_for_in_with_usize_type(self, parser):
        """Test: for idx : usize in 0..length { }"""
        code = """
        for idx : usize in 0..100 {
            print(idx)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable_type"] == "usize"


class TestForInArrayIteration:
    """Test for-in loops with array iteration."""

    def test_for_in_array_full_slice(self, parser):
        """Test: for elem in data[..] { }"""
        code = """
        val data : [_]i32 = [1, 2, 3]
        for elem in data[..] {
            print(elem)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][1]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "elem"

    def test_for_in_array_partial_slice(self, parser):
        """Test: for elem in data[2..5] { }"""
        code = """
        val data : [_]i32 = [1, 2, 3, 4, 5, 6, 7]
        for elem in data[2..5] {
            print(elem)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][1]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_for_in_array_literal(self, parser):
        """Test: for elem in [1, 2, 3] { }"""
        code = """
        for elem in [1, 2, 3] {
            print(elem)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value


class TestForInExpressionMode:
    """Test for-in loops in expression mode (producing arrays)."""

    def test_loop_expression_basic(self, parser):
        """Test: val result : [_]i32 = for i in 1..10 { -> i }"""
        code = """
        val result : [_]i32 = for i in 1..10 {
            -> i
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        assert decl["type"] == NodeType.VAL_DECLARATION.value
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert len(loop["body"]["statements"]) == 1
        assert loop["body"]["statements"][0]["type"] == NodeType.ASSIGN_STATEMENT.value

    def test_loop_expression_with_computation(self, parser):
        """Test: val squares : [_]i32 = for i in 1..10 { -> i * i }"""
        code = """
        val squares : [_]i32 = for i in 1..10 {
            -> i * i
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["body"]["statements"][0]["type"] == NodeType.ASSIGN_STATEMENT.value

    def test_loop_expression_with_filtering(self, parser):
        """Test: val evens : [_]i32 = for i in 1..20 { if i % 2 == 0 { -> i } }"""
        code = """
        val evens : [_]i32 = for i in 1..20 {
            if i % 2 == 0 {
                -> i
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert len(loop["body"]["statements"]) == 1
        assert loop["body"]["statements"][0]["type"] == NodeType.CONDITIONAL_STATEMENT.value

    def test_loop_expression_with_early_termination(self, parser):
        """Test: val partial : [_]i32 = for i in 1..100 { if i > 50 { break }; -> i }"""
        code = """
        val partial : [_]i32 = for i in 1..100 {
            if i > 50 {
                break
            }
            -> i
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert len(loop["body"]["statements"]) == 2


class TestNestedForInLoops:
    """Test nested for-in loop structures."""

    def test_nested_2d_loops(self, parser):
        """Test: for i in 1..3 { for j in 1..4 { } }"""
        code = """
        for i in 1..3 {
            for j in 1..4 {
                print(i, j)
            }
        }
        """
        ast = parser.parse(code)
        outer = ast["statements"][0]
        assert outer["type"] == NodeType.FOR_IN_LOOP.value
        inner = outer["body"]["statements"][0]
        assert inner["type"] == NodeType.FOR_IN_LOOP.value

    def test_nested_2d_loop_expression(self, parser):
        """Test: val matrix : [_][_]i32 = for i in 1..3 { -> for j in 1..4 { -> i*j } }"""
        code = """
        val matrix : [_][_]i32 = for i in 1..3 {
            -> for j in 1..4 {
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        outer_loop = decl["value"]
        assert outer_loop["type"] == NodeType.FOR_IN_LOOP.value
        yield_stmt = outer_loop["body"]["statements"][0]
        inner_loop = yield_stmt["value"]
        assert inner_loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_nested_3d_loop_expression(self, parser):
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
        ast = parser.parse(code)
        decl = ast["statements"][0]
        outer = decl["value"]
        assert outer["type"] == NodeType.FOR_IN_LOOP.value
        middle = outer["body"]["statements"][0]["value"]
        assert middle["type"] == NodeType.FOR_IN_LOOP.value
        inner = middle["body"]["statements"][0]["value"]
        assert inner["type"] == NodeType.FOR_IN_LOOP.value

    def test_nested_4d_loop_expression(self, parser):
        """Test: 4D tensor generation"""
        code = """
        val tensor4d : [_][_][_][_]i32 = for i in 1..2 {
            -> for j in 1..2 {
                -> for k in 1..2 {
                    -> for l in 1..2 {
                        -> i + j + k + l
                    }
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        level1 = decl["value"]
        level2 = level1["body"]["statements"][0]["value"]
        level3 = level2["body"]["statements"][0]["value"]
        level4 = level3["body"]["statements"][0]["value"]
        assert level1["type"] == NodeType.FOR_IN_LOOP.value
        assert level2["type"] == NodeType.FOR_IN_LOOP.value
        assert level3["type"] == NodeType.FOR_IN_LOOP.value
        assert level4["type"] == NodeType.FOR_IN_LOOP.value


class TestFloatRangeIteration:
    """Test for-in loops with float ranges."""

    def test_float_range_with_step(self, parser):
        """Test: for x in 0.0..10.0:0.5 { }"""
        code = """
        for x in 0.0..10.0:0.5 {
            print(x)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["iterable"]["type"] == NodeType.RANGE_EXPR.value

    def test_float_range_with_type_annotation(self, parser):
        """Test: for x : f64 in 0.0..100.0:1.0 { }"""
        code = """
        for x : f64 in 0.0..100.0:1.0 {
            print(x)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable_type"] == "f64"


class TestComplexForInPatterns:
    """Test complex real-world for-in patterns."""

    def test_multiplication_table(self, parser):
        """Test: Generate 10x10 multiplication table"""
        code = """
        val table : [_][_]i32 = for i in 1..=10 {
            -> for j in 1..=10 {
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["iterable"]["inclusive"] is True

    def test_identity_matrix_pattern(self, parser):
        """Test: Identity matrix generation with conditionals"""
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
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_filtered_nested_loops(self, parser):
        """Test: Skip empty rows in nested loop expressions"""
        code = """
        val filtered : [_][_]i32 = for i in 1..10 {
            if i % 2 == 0 {
                -> for j in 1..5 {
                    -> i * j
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_loop_with_local_accumulator(self, parser):
        """Test: Loop with local variable accumulation"""
        code = """
        for i in 1..10 {
            val square : i32 = i * i
            val cube : i32 = square * i
            print(cube)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert len(loop["body"]["statements"]) == 3

    def test_loop_expression_with_function_calls(self, parser):
        """Test: Loop expression with function calls in body"""
        code = """
        val results : [_]i32 = for i in 1..10 {
            -> process(i)
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value


class TestForInEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_element_range(self, parser):
        """Test: for i in 5..=5 { }"""
        code = """
        for i in 5..=5 {
            print(i)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_large_range(self, parser):
        """Test: for i in 0..1000000 { }"""
        code = """
        for i in 0..1000000 {
            break
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_negative_range(self, parser):
        """Test: for i in -10..10 { }"""
        code = """
        for i in -10..10 {
            print(i)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

    def test_long_variable_name(self, parser):
        """Test: for very_long_variable_name in 1..10 { }"""
        code = """
        for very_long_variable_name_for_iteration in 1..10 {
            print(very_long_variable_name_for_iteration)
        }
        """
        ast = parser.parse(code)
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "very_long_variable_name_for_iteration"
