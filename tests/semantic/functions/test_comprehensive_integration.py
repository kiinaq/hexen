"""
Comprehensive integration tests for the complete function system.

Tests all function features working together including declarations, calls,
parameters, returns, type system integration, and unified block system.
This validates the complete function system as specified in FUNCTION_SYSTEM.md.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestFunctionSystemIntegration:
    """Test complete function system integration with all features."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_complete_function_program(self):
        """Test a complete program using all function features."""
        code = """
        func calculate_area(width: f64, height: f64) : f64 = {
            return width * height
        }

        func increment_counter(mut counter: i32, amount: i32) : i32 = {
            counter = counter + amount
            return counter
        }

        func validate_and_scale(input: i64, mut result: f32, factor: f64) : f32 = {
            val validated : f32 = input:f32
            result = validated * factor:f32
            return result
        }

        func main() : i32 = {
            val area : f64 = calculate_area(10.0, 20.0)
            val count : i32 = increment_counter(100, 25)
            mut temp : f32 = 0.0
            val scaled : f32 = validate_and_scale(42, temp, 2.5)
            return count
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_nested_function_calls(self):
        """Test complex nested function call scenarios."""
        code = """
        func add(a: i32, b: i32) : i32 = {
            return a + b
        }

        func multiply(a: i32, b: i32) : i32 = {
            return a * b
        }

        func complex_calc(x: i32, y: i32, z: i32) : i32 = {
            val intermediate : i32 = add(multiply(x, y), z)
            val final_result : i32 = multiply(intermediate, add(2, 3))
            return final_result
        }

        func main() : i32 = {
            return complex_calc(add(1, 2), multiply(3, 4), add(5, 6))
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_functions_with_expression_blocks(self):
        """Test functions using expression blocks with assign/return dual capability."""
        code = """
        func safe_multiply(numerator: f64, factor: f64) : f64 = {
            val result : f64 = {
                assign numerator * factor
            }
            return result
        }

        func cached_calculation(key: i32) : f64 = {
            val computed = {
                val base : f64 = key:f64 * 3.14
                assign base * 2.0
            }
            return computed + 1.0
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_comptime_type_preservation_across_functions(self):
        """Test comptime type preservation in function call chains."""
        code = """
        func process_int(value: i64) : i64 = {
            return value * 2
        }

        func process_float(value: f64) : f64 = {
            return value * 3.14
        }

        func flexible_processing() : void = {
            val comptime_value = 42 + 100  // comptime_int preserved
            
            // Same expression adapts to different parameter types
            val as_int : i64 = process_int(comptime_value)     // comptime_int → i64
            val as_float : f64 = process_float(comptime_value) // comptime_int → f64
            
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mixed_parameter_types_with_conversions(self):
        """Test functions with mixed parameter types requiring explicit conversions."""
        code = """
        func mixed_types(small: i32, large: i64, precise: f64, single: f32) : f64 = {
            // All mixed concrete types require explicit conversions
            val converted : f64 = small:f64 + large:f64 + precise + single:f64
            return converted
        }

        func caller() : f64 = {
            val a : i32 = 10
            val b : i64 = 20
            val c : f64 = 3.14
            val d : f32 = 2.5
            
            return mixed_types(a, b, c, d)
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_mutable_parameters_with_complex_logic(self):
        """Test mutable parameters in complex scenarios."""
        code = """
        func transform_data(mut accumulator: f64, inputs: i32, factor: f64) : f64 = {
            // Mutable parameter modified multiple times
            accumulator = accumulator + inputs:f64
            accumulator = accumulator * factor
            accumulator = accumulator / 2.0
            
            val final_adjustment = {
                accumulator = accumulator * 1.1
                assign accumulator
            }
            
            return final_adjustment
        }

        func processing_pipeline() : f64 = {
            mut total : f64 = 0.0
            val step1 : f64 = transform_data(total, 10, 2.0)
            val step2 : f64 = transform_data(step1, 20, 1.5)
            return step2
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_all_return_types_and_patterns(self):
        """Test functions with all possible return types and return patterns."""
        code = """
        func return_i32() : i32 = { return 42 }
        func return_i64() : i64 = { return 9223372036854775807 }
        func return_f32() : f32 = { return 3.14 }
        func return_f64() : f64 = { return 2.718281828459045 }
        func return_bool() : bool = { return true }
        func return_string() : string = { return "hello" }
        func return_void() : void = { return }

        func complex_returns(flag: bool) : i32 = {
            val result = {
                val computation = 10 * 20
                assign computation
            }
            
            return result + 3
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_parameter_scoping_and_shadowing(self):
        """Test parameter scoping with local variable interactions."""
        code = """
        func scoping_test(param1: i32, param2: f64, mut param3: i64) : f64 = {
            val local_var : i32 = param1 * 2
            
            {
                // Parameters accessible in nested blocks
                val nested_calc : f64 = param2 * 3.14
                param3 = param1:i64 + 100  // Mutable parameter modification
            }
            
            // Local variable shadows parameter
            val param2 : f64 = 999.0  // Shadow param2
            
            val final_result = {
                // Use shadowed variable and modified parameter
                assign param2 + param3:f64
            }
            
            return final_result
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"


class TestFunctionErrorIntegration:
    """Test integrated error scenarios across function features."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_function_call_argument_type_errors(self):
        """Test comprehensive function call argument type validation."""
        code = """
        func strict_types(small: i32, large: i64, precise: f64) : f64 = {
            return small:f64 + large:f64 + precise
        }

        func caller() : f64 = {
            val a : i64 = 10
            val b : f32 = 3.14
            val c : i32 = 20
            
            // Multiple type mismatches - requires explicit conversions
            return strict_types(a, b, c)  // Error: i64→i32, f32→i64, i32→f64
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should have multiple type conversion errors

    def test_immutable_parameter_reassignment_errors(self):
        """Test immutable parameter reassignment error detection."""
        code = """
        func bad_function(readonly: i32, mut mutable: i32) : i32 = {
            readonly = 100  // Error: Cannot reassign immutable parameter
            mutable = 200   // OK: Mutable parameter
            return readonly + mutable
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Cannot reassign immutable parameter 'readonly'" in error_msg
        assert "Use 'mut readonly: i32' for mutable parameters" in error_msg

    def test_return_type_mismatch_errors(self):
        """Test return type validation across complex scenarios."""
        code = """
        func wrong_return_type() : i32 = {
            return "string"  // Error: string cannot be returned as i32
        }

        func mixed_concrete_return(a: i32, b: f64) : f64 = {
            return a + b  // Error: Mixed concrete types require explicit conversion
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should have return type and mixed type errors

    def test_undefined_function_call_errors(self):
        """Test undefined function call error handling."""
        code = """
        func caller() : i32 = {
            val result1 : i32 = undefined_function(10, 20)  // Error: undefined function
            val result2 : i32 = another_missing_func()      // Error: undefined function
            return result1 + result2
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should have undefined function errors
        error_messages = [str(error) for error in errors]
        assert any(
            "Undefined function: 'undefined_function'" in msg for msg in error_messages
        )
        assert any(
            "Undefined function: 'another_missing_func'" in msg
            for msg in error_messages
        )

    def test_argument_count_mismatch_errors(self):
        """Test function call argument count validation."""
        code = """
        func three_params(a: i32, b: i32, c: i32) : i32 = {
            return a + b + c
        }

        func caller() : i32 = {
            val too_few : i32 = three_params(1, 2)        // Error: too few arguments
            val too_many : i32 = three_params(1, 2, 3, 4) // Error: too many arguments
            return too_few + too_many
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should have argument count errors


class TestEdgeCases:
    """Test complex edge cases and boundary conditions."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_recursive_function_calls(self):
        """Test recursive function calls (basic validation)."""
        code = """
        func factorial(n: i32) : i32 = {
            return n * factorial(n - 1)
        }

        func fibonacci(n: i32) : i32 = {
            return fibonacci(n - 1) + fibonacci(n - 2)
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_functions_with_all_literal_types(self):
        """Test functions handling all literal types correctly."""
        code = """
        func handle_all_types(
            int_val: i32,
            long_val: i64, 
            float_val: f32,
            double_val: f64,
            bool_val: bool,
            string_val: string
        ) : string = {
            return string_val
        }

        func call_with_literals() : string = {
            return handle_all_types(
                42,              // comptime_int → i32
                1000000000000,   // comptime_int → i64  
                3.14,            // comptime_float → f32
                2.718281828,     // comptime_float → f64
                true,            // bool → bool
                "test"           // string → string
            )
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_deeply_nested_expression_blocks_in_functions(self):
        """Test deeply nested expression blocks with functions."""
        code = """
        func nested_logic(input: i32) : i32 = {
            val level1 = {
                val level2 = {
                    val level3 = {
                        assign input * 2
                    }
                    assign level3 + 10
                }
                assign level2 * 3
            }
            return level1 + 5
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_complex_type_conversion_chains(self):
        """Test complex chains of type conversions in function context."""
        code = """
        func conversion_chain(base: i32) : f32 = {
            val step1 : i64 = base:i64 * 1000
            val step2 : f64 = step1:f64 / 3.14159
            val step3 : f32 = step2:f32 + 1.0
            return step3
        }

        func chained_calls() : f32 = {
            val intermediate : f32 = conversion_chain(42)
            return conversion_chain(intermediate:i32)  // f32 → i32 → chain → f32
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_function_with_maximum_complexity(self):
        """Test function with maximum complexity using all features."""
        code = """
        func kitchen_sink(
            immutable: i32,
            mut mutable: i64, 
            precise: f64,
            mut result: f32
        ) : f64 = {
            // Mutable parameter modifications
            mutable = immutable:i64 * 2
            result = precise:f32 / 3.14
            
            // Expression block with complex logic
            val computed = {
                val nested_calc = {
                    mutable = mutable + 100
                    assign mutable:f64 * 1.5
                }
                
                result = 999.0
                assign nested_calc + precise
            }
            
            // Complex final computation with explicit conversions
            val final_value : f64 = computed + mutable:f64 + result:f64
            return final_value * 0.5
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, f"Unexpected errors: {errors}"
