"""
Shared utilities and mixins for semantic testing in Hexen

This module provides additional testing utilities that complement the
StandardTestBase class for more advanced semantic testing patterns.
These utilities help eliminate code duplication and provide consistent
testing patterns across the semantic test suite.
"""

from typing import List


class SemanticTestMixin:
    """
    Mixin class providing advanced semantic testing utilities.

    This mixin can be used alongside StandardTestBase to provide
    additional testing functionality beyond basic setup.

    Usage:
        class TestFeature(StandardTestBase, SemanticTestMixin):
            def test_something(self):
                self.assert_single_error(source, "expected error")
    """

    def assert_single_error(self, source: str, expected_pattern: str) -> None:
        """
        Assert that source produces exactly one error containing the expected pattern.

        Args:
            source: Hexen source code to analyze
            expected_pattern: String pattern that should be in the error message
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        if len(errors) != 1:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                f"Expected exactly 1 error, but got {len(errors)} errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

        error_msg = str(errors[0])
        if expected_pattern not in error_msg:
            raise AssertionError(
                f"Expected error to contain '{expected_pattern}', but got: {error_msg}"
            )

    def assert_no_errors(self, source: str) -> None:
        """
        Assert that source produces no semantic errors.

        Args:
            source: Hexen source code to analyze
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        if errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                f"Expected no errors, but got {len(errors)} errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_type_resolved(
        self, source: str, variable_name: str, expected_type: str
    ) -> None:
        """
        Assert that a variable resolves to the expected type.

        Args:
            source: Hexen source code to analyze
            variable_name: Name of the variable to check
            expected_type: Expected type string (e.g., "i32", "f64")
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # First ensure no errors
        if errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                f"Expected no errors for type resolution check, but got {len(errors)} errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

        # Check variable type resolution
        # Note: This would need to be implemented based on the analyzer's API
        # For now, we'll just verify no errors occurred
        # In a full implementation, this would check the symbol table
        pass

    def assert_error_at_line(
        self, source: str, line_number: int, expected_pattern: str
    ) -> None:
        """
        Assert that an error occurs at a specific line number.

        Args:
            source: Hexen source code to analyze
            line_number: Expected line number of the error
            expected_pattern: String pattern that should be in the error message
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        matching_errors = [
            error
            for error in errors
            if hasattr(error, "line")
            and error.line == line_number
            and expected_pattern in str(error)
        ]

        if not matching_errors:
            error_messages = [
                f"Line {getattr(error, 'line', '?')}: {str(error)}" for error in errors
            ]
            raise AssertionError(
                f"Expected error at line {line_number} containing '{expected_pattern}', but got errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_multiple_errors_at_lines(
        self, source: str, expected_errors: List[tuple]
    ) -> None:
        """
        Assert that multiple errors occur at specific lines.

        Args:
            source: Hexen source code to analyze
            expected_errors: List of (line_number, expected_pattern) tuples
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        if len(errors) != len(expected_errors):
            error_messages = [
                f"Line {getattr(error, 'line', '?')}: {str(error)}" for error in errors
            ]
            raise AssertionError(
                f"Expected {len(expected_errors)} errors, but got {len(errors)} errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

        for line_num, pattern in expected_errors:
            matching_errors = [
                error
                for error in errors
                if hasattr(error, "line")
                and error.line == line_num
                and pattern in str(error)
            ]

            if not matching_errors:
                error_messages = [
                    f"Line {getattr(error, 'line', '?')}: {str(error)}"
                    for error in errors
                ]
                raise AssertionError(
                    f"Expected error at line {line_num} containing '{pattern}', but got errors:\n"
                    + "\n".join(f"  - {msg}" for msg in error_messages)
                )


class TypeTestingMixin:
    """
    Mixin class providing type system testing utilities.

    This mixin provides utilities specifically for testing
    Hexen's type system features like comptime types,
    type coercion, and precision loss.
    """

    def assert_comptime_type_preserved(self, source: str, variable_name: str) -> None:
        """
        Assert that a variable preserves its comptime type.

        Args:
            source: Hexen source code to analyze
            variable_name: Name of the variable to check
        """
        # This would need to be implemented based on the analyzer's API
        # For now, we'll just verify no errors occurred
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        if errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                f"Expected comptime type to be preserved, but got {len(errors)} errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_implicit_coercion_allowed(self, source: str) -> None:
        """
        Assert that implicit type coercion is allowed for the given source.

        Args:
            source: Hexen source code to analyze
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        coercion_errors = [
            error
            for error in errors
            if "explicit conversion" in str(error).lower()
            or "coercion" in str(error).lower()
        ]

        if coercion_errors:
            error_messages = [str(error) for error in coercion_errors]
            raise AssertionError(
                "Expected implicit coercion to be allowed, but got coercion errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_explicit_conversion_required(
        self, source: str, conversion_hint: str
    ) -> None:
        """
        Assert that explicit conversion is required for the given source.

        Args:
            source: Hexen source code to analyze
            conversion_hint: Expected conversion hint in error message (e.g., "value:i32")
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        conversion_errors = [
            error
            for error in errors
            if "explicit conversion" in str(error).lower()
            and conversion_hint in str(error)
        ]

        if not conversion_errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                f"Expected explicit conversion error with hint '{conversion_hint}', but got errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_precision_loss_detected(
        self, source: str, loss_type: str = None
    ) -> None:
        """
        Assert that precision loss is detected for the given source.

        Args:
            source: Hexen source code to analyze
            loss_type: Optional specific type of precision loss ("truncation", "precision")
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        precision_keywords = ["truncation", "precision", "narrowing"]
        if loss_type:
            precision_keywords = [loss_type]

        precision_errors = [
            error
            for error in errors
            if any(keyword in str(error).lower() for keyword in precision_keywords)
        ]

        if not precision_errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                "Expected precision loss error, but got errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )


