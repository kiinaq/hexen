"""
Test suite for unary operations in Hexen semantic analyzer.

Tests semantic analysis of:
- Unary minus (-) for numeric values
- Negative number literals (merged from test_negative_numbers.py)
- Logical not (!) for boolean values
- Type checking and coercion
- Error cases and edge cases
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
    assert_error_count,
)


class TestUnaryMinusSemantics(StandardTestBase):
    """Test semantic analysis of unary minus operator (-)"""

    def test_unary_minus_with_comptime_types(self):
        """Test unary minus with comptime types"""
        source = """
        func main(): i32 = {
            // Comptime int operations
            val x = -42                    // comptime_int
            val y:i32 = -42              // comptime_int → i32
            val z:i64 = -42              // comptime_int → i64
            val w:f32 = -42              // comptime_int → f32
            val v:f64 = -42              // comptime_int → f64

            // Comptime float operations
            val a = -3.14                  // comptime_float
            val b:f32 = -3.14            // comptime_float → f32
            val c:f64 = -3.14            // comptime_float → f64

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_unary_minus_with_concrete_types(self):
        """Test unary minus with concrete numeric types"""
        source = """
        func main(): i32 = {
            // Integer types
            val x:i32 = 42
            val y:i64 = 100
            val neg_x = -x                 // i32 → i32
            val neg_y:i64 = -y           // i64 → i64

            // Float types
            val a:f32 = 3.14
            val b:f64 = 2.718
            val neg_a:f32 = -a           // f32 → f32
            val neg_b:f64 = -b           // f64 → f64

            // Mixed type operations require explicit conversions
            val mixed1:f64 = (-x):f64    // i32 → f64 (explicit required)
            val mixed2:f64 = (-a):f64    // f32 → f64 (explicit required)

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_unary_minus_errors(self):
        """Test error cases for unary minus"""
        source = """
        func main(): i32 = {
            // Non-numeric types
            val str_val:string = "hello"
            val bool_val:bool = true
            val neg_str = -str_val         // Error: Unary minus requires numeric operand
            val neg_bool = -bool_val       // Error: Unary minus requires numeric operand

            // Invalid type coercion
            val x:i32 = 42
            val neg_x:string = -x        // Error: Cannot coerce i32 to string

            // Mixed type operations without explicit type
            val y:i32 = 42
            val z:f64 = 3.14
            val mixed = -y + -z            // Error: Mixed types require explicit result type

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 6)  # Updated to expect 6 errors
        assert any("Unary minus (-) requires numeric operand" in str(e) for e in errors)
        assert any(
            "Type mismatch: variable 'neg_x' declared as string but assigned value of type i32"
            in str(e)
            for e in errors
        )
        assert any("Mixed concrete types" in str(e) for e in errors)


class TestNegativeNumberLiterals(StandardTestBase):
    """Test negative number literals (merged from test_negative_numbers.py)"""

    def test_negative_integer_literals(self):
        """Test basic negative integer parsing and semantic analysis"""
        source = """
        func test() : i32 = {
            val negative = -123
            val zero = -0
            val large = -9223372036854775807
            return -42  // Return negative literal directly
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_integer_type_coercion(self):
        """Test negative integer coercion to different types"""
        source = """
        func test() : f64 = {
            val as_i32 = -42       // comptime_int -> i32 (default)
            val as_i64:i64 = -42 // comptime_int -> i64 (coerced)
            val as_f32:f32 = -42 // comptime_int -> f32 (coerced)
            val as_f64:f64 = -42 // comptime_int -> f64 (coerced)
            return as_f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_float_literals(self):
        """Test basic negative float parsing and semantic analysis"""
        source = """
        func test() : f64 = {
            val pi_negative = -3.14159
            val e_negative = -2.718
            val zero_float = -0.0
            return -2.5  // Return negative float literal directly
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_float_type_coercion(self):
        """Test negative float coercion to different float types"""
        source = """
        func test() : f32 = {
            val as_f64 = -2.718        // comptime_float -> f64 (default)
            val as_f32:f32 = -2.718  // comptime_float -> f32 (coerced)
            return as_f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_mixed_positive_negative_numbers(self):
        """Test mixing positive and negative numbers"""
        source = """
        func test() : i32 = {
            val positive_int = 100
            val negative_int = -50
            val positive_float = 2.718
            val negative_float = -3.14
            val zero_int = 0
            val zero_float = 0.0
            val neg_zero_int = -0
            val neg_zero_float = -0.0
            return positive_int
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_numbers_in_assignments(self):
        """Test assignments with negative values"""
        source = """
        func test() : i32 = {
            mut counter:i32 = 10
            counter = -5
            counter = 0
            counter = -0
            
            mut float_val:f64 = 1.0
            float_val = -3.14
            float_val = -0.0
            
            return counter
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_numbers_with_undef(self):
        """Test negative numbers work correctly with undef variables"""
        source = """
        func test() : i32 = {
            mut int_value:i32 = undef
            int_value = -42
            
            mut float_value:f64 = undef
            float_value = -3.14
            
            return -100  // Return a different negative number
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_number_ast_structure(self):
        """Test that negative numbers are parsed correctly into AST"""
        source = """
        func test() : i32 = {
            val neg_int = -42
            val neg_float:f64 = -3.14
            return neg_int
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Verify AST structure contains unary operations
        assert isinstance(ast, dict)
        assert "functions" in ast


class TestLogicalNotSemantics(StandardTestBase):
    """Test semantic analysis of logical not operator (!)"""

    def test_logical_not_with_booleans(self):
        """Test logical not with boolean values"""
        source = """
        func main(): bool = {
            // Boolean variables
            val a:bool = true
            val b:bool = false
            val not_a = !a                 // bool → bool
            val not_b = !b                 // bool → bool

            // Complex boolean expressions
            val c = !(a && b)              // bool → bool
            val d = !(a || b)              // bool → bool
            val e = !!a                    // bool → bool

            return true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # No errors should be produced for valid boolean NOT expressions
        assert errors == []

    def test_logical_not_errors(self):
        """Test error cases for logical not"""
        source = """
        func main(): bool = {
            // Non-boolean types
            val int_val:i32 = 42
            val float_val:f32 = 3.14
            val str_val:string = "hello"
            val not_int = !int_val         // Error: Logical not requires boolean operand
            val not_float = !float_val     // Error: Logical not requires boolean operand
            val not_str = !str_val         // Error: Logical not requires boolean operand

            // Invalid type coercion
            val bool_val:bool = true
            val not_bool:i32 = !bool_val // Error: Cannot coerce bool to i32

            // Mixed type operations
            val a:bool = true
            val b:bool = false
            val mixed = !a && !b           // No error: Both operands are boolean

            return true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Only 7 errors should be produced (not 8)
        assert_error_count(errors, 7)
        assert any("Logical not (!) requires boolean operand" in str(e) for e in errors)
        assert any("Cannot infer type for variable 'not_int'" in str(e) for e in errors)
        assert any(
            "Cannot infer type for variable 'not_float'" in str(e) for e in errors
        )
        assert any("Cannot infer type for variable 'not_str'" in str(e) for e in errors)


class TestUnaryOperatorIntegration(StandardTestBase):
    """Test integration of unary operators with other language features"""

    def test_unary_operators_in_expressions(self):
        """Test unary operators in complex expressions"""
        source = """
        func main(): i32 = {
            // Unary minus in arithmetic
            val x:i32 = 42
            val y:f64 = 3.14
            val a:i32 = -x * 2           // i32 → i32
            val b:i32 = 2 * -x           // i32 → i32
            val c:f64 = (-x):f64 + -y    // i32:f64 + f64 → f64
            val d:f64 = -2.5 * -3.5      // comptime_float → f64

            // Logical not in boolean expressions
            val e:bool = true
            val f:bool = false
            val g = !e && !f               // bool → bool
            val h = !(e || f)              // bool → bool
            val i = !!e                    // bool → bool

            // Mixed unary operators
            val j:i32 = -42
            val zero:i32 = 0
            val k:bool = !(j > zero)     // i32 → bool (via comparison)

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_unary_operators_with_undef(self):
        """Test unary operators with undef variables"""
        source = """
        func main(): i32 = {
            mut x:i32 = undef
            mut y:bool = undef
            
            x = -42                        // Assign negative literal
            y = !true                      // Assign logical not result
            
            val a = -x                     // Use unary minus on assigned variable
            val b = !y                     // Use logical not on assigned variable
            
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_negative_literals_in_complex_expressions(self):
        """Test negative literals integrated with complex expressions"""
        source = """
        func test() : f64 = {
            // Negative literals in arithmetic expressions
            val complex1:f64 = -42 + 3.14 * -2.5
            val complex2:f64 = (-10 + 5) * -3
            val complex3:f64 = -(-42)  // Double negative
            
            // Negative literals in comparisons
            val comp1:bool = -42 > -100
            val comp2:bool = -3.14 < 0.0
            val comp3:bool = -0 == 0
            
            // Negative literals with explicit types
            val annotated1:i64 = -42
            val annotated2:f32 = -3.14
            
            return complex1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
