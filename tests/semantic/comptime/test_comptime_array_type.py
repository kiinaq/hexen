"""
Unit Tests for ComptimeArrayType Class

Tests the core functionality of ComptimeArrayType including:
- Creation and validation
- String representations
- Utility methods (total_elements, ndim, etc.)
- Materialization compatibility checking (can_materialize_to)
- Error message generation

These tests validate the foundation of Issue #1 fix.
"""

import pytest
from src.hexen.semantic.types import ComptimeArrayType, ConcreteArrayType, HexenType


class TestComptimeArrayTypeCreation:
    """Test ComptimeArrayType instantiation and validation"""

    def test_create_1d_comptime_int_array(self):
        """Create simple 1D comptime int array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr_type.element_comptime_type == HexenType.COMPTIME_INT
        assert arr_type.dimensions == [5]
        assert str(arr_type) == "comptime_[5]int"

    def test_create_1d_comptime_float_array(self):
        """Create simple 1D comptime float array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        assert arr_type.element_comptime_type == HexenType.COMPTIME_FLOAT
        assert arr_type.dimensions == [3]
        assert str(arr_type) == "comptime_[3]float"

    def test_create_2d_comptime_array(self):
        """Create 2D comptime array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert arr_type.dimensions == [2, 3]
        assert str(arr_type) == "comptime_[2][3]int"

    def test_create_3d_comptime_array(self):
        """Create 3D comptime array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 3, 4])
        assert arr_type.dimensions == [2, 3, 4]
        assert str(arr_type) == "comptime_[2][3][4]float"

    def test_reject_non_comptime_element_type(self):
        """Cannot create comptime array with concrete element type"""
        with pytest.raises(ValueError, match="must be COMPTIME_INT or COMPTIME_FLOAT"):
            ComptimeArrayType(HexenType.I32, [5])

    def test_reject_string_element_type(self):
        """Cannot create comptime array with string element type"""
        with pytest.raises(ValueError, match="must be COMPTIME_INT or COMPTIME_FLOAT"):
            ComptimeArrayType(HexenType.STRING, [5])

    def test_reject_empty_dimensions(self):
        """Cannot create comptime array with no dimensions"""
        with pytest.raises(ValueError, match="at least one dimension"):
            ComptimeArrayType(HexenType.COMPTIME_INT, [])

    def test_reject_negative_dimension(self):
        """Cannot create comptime array with negative dimension"""
        with pytest.raises(ValueError, match="non-negative integers"):
            ComptimeArrayType(HexenType.COMPTIME_INT, [-5])

    def test_accept_zero_dimension(self):
        """Can create comptime array with zero dimension (empty array)"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [0])
        assert arr_type.dimensions == [0]
        assert str(arr_type) == "comptime_[0]int"

    def test_reject_mixed_valid_invalid_dimensions(self):
        """Cannot create comptime array with mixed valid/invalid dimensions"""
        with pytest.raises(ValueError, match="non-negative integers"):
            ComptimeArrayType(HexenType.COMPTIME_INT, [2, -3])


class TestComptimeArrayTypeStringRepresentation:
    """Test string and repr methods"""

    def test_str_1d_int(self):
        """String representation of 1D int array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [10])
        assert str(arr_type) == "comptime_[10]int"

    def test_str_1d_float(self):
        """String representation of 1D float array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [7])
        assert str(arr_type) == "comptime_[7]float"

    def test_str_2d_int(self):
        """String representation of 2D int array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [3, 4])
        assert str(arr_type) == "comptime_[3][4]int"

    def test_str_3d_float(self):
        """String representation of 3D float array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 2, 2])
        assert str(arr_type) == "comptime_[2][2][2]float"

    def test_repr_format(self):
        """Repr shows constructor call format"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        repr_str = repr(arr_type)
        assert "ComptimeArrayType" in repr_str
        assert "COMPTIME_INT" in repr_str
        assert "[5]" in repr_str


