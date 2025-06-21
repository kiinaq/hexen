"""
Tests for f32 type and comptime type system.

This module tests the new numeric type system:
- f32 type support
- comptime_int for integer literals
- comptime_float for float literals
- Context-dependent type coercion
- Type safety with elegant flexibility
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestF32Type:
    """Test f32 type support"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_f32_explicit_declaration(self):
        """Test explicit f32 variable declaration"""
        source = """
        func test() : f32 = {
            val x : f32 = 3.14
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_f32_function_return(self):
        """Test f32 function return type"""
        source = """
        func get_pi() : f32 = {
            return 3.14159
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_f32_with_integer_coercion(self):
        """Test f32 can accept integer literals via comptime_int coercion"""
        source = """
        func test() : f32 = {
            val x : f32 = 42  // comptime_int -> f32
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_f32_assignment(self):
        """Test f32 variable assignment"""
        source = """
        func test() : void = {
            mut x : f32 = 1.0
            x = 2.5
            x = 42  // comptime_int -> f32 coercion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComptimeInt:
    """Test comptime_int behavior (integer literals)"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_int_to_i32_inference(self):
        """Test comptime_int infers to i32 by default"""
        source = """
        func test() : i32 = {
            val x = 42  // comptime_int -> i32 (default)
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_int_to_i64_coercion(self):
        """Test comptime_int can coerce to i64"""
        source = """
        func test() : i64 = {
            val x : i64 = 42  // comptime_int -> i64
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_int_to_f32_coercion(self):
        """Test comptime_int can coerce to f32"""
        source = """
        func test() : f32 = {
            val x : f32 = 42  // comptime_int -> f32
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_int_to_f64_coercion(self):
        """Test comptime_int can coerce to f64"""
        source = """
        func test() : f64 = {
            val x : f64 = 42  // comptime_int -> f64
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_int_cannot_coerce_to_bool(self):
        """Test comptime_int cannot coerce to bool (type safety)"""
        source = """
        func test() : bool = {
            val x : bool = 42  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Type mismatch" in errors[0].message
        assert "bool" in errors[0].message
        assert "comptime_int" in errors[0].message

    def test_comptime_int_cannot_coerce_to_string(self):
        """Test comptime_int cannot coerce to string (type safety)"""
        source = """
        func test() : string = {
            val x : string = 42  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Type mismatch" in errors[0].message
        assert "string" in errors[0].message
        assert "comptime_int" in errors[0].message


class TestComptimeFloat:
    """Test comptime_float behavior (float literals)"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_float_to_f64_inference(self):
        """Test comptime_float infers to f64 by default"""
        source = """
        func test() : f64 = {
            val x = 3.14  // comptime_float -> f64 (default)
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_float_to_f32_coercion(self):
        """Test comptime_float can coerce to f32"""
        source = """
        func test() : f32 = {
            val x : f32 = 3.14  // comptime_float -> f32
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_float_cannot_coerce_to_int(self):
        """Test comptime_float cannot coerce to integer types (precision loss)"""
        source = """
        func test() : i32 = {
            val x : i32 = 3.14  // Should fail - precision loss
            return 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "truncation" in errors[0].message
        assert "i32" in errors[0].message

    def test_comptime_float_cannot_coerce_to_bool(self):
        """Test comptime_float cannot coerce to bool (type safety)"""
        source = """
        func test() : bool = {
            val x : bool = 3.14  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Type mismatch" in errors[0].message
        assert "bool" in errors[0].message
        assert "comptime_float" in errors[0].message


class TestRegularTypeCoercion:
    """Test regular type coercion (non-comptime types)"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_i32_to_i64_widening(self):
        """Test i32 can widen to i64"""
        source = """
        func test() : i64 = {
            val small : i32 = 42
            val large : i64 = small  // i32 -> i64 widening
            return large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i32_to_f32_conversion(self):
        """Test i32 can convert to f32"""
        source = """
        func test() : f32 = {
            val int_val : i32 = 42
            val float_val : f32 = int_val  // i32 -> f32 conversion
            return float_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_f32_to_f64_widening(self):
        """Test f32 can widen to f64"""
        source = """
        func test() : f64 = {
            val small : f32 = 3.14
            val large : f64 = small  // f32 -> f64 widening
            return large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestMixedNumericOperations:
    """Test mixed numeric operations with the new type system"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mixed_numeric_declarations(self):
        """Test mixed numeric type declarations"""
        source = """
        func test() : void = {
            val int_literal = 42        // comptime_int -> i32
            val float_literal = 3.14    // comptime_float -> f64
            val explicit_i64 : i64 = 100    // comptime_int -> i64
            val explicit_f32 : f32 = 2.5    // comptime_float -> f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_numeric_assignments(self):
        """Test mixed numeric type assignments"""
        source = """
        func test() : void = {
            mut i32_var : i32 = 0
            mut i64_var : i64 = 0
            mut f32_var : f32 = 0.0
            mut f64_var : f64 = 0.0
            
            i32_var = 42        // comptime_int -> i32
            i64_var = 100       // comptime_int -> i64
            f32_var = 3.14      // comptime_float -> f32
            f64_var = 2.718     // comptime_float -> f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_numeric_returns(self):
        """Test mixed numeric return types"""
        source = """
        func get_i32() : i32 = {
            return 42  // comptime_int -> i32
        }
        
        func get_f32() : f32 = {
            return 3.14  // comptime_float -> f32
        }
        
        func get_mixed() : f64 = {
            return 42  // comptime_int -> f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComptimeTypeEdgeCases:
    """Test edge cases and error conditions with comptime types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_type_in_error_messages(self):
        """Test that error messages properly show comptime types"""
        source = """
        func test() : string = {
            return 42  // comptime_int cannot coerce to string
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "comptime_int" in errors[0].message
        assert "string" in errors[0].message

    def test_multiple_comptime_coercions(self):
        """Test multiple comptime type coercions in one function"""
        source = """
        func test() : void = {
            val a : i32 = 42    // comptime_int -> i32
            val b : i64 = 100   // comptime_int -> i64
            val c : f32 = 3.14  // comptime_float -> f32
            val d : f64 = 2.718 // comptime_float -> f64
            val e : f32 = 5     // comptime_int -> f32
            val f : f64 = 7     // comptime_int -> f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
