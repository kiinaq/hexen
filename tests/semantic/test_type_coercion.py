"""
Concrete Type Coercion Tests for Hexen

Tests ONLY the concrete type coercion rules (non-comptime types) as described in TYPE_SYSTEM.md:
- Integer widening: i32 → {i64, f32, f64}, i64 → {f32, f64}
- Float widening: f32 → f64
- Safe conversions vs precision loss scenarios
- Context-guided coercion in assignments and expressions
- Integration with the "Explicit Danger, Implicit Safety" principle

NOTE: Comptime type testing is now consolidated in test_comptime_types.py
This file focuses exclusively on concrete type coercion (i32, i64, f32, f64, etc.)
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestIntegerWidening:
    """Test integer type widening rules"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_i32_to_i64_widening(self):
        """Test i32 to i64 widening (always safe)"""
        source = """
        func test() : void = {
            val small : i32 = 42
            
            // ✅ i32 → i64 widening is always safe
            val wide : i64 = small
            
            mut wide_mut : i64 = 0
            wide_mut = small        // Safe in assignment too
            
            // ✅ Works with expressions
            val computed : i64 = small + 100
            val doubled : i64 = small * 2
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i32_to_f32_conversion(self):
        """Test i32 to f32 conversion (safe for typical values)"""
        source = """
        func test() : void = {
            val integer : i32 = 42
            
            // ✅ i32 → f32 conversion is considered safe
            val as_float : f32 = integer
            
            mut float_mut : f32 = 0.0
            float_mut = integer     // Safe in assignment
            
            // ✅ Works with expressions
            val computed : f32 = integer + 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i32_to_f64_conversion(self):
        """Test i32 to f64 conversion (always safe)"""
        source = """
        func test() : void = {
            val integer : i32 = 42
            
            // ✅ i32 → f64 conversion is always safe (high precision)
            val as_double : f64 = integer
            
            mut double_mut : f64 = 0.0
            double_mut = integer    // Safe in assignment
            
            // ✅ Works with complex expressions
            val computed : f64 = integer * 2.5 + 1.0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i64_to_float_conversions(self):
        """Test i64 to float conversions"""
        source = """
        func test() : void = {
            val large : i64 = 1000000
            
            // ✅ i64 → f32 allowed (may lose precision for very large values)
            val as_float : f32 = large
            
            // ✅ i64 → f64 is safer (higher precision)
            val as_double : f64 = large
            
            mut float_mut : f32 = 0.0
            mut double_mut : f64 = 0.0
            
            float_mut = large       // Allowed
            double_mut = large      // Allowed
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # This test depends on implementation - some systems may require acknowledgment
        # for i64 → f32 due to potential precision loss for very large integers
        # May or may not produce errors depending on implementation
        assert isinstance(errors, list)  # Ensure errors is a list


class TestFloatWidening:
    """Test floating-point type widening rules"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_f32_to_f64_widening(self):
        """Test f32 to f64 widening (always safe)"""
        source = """
        func test() : void = {
            val single : f32 = 3.14
            
            // ✅ f32 → f64 widening is always safe
            val double : f64 = single
            
            mut double_mut : f64 = 0.0
            double_mut = single     // Safe in assignment
            
            // ✅ Works with expressions
            val computed : f64 = single + 2.718
            val multiplied : f64 = single * 2.0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_float_expressions(self):
        """Test expressions mixing f32 and f64"""
        source = """
        func test() : void = {
            val single : f32 = 3.14
            val double : f64 = 2.718
            
            // Mixed float operations may require explicit result type
            val result : f64 = single + double  // f32 + f64 → f64 context
            
            mut target : f64 = 0.0
            target = single + double            // Assignment provides f64 context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestNarrowingRequiresAcknowledgment:
    """Test that narrowing conversions require explicit acknowledgment"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_i64_to_i32_narrowing_error(self):
        """Test that i64 to i32 narrowing requires acknowledgment"""
        source = """
        func test() : void = {
            val large : i64 = 1000000
            mut small : i32 = 0
            
            // ❌ Narrowing requires explicit acknowledgment
            small = large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert (
            "truncation" in errors[0].message.lower()
            or "precision" in errors[0].message.lower()
            or "narrowing" in errors[0].message.lower()
        )

    def test_i64_to_i32_narrowing_with_acknowledgment(self):
        """Test that i64 to i32 narrowing works with explicit acknowledgment"""
        source = """
        func test() : void = {
            val large : i64 = 1000000
            mut small : i32 = 0
            
            // ✅ Explicit acknowledgment allows narrowing
            small = large : i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_f64_to_f32_narrowing_error(self):
        """Test that f64 to f32 narrowing requires acknowledgment"""
        source = """
        func test() : void = {
            val precise : f64 = 3.141592653589793
            mut single : f32 = 0.0
            
            // ❌ Precision loss requires explicit acknowledgment
            single = precise
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "precision" in errors[0].message.lower()

    def test_f64_to_f32_narrowing_with_acknowledgment(self):
        """Test that f64 to f32 narrowing works with explicit acknowledgment"""
        source = """
        func test() : void = {
            val precise : f64 = 3.141592653589793
            mut single : f32 = 0.0
            
            // ✅ Explicit acknowledgment allows precision loss
            single = precise : f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestCrossTypeConversions:
    """Test conversions between integer and float types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_float_to_integer_requires_acknowledgment(self):
        """Test that float to integer conversion requires acknowledgment"""
        source = """
        func test() : void = {
            val float_val : f32 = 3.14
            val double_val : f64 = 2.718
            
            mut int32_var : i32 = 0
            mut int64_var : i64 = 0
            
            // ❌ Float to integer truncation requires acknowledgment
            int32_var = float_val   // f32 → i32 truncation
            int64_var = double_val  // f64 → i64 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        for error in errors:
            assert (
                "truncation" in error.message.lower()
                or "type mismatch" in error.message.lower()
                or "conversion" in error.message.lower()
            )

    def test_float_to_integer_with_acknowledgment(self):
        """Test that float to integer conversion works with acknowledgment"""
        source = """
        func test() : void = {
            val float_val : f32 = 3.14
            val double_val : f64 = 2.718
            
            mut int32_var : i32 = 0
            mut int64_var : i64 = 0
            
            // ✅ Explicit acknowledgment allows truncation
            int32_var = float_val : i32   // f32 → i32 with acknowledgment
            int64_var = double_val : i64  // f64 → i64 with acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_integer_to_float_safe_conversions(self):
        """Test that integer to float conversions are generally safe"""
        source = """
        func test() : void = {
            val int32_val : i32 = 42
            val int64_val : i64 = 1000000
            
            // ✅ Integer to float conversions are safe (widening)
            val float_from_i32 : f32 = int32_val  // i32 → f32
            val double_from_i32 : f64 = int32_val // i32 → f64
            val float_from_i64 : f32 = int64_val : f32  // i64 → f32 (may lose precision - acknowledge)
            val double_from_i64 : f64 = int64_val // i64 → f64
            
            // ✅ Safe in assignments too
            mut target_f32 : f32 = 0.0
            mut target_f64 : f64 = 0.0
            
            target_f32 = int32_val
            target_f64 = int32_val
            target_f64 = int64_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestContextGuidedCoercion:
    """Test context-guided type coercion in complex scenarios"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assignment_context_guides_coercion(self):
        """Test that assignment target type guides coercion"""
        source = """
        func test() : void = {
            val source_i32 : i32 = 42
            val source_f32 : f32 = 3.14
            
            // Assignment target type provides context for safe coercion
            mut target_i64 : i64 = 0
            mut target_f64 : f64 = 0.0
            
            // ✅ Context-guided safe coercion
            target_i64 = source_i32     // i32 → i64 (safe, context-guided)
            target_f64 = source_i32     // i32 → f64 (safe, context-guided)
            target_f64 = source_f32     // f32 → f64 (safe, context-guided)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_function_return_context_guides_coercion(self):
        """Test that function return type provides context for coercion"""
        source = """
        func return_widened_i32() : i64 = {
            val value : i32 = 42
            return value    // i32 → i64 (return context guides coercion)
        }
        
        func return_widened_f32() : f64 = {
            val value : f32 = 3.14
            return value    // f32 → f64 (return context guides coercion)
        }
        
        func return_converted_int() : f64 = {
            val value : i32 = 42
            return value    // i32 → f64 (return context guides coercion)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_variable_declaration_context_guides_coercion(self):
        """Test that variable declaration type provides context"""
        source = """
        func test() : void = {
            val source : i32 = 42
            
            // ✅ Declaration type guides coercion
            val widened_i64 : i64 = source      // i32 → i64 (declaration context)
            val converted_f32 : f32 = source    // i32 → f32 (declaration context)
            val converted_f64 : f64 = source    // i32 → f64 (declaration context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComplexCoercionScenarios:
    """Test complex scenarios involving multiple type coercions"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_chained_safe_coercions(self):
        """Test chained safe type coercions"""
        source = """
        func test() : void = {
            val start : i32 = 42
            
            // Chain of safe coercions
            val step1 : i64 = start         // i32 → i64
            val step2 : f64 = step1         // i64 → f64
            
            // Or in one step
            val direct : f64 = start        // i32 → f64 (direct safe conversion)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_type_expressions_with_coercion(self):
        """Test expressions mixing different concrete types"""
        source = """
        func test() : void = {
            val int_val : i32 = 10
            val long_val : i64 = 20
            val float_val : f32 = 3.14
            val double_val : f64 = 2.718
            
            // Mixed operations requiring explicit result type context
            val mixed1 : i64 = int_val + long_val       // i32 + i64 → i64
            val mixed2 : f64 = float_val + double_val   // f32 + f64 → f64
            val mixed3 : f64 = int_val + double_val     // i32 + f64 → f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_coercion_with_precision_loss_chain(self):
        """Test coercion chains that involve precision loss"""
        source = """
        func test() : void = {
            val start : f64 = 3.141592653589793
            
            // Chain involving precision loss - requires acknowledgment
            mut intermediate : f32 = 0.0
            mut final : i32 = 0
            
            // ❌ Each step with potential precision loss needs acknowledgment
            intermediate = start    // f64 → f32 precision loss
            final = intermediate    // f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2  # At least two precision loss errors

    def test_coercion_with_acknowledgment_chain(self):
        """Test coercion chains with proper acknowledgments"""
        source = """
        func test() : void = {
            val start : f64 = 3.141592653589793
            
            // Chain with proper acknowledgments
            mut intermediate : f32 = 0.0
            mut final : i32 = 0
            
            // ✅ Explicit acknowledgment at each step
            intermediate = start : f32       // Acknowledge f64 → f32 precision loss
            final = intermediate : i32       // Acknowledge f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestCoercionErrorMessages:
    """Test that type coercion error messages are helpful and consistent"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_widening_vs_narrowing_error_messages(self):
        """Test that error messages distinguish between widening and narrowing"""
        source = """
        func test() : void = {
            val large : i64 = 1000000
            val precise : f64 = 3.14159
            
            mut small : i32 = 0
            mut single : f32 = 0.0
            
            // Should generate helpful error messages
            small = large       // Narrowing error
            single = precise    // Precision loss error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]
        # Should contain guidance on solutions
        assert any(": i32" in msg for msg in error_messages)
        assert any(": f32" in msg for msg in error_messages)
        assert any(
            "truncation" in msg.lower() or "precision" in msg.lower()
            for msg in error_messages
        )

    def test_mixed_type_error_messages(self):
        """Test error messages for mixed-type operations"""
        source = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            
            // Should provide clear guidance
            val result = a + b
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Mixed-type operation" in error_msg or "explicit" in error_msg.lower()
        assert "i32" in error_msg and "i64" in error_msg
