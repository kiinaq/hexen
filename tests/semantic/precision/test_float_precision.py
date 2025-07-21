"""
Test suite for float precision loss detection in Hexen

Tests floating-point precision loss scenarios:
- f64 to f32 precision loss detection
- High-precision literal handling
- Safe float widening validation
- Explicit conversion acknowledgment

Part of the "Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit conversion needed)
- Dangerous operations require explicit conversion via value:type syntax
"""

from tests.semantic import StandardTestBase


class TestFloatPrecisionLoss(StandardTestBase):
    """Test precision loss scenarios for floating-point types"""

    def test_f64_to_f32_precision_loss_detection(self):
        """Test detection of f64 to f32 precision loss"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793  // High precision π
            mut single:f32 = 0.0
            
            // ❌ Should require explicit conversion of precision loss
            single = precise
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential precision loss" in error_msg
        assert "f32" in error_msg
        assert "Use explicit conversion: 'value:f32'" in error_msg

    def test_f64_to_f32_precision_loss_with_conversion(self):
        """Test that explicit conversion allows f64 to f32 conversion"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793  // High precision π
            mut single:f32 = 0.0
            
            // ✅ Explicit conversion of precision loss
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
            
            // But concrete f64 to f32 requires conversion
            val double:f64 = 3.141592653589793
            mut target:f32 = 0.0
            target = double:f32                   // ✅ Explicit conversion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_val_float_precision_loss_conversion(self):
        """Test val variables work with float precision loss conversions"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            
            // ✅ val variables support precision loss conversion
            val reduced:f32 = precise:f32     // Acknowledge precision loss
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_float_precision_loss_in_reassignment(self):
        """Test mut variables support float precision loss conversion in reassignments"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            mut single:f32 = 0.0
            
            // ✅ mut reassignment supports precision loss conversion
            single = precise:f32   // Acknowledge precision loss
            single = (precise + 1.0):f32 // Complex expression with conversion
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
            val max_f64:f64 = 179769313486231570000000000000000000000.0
            mut target_f32:f32 = 0.0

            // These should definitely require conversion
            target_f32 = max_f64:f32    // ✅ Acknowledge precision loss
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_concrete_float_conversions_require_explicit_syntax(self):
        """Test that ALL f64→f32 conversions require explicit syntax per TYPE_SYSTEM.md"""
        test_cases = [
            ("3.14", "Small value that fits in f32"),
            ("2.0", "Exactly representable value"),
            ("1.0", "Simple exact value"),
            ("0.5", "Simple fractional value"),
        ]

        for value, description in test_cases:
            source = f"""
            func test() : void = {{
                val source_f64:f64 = {value}    // {description}
                mut target_f32:f32 = 0.0
                
                // ❌ ALL concrete conversions require explicit syntax per TYPE_SYSTEM.md
                target_f32 = source_f64     // Error: requires source_f64:f32
            }}
            """
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)

            # Per TYPE_SYSTEM.md: ALL concrete conversions require explicit syntax
            assert len(errors) == 1, f"Expected error for {description} ({value})"
            assert "Potential precision loss" in errors[0].message

    # NOTE: Error message format testing is centralized in test_error_messages.py
    # This test was removed to avoid duplication - see test_precision_loss_error_message_format
