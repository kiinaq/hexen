"""
Test Array Type Conversion Semantic Analysis

Tests for explicit array type conversions (value:[N]T syntax) following
ARRAY_IMPLEMENTATION_PLAN.md Week 2 Part 6 implementation.

Key principles tested:
- Size as structural property (fixed sizes must match exactly)
- Inferred size [_]T as wildcard (accepts any size)
- Element type conversions with explicit syntax
- Dimension flattening with calculated size match
- Combined conversions (flattening + element type change)
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestElementTypeConversion:
    """Test array element type conversions (same dimensions)"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_element_type_conversion(self):
        """Test basic element type conversion i32 → i64"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val converted : [3]i64 = source:[3]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_element_type_conversion_i32_to_f64(self):
        """Test element type conversion i32 → f64"""
        source = """
        func test() : void = {
            val ints : [4]i32 = [10, 20, 30, 40]
            val floats : [4]f64 = ints:[4]f64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_element_type_conversion_f64_to_i32(self):
        """Test element type conversion f64 → i32 (data loss allowed with explicit syntax)"""
        source = """
        func test() : void = {
            val floats : [3]f64 = [1.5, 2.7, 3.9]
            val ints : [3]i32 = floats:[3]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_multidimensional_element_type_conversion(self):
        """Test element type conversion on multidimensional arrays"""
        source = """
        func test() : void = {
            val matrix_i32 : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val matrix_i64 : [2][3]i64 = matrix_i32:[2][3]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_element_type_conversion_f32_to_f64(self):
        """Test element type conversion f32 → f64"""
        source = """
        func test() : void = {
            val small : [5]f32 = [1.0, 2.0, 3.0, 4.0, 5.0]
            val large : [5]f64 = small:[5]f64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_element_type_conversion_in_return(self):
        """Test element type conversion in return statement"""
        source = """
        func convert_to_i64() : [3]i64 = {
            val source : [3]i32 = [10, 20, 30]
            return source:[3]i64
        }
        func test() : void = {
            val result : [3]i64 = convert_to_i64()
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_element_type_conversion_size_mismatch_error(self):
        """Test error when converting with mismatched sizes"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val invalid : [4]i64 = source:[4]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Array size mismatch in type conversion"
        )
        assert_error_contains(
            errors,
            "Dimension 0 mismatch: source has size 3, target expects 4"
        )

    def test_element_type_conversion_without_explicit_syntax_error(self):
        """Test error when attempting implicit element type conversion"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val invalid : [3]i64 = source
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Type mismatch"
        )


class TestInferredSizeWildcard:
    """Test inferred size [_]T wildcard acceptance"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_inferred_size_accepts_any_size(self):
        """Test [_]T accepts any source size"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val inferred : [_]i64 = source:[_]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_with_different_source_sizes(self):
        """Test [_]T wildcard with multiple different source sizes"""
        source = """
        func test() : void = {
            val small : [3]i32 = [1, 2, 3]
            val large : [10]i32 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

            val inferred_small : [_]i64 = small:[_]i64
            val inferred_large : [_]i64 = large:[_]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_multidimensional_single_dim(self):
        """Test inferred size in one dimension of multidimensional array"""
        source = """
        func test() : void = {
            val source : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val inferred : [_][3]i64 = source:[_][3]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_multidimensional_both_dims(self):
        """Test inferred size in both dimensions"""
        source = """
        func test() : void = {
            val source : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val inferred : [_][_]i64 = source:[_][_]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_inferred_size_no_flattening_needed(self):
        """Test inferred size on same-dimension conversion"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val inferred_same : [_]i32 = source
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)


class TestDimensionFlattening:
    """Test dimension flattening with size match validation"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_2d_to_1d_flattening(self):
        """Test basic [2][3] → [6] flattening"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val flat : [6]i32 = matrix:[6]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_3d_to_1d_flattening(self):
        """Test [2][2][2] → [8] flattening"""
        source = """
        func test() : void = {
            val cube : [2][2][2]i32 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
            val flat : [8]i32 = cube:[8]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_3d_to_2d_partial_flattening(self):
        """Test [2][3][4] → [6][4] partial flattening"""
        source = """
        func test() : void = {
            val cube : [2][3][4]i32 = [
                [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
                [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]
            ]
            val partial : [6][4]i32 = cube:[6][4]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_flattening_size_mismatch_error(self):
        """Test error when flattening with incorrect calculated size"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val invalid : [5]i32 = matrix:[5]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Array size mismatch in dimension conversion"
        )
        assert_error_contains(
            errors,
            "6 elements total"
        )
        assert_error_contains(
            errors,
            "5 elements"
        )

    def test_flattening_with_fixed_target_only(self):
        """Test flattening requires fixed target size"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val flat : [6]i32 = matrix:[6]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)


class TestCombinedConversions:
    """Test combined flattening + element type conversions"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_flatten_and_convert_element_type(self):
        """Test [2][3]i32 → [6]i64 (flattening + element type conversion)"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val flat_i64 : [6]i64 = matrix:[6]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_flatten_and_convert_to_float(self):
        """Test [2][2]i32 → [4]f64 (flattening + int to float)"""
        source = """
        func test() : void = {
            val matrix : [2][2]i32 = [[1, 2], [3, 4]]
            val flat_floats : [4]f64 = matrix:[4]f64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_partial_flatten_and_convert(self):
        """Test [2][3][4]i32 → [6][4]f32 (partial flattening + conversion)"""
        source = """
        func test() : void = {
            val cube : [2][3][4]i32 = [
                [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
                [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]
            ]
            val partial_f32 : [6][4]f32 = cube:[6][4]f32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_flatten_with_fixed_size_and_convert(self):
        """Test [2][3]i32 → [6]f64 (fixed flattening + conversion)"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val flat_floats : [6]f64 = matrix:[6]f64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_combined_conversion_size_mismatch_error(self):
        """Test error when combined conversion has size mismatch"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val invalid : [5]f64 = matrix:[5]f64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Array size mismatch in dimension conversion"
        )


class TestConversionErrorCases:
    """Test error cases for array type conversions"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_fixed_size_mismatch_same_dimensions(self):
        """Test error when fixed sizes don't match (same dimensionality)"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val invalid : [4]i32 = source:[4]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Array size mismatch in type conversion"
        )
        assert_error_contains(
            errors,
            "Fixed-size dimensions must match exactly"
        )

    def test_multidimensional_size_mismatch(self):
        """Test error when multidimensional sizes don't match"""
        source = """
        func test() : void = {
            val source : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val invalid : [2][4]i32 = source:[2][4]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Array size mismatch in type conversion"
        )

    def test_flattening_incorrect_calculation(self):
        """Test error when flattening calculation is wrong"""
        source = """
        func test() : void = {
            val matrix : [3][4]i32 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
            val invalid : [10]i32 = matrix:[10]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Array size mismatch in dimension conversion"
        )
        assert_error_contains(
            errors,
            "12 elements total"
        )

    def test_invalid_element_type_conversion(self):
        """Test error when element type conversion is invalid"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val invalid : [3]bool = source:[3]bool
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Invalid element type conversion in array conversion"
        )

    def test_non_array_to_array_conversion_error(self):
        """Test error when trying to convert non-array to array type"""
        source = """
        func test() : void = {
            val number : i32 = 42
            val invalid : [3]i32 = number:[3]i32
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should get an error about type mismatch or invalid conversion
        assert len(errors) > 0


class TestComptimeArrayConversions:
    """Test conversions involving comptime arrays"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_array_to_concrete_no_conversion_needed(self):
        """Test comptime arrays adapt without explicit conversion"""
        source = """
        func test() : void = {
            val comptime_arr = [1, 2, 3]
            val concrete : [3]i32 = comptime_arr
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_comptime_array_adapts_to_different_element_types(self):
        """Test comptime array adapts to different concrete types"""
        source = """
        func test() : void = {
            val comptime_arr = [1, 2, 3]
            val as_i32 : [3]i32 = comptime_arr
            val as_i64 : [3]i64 = comptime_arr
            val as_f64 : [3]f64 = comptime_arr
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_comptime_array_no_explicit_conversion_needed(self):
        """Test comptime arrays don't need explicit conversion (adapt automatically)"""
        source = """
        func test() : void = {
            val comptime_arr = [1, 2, 3]
            val as_i64 : [3]i64 = comptime_arr
            val as_f64 : [3]f64 = comptime_arr
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)


class TestConversionInExpressions:
    """Test array type conversions in various expression contexts"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_conversion_then_function_call(self):
        """Test array conversion then use in function call"""
        source = """
        func process(data: [3]i64) : void = {
            return
        }
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val converted : [3]i64 = source:[3]i64
            process(converted[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_conversion_in_return_statement(self):
        """Test array conversion in return statement"""
        source = """
        func convert() : [4]f64 = {
            val ints : [4]i32 = [10, 20, 30, 40]
            return ints:[4]f64
        }
        func test() : void = {
            val result : [4]f64 = convert()
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_conversion_in_assignment(self):
        """Test array conversion in simple assignment"""
        source = """
        func test() : void = {
            val source : [3]i32 = [1, 2, 3]
            val converted : [3]i64 = source:[3]i64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_chained_conversions(self):
        """Test multiple sequential conversions"""
        source = """
        func test() : void = {
            val source : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            val step1 : [6]i32 = source:[6]i32
            val step2 : [6]i64 = step1:[6]i64
            val step3 : [6]f64 = step2:[6]f64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)
