"""
Test suite for statement block semantics in Hexen's Unified Block System

Tests statement block behavior:
- Execute code without producing values
- Create isolated scopes
- Allow access to outer scope variables
- Support variable shadowing
- Allow function returns (exits containing function)
- Support nested blocks with proper scope management

Part of the unified block system described in UNIFIED_BLOCK_SYSTEM.md:
- Single { } syntax for all contexts with context-driven behavior
- Statement blocks: execute code, allow function returns, no value production
- Universal scope isolation: ALL blocks manage their own scope regardless of context
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
