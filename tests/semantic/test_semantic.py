"""
Test module for semantic analysis

Tests semantic analysis including type checking, symbol table management,
and error detection.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestSemanticAnalysis:
    """Test semantic analysis functionality"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_basic_type_inference(self):
        """Test basic type inference from literals"""
        source = """
        func main() : i32  = {
            val x = 42
            val message = "Hello"
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, (
            f"Expected no errors, got: {[e.message for e in errors]}"
        )

    def test_explicit_type_annotations(self):
        """Test explicit type annotations work correctly"""
        source = """
        func main() : i32  = {
            val x: i32 = 42
            val message: string = "Hello"
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_undef_requires_explicit_type(self):
        """Test that undef variables work with explicit types"""
        source = """
        func main() : i32  = {
            val x: i32 = undef
            val y = 42
            return y
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_type_mismatch_error(self):
        """Test type mismatch detection"""
        source = """
        func main() : i32  = {
            val x: string = 42
            return 0
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Type mismatch" in errors[0].message
        assert "string" in errors[0].message
        assert "i32" in errors[0].message

    def test_undefined_variable_error(self):
        """Test undefined variable detection"""
        source = """
        func main() : i32  = {
            return unknown_var
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable" in errors[0].message
        assert "unknown_var" in errors[0].message

    def test_uninitialized_variable_usage(self):
        """Test that using uninitialized variables is caught"""
        source = """
        func main() : i32  = {
            val x: i32 = undef
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Use of uninitialized variable" in errors[0].message

    def test_return_type_mismatch(self):
        """Test return type mismatch detection"""
        source = """
        func main() : string  = {
            val x = 42
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Return type mismatch" in errors[0].message
        assert "expected string" in errors[0].message
        assert "got i32" in errors[0].message

    def test_multiple_variables_same_scope(self):
        """Test multiple variable declarations in same scope"""
        source = """
        func main() : i32  = {
            val x = 42
            val y = "hello"
            mut z = 100
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_variable_redeclaration_error(self):
        """Test that redeclaring variables in same scope is caught"""
        source = """
        func main() : i32  = {
            val x = 42
            val x = 100
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "already declared" in errors[0].message

    def test_all_types_supported(self):
        """Test that all Hexen types work correctly"""
        source = """
        func main() : i32  = {
            val a = 42
            val b = 100
            val d = "hello"
            return a
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0
