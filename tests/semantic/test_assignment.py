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

    def test_simple_mut_assignment(self):
        """Test basic assignment to mut variable"""
        source = """
        func test() : void = {
            mut x = 42
            x = 100
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_self_assignment(self):
        """Test self-assignment (x = x)"""
        source = """
        func test() : void = {
            mut x = 42
            x = x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestAssignmentErrors:
    """Test assignment error cases"""

    def test_assignment_to_val_variable(self):
        """Test that assignment to val variable fails"""
        source = """
        func test() : void = {
            val x = 42
            x = 100
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Cannot assign to immutable variable 'x'" in errors[0].message

    def test_assignment_to_undefined_variable(self):
        """Test assignment to undefined variable fails"""
        source = """
        func test() : void = {
            unknown = 42
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 2
        # Check that both errors are detected


class TestAssignmentInBlocks:
    """Test assignment in different block contexts"""

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

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

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_assignment_to_scoped_variable_error(self):
        """Test that assignment to out-of-scope variable fails"""
        source = """
        func test() : void = {
            mut x = 42
            {
                mut scoped = 100
            }
            scoped = 200
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable: 'scoped'" in errors[0].message


class TestAssignmentWithExplicitTypes:
    """Test assignment with explicit type annotations"""

    def test_assignment_with_explicit_types(self):
        """Test assignment to explicitly typed variables"""
        source = """
        func test() : void = {
            mut x : i32 = 42
            mut y : string = "hello"
            x = 100
            y = "world"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_assignment_with_type_mismatch_explicit(self):
        """Test type mismatch with explicitly typed variable"""
        source = """
        func test() : void = {
            mut x : i64 = 42
            x = "wrong type"
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        # With Zig-style comptime types, expect only 1 error:
        # - Assignment type mismatch (string to i64 variable)
        # No error for declaration because comptime_int (42) can coerce to i64
        assert len(errors) == 1
        assert any("Type mismatch in assignment" in error.message for error in errors)
        assert any(
            "variable 'x' is i64, but assigned value is string" in error.message
            for error in errors
        )


class TestAssignmentWithUndef:
    """Test assignment with undef variables"""

    def test_assignment_to_undef_variable(self):
        """Test assignment to undef variable"""
        source = """
        func test() : void = {
            mut x : i32 = undef
            x = 42
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_assignment_from_undef_variable(self):
        """Test assignment from undef variable (should fail)"""
        source = """
        func test() : void = {
            mut x : i32 = undef
            mut y = 42
            y = x
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Use of uninitialized variable: 'x'" in errors[0].message


class TestAssignmentIntegration:
    """Test assignment integration with other features"""

    def test_assignment_with_variable_references(self):
        """Test assignment using other variables as values"""
        source = """
        func test() : void = {
            val source = 42
            mut target = 0
            target = source
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_assignment_chain_pattern(self):
        """Test pattern of sequential assignments"""
        source = """
        func test() : void = {
            val initial = 42
            mut step1 = 0
            mut step2 = 0
            mut final = 0
            
            step1 = initial
            step2 = step1
            final = step2
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []
