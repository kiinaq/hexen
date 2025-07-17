"""
Test suite for function body blocks in Hexen's Unified Block System

Tests function body block behavior:
- Void functions don't require return statements
- Void functions allow bare return statements
- Value-returning functions require return with value
- Return type validation
- Nested blocks within function bodies
- Scope management like other blocks

Part of the unified block system described in UNIFIED_BLOCK_SYSTEM.md:
- Single { } syntax for all contexts with context-driven behavior
- Function bodies: unified with all other blocks, context provides return type validation
- Universal scope isolation: ALL blocks manage their own scope regardless of context
"""

from tests.semantic import StandardTestBase


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
