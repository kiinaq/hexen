"""
Unit Tests for ComptimeArrayType Coercion (Phase 5)

Tests the type coercion logic in type_util.py for ComptimeArrayType including:
- ComptimeArrayType → ConcreteArrayType coercion (Phase 2)
- ComptimeArrayType → ComptimeArrayType coercion (Phase 5)
- ComptimeArrayType → HexenType validation (Phase 5)

These tests validate the complete type coercion integration for Issue #1 fix.
"""

import pytest
from src.hexen.semantic.types import ComptimeArrayType, ArrayType, HexenType
from src.hexen.semantic.type_util import can_coerce


class TestComptimeArrayToConcreteArrayCoercion:
    """Test ComptimeArrayType → ConcreteArrayType coercion (Phase 2)"""

    def test_comptime_int_array_to_i32_array_succeeds(self):
        """Comptime int array can coerce to i32 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ArrayType(HexenType.I32, [5])
        assert can_coerce(comptime, concrete) is True

    def test_comptime_int_array_to_i64_array_succeeds(self):
        """Comptime int array can coerce to i64 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ArrayType(HexenType.I64, [5])
        assert can_coerce(comptime, concrete) is True

    def test_comptime_int_array_to_f32_array_succeeds(self):
        """Comptime int array can coerce to f32 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ArrayType(HexenType.F32, [5])
        assert can_coerce(comptime, concrete) is True

    def test_comptime_int_array_to_f64_array_succeeds(self):
        """Comptime int array can coerce to f64 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ArrayType(HexenType.F64, [5])
        assert can_coerce(comptime, concrete) is True

    def test_comptime_float_array_to_f32_array_succeeds(self):
        """Comptime float array can coerce to f32 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        concrete = ArrayType(HexenType.F32, [3])
        assert can_coerce(comptime, concrete) is True

    def test_comptime_float_array_to_f64_array_succeeds(self):
        """Comptime float array can coerce to f64 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        concrete = ArrayType(HexenType.F64, [3])
        assert can_coerce(comptime, concrete) is True

    def test_comptime_float_array_to_i32_array_fails(self):
        """Comptime float array CANNOT coerce to i32 array (element type incompatible)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        concrete = ArrayType(HexenType.I32, [3])
        assert can_coerce(comptime, concrete) is False

    def test_comptime_float_array_to_i64_array_fails(self):
        """Comptime float array CANNOT coerce to i64 array (element type incompatible)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        concrete = ArrayType(HexenType.I64, [3])
        assert can_coerce(comptime, concrete) is False

    def test_2d_comptime_int_array_to_i32_array_succeeds(self):
        """2D comptime int array can coerce to 2D i32 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        concrete = ArrayType(HexenType.I32, [2, 3])
        assert can_coerce(comptime, concrete) is True

    def test_3d_comptime_float_array_to_f64_array_succeeds(self):
        """3D comptime float array can coerce to 3D f64 array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 3, 4])
        concrete = ArrayType(HexenType.F64, [2, 3, 4])
        assert can_coerce(comptime, concrete) is True


