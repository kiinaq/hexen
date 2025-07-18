"""
Test bool type semantic analysis in Hexen
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
    assert_error_count,
    assert_error_contains,
)


class TestBoolTypeSemantics(StandardTestBase):
    """Test semantic analysis of bool type"""

    def test_bool_type_inference(self):
        """Test type inference for boolean literals"""
        source = """
        func test() : bool = {
            val flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_bool_explicit_type_declaration(self):
        """Test explicit bool type declaration"""
        source = """
        func test() : bool = {
            val flag:bool = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_bool_function_return_type(self):
        """Test function returning bool type"""
        source = """
        func is_ready() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_bool_mut_variable_assignment(self):
        """Test mutable bool variable assignment"""
        source = """
        func test() : bool = {
            mut flag:bool = false
            flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_bool_undef_declaration(self):
        """Test bool variable with undef value"""
        source = """
        func test() : bool = {
            mut flag:bool = undef
            flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestBoolTypeErrors(StandardTestBase):
    """Test error cases for bool type"""

    def test_bool_type_mismatch_assignment(self):
        """Test type mismatch when assigning non-bool to bool variable"""
        source = """
        func test() : bool = {
            mut flag:bool = true
            flag = 42
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Type mismatch in assignment")
        assert_error_contains(errors, "bool")
        assert_error_contains(errors, "i32")

    def test_bool_type_mismatch_declaration(self):
        """Test type mismatch in bool variable declaration"""
        source = """
        func test() : bool = {
            val flag:bool = 42
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Type mismatch")
        assert_error_contains(errors, "bool")
        assert_error_contains(errors, "comptime_int")

    def test_bool_return_type_mismatch(self):
        """Test return type mismatch with bool function"""
        source = """
        func test() : bool = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Return type mismatch")
        assert_error_contains(errors, "bool")
        assert_error_contains(errors, "comptime_int")

    def test_bool_assignment_to_immutable(self):
        """Test assignment to immutable bool variable"""
        source = """
        func test() : bool = {
            val flag = true
            flag = false
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Cannot assign to immutable variable")

    def test_bool_undef_usage_error(self):
        """Test using uninitialized bool variable"""
        source = """
        func test() : bool = {
            mut flag:bool = undef
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Use of uninitialized variable")
