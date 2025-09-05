"""
Tests for comprehensive array error handling and messages.

This module tests the array-specific error handling system, ensuring
proper error messages and suggestions are provided for common mistakes.
"""

import pytest
from src.hexen.semantic.arrays.error_messages import (
    ArraySemanticError,
    ArrayErrorMessages, 
    ArrayErrorFactory
)


class TestArrayErrorMessages:
    """Test comprehensive error message formatting."""
    
    def test_size_mismatch_message(self):
        """Test array size mismatch error message formatting."""
        message = ArrayErrorMessages.size_mismatch(3, 5, "array assignment")
        
        assert "expected 3 elements, got 5" in message
        assert "array assignment" in message
        assert "size-as-type principle" in message
    
    def test_dimension_mismatch_message(self):
        """Test dimension mismatch error message formatting."""
        message = ArrayErrorMessages.dimension_mismatch(2, 3, "array operation")
        
        assert "expected 2D array, got 3D" in message
        assert "array operation" in message
        assert "same dimensionality" in message
    
    def test_index_out_of_bounds_message(self):
        """Test index out of bounds error message formatting."""
        message = ArrayErrorMessages.index_out_of_bounds(5, 3)
        
        assert "index 5 out of bounds" in message
        assert "array of size 3" in message
        assert "Valid indices: 0 to 2" in message
    
    def test_comptime_conversion_required_message(self):
        """Test comptime conversion required error message."""
        message = ArrayErrorMessages.comptime_conversion_required(
            "comptime_array_float", "[3]i32"
        )
        
        assert "comptime_array_float" in message
        assert "[3]i32" in message
        assert "explicit conversion" in message
        assert "array:[3]i32" in message
    
    def test_empty_array_context_required_message(self):
        """Test empty array context required error message."""
        message = ArrayErrorMessages.empty_array_context_required()
        
        assert "Empty array literal" in message
        assert "explicit type context" in message
        assert "val array : [N]T = []" in message
    
    def test_inconsistent_multidim_structure_message(self):
        """Test inconsistent multidimensional structure error message."""
        message = ArrayErrorMessages.inconsistent_multidim_structure(1, 3, 2)
        
        assert "Row 0 has 3 elements" in message
        assert "row 1 has 2 elements" in message
        assert "same number of columns" in message
    
    def test_invalid_index_type_message(self):
        """Test invalid index type error message."""
        message = ArrayErrorMessages.invalid_index_type("f64")
        
        assert "index must be integer type" in message
        assert "got f64" in message
        assert "i32, i64, comptime_int" in message
    
    def test_non_array_indexing_message(self):
        """Test non-array indexing error message."""
        message = ArrayErrorMessages.non_array_indexing("i32")
        
        assert "Cannot index non-array type: i32" in message
        assert "Only array types support indexing" in message
    
    def test_mixed_concrete_types_message(self):
        """Test mixed concrete types error message."""
        message = ArrayErrorMessages.mixed_concrete_types("[3]i32", "[3]f64", "assignment")
        
        assert "[3]i32" in message
        assert "[3]f64" in message
        assert "assignment" in message
        assert "Transparent costs principle" in message


class TestArraySemanticError:
    """Test ArraySemanticError exception functionality."""
    
    def test_basic_error_creation(self):
        """Test creating basic ArraySemanticError."""
        error = ArraySemanticError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.node is None
        assert error.suggestion is None
    
    def test_error_with_suggestion(self):
        """Test ArraySemanticError with suggestion."""
        error = ArraySemanticError(
            "Size mismatch",
            suggestion="Use array with correct size"
        )
        
        expected = "Size mismatch\nSuggestion: Use array with correct size"
        assert str(error) == expected
        assert error.suggestion == "Use array with correct size"
    
    def test_error_with_node(self):
        """Test ArraySemanticError with AST node."""
        node = {"type": "array_literal", "elements": []}
        error = ArraySemanticError("Test error", node=node)
        
        assert error.node == node
        assert error.message == "Test error"