class TestComptimeArrayToComptimeArrayCoercion:
    """Test ComptimeArrayType → ComptimeArrayType coercion (Phase 5)"""

    def test_identical_comptime_arrays_coerce(self):
        """Two identical comptime arrays can coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime1, comptime2) is True

    def test_different_dimensions_fail(self):
        """Comptime arrays with different dimensions cannot coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_INT, [3])
        assert can_coerce(comptime1, comptime2) is False

    def test_different_element_types_fail(self):
        """Comptime arrays with different element types cannot coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [5])
        assert can_coerce(comptime1, comptime2) is False

    def test_different_dimension_counts_fail(self):
        """Comptime arrays with different dimension counts cannot coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [6])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert can_coerce(comptime1, comptime2) is False

    def test_2d_identical_arrays_coerce(self):
        """Two identical 2D comptime arrays can coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert can_coerce(comptime1, comptime2) is True

    def test_2d_different_outer_dimension_fail(self):
        """2D comptime arrays with different outer dimensions cannot coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_INT, [3, 3])
        assert can_coerce(comptime1, comptime2) is False

    def test_2d_different_inner_dimension_fail(self):
        """2D comptime arrays with different inner dimensions cannot coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 4])
        assert can_coerce(comptime1, comptime2) is False

    def test_3d_identical_arrays_coerce(self):
        """Two identical 3D comptime arrays can coerce"""
        comptime1 = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 3, 4])
        comptime2 = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 3, 4])
        assert can_coerce(comptime1, comptime2) is True


class TestComptimeArrayToScalarCoercion:
    """Test ComptimeArrayType → HexenType validation (Phase 5)"""

    def test_comptime_int_array_to_i32_fails(self):
        """Comptime int array CANNOT coerce to i32 scalar"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, HexenType.I32) is False

    def test_comptime_int_array_to_i64_fails(self):
        """Comptime int array CANNOT coerce to i64 scalar"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, HexenType.I64) is False

    def test_comptime_float_array_to_f32_fails(self):
        """Comptime float array CANNOT coerce to f32 scalar"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        assert can_coerce(comptime, HexenType.F32) is False

    def test_comptime_float_array_to_f64_fails(self):
        """Comptime float array CANNOT coerce to f64 scalar"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        assert can_coerce(comptime, HexenType.F64) is False

    def test_comptime_int_array_to_comptime_int_fails(self):
        """Comptime int array CANNOT coerce to comptime_int scalar"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, HexenType.COMPTIME_INT) is False

    def test_comptime_float_array_to_comptime_float_fails(self):
        """Comptime float array CANNOT coerce to comptime_float scalar"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [3])
        assert can_coerce(comptime, HexenType.COMPTIME_FLOAT) is False

    def test_comptime_array_to_string_fails(self):
        """Comptime array CANNOT coerce to string"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, HexenType.STRING) is False

    def test_comptime_array_to_bool_fails(self):
        """Comptime array CANNOT coerce to bool"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, HexenType.BOOL) is False

    def test_comptime_array_to_void_fails(self):
        """Comptime array CANNOT coerce to void"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, HexenType.VOID) is False

    def test_2d_comptime_array_to_scalar_fails(self):
        """2D comptime array CANNOT coerce to any scalar type"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert can_coerce(comptime, HexenType.I32) is False
        assert can_coerce(comptime, HexenType.F64) is False


class TestIdentityCoercion:
    """Test identity coercion (any type to itself)"""

    def test_comptime_array_to_self_succeeds(self):
        """Comptime array can coerce to itself (identity)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert can_coerce(comptime, comptime) is True

    def test_2d_comptime_array_to_self_succeeds(self):
        """2D comptime array can coerce to itself (identity)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 3])
        assert can_coerce(comptime, comptime) is True


class TestEdgeCases:
    """Test edge cases and corner scenarios"""

    def test_single_element_array_to_i32_array(self):
        """Single-element comptime array can coerce to single-element concrete array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [1])
        concrete = ArrayType(HexenType.I32, [1])
        assert can_coerce(comptime, concrete) is True

    def test_single_element_array_cannot_coerce_to_scalar(self):
        """Single-element comptime array CANNOT coerce to scalar (array != scalar)"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [1])
        assert can_coerce(comptime, HexenType.I32) is False

    def test_large_array_coercion(self):
        """Large comptime array can coerce to concrete array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [1000])
        concrete = ArrayType(HexenType.I64, [1000])
        assert can_coerce(comptime, concrete) is True

    def test_deeply_nested_array_coercion(self):
        """Deeply nested comptime array can coerce to concrete array"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [2, 2, 2, 2])
        concrete = ArrayType(HexenType.F32, [2, 2, 2, 2])
        assert can_coerce(comptime, concrete) is True
