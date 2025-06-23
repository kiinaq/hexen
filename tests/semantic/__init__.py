"""
Semantic analysis test package for Hexen - REFACTORED

Contains comprehensive tests for semantic analysis functionality organized by feature:

Core Integration Tests:
- test_basic_semantics.py - Cross-cutting semantic validation and integration tests

Core Type System Tests (NEW - Complete TYPE_SYSTEM.md Coverage):
- test_type_annotations.py - Type annotation system and explicit acknowledgment rules
- test_precision_loss.py - "Explicit Danger, Implicit Safety" principle enforcement
- test_mutability.py - Comprehensive val/mut variable system testing
- test_type_coercion.py - Regular type coercion and widening rules
- test_error_messages.py - Error message consistency and helpfulness

Advanced Type System Tests:
- test_f32_comptime.py - Numeric types and comptime type coercion system
- test_context_framework.py - Context-guided type resolution framework
- test_binary_ops.py - Binary operations and mixed-type expression handling
- test_unary_ops.py - Unary operations semantic analysis
- test_negative_numbers.py - Negative number literal handling

Feature-Specific Tests:
- test_assignment.py - Assignment statement validation and mutability enforcement
- test_bool.py - Boolean type semantics and validation
- test_bare_returns.py - Bare return statement handling in void functions
- test_unified_blocks.py - Unified block system (statement, expression, function body)

These tests operate on ASTs produced by the parser and validate the semantic
correctness of Hexen programs including type checking, symbol resolution,
scope management, and use-before-definition detection. The new type system tests
provide comprehensive coverage of the sophisticated type system described in
TYPE_SYSTEM.md, ensuring full compliance with the "Explicit Danger, Implicit Safety"
design philosophy.
"""

# =============================================================================
# STANDARDIZED TEST UTILITIES - SESSION 1 REFACTORING
# =============================================================================

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class StandardTestBase:
    """
    Base class providing standardized setup for all semantic tests.

    Usage:
        class TestSomeFeature(StandardTestBase):
            def test_some_functionality(self):
                source = "func main() : void = { ... }"
                ast = self.parser.parse(source)
                errors = self.analyzer.analyze(ast)
                assert errors == []
    """

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()


def assert_no_errors(errors):
    """
    Assert that no semantic errors occurred.
    Provides detailed error information if assertion fails.

    Args:
        errors: List of semantic errors from analyzer
    """
    if errors:
        error_messages = [str(error) for error in errors]
        raise AssertionError(
            f"Expected no errors, but got {len(errors)} errors:\n"
            + "\n".join(f"  - {msg}" for msg in error_messages)
        )
    assert errors == []


def assert_error_count(errors, expected_count):
    """
    Assert exact number of semantic errors.
    Provides detailed error information if assertion fails.

    Args:
        errors: List of semantic errors from analyzer
        expected_count: Expected number of errors
    """
    actual_count = len(errors)
    if actual_count != expected_count:
        error_messages = [str(error) for error in errors]
        raise AssertionError(
            f"Expected {expected_count} errors, but got {actual_count} errors:\n"
            + "\n".join(f"  - {msg}" for msg in error_messages)
        )


def assert_error_contains(errors, substring):
    """
    Assert that at least one error message contains the given substring.

    Args:
        errors: List of semantic errors from analyzer
        substring: Substring to search for in error messages
    """
    error_messages = [str(error) for error in errors]
    if not any(substring in msg for msg in error_messages):
        raise AssertionError(
            f"Expected an error containing '{substring}', but got errors:\n"
            + "\n".join(f"  - {msg}" for msg in error_messages)
        )


def assert_multiple_errors_contain(errors, substrings):
    """
    Assert that error messages contain all specified substrings (one per error).

    Args:
        errors: List of semantic errors from analyzer
        substrings: List of substrings to search for
    """
    error_messages = [str(error) for error in errors]
    missing_substrings = []

    for substring in substrings:
        if not any(substring in msg for msg in error_messages):
            missing_substrings.append(substring)

    if missing_substrings:
        raise AssertionError(
            f"Expected errors containing {missing_substrings}, but got errors:\n"
            + "\n".join(f"  - {msg}" for msg in error_messages)
        )


def parse_and_analyze(source):
    """
    Convenience function to parse and analyze source code.

    Args:
        source: Hexen source code string

    Returns:
        tuple: (ast, errors) from parsing and analysis
    """
    parser = HexenParser()
    analyzer = SemanticAnalyzer()
    ast = parser.parse(source)
    errors = analyzer.analyze(ast)
    return ast, errors


# =============================================================================
# COMMON ASSERTION PATTERNS
# =============================================================================


def assert_type_mismatch_error(errors, variable_name, expected_type, actual_type):
    """Assert specific type mismatch error pattern."""
    assert_error_contains(
        errors, f"variable '{variable_name}' declared as {expected_type}"
    )
    assert_error_contains(errors, f"assigned value of type {actual_type}")


def assert_immutable_assignment_error(errors, variable_name):
    """Assert specific immutable variable assignment error pattern."""
    assert_error_contains(
        errors, f"Cannot assign to immutable variable '{variable_name}'"
    )


def assert_undefined_variable_error(errors, variable_name):
    """Assert specific undefined variable error pattern."""
    assert_error_contains(errors, f"Undefined variable: '{variable_name}'")


def assert_precision_loss_error(errors):
    """Assert precision loss error pattern."""
    error_messages = [str(error).lower() for error in errors]
    precision_keywords = ["truncation", "precision", "narrowing"]
    has_precision_error = any(
        any(keyword in msg for keyword in precision_keywords) for msg in error_messages
    )
    if not has_precision_error:
        raise AssertionError(
            "Expected a precision loss error, but got:\n"
            + "\n".join(f"  - {msg}" for msg in [str(e) for e in errors])
        )


# =============================================================================
# SESSION 1 VALIDATION
# =============================================================================

# This module provides standardized utilities for all semantic tests
# following the refactoring plan from SEMANTIC_TESTS_REFACTORING_PLAN.md
