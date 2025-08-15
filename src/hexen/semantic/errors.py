"""
Hexen Semantic Error Handling

Error classes and utilities for semantic analysis error reporting.
Provides structured error handling with optional AST node context.

Enhanced with Session 4 context-specific error messages for the unified block system.
"""

from typing import Dict, List, Optional
from .types import HexenType, BlockEvaluability


class SemanticError(Exception):
    """
    Represents a semantic analysis error with optional AST node context.

    Design philosophy:
    - Collect all errors before failing (don't stop at first error)
    - Provide context when available for better error messages
    - Separate from syntax errors (which are caught by parser)

    Future enhancements:
    - Line/column information
    - Error severity levels
    - Suggested fixes
    """

    def __init__(self, message: str, node: Optional[Dict] = None):
        self.message = message
        self.node = node  # AST node where error occurred (for future line/col info)
        super().__init__(message)


class BlockAnalysisError:
    """
    Context-specific error messages for block analysis with actionable guidance.
    
    Implements Session 4 objectives:
    - Context-specific error messages with actionable guidance
    - "Context REQUIRED!" messages for runtime blocks  
    - Explicit conversion suggestions
    - Specification-aligned error messages
    """
    
    @staticmethod
    def runtime_context_required(reasons: List[str], context_type: str = "type annotation") -> str:
        """
        Generate context requirement error with actionable suggestion.
        
        Args:
            reasons: List of reasons why runtime context is required
            context_type: Type of context needed (e.g., "type annotation", "target type")
            
        Returns:
            Detailed error message with specific suggestion
        """
        if not reasons:
            return f"Runtime block requires explicit {context_type}."
            
        reason_text = " and ".join(reasons)
        
        # Context-specific suggestions based on reason type
        if any("function call" in reason for reason in reasons):
            suggestion = f"Add explicit {context_type} like: val result : i32 = {{ /* function call block */ }}"
        elif any("conditional" in reason for reason in reasons):
            suggestion = f"Add explicit {context_type} like: val result : f64 = {{ /* conditional block */ }}"
        elif any("concrete type variable" in reason for reason in reasons):
            suggestion = f"Add explicit {context_type} like: val result : i64 = {{ /* mixed types block */ }}"
        else:
            suggestion = f"Add explicit {context_type} to the target variable"
            
        return (
            f"Context REQUIRED! Runtime block requires explicit {context_type} because it {reason_text}. "
            f"Suggestion: {suggestion}"
        )
    
    @staticmethod
    def mixed_types_need_conversion(from_type: str, to_type: str, operation_context: str = "operation") -> str:
        """
        Generate conversion requirement error with syntax example.
        
        Args:
            from_type: Source type name
            to_type: Target type name  
            operation_context: Context where conversion is needed
            
        Returns:
            Error message with explicit conversion syntax
        """
        return (
            f"Mixed concrete types in {operation_context}: {from_type} incompatible with {to_type}. "
            f"Transparent costs principle requires explicit conversion. "
            f"Use explicit conversion syntax: value:{to_type}"
        )
    
    @staticmethod  
    def branch_type_mismatch(branch_type: str, target_type: str, branch_context: str = "conditional branch") -> str:
        """
        Generate branch type mismatch error with conversion suggestion.
        
        Args:
            branch_type: Type from the problematic branch
            target_type: Expected target type
            branch_context: Context description (e.g., "conditional branch", "assign statement")
            
        Returns:
            Error message with explicit conversion suggestion
        """
        return (
            f"Branch type mismatch in {branch_context}: {branch_type} incompatible with target type {target_type}. "
            f"Use explicit conversion: value:{target_type}"
        )
    
    @staticmethod
    def comptime_preservation_explanation(block_type: str, suggestion: str) -> str:
        """
        Explain comptime type preservation behavior with usage guidance.
        
        Args:
            block_type: Type of block (compile-time or runtime)
            suggestion: Specific usage suggestion
            
        Returns:
            Educational error message explaining comptime preservation
        """
        if block_type == "compile_time":
            return (
                f"Compile-time evaluable blocks preserve comptime types for maximum flexibility. "
                f"This enables the 'one computation, multiple uses' pattern. "
                f"Suggestion: {suggestion}"
            )
        else:
            return (
                f"Runtime blocks require explicit type context for immediate resolution. "
                f"This ensures transparent costs for all runtime operations. "
                f"Suggestion: {suggestion}"
            )
    
    @staticmethod
    def function_call_runtime_explanation(function_name: Optional[str] = None) -> str:
        """
        Explain why function calls trigger runtime classification.
        
        Args:
            function_name: Optional function name for specific context
            
        Returns:
            Explanation of function call runtime behavior
        """
        func_text = f"Function '{function_name}'" if function_name else "Function calls"
        return (
            f"{func_text} always trigger runtime classification because:\n"
            f"1. Functions always return concrete types (never comptime types)\n"
            f"2. Function execution happens at runtime\n"
            f"3. Results cannot be computed at compile-time\n"
            f"Specification: All blocks containing function calls require explicit type context."
        )
    
    @staticmethod
    def conditional_runtime_explanation() -> str:
        """
        Explain why conditionals trigger runtime classification.
        
        Returns:
            Explanation of conditional runtime behavior per CONDITIONAL_SYSTEM.md
        """
        return (
            f"Conditional expressions always trigger runtime classification because:\n"
            f"1. All conditionals are runtime per CONDITIONAL_SYSTEM.md specification\n"
            f"2. Condition evaluation happens at runtime\n"
            f"3. Branch selection cannot be determined at compile-time\n"
            f"Specification: Blocks with conditionals require explicit type context."
        )
    
    @staticmethod
    def ambiguity_resolution_guidance(ambiguous_element: str, resolution_options: List[str]) -> str:
        """
        Provide guidance for resolving type ambiguities.
        
        Args:
            ambiguous_element: What element is ambiguous (e.g., "literal", "expression")
            resolution_options: List of resolution options
            
        Returns:
            Guidance for resolving the ambiguity
        """
        options_text = " or ".join(resolution_options)
        return (
            f"Type ambiguity detected in {ambiguous_element}. "
            f"Multiple interpretations possible. "
            f"Resolution: Provide explicit context using {options_text}. "
            f"This ensures predictable behavior and transparent costs."
        )


