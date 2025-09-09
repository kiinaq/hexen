"""
Test Multidimensional Array Semantic Analysis

Tests for multidimensional array literal validation and structure consistency
with end-to-end Hexen source code.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestMultidimensionalArrays:
    """Test multidimensional array semantic analysis with real Hexen source code"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_2d_array_literal(self):
        """Test 2D array literal with consistent structure"""
        source = """
        func test() : void = {
            val matrix = [[1, 2], [3, 4]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with consistent 2D structure
        assert_no_errors(errors)

    def test_3d_array_literal(self):
        """Test 3D array literal with consistent structure"""
        source = """
        func test() : void = {
            val cube = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with consistent 3D structure
        assert_no_errors(errors)

    def test_inconsistent_2d_structure_error(self):
        """Test error detection for inconsistent 2D array structure"""
        source = """
        func test() : void = {
            val inconsistent = [[1, 2], [3]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect inconsistent inner array dimensions
        assert_error_contains(errors, "Inconsistent inner array dimensions")

    def test_mixed_2d_structure_error(self):
        """Test error detection for mixed array/non-array elements"""
        source = """
        func test() : void = {
            val mixed = [[1, 2], 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect non-array element in multidimensional array
        assert_error_contains(
            errors, "is not an array in multidimensional array literal"
        )

    def test_empty_2d_array_rows(self):
        """Test 2D array with empty rows (consistent structure)"""
        source = """
        func test() : void = {
            val empty_rows = [[], []]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with consistently empty rows
        assert_no_errors(errors)

    def test_rectangular_matrix(self):
        """Test rectangular (non-square) matrix"""
        source = """
        func test() : void = {
            val rectangular = [[1, 2, 3], [4, 5, 6]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with rectangular matrices
        assert_no_errors(errors)

    def test_single_row_matrix(self):
        """Test single-row matrix (edge case)"""
        source = """
        func test() : void = {
            val single_row = [[1, 2, 3]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with single-row matrices
        assert_no_errors(errors)

    def test_large_3d_array(self):
        """Test larger 3D array structure"""
        source = """
        func test() : void = {
            val large_cube = [
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
            ]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should work with larger consistent 3D structure
        assert_no_errors(errors)

    def test_deeply_inconsistent_3d_error(self):
        """Test error detection in deeply nested inconsistent structure"""
        source = """
        func test() : void = {
            val bad_cube = [
                [[1, 2], [3, 4]],
                [[5, 6, 7], [8, 9]]
            ]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect inconsistent inner structure
        assert_error_contains(errors, "Inconsistent inner array dimensions")

    def test_deeply_inconsistent_3d_error_detailed(self):
        """Test error detection in deeply nested inconsistent structure"""
        source = """
        func test() : void = {
            val bad_cube = [
                [[1, 2], [3, 4]],
                [[5, 6, 7], [8, 9]]
            ]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect inconsistent inner structure in 3D arrays
        assert_error_contains(errors, "Inconsistent inner array dimensions")


class TestArrayFlattening:
    """Test array flattening functionality (basic implementation)"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_2d_flattening_concept(self):
        """Test that 2D arrays can conceptually be flattened (validation test)"""
        source = """
        func test() : void = {
            val matrix = [[1, 2], [3, 4]]
            // In full implementation, this would be: val flattened : [4]i32 = flatten(matrix)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Basic 2D array should parse and analyze correctly
        assert_no_errors(errors)


if __name__ == "__main__":
    pytest.main([__file__])
