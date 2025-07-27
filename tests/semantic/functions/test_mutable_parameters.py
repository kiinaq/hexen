"""
Comprehensive tests for mutable parameter functionality.

Tests parameter reassignment validation, mutability checking, and error messages
as specified in FUNCTION_SYSTEM.md Session 10.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestMutableParameterValidation:
    """Test parameter mutability validation and reassignment rules."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_immutable_parameter_reassignment_rejected(self):
        """Test that reassigning immutable parameters is properly rejected."""
        code = """
        func test_function(input: i32) : i32 = {
            input = 42
            return input
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Cannot reassign immutable parameter 'input'" in error_msg
        assert "Parameters are immutable by default" in error_msg
        assert "Use 'mut input: i32' for mutable parameters" in error_msg

    def test_mutable_parameter_reassignment_allowed(self):
        """Test that reassigning mutable parameters is allowed."""
        code = """
        func test_function(mut input: i32) : i32 = {
            input = 42
            return input
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_multiple_parameter_reassignments(self):
        """Test mixed mutable and immutable parameter scenarios."""
        code = """
        func mixed_params(immutable: i32, mut mutable: i32) : i32 = {
            mutable = 100
            return immutable + mutable
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mixed_params_with_immutable_reassignment_error(self):
        """Test error when trying to reassign immutable parameter in mixed scenario."""
        code = """
        func mixed_params(immutable: i32, mut mutable: i32) : i32 = {
            immutable = 50
            mutable = 100
            return immutable + mutable
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Cannot reassign immutable parameter 'immutable'" in error_msg

    def test_mutable_parameter_type_consistency(self):
        """Test that mutable parameter reassignments follow type system rules."""
        code = """
        func type_test(mut value: i32) : i32 = {
            value = 42
            return value
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_type_conversion_required(self):
        """Test that explicit conversions are required for mutable parameter reassignments."""
        code = """
        func conversion_test(mut small: i32, large: i64) : i32 = {
            small = large
            return small
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        # Should require explicit conversion for i64 -> i32 assignment


class TestParameterReassignmentTypes:
    """Test type system integration with parameter reassignment."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mutable_parameter_comptime_adaptation(self):
        """Test that comptime types adapt to mutable parameter types."""
        code = """
        func comptime_test(mut value: i64) : i64 = {
            value = 42
            return value
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_precision_loss_explicit_conversion(self):
        """Test that precision loss operations require explicit conversion."""
        code = """
        func precision_test(mut precise: f32, source: f64) : f32 = {
            precise = source:f32
            return precise
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_same_type_assignment(self):
        """Test that same-type assignments work seamlessly."""
        code = """
        func same_type_test(mut target: f64, source: f64) : f64 = {
            target = source
            return target
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"


class TestParameterScopeIntegration:
    """Test parameter scope and interaction with local variables."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_parameter_and_local_variable_interaction(self):
        """Test mutable parameter interaction with local variables."""
        code = """
        func interaction_test(mut param: i32, input: i32) : i32 = {
            val local_val : i32 = input * 2
            param = local_val
            return param
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_parameter_shadowing_by_local_variable(self):
        """Test that local variables can shadow parameters."""
        code = """
        func shadowing_test(param: i32) : i32 = {
            val param : i32 = 100
            return param
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_in_nested_blocks(self):
        """Test mutable parameter access in nested blocks."""
        code = """
        func nested_test(mut param: i32) : i32 = {
            {
                param = 50
            }
            return param
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"


class TestParameterErrorMessages:
    """Test parameter-specific error message quality and clarity."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_immutable_parameter_error_message_specificity(self):
        """Test that parameter error messages are specific and helpful."""
        code = """
        func error_test(readonly: string) : string = {
            readonly = "modified"
            return readonly
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Verify error message contains key information
        assert "Cannot reassign immutable parameter 'readonly'" in error_msg
        assert "Parameters are immutable by default" in error_msg
        assert "Use 'mut readonly: string' for mutable parameters" in error_msg

    def test_parameter_vs_variable_error_distinction(self):
        """Test that parameter errors are distinct from variable errors."""
        # Test parameter error
        param_code = """
        func param_test(input: i32) : i32 = {
            input = 42
            return input
        }
        """

        # Test variable error
        var_code = """
        func var_test() : i32 = {
            val input : i32 = 10
            input = 42
            return input
        }
        """

        # Analyze parameter error
        param_ast = self.parser.parse(param_code)
        param_errors = self.analyzer.analyze(param_ast)

        # Analyze variable error
        var_analyzer = SemanticAnalyzer()  # Fresh analyzer
        var_ast = self.parser.parse(var_code)
        var_errors = var_analyzer.analyze(var_ast)

        assert len(param_errors) == 1
        assert len(var_errors) == 1

        param_msg = str(param_errors[0])
        var_msg = str(var_errors[0])

        # Verify messages are different and context-appropriate
        assert "immutable parameter" in param_msg
        assert "mut input: i32" in param_msg
        assert "immutable variable" in var_msg
        assert "val variables can only be assigned once" in var_msg


class TestAdvancedParameterScenarios:
    """Test advanced mutable parameter scenarios and edge cases."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mutable_parameter_self_modification(self):
        """Test self-modification patterns with mutable parameters."""
        code = """
        func increment(mut value: i32) : i32 = {
            value = value + 1
            return value
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_complex_expressions(self):
        """Test mutable parameters with complex expressions."""
        code = """
        func complex_modification(mut target: f64, factor: f64) : f64 = {
            target = target * factor + 10.0
            return target
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_multiple_reassignments(self):
        """Test multiple reassignments of same mutable parameter."""
        code = """
        func multiple_assignments(mut accumulator: i32, a: i32, b: i32) : i32 = {
            accumulator = a
            accumulator = accumulator + b
            accumulator = accumulator * 2
            return accumulator
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_all_mutable_parameters(self):
        """Test function with all mutable parameters."""
        code = """
        func all_mutable(mut a: i32, mut b: i32, mut c: i32) : i32 = {
            a = 10
            b = 20  
            c = 30
            return a + b + c
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameter_with_expression_blocks(self):
        """Test mutable parameters in expression blocks."""
        code = """
        func expression_block_test(mut value: i32) : i32 = {
            val result = {
                value = value * 2
                assign value
            }
            return result
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"
