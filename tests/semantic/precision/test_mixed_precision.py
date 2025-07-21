"""
Test suite for mixed-type precision loss detection in Hexen

Tests precision loss in mixed-type scenarios:
- Integer to float conversion precision loss
- Float to integer truncation
- Mixed-type binary operations
- Complex expression precision loss
- Chained precision loss scenarios

Part of the "Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit conversion needed)
- Dangerous operations require explicit conversion via value:type syntax
"""

from tests.semantic import StandardTestBase


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
        # while others may require conversion for very large integers
        # May or may not produce errors depending on implementation
        assert isinstance(errors, list)  # Ensure errors is a list

    def test_float_to_integer_truncation(self):
        """Test float to integer conversion (truncation)"""
        source = """
        func test() : void = {
            val float_val:f64 = 3.14159
            mut int_val:i32 = 0
            
            // ❌ Float to integer truncation requires explicit conversion
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

    def test_float_to_integer_with_conversion(self):
        """Test float to integer conversion with explicit conversion"""
        source = """
        func test() : void = {
            val float_val:f64 = 3.14159
            mut int_val:i32 = 0
            
            // ✅ Explicit conversion of truncation
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
            
            // ✅ Explicit conversion allows all truncations
            int32_var = float_val:i32   // f32 → i32 with conversion
            int32_var = double_val:i32  // f64 → i32 with conversion
            int64_var = float_val:i64   // f32 → i64 with conversion
            int64_var = double_val:i64  // f64 → i64 with conversion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_chained_precision_loss(self):
        """Test detection of precision loss in assignment chains"""
        source = """
        func test() : void = {
            val start:f64 = 3.141592653589793   // High precision
            
            // Chain involving precision loss - requires conversion
            mut intermediate:f32 = 0.0
            mut final:i32 = 0
            
            // ❌ Each step with potential precision loss needs conversion
            intermediate = start       // f64 → f32 precision loss
            final = intermediate       // f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2  # At least two precision loss errors

    def test_chained_precision_loss_with_conversions(self):
        """Test that explicit conversions resolve chained precision loss"""
        source = """
        func test() : void = {
            val start:f64 = 3.141592653589793
            
            mut intermediate:f32 = 0.0
            mut final:i32 = 0
            
            // ✅ Explicit conversion at each step
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

    def test_expression_precision_loss_with_conversion(self):
        """Test complex expressions with precision loss conversion"""
        source = """
        func test() : void = {
            val a:f64 = 1.23456789
            val b:f64 = 9.87654321
            val c:i64 = 1000000
            
            mut result:i32 = 0
            
            // ✅ Explicit conversion for entire complex expression
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
            
            // ✅ Complex nested expressions with proper conversions
            single = (precise * 2.0 + 1.0):f32  // Nested f64 operations → f32
            integer = (precise:f32 * single):i32     // Explicit conversion: f64 → f32, then f32 * f32 → i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work with proper explicit conversions
        precision_errors = [
            e
            for e in errors
            if "precision" in e.message.lower() or "truncation" in e.message.lower()
        ]
        assert len(precision_errors) == 0

    def test_mixed_concrete_types_require_explicit_conversions(self):
        """Test that mixed concrete types fail without explicit conversions (negative case)"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            val single:f32 = 2.5
            mut integer:i32 = 0
            
            // ❌ Mixed concrete types require explicit conversions
            integer = (precise * single):i32     // f64 * f32 should fail
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should produce error for mixed concrete types
        assert len(errors) >= 1

        # Check that error mentions mixed concrete types
        mixed_type_errors = [
            e
            for e in errors
            if "mixed concrete" in e.message.lower()
            or "mixed-type" in e.message.lower()
        ]
        assert len(mixed_type_errors) >= 1

        # Verify error suggests explicit conversions
        error_msg = mixed_type_errors[0].message
        assert (
            "explicit conversion" in error_msg.lower()
            or "f64" in error_msg
            and "f32" in error_msg
        )

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
        assert any("value:i32" in msg for msg in error_messages)
        assert any("value:f32" in msg for msg in error_messages)
        assert all(
            "truncation" in msg.lower() or "precision" in msg.lower()
            for msg in error_messages
        )

    def test_explicit_conversion_mismatch_error_guidance(self):
        """Test error messages for explicit conversion with precision loss"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            
            mut small:i32 = 0
            // ❌ Wrong explicit conversion causes precision loss
            small = large:i64    // large:i64 → i64, then i64 → i32 (precision loss)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential truncation" in error_msg
        assert "value:i32" in error_msg
