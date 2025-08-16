"""
Test suite for function call semantic analysis in Hexen

This module provides comprehensive testing for function call resolution,
parameter type checking, and argument validation implemented in Session 7.

Test Coverage:
- Function call resolution (name lookup, argument count validation)
- Type system integration (comptime type adaptation, explicit conversions)
- Complex argument handling (expressions, nested calls, comptime preservation)
- Error cases (undefined functions, type mismatches, argument count errors)
- Integration with existing language features

Related Implementation:
- src/hexen/semantic/function_analyzer.py: Function call analysis logic
- src/hexen/semantic/expression_analyzer.py: Function call in expression context
- src/hexen/semantic/analyzer.py: Main semantic analyzer integration

Quality Standards:
- All tests use unique function names to avoid conflicts
- Comprehensive positive and negative test cases
- Clear, descriptive test names and documentation
- Integration with existing semantic test framework
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
    assert_error_contains,
)


class TestValidFunctionCalls(StandardTestBase):
    """Test valid function call scenarios"""

    def test_simple_function_call_no_arguments(self):
        """Test basic function call with no arguments"""
        source = """
        func get_value() : i32 = {
            return 42
        }
        
        func main() : i32 = {
            val result = get_value()
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_single_argument(self):
        """Test function call with one argument"""
        source = """
        func double_value(x: i32) : i32 = {
            return x * 2
        }
        
        func main() : i32 = {
            val result = double_value(21)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_multiple_arguments(self):
        """Test function call with multiple arguments"""
        source = """
        func add_three(a: i32, b: i32, c: i32) : i32 = {
            return a + b + c
        }
        
        func main() : i32 = {
            val result = add_three(10, 20, 30)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_all_parameter_types(self):
        """Test function call with all supported parameter types"""
        source = """
        func process_all(
            int_val: i32,
            long_val: i64, 
            float_val: f32,
            double_val: f64,
            text_val: string,
            bool_val: bool
        ) : i32 = {
            return 42
        }
        
        func main() : i32 = {
            val result = process_all(1, 2, 3.0, 4.0, "text", true)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_nested_function_calls(self):
        """Test nested function calls"""
        source = """
        func inner(x: i32) : i32 = {
            return x + 1
        }
        
        func outer(y: i32) : i32 = {
            return y * 2
        }
        
        func main() : i32 = {
            val result = outer(inner(10))
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_in_return_statement(self):
        """Test function call as return value"""
        source = """
        func calculate(x: i32) : i32 = {
            return x * 5
        }
        
        func main() : i32 = {
            return calculate(8)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_with_variables(self):
        """Test function call using variables as arguments"""
        source = """
        func multiply(a: i32, b: i32) : i32 = {
            return a * b
        }
        
        func main() : i32 = {
            val x = 6
            val y = 7
            val result = multiply(x, y)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestTypeSystemIntegration(StandardTestBase):
    """Test function calls with type system integration"""

    def test_comptime_type_adaptation_to_parameters(self):
        """Test comptime types adapting to parameter contexts"""
        source = """
        func test_adaptation(int_param: i32, long_param: i64, float_param: f64) : i32 = {
            return 0
        }
        
        func main() : i32 = {
            // Comptime literals adapt to parameter types
            val result = test_adaptation(42, 100, 3.14)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_same_concrete_types_allowed(self):
        """Test same concrete types work without conversion"""
        source = """
        func process_concrete(a: i32, b: i32) : i32 = {
            return a + b
        }
        
        func main() : i32 = {
            val x : i32 = 10
            val y : i32 = 20
            val result = process_concrete(x, y)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_explicit_conversions_required_for_mixed_types(self):
        """Test explicit conversions work for mixed concrete types"""
        source = """
        func mixed_params(small: i32, large: i64) : i32 = {
            return 0
        }
        
        func main() : i32 = {
            val long_val : i64 = 1000
            val int_val : i32 = 100
            
            // Explicit conversion required for i64 -> i32
            val result = mixed_params(long_val:i32, int_val:i64)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_return_type_context(self):
        """Test function return type provides context"""
        source = """
        func get_float() : f64 = {
            return 42  // comptime_int -> f64 (return type context)
        }
        
        func get_precise() : f32 = {
            return 3.14  // comptime_float -> f32 (return type context)
        }
        
        func main() : i32 = {
            val f1 = get_float()
            val f2 = get_precise()
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_type_preservation_in_expressions(self):
        """Test comptime types preserved until parameter context"""
        source = """
        func calculate(base: f64, factor: f64) : f64 = {
            return base * factor
        }
        
        func main() : i32 = {
            // Comptime expression stays flexible until function call
            val math_expr = 42 + 100  // comptime_int (preserved)
            val result = calculate(math_expr, 2.5)  // adapts to f64
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_mixed_comptime_and_concrete_arguments(self):
        """Test mixing comptime and concrete types in arguments"""
        source = """
        func mixed_types(a: i32, b: f64, c: i64) : i32 = {
            return 0
        }
        
        func main() : i32 = {
            val concrete_int : i32 = 50
            val concrete_float : f64 = 2.5
            
            // Mix comptime and concrete arguments
            val result = mixed_types(concrete_int, concrete_float, 1000)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComplexArgumentHandling(StandardTestBase):
    """Test complex expression arguments and edge cases"""

    def test_binary_expression_arguments(self):
        """Test binary expressions as function arguments"""
        source = """
        func compute(x: i32, y: f64) : f64 = {
            return x:f64 + y
        }
        
        func main() : i32 = {
            val a = 10
            val b = 20
            val result = compute(a + b, 3.14 * 2.0)
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_explicit_conversion_in_arguments(self):
        """Test explicit type conversions in function arguments"""
        source = """
        func precise_calc(value: f32) : f32 = {
            return value * 2.0:f32
        }
        
        func main() : i32 = {
            val double_val : f64 = 3.14159
            
            // Explicit precision loss conversion
            val result = precise_calc(double_val:f32)
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_complex_nested_expressions(self):
        """Test complex nested expressions as arguments"""
        source = """
        func complex_func(a: f64, b: i32, c: f64) : f64 = {
            return a + b:f64 + c
        }
        
        func main() : i32 = {
            val x = 10
            val y = 3.14
            
            // Complex nested expression arguments
            val result = complex_func(
                (x + 5):f64 * y,
                (x * 2) + 1,
                y * 2.0 + 1.5
            )
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_calls_in_expression_blocks(self):
        """Test function calls within expression blocks"""
        source = """
        func helper(x: i32) : i32 = {
            return x + 10
        }
        
        func main() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function call)
                val temp = helper(5)
                assign temp * 2
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_multiple_function_calls_same_statement(self):
        """Test multiple function calls in same statement"""
        source = """
        func add_two(a: i32, b: i32) : i32 = {
            return a + b
        }
        
        func multiply(x: i32, y: i32) : i32 = {
            return x * y
        }
        
        func main() : i32 = {
            // Multiple function calls in same expression
            val result = add_two(multiply(2, 3), multiply(4, 5))
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_void_function_calls(self):
        """Test calling void functions in assignment context"""
        source = """
        func do_work() : void = {
            return
        }
        
        func get_result() : i32 = {
            return 42
        }
        
        func main() : i32 = {
            // Void functions can be called but can't be assigned to variables
            val result = get_result()  // Valid: non-void function
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestFunctionCallErrors(StandardTestBase):
    """Test function call error cases"""

    def test_undefined_function_error(self):
        """Test calling undefined function"""
        source = """
        func main() : i32 = {
            val result = undefined_function()
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_contains(errors, "Undefined function: 'undefined_function'")

    def test_argument_count_mismatch_too_few(self):
        """Test function call with too few arguments"""
        source = """
        func add_numbers(a: i32, b: i32, c: i32) : i32 = {
            return a + b + c
        }
        
        func main() : i32 = {
            val result = add_numbers(10, 20)  // Missing third argument
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_contains(
            errors, "Function 'add_numbers' expects 3 arguments, but 2 provided"
        )

    def test_argument_count_mismatch_too_many(self):
        """Test function call with too many arguments"""
        source = """
        func simple_add(x: i32, y: i32) : i32 = {
            return x + y
        }
        
        func main() : i32 = {
            val result = simple_add(10, 20, 30)  // Extra argument
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_contains(
            errors, "Function 'simple_add' expects 2 arguments, but 3 provided"
        )

    def test_type_conversion_error_mixed_concrete_types(self):
        """Test type conversion error for mixed concrete types"""
        source = """
        func process_int(value: i32) : i32 = {
            return value + 1
        }
        
        func main() : i32 = {
            val large_value : i64 = 9223372036854775807
            
            // i64 -> i32 requires explicit conversion
            val result = process_int(large_value)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_contains(
            errors,
            "Function 'process_int' argument 1: Cannot assign i64 to parameter 'value' of type i32",
        )
        assert_error_contains(errors, "Use explicit conversion: 'expression:i32'")

    def test_precision_loss_conversion_error(self):
        """Test precision loss conversion error"""
        source = """
        func process_float(value: f32) : f32 = {
            return value * 2.0:f32
        }
        
        func main() : i32 = {
            val high_precision : f64 = 3.141592653589793
            
            // f64 -> f32 requires explicit conversion (precision loss)
            val result = process_float(high_precision)
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_contains(
            errors,
            "Function 'process_float' argument 1: Cannot assign f64 to parameter 'value' of type f32",
        )

    def test_multiple_argument_errors(self):
        """Test multiple argument type errors in single call"""
        source = """
        func multi_param(a: i32, b: f32, c: i64) : i32 = {
            return 0
        }
        
        func main() : i32 = {
            val wrong_a : i64 = 100  // Wrong type for param a
            val wrong_b : f64 = 2.5  // Wrong type for param b
            val correct_c : i64 = 300
            
            // Multiple type errors
            val result = multi_param(wrong_a, wrong_b, correct_c)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should have errors for arguments 1 and 2
        assert_error_contains(
            errors, "argument 1: Cannot assign i64 to parameter 'a' of type i32"
        )
        assert_error_contains(
            errors, "argument 2: Cannot assign f64 to parameter 'b' of type f32"
        )

    def test_function_call_in_invalid_context(self):
        """Test function call return type mismatches"""
        source = """
        func get_string() : string = {
            return "hello"
        }
        
        func main() : i32 = {
            val num_result : i32 = get_string()  // Type mismatch
            return num_result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # The error will be about type mismatch in variable assignment
        assert_error_contains(
            errors,
            "Type mismatch: variable 'num_result' declared as i32 but assigned value of type string",
        )


class TestAdvancedFunctionCallScenarios(StandardTestBase):
    """Test advanced function call scenarios and edge cases"""

    def test_recursive_function_calls(self):
        """Test recursive function calls (basic validation)"""
        source = """
        func factorial(n: i32) : i32 = {
            // Simplified recursive call for testing - just validate the call works
            val result = factorial(n - 1)  // Recursive call
            return result + 1
        }
        
        func main() : i32 = {
            val result = factorial(5)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_with_early_returns(self):
        """Test function calls with early return patterns"""
        source = """
        func validate_and_process(input: i32) : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (uses concrete parameter)
                // Simplified early return testing - just check the syntax works
                val negative_check = input < 0
                assign input * 2  // Normal processing
            }
            return result
        }
        
        func main() : i32 = {
            val result1 = validate_and_process(-5)   
            val result2 = validate_and_process(50)   
            val result3 = validate_and_process(2000) 
            return result1 + result2 + result3
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_composition_patterns(self):
        """Test function composition and chaining"""
        source = """
        func add_ten(x: i32) : i32 = {
            return x + 10
        }
        
        func multiply_by_two(x: i32) : i32 = {
            return x * 2
        }
        
        func square(x: i32) : i32 = {
            return x * x
        }
        
        func main() : i32 = {
            // Function composition: square(multiply_by_two(add_ten(5)))
            val step1 = add_ten(5)          // 15
            val step2 = multiply_by_two(step1)  // 30
            val step3 = square(step2)       // 900
            
            // Nested composition
            val composed = square(multiply_by_two(add_ten(5)))
            
            return composed
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_parameter_shadowing_edge_cases(self):
        """Test parameter names don't conflict with local variables"""
        source = """
        func process_data(data: i32, factor: i32) : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (uses concrete parameters)
                val data = data * 2  // Local variable shadows parameter
                val temp = data + factor
                assign temp
            }
            return result
        }
        
        func main() : i32 = {
            val result = process_data(10, 5)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_complex_type_inference_with_function_calls(self):
        """Test type inference works correctly with function call results"""
        source = """
        func get_int() : i32 = {
            return 42
        }
        
        func get_float() : f64 = {
            return 3.14
        }
        
        func main() : i32 = {
            // Type inference should work with function call results
            val inferred_int = get_int()     // Should infer i32
            val inferred_float = get_float() // Should infer f64
            
            // Use in expressions
            val combined = inferred_int:f64 + inferred_float
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestFunctionCallIntegrationWithExistingFeatures(StandardTestBase):
    """Test function calls work correctly with all existing language features"""

    def test_function_calls_with_all_literal_types(self):
        """Test function calls with all supported literal types"""
        source = """
        func process_literals(
            int_lit: i32,
            float_lit: f64,
            string_lit: string,
            bool_lit: bool
        ) : i32 = {
            return 1
        }
        
        func main() : i32 = {
            val result = process_literals(42, 3.14, "hello", true)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_calls_with_unary_operations(self):
        """Test function calls with unary operation arguments"""
        source = """
        func process_unary(neg_int: i32, neg_float: f64, not_bool: bool) : i32 = {
            return 0
        }
        
        func main() : i32 = {
            val result = process_unary(-42, -3.14, !true)
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_calls_with_all_binary_operations(self):
        """Test function calls with binary operation arguments"""
        source = """
        func math_operations(
            add_result: i32,
            mult_result: f64,
            div_result: f64,
            comparison: bool
        ) : i32 = {
            return 0
        }
        
        func main() : i32 = {
            val result = math_operations(
                10 + 20,        // Addition
                3.14 * 2.0,     // Multiplication  
                10.0 / 3.0,     // Float division
                5 > 3           // Comparison
            )
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_calls_with_assignment_contexts(self):
        """Test function calls in various assignment contexts"""
        source = """
        func get_value() : i32 = {
            return 100
        }
        
        func main() : i32 = {
            // Direct assignment
            val direct = get_value()
            
            // Assignment with explicit type
            val explicit : i32 = get_value()
            
            // Mutable variable assignment
            mut changeable : i32 = get_value()
            changeable = get_value()  // Reassignment
            
            return direct + explicit + changeable
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_calls_with_block_system_integration(self):
        """Test function calls integrate correctly with unified block system"""
        source = """
        func helper(x: i32) : i32 = {
            return x + 1
        }
        
        func main() : i32 = {
            // Function calls in expression blocks
            val expr_block_result : i32 = {  // Explicit type required for runtime block (contains function call)
                val temp = helper(10)
                assign temp * 2
            }
            
            // Function calls in statement blocks
            {
                val local = helper(5)
                // Statement block - no value production
            }
            
            // Function calls in function return
            return helper(expr_block_result)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
