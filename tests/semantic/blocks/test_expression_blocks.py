"""
Test suite for expression block semantics in Hexen's Unified Block System

Tests expression block behavior (NEW assign/return semantics):
- Produce values via -> statements
- Require final -> OR return statement (dual capability)
- Create isolated scopes
- Allow access to outer scope variables
- Support variable shadowing
- Support nested blocks with proper scope management
- Comptime type context-driven resolution from -> statements

Part of the unified block system described in UNIFIED_BLOCK_SYSTEM.md:
- Single { } syntax for all contexts with context-driven behavior
- Expression blocks: produce values, require final -> statement OR return for function exit
- Universal scope isolation: ALL blocks manage their own scope regardless of context
"""

from tests.semantic import StandardTestBase


class TestExpressionBlocks(StandardTestBase):
    """Test expression block semantics following unified block system"""

    def test_basic_expression_block_value_production(self):
        """Test expression blocks produce values via -> statements with explicit types"""
        source = """
        func test() : i32 = {
            // ✅ Expression block produces value (explicit type required)
            val result : i32 = {
                val computed = 42 * 2
                -> computed
            }

            val another : string = {
                -> "hello world"
            }

            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_requires_assign_or_return(self):
        """Test expression blocks must end with -> or return statement"""
        source = """
        func test() : void = {
            // ❌ Expression block without -> or return
            val invalid = {
                val temp = 42
                val computed = temp * 2
                // Missing -> or return statement
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any("assign" in msg or "return" in msg for msg in error_messages)

    def test_nested_expression_blocks(self):
        """Test nested expression blocks with value production"""
        source = """
        func test() : i32 = {
            val result:i32 = {
                val inner_result:i32 = {
                    val deep_value:i32 = 42
                    -> deep_value
                }
                val computed:i32 = inner_result * 2
                -> computed
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_comptime_type_context(self):
        """Test expression blocks with explicit type annotations (always required)"""
        source = """
        func test() : i32 = {
            // Expression blocks always require explicit type annotations
            val flexible_result : i32 = {
                -> 42              // comptime_int adapts to i32
            }

            val string_result : string = {
                -> "hello"         // string (concrete)
            }

            val bool_result : bool = {
                -> true            // bool (concrete)
            }

            return flexible_result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_complex_computation(self):
        """Test expression blocks with complex internal computation (explicit type required)"""
        source = """
        func test() : i32 = {
            val result : i32 = {
                val base = 10
                val multiplier = 5
                val offset = 3

                val intermediate = base * multiplier
                val final_result = intermediate + offset

                -> final_result
            }

            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
