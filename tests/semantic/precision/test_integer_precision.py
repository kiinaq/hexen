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

    def test_large_integer_literal_overflow_detection(self):
        """Test overflow detection for large integer literals per LITERAL_OVERFLOW_BEHAVIOR.md"""
        source = """
        func test() : void = {
            // ❌ Large literal that overflows i32 range - should trigger overflow error
            val truncated:i32 = 4294967296  // 2^32, exceeds i32 max (2147483647)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Per LITERAL_OVERFLOW_BEHAVIOR.md: compile-time overflow detection should catch this
        assert len(errors) >= 1, (
            "Expected overflow error for literal exceeding i32 range"
        )
        assert "overflows i32 range" in errors[0].message

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
