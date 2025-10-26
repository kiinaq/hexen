# Range System Parser Implementation Plan 🦉

*Parser-Level Changes for Range Type System*

> **Scope**: This document focuses exclusively on **parser-level changes** (syntax analysis, AST nodes) for the Range System. Semantic analysis (type checking, validation) will be addressed in a separate implementation phase.

> **⚠️ Prerequisites**: This implementation requires adding `usize` (platform index type) support to the parser first. See **Phase 0** below for details.

## Overview

This plan covers the parser changes needed to support Hexen's range type system as specified in [RANGE_SYSTEM.md](RANGE_SYSTEM.md). The range system provides lazy sequence representations for iteration and array slicing following the "Ergonomic Literals + Transparent Costs" philosophy.

### 🔑 **Critical Conceptual Shift: `[..]` is Now a Range Operation**

**IMPORTANT:** The existing `[..]` array copy operator is **NOT a separate operator** - it's the **unbounded range `..` used in indexing context**!

```hexen
// OLD MENTAL MODEL (incorrect):
val copy = source[..]    // Special "copy operator"

// NEW UNIFIED MODEL (correct):
val copy = source[..]    // Indexing with unbounded range `..`
                         // Equivalent to: source[range_full]
```

**This means:**
- `[..]` is just `[range_full]` - a specific case of range indexing
- All range operations (bounded, unbounded, stepped) use the **same indexing syntax**
- The parser treats `arr[..]` identically to `arr[1..4]` or `arr[2..]` - all are `IndexExpr` with `RangeExpr` index
- No special-case "copy operator" exists - it's unified under range indexing

**Key Insight from RANGE_SYSTEM.md:**
> The `[..]` operator is actually `[range_full]` - slicing with the unbounded range `..`!

**Key Insight from ARRAY_TYPE_SYSTEM.md:**
> The `[..]` operator is **range slicing with the unbounded range `..`** (not a separate copy operator).

## Goals

1. **Parse all range syntax variants** (bounded, unbounded, inclusive, exclusive, stepped)
2. **Create proper AST nodes** for range expressions and types
3. **Support range indexing operations** on arrays (including `[..]` as unbounded range)
4. **Unify array copy syntax** under range indexing (no special cases!)
5. **Comprehensive test coverage** for all syntax variations

## Migration from Old Array Copy Model

### Before: Separate `[..]` Copy Operator (Old Design)

In the previous design, `[..]` was treated as a **special copy operator**:

```python
# OLD AST design (conceptually):
@dataclass
class ArrayCopyExpr:
    """Special operator for array copying."""
    array: Expression
    # No index - just "copy everything"
```

