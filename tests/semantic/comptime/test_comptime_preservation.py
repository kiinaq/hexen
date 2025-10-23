"""
Comptime Type Adaptation in Expression Blocks Tests

Tests comptime type adaptation within expression blocks (all expression blocks now require explicit types):
- Expression blocks with explicit type annotations allow comptime values to adapt
- Comptime values (literals, arithmetic) adapt to explicit target types
- "One computation, multiple uses" pattern - same comptime computation adapts to different explicit types
- Integration with existing type system and comptime infrastructure

NOTE: After Phase 1 implementation, ALL expression blocks assigned to variables require explicit type annotations.
This file tests that comptime VALUES still adapt correctly within those explicitly-typed blocks.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestExpressionBlockInfrastructure:
    """Test expression block analysis infrastructure with explicit type requirements."""

    def test_expression_block_analysis_methods_available(self):
        """Test expression block analysis methods are available and functional."""
        analyzer = SemanticAnalyzer()

        # Test that expression block analysis methods exist (legacy methods kept for safety)
        assert hasattr(analyzer.block_analyzer, "_analyze_expression_preserve_comptime")
        assert hasattr(analyzer.block_analyzer, "_analyze_expression_with_context")
        assert hasattr(
            analyzer.block_analyzer, "_validate_runtime_block_context_requirement"
        )

        # Test that methods are callable (basic infrastructure test)
        assert callable(analyzer.block_analyzer._analyze_expression_preserve_comptime)
        assert callable(analyzer.block_analyzer._analyze_expression_with_context)
        assert callable(
            analyzer.block_analyzer._validate_runtime_block_context_requirement
        )

    def test_expression_block_with_explicit_type_annotation(self):
        """Test expression blocks work correctly with explicit type annotations (universal requirement)."""
        # All expression blocks now require explicit type annotations
        source = """
        func test_explicit_type() : i32 = {
            val result : i32 = {  // Explicit type REQUIRED
                val calc = 42 + 100
                -> calc
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - expression block with explicit type works
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


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


class TestExpressionBlocksWithFunctionCalls:
    """Test expression blocks containing function calls (with required explicit types)."""

    def test_expression_block_with_function_call_requires_explicit_type(self):
        """Test expression blocks with function calls require explicit type annotations."""
        source = """
        func helper() : i32 = {
            return 42
        }
        
        func test_runtime() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function call)
                val computed : i32 = helper()  // Function call triggers runtime
                -> computed
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - runtime blocks work with explicit context
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_mixed_comptime_and_runtime_values_with_explicit_type(self):
        """Test expression blocks mixing comptime values and runtime operations with explicit type."""
        source = """
        func get_multiplier() : i32 = {
            return 5
        }
        
        func test_mixed() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block
                val base = 42              // comptime_int
                val runtime_mult : i32 = get_multiplier()  // runtime function call
                val combined = base * runtime_mult   // mixed operation (comptime adapts to runtime_mult's i32)
                -> combined
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - mixed operations work with explicit context
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestComptimeAdaptationToMultipleTypes:
    """Test comptime values adapt to different explicit types ('one computation, multiple uses' pattern)."""

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
    """Test nested expression blocks with different evaluabilities."""

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
    """Test division operators work correctly in expression blocks."""

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


class TestExpressionBlocksWithConditionals:
    """Test expression blocks containing conditionals (require explicit types)."""

    def test_conditional_expression_requires_explicit_type(self):
        """Test conditional expressions require explicit type annotations."""
        source = """
        func test_conditional_runtime() : i32 = {
            val result : i32 = if 10 > 5 {
                -> 100
            } else {
                -> 200
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - conditional blocks work with explicit type annotation
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestReturnStatementsInExpressionBlocks:
    """Test return statements work correctly in expression blocks."""

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

    def test_conditional_expression_with_function_call(self):
        """Test conditional expressions with function calls require explicit type annotations."""
        source = """
        func get_condition() : bool = {
            return true
        }
        
        func test_runtime_early_return() : i32 = {
            val result : i32 = if get_condition() {
                -> 777
            } else {
                -> 0
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have no errors - runtime blocks work with explicit type annotation
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestComptimeAdaptationComprehensive:
    """Test comprehensive comptime value adaptation within explicitly-typed expression blocks."""

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

    def test_expression_block_infrastructure_available(self):
        """Test expression block analysis infrastructure is available for validation."""
        analyzer = SemanticAnalyzer()

        # Test that all comptime preservation infrastructure is available for enhanced error messages
        assert hasattr(analyzer.block_analyzer, "_validate_runtime_block_context")
        assert hasattr(analyzer.block_analyzer, "_get_runtime_operation_reason")

        # Test that runtime detection infrastructure is still available
        assert hasattr(analyzer.block_analyzer, "_contains_runtime_operations")
        assert hasattr(analyzer.block_analyzer, "_contains_function_calls")
        assert hasattr(analyzer.block_analyzer, "_contains_conditionals")

        # Test that evaluability infrastructure is still available
        assert hasattr(analyzer.block_analyzer, "_classify_block_evaluability")
        assert hasattr(analyzer.block_analyzer, "_has_comptime_only_operations")
        assert hasattr(analyzer.block_analyzer, "_has_runtime_variables")
