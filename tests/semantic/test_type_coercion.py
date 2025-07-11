"""
Test suite for type coercion system in Hexen

Tests the comprehensive type coercion system described in TYPE_SYSTEM.md:
- Integer widening: i32 → {i64, f32, f64}, i64 → {f32, f64}
- Float widening: f32 → f64
- Safe conversions and context-guided coercion
- Integration with assignment and return contexts

This file focuses on SAFE COERCION (widening), not precision loss scenarios.
Precision loss testing is comprehensively covered in test_precision_loss.py.
"""

from tests.semantic import StandardTestBase


class TestIntegerWidening(StandardTestBase):
    """Test safe integer widening coercions"""

    def test_i32_to_i64_widening(self):
        """Test i32 to i64 widening is always safe"""
        source = """
        func test() : void = {
            val small:i32 = 42
            
            // ✅ i32 → i64 widening is always safe
            val wide:i64 = small
            
            mut wide_mut:i64 = 0
            wide_mut = small                // Safe in reassignment too
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i32_to_f32_conversion(self):
        """Test i32 to f32 conversion"""
        source = """
        func test() : void = {
            val integer:i32 = 42
            
            // ✅ i32 → f32 conversion is safe for typical values
            val as_float:f32 = integer
            
            mut float_mut:f32 = 0.0
            float_mut = integer
            
            // Complex expressions maintain safety
            val computed:f32 = integer + 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i32_to_f64_conversion(self):
        """Test i32 to f64 conversion"""
        source = """
        func test() : void = {
            val integer:i32 = 42
            
            // ✅ i32 → f64 conversion is always safe (double precision)
            val as_double:f64 = integer
            
            mut double_mut:f64 = 0.0
            double_mut = integer
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_i64_to_float_conversions(self):
        """Test i64 to float conversions"""
        source = """
        func test() : void = {
            val large:i64 = 1000
            
            // ✅ i64 → f64 is generally safe
            val as_double:f64 = large
            
            mut target_f64:f64 = 0.0
            target_f64 = large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestFloatWidening(StandardTestBase):
    """Test safe float widening coercions"""

    def test_f32_to_f64_widening(self):
        """Test f32 to f64 widening is always safe"""
        source = """
        func test() : void = {
            val single:f32 = 3.14
            
            // ✅ f32 → f64 widening is always safe
            val double:f64 = single
            
            mut double_mut:f64 = 0.0
            double_mut = single
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_float_expressions(self):
        """Test expressions mixing f32 and f64 with explicit context"""
        source = """
        func test() : void = {
            val single:f32 = 3.14
            val double:f64 = 2.718
            
            // ✅ Mixed expressions require explicit context
            val result_f64:f64 = single + double
            val result_f32:f32 = single + double:f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestSafeConversions(StandardTestBase):
    """Test all safe type conversions that don't require explicit acknowledgment"""

    def test_comprehensive_safe_conversions(self):
        """Test all safe conversion patterns"""
        source = """
        func test() : void = {
            val small_int:i32 = 42
            val large_int:i64 = 1000
            val small_float:f32 = 3.14
            val large_float:f64 = 2.718
            
            // ✅ All safe widening conversions
            val i32_to_i64:i64 = small_int
            val i32_to_f32:f32 = small_int  
            val i32_to_f64:f64 = small_int
            val i64_to_f64:f64 = large_int
            val f32_to_f64:f64 = small_float
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_safe_conversions_in_assignments(self):
        """Test safe conversions work in assignment contexts"""
        source = """
        func test() : void = {
            val source_i32:i32 = 42
            val source_f32:f32 = 3.14
            
            // ✅ Safe conversions in assignments
            mut target_i64:i64 = 0
            mut target_f32:f32 = 0.0
            mut target_f64:f64 = 0.0
            
            target_i64 = source_i32     // i32 → i64
            target_f32 = source_i32     // i32 → f32
            target_f64 = source_i32     // i32 → f64
            target_f64 = source_f32     // f32 → f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_type_safety(self):
        """Test that comptime types safely coerce to all appropriate concrete types"""
        source = """
        func test() : void = {
            // ✅ Comptime int can safely become any numeric type
            val as_i32:i32 = 42
            val as_i64:i64 = 42
            val as_f32:f32 = 42
            val as_f64:f64 = 42
            
            // ✅ Comptime float can safely become any float type
            val float_f32:f32 = 3.14
            val float_f64:f64 = 3.14
            
            // ✅ Mixed comptime operations with context
            val mixed_result:f64 = 42 + 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestContextGuidedCoercion(StandardTestBase):
    """Test context-guided type coercion in complex scenarios"""

    def test_assignment_context_guides_coercion(self):
        """Test that assignment target type guides coercion"""
        source = """
        func test() : void = {
            val source_i32:i32 = 42
            val source_f32:f32 = 3.14
            
            // Assignment target type provides context for safe coercion
            mut target_i64:i64 = 0
            mut target_f64:f64 = 0.0
            
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
            val value:i32 = 42
            return value    // i32 → i64 (return context guides coercion)
        }
        
        func return_widened_f32() : f64 = {
            val value:f32 = 3.14
            return value    // f32 → f64 (return context guides coercion)
        }
        
        func return_converted_int() : f64 = {
            val value:i32 = 42
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
            val source:i32 = 42
            
            // Variable declaration type provides context for widening
            val widened_i64:i64 = source     // i32 → i64 (declaration context)
            val converted_f32:f32 = source   // i32 → f32 (declaration context)
            val converted_f64:f64 = source   // i32 → f64 (declaration context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_context_propagation(self):
        """Test that context propagates through expressions"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            
            // ✅ Expression context guides result type
            val sum_i64:i64 = a + b           // i32 + i32 → i64 (context)
            val sum_f64:f64 = a + b           // i32 + i32 → f64 (context)
            val complex:f64 = (a * b) + 100  // Complex expression → f64 (context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComplexCoercionScenarios(StandardTestBase):
    """Test complex coercion scenarios and edge cases"""

    def test_chained_safe_coercions(self):
        """Test chained safe coercions work correctly"""
        source = """
        func test() : void = {
            val start:i32 = 42
            
            // Chained safe coercions
            val step1:i64 = start         // i32 → i64
            val step2:f64 = step1         // i64 → f64
            
            // Direct multi-step coercion
            val direct:f64 = start        // i32 → f64 (direct)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mixed_type_expressions_with_coercion(self):
        """Test mixed-type expressions with safe coercion"""
        source = """
        func test() : void = {
            val int_val:i32 = 10
            val float_val:f64 = 3.14
            
            // ✅ Mixed expressions with explicit result type
            val result_f64:f64 = int_val + float_val  // i32 + f64 → f64
            val result_i64:i64 = int_val + int_val    // i32 + i32 → i64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_nested_expression_coercion(self):
        """Test coercion in nested expressions"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            val c:f32 = 3.14
            
            // ✅ Nested expressions with context-guided coercion
            val result1:f64 = (a + b) * 2    // (i32 + i32) * i32 → f64
            val result2:f64 = a + (b * c)    // i32 + (i32 * f32) → f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestCoercionEdgeCases(StandardTestBase):
    """Test edge cases and boundary conditions for type coercion"""

    def test_same_type_assignments(self):
        """Test that same-type assignments always work"""
        source = """
        func test() : void = {
            val int_val:i32 = 42
            val float_val:f64 = 3.14
            val bool_val:bool = true
            val string_val:string = "hello"
            
            // ✅ Same type assignments (identity coercion)
            mut int_mut:i32 = int_val
            mut float_mut:f64 = float_val
            mut bool_mut:bool = bool_val
            mut string_mut:string = string_val
            
            // ✅ Reassignments of same type
            int_mut = int_val
            float_mut = float_val
            bool_mut = bool_val
            string_mut = string_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_zero_and_small_values_coercion(self):
        """Test coercion with zero and small values"""
        source = """
        func test() : void = {
            val zero_i32:i32 = 0
            val small_i32:i32 = 1
            val zero_f32:f32 = 0.0
            val small_f32:f32 = 0.1
            
            // ✅ Safe coercion works for all values
            val zero_i64:i64 = zero_i32
            val small_i64:i64 = small_i32
            val zero_f64:f64 = zero_f32
            val small_f64:f64 = small_f32
            val zero_float:f64 = zero_i32
            val small_float:f64 = small_i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_type_default_resolution(self):
        """Test comptime type default resolution behavior"""
        source = """
        func test() : void = {
            // ✅ Comptime types use sensible defaults
            val default_int = 42        // comptime_int → i32 (default)
            val default_float = 3.14    // comptime_float → f64 (default)
            
            // ✅ Context overrides defaults
            val explicit_i64:i64 = 42    // comptime_int → i64 (context)
            val explicit_f32:f32 = 3.14  // comptime_float → f32 (context)
            
            // ✅ Mixed comptime operations with explicit types (as required by analyzer)
            val mixed_explicit:f64 = 42 + 3.14  // comptime_int + comptime_float → f64 (explicit)
            val mixed_f32:f32 = 42 + 3.14       // comptime_int + comptime_float → f32 (explicit)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestCoercionErrorMessages(StandardTestBase):
    """Test error messages for type coercion scenarios"""

    def test_clear_error_messages_for_unsupported_coercions(self):
        """Test clear error messages for type coercions that aren't supported"""
        source = """
        func test() : void = {
            val int_val:i32 = 42
            val string_val:string = "hello"
            val bool_val:bool = true
            
            // ❌ Unsupported coercions should give clear errors
            val bad1:string = int_val     // i32 → string not supported
            val bad2:i32 = string_val     // string → i32 not supported  
            val bad3:bool = int_val       // i32 → bool not supported
            val bad4:i32 = bool_val       // bool → i32 not supported
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 4

        # Check that error messages are informative
        for error in errors:
            assert (
                "Type mismatch" in error.message
                or "Cannot coerce" in error.message
                or "Invalid conversion" in error.message
            )

    def test_mixed_type_operation_error_messages(self):
        """Test error messages for mixed-type operations without context"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            val c:f32 = 3.14
            val d:f64 = 2.718
            
            // ❌ Mixed operations without explicit context
            val mixed1 = a + b     // i32 + i64 needs context
            val mixed2 = c + d     // f32 + f64 needs context  
            val mixed3 = a + c     // i32 + f32 needs context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        for error in errors:
            assert (
                "requires explicit result type" in error.message
                or "Mixed-type operation" in error.message
                or "ambiguous" in error.message.lower()
            )
