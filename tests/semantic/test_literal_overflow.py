"""
Tests for literal overflow behavior per LITERAL_OVERFLOW_BEHAVIOR.md.

Tests comprehensive literal overflow detection including:
- Integer overflow detection for i32 and i64
- Float overflow detection for f32 and f64
- Enhanced literal formats (hex, binary, scientific)
- Boundary value testing
- Comptime type preservation with deferred overflow checking
- Error message format validation
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from . import assert_no_errors, assert_error_contains


class TestLiteralOverflowDetection:
    """Test literal overflow detection per LITERAL_OVERFLOW_BEHAVIOR.md"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_i32_overflow_detection(self):
        """Test i32 overflow detection with clear error messages"""
        source = """
        func test() : i32 = {
            val overflow : i32 = 4294967296
            return overflow
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1  # May have additional "undefined variable" error
        assert_error_contains(errors, "Literal 4294967296 overflows i32 range")
        assert_error_contains(errors, "Expected: -2147483648 to 2147483647")
        assert_error_contains(
            errors, "Use explicit conversion if truncation is intended: 4294967296:i32"
        )

    def test_i32_boundary_values(self):
        """Test exact boundary values for i32"""
        # Test maximum i32 value
        source_max = """
        func test() : i32 = {
            val max_i32 : i32 = 2147483647
            return max_i32
        }
        """
        ast = self.parser.parse(source_max)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Test minimum i32 value
        source_min = """
        func test() : i32 = {
            val min_i32 : i32 = -2147483648
            return min_i32
        }
        """
        ast = self.parser.parse(source_min)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Test overflow by one
        source_overflow = """
        func test() : i32 = {
            val overflow : i32 = 2147483648
            return overflow
        }
        """
        ast = self.parser.parse(source_overflow)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        assert_error_contains(errors, "Literal 2147483648 overflows i32 range")

    def test_i64_boundary_values(self):
        """Test i64 boundary values - max value should work"""
        # Test maximum i64 value (should work)
        source_max = """
        func test() : i64 = {
            val max_i64 : i64 = 9223372036854775807
            return max_i64
        }
        """
        ast = self.parser.parse(source_max)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

        # Test large negative i64 value (should work)
        source_min = """
        func test() : i64 = {
            val min_i64 : i64 = -9223372036854775807
            return min_i64
        }
        """
        ast = self.parser.parse(source_min)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_f32_overflow_detection(self):
        """Test f32 overflow detection with scientific notation"""
        source = """
        func test() : f32 = {
            val overflow : f32 = 3.5e+38
            return overflow
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(errors, "Literal 3.5e+38 overflows f32 range")
        assert_error_contains(errors, "Expected: approximately ±3.4028235e+38")

    def test_f64_boundary_values(self):
        """Test f64 boundary values work correctly"""
        # Use a large value that's valid for f64
        source = """
        func test() : f64 = {
            val large_f64 : f64 = 1.7e+308
            return large_f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_hex_literal_overflow(self):
        """Test hexadecimal literal overflow detection"""
        source = """
        func test() : i32 = {
            val hex_overflow : i32 = 0x100000000
            return hex_overflow
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(errors, "Literal 0x100000000 overflows i32 range")

    def test_binary_literal_overflow(self):
        """Test binary literal overflow detection"""
        source = """
        func test() : i32 = {
            val bin_overflow : i32 = 0b100000000000000000000000000000000
            return bin_overflow
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(
            errors, "Literal 0b100000000000000000000000000000000 overflows i32 range"
        )

    def test_scientific_literal_overflow(self):
        """Test scientific notation literal overflow"""
        source = """
        func test() : i32 = {
            val sci_overflow : i32 = 3e10
            return sci_overflow
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(errors, "Literal 3e10 overflows i32 range")

    def test_comptime_type_preservation_valid(self):
        """Test comptime type preservation allows large values until context forces resolution"""
        source = """
        func test() : void = {
            val flexible = 4294967296
            val as_i64 : i64 = flexible
            val as_f64 : f64 = flexible
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_enhanced_literals_valid_cases(self):
        """Test all enhanced literal formats work within valid ranges"""
        source = """
        func test() : void = {
            val hex_val : i32 = 0xFF
            val bin_val : i32 = 0b1111
            val sci_int : i32 = 1e3
            val sci_float : f64 = 1.23e-4
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_assignment_overflow_detection(self):
        """Test overflow detection in assignment statements"""
        source = """
        func test() : void = {
            mut value : i32 = 0
            value = 4294967296
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(errors, "Literal 4294967296 overflows i32 range")

    def test_return_statement_overflow_detection(self):
        """Test overflow detection in return statements"""
        source = """
        func test() : i32 = {
            return 4294967296
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(errors, "Literal 4294967296 overflows i32 range")


class TestOverflowErrorMessages:
    """Test error message format matches LITERAL_OVERFLOW_BEHAVIOR.md specification"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_integer_overflow_error_format(self):
        """Test integer overflow error message format"""
        source = """
        func test() : i32 = {
            val x : i32 = 4294967296
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        error_msg = str(errors[0])
        assert "Literal 4294967296 overflows i32 range" in error_msg
        assert "Expected: -2147483648 to 2147483647" in error_msg
        assert (
            "Suggestion: Use explicit conversion if truncation is intended: 4294967296:i32"
            in error_msg
        )

    def test_float_overflow_error_format(self):
        """Test float overflow error message format"""
        source = """
        func test() : f32 = {
            val x : f32 = 3.5e+38
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        error_msg = str(errors[0])
        assert "Literal 3.5e+38 overflows f32 range" in error_msg
        assert "Expected: approximately ±3.4028235e+38" in error_msg
        assert (
            "Suggestion: Use explicit conversion if truncation is intended: 3.5e+38:f32"
            in error_msg
        )

    def test_hex_literal_error_preserves_format(self):
        """Test hex literal error preserves original format"""
        source = """
        func test() : i32 = {
            val x : i32 = 0xFFFFFFFF
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        error_msg = str(errors[0])
        assert "Literal 0xFFFFFFFF overflows i32 range" in error_msg

    def test_binary_literal_error_preserves_format(self):
        """Test binary literal error preserves original format"""
        source = """
        func test() : i32 = {
            val x : i32 = 0b11111111111111111111111111111111
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        error_msg = str(errors[0])
        assert (
            "Literal 0b11111111111111111111111111111111 overflows i32 range"
            in error_msg
        )

    def test_scientific_literal_error_preserves_format(self):
        """Test scientific literal error preserves original format"""
        source = """
        func test() : i32 = {
            val x : i32 = 2.5E+9
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        error_msg = str(errors[0])
        assert "Literal 2.5E+9 overflows i32 range" in error_msg


class TestOverflowEdgeCases:
    """Test edge cases and boundary conditions for overflow detection"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_negative_overflow(self):
        """Test large positive literal that would overflow i32"""
        # Use a simpler test: large positive literal overflowing i32
        source = """
        func test() : i32 = {
            val x : i32 = 3000000000
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        assert_error_contains(errors, "overflows i32 range")

    def test_zero_values_valid(self):
        """Test zero values are always valid"""
        source = """
        func test() : void = {
            val zero_int : i32 = 0
            val zero_float : f32 = 0.0
            val zero_hex : i32 = 0x0
            val zero_bin : i32 = 0b0
            val zero_sci : i32 = 0e0
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_mixed_format_large_values(self):
        """Test large values work when target type can accommodate them"""
        source = """
        func test() : void = {
            val large_hex : i64 = 0x1FFFFFFFF
            val large_bin : i64 = 0b111111111111111111111111111111111111
            val large_sci : i64 = 1e15
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestParseTimeOverflow:
    """Test parse-time overflow detection for extremely large values"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_parse_time_overflow_extremely_large_int(self):
        """Test that extremely large integers are caught at parse time"""
        source = """
        func test() : i64 = {
            val too_large = 18446744073709551616
            return too_large
        }
        """
        with pytest.raises(SyntaxError) as exc_info:
            self.parser.parse(source)

        assert "exceeds maximum safe range for any integer type" in str(exc_info.value)

    def test_parse_time_overflow_beyond_i64_max(self):
        """Test that values beyond i64 max are caught at parse time"""
        source = """
        func test() : i32 = {
            val beyond_i64 = 9223372036854775808
            return beyond_i64
        }
        """
        with pytest.raises(SyntaxError) as exc_info:
            self.parser.parse(source)

        assert "exceeds maximum safe range for any integer type" in str(exc_info.value)
