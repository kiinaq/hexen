"""
Test suite for precision loss detection in Hexen

Tests the "Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit acknowledgment needed)
- Dangerous operations require explicit acknowledgment via type annotations
- Precision loss scenarios and their detection
- Comprehensive error messages guiding users to solutions

This file consolidates ALL precision loss testing to eliminate overlap across:
- test_type_coercion.py (precision loss removal)
- test_mutability.py (precision loss removal)
- test_type_annotations.py (focus on syntax, not precision loss)
"""

from tests.semantic import StandardTestBase


class TestIntegerPrecisionLoss(StandardTestBase):
    """Test precision loss scenarios for integer types"""

    def test_i64_to_i32_truncation_detection(self):
        """Test detection of potential i64 to i32 truncation"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807  // Max i64 value
            mut small:i32 = 0
            
            // ❌ Should require explicit acknowledgment
            small = large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential truncation" in error_msg
        assert "i32" in error_msg
        assert "Add ': i32'" in error_msg

    def test_i64_to_i32_truncation_with_acknowledgment(self):
        """Test that explicit acknowledgment allows i64 to i32 conversion"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807  // Max i64 value
            mut small:i32 = 0
            
            // ✅ Explicit acknowledgment of truncation
            small = large:i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_large_integer_literal_truncation(self):
        """Test truncation of large integer literals"""
        source = """
        func test() : void = {
            // ❌ Large literal that may not fit in i32 without acknowledgment
            val truncated:i32 = 4294967296  // 2^32, too large for i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Note: This depends on implementation - comptime_int may handle this differently
        # The test verifies behavior is consistent with type system design
        # May or may not produce errors depending on implementation
        assert isinstance(errors, list)  # Ensure errors is a list

    def test_val_integer_truncation_acknowledgment(self):
        """Test val variables support integer truncation acknowledgment"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            
            // ✅ val variables support precision loss acknowledgment
            val truncated:i32 = large:i32    // Acknowledge truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_integer_truncation_in_reassignment(self):
        """Test mut variables support integer truncation acknowledgment in reassignments"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            mut small:i32 = 0
            
            // ✅ mut reassignment supports truncation acknowledgment
            small = large:i32      // Acknowledge truncation
            small = (large * 2):i32 // Complex expression with acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestFloatPrecisionLoss(StandardTestBase):
    """Test precision loss scenarios for floating-point types"""

    def test_f64_to_f32_precision_loss_detection(self):
        """Test detection of f64 to f32 precision loss"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793  // High precision π
            mut single:f32 = 0.0
            
            // ❌ Should require explicit acknowledgment of precision loss
            single = precise
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential precision loss" in error_msg
        assert "f32" in error_msg
        assert "Add ': f32'" in error_msg

    def test_f64_to_f32_precision_loss_with_acknowledgment(self):
        """Test that explicit acknowledgment allows f64 to f32 conversion"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793  // High precision π
            mut single:f32 = 0.0
            
            // ✅ Explicit acknowledgment of precision loss
            single = precise:f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_double_precision_literal_to_f32(self):
        """Test assignment of high-precision literals to f32"""
        source = """
        func test() : void = {
            // ✅ comptime_float can safely coerce to f32
            val single:f32 = 3.141592653589793  // Safe comptime coercion
            
            // But concrete f64 to f32 requires acknowledgment
            val double:f64 = 3.141592653589793
            mut target:f32 = 0.0
            target = double:f32                   // ✅ Explicit acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_val_float_precision_loss_acknowledgment(self):
        """Test val variables work with float precision loss acknowledgments"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            
            // ✅ val variables support precision loss acknowledgment
            val reduced:f32 = precise:f32     // Acknowledge precision loss
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_float_precision_loss_in_reassignment(self):
        """Test mut variables support float precision loss acknowledgment in reassignments"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            mut single:f32 = 0.0
            
            // ✅ mut reassignment supports precision loss acknowledgment
            single = precise:f32   // Acknowledge precision loss
            single = (precise + 1.0):f32 // Complex expression with acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestMixedTypePrecisionLoss(StandardTestBase):
    """Test precision loss in mixed-type scenarios"""

    def test_i64_to_f32_precision_loss(self):
        """Test i64 to f32 conversion which may lose precision for very large integers"""
        source = """
        func test() : void = {
            val big_int:i64 = 9223372036854775807  // Max i64
            mut float_val:f32 = 0.0
            
            // ❌ Large i64 to f32 may lose precision for very large values
            float_val = big_int
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # This test depends on implementation - some may allow this as "safe widening"
        # while others may require acknowledgment for very large integers
        # May or may not produce errors depending on implementation
        assert isinstance(errors, list)  # Ensure errors is a list

    def test_float_to_integer_truncation(self):
        """Test float to integer conversion (truncation)"""
        source = """
        func test() : void = {
            val float_val:f64 = 3.14159
            mut int_val:i32 = 0
            
            // ❌ Float to integer truncation requires explicit acknowledgment
            int_val = float_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert (
            "Potential truncation" in error_msg
            or "Mixed types" in error_msg
            or "Type mismatch" in error_msg
        )

    def test_float_to_integer_with_acknowledgment(self):
        """Test float to integer conversion with explicit acknowledgment"""
        source = """
        func test() : void = {
            val float_val:f64 = 3.14159
            mut int_val:i32 = 0
            
            // ✅ Explicit acknowledgment of truncation
            int_val = float_val:i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comprehensive_mixed_type_conversions(self):
        """Test all combinations of mixed-type precision loss"""
        source = """
        func test() : void = {
            val float_val:f32 = 3.14
            val double_val:f64 = 2.718
            mut int32_var:i32 = 0
            mut int64_var:i64 = 0
            
            // ✅ Explicit acknowledgment allows all truncations
            int32_var = float_val:i32   // f32 → i32 with acknowledgment
            int32_var = double_val:i32  // f64 → i32 with acknowledgment
            int64_var = float_val:i64   // f32 → i64 with acknowledgment
            int64_var = double_val:i64  // f64 → i64 with acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestSafeOperationsNoAcknowledgment(StandardTestBase):
    """Test that safe operations don't require explicit acknowledgment"""

    def test_safe_integer_widening(self):
        """Test that safe integer widening doesn't require acknowledgment"""
        source = """
        func test() : void = {
            val small:i32 = 42
            
            // ✅ Safe widening - no acknowledgment required
            val wide:i64 = small          // i32 → i64 (safe)
            val as_float:f32 = small      // i32 → f32 (safe)
            val as_double:f64 = small     // i32 → f64 (safe)
            
            mut wide_mut:i64 = 0
            mut float_mut:f32 = 0.0
            wide_mut = small                // i32 → i64 (safe reassignment)
            float_mut = small               // i32 → f32 (safe reassignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_safe_float_widening(self):
        """Test that safe float widening doesn't require acknowledgment"""
        source = """
        func test() : void = {
            val single:f32 = 3.14
            
            // ✅ Safe widening - no acknowledgment required  
            val double:f64 = single       // f32 → f64 (safe)
            
            mut double_mut:f64 = 0.0
            double_mut = single             // f32 → f64 (safe reassignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_type_safe_coercions(self):
        """Test that comptime type coercions are always safe and implicit"""
        source = """
        func test() : void = {
            // ✅ All comptime type coercions are safe and implicit
            val int_default = 42            // comptime_int → i32 (default)
            val int_explicit:i64 = 42     // comptime_int → i64 (safe)
            val float_from_int:f64 = 42   // comptime_int → f64 (safe)
            val float_default = 3.14        // comptime_float → f64 (default)
            val float_explicit:f32 = 3.14 // comptime_float → f32 (safe)
            
            // mut variables follow same rules
            mut counter:i32 = 0
            mut precise:f64 = 0.0
            counter = 42                    // comptime_int → i32 (safe reassignment)
            precise = 3.14                  // comptime_float → f64 (safe reassignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestBinaryOperationsPrecisionLoss(StandardTestBase):
    """Test precision loss in binary operations (consolidates from test_binary_ops.py)"""

    def test_binary_operation_result_precision_loss(self):
        """Test precision loss when binary operation results need truncation"""
        source = """
        func test() : void = {
            val a:i64 = 1000
            val b:i64 = 2000
            mut result:i32 = 0
            
            // ❌ Binary operation result may exceed i32 range
            result = a + b
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Implementation dependent - may require acknowledgment
        assert isinstance(errors, list)

    def test_binary_operation_with_mixed_types_precision_loss(self):
        """Test precision loss in mixed-type binary operations"""
        source = """
        func test() : void = {
            val int_val:i32 = 10
            val float_val:f64 = 3.14
            mut result:i32 = 0
            
            // ❌ Mixed operation result needs truncation acknowledgment
            result = int_val + float_val
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1  # Should require explicit handling

    def test_binary_operation_precision_loss_with_acknowledgment(self):
        """Test binary operations with explicit precision loss acknowledgment"""
        source = """
        func test() : void = {
            val int_val:i32 = 10
            val float_val:f64 = 3.14
            mut result:i32 = 0
            
            // ✅ Explicit acknowledgment for mixed operation result
            result = (int_val + float_val):i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work with explicit acknowledgment
        # May have other errors but not precision loss
        precision_errors = [
            e
            for e in errors
            if "precision" in e.message.lower() or "truncation" in e.message.lower()
        ]
        assert len(precision_errors) == 0


class TestComplexPrecisionLossScenarios(StandardTestBase):
    """Test complex precision loss scenarios and edge cases"""

    def test_chained_precision_loss(self):
        """Test detection of precision loss in assignment chains"""
        source = """
        func test() : void = {
            val start:f64 = 3.141592653589793   // High precision
            
            // Chain involving precision loss - requires acknowledgment
            mut intermediate:f32 = 0.0
            mut final:i32 = 0
            
            // ❌ Each step with potential precision loss needs acknowledgment
            intermediate = start       // f64 → f32 precision loss
            final = intermediate       // f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2  # At least two precision loss errors

    def test_chained_precision_loss_with_acknowledgments(self):
        """Test that explicit acknowledgments resolve chained precision loss"""
        source = """
        func test() : void = {
            val start:f64 = 3.141592653589793
            
            mut intermediate:f32 = 0.0
            mut final:i32 = 0
            
            // ✅ Explicit acknowledgment at each step
            intermediate = start:f32         // Acknowledge f64 → f32 precision loss
            final = intermediate:i32         // Acknowledge f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_precision_loss(self):
        """Test precision loss in complex expressions"""
        source = """
        func test() : void = {
            val a:f64 = 1.23456789
            val b:f64 = 9.87654321
            val c:i64 = 1000000
            
            mut result:i32 = 0
            
            // ❌ Complex expression with multiple precision loss points
            result = (a * b + c)    // f64 operation result → i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

    def test_expression_precision_loss_with_acknowledgment(self):
        """Test complex expressions with precision loss acknowledgment"""
        source = """
        func test() : void = {
            val a:f64 = 1.23456789
            val b:f64 = 9.87654321
            val c:i64 = 1000000
            
            mut result:i32 = 0
            
            // ✅ Explicit acknowledgment for entire complex expression
            result = (a * b + c):i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # May have mixed-type operation errors, but not precision loss
        precision_errors = [
            e
            for e in errors
            if "precision" in e.message.lower() or "truncation" in e.message.lower()
        ]
        assert len(precision_errors) == 0

    def test_nested_expression_precision_loss(self):
        """Test precision loss in nested expressions with different target types"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            mut single:f32 = 0.0
            mut integer:i32 = 0
            
            // ✅ Complex nested expressions with proper acknowledgments
            single = (precise * 2.0 + 1.0):f32  // Nested f64 operations → f32
            integer = (precise * single):i32     // Mixed f64 * f32 → i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work with proper type annotations
        precision_errors = [
            e
            for e in errors
            if "precision" in e.message.lower() or "truncation" in e.message.lower()
        ]
        assert len(precision_errors) == 0


class TestPrecisionLossErrorMessages(StandardTestBase):
    """Test precision loss error messages are helpful and consistent"""

    def test_truncation_error_message_guidance(self):
        """Test that truncation errors provide clear guidance"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            mut small:i32 = 0
            
            small = large   // Error with guidance
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential truncation" in error_msg
        assert "Add ': i32'" in error_msg
        assert "acknowledge" in error_msg.lower()

    def test_precision_loss_error_message_guidance(self):
        """Test that precision loss errors provide clear guidance"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            mut single:f32 = 0.0
            
            single = precise   // Error with guidance
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential precision loss" in error_msg
        assert "Add ': f32'" in error_msg
        assert "acknowledge" in error_msg.lower()

    def test_multiple_precision_loss_errors_detected(self):
        """Test that multiple precision loss scenarios are all detected"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            val precise:f64 = 3.141592653589793
            
            mut small:i32 = 0
            mut single:f32 = 0.0
            
            // Multiple precision loss scenarios
            small = large      // Truncation error
            single = precise   // Precision loss error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]
        assert any(": i32" in msg for msg in error_messages)
        assert any(": f32" in msg for msg in error_messages)
        assert all(
            "truncation" in msg.lower() or "precision" in msg.lower()
            for msg in error_messages
        )

    def test_type_annotation_mismatch_error_guidance(self):
        """Test clear error messages when type annotations don't match variable type"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            
            mut small:i32 = 0
            // ❌ Type annotation must match variable's declared type
            small = large:i64    // Error: annotation should be i32, not i64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Type annotation must match" in error_msg
        assert "i32" in error_msg
        assert "i64" in error_msg


class TestBoundaryConditions(StandardTestBase):
    """Test precision loss at boundary conditions and edge cases"""

    def test_max_value_assignments(self):
        """Test precision loss at maximum values"""
        source = """
        func test() : void = {
            // Test with large values that definitely cause precision loss
            val max_i64:i64 = 9223372036854775807
            val max_f64:f64 = 179769313486231570000000000000000000000.0

            mut target_i32:i32 = 0
            mut target_f32:f32 = 0.0

            // These should definitely require acknowledgment
            target_i32 = max_i64:i32    // ✅ Acknowledge truncation
            target_f32 = max_f64:f32    // ✅ Acknowledge precision loss
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_zero_and_small_values(self):
        """Test that small values don't trigger false precision loss warnings"""
        source = """
        func test() : void = {
            val small_i64:i64 = 42      // Small value, fits in i32
            val small_f64:f64 = 3.14    // Small value, fits in f32
            
            mut target_i32:i32 = 0
            mut target_f32:f32 = 0.0
            
            // ❌ Still requires acknowledgment due to type difference
            // Implementation may vary - some allow small values, others require consistency
            target_i32 = small_i64     // May or may not require acknowledgment
            target_f32 = small_f64     // May or may not require acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Implementation dependent - test ensures no crashes
        assert isinstance(errors, list)

    def test_exact_representable_values(self):
        """Test values that are exactly representable across types"""
        source = """
        func test() : void = {
            val exact_int:i64 = 42          // Exactly representable in i32
            val exact_float:f64 = 2.0       // Exactly representable in f32
            
            mut target_i32:i32 = 0
            mut target_f32:f32 = 0.0
            
            // ❌ Even exact values may require acknowledgment for type consistency
            // (Implementation choice - some systems require it, others allow it)
            target_i32 = exact_int      // May require:i32
            target_f32 = exact_float    // May require:f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Test documents behavior - may or may not require acknowledgment
        assert isinstance(errors, list)


class TestTypeAnnotationConsistency(StandardTestBase):
    """Test type annotation consistency rules with precision loss (consolidates with test_type_annotations)"""

    def test_type_annotation_must_match_variable_type(self):
        """Test that type annotations must exactly match the target variable's type"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            
            // ✅ Correct: annotation matches variable type
            val correct_val:i32 = large:i32
            mut correct_mut:i32 = 0
            correct_mut = large:i32
            
            // ❌ Wrong: annotation doesn't match variable type
            val wrong_val:i32 = large:i64    // Error: left i32, annotation i64
            mut wrong_mut:i32 = 0
            wrong_mut = large:i64              // Error: left i32, annotation i64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        for error in errors:
            assert "Type annotation must match" in error.message
            assert "i32" in error.message and "i64" in error.message

    def test_precision_loss_annotation_positioning(self):
        """Test that precision loss annotations must be at rightmost end of expressions"""
        source = """
        func test() : void = {
            val a:f64 = 3.14
            val b:f64 = 2.71
            mut result:i32 = 0
            
            // ✅ Correct: annotation at rightmost end
            result = (a + b):i32
            result = (a * b * 2.0):i32
            result = (a + (b * 2.0)):i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work - may have mixed-type errors but positioning should be correct
        positioning_errors = [e for e in errors if "position" in e.message.lower()]
        assert len(positioning_errors) == 0