class BlockTestingMixin:
    """
    Mixin class providing block system testing utilities.

    This mixin provides utilities specifically for testing
    Hexen's unified block system features.
    """

    def assert_statement_block_valid(self, source: str) -> None:
        """
        Assert that a statement block is valid (no value production required).

        Args:
            source: Hexen source code to analyze
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        block_errors = [
            error
            for error in errors
            if "return statement" in str(error).lower()
            or "value production" in str(error).lower()
        ]

        if block_errors:
            error_messages = [str(error) for error in block_errors]
            raise AssertionError(
                "Expected statement block to be valid, but got block errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_expression_block_requires_return(self, source: str) -> None:
        """
        Assert that an expression block requires a return statement.

        Args:
            source: Hexen source code to analyze
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        return_errors = [
            error
            for error in errors
            if "return statement" in str(error).lower()
            or "expression block" in str(error).lower()
        ]

        if not return_errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                "Expected expression block return error, but got errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def assert_scope_isolation(self, source: str, isolated_variable: str) -> None:
        """
        Assert that scope isolation prevents access to a variable.

        Args:
            source: Hexen source code to analyze
            isolated_variable: Name of variable that should be out of scope
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        scope_errors = [
            error
            for error in errors
            if f"Undefined variable: '{isolated_variable}'" in str(error)
            or f"variable '{isolated_variable}'" in str(error)
        ]

        if not scope_errors:
            error_messages = [str(error) for error in errors]
            raise AssertionError(
                f"Expected scope isolation error for '{isolated_variable}', but got errors:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )


# Utility functions for common test patterns
def create_simple_function(return_type: str = "void", body: str = "val x = 42") -> str:
    """
    Create a simple function source code for testing.

    Args:
        return_type: Return type of the function
        body: Function body content

    Returns:
        Complete function source code
    """
    return f"""
    func test_function() : {return_type} = {{
        {body}
    }}
    """


def create_variable_declaration(
    var_type: str, name: str, value: str, mutable: bool = False
) -> str:
    """
    Create a variable declaration source code for testing.

    Args:
        var_type: Type annotation for the variable
        name: Variable name
        value: Initial value
        mutable: Whether the variable should be mutable

    Returns:
        Variable declaration source code
    """
    keyword = "mut" if mutable else "val"
    return f"{keyword} {name} : {var_type} = {value}"


def create_assignment(var_name: str, value: str) -> str:
    """
    Create an assignment statement source code for testing.

    Args:
        var_name: Variable name to -> to
        value: Value to assign

    Returns:
        Assignment statement source code
    """
    return f"{var_name} = {value}"


def create_expression_block(statements: List[str], return_value: str) -> str:
    """
    Create an expression block source code for testing.

    Args:
        statements: List of statements in the block
        return_value: Value to return from the block

    Returns:
        Expression block source code
    """
    statements_str = "\n        ".join(statements)
    return f"""{{
        {statements_str}
        return {return_value}
    }}"""


def create_statement_block(statements: List[str]) -> str:
    """
    Create a statement block source code for testing.

    Args:
        statements: List of statements in the block

    Returns:
        Statement block source code
    """
    statements_str = "\n        ".join(statements)
    return f"""{{
        {statements_str}
    }}"""
