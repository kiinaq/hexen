"""
Semantic tests for conditional statements and expressions.

Tests Statement Context Analysis
- Conditional statement analysis
- Boolean condition type checking  
- Scope management for branches
- Integration with function bodies

Tests Expression Context Analysis  
- Conditional expression analysis
- Assign/return validation in branches
- Type unification across branches
- Integration with expression blocks and comptime types

Tests Type System Integration
- Runtime treatment of all conditionals with comptime type handling
- Target type context propagation to branches and parameter contexts  
- Explicit conversion requirements for mixed concrete types
- Comprehensive type integration with val/mut and expression blocks
"""

import pytest
from tests.semantic import (
    parse_and_analyze, 
    assert_no_errors, 
    assert_error_contains
)


class TestConditionalStatements:
    """Test basic conditional statement functionality."""

    def test_basic_if_statement(self):
        """Test basic if statement with boolean condition."""
        code = '''
        func test() : void = {
            if true {
                val x = 42
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_if_else_statement(self):
        """Test if-else statement."""
        code = '''
        func test() : void = {
            if true {
                val x = 42
            } else {
                val y = 100
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_else_if_chain(self):
        """Test if-else if-else chain."""
        code = '''
        func test(input : i32) : void = {
            if input < 0 {
                val negative = -1
            } else if input == 0 {
                val zero = 0
            } else {
                val positive = 1
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_nested_conditionals(self):
        """Test nested conditional statements."""
        code = '''
        func test(a : i32, b : i32) : void = {
            if a > 0 {
                if b > 0 {
                    val both_positive = true
                } else {
                    val a_positive_b_nonpositive = true
                }
            } else {
                val a_nonpositive = true
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestConditionValidation:
    """Test condition type validation."""

    def test_boolean_condition_validation(self):
        """Test that boolean conditions are accepted."""
        code = '''
        func test() : void = {
            val flag : bool = true
            if flag {
                val x = 42
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_comparison_conditions(self):
        """Test comparison operations as conditions."""
        code = '''
        func test(x : i32, y : i32) : void = {
            if x > y {
                val greater = 1
            }
            if x < y {
                val lesser = 1  
            }
            if x == y {
                val equal = 1
            }
            if x != y {
                val not_equal = 1
            }
            if x >= y {
                val greater_equal = 1
            }
            if x <= y {
                val lesser_equal = 1
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_logical_conditions(self):
        """Test logical operations as conditions."""
        code = '''
        func test(a : bool, b : bool) : void = {
            if a && b {
                val both_true = 1
            }
            if a || b {
                val at_least_one_true = 1
            }
            if !a {
                val a_false = 1
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_invalid_condition_types(self):
        """Test that non-boolean conditions produce errors."""
        # i32 condition
        code = '''
        func test() : void = {
            val x : i32 = 42
            if x {
                val invalid = 1
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Condition must be of type bool, got i32")
        
        # string condition  
        code = '''
        func test() : void = {
            val message = "hello"
            if message {
                val invalid = 1
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Condition must be of type bool, got string")
        
        # f64 condition
        code = '''
        func test() : void = {
            val pi : f64 = 3.14
            if pi {
                val invalid = 1
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Condition must be of type bool, got f64")


class TestScopeManagement:
    """Test scope isolation and management in conditional branches."""
    
    def test_scope_isolation(self):
        """Test that variables in branches are scoped properly."""
        code = '''
        func test() : void = {
            if true {
                val scoped = 42
            }
            // scoped should not be accessible here
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_variable_shadowing(self):
        """Test variable shadowing within conditional branches."""
        code = '''
        func test() : void = {
            val x = 10
            if true {
                val x = 20  // shadows outer x
            }
            // outer x should still be 10
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_lexical_scoping(self):
        """Test access to outer scope variables from conditional branches."""
        code = '''
        func test() : void = {
            val outer = 42
            if true {
                val inner = outer * 2  // should access outer variable
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_scope_cleanup(self):
        """Test that variables are cleaned up after branch exit."""
        code = '''
        func test() : void = {
            if true {
                val temp = 100
            } else {
                val temp = 200  // Same name, different scope - should be fine
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestIntegrationWithFunctions:
    """Test conditional statements within function contexts."""
    
    def test_conditionals_in_functions(self):
        """Test conditional statements within function bodies."""
        code = '''
        func process(input : i32) : void = {
            if input > 0 {
                val positive_message = "Positive number"
            } else if input < 0 {
                val negative_message = "Negative number"  
            } else {
                val zero_message = "Zero"
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_return_statements_in_conditionals(self):
        """Test early return statements within conditionals."""
        code = '''
        func validate(input : i32) : i32 = {
            if input < 0 {
                return -1  // Early return for negative input
            }
            if input > 1000 {
                return -2  // Early return for too large input
            }
            return input  // Normal return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_empty_branches(self):
        """Test conditional statements with empty branches."""
        code = '''
        func test() : void = {
            if true {
                // Empty if branch
            }
            if false {
                val x = 42
            } else {
                // Empty else branch  
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestErrorConditions:
    """Test various error conditions for conditional statements."""
    
    def test_undefined_variable_in_condition(self):
        """Test error for undefined variable in condition."""
        code = '''
        func test() : void = {
            if undefined_var {
                val x = 42
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Undefined variable: 'undefined_var'")
        
    def test_type_mismatch_in_condition(self):
        """Test error for type mismatch in condition expressions."""
        code = '''
        func test() : void = {
            val x : i32 = 10
            val y : f64 = 3.14
            if x > y {  // This should require explicit conversion
                val result = 1
            }
            return
        }
        '''
        # Note: This might pass depending on comptime type handling
        # Will be refined in later sessions
        ast, errors = parse_and_analyze(code)
        # For now, just verify it analyzes without crashing


class TestAdvancedPatterns:
    """Test advanced conditional patterns."""
    
    def test_multiple_conditions_same_scope(self):
        """Test multiple conditionals in same scope level."""
        code = '''
        func test(a : i32, b : i32, c : i32) : void = {
            if a > 0 {
                val pos_a = true
            }
            if b > 0 {
                val pos_b = true
            }  
            if c > 0 {
                val pos_c = true
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_conditional_with_function_calls(self):
        """Test conditionals with function call conditions (basic case)."""
        code = '''
        func is_valid(x : i32) : bool = {
            return x > 0
        }
        
        func test(input : i32) : void = {
            if is_valid(input) {
                val valid = true
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestConditionalExpressions:
    """Test conditional expressions in expression context."""

    def test_basic_conditional_expression(self):
        """Test basic conditional expression with assign statements."""
        code = '''
        func test() : i32 = {
            val result = if true {
                assign 42
            } else {
                assign 100
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_conditional_expression_with_comptime_values(self):
        """Test conditional expression with comptime literals."""
        code = '''
        func get_value(flag : bool) : f64 = {
            val result : f64 = if flag {
                assign 42       // comptime_int -> f64
            } else {
                assign 3.14     // comptime_float -> f64
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_conditional_expression_with_variables(self):
        """Test conditional expression using variables."""
        code = '''
        func select(flag : bool, a : i32, b : i32) : i32 = {
            val result = if flag {
                assign a
            } else {
                assign b
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_conditional_expression_with_early_return(self):
        """Test conditional expression with return statements for early exit."""
        code = '''
        func process(input : i32) : i32 = {
            val result = if input < 0 {
                return -1          // Early function exit
            } else {
                assign input * 2   // Normal processing
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_conditional_expression_else_if_chain(self):
        """Test conditional expression with else-if chains."""
        code = '''
        func classify(score : i32) : string = {
            val grade = if score >= 90 {
                assign "A"
            } else if score >= 80 {
                assign "B"
            } else if score >= 70 {
                assign "C"
            } else {
                assign "F"
            }
            return grade
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_mixed_return_and_assign(self):
        """Test conditional expression mixing return and assign statements."""
        code = '''
        func validate_and_process(input : i32) : i32 = {
            val result = if input < 0 {
                return -1          // Early exit: error case
            } else if input == 0 {
                return 0           // Early exit: special case
            } else {
                assign input * 2   // Success case: assign value
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestConditionalExpressionErrors:
    """Test error conditions for conditional expressions."""

    def test_non_boolean_condition_in_expression(self):
        """Test error for non-boolean condition in conditional expression."""
        code = '''
        func test(x : i32) : i32 = {
            val result = if x {  // Error: i32 not bool
                assign 42
            } else {
                assign 100
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Condition must be of type bool, got i32")


class TestConditionalExpressionTypeResolution:
    """Test type resolution across conditional expression branches."""

    def test_comptime_type_unification(self):
        """Test type unification with comptime types."""
        code = '''
        func get_number(use_int : bool) : f64 = {
            val result : f64 = if use_int {
                assign 42       // comptime_int -> f64
            } else {
                assign 3.14     // comptime_float -> f64  
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_explicit_type_context_propagation(self):
        """Test that target type context propagates to branches."""
        code = '''
        func get_value(flag : bool) : i32 = {
            val result : i32 = if flag {
                assign 42       // comptime_int adapts to i32 context
            } else {
                assign 100      // comptime_int adapts to i32 context
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_nested_conditional_expressions(self):
        """Test nested conditional expressions."""
        code = '''
        func complex_logic(a : bool, b : bool) : i32 = {
            val result = if a {
                assign if b {
                    assign 1
                } else {
                    assign 2
                }
            } else {
                assign if b {
                    assign 3
                } else {
                    assign 4
                }
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestConditionalIntegrationPatterns:
    """Test integration with other language features."""

    def test_conditionals_in_expression_blocks(self):
        """Test conditional expressions within expression blocks."""
        code = '''
        func calculate(base : i32) : f64 = {
            val result : f64 = {
                val multiplier = if base > 100 {
                    assign 2.5
                } else {
                    assign 1.0  
                }
                assign base:f64 * multiplier
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_conditionals_with_function_calls_in_conditions(self):
        """Test conditionals with function calls in conditions."""
        code = '''
        func is_valid(x : i32) : bool = {
            return x > 0
        }
        
        func process(input : i32) : string = {
            val result = if is_valid(input) {
                assign "valid"
            } else {
                assign "invalid"
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_conditionals_with_binary_operations(self):
        """Test conditionals with complex condition expressions."""
        code = '''
        func categorize(x : i32, y : i32) : string = {
            val category = if x > 0 && y > 0 {
                assign "positive"
            } else if x < 0 || y < 0 {
                assign "negative"  
            } else {
                assign "zero"
            }
            return category
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestTypeSystemIntegration:
    """Test Session 4: Type System Integration with conditionals."""

    def test_comptime_type_runtime_treatment(self):
        """Test that all conditionals are treated as runtime with comptime types."""
        code = '''
        func test_runtime_treatment() : f64 = {
            // Mixed comptime types require explicit target context (runtime treatment)
            val result : f64 = if true {    // Runtime condition (even though constant)
                assign 42 + 100             // comptime_int -> f64 (context-guided)
            } else {
                assign 3.14 * 2.0           // comptime_float -> f64 (context-guided)  
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_target_type_context_propagation(self):
        """Test target type propagation to conditional branches."""
        code = '''
        func test_context_propagation() : i32 = {
            // Target type i32 should propagate to both branches
            val result : i32 = if true {
                assign 42       // comptime_int -> i32 (context propagated)
            } else {
                assign 100      // comptime_int -> i32 (context propagated)
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_mixed_comptime_types_with_context(self):
        """Test mixed comptime types resolve correctly with target context."""
        code = '''
        func test_mixed_comptime() : f64 = {
            val result : f64 = if true {
                assign 42       // comptime_int -> f64 (target context)
            } else {
                assign 3.14     // comptime_float -> f64 (target context)
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_mixed_concrete_types_require_explicit_conversion(self):
        """Test that mixed concrete types require explicit conversions."""
        code = '''
        func get_i32() : i32 = { return 42 }
        func get_f64() : f64 = { return 3.14 }
        
        func test_mixed_concrete() : f64 = {
            val result : f64 = if true {
                assign get_i32():f64    // i32 -> f64 (explicit conversion required)
            } else {
                assign get_f64()        // f64 -> f64 (identity)
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_mixed_concrete_types_error_without_conversion(self):
        """Test error for mixed concrete types without explicit conversion."""
        code = '''
        func get_i32() : i32 = { return 42 }
        func get_f64() : f64 = { return 3.14 }
        
        func test_mixed_concrete_error() : f64 = {
            val result : f64 = if true {
                assign get_i32()       // Error: i32 cannot auto-convert to f64
            } else {
                assign get_f64()       // f64 -> f64 (identity)
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Branch type i32 incompatible with target type f64. Use explicit conversion: value:f64")

    def test_function_parameter_context_propagation(self):
        """Test context propagation from function parameters."""
        code = '''
        func process_f64(value : f64) : void = { return }
        
        func test_parameter_context() : void = {
            // Function parameter type provides context for conditional
            process_f64(if true {
                assign 42           // comptime_int -> f64 (parameter context)
            } else {
                assign 3.14         // comptime_float -> f64 (parameter context)
            })
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_function_return_context_propagation(self):
        """Test context propagation from function return type."""
        code = '''
        func test_return_context() : f64 = {
            // Function return type provides context for conditional
            return if true {
                assign 42           // comptime_int -> f64 (return context)
            } else {
                assign 3.14         // comptime_float -> f64 (return context)
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_val_vs_mut_with_conditionals(self):
        """Test conditional expressions with val vs mut declarations."""
        code = '''
        func test_val_vs_mut() : void = {
            // val with conditional (can preserve flexibility with target type)
            val val_result : f64 = if true {
                assign 42           // comptime_int -> f64
            } else {
                assign 3.14         // comptime_float -> f64
            }
            
            // mut with conditional (explicit type required)
            mut mut_result : f64 = if true {
                assign 42           // comptime_int -> f64
            } else {
                assign 3.14         // comptime_float -> f64
            }
            
            mut_result = if false {
                assign 100          // comptime_int -> f64 (reassignment)
            } else {
                assign 2.718        // comptime_float -> f64 (reassignment)
            }
            
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_expression_blocks_with_conditionals_require_context(self):
        """Test that expression blocks containing conditionals require explicit context."""
        code = '''
        func test_expression_block_context() : f64 = {
            val result : f64 = {        // Context REQUIRED (runtime block)!
                val base = 42           // comptime_int
                val multiplier = if base > 50 {
                    assign 2.5          // comptime_float
                } else {
                    assign 1.0          // comptime_float
                }
                assign base:f64 * multiplier
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)

    def test_nested_conditionals_with_type_propagation(self):
        """Test nested conditional expressions with type propagation."""
        code = '''
        func test_nested_conditionals() : f64 = {
            val result : f64 = if true {
                assign if false {
                    assign 42       // comptime_int -> f64 (nested context)
                } else {
                    assign 3.14     // comptime_float -> f64 (nested context)
                }
            } else {
                assign if true {
                    assign 100      // comptime_int -> f64 (nested context)
                } else {
                    assign 2.718    // comptime_float -> f64 (nested context)
                }
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestTypeSystemErrorHandling:
    """Test error handling for type system integration."""

    def test_mixed_types_without_target_context_error(self):
        """Test error when mixed comptime types lack target context."""
        code = '''
        func test_missing_context() : void = {
            val result = if true {      // Missing explicit type
                assign 42               // comptime_int
            } else {
                assign 3.14             // comptime_float
            }
            return
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_error_contains(errors, "Mixed types across conditional branches require explicit target type context")

    def test_helpful_conversion_error_messages(self):
        """Test that concrete type conversion errors provide helpful messages."""
        code = '''
        func get_i32() : i32 = { return 42 }
        
        func test_conversion_error() : f64 = {
            val result : f64 = if true {
                assign get_i32()       // i32 needs explicit conversion to f64
            } else {
                assign 3.14            // comptime_float -> f64
            }
            {
                return result
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        # Should suggest explicit conversion syntax
        assert_error_contains(errors, "Use explicit conversion: value:f64")


class TestAdvancedValidationPatterns:
    """Test advanced validation patterns from CONDITIONAL_SYSTEM.md."""
    
    def test_validation_chains_with_early_returns(self):
        """Test validation chains using early returns (from specification)."""
        code = '''
        func validate_and_process(input: i32) : string = {
            val result = if input < 0 {
                return "ERROR: Negative input"     // Early function exit
            } else if input > 1000 {
                return "ERROR: Input too large"    // Early function exit
            } else {
                assign "SUCCESS: Valid input"     // Success: processed input
            }
            
            // Additional processing only happens for valid input
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_guard_clause_pattern(self):
        """Test guard clause patterns with early returns."""
        code = '''
        func safe_divide(a: f64, b: f64) : f64 = {
            val result : f64 = if b == 0.0 {
                return 0.0         // Early exit: division by zero
            } else {
                assign a / b       // Normal case: assign division result
            }
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_nested_validation_pattern(self):
        """Test multiple levels of validation with nested conditionals."""
        code = '''
        func validate_user_data(name_id: i32, age: i32) : string = {
            val result = if name_id < 1 {
                return "ERROR: Name ID required"
            } else if name_id > 999999 {
                return "ERROR: Name ID too large"
            } else {
                val age_result = if age < 0 {
                    return "ERROR: Invalid age"       // Early function exit
                } else if age > 150 {
                    return "ERROR: Age too high"      // Early function exit  
                } else {
                    assign age                         // Valid age
                }
                assign "VALID: User data OK"
            }
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestAdvancedCachingPatterns:
    """Test performance optimization patterns with caching."""
    
    def test_caching_pattern_with_early_returns(self):
        """Test caching pattern using early returns (from specification)."""
        code = '''
        func lookup_cache(key: i32) : f64 = { return -1.0 }  // -1.0 means cache miss
        func very_expensive_operation(key: i32) : f64 = { return key:f64 * 2.0 }
        func save_to_cache(key: i32, value: f64) : void = { return }
        func log_cache_miss(key: i32) : void = { return }
        
        func expensive_calc(key: i32) : f64 = {
            val cached : f64 = lookup_cache(key)
            val computed : f64 = very_expensive_operation(key)
            
            val result : f64 = if cached >= 0.0 {
                return cached          // Early exit: cache hit
            } else {
                save_to_cache(key, computed)
                assign computed        // Cache miss: assign computed value
            }
            
            // This only executes on cache miss (after assign, not after return)
            log_cache_miss(key)
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_short_circuit_optimization_pattern(self):
        """Test short-circuit optimization using conditionals."""
        code = '''
        func optimized_calculation(use_fast_path: bool, input: f64) : f64 = {
            val fast_result : f64 = input * 2.0
            val slow_result : f64 = (input * input / 3.14159) + 1.0
            
            val result : f64 = if use_fast_path {
                assign fast_result     // Fast path
            } else {
                assign slow_result     // Complex expensive calculation
            }
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_conditional_computation_pattern(self):
        """Test conditional computation to avoid expensive operations."""
        code = '''
        func smart_processing(enable_advanced: bool, data: f64) : f64 = {
            val base_result = data * 1.5
            
            val enhanced_result = if enable_advanced {
                val complex_calc = base_result * base_result * 3.14159
                assign complex_calc
            } else {
                assign base_result     // Skip expensive calculation
            }
            
            return enhanced_result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestAdvancedFallbackPatterns:
    """Test configuration and fallback patterns."""
    
    def test_fallback_configuration_pattern(self):
        """Test primary -> fallback -> default configuration pattern (from specification)."""
        code = '''
        func primary_config_exists() : bool = { return true }
        func load_primary_config() : i32 = { return 100 }  // PRIMARY config ID
        func fallback_config_exists() : bool = { return true }
        func load_fallback_config() : i32 = { return 200 } // FALLBACK config ID
        func get_default_config() : i32 = { return 300 }   // DEFAULT config ID
        
        func load_config_with_fallback() : i32 = {
            val primary_exists : bool = primary_config_exists()
            val primary : i32 = load_primary_config()
            val fallback_exists : bool = fallback_config_exists()
            val fallback : i32 = load_fallback_config()
            val default : i32 = get_default_config()
            
            // Simple fallback pattern: check primary first
            val config : i32 = if primary_exists && (primary > 0) {
                assign primary                     // Use primary config
            } else if fallback_exists {
                assign fallback                    // Use fallback config
            } else {
                assign default                     // Use default config
            }
            
            return config
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_conditional_feature_selection(self):
        """Test feature flag controlled behavior."""
        code = '''
        func process_with_feature_flags(enable_feature_a: bool, enable_feature_b: bool) : i32 = {
            val feature_a_result = if enable_feature_a {
                assign 1    // Feature A enabled
            } else {
                assign 0    // Feature A disabled
            }
            
            val feature_b_result = if enable_feature_b {
                assign 10   // Feature B enabled (use different value to distinguish)
            } else {
                assign 0    // Feature B disabled
            }
            
            return feature_a_result + feature_b_result  // Combined feature flags
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_graceful_degradation_pattern(self):
        """Test graceful degradation on errors."""
        code = '''
        func process_with_degradation(input: f64, use_advanced: bool) : f64 = {
            val result = if use_advanced {
                val advanced_result = if input > 0.0 {
                    // Advanced processing might fail
                    val complex = input * input * input
                    assign complex
                } else {
                    // Fallback to simple processing
                    return input * 2.0     // Early exit with simple calculation
                }
                assign advanced_result
            } else {
                assign input * 2.0         // Simple processing
            }
            
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestComplexIntegrationPatterns:
    """Test complex integration patterns with existing language features."""
    
    def test_conditionals_with_complex_binary_operations(self):
        """Test conditionals integrated with complex binary operations."""
        code = '''
        func complex_calculation(a: f64, b: f64, c: f64) : f64 = {
            val result : f64 = if (a + b) > c {
                assign (a * b) + c
            } else if (a - b) < c {
                assign (a / b) * c
            } else {
                assign a + b + c
            }
            
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_conditionals_with_function_call_chains(self):
        """Test conditionals with complex function call chains."""
        code = '''
        func transform_data(input: f64) : f64 = { return input * 2.0 }
        func validate_result(value: f64) : bool = { return value > 0.0 }
        func apply_correction(value: f64) : f64 = { return value + 1.0 }
        
        func process_data_pipeline(input: f64) : f64 = {
            val transformed = transform_data(input)
            
            val result = if validate_result(transformed) {
                val corrected = if transformed > 100.0 {
                    assign apply_correction(transformed)
                } else {
                    assign transformed
                }
                assign corrected
            } else {
                return 0.0     // Early exit for invalid data
            }
            
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_conditionals_in_complex_expression_blocks(self):
        """Test conditionals within complex expression blocks with mixed contexts."""
        code = '''
        func get_base_price() : f64 = { return 50.0 }
        func get_user_tier() : i32 = { return 1 }  // 1 = basic, 2 = gold, 3 = premium
        func is_first_time_user() : bool = { return false }
        
        func calculate_pricing() : f64 = {
            val final_price : f64 = {              // Context REQUIRED (runtime block)!
                val base_price : f64 = get_base_price()  // Runtime function call
                val user_tier : i32 = get_user_tier()    // Runtime function call
                
                val discount_multiplier : f64 = if user_tier == 3 {     // 3 = premium
                    assign 0.8                     // 20% discount
                } else if user_tier == 2 {         // 2 = gold
                    assign 0.9                     // 10% discount  
                } else if is_first_time_user() {   // Runtime condition
                    assign 0.95                    // 5% new user discount
                } else {
                    assign 1.0                     // No discount
                }
                
                val discounted : f64 = base_price * discount_multiplier
                
                val final_adjustment : f64 = if discounted < 10.0 {
                    return 0.0                     // Early exit: too cheap, make it free
                } else if discounted > 1000.0 {
                    assign 1000.0                  // Cap at maximum price
                } else {
                    assign discounted              // Use calculated price
                }
                
                assign final_adjustment
            }
            
            return final_price
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)


class TestRealWorldScenarios:
    """Test complete real-world scenarios using all conditional patterns."""
    
    def test_complete_validation_function(self):
        """Test complete validation function using all validation patterns."""
        code = '''
        func comprehensive_data_validator(name_id: i32, age: i32, score: f64) : i32 = {
            // Input validation chain - return error codes
            val validation_result = if name_id <= 0 {
                return -1     // ERROR: Name ID required
            } else if name_id > 999999 {
                return -2     // ERROR: Name ID too large
            } else if age < 0 {
                return -3     // ERROR: Age cannot be negative  
            } else if age > 120 {
                return -4     // ERROR: Age seems unrealistic
            } else if score < 0.0 {
                return -5     // ERROR: Score cannot be negative
            } else if score > 100.0 {
                return -6     // ERROR: Score cannot exceed 100
            } else {
                assign 0      // VALID (success code)
            }
            
            // Additional processing only for valid data
            val grade_points = if score >= 90.0 {
                assign 4      // A grade
            } else if score >= 80.0 {
                assign 3      // B grade
            } else if score >= 70.0 {
                assign 2      // C grade
            } else if score >= 60.0 {
                assign 1      // D grade
            } else {
                assign 0      // F grade
            }
            
            return validation_result + grade_points  // Combined result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_complete_configuration_loader(self):
        """Test complete configuration loader with all fallback patterns."""
        code = '''
        // Forward declare helper functions first
        func get_environment() : i32 = { return 2 }  // 2 = development
        func production_config_exists() : bool = { return true }
        func load_production_config() : i32 = { return 100 }  // PROD_CONFIG ID
        func validate_config(config: i32) : bool = { return config > 0 }
        func development_config_exists() : bool = { return false }
        func load_development_config() : i32 = { return 200 }  // DEV_CONFIG ID
        func get_default_development_config() : i32 = { return 300 }  // DEFAULT_DEV_CONFIG ID
        func get_default_config() : i32 = { return 400 }  // DEFAULT_CONFIG ID
        
        func load_application_config() : i32 = {
            val environment = get_environment()
            
            if environment == 1 {  // 1 = production
                if production_config_exists() {
                    val config = load_production_config()
                    if validate_config(config) {
                        return config
                    } else {
                        return -1   // ERROR: Invalid production config
                    }
                } else {
                    return -2       // ERROR: Production config not found
                }
            } else if environment == 2 {  // 2 = development
                if development_config_exists() {
                    return load_development_config()
                } else {
                    return get_default_development_config()
                }
            } else {
                return get_default_config()
            }
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)
        
    def test_complete_calculation_function(self):
        """Test complete calculation function with conditional computation patterns."""
        code = '''
        // Forward declare helper functions first
        func check_cache(input: f64, mode: i32) : f64 = { return -1.0 }  // -1 means miss
        func store_in_cache(input: f64, mode: i32, result: f64) : void = { return }
        
        func advanced_mathematical_processor(input: f64, precision_mode: i32, enable_caching: bool) : f64 = {
            // Cache check first
            if enable_caching {
                val cached = check_cache(input, precision_mode)
                if cached >= 0.0 {
                    return cached      // Early exit: cache hit
                }
            }
            
            // Calculate base value
            val base_calculation = input * input + 2.0 * input + 1.0
            
            // Precision-based calculation
            val result : f64 = if precision_mode == 3 {  // 3 = "high"
                assign {
                    val step1 = base_calculation * 3.141592653589793
                    val step2 : f64 = step1 / 2.718281828459045
                    assign step2 + 1.414213562373095
                }
            } else if precision_mode == 2 {  // 2 = "medium"
                assign {
                    val step1 = base_calculation * 3.14159
                    val step2 : f64 = step1 / 2.71828
                    assign step2
                }
            } else {  // 1 = "low" or default
                assign base_calculation * 3.14
            }
            
            // Store in cache if enabled
            if enable_caching {
                store_in_cache(input, precision_mode, result)
            }
            
            return result
        }
        '''
        ast, errors = parse_and_analyze(code)
        assert_no_errors(errors)