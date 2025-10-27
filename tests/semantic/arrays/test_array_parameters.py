"""
Test Array Function Parameters - Function Integration & Parameter Passing

**Focus:** Function integration and parameter passing rules
Tests how arrays interact with function calls, focusing on the "Explicit Danger,
Implicit Safety" principle that makes performance costs transparent.

**What this file tests:**
- Explicit copy requirement ([..] for concrete arrays, not for literals)
- Fixed-size parameter matching (exact size validation)
- Comptime array adaptation (literals auto-adapt to parameter types)
- Mixed scenarios (scalars + arrays, multiple parameters, nested calls)

**Key principle: "Explicit Danger, Implicit Safety"**
- Comptime arrays (literals): No [..] needed (first materialization - safe)
- Concrete arrays (variables): Require explicit [..] (copy cost - visible)
- Function returns: No [..] needed (fresh arrays - safe)
- Expression blocks inline: No [..] needed (built fresh - safe)

**Complementary files:**
- `test_array_conversions.py` - Type conversion system validation

**Testing philosophy:**
This file ensures that array parameter passing is both safe (no hidden bugs)
and transparent (costs are visible). Tests verify that the rules are consistent,
error messages are helpful, and common patterns work as expected.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains, assert_error_count


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

        assert_error_contains(errors, "Missing explicit copy syntax for array argument")
        assert_error_contains(
            errors, "Concrete array 'arr' requires explicit copy operator [..]"
        )
        assert_error_contains(errors, "process(arr[..])")

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
        assert_error_contains(errors, "Missing explicit copy syntax")

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

        assert_error_contains(errors, "Missing explicit copy syntax")

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


class TestFixedSizeArrayParameterMatching:
    """Test exact size matching for fixed-size array parameters"""

    def setup_method(self):
        """Standard setup method used by all semantic test classes."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_exact_size_match_passes(self):
        """Fixed-size parameters accept exact size matches"""
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

    def test_size_mismatch_error(self):
        """Fixed-size parameters reject different sizes"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [4]i32 = [1, 2, 3, 4]
            process(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "Array size mismatch")
        assert_error_contains(errors, "expected 3, got 4")
        assert_error_contains(errors, "[3]i32")
        assert_error_contains(errors, "[4]i32")

    def test_smaller_array_rejected(self):
        """Smaller arrays also rejected (not just larger)"""
        source = """
        func process(data: [5]i32) : void = {
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

        assert_error_contains(errors, "Array size mismatch")
        assert_error_contains(errors, "expected 5, got 3")

    def test_multidimensional_exact_match(self):
        """Multidimensional arrays require exact dimension match"""
        source = """
        func process(data: [2][3]i32) : void = {
            return
        }

        func main() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            process(matrix[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_multidimensional_first_dim_mismatch(self):
        """Multidimensional arrays - first dimension mismatch"""
        source = """
        func process(data: [2][3]i32) : void = {
            return
        }

        func main() : void = {
            val matrix : [3][3]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            process(matrix[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "Array size mismatch")
        assert_error_contains(errors, "[2][3]i32")
        assert_error_contains(errors, "[3][3]i32")

    def test_multidimensional_second_dim_mismatch(self):
        """Multidimensional arrays - second dimension mismatch"""
        source = """
        func process(data: [2][3]i32) : void = {
            return
        }

        func main() : void = {
            val matrix : [2][4]i32 = [[1, 2, 3, 4], [5, 6, 7, 8]]
            process(matrix[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "Array size mismatch")
        assert_error_contains(errors, "[2][3]i32")
        assert_error_contains(errors, "[2][4]i32")

    def test_dimension_count_mismatch(self):
        """1D vs 2D arrays are incompatible"""
        source = """
        func process(data: [6]i32) : void = {
            return
        }

        func main() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            process(matrix[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "Array dimension mismatch")
        assert_error_contains(errors, "1D array")
        assert_error_contains(errors, "2D array")

    def test_element_type_mismatch(self):
        """Element types must match even if sizes match"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            val arr : [3]f64 = [1.0, 2.0, 3.0]
            process(arr[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "element type mismatch")
        assert_error_contains(errors, "[3]i32")
        assert_error_contains(errors, "[3]f64")

    def test_multiple_parameters_all_must_match(self):
        """All array parameters must have exact size matches"""
        source = """
        func process(a: [3]i32, b: [4]i32) : void = {
            return
        }

        func main() : void = {
            val arr1 : [3]i32 = [1, 2, 3]
            val arr2 : [4]i32 = [4, 5, 6, 7]
            process(arr1[..], arr2[..])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_no_errors(errors)

    def test_comptime_arrays_adapt_to_size(self):
        """Comptime array literals adapt to parameter size"""
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

    def test_comptime_wrong_size_error(self):
        """Comptime arrays with wrong size are rejected"""
        source = """
        func process(data: [3]i32) : void = {
            return
        }

        func main() : void = {
            process([1, 2, 3, 4])
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert_error_contains(errors, "size mismatch")
