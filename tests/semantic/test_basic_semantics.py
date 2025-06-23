"""
Test basic semantic analysis functionality

This module tests fundamental semantic analysis features that span multiple
language constructs and serve as integration tests. More specific features
are tested in their dedicated test files:

- test_assignment.py: Assignment statement validation
- test_f32_comptime.py: Comptime type system and numeric coercion
- test_bool.py: Boolean type handling
- test_bare_returns.py: Bare return statements
- test_statement_blocks.py: Statement block semantics
- test_expression_blocks.py: Expression block semantics

This file focuses on cross-cutting concerns and basic integration scenarios.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestBasicIntegration:
    """Test basic semantic integration across language features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_minimal_valid_program(self):
        """Test minimal valid Hexen program passes semantic analysis"""
        source = """
        func main() : i32 = {
            val x = 42
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, (
            f"Expected no errors, got: {[e.message for e in errors]}"
        )

    def test_basic_variable_declaration_and_usage(self):
        """Test basic variable declaration and usage pattern"""
        source = """
        func test() : string = {
            val message = "Hello, Hexen!"
            val number = 123
            return message
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_multiple_functions_basic_validation(self):
        """Test multiple function declarations work correctly"""
        source = """
        func first() : i32 = {
            return 42
        }
        
        func second() : string = {
            return "hello"
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0


class TestCrossFeatureIntegration:
    """Test integration between different language features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mixed_declarations_and_assignments(self):
        """Test val/mut declarations with assignments work together"""
        source = """
        func test() : i32 = {
            val immutable = 100
            mut mutable = 200
            mutable = 300
            return immutable
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_blocks_with_mixed_features(self):
        """Test expression and statement blocks with various features"""
        source = """
        func test() : i32 = {
            val base = 10
            val computed = {
                val temp = base
                return temp
            }
            {
                mut counter = 0
                counter = computed
            }
            return computed
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0


class TestErrorIntegration:
    """Test error detection across multiple language features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_multiple_semantic_errors_detected(self):
        """Test that multiple different semantic errors are all detected"""
        source = """
        func test() : i32 = {
            val x = undeclared_var   // Error: undefined variable 
            val y : string = 42      // Error: type mismatch
            val z = "hello"
            z = "world"              // Error: assignment to immutable
            return "wrong"           // Error: return type mismatch
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect multiple errors
        assert len(errors) >= 3  # At least the major errors

        error_messages = [e.message for e in errors]

        # Check for key error types (not exact count due to error recovery)
        assert any("Undefined variable" in msg for msg in error_messages)
        assert any("Type mismatch" in msg for msg in error_messages)
        assert any("Cannot assign to immutable" in msg for msg in error_messages)

    def test_scoping_errors_with_mixed_features(self):
        """Test scoping errors are detected with mixed language features"""
        source = """
        func test() : i32 = {
            val outer = 42
            {
                val inner = 100
                mut temp = inner
            }
            return inner  // Error: inner is out of scope
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message
