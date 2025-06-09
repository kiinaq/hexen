"""
Test suite for statement blocks

Statement blocks are standalone execution blocks that:
- Manage their own scope
- Allow return statements that match function signature
- Don't require return statements (unlike expression blocks)
- Can be nested and interact with other block types
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestStatementBlockBasics:
    """Basic statement block functionality"""

    def test_simple_statement_block(self):
        """Test basic statement block with variable declarations"""
        source = """
        func main() : i32 = {
            val x = 42
            {
                val y = "hello"
                val z = 123
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_statement_block_in_void_function(self):
        """Test statement block within void function"""
        source = """
        func doWork() : void = {
            val x = 42
            {
                val temp = "processing"
                val counter = 100
            }
            val y = "done"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_empty_statement_block(self):
        """Test empty statement block"""
        source = """
        func test() : void = {
            val x = 42
            {
            }
            val y = "after"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_multiple_statement_blocks(self):
        """Test multiple statement blocks in same function"""
        source = """
        func process() : void = {
            val step1 = "start"
            {
                val temp1 = 100
                val result1 = "phase1"
            }
            val step2 = "middle"
            {
                val temp2 = 200
                val result2 = "phase2"
            }
            val step3 = "end"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestStatementBlockScoping:
    """Test scoping behavior of statement blocks"""

    def test_statement_block_variables_are_scoped(self):
        """Test that variables in statement block don't leak to outer scope"""
        source = """
        func test() : i32 = {
            val outer = 42
            {
                val inner = 100
                val temp = "scoped"
            }
            return inner
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message

    def test_statement_block_can_access_outer_scope(self):
        """Test that statement block can access outer scope variables"""
        source = """
        func test() : i32 = {
            val outer = 42
            {
                val sum = outer
                val temp = "using outer"
            }
            return outer
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_statement_block_shadowing(self):
        """Test variable shadowing in statement blocks"""
        source = """
        func test() : i32 = {
            val x = 42
            {
                val x = 100
                val y = x
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_nested_statement_blocks(self):
        """Test nested statement blocks and their scoping"""
        source = """
        func test() : i32 = {
            val level1 = 1
            {
                val level2 = 2
                {
                    val level3 = 3
                    val sum = level1
                }
                val access = level1
            }
            return level1
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestStatementBlockReturns:
    """Test return statement behavior in statement blocks"""

    def test_statement_block_return_from_function(self):
        """Test that statement block can return from outer function"""
        source = """
        func earlyReturn() : i32 = {
            val x = 42
            {
                val condition = 100
                return condition
            }
            val unreachable = "never executed"
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_statement_block_return_type_validation(self):
        """Test that returns in statement blocks are validated against function signature"""
        source = """
        func test() : i32 = {
            val x = 42
            {
                val message = "wrong type"
                return message
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Return type mismatch" in errors[0].message
        assert "expected i32, got string" in errors[0].message

    def test_statement_block_multiple_returns(self):
        """Test multiple return statements in statement blocks"""
        source = """
        func conditional() : i32 = {
            val x = 42
            {
                val a = 10
                return a
                val b = 20
                return b
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_void_function_statement_block_no_returns(self):
        """Test that void functions can't have returns even in statement blocks"""
        source = """
        func doWork() : void = {
            val x = 42
            {
                val temp = 100
                return temp
            }
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) >= 1
        # Should detect void function return error
        assert any(
            "Void function cannot have return statements" in error.message
            for error in errors
        )


class TestStatementBlockIntegration:
    """Test statement blocks with other language features"""

    def test_statement_block_with_expression_block(self):
        """Test statement block alongside expression block"""
        source = """
        func mixed() : i32 = {
            val x = 42
            {
                val temp = "statement block"
                val counter = 100
            }
            val result = {
                val computed = x
                return computed
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_statement_block_with_undef(self):
        """Test statement block with undef variables"""
        source = """
        func withUndef() : i32 = {
            val x : i32 = undef
            {
                val temp = 42
                val message = "processing"
            }
            val result = 100
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_statement_block_with_all_types(self):
        """Test statement block with all supported types"""
        source = """
        func allTypes() : string = {
            val i32_val = 42
            {
                val str_val = "hello"
                val another_i32 = 100
            }
            return "completed"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestStatementBlockEdgeCases:
    """Test edge cases and error conditions"""

    def test_statement_block_variable_redeclaration(self):
        """Test variable redeclaration within statement block"""
        source = """
        func test() : i32 = {
            {
                val x = 42
                val x = 100
            }
            return 0
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "already declared in this scope" in errors[0].message

    def test_deeply_nested_statement_blocks(self):
        """Test deeply nested statement blocks"""
        source = """
        func deepNesting() : i32 = {
            val level0 = 0
            {
                val level1 = 1
                {
                    val level2 = 2
                    {
                        val level3 = 3
                        {
                            val level4 = 4
                            val sum = level0
                        }
                    }
                }
            }
            return level0
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_statement_block_return_from_nested_context(self):
        """Test return from deeply nested statement blocks"""
        source = """
        func nestedReturn() : i32 = {
            val x = 42
            {
                val a = 10
                {
                    val b = 20
                    {
                        val c = 30
                        return c
                    }
                }
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []
