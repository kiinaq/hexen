"""
Test Array Operations Semantic Analysis

Tests for array copy ([..]) and property access (.length) semantic analysis
using end-to-end Hexen source code.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestArrayCopy:
    """Test semantic analysis of array copy operations ([..])"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_array_copy(self):
        """Test basic array copy preserves type"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val copy : [3]i32 = source[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_array_copy_type_preservation(self):
        """Test array copy preserves exact array type"""
        source = """
        func test() : void = {
            val floats : [5]f64 = [1.0, 2.0, 3.0, 4.0, 5.0]
            val copy : [5]f64 = floats[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_array_copy_comptime_array(self):
        """Test array copy on comptime arrays"""
        source = """
        func test() : void = {
            val source = [10, 20, 30]
            val copy : [3]i32 = source[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_array_copy_multidimensional(self):
        """Test array copy on multidimensional arrays"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val copy : [2][3]i32 = matrix[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_array_copy_of_array_access(self):
        """Test copying result of array access (row copy)"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val row : [3]i32 = matrix[0][..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_array_copy_in_return_statement(self):
        """Test array copy in return statements"""
        source = """
        func get_copy() : [3]i32 = {
            val data : [3]i32 = [1, 2, 3]
            return data[..]
        }
        func main() : void = {
            val result : [3]i32 = get_copy()
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_copy_non_array_error(self):
        """Test error when using [..] on non-array type"""
        source = """
        func test() : void = {
            val number : i32 = 42
            val invalid = number[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # After range system migration: [..] is now range indexing, not a separate operator
        assert_error_contains(errors, "Cannot index non-array type")

    def test_copy_string_error(self):
        """Test error when using [..] on string type"""
        source = """
        func test() : void = {
            val text : string = "hello"
            val invalid = text[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # After range system migration: [..] is now range indexing, not a separate operator
        assert_error_contains(errors, "Cannot index non-array type")


class TestPropertyAccess:
    """Test semantic analysis of property access (.length)"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_length_property(self):
        """Test basic .length property access on arrays"""
        source = """
        func test() : void = {
            val arr : [5]i32 = [1, 2, 3, 4, 5]
            val size : i32 = arr.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_property_comptime_int(self):
        """Test .length returns comptime_int that adapts"""
        source = """
        func test() : void = {
            val arr : [3]f64 = [1.0, 2.0, 3.0]
            val size_i32 : i32 = arr.length
            val size_i64 : i64 = arr.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_property_in_expression(self):
        """Test .length property in arithmetic expressions"""
        source = """
        func test() : void = {
            val arr : [10]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val last_index : i32 = arr.length - 1
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_property_in_comparison(self):
        """Test .length property in comparison operations"""
        source = """
        func test() : void = {
            val arr : [5]i32 = [1, 2, 3, 4, 5]
            val check : bool = arr.length > 0
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_of_array_access(self):
        """Test .length on result of array access (row length)"""
        source = """
        func test() : void = {
            val matrix : [2][4]i32 = [[1, 2, 3, 4], [5, 6, 7, 8]]
            val row_len : i32 = matrix[0].length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_property_comptime_array(self):
        """Test .length on comptime arrays"""
        source = """
        func test() : void = {
            val arr = [1, 2, 3, 4]
            val size : i32 = arr.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_on_non_array_error(self):
        """Test error when using .length on non-array type"""
        source = """
        func test() : void = {
            val number : i32 = 42
            val invalid = number.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors, "Property 'length' is only available on array types"
        )

    def test_length_on_string_error(self):
        """Test error when using .length on string type"""
        source = """
        func test() : void = {
            val text : string = "hello"
            val invalid = text.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors, "Property 'length' is only available on array types"
        )

    def test_unknown_property_error(self):
        """Test error for unknown property access"""
        source = """
        func test() : void = {
            val arr : [3]i32 = [1, 2, 3]
            val invalid = arr.unknown
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "Property 'unknown' not found on type")


class TestCombinedOperations:
    """Test combined array copy and property access operations"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_copy_then_length(self):
        """Test chaining copy and length: arr[..].length"""
        source = """
        func test() : void = {
            val arr : [5]i32 = [1, 2, 3, 4, 5]
            val size : i32 = arr[..].length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_access_then_copy_then_length(self):
        """Test complex chain: matrix[i][..].length"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val row_size : i32 = matrix[0][..].length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_multidimensional_access_then_length(self):
        """Test multidimensional access then length"""
        source = """
        func test() : void = {
            val cube : [2][3][4]i32 = [
                [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
                [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]
            ]
            val depth : i32 = cube[0][0].length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_in_conditional(self):
        """Test .length in conditional expressions"""
        source = """
        func test() : void = {
            val arr : [10]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            if arr.length > 5 {
                val temp : i32 = 1
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_multiple_arrays_different_lengths(self):
        """Test .length on multiple arrays with different sizes"""
        source = """
        func test() : void = {
            val small : [3]i32 = [1, 2, 3]
            val large : [10]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val total : i32 = small.length + large.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)


class TestRangeSlicingIntegration:
    """
    Test range-based array slicing integrated with array copy operations.

    Focus: How range indexing [start..end] combines with array copy [..]
    from the array operations perspective.

    Complementary to tests/semantic/ranges/test_range_indexing.py which
    tests range indexing from the range system perspective.
    """

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_range_slice_then_full_copy(self):
        """Test range slice followed by full array copy"""
        source = """
        func test() : void = {
            val matrix : [_][_]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            val rows_slice : [_][_]i32 = matrix[0..2][..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range slice returns array, then [..] copies it
        assert_no_errors(errors)

    def test_range_slice_with_property_access(self):
        """Test range slice followed by .length property"""
        source = """
        func test() : void = {
            val data : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val slice : [_]i32 = data[2..8]
            val slice_len : i32 = slice.length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range slice produces array, .length works on result
        assert_no_errors(errors)

    def test_range_slice_inline_length(self):
        """Test .length directly on range slice result"""
        source = """
        func test() : void = {
            val data : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val len : i32 = data[2..8].length
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should be able to chain range slice with .length
        assert_no_errors(errors)

    def test_full_copy_then_range_slice(self):
        """Test full array copy followed by range slice"""
        source = """
        func test() : void = {
            val source : [_]i32 = [1, 2, 3, 4, 5]
            val copied : [_]i32 = source[..]
            val sliced : [_]i32 = copied[1..4]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Copy entire array, then slice the copy
        assert_no_errors(errors)

    def test_nested_range_slicing(self):
        """Test range slicing on multidimensional arrays"""
        source = """
        func test() : void = {
            val matrix : [_][_]i32 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
            val sub_matrix : [_][_]i32 = matrix[0..2]
            val row : [_]i32 = sub_matrix[0][..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range slice outer dimension, then copy inner row
        assert_no_errors(errors)

    def test_range_slice_with_step_then_copy(self):
        """Test stepped range slice followed by copy"""
        source = """
        func test() : void = {
            val data : [_]i32 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            val evens : [_]i32 = data[0..10:2][..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Stepped range slice produces array, then copy
        assert_no_errors(errors)

    def test_unbounded_from_range_slice(self):
        """Test unbounded from range slice: arr[5..]"""
        source = """
        func test() : void = {
            val data : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val tail : [_]i32 = data[5..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Unbounded from slice should work
        assert_no_errors(errors)

    def test_unbounded_to_range_slice(self):
        """Test unbounded to range slice: arr[..5]"""
        source = """
        func test() : void = {
            val data : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val head : [_]i32 = data[..5]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Unbounded to slice should work
        assert_no_errors(errors)

    def test_full_range_equals_copy(self):
        """Test full unbounded range [..] is equivalent to [..]"""
        source = """
        func test() : void = {
            val source : [_]i32 = [1, 2, 3, 4, 5]
            val copy1 : [_]i32 = source[..]
            val copy2 : [_]i32 = source[..]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Both syntaxes should work equivalently
        assert_no_errors(errors)

    def test_range_slice_preserves_element_type(self):
        """Test range slice preserves array element type"""
        source = """
        func test() : void = {
            val floats : [_]f64 = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6]
            val slice : [_]f64 = floats[1..5]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Slice should preserve f64 element type
        assert_no_errors(errors)

    def test_range_slice_comptime_range_adaptation(self):
        """Test comptime range literal adapts to usize for indexing"""
        source = """
        func test() : void = {
            val data : [_]i32 = [10, 20, 30, 40, 50]
            val slice : [_]i32 = data[1..4]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Comptime range 1..4 should adapt to range[usize]
        assert_no_errors(errors)

    def test_range_slice_in_function_call(self):
        """Test passing range-sliced array to function"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func test() : void = {
            val source : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8]
            process(source[2..6][..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range slice result requires explicit [..] for function parameter
        assert_no_errors(errors)

    def test_range_slice_in_return(self):
        """Test returning range-sliced array"""
        source = """
        func get_middle() : [_]i32 = {
            val data : [_]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            return data[3..7]
        }

        func test() : void = {
            val middle : [_]i32 = get_middle()
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Range slice should work in return statement
        assert_no_errors(errors)

    def test_chained_range_slices(self):
        """Test multiple sequential range slices"""
        source = """
        func test() : void = {
            val data : [_]i32 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            val first_slice : [_]i32 = data[2..8]
            val second_slice : [_]i32 = first_slice[1..4]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should be able to slice a slice
        assert_no_errors(errors)
