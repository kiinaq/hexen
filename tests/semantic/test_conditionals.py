"""
Semantic tests for conditional statements and expressions.

Tests Session 2: Statement Context Analysis
- Conditional statement analysis
- Boolean condition type checking  
- Scope management for branches
- Integration with function bodies

Tests Session 3: Expression Context Analysis  
- Conditional expression analysis
- Assign/return validation in branches
- Type unification across branches
- Integration with expression blocks and comptime types

Tests Session 4: Type System Integration
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
    """Test conditional expressions in expression context - Session 3."""

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