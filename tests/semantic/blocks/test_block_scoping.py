"""
Test suite for universal block scoping in Hexen's Unified Block System

Tests universal scope management across all block types:
- Consistent scope stack behavior
- Variable shadowing across block types
- Scope isolation consistency
- Context-driven behavior determination
- Complex nested block scenarios
- Error propagation across block boundaries

Part of the unified block system described in UNIFIED_BLOCK_SYSTEM.md:
- Universal scope isolation: ALL blocks manage their own scope regardless of context
- Context-driven behavior determination
- Integration with variable declarations and assignments
"""

from tests.semantic import StandardTestBase


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
                assign base + computed
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
                // ❌ Missing assign statement
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2
        error_messages = [e.message for e in errors]
        assert any("Undefined variable" in msg for msg in error_messages)
        assert any("assign" in msg or "return" in msg for msg in error_messages)
