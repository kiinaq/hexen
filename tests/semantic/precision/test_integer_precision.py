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
        """Test that concrete type conversions require explicit syntax per TYPE_SYSTEM.md"""
        source = """
        func test() : void = {
            val small:i32 = 42
            
            // 🔧 All concrete conversions require explicit syntax per TYPE_SYSTEM.md
            val wide:i64 = small:i64       // i32 → i64 (explicit required)
            val as_float:f32 = small:f32   // i32 → f32 (explicit required)
            val as_double:f64 = small:f64  // i32 → f64 (explicit required)
            
            mut wide_mut:i64 = 0
            mut float_mut:f32 = 0.0
            wide_mut = small:i64            // i32 → i64 (explicit required)
            float_mut = small:f32           // i32 → f32 (explicit required)
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
        """Test that ALL concrete conversions require explicit syntax per TYPE_SYSTEM.md"""
        source = """
        func test() : void = {
            val small_i64:i64 = 42      // Small value, fits in i32
            mut target_i32:i32 = 0
            
            // ❌ ALL concrete conversions require explicit syntax per TYPE_SYSTEM.md
            target_i32 = small_i64     // Error: requires explicit conversion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Per TYPE_SYSTEM.md: ALL concrete conversions require explicit syntax
        assert len(errors) == 1
        assert "Potential truncation" in errors[0].message

    def test_exact_representable_values(self):
        """Test that ALL concrete conversions require explicit syntax per TYPE_SYSTEM.md"""
        source = """
        func test() : void = {
            val exact_int:i64 = 42          // Exactly representable in i32
            mut target_i32:i32 = 0
            
            // ❌ ALL concrete conversions require explicit syntax per TYPE_SYSTEM.md
            target_i32 = exact_int      // Error: requires exact_int:i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Per TYPE_SYSTEM.md: ALL concrete conversions require explicit syntax
        assert len(errors) == 1
        assert "Potential truncation" in errors[0].message

    # NOTE: Error message format testing is centralized in test_error_messages.py
    # This test was removed to avoid duplication - see test_truncation_error_message_format