**Problems with old model:**
- ❌ Special case in grammar and AST
- ❌ Doesn't generalize to partial slices
- ❌ Obscures the underlying operation (it's actually a range!)

### After: Unified Range Indexing (New Design)

In the new design, `[..]` is just **range indexing with unbounded range**:

```python
# NEW AST design (unified):
@dataclass
class IndexExpr:
    """Array indexing with any expression (int, variable, or range)."""
    array: Expression
    index: Expression  # Can be RangeExpr(None, None, None, False) for [..]
```

**Benefits of new model:**
- ✅ No special cases - everything is range indexing
- ✅ Generalizes to all slicing operations (partial, stepped, reverse)
- ✅ Reveals the conceptual unity: `[..]` = `[range_full]`

### Concrete Examples of the Unification

| Syntax | Old Model | New Model |
|--------|-----------|-----------|
| `arr[..]` | `ArrayCopyExpr(arr)` | `IndexExpr(arr, RangeExpr(None, None, None, False))` |
| `arr[1..4]` | N/A (not supported) | `IndexExpr(arr, RangeExpr(1, 4, None, False))` |
| `arr[2..]` | N/A (not supported) | `IndexExpr(arr, RangeExpr(2, None, None, False))` |
| `arr[..5]` | N/A (not supported) | `IndexExpr(arr, RangeExpr(None, 5, None, False))` |
| `arr[0]` | `IndexExpr(arr, 0)` | `IndexExpr(arr, IntLiteral(0))` ✅ Same! |

**Key observation:** Single-element indexing (`arr[0]`) uses the **same AST node** - just with an integer expression instead of a range expression. This is the power of the unified model!

### Parser Implementation Impact

**What needs to change:**

1. **Grammar rule update** - Replace special `[..]` rule with general range indexing:
   ```lark
   // OLD (if existed as special case):
   postfix_expr: postfix_expr "[" ".." "]"    // Special case for [..]

   // NEW (unified):
   postfix_expr: postfix_expr "[" range_expr "]"  // Handles all ranges, including ..
   ```

2. **Remove special-case AST handling** - No separate `ArrayCopyExpr` node needed
   ```python
   # OLD (if existed):
   def array_copy_expr(self, items):
       return ArrayCopyExpr(array=items[0])

   # NEW (unified):
   # Nothing special needed! IndexExpr handles it automatically
   # Parser just creates: IndexExpr(array, RangeExpr(None, None, None, False))
   ```

3. **Backward compatibility** - Existing `IndexExpr` with integer indices **unchanged**:
   ```python
   # This still works exactly the same:
   arr[0]  → IndexExpr(array=arr, index=IntLiteral(0))

   # And now these work too:
   arr[..] → IndexExpr(array=arr, index=RangeExpr(None, None, None, False))
   arr[1..4] → IndexExpr(array=arr, index=RangeExpr(1, 4, None, False))
   ```

**What stays the same:**
- ✅ `IndexExpr` AST node (just accepts more index types)
- ✅ Single-element indexing syntax (`arr[0]`)
- ✅ Existing semantic analysis for integer indexing
- ✅ All existing parser tests for non-range indexing

**Key insight:** This is a **generalization**, not a breaking change. We're expanding what `IndexExpr.index` can be (from just integers to any expression, including ranges), not changing its fundamental structure.

## Non-Goals (Future Phases)

- ❌ Type checking and semantic validation (separate phase)
- ❌ Range materialization to arrays (semantic analysis)
- ❌ Range iteration (future feature)
- ❌ Range operations (`.length()`, `.contains()`, etc. - future)

---

## Phase 0: Prerequisites - Add `usize` Platform Index Type

### 0.1 Critical Dependency: `usize` Type Support

**IMPORTANT:** Before implementing range syntax, we must add `usize` (platform index type) support to the parser, as it's required for range type annotations and array indexing.

#### Grammar Changes for `usize`

Add `usize` to the primitive types in `src/hexen/hexen.lark`:

```lark
primitive_type: TYPE_I32
              | TYPE_I64
              | TYPE_F32
              | TYPE_F64
              | TYPE_USIZE      // NEW: Platform index type
              | TYPE_STRING
              | TYPE_BOOL
              | TYPE_VOID

// Type terminals
TYPE_I32: "i32"
TYPE_I64: "i64"
TYPE_F32: "f32"
TYPE_F64: "f64"
TYPE_USIZE: "usize"            // NEW: Platform-dependent unsigned integer
TYPE_STRING: "string"
TYPE_BOOL: "bool"
TYPE_VOID: "void"
```

#### Conversion Operator Update

Update the conversion operator regex to include `usize`:

```lark
// OLD:
CONVERSION_OP.10: /:(?=i32|i64|f32|f64|string|bool|void|\[)/

// NEW:
CONVERSION_OP.10: /:(?=i32|i64|f32|f64|usize|string|bool|void|\[)/
```

#### AST Node Support

Add `usize` to `PrimitiveType` handling in `src/hexen/ast_nodes.py`:

```python
@dataclass
class PrimitiveType:
    """
    Represents a primitive type.

    Supported types:
    - Integer types: i32, i64
    - Float types: f32, f64
    - Index type: usize (platform-dependent, for array indexing)
    - Other types: string, bool, void
    """
    name: str  # "i32", "i64", "f32", "f64", "usize", "string", "bool", "void"
    location: SourceLocation
```

#### Parser Transformer

No special handling needed in `parser.py` - `PrimitiveType` already handles all type names generically.

#### Testing for `usize`

Add tests in `tests/parser/test_usize_type.py`:

```python
"""Parser tests for usize platform index type."""

import pytest
from src.hexen.parser import parse
from src.hexen.ast_nodes import PrimitiveType, VariableDeclaration

class TestUsizeTypeParsing:
    """Test parsing of usize type annotations."""

    def test_usize_variable_declaration(self):
        """Test variable with usize type: val idx : usize = 0"""
        code = "val idx : usize = 0"
        ast = parse(code)

        decl = ast.declarations[0]
        assert isinstance(decl.type_annotation, PrimitiveType)
        assert decl.type_annotation.name == "usize"

    def test_usize_function_parameter(self):
        """Test usize as function parameter type"""
        code = """
        func get_element(index : usize) : i32 = {
            return 0
        }
        """
        ast = parse(code)

        func = ast.declarations[0]
        param_type = func.parameters[0].type_annotation
        assert isinstance(param_type, PrimitiveType)
        assert param_type.name == "usize"

    def test_usize_function_return_type(self):
        """Test usize as function return type"""
        code = """
        func get_index() : usize = {
            return 0
        }
        """
        ast = parse(code)

        func = ast.declarations[0]
        assert isinstance(func.return_type, PrimitiveType)
        assert func.return_type.name == "usize"

    def test_usize_conversion(self):
        """Test explicit conversion to usize: val idx : usize = value:usize"""
        code = "val idx : usize = some_value:usize"
        ast = parse(code)

        # Should parse conversion syntax correctly
        decl = ast.declarations[0]
        assert decl.type_annotation.name == "usize"
        # Conversion expression parsing verified
```

#### Validation Checklist for Phase 0

- [ ] Add `TYPE_USIZE` terminal to grammar
- [ ] Add `usize` to `primitive_type` rule
- [ ] Update `CONVERSION_OP` regex to include `usize`
- [ ] Document `usize` in `PrimitiveType` docstring
- [ ] Create `test_usize_type.py` with comprehensive tests
- [ ] Run full parser test suite (ensure no regressions)
- [ ] Verify `usize` appears in conversion syntax
- [ ] Verify `usize` works in variable declarations
- [ ] Verify `usize` works in function parameters/returns

**Success Criteria for Phase 0:**
✅ `usize` parses as a valid primitive type
✅ `usize` works in all type annotation contexts
✅ `usize` works in conversion expressions (`:usize`)
✅ All existing tests still pass
✅ New `usize` tests cover all contexts

**Estimated Time:** 1-2 hours (simple addition, well-defined scope)

**Dependencies:** None - can be implemented immediately

---

## Phase 1: Grammar Updates

### 1.1 Range Expression Syntax

Add range expression rules to `src/hexen/hexen.lark`:

```lark
// Range Expressions
range_expr: range_bounded
          | range_from
          | range_to
          | range_full

// Bounded ranges: start..end or start..=end (with optional step)
range_bounded: expression ".." expression (":" expression)?      // Exclusive: 1..10 or 1..10:2
             | expression "..=" expression (":" expression)?     // Inclusive: 1..=10 or 1..=10:2

// Unbounded from: start.. (with optional step)
range_from: expression ".." (":" expression)?                    // 5.. or 5..:2

// Unbounded to: ..end or ..=end (NO step allowed!)
range_to: ".." expression                                        // ..10 (exclusive)
        | "..=" expression                                       // ..=10 (inclusive)

// Full unbounded: .. (NO step allowed!)
range_full: ".."

// Operators (already exist, but documenting for clarity)
// ".."   - Exclusive range operator
// "..="  - Inclusive range operator
// ":"    - Step separator (within range context)
```

**Key Grammar Design Decisions:**

1. **Range expressions are primary expressions** - can appear anywhere expressions are valid
2. **Step syntax uses `:`** - distinguishes from type annotations (context-dependent)
3. **Unbounded ranges with no step** - `..end` and `..` forbid step syntax (ambiguous start)
4. **Expression-based bounds** - supports literals, variables, and complex expressions

### 1.2 Range Type Annotations

Add range type syntax:

```lark
// Type annotations
type: primitive_type
    | array_type
    | range_type       // NEW: Range type support

range_type: "range" "[" type "]"    // range[i32], range[usize], range[f64]
```

**Examples:**
- `range[i32]` - Range with i32 element type
- `range[usize]` - Range with platform index type (for array slicing)
- `range[f64]` - Range with f64 element type (iteration only)

### 1.3 Array Indexing with Ranges

Update array indexing to support range expressions:

```lark
// Array indexing (existing, needs update)
postfix_expr: primary_expr
            | postfix_expr "[" expression "]"        // Single index: arr[5]
            | postfix_expr "[" range_expr "]"        // NEW: Range index: arr[1..4]

// Examples:
// arr[0]           - Single element access
// arr[1..4]        - Range slice: exclusive end
// arr[1..=4]       - Range slice: inclusive end
// arr[2..]         - Range slice: from index to end
// arr[..5]         - Range slice: from start to index
// arr[..]          - Range slice: full array copy
// arr[0..10:2]     - Range slice: with step
```

### 1.4 Operator Precedence

Range operators need proper precedence to avoid ambiguity:

```lark
// Operator precedence (update existing rules)
// Precedence level: Lower than arithmetic, higher than comparison

?expression: comparison_expr

?comparison_expr: range_expr
                | comparison_expr "<" range_expr
                | comparison_expr ">" range_expr
                // ... other comparison operators

?range_expr: additive_expr
           | range_bounded
           | range_from
           | range_to
           | range_full

?additive_expr: multiplicative_expr
              | additive_expr "+" multiplicative_expr
              // ... etc
```

**Rationale:** Range expressions should bind tighter than comparisons but looser than arithmetic to allow `1..10+5` to parse as `1..(10+5)`.

---

## Phase 2: AST Node Design

### 2.1 Range Expression Nodes

Create new AST nodes in `src/hexen/ast_nodes.py`:

```python
@dataclass
class RangeExpr:
    """
    Represents a range expression (e.g., 1..10, 5.., ..=100:2).

    Attributes:
        start: Optional[Expression] - Start bound (None for ..end and ..)
        end: Optional[Expression] - End bound (None for start.. and ..)
        step: Optional[Expression] - Step value (None for implicit step)
        inclusive: bool - True for ..=, False for ..
        location: SourceLocation - Source code location

    Examples:
        1..10        → RangeExpr(start=1, end=10, step=None, inclusive=False)
        1..=10       → RangeExpr(start=1, end=10, step=None, inclusive=True)
        1..10:2      → RangeExpr(start=1, end=10, step=2, inclusive=False)
        5..          → RangeExpr(start=5, end=None, step=None, inclusive=False)
        5..:2        → RangeExpr(start=5, end=None, step=2, inclusive=False)
        ..10         → RangeExpr(start=None, end=10, step=None, inclusive=False)
        ..=10        → RangeExpr(start=None, end=10, step=None, inclusive=True)
        ..           → RangeExpr(start=None, end=None, step=None, inclusive=False)
    """
    start: Optional[Expression]
    end: Optional[Expression]
    step: Optional[Expression]
    inclusive: bool
    location: SourceLocation
```

### 2.2 Range Type Node

```python
@dataclass
class RangeType:
    """
    Represents a range type annotation (e.g., range[i32]).

    Attributes:
        element_type: Type - The element type of the range
        location: SourceLocation - Source code location

    Examples:
        range[i32]   → RangeType(element_type=PrimitiveType("i32"))
        range[usize] → RangeType(element_type=PrimitiveType("usize"))
        range[f64]   → RangeType(element_type=PrimitiveType("f64"))
    """
    element_type: Type
    location: SourceLocation
```

### 2.3 Array Indexing Update

Update existing `IndexExpr` to handle range indices:

```python
@dataclass
class IndexExpr:
    """
    Array indexing expression.

    Attributes:
        array: Expression - The array being indexed
        index: Expression - The index (can be IntLiteral, Variable, or RangeExpr)
        location: SourceLocation - Source code location

    Examples:
        arr[0]       → IndexExpr(array=arr, index=IntLiteral(0))
        arr[i]       → IndexExpr(array=arr, index=Variable("i"))
        arr[1..4]    → IndexExpr(array=arr, index=RangeExpr(1, 4, None, False))
        arr[..]      → IndexExpr(array=arr, index=RangeExpr(None, None, None, False))
    """
    array: Expression
    index: Expression  # Can be any expression, including RangeExpr
    location: SourceLocation
```

**Design Note:** Reusing `IndexExpr` keeps AST structure simple - semantic analyzer handles range vs single-index distinction.

---

## Phase 3: Parser Logic Updates

### 3.1 Range Expression Parsing

Add parser transformation rules in `src/hexen/parser.py`:

```python
class HexenTransformer(Transformer):
    # ... existing methods ...

    def range_bounded(self, items):
        """
        Parse bounded range: start..end or start..=end (with optional step).

        Grammar:
            range_bounded: expression ".." expression (":" expression)?
                         | expression "..=" expression (":" expression)?

        Args:
            items: [start_expr, end_expr, ?step_expr] or
                   [start_expr, "..=", end_expr, ?step_expr]

        Returns:
            RangeExpr with start, end, optional step, and inclusive flag
        """
        start = items[0]

        # Check if inclusive (..= operator present)
        if len(items) > 1 and items[1] == "..=":
            inclusive = True
            end = items[2]
            step = items[3] if len(items) > 3 else None
        else:
            inclusive = False
            end = items[1]
            step = items[2] if len(items) > 2 else None

        return RangeExpr(
            start=start,
            end=end,
            step=step,
            inclusive=inclusive,
            location=self._get_location(items[0])
        )

    def range_from(self, items):
        """
        Parse unbounded from range: start.. (with optional step).

        Grammar:
            range_from: expression ".." (":" expression)?

        Args:
            items: [start_expr, ?step_expr]

        Returns:
            RangeExpr with start, no end, optional step
        """
        start = items[0]
        step = items[1] if len(items) > 1 else None

        return RangeExpr(
            start=start,
            end=None,
            step=step,
            inclusive=False,  # Inclusive only meaningful with end bound
            location=self._get_location(items[0])
        )

    def range_to(self, items):
        """
        Parse unbounded to range: ..end or ..=end (NO step allowed).

        Grammar:
            range_to: ".." expression
                    | "..=" expression

        Args:
            items: [end_expr] or ["..=", end_expr]

        Returns:
            RangeExpr with no start, end, no step
        """
        if items[0] == "..=":
            inclusive = True
            end = items[1]
        else:
            inclusive = False
            end = items[0]

        return RangeExpr(
            start=None,
            end=end,
            step=None,  # Step not allowed for ..end ranges
            inclusive=inclusive,
            location=self._get_location(items[0])
        )

    def range_full(self, items):
        """
        Parse full unbounded range: .. (NO step allowed).

        Grammar:
            range_full: ".."

        Args:
            items: []

        Returns:
            RangeExpr with no start, no end, no step
        """
        return RangeExpr(
            start=None,
            end=None,
            step=None,  # Step not allowed for .. ranges
            inclusive=False,
            location=self._get_location(items)
        )

    def range_type(self, items):
        """
        Parse range type annotation: range[T].

        Grammar:
            range_type: "range" "[" type "]"

        Args:
            items: [element_type]

        Returns:
            RangeType with element type
        """
        element_type = items[0]

        return RangeType(
            element_type=element_type,
            location=self._get_location(items[0])
        )
```

### 3.2 Location Tracking

Ensure proper source location tracking for error messages:

```python
def _get_location(self, item) -> SourceLocation:
    """
    Extract source location from parse tree item.

    Handles:
    - Lark Token objects
    - AST nodes with location attribute
    - Lists of items (use first item)
    """
    if isinstance(item, Token):
        return SourceLocation(
            line=item.line,
            column=item.column,
            file="<input>"  # Update with actual file tracking
        )
    elif hasattr(item, 'location'):
        return item.location
    elif isinstance(item, list) and len(item) > 0:
        return self._get_location(item[0])
    else:
        return SourceLocation(line=0, column=0, file="<unknown>")
```

---

## Phase 4: Testing Strategy

### 4.1 Test File Organization

Create comprehensive parser tests in `tests/parser/test_range_syntax.py`:

```python
"""
Parser tests for range system syntax.

Tests ONLY syntax parsing and AST generation.
Semantic validation (type checking) tested separately in tests/semantic/ranges/.
"""

import pytest
from src.hexen.parser import parse
from src.hexen.ast_nodes import RangeExpr, RangeType, IndexExpr, IntLiteral

class TestRangeLiteralSyntax:
    """Test parsing of range literal expressions."""

    def test_bounded_exclusive(self):
        """Test exclusive bounded range: 1..10"""
        code = "val r = 1..10"
        ast = parse(code)

        # Verify AST structure
        assert isinstance(ast.declarations[0].value, RangeExpr)
        range_expr = ast.declarations[0].value

        assert isinstance(range_expr.start, IntLiteral)
        assert range_expr.start.value == 1
        assert isinstance(range_expr.end, IntLiteral)
        assert range_expr.end.value == 10
        assert range_expr.step is None
        assert range_expr.inclusive is False

    def test_bounded_inclusive(self):
        """Test inclusive bounded range: 1..=10"""
        code = "val r = 1..=10"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.inclusive is True

    def test_bounded_with_step_exclusive(self):
        """Test exclusive bounded range with step: 0..100:2"""
        code = "val r = 0..100:2"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert isinstance(range_expr.step, IntLiteral)
        assert range_expr.step.value == 2
        assert range_expr.inclusive is False

    def test_bounded_with_step_inclusive(self):
        """Test inclusive bounded range with step: 0..=100:2"""
        code = "val r = 0..=100:2"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.step.value == 2
        assert range_expr.inclusive is True

    def test_negative_step(self):
        """Test range with negative step: 10..0:-1"""
        code = "val r = 10..0:-1"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start.value == 10
        assert range_expr.end.value == 0
        assert range_expr.step.value == -1

    def test_float_range_with_step(self):
        """Test float range (step required): 0.0..10.0:0.1"""
        code = "val r = 0.0..10.0:0.1"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start.value == 0.0
        assert range_expr.end.value == 10.0
        assert range_expr.step.value == 0.1

class TestUnboundedRangeSyntax:
    """Test parsing of unbounded range expressions."""

    def test_range_from(self):
        """Test unbounded from range: 5.."""
        code = "val r = 5.."
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start.value == 5
        assert range_expr.end is None
        assert range_expr.step is None

    def test_range_from_with_step(self):
        """Test unbounded from range with step: 5..:2"""
        code = "val r = 5..:2"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start.value == 5
        assert range_expr.end is None
        assert range_expr.step.value == 2

    def test_range_to_exclusive(self):
        """Test unbounded to range (exclusive): ..10"""
        code = "val r = ..10"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start is None
        assert range_expr.end.value == 10
        assert range_expr.step is None
        assert range_expr.inclusive is False

    def test_range_to_inclusive(self):
        """Test unbounded to range (inclusive): ..=10"""
        code = "val r = ..=10"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start is None
        assert range_expr.end.value == 10
        assert range_expr.inclusive is True

    def test_range_full(self):
        """Test full unbounded range: .."""
        code = "val r = .."
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start is None
        assert range_expr.end is None
        assert range_expr.step is None
        assert range_expr.inclusive is False

class TestRangeTypeAnnotations:
    """Test parsing of range type annotations."""

    def test_range_type_i32(self):
        """Test range[i32] type annotation"""
        code = "val r : range[i32] = 1..10"
        ast = parse(code)

        decl = ast.declarations[0]
        assert isinstance(decl.type_annotation, RangeType)
        assert decl.type_annotation.element_type.name == "i32"

    def test_range_type_usize(self):
        """Test range[usize] type annotation"""
        code = "val r : range[usize] = 0..100"
        ast = parse(code)

        assert ast.declarations[0].type_annotation.element_type.name == "usize"

    def test_range_type_f64(self):
        """Test range[f64] type annotation"""
        code = "val r : range[f64] = 0.0..1.0:0.01"
        ast = parse(code)

        assert ast.declarations[0].type_annotation.element_type.name == "f64"

class TestArrayIndexingWithRanges:
    """Test parsing of array indexing using range expressions."""

    def test_array_slice_exclusive(self):
        """Test array slice with exclusive range: arr[1..4]"""
        code = """
        val arr = [10, 20, 30, 40, 50]
        val slice = arr[1..4]
        """
        ast = parse(code)

        slice_expr = ast.declarations[1].value
        assert isinstance(slice_expr, IndexExpr)
        assert isinstance(slice_expr.index, RangeExpr)

        range_idx = slice_expr.index
        assert range_idx.start.value == 1
        assert range_idx.end.value == 4
        assert range_idx.inclusive is False

    def test_array_slice_inclusive(self):
        """Test array slice with inclusive range: arr[1..=4]"""
        code = "val slice = arr[1..=4]"
        ast = parse(code)

        slice_expr = ast.declarations[0].value
        assert slice_expr.index.inclusive is True

    def test_array_slice_from(self):
        """Test array slice from index: arr[2..]"""
        code = "val slice = arr[2..]"
        ast = parse(code)

        range_idx = ast.declarations[0].value.index
        assert range_idx.start.value == 2
        assert range_idx.end is None

    def test_array_slice_to(self):
        """Test array slice to index: arr[..5]"""
        code = "val slice = arr[..5]"
        ast = parse(code)

        range_idx = ast.declarations[0].value.index
        assert range_idx.start is None
        assert range_idx.end.value == 5

    def test_array_slice_full(self):
        """Test full array slice: arr[..]"""
        code = "val copy = arr[..]"
        ast = parse(code)

        range_idx = ast.declarations[0].value.index
        assert range_idx.start is None
        assert range_idx.end is None

    def test_array_slice_with_step(self):
        """Test array slice with step: arr[0..10:2]"""
        code = "val evens = arr[0..10:2]"
        ast = parse(code)

        range_idx = ast.declarations[0].value.index
        assert range_idx.step.value == 2

    def test_array_reverse_slice(self):
        """Test reverse array slice: arr[9..0:-1]"""
        code = "val reversed = arr[9..0:-1]"
        ast = parse(code)

        range_idx = ast.declarations[0].value.index
        assert range_idx.start.value == 9
        assert range_idx.end.value == 0
        assert range_idx.step.value == -1

class TestRangeExpressionContext:
    """Test range expressions in various contexts."""

    def test_range_in_variable_declaration(self):
        """Test range as variable initializer"""
        code = "val r : range[i32] = 1..100"
        ast = parse(code)

        assert isinstance(ast.declarations[0].value, RangeExpr)

    def test_range_with_variable_bounds(self):
        """Test range with variable bounds: start..end"""
        code = """
        val start = 5
        val end = 10
        val r = start..end
        """
        ast = parse(code)

        range_expr = ast.declarations[2].value
        assert range_expr.start.name == "start"
        assert range_expr.end.name == "end"

    def test_range_with_expression_bounds(self):
        """Test range with expression bounds: (x+1)..(y*2)"""
        code = "val r = (x + 1)..(y * 2)"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert isinstance(range_expr.start, BinaryOp)  # x + 1
        assert isinstance(range_expr.end, BinaryOp)    # y * 2

    def test_range_with_function_call_bounds(self):
        """Test range with function call bounds: get_start()..get_end()"""
        code = "val r = get_start()..get_end()"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert isinstance(range_expr.start, FunctionCall)
        assert isinstance(range_expr.end, FunctionCall)

class TestComplexRangeSyntax:
    """Test complex range syntax combinations."""

    def test_nested_array_range_indexing(self):
        """Test range indexing on multidimensional arrays: matrix[0][1..3]"""
        code = "val row_slice = matrix[0][1..3]"
        ast = parse(code)

        # Outer index: matrix[0]
        outer_index = ast.declarations[0].value
        assert isinstance(outer_index, IndexExpr)
        assert outer_index.index.value == 0

        # Inner index: result[1..3]
        inner_array = outer_index.array
        assert isinstance(inner_array, IndexExpr)
        assert isinstance(inner_array.index, RangeExpr)

    def test_range_in_array_literal_context(self):
        """Test materialization syntax: [range]"""
        code = "val arr = [1..10]"
        ast = parse(code)

        # Array literal containing range expression
        array_literal = ast.declarations[0].value
        assert isinstance(array_literal, ArrayLiteral)
        assert isinstance(array_literal.elements[0], RangeExpr)

    def test_multiple_ranges_in_expression(self):
        """Test multiple range expressions in same statement"""
        code = """
        val r1 = 1..10
        val r2 = 20..30
        val combined = process(r1, r2)
        """
        ast = parse(code)

        assert isinstance(ast.declarations[0].value, RangeExpr)
        assert isinstance(ast.declarations[1].value, RangeExpr)

        call = ast.declarations[2].value
        assert isinstance(call.arguments[0], Variable)  # r1
        assert isinstance(call.arguments[1], Variable)  # r2

class TestOperatorPrecedence:
    """Test range operator precedence and associativity."""

    def test_range_vs_arithmetic(self):
        """Test range binds looser than arithmetic: 1..10+5 → 1..(10+5)"""
        code = "val r = 1..10 + 5"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert isinstance(range_expr.end, BinaryOp)  # 10 + 5
        assert range_expr.end.operator == "+"

    def test_range_step_precedence(self):
        """Test step binds to range, not outer expression: 1..10:2+1 → 1..10:(2+1)"""
        code = "val r = 1..10:2 + 1"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        # Step should be 2, outer addition creates BinaryOp(range, 1)
        # OR: step is (2+1) if step binds tighter
        # Grammar needs to clarify this!

    def test_parenthesized_range(self):
        """Test parentheses override precedence: (1..10) + 5"""
        code = "val r = (1..10) + 5"
        ast = parse(code)

        # Should create BinaryOp with range as left operand
        assert isinstance(ast.declarations[0].value, BinaryOp)

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_range(self):
        """Test empty range: 5..5"""
        code = "val empty = 5..5"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.start.value == 5
        assert range_expr.end.value == 5

    def test_reversed_range(self):
        """Test reversed range (semantic error, but should parse): 10..1"""
        code = "val reversed = 10..1"
        ast = parse(code)

        # Parser allows this, semantic analyzer will validate
        range_expr = ast.declarations[0].value
        assert range_expr.start.value == 10
        assert range_expr.end.value == 1

    def test_large_range_values(self):
        """Test ranges with large literal values"""
        code = "val large = 0..1000000"
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.end.value == 1000000

    def test_zero_step(self):
        """Test zero step (semantic error, but should parse): 1..10:0"""
        code = "val zero_step = 1..10:0"
        ast = parse(code)

        # Parser allows this, semantic analyzer will reject
        range_expr = ast.declarations[0].value
        assert range_expr.step.value == 0

class TestErrorRecovery:
    """Test parser error messages and recovery."""

    def test_missing_end_bound(self):
        """Test incomplete range syntax: 1.."""
        # This should parse as range_from, not error
        code = "val r = 1.."
        ast = parse(code)

        range_expr = ast.declarations[0].value
        assert range_expr.end is None  # Unbounded from

    def test_step_on_unbounded_to(self):
        """Test forbidden step on ..end range: ..10:2"""
        code = "val r = ..10:2"

        # This should be a PARSE ERROR (step not allowed)
        with pytest.raises(ParseError):
            parse(code)

    def test_step_on_full_range(self):
        """Test forbidden step on .. range: ..:2"""
        code = "val r = ..:2"

        # This should be a PARSE ERROR (step not allowed)
        with pytest.raises(ParseError):
            parse(code)

    def test_multiple_colons(self):
        """Test invalid multiple steps: 1..10:2:3"""
        code = "val r = 1..10:2:3"

        with pytest.raises(ParseError):
            parse(code)
```

### 4.2 Test Coverage Matrix

Ensure comprehensive coverage across all syntax dimensions:

| Feature | Test Cases | Status |
|---------|------------|--------|
| **Bounded Ranges** | | |
| Exclusive (`..`) | ✅ `test_bounded_exclusive` | |
| Inclusive (`..=`) | ✅ `test_bounded_inclusive` | |
| With step exclusive | ✅ `test_bounded_with_step_exclusive` | |
| With step inclusive | ✅ `test_bounded_with_step_inclusive` | |
| Negative step | ✅ `test_negative_step` | |
| Float bounds | ✅ `test_float_range_with_step` | |
| **Unbounded Ranges** | | |
| From (`start..`) | ✅ `test_range_from` | |
| From with step | ✅ `test_range_from_with_step` | |
| To exclusive (`..end`) | ✅ `test_range_to_exclusive` | |
| To inclusive (`..=end`) | ✅ `test_range_to_inclusive` | |
| Full (`..`) | ✅ `test_range_full` | |
| **Type Annotations** | | |
| `range[i32]` | ✅ `test_range_type_i32` | |
| `range[usize]` | ✅ `test_range_type_usize` | |
| `range[f64]` | ✅ `test_range_type_f64` | |
| **Array Indexing** | | |
| Slice exclusive | ✅ `test_array_slice_exclusive` | |
| Slice inclusive | ✅ `test_array_slice_inclusive` | |
| Slice from | ✅ `test_array_slice_from` | |
| Slice to | ✅ `test_array_slice_to` | |
| Slice full (`[..]`) | ✅ `test_array_slice_full` | |
| Slice with step | ✅ `test_array_slice_with_step` | |
| Reverse slice | ✅ `test_array_reverse_slice` | |
| **Expression Context** | | |
| Variable bounds | ✅ `test_range_with_variable_bounds` | |
| Expression bounds | ✅ `test_range_with_expression_bounds` | |
| Function call bounds | ✅ `test_range_with_function_call_bounds` | |
| **Complex Syntax** | | |
| Nested indexing | ✅ `test_nested_array_range_indexing` | |
| Materialization `[range]` | ✅ `test_range_in_array_literal_context` | |
| Multiple ranges | ✅ `test_multiple_ranges_in_expression` | |
| **Precedence** | | |
| Range vs arithmetic | ✅ `test_range_vs_arithmetic` | |
| Step precedence | ✅ `test_range_step_precedence` | |
| Parenthesized | ✅ `test_parenthesized_range` | |
| **Edge Cases** | | |
| Empty range | ✅ `test_empty_range` | |
| Reversed range | ✅ `test_reversed_range` | |
| Large values | ✅ `test_large_range_values` | |
| Zero step | ✅ `test_zero_step` | |
| **Error Cases** | | |
| Step on `..end` | ✅ `test_step_on_unbounded_to` | |
| Step on `..` | ✅ `test_step_on_full_range` | |
| Multiple steps | ✅ `test_multiple_colons` | |

### 4.3 Integration with Existing Tests

Ensure range syntax doesn't break existing functionality:

1. **Run full parser test suite** after changes
2. **Verify array indexing** still works with integer indices
3. **Check operator precedence** doesn't conflict with existing operators
4. **Validate type annotations** work with existing types

---

## Phase 5: Implementation Checklist

### 5.1 Pre-Implementation

- [ ] Review RANGE_SYSTEM.md specification thoroughly
- [ ] Review TYPE_SYSTEM.md for `usize` specification
- [ ] Understand grammar precedence rules
- [ ] Plan AST node structure
- [ ] Design test organization

### 5.2 Phase 0: Add `usize` Type Support

- [ ] Add `TYPE_USIZE: "usize"` terminal to grammar
- [ ] Add `TYPE_USIZE` to `primitive_type` rule
- [ ] Update `CONVERSION_OP` regex to include `usize`
- [ ] Update `PrimitiveType` docstring to document `usize`
- [ ] Create `tests/parser/test_usize_type.py`
- [ ] Write tests for variable declarations with `usize`
- [ ] Write tests for function parameters with `usize`
- [ ] Write tests for function return types with `usize`
- [ ] Write tests for `usize` conversion syntax
- [ ] Run full parser test suite (verify no regressions)
- [ ] Verify all `usize` tests pass

### 5.3 Grammar Updates (Range Syntax)

- [ ] Add range expression rules to `hexen.lark`
- [ ] Add range type annotation rules
- [ ] Update array indexing rules
- [ ] Set operator precedence correctly
- [ ] Test grammar with Lark playground/validator

### 5.3 AST Node Creation

- [ ] Create `RangeExpr` node in `ast_nodes.py`
- [ ] Create `RangeType` node
- [ ] Update `IndexExpr` documentation
- [ ] Add `__repr__` methods for debugging
- [ ] Add type hints for all fields

### 5.4 Parser Transformations

- [ ] Implement `range_bounded()` transformer
- [ ] Implement `range_from()` transformer
- [ ] Implement `range_to()` transformer
- [ ] Implement `range_full()` transformer
- [ ] Implement `range_type()` transformer
- [ ] Add location tracking to all nodes
- [ ] Test each transformer individually

### 5.5 Testing

- [ ] Create `test_range_syntax.py` test file
- [ ] Write tests for all bounded range variants
- [ ] Write tests for all unbounded range variants
- [ ] Write tests for range type annotations
- [ ] Write tests for array indexing with ranges
- [ ] Write tests for expression contexts
- [ ] Write tests for operator precedence
- [ ] Write tests for edge cases
- [ ] Write tests for error cases
- [ ] Achieve 100% coverage for new code

### 5.6 Documentation

- [ ] Update parser documentation
- [ ] Add comments to grammar rules
- [ ] Document AST node structure
- [ ] Add examples to docstrings
- [ ] Update CLAUDE.md with range patterns

### 5.7 Validation

- [ ] Run full parser test suite (ensure no regressions)
- [ ] Run new range syntax tests
- [ ] Check test coverage metrics
- [ ] Manual testing with example programs
- [ ] Review AST output for correctness

---

## Open Questions & Design Decisions

### Q1: Operator Precedence for Step Syntax

**Question:** How should `1..10:2+1` parse?

**Options:**
1. **Step binds to range only**: `1..10:(2+1)` - Step is part of range syntax
2. **Addition binds tighter**: `(1..10:2)+1` - Creates BinaryOp with range

**Recommendation:** Option 1 - Step is syntactically part of range expression, should bind tightly to range.

**Resolution:** Grammar rule should be:
```lark
range_bounded: expression ".." expression (":" additive_expr)?
```
This ensures `1..10:2+1` parses as `1..10:(2+1)`.

### Q2: Materialization Syntax `[range]`

**Question:** Should `[1..10]` create an array literal with a range element, or materialize the range?

**Options:**
1. **Array literal**: `ArrayLiteral([RangeExpr(1, 10)])` - Just syntax
2. **Special form**: Recognize and transform to materialization node

**Recommendation:** Option 1 for parser phase - treat as array literal. Semantic analyzer handles materialization semantics.

**Rationale:** Keeps parser simple and focused on syntax. Semantic meaning determined later.

### Q3: Range Expression in Non-Index Contexts

**Question:** Should ranges be allowed in arbitrary expression positions?

**Current spec allows:**
```hexen
val r = 1..10           // ✅ Variable assignment
val arr = array[1..4]   // ✅ Array indexing
val mat = [1..10]       // ✅ Materialization
```

**But what about:**
```hexen
val x = (1..10) + 5     // ❓ Range as operand?
func process(r: range[i32]) = { ... }
process(1..10)          // ❓ Range as function argument?
```

**Recommendation:** Allow ranges as first-class expressions everywhere. Semantic analyzer validates usage.

**Rationale:** Simpler grammar, more flexible (future use cases), consistent with expression-based language design.

### Q4: Error Messages for Forbidden Step Syntax

**Question:** Should step on `..end` and `..` be a **parse error** or **semantic error**?

**Options:**
1. **Parse error**: Grammar forbids it syntactically
2. **Semantic error**: Parser allows, semantic analyzer rejects

**Recommendation:** **Parse error** (grammar forbids it).

**Rationale:**
- Spec explicitly forbids step for `..end` and `..`
- Better error messages at parse time
- Prevents invalid AST structures

**Implementation:**
```lark
range_to: ".." expression          // NO step production
        | "..=" expression         // NO step production

range_full: ".."                   // NO step production
```

Parse error message:
```
Error: Step syntax not allowed for unbounded ranges without start
  val r = ..10:2
              ^^
Help: Remove step - unbounded ranges require a defined start for stepping
```

---

## Success Criteria

### Parser Phase Complete When:

✅ **All range syntax variants parse correctly**
- Bounded ranges (exclusive, inclusive, with/without step)
- Unbounded ranges (from, to, full)
- Range type annotations
- Array indexing with ranges

✅ **AST nodes properly represent range semantics**
- `RangeExpr` captures all range attributes
- `RangeType` represents type annotations
- `IndexExpr` supports range indices

✅ **Comprehensive test coverage**
- 100% line coverage for new code
- All syntax variants tested
- Edge cases covered
- Error cases verified

✅ **No regressions in existing functionality**
- All existing parser tests pass
- Array indexing with integers still works
- Operator precedence preserved

✅ **Documentation complete**
- Grammar rules documented
- AST nodes documented
- Test coverage documented
- Examples provided

---

## Future Phases (Not in Scope)

### Semantic Analysis Phase (Separate Plan)

Will cover:
- ❌ Range type checking and inference
- ❌ Range bound type consistency validation
- ❌ Float range step requirement enforcement
- ❌ Unbounded range materialization errors
- ❌ Array slicing type inference
- ❌ Range conversion rules (user types ↔ usize)

### Runtime/Codegen Phase (Future)

Will cover:
- ❌ Range materialization to arrays
- ❌ Array slicing view implementation
- ❌ Range iteration (future feature)
- ❌ Range operations (`.length()`, `.contains()`, etc.)

---

## Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|---------------|--------------|
| **Phase 0: Add `usize` Type** | 1-2 hours | None (prerequisite) |
| **Phase 1: Grammar Updates** | 2-3 hours | Phase 0 ✅ |
| **Phase 2: AST Node Design** | 1-2 hours | Phase 1 |
| **Phase 3: Parser Logic** | 3-4 hours | Phase 2 |
| **Phase 4: Testing** | 4-6 hours | Phase 3 |
| **Phase 5: Documentation** | 1-2 hours | Phase 4 |
| **Total** | **12-19 hours** | Sequential |

**Critical Path:** `usize` Type → Grammar → AST → Parser → Tests

**Parallelizable:** Documentation can start during testing phase

---

## Risk Assessment

### High Risk

- **Operator precedence conflicts** - Range operators might conflict with existing operators
  - *Mitigation:* Careful grammar design, thorough precedence testing

### Medium Risk

- **AST complexity** - Range expressions have many optional fields
  - *Mitigation:* Clear documentation, comprehensive tests

- **Test coverage gaps** - Easy to miss edge cases in range syntax
  - *Mitigation:* Test coverage matrix, systematic test generation

### Low Risk

- **Breaking changes** - Range syntax is additive, shouldn't break existing code
  - *Mitigation:* Run full test suite, manual regression testing

---

## Appendix: Example AST Outputs

### Example 1: Bounded Range with Step

**Input:**
```hexen
val r : range[i32] = 1..10:2
```

**Expected AST:**
```python
Program(
    declarations=[
        VariableDeclaration(
            keyword="val",
            name="r",
            type_annotation=RangeType(
                element_type=PrimitiveType("i32")
            ),
            value=RangeExpr(
                start=IntLiteral(1),
                end=IntLiteral(10),
                step=IntLiteral(2),
                inclusive=False
            )
        )
    ]
)
```

### Example 2: Array Slice

**Input:**
```hexen
val slice = arr[1..4]
```

**Expected AST:**
```python
Program(
    declarations=[
        VariableDeclaration(
            keyword="val",
            name="slice",
            type_annotation=None,
            value=IndexExpr(
                array=Variable("arr"),
                index=RangeExpr(
                    start=IntLiteral(1),
                    end=IntLiteral(4),
                    step=None,
                    inclusive=False
                )
            )
        )
    ]
)
```

### Example 3: Full Unbounded Range

**Input:**
```hexen
val copy = arr[..]
```

**Expected AST:**
```python
Program(
    declarations=[
        VariableDeclaration(
            keyword="val",
            name="copy",
            type_annotation=None,
            value=IndexExpr(
                array=Variable("arr"),
                index=RangeExpr(
                    start=None,
                    end=None,
                    step=None,
                    inclusive=False
                )
            )
        )
    ]
)
```

---

**Last Updated:** 2025-10-26
**Status:** Draft - Ready for Review
**Next Steps:** Review and approval before implementation
