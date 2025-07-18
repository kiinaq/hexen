"""
Test suite for safe operations requiring no explicit conversion in Hexen

Tests operations that don't require explicit conversion:
- Safe type widening (i32 → i64, f32 → f64)
- Comptime type safe coercions
- Binary operations with safe results
- Type annotation consistency rules

Part of the "Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit conversion needed)
- Dangerous operations require explicit conversion via value:type syntax
"""

from tests.semantic import StandardTestBase


class TestSafeOperationsNoConversion(StandardTestBase):
    """Test that safe operations don't require explicit conversion"""

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

    def test_safe_float_widening(self):
        """Test that concrete type conversions require explicit syntax per TYPE_SYSTEM.md"""
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

    def test_binary_operation_result_safe_assignment(self):
        """Test binary operation results that don't require precision loss conversion"""
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

    def test_binary_operation_with_comptime_safe(self):
        """Test binary operations with comptime types are safe"""
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

    def test_type_declaration_consistency_safe(self):
        """Test that correct type declarations don't cause precision loss"""
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

    def test_precision_loss_annotation_positioning_safe(self):
        """Test explicit conversions with no precision loss"""
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

    def test_function_return_safe_coercion(self):
        """Test that function returns can safely return comptime types"""
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

    def test_safe_assignment_chains(self):
        """Test that concrete type conversions require explicit syntax per TYPE_SYSTEM.md"""
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
