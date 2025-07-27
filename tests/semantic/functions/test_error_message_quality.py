"""
Comprehensive error message quality tests for the function system.

Tests that error messages are clear, consistent, and provide actionable guidance
for common function-related errors across all function features.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestFunctionDeclarationErrorMessages:
    """Test error message quality for function declaration issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_duplicate_function_names_error_message(self):
        """Test clear error message for duplicate function declarations."""
        code = """
        func calculate(x: i32) : i32 = {
            return x * 2
        }

        func calculate(y: f64) : f64 = {
            return y * 3.14
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Function 'calculate' is already declared" in error_msg
        # Error message is concise and clear - that's good quality

    def test_void_parameter_error_message(self):
        """Test clear error message for void parameter types."""
        code = """
        func invalid_param(bad_param: void) : i32 = {
            return 42
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Parameter 'bad_param' cannot have void type" in error_msg

    def test_duplicate_parameter_names_error_message(self):
        """Test clear error message for duplicate parameter names."""
        code = """
        func bad_params(param: i32, param: f64) : i32 = {
            return 42
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Duplicate parameter name: 'param'" in error_msg


class TestFunctionCallErrorMessages:
    """Test error message quality for function call issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_undefined_function_error_message(self):
        """Test clear error message for undefined function calls."""
        code = """
        func caller() : i32 = {
            return missing_function(42)
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Undefined function: 'missing_function'" in error_msg

    def test_argument_count_mismatch_error_messages(self):
        """Test clear error messages for argument count mismatches."""
        code = """
        func target_func(a: i32, b: i32, c: i32) : i32 = {
            return a + b + c
        }

        func caller() : i32 = {
            val too_few : i32 = target_func(1, 2)
            val too_many : i32 = target_func(1, 2, 3, 4, 5)
            return too_few + too_many
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 2

        error_messages = [str(error) for error in errors]

        # Check for clear argument count messages
        too_few_msg = next(
            (
                msg
                for msg in error_messages
                if "expects 3 arguments" in msg and "2 provided" in msg
            ),
            None,
        )
        too_many_msg = next(
            (
                msg
                for msg in error_messages
                if "expects 3 arguments" in msg and "5 provided" in msg
            ),
            None,
        )

        assert too_few_msg is not None, (
            f"Missing 'too few arguments' error message in: {error_messages}"
        )
        assert too_many_msg is not None, (
            f"Missing 'too many arguments' error message in: {error_messages}"
        )

    def test_argument_type_mismatch_error_messages(self):
        """Test clear error messages for argument type mismatches."""
        code = """
        func strict_types(small: i32, large: i64, precise: f64) : f64 = {
            return small:f64 + large:f64 + precise
        }

        func caller() : f64 = {
            val wrong_type : f32 = 3.14
            return strict_types(wrong_type, 100, "string")
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should have multiple type conversion errors

        error_messages = [str(error) for error in errors]

        # Check for explicit conversion guidance
        conversion_guidance = any(
            "Use explicit conversion" in msg for msg in error_messages
        )
        assert conversion_guidance, (
            f"Missing explicit conversion guidance in: {error_messages}"
        )


class TestParameterErrorMessages:
    """Test error message quality for parameter-related issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_immutable_parameter_reassignment_error_message(self):
        """Test specific error message for immutable parameter reassignment."""
        code = """
        func bad_reassignment(readonly: i32, mut mutable: i32) : i32 = {
            readonly = 100
            mutable = 200
            return readonly + mutable
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Verify parameter-specific error message components
        assert "Cannot reassign immutable parameter 'readonly'" in error_msg
        assert "Parameters are immutable by default" in error_msg
        assert "Use 'mut readonly: i32' for mutable parameters" in error_msg

    def test_parameter_vs_variable_error_distinction(self):
        """Test that parameter and variable errors are clearly distinguished."""
        # Test parameter error
        param_code = """
        func param_error(input: string) : string = {
            input = "modified"
            return input
        }
        """

        # Test variable error
        var_code = """
        func var_error() : string = {
            val input : string = "original"
            input = "modified"
            return input
        }
        """

        # Analyze parameter error
        param_ast = self.parser.parse(param_code)
        param_errors = self.analyzer.analyze(param_ast)

        # Analyze variable error
        var_analyzer = SemanticAnalyzer()
        var_ast = self.parser.parse(var_code)
        var_errors = var_analyzer.analyze(var_ast)

        assert len(param_errors) == 1
        assert len(var_errors) == 1

        param_msg = str(param_errors[0])
        var_msg = str(var_errors[0])

        # Verify distinct error messages
        assert "immutable parameter" in param_msg
        assert "Use 'mut input: string' for mutable parameters" in param_msg
        assert "immutable variable" in var_msg
        assert "val variables can only be assigned once at declaration" in var_msg

    def test_mutable_parameter_type_conversion_error_message(self):
        """Test error messages for mutable parameter type conversion issues."""
        code = """
        func conversion_error(mut target: i32, source: i64) : i32 = {
            target = source  // Should require explicit conversion
            return target
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Should provide guidance on explicit conversion
        assert (
            "explicit conversion" in error_msg.lower()
            or "truncation" in error_msg.lower()
        )


class TestReturnTypeErrorMessages:
    """Test error message quality for return type issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_return_type_mismatch_error_message(self):
        """Test clear error message for return type mismatches."""
        code = """
        func wrong_return() : i32 = {
            return "string value"
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Should clearly indicate type mismatch
        assert "type mismatch" in error_msg.lower() or "cannot" in error_msg.lower()

    def test_void_function_value_return_error_message(self):
        """Test error message for returning value from void function."""
        code = """
        func void_func() : void = {
            return 42
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Should mention void function constraint
        assert "void" in error_msg.lower()

    def test_mixed_concrete_types_in_return_error_message(self):
        """Test error message for mixed concrete types in return statements."""
        code = """
        func mixed_return(a: i32, b: f64) : f64 = {
            return a + b  // Mixed concrete types require explicit conversion
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Should provide guidance on explicit conversion
        assert "explicit conversion" in error_msg.lower()


class TestErrorMessageConsistency:
    """Test consistency of error messages across function system."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_explicit_conversion_message_consistency(self):
        """Test that explicit conversion error messages are consistent."""
        # Test in function call context
        call_code = """
        func target(param: i32) : i32 = { return param }
        func caller() : i32 = {
            val large : i64 = 1000
            return target(large)
        }
        """

        # Test in assignment context
        assign_code = """
        func assigner() : i32 = {
            val large : i64 = 1000
            mut small : i32 = 0
            small = large
            return small
        }
        """

        # Test in return context
        return_code = """
        func returner() : i32 = {
            val large : i64 = 1000
            return large
        }
        """

        # Analyze all contexts
        call_ast = self.parser.parse(call_code)
        call_errors = self.analyzer.analyze(call_ast)

        assign_analyzer = SemanticAnalyzer()
        assign_ast = self.parser.parse(assign_code)
        assign_errors = assign_analyzer.analyze(assign_ast)

        return_analyzer = SemanticAnalyzer()
        return_ast = self.parser.parse(return_code)
        return_errors = return_analyzer.analyze(return_ast)

        # All should have similar explicit conversion guidance
        all_errors = call_errors + assign_errors + return_errors
        assert len(all_errors) >= 3

        conversion_messages = [str(error) for error in all_errors]

        # Check for consistent terminology
        consistent_terminology = all(
            "explicit conversion" in msg.lower() or "truncation" in msg.lower()
            for msg in conversion_messages
        )

        assert consistent_terminology, (
            f"Inconsistent conversion messages: {conversion_messages}"
        )

    def test_error_message_actionability(self):
        """Test that error messages provide actionable guidance."""
        code = """
        func bad_example() : i32 = {
            val large : i64 = 1000
            mut small : i32 = 0
            small = large  // Should provide actionable guidance
            return small
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])

        # Should provide actionable guidance (how to fix the error)
        actionable_keywords = ["use", "add", "require", "convert", ":i32"]
        has_actionable_guidance = any(
            keyword in error_msg.lower() for keyword in actionable_keywords
        )

        assert has_actionable_guidance, (
            f"Error message lacks actionable guidance: {error_msg}"
        )


class TestComplexScenarioErrorMessages:
    """Test error message quality in complex scenarios."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_multiple_errors_in_single_function(self):
        """Test that multiple errors in single function are all reported clearly."""
        code = """
        func multiple_errors(readonly: i32) : string = {
            readonly = 100        // Error 1: Immutable parameter reassignment
            val result : i32 = missing_func(42)  // Error 2: Undefined function
            return result         // Error 3: Type mismatch (i32 → string)
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should catch multiple errors

        error_messages = [str(error) for error in errors]

        # Should catch the parameter reassignment error
        param_error = any(
            "Cannot reassign immutable parameter" in msg for msg in error_messages
        )
        assert param_error, f"Missing parameter reassignment error in: {error_messages}"

    def test_nested_error_reporting(self):
        """Test error reporting in nested function calls and expression blocks."""
        code = """
        func outer() : i32 = {
            val result = {
                val inner_result : i32 = undefined_function(42)
                assign inner_result
            }
            return result
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])

        # Should report the undefined function error clearly
        assert "undefined_function" in error_msg.lower()

    def test_function_composition_error_messages(self):
        """Test error messages in function composition scenarios."""
        code = """
        func process_int(value: i32) : i32 = {
            return value * 2
        }

        func process_string(text: string) : string = {
            return text
        }

        func compose_incorrectly() : string = {
            val number : i32 = 42
            return process_string(process_int(number))  // Type mismatch in composition
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]

        # Should provide clear guidance about the type mismatch
        type_guidance = any("i32" in msg and "string" in msg for msg in error_messages)
        assert type_guidance, (
            f"Missing type guidance in composition error: {error_messages}"
        )