class ContextualErrorMessages:
    """
    Context-aware error message generation based on analysis context.
    
    Provides different error messages based on where the error occurs:
    - Variable declaration context
    - Function return context  
    - Expression block context
    - Assignment context
    """
    
    @staticmethod
    def for_variable_declaration(var_name: str, error_details: str, suggestion: str) -> str:
        """Generate error message for variable declaration context."""
        return (
            f"Variable declaration error for '{var_name}': {error_details}. "
            f"Declaration context suggestion: {suggestion}"
        )
    
    @staticmethod
    def for_function_return(func_name: Optional[str], error_details: str, suggestion: str) -> str:
        """Generate error message for function return context."""
        func_text = f"function '{func_name}'" if func_name else "function"
        return (
            f"Function return error in {func_text}: {error_details}. "
            f"Return context suggestion: {suggestion}"
        )
    
    @staticmethod
    def for_expression_block(error_details: str, suggestion: str) -> str:
        """Generate error message for expression block context."""
        return (
            f"Expression block error: {error_details}. "
            f"Block context suggestion: {suggestion}"
        )
    
    @staticmethod
    def for_assignment(target: str, error_details: str, suggestion: str) -> str:
        """Generate error message for assignment context."""
        return (
            f"Assignment error to '{target}': {error_details}. "
            f"Assignment context suggestion: {suggestion}"
        )


class SpecificationExamples:
    """
    Error messages that reference specification examples for educational purposes.
    
    Helps developers understand the unified block system by referencing
    concrete examples from the specification documents.
    """
    
    @staticmethod
    def comptime_preservation_example() -> str:
        """Provide example of comptime type preservation."""
        return (
            "Example of comptime preservation:\n"
            "val flexible = { val calc = 42 + 100; assign calc }  // comptime_int preserved\n"
            "val as_i32 : i32 = flexible  // Same source → i32\n"
            "val as_f64 : f64 = flexible  // Same source → f64"
        )
    
    @staticmethod
    def runtime_context_example() -> str:
        """Provide example of runtime context requirement."""
        return (
            "Example of runtime context requirement:\n"
            "val result : i32 = { val x = get_input(); assign x * 2 }  // Context required\n"
            "// Function call triggers runtime → explicit type needed"
        )
    
    @staticmethod
    def mixed_types_example() -> str:
        """Provide example of mixed type explicit conversion."""
        return (
            "Example of mixed type conversion:\n"
            "val a : i32 = 10; val b : i64 = 20\n"
            "val result : i64 = a:i64 + b  // Explicit conversion required\n"
            "// Transparent costs: conversion visible in syntax"
        )
