# Issue #1: Comptime Array Size Mismatch Validation - Implementation Plan

**Status**: Ready for Implementation
**Priority**: HIGH - Must fix before Week 3
**Estimated Effort**: 3-4 hours
**Approach**: Option A - Enhanced Type System with Rich Comptime Array Types

---

## Executive Summary

### Problem Statement

Comptime arrays lose their size information when assigned to variables, allowing silent truncation when passed to fixed-size function parameters:

```hexen
val wrong_size = [1, 2, 3, 4, 5]  // comptime array with 5 elements
func exact_three(data: [3]i32) : i32 = { return data[0] }
val result : i32 = exact_three(wrong_size)  // ❌ Should fail but passes, silently truncates to 3
```

### Root Cause

The type system uses `HexenType.COMPTIME_ARRAY_INT` enum values that carry no dimensional information. When a comptime array literal is stored in a symbol, the size metadata is lost. Later function parameter validation cannot detect size mismatches.

### Solution Architecture

Introduce `ComptimeArrayType` class that preserves dimensional information throughout the semantic analysis pipeline, enabling size validation at function call sites.

**Key Design Principle**: Comptime arrays should be as safe as concrete arrays - size mismatches must be caught at compile time.

---

## 1. Detailed Problem Analysis

### Data Flow Bug

```
[1, 2, 3, 4, 5]  →  analyze_array_literal()
                 →  returns HexenType.COMPTIME_ARRAY_INT (size LOST!)
                 →  stored in symbol table (no size metadata)
                 →  function call looks up symbol
                 →  sees HexenType.COMPTIME_ARRAY_INT
                 →  can_coerce(COMPTIME_ARRAY_INT, [3]i32) = True
                 →  NO SIZE VALIDATION!
                 →  Silent truncation from 5 to 3 elements
```

### Current Architecture Limitations

**Type System (types.py)**:
- `HexenType` is an enum - cannot carry metadata
- `ConcreteArrayType` has dimensions but is for concrete types only
- No representation for "comptime array with known dimensions"

**Symbol Table (symbol_table.py)**:
- `Symbol.type` stores `Union[HexenType, ConcreteArrayType]`
- Works correctly, but needs to include new `ComptimeArrayType`

**Function Analyzer (function_analyzer.py)**:
- Explicit copy check happens before type analysis (lines 177-267)
- Only sees AST node types at that point
- Type analysis happens later (line 146) but size is already lost

**Type Coercion (type_util.py)**:
- `can_coerce()` allows comptime → concrete without size checking
- No mechanism to validate dimensional compatibility

### Impact Assessment

**Severity**: HIGH
- **Safety Violation**: Silent data loss through truncation
- **Spec Violation**: ARRAY_TYPE_SYSTEM.md requires exact size matching for fixed-size parameters
- **User Trust**: Silent failures unacceptable in systems programming language

**Affected Scenarios**:
1. ✅ **Direct literals** (WORKING): `exact_three([1,2,3])` - size validated during literal analysis
2. ❌ **Variable references** (BROKEN): `val arr = [1,2,3,4,5]; exact_three(arr)` - size lost
3. ❌ **Expression blocks** (BROKEN): `val arr = { -> [1,2,3,4,5] }; exact_three(arr)` - size lost
4. ❌ **Multiple uses** (BROKEN): Same comptime array reused with different size parameters

---

## 2. Solution Architecture: Option A

### Design Overview

Extend the type system with a new `ComptimeArrayType` class that preserves dimensional information alongside element type information.

**Core Principle**: Make comptime arrays "first-class types" with full metadata, not just enum values.

### Type Hierarchy

```
Type System
├── HexenType (enum)
│   ├── I32, I64, F32, F64 (concrete scalars)
│   ├── COMPTIME_INT, COMPTIME_FLOAT (comptime scalars)
│   ├── STRING, BOOL, VOID
│   └── [DEPRECATED] COMPTIME_ARRAY_INT, COMPTIME_ARRAY_FLOAT
├── ConcreteArrayType (class)
│   ├── element_type: HexenType
│   └── dimensions: List[Union[int, "_"]]
└── ComptimeArrayType (class) ⭐ NEW
    ├── element_comptime_type: HexenType (COMPTIME_INT or COMPTIME_FLOAT)
    └── dimensions: List[int]
```

### Key Design Decisions

**Decision 1**: Use class instead of enum
- **Rationale**: Classes can carry metadata; enums cannot
- **Trade-off**: Slightly more complex type checking, but much more flexible

**Decision 2**: Separate `ComptimeArrayType` from `ConcreteArrayType`
- **Rationale**: Semantic distinction between "not yet materialized" (comptime) and "concrete type" (concrete)
- **Trade-off**: Two array type representations, but clearer semantics