class TestArrayErrorFactory:
    """Test ArrayErrorFactory for creating specific errors."""
    
    def test_create_size_mismatch_error(self):
        """Test creating size mismatch error via factory."""
        node = {"type": "array_literal"}
        error = ArrayErrorFactory.create_size_mismatch_error(3, 5, "assignment", node)
        
        assert isinstance(error, ArraySemanticError)
        assert "expected 3 elements, got 5" in error.message
        assert "assignment" in error.message
        assert error.node == node
        assert "exactly 3 elements" in error.suggestion
    
    def test_create_bounds_error(self):
        """Test creating index bounds error via factory."""
        error = ArrayErrorFactory.create_bounds_error(5, 3)
        
        assert isinstance(error, ArraySemanticError)
        assert "index 5 out of bounds" in error.message
        assert "size 3" in error.message
        assert "0..2" in error.suggestion
    
    def test_create_empty_context_error(self):
        """Test creating empty array context error via factory."""
        node = {"type": "array_literal", "elements": []}
        error = ArrayErrorFactory.create_empty_context_error(node)
        
        assert isinstance(error, ArraySemanticError)
        assert "Empty array literal" in error.message
        assert error.node == node
        assert "val array : [N]T = []" in error.suggestion
    
    def test_create_inconsistent_structure_error(self):
        """Test creating inconsistent structure error via factory."""
        error = ArrayErrorFactory.create_inconsistent_structure_error(1, 3, 2)
        
        assert isinstance(error, ArraySemanticError)
        assert "Row 0 has 3 elements" in error.message
        assert "row 1 has 2 elements" in error.message
        assert "exactly 3 elements" in error.suggestion
    
    def test_create_invalid_index_type_error(self):
        """Test creating invalid index type error via factory."""
        error = ArrayErrorFactory.create_invalid_index_type_error("f64")
        
        assert isinstance(error, ArraySemanticError)
        assert "got f64" in error.message
        assert "integer types" in error.suggestion


class TestErrorMessageConsistency:
    """Test error message consistency and quality."""
    
    def test_all_messages_have_helpful_content(self):
        """Test that all error messages provide helpful information."""
        # Test a sample of error messages for helpful content
        messages = [
            ArrayErrorMessages.size_mismatch(3, 5, "assignment"),
            ArrayErrorMessages.index_out_of_bounds(10, 5),
            ArrayErrorMessages.invalid_index_type("string"),
            ArrayErrorMessages.empty_array_context_required(),
        ]
        
        for message in messages:
            # Should contain specific details about the error
            assert len(message) > 20  # Not just generic messages
            # Should contain actionable information
            assert any(word in message.lower() for word in 
                      ["expected", "use", "valid", "must", "required"])
    
    def test_error_messages_follow_consistent_format(self):
        """Test that error messages follow consistent formatting."""
        message1 = ArrayErrorMessages.size_mismatch(3, 5, "assignment")
        message2 = ArrayErrorMessages.dimension_mismatch(2, 3, "operation")
        
        # Both should have similar structure (problem description + explanation)
        assert "\n" in message1  # Multi-line with explanation
        assert "\n" in message2
        
        # Should not end with periods (consistent with existing style)
        assert not message1.strip().endswith(".")
        assert not message2.strip().endswith(".")
    
    def test_factory_errors_include_suggestions(self):
        """Test that factory-created errors include helpful suggestions."""
        factory_methods = [
            lambda: ArrayErrorFactory.create_size_mismatch_error(3, 5, "assignment"),
            lambda: ArrayErrorFactory.create_bounds_error(10, 5),
            lambda: ArrayErrorFactory.create_empty_context_error(),
            lambda: ArrayErrorFactory.create_invalid_index_type_error("f64"),
        ]
        
        for create_error in factory_methods:
            error = create_error()
            assert error.suggestion is not None
            assert len(error.suggestion) > 10  # Should be meaningful
            assert not error.suggestion.startswith("Suggestion:")  # Avoid redundancy


if __name__ == "__main__":
    pytest.main([__file__])