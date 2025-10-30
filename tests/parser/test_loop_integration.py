"""
Comprehensive integration tests for loop system.

Tests cover complex real-world scenarios that combine multiple features:
- Matrix operations (multiplication tables, identity matrices)
- Filtered nested loops
- Complex control flow with labels
- Loop expressions with conditionals
- Multi-dimensional tensor generation
- Realistic data processing patterns
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


@pytest.fixture
def parser():
    """Create parser instance for testing."""
    return HexenParser()


class TestMatrixOperations:
    """Test matrix generation and manipulation patterns."""

    def test_multiplication_table_10x10(self, parser):
        """Test: Generate complete 10x10 multiplication table"""
        code = """
        val table : [_][_]i32 = for i in 1..=10 {
            -> for j in 1..=10 {
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        assert decl["type"] == NodeType.VAL_DECLARATION.value
        assert decl["name"] == "table"

        # Verify nested loop expression structure
        outer_loop = decl["value"]
        assert outer_loop["type"] == NodeType.FOR_IN_LOOP.value
        assert outer_loop["iterable"]["inclusive"] is True

    def test_identity_matrix_generation(self, parser):
        """Test: Generate NxN identity matrix with conditionals"""
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
        outer_loop = decl["value"]
        inner_yield = outer_loop["body"]["statements"][0]
        inner_loop = inner_yield["value"]

        # Verify conditional in inner loop
        assert inner_loop["body"]["statements"][0]["type"] == NodeType.CONDITIONAL_STATEMENT.value

    def test_upper_triangular_matrix(self, parser):
        """Test: Generate upper triangular matrix"""
        code = """
        val upper : [_][_]i32 = for i in 0..5 {
            -> for j in 0..5 {
                if j >= i {
                    -> i + j
                } else {
                    -> 0
                }
            }
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_symmetric_matrix(self, parser):
        """Test: Generate symmetric matrix"""
        code = """
        val symmetric : [_][_]i32 = for i in 0..4 {
            -> for j in 0..4 {
                -> i * j + j * i
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        assert decl["value"]["type"] == NodeType.FOR_IN_LOOP.value

    def test_diagonal_matrix(self, parser):
        """Test: Generate diagonal matrix with specified values"""
        code = """
        val values : [_]i32 = [2, 4, 6, 8, 10]
        val diagonal : [_][_]i32 = for i in 0..5 {
            -> for j in 0..5 {
                if i == j {
                    -> values[i]
                } else {
                    -> 0
                }
            }
        }
        """
        ast = parser.parse(code)
        assert len(ast["statements"]) == 2


class TestFilteredNestedLoops:
    """Test filtered nested loop patterns."""

    def test_skip_even_rows(self, parser):
        """Test: Skip even-numbered rows in matrix generation"""
        code = """
        val odd_rows : [_][_]i32 = for i in 1..10 {
            if i % 2 == 1 {
                -> for j in 1..5 {
                    -> i * j
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        outer_loop = decl["value"]
        assert outer_loop["body"]["statements"][0]["type"] == NodeType.CONDITIONAL_STATEMENT.value

    def test_skip_even_columns(self, parser):
        """Test: Skip even-numbered columns in matrix generation"""
        code = """
        val odd_cols : [_][_]i32 = for i in 1..5 {
            -> for j in 1..10 {
                if j % 2 == 1 {
                    -> i * j
                }
            }
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_both_dimensions_filtered(self, parser):
        """Test: Filter both rows and columns"""
        code = """
        val sparse : [_][_]i32 = for i in 1..20 {
            if i % 3 == 0 {
                -> for j in 1..20 {
                    if j % 5 == 0 {
                        -> i + j
                    }
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        assert decl["name"] == "sparse"

    def test_conditional_row_lengths(self, parser):
        """Test: Generate rows of different lengths based on condition"""
        code = """
        val varied : [_][_]i32 = for i in 1..5 {
            -> for j in 1..i {
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        # This creates a triangular/jagged array structure
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value


class TestComplexControlFlow:
    """Test complex control flow with labels and break/continue."""

    def test_labeled_break_from_inner_to_outer(self, parser):
        """Test: Break from inner loop to outer loop label"""
        code = """
        'outer for i in 1..100 {
            'inner for j in 1..100 {
                if i * j > 1000 {
                    break 'outer
                }
                print(i, j)
            }
        }
        """
        ast = parser.parse(code)
        labeled = ast["statements"][0]
        assert labeled["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled["label"] == "outer"

    def test_labeled_continue_to_outer(self, parser):
        """Test: Continue outer loop from inner loop"""
        code = """
        'outer for i in 1..10 {
            val sum : i32 = 0
            'inner for j in 1..10 {
                if sum > 50 {
                    continue 'outer
                }
                sum = sum + j
            }
            print(sum)
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.LABELED_STATEMENT.value

    def test_triple_nested_with_multiple_breaks(self, parser):
        """Test: Three levels deep with breaks to different labels"""
        code = """
        'a for i in 1..10 {
            'b for j in 1..10 {
                'c for k in 1..10 {
                    if k > 5 {
                        break 'c
                    }
                    if j > 7 {
                        break 'b
                    }
                    if i > 8 {
                        break 'a
                    }
                    process(i, j, k)
                }
            }
        }
        """
        ast = parser.parse(code)
        level_a = ast["statements"][0]
        assert level_a["label"] == "a"

    def test_early_termination_in_expression(self, parser):
        """Test: Early termination in loop expression with break"""
        code = """
        'bounded val limited : [_]i32 = for i in 1..1000 {
            if i > 100 {
                break 'bounded
            }
            if i % 3 == 0 {
                -> i
            }
        }
        """
        ast = parser.parse(code)
        labeled_stmt = ast["statements"][0]
        assert labeled_stmt["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled_stmt["label"] == "bounded"


class TestMultiDimensionalTensors:
    """Test generation of multi-dimensional tensors."""

    def test_3d_tensor_generation(self, parser):
        """Test: Generate 3D tensor with computations"""
        code = """
        val tensor3d : [_][_][_]i32 = for i in 0..3 {
            -> for j in 0..4 {
                -> for k in 0..5 {
                    -> i * 100 + j * 10 + k
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        level1 = decl["value"]
        level2 = level1["body"]["statements"][0]["value"]
        level3 = level2["body"]["statements"][0]["value"]

        assert level1["type"] == NodeType.FOR_IN_LOOP.value
        assert level2["type"] == NodeType.FOR_IN_LOOP.value
        assert level3["type"] == NodeType.FOR_IN_LOOP.value

    def test_4d_tensor_with_conditionals(self, parser):
        """Test: 4D tensor with conditional values"""
        code = """
        val tensor4d : [_][_][_][_]i32 = for a in 0..2 {
            -> for b in 0..2 {
                -> for c in 0..2 {
                    -> for d in 0..2 {
                        if (a + b + c + d) % 2 == 0 {
                            -> 1
                        } else {
                            -> 0
                        }
                    }
                }
            }
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_5d_tensor_minimal(self, parser):
        """Test: 5D tensor generation"""
        code = """
        val tensor5d : [_][_][_][_][_]i32 = for a in 0..2 {
            -> for b in 0..2 {
                -> for c in 0..2 {
                    -> for d in 0..2 {
                        -> for e in 0..2 {
                            -> a + b + c + d + e
                        }
                    }
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        assert decl["name"] == "tensor5d"


class TestRealisticDataProcessing:
    """Test realistic data processing patterns."""

    def test_prime_number_sieve_pattern(self, parser):
        """Test: Generate primes using sieve-like pattern"""
        code = """
        val primes : [_]i32 = for i in 2..100 {
            val is_prime : bool = check_prime(i)
            if is_prime {
                -> i
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert len(loop["body"]["statements"]) == 2

    def test_fibonacci_pattern(self, parser):
        """Test: Generate Fibonacci sequence"""
        code = """
        val fibs : [_]i32 = for i in 0..20 {
            -> fib(i)
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_coordinate_grid_generation(self, parser):
        """Test: Generate 2D coordinate grid"""
        code = """
        val grid : [_][_]i32 = for x in -5..=5 {
            -> for y in -5..=5 {
                -> x * x + y * y
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        outer = decl["value"]
        assert outer["iterable"]["inclusive"] is True

    def test_nested_ranges_with_steps(self, parser):
        """Test: Nested loops with different step sizes"""
        code = """
        val stepped : [_][_]i32 = for i in 0..100:10 {
            -> for j in 0..50:5 {
                -> i + j
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        outer = decl["value"]
        assert outer["iterable"]["step"] is not None


class TestMixedLoopTypes:
    """Test mixing for-in and while loops."""

    def test_for_containing_while(self, parser):
        """Test: For loop containing while loop"""
        code = """
        for i in 1..10 {
            val count : i32 = 0
            while count < i {
                print(count)
                count = count + 1
            }
        }
        """
        ast = parser.parse(code)
        for_loop = ast["statements"][0]
        assert for_loop["type"] == NodeType.FOR_IN_LOOP.value
        while_loop = for_loop["body"]["statements"][1]
        assert while_loop["type"] == NodeType.WHILE_LOOP.value

    def test_while_containing_for(self, parser):
        """Test: While loop containing for loop"""
        code = """
        val running : bool = true
        while running {
            for i in 1..5 {
                if i > 3 {
                    running = false
                    break
                }
                process(i)
            }
        }
        """
        ast = parser.parse(code)
        while_loop = ast["statements"][1]
        assert while_loop["type"] == NodeType.WHILE_LOOP.value

    def test_nested_mixed_loops_with_labels(self, parser):
        """Test: Mixed loop types with labels"""
        code = """
        'outer while running {
            'inner for i in 1..100 {
                if should_exit {
                    break 'outer
                }
                if should_skip {
                    continue 'inner
                }
                work(i)
            }
            check_status()
        }
        """
        ast = parser.parse(code)
        labeled_while = ast["statements"][0]
        assert labeled_while["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled_while["label"] == "outer"


class TestComplexExpressionPatterns:
    """Test complex expression patterns in loops."""

    def test_pascal_triangle_generation(self, parser):
        """Test: Generate Pascal's triangle rows"""
        code = """
        val pascal : [_][_]i32 = for row in 0..10 {
            -> for col in 0..=row {
                -> binomial(row, col)
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        outer = decl["value"]
        inner_yield = outer["body"]["statements"][0]
        inner_loop = inner_yield["value"]
        assert inner_loop["iterable"]["inclusive"] is True

    def test_transformation_pipeline(self, parser):
        """Test: Multi-stage transformation pipeline"""
        code = """
        val transformed : [_]i32 = for i in 1..100 {
            if i % 3 == 0 {
                if i % 5 == 0 {
                    -> i * 10
                } else {
                    -> i * 3
                }
            } else {
                if i % 5 == 0 {
                    -> i * 5
                } else {
                    -> i
                }
            }
        }
        """
        ast = parser.parse(code)
        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["body"]["statements"][0]["type"] == NodeType.CONDITIONAL_STATEMENT.value

    def test_nested_filtering_complex(self, parser):
        """Test: Complex nested filtering logic"""
        code = """
        val filtered : [_][_]i32 = for i in 1..20 {
            if i > 5 {
                if i < 15 {
                    -> for j in 1..10 {
                        if j % 2 == 0 {
                            if j < 8 {
                                -> i * j
                            }
                        }
                    }
                }
            }
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value


class TestEdgeCaseIntegration:
    """Test edge cases in integrated scenarios."""

    def test_single_element_matrix(self, parser):
        """Test: 1x1 matrix generation"""
        code = """
        val single : [_][_]i32 = for i in 5..=5 {
            -> for j in 10..=10 {
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_empty_rows_filtered(self, parser):
        """Test: All rows filtered out scenario"""
        code = """
        val empty : [_][_]i32 = for i in 1..10 {
            if i > 100 {
                -> for j in 1..5 {
                    -> i * j
                }
            }
        }
        """
        ast = parser.parse(code)
        assert ast["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_deeply_nested_with_all_features(self, parser):
        """Test: Deep nesting with labels, breaks, filtering"""
        code = """
        'outer val complex : [_][_][_]i32 = for i in 1..5 {
            if i % 2 == 0 {
                -> for j in 1..5 {
                    if j > 3 {
                        break 'outer
                    }
                    -> for k in 1..5 {
                        if k == j {
                            -> i + j
                        } else {
                            -> i + j + k
                        }
                    }
                }
            }
        }
        """
        ast = parser.parse(code)
        labeled_outer = ast["statements"][0]
        assert labeled_outer["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled_outer["label"] == "outer"

    def test_large_range_with_early_exit(self, parser):
        """Test: Large range with early termination"""
        code = """
        'search val limited : [_]i32 = for i in 1..1000000 {
            if i > 1000 {
                break 'search
            }
            if is_valid(i) {
                -> i
            }
        }
        """
        ast = parser.parse(code)
        labeled = ast["statements"][0]
        assert labeled["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled["label"] == "search"
