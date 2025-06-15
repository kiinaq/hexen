"""
Tests for binary operations semantic analysis in Hexen

These tests validate that binary operations follow the type system rules:
- Comptime type preservation and adaptation
- Context-guided resolution
- Division operators (float vs integer)
- Mixed type operations
- Assignment context
- Error cases

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
            val explicit_idiv : i64 = 100 \ 3  // comptime_int \ comptime_int -> i64
            
            // Float division requires explicit type
            val explicit_fdiv : f64 = 100 / 3  // comptime_int / comptime_int -> f64
            
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
            val add : f64 = 3.14 + 2.71     // comptime_float + comptime_float -> f64
            val sub : f64 = 3.14 - 2.71     // comptime_float - comptime_float -> f64
            val mul : f64 = 3.14 * 2.71     // comptime_float * comptime_float -> f64
            val div : f64 = 3.14 / 2.71     // comptime_float / comptime_float -> f64
            
            // Can use f32 for reduced precision
            val single : f32 = 3.14 + 2.71  // comptime_float + comptime_float -> f32
            
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
            val add : f64 = 42 + 3.14       // comptime_int + comptime_float -> f64
            val sub : f64 = 42 - 3.14       // comptime_int - comptime_float -> f64
            val mul : f64 = 42 * 3.14       // comptime_int * comptime_float -> f64
            val div : f64 = 42 / 3.14       // comptime_int / comptime_float -> f64
            
            // Can use f32 for reduced precision
            val single : f32 = 42 + 3.14    // comptime_int + comptime_float -> f32
            
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
            val div1 : f64 = 10 / 3         // comptime_int / comptime_int -> f64 (3.333...)
            val div2 : f64 = 7 / 2          // comptime_int / comptime_int -> f64 (3.5)
            val div3 : f32 = 22 / 7         // comptime_int / comptime_int -> f32 (3.142857...)

            // Float division with float literals
            val div4 : f64 = 10.5 / 2.1     // comptime_float / comptime_float -> f64

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
            val div3 : i64 = 22 \ 7         // comptime_int \ comptime_int -> i64
            
            // Integer division with concrete types
            val a : i32 = 10
            val b : i32 = 3
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
            val a : i32 = 10
            val b : i64 = 20
            
            // Mixed integer types require explicit result type
            val add : i64 = a + b           // i32 + i64 -> comptime_int (adapts to i64)
            val sub : i64 = a - b           // i32 - i64 -> comptime_int (adapts to i64)
            val mul : i64 = a * b           // i32 * i64 -> comptime_int (adapts to i64)
            val idiv : i64 = a \ b          // i32 \ i64 -> comptime_int (adapts to i64)
            
            // Can use f64 for full precision
            val fdiv : f64 = a / b          // i32 / i64 -> f64 (float division)
            
            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_float_types(self):
        """Test operations between different float types"""
        source = """
        func test() : f64 = {
            val a : f32 = 3.14
            val b : f64 = 2.71

            // Mixed float types require explicit result type
            val add : f64 = a + b           // f32 + f64 -> comptime_float (adapts to f64)
            val sub : f64 = a - b           // f32 - f64 -> comptime_float (adapts to f64)
            val mul : f64 = a * b           // f32 * f64 -> comptime_float (adapts to f64)
            val div : f64 = a / b           // f32 / f64 -> comptime_float (adapts to f64)

            // Can use f32 for reduced precision
            val single : f32 = a + b        // f32 + f64 -> f32 (explicit precision loss)

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
            val a : i32 = 10
            val b : f64 = 3.14

            // Mixed numeric types require explicit result type
            val add : f64 = a + b           // i32 + f64 -> comptime_float (adapts to f64)
            val sub : f64 = a - b           // i32 - f64 -> comptime_float (adapts to f64)
            val mul : f64 = a * b           // i32 * f64 -> comptime_float (adapts to f64)
            val div : f64 = a / b           // i32 / f64 -> comptime_float (adapts to f64)

            // Can use f32 for reduced precision
            val single : f32 = a + b        // i32 + f64 -> f32 (explicit precision loss)

            return add
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestAssignmentContext:
    """Test binary operations in assignment context"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_with_comptime_types(self):
        """Test assignment with comptime types"""
        source = """
        func test() : void = {
            // Comptime types adapt to target type
            mut i32_var : i32 = 0
            mut i64_var : i64 = 0
            mut f32_var : f32 = 0.0
            mut f64_var : f64 = 0.0
            
            // Safe assignments - comptime types adapt to context
            i32_var = 42 + 100             // comptime_int + comptime_int -> comptime_int (adapts to i32)
            i64_var = 42 + 100             // comptime_int + comptime_int -> comptime_int (adapts to i64)
            f32_var = 3.14 + 2.71          // comptime_float + comptime_float -> comptime_float (adapts to f32)
            f64_var = 3.14 + 2.71          // comptime_float + comptime_float -> comptime_float (adapts to f64)
            
            // Mixed comptime types adapt to target type
            f64_var = 42 + 3.14            // comptime_int + comptime_float -> comptime_float (adapts to f64)
            f32_var = 42 + 3.14            // comptime_int + comptime_float -> comptime_float (adapts to f32)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_with_mixed_types(self):
        """Test assignment with mixed concrete types"""
        source = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            val c : f32 = 3.14
            val d : f64 = 2.71

            mut i32_var : i32 = 0
            mut i64_var : i64 = 0
            mut f32_var : f32 = 0.0
            mut f64_var : f64 = 0.0

            // Mixed types require explicit type annotation for potential precision loss
            i32_var = (a + b) : i32          // i32 + i64 -> comptime_int (explicit truncation)
            i64_var = a + b                  // i32 + i64 -> comptime_int (adapts to i64)
            f32_var = (a + c) : f32          // i32 + f32 -> comptime_float (explicit precision loss)
            f64_var = a + d                  // i32 + f64 -> comptime_float (adapts to f64)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    # def test_precision_loss_without_annotation(self):
    #     """Test precision loss without explicit type annotation"""
    #     source = """
    #     func test() : void = {
    #         val a : i64 = 0xFFFFFFFF
    #         val b : f64 = 3.14159265359
    #
    #         mut i32_var : i32 = 0
    #         mut f32_var : f32 = 0.0
    #
    #         // Potential truncation without type annotation
    #         i32_var = a                    // Error: Potential truncation, add ': i32'
    #         i32_var = (a + b) : i32        // Mixed types with potential truncation, explicit type
    #
    #         // Potential precision loss without type annotation
    #         f32_var = b                    // Error: Potential precision loss, add ': f32'
    #         f32_var = (a + b) : f32        // Mixed types with potential precision loss, explicit type
    #     }
    #     """
    #     ast = self.parser.parse(source)
    #     errors = self.analyzer.analyze(ast)
    #     assert len(errors) == 2
    #     assert any("Potential truncation" in e.message for e in errors)
    #     assert any("Potential precision loss" in e.message for e in errors)


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
            val a : i32 = 10
            val b : i64 = 20
            val add2 = a + b               // Error: Mixed concrete types require explicit result type

            // Float operations require explicit type
            val add3 = 3.14 + 2.71         // Error: comptime_float operations require explicit result type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        print("[DEBUG] Errors:", [e.message for e in errors])
        assert len(errors) == 8, "Expected 8 errors (4 granular + 4 infer errors)"
        assert any(
            "Float division requires explicit result type" in e.message for e in errors
        ), "Missing granular error for div1"
        assert any(
            "Mixed comptime types require explicit result type" in e.message
            for e in errors
        ), "Missing granular error for add1"
        assert any(
            "Mixed concrete types require explicit result type" in e.message
            for e in errors
        ), "Missing granular error for add2"
        assert any(
            "comptime_float operations require explicit result type" in e.message
            for e in errors
        ), "Missing granular error for add3"
        assert any(
            "Cannot infer type for variable 'div1'" in e.message for e in errors
        ), "Missing infer error for div1"
        assert any(
            "Cannot infer type for variable 'add1'" in e.message for e in errors
        ), "Missing infer error for add1"
        assert any(
            "Cannot infer type for variable 'add2'" in e.message for e in errors
        ), "Missing infer error for add2"
        assert any(
            "Cannot infer type for variable 'add3'" in e.message for e in errors
        ), "Missing infer error for add3"

    def test_invalid_integer_division(self):
        """Test invalid integer division operations"""
        source = """
        func test() : void = {
            // Integer division requires integer operands
            val div1 = 10.5 \ 2.1          // Error: Integer division requires integer operands
            val div2 = 3.14 \ 42           // Error: Integer division requires integer operands

            // Mixed types with integer division
            val a : i32 = 10
            val b : f64 = 3.14
            val div3 = a \ b               // Error: Integer division requires integer operands
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        print("[DEBUG] Errors:", [e.message for e in errors])
        assert len(errors) == 6  # 3 integer division errors + 3 type inference errors

        # Check for integer division errors
        division_errors = [e for e in errors if "Integer division" in e.message]
        assert len(division_errors) == 3
        assert all(
            "Integer division (\) cannot be used with float operands" in e.message
            for e in division_errors
        )

        # Check for type inference errors
        type_errors = [
            e for e in errors if "Cannot infer type for variable" in e.message
        ]
        assert len(type_errors) == 3
        assert all(
            any(
                f"Cannot infer type for variable 'div{i}'" in e.message
                for i in range(1, 4)
            )
            for e in type_errors
        )

    # def test_precision_loss_without_annotation(self):
    #     """Test precision loss without explicit type annotation"""
    #     source = """
    #     func test() : void = {
    #         val a : i64 = 0xFFFFFFFF + 1
    #         val b : f64 = 3.14159265359
    #
    #         mut i32_var : i32 = 0
    #         mut f32_var : f32 = 0.0
    #
    #         // Potential truncation without type annotation
    #         i32_var = a                    // Error: Potential truncation, add ': i32'
    #         i32_var = a + b                // Error: Mixed types with potential truncation, add ': i32'
    #
    #         // Potential precision loss without type annotation
    #         f32_var = b                    // Error: Potential precision loss, add ': f32'
    #         f32_var = a + b                // Error: Mixed types with potential precision loss, add ': f32'
    #     }
    #     """
    #     ast = self.parser.parse(source)
    #     errors = self.analyzer.analyze(ast)
    #     assert len(errors) == 4
    #     assert any("Potential truncation" in e.message for e in errors)
    #     assert any("Potential precision loss" in e.message for e in errors)
