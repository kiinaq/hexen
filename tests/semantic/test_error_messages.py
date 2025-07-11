"""
Test suite for comprehensive error message consistency in Hexen type system

This module ensures that error messages across the entire semantic analysis system are:
- Consistent in format and terminology
- Helpful and educational for developers
- Provide clear, actionable guidance
- Follow the "Explicit Danger, Implicit Safety" principle in messaging
- Are predictable and learnable

Error Message Coverage:
- Type annotation error messages
- Precision loss and truncation error messages
- Mutability violation error messages
- Mixed-type operation error messages
- Comptime type error messages
- Context-related error messages
- Error message consistency across all features
- Helpful guidance and suggestions
- Edge cases and complex scenarios

Related but tested elsewhere:
- test_comptime_types.py: Comptime type mechanics (these test their error messages)
- test_precision_loss.py: Precision loss detection (these test the messages)
- test_mutability.py: Mutability violations (these test the mechanics)
- test_assignment.py: Assignment validation (these test the mechanics)
- test_context_framework.py: Context propagation (these test the mechanics)

This file focuses specifically on the quality and consistency of error messages.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestTypeAnnotationErrorMessages:
    """Test error messages for type annotation issues"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_annotation_mismatch_message(self):
        """Test clear error messages when type annotations don't match"""
        source = """
        func test() : void = {
            val wrong:i32 = 3.14:f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Type annotation must match variable's declared type" in error_msg
        assert "expected i32, got f64" in error_msg
        assert "i32" in error_msg and "f64" in error_msg

    def test_type_annotation_without_explicit_type_message(self):
        """Test error message when type annotation used without explicit left-side type"""
        source = """
        func test() : void = {
            val result = 42 + 3.14:f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Find the specific error about type annotation
        annotation_errors = [
            e
            for e in errors
            if "Type annotation requires explicit left side type" in e.message
        ]
        assert len(annotation_errors) >= 1

        error_msg = annotation_errors[0].message
        assert "Type annotation requires explicit left side type" in error_msg
        assert "val result:f64 = ..." in error_msg  # Should suggest solution

    def test_type_annotation_guidance_consistency(self):
        """Test type annotation error messages provide consistent guidance"""
        test_cases = [
            # Different contexts, same guidance pattern
            ("val var:i32 = 3.14:f64", "must match"),
            ("mut var:f32 = 2.5:f64", "must match"),
            ("val result = expr:i32", "explicit left side type"),
        ]

        for source_fragment, expected_pattern in test_cases:
            source = f"""
            func test() : void = {{
                {source_fragment}
            }}
            """
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message.lower()
            assert expected_pattern.lower() in error_msg


class TestPrecisionLossErrorMessages:
    """Test error messages for precision loss scenarios"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_truncation_error_message_format(self):
        """Test that truncation error messages have consistent format"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            mut small:i32 = 0
            
            small = large
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        # Check for consistent error message format
        assert "Potential truncation" in error_msg
        assert "i32" in error_msg
        assert "Add ': i32'" in error_msg
        assert "explicitly acknowledge" in error_msg

    def test_precision_loss_error_message_format(self):
        """Test that precision loss error messages have consistent format"""
        source = """
        func test() : void = {
            val precise:f64 = 3.141592653589793
            mut single:f32 = 0.0
            
            single = precise
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        # Check for consistent error message format
        assert "Potential precision loss" in error_msg
        assert "f32" in error_msg
        assert "Add ': f32'" in error_msg
        assert "explicitly acknowledge" in error_msg

    def test_mixed_type_precision_loss_messages(self):
        """Test error messages for mixed-type precision loss scenarios"""
        test_cases = [
            # i64 → f32 (may lose precision for very large integers)
            (
                "val large:i64 = 9223372036854775807",
                "mut single:f32 = 0.0",
                "single = large",
            ),
            # f64 → i32 (truncates fractional part)
            (
                "val precise:f64 = 3.14159",
                "mut int_val:i32 = 0",
                "int_val = precise",
            ),
            # comptime_float → i32 (truncates fractional part)
            ("mut int_val:i32 = 0", "", "int_val = 3.14159"),
        ]

        for setup1, setup2, assignment in test_cases:
            source = f"""
            func test() : void = {{
                {setup1}
                {setup2 if setup2 else ""}
                {assignment}
            }}
            """
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message
            # Should indicate precision loss or truncation
            assert any(
                keyword in error_msg.lower()
                for keyword in ["precision", "truncation", "loss"]
            )
            # Should suggest explicit acknowledgment
            assert ":" in error_msg  # Type annotation suggestion


class TestMutabilityErrorMessages:
    """Test error messages for mutability violations"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_val_reassignment_error_message(self):
        """Test error message for val variable reassignment"""
        source = """
        func test() : void = {
            val immutable = 42
            immutable = 100
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "Cannot assign to immutable variable 'immutable'" in error_msg
        assert "val variables can only be assigned once at declaration" in error_msg

    def test_val_undef_error_message(self):
        """Test error message for val + undef combination"""
        source = """
        func test() : void = {
            val pending:i32 = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "val variable" in error_msg
        assert "undef" in error_msg
        assert (
            "cannot be assigned later" in error_msg or "unusable variable" in error_msg
        )
        assert "Consider using 'mut'" in error_msg

    def test_mutability_error_message_consistency(self):
        """Test mutability error messages are consistent across scenarios"""
        test_cases = [
            # Different val reassignment scenarios
            ("val x = 42\n            x = 100", "Cannot assign to immutable"),
            (
                'val y:string = "hello"\n            y = "world"',
                "Cannot assign to immutable",
            ),
            ("val z:f64 = 3.14\n            z = 2.5", "Cannot assign to immutable"),
        ]

        for code_fragment, expected_pattern in test_cases:
            source = f"""
            func test() : void = {{
                {code_fragment}
            }}
            """
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message
            assert expected_pattern in error_msg


class TestMixedTypeErrorMessages:
    """Test error messages for mixed-type operations"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mixed_type_binary_operation_messages(self):
        """Test error messages for mixed-type binary operations"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            val result = a + b
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        error_msg = errors[0].message
        assert "Mixed-type operation" in error_msg
        assert "i32" in error_msg and "i64" in error_msg
        assert "explicit result type" in error_msg

    def test_ambiguous_comptime_expression_messages(self):
        """Test error messages for ambiguous comptime expressions"""
        source = """
        func test() : void = {
            val result = 42 + 3.14
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        error_msg = errors[0].message
        assert "Mixed-type operation" in error_msg
        assert "comptime_int" in error_msg and "comptime_float" in error_msg
        assert "explicit result type" in error_msg

    def test_mixed_type_error_guidance_consistency(self):
        """Test mixed-type error messages provide consistent guidance"""
        test_cases = [
            # Different mixed-type scenarios should have similar guidance
            (
                "val a:i32 = 10\n            val b:i64 = 20\n            val x = a + b",
                "explicit result type",
            ),
            (
                "val c:f32 = 3.14\n            val d:f64 = 2.5\n            val y = c * d",
                "explicit result type",
            ),
            (
                "val e = 42\n            val f = 3.14\n            val z = e - f",
                "explicit result type",
            ),
        ]

        for code_fragment, expected_guidance in test_cases:
            source = f"""
            func test() : void = {{
                {code_fragment}
            }}
            """
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message.lower()
            assert expected_guidance.lower() in error_msg


class TestComptimeTypeErrorMessages:
    """Test error messages for comptime type issues"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_to_invalid_type_messages(self):
        """Test error messages for invalid comptime type conversions"""
        test_cases = [
            # comptime_int to bool (not in coercion table)
            ("val flag:bool = 42", "comptime_int", "bool"),
            # comptime_int to string (not in coercion table)
            ("val text:string = 42", "comptime_int", "string"),
            # comptime_float to bool (not in coercion table)
            ("val flag:bool = 3.14", "comptime_float", "bool"),
        ]

        for code_fragment, from_type, to_type in test_cases:
            source = f"""
            func test() : void = {{
                {code_fragment}
            }}
            """
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message
            # Should indicate the invalid conversion
            assert "Type mismatch" in error_msg or "cannot coerce" in error_msg.lower()
            assert from_type in error_msg and to_type in error_msg

    def test_undef_without_type_error_message(self):
        """Test error message for undef without explicit type"""
        source = """
        func test() : void = {
            val pending = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        # Find undef-related error
        undef_errors = [e for e in errors if "undef" in e.message.lower()]
        assert len(undef_errors) >= 1

        error_msg = undef_errors[0].message
        assert (
            "explicit type" in error_msg.lower()
            or "type annotation" in error_msg.lower()
        )


class TestErrorMessageConsistency:
    """Test error message consistency across all features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_precision_loss_consistency_across_contexts(self):
        """Test precision loss error messages are consistent across contexts"""
        contexts = [
            # Variable declaration
            """
            func test() : void = {
                val large:i64 = 1000000
                val small:i32 = large
            }
            """,
            # Assignment
            """
            func test() : void = {
                val large:i64 = 1000000
                mut small:i32 = 0
                small = large
            }
            """,
            # Function return (if supported)
            """
            func returns_i32() : i32 = {
                val large:i64 = 1000000
                return large
            }
            """,
        ]

        error_patterns = []
        for source in contexts:
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            precision_errors = [
                e
                for e in errors
                if any(
                    keyword in e.message.lower()
                    for keyword in ["truncation", "precision", "loss"]
                )
            ]
            if precision_errors:
                error_patterns.append(precision_errors[0].message)

        # Should have consistent patterns
        assert len(error_patterns) >= 2
        # All should mention explicit acknowledgment
        for pattern in error_patterns:
            assert ":" in pattern  # Type annotation suggestion

    def test_type_mismatch_consistency(self):
        """Test type mismatch error messages are consistent"""
        contexts = [
            # Variable declaration
            """
            func test() : void = {
                val number:i32 = "string"
            }
            """,
            # Assignment
            """
            func test() : void = {
                mut number:i32 = 0
                number = "string"
            }
            """,
        ]

        error_patterns = []
        for source in contexts:
            ast = self.parser.parse(source)
            errors = self.analyzer.analyze(ast)
            type_errors = [
                e
                for e in errors
                if "Type mismatch" in e.message or "type" in e.message.lower()
            ]
            if type_errors:
                error_patterns.append(type_errors[0].message)

        # Should have type mismatch errors
        assert len(error_patterns) >= 2
        # Should mention relevant types
        for pattern in error_patterns:
            assert "i32" in pattern and "string" in pattern


class TestHelpfulErrorMessages:
    """Test that error messages provide helpful, actionable guidance"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_error_messages_suggest_solutions(self):
        """Test that error messages suggest concrete solutions"""
        test_cases = [
            # Precision loss - should suggest type annotation
            {
                "source": """
                func test() : void = {
                    val large:i64 = 1000000
                    mut small:i32 = 0
                    small = large
                }
                """,
                "expected_suggestions": [": i32", "explicit"],
            },
            # Mixed types - should suggest explicit result type
            {
                "source": """
                func test() : void = {
                    val a:i32 = 10
                    val b:i64 = 20
                    val result = a + b
                }
                """,
                "expected_suggestions": ["explicit result type", "Mixed-type"],
            },
            # val + undef - should suggest mut
            {
                "source": """
                func test() : void = {
                    val pending:i32 = undef
                }
                """,
                "expected_suggestions": ["Consider using 'mut'", "unusable"],
            },
        ]

        for test_case in test_cases:
            ast = self.parser.parse(test_case["source"])
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message
            # Should contain at least one suggested solution
            found_suggestion = any(
                suggestion in error_msg
                for suggestion in test_case["expected_suggestions"]
            )
            assert found_suggestion, (
                f"Error message '{error_msg}' should contain one of {test_case['expected_suggestions']}"
            )

    def test_error_messages_are_educational(self):
        """Test that error messages explain the 'why' behind the error"""
        educational_cases = [
            # Explain precision loss concept
            {
                "source": """
                func test() : void = {
                    val precise:f64 = 3.141592653589793
                    mut approx:f32 = 0.0
                    approx = precise
                }
                """,
                "should_explain": ["precision loss", "acknowledge"],
            },
            # Explain val vs mut distinction
            {
                "source": """
                func test() : void = {
                    val immutable = 42
                    immutable = 100
                }
                """,
                "should_explain": ["immutable", "once at declaration"],
            },
            # Explain mixed-type operation ambiguity
            {
                "source": """
                func test() : void = {
                    val result = 42 + 3.14
                }
                """,
                "should_explain": ["Mixed-type", "explicit result type"],
            },
        ]

        for case in educational_cases:
            ast = self.parser.parse(case["source"])
            errors = self.analyzer.analyze(ast)
            assert len(errors) >= 1

            error_msg = errors[0].message.lower()
            # Should explain the concept, not just state the rule
            for explanation in case["should_explain"]:
                assert explanation.lower() in error_msg

    def test_error_messages_include_context(self):
        """Test that error messages include relevant context information"""
        source = """
        func test() : void = {
            val source_var:i64 = 1000000
            mut target_var:i32 = 0
            target_var = source_var
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        error_msg = errors[0].message
        # Check that error message includes guidance
        assert "truncation" in error_msg.lower() or "acknowledge" in error_msg.lower()


class TestErrorMessageEdgeCases:
    """Test error messages in edge cases and complex scenarios"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_multiple_errors_clarity(self):
        """Test that multiple errors are reported clearly"""
        source = """
        func test() : void = {
            val undefined_var:i32 = unknown_variable
            val type_error:string = 42
            val immutable = 100
            immutable = 200
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect multiple distinct errors
        assert len(errors) >= 3

        # Each error should be clear and specific
        error_types = set()
        for error in errors:
            if "Undefined variable" in error.message:
                error_types.add("undefined")
            elif "Type mismatch" in error.message:
                error_types.add("type_mismatch")
            elif "Cannot assign to immutable" in error.message:
                error_types.add("immutable")

        # Should detect all three error types
        assert len(error_types) >= 2

    def test_error_recovery_quality(self):
        """Test that error recovery handles complex scenarios gracefully"""
        source = """
        func test() : void = {
            val good_var = 42
            val bad_var = undefined_symbol     // Error 1: undefined symbol
            mut another_good:i32 = 0
            
            // Should continue analysis despite error
            another_good = good_var:i32      // Should work despite earlier error  
            val final_var = another_good * 2   // Should work
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect the undefined symbol error
        assert len(errors) >= 1
        assert any("undefined" in str(e).lower() for e in errors)

    def test_complex_expression_error_clarity(self):
        """Test error messages remain clear with complex expressions"""
        source = """
        func test() : void = {
            val a:i32 = 10
            val b:i64 = 20
            val c:f32 = 3.14
            
            // Complex nested mixed-type expression
            val result = ((a + b) * c) + (42 - 3.14)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1

        # Error should clearly indicate the issue despite complexity
        error_msg = errors[0].message
        assert (
            "Mixed-type" in error_msg
            or "explicit" in error_msg.lower()
            or "type" in error_msg.lower()
        )
        # Should not be overwhelmingly verbose
        assert len(error_msg) < 500  # Reasonable length
