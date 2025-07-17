"""
Test suite for expression block semantics in Hexen's Unified Block System

Tests expression block behavior:
- Produce values via return statements
- Require final return statement
- Create isolated scopes
- Allow access to outer scope variables
- Support variable shadowing
- Support nested blocks with proper scope management
- Type inference from return statements

Part of the unified block system described in UNIFIED_BLOCK_SYSTEM.md:
- Single { } syntax for all contexts with context-driven behavior
- Expression blocks: produce values, require final return statement
- Universal scope isolation: ALL blocks manage their own scope regardless of context
"""

from tests.semantic import StandardTestBase


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