**Decision 3**: Store dimensions as `List[int]` (not `List[Union[int, "_"]]`)
- **Rationale**: Comptime arrays always have known, concrete sizes
- **Trade-off**: Cannot represent "comptime array with inferred dimension" (but that concept doesn't exist)

**Decision 4**: Deprecate but don't remove `HexenType.COMPTIME_ARRAY_INT/FLOAT`
- **Rationale**: Phase out gradually to catch any missed code paths
- **Trade-off**: Temporary technical debt, but safer migration

---

## 3. Implementation Plan

### Phase 1: Type System Foundation (1 hour)

**File**: `src/hexen/semantic/types.py`

**Objective**: Define `ComptimeArrayType` class with complete functionality

#### Implementation

```python
"""
Type System Extensions for Comptime Arrays
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


@dataclass
class ComptimeArrayType:
    """
    Comptime array type with preserved dimensional information.

    Represents array literals like [1, 2, 3] (comptime_array_int with size 3)
    before they materialize to concrete types like [3]i32.

    Key Properties:
    - Preserves exact dimensions for validation against fixed-size parameters
    - Supports multidimensional arrays (e.g., [[1, 2], [3, 4]] has dimensions [2, 2])
    - Materializes to ConcreteArrayType when assigned explicit type or passed to function
    - Element types are COMPTIME_INT or COMPTIME_FLOAT (not concrete types)

    Design Philosophy:
    - Comptime arrays are "flexible" - same array can materialize to different types
    - But they're not "shapeless" - dimensions must match target requirements
    - This balances ergonomics (no type annotations needed) with safety (no silent truncation)

    Examples:
        [1, 2, 3]           → ComptimeArrayType(COMPTIME_INT, [3])
        [1.5, 2.5]          → ComptimeArrayType(COMPTIME_FLOAT, [2])
        [[1, 2], [3, 4]]    → ComptimeArrayType(COMPTIME_INT, [2, 2])
        [[[1]], [[2]]]      → ComptimeArrayType(COMPTIME_INT, [2, 1, 1])
    """

    element_comptime_type: 'HexenType'  # COMPTIME_INT or COMPTIME_FLOAT
    dimensions: List[int]               # Dimensions (e.g., [5] or [2, 3])

    def __post_init__(self):
        """Validate comptime array type constraints"""
        # Validate element type is comptime
        if self.element_comptime_type not in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            raise ValueError(
                f"ComptimeArrayType element must be COMPTIME_INT or COMPTIME_FLOAT, "
                f"got {self.element_comptime_type}"
            )

        # Validate dimensions are positive integers
        if not self.dimensions:
            raise ValueError("ComptimeArrayType must have at least one dimension")

        for dim in self.dimensions:
            if not isinstance(dim, int) or dim <= 0:
                raise ValueError(f"All dimensions must be positive integers, got {dim}")

    def __str__(self):
        """Human-readable string representation"""
        dims_str = "".join(f"[{d}]" for d in self.dimensions)
        elem_str = "int" if self.element_comptime_type == HexenType.COMPTIME_INT else "float"
        return f"comptime_{dims_str}{elem_str}"

    def __repr__(self):
        """Debug representation"""
        return f"ComptimeArrayType({self.element_comptime_type}, {self.dimensions})"

    def total_elements(self) -> int:
        """
        Calculate total number of elements across all dimensions.

        Examples:
            [3] → 3
            [2, 3] → 6
            [2, 3, 4] → 24
        """
        result = 1
        for dim in self.dimensions:
            result *= dim
        return result

    def ndim(self) -> int:
        """Return number of dimensions (1 for 1D, 2 for 2D, etc.)"""
        return len(self.dimensions)

    def is_1d(self) -> bool:
        """Check if this is a 1D array"""
        return len(self.dimensions) == 1

    def is_multidimensional(self) -> bool:
        """Check if this is a multidimensional array (2D or higher)"""
        return len(self.dimensions) > 1

    def can_materialize_to(self, target: 'ConcreteArrayType') -> bool:
        """
        Check if this comptime array can materialize to target concrete type.

        Rules:
        1. Dimension count must match
        2. Each dimension must be compatible:
           - Fixed dimension (int) must match exactly
           - Inferred dimension ("_") accepts any size
        3. Element type compatibility checked elsewhere

        Args:
            target: ConcreteArrayType to check compatibility against

        Returns:
            True if dimensions are compatible, False otherwise

        Examples:
            comptime_[3]int can materialize to:
            - [3]i32 ✅ (exact match)
            - [3]i64 ✅ (exact match, different element type OK)
            - [_]i32 ✅ (inferred accepts any size)

            comptime_[3]int CANNOT materialize to:
            - [4]i32 ❌ (size mismatch)
            - [2]i32 ❌ (size mismatch)
        """
        # Check dimension count
        if len(self.dimensions) != len(target.dimensions):
            return False

        # Check each dimension
        for comptime_dim, concrete_dim in zip(self.dimensions, target.dimensions):
            if concrete_dim == "_":
                # Inferred dimension accepts any size
                continue
            if comptime_dim != concrete_dim:
                # Fixed dimension must match exactly
                return False

        return True

    def dimension_mismatch_details(self, target: 'ConcreteArrayType') -> str:
        """
        Generate detailed error message for dimension mismatches.

        Used by function analyzer to provide helpful error messages.

        Returns:
            Human-readable string describing the mismatch
        """
        if len(self.dimensions) != len(target.dimensions):
            return (
                f"Dimension count mismatch: "
                f"comptime array has {len(self.dimensions)} dimension(s), "
                f"parameter expects {len(target.dimensions)} dimension(s)"
            )

        mismatches = []
        for i, (comptime_dim, concrete_dim) in enumerate(zip(self.dimensions, target.dimensions)):
            if concrete_dim != "_" and comptime_dim != concrete_dim:
                mismatches.append(
                    f"dimension {i}: expected {concrete_dim}, got {comptime_dim}"
                )

        if mismatches:
            return "; ".join(mismatches)

        return "dimensions compatible"
```

#### Testing for Phase 1

```python
# tests/unit/test_comptime_array_type.py (new file)

"""Unit tests for ComptimeArrayType class"""

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

    def test_reject_non_comptime_element_type(self):
        """Cannot create comptime array with concrete element type"""
        with pytest.raises(ValueError, match="must be COMPTIME_INT or COMPTIME_FLOAT"):
            ComptimeArrayType(HexenType.I32, [5])

    def test_reject_empty_dimensions(self):
        """Cannot create comptime array with no dimensions"""
        with pytest.raises(ValueError, match="at least one dimension"):
            ComptimeArrayType(HexenType.COMPTIME_INT, [])

    def test_reject_negative_dimension(self):
        """Cannot create comptime array with negative dimension"""
        with pytest.raises(ValueError, match="positive integers"):
            ComptimeArrayType(HexenType.COMPTIME_INT, [-5])

    def test_reject_zero_dimension(self):
        """Cannot create comptime array with zero dimension"""
        with pytest.raises(ValueError, match="positive integers"):
            ComptimeArrayType(HexenType.COMPTIME_INT, [0])


class TestComptimeArrayTypeProperties:
    """Test ComptimeArrayType utility methods"""

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

    def test_ndim_1d(self):
        """Check dimension count for 1D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        assert arr_type.ndim() == 1
        assert arr_type.is_1d() is True
        assert arr_type.is_multidimensional() is False

    def test_ndim_2d(self):
        """Check dimension count for 2D array"""
        arr_type = ComptimeArrayType(HexenType.COMPTIME_INT, [2, 3])
        assert arr_type.ndim() == 2
        assert arr_type.is_1d() is False
        assert arr_type.is_multidimensional() is True


class TestComptimeArrayMaterialization:
    """Test can_materialize_to() compatibility checking"""

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
        """Comptime [5] CANNOT materialize to [3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, [3])
        assert comptime.can_materialize_to(concrete) is False

    def test_dimension_count_mismatch_fails(self):
        """Comptime [5] CANNOT materialize to [2][3]i32"""
        comptime = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        concrete = ConcreteArrayType(HexenType.I32, [2, 3])
        assert comptime.can_materialize_to(concrete) is False

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
```

**Deliverables**:
- ✅ `ComptimeArrayType` class fully implemented
- ✅ Unit tests passing (20+ tests)
- ✅ Documentation complete

---

### Phase 2: Array Literal Analyzer Updates (30 minutes)

**File**: `src/hexen/semantic/arrays/literal_analyzer.py`

**Objective**: Return `ComptimeArrayType` instead of `HexenType.COMPTIME_ARRAY_INT/FLOAT`

#### Implementation

```python
"""
Array Literal Analyzer - Enhanced with ComptimeArrayType support
"""

from ..types import HexenType, ConcreteArrayType, ComptimeArrayType


class ArrayLiteralAnalyzer:
    """Analyzes array literal expressions with rich type information"""

    def analyze_array_literal(
        self,
        node: Dict[str, Any],
        target_type: Optional[Union[HexenType, ConcreteArrayType, ComptimeArrayType]] = None,
    ) -> Union[HexenType, ComptimeArrayType, ConcreteArrayType]:
        """
        Analyze array literal and return type WITH FULL DIMENSIONAL INFORMATION.

        CHANGE: Now returns ComptimeArrayType instead of HexenType.COMPTIME_ARRAY_INT
        to preserve size information throughout semantic analysis.

        Args:
            node: Array literal AST node
            target_type: Optional target type for context-guided resolution

        Returns:
            ComptimeArrayType with preserved dimensions, or ConcreteArrayType if
            explicit context provided, or HexenType.UNKNOWN on error
        """
        elements = node.get("elements", [])

        # Handle empty arrays - require explicit context
        if not elements:
            if target_type is None:
                self._error(ArrayErrorMessages.empty_array_type_annotation_required(), node)
                return HexenType.UNKNOWN
            # Empty array with context returns appropriate type
            return target_type

        # Check if multidimensional (first element is array literal)
        first_element = elements[0]
        if first_element.get("type") == "array_literal":
            # Delegate to multidimensional analyzer
            return self._analyze_multidimensional_literal(node, target_type, elements)

        # Handle ConcreteArrayType context (explicit type annotation)
        if isinstance(target_type, ConcreteArrayType):
            return self._analyze_with_concrete_context(node, target_type)

        # Analyze elements to determine unified element type
        if self._analyze_expression is not None:
            element_types = []
            for element in elements:
                element_type = self._analyze_expression(element, None)
                element_types.append(element_type)

            # Unify element types
            unified_element_type = self._unify_element_types(element_types, node)

            # CHANGE: Return ComptimeArrayType with size information
            if unified_element_type == HexenType.COMPTIME_INT:
                return ComptimeArrayType(
                    element_comptime_type=HexenType.COMPTIME_INT,
                    dimensions=[len(elements)]
                )
            elif unified_element_type == HexenType.COMPTIME_FLOAT:
                return ComptimeArrayType(
                    element_comptime_type=HexenType.COMPTIME_FLOAT,
                    dimensions=[len(elements)]
                )
            elif unified_element_type == HexenType.UNKNOWN:
                return HexenType.UNKNOWN
            else:
                # Non-comptime element types require explicit context
                self._error(
                    "Array with concrete element types requires explicit array type annotation",
                    node
                )
                return HexenType.UNKNOWN

        # Fallback for backward compatibility (should rarely happen)
        return HexenType.UNKNOWN

    def _analyze_multidimensional_literal(
        self,
        node: Dict[str, Any],
        target_type: Optional[Union[HexenType, ConcreteArrayType, ComptimeArrayType]],
        elements: List[Dict]
    ) -> Union[ComptimeArrayType, ConcreteArrayType, HexenType]:
        """
        Analyze multidimensional array literal.

        CHANGE: Returns ComptimeArrayType with full dimensional information.
        """
        # Analyze first sub-array to determine inner dimensions
        first_sub_array = elements[0]
        first_sub_type = self.analyze_array_literal(first_sub_array, None)

        if isinstance(first_sub_type, ComptimeArrayType):
            # Multidimensional comptime array
            # Validate all sub-arrays have same dimensions
            for i, sub_array in enumerate(elements[1:], start=1):
                sub_type = self.analyze_array_literal(sub_array, None)
                if not isinstance(sub_type, ComptimeArrayType):
                    self._error(f"Sub-array {i} is not a comptime array", sub_array)
                    return HexenType.UNKNOWN

                if sub_type.dimensions != first_sub_type.dimensions:
                    self._error(
                        f"Sub-array {i} dimension mismatch: "
                        f"expected {first_sub_type.dimensions}, got {sub_type.dimensions}",
                        sub_array
                    )
                    return HexenType.UNKNOWN

            # All sub-arrays compatible - construct multidimensional type
            outer_dimension = len(elements)
            inner_dimensions = first_sub_type.dimensions
            full_dimensions = [outer_dimension] + inner_dimensions

            return ComptimeArrayType(
                element_comptime_type=first_sub_type.element_comptime_type,
                dimensions=full_dimensions
            )

        # Handle concrete or error cases
        return HexenType.UNKNOWN
```

#### Testing for Phase 2

```python
# tests/semantic/arrays/test_comptime_array_type_integration.py (new file)

"""Integration tests for ComptimeArrayType in array literal analysis"""

import pytest
from src.hexen.semantic.analyzer import SemanticAnalyzer
from src.hexen.semantic.types import ComptimeArrayType, HexenType


class TestComptimeArrayLiteralAnalysis:
    """Test that array literals return ComptimeArrayType"""

    def test_simple_int_array_returns_comptime_type(self):
        """[1, 2, 3] returns ComptimeArrayType([3], COMPTIME_INT)"""
        code = "val arr = [1, 2, 3]"
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)

        # Look up symbol and check type
        symbol = analyzer.symbol_table.lookup_symbol("arr")
        assert isinstance(symbol.type, ComptimeArrayType)
        assert symbol.type.dimensions == [3]
        assert symbol.type.element_comptime_type == HexenType.COMPTIME_INT

    def test_float_array_returns_comptime_type(self):
        """[1.5, 2.5] returns ComptimeArrayType([2], COMPTIME_FLOAT)"""
        code = "val arr = [1.5, 2.5]"
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)

        symbol = analyzer.symbol_table.lookup_symbol("arr")
        assert isinstance(symbol.type, ComptimeArrayType)
        assert symbol.type.dimensions == [2]
        assert symbol.type.element_comptime_type == HexenType.COMPTIME_FLOAT

    def test_2d_array_returns_comptime_type_with_dimensions(self):
        """[[1, 2], [3, 4]] returns ComptimeArrayType([2, 2], COMPTIME_INT)"""
        code = "val matrix = [[1, 2], [3, 4]]"
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)

        symbol = analyzer.symbol_table.lookup_symbol("matrix")
        assert isinstance(symbol.type, ComptimeArrayType)
        assert symbol.type.dimensions == [2, 2]
        assert symbol.type.element_comptime_type == HexenType.COMPTIME_INT
```

**Deliverables**:
- ✅ Array literals return `ComptimeArrayType` with dimensions
- ✅ Multidimensional arrays correctly analyzed
- ✅ Integration tests passing

---

### Phase 3: Symbol Table Integration (15 minutes)

**File**: `src/hexen/semantic/symbol_table.py`

**Objective**: Ensure symbol table accepts `ComptimeArrayType`

#### Implementation

```python
"""
Symbol Table - Extended to support ComptimeArrayType
"""

from .types import HexenType, ConcreteArrayType, ComptimeArrayType


@dataclass
class Symbol:
    """
    Represents a symbol with full metadata.

    CHANGE: type field now supports ComptimeArrayType to preserve
    dimensional information for comptime arrays.
    """
    name: str
    type: Union[HexenType, ConcreteArrayType, ComptimeArrayType]  # Extended!
    mutability: Mutability
    declared_line: Optional[int] = None
    initialized: bool = True
    used: bool = False


@dataclass
class Parameter:
    """
    Function parameter with type and mutability.

    Note: Parameters cannot be ComptimeArrayType (they're always concrete).
    ComptimeArrayType only appears in expressions and intermediate values.
    """
    name: str
    param_type: Union[HexenType, ConcreteArrayType]  # No ComptimeArrayType
    is_mutable: bool


@dataclass
class FunctionSignature:
    """
    Function signature for symbol table.

    Note: Return types cannot be ComptimeArrayType (functions return concrete types).
    """
    name: str
    parameters: List[Parameter]
    return_type: Union[HexenType, ConcreteArrayType]  # No ComptimeArrayType
    declared_line: Optional[int] = None
```

**Key Insight**: Only `Symbol.type` needs `ComptimeArrayType`. Parameters and return types are always concrete.

#### Testing for Phase 3

```python
# tests/unit/test_symbol_table_comptime_arrays.py (new file)

"""Unit tests for symbol table with ComptimeArrayType support"""

from src.hexen.semantic.symbol_table import SymbolTable, Symbol
from src.hexen.semantic.types import ComptimeArrayType, HexenType, Mutability


class TestSymbolTableComptimeArrays:
    """Test symbol table handles ComptimeArrayType correctly"""

    def test_declare_symbol_with_comptime_array_type(self):
        """Symbol table accepts ComptimeArrayType"""
        table = SymbolTable()

        comptime_type = ComptimeArrayType(HexenType.COMPTIME_INT, [5])
        symbol = Symbol(
            name="arr",
            type=comptime_type,
            mutability=Mutability.IMMUTABLE
        )

        assert table.declare_symbol(symbol) is True

    def test_lookup_symbol_returns_comptime_array_type(self):
        """Lookup preserves ComptimeArrayType"""
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
```

**Deliverables**:
- ✅ Symbol table accepts `ComptimeArrayType`
- ✅ Type information preserved through storage and lookup
- ✅ Unit tests passing

---

### Phase 4: Function Analyzer Size Validation (1 hour)

**File**: `src/hexen/semantic/function_analyzer.py`

**Objective**: Add size validation when comptime arrays are passed to fixed-size parameters

#### Implementation

```python
"""
Function Analyzer - Enhanced with comptime array size validation
"""

from .types import HexenType, ConcreteArrayType, ComptimeArrayType


class FunctionAnalyzer:
    """Analyzes function calls with complete type validation"""

    def _analyze_argument_against_parameter(
        self, argument: Dict, parameter, function_name: str, position: int
    ):
        """
        Analyze argument against parameter with FULL SIZE VALIDATION.

        CHANGE: Added comptime array size validation before general coercion check.
        This prevents silent truncation of comptime arrays to smaller fixed-size parameters.
        """
        # Check explicit copy requirement (existing code)
        self._check_array_argument_copy_requirement(
            argument, parameter, function_name, position
        )

        # Analyze argument expression with parameter type as context
        argument_type = self._analyze_expression(argument, parameter.param_type)

        # NEW: Validate comptime array size compatibility
        if isinstance(argument_type, ComptimeArrayType) and isinstance(parameter.param_type, ConcreteArrayType):
            if not self._validate_comptime_array_size(
                argument_type, parameter.param_type, function_name, position, argument
            ):
                # Error already reported, skip further validation
                return

        # Validate type compatibility using TYPE_SYSTEM.md rules
        if not can_coerce(argument_type, parameter.param_type):
            # Existing error handling...
            pass

    def _validate_comptime_array_size(
        self,
        comptime_type: ComptimeArrayType,
        target_type: ConcreteArrayType,
        function_name: str,
        position: int,
        argument_node: Dict
    ) -> bool:
        """
        Validate that comptime array dimensions match target parameter dimensions.

        This is the CORE FIX for Issue #1. It prevents:
        - Silent truncation (comptime [5] → parameter [3])
        - Silent padding (comptime [2] → parameter [3])
        - Dimension mismatches (comptime [2][3] → parameter [6])

        Rules:
        1. Dimension count must match
        2. Each dimension checked individually:
           - Inferred dimension ("_") accepts any size
           - Fixed dimension (int) requires exact match
        3. Clear error messages guide user to fix

        Args:
            comptime_type: ComptimeArrayType from argument expression
            target_type: ConcreteArrayType from parameter definition
            function_name: Function name for error messages
            position: Argument position (1-based) for error messages
            argument_node: AST node for error reporting

        Returns:
            True if dimensions compatible, False if mismatch (error already reported)
        """
        # Check dimension count first
        if len(comptime_type.dimensions) != len(target_type.dimensions):
            self._error_comptime_array_dimension_count_mismatch(
                comptime_type, target_type, function_name, position, argument_node
            )
            return False

        # Check each dimension for compatibility
        mismatched_dims = []
        for i, (comptime_dim, target_dim) in enumerate(
            zip(comptime_type.dimensions, target_type.dimensions)
        ):
            if target_dim == "_":
                # Inferred dimension - accepts any size
                continue

            if comptime_dim != target_dim:
                # Fixed dimension mismatch
                mismatched_dims.append((i, comptime_dim, target_dim))

        if mismatched_dims:
            self._error_comptime_array_size_mismatch(
                comptime_type, target_type, function_name, position,
                mismatched_dims, argument_node
            )
            return False

        # All dimensions compatible
        return True

    def _error_comptime_array_dimension_count_mismatch(
        self,
        comptime_type: ComptimeArrayType,
        target_type: ConcreteArrayType,
        function_name: str,
        position: int,
        argument_node: Dict
    ):
        """Generate error for dimension count mismatch"""
        comptime_str = str(comptime_type)
        target_str = str(target_type)

        self._error(
            f"Comptime array dimension count mismatch in function call\n"
            f"  Function: {function_name}(...)\n"
            f"  Argument {position}: comptime array type {comptime_str}\n"
            f"  Parameter expects: {target_str}\n"
            f"\n"
            f"  Comptime array has {len(comptime_type.dimensions)} dimension(s)\n"
            f"  Parameter expects {len(target_type.dimensions)} dimension(s)\n"
            f"\n"
            f"  Cannot materialize {len(comptime_type.dimensions)}D array to "
            f"{len(target_type.dimensions)}D parameter",
            argument_node
        )

    def _error_comptime_array_size_mismatch(
        self,
        comptime_type: ComptimeArrayType,
        target_type: ConcreteArrayType,
        function_name: str,
        position: int,
        mismatched_dims: List[Tuple[int, int, int]],
        argument_node: Dict
    ):
        """
        Generate detailed error message for size mismatches.

        Provides actionable guidance:
        - Shows exact size mismatch
        - Suggests using inferred-size parameter [_]T
        - Explains that truncation/padding not allowed
        """
        comptime_str = str(comptime_type)
        target_str = str(target_type)

        # Build dimension mismatch details
        if len(mismatched_dims) == 1:
            dim_idx, comptime_size, target_size = mismatched_dims[0]
            dim_detail = (
                f"  Dimension {dim_idx}: comptime size {comptime_size}, "
                f"parameter expects {target_size}\n"
            )
        else:
            dim_lines = []
            for dim_idx, comptime_size, target_size in mismatched_dims:
                dim_lines.append(
                    f"    - Dimension {dim_idx}: {comptime_size} ≠ {target_size}"
                )
            dim_detail = "  Multiple dimension mismatches:\n" + "\n".join(dim_lines) + "\n"

        self._error(
            f"Comptime array size mismatch in function call\n"
            f"  Function: {function_name}(...)\n"
            f"  Argument {position}: comptime array type {comptime_str}\n"
            f"  Parameter expects: {target_str}\n"
            f"\n"
            f"{dim_detail}"
            f"\n"
            f"  Fixed-size parameters require exact size match.\n"
            f"  Cannot truncate or pad comptime arrays.\n"
            f"\n"
            f"  Suggestions:\n"
            f"    - Use inferred-size parameter to accept any size: [_]T\n"
            f"    - Adjust array literal to match parameter size\n"
            f"    - Use slice operation (when implemented) for intentional truncation",
            argument_node
        )
```

#### Testing for Phase 4

```python
# tests/semantic/arrays/test_issue1_comptime_array_size_validation.py (new file)

"""
Test Suite: Issue #1 - Comptime Array Size Mismatch Validation

Validates that comptime array sizes are checked against fixed-size parameters
to prevent silent truncation or padding. This is the PRIMARY TEST for Issue #1 fix.
"""

import pytest
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestIssue1BasicSizeMismatch:
    """Core test cases from Issue #1 bug report"""

    def test_issue1_example_size_too_large_fails(self):
        """
        ISSUE #1 PRIMARY TEST CASE

        Comptime array [5] should NOT pass to fixed [3] parameter.
        This was the original bug - it silently truncated from 5 to 3.
        """
        code = """
        func exact_three(data: [3]i32) : i32 = {
            return data[0]
        }

        val wrong_size = [1, 2, 3, 4, 5]
        val result : i32 = exact_three(wrong_size)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="size mismatch|expected 3|5"):
            analyzer.analyze(code)

    def test_comptime_array_size_too_small_fails(self):
        """Comptime array [2] cannot pass to fixed [3] parameter"""
        code = """
        func exact_three(data: [3]i32) : i32 = {
            return data[0]
        }

        val too_small = [1, 2]
        val result : i32 = exact_three(too_small)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="size mismatch|expected 3|2"):
            analyzer.analyze(code)

    def test_comptime_array_exact_size_succeeds(self):
        """Comptime array [3] CAN pass to fixed [3] parameter (exact match)"""
        code = """
        func exact_three(data: [3]i32) : i32 = {
            return data[0]
        }

        val correct_size = [1, 2, 3]
        val result : i32 = exact_three(correct_size)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should succeed

    def test_comptime_array_to_inferred_size_always_succeeds(self):
        """Comptime arrays of ANY size work with inferred [_]T parameters"""
        code = """
        func any_size(data: [_]i32) : i32 = {
            return data[0]
        }

        val size_3 = [1, 2, 3]
        val size_5 = [1, 2, 3, 4, 5]
        val size_10 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        val r1 : i32 = any_size(size_3)
        val r2 : i32 = any_size(size_5)
        val r3 : i32 = any_size(size_10)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # All should succeed


class TestComptimeArraySizeMismatchVariations:
    """Additional size mismatch scenarios"""

    def test_off_by_one_too_large(self):
        """Comptime [4] cannot pass to [3] parameter"""
        code = """
        func f(data: [3]i32) : i32 = { return data[0] }
        val arr = [1, 2, 3, 4]
        f(arr)
        """
        with pytest.raises(Exception, match="size mismatch"):
            SemanticAnalyzer().analyze(code)

    def test_off_by_one_too_small(self):
        """Comptime [2] cannot pass to [3] parameter"""
        code = """
        func f(data: [3]i32) : i32 = { return data[0] }
        val arr = [1, 2]
        f(arr)
        """
        with pytest.raises(Exception, match="size mismatch"):
            SemanticAnalyzer().analyze(code)

    def test_way_off_large_array(self):
        """Comptime [100] cannot pass to [10] parameter"""
        code = """
        func f(data: [10]i32) : i32 = { return data[0] }
        val arr = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,
                   21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,
                   41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,
                   61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,
                   81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]
        f(arr)
        """
        with pytest.raises(Exception, match="size mismatch"):
            SemanticAnalyzer().analyze(code)


class TestComptimeArrayMultidimensionalSizeMismatch:
    """Test size validation for multidimensional comptime arrays"""

    def test_2d_outer_dimension_mismatch(self):
        """Comptime [3][2] cannot pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val wrong = [[1, 2], [3, 4], [5, 6]]
        val result : i32 = exact_2x2(wrong)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="size mismatch|dimension"):
            analyzer.analyze(code)

    def test_2d_inner_dimension_mismatch(self):
        """Comptime [2][3] cannot pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val wrong = [[1, 2, 3], [4, 5, 6]]
        val result : i32 = exact_2x2(wrong)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="size mismatch|dimension"):
            analyzer.analyze(code)

    def test_2d_both_dimensions_mismatch(self):
        """Comptime [3][3] cannot pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val wrong = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        val result : i32 = exact_2x2(wrong)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="size mismatch|dimension"):
            analyzer.analyze(code)

    def test_2d_exact_match_succeeds(self):
        """Comptime [2][2] CAN pass to fixed [2][2] parameter"""
        code = """
        func exact_2x2(data: [2][2]i32) : i32 = {
            return data[0][0]
        }

        val correct = [[1, 2], [3, 4]]
        val result : i32 = exact_2x2(correct)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should succeed

    def test_2d_inferred_outer_dimension_accepts_any(self):
        """Comptime [3][2] CAN pass to inferred [_][2] parameter"""
        code = """
        func any_rows(data: [_][2]i32) : i32 = {
            return data[0][0]
        }

        val arr = [[1, 2], [3, 4], [5, 6]]
        val result : i32 = any_rows(arr)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should succeed

    def test_2d_fully_inferred_accepts_any(self):
        """Comptime [3][5] CAN pass to inferred [_][_] parameter"""
        code = """
        func any_matrix(data: [_][_]i32) : i32 = {
            return data[0][0]
        }

        val arr = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]]
        val result : i32 = any_matrix(arr)
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should succeed


class TestComptimeArrayDimensionCountMismatch:
    """Test dimension count mismatches (1D vs 2D vs 3D)"""

    def test_1d_cannot_pass_to_2d_parameter(self):
        """Comptime [6] cannot pass to [2][3] parameter (dimension count mismatch)"""
        code = """
        func matrix_func(data: [2][3]i32) : i32 = {
            return data[0][0]
        }

        val flat = [1, 2, 3, 4, 5, 6]
        val result : i32 = matrix_func(flat)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="dimension.*mismatch|1.*dimension|2.*dimension"):
            analyzer.analyze(code)

    def test_2d_cannot_pass_to_1d_parameter(self):
        """Comptime [2][3] cannot pass to [6] parameter (dimension count mismatch)"""
        code = """
        func flat_func(data: [6]i32) : i32 = {
            return data[0]
        }

        val matrix = [[1, 2, 3], [4, 5, 6]]
        val result : i32 = flat_func(matrix)
        """
        analyzer = SemanticAnalyzer()
        with pytest.raises(Exception, match="dimension.*mismatch|2.*dimension|1.*dimension"):
            analyzer.analyze(code)


class TestExistingBehaviorPreserved:
    """Ensure fix doesn't break existing working scenarios"""

    def test_direct_literal_still_works(self):
        """Direct array literals to functions (already worked before fix)"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val result : i32 = process([1, 2, 3])
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should still work

    def test_comptime_to_same_size_variable_still_works(self):
        """Comptime array to same-size concrete variable (already worked)"""
        code = """
        val arr : [3]i32 = [1, 2, 3]
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should still work

    def test_concrete_array_with_explicit_copy_still_works(self):
        """Concrete arrays with [..] to functions (already worked)"""
        code = """
        func process(data: [3]i32) : i32 = {
            return data[0]
        }

        val concrete : [3]i32 = [1, 2, 3]
        val result : i32 = process(concrete[..])
        """
        analyzer = SemanticAnalyzer()
        analyzer.analyze(code)  # Should still work
```

**Deliverables**:
- ✅ Size validation implemented
- ✅ Clear error messages generated
- ✅ 30+ tests passing
- ✅ Issue #1 fixed

---

### Phase 5: Type Coercion Updates (30 minutes)

**File**: `src/hexen/semantic/type_util.py`

**Objective**: Extend `can_coerce()` to handle `ComptimeArrayType`

#### Implementation

```python
"""
Type Utilities - Extended for ComptimeArrayType support
"""

from .types import HexenType, ConcreteArrayType, ComptimeArrayType


def can_coerce(
    from_type: Union[HexenType, ConcreteArrayType, ComptimeArrayType],
    to_type: Union[HexenType, ConcreteArrayType, ComptimeArrayType]
) -> bool:
    """
    Check if from_type can be coerced to to_type following TYPE_SYSTEM.md rules.

    CHANGE: Added support for ComptimeArrayType coercion rules.

    Comptime Array Coercion Rules:
    1. ComptimeArrayType → ConcreteArrayType: YES (materialization)
       - Size validation done by caller (function_analyzer)
       - Here we just check element type compatibility
    2. ComptimeArrayType → HexenType: NO (cannot coerce array to scalar)
    3. ComptimeArrayType → ComptimeArrayType: YES if dimensions match

    Args:
        from_type: Source type
        to_type: Target type

    Returns:
        True if coercion is valid, False otherwise
    """
    # Handle ComptimeArrayType → ConcreteArrayType (materialization)
    if isinstance(from_type, ComptimeArrayType) and isinstance(to_type, ConcreteArrayType):
        # Size validation should be done by caller (function_analyzer)
        # Here we just check element type compatibility
        return _comptime_element_can_coerce_to_concrete(
            from_type.element_comptime_type,
            to_type.element_type
        )

    # Handle ComptimeArrayType → ComptimeArrayType
    if isinstance(from_type, ComptimeArrayType) and isinstance(to_type, ComptimeArrayType):
        # Both comptime arrays - check if dimensions and element types match
        return (
            from_type.dimensions == to_type.dimensions
            and from_type.element_comptime_type == to_type.element_comptime_type
        )

    # Handle ComptimeArrayType → HexenType (invalid)
    if isinstance(from_type, ComptimeArrayType) and isinstance(to_type, HexenType):
        return False  # Cannot coerce array to scalar

    # Existing coercion rules for other type combinations...
    # (rest of function unchanged)


def _comptime_element_can_coerce_to_concrete(
    comptime_elem: HexenType,
    concrete_elem: HexenType
) -> bool:
    """
    Check if comptime element type can coerce to concrete element type.

    Rules:
    - COMPTIME_INT → any numeric type (i32, i64, f32, f64)
    - COMPTIME_FLOAT → any float type (f32, f64)
    """
    if comptime_elem == HexenType.COMPTIME_INT:
        return concrete_elem in {
            HexenType.I32, HexenType.I64,
            HexenType.F32, HexenType.F64
        }

    if comptime_elem == HexenType.COMPTIME_FLOAT:
        return concrete_elem in {HexenType.F32, HexenType.F64}

    return False


def is_array_type(type_: Union[HexenType, ConcreteArrayType, ComptimeArrayType]) -> bool:
    """
    Check if type represents an array (comptime or concrete).

    CHANGE: Added ComptimeArrayType support.
    """
    return (
        isinstance(type_, (ConcreteArrayType, ComptimeArrayType))
        or type_ in {HexenType.COMPTIME_ARRAY_INT, HexenType.COMPTIME_ARRAY_FLOAT}
    )
```

**Deliverables**:
- ✅ Type coercion handles `ComptimeArrayType`
- ✅ Element type compatibility checked
- ✅ Array type detection updated

---

### Phase 6: Comprehensive Testing & Validation (1 hour)

**Objective**: Ensure fix works and doesn't break existing functionality

#### Test Strategy

1. **Issue #1 Specific Tests** (already written in Phase 4)
   - Primary bug case: `[1,2,3,4,5]` to `[3]i32` parameter
   - Size too small, too large, exact match
   - Multidimensional size mismatches
   - Dimension count mismatches

2. **Integration Tests** (new)
   - Comptime arrays through expression blocks
   - Multiple uses of same comptime array
   - Nested function calls
   - Mixed comptime and concrete arrays

3. **Regression Tests** (run existing suite)
   - All 1173 existing tests must pass
   - Week 2 Task 9 xfail test should now pass

4. **Edge Case Tests** (new)
   - Empty arrays
   - Very large arrays
   - Deeply nested multidimensional arrays

#### Running Full Test Suite

```bash
# Run complete test suite
uv run pytest tests/ -v

# Run just Issue #1 tests
uv run pytest tests/semantic/arrays/test_issue1_comptime_array_size_validation.py -v

# Run with coverage
uv run pytest tests/ -v --cov=src/hexen/semantic --cov-report=html
```

#### Expected Results

- **All existing tests pass**: 1173/1173 ✅
- **Issue #1 tests pass**: 30+/30+ ✅
- **Week 2 Task 9 xfail resolved**: 24/24 (was 22/24) ✅
- **No regressions**: 100% success rate maintained ✅

---

## 4. Risk Assessment & Mitigation

### Low Risk Implementation ⭐

**Why Low Risk:**
1. ✅ **Isolated changes**: Only affects comptime array code paths
2. ✅ **Type-safe**: Compiler catches missing ComptimeArrayType cases
3. ✅ **Backward compatible**: Doesn't break concrete array handling
4. ✅ **Well-tested**: 50+ new tests + 1173 existing tests

**Potential Risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missed code path using COMPTIME_ARRAY_INT | Low | Medium | Search codebase for all uses before deprecation |
| Performance regression | Very Low | Low | ComptimeArrayType is lightweight dataclass |
| Type checking complexity increase | Low | Low | Well-documented, type system remains clean |
| Integration issues | Very Low | Medium | Incremental testing after each phase |

**Mitigation Strategy:**
1. ✅ Run tests after EACH phase (not just at end)
2. ✅ Search for all `HexenType.COMPTIME_ARRAY_INT` uses before starting
3. ✅ Keep `HexenType.COMPTIME_ARRAY_*` enums for transition period
4. ✅ Add comprehensive logging for debugging

---

## 5. Implementation Checklist

### Pre-Implementation
- [ ] Search codebase for all `COMPTIME_ARRAY_INT` uses
- [ ] Review all files that will be modified
- [ ] Set up test-driven development environment
- [ ] Create feature branch: `fix/issue1-comptime-array-size-validation`

### Phase 1: Type System (1 hour)
- [ ] Define `ComptimeArrayType` class in `types.py`
- [ ] Add `__str__`, `__repr__`, helper methods
- [ ] Add `can_materialize_to()` method
- [ ] Write 20+ unit tests for `ComptimeArrayType`
- [ ] Run unit tests - all pass
- [ ] Commit: "Phase 1: Add ComptimeArrayType class"

### Phase 2: Array Literal Analyzer (30 min)
- [ ] Update `analyze_array_literal()` to return `ComptimeArrayType`
- [ ] Update multidimensional analysis
- [ ] Write integration tests
- [ ] Run tests - all pass
- [ ] Commit: "Phase 2: Return ComptimeArrayType from literal analyzer"

### Phase 3: Symbol Table (15 min)
- [ ] Update `Symbol.type` Union type hint
- [ ] Verify no other changes needed
- [ ] Write symbol table tests
- [ ] Run tests - all pass
- [ ] Commit: "Phase 3: Extend symbol table for ComptimeArrayType"

### Phase 4: Function Analyzer (1 hour)
- [ ] Add `_validate_comptime_array_size()` method
- [ ] Add `_error_comptime_array_size_mismatch()` method
- [ ] Call validation from `_analyze_argument_against_parameter()`
- [ ] Write 30+ function call validation tests
- [ ] Run Issue #1 specific tests - all pass
- [ ] Run full test suite - all pass
- [ ] Commit: "Phase 4: Add comptime array size validation (fixes Issue #1)"

### Phase 5: Type Coercion (30 min)
- [ ] Update `can_coerce()` for `ComptimeArrayType`
- [ ] Add `_comptime_element_can_coerce_to_concrete()`
- [ ] Update `is_array_type()`
- [ ] Write type coercion tests
- [ ] Run tests - all pass
- [ ] Commit: "Phase 5: Extend type coercion for ComptimeArrayType"

### Phase 6: Testing & Validation (1 hour)
- [ ] Run complete test suite: `uv run pytest tests/ -v`
- [ ] Verify 1173+ tests passing
- [ ] Check Week 2 Task 9 xfail now passes
- [ ] Run with coverage analysis
- [ ] Fix any regressions
- [ ] Final commit: "Phase 6: Complete testing and validation"

### Post-Implementation
- [ ] Update `ARRAY_IMPLEMENTATION_PLAN.md` - mark Issue #1 as resolved
- [ ] Update `WEEK2_TASK9_SUMMARY.md` - remove xfail note
- [ ] Update `tests/semantic/arrays/test_comptime_array_parameter_adaptation.py` - remove xfail decorator
- [ ] Write summary in commit message
- [ ] Push feature branch
- [ ] Ready for Week 3!

---

## 6. Success Criteria

✅ **Fix is complete when:**

1. **Core functionality works**:
   - [ ] Comptime array `[5]` to parameter `[3]i32` raises error
   - [ ] Comptime array `[3]` to parameter `[3]i32` succeeds
   - [ ] Comptime array `[5]` to parameter `[_]i32` succeeds
   - [ ] Multidimensional mismatches caught

2. **Tests pass**:
   - [ ] All 30+ Issue #1 tests passing
   - [ ] All 1173 existing tests still passing
   - [ ] Week 2 Task 9 xfail resolved (24/24 passing)
   - [ ] No regressions introduced

3. **Code quality maintained**:
   - [ ] Type hints complete and correct
   - [ ] Documentation updated
   - [ ] Error messages clear and actionable
   - [ ] No code duplication

4. **Documentation complete**:
   - [ ] `ARRAY_IMPLEMENTATION_PLAN.md` updated
   - [ ] Issue #1 marked as resolved
   - [ ] Code comments comprehensive
   - [ ] Commit messages clear

---

## 7. Timeline & Effort

| Phase | Estimated Time | Dependencies |
|-------|----------------|--------------|
| **Pre-work** | 15 min | None |
| **Phase 1: Type System** | 1 hour | None |
| **Phase 2: Literal Analyzer** | 30 min | Phase 1 |
| **Phase 3: Symbol Table** | 15 min | Phase 1 |
| **Phase 4: Function Analyzer** | 1 hour | Phases 1-3 |
| **Phase 5: Type Coercion** | 30 min | Phase 1 |
| **Phase 6: Testing** | 1 hour | Phases 1-5 |
| **Post-work** | 15 min | Phase 6 |
| **Total** | **~4 hours** | |

**Recommended Schedule:**
- **Session 1** (2 hours): Phases 1-3 (foundation)
- **Session 2** (2 hours): Phases 4-6 (validation & testing)

---

## 8. Future Enhancements (Post-Fix)

Once Issue #1 is fixed, consider these improvements:

1. **Deprecate old enum values** (low priority)
   - Remove `HexenType.COMPTIME_ARRAY_INT`
   - Remove `HexenType.COMPTIME_ARRAY_FLOAT`
   - Search and replace all uses

2. **Enhanced error messages** (medium priority)
   - Show array contents in errors (for small arrays)
   - Suggest common fixes
   - Link to documentation

3. **Performance optimization** (low priority)
   - Cache `ComptimeArrayType` instances
   - Optimize dimension comparison

4. **Type system refinement** (future)
   - Support for jagged arrays (different row sizes)
   - Support for dynamic arrays (runtime size)

---

## 9. References

### Related Documentation
- `docs/ARRAY_IMPLEMENTATION_PLAN.md` - Overall implementation plan
- `docs/ARRAY_TYPE_SYSTEM.md` - Array type system specification
- `docs/FUNCTION_SYSTEM.md` - Function parameter semantics
- `tests/semantic/arrays/WEEK2_TASK9_SUMMARY.md` - Task 9 summary with xfail notes

### Related Issues
- **Issue #1**: This document (comptime array size validation)
- **Week 2 Task 9**: Comptime array parameter adaptation (related but separate concern)

### Code Locations
- `src/hexen/semantic/types.py` - Type system definitions
- `src/hexen/semantic/arrays/literal_analyzer.py` - Array literal analysis
- `src/hexen/semantic/symbol_table.py` - Symbol storage
- `src/hexen/semantic/function_analyzer.py` - Function call validation
- `src/hexen/semantic/type_util.py` - Type coercion utilities

---

**Ready to implement? Start with Phase 1!** 🚀
