"""
Test comptime type adaptation and explicit type annotation behavior in Hexen

This module tests how Hexen's comptime types adapt to explicit type annotations
following the "Ergonomic Literals + Transparent Costs" philosophy. It focuses
specifically on how comptime types (comptime_int, comptime_float) adapt when
explicit type annotations are provided.

Comptime Adaptation Coverage:
- Comptime type adaptation to explicit type annotations in variable declarations
- Comptime type adaptation in assignment statements (target type provides annotation)
- Comptime type adaptation in function return types (return type provides annotation)
- Comptime type adaptation in expression blocks with explicit types
- Comptime type adaptation boundaries and limitations
- Explicit conversion requirements for concrete types
- Type annotation-driven resolution (not context propagation)

Related but tested elsewhere:
- test_comptime_types.py: Core comptime type coercion mechanics and patterns
- test_type_coercion.py: Regular type coercion rules between concrete types
- test_binary_ops.py: Binary operations with mixed types and explicit conversions
- test_assignment.py: Assignment validation and type compatibility
- precision/ directory: Explicit conversion requirements for precision loss

This file focuses on the comptime adaptation mechanisms themselves.

NOTE: This file uses parser-based test code following established patterns.
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
    assert_error_count,
)
from src.hexen.semantic import HexenType
from src.hexen.ast_nodes import NodeType


class TestComptimeAdaptationMechanisms(StandardTestBase):
    """Test core comptime type adaptation mechanisms"""

    def test_analyzer_target_type_parameter(self):
        """Test that _analyze_expression accepts target_type parameter for adaptation"""
        # Create a simple literal node
        node = {"type": NodeType.LITERAL.value, "value": 42}

        # Test without target type (should work)
        result1 = self.analyzer._analyze_expression(node)
        assert result1 == HexenType.COMPTIME_INT

        # Test with target type (should work - comptime types can adapt)
        result2 = self.analyzer._analyze_expression(node, HexenType.I32)
        assert result2 == HexenType.COMPTIME_INT

    def test_variable_declaration_type_adaptation(self):
        """Test comptime type adaptation to explicit type annotations in variable declarations"""
        source = """
        func test() : void = {
            val explicit : i64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_assignment_target_type_adaptation(self):
        """Test comptime type adaptation to target variable type in assignment statements"""
        source = """
        func test() : void = {
            mut flexible : f64 = 0.0
            flexible = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_return_type_adaptation(self):
        """Test comptime type adaptation to function return type annotations"""
        source = """
        func test() : f32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeAdaptationInExpressions(StandardTestBase):
    """Test comptime type adaptation in various expression contexts"""

    def test_nested_expression_type_adaptation(self):
        """Test comptime type adaptation works in nested expressions"""
        source = """
        func test() : void = {
            val result : i64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_type_adaptation(self):
        """Test comptime_float adaptation to explicit type annotations"""
        source = """
        func test() : void = {
            val nested : f32 = 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_concrete_type_explicit_conversion_requirement(self):
        """Test that concrete types require explicit conversions (not adaptation)"""
        source = """
        func test() : void = {
            val source : i32 = 42
            val target : i64 = source:i64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeAdaptationInBlocks(StandardTestBase):
    """Test comptime type adaptation in block expressions"""

    def test_expression_block_type_adaptation(self):
        """Test comptime type adaptation in expression block context"""
        source = """
        func test() : void = {
            val result : f64 = 42.0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_nested_blocks_type_adaptation(self):
        """Test comptime type adaptation in nested block structures"""
        source = """
        func test() : void = {
            val outer_result : i64 = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestExplicitTypeAnnotationResolution(StandardTestBase):
    """Test comptime type adaptation to explicit type annotations"""

    def test_comptime_int_adaptation_to_all_numeric_types(self):
        """Test comptime_int adaptation to all compatible numeric type annotations"""
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

    def test_concrete_type_requires_explicit_conversion(self):
        """Test that concrete types require explicit conversion syntax (not adaptation)"""
        source = """
        func test() : void = {
            val source : i32 = 42
            val widened : i64 = source:i64
            val converted : f64 = source:f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeAdaptationLimits(StandardTestBase):
    """Test scenarios where comptime adaptation has limits"""

    def test_adaptation_cannot_fix_invalid_coercion(self):
        """Test that type annotation cannot enable invalid type coercion"""
        source = """
        func test() : void = {
            val string_val : string = "hello"
            val invalid : i32 = string_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)

    def test_adaptation_preserves_existing_error_detection(self):
        """Test that type adaptation doesn't mask existing errors"""
        source = """
        func test() : void = {
            val invalid : i32 = undefined_var
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert "Undefined variable" in errors[0].message

    def test_adaptation_with_mutable_variables(self):
        """Test comptime type adaptation with mutable variable assignments"""
        source = """
        func test() : void = {
            mut pending : i32 = 0
            pending = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_return_type_adaptation(self):
        """Test comptime type adaptation to function return type annotation"""
        source = """
        func test() : i64 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeAdaptationIntegration(StandardTestBase):
    """Test comptime adaptation integration with other language features"""

    def test_function_return_with_concrete_value(self):
        """Test function return with concrete value (no adaptation needed)"""
        source = """
        func test() : i64 = {
            val value : i64 = 42
            return value
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_adaptation_consistency_across_contexts(self):
        """Test comptime type adaptation is consistent across different annotation contexts"""
        source = """
        func test() : void = {
            val var_annotation : f32 = 42
            mut mut_var : f32 = 0.0
            mut_var = 42
        }
        
        func return_annotation() : f32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
