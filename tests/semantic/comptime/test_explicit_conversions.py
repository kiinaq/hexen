"""
Test explicit conversion semantic analysis.

Tests the conversion analyzer implementation following TYPE_SYSTEM.md rules:
- Valid comptime type conversions (ergonomic)
- Valid concrete type conversions (explicit)
- Invalid conversions with clear error messages
- Integration with expression analysis
"""

from tests.semantic import (
    StandardTestBase,
    assert_no_errors,
)


class TestExplicitConversionSemantics(StandardTestBase):
    """Test semantic analysis of explicit conversions per TYPE_SYSTEM.md"""

    def _analyze_source(self, source: str):
        """Helper to parse and analyze source code"""
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        return errors

    def test_valid_comptime_int_conversions(self):
        """Test valid comptime_int conversions per TYPE_SYSTEM.md"""
        test_cases = [
            ("42:i32", "i32"),
            ("42:i64", "i64"),
            ("42:f32", "f32"),
            ("42:f64", "f64"),
            ("-100:i32", "i32"),
            ("0:i64", "i64"),
        ]

        for i, (expr, target_type) in enumerate(test_cases):
            source = f"""
            func test_{i}() : void = {{
                val result : {target_type} = {expr}
            }}
            """
            errors = self._analyze_source(source)
            assert_no_errors(errors)

    def test_valid_comptime_float_conversions(self):
        """Test valid comptime_float conversions per TYPE_SYSTEM.md"""
        test_cases = [
            ("3.14:f32", "f32"),
            ("3.14:f64", "f64"),
            ("-2.5:f32", "f32"),
            ("0.0:f64", "f64"),
            # Explicit conversions with potential data loss
            ("3.14:i32", "i32"),
            ("3.14:i64", "i64"),
        ]

        for i, (expr, target_type) in enumerate(test_cases):
            source = f"""
            func test_{i}() : void = {{
                val result : {target_type} = {expr}
            }}
            """
            errors = self._analyze_source(source)
            assert_no_errors(errors)

    def test_valid_concrete_conversions(self):
        """Test valid concrete type conversions per TYPE_SYSTEM.md"""
        source = """
        func test() : void = {
            val int_val:i32 = 10
            val float_val:f32 = 3.14
            
            val widened:i64 = int_val:i64
            val converted:f64 = int_val:f64
            val precise:f64 = float_val:f64
            val narrowed:i32 = float_val:i32
        }
        """
        errors = self._analyze_source(source)
        assert_no_errors(errors)

    def test_invalid_conversions_to_bool(self):
        """Test that conversions to bool are forbidden with clear guidance"""
        invalid_cases = [
            "42:bool",
            "3.14:bool",
            "int_val:bool",
            "float_val:bool",
        ]

        for i, expr in enumerate(invalid_cases):
            source = f"""
            func test_{i}() : void = {{
                val int_val:i32 = 10
                val float_val:f32 = 3.14
                val result:bool = {expr}
            }}
            """
            errors = self._analyze_source(source)
            assert len(errors) > 0, f"Conversion {expr} should be invalid"
            assert any(
                "bool" in error.message and "explicit comparison" in error.message
                for error in errors
            ), f"Error should suggest explicit comparison for {expr}"

    def test_invalid_conversions_to_string(self):
        """Test that conversions to string are forbidden with clear guidance"""
        invalid_cases = [
            "42:string",
            "3.14:string",
            "true:string",
        ]

        for i, expr in enumerate(invalid_cases):
            source = f"""
            func test_{i}() : void = {{
                val result:string = {expr}
            }}
            """
            errors = self._analyze_source(source)
            assert len(errors) > 0, f"Conversion {expr} should be invalid"
            assert any(
                "string" in error.message and "formatting functions" in error.message
                for error in errors
            ), f"Error should suggest formatting functions for {expr}"

    def test_invalid_conversions_from_bool(self):
        """Test that conversions from bool are forbidden with clear guidance"""
        invalid_cases = [
            ("true:i32", "i32"),
            ("false:i64", "i64"),
            ("flag:f32", "f32"),
        ]

        for i, (expr, target_type) in enumerate(invalid_cases):
            source = f"""
            func test_{i}() : void = {{
                val flag:bool = true
                val result : {target_type} = {expr}
            }}
            """
            errors = self._analyze_source(source)
            assert len(errors) > 0, f"Conversion {expr} should be invalid"
            assert any("conditional expression" in error.message for error in errors), (
                f"Error should suggest conditional expression for {expr}"
            )

    def test_invalid_conversions_from_string(self):
        """Test that conversions from string are forbidden with clear guidance"""
        invalid_cases = [
            ("text:i32", "i32"),
            ("text:f64", "f64"),
            ("text:bool", "bool"),
        ]

        for i, (expr, target_type) in enumerate(invalid_cases):
            source = f"""
            func test_{i}() : void = {{
                val text:string = "123"
                val result : {target_type} = {expr}
            }}
            """
            errors = self._analyze_source(source)
            assert len(errors) > 0, f"Conversion {expr} should be invalid"
            # Check for appropriate error message based on target type
            if target_type == "bool":
                assert any(
                    "explicit comparison" in error.message for error in errors
                ), f"Error should suggest explicit comparison for {expr}"
            else:
                assert any("parsing functions" in error.message for error in errors), (
                    f"Error should suggest parsing functions for {expr}"
                )

    def test_identity_conversions(self):
        """Test that identity conversions (same type) are valid"""
        test_cases = [
            ("42", "comptime_int", "42:i32", "i32"),
            ("int_val", "i32", "int_val:i32", "i32"),
            ("float_val", "f64", "float_val:f64", "f64"),
            ("text", "string", "text:string", "string"),
        ]

        for i, (source_expr, source_type, conv_expr, target_type) in enumerate(
            test_cases
        ):
            if source_type == "comptime_int":
                source = f"""
                func test_{i}() : void = {{
                    val result : {target_type} = {conv_expr}
                }}
                """
            else:
                # Build proper variable declaration based on type
                if source_expr == "text":
                    var_decl = 'val text : string = "hello"'
                elif source_expr == "int_val":
                    var_decl = "val int_val : i32 = 42"
                elif source_expr == "float_val":
                    var_decl = "val float_val : f64 = 3.14"
                else:
                    var_decl = f"val {source_expr} : {source_type} = 42"

                source = f"""
                func test_{i}() : void = {{
                    {var_decl}
                    val result : {target_type} = {conv_expr}
                }}
                """

            errors = self._analyze_source(source)
            assert len(errors) == 0, (
                f"Identity conversion {conv_expr} should be valid but got errors: {[e.message for e in errors]}"
            )

    def test_complex_expression_conversions(self):
        """Test conversions with complex expressions (parenthesized literals for now)"""
        source = """
        func test() : void = {
            val result1:i64 = (42):i64
            val result2:f32 = (100):f32
            val result3:f64 = (3.14):f64
        }
        """
        errors = self._analyze_source(source)
        assert len(errors) == 0, (
            f"Complex expression conversions should be valid but got errors: {[e.message for e in errors]}"
        )

    def test_conversion_error_recovery(self):
        """Test that conversion errors are reported but analysis continues"""
        source = """
        func test() : void = {
            val bad1:bool = 42:bool
            val good:i64 = 42:i64
            val bad2:string = 3.14:string
            val also_good:f32 = 3.14:f32
        }
        """
        errors = self._analyze_source(source)

        # Should have 2 errors (bool and string conversions)
        assert len(errors) == 2, (
            f"Expected 2 errors but got {len(errors)}: {[e.message for e in errors]}"
        )

        # Check that both error types are present
        bool_error_found = any("bool" in error.message for error in errors)
        string_error_found = any("string" in error.message for error in errors)

        assert bool_error_found, "Should have error for bool conversion"
        assert string_error_found, "Should have error for string conversion"

    def test_conversion_in_different_contexts(self):
        """Test conversions work in different expression contexts"""
        source = """
        func get_value() : i64 = {
            return 42:i64
        }
        
        func test() : void = {
            val in_declaration:f32 = 3.14:f32
            
            mut mutable:i32 = 0
            mutable = 100:i32
        }
        """
        errors = self._analyze_source(source)
        assert len(errors) == 0, (
            f"Conversions in different contexts should be valid but got errors: {[e.message for e in errors]}"
        )


