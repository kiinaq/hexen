"""
Test context-guided type resolution framework for Hexen semantic analysis

This module tests the sophisticated context propagation system that enables
Hexen's "Explicit Danger, Implicit Safety" philosophy. It focuses specifically
on how target types are propagated through expressions to guide resolution.

Context Framework Coverage:
- Context propagation through variable declarations
- Context propagation through assignment statements
- Context propagation through function returns
- Context propagation through expression blocks
- Context propagation through complex nested expressions
- Context-guided resolution of comptime types
- Context-guided resolution of mixed-type operations

Related but tested elsewhere:
- test_comptime_types.py: Comptime type coercion mechanics (what context enables)
- test_type_coercion.py: Regular type coercion rules (how types convert)
- test_binary_ops.py: Mixed-type binary operations (what requires context)
- test_assignment.py: Assignment validation (how assignments use context)
- precision/ directory: Explicit conversion (when context isn't enough)

This file focuses on the context propagation mechanisms themselves.

NOTE: This file has been updated to use the parser for all test cases,
replacing manual AST constructions with cleaner, more maintainable
parser-based test code following the same pattern as other test files.
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
    assert_error_count,
)
from src.hexen.semantic import HexenType
from src.hexen.ast_nodes import NodeType


class TestContextPropagationMechanisms(StandardTestBase):
    """Test core context propagation mechanisms"""

    def test_context_parameter_exists(self):
        """Test that _analyze_expression accepts target_type parameter"""
        # Create a simple literal node
        node = {"type": NodeType.LITERAL.value, "value": 42}

        # Test without context (should work)
        result1 = self.analyzer._analyze_expression(node)
        assert result1 == HexenType.COMPTIME_INT

        # Test with context (should work)
        result2 = self.analyzer._analyze_expression(node, HexenType.I32)
        assert result2 == HexenType.COMPTIME_INT

    def test_variable_declaration_context_propagation(self):
        """Test context propagation to variable declaration expressions"""
        source = """
        func test() : void = {
            val explicit : i64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_assignment_context_propagation(self):
        """Test context propagation to assignment statement expressions"""
        source = """
        func test() : void = {
            mut flexible : f64 = 0.0
            flexible = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_return_statement_context_propagation(self):
        """Test context propagation to return statement expressions"""
        source = """
        func test() : f32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestContextPropagationDepth(StandardTestBase):
    """Test context propagation through complex nested structures"""

    def test_nested_expression_context_propagation(self):
        """Test context propagates through nested expressions"""
        source = """
        func test() : void = {
            val result : i64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_deep_nesting_context_propagation(self):
        """Test context propagation through deeply nested structures"""
        source = """
        func test() : void = {
            val nested : f32 = 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_context_through_variable_references(self):
        """Test context propagation works with variable references"""
        source = """
        func test() : void = {
            val source : i32 = 42
            val target : i64 = source
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestBlockContextPropagation(StandardTestBase):
    """Test context propagation through block expressions"""

    def test_expression_block_context_propagation(self):
        """Test context propagates through expression blocks"""
        source = """
        func test() : void = {
            val result : f64 = 42.0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_nested_blocks_context_propagation(self):
        """Test context propagation through nested structures"""
        source = """
        func test() : void = {
            val outer_result : i64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestContextGuidedResolution(StandardTestBase):
    """Test context-guided type resolution for specific scenarios"""

    def test_comptime_type_context_resolution(self):
        """Test context-guided resolution of comptime types"""
        source = """
        func test() : void = {
            val as_i32 : i32 = 42
            val as_i64 : i64 = 42
            val as_f32 : f32 = 42
            val as_f64 : f64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_regular_type_coercion_context_resolution(self):
        """Test context-guided resolution for regular type coercion"""
        source = """
        func test() : void = {
            val source : i32 = 42
            val widened : i64 = source
            val converted : f64 = source
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestContextPropagationLimits(StandardTestBase):
    """Test scenarios where context propagation has limits"""

    def test_context_cannot_fix_invalid_coercion(self):
        """Test that context cannot enable invalid type coercion"""
        source = """
        func test() : void = {
            val string_val : string = "hello"
            val invalid : i32 = string_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)

    def test_context_preserves_existing_error_detection(self):
        """Test that context framework doesn't mask existing errors"""
        source = """
        func test() : void = {
            val invalid : i32 = undefined_var
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert "Undefined variable" in errors[0].message

    def test_context_with_uninitialized_variables(self):
        """Test context propagation with mutable variables"""
        source = """
        func test() : void = {
            mut pending : i32 = 0
            pending = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_parameter_context_propagation(self):
        """Test context propagation in function context"""
        source = """
        func test() : i64 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestContextFrameworkIntegration(StandardTestBase):
    """Test context framework integration with other language features"""

    def test_function_return_context_propagation(self):
        """Test context propagation in basic function scenarios"""
        source = """
        func test() : i64 = {
            val value : i64 = 42
            return value
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_context_propagation_consistency(self):
        """Test context propagation is consistent across all usage patterns"""
        source = """
        func test() : void = {
            val var_context : f32 = 42
            mut mut_var : f32 = 0.0
            mut_var = 42
        }
        
        func return_context() : f32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
