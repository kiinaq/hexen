"""
Comptime Type Adaptation Tests

Tests the core comptime type system feature: adaptation of comptime values
to concrete types based on explicit type annotations in expression blocks.

FOCUS: Type adaptation behavior (not block semantics)
COMPLEMENTS: tests/semantic/blocks/ (which focus on block semantics)

Core features tested:
1. Comptime values adapt to explicit target types (i32, i64, f32, f64)
2. "One computation, multiple uses" - same literal adapts to different types
3. Division operators produce correct comptime types (/ → float, \\ → int)
4. Nested blocks preserve comptime adaptation capabilities
5. Complex scenarios mixing comptime and explicit types

NOTE: After Phase 1 implementation, ALL expression blocks assigned to variables
require explicit type annotations. This file tests that comptime VALUES still
adapt correctly within those explicitly-typed blocks.

CONSOLIDATION NOTE: This file previously had 18 tests. After overlap analysis
with tests/semantic/blocks/, 7 duplicate tests were removed (39% reduction).
The remaining 11 tests (61%) validate unique comptime type adaptation behavior
that is not tested elsewhere.

Removed duplicates:
- Infrastructure tests → Covered by test_block_evaluability.py
- Runtime operation tests → Covered by test_runtime_operations.py
- Basic expression block tests → Covered by test_expression_blocks.py
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestComptimeValueAdaptation:
    """Test comptime value adaptation within explicitly-typed expression blocks."""

    def test_comptime_int_adapts_to_explicit_i32_type(self):
        """Test comptime_int values adapt to explicit i32 type annotation in expression blocks."""
        source = """
        func test_comptime_int() : i32 = {
            val flexible : i32 = {
                val base = 42
                val multiplier = 100
                val result = base * multiplier
                -> result
            }
            return flexible
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime arithmetic should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_comptime_float_adapts_to_explicit_f64_type(self):
        """Test comptime_float values adapt to explicit f64 type annotation in expression blocks."""
        source = """
        func test_comptime_float() : f64 = {
            val flexible : f64 = {  // Explicit type required (f64)
                val base = 42
                val factor = 3.14
                val result = base * factor
                -> result
            }
            return flexible
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime values adapt to explicit type
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_complex_comptime_arithmetic_with_explicit_type(self):
        """Test complex comptime arithmetic adapts to explicit type annotation in expression blocks."""
        source = """
        func test_complex_comptime() : f64 = {
            val computation : f64 = {  // Explicit type required for runtime block (contains concrete variable)
                val step1 = 42 + 100
                val step2 = step1 * 3.14
                val step3 : f64 = step2 / 2.0  // Float division requires explicit type
                -> step3
            }
            return computation
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - complex comptime operations should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestComptimeAdaptationToMultipleTypes:
    """
    Test comptime values adapt to different explicit types ('one computation, multiple uses' pattern).

    This is the CORE FEATURE of Hexen's comptime system - the same literal or computation
    can adapt to different concrete types based on context, providing ergonomic code reuse
    without explicit conversions.

    UNIQUE: This pattern is not tested anywhere else in the test suite.
    """

    def test_same_comptime_computation_adapts_to_different_explicit_types(self):
        """Test same comptime computation adapts to i32, i64, and f64 based on explicit type annotations."""
        source = """
        func test_as_i32() : i32 = {
            val flexible : i32 = {  // Explicit type required
                val calc = 42 + 100 * 3
                -> calc
            }
            return flexible  // comptime_int adapts to i32
        }

        func test_as_i64() : i64 = {
            val same_calc : i64 = {  // Explicit type required (i64 here)
                val calc = 42 + 100 * 3  // Same computation source
                -> calc
            }
            return same_calc  // comptime_int adapts to i64
        }

        func test_as_f64() : f64 = {
            val another_calc : f64 = {  // Explicit type required (f64 here)
                val calc = 42 + 100 * 3  // Same computation source
                -> calc
            }
            return another_calc  // comptime_int adapts to f64
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime values adapt to explicit types
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_comptime_float_computation_adapts_to_f32_and_f64(self):
        """Test same comptime float computation adapts to f32 and f64 based on explicit type annotations."""
        source = """
        func test_as_f32() : f32 = {
            val flexible : f32 = {  // Explicit type required
                val calc = 42 * 3.14159
                -> calc
            }
            return flexible  // comptime_float adapts to f32
        }

        func test_as_f64() : f64 = {
            val same_calc : f64 = {  // Explicit type required (different type)
                val calc = 42 * 3.14159  // Same computation source
                -> calc
            }
            return same_calc  // comptime_float adapts to f64
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime values adapt to explicit types
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestNestedExpressionBlocks:
    """Test nested expression blocks preserve comptime adaptation through nesting levels."""

    def test_nested_expression_blocks_with_explicit_types(self):
        """Test nested expression blocks each require explicit types, comptime values adapt correctly."""
        source = """
        func test_nested_comptime() : f64 = {
            val outer : f64 = {  // Explicit type required (f64 for outer)
                val inner : i32 = {  // Explicit type required (i32 for inner)
                    val calc = 42 + 100
                    -> calc  // comptime_int adapts to i32
                }
                val scaled = inner * 3.14  // i32 * comptime_float -> comptime_float
                -> scaled  // comptime_float adapts to f64
            }
            return outer
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - nested expression blocks with explicit types
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_nested_blocks_mixing_comptime_and_runtime_values(self):
        """Test nested expression blocks mixing comptime values and runtime operations."""
        source = """
        func get_base() : i32 = {
            return 50
        }

        func test_mixed_nested() : f64 = {
            val outer : f64 = {  // Explicit type required for runtime block
                val comptime_part : i32 = {
                    val calc = 42 * 2
                    -> calc  // Compile-time evaluable -> comptime_int
                }
                val runtime_part : i32 = get_base()  // Runtime function call -> i32
                val combined = comptime_part + runtime_part  // comptime_int + i32 -> i32 (comptime adapts)
                -> combined:f64  // Explicit conversion to match block type
            }
            return outer
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - mixed nested scenarios should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestDivisionOperatorsInBlocks:
    """
    Test division operators produce correct comptime types in expression blocks.

    Division operators in Hexen have unique type semantics:
    - / (float division) always produces comptime_float
    - \\ (integer division) always produces comptime_int

    These tests validate that the division result types are correct for adaptation.
    """

    def test_float_division_in_expression_block_with_explicit_type(self):
        """Test float division (/) produces comptime_float that adapts to explicit f64 type."""
        source = """
        func test_float_division() : f64 = {
            val precise : f64 = {  // Explicit type required
                val numerator = 22
                val denominator = 7
                -> numerator / denominator  // comptime_int / comptime_int -> comptime_float adapts to f64
            }
            return precise
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime float division adapts to explicit type
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_integer_division_in_expression_block_with_explicit_type(self):
        """Test integer division (\\) produces comptime_int that adapts to explicit i32 type."""
        source = """
        func test_integer_division() : i32 = {
            val efficient : i32 = {
                val total = 100
                val parts = 3
                val result = total \\ parts  // comptime integer division
                -> result
            }
            return efficient  // comptime_int -> i32
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime integer division should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestReturnStatementsInExpressionBlocks:
    """Test expression blocks with comptime values and return statements."""

    def test_expression_block_with_comptime_values(self):
        """Test expression blocks with comptime values and explicit type annotations."""
        source = """
        func test_early_return() : i32 = {
            val result : i32 = {
                val base = 42  // comptime value
                val check = base > 30  // comptime comparison
                // For demonstration: comptime block that can preserve flexibility
                -> base * 2  // comptime operation
            }
            return result  // Uses the computed result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - comptime blocks preserve flexibility
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestComptimeAdaptationComprehensive:
    """Test comprehensive comptime value adaptation in complex real-world scenarios."""

    def test_comptime_adaptation_with_mixed_scenarios(self):
        """Test comptime values adapt correctly in mixed scenarios with explicit type annotations."""
        source = """
        func helper(x: i32) : i32 = {
            return x * 2
        }

        func test_comprehensive() : f64 = {
            // Expression block with explicit type required
            val comptime_calc : f64 = {  // Explicit type required (f64)
                val base = 42 + 100
                val scaled = base * 3.14
                -> scaled  // comptime_float adapts to f64
            }

            // Runtime block with function call - explicit type required
            val runtime_calc : f64 = {
                val runtime_val : i32 = helper(10)  // Function call
                val combined = runtime_val:f64 + comptime_calc  // Explicit conversion for mixed types
                -> combined
            }

            return runtime_calc
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - all comptime preservation patterns work together
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
