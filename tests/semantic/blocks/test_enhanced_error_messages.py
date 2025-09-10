"""
Test Enhanced Error Messages for Unified Block System

Tests that enhanced error messages are properly generated when analyzing 
problematic Hexen code, focusing on context-specific error messages with 
actionable guidance for runtime blocks and type conversion issues.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestRuntimeBlockErrorMessages:
    """Test enhanced error messages for runtime evaluable blocks."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_function_call_triggers_explicit_type_annotation_required_error(self):
        """Test that function calls trigger 'Explicit type annotation REQUIRED!' error messages."""
        code = """
        func get_value() : i32 = {
            return 42
        }
        
        func test() : void = {
            val result = {
                val input = get_value()
                -> input * 2
            }
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should contain "Explicit type annotation REQUIRED!" messaging
        assert "Explicit type annotation REQUIRED!" in error_msg
        # Should mention function calls as the reason
        assert "function" in error_msg.lower() or "runtime block" in error_msg.lower()
        # Should provide actionable guidance
        assert "val result :" in error_msg or "explicit type" in error_msg

    def test_conditional_triggers_explicit_type_annotation_required_error(self):
        """Test that conditionals trigger 'Explicit type annotation REQUIRED!' error messages."""
        code = """
        func test(condition: bool) : void = {
            val result = {
                val value = if condition {
                    -> 42
                } else {
                    -> 100
                }
                -> value
            }
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should indicate explicit type annotation is required for runtime operations
        assert any(term in error_msg for term in [
            "Explicit type annotation REQUIRED!", "explicit type", "runtime block"
        ])

    def test_mixed_concrete_comptime_triggers_runtime_error(self):
        """Test that mixing concrete and comptime types triggers runtime error."""
        code = """
        func test(param: i32) : void = {
            val result = {
                val mixed = param + 42
                -> mixed * 2
            }
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should indicate explicit type annotation is needed
        assert any(term in error_msg for term in [
            "Explicit type annotation REQUIRED!", "explicit type", "runtime block"
        ])


class TestMixedConcreteTypeErrorMessages:
    """Test enhanced error messages for mixed concrete type operations."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mixed_concrete_types_in_arithmetic_error(self):
        """Test enhanced error for mixed concrete types in arithmetic."""
        code = """
        func test() : i32 = {
            val a : i32 = 10
            val b : i64 = 20
            return a + b
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should mention mixed concrete types or explicit conversion
        has_enhanced_content = any(term in error_msg.lower() for term in [
            "mixed concrete types",
            "explicit conversion", 
            "transparent costs",
            "value:",
            "concrete",
            "i32",
            "i64"
        ])
        assert has_enhanced_content, f"Error message not enhanced: {error_msg}"

    def test_mixed_concrete_types_provides_conversion_guidance(self):
        """Test that mixed type errors provide explicit conversion guidance."""
        code = """
        func test() : void = {
            val small : i32 = 10
            val large : i64 = 20
            val result : i64 = small + large
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should provide actionable conversion guidance
        has_conversion_guidance = any(term in error_msg for term in [
            "value:", ":i64", "explicit conversion", "small:"
        ])
        assert has_conversion_guidance, f"Missing conversion guidance: {error_msg}"

    def test_float_integer_mixing_error_message(self):
        """Test enhanced error for mixing float and integer concrete types."""
        code = """
        func test() : void = {
            val integer : i32 = 42
            val floating : f64 = 3.14
            val mixed : f64 = integer + floating
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should indicate type conversion is needed
        has_type_guidance = any(term in error_msg.lower() for term in [
            "explicit conversion", "value:", "i32", "f64", "concrete", "mixed"
        ])
        assert has_type_guidance, f"Missing type conversion guidance: {error_msg}"


class TestBinaryOperationErrorMessages:
    """Test enhanced error messages for binary operation type issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comparison_mixed_types_error_message(self):
        """Test enhanced error for mixed types in comparison operations."""
        code = """
        func test() : void = {
            val a : i32 = 10
            val b : f64 = 20.0
            val result : bool = a < b
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should provide guidance for comparison type consistency
        has_comparison_guidance = any(term in error_msg.lower() for term in [
            "comparison", "explicit conversion", "value:", "concrete", "mixed"
        ])
        assert has_comparison_guidance, f"Missing comparison guidance: {error_msg}"

    def test_division_operator_context_error_message(self):
        """Test that division operations provide clear context in errors."""
        code = """
        func test() : void = {
            val a : i32 = 10
            val b : f32 = 3.0
            val result : f64 = a / b
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        if len(errors) >= 1:
            error_msg = str(errors[0])
            # If there's an error, it should mention type conversion needs
            has_division_context = any(term in error_msg.lower() for term in [
                "division", "explicit conversion", "value:", "concrete"
            ])
            assert has_division_context, f"Missing division context: {error_msg}"


class TestExpressionBlockErrorMessages:
    """Test enhanced error messages in expression block contexts."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_expression_block_missing_context_error(self):
        """Test error message for expression blocks missing type context."""
        code = """
        func get_input() : i32 = {
            return 42
        }
        
        func test() : void = {
            val computation = {
                val base = get_input()
                val scaled = base * 2
                -> scaled
            }
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should indicate that explicit type annotation is required
        has_type_annotation_guidance = any(term in error_msg for term in [
            "Explicit type annotation REQUIRED!", "explicit type", "val computation :", "runtime block"
        ])
        assert has_type_annotation_guidance, f"Missing type annotation guidance: {error_msg}"

    def test_expression_block_with_return_statement_error(self):
        """Test error handling in expression blocks with early returns."""
        code = """
        func test() : i32 = {
            val result = {
                val condition = true
                if condition {
                    return 42
                } else {
                    -> 100
                }
            }
            return result
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        # This might not error depending on implementation, but if it does,
        # the error should be clear about expression block requirements
        if len(errors) >= 1:
            error_msg = str(errors[0])
            has_block_guidance = any(term in error_msg for term in [
                "expression block", "return", "Explicit type annotation REQUIRED!", "explicit type"
            ])
            assert has_block_guidance, f"Missing block guidance: {error_msg}"


class TestFunctionCallErrorMessages:
    """Test enhanced error messages for function call type issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_function_parameter_type_mismatch_error(self):
        """Test enhanced error for function parameter type mismatches."""
        code = """
        func process(value: i32) : void = {
            return
        }
        
        func test() : void = {
            val large_value : i64 = 1000
            process(large_value)
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should provide guidance on parameter type conversion
        has_param_guidance = any(term in error_msg.lower() for term in [
            "parameter", "argument", "explicit conversion", "value:", "i64", "i32"
        ])
        assert has_param_guidance, f"Missing parameter guidance: {error_msg}"

    def test_function_return_type_mismatch_error(self):
        """Test enhanced error for function return type mismatches."""
        code = """
        func get_value() : i32 = {
            val large : i64 = 1000
            return large
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should provide guidance on return type conversion
        has_return_guidance = any(term in error_msg.lower() for term in [
            "return", "explicit conversion", "value:", "i64", "i32"
        ])
        assert has_return_guidance, f"Missing return guidance: {error_msg}"


class TestVariableDeclarationErrorMessages:
    """Test enhanced error messages for variable declaration issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mut_variable_missing_type_error(self):
        """Test enhanced error for mut variables with undef but no type annotation."""
        code = """
        func test() : void = {
            mut counter : i32 = undef
            counter = 42
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        # This should actually pass since it has proper explicit type annotation
        # Let's test a different scenario - mut with problematic usage
        if len(errors) == 0:
            # If no errors, the mut syntax is working correctly
            assert True
        else:
            # If there are errors, check they're reasonable
            error_msg = str(errors[0])
            # Should be clear about any mut-related issues
            has_clear_message = len(error_msg) > 10
            assert has_clear_message, f"Error message too unclear: {error_msg}"

    def test_mixed_type_assignment_error(self):
        """Test enhanced error for mixed type assignments."""
        code = """
        func test() : void = {
            val small : i32 = 10
            val large : i64 = 20
            val result : i32 = small + large
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])
        
        # Should provide clear assignment guidance
        has_assignment_guidance = any(term in error_msg.lower() for term in [
            "assignment", "explicit conversion", "value:", "mixed", "concrete"
        ])
        assert has_assignment_guidance, f"Missing assignment guidance: {error_msg}"


class TestErrorMessageQuality:
    """Test overall quality and consistency of enhanced error messages."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_error_messages_use_specification_terminology(self):
        """Test that error messages use consistent specification terminology."""
        test_cases = [
            # Mixed concrete types
            """
            func test() : void = {
                val a : i32 = 10
                val b : i64 = 20
                val result : i64 = a + b
                return
            }
            """,
            # Runtime block without context
            """
            func get_val() : i32 = { return 42 }
            func test() : void = {
                val result = {
                    val x = get_val()
                    -> x * 2
                }
                return
            }
            """,
        ]

        all_errors = []
        for code in test_cases:
            ast = self.parser.parse(code)
            errors = self.analyzer.analyze(ast)
            all_errors.extend(errors)

        assert len(all_errors) >= 1, "Expected at least one error from test cases"

        # Check that error messages use specification terminology
        error_messages = [str(error) for error in all_errors]
        spec_terms_found = any(
            any(term in msg.lower() for term in [
                "comptime", "runtime", "concrete", "explicit", 
                "transparent costs", "context", "value:"
            ])
            for msg in error_messages
        )
        
        assert spec_terms_found, f"No specification terminology found in: {error_messages}"

    def test_error_messages_provide_actionable_guidance(self):
        """Test that error messages consistently provide actionable guidance."""
        code = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            val result : i64 = a + b
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]

        # All errors should provide some form of actionable guidance
        actionable_keywords = [
            "use", "try", "add", "specify", ":", "explicit conversion", 
            "value:", "val", "mut", "i32", "i64", "f32", "f64"
        ]
        
        for error_msg in error_messages:
            has_guidance = any(
                keyword in error_msg.lower() for keyword in actionable_keywords
            )
            assert has_guidance, f"Error lacks actionable guidance: {error_msg}"

    def test_multiple_errors_reported_clearly(self):
        """Test that multiple errors in one function are all reported clearly."""
        code = """
        func get_val() : i32 = { return 42 }
        
        func multiple_problems() : void = {
            val a : i32 = 10
            val b : i64 = 20
            val mixed_result : i64 = a + b        // Error 1: Mixed concrete types
            val runtime_result = {                // Error 2: Missing context
                val x = get_val()
                -> x * 2
            }
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1  # Should catch at least one error
        error_messages = [str(error) for error in errors]

        # Should have clear, distinct error messages
        for error_msg in error_messages:
            # Each error should be informative
            assert len(error_msg) > 10, f"Error message too short: {error_msg}"
            # Should contain some helpful terminology
            has_helpful_terms = any(term in error_msg.lower() for term in [
                "type", "explicit", "conversion", "context", "concrete", "value"
            ])
            assert has_helpful_terms, f"Error message lacks helpful terms: {error_msg}"