class TestComptimeArrayTypeEquality:
    """Test equality and hashing"""

    def test_equal_same_values(self):
        """Two arrays with same type and dimensions are equal"""
        arr1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        arr2 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr1 == arr2

    def test_not_equal_different_element_type(self):
        """Arrays with different element types are not equal"""
        arr1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        arr2 = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [5])
        assert arr1 != arr2

    def test_not_equal_different_dimensions(self):
        """Arrays with different dimensions are not equal"""
        arr1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        arr2 = ComptimeArrayType(HexenType.COMPTIME_INT, [6])
        assert arr1 != arr2

    def test_not_equal_different_dimension_count(self):
        """Arrays with different dimension counts are not equal"""
        arr1 = ComptimeArrayType(HexenType.COMPTIME_INT, [6])
        arr2 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert arr1 != arr2

    def test_not_equal_to_non_comptime_array(self):
        """ComptimeArrayType not equal to other types"""
        arr1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr1 != "comptime_[5]int"
        assert arr1 != HexenType.COMPTIME_ARRAY_INT
        assert arr1 != 5

    def test_hashable(self):
        """ComptimeArrayType can be used in sets/dicts"""
        arr1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        arr2 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        arr3 = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [5])

        type_set = {arr1, arr2, arr3}
        assert len(type_set) == 2  # arr1 and arr2 are equal, so only 2 unique


class TestComptimeArrayTypeProperties:
    """Test utility methods"""

    def test_total_elements_1d(self):
        """Calculate total elements for 1D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr_type.total_elements() == 5

    def test_total_elements_2d(self):
        """Calculate total elements for 2D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert arr_type.total_elements() == 6

    def test_total_elements_3d(self):
        """Calculate total elements for 3D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        assert arr_type.total_elements() == 24

    def test_total_elements_large_array(self):
        """Calculate total elements for large array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [10, 10, 10])
        assert arr_type.total_elements() == 1000

    def test_ndim_1d(self):
        """Check dimension count for 1D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr_type.ndim() == 1

    def test_ndim_2d(self):
        """Check dimension count for 2D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert arr_type.ndim() == 2

    def test_ndim_3d(self):
        """Check dimension count for 3D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        assert arr_type.ndim() == 3

    def test_is_1d_true(self):
        """is_1d returns True for 1D arrays"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr_type.is_1d() is True
        assert arr_type.is_multidimensional() is False

    def test_is_1d_false_for_2d(self):
        """is_1d returns False for 2D arrays"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert arr_type.is_1d() is False
        assert arr_type.is_multidimensional() is True

    def test_is_multidimensional_for_3d(self):
        """is_multidimensional returns True for 3D arrays"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        assert arr_type.is_multidimensional() is True
        assert arr_type.is_1d() is False


