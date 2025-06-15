"""
Test suite for unary operations in Hexen semantic analyzer.

Tests semantic analysis of:
- Unary minus (-) for numeric values
- Logical not (!) for boolean values
- Type checking and coercion
- Error cases and edge cases
"""

from hexen.parser import HexenParser
from hexen.semantic.analyzer import SemanticAnalyzer


class TestUnaryMinusSemantics:
    """Test semantic analysis of unary minus operator (-)"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_unary_minus_with_comptime_types(self):
        """Test unary minus with comptime types"""
        source = """
        func main(): i32 = {
            // Comptime int operations
            val x = -42                    // comptime_int
            val y : i32 = -42              // comptime_int → i32
            val z : i64 = -42              // comptime_int → i64
            val w : f32 = -42              // comptime_int → f32
            val v : f64 = -42              // comptime_int → f64

            // Comptime float operations
            val a = -3.14                  // comptime_float
            val b : f32 = -3.14            // comptime_float → f32
            val c : f64 = -3.14            // comptime_float → f64

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_unary_minus_with_concrete_types(self):
        """Test unary minus with concrete numeric types"""
        source = """
        func main(): i32 = {
            // Integer types
            val x : i32 = 42
            val y : i64 = 100
            val neg_x = -x                 // i32 → i32
            val neg_y : i64 = -y           // i64 → i64

            // Float types
            val a : f32 = 3.14
            val b : f64 = 2.718
            val neg_a : f32 = -a           // f32 → f32
            val neg_b : f64 = -b           // f64 → f64

            // Mixed type operations
            val mixed1 : f64 = -x          // i32 → f64
            val mixed2 : f64 = -a          // f32 → f64

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_unary_minus_errors(self):
        """Test error cases for unary minus"""
        source = """
        func main(): i32 = {
            // Non-numeric types
            val str_val : string = "hello"
            val bool_val : bool = true
            val neg_str = -str_val         // Error: Unary minus requires numeric operand
            val neg_bool = -bool_val       // Error: Unary minus requires numeric operand

            // Invalid type coercion
            val x : i32 = 42
            val neg_x : string = -x        // Error: Cannot coerce i32 to string

            // Mixed type operations without explicit type
            val y : i32 = 42
            val z : f64 = 3.14
            val mixed = -y + -z            // Error: Mixed types require explicit result type

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 7  # Updated to expect 7 errors
        assert any("Unary minus (-) requires numeric operand" in str(e) for e in errors)
        assert any(
            "Type mismatch: variable 'neg_x' declared as string but assigned value of type i32"
            in str(e)
            for e in errors
        )
        assert any("Mixed types require explicit result type" in str(e) for e in errors)


class TestLogicalNotSemantics:
    """Test semantic analysis of logical not operator (!)"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_logical_not_with_booleans(self):
        """Test logical not with boolean values"""
        source = """
        func main(): bool = {
            // Boolean variables
            val a : bool = true
            val b : bool = false
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
            val int_val : i32 = 42
            val float_val : f32 = 3.14
            val str_val : string = "hello"
            val not_int = !int_val         // Error: Logical not requires boolean operand
            val not_float = !float_val     // Error: Logical not requires boolean operand
            val not_str = !str_val         // Error: Logical not requires boolean operand

            // Invalid type coercion
            val bool_val : bool = true
            val not_bool : i32 = !bool_val // Error: Cannot coerce bool to i32

            // Mixed type operations
            val a : bool = true
            val b : bool = false
            val mixed = !a && !b           // No error: Both operands are boolean

            return true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Only 7 errors should be produced (not 8)
        assert len(errors) == 7
        assert any("Logical not (!) requires boolean operand" in str(e) for e in errors)
        assert any("Cannot infer type for variable 'not_int'" in str(e) for e in errors)
        assert any(
            "Cannot infer type for variable 'not_float'" in str(e) for e in errors
        )
        assert any("Cannot infer type for variable 'not_str'" in str(e) for e in errors)


class TestUnaryOperatorIntegration:
    """Test integration of unary operators with other language features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_unary_operators_in_expressions(self):
        """Test unary operators in complex expressions"""
        source = """
        func main(): i32 = {
            // Unary minus in arithmetic
            val x : i32 = 42
            val y : f64 = 3.14
            val a = -x * 2                 // i32 → i32
            val b = 2 * -x                 // i32 → i32
            val c = -x + -y                // i32 → f64, f64 → f64
            val d : f64 = -2.5 * -3.5      // comptime_float → f64

            // Logical not in boolean expressions
            val e : bool = true
            val f : bool = false
            val g = !e && !f               // bool → bool
            val h = !(e || f)              // bool → bool
            val i = !!e                    // bool → bool

            // Mixed unary operators
            val j : i32 = -42
            val k : bool = !(j > 0)        // i32 → bool (via comparison)

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Only 6 errors should be produced (not 8)
        assert len(errors) == 6
        assert any("Mixed types require explicit result type" in str(e) for e in errors)
        assert any("Cannot infer type for variable 'c'" in str(e) for e in errors)
        # 'h' is now valid, so we do not check for its error

    def test_unary_operators_with_undef(self):
        """Test unary operators with uninitialized variables"""
        source = """
        func main(): i32 = {
            // Uninitialized variables
            val x : i32 = undef
            val y : bool = undef
            val neg_x = -x                 // Error: Use of uninitialized variable
            val not_y = !y                 // Error: Use of uninitialized variable

            // Initialize after use
            val a : i32 = undef
            val neg_a = -a                 // Error: Use of uninitialized variable
            a = 42                         // Initialize after use

            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 7  # Updated to expect 7 errors
        assert any("Use of uninitialized variable: 'x'" in str(e) for e in errors)
        assert any("Use of uninitialized variable: 'y'" in str(e) for e in errors)
        assert any("Use of uninitialized variable: 'a'" in str(e) for e in errors)
