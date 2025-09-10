"""
Test suite for valid operations with proper explicit conversions in Hexen

Tests operations that work correctly with explicit conversions:
- Concrete type conversions with explicit syntax (i32:i64, f32:f64)
- Comptime type implicit coercions (comptime_int → i32)
- Binary operations with same concrete types
- Proper explicit conversion syntax validation

Part of the "Ergonomic Literals + Transparent Costs" principle:
- Comptime types adapt implicitly (ergonomic for literals)
- All concrete conversions require explicit syntax (transparent costs)
"""

from tests.semantic import StandardTestBase


class TestValidOperationsWithExplicitConversions(StandardTestBase):
    """
    Test that valid operations work correctly with proper explicit conversions.

    This test suite validates the positive cases where operations should succeed:
    - Comptime types implicitly coercing to concrete types (ergonomic)
    - Explicit conversions with proper syntax (transparent costs)
    - Same-type operations requiring no conversions (identity)

    Complements test_mixed_precision.py which focuses on error cases.
    """

    def test_concrete_integer_conversions_with_explicit_syntax(self):
        """Test that concrete type conversions work with explicit syntax per TYPE_SYSTEM.md"""
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

    def test_concrete_float_conversions_with_explicit_syntax(self):
        """Test that concrete float conversions work with explicit syntax per TYPE_SYSTEM.md"""
        source = """
        func test() : void = {
            val single:f32 = 3.14
            
            // 🔧 All concrete conversions require explicit syntax per TYPE_SYSTEM.md
            val double:f64 = single:f64   // f32 → f64 (explicit required)
            
            mut double_mut:f64 = 0.0
            double_mut = single:f64         // f32 → f64 (explicit required)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_type_implicit_coercions(self):
        """Test that comptime type coercions are always implicit (ergonomic literals)"""
        source = """
        func test() : void = {
            // ✅ All comptime type coercions are safe and implicit
            val flexible_int = 42           // comptime_int (preserved flexibility)
            val int_explicit:i64 = 42     // comptime_int → i64 (safe)
            val float_from_int:f64 = 42   // comptime_int → f64 (safe)
            val flexible_float = 3.14       // comptime_float (preserved flexibility)
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

    def test_same_concrete_type_binary_operations(self):
        """Test binary operations with same concrete types (no conversion needed)"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            mut result:i32 = 0
            
            // ✅ Same type binary operations are safe
            result = a + b                  // i32 + i32 → i32 (safe)
            result = a * b                  // i32 * i32 → i32 (safe)
            result = a - b                  // i32 - i32 → i32 (safe)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_comptime_concrete_mixed_binary_operations(self):
        """Test binary operations with comptime types adapting to concrete context"""
        source = """
        func test() : void = {
            val concrete:i32 = 100
            mut result:i32 = 0
            
            // ✅ Comptime types adapt to concrete type context
            result = concrete + 42          // i32 + comptime_int → i32 (safe)
            result = concrete * 2           // i32 * comptime_int → i32 (safe)
            result = concrete - 10          // i32 - comptime_int → i32 (safe)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_explicit_conversions_with_no_precision_loss(self):
        """Test explicit conversions that preserve or increase precision"""
        source = """
        func test() : void = {
            val source:i32 = 42
            
            // ✅ Correct: explicit conversion to same type (no precision loss)
            val same_type:i32 = source:i32    // i32:i32 → i32 (identity, safe)
            
            // ✅ Correct: explicit conversion to wider type (no precision loss)
            val wider_type:i64 = source:i64   // i32:i64 → i64 (safe widening)
            
            mut same_mut:i32 = 0
            mut wider_mut:i64 = 0
            same_mut = source:i32               // i32:i32 → i32 (identity, safe)
            wider_mut = source:i64              // i32:i64 → i64 (safe widening)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_explicit_expression_conversions_no_precision_loss(self):
        """Test explicit conversions of expressions with no precision loss"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            mut result:i64 = 0
            
            // 🔧 Explicit conversions required per TYPE_SYSTEM.md
            result = (a + b):i64            // i32 + i32 → i32, then i32:i64 → i64 (explicit)
            result = (a * b * 2):i64        // All i32 ops → i32, then i32:i64 → i64 (explicit)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_function_return_comptime_coercion(self):
        """Test that function returns can implicitly coerce comptime types"""
        source = """
        func get_int() : i32 = {
            return 42                       // comptime_int → i32 (safe)
        }
        
        func get_float() : f64 = {
            return 3.14                     // comptime_float → f64 (safe)
        }
        
        func get_mixed() : f64 = {
            return 42                       // comptime_int → f64 (safe)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_explicit_conversion_chains_no_precision_loss(self):
        """Test chained explicit conversions that preserve or increase precision"""
        source = """
        func test() : void = {
            val start:i32 = 42
            
            // 🔧 All concrete conversions require explicit syntax per TYPE_SYSTEM.md
            val intermediate:i64 = start:i64     // i32 → i64 (explicit required)
            val final:f64 = intermediate:f64     // i64 → f64 (explicit required)
            
            mut chain_mut:i64 = 0
            mut final_mut:f64 = 0.0
            chain_mut = start:i64                // i32 → i64 (explicit required)
            final_mut = chain_mut:f64            // i64 → f64 (explicit required)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
