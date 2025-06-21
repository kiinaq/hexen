"""
Test bool type semantic analysis in Hexen
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestBoolTypeSemantics:
    """Test semantic analysis of bool type"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

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
        assert len(errors) == 0

    def test_bool_explicit_type_annotation(self):
        """Test explicit bool type annotation"""
        source = """
        func test() : bool = {
            val flag : bool = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_bool_function_return_type(self):
        """Test function returning bool type"""
        source = """
        func is_ready() : bool = {
            return true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_bool_mut_variable_assignment(self):
        """Test mutable bool variable assignment"""
        source = """
        func test() : bool = {
            mut flag : bool = false
            flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_bool_undef_declaration(self):
        """Test bool variable with undef value"""
        source = """
        func test() : bool = {
            mut flag : bool = undef
            flag = true
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestBoolTypeErrors:
    """Test error cases for bool type"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_bool_type_mismatch_assignment(self):
        """Test type mismatch when assigning non-bool to bool variable"""
        source = """
        func test() : bool = {
            mut flag : bool = true
            flag = 42
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Type mismatch in assignment" in errors[0].message
        assert "bool" in errors[0].message
        assert "i32" in errors[0].message

    def test_bool_type_mismatch_declaration(self):
        """Test type mismatch in bool variable declaration"""
        source = """
        func test() : bool = {
            val flag : bool = 42
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Type mismatch" in errors[0].message
        assert "bool" in errors[0].message
        assert "comptime_int" in errors[0].message

    def test_bool_return_type_mismatch(self):
        """Test return type mismatch with bool function"""
        source = """
        func test() : bool = {
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Return type mismatch" in errors[0].message
        assert "bool" in errors[0].message
        assert "comptime_int" in errors[0].message

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
        assert len(errors) == 1
        assert "Cannot assign to immutable variable" in errors[0].message

    def test_bool_undef_usage_error(self):
        """Test using uninitialized bool variable"""
        source = """
        func test() : bool = {
            mut flag : bool = undef
            return flag
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Use of uninitialized variable" in errors[0].message
