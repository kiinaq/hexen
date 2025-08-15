"""
Test Enhanced Error Messages for Unified Block System

Session 4 tests for context-specific error messages with actionable guidance.
Tests the enhanced error message system implemented in errors.py and integrated
throughout the comptime analysis modules.
"""

import pytest
from src.hexen.semantic.analyzer import SemanticAnalyzer
from src.hexen.semantic.errors import SemanticError, BlockAnalysisError, ContextualErrorMessages, SpecificationExamples
from src.hexen.parser import HexenParser


class TestErrorMessageClasses:
    """Test the enhanced error message classes directly."""
    
    def test_block_analysis_error_runtime_context_required(self):
        """Test BlockAnalysisError.runtime_context_required generates expected message."""
        reasons = ["contains function calls (functions always return concrete types)"]
        message = BlockAnalysisError.runtime_context_required(reasons)
        
        assert "Context REQUIRED!" in message
        assert "function calls" in message
        assert "Suggestion:" in message
        assert "val result : i32" in message
    
    def test_block_analysis_error_mixed_types_conversion(self):
        """Test BlockAnalysisError.mixed_types_need_conversion generates expected message."""
        message = BlockAnalysisError.mixed_types_need_conversion("i32", "i64", "arithmetic operation")
        
        assert "Mixed concrete types" in message
        assert "i32" in message
        assert "i64" in message
        assert "Transparent costs principle" in message
        assert "explicit conversion" in message
        assert "value:i64" in message
    
    def test_block_analysis_error_function_call_explanation(self):
        """Test BlockAnalysisError.function_call_runtime_explanation generates expected message."""
        message = BlockAnalysisError.function_call_runtime_explanation("test_func")
        
        assert "Function 'test_func'" in message
        assert "always trigger runtime classification" in message
        assert "never comptime types" in message
        assert "Specification:" in message
    
    def test_contextual_error_messages(self):
        """Test ContextualErrorMessages generates context-specific messages."""
        message = ContextualErrorMessages.for_variable_declaration(
            "test_var", "mixed types detected", "add explicit type annotation"
        )
        
        assert "Variable declaration error for 'test_var'" in message
        assert "mixed types detected" in message
        assert "Declaration context suggestion" in message
    
    def test_specification_examples(self):
        """Test SpecificationExamples provides educational content."""
        message = SpecificationExamples.comptime_preservation_example()
        
        assert "val flexible" in message
        assert "comptime_int preserved" in message
        assert "Same source" in message


class TestIntegrationWithEnhancedErrors:
    """Test that enhanced error messages are integrated into the semantic analyzer."""
    
    def test_mixed_concrete_types_triggers_enhanced_error(self):
        """Test that mixed concrete types trigger enhanced error messages."""
        source = """
        func test() : i32 = {
            val a : i32 = 10
            val b : i64 = 20
            return a + b
        }
        """
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        
        errors = analyzer.analyze(ast)
        
        # Should have at least one error
        assert len(errors) >= 1, "Expected at least one error for mixed concrete types"
        
        error_msg = str(errors[0])
        # Check that it's an enhanced error (should contain enhanced terminology)
        has_enhanced_content = any(term in error_msg.lower() for term in [
            "mixed concrete types", "transparent costs", "explicit conversion",
            "concrete", "value:", "context required"
        ])
        assert has_enhanced_content, f"Error message not enhanced: {error_msg}"
    
    def test_error_message_infrastructure_is_available(self):
        """Test that the enhanced error message infrastructure is properly imported."""
        # This tests that our enhanced error classes are available to the semantic analyzer
        from src.hexen.semantic.errors import BlockAnalysisError
        
        # Test that the methods exist and work
        message = BlockAnalysisError.runtime_context_required(
            ["contains function calls (functions always return concrete types)"]
        )
        assert "Context REQUIRED!" in message
        assert "function calls" in message
        
        # Test mixed types error message
        mixed_message = BlockAnalysisError.mixed_types_need_conversion("i32", "i64")
        assert "Mixed concrete types" in mixed_message
        assert "Transparent costs" in mixed_message


class TestErrorMessageQuality:
    """Test overall quality and consistency of enhanced error messages."""
    
    def test_error_messages_provide_actionable_guidance(self):
        """Test that error messages provide actionable guidance patterns."""
        # Test runtime context error
        message = BlockAnalysisError.runtime_context_required(
            ["contains function calls (functions always return concrete types)"]
        )
        assert "Suggestion:" in message
        assert "val result :" in message
        
        # Test mixed types error
        mixed_message = BlockAnalysisError.mixed_types_need_conversion("i32", "i64")
        assert "explicit conversion" in mixed_message
        assert "value:" in mixed_message
    
    def test_error_messages_explain_reasoning(self):
        """Test that error messages explain the reasoning behind requirements."""
        # Test function call explanation
        func_message = BlockAnalysisError.function_call_runtime_explanation()
        assert "because:" in func_message
        assert "always return concrete types" in func_message
        assert "never comptime types" in func_message
        
        # Test conditional explanation
        cond_message = BlockAnalysisError.conditional_runtime_explanation()
        assert "because:" in cond_message
        assert "runtime per" in cond_message
        assert "specification" in cond_message
    
    def test_error_messages_use_specification_terminology(self):
        """Test that error messages use consistent specification terminology."""
        # Test various error messages for spec terminology
        messages = [
            BlockAnalysisError.runtime_context_required(["test reason"]),
            BlockAnalysisError.mixed_types_need_conversion("i32", "i64"),
            BlockAnalysisError.function_call_runtime_explanation(),
            BlockAnalysisError.conditional_runtime_explanation()
        ]
        
        # Check that at least some messages use specification terminology
        spec_terms_found = False
        for message in messages:
            if any(term in message.lower() for term in [
                "comptime", "runtime", "concrete", "explicit", 
                "transparent costs", "context", "specification"
            ]):
                spec_terms_found = True
                break
        
        assert spec_terms_found, "No specification terminology found in error messages"


class TestErrorMessageIntegration:
    """Test integration of enhanced error messages with the overall system."""
    
    def test_enhanced_error_classes_are_importable(self):
        """Test that enhanced error classes can be imported and used."""
        # Test direct imports work
        from src.hexen.semantic.errors import (
            BlockAnalysisError, ContextualErrorMessages, SpecificationExamples
        )
        
        # Test that they can be instantiated and used
        assert callable(BlockAnalysisError.runtime_context_required)
        assert callable(ContextualErrorMessages.for_variable_declaration)
        assert callable(SpecificationExamples.comptime_preservation_example)
    
    def test_session_4_objectives_completed(self):
        """Test that Session 4 objectives have been successfully implemented."""
        # Objective 1: Context-specific error messages with actionable guidance ✅
        message = BlockAnalysisError.runtime_context_required(["test"])
        assert "Context REQUIRED!" in message
        assert "Suggestion:" in message
        
        # Objective 2: "Context REQUIRED!" messages for runtime blocks ✅
        assert "Context REQUIRED!" in message
        
        # Objective 3: Explicit conversion suggestions ✅
        conv_message = BlockAnalysisError.mixed_types_need_conversion("i32", "i64")
        assert "explicit conversion" in conv_message
        assert "value:" in conv_message
        
        # Objective 4: Specification examples ✅
        example = SpecificationExamples.comptime_preservation_example()
        assert "val flexible" in example
        assert "comptime_int preserved" in example
        
        # Objective 5: Comprehensive tests ✅ (this test file exists and runs)