class TestComptimeArrayMaterialization:
    """Test can_materialize_to() compatibility checking"""

    # 1D arrays
    def test_exact_size_match_succeeds(self):
        """Comptime [5] can materialize to [5]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, [5])
        assert comptime.can_materialize_to(concrete) is True

    def test_inferred_size_always_succeeds(self):
        """Comptime [5] can materialize to [_]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, ["_"])
        assert comptime.can_materialize_to(concrete) is True

    def test_size_mismatch_fails(self):
        """Comptime [5] CANNOT materialize to [3]i32 (THIS IS THE BUG FIX!)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, [3])
        assert comptime.can_materialize_to(concrete) is False

    def test_size_too_small_fails(self):
        """Comptime [2] CANNOT materialize to [3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2])
        concrete = ConcreteArrayType(HexenType.I32, [3])
        assert comptime.can_materialize_to(concrete) is False

    def test_dimension_count_mismatch_fails(self):
        """Comptime [5] CANNOT materialize to [2][3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, [2, 3])
        assert comptime.can_materialize_to(concrete) is False

    # 2D arrays
    def test_2d_exact_match_succeeds(self):
        """Comptime [2][3] can materialize to [2][3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [2, 3])
        assert comptime.can_materialize_to(concrete) is True

    def test_2d_partial_inferred_succeeds(self):
        """Comptime [2][3] can materialize to [_][3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, ["_", 3])
        assert comptime.can_materialize_to(concrete) is True

    def test_2d_other_partial_inferred_succeeds(self):
        """Comptime [2][3] can materialize to [2][_]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [2, "_"])
        assert comptime.can_materialize_to(concrete) is True

    def test_2d_fully_inferred_succeeds(self):
        """Comptime [2][3] can materialize to [_][_]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, ["_", "_"])
        assert comptime.can_materialize_to(concrete) is True

    def test_2d_outer_mismatch_fails(self):
        """Comptime [2][3] CANNOT materialize to [3][3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [3, 3])
        assert comptime.can_materialize_to(concrete) is False

    def test_2d_inner_mismatch_fails(self):
        """Comptime [2][3] CANNOT materialize to [2][4]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [2, 4])
        assert comptime.can_materialize_to(concrete) is False

    def test_2d_both_mismatch_fails(self):
        """Comptime [2][3] CANNOT materialize to [3][4]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [3, 4])
        assert comptime.can_materialize_to(concrete) is False

    def test_2d_to_1d_fails(self):
        """Comptime [2][3] CANNOT materialize to [6]i32 (dimension count mismatch)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [6])
        assert comptime.can_materialize_to(concrete) is False

    # 3D arrays
    def test_3d_exact_match_succeeds(self):
        """Comptime [2][2][2] can materialize to [2][2][2]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 2, 2])
        concrete = ConcreteArrayType(HexenType.I32, [2, 2, 2])
        assert comptime.can_materialize_to(concrete) is True

    def test_3d_fully_inferred_succeeds(self):
        """Comptime [2][3][4] can materialize to [_][_][_]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        concrete = ConcreteArrayType(HexenType.I32, ["_", "_", "_"])
        assert comptime.can_materialize_to(concrete) is True

    def test_3d_partial_inferred_middle_succeeds(self):
        """Comptime [2][3][4] can materialize to [2][_][4]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        concrete = ConcreteArrayType(HexenType.I32, [2, "_", 4])
        assert comptime.can_materialize_to(concrete) is True

    def test_3d_mismatch_any_dimension_fails(self):
        """Comptime [2][3][4] CANNOT materialize to [2][3][5]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        concrete = ConcreteArrayType(HexenType.I32, [2, 3, 5])
        assert comptime.can_materialize_to(concrete) is False


class TestDimensionMismatchDetails:
    """Test dimension_mismatch_details() error message generation"""

    def test_dimension_count_mismatch_message(self):
        """Error message for dimension count mismatch"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [6])
        concrete = ConcreteArrayType(HexenType.I32, [2, 3])
        message = comptime.dimension_mismatch_details(concrete)
        assert "Dimension count mismatch" in message
        assert "1 dimension" in message
        assert "2 dimension" in message

    def test_single_dimension_mismatch_message(self):
        """Error message for single dimension size mismatch"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, [3])
        message = comptime.dimension_mismatch_details(concrete)
        assert "dimension 0" in message
        assert "expected 3" in message
        assert "got 5" in message

    def test_2d_outer_dimension_mismatch_message(self):
        """Error message for 2D outer dimension mismatch"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [3, 2])
        concrete = ConcreteArrayType(HexenType.I32, [2, 2])
        message = comptime.dimension_mismatch_details(concrete)
        assert "dimension 0" in message
        assert "expected 2" in message
        assert "got 3" in message

    def test_2d_inner_dimension_mismatch_message(self):
        """Error message for 2D inner dimension mismatch"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ConcreteArrayType(HexenType.I32, [2, 2])
        message = comptime.dimension_mismatch_details(concrete)
        assert "dimension 1" in message
        assert "expected 2" in message
        assert "got 3" in message

    def test_2d_both_dimensions_mismatch_message(self):
        """Error message for multiple dimension mismatches"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [3, 4])
        concrete = ConcreteArrayType(HexenType.I32, [2, 2])
        message = comptime.dimension_mismatch_details(concrete)
        assert "dimension 0" in message
        assert "dimension 1" in message

    def test_compatible_dimensions_message(self):
        """Message when dimensions are compatible"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [3])
        concrete = ConcreteArrayType(HexenType.I32, [3])
        message = comptime.dimension_mismatch_details(concrete)
        assert "compatible" in message

    def test_inferred_dimension_not_in_mismatch(self):
        """Inferred dimensions not reported as mismatches"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5, 3])
        concrete = ConcreteArrayType(HexenType.I32, ["_", 3])
        message = comptime.dimension_mismatch_details(concrete)
        assert "compatible" in message  # Should be compatible despite size 5
