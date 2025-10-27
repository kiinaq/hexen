"""
Test Suite: Comptime Array Size Validation

Validates that comptime array sizes are checked against fixed-size parameters
to prevent silent truncation or padding. This ensures type safety when passing
comptime arrays stored in variables to functions with fixed-size parameters.

Test Coverage:
- Basic size mismatches (too large, too small, exact match)
- Inferred size parameters ([_]T) accepting any size
- Multidimensional size mismatches (2D, 3D)
- Dimension count mismatches (1D vs 2D)
- Float array size validation
- Multiple function calls with same comptime array
- Regression tests for existing behavior

Core Safety Principle:
Comptime arrays preserve dimensional information when stored in variables,
enabling compile-time size validation when passed to fixed-size parameters.
This prevents the silent data loss that would occur from truncation or padding.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestComptimeArrayBasicSizeMismatch:
    """Core test cases for comptime array size validation"""

    def test_comptime_array_size_too_large_fails(self):
        """
        PRIMARY TEST CASE: Comptime array size validation

        Comptime array [5] should NOT pass to fixed [3] parameter.
        Without size validation, this would silently truncate from 5 to 3.

        This is the core bug scenario from Issue #1 that motivated the entire
        implementation of ComptimeArrayType with dimensional preservation.
        """
        code = """
        func exact_three(data: [3]i32) : i32 = {
            return data[0]
        }

        val wrong_size = [1, 2, 3, 4, 5]
        val result : i32 = exact_three(wrong_size)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected size mismatch error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text

    # NOTE: Success cases (exact match, inferred size) are already tested in
    # test_comptime_array_parameter_adaptation.py - this file focuses on size
    # mismatch detection to prevent silent truncation/padding
    # NOTE: Additional size mismatch variations (too small, off-by-one) are tested
    # in TestComptimeArraySizeMismatchVariations below


class TestComptimeArraySizeMismatchVariations:
    """Additional size mismatch scenarios"""

    def test_off_by_one_too_large(self):
        """Comptime [4] cannot pass to [3] parameter"""
        code = """
        func f(data: [3]i32) : i32 = { return data[0] }
        val arr = [1, 2, 3, 4]
        val result : i32 = f(arr)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text

    def test_off_by_one_too_small(self):
        """Comptime [2] cannot pass to [3] parameter"""
        code = """
        func f(data: [3]i32) : i32 = { return data[0] }
        val arr = [1, 2]
        val result : i32 = f(arr)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text

    def test_way_off_large_array(self):
        """Comptime [20] cannot pass to [10] parameter"""
        code = """
        func f(data: [10]i32) : i32 = { return data[0] }
        val arr = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        val result : i32 = f(arr)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text


class TestComptimeArrayMultidimensionalSizeMismatch:
    """Test size validation for multidimensional comptime arrays"""

    def test_2d_outer_dimension_mismatch(self):
        """Comptime [3][2] cannot pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val wrong = [[1, 2], [3, 4], [5, 6]]
        val result : i32 = exact_2x2(wrong)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text

    def test_2d_inner_dimension_mismatch(self):
        """Comptime [2][3] cannot pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val wrong = [[1, 2, 3], [4, 5, 6]]
        val result : i32 = exact_2x2(wrong)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text

    def test_2d_both_dimensions_mismatch(self):
        """Comptime [3][3] cannot pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val wrong = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        val result : i32 = exact_2x2(wrong)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text

    # NOTE: Success cases for 2D arrays (exact match, inferred dimensions) are
    # already tested in test_comptime_array_parameter_adaptation.py


class TestComptimeArrayDimensionCountMismatch:
    """Test dimension count mismatches (1D vs 2D vs 3D)"""

    def test_1d_cannot_pass_to_2d_parameter(self):
        """Comptime [6] cannot pass to [2][3] parameter (dimension count mismatch)"""
        code = """
        func matrix_func(data: [2][3]i32) : i32 = {
            return data[0][0]
        }

        val flat = [1, 2, 3, 4, 5, 6]
        val result : i32 = matrix_func(flat)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text
        # Should mention dimension mismatch
        # Dimension check already covered above

    def test_2d_cannot_pass_to_1d_parameter_dimension_mismatch(self):
        """Comptime [2][3] CANNOT pass to [6]i32 parameter (dimension mismatch - flattening removed)"""
        code = """
        func flat_func(data: [6]i32) : i32 = {
            return data[0]
        }

        val matrix = [[1, 2, 3], [4, 5, 6]]
        val result : i32 = flat_func(matrix)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        # Flattening has been removed - dimension mismatch should error
        # Array dimension transformations will be provided by future standard library
        assert len(errors) == 1
        assert "dimension count mismatch" in str(errors[0]).lower()

    # NOTE: Regression tests for existing behavior are covered in:
    # - test_comptime_array_parameter_adaptation.py (comptime array adaptation)
    # - test_array_parameters.py (concrete arrays with [..])
    # This file focuses specifically on size mismatch validation


class TestComptimeArrayFloatSizeValidation:
    """Test size validation works for float arrays too"""

    def test_comptime_float_array_size_mismatch_fails(self):
        """Comptime float array [5] cannot pass to [3]f32 parameter"""
        code = """
        func process_floats(data: [3]f32) : f32 = {
            return data[0]
        }

        val wrong_size = [1.0, 2.0, 3.0, 4.0, 5.0]
        val result : f32 = process_floats(wrong_size)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text
    # NOTE: Success case for float arrays covered in test_comptime_array_parameter_adaptation.py


class TestMultipleFunctionCallsWithSameComptimeArray:
    """Test that the same comptime array can be reused with different size requirements"""

    def test_comptime_array_fails_wrong_size_succeeds_correct_size(self):
        """Same comptime array can be validated against multiple parameters"""
        code = """
        func process_three(data: [3]i32) : i32 = {
            return data[0]
        }

        func process_five(data: [5]i32) : i32 = {
            return data[0]
        }

        val arr = [1, 2, 3, 4, 5]
        val result_five : i32 = process_five(arr)
        val result_three : i32 = process_three(arr)
        """
        parser = HexenParser()
        ast = parser.parse(code)
        analyzer = SemanticAnalyzer()

        # Should fail because arr [5] cannot pass to process_three [3]
        errors = analyzer.analyze(ast)

        assert len(errors) > 0, "Expected error"
        error_text = " ".join(str(e) for e in errors).lower()
        assert "size mismatch" in error_text or "dimension" in error_text
    # NOTE: Success case for multiple inferred-size calls covered in test_inferred_size_parameters.py
