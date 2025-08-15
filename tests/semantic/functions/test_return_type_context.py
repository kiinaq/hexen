"""
Return Type Context and Validation Tests

Tests for comprehensive return statement analysis and return type context validation.
This test file validates the key function system feature where function return types
provide context for mixed concrete type resolution in return statements.

Test coverage:
1. Return statement analysis (expression type checking, void function validation)
2. Return type context (function return type provides context for mixed type expressions)
3. Function body return validation (execution paths, consistency)
4. Integration with unified block system (assign/return dual capability)
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestReturnStatementAnalysis:
    """Test return statement analysis functionality."""

    def test_return_expression_type_checking_all_types(self):
        """Test return expressions are properly type-checked against function return type."""
        program = """
        func test_i32() : i32 = {
            return 42
        }
        
        func test_f64() : f64 = {
            return 3.14
        }
        
        func test_bool() : bool = {
            return true
        }
        
        func test_string() : string = {
            return "hello"
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_return_type_mismatch_errors(self):
        """Test proper error reporting for return type mismatches."""
        program = """
        func wrong_return() : i32 = {
            return "not an integer"
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Return type mismatch" in str(errors[0])

    def test_void_function_bare_return_validation(self):
        """Test that void functions properly validate bare returns."""
        program = """
        func valid_void() : void = {
            return
        }
        
        func invalid_void() : void = {
            return 42
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Void function cannot return a value" in str(errors[0])

    def test_non_void_function_requires_return_value(self):
        """Test that non-void functions cannot have bare returns."""
        program = """
        func needs_value() : i32 = {
            return
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "cannot have bare return statement" in str(errors[0])


class TestReturnTypeContext:
    """Test return type context functionality."""

    def test_function_return_requires_explicit_conversions_for_mixed_types(self):
        """Test that function return statements require explicit conversions for mixed concrete types."""
        program = """
        func mixed_operation(a: i32, b: f64) : f64 = {
            return a + b
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        # This should fail because mixed concrete types require explicit conversions
        # following TYPE_SYSTEM.md transparent costs principle
        assert len(errors) == 1
        assert "Mixed concrete types" in str(errors[0])
        assert "requires explicit conversion" in str(errors[0])

    def test_function_return_with_explicit_conversions_works(self):
        """Test that function return statements work with explicit conversions for mixed concrete types."""
        program = """
        func mixed_operation_correct(a: i32, b: f64) : f64 = {
            return a:f64 + b
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        # This should work because explicit conversion is provided
        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_comptime_type_resolution_in_return_context(self):
        """Test comptime types resolve properly in return context."""
        program = """
        func comptime_math() : f64 = {
            return 42 + 100 * 3.14
        }
        
        func same_expression_different_context() : i32 = {
            val expr = 42 + 100
            return expr
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_explicit_conversion_still_required_for_precision_loss(self):
        """Test that explicit conversions are still required for precision loss in returns."""
        program = """
        func precision_loss() : f32 = {
            val big_number : f64 = 12345.6789012345
            return big_number
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "precision loss" in str(errors[0]).lower()

    def test_return_type_context_with_complex_expressions(self):
        """Test return type context works with complex expressions."""
        program = """
        func complex_calculation(base: i32, multiplier: f32, offset: f64) : f64 = {
            return base:f64 * multiplier:f64 + offset / 2.0
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"


class TestFunctionBodyReturnValidation:
    """Test function body return validation."""

    def test_void_function_no_explicit_return_required(self):
        """Test that void functions don't require explicit returns."""
        program = """
        func side_effect_only() : void = {
            val temp = 42
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_early_return_handling_in_expression_blocks(self):
        """Test early return handling in expression blocks (simplified - no if statements yet)."""
        program = """
        func simple_early_return(input: i32) : i32 = {
            val result = {
                return input * 2
            }
            return result + 10
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        # This should work - expression block returns early, skipping the assign
        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_multiple_return_paths_consistency(self):
        """Test that multiple return paths are consistent (simplified)."""
        program = """
        func multiple_returns(condition: bool) : i32 = {
            return 42
        }
        
        func another_return() : i32 = {
            return 100
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        # For now, we test that basic return statements work consistently
        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_void_function_consistency_with_multiple_returns(self):
        """Test void function consistency with multiple return points (simplified)."""
        program = """
        func void_with_early_return() : void = {
            return
        }
        
        func void_with_late_return() : void = {
            val temp = 42
            return
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"


class TestUnifiedBlockSystemIntegration:
    """Test integration with unified block system assign/return dual capability."""

    def test_expression_block_assign_for_value_production(self):
        """Test expression blocks use assign for value production."""
        program = """
        func expression_block_assign() : i32 = {
            val computation = {
                val base = 42
                val result = base * 2
                assign result
            }
            return computation
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_expression_block_return_for_early_function_exit(self):
        """Test expression blocks use return for early function exits (simplified)."""
        program = """
        func validation_pattern(input: i32) : i32 = {
            val validated = {
                return input * 2
            }
            return validated + 10
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        # Expression block with return should work (early function exit)
        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_statement_block_return_function_exit_only(self):
        """Test statement blocks use return for function exits only (simplified)."""
        program = """
        func statement_block_returns() : i32 = {
            {
                val setup = 42
                return setup
            }
            return 100
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_dual_capability_validation_caching_pattern(self):
        """Test dual capability enables validation and caching patterns (simplified)."""
        program = """
        func expensive_operation(input: f64) : f64 = {
            return input * 3.14
        }
        
        func simple_pattern(value: f64) : f64 = {
            val result = {
                val computed = expensive_operation(value)
                assign computed
            }
            return result
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_expression_block_bare_return_error(self):
        """Test that expression blocks cannot have bare returns (need value for function exit)."""
        program = """
        func invalid_bare_return_in_expression_block() : i32 = {
            val result = {
                return
            }
            return 42
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) >= 1
        # Look for the specific error about expression blocks requiring values
        error_messages = [str(e) for e in errors]
        assert any(
            "Expression block 'return' statement must have a value" in msg
            for msg in error_messages
        )


class TestAdvancedReturnTypeContextScenarios:
    """Test advanced scenarios for return type context."""

    def test_function_composition_with_return_type_context(self):
        """Test function composition leveraging return type context."""
        program = """
        func scale_value(value: f64, factor: f64) : f64 = {
            return value * factor
        }
        
        func truncate_to_int(value: f64) : i32 = {
            return value:i32
        }
        
        func process_chain(input: i32) : i32 = {
            val scaled = scale_value(input:f64, 2.5)
            val final = truncate_to_int(scaled)
            return final
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_division_operations_in_return_context(self):
        """Test division operations with return type context."""
        program = """
        func calculate_average(total: i32, count: i32) : f64 = {
            return total / count
        }
        
        func calculate_quotient(dividend: i32, divisor: i32) : i32 = {
            return dividend \\ divisor
        }
        
        func mixed_division(base: i64, factor: f32) : f64 = {
            return base:f64 / factor:f64
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    def test_comparison_operations_in_return_context(self):
        """Test comparison operations work properly in return context."""
        program = """
        func compare_values(a: i32, b: i32) : bool = {
            return a > b
        }
        
        func validate_range(value: f64, min: f64, max: f64) : bool = {
            return value >= min && value <= max
        }
        
        func mixed_comparison(int_val: i32, float_val: f64) : bool = {
            return int_val:f64 < float_val
        }
        """
        parser = HexenParser()
        analyzer = SemanticAnalyzer()

        ast = parser.parse(program)
        errors = analyzer.analyze(ast)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"
