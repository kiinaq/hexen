"""
Test suite for binary operations in Hexen

Tests binary operations with focus on:
- Comptime type operations and adaptation
- Division operators (/ vs \)
- Mixed type operations requiring context
- Logical operations (&&, ||)
- Comparison operations (==, !=, <, >, <=, >=)
- Error conditions and edge cases
- Integration with type system

This file focuses on PURE BINARY OPERATIONS:
- Operator behavior and precedence
- Type resolution and context requirements
- Comptime type preservation and adaptation
- Error detection for invalid operations

ASSIGNMENT CONTEXT is covered in test_assignment.py.
PRECISION LOSS scenarios are covered in test_precision_loss.py.
MUTABILITY semantics are covered in test_mutability.py.

See TYPE_SYSTEM.md and BINARY_OPS.md for detailed specifications.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestComptimeBinaryOperations:
    """Test binary operations with comptime types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_int_operations(self):
        """Test operations between comptime_int values"""
        source = """
        func test() : i32 = {
            // Basic arithmetic with comptime_int
            val add = 42 + 100          // comptime_int + comptime_int -> comptime_int
            val sub = 100 - 42          // comptime_int - comptime_int -> comptime_int
            val mul = 10 * 20           // comptime_int * comptime_int -> comptime_int
            val idiv = 100 \ 3          // comptime_int \ comptime_int -> comptime_int
            
            // Integer division with explicit type
            val explicit_idiv:i64 = 100 \ 3  // comptime_int \ comptime_int -> i64
            
            // Float division requires explicit type
            val explicit_fdiv:f64 = 100 / 3  // comptime_int / comptime_int -> f64
            
            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_float_operations(self):
        """Test operations between comptime_float values"""
        source = """
        func test() : f64 = {
            // Float operations require explicit type
            val add:f64 = 3.14 + 2.71     // comptime_float + comptime_float -> f64
            val sub:f64 = 3.14 - 2.71     // comptime_float - comptime_float -> f64
            val mul:f64 = 3.14 * 2.71     // comptime_float * comptime_float -> f64
            val div:f64 = 3.14 / 2.71     // comptime_float / comptime_float -> f64
            
            // Can use f32 for reduced precision
            val single:f32 = 3.14 + 2.71  // comptime_float + comptime_float -> f32
            
            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_comptime_operations(self):
        """Test operations between mixed comptime types"""
        source = """
        func test() : f64 = {
            // Mixed comptime types require explicit result type
            val add:f64 = 42 + 3.14       // comptime_int + comptime_float -> f64
            val sub:f64 = 42 - 3.14       // comptime_int - comptime_float -> f64
            val mul:f64 = 42 * 3.14       // comptime_int * comptime_float -> f64
            val div:f64 = 42 / 3.14       // comptime_int / comptime_float -> f64
            
            // Can use f32 for reduced precision
            val single:f32 = 42 + 3.14    // comptime_int + comptime_float -> f32
            
            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestDivisionOperators:
    """Test float vs integer division operators"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_float_division(self):
        """Test float division operator (/)"""
        source = """
        func test() : f64 = {
            // Float division always requires explicit type
            val div1:f64 = 10 / 3         // comptime_int / comptime_int -> f64 (3.333...)
            val div2:f64 = 7 / 2          // comptime_int / comptime_int -> f64 (3.5)
            val div3:f32 = 22 / 7         // comptime_int / comptime_int -> f32 (3.142857...)

            // Float division with float literals
            val div4:f64 = 10.5 / 2.1     // comptime_float / comptime_float -> f64

            return div1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_integer_division(self):
        """Test integer division operator (\)"""
        source = """
        func test() : i32 = {
            // Integer division preserves comptime_int
            val div1 = 10 \ 3               // comptime_int \ comptime_int -> comptime_int
            val div2 = 7 \ 2                // comptime_int \ comptime_int -> comptime_int
            
            // Integer division with explicit type
            val div3:i64 = 22 \ 7         // comptime_int \ comptime_int -> i64
            
            // Integer division with concrete types
            val a:i32 = 10
            val b:i32 = 3
            val div4 = a \ b                // i32 \ i32 -> comptime_int
            
            return div1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestMixedTypeOperations:
    """Test operations between mixed concrete types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mixed_integer_types(self):
        """Test operations between different integer types"""
        source = """
        func test() : i64 = {
            val a:i32 = 10
            val b:i64 = 20
            
            // Mixed integer types require explicit result type
            val add:i64 = a + b           // i32 + i64 -> comptime_int (adapts to i64)
            val sub:i64 = a - b           // i32 - i64 -> comptime_int (adapts to i64)
            val mul:i64 = a * b           // i32 * i64 -> comptime_int (adapts to i64)
            val idiv:i64 = a \ b          // i32 \ i64 -> comptime_int (adapts to i64)
            
            // Can use f64 for full precision
            val fdiv:f64 = a / b          // i32 / i64 -> f64 (float division)
            
            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_float_types(self):
        """Test operations between different float types with explicit conversions"""
        source = """
        func test() : f64 = {
            val a:f32 = 3.14
            val b:f64 = 2.71

            // Mixed float types require explicit conversions per BINARY_OPS.md Pattern 4
            val add:f64 = (a:f64) + b     // f32 → f64 + f64 (explicit conversion)
            val sub:f64 = (a:f64) - b     // f32 → f64 - f64 (explicit conversion)
            val mul:f64 = (a:f64) * b     // f32 → f64 * f64 (explicit conversion)
            val div:f64 = (a:f64) / b     // f32 → f64 / f64 (explicit conversion)

            // Can use f32 for reduced precision with explicit conversions
            val single:f32 = a + (b:f32)  // f32 + f64 → f32 (explicit conversion)

            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_numeric_types(self):
        """Test operations between mixed numeric types"""
        source = """
        func test() : f64 = {
            val a:i32 = 10
            val b:f64 = 3.14

            // Mixed numeric types require explicit conversions per BINARY_OPS.md Pattern 4
            val add:f64 = (a:f64) + b     // i32 → f64 + f64 (explicit conversion)
            val sub:f64 = (a:f64) - b     // i32 → f64 - f64 (explicit conversion)
            val mul:f64 = (a:f64) * b     // i32 → f64 * f64 (explicit conversion)
            val div:f64 = (a:f64) / b     // i32 → f64 / f64 (explicit conversion)

            // Can use f32 for reduced precision with explicit conversions
            val single:f32 = a + (b:f32)  // i32 + f64 → f32 (explicit conversion)

            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


# Assignment context testing moved to test_assignment.py
# This file focuses on pure binary operations without assignment overlap


class TestBinaryOperationErrors:
    """Test error cases for binary operations"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_missing_type_annotation(self):
        """Test missing type annotations for operations requiring them"""
        source = """
        func test() : void = {
            // Float division requires explicit type
            val div1 = 10 / 3              // Error: Float division requires explicit result type

            // Mixed comptime types require explicit type
            val add1 = 42 + 3.14           // Error: Mixed comptime types require explicit result type

            // Mixed concrete types require explicit type
            val a:i32 = 10
            val b:i64 = 20
            val add2 = a + b               // Error: Mixed concrete types require explicit result type

            // Float operations require explicit type
            val add3 = 3.14 + 2.71         // Error: comptime_float operations require explicit result type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        print("[DEBUG] Errors:", [e.message for e in errors])
        assert len(errors) == 4, "Expected 4 errors (granular errors only)"
        assert any(
            "Float division requires explicit result type" in e.message for e in errors
        ), "Missing granular error for div1"
        assert any("Mixed-type operation" in e.message for e in errors), (
            "Missing granular error for add1"
        )
        assert any("Mixed-type operation" in e.message for e in errors), (
            "Missing granular error for add2"
        )
        assert any(
            "comptime_float operations require explicit result type" in e.message
            for e in errors
        ), "Missing granular error for add3"

    def test_invalid_integer_division(self):
        """Test invalid integer division operations"""
        source = """
        func test() : void = {
            // Integer division requires integer operands
            val div1 = 10.5 \ 2.1          // Error: Integer division requires integer operands
            val div2 = 3.14 \ 42           // Error: Integer division requires integer operands

            // Mixed types with integer division
            val a:i32 = 10
            val b:f64 = 3.14
            val div3 = a \ b               // Error: Integer division requires integer operands
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        print("[DEBUG] Errors:", [e.message for e in errors])
        assert len(errors) == 3  # 3 integer division errors only

        # Check for integer division errors
        division_errors = [e for e in errors if "Integer division" in e.message]
        assert len(division_errors) == 3
        assert all(
            "Integer division (\) cannot be used with float operands" in e.message
            for e in division_errors
        )

        # Type inference errors are not generated for these cases


class TestLogicalOperations:
    """Test logical operations (&&, ||)"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_basic_logical_operations(self):
        """Test basic logical operations with boolean operands"""
        source = """
        func test():bool = {
            // Basic logical operations
            val and_op = true && false
            val or_op = true || false
            val complex = (true && false) || (false && true)
            val nested = true && (false || true) && false
            
            // Logical operations with boolean variables
            val a:bool = true
            val b:bool = false
            val var_and = a && b
            val var_or = a || b
            val var_complex = (a && b) || (!a && b)
            
            return and_op
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_logical_operation_errors(self):
        """Test error cases for logical operations"""
        source = """
        func test() : void = {
            // Non-boolean operands
            val a:i32 = 10
            val b:f64 = 3.14
            val c:string = "hello"
    
            // Invalid logical operations
            val error1 = a && true          // Error: Logical operator requires boolean operands
            val error2 = true && b          // Error: Logical operator requires boolean operands
            val error3 = c || false         // Error: Logical operator requires boolean operands
            val error4 = true && 42         // Error: Logical operator requires boolean operands
            val error5 = 3.14 || false      // Error: Logical operator requires boolean operands
    
            // Mixed type logical operations
            val error6 = true && 1          // Error: Logical operator requires boolean operands
            val error7 = false || "true"    // Error: Logical operator requires boolean operands
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        print("[DEBUG] Errors:", [e.message for e in errors])

        # Check for logical operation errors
        logical_errors = [e for e in errors if "Logical operator" in e.message]
        assert len(logical_errors) == 7, "Expected 7 logical operation errors"
        assert all(
            "Logical operator" in e.message
            and "requires boolean operands" in e.message
            and "got" in e.message
            for e in logical_errors
        ), "Missing or incorrect error message for logical operations"

        # Type inference errors are not generated for these cases

    def test_logical_operation_precedence(self):
        """Test operator precedence in logical operations"""
        source = """
        func test():bool = {
            // Test AND precedence over OR
            val a:bool = true
            val b:bool = false
            val c:bool = true
            
            // a && b || c should be (a && b) || c
            val prec1 = a && b || c
            
            // a || b && c should be a || (b && c)
            val prec2 = a || b && c
            
            // Complex precedence
            val prec3 = !a && b || c && !b
            
            return prec1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_logical_operation_with_unary_not(self):
        """Test logical operations with unary NOT operator"""
        source = """
        func test():bool = {
            val a:bool = true
            val b:bool = false
            
            // Logical operations with NOT
            val not_and = !a && b
            val not_or = !a || b
            val complex_not = !(a && b) || !(a || b)
            val nested_not = !(!a && b) || !(a && !b)
            
            return not_and
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComparisonOperations:
    """Test comparison operations semantic analysis"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_numeric_comparisons(self):
        """Test numeric type comparisons"""
        source = """
        func test() : void = {
            // Same type comparisons
            val a:i32 = 10
            val b:i32 = 20
            val c:f64 = 3.14
            val d:f64 = 2.71
            
            val result1:bool = a < b              // i32 < i32 -> bool
            val result2:bool = c > d              // f64 > f64 -> bool
            val result3:bool = a <= b             // i32 <= i32 -> bool
            val result4:bool = c >= d             // f64 >= f64 -> bool
            
            // Mixed numeric type comparisons
            val result5:bool = a < c              // i32 < f64 -> bool (with warning)
            val result6:bool = c > a              // f64 > i32 -> bool (with warning)
            
            // Comptime numeric comparisons
            val result7:bool = 42 < 100           // comptime_int < comptime_int -> bool
            val result8:bool = 3.14 > 2.71        // comptime_float > comptime_float -> bool
            val result9:bool = 42 < 3.14          // comptime_int < comptime_float -> bool (with warning)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should have warnings about mixed numeric type comparisons
        assert len(errors) == 3, (
            "Expected 3 warnings about mixed numeric type comparisons"
        )
        assert all(
            "Comparison between different numeric types may have unexpected results"
            in str(e)
            for e in errors
        )

    def test_equality_comparisons(self):
        """Test equality operator comparisons"""
        source = """
        func test() : void = {
            // Same type equality
            val a:i32 = 10
            val b:i32 = 20
            val c:string = "hello"
            val d:string = "world"
            val e:bool = true
            val f:bool = false
            
            val result1:bool = a == b             // i32 == i32 -> bool
            val result2:bool = c == d             // string == string -> bool
            val result3:bool = e == f             // bool == bool -> bool
            
            // Mixed type equality (should error)
            val result4:bool = a == c             // Error: i32 == string
            val result5:bool = c == e             // Error: string == bool
            val result6:bool = e == a             // Error: bool == i32
            
            // Comptime equality
            val result7:bool = 42 == 42           // comptime_int == comptime_int -> bool
            val result8:bool = "hello" == "world" // string == string -> bool
            val result9:bool = true == false      // bool == bool -> bool
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3, "Expected 3 errors for invalid type comparisons"
        assert all("Cannot compare different types with ==" in str(e) for e in errors)

    def test_relational_operator_restrictions(self):
        """Test restrictions on relational operators"""
        source = """
        func test() : void = {
            val a:string = "hello"
            val b:string = "world"
            val c:bool = true
            val d:bool = false
            
            // Relational operators only work with numeric types
            val result1:bool = a < b              // Error: string < string
            val result2:bool = c > d              // Error: bool > bool
            val result3:bool = a <= b             // Error: string <= string
            val result4:bool = c >= d             // Error: bool >= bool
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 4, (
            "Expected 4 errors for invalid relational operator usage"
        )
        assert all(
            "Relational operator" in str(e)
            and "can only be used with numeric types" in str(e)
            for e in errors
        )

    def test_comparison_target_type(self):
        """Test comparison operations with target type context"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            
            // Comparison operations always produce bool
            val result1:i32 = a < b              // Error: cannot assign bool to i32
            val result2:string = a == b          // Error: cannot assign bool to string
            val result3:f64 = a > b              // Error: cannot assign bool to f64
            
            // Valid boolean assignments
            val result4:bool = a < b             // i32 < i32 -> bool
            val result5:bool = a == b            // i32 == i32 -> bool
            val result6:bool = a > b             // i32 > i32 -> bool
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3, "Expected 3 errors for invalid target types"
        assert all(
            "Comparison operation" in str(e)
            and "always produces boolean result" in str(e)
            for e in errors
        )
