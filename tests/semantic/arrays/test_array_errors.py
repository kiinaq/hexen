"""
Comprehensive error message quality tests for the array system.

Tests that error messages are clear, consistent, and provide actionable guidance
for common array-related errors across all array features.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_error_contains


class TestArrayLiteralErrorMessages:
    """Test error message quality for array literal issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_empty_array_context_required_error_message(self):
        """Test clear error message for empty array literals."""
        code = """
        func test() : void = {
            val empty = []
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Empty array literal requires explicit type context" in error_msg
        # Should provide actionable guidance
        assert "val array : [N]T = []" in error_msg or "[0]" in error_msg

    def test_mixed_concrete_comptime_error_message(self):
        """Test clear error message for mixed concrete/comptime elements."""
        code = """
        func test(param: i32) : void = {
            val mixed = [param, 42]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        assert "Mixed concrete/comptime element types require explicit array context" in error_msg

    def test_type_mismatch_in_array_elements_error_message(self):
        """Test clear error message for incompatible element types."""
        code = """
        func test() : void = {
            val mixed_types = [42, "string"]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should indicate type compatibility issues
        has_type_guidance = any(
            "type" in msg.lower() and ("mismatch" in msg.lower() or "incompatible" in msg.lower())
            for msg in error_messages
        )
        assert has_type_guidance, f"Missing type compatibility guidance in: {error_messages}"


class TestMultidimensionalArrayErrorMessages:
    """Test error message quality for multidimensional array issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_inconsistent_2d_structure_error_message(self):
        """Test clear error message for inconsistent 2D array structure."""
        code = """
        func test() : void = {
            val inconsistent = [[1, 2, 3], [4, 5]]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        
        # Should clearly describe the structural problem
        assert "Inconsistent inner array dimensions" in error_msg or "dimensions" in error_msg.lower()
        # Should provide specific details about the mismatch
        assert "3" in error_msg and "2" in error_msg

    def test_mixed_array_non_array_elements_error_message(self):
        """Test clear error message for mixing arrays and non-arrays."""
        code = """
        func test() : void = {
            val mixed = [[1, 2], 3]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        
        # Should clearly identify the mixed element types
        assert "not an array" in error_msg.lower() or "multidimensional" in error_msg.lower()

    def test_deep_3d_inconsistency_error_message(self):
        """Test error message for deep 3D structural inconsistencies."""
        code = """
        func test() : void = {
            val bad_cube = [
                [[1, 2], [3, 4]], 
                [[5, 6, 7], [8, 9]]
            ]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should detect structural inconsistency
        structural_error = any(
            "inconsistent" in msg.lower() or "dimensions" in msg.lower()
            for msg in error_messages
        )
        assert structural_error, f"Missing structural consistency error in: {error_messages}"


class TestArrayAccessErrorMessages:
    """Test error message quality for array access issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_invalid_index_type_error_message(self):
        """Test clear error message for non-integer array indices."""
        code = """
        func test() : void = {
            val numbers = [1, 2, 3]
            val invalid = numbers["hello"]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        
        # Should clearly state index type requirement
        assert "Array index must be integer type" in error_msg
        # Should provide guidance on valid types
        assert "i32, i64, comptime_int" in error_msg

    def test_non_array_indexing_error_message(self):
        """Test clear error message for indexing non-array types."""
        code = """
        func test() : void = {
            val not_array : i32 = 42
            val invalid = not_array[0]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should clearly indicate non-array indexing attempt
        indexing_error = any(
            "cannot index" in msg.lower() or "not an array" in msg.lower()
            for msg in error_messages
        )
        assert indexing_error, f"Missing non-array indexing error in: {error_messages}"

    def test_float_index_error_message(self):
        """Test error message for using float as array index."""
        code = """
        func test() : void = {
            val numbers = [1, 2, 3]
            val float_index : f64 = 1.5
            val invalid = numbers[float_index]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        error_msg = str(errors[0])
        
        # Should specify that integers are required
        assert "integer type" in error_msg.lower()
        assert "f64" in error_msg


class TestArrayTypeContextErrorMessages:
    """Test error message quality for array type context issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_explicit_context_type_mismatch_error_message(self):
        """Test error message for type mismatch with explicit context."""
        code = """
        func test() : void = {
            val strings : [2]i32 = ["hello", "world"]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should indicate type mismatch between expected and actual
        type_mismatch = any(
            "type mismatch" in msg.lower() or ("i32" in msg and "string" in msg.lower())
            for msg in error_messages
        )
        assert type_mismatch, f"Missing type mismatch guidance in: {error_messages}"

    def test_array_size_mismatch_error_message(self):
        """Test error message for array size mismatches with explicit context."""
        code = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2]
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should clearly indicate size mismatch
        size_mismatch = any(
            ("expected" in msg.lower() and "got" in msg.lower()) or "size mismatch" in msg.lower()
            for msg in error_messages
        )
        assert size_mismatch, f"Missing size mismatch guidance in: {error_messages}"


class TestArrayFunctionIntegrationErrorMessages:
    """Test error message quality for array/function integration issues."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_array_parameter_type_mismatch_error_message(self):
        """Test error message for array parameter type mismatches."""
        code = """
        func process(arr: [3]i32) : void = {
            return
        }
        
        func test() : void = {
            val floats = [1.1, 2.2, 3.3]
            process(floats)
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should indicate parameter type mismatch
        param_mismatch = any(
            ("parameter" in msg.lower() or "argument" in msg.lower()) and "type" in msg.lower()
            for msg in error_messages
        )
        assert param_mismatch, f"Missing parameter type mismatch error in: {error_messages}"

    def test_array_return_type_mismatch_error_message(self):
        """Test error message for array return type mismatches."""
        code = """
        func get_numbers() : [3]i32 = {
            return [1.1, 2.2, 3.3]
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]
        
        # Should indicate return type mismatch
        return_mismatch = any(
            "return" in msg.lower() and "type" in msg.lower()
            for msg in error_messages
        )
        assert return_mismatch, f"Missing return type mismatch error in: {error_messages}"


class TestComplexArrayScenarioErrorMessages:
    """Test error message quality in complex array scenarios."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_multiple_array_errors_in_single_function(self):
        """Test that multiple array errors are all reported clearly."""
        code = """
        func multiple_problems() : void = {
            val empty = []                    // Error 1: Empty array
            val inconsistent = [[1, 2], [3]]  // Error 2: Inconsistent structure
            val bad_index = empty["string"]   // Error 3: Invalid index type
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2  # Should catch multiple errors
        error_messages = [str(error) for error in errors]

        # Should catch empty array error
        empty_error = any(
            "empty array" in msg.lower() or "explicit type context" in msg.lower()
            for msg in error_messages
        )
        assert empty_error, f"Missing empty array error in: {error_messages}"

    def test_nested_array_access_error_message(self):
        """Test error messages in nested array access scenarios."""
        code = """
        func nested_problems() : void = {
            val matrix = [[1, 2], [3, 4]]
            val element = matrix[0]["invalid"]  // Invalid 2D access
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_messages = [str(error) for error in errors]

        # Should provide clear guidance about the indexing error
        indexing_guidance = any(
            "index" in msg.lower() and ("integer" in msg.lower() or "type" in msg.lower())
            for msg in error_messages
        )
        assert indexing_guidance, f"Missing indexing guidance in: {error_messages}"

    def test_array_expression_block_error_message(self):
        """Test error messages for arrays in expression blocks."""
        code = """
        func expression_block_problem() : void = {
            val result = {
                val empty = []  // Error in expression block
                -> empty
            }
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_msg = str(errors[0])

        # Should report the empty array error clearly
        assert "empty array" in error_msg.lower() or "explicit type context" in error_msg.lower()


class TestErrorMessageConsistency:
    """Test consistency of error messages across array system."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_type_mismatch_message_consistency(self):
        """Test that type mismatch error messages are consistent across contexts."""
        # Test in array literal context
        literal_code = """
        func test1() : void = {
            val mixed : [2]i32 = ["hello", "world"]
            return
        }
        """

        # Test in array access context  
        access_code = """
        func test2() : void = {
            val numbers = [1, 2, 3]
            val invalid = numbers["hello"]
            return
        }
        """

        # Analyze both contexts
        literal_ast = self.parser.parse(literal_code)
        literal_errors = self.analyzer.analyze(literal_ast)

        access_analyzer = SemanticAnalyzer()
        access_ast = self.parser.parse(access_code)
        access_errors = access_analyzer.analyze(access_ast)

        # Both should have type-related error messages
        all_errors = literal_errors + access_errors
        assert len(all_errors) >= 2

        error_messages = [str(error) for error in all_errors]

        # Check for consistent type terminology
        type_consistency = all(
            "type" in msg.lower() for msg in error_messages
        )
        assert type_consistency, f"Inconsistent type messages: {error_messages}"

    def test_actionable_guidance_consistency(self):
        """Test that error messages consistently provide actionable guidance."""
        code = """
        func guidance_test() : void = {
            val empty = []                    // Should suggest explicit context
            val numbers = [1, 2, 3]
            val bad = numbers["invalid"]      // Should suggest integer types
            return
        }
        """

        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 2
        error_messages = [str(error) for error in errors]

        # All errors should provide actionable guidance
        actionable_keywords = ["use", "try", "add", "specify", ":", "[", "i32", "i64"]
        for error_msg in error_messages:
            has_guidance = any(
                keyword in error_msg.lower() for keyword in actionable_keywords
            )
            assert has_guidance, f"Error lacks actionable guidance: {error_msg}"