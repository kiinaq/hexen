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

        assert_error_contains(
            errors,
            "Cannot use copy operator [..] on non-array type"
        )

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

        assert_error_contains(
            errors,
            "Cannot use copy operator [..] on non-array type"
        )


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
            errors,
            "Property 'length' is only available on array types"
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
            errors,
            "Property 'length' is only available on array types"
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

        assert_error_contains(
            errors,
            "Property 'unknown' not found on type"
        )


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
