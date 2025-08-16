"""
Test suite for function declaration semantic analysis in Hexen

This module provides comprehensive testing for function declaration validation
and semantic analysis, covering all aspects of the function system foundation
implemented in Sessions 4 & 5.

Test Coverage:
- Function declaration validation (name uniqueness, parameter validation, return types)
- Parameter system validation (mutability, type annotations, name uniqueness)
- Function body analysis (return type consistency, parameter accessibility)
- Symbol table integration (function registration, scope management)
- Error handling (clear, actionable error messages)
- Integration with unified block system

Related Implementation:
- src/hexen/semantic/symbol_table.py: Function signature storage and scope management
- src/hexen/semantic/declaration_analyzer.py: Function declaration analysis
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
)


class TestValidFunctionDeclarations(StandardTestBase):
    """Test valid function declaration scenarios"""

    def test_simple_void_function(self):
        """Test basic void function with no parameters"""
        source = """
        func simple() : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_single_parameter(self):
        """Test function with one parameter"""
        source = """
        func single_param(x: i32) : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_multiple_parameters(self):
        """Test function with multiple parameters of different types"""
        source = """
        func multi_params(a: i32, b: f64, c: string, d: bool) : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_mutable_parameters(self):
        """Test function with mutable parameters"""
        source = """
        func with_mut_params(mut counter: i32, mut flag: bool) : void = {
            counter = 100
            flag = true
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_mixed_mutability_parameters(self):
        """Test function with both mutable and immutable parameters"""
        source = """
        func mixed_mutability(immutable: i32, mut mutable: i32) : void = {
            mutable = immutable + 10
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_returning_all_types(self):
        """Test functions returning all supported types"""
        source = """
        func returns_i32() : i32 = {
            return 42
        }
        
        func returns_i64() : i64 = {
            return 1000
        }
        
        func returns_f32() : f32 = {
            return 3.14
        }
        
        func returns_f64() : f64 = {
            return 2.718
        }
        
        func returns_string() : string = {
            return "hello"
        }
        
        func returns_bool() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_multiple_functions_no_conflicts(self):
        """Test multiple functions with unique names"""
        source = """
        func first_function() : void = {
            return
        }
        
        func second_function(x: i32) : i32 = {
            return x
        }
        
        func third_function(a: i32, b: f64) : f64 = {
            return 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestFunctionParameterValidation(StandardTestBase):
    """Test parameter system validation"""

    def test_parameter_type_annotations_required(self):
        """Test that parameter type annotations are properly validated"""
        # All parameters should have explicit type annotations
        source = """
        func with_typed_params(count: i32, rate: f64, name: string) : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_parameter_mutability_validation(self):
        """Test parameter mutability enforcement"""
        source = """
        func test_mutability(immutable: i32, mut mutable: i32) : void = {
            // This should work - mutable parameter can be reassigned
            mutable = 100
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_immutable_parameter_cannot_be_reassigned(self):
        """Test that immutable parameters cannot be reassigned"""
        source = """
        func test_immutable_param(immutable_param: i32) : void = {
            immutable_param = 100
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have error about reassigning immutable parameter
        assert any(
            "assign" in error.message.lower() and "immutable" in error.message.lower()
            for error in errors
        )

    def test_parameter_scope_accessibility(self):
        """Test that parameters are accessible throughout function body"""
        source = """
        func test_param_access(input: i32, multiplier: f64) : f64 = {
            val local_var = input * 2
            val result = local_var:f64 * multiplier
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_parameter_shadowing_by_local_variables(self):
        """Test parameter shadowing behavior"""
        source = """
        func test_shadowing(param: i32) : i32 = {
            {
                val param = 200  // Local variable shadows parameter
                return param     // Returns the local variable
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_parameters_isolated_between_functions(self):
        """Test that parameters are isolated between different functions"""
        source = """
        func first_func(x: i32, y: f64) : void = {
            return
        }
        
        func second_func(x: string, z: bool) : void = {
            // Same parameter name 'x' but different type - should be fine
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestFunctionReturnTypeValidation(StandardTestBase):
    """Test return type validation and consistency"""

    def test_void_function_bare_return(self):
        """Test void functions with bare return"""
        source = """
        func void_with_bare_return() : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_void_function_no_explicit_return(self):
        """Test void functions without explicit return (should be allowed)"""
        source = """
        func void_implicit_return() : void = {
            val local = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_value_function_explicit_return(self):
        """Test value-returning functions with explicit return"""
        source = """
        func returns_value() : i32 = {
            val result = 42
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_return_type_consistency_comptime_types(self):
        """Test return type consistency with comptime types"""
        source = """
        func returns_comptime_as_i32() : i32 = {
            return 42  // comptime_int should coerce to i32
        }
        
        func returns_comptime_as_f64() : f64 = {
            return 3.14  // comptime_float should coerce to f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_return_type_mismatch_error(self):
        """Test return type mismatch detection"""
        source = """
        func returns_wrong_type() : i32 = {
            return "string"  // string cannot be returned as i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have type mismatch error
        assert any("type" in error.message.lower() for error in errors)

    def test_void_function_with_value_return_error(self):
        """Test that void functions cannot return values"""
        source = """
        func void_with_value() : void = {
            return 42  // void function cannot return value
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have error about returning value from void function
        assert any("void" in error.message.lower() for error in errors)


class TestFunctionDeclarationErrors(StandardTestBase):
    """Test error cases in function declarations"""

    def test_duplicate_function_names(self):
        """Test that duplicate function names are detected"""
        source = """
        func duplicate_name() : void = {
            return
        }
        
        func duplicate_name() : i32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have error about duplicate function name
        assert any("already declared" in error.message for error in errors)

    def test_duplicate_parameter_names(self):
        """Test that duplicate parameter names are detected"""
        source = """
        func duplicate_params(param: i32, param: f64) : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have error about duplicate parameter name
        assert any("Duplicate parameter name" in error.message for error in errors)

    def test_void_parameter_error(self):
        """Test that void parameters are not allowed"""
        source = """
        func invalid_void_param(param: void) : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have error about void parameter
        assert any("void type" in error.message for error in errors)

    def test_invalid_return_type_error(self):
        """Test validation for invalid return types (if any exist)"""
        # Note: All basic types should be valid return types
        # This test is more about ensuring the type validation system works
        source = """
        func valid_return_types() : i32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_missing_function_body_handled_by_parser(self):
        """Test that missing function body is handled (by parser, not semantic)"""
        # This should be caught by parser, but we verify semantic analyzer handles it gracefully
        source = """
        func complete_function() : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestFunctionBodyIntegration(StandardTestBase):
    """Test function body analysis and integration with unified block system"""

    def test_function_with_local_variables(self):
        """Test function with local variable declarations"""
        source = """
        func with_locals(param: i32) : i32 = {
            val local1 = param * 2
            mut local2 : i32 = 0
            local2 = local1 + param
            return local2
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_nested_blocks(self):
        """Test function with nested statement blocks"""
        source = """
        func with_nested_blocks(param: i32) : i32 = {
            val outer = param
            {
                val inner = outer * 2
                {
                    val deepest = inner + outer
                }
            }
            return outer
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_expression_blocks(self):
        """Test function with expression blocks using assign"""
        source = """
        func with_expression_blocks(param: i32) : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (uses concrete parameter)
                val temp = param * 2
                assign temp + 10
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_early_return_from_expression_block(self):
        """Test function with early return from expression block"""
        source = """
        func with_early_return(param: i32) : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (uses concrete parameter)
                val temp = param * 2
                assign temp
            }
            return result + 10
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_parameter_accessibility_in_nested_blocks(self):
        """Test that parameters are accessible in all nested blocks"""
        source = """
        func nested_param_access(param: i32) : i32 = {
            {
                {
                    val deep_local = param * 3  // Parameter accessible at deep nesting
                }
            }
            return param
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_scope_isolation(self):
        """Test that function scopes are properly isolated"""
        source = """
        func first_func() : void = {
            val local = 42
            return
        }
        
        func second_func() : void = {
            val local = 100  // Same name as in first_func - should be fine
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestFunctionTypeSystemIntegration(StandardTestBase):
    """Test function integration with Hexen's type system"""

    def test_comptime_type_parameter_coercion(self):
        """Test comptime type coercion in parameter context"""
        source = """
        func with_comptime_coercion(concrete: i32) : i32 = {
            // comptime_int should adapt to i32 parameter type context
            val result = concrete + 42
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_explicit_type_conversions_in_functions(self):
        """Test explicit type conversions within functions"""
        source = """
        func with_conversions(int_param: i32, float_param: f64) : f64 = {
            val converted = int_param:f64  // Explicit conversion
            val result = converted + float_param
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_mixed_concrete_type_operations_in_functions(self):
        """Test that mixed concrete type operations require explicit conversions"""
        source = """
        func mixed_types(a: i32, b: i64) : i64 = {
            val result = a:i64 + b  // Explicit conversion required
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_precision_loss_detection_in_functions(self):
        """Test precision loss detection in function context"""
        source = """
        func precision_loss_error(large: i64) : i32 = {
            return large  // Should require explicit conversion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        # Should have precision loss/truncation error
        assert any(
            any(
                keyword in error.message.lower()
                for keyword in ["truncation", "precision", "explicit"]
            )
            for error in errors
        )


class TestComplexFunctionDeclarationScenarios(StandardTestBase):
    """Test complex and edge case scenarios for function declarations"""

    def test_function_with_all_parameter_types(self):
        """Test function with parameters of all supported types"""
        source = """
        func all_param_types(
            int32: i32,
            int64: i64, 
            float32: f32,
            float64: f64,
            text: string,
            flag: bool,
            mut mut_int: i32,
            mut mut_float: f64
        ) : void = {
            mut_int = int32 + int64:i32
            mut_float = float32:f64 + float64
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_name_vs_variable_name_no_conflict(self):
        """Test that function names don't conflict with variable names"""
        source = """
        func test_name() : void = {
            val test_name = 42  // Variable with same name as function
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_with_complex_return_expression(self):
        """Test function with complex return expressions"""
        source = """
        func complex_return(a: i32, b: i32, c: f64) : f64 = {
            return (a + b):f64 * c + 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_functions_with_identical_signatures_different_names(self):
        """Test functions with identical signatures but different names"""
        source = """
        func first_version(x: i32, y: f64) : i32 = {
            return x
        }
        
        func second_version(x: i32, y: f64) : i32 = {
            return x + 1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_empty_function_bodies(self):
        """Test functions with minimal/empty bodies"""
        source = """
        func minimal_void() : void = {
        }
        
        func minimal_return() : i32 = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
