"""
Test Mutable Parameter Enforcement Rules

**Focus:** Enforce that functions with modified `mut` parameters must return the modified value
This addresses the confusion that could arise from pass-by-value semantics where developers
might mistakenly expect `mut` parameters to modify caller's values through side effects.

**Design Decision: Design A**
Hexen enforces that functions modifying `mut` parameters MUST return the modified value,
making pass-by-value semantics crystal clear and preventing developer confusion.

**What this file tests:**
- Functions with modified `mut` scalar parameters + void return → ERROR
- Functions with modified `mut` array parameters + void return → ERROR
- Functions with modified `mut` string parameters + void return → ERROR
- Functions with modified `mut` parameters + non-void return → OK
- Functions with unmodified `mut` parameters + void return → OK
- Complex modification patterns (multiple parameters, expression blocks, conditionals)

**Key principle: "Local Copy Behavior Enforcement"**
- `mut` parameters modify LOCAL COPIES (pass-by-value semantics)
- Modifications are lost unless returned to caller
- Enforcement makes this crystal clear through type system
- Prevents "silent confusion" where modifications appear to work but are lost

**Complementary files:**
- `test_pass_by_value.py` - Validates pass-by-value semantics (caller isolation)
- `test_mutable_parameters.py` - Tests parameter reassignment validation rules
- `test_function_calls.py` - Function call mechanics and type checking

**Testing philosophy:**
This file enforces the contract that modified `mut` parameters must be returned,
making pass-by-value semantics explicit and preventing developer confusion about
whether modifications affect the caller (they don't!).
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestScalarMutParameterEnforcement:
    """Test enforcement of return requirement for modified mut scalar parameters."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def assert_no_errors(self, code: str):
        """Helper to assert code compiles without errors."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def assert_has_error(self, code: str, expected_msg_fragment: str):
        """Helper to assert code produces expected error."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error but got none"
        error_messages = " ".join(str(e) for e in errors)
        assert expected_msg_fragment in error_messages, (
            f"Expected error containing '{expected_msg_fragment}', "
            f"but got: {error_messages}"
        )

    def test_modified_mut_scalar_with_void_return_error(self):
        """Test that modifying mut scalar parameter with void return triggers error."""
        code = """
        func broken_increment(mut counter: i32) : void = {
            counter = counter + 1
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_modified_mut_scalar_with_value_return_ok(self):
        """Test that modifying mut scalar parameter with value return is valid."""
        code = """
        func increment(mut counter: i32) : i32 = {
            counter = counter + 1
            return counter
        }
        """
        self.assert_no_errors(code)

    def test_unmodified_mut_scalar_with_void_return_ok(self):
        """Test that unmodified mut scalar parameter with void return is valid."""
        code = """
        func process_and_log(mut value: i32) : void = {
            val doubled : i32 = value * 2
            return
        }
        """
        self.assert_no_errors(code)

    def test_multiple_mut_scalars_one_modified_void_return_error(self):
        """Test that modifying one of multiple mut parameters requires return."""
        code = """
        func partial_modification(mut a: i32, mut b: i32, mut c: i32) : void = {
            a = 10
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_mut_scalar_self_assignment_considered_modification(self):
        """Test that self-assignment of mut parameter counts as modification."""
        code = """
        func identity_assignment(mut value: i32) : void = {
            value = value
            return
        }
        """
        self.assert_has_error(code, "but returns void")


class TestArrayMutParameterEnforcement:
    """Test enforcement of return requirement for modified mut array parameters."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def assert_no_errors(self, code: str):
        """Helper to assert code compiles without errors."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def assert_has_error(self, code: str, expected_msg_fragment: str):
        """Helper to assert code produces expected error."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error but got none"
        error_messages = " ".join(str(e) for e in errors)
        assert expected_msg_fragment in error_messages, (
            f"Expected error containing '{expected_msg_fragment}', "
            f"but got: {error_messages}"
        )

    def test_modified_mut_array_with_void_return_error(self):
        """Test that modifying mut array parameter with void return triggers error."""
        code = """
        func broken_scale_array(mut data: [3]f64) : void = {
            data = [1.0, 2.0, 3.0]
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_modified_mut_array_with_value_return_ok(self):
        """Test that modifying mut array parameter with value return is valid."""
        code = """
        func scale_array(mut data: [3]f64) : [3]f64 = {
            data = [1.0, 2.0, 3.0]
            return data
        }
        """
        self.assert_no_errors(code)

    def test_unmodified_mut_array_with_void_return_ok(self):
        """Test that unmodified mut array parameter with void return is valid."""
        code = """
        func inspect_array(mut arr: [5]i32) : void = {
            val first : i32 = arr[0]
            return
        }
        """
        self.assert_no_errors(code)


class TestStringMutParameterEnforcement:
    """Test enforcement of return requirement for modified mut string parameters."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def assert_no_errors(self, code: str):
        """Helper to assert code compiles without errors."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def assert_has_error(self, code: str, expected_msg_fragment: str):
        """Helper to assert code produces expected error."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error but got none"
        error_messages = " ".join(str(e) for e in errors)
        assert expected_msg_fragment in error_messages, (
            f"Expected error containing '{expected_msg_fragment}', "
            f"but got: {error_messages}"
        )

    def test_modified_mut_string_with_void_return_error(self):
        """Test that modifying mut string parameter with void return triggers error."""
        code = """
        func broken_update_message(mut msg: string) : void = {
            msg = "updated"
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_modified_mut_string_with_value_return_ok(self):
        """Test that modifying mut string parameter with value return is valid."""
        code = """
        func update_message(mut msg: string) : string = {
            msg = "updated"
            return msg
        }
        """
        self.assert_no_errors(code)


class TestComplexMutParameterScenarios:
    """Test complex scenarios with mut parameter enforcement."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def assert_no_errors(self, code: str):
        """Helper to assert code compiles without errors."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def assert_has_error(self, code: str, expected_msg_fragment: str):
        """Helper to assert code produces expected error."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error but got none"
        error_messages = " ".join(str(e) for e in errors)
        assert expected_msg_fragment in error_messages, (
            f"Expected error containing '{expected_msg_fragment}', "
            f"but got: {error_messages}"
        )

    def test_mut_param_modified_in_expression_block_void_return_error(self):
        """Test that mut parameter modified in expression block requires return."""
        code = """
        func broken_block_modification(mut value: i32) : void = {
            val result : i32 = {
                value = value * 2
                -> value
            }
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_mut_param_modified_multiple_times_void_return_error(self):
        """Test that multiple modifications to mut parameter require return."""
        code = """
        func broken_chain_modification(mut value: f64) : void = {
            value = value * 2.0
            value = value + 10.0
            value = value / 3.0
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_mixed_parameters_modified_mut_requires_return(self):
        """Test that modifying mut parameter among mixed parameters requires return."""
        code = """
        func mixed_modification(immutable: i32, mut modifiable: i32, flag: bool) : void = {
            modifiable = modifiable + immutable
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_mut_param_conditional_modification_void_return_error(self):
        """Test that conditional modification of mut parameter requires return."""
        code = """
        func broken_conditional_mod(mut value: i32, flag: bool) : void = {
            if flag {
                value = 42
            }
            return
        }
        """
        self.assert_has_error(code, "but returns void")

    def test_all_mut_params_unmodified_void_return_ok(self):
        """Test that unmodified mut parameters allow void return."""
        code = """
        func read_only_mut(mut a: i32, mut b: i32, mut c: i32) : void = {
            val sum : i32 = a + b + c
            return
        }
        """
        self.assert_no_errors(code)


class TestEdgeCasesMutParameterEnforcement:
    """Test edge cases for mut parameter enforcement."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def assert_no_errors(self, code: str):
        """Helper to assert code compiles without errors."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def assert_has_error(self, code: str, expected_msg_fragment: str):
        """Helper to assert code produces expected error."""
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0, "Expected error but got none"
        error_messages = " ".join(str(e) for e in errors)
        assert expected_msg_fragment in error_messages, (
            f"Expected error containing '{expected_msg_fragment}', "
            f"but got: {error_messages}"
        )

    def test_function_with_no_parameters_void_return_ok(self):
        """Test that functions without parameters can have void return."""
        code = """
        func no_params() : void = {
            return
        }
        """
        self.assert_no_errors(code)

    def test_immutable_param_cannot_be_modified_separate_error(self):
        """Test that immutable parameter modification has separate error."""
        code = """
        func broken_immutable_mod(value: i32) : void = {
            value = 42
            return
        }
        """
        # This should error about immutable parameter, not about return type
        self.assert_has_error(code, "immutable parameter")

    def test_modified_mut_param_returned_correctly_typed(self):
        """Test that returned mut parameter matches function return type."""
        code = """
        func correct_return_type(mut value: i32) : i32 = {
            value = value + 1
            return value
        }
        """
        self.assert_no_errors(code)
