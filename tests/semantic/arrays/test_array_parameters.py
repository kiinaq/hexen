"""
Test Array Function Parameters - Explicit Copy Requirement

Tests the "Explicit Danger, Implicit Safety" principle for array arguments:
- Comptime arrays (literals): No [..] needed (first materialization)
- Concrete arrays (variables): Require explicit [..] copy operator
- Function returns & expression blocks: No [..] needed (fresh arrays)

This enforces transparent performance costs for array parameter passing.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestExplicitCopyRequirement:
    """Test explicit [..] requirement for concrete array arguments"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_array_no_copy_needed(self):
        """Comptime arrays (literals) don't need [..] - first materialization"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            process([1, 2, 3])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_concrete_array_requires_explicit_copy(self):
        """Concrete array variables require explicit [..] operator"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [3]i32 = [1, 2, 3]
            process(arr)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Missing explicit copy syntax for array argument"
        )
        assert_error_contains(
            errors,
            "Concrete array 'arr' requires explicit copy operator [..]"
        )
        assert_error_contains(
            errors,
            "process(arr[..])"
        )

    def test_concrete_array_with_explicit_copy_allowed(self):
        """Concrete arrays with [..] are accepted"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [3]i32 = [1, 2, 3]
            process(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_function_return_no_copy_needed(self):
        """Function returns are fresh arrays - no [..] needed"""
        source = """
        func create_array() : [3]i32 = {
            return [1, 2, 3]
        }

        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            process(create_array())
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_expression_block_inline_no_copy_needed(self):
        """Expression blocks passed inline build fresh arrays - no [..] needed"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            process({
                -> [1, 2, 3]
            })
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_expression_block_variable_requires_copy(self):
        """Expression block assigned to variable becomes concrete - requires [..]"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            val result : [3]i32 = {
                -> [1, 2, 3]
            }
            process(result)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Expression block variable is concrete, requires [..]
        assert_error_contains(
            errors,
            "Missing explicit copy syntax"
        )

    def test_multidimensional_array_requires_copy(self):
        """Multidimensional concrete arrays require [..]"""
        source = """
        func process_matrix(data: [2][3]i32) : void = {
            return
        }

        func main() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            process_matrix(matrix)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(
            errors,
            "Missing explicit copy syntax"
        )

    def test_multidimensional_array_with_copy_allowed(self):
        """Multidimensional arrays with [..] are accepted"""
        source = """
        func process_matrix(data: [2][3]i32) : void = {
            return
        }

        func main() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            process_matrix(matrix[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_multiple_array_parameters(self):
        """Multiple array parameters each require [..] for concrete args"""
        source = """
        func combine(a: [3]i32, b: [3]i32) : [3]i32 = {
            return a
        }

        func main() : void = {
            val arr1 : [3]i32 = [1, 2, 3]
            val arr2 : [3]i32 = [4, 5, 6]
            val result : [3]i32 = combine(arr1, arr2)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should have errors for both arguments
        assert len(errors) >= 2
        assert_error_contains(errors, "Missing explicit copy syntax")

    def test_multiple_parameters_with_copies_allowed(self):
        """Multiple parameters with [..] on all concrete arrays"""
        source = """
        func combine(a: [3]i32, b: [3]i32) : [3]i32 = {
            return a
        }

        func main() : void = {
            val arr1 : [3]i32 = [1, 2, 3]
            val arr2 : [3]i32 = [4, 5, 6]
            val result : [3]i32 = combine(arr1[..], arr2[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_mixed_concrete_and_comptime_arguments(self):
        """Mixing concrete arrays (need [..]) and literals (don't need [..])"""
        source = """
        func process_two(a: [3]i32, b: [3]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [3]i32 = [1, 2, 3]
            process_two(arr[..], [4, 5, 6])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)


class TestScalarParametersUnaffected:
    """Verify that scalar parameters aren't affected by array validation"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_scalar_parameter_no_copy_requirement(self):
        """Scalar parameters don't require any copy operator"""
        source = """
        func process(x: i32, y: f64) : void = {
            return
        }

        func main() : void = {
            val a : i32 = 42
            val b : f64 = 3.14
            process(a, b)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_mixed_scalar_and_array_parameters(self):
        """Functions with both scalar and array parameters"""
        source = """
        func process(count: i32, data: [3]i32, factor: f64) : void = {
            return
        }

        func main() : void = {
            val n : i32 = 5
            val arr : [3]i32 = [1, 2, 3]
            val f : f64 = 2.5
            process(n, arr[..], f)
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)
