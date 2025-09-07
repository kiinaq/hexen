"""
Test Array Literal Semantic Analysis

Tests for array literal type inference, validation, and integration
with the existing comptime type system using end-to-end Hexen source code.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains, assert_error_count


class TestArrayLiteralSemantics:
    """Test semantic analysis of array literals with real Hexen source code"""
    
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
        
        # Should work with comptime array int inference
        assert_no_errors(errors)
    
    def test_comptime_array_float_inference(self):
        """Test comptime_array_float inference from mixed numeric literals"""
        source = """
        func test() : void = {
            val mixed = [42, 3.14]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with comptime array float promotion
        assert_no_errors(errors)
    
    def test_comptime_array_flexibility(self):
        """Test comptime arrays adapt to different contexts"""
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
        
        # Comptime arrays should adapt to all numeric contexts
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
    
    def test_empty_array_with_context(self):
        """Test empty array literal with explicit context works"""
        source = """
        func test() : void = {
            val empty : [0]i32 = []
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with explicit context
        assert_no_errors(errors)
    
    def test_context_driven_resolution(self):
        """Test array literal resolution with explicit context"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Context-driven resolution should work
        assert_no_errors(errors)
    
    def test_array_size_mismatch_error(self):
        """Test error when array size doesn't match context"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should detect size mismatch
        assert_error_contains(errors, "Array size mismatch: expected 3 elements, got 2")
    
    def test_mixed_concrete_types_error(self):
        """Test error for mixed concrete/comptime types without context"""
        source = """
        func test(x: i32) : void = {
            val mixed = [1, x]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should require explicit context for mixed types
        assert_error_contains(errors, "Mixed concrete/comptime element types require explicit array context")
    
    def test_mixed_concrete_types_with_context(self):
        """Test mixed concrete/comptime types work with explicit context"""
        source = """
        func test(x: i32) : void = {
            val mixed : [2]i32 = [1, x]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should work with explicit context
        assert_no_errors(errors)
    
    
    def test_array_literals_in_function_parameters(self):
        """Test array literals in function call parameters"""
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
        
        # Function parameter context should work
        assert_no_errors(errors)
    
    def test_array_literals_in_return_statements(self):
        """Test array literals in return statements"""
        source = """
        func create_array() : [3]i32 = {
            return [1, 2, 3]
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Return type context should work
        assert_no_errors(errors)
    
    def test_array_literals_with_expressions(self):
        """Test array literals containing expressions"""
        source = """
        func test() : void = {
            val computed = [1 + 2, 3 * 4, 5 / 2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Expression elements should work
        assert_no_errors(errors)
    
    def test_large_array_literals(self):
        """Test arrays with many elements"""
        source = """
        func test() : void = {
            val many = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Large arrays should work
        assert_no_errors(errors)
    
    def test_type_mismatch_in_context(self):
        """Test type mismatch with explicit context"""
        source = """
        func test() : void = {
            val strings : [2]i32 = ["hello", "world"]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Should detect type mismatch
        assert_error_contains(errors, "type mismatch")
    
    def test_comptime_array_type_adaptation(self):
        """Test comptime arrays adapt to different explicit type contexts"""
        source = """
        func test() : void = {
            val flexible = [1, 2, 3]
            val as_i32 : [3]i32 = flexible
            val as_i64 : [3]i64 = flexible
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        
        # Comptime arrays should adapt to all numeric contexts
        assert_no_errors(errors)
    
    def test_array_function_parameters(self):
        """Test array literals as function parameters"""
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
        
        # Function parameter context should work
        assert_no_errors(errors)


if __name__ == "__main__":
    pytest.main([__file__])