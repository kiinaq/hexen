"""
Comprehensive Comptime Type System Tests for Hexen

This module provides complete test coverage for Hexen's comptime type system as
described in TYPE_SYSTEM.md. It consolidates all comptime type testing from:
- test_f32_comptime.py (will be deleted)
- overlapping content from test_type_coercion.py
- basic comptime tests from test_context_framework.py
- comptime tests from test_basic_semantics.py

The comptime type system enables "Explicit Danger, Implicit Safety" through:
- comptime_int: Integer literals that adapt to context (42 → i32, i64, f32, f64)
- comptime_float: Float literals that adapt to context (3.14 → f32, f64)
- Safe implicit coercion within allowed type tables
- Explicit acknowledgment required for unsafe conversions
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
    assert_error_count,
    assert_error_contains,
)


class TestComptimeIntCoercion(StandardTestBase):
    """Test comptime_int coercion to all allowed numeric types"""

    def test_comptime_int_to_i32_default(self):
        """Test comptime_int defaults to i32 when no explicit type provided"""
        source = """
        func test() : i32 = {
            val x = 42  // comptime_int → i32 (default)
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_int_to_i32_explicit(self):
        """Test comptime_int explicit coercion to i32"""
        source = """
        func test() : i32 = {
            val x : i32 = 42  // comptime_int → i32 (explicit)
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_int_to_i64_coercion(self):
        """Test comptime_int can coerce to i64 (safe implicit)"""
        source = """
        func test() : i64 = {
            val x : i64 = 42  // comptime_int → i64
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_int_to_f32_coercion(self):
        """Test comptime_int can coerce to f32 (safe implicit)"""
        source = """
        func test() : f32 = {
            val x : f32 = 42  // comptime_int → f32
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_int_to_f64_coercion(self):
        """Test comptime_int can coerce to f64 (safe implicit)"""
        source = """
        func test() : f64 = {
            val x : f64 = 42  // comptime_int → f64
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_int_large_values(self):
        """Test comptime_int with large values adapts to appropriate types"""
        source = """
        func test() : void = {
            val small : i32 = 2147483647      // Max i32
            val large : i64 = 9223372036854775807    // Max i64
            val float_val : f32 = 1000000     // Large but safe for f32
            val precise : f64 = 1000000000000 // Large value for f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_int_negative_values(self):
        """Test comptime_int with negative values"""
        source = """
        func test() : void = {
            val neg_i32 : i32 = -42
            val neg_i64 : i64 = -1000000
            val neg_f32 : f32 = -123
            val neg_f64 : f64 = -456789
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeFloatCoercion(StandardTestBase):
    """Test comptime_float coercion to allowed float types"""

    def test_comptime_float_to_f64_default(self):
        """Test comptime_float defaults to f64 when no explicit type provided"""
        source = """
        func test() : f64 = {
            val x = 3.14  // comptime_float → f64 (default)
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_to_f32_coercion(self):
        """Test comptime_float can coerce to f32 (safe implicit)"""
        source = """
        func test() : f32 = {
            val x : f32 = 3.14  // comptime_float → f32
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_to_f64_explicit(self):
        """Test comptime_float explicit coercion to f64"""
        source = """
        func test() : f64 = {
            val x : f64 = 3.14159265359  // comptime_float → f64 (explicit)
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_precision_values(self):
        """Test comptime_float with various precision values"""
        source = """
        func test() : void = {
            val simple : f32 = 3.14
            val precise : f64 = 3.141592653589793
            val small : f32 = 0.000001
            val large : f64 = 123456789.987654321
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_negative_values(self):
        """Test comptime_float with negative values"""
        source = """
        func test() : void = {
            val neg_f32 : f32 = -3.14
            val neg_f64 : f64 = -2.718281828
            val neg_small : f32 = -0.001
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeUnsafeCoercions(StandardTestBase):
    """Test that unsafe comptime coercions require explicit acknowledgment"""

    def test_comptime_int_to_bool_forbidden(self):
        """Test comptime_int cannot coerce to bool (type safety)"""
        source = """
        func test() : bool = {
            val x : bool = 42  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Type mismatch")
        assert_error_contains(errors, "bool")
        assert_error_contains(errors, "comptime_int")

    def test_comptime_int_to_string_forbidden(self):
        """Test comptime_int cannot coerce to string (type safety)"""
        source = """
        func test() : string = {
            val x : string = 42  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Type mismatch")
        assert_error_contains(errors, "string")
        assert_error_contains(errors, "comptime_int")

    def test_comptime_float_to_int_requires_acknowledgment(self):
        """Test comptime_float cannot implicitly coerce to integer types"""
        source = """
        func test() : i32 = {
            val x : i32 = 3.14  // Should fail - precision loss requires acknowledgment
            return 42           // Return a valid value to avoid undefined variable error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should have 1 error for the truncation (not undefined variable)
        assert len(errors) >= 1
        assert_error_contains(errors, "truncation")

    def test_comptime_float_to_int_with_acknowledgment(self):
        """Test comptime_float can coerce to integer with explicit acknowledgment"""
        source = """
        func test() : i32 = {
            val x : i32 = 3.14 : i32  // Explicit acknowledgment
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_to_bool_forbidden(self):
        """Test comptime_float cannot coerce to bool (type safety)"""
        source = """
        func test() : bool = {
            val x : bool = 3.14  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Type mismatch")
        assert_error_contains(errors, "bool")
        assert_error_contains(errors, "comptime_float")

    def test_comptime_float_to_string_forbidden(self):
        """Test comptime_float cannot coerce to string (type safety)"""
        source = """
        func test() : string = {
            val x : string = 3.14  // Should fail - unsafe coercion
            return x
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 1)
        assert_error_contains(errors, "Type mismatch")
        assert_error_contains(errors, "string")
        assert_error_contains(errors, "comptime_float")


class TestComptimeContextDependentResolution(StandardTestBase):
    """Test context-dependent resolution of comptime types"""

    def test_variable_declaration_context(self):
        """Test variable declaration type provides context for comptime resolution"""
        source = """
        func test() : void = {
            val explicit_i64 : i64 = 42   // comptime_int sees i64 context
            val explicit_f32 : f32 = 42   // comptime_int sees f32 context
            val explicit_f64 : f64 = 3.14 // comptime_float sees f64 context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_assignment_context(self):
        """Test assignment target type provides context for comptime resolution"""
        source = """
        func test() : void = {
            mut flexible : f64 = 0.0
            flexible = 42                // comptime_int → f64 (assignment context)
            
            mut int_var : i64 = 0
            int_var = 123456789         // comptime_int → i64 (assignment context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_return_context(self):
        """Test function return type provides context for comptime resolution"""
        source = """
        func get_int() : i32 = {
            return 42                   // comptime_int sees i32 return type
        }
        
        func get_float() : f32 = {
            return 3.14                 // comptime_float sees f32 return type
        }
        
        func get_mixed() : f64 = {
            return 42                   // comptime_int sees f64 return type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_return_context_comprehensive(self):
        """Test function return types provide comprehensive context for comptime resolution"""
        source = """
        func get_int32() : i32 = {
            return 1000     // comptime_int → i32 (return context)
        }
        
        func get_int64() : i64 = {
            return 2000     // comptime_int → i64 (return context)
        }
        
        func get_float32() : f32 = {
            return 3.14     // comptime_float → f32 (return context)
        }
        
        func get_float64() : f64 = {
            return 2.718    // comptime_float → f64 (return context)
        }
        
        func mixed_return() : f64 = {
            return 42       // comptime_int → f64 (return context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeMixedOperations(StandardTestBase):
    """Test comptime types in mixed operations and expressions"""

    def test_comptime_arithmetic_operations(self):
        """Test arithmetic operations with comptime types"""
        source = """
        func test() : void = {
            val int_result : i32 = 10 + 20        // comptime_int + comptime_int → i32
            val float_result : f64 = 3.14 + 2.86  // comptime_float + comptime_float → f64
            val mixed_result : f64 = 42 + 3.14    // Mixed: needs explicit context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_comparison_operations(self):
        """Test comparison operations with comptime types"""
        source = """
        func test() : void = {
            val int_comparison : bool = 42 > 30     // comptime_int comparison
            val float_comparison : bool = 3.14 < 4.0 // comptime_float comparison
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_in_complex_expressions(self):
        """Test comptime types in complex nested expressions"""
        source = """
        func test() : void = {
            val complex : f64 = (42 + 8) * 3.14   // Mixed expression with explicit context
            val nested : i32 = ((10 + 5) * 2) + 100  // Nested comptime_int operations
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeDefaults(StandardTestBase):
    """Test default type resolution for comptime types without context"""

    def test_comptime_int_default_to_i32(self):
        """Test comptime_int defaults to i32 when no context provided"""
        source = """
        func test() : void = {
            val default_int = 42          // comptime_int → i32 (default)
            mut mutable_int = 123         // comptime_int → i32 (default)
            mutable_int = 456            // comptime_int → i32 (assignment context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_float_default_to_f64(self):
        """Test comptime_float defaults to f64 when no context provided"""
        source = """
        func test() : void = {
            val default_float = 3.14      // comptime_float → f64 (default)
            mut mutable_float = 2.718     // comptime_float → f64 (default)
            mutable_float = 1.414        // comptime_float → f64 (assignment context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_mixed_defaults(self):
        """Test mixed comptime types with default resolution"""
        source = """
        func test() : void = {
            val int_default = 42          // comptime_int → i32
            val float_default = 3.14      // comptime_float → f64
            val explicit_mix : f32 = 42   // comptime_int → f32 (explicit context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeWithConcreteTypes(StandardTestBase):
    """Test interaction between comptime types and concrete types"""

    def test_comptime_and_concrete_type_mixing(self):
        """Test mixing comptime types with concrete types in expressions"""
        source = """
        func test() : void = {
            val concrete : i32 = 10
            
            // ✅ Comptime types adapt to context when mixed with concrete types
            val result1 : i64 = concrete + 42       // i32 + comptime_int → i64 context
            val result2 : f64 = concrete + 3.14     // i32 + comptime_float → f64 context
            
            // ✅ In assignments
            mut target : f64 = 0.0
            target = concrete + 42      // i32 + comptime_int → f64 assignment context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_multiple_concrete_types_require_context(self):
        """Test that multiple concrete types require explicit context"""
        source = """
        func test() : void = {
            val int32_val : i32 = 10
            val int64_val : i64 = 20
            val float_val : f32 = 3.14
            
            // ❌ Mixed concrete types require explicit result type
            val mixed1 = int32_val + int64_val      // i32 + i64 needs context
            val mixed2 = int32_val + float_val      // i32 + f32 needs context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2

        error_messages = [str(error) for error in errors]
        assert any(
            "Mixed-type operation" in msg or "explicit" in msg.lower()
            for msg in error_messages
        )

    def test_concrete_types_with_explicit_context(self):
        """Test mixed concrete types with explicit context"""
        source = """
        func test() : void = {
            val int32_val : i32 = 10
            val int64_val : i64 = 20
            val float_val : f32 = 3.14
            
            // ✅ Explicit context resolves mixed concrete types
            val mixed1 : i64 = int32_val + int64_val    // i32 + i64 → i64
            val mixed2 : f64 = int32_val + float_val    // i32 + f32 → f64
            val mixed3 : f32 = int32_val + float_val    // i32 + f32 → f32 (precision choice)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_with_concrete_in_complex_expressions(self):
        """Test comptime types with concrete types in complex expressions"""
        source = """
        func test() : void = {
            val base : i32 = 100
            val multiplier : f32 = 2.5
            
            // Complex mixed expressions with explicit context
            val result1 : f64 = (base + 50) * 3.14      // (i32 + comptime_int) * comptime_float → f64
            val result2 : f32 = multiplier + 42         // f32 + comptime_int → f32 context
            val result3 : i64 = base * 2                // i32 * comptime_int → i64 context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeEdgeCases(StandardTestBase):
    """Test edge cases and error scenarios for comptime types"""

    def test_comptime_type_in_error_messages(self):
        """Test that comptime types appear correctly in error messages"""
        source = """
        func test() : void = {
            val x : bool = 42             // Error should mention comptime_int
            val y : string = 3.14         // Error should mention comptime_float
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_count(errors, 2)

        # Check that comptime types are mentioned in error messages
        error_messages = [str(error) for error in errors]
        assert any("comptime_int" in msg for msg in error_messages)
        assert any("comptime_float" in msg for msg in error_messages)

    def test_multiple_comptime_coercions(self):
        """Test multiple comptime type coercions in same function"""
        source = """
        func test() : void = {
            val a : i32 = 42              // comptime_int → i32
            val b : i64 = 42              // comptime_int → i64
            val c : f32 = 42              // comptime_int → f32
            val d : f64 = 42              // comptime_int → f64
            val e : f32 = 3.14            // comptime_float → f32
            val f : f64 = 3.14            // comptime_float → f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_with_reassignment(self):
        """Test comptime types with mutable variable reassignment"""
        source = """
        func test() : void = {
            mut counter : i32 = 0         // comptime_int → i32
            counter = 42                  // comptime_int → i32 (assignment context)
            counter = 123                 // comptime_int → i32 (assignment context)
            
            mut precise : f64 = 0.0       // comptime_float → f64  
            precise = 3.14                // comptime_float → f64 (assignment context)
            precise = 42                  // comptime_int → f64 (assignment context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_zero_and_special_values(self):
        """Test comptime types with zero and special numeric values"""
        source = """
        func test() : void = {
            val zero_int : i32 = 0        // comptime_int zero
            val zero_float : f64 = 0.0    // comptime_float zero
            val negative : i64 = -1       // Negative comptime_int
            val small_float : f32 = 0.001 // Small comptime_float
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
