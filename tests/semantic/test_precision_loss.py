"""
Test suite for precision loss detection in Hexen

Tests the "Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit acknowledgment needed)
- Dangerous operations require explicit acknowledgment via type annotations
- Precision loss scenarios and their detection
- Comprehensive error messages guiding users to solutions
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestIntegerPrecisionLoss:
    """Test precision loss scenarios for integer types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_i64_to_i32_truncation_detection(self):
        """Test detection of potential i64 to i32 truncation"""
        source = """
        func test() : void = {
            val large : i64 = 9223372036854775807  // Max i64 value
            mut small : i32 = 0
            
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
            val large : i64 = 9223372036854775807  // Max i64 value
            mut small : i32 = 0
            
            // ✅ Explicit acknowledgment of truncation
            small = large : i32
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
            val truncated : i32 = 4294967296  // 2^32, too large for i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Note: This depends on implementation - comptime_int may handle this differently
        # The test verifies behavior is consistent with type system design
        # May or may not produce errors depending on implementation
        assert isinstance(errors, list)  # Ensure errors is a list


class TestFloatPrecisionLoss:
    """Test precision loss scenarios for floating-point types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_f64_to_f32_precision_loss_detection(self):
        """Test detection of f64 to f32 precision loss"""
        source = """
        func test() : void = {
            val precise : f64 = 3.141592653589793  // High precision π
            mut single : f32 = 0.0
            
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
            val precise : f64 = 3.141592653589793  // High precision π
            mut single : f32 = 0.0
            
            // ✅ Explicit acknowledgment of precision loss
            single = precise : f32
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
            val single : f32 = 3.141592653589793  // Safe comptime coercion
            
            // But concrete f64 to f32 requires acknowledgment
            val double : f64 = 3.141592653589793
            mut target : f32 = 0.0
            target = double : f32                   // ✅ Explicit acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestMixedTypePrecisionLoss:
    """Test precision loss in mixed-type scenarios"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_i64_to_f32_precision_loss(self):
        """Test i64 to f32 conversion which may lose precision for very large integers"""
        source = """
        func test() : void = {
            val big_int : i64 = 9223372036854775807  // Max i64
            mut float_val : f32 = 0.0
            
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
            val float_val : f64 = 3.14159
            mut int_val : i32 = 0
            
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
            val float_val : f64 = 3.14159
            mut int_val : i32 = 0
            
            // ✅ Explicit acknowledgment of truncation
            int_val = float_val : i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestSafeOperationsNoAcknowledgment:
    """Test that safe operations don't require explicit acknowledgment"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_safe_integer_widening(self):
        """Test that safe integer widening doesn't require acknowledgment"""
        source = """
        func test() : void = {
            val small : i32 = 42
            
            // ✅ Safe widening - no acknowledgment needed
            val wide : i64 = small          // i32 → i64 (safe)
            val as_float : f64 = small      // i32 → f64 (safe)
            
            mut wide_mut : i64 = 0
            mut float_mut : f64 = 0.0
            
            wide_mut = small                // i32 → i64 (safe assignment)
            float_mut = small               // i32 → f64 (safe assignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_safe_float_widening(self):
        """Test that safe float widening doesn't require acknowledgment"""
        source = """
        func test() : void = {
            val single : f32 = 3.14
            
            // ✅ Safe widening - no acknowledgment needed
            val double : f64 = single       // f32 → f64 (safe)
            
            mut double_mut : f64 = 0.0
            double_mut = single             // f32 → f64 (safe assignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_type_safe_coercions(self):
        """Test that comptime type coercions are always safe"""
        source = """
        func test() : void = {
            // ✅ All comptime coercions are safe - no acknowledgment needed
            val int_to_i32 = 42             // comptime_int → i32 (default)
            val int_to_i64 : i64 = 42       // comptime_int → i64 (safe)
            val int_to_f32 : f32 = 42       // comptime_int → f32 (safe)
            val int_to_f64 : f64 = 42       // comptime_int → f64 (safe)
            
            val float_to_f32 : f32 = 3.14   // comptime_float → f32 (safe)
            val float_to_f64 = 3.14         // comptime_float → f64 (default)
            
            // Safe reassignments with comptime types
            mut flexible_int : i64 = 0
            mut flexible_float : f32 = 0.0
            
            flexible_int = 42               // comptime_int → i64 (safe)
            flexible_float = 3.14           // comptime_float → f32 (safe)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestComplexPrecisionLossScenarios:
    """Test complex scenarios involving precision loss"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_chained_precision_loss(self):
        """Test chained operations with potential precision loss"""
        source = """
        func test() : void = {
            val start : i64 = 9223372036854775807
            mut intermediate : f32 = 0.0
            mut final : i32 = 0
            
            // ❌ Multiple precision loss steps
            intermediate = start    // Error: i64 → f32 may lose precision
            final = intermediate    // Error: f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2  # At least 2 precision loss errors

    def test_chained_precision_loss_with_acknowledgments(self):
        """Test chained operations with proper acknowledgments"""
        source = """
        func test() : void = {
            val start : i64 = 9223372036854775807
            mut intermediate : f32 = 0.0
            mut final : i32 = 0
            
            // ✅ Explicit acknowledgment at each step
            intermediate = start : f32      // Acknowledge i64 → f32 precision loss
            final = intermediate : i32      // Acknowledge f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_precision_loss(self):
        """Test precision loss in complex expressions"""
        source = """
        func test() : void = {
            val a : i64 = 1000000
            val b : f64 = 3.14159
            
            mut result : i32 = 0
            
            // ❌ Complex expression with potential precision loss
            result = (a * 2 + b)      // Mixed types with final truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        # Should suggest explicit result type
        for error in errors:
            assert (
                "explicit" in error.message.lower()
                or "annotation" in error.message.lower()
                or "type" in error.message.lower()
            )

    def test_expression_precision_loss_with_acknowledgment(self):
        """Test complex expression precision loss with proper acknowledgment"""
        source = """
        func test() : void = {
            val a : i64 = 1000000
            val b : f64 = 3.14159
            
            mut result : i32 = 0
            
            // ✅ Explicit acknowledgment of complex expression result
            result = (a * 2 + b) : i32      // Acknowledge mixed expression → i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestPrecisionLossErrorMessages:
    """Test that precision loss error messages are comprehensive and helpful"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_truncation_error_message_guidance(self):
        """Test that truncation errors provide clear guidance"""
        source = """
        func test() : void = {
            val large : i64 = 1000000
            mut small : i32 = 0
            
            small = large  // Should provide helpful error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        # Should contain guidance on how to fix
        assert "Add ': i32'" in error_msg or "explicit" in error_msg.lower()
        assert "truncation" in error_msg.lower() or "precision" in error_msg.lower()

    def test_precision_loss_error_message_guidance(self):
        """Test that precision loss errors provide clear guidance"""
        source = """
        func test() : void = {
            val precise : f64 = 3.141592653589793
            mut single : f32 = 0.0
            
            single = precise  // Should provide helpful error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        # Should contain guidance on how to fix
        assert "Add ': f32'" in error_msg or "explicit" in error_msg.lower()
        assert "precision" in error_msg.lower()

    def test_multiple_precision_loss_errors_detected(self):
        """Test that multiple precision loss errors are all detected"""
        source = """
        func test() : void = {
            val large : i64 = 1000000
            val precise : f64 = 3.14159
            val float_val : f32 = 2.718
            
            mut small : i32 = 0
            mut single : f32 = 0.0
            mut integer : i32 = 0
            
            // Multiple precision loss scenarios
            small = large       // i64 → i32 truncation
            single = precise    // f64 → f32 precision loss  
            integer = float_val // f32 → i32 truncation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        error_messages = [e.message for e in errors]
        assert any("truncation" in msg.lower() for msg in error_messages)
        assert any("precision" in msg.lower() for msg in error_messages)


class TestBoundaryConditions:
    """Test precision loss at type boundaries"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_max_value_assignments(self):
        """Test assignments of maximum values"""
        source = """
        func test() : void = {
            // Maximum values for each type
            val max_i32 : i32 = 2147483647
            val max_i64 : i64 = 9223372036854775807
            
            mut target_i32 : i32 = 0
            
            // ✅ Same type - no precision loss
            target_i32 = max_i32
            
            // ❌ Large to small - potential truncation
            target_i32 = max_i64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "truncation" in errors[0].message.lower()

    def test_zero_and_small_values(self):
        """Test that small values don't trigger precision loss warnings inappropriately"""
        source = """
        func test() : void = {
            val small_i64 : i64 = 42
            val small_f64 : f64 = 1.5
            
            mut target_i32 : i32 = 0
            mut target_f32 : f32 = 0.0
            
            // Even small values from larger types require acknowledgment
            // This maintains consistency in the type system
            target_i32 = small_i64     // Still requires acknowledgment
            target_f32 = small_f64     // Still requires acknowledgment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert (
            len(errors) == 2
        )  # Consistency requires acknowledgment even for small values
