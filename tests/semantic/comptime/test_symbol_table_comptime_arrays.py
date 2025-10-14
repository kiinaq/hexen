"""
Unit tests for symbol table with ComptimeArrayType support (Phase 3)

Tests that the symbol table correctly stores and retrieves ComptimeArrayType
instances, preserving dimensional information through the storage/lookup cycle.

This is part of Issue #1 fix - ensuring comptime array size metadata is never
lost during semantic analysis.
"""

import pytest

from src.hexen.semantic.symbol_table import SymbolTable, Symbol
from src.hexen.semantic.types import ComptimeArrayType, HexenType, Mutability


class TestSymbolTableComptimeArrays:
    """Test symbol table handles ComptimeArrayType correctly"""

    def test_declare_symbol_with_comptime_array_type_1d(self):
        """Symbol table accepts ComptimeArrayType for 1D arrays"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        symbol = Symbol(
            name="arr",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )

        assert table.declare_symbol(symbol) is True

    def test_lookup_symbol_returns_comptime_array_type_1d(self):
        """Lookup preserves ComptimeArrayType for 1D arrays"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [3])
        symbol = Symbol(
            name="data",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )

        table.declare_symbol(symbol)

        looked_up = table.lookup_symbol("data")
        assert looked_up is not None
        assert isinstance(looked_up.type, ComptimeArrayType)
        assert looked_up.type.dimensions == [3]
        assert looked_up.type.element_comptime_type == HexenType.COMPTIME_INT

    def test_lookup_symbol_returns_comptime_array_type_2d(self):
        """Lookup preserves ComptimeArrayType for 2D arrays"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [3, 4])
        symbol = Symbol(
            name="matrix",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )

        table.declare_symbol(symbol)

        looked_up = table.lookup_symbol("matrix")
        assert looked_up is not None
        assert isinstance(looked_up.type, ComptimeArrayType)
        assert looked_up.type.dimensions == [3, 4]
        assert looked_up.type.element_comptime_type == HexenType.COMPTIME_INT

    def test_lookup_symbol_returns_comptime_float_array(self):
        """Lookup preserves ComptimeArrayType for float arrays"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_FLOAT, [10])
        symbol = Symbol(
            name="floats",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )

        table.declare_symbol(symbol)

        looked_up = table.lookup_symbol("floats")
        assert looked_up is not None
        assert isinstance(looked_up.type, ComptimeArrayType)
        assert looked_up.type.dimensions == [10]
        assert looked_up.type.element_comptime_type == HexenType.COMPTIME_FLOAT

    def test_multiple_comptime_arrays_different_sizes(self):
        """Symbol table can store multiple comptime arrays with different sizes"""
        table = SymbolTable()

        # Declare multiple arrays with different sizes
        arr1 = Symbol(
            name="small",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [3]),
            mutability=Mutability.IMMUTABLE
        )
        arr2 = Symbol(
            name="medium",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [10]),
            mutability=Mutability.IMMUTABLE
        )
        arr3 = Symbol(
            name="large",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [100]),
            mutability=Mutability.IMMUTABLE
        )

        assert table.declare_symbol(arr1) is True
        assert table.declare_symbol(arr2) is True
        assert table.declare_symbol(arr3) is True

        # Verify all can be looked up with correct dimensions
        small = table.lookup_symbol("small")
        assert small.type.dimensions == [3]

        medium = table.lookup_symbol("medium")
        assert medium.type.dimensions == [10]

        large = table.lookup_symbol("large")
        assert large.type.dimensions == [100]

    def test_comptime_array_in_nested_scope(self):
        """Comptime arrays work correctly in nested scopes"""
        table = SymbolTable()

        # Declare in global scope
        global_arr = Symbol(
            name="global_data",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [5]),
            mutability=Mutability.IMMUTABLE
        )
        table.declare_symbol(global_arr)

        # Enter nested scope
        table.enter_scope()

        # Declare in nested scope
        local_arr = Symbol(
            name="local_data",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [3]),
            mutability=Mutability.IMMUTABLE
        )
        table.declare_symbol(local_arr)

        # Both should be accessible from nested scope
        global_lookup = table.lookup_symbol("global_data")
        assert global_lookup is not None
        assert global_lookup.type.dimensions == [5]

        local_lookup = table.lookup_symbol("local_data")
        assert local_lookup is not None
        assert local_lookup.type.dimensions == [3]

        # Exit nested scope
        table.exit_scope()

        # Global still accessible
        assert table.lookup_symbol("global_data") is not None

        # Local no longer accessible
        assert table.lookup_symbol("local_data") is None

    def test_comptime_array_shadowing(self):
        """Comptime array can shadow outer scope with different size"""
        table = SymbolTable()

        # Outer scope: array with 5 elements
        outer_arr = Symbol(
            name="data",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [5]),
            mutability=Mutability.IMMUTABLE
        )
        table.declare_symbol(outer_arr)

        # Enter nested scope
        table.enter_scope()

        # Inner scope: array with same name but 3 elements
        inner_arr = Symbol(
            name="data",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [3]),
            mutability=Mutability.IMMUTABLE
        )
        table.declare_symbol(inner_arr)

        # In nested scope, should see inner array
        looked_up = table.lookup_symbol("data")
        assert looked_up.type.dimensions == [3]

        # Exit nested scope
        table.exit_scope()

        # Back in outer scope, should see outer array
        looked_up = table.lookup_symbol("data")
        assert looked_up.type.dimensions == [5]

    def test_mutable_comptime_array(self):
        """Symbol table accepts mutable comptime arrays (mut variables)"""
        table = SymbolTable()

        # Note: In actual usage, mut + comptime array would force resolution
        # But the symbol table should still accept the type
        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        symbol = Symbol(
            name="mutable_arr",
            type=comptime_type,
            mutability=Mutability.MUTABLE
        )

        assert table.declare_symbol(symbol) is True

        looked_up = table.lookup_symbol("mutable_arr")
        assert looked_up is not None
        assert looked_up.mutability == Mutability.MUTABLE
        assert isinstance(looked_up.type, ComptimeArrayType)

    def test_comptime_array_mark_used(self):
        """Mark comptime array symbols as used for dead code analysis"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        symbol = Symbol(
            name="data",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )
        table.declare_symbol(symbol)

        # Initially not used
        assert symbol.used is False

        # Mark as used
        assert table.mark_used("data") is True

        # Verify marked as used
        looked_up = table.lookup_symbol("data")
        assert looked_up.used is True

    def test_3d_comptime_array(self):
        """Symbol table handles 3D comptime arrays correctly"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3, 4])
        symbol = Symbol(
            name="tensor",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )

        table.declare_symbol(symbol)

        looked_up = table.lookup_symbol("tensor")
        assert looked_up is not None
        assert isinstance(looked_up.type, ComptimeArrayType)
        assert looked_up.type.dimensions == [2, 3, 4]
        assert looked_up.type.total_elements() == 24
        assert looked_up.type.ndim() == 3

    def test_comptime_array_declared_line_tracking(self):
        """Symbol table preserves declared_line for comptime arrays"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        symbol = Symbol(
            name="data",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE,
            declared_line=42
        )
        table.declare_symbol(symbol)

        looked_up = table.lookup_symbol("data")
        assert looked_up is not None
        assert looked_up.declared_line == 42


class TestSymbolTableComparisonWithConcreteArrays:
    """Compare behavior between ComptimeArrayType and ConcreteArrayType"""

    def test_both_array_types_coexist(self):
        """Symbol table can store both comptime and concrete arrays"""
        from src.hexen.semantic.types import ConcreteArrayType

        table = SymbolTable()

        # Comptime array
        comptime_arr = Symbol(
            name="comptime_data",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [5]),
            mutability=Mutability.IMMUTABLE
        )

        # Concrete array
        concrete_arr = Symbol(
            name="concrete_data",
            type=ConcreteArrayType(HexenType.I32, [5]),
            mutability=Mutability.IMMUTABLE
        )

        assert table.declare_symbol(comptime_arr) is True
        assert table.declare_symbol(concrete_arr) is True

        # Verify both types are preserved
        comptime_lookup = table.lookup_symbol("comptime_data")
        assert isinstance(comptime_lookup.type, ComptimeArrayType)

        concrete_lookup = table.lookup_symbol("concrete_data")
        assert isinstance(concrete_lookup.type, ConcreteArrayType)

    def test_comptime_vs_concrete_same_size(self):
        """Comptime [5] and concrete [5]i32 are different types"""
        from src.hexen.semantic.types import ConcreteArrayType

        table = SymbolTable()

        comptime_arr = Symbol(
            name="arr1",
            type=ComptimeArrayType(HexenType.COMPTIME_INT, [5]),
            mutability=Mutability.IMMUTABLE
        )

        concrete_arr = Symbol(
            name="arr2",
            type=ConcreteArrayType(HexenType.I32, [5]),
            mutability=Mutability.IMMUTABLE
        )

        table.declare_symbol(comptime_arr)
        table.declare_symbol(concrete_arr)

        # Types should be different
        lookup1 = table.lookup_symbol("arr1")
        lookup2 = table.lookup_symbol("arr2")

        assert type(lookup1.type) != type(lookup2.type)
        assert isinstance(lookup1.type, ComptimeArrayType)
        assert isinstance(lookup2.type, ConcreteArrayType)
