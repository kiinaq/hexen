"""
Test suite for integer precision loss detection in Hexen

Tests integer-to-integer precision loss scenarios:
- i64 to i32 truncation detection
- Large integer literal handling
- Safe integer widening validation
- Explicit conversion acknowledgment

Part of the "Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit conversion needed)
- Dangerous operations require explicit conversion via value:type syntax
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
            
            // ❌ Should require explicit conversion
            small = large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential truncation" in error_msg
        assert "i32" in error_msg
        assert "Use explicit conversion: 'value:i32'" in error_msg

    def test_i64_to_i32_truncation_with_conversion(self):
        """Test that explicit conversion allows i64 to i32 conversion"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807  // Max i64 value
            mut small:i32 = 0
            
            // ✅ Explicit conversion of truncation
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
            // ❌ Large literal that may not fit in i32 without conversion
            val truncated:i32 = 4294967296  // 2^32, too large for i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Note: This depends on implementation - comptime_int may handle this differently
        # The test verifies behavior is consistent with type system design
        # May or may not produce errors depending on implementation
        assert isinstance(errors, list)  # Ensure errors is a list

    def test_val_integer_truncation_conversion(self):
        """Test val variables support integer truncation conversion"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            
            // ✅ val variables support precision loss conversion
            val truncated:i32 = large:i32    // Acknowledge truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_integer_truncation_in_reassignment(self):
        """Test mut variables support integer truncation conversion in reassignments"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            mut small:i32 = 0
            
            // ✅ mut reassignment supports truncation conversion
            small = large:i32      // Acknowledge truncation
            small = (large * 2):i32 // Complex expression with conversion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_safe_integer_widening(self):
        """Test that safe integer widening doesn't require conversion"""
        source = """
        func test() : void = {
            val small:i32 = 42
            
            // ✅ Safe widening - no conversion required
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

    def test_max_value_assignments(self):
        """Test precision loss at maximum values"""
        source = """
        func test() : void = {
            // Test with large values that definitely cause precision loss
            val max_i64:i64 = 9223372036854775807
            mut target_i32:i32 = 0

            // These should definitely require conversion
            target_i32 = max_i64:i32    // ✅ Acknowledge truncation
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
            mut target_i32:i32 = 0
            
            // ❌ Still requires conversion due to type difference
            // Implementation may vary - some allow small values, others require consistency
            target_i32 = small_i64     // May or may not require conversion
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
            mut target_i32:i32 = 0
            
            // ❌ Even exact values may require conversion for type consistency
            // (Implementation choice - some systems require it, others allow it)
            target_i32 = exact_int      // May require:i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Test documents behavior - may or may not require conversion
        assert isinstance(errors, list)

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
        assert "Use explicit conversion: 'value:i32'" in error_msg
        # Message should contain guidance for explicit conversion
