"""
Tests for inferred-size array parameter support ([_]T).

Tests that inferred-size parameters accept any array size and provide
compile-time .length property access within functions.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer

from .. import assert_no_errors, assert_error_contains


class TestInferredSizeParameterMatching:
    """Test that [_]T parameters accept any size array"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_inferred_size_accepts_small_array(self):
        """[_]T parameter accepts small array"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [3]i32 = [1, 2, 3]
            process(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_accepts_large_array(self):
        """[_]T parameter accepts large array"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [100]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                   11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                   21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                                   31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                                   41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                   51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                                   61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
                                   71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
                                   81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
                                   91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
            process(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_multiple_sizes_same_function(self):
        """Same [_]T function can accept different sizes"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func main() : void = {
            val arr1 : [3]i32 = [1, 2, 3]
            val arr2 : [5]i32 = [1, 2, 3, 4, 5]
            process(arr1[..])
            process(arr2[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_element_type_must_match(self):
        """[_]T requires matching element types"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [3]f64 = [1.0, 2.0, 3.0]
            process(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "element type")
        assert_error_contains(errors, "[_]i32")
        assert_error_contains(errors, "[3]f64")

    def test_inferred_size_comptime_arrays_work(self):
        """Comptime arrays work with [_]T parameters"""
        source = """
        func process(data: [_]i32) : void = {
            return
        }

        func main() : void = {
            process([1, 2, 3])
            process([1, 2, 3, 4, 5])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)


class TestMultidimensionalInferredSize:
    """Test inferred-size with multidimensional arrays"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_2d_first_dimension_inferred(self):
        """[_][N]T accepts different row counts"""
        source = """
        func process(matrix: [_][3]i32) : void = {
            return
        }

        func main() : void = {
            val mat2 : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val mat4 : [4][3]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
            process(mat2[..])
            process(mat4[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_2d_second_dimension_inferred(self):
        """[N][_]T accepts different column counts"""
        source = """
        func process(matrix: [2][_]i32) : void = {
            return
        }

        func main() : void = {
            val mat3 : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val mat5 : [2][5]i32 = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
            process(mat3[..])
            process(mat5[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_2d_both_dimensions_inferred(self):
        """[_][_]T accepts any 2D array"""
        source = """
        func process(matrix: [_][_]i32) : void = {
            return
        }

        func main() : void = {
            val mat2x3 : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val mat4x5 : [4][5]i32 = [[1, 2, 3, 4, 5],
                                       [6, 7, 8, 9, 10],
                                       [11, 12, 13, 14, 15],
                                       [16, 17, 18, 19, 20]]
            process(mat2x3[..])
            process(mat4x5[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_2d_column_count_must_match_if_fixed(self):
        """[_][3]i32 rejects [N][4]i32"""
        source = """
        func process(matrix: [_][3]i32) : void = {
            return
        }

        func main() : void = {
            val mat : [2][4]i32 = [[1, 2, 3, 4], [5, 6, 7, 8]]
            process(mat[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "size mismatch")


class TestLengthPropertyWithInferredSize:
    """Test .length property access for inferred-size parameters"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_length_property_available_in_function(self):
        """[_]T parameters provide .length property"""
        source = """
        func get_length(data: [_]i32) : i32 = {
            return data.length
        }

        func main() : void = {
            val arr : [5]i32 = [1, 2, 3, 4, 5]
            val len : i32 = get_length(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_in_conditional(self):
        """Use .length in conditional expressions"""
        source = """
        func check_size(numbers: [_]i32) : i32 = {
            val len : i32 = numbers.length
            val result : i32 = if len > 5 {
                -> 1
            } else {
                -> 0
            }
            return result
        }

        func main() : void = {
            val arr : [3]i32 = [10, 20, 30]
            val result : i32 = check_size(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_length_in_expression(self):
        """Use .length in arithmetic expressions"""
        source = """
        func avg_size(a: [_]i32, b: [_]i32) : i32 = {
            val total : i32 = a.length + b.length
            return total
        }

        func main() : void = {
            val arr1 : [3]i32 = [1, 2, 3]
            val arr2 : [5]i32 = [1, 2, 3, 4, 5]
            val avg : i32 = avg_size(arr1[..], arr2[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_multidimensional_inferred_length(self):
        """[_][_]T can access .length for first dimension"""
        source = """
        func count_rows(matrix: [_][_]i32) : i32 = {
            return matrix.length
        }

        func main() : void = {
            val mat : [3][4]i32 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
            val rows : i32 = count_rows(mat[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)
