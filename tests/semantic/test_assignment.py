"""
Test suite for assignment statements

Assignment statements should:
- Only work with mut variables (not val)
- Require type compatibility between target and value
- Work in all block types (expression, statement, function)
- Validate variable existence and mutability
- Support self-assignment
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestBasicAssignment:
    """Test basic assignment functionality"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_mut_assignment(self):
        """Test basic assignment to mut variable"""
        source = """
        func test() : void = {
            mut x = 42
            x = 100
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_multiple_assignments(self):
        """Test multiple assignments to same variable"""
        source = """
        func test() : void = {
            mut counter = 0
            counter = 10
            counter = 20
            counter = 30
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_different_types_assignment(self):
        """Test assignment with different compatible types"""
        source = """
        func test() : void = {
            mut number = 42
            mut text = "hello"
            number = 100
            text = "world"
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_self_assignment(self):
        """Test self-assignment (x = x)"""
        source = """
        func test() : void = {
            mut x = 42
            x = x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []


class TestAssignmentErrors:
    """Test assignment error cases"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_to_val_variable(self):
        """Test that assignment to val variable fails"""
        source = """
        func test() : void = {
            val x = 42
            x = 100
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Cannot assign to immutable variable 'x'" in errors[0].message

    def test_assignment_to_undefined_variable(self):
        """Test assignment to undefined variable fails"""
        source = """
        func test() : void = {
            unknown = 42
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable: 'unknown'" in errors[0].message

    def test_type_mismatch_assignment(self):
        """Test type mismatch in assignment"""
        source = """
        func test() : void = {
            mut x = 42
            x = "wrong type"
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Type mismatch in assignment" in errors[0].message
        assert "variable 'x' is i32, but assigned value is string" in errors[0].message

    def test_multiple_type_mismatches(self):
        """Test multiple type mismatch errors"""
        source = """
        func test() : void = {
            mut number = 42
            mut text = "hello"
            number = "wrong"
            text = 123
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 2
        # Check that both errors are detected


class TestAssignmentInBlocks:
    """Test assignment in different block contexts"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_in_statement_block(self):
        """Test assignment works in statement blocks"""
        source = """
        func test() : void = {
            mut x = 42
            {
                x = 100
                mut y = "hello"
                y = "world"
            }
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_assignment_in_expression_block(self):
        """Test assignment works in expression blocks"""
        source = """
        func test() : i32 = {
            mut x = 42
            val result = {
                x = 100
                return x
            }
            return result
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_assignment_across_scopes(self):
        """Test assignment to outer scope variables"""
        source = """
        func test() : void = {
            mut outer = 42
            {
                outer = 100
                mut inner = "hello"
                {
                    outer = 200
                    inner = "nested"
                }
            }
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_assignment_to_scoped_variable_error(self):
        """Test assignment to inner scope variable from outer scope fails"""
        source = """
        func test() : void = {
            {
                mut inner = 42
            }
            inner = 100
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message


class TestAssignmentWithExplicitTypes:
    """Test assignment with explicit type annotations"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_with_explicit_types(self):
        """Test assignment with explicit type annotations"""
        source = """
        func test() : void = {
            mut x : i32 = 42
            mut y : string = "hello"
            x = 100
            y = "world"
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_assignment_with_type_mismatch_explicit(self):
        """Test assignment with type mismatch and explicit types"""
        source = """
        func test() : void = {
            mut x : i32 = 42
            mut y : string = "hello"
            x = "wrong"
            y = 123
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 2  # Both x and y assignments should fail
        assert all("Type mismatch in assignment" in str(error) for error in errors)


class TestAssignmentWithUndef:
    """Test assignment with undef values"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_to_undef_variable(self):
        """Test assignment to variable initialized with undef"""
        source = """
        func test() : void = {
            mut x : i32 = undef
            x = 42
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_assignment_from_undef_variable(self):
        """Test assignment from variable that is undef"""
        source = """
        func test() : void = {
            mut x : i32 = undef
            mut y : i32 = 0
            y = x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Use of uninitialized variable: 'x'" in errors[0].message


class TestAssignmentIntegration:
    """Test assignment integration with other features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_with_variable_references(self):
        """Test assignment using other variable references"""
        source = """
        func test() : void = {
            val a = 42
            mut b = 100
            b = a
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []

    def test_assignment_chain_pattern(self):
        """Test chained assignment patterns"""
        source = """
        func test() : void = {
            mut x = 42
            mut y = 100
            x = y
            y = x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert errors == []
