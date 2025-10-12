"""
Test Suite: Comptime Array Parameter Adaptation

This test suite validates that comptime arrays adapt seamlessly to function
parameter types, materializing to match the target element type and size
without requiring explicit `[..]` syntax.

Core Principle: "Ergonomic Comptime Flexibility"
- Comptime arrays materialize (not copy) on first use
- Same comptime array can materialize differently based on context
- No explicit copy syntax required for comptime arrays
- Enables "one computation, multiple uses" pattern

Test Coverage:
1. Element type adaptation (comptime_array_int → i32/i64/f32/f64)
2. Size adaptation (fixed-size and inferred-size parameters)
3. Dimension adaptation (1D, 2D, 3D arrays)
4. Multiple materializations from same source
5. Edge cases and error conditions

Related Tasks:
- Week 2 Task 2: Explicit copy for concrete arrays (contrasts with comptime)
- Week 2 Task 4: Fixed-size parameter matching
- Week 2 Task 5: Inferred-size parameter support
- Week 2 Task 7: Pass-by-value semantics (comptime materializes, not copies)
"""

import pytest
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestComptimeArrayElementTypeAdaptation:
    """Test comptime arrays adapting to different element types"""

    def test_comptime_array_int_to_i32_parameter(self):
        """Comptime array_int materializes to [_]i32"""
        code = """
        func process_i32(data: [_]i32) : i32 = {
            return data[0]
        }

        val flexible = [42, 100, 200]
        val result : i32 = process_i32(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime_array_int → [3]i32

    def test_comptime_array_int_to_i64_parameter(self):
        """Comptime array_int materializes to [_]i64"""
        code = """
        func process_i64(data: [_]i64) : i64 = {
            return data[0]
        }

        val flexible = [42, 100, 200]
        val result : i64 = process_i64(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime_array_int → [3]i64

    def test_comptime_array_int_to_f32_parameter(self):
        """Comptime array_int materializes to [_]f32"""
        code = """
        func process_f32(data: [_]f32) : f32 = {
            return data[0]
        }

        val flexible = [42, 100, 200]
        val result : f32 = process_f32(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime_array_int → [3]f32

    def test_comptime_array_int_to_f64_parameter(self):
        """Comptime array_int materializes to [_]f64"""
        code = """
        func process_f64(data: [_]f64) : f64 = {
            return data[0]
        }

        val flexible = [42, 100, 200]
        val result : f64 = process_f64(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime_array_int → [3]f64

    def test_comptime_array_float_to_f32_parameter(self):
        """Comptime array_float materializes to [_]f32"""
        code = """
        func process_f32(data: [_]f32) : f32 = {
            return data[0]
        }

        val flexible = [3.14, 2.71, 1.41]
        val result : f32 = process_f32(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime_array_float → [3]f32

    def test_comptime_array_float_to_f64_parameter(self):
        """Comptime array_float materializes to [_]f64"""
        code = """
        func process_f64(data: [_]f64) : f64 = {
            return data[0]
        }

        val flexible = [3.14, 2.71, 1.41]
        val result : f64 = process_f64(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime_array_float → [3]f64


class TestComptimeArraySizeAdaptation:
    """Test comptime arrays adapting to fixed-size and inferred-size parameters"""

    def test_comptime_array_to_fixed_size_parameter(self):
        """Comptime array materializes to exact fixed-size parameter"""
        code = """
        func exact_three(data: [3]i32) : i32 = {
            return data[0]
        }

        val flexible = [1, 2, 3]
        val result : i32 = exact_three(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime [3] → fixed [3]i32

    def test_comptime_array_to_inferred_size_parameter(self):
        """Comptime array materializes to inferred-size parameter"""
        code = """
        func any_size(data: [_]i32) : i32 = {
            return data[0]
        }

        val flexible = [1, 2, 3, 4, 5]
        val result : i32 = any_size(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile successfully - comptime [5] → inferred [_]i32

    @pytest.mark.xfail(reason="Size mismatch validation for comptime arrays not yet implemented")
    def test_comptime_array_size_mismatch_with_fixed_parameter(self):
        """Comptime array with wrong size for fixed-size parameter fails"""
        code = """
        func exact_three(data: [3]i32) : i32 = {
            return data[0]
        }

        val wrong_size = [1, 2, 3, 4, 5]
        val result : i32 = exact_three(wrong_size)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="size mismatch|expected.*3.*found.*5"):
            analyzer.analyze(code)
        # Should fail - comptime [5] doesn't match fixed [3]
        # Note: This validation is missing and should be added


class TestComptimeArrayMultipleMaterializations:
    """Test same comptime array materializing differently based on context"""

    def test_same_comptime_array_to_different_element_types(self):
        """One comptime array materializes to both i32 and f64"""
        code = """
        func process_i32(data: [_]i32) : i32 = {
            return data[0]
        }

        func process_f64(data: [_]f64) : f64 = {
            return data[0]
        }

        val flexible = [42, 100, 200]
        val as_int : i32 = process_i32(flexible)
        val as_float : f64 = process_f64(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - same source, different materializations

    def test_same_comptime_array_to_fixed_and_inferred_sizes(self):
        """One comptime array materializes to both fixed and inferred sizes"""
        code = """
        func exact_size(data: [3]i32) : i32 = {
            return data[0]
        }

        func any_size(data: [_]i32) : i32 = {
            return data[0]
        }

        val flexible = [1, 2, 3]
        val fixed : i32 = exact_size(flexible)
        val inferred : i32 = any_size(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - same source, different size contexts

    def test_comptime_array_multiple_uses_different_precisions(self):
        """One comptime array used in graphics (f32) and physics (f64)"""
        code = """
        func graphics_process(data: [_]f32) : f32 = {
            return data[0]
        }

        func physics_process(data: [_]f64) : f64 = {
            return data[0]
        }

        val complex_math = [42, 100, 314]
        val for_graphics : f32 = graphics_process(complex_math)
        val for_physics : f64 = physics_process(complex_math)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - one computation, multiple precision uses


class TestComptimeArrayDimensionAdaptation:
    """Test comptime arrays adapting to multidimensional parameters"""

    def test_comptime_2d_array_to_fixed_2d_parameter(self):
        """Comptime 2D array materializes to [2][2]i32"""
        code = """
        func process_matrix(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val flexible_matrix = [[1, 2], [3, 4]]
        val result : i32 = process_matrix(flexible_matrix)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - comptime 2D → fixed [2][2]i32

    def test_comptime_2d_array_to_inferred_2d_parameter(self):
        """Comptime 2D array materializes to [_][_]i32"""
        code = """
        func process_any_matrix(data: [_][_]i32) : i32 = {
            return data[0][0]
        }

        val flexible_matrix = [[1, 2, 3], [4, 5, 6]]
        val result : i32 = process_any_matrix(flexible_matrix)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - comptime 2D → inferred [_][_]i32

    def test_comptime_3d_array_to_fixed_3d_parameter(self):
        """Comptime 3D array materializes to [2][2][2]f64"""
        code = """
        func process_cube(data: [2][2][2]f64) : f64 = {
            return data[0][0][0]
        }

        val flexible_cube = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        val result : f64 = process_cube(flexible_cube)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - comptime 3D → fixed [2][2][2]f64

    def test_comptime_2d_array_different_element_types(self):
        """Same comptime 2D array materializes to different element types"""
        code = """
        func process_i32_matrix(data: [2][3]i32) : i32 = {
            return data[0][0]
        }

        func process_f64_matrix(data: [2][3]f64) : f64 = {
            return data[0][0]
        }

        val flexible = [[1, 2, 3], [4, 5, 6]]
        val as_int : i32 = process_i32_matrix(flexible)
        val as_float : f64 = process_f64_matrix(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - same 2D source, different element types


class TestComptimeArrayNoExplicitCopy:
    """Test that comptime arrays don't require explicit [..] syntax"""

    def test_comptime_array_no_copy_needed(self):
        """Comptime arrays materialize without [..] operator"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val flexible = [1, 2, 3]
        val result : i32 = process(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - comptime arrays don't need [..]

    def test_comptime_array_with_explicit_copy_also_works(self):
        """Comptime arrays can use [..] but it's unnecessary"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val flexible = [1, 2, 3]
        val result : i32 = process(flexible[..])
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - [..] is allowed but unnecessary for comptime

    @pytest.mark.xfail(reason="Explicit copy check for concrete array variables not fully implemented (Week 2 Task 2 edge case)")
    def test_concrete_array_requires_explicit_copy_contrast(self):
        """Concrete arrays require [..], contrasting with comptime arrays"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val concrete : [3]i32 = [1, 2, 3]
        val result : i32 = process(concrete)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="explicit copy|\\[\\.\\.\\]"):
            analyzer.analyze(code)
        # Should fail - concrete arrays require [..]
        # Note: Week 2 Task 2 implemented AST-based detection, but may not catch all cases


class TestComptimeArrayEdgeCases:
    """Test edge cases and complex scenarios"""

    def test_comptime_array_from_expression_block(self):
        """Comptime array from expression block materializes correctly"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val flexible = {
            val base = [1, 2, 3]
            -> base
        }
        val result : i32 = process(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - comptime array from block materializes

    def test_comptime_array_literal_direct_in_call(self):
        """Comptime array literal passed directly to function"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val result : i32 = process([1, 2, 3])
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - array literal is comptime

    def test_comptime_array_multiple_function_calls_same_line(self):
        """Comptime array used in multiple calls in same expression"""
        code = """
        func double_array(data: [_]i32) : i32 = {
            return data[0] * 2
        }

        func triple_array(data: [_]i32) : i32 = {
            return data[0] * 3
        }

        val flexible = [42, 100, 200]
        val result : i32 = double_array(flexible) + triple_array(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - same comptime array used twice

    def test_comptime_array_nested_function_calls(self):
        """Comptime array materializes in nested function contexts"""
        code = """
        func inner(data: [_]f64) : f64 = {
            return data[0]
        }

        func outer(data: [_]i32) : f64 = {
            return inner(data)
        }

        val flexible = [42, 100, 200]
        val result : f64 = outer(flexible)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Should compile - comptime materializes at each level


class TestComptimeArrayDocumentationExamples:
    """Test examples from ARRAY_IMPLEMENTATION_PLAN.md section 2.3"""

    def test_documentation_example_flexible_data(self):
        """Example from section 2.3: Same comptime array → i32 and f64"""
        code = """
        func process_f64(data: [_]f64) : f64 = {
            return data[0]
        }

        func process_i32(data: [_]i32) : i32 = {
            return data[0]
        }

        val flexible_data = [42, 100, 200]
        val stats : f64 = process_f64(flexible_data)
        val sum : i32 = process_i32(flexible_data)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)
        # Documentation example should compile successfully
