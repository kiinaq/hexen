"""
Test suite for Hexen's Unified Block System

Tests the comprehensive block system described in UNIFIED_BLOCK_SYSTEM.md:
- Single { } syntax for all contexts with context-driven behavior
- Expression blocks: produce values, require final return statement
- Statement blocks: execute code, allow function returns, no value production
- Function bodies: unified with all other blocks, context provides return type validation
- Universal scope isolation: ALL blocks manage their own scope regardless of context

This file provides COMPREHENSIVE block testing:
- Statement block semantics and scoping
- Expression block semantics and return requirements
- Function body blocks with return type validation
- Universal scope management across all block types
- Context-driven behavior determination
- Complex nested block scenarios
- Integration with variable declarations, assignments, and type system

BLOCK-SPECIFIC features are tested here - not general language features.
MUTABILITY semantics are covered in test_mutability.py.
ASSIGNMENT mechanics are covered in test_assignment.py.
"""

from tests.semantic import StandardTestBase


class TestStatementBlocks(StandardTestBase):
    """Test statement block semantics following unified block system"""

    def test_basic_statement_block_execution(self):
        """Test basic statement blocks execute code without producing values"""
        source = """
        func test() : void = {
            val outer = 42
            
            // ✅ Statement block for scoped execution
            {
                val temp_config = "setup"
                val processed_data = 100
                val flag = true
                // No return statement needed
            }
            
            val after = "completed"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_statement_block_scope_isolation(self):
        """Test statement blocks create isolated scopes (variables don't leak)"""
        source = """
        func test() : void = {
            val outer = 42
            
            {
                val inner_var = "scoped"
                val temp_data = 100
            }
            
            // ❌ Cannot access inner_var (out of scope)
            val invalid:string = inner_var
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any("Undefined variable: 'inner_var'" in msg for msg in error_messages)

    def test_statement_block_access_outer_scope(self):
        """Test statement blocks can access variables from outer scopes"""
        source = """
        func test() : void = {
            val config = "production"
            val counter:i32 = 100
            
            {
                // ✅ Can access outer scope variables
                val local_config = config    // Accesses outer 'config'
                val doubled:i32 = counter * 2    // Accesses outer 'counter'
                val processed = "done"
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_statement_block_variable_shadowing(self):
        """Test statement blocks can shadow outer scope variables"""
        source = """
        func test() : void = {
            val config = "global"
            val counter = 42
            
            {
                val config = "local"       // Shadows outer 'config'
                val counter = 100          // Shadows outer 'counter'
                val check = config         // "local" (shadowed)
            }
            
            // Original variables unchanged
            val final_config = config     // "global" (original)
            val final_counter = counter   // 42 (original)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_nested_statement_blocks(self):
        """Test nested statement blocks with proper scope management"""
        source = """
        func test() : void = {
            val level1 = "outer"
            
            {
                val level2 = "middle"
                
                {
                    val level3 = "inner"
                    
                    // ✅ Can access all outer levels
                    val access1 = level1    // "outer"
                    val access2 = level2    // "middle"
                    val access3 = level3    // "inner"
                }
                
                // ✅ Can access level1, level2 but not level3
                val access_outer = level1
                val access_current = level2
            }
            
            // ✅ Can only access level1
            val final = level1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_statement_block_function_returns(self):
        """Test statement blocks allow function returns (exits containing function)"""
        source = """
        func early_exit() : i32 = {
            val setup:i32 = 100
            
            {
                val condition = true
                // ✅ Function return from statement block (simplified)
                return 42        
            }
            
            return 0    // Fallback return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_multiple_statement_blocks_same_function(self):
        """Test multiple statement blocks in the same function scope"""
        source = """
        func process() : void = {
            val phase = "start"
            
            // First statement block
            {
                val step1_data = "preprocessing"
                val step1_result = 100
            }
            
            val checkpoint = "middle"
            
            // Second statement block
            {
                val step2_data = "processing"
                val step2_result = 200
            }
            
            val final = "complete"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_empty_statement_block(self):
        """Test empty statement blocks are valid"""
        source = """
        func test() : void = {
            val before = "setup"
            
            {
                // Empty statement block - valid
            }
            
            val after = "cleanup"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestExpressionBlocks(StandardTestBase):
    """Test expression block semantics following unified block system"""

    def test_basic_expression_block_value_production(self):
        """Test expression blocks produce values via return statements"""
        source = """
        func test() : i32 = {
            // ✅ Expression block produces value
            val result = {
                val computed = 42 * 2
                return computed
            }
            
            val another = {
                return "hello world"
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_requires_return(self):
        """Test expression blocks must end with return statement"""
        source = """
        func test() : void = {
            // ❌ Expression block without return
            val invalid = {
                val temp = 42
                val computed = temp * 2
                // Missing return statement
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any(
            "Expression block must end with a return statement" in msg
            for msg in error_messages
        )

    def test_expression_block_scope_isolation(self):
        """Test expression blocks create isolated scopes"""
        source = """
        func test() : i32 = {
            val result = {
                val inner = 42
                val computed = inner * 2
                return computed
            }
            
            // ❌ Cannot access inner (out of scope)
            return inner
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any("Undefined variable: 'inner'" in msg for msg in error_messages)

    def test_expression_block_access_outer_scope(self):
        """Test expression blocks can access outer scope variables"""
        source = """
        func test() : i32 = {
            val base = 100
            val multiplier = 3
            
            val result = {
                // ✅ Can access outer scope
                val computed = base * multiplier
                return computed
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_variable_shadowing(self):
        """Test expression blocks can shadow outer variables"""
        source = """
        func test() : i32 = {
            val value = 42
            
            val result = {
                val value = 100        // Shadows outer 'value'
                return value           // Returns 100 (shadowed)
            }
            
            return value               // Returns 42 (original)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_nested_expression_blocks(self):
        """Test nested expression blocks with value production"""
        source = """
        func test() : i32 = {
            val result:i32 = {
                val inner_result:i32 = {
                    val deep_value:i32 = 42
                    return deep_value
                }
                val computed:i32 = inner_result * 2
                return computed
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_type_inference(self):
        """Test expression blocks infer type from return statement"""
        source = """
        func test() : i32 = {
            // Expression block type inferred from return
            val int_result = {
                return 42              // Inferred as i32
            }
            
            val string_result = {
                return "hello"         // Inferred as string
            }
            
            val bool_result = {
                return true            // Inferred as bool
            }
            
            return int_result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_complex_computation(self):
        """Test expression blocks with complex internal computation"""
        source = """
        func test() : i32 = {
            val result = {
                val base = 10
                val multiplier = 5
                val offset = 3
                
                val intermediate = base * multiplier
                val final_result = intermediate + offset
                
                return final_result
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestFunctionBodyBlocks(StandardTestBase):
    """Test function body blocks following unified block system"""

    def test_void_function_body_no_return_required(self):
        """Test void function bodies don't require return statements"""
        source = """
        func setup() : void = {
            val config = "initialize"
            val data = 100
            val flag = true
            // No return required for void functions
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_void_function_body_bare_return_allowed(self):
        """Test void function bodies allow bare return statements"""
        source = """
        func early_exit() : void = {
            val config = "setup"
            val condition = true
            
            // ✅ Bare return allowed in void function (simplified)
            return
            
            val cleanup = "done"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_value_function_body_requires_return(self):
        """Test value-returning function bodies require return with value"""
        source = """
        func compute() : i32 = {
            val base = 100
            val multiplier = 2
            
            return base * multiplier    // ✅ Must return i32-compatible value
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_function_body_return_type_validation(self):
        """Test function body validates return type compatibility"""
        source = """
        func get_number() : i32 = {
            val result:string = "not a number"
            return result              // ❌ string → i32 (invalid)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any(
            "Type mismatch" in msg or "Cannot return" in msg or "string" in msg
            for msg in error_messages
        )

    def test_function_body_with_nested_blocks(self):
        """Test function bodies with nested statement and expression blocks"""
        source = """
        func process_data() : string = {
            val input = "raw_data"
            
            // Statement block for preprocessing
            {
                val validation = true
                val normalized = input
            }
            
            // Expression block for computation
            val result = {
                val processed = "processed_" + input
                return processed
            }
            
            return result    // Function return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_function_body_scope_management(self):
        """Test function bodies manage scope like other blocks"""
        source = """
        func demonstrate_scope() : i32 = {
            val function_scope = 42
            
            {
                val block_scope = 100
                val sum = function_scope + block_scope   // ✅ Access outer scope
            }
            
            // ❌ Cannot access block_scope
            val invalid = block_scope
            
            return function_scope
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any("Undefined variable: 'block_scope'" in msg for msg in error_messages)


class TestUniversalBlockScoping(StandardTestBase):
    """Test universal scope management across all block types"""

    def test_scope_stack_behavior(self):
        """Test consistent scope stack behavior across all block types"""
        source = """
        func test() : i32 = {
            val level1 = "function"      // Function scope
            
            {                            // Statement block scope
                val level2 = "statement"
                
                val expr_result = {      // Expression block scope
                    val level3 = "expression"
                    
                    // ✅ All levels accessible in expression block
                    val check1 = level1  // "function"
                    val check2 = level2  // "statement"  
                    val check3 = level3  // "expression"
                    
                    return 42
                }
                
                // ✅ Function and statement scope accessible
                val check_outer1 = level1    // "function"
                val check_outer2 = level2    // "statement"
            }
            
            // ✅ Only function scope accessible
            val final_check = level1         // "function"
            
            return 100
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_shadowing_across_block_types(self):
        """Test variable shadowing works consistently across all block types"""
        source = """
        func test() : string = {
            val name = "function"
            
            {                                // Statement block
                val name = "statement"       // Shadows function 'name'
                
                val result = {               // Expression block
                    val name = "expression"  // Shadows statement 'name'
                    return name              // "expression"
                }
                
                val statement_name = name    // "statement"
            }
            
            return name                      // "function" (original)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_scope_isolation_across_block_types(self):
        """Test scope isolation works consistently for all block types"""
        source = """
        func test() : void = {
            // Each block type creates isolated scope
            
            {                                // Statement block 1
                val statement_var1 = "first"
            }
            
            val expr_result = {              // Expression block
                val expr_var = "expression"
                return expr_var
            }
            
            {                                // Statement block 2
                val statement_var2 = "second"
                
                // ❌ Cannot access other block variables
                val invalid1:string = statement_var1    // Error: out of scope
                val invalid2:string = expr_var          // Error: out of scope
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2
        error_messages = [e.message for e in errors]
        assert any(
            "Undefined variable: 'statement_var1'" in msg for msg in error_messages
        )
        assert any("Undefined variable: 'expr_var'" in msg for msg in error_messages)


class TestBlockContextDetermination(StandardTestBase):
    """Test context-driven behavior determination in blocks"""

    def test_block_context_by_usage(self):
        """Test blocks behave differently based on usage context"""
        source = """
        func test() : i32 = {
            // Statement context - block executes without producing value
            {
                val temp = "processing"
                val flag = true
            }
            
            // Expression context - block must produce value
            val result = {
                val computed = 42 * 2
                return computed          // Required in expression context
            }
            
            // Assignment context - expression block
            mut mutable_result:i32 = {
                val value = 100
                return value
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_block_return_requirements_by_context(self):
        """Test return requirements differ by block context"""
        source = """
        func test() : i32 = {
            // Statement block - no return required
            {
                val processing = "step1"
                val validation = true
                // No return needed
            }
            
            // Expression block - return required
            val computed = {
                val base = 50
                return base * 2         // Return required for expression context
            }
            
            return computed
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_function_context_provides_return_type(self):
        """Test function context provides return type validation for blocks"""
        source = """
        func returns_int() : i32 = {
            val intermediate = {
                return 42               // Expression block returns i32
            }
            
            {
                val processing = "internal"
                return 100              // Function return (i32 required)
            }
        }
        
        func returns_string() : string = {
            val result = {
                return "computed"       // Expression block returns string
            }
            
            return result               // Function return (string required)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComplexBlockScenarios(StandardTestBase):
    """Test complex scenarios involving multiple block types and interactions"""

    def test_mixed_block_types_interaction(self):
        """Test statement blocks and expression blocks working together"""
        source = """
        func complex_processing() : i32 = {
            val input:i32 = 100
            
            // Statement block for setup
            {
                val config = "setup"
                val validation = true
            }
            
            // Expression block for computation  
            val intermediate:i32 = {
                val base:i32 = input * 2
                val offset:i32 = 10
                return base + offset
            }
            
            // Statement block for cleanup
            {
                val cleanup = "finalize"
                val status = "done"
            }
            
            // Expression block for final result
            val final_result:i32 = {
                val bonus:i32 = 5
                return intermediate + bonus
            }
            
            return final_result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_deeply_nested_mixed_blocks(self):
        """Test deeply nested blocks of different types"""
        source = """
        func nested_complexity() : string = {
            val config = "start"
            
            {                                    // Statement block level 1
                val step1 = "preprocessing"
                
                val intermediate = {             // Expression block level 2
                    val data = "processing"
                    
                    {                            // Statement block level 3
                        val temp = "internal"
                        val validation = true
                    }
                    
                    val result = {               // Expression block level 4
                        val computed = data + "_computed"
                        return computed
                    }
                    
                    return result
                }
                
                val step2 = "postprocessing"
            }
            
            val final = {                        // Expression block final
                val status = config + "_complete"
                return status
            }
            
            return final
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_block_integration_with_variables_and_assignments(self):
        """Test blocks integrate properly with variable declarations and assignments"""
        source = """
        func integration_test() : i32 = {
            val base = 42
            
            // Expression block assigned to val
            val computed = {
                return base + 10
            }
            
            // Expression block assigned to mut  
            mut mutable_result:i32 = {
                return computed + 5
            }
            
            // Statement block with assignments
            {
                mutable_result = computed + 5    // Assignment in statement block
                val local = mutable_result
            }
            
            // Expression block with outer variable access
            val final = {
                return base + computed
            }
            
            return final
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_error_propagation_across_block_boundaries(self):
        """Test that errors are properly detected across different block contexts"""
        source = """
        func error_scenarios() : i32 = {
            {                                    // Statement block with error
                val temp:i32 = undefined_variable    // ❌ Undefined variable
            }
            
            val result = {                       // Expression block with error
                val computed = 42
                // ❌ Missing return statement
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2
        error_messages = [e.message for e in errors]
        assert any("Undefined variable" in msg for msg in error_messages)
        assert any(
            "Expression block must end with a return statement" in msg
            for msg in error_messages
        )


# ... existing code ...
