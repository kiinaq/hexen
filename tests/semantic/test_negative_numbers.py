"""
Tests for negative number support in Hexen

These tests validate that negative integers and floats work correctly
with the comptime type system and type coercion.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestNegativeIntegers:
    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_negative_integer_literal(self):
        """Test basic negative integer parsing and semantic analysis"""
        code = """
        func test() : i32 = {
            return -42
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_integer_in_variable(self):
        """Test negative integer in variable declaration"""
        code = """
        func test() : i32 = {
            val negative = -123
            return negative
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_integer_type_coercion(self):
        """Test negative integer coercion to different types"""
        code = """
        func test() : f64 = {
            val as_i32 = -42       // comptime_int -> i32 (default)
            val as_i64 : i64 = -42 // comptime_int -> i64 (coerced)
            val as_f32 : f32 = -42 // comptime_int -> f32 (coerced)
            val as_f64 : f64 = -42 // comptime_int -> f64 (coerced)
            return as_f64
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_mixed_positive_negative_integers(self):
        """Test mixing positive and negative integers"""
        code = """
        func test() : i32 = {
            val positive = 100
            val negative = -50
            return positive
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestNegativeFloats:
    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_negative_float_literal(self):
        """Test basic negative float parsing and semantic analysis"""
        code = """
        func test() : f64 = {
            return -3.14
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_float_in_variable(self):
        """Test negative float in variable declaration"""
        code = """
        func test() : f64 = {
            val pi_negative = -3.14159
            return pi_negative
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_float_type_coercion(self):
        """Test negative float coercion to different float types"""
        code = """
        func test() : f32 = {
            val as_f64 = -2.718        // comptime_float -> f64 (default)
            val as_f32 : f32 = -2.718  // comptime_float -> f32 (coerced)
            return as_f32
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_mixed_positive_negative_floats(self):
        """Test mixing positive and negative floats"""
        code = """
        func test() : f64 = {
            val positive = 2.718
            val negative = -3.14
            val zero = 0.0
            return negative
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestNegativeNumberEdgeCases:
    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_negative_zero_integer(self):
        """Test negative zero integer"""
        code = """
        func test() : i32 = {
            val neg_zero = -0
            return neg_zero
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_zero_float(self):
        """Test negative zero float"""
        code = """
        func test() : f64 = {
            val neg_zero = -0.0
            return neg_zero
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_mixed_negative_positive_assignments(self):
        """Test assignments between negative and positive values"""
        code = """
        func test() : i32 = {
            mut counter = 10
            counter = -5
            counter = 0
            counter = -0
            return counter
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_numbers_in_expression_blocks(self):
        """Test negative numbers work in expression blocks"""
        code = """
        func test() : i32 = {
            val result = {
                val temp = -100
                return temp
            }
            return result
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_negative_numbers_with_undef(self):
        """Test negative numbers work correctly with undef variables"""
        code = """
        func test() : i32 = {
            mut value : i32 = undef
            value = -42
            return -100  // Return a different negative number, not the undef variable
        }
        """
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestNegativeNumberAST:
    def setup_method(self):
        self.parser = HexenParser()

    def test_negative_integer_ast_structure(self):
        """Test that negative integers are parsed correctly in AST"""
        code = """
        func test() : i32 = {
            return -42
        }
        """
        ast = self.parser.parse(code)

        # Navigate to the return statement value
        return_stmt = ast["functions"][0]["body"]["statements"][0]
        value = return_stmt["value"]

        # Expect a unary_operation node wrapping a positive literal
        assert value["type"] == "unary_operation"
        assert value["operator"] == "-"
        assert value["operand"]["type"] == "literal"
        assert value["operand"]["value"] == 42

    def test_negative_float_ast_structure(self):
        """Test that negative floats are parsed correctly in AST"""
        code = """
        func test() : f64 = {
            return -3.14
        }
        """
        ast = self.parser.parse(code)

        # Navigate to the return statement value
        return_stmt = ast["functions"][0]["body"]["statements"][0]
        value = return_stmt["value"]

        # Expect a unary_operation node wrapping a positive literal
        assert value["type"] == "unary_operation"
        assert value["operator"] == "-"
        assert value["operand"]["type"] == "literal"
        assert value["operand"]["value"] == 3.14
