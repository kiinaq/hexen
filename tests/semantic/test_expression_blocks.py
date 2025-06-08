"""
Tests for expression blocks in Hexen

Tests the unified block concept where blocks can be used as expressions
with explicit return statements. Covers parsing, semantic analysis,
scoping, and error handling.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestExpressionBlockBasics:
    """Test basic expression block functionality"""

    def test_simple_expression_block_i32(self):
        """Test basic expression block returning i32"""
        source = """
        func main() -> i32 {
            val result = {
                return 42
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_expression_block_with_local_variable(self):
        """Test expression block with local variable declaration"""
        source = """
        func main() -> i32 {
            val result = {
                val x = 42
                return x
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_expression_block_different_types(self):
        """Test expression blocks with different return types"""
        source = """
        func main() -> i32 {
            val int_result = {
                return 42
            }
            val string_result = {
                return "hello"
            }
            return int_result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_expression_block_multiple_statements(self):
        """Test expression block with multiple statements before return"""
        source = """
        func main() -> i32 {
            val result = {
                val x = 10
                val y = 32
                return y
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should work fine now
        assert errors == []


class TestExpressionBlockScoping:
    """Test scoping behavior of expression blocks"""

    def test_block_variables_are_scoped(self):
        """Test that variables declared in block don't leak to outer scope"""
        source = """
        func main() -> i32 {
            val result = {
                val inner = 42
                return inner
            }
            return inner
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # Should fail - 'inner' is not accessible outside the block
        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message

    def test_block_can_access_outer_scope(self):
        """Test that expression blocks can access variables from outer scope"""
        source = """
        func main() -> i32 {
            val outer = 10
            val result = {
                return outer
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_shadowing_in_expression_block(self):
        """Test variable shadowing in expression blocks"""
        source = """
        func main() -> i32 {
            val x = 10
            val result = {
                val x = 42
                return x
            }
            return x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_nested_expression_blocks(self):
        """Test nested expression blocks"""
        source = """
        func main() -> i32 {
            val result = {
                val inner = {
                    return 42
                }
                return inner
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestExpressionBlockErrors:
    """Test error handling for expression blocks"""

    def test_block_without_return_statement(self):
        """Test that expression blocks require a return statement"""
        source = """
        func main() -> i32 {
            val result = {
                val x = 42
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
            "Expression block must end with a return statement" in error.message
            for error in errors
        )

    def test_return_not_last_statement(self):
        """Test that return statement must be the last statement in expression block"""
        source = """
        func main() -> i32 {
            val result = {
                return 42
                val x = 10
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
            "Return statement must be the last statement in expression block"
            in error.message
            for error in errors
        )

    def test_type_mismatch_with_explicit_annotation(self):
        """Test type mismatch when using explicit type annotation"""
        source = """
        func main() -> i32 {
            val result: i32 = {
                return "hello"
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) >= 1
        assert any("Type mismatch" in error.message for error in errors)


class TestExpressionBlockIntegration:
    """Test integration with existing language features"""

    def test_expression_block_with_explicit_type(self):
        """Test expression block with explicit type annotation"""
        source = """
        func main() -> i32 {
            val result: i32 = {
                val x = 42
                return x
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_expression_block_with_mut_variable(self):
        """Test expression block assigned to mutable variable"""
        source = """
        func main() -> i32 {
            mut result = {
                return 42
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_expression_block_with_undef_handling(self):
        """Test expression block with undef values"""
        source = """
        func main() -> i32 {
            val x: i32 = undef
            val result = {
                return 42
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_complex_expression_block_scenario(self):
        """Test complex scenario with multiple features"""
        source = """
        func main() -> string {
            val outer = "world"
            val greeting = {
                val prefix = "hello"
                return prefix
            }
            return greeting
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestExpressionBlockAST:
    """Test AST structure of expression blocks"""

    def test_expression_block_ast_structure(self):
        """Test that expression blocks generate correct AST structure"""
        source = """
        func main() -> i32 {
            val result = {
                val x = 42
                return x
            }
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        # Check AST structure
        function = ast["functions"][0]
        val_declaration = function["body"]["statements"][0]
        block_expression = val_declaration["value"]

        assert block_expression["type"] == "block"
        assert len(block_expression["statements"]) == 2
        assert block_expression["statements"][0]["type"] == "val_declaration"
        assert block_expression["statements"][1]["type"] == "return_statement"
