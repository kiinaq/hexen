"""
Test suite for type annotation system in Hexen

Tests the comprehensive type annotation system described in TYPE_SYSTEM.md:
- Type annotations must match left-hand side type exactly
- Type annotations must be at rightmost end of expression
- Type annotations are explicit acknowledgments, not conversions
- Type annotations require explicit left-side types
- "Explicit Danger, Implicit Safety" principle enforcement
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestTypeAnnotationBasics:
    """Test basic type annotation functionality"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_annotation_matches_left_side(self):
        """Test that type annotations must match the left-hand side type exactly"""
        source = """
        func test() : void = {
            val integer : i32 = 3.14 : i32      // ✅ Both sides i32
            val long_int : i64 = 12345 : i64    // ✅ Both sides i64
            val single : f32 = 2.718 : f32      // ✅ Both sides f32
            val double : f64 = 3.14159 : f64    // ✅ Both sides f64
            
            mut counter : i32 = 0
            counter = large_value : i32          // ✅ Both sides i32 (assignment)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_annotation_mismatch_error(self):
        """Test error when type annotation doesn't match left-hand side"""
        source = """
        func test() : void = {
            val wrong : i32 = 3.14 : f64        // ❌ Left i32, right f64
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
            // ✅ Correct: annotation at rightmost end
            val result : i32 = (10 + 20) : i32
            val complex : f64 = (a * b + c) : f64
            
            mut value : f32 = 0.0
            value = (x + y * z) : f32            // ✅ Assignment with annotation
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should have some errors due to undefined variables, but no type annotation errors
        type_annotation_errors = [e for e in errors if "Type annotation" in e.message]
        assert len(type_annotation_errors) == 0

    def test_type_annotation_explicit_acknowledgment(self):
        """Test type annotations as explicit acknowledgment of precision loss"""
        source = """
        func test() : void = {
            val a : i64 = 9223372036854775807    // Max i64
            val b : f64 = 3.141592653589793      // High precision
            
            // Explicit acknowledgment of precision loss
            val truncated : i32 = a : i32        // ✅ Acknowledge truncation
            val reduced : f32 = b : f32          // ✅ Acknowledge precision loss
            val mixed : i32 = b : i32            // ✅ Acknowledge float→int conversion
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestTypeAnnotationRequirements:
    """Test when type annotations are required vs optional"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_annotation_required_for_precision_loss(self):
        """Test that type annotations are required for potential precision loss"""
        source = """
        func test() : void = {
            val large : i64 = 9223372036854775807
            val precise : f64 = 3.141592653589793
            
            mut small : i32 = 0
            mut single : f32 = 0.0
            
            // ❌ These should require explicit acknowledgment
            small = large      // Error: Potential truncation, add ": i32"
            single = precise   // Error: Potential precision loss, add ": f32"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]
        assert any(
            "Potential truncation" in msg and ": i32" in msg for msg in error_messages
        )
        assert any(
            "Potential precision loss" in msg and ": f32" in msg
            for msg in error_messages
        )

    def test_type_annotation_required_for_mixed_operations(self):
        """Test that mixed-type operations require explicit result type"""
        source = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            val c : f32 = 3.14
            val d : f64 = 2.718
            
            // ❌ Mixed operations require explicit result type
            val mixed1 = a + b     // Error: i32 + i64 requires explicit result type
            val mixed2 = c + d     // Error: f32 + f64 requires explicit result type
            val mixed3 = a + c     // Error: i32 + f32 requires explicit result type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        for error in errors:
            assert "Mixed-type operation" in error.message
            assert "requires explicit result type" in error.message

    def test_type_annotation_not_required_for_safe_operations(self):
        """Test that safe operations don't require type annotations"""
        source = """
        func test() : void = {
            // ✅ Safe comptime type coercions (no annotation needed)
            val int_default = 42           // comptime_int → i32 (default)
            val int_explicit : i64 = 42    // comptime_int → i64 (safe)
            val float_from_int : f64 = 42  // comptime_int → f64 (safe)
            val float_default = 3.14       // comptime_float → f64 (default)
            val float_explicit : f32 = 3.14 // comptime_float → f32 (safe)
            
            // ✅ Safe widening coercions (no annotation needed)
            val small : i32 = 100
            val wide : i64 = small         // i32 → i64 (safe widening)
            val as_float : f64 = small     // i32 → f64 (safe conversion)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestTypeAnnotationWithoutExplicitLeftType:
    """Test the critical rule: no type annotation without explicit left-side type"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_annotation_forbidden_without_explicit_left_type(self):
        """Test that type annotations cannot be used without explicit left-side type"""
        source = """
        func test() : void = {
            // ❌ FORBIDDEN: Type annotation without explicit left side type
            val result = 42 + 3.14 : f64      // Error: No explicit left side type
            val mixed = some_expr : i32       // Error: No explicit left side type
            mut counter = large_value : i32   // Error: No explicit left side type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should have multiple errors including the type annotation errors
        type_annotation_errors = [
            e
            for e in errors
            if "Type annotation requires explicit left side type" in e.message
        ]
        assert len(type_annotation_errors) >= 3

    def test_type_annotation_allowed_with_explicit_left_type(self):
        """Test that type annotations work when left-side type is explicit"""
        source = """
        func test() : void = {
            // ✅ CORRECT: Explicit left side type that matches right side annotation
            val result : f64 = (42 + 3.14) : f64    // Both sides have f64
            val mixed : i32 = some_expr : i32        // Both sides have i32
            mut counter : i32 = large_value : i32    // Both sides have i32
            
            // ✅ CORRECT: No type annotation needed when left side provides context
            val auto_result : f64 = 42 + 3.14        // Left side provides f64 context
            val auto_mixed : i32 = some_expr          // Left side provides i32 context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should only have errors for undefined variables, not type annotation errors
        type_annotation_errors = [e for e in errors if "Type annotation" in e.message]
        assert len(type_annotation_errors) == 0


class TestTypeAnnotationComplexExpressions:
    """Test type annotations with complex expressions"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_annotation_with_nested_operations(self):
        """Test type annotations work with nested operations"""
        source = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            val c : f32 = 3.14
            val d : f64 = 2.718
            
            // Complex expressions with explicit result types
            val complex1 : i64 = (a + b * 2) : i64
            val complex2 : f64 = (c * d + a) : f64
            val complex3 : f32 = (a + b + c) : f32
            
            // Nested operations with precision acknowledgment
            val nested : i32 = ((a + b) * c) : i32  // Acknowledge potential precision loss
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    # COMMENTED OUT: Requires function parameters (Phase 1.1 Parser Extensions)
    # def test_type_annotation_with_function_calls(self):
    #     """Test type annotations work with function call expressions"""
    #     source = """
    #     func compute(x: i32) : i64 = {
    #         return x * 1000
    #     }
    #
    #     func test() : void = {
    #         // Function call with type annotation for precision loss
    #         val result : i32 = compute(42) : i32    // Acknowledge i64 → i32 truncation
    #
    #         mut accumulator : f32 = 0.0
    #         accumulator = compute(10) : f32          // Acknowledge i64 → f32 conversion
    #     }
    #     """
    #     ast = self.parser.parse(source)
    #     errors = self.analyzer.analyze(ast)
    #     assert errors == []


class TestTypeAnnotationErrorMessages:
    """Test comprehensive error messages for type annotation system"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comprehensive_error_messages(self):
        """Test that error messages provide clear guidance"""
        source = """
        func test() : void = {
            val large : i64 = 9223372036854775807
            mut small : i32 = 0
            
            // Should provide helpful error message
            small = large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Potential truncation" in error_msg
        assert "Add ': i32'" in error_msg
        assert "explicitly acknowledge" in error_msg

    def test_multiple_type_annotation_errors(self):
        """Test that multiple type annotation errors are detected"""
        source = """
        func test() : void = {
            val a : i64 = 1000
            val b : f64 = 3.14
            
            mut x : i32 = 0
            mut y : f32 = 0.0
            
            // Multiple precision loss cases
            x = a           // Error 1: i64 → i32
            y = b           // Error 2: f64 → f32
            x = b : f32     // Error 3: Wrong annotation type
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        # Check for specific error types
        error_messages = [e.message for e in errors]
        assert any("Potential truncation" in msg for msg in error_messages)
        assert any("Potential precision loss" in msg for msg in error_messages)
        assert any("Type annotation must match" in msg for msg in error_messages)


class TestTypeAnnotationIntegration:
    """Test type annotation integration with other language features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_annotation_with_expression_blocks(self):
        """Test type annotations work in expression blocks"""
        source = """
        func test() : i32 = {
            val large : i64 = 1000000
            
            val result : i32 = {
                val temp = large * 2
                return temp : i32     // Explicit acknowledgment in expression block
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_annotation_with_binary_operations(self):
        """Test type annotations integrate properly with binary operations"""
        source = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            val c : f32 = 3.14
            val d : f64 = 2.718
            
            // Mixed operations with proper type annotations
            val int_result : i64 = (a + b) : i64      // Mixed int → i64
            val float_result : f64 = (c + d) : f64    // Mixed float → f64
            val cross_result : f64 = (a + c) : f64    // Int + float → f64
            
            // Division operations with type annotations
            val float_div : f64 = (a / b) : f64       // Force float division
            val int_div : i64 = (a \ b) : i64         // Force integer division
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    # COMMENTED OUT: Requires function parameters (Phase 1.1 Parser Extensions)
    # def test_type_annotation_consistency_across_contexts(self):
    #     """Test that type annotation rules are consistent across all contexts"""
    #     source = """
    #     func compute(x: i64) : i64 = {
    #         return x * 2
    #     }
    #
    #     func test() : i32 = {
    #         val large : i64 = 1000000
    #         mut accumulator : i32 = 0
    #
    #         // Variable declaration context
    #         val truncated : i32 = large : i32
    #
    #         // Assignment context
    #         accumulator = large : i32
    #
    #         // Function return context - explicit acknowledgment
    #         return compute(large) : i32
    #     }
    #     """
    #     ast = self.parser.parse(source)
    #     errors = self.analyzer.analyze(ast)
    #     assert errors == []
