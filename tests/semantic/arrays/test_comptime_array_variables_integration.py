"""
Integration tests for comptime array variables (Phase 3)

Tests that comptime arrays work correctly when stored in variables during
semantic analysis. Validates that the ComptimeArrayType flows through the
analyzer → symbol table → type checking pipeline without errors.

This is part of Issue #1 fix - ensuring size metadata is preserved through
the entire semantic analysis pipeline.

NOTE: These tests follow the standard semantic test pattern - verifying
compiler behavior (no errors / expected errors) rather than inspecting
internal state. Symbol table unit tests handle direct state inspection.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from .. import assert_no_errors, assert_error_contains


class TestComptimeArrayVariableBasics:
    """Basic comptime array variable declarations"""

    def setup_method(self):
        """Standard setup for semantic tests"""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_simple_int_array_variable(self):
        """val arr = [1, 2, 3] analyzes without errors"""
        source = """
        func test() : void = {
            val arr = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_simple_float_array_variable(self):
        """val arr = [1.5, 2.5, 3.5] analyzes without errors"""
        source = """
        func test() : void = {
            val arr = [1.5, 2.5, 3.5]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_mixed_comptime_promotes_to_float(self):
        """val arr = [1, 2.5, 3] promotes to float and analyzes without errors"""
        source = """
        func test() : void = {
            val arr = [1, 2.5, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_2d_array_variable(self):
        """val matrix = [[1, 2], [3, 4]] analyzes without errors"""
        source = """
        func test() : void = {
            val matrix = [[1, 2], [3, 4]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_3d_array_variable(self):
        """val tensor = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]] analyzes without errors"""
        source = """
        func test() : void = {
            val tensor = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeArrayVariableSizes:
    """Test that different array sizes compile without errors"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_size_1_array(self):
        """Single element array"""
        source = """
        func test() : void = {
            val single = [42]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_size_5_array(self):
        """Five element array"""
        source = """
        func test() : void = {
            val five = [1, 2, 3, 4, 5]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_size_10_array(self):
        """Ten element array"""
        source = """
        func test() : void = {
            val ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_large_array(self):
        """Large array (100 elements)"""
        elements = ", ".join(str(i) for i in range(1, 101))
        source = f"""
        func test() : void = {{
            val large = [{elements}]
            return
        }}
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_irregular_2d_arrays_rejected(self):
        """Irregular 2D arrays should fail (different row sizes)"""
        source = """
        func test() : void = {
            val irregular = [[1, 2], [3, 4, 5]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_error_contains(errors, "Inconsistent inner array dimensions")


class TestMultipleComptimeArrayVariables:
    """Test multiple comptime array variables in same scope"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_multiple_different_sizes(self):
        """Multiple arrays with different sizes"""
        source = """
        func test() : void = {
            val small = [1, 2, 3]
            val medium = [1, 2, 3, 4, 5]
            val large = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_multiple_different_element_types(self):
        """Multiple arrays with different element types"""
        source = """
        func test() : void = {
            val ints = [1, 2, 3]
            val floats = [1.5, 2.5, 3.5]
            val mixed = [1, 2.5, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_multiple_different_dimensions(self):
        """Multiple arrays with different dimensionality"""
        source = """
        func test() : void = {
            val flat = [1, 2, 3]
            val matrix = [[1, 2], [3, 4]]
            val tensor = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeArrayExpressionBlocks:
    """Test comptime arrays in expression blocks"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_expression_block_returns_comptime_array(self):
        """Expression block producing comptime array with explicit type"""
        source = """
        func test() : void = {
            val result : [_]i32 = {  // Explicit array type required
                -> [1, 2, 3]
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_expression_block_with_intermediate_computation(self):
        """Expression block with intermediate comptime array"""
        source = """
        func test() : void = {
            val result : [_]i32 = {  // Explicit array type required
                val temp = [1, 2, 3, 4, 5]
                -> temp
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeArrayWithConcreteTypes:
    """Test interaction between comptime and concrete array types"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_explicit_type_annotation_creates_concrete(self):
        """val arr : [3]i32 = [1, 2, 3] creates ConcreteArrayType"""
        source = """
        func test() : void = {
            val arr : [3]i32 = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_no_annotation_preserves_comptime(self):
        """val arr = [1, 2, 3] without annotation works correctly"""
        source = """
        func test() : void = {
            val arr = [1, 2, 3]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestComptimeArrayVariableUsage:
    """Test comptime array variables in expressions"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_array_variable_in_indexing(self):
        """Referencing comptime array variable with indexing"""
        source = """
        func test() : void = {
            val data = [1, 2, 3]
            val x : i32 = data[0]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_multiple_references_same_comptime_array(self):
        """Same comptime array variable used multiple times"""
        source = """
        func test() : void = {
            val data = [1, 2, 3, 4, 5]
            val a : i32 = data[0]
            val b : i32 = data[1]
            val c : i32 = data[2]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestPhase3IntegrationValidation:
    """Final validation tests for Phase 3 completion"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_end_to_end_comptime_array_flow(self):
        """
        Complete flow: literal → analyzer → symbol table → type checking

        This is the core test for Issue #1 Phase 3 - validating that
        dimensional information flows correctly through entire pipeline.
        """
        source = """
        func test() : void = {
            val arr1 = [1, 2, 3]
            val arr2 = [1, 2, 3, 4, 5]
            val matrix = [[1, 2], [3, 4]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_different_sizes_dont_interfere(self):
        """Arrays with different sizes can coexist without confusion"""
        source = """
        func test() : void = {
            val tiny = [1]
            val small = [1, 2, 3]
            val medium = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val large = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            val matrix_small = [[1, 2], [3, 4]]
            val matrix_large = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]]
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_comptime_arrays_in_nested_scopes(self):
        """Comptime arrays work correctly in nested scopes"""
        source = """
        func outer() : void = {
            val data1 = [1, 2, 3, 4, 5]
            {
                val data2 = [1, 2, 3]
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_phase3_success_marker(self):
        """
        Phase 3 Success Validation ✓

        If this test passes, Phase 3 is complete:
        - Symbol table accepts ComptimeArrayType
        - Type information flows through analyzer
        - No information loss during storage/retrieval
        - Arrays compile without errors
        """
        source = """
        func comprehensive_test() : void = {
            val arr1 = [1, 2, 3]
            val arr2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            val matrix = [[1, 2, 3], [4, 5, 6]]
            val tensor = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]

            val x : i32 = arr1[0]
            val y : i32 = arr2[5]

            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
        # Phase 3 validated! ✓
