"""
Test suite for bare return statements

Bare return statements (return;) should be allowed in:
- Void functions
- Statement blocks in void functions
- Statement blocks in non-void functions (early exit)

They should be rejected in:
- Expression blocks (must return a value)
- Non-void functions (without statement block context)
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestBareReturnsInVoidFunctions:
    """Test bare return statements in void functions"""

    def test_bare_return_in_void_function(self):
        """Test basic bare return in void function"""
        source = """
        func doWork() : void = {
            val x = 42
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_multiple_bare_returns_in_void_function(self):
        """Test multiple bare returns in void function"""
        source = """
        func process() : void = {
            val step1 = "start"
            return
            val step2 = "unreachable"
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_bare_return_with_variables_void_function(self):
        """Test bare return with variable declarations in void function"""
        source = """
        func setup() : void = {
            val config = "default"
            val initialized = 100
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_void_function_without_return_still_works(self):
        """Test that void functions don't require return statements"""
        source = """
        func initialize() : void = {
            val x = 42
            val y = "setup"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestBareReturnsInStatementBlocks:
    """Test bare return statements in statement blocks"""

    def test_bare_return_in_statement_block_void_function(self):
        """Test bare return in statement block within void function"""
        source = """
        func process() : void = {
            val x = 42
            {
                val temp = "processing"
                return
            }
            val y = "unreachable"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_bare_return_in_statement_block_non_void_function(self):
        """Test bare return in statement block within non-void function (should fail)"""
        source = """
        func getValue() : i32 = {
            val x = 42
            {
                val condition = 1
                return
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) >= 1
        assert any(
            "cannot have bare return statement" in error.message for error in errors
        )

    def test_nested_statement_blocks_with_bare_returns(self):
        """Test nested statement blocks with bare returns"""
        source = """
        func deepProcess() : void = {
            val level1 = 1
            {
                val level2 = 2
                {
                    val level3 = 3
                    return
                }
            }
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestBareReturnErrors:
    """Test error cases for bare return statements"""

    def test_bare_return_in_expression_block(self):
        """Test that bare return is rejected in expression blocks"""
        source = """
        func test() : i32 = {
            val x = 42
            val result = {
                val temp = 100
                return
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) >= 1
        assert any(
            "Expression block return statement must have a value" in error.message
            for error in errors
        )

    def test_bare_return_in_non_void_function(self):
        """Test that bare return is rejected in non-void functions"""
        source = """
        func getValue() : i32 = {
            val x = 42
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "cannot have bare return statement" in errors[0].message

    def test_void_function_cannot_return_value(self):
        """Test that void functions cannot return values"""
        source = """
        func doWork() : void = {
            val x = 42
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) >= 1
        assert any(
            "Void function cannot return a value" in error.message for error in errors
        )


class TestMixedReturnStatements:
    """Test mixing bare returns with value returns"""

    def test_void_function_mixed_returns_error(self):
        """Test that void functions reject both bare returns and value returns"""
        source = """
        func badFunction() : void = {
            val x = 42
            return
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should have error for the value return
        assert len(errors) >= 1
        assert any(
            "Void function cannot return a value" in error.message for error in errors
        )

    def test_non_void_function_mixed_returns_in_statement_blocks(self):
        """Test mixing bare and value returns in statement blocks"""
        source = """
        func conditional() : i32 = {
            val x = 42
            {
                val condition = true
                return
            }
            {
                val result = 100
                return result
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should reject the bare return in non-void function
        assert len(errors) >= 1
        assert any(
            "cannot have bare return statement" in error.message for error in errors
        )


class TestBareReturnIntegration:
    """Test bare returns with other language features"""

    def test_bare_return_with_undef_variables(self):
        """Test bare return with undef variable handling"""
        source = """
        func setupWithUndef() : void = {
            mut x:i32 = undef
            val message = "initialized"
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_bare_return_early_exit_pattern(self):
        """Test bare return for early exit pattern in void function"""
        source = """
        func earlyExitVoid() : void = {
            val prerequisite = "check"
            return
            val unreachable1 = "never executed"
            val unreachable2 = 999
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []
