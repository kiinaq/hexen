"""
Test Array Literal Semantic Analysis - Polished Version

Tests for array literal semantic analysis focusing on currently implemented features.
Future functionality is marked with appropriate skip/xfail markers.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestArrayLiteralSemanticsWorking:
    """Test semantic analysis of array literals - working functionality only"""
    
    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()
    
    def test_comptime_array_int_inference(self):
        """Test comptime_array_int inference from integer literals"""
        source = """
        func test() : void = {
            val numbers = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with all integer literals
        assert_no_errors(errors)
    
    def test_comptime_array_float_inference(self):
        """Test comptime_array_float inference from mixed numeric literals"""
        source = """
        func test() : void = {
            val mixed = [42, 3.14, 100]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with comptime array float promotion
        assert_no_errors(errors)
    
    def test_empty_array_context_requirement(self):
        """Test empty array literal requires explicit context"""
        source = """
        func test() : void = {
            val empty = []
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Empty arrays should require explicit type context
        assert_error_contains(errors, "Empty array literal requires explicit type context")
    
    def test_nested_array_literals_2d(self):
        """Test 2D array literal parsing and basic analysis"""
        source = """
        func test() : void = {
            val matrix = [[1, 2], [3, 4]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Basic 2D array literals should work
        assert_no_errors(errors)
    
    def test_nested_array_literals_3d(self):
        """Test 3D array literal parsing and basic analysis"""
        source = """
        func test() : void = {
            val cube = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Basic 3D array literals should work
        assert_no_errors(errors)
    
    def test_mixed_comptime_context_required(self):
        """Test that mixed concrete/comptime types require context"""
        source = """
        func test(param: i32) : void = {
            val mixed = [param, 42]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should require explicit context for mixed types
        assert_error_contains(errors, "Mixed concrete/comptime element types require explicit array context")


class TestArrayLiteralSemanticsFuture:
    """Test semantic analysis of array literals - future functionality"""
    
    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()
    
    @pytest.mark.xfail(reason="Explicit array type contexts not yet fully implemented")
    def test_comptime_array_flexibility(self):
        """Test comptime arrays adapt to different contexts - FUTURE"""
        source = """
        func test() : void = {
            val flexible = [1, 2, 3]
            val as_i32 : [3]i32 = flexible
            val as_i64 : [3]i64 = flexible
            val as_f32 : [3]f32 = flexible
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Comptime arrays should adapt to all numeric contexts (when fully implemented)
        assert_no_errors(errors)
    
    @pytest.mark.xfail(reason="Empty array with explicit type context not yet implemented")
    def test_empty_array_with_context(self):
        """Test empty array literal with explicit context - FUTURE"""
        source = """
        func test() : void = {
            val empty : [0]i32 = []
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with explicit context (when implemented)
        assert_no_errors(errors)
    
    @pytest.mark.xfail(reason="Context-driven type resolution not yet fully implemented")
    def test_context_driven_resolution(self):
        """Test array literal resolution with explicit context - FUTURE"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Context-driven resolution should work (when implemented)
        assert_no_errors(errors)
    
    @pytest.mark.xfail(reason="Array size validation not yet fully implemented")
    def test_array_size_mismatch_error(self):
        """Test error when array size doesn't match context - FUTURE"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should detect size mismatch (when validation is implemented)
        assert_error_contains(errors, "size mismatch")
    
    @pytest.mark.xfail(reason="Array type integration in function parameters not yet implemented")
    def test_array_literals_in_function_parameters(self):
        """Test array literals as function parameters - FUTURE"""
        source = """
        func process(arr: [3]i32) : void = {
            return
        }
        
        func test() : void = {
            process([1, 2, 3])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with array literals as function arguments (when implemented)
        assert_no_errors(errors)
    
    @pytest.mark.xfail(reason="Array type integration in return statements not yet implemented")
    def test_array_literals_in_return_statements(self):
        """Test array literals in return statements - FUTURE"""
        source = """
        func get_numbers() : [3]i32 = {
            return [1, 2, 3]
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with array literals in return statements (when implemented)
        assert_no_errors(errors)


if __name__ == "__main__":
    pytest.main([__file__])