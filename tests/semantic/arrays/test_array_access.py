"""
Test Array Access Semantic Analysis

Tests for array access (indexing) operations with end-to-end Hexen source code.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestArrayAccessSemantics:
    """Test semantic analysis of array access operations with real Hexen source code"""
    
    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()
    
    def test_basic_array_access(self):
        """Test basic array access with integer index"""
        source = """
        func test() : void = {
            val numbers = [1, 2, 3]
            val first = numbers[0]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with basic array access
        assert_no_errors(errors)
    
    def test_array_access_with_comptime_index(self):
        """Test array access with comptime integer index"""
        source = """
        func test() : void = {
            val numbers = [10, 20, 30]
            val second = numbers[1]
            val third = numbers[2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with comptime integer indices
        assert_no_errors(errors)
    
    def test_array_access_in_return(self):
        """Test array access in return statement"""
        source = """
        func get_first() : i32 = {
            val numbers = [42, 100, 200]
            return numbers[0]
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with array access in return
        assert_no_errors(errors)
    
    def test_array_access_with_expressions(self):
        """Test array access with expression results"""
        source = """
        func test() : void = {
            val numbers = [1, 2, 3, 4, 5]
            val computed = [10, 20, 30]
            val first_sum = numbers[0] + computed[0]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with array access in expressions
        assert_no_errors(errors)
    
    def test_invalid_string_index(self):
        """Test error for non-integer index"""
        source = """
        func test() : void = {
            val numbers = [1, 2, 3]
            val invalid = numbers["hello"]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should detect invalid index type
        assert_error_contains(errors, "Array index must be an integer type")
    
    def test_float_array_access(self):
        """Test array access on float arrays"""
        source = """
        func test() : void = {
            val floats = [3.14, 2.71, 1.41]
            val pi = floats[0]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with float array access
        assert_no_errors(errors)
    
    def test_nested_array_access_2d(self):
        """Test 2D array access"""
        source = """
        func test() : void = {
            val matrix = [[1, 2], [3, 4]]
            val element = matrix[0][1]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with 2D array access
        assert_no_errors(errors)
    
    def test_array_access_as_function_argument(self):
        """Test array access as function argument"""
        source = """
        func process(x: i32) : void = {
            return
        }
        
        func test() : void = {
            val numbers = [42, 100, 200]
            process(numbers[1])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with array access as function argument
        assert_no_errors(errors)


if __name__ == "__main__":
    pytest.main([__file__])