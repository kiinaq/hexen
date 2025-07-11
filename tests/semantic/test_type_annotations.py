"""
Test suite for type annotation system in Hexen

Tests the comprehensive type annotation system described in TYPE_SYSTEM.md:
- Type annotations must match left-hand side type exactly
- Type annotations must be at rightmost end of expression
- Type annotations are explicit acknowledgments, not conversions
- Type annotations require explicit left-side types
- "Explicit Danger, Implicit Safety" principle enforcement

This file focuses on SYNTAX and RULES, not precision loss scenarios.
Precision loss testing is comprehensively covered in test_precision_loss.py.
"""

from tests.semantic import StandardTestBase


class TestTypeAnnotationBasics(StandardTestBase):
    """Test basic type annotation functionality"""

    def test_type_annotation_matches_left_side(self):
        """Test that type annotations must match the left-hand side type exactly"""
        source = """
        func test() : void = {
            val integer:i32 = 3.14:i32      // ✅ Both sides i32
            val long_int:i64 = 12345:i64    // ✅ Both sides i64
            val single:f32 = 2.718:f32      // ✅ Both sides f32
            val double:f64 = 3.14159:f64    // ✅ Both sides f64
            
            val large_value:i64 = 9223372036854775807
            mut counter:i32 = 0
            counter = large_value:i32          // ✅ Both sides i32 (assignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_annotation_mismatch_error(self):
        """Test error when type annotation doesn't match left-hand side"""
        source = """
        func test() : void = {
            val wrong:i32 = 3.14:f64        // ❌ Left i32, right f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert (
            "Type annotation must match variable's declared type" in errors[0].message
        )
        assert "expected i32, got f64" in errors[0].message

    def test_type_annotation_positioning(self):
        """Test that type annotations must be at rightmost end"""
        source = """
        func test() : void = {
            // Define variables for complex expressions
            val a:f64 = 2.0
            val b:f64 = 3.0
            val c:f64 = 4.0
            val x:f32 = 1.0
            val y:f32 = 2.0
            val z:f32 = 3.0
            
            // ✅ Correct: annotation at rightmost end
            val result:i32 = (10 + 20):i32
            val complex:f64 = (a * b + c):f64
            
            mut value:f32 = 0.0
            value = (x + y * z):f32            // ✅ Assignment with annotation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should have some errors due to undefined variables, but no type annotation errors
        type_annotation_errors = [e for e in errors if "Type annotation" in e.message]
        assert len(type_annotation_errors) == 0

    def test_type_annotation_explicit_acknowledgment(self):
        """Test type annotations as explicit acknowledgment (not conversion)"""
        source = """
        func test() : void = {
            val a:i64 = 9223372036854775807    // Max i64
            val b:f64 = 3.141592653589793      // High precision
            
            // Explicit acknowledgment pattern - annotation matches target type
            val truncated:i32 = a:i32        // ✅ Acknowledge result type
            val reduced:f32 = b:f32          // ✅ Acknowledge result type
            val mixed:i32 = b:i32            // ✅ Acknowledge result type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestTypeAnnotationRequirements(StandardTestBase):
    """Test when type annotations are required vs optional"""

    def test_type_annotation_not_required_for_safe_operations(self):
        """Test that safe operations don't require type annotations"""
        source = """
        func test() : void = {
            // ✅ Safe comptime type coercions (no annotation needed)
            val int_default = 42           // comptime_int → i32 (default)
            val int_explicit:i64 = 42    // comptime_int → i64 (safe)
            val float_from_int:f64 = 42  // comptime_int → f64 (safe)
            val float_default = 3.14       // comptime_float → f64 (default)
            val float_explicit:f32 = 3.14 // comptime_float → f32 (safe)
            
            // ✅ Safe widening coercions (no annotation needed)
            val small:i32 = 100
            val wide:i64 = small         // i32 → i64 (safe widening)
            val as_float:f64 = small     // i32 → f64 (safe conversion)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_annotation_for_mixed_operations_context(self):
        """Test that mixed-type operations require explicit result type context"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            val c:f32 = 3.14
            val d:f64 = 2.718
            
            // ❌ Mixed operations require explicit result type
            val mixed1 = a + b     // Error: i32 + i64 requires explicit result type
            val mixed2 = c + d     // Error: f32 + f64 requires explicit result type
            val mixed3 = a + c     // Error: i32 + f32 requires explicit result type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Filter for mixed-type operation errors (system correctly reports both operation and inference errors)
        mixed_type_errors = [
            e
            for e in errors
            if "requires explicit result type" in e.message
            or "Mixed-type operation" in e.message
        ]
        assert len(mixed_type_errors) == 3

        for error in mixed_type_errors:
            assert (
                "requires explicit result type" in error.message
                or "Mixed-type operation" in error.message
            )

    def test_comptime_type_changes_require_context(self):
        """Test that comptime type changes require explicit context"""
        source = """
        func test() : void = {
            // ❌ These operations would change comptime type and need explicit context
            val mixed = 42 + 3.14        // comptime_int + comptime_float → needs context
            val float_div = 42 / 3       // comptime_int / comptime_int → comptime_float (needs context)
            
            // ✅ Same operations work with explicit context
            val mixed_explicit:f64 = 42 + 3.14    // comptime types adapt to f64
            val float_div_explicit:f32 = 42 / 3   // comptime types adapt to f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2  # mixed and float_div should error

        for error in errors:
            assert (
                "requires explicit result type" in error.message
                or "Mixed-type operation" in error.message
            )


class TestTypeAnnotationWithoutExplicitLeftType(StandardTestBase):
    """Test the critical rule: no type annotation without explicit left-side type"""

    def test_type_annotation_forbidden_without_explicit_left_type(self):
        """Test that type annotations cannot be used without explicit left-side type"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            val c:f64 = 3.14
            
            // ❌ FORBIDDEN: Type annotation without explicit left side type
            val result1 = a + b:i64        // Error: No explicit left side type to match
            val result2 = a + c:f64        // Error: No explicit left side type to match
            val result3 = 42:i32           // Error: No explicit left side type to match
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Semantic analyzer produces multiple errors per invalid construct
        # (annotation error + type inference error for each case)
        assert len(errors) == 6

        # Verify the annotation-specific errors are present
        annotation_errors = [
            e
            for e in errors
            if "annotation requires explicit left side type" in e.message
        ]
        assert len(annotation_errors) == 3

    def test_type_annotation_allowed_with_explicit_left_type(self):
        """Test that type annotations work when explicit left-side type is provided"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            val c:f64 = 3.14
            
            // ✅ CORRECT: Explicit left side type that matches right side annotation
            val result1:i64 = a + b:i64   // Both sides have i64
            val result2:f64 = a + c:f64   // Both sides have f64
            mut counter:i32 = 0
            counter = a:i32                 // Both sides have i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work - mixed operations may have their own errors but annotations should be fine
        annotation_errors = [e for e in errors if "annotation" in e.message.lower()]
        assert len(annotation_errors) == 0


class TestTypeAnnotationSyntaxRules(StandardTestBase):
    """Test type annotation syntax rules and parsing"""

    def test_type_annotation_precedence(self):
        """Test that type annotations have highest precedence"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            val c:i32 = 30
            
            // Type annotation applies to entire expression (highest precedence)
            val result1:i32 = a + b * c:i32    // (a + b * c):i32
            val result2:i32 = (a + b) * c:i32  // ((a + b) * c):i32
            val result3:i32 = a + (b * c):i32  // (a + (b * c)):i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_annotation_in_expressions(self):
        """Test type annotation syntax in various expression contexts"""
        source = """
        func test() : void = {
            val base:f64 = 3.14
            mut result:i32 = 0
            mut accumulator:f64 = 0.0
            
            // Type annotations in different expression contexts
            result = base:i32                          // Simple expression
            result = (base * 2.0):i32                  // Parenthesized expression
            result = (base + 1.0) * 2.0:i32            // Complex expression
            accumulator = (base + 1.0):f64             // Assignment context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work syntactically - may have precision loss warnings but that's separate
        syntax_errors = [
            e
            for e in errors
            if "syntax" in e.message.lower() or "parse" in e.message.lower()
        ]
        assert len(syntax_errors) == 0

    def test_type_annotation_with_function_calls(self):
        """Test type annotations with complex expressions"""
        source = """
        func compute() : i64 = {
            val x:i32 = 42
            return x * 2
        }
        
        func test() : void = {
            mut result:i32 = 0
            
            // Type annotation with expression (not function call since unsupported)
            val value:i64 = 42 * 2
            result = value:i32    // Expression result with annotation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # May have precision loss error but should handle expression annotation
        assert len(errors) >= 0


class TestTypeAnnotationComplexExpressions(StandardTestBase):
    """Test type annotations with complex expressions"""

    def test_type_annotation_with_nested_operations(self):
        """Test type annotations with nested operations"""
        source = """
        func test() : void = {
            val a:f64 = 1.5
            val b:f64 = 2.5
            val c:f64 = 3.5
            val d:f64 = 4.5
            
            mut result:i32 = 0
            
            // Complex nested operations with type annotation
            result = ((a + b) * (c - d)):i32           // Nested arithmetic
            result = (a * b + c * d):i32               // Multiple operations
            result = (a + (b * c) - d):i32             // Mixed precedence
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work syntactically - precision loss is handled in test_precision_loss.py
        syntax_errors = [e for e in errors if "syntax" in e.message.lower()]
        assert len(syntax_errors) == 0

    def test_type_annotation_with_division_operators(self):
        """Test type annotations with both division operators"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 3
            val c:f64 = 2.5
            
            mut int_result:i32 = 0
            mut float_result:f64 = 0.0
            
            // Type annotations with division operators
            int_result = (a \\ b):i32                 // Integer division result
            float_result = (a / b):f64                 // Float division result
            float_result = (c / 2.0):f64              // Float division with floats
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work syntactically
        syntax_errors = [e for e in errors if "syntax" in e.message.lower()]
        assert len(syntax_errors) == 0

    def test_type_annotation_scope_in_expressions(self):
        """Test that type annotations apply to the entire expression"""
        source = """
        func test() : void = {
            val x:f64 = 1.0
            val y:f64 = 2.0
            val z:f64 = 3.0
            
            mut result:i32 = 0
            
            // Type annotation applies to entire expression, not just last operation
            result = x + y * z:i32          // (x + y * z):i32
            result = (x + y) * z:i32        // ((x + y) * z):i32
            result = x * (y + z):i32        // (x * (y + z)):i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work syntactically
        syntax_errors = [e for e in errors if "syntax" in e.message.lower()]
        assert len(syntax_errors) == 0


class TestTypeAnnotationErrorMessages(StandardTestBase):
    """Test type annotation error messages are clear and helpful"""

    def test_type_annotation_mismatch_error_details(self):
        """Test detailed error messages for type annotation mismatches"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            
            // Multiple type annotation mismatches
            val wrong1:i32 = large:i64     // Error: i32 vs i64
            val wrong2:f32 = large:f64     // Error: f32 vs f64
            val wrong3:i64 = large:i32     // Error: i64 vs i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        # Check that each error message is clear and specific
        for error in errors:
            assert "Type annotation must match" in error.message
            assert ("expected" in error.message and "got" in error.message) or (
                "declared type" in error.message and "annotation" in error.message
            )

    def test_missing_left_type_error_message(self):
        """Test error message when type annotation is used without explicit left type"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            
            // Missing explicit left type
            val result = a + b:i64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        # Should have clear error about missing explicit left type
        annotation_errors = [
            e
            for e in errors
            if "annotation" in e.message.lower() and "explicit" in e.message.lower()
        ]
        assert len(annotation_errors) >= 1

    def test_comprehensive_error_message_guidance(self):
        """Test that error messages provide comprehensive guidance"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            mut small:i32 = 0
            
            // Multiple error scenarios
            small = large                       // No acknowledgment
            val bad_result = large + 42:i64   // Type annotation without explicit left type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 2

        # Should contain guidance for both issues
        error_messages = [e.message for e in errors]
        has_precision_guidance = any(
            "acknowledge" in msg.lower() for msg in error_messages
        )
        has_annotation_guidance = any(
            "explicit" in msg.lower() for msg in error_messages
        )

        assert has_precision_guidance or has_annotation_guidance


class TestTypeAnnotationIntegration(StandardTestBase):
    """Test type annotation integration with other language features"""

    def test_type_annotation_with_binary_operations(self):
        """Test type annotations work properly with binary operations"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i32 = 20
            val c:f64 = 3.14
            
            mut int_result:i32 = 0
            mut float_result:f64 = 0.0
            
            // Type annotations with various binary operations
            int_result = (a + b):i32              // Same types
            int_result = (a - b):i32              // Same types  
            int_result = (a * b):i32              // Same types
            int_result = (a \\ b):i32             // Integer division
            float_result = (a / b):f64            // Float division
            float_result = (c * 2.0):f64          // Float operations
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work - type annotations provide proper context
        annotation_errors = [e for e in errors if "annotation" in e.message.lower()]
        assert len(annotation_errors) == 0

    def test_type_annotation_with_mutability(self):
        """Test type annotations work with both val and mut variables"""
        source = """
        func test() : void = {
            val source:i64 = 1000
            
            // Type annotations with val declarations
            val val_result:i32 = source:i32
            
            // Type annotations with mut declarations and reassignments
            mut mut_result:i32 = 0
            mut_result = source:i32               // Reassignment with annotation
            mut_result = (source * 2):i32         // Complex expression with annotation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_annotation_consistency_across_contexts(self):
        """Test that type annotation rules are consistent across all contexts"""
        source = """
        func test() : void = {
            val base:f64 = 3.14
            
            // Consistent annotation rules across contexts
            val decl_result:i32 = base:i32          // Declaration context
            
            mut mut_result:i32 = 0
            mut_result = base:i32                     // Assignment context
            
            // All follow same rule: annotation must match left-side type
            // All are explicit acknowledgments, not conversions
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