class TestConversionIntegration(StandardTestBase):
    """Test conversion analyzer integration with the broader semantic analysis"""

    def _analyze_source(self, source: str):
        """Helper to parse and analyze source code"""
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        return errors

    def test_conversion_with_symbol_lookup(self):
        """Test conversions work correctly with symbol table integration"""
        source = """
        func test() : void = {
            val source_val:i32 = 42
            val converted:i64 = source_val:i64
            val also_converted:f64 = source_val:f64
        }
        """
        errors = self._analyze_source(source)
        assert len(errors) == 0, (
            f"Conversion with symbol lookup should work but got errors: {[e.message for e in errors]}"
        )

    def test_conversion_with_undefined_variable_error(self):
        """Test that undefined variable errors are properly handled in conversions"""
        source = """
        func test() : void = {
            val result:i64 = undefined_var:i64
        }
        """
        errors = self._analyze_source(source)
        assert len(errors) > 0, "Should have error for undefined variable"
        assert any("undefined" in error.message.lower() for error in errors), (
            "Should have undefined variable error"
        )

    def test_conversion_with_uninitialized_variable_error(self):
        """Test that uninitialized variable errors are properly handled in conversions"""
        source = """
        func test() : void = {
            mut uninitialized:i32 = undef
            val result:i64 = uninitialized:i64
        }
        """
        errors = self._analyze_source(source)
        assert len(errors) > 0, "Should have error for uninitialized variable"
        assert any("uninitialized" in error.message.lower() for error in errors), (
            "Should have uninitialized variable error"
        )
