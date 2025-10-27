# Range-Based Array Materialization Implementation Plan 🦉

*Implementation Strategy for `[range_expr]` Syntax*

> **Feature Overview**: Enable creating arrays from range expressions using `[range_expr]` syntax, as specified in RANGE_SYSTEM.md (Materialization section) and integrated into ARRAY_TYPE_SYSTEM.md.

## Current State Analysis

### ✅ Already Implemented

**Grammar (hexen.lark):**
- ✅ Range expressions fully supported (lines 50-72):
  - `range_bounded`: `start..end` and `start..=end` with optional step
  - `range_from`: `start..` with optional step
  - `range_to`: `..end` and `..=end` (step forbidden)
  - `range_full`: `..` (step forbidden)
- ✅ Array literals supported (line 77): `[expression ("," expression)*]`
- ✅ Array access supported (line 75): `[expression]`

**AST Nodes (ast_nodes.py):**
- ✅ `RANGE_EXPR`: Represents range expressions
- ✅ `RANGE_TYPE`: Represents `range[T]` type annotations
- ✅ `ARRAY_LITERAL`: Represents `[elem, elem, ...]` literals
- ✅ `ARRAY_ACCESS`: Represents `array[index]` or `array[range]` slicing

**Parser (parser.py):**
- ✅ Range expression parsing (lines ~200+)
- ✅ Array literal parsing (lines ~417-426)
- ✅ Array access parsing (lines ~391-398)

### 🔍 Key Syntactic Ambiguity

**The Challenge:**
```hexen
// These look identical syntactically:
val arr : [_]i32 = source[1..10]    // Array slicing (ARRAY_ACCESS with range index)
val arr : [_]i32 = [1..10]          // Range materialization (ARRAY_LITERAL with single range element)
```

**Current Parser Behavior:**
- `source[1..10]` → Parsed as `ARRAY_ACCESS` with `range_expr` as index ✅ (correct)
- `[1..10]` → Parsed as `ARRAY_LITERAL` with single `range_expr` element ✅ (correct!)

**Resolution:**
The parser already handles this correctly! The grammar disambiguates:
- `postfix: primary (array_suffix)*` → `array[range]` is array access
- `primary: ... | array_literal` → `[range]` is array literal

The distinction is **syntactically unambiguous** - it depends on whether there's a base expression before `[...]`.

---

## Implementation Strategy

### Phase 1: Parser Changes (✅ MINIMAL - Already Works!)

**Status:** The parser already correctly handles `[range_expr]` as an `ARRAY_LITERAL` node.

**Verification Needed:**
```python
# Test that parser produces correct AST for:
val arr : [_]i32 = [1..10]

# Expected AST:
{
    "type": "val_declaration",
    "name": "arr",
    "declared_type": "[_]i32",
    "value": {
        "type": "array_literal",
        "elements": [
            {
                "type": "range_expr",
                "start": {...},  # 1
                "end": {...},    # 10
                "step": None,
                "inclusive": False,
                "bounds": "bounded"
            }
        ]
    }
}
```

**Action Items:**
1. ✅ **No grammar changes needed** - Current grammar handles this
2. ✅ **No parser changes needed** - Current parser handles this
3. 🔲 **Add parser tests** to verify `[range_expr]` parses as `ARRAY_LITERAL`

---

### Phase 2: Semantic Analysis Changes (🚧 PRIMARY WORK)

This is where the main implementation work happens.

#### 2.1 Array Literal Analyzer Enhancement

**File:** `src/hexen/semantic/arrays/literal_analyzer.py`

**Current Behavior:**
- Analyzes `ARRAY_LITERAL` nodes with element expressions
- Infers element type from elements
- Creates comptime or concrete array types

**Required Changes:**
```python
# In analyze_array_literal():

def analyze_array_literal(self, node, context):
    elements = node.get("elements", [])

    # NEW: Detect range materialization pattern
    if len(elements) == 1:
        elem = elements[0]
        if elem.get("type") == NodeType.RANGE_EXPR.value:
            # Delegate to range materialization analyzer
            return self._analyze_range_materialization(elem, context)

    # EXISTING: Standard array literal analysis
    # ... (current implementation continues)
```

**New Method:**
```python
def _analyze_range_materialization(self, range_node, context):
    """
    Analyze range materialization: [range_expr] → array

    From RANGE_SYSTEM.md:
    - ✅ Bounded ranges can materialize: [start..end], [start..=end]
    - ❌ Unbounded ranges cannot: [start..], [..end], [..]
    - ✅ Float ranges require explicit step
    - ✅ Comptime ranges adapt to target type
    """

    # 1. Analyze the range expression itself
    range_type_info = self._analyze_range_expression(range_node, context)

    # 2. Validate range is bounded (can materialize)
    bounds = range_node.get("bounds")  # "bounded", "from", "to", "full"
    if bounds != "bounded":
        self.error(
            f"Cannot materialize unbounded range to array",
            range_node,
            help="Only bounded ranges (start..end) can be converted to arrays",
            note=f"Range {self._format_range(range_node)} has no {'start' if bounds in ['to', 'full'] else 'end'} bound"
        )

    # 3. Validate float ranges have explicit step
    element_type = range_type_info["element_type"]
    if self._is_float_type(element_type):
        if range_node.get("step") is None:
            self.error(
                "Float range requires explicit step for materialization",
                range_node,
                help=f"Specify step size: {self._format_range(range_node)}:0.1"
            )

    # 4. Compute materialized array properties
    # Array size can be computed at compile time for constant ranges
    size = self._compute_range_length(range_node, element_type)

    # 5. Create array type (comptime or concrete based on range element type)
    if self._is_comptime_type(element_type):
        # Comptime range materializes to comptime array
        array_type = f"comptime_array_{self._comptime_base(element_type)}"
    else:
        # Concrete range materializes to concrete array
        array_type = f"[{size}]{element_type}"

    return {
        "type": array_type,
        "size": size,
        "element_type": element_type,
        "materialization_source": "range",
        "range_info": range_type_info
    }
```

#### 2.2 Range Expression Analysis Integration

**File:** `src/hexen/semantic/expression_analyzer.py` (or new `range_analyzer.py`)

**Required Functionality:**
```python
def _analyze_range_expression(self, range_node, context):
    """
    Analyze range expression and determine its type.

    Returns:
    {
        "range_type": "range[i32]",
        "element_type": "i32",
        "bounds": "bounded" | "from" | "to" | "full",
        "start_type": "i32" | None,
        "end_type": "i32" | None,
        "step_type": "i32" | None,
        "inclusive": bool
    }
    """

    # 1. Analyze start bound (if present)
    start_type = None
    if range_node.get("start"):
        start_info = self.analyze_expression(range_node["start"], context)
        start_type = start_info["type"]

    # 2. Analyze end bound (if present)
    end_type = None
    if range_node.get("end"):
        end_info = self.analyze_expression(range_node["end"], context)
        end_type = end_info["type"]

    # 3. Analyze step (if present)
    step_type = None
    if range_node.get("step"):
        step_info = self.analyze_expression(range_node["step"], context)
        step_type = step_info["type"]

    # 4. Validate type consistency (RANGE_SYSTEM.md rules)
    element_type = self._resolve_range_element_type(
        start_type, end_type, step_type, range_node
    )

    # 5. Validate step requirements
    self._validate_range_step_requirements(element_type, step_type, range_node)

    return {
        "range_type": f"range[{element_type}]",
        "element_type": element_type,
        "bounds": range_node.get("bounds"),
        "start_type": start_type,
        "end_type": end_type,
        "step_type": step_type,
        "inclusive": range_node.get("inclusive", False)
    }
```

#### 2.3 Range Length Computation

**Helper Methods:**
```python
def _compute_range_length(self, range_node, element_type):
    """
    Compute range length at compile time (for constant ranges).

    Formula (exclusive): length = ceil((end - start) / step)
    Formula (inclusive): length = floor((end - start) / step) + 1

    Returns:
    - Integer length (for constant ranges)
    - "_" (for runtime-computed ranges)
    """

    # Extract constant values (if available)
    start = self._extract_constant_value(range_node.get("start"))
    end = self._extract_constant_value(range_node.get("end"))
    step = self._extract_constant_value(range_node.get("step")) or 1

    if start is None or end is None:
        return "_"  # Runtime-computed size

    # Compute length based on inclusive flag
    if range_node.get("inclusive"):
        # Inclusive: [start, start+step, ..., end]
        import math
        length = math.floor((end - start) / step) + 1
    else:
        # Exclusive: [start, start+step, ..., end-step]
        import math
        length = math.ceil((end - start) / step)

    return max(0, length)  # Ensure non-negative
```

#### 2.4 Type Adaptation for Comptime Ranges

**Integration with Comptime System:**
```python
def _resolve_materialized_array_type(self, range_info, target_type_hint):
    """
    Resolve materialized array type considering comptime adaptation.

    From ARRAY_TYPE_SYSTEM.md:
    - Comptime ranges adapt to target array type
    - val arr : [_]i32 = [flex_range]  → [N]i32
    - val arr : [_]f64 = [flex_range]  → [N]f64
    """

    element_type = range_info["element_type"]

    # Comptime range adapts to target type (if provided)
    if self._is_comptime_type(element_type) and target_type_hint:
        target_elem_type = self._extract_array_element_type(target_type_hint)
        if self._can_adapt_comptime_to(element_type, target_elem_type):
            element_type = target_elem_type

    return element_type
```

---

### Phase 3: Error Handling & Validation

**Required Error Messages:**

```python
# 1. Unbounded range materialization
Error: Cannot materialize unbounded range to array
  val arr : [_]i32 = [5..]
                      ^^^
Help: Range 5.. has no end bound
Note: Only bounded ranges (start..end) can be converted to arrays

# 2. Float range without step
Error: Float range requires explicit step for materialization
  val arr : [_]f32 = [0.0..10.0]
                      ^^^^^^^^^^
Help: Specify step size: 0.0..10.0:0.1
Note: Float ranges cannot have implicit step due to precision ambiguity

# 3. Mixed concrete type bounds
Error: Range bounds must have the same type
  val r : range[i32] = i32_val..i64_val
                       ^^^^^^^^^^^^^^^^^
  start: i32
  end:   i64
Help: Convert end to i32: i32_val..(i64_val:i32)
Note: Range start and end must be the same type for type safety

# 4. Float range for indexing (different error - not materialization)
Error: Array indexing requires range[usize], found range[f32]
  val slice : [_]f32 = array[float_range]
                             ^^^^^^^^^^^
Help: Use range[usize] for array indexing
Note: Float ranges are only valid for iteration/materialization, not indexing
```

---

### Phase 4: Testing Strategy

#### 4.1 Parser Tests (`tests/parser/test_range_materialization.py`)

```python
class TestRangeMaterializationParsing:
    """Test that range materialization syntax parses correctly."""

    def test_basic_range_materialization(self):
        """Test [1..10] parses as array_literal with range element."""
        code = "val arr : [_]i32 = [1..10]"
        ast = parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == "array_literal"
        assert len(value["elements"]) == 1
        assert value["elements"][0]["type"] == "range_expr"

    def test_range_with_step_materialization(self):
        """Test [0..100:10] parses correctly."""
        code = "val arr : [_]i32 = [0..100:10]"
        ast = parse(code)

        range_elem = ast["statements"][0]["value"]["elements"][0]
        assert range_elem["type"] == "range_expr"
        assert range_elem["step"] is not None

    def test_float_range_materialization(self):
        """Test [0.0..1.0:0.1] parses correctly."""
        code = "val arr : [_]f32 = [0.0..1.0:0.1]"
        ast = parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == "array_literal"

    def test_distinguishes_array_access_from_materialization(self):
        """Ensure source[1..10] is array_access, not array_literal."""
        code = "val slice : [_]i32 = source[1..10]"
        ast = parse(code)

        value = ast["statements"][0]["value"]
        assert value["type"] == "array_access"  # Not array_literal!
        assert value["index"]["type"] == "range_expr"
```

#### 4.2 Semantic Tests (`tests/semantic/test_range_materialization.py`)

```python
class TestRangeMaterializationSemantics:
    """Test semantic analysis of range materialization."""

    def test_bounded_range_materializes_successfully(self):
        """✅ Bounded ranges can materialize."""
        code = """
        val arr : [_]i32 = [1..10]
        """
        analyze(code)  # Should succeed

    def test_unbounded_range_from_fails(self):
        """❌ Range 5.. cannot materialize (no end bound)."""
        code = """
        val arr : [_]i32 = [5..]
        """
        with pytest.raises(SemanticError, match="unbounded range"):
            analyze(code)

    def test_unbounded_range_to_fails(self):
        """❌ Range ..10 cannot materialize (no start bound)."""
        code = """
        val arr : [_]i32 = [..10]
        """
        with pytest.raises(SemanticError, match="unbounded range"):
            analyze(code)

    def test_unbounded_range_full_fails(self):
        """❌ Range .. cannot materialize (no bounds)."""
        code = """
        val arr : [_]i32 = [..]
        """
        with pytest.raises(SemanticError, match="unbounded range"):
            analyze(code)

    def test_float_range_requires_step(self):
        """❌ Float ranges must have explicit step."""
        code = """
        val arr : [_]f32 = [0.0..10.0]
        """
        with pytest.raises(SemanticError, match="explicit step"):
            analyze(code)

    def test_float_range_with_step_succeeds(self):
        """✅ Float range with step materializes."""
        code = """
        val arr : [_]f32 = [0.0..10.0:0.5]
        """
        analyze(code)  # Should succeed

    def test_comptime_range_adapts_to_target_type(self):
        """✅ Comptime range adapts to array element type."""
        code = """
        val flex_range = 1..10
        val as_i32 : [_]i32 = [flex_range]
        val as_i64 : [_]i64 = [flex_range]
        val as_f64 : [_]f64 = [flex_range]
        """
        analyze(code)  # Should succeed

    def test_materialized_array_has_correct_size(self):
        """Test array size computation for materialized ranges."""
        code = """
        val arr : [_]i32 = [1..10]
        """
        result = analyze(code)
        arr_info = result.symbol_table.lookup("arr")
        assert arr_info["type"] == "[9]i32"  # 10 - 1 = 9 elements

    def test_inclusive_range_materialization(self):
        """Test inclusive range [1..=10] materializes correctly."""
        code = """
        val arr : [_]i32 = [1..=10]
        """
        result = analyze(code)
        arr_info = result.symbol_table.lookup("arr")
        assert arr_info["type"] == "[10]i32"  # 10 elements (inclusive)

    def test_stepped_range_materialization(self):
        """Test stepped range [0..100:10] computes size correctly."""
        code = """
        val arr : [_]i32 = [0..100:10]
        """
        result = analyze(code)
        arr_info = result.symbol_table.lookup("arr")
        assert arr_info["type"] == "[10]i32"  # [0, 10, 20, ..., 90]
```

#### 4.3 Integration Tests

```python
class TestRangeMaterializationIntegration:
    """Test range materialization in realistic scenarios."""

    def test_range_in_function_call(self):
        """Test materialized range passed to function."""
        code = """
        func sum(arr : [_]i32) : i32 = {
            return 42
        }

        val result : i32 = sum([1..10])
        """
        analyze(code)  # Should succeed

    def test_range_materialization_with_inference(self):
        """Test type inference with materialized ranges."""
        code = """
        val arr = [1..10]                   // comptime_array_int
        val concrete : [_]i32 = arr         // Materialize to [9]i32
        """
        analyze(code)

    def test_nested_range_materialization_fails(self):
        """❌ Cannot have array literal with both ranges and other elements."""
        code = """
        val arr : [_]i32 = [1..5, 10, 20]
        """
        with pytest.raises(SemanticError):
            analyze(code)
```

---

## Implementation Checklist

### Parser Phase
- [ ] **Write parser tests** to verify `[range_expr]` parses as `ARRAY_LITERAL`
- [ ] **Verify existing grammar** handles all range materialization cases
- [ ] **Document ambiguity resolution** (array access vs materialization)

### Semantic Analysis Phase
- [ ] **Enhance `literal_analyzer.py`**:
  - [ ] Detect single-element array literal with range
  - [ ] Delegate to range materialization analyzer
- [ ] **Implement range analysis** (in `range_analyzer.py` or `expression_analyzer.py`):
  - [ ] Analyze range expressions (bounds, types, step)
  - [ ] Validate type consistency (start/end/step same type)
  - [ ] Validate float step requirements
- [ ] **Implement range materialization**:
  - [ ] Validate bounded ranges only
  - [ ] Compute range length (compile-time if constant)
  - [ ] Handle comptime range adaptation
  - [ ] Create materialized array type
- [ ] **Integrate with comptime system**:
  - [ ] Support `val range = 1..10` (comptime preservation)
  - [ ] Support `val arr : [_]i32 = [range]` (adaptation)

### Testing Phase
- [ ] **Parser tests** (10+ tests)
- [ ] **Semantic tests** (20+ tests covering all cases)
- [ ] **Integration tests** (5+ realistic scenarios)
- [ ] **Error message tests** (verify helpful error messages)

### Documentation Phase
- [ ] **Update CLAUDE.md** with range materialization patterns
- [ ] **Add examples** to `examples/` directory
- [ ] **Document known limitations** (if any)

---

## Implementation Timeline Estimate

| Phase | Estimated Time | Complexity |
|-------|----------------|------------|
| **Parser Verification** | 2 hours | Low (already works!) |
| **Semantic Analysis Core** | 8 hours | Medium-High |
| **Error Handling** | 4 hours | Medium |
| **Testing** | 6 hours | Medium |
| **Documentation** | 2 hours | Low |
| **Total** | **22 hours** | Medium overall |

---

## Known Edge Cases & Considerations

### 1. Mixed Array Literals (Not Supported)

```hexen
// ❌ ERROR: Cannot mix range materialization with explicit elements
val arr : [_]i32 = [1..5, 10, 20]
```

**Rationale:** Ambiguous semantics. Should this be `[1, 2, 3, 4, 10, 20]` (flattened) or error?
**Decision:** Error for now. Use array concatenation (future feature) if needed.

### 2. Multi-Element Range Literals (Not Supported)

```hexen
// ❌ ERROR: Multiple ranges in single array literal
val arr : [_]i32 = [1..5, 10..15]
```

**Rationale:** Same as above - unclear semantics.
**Decision:** Error for now.

### 3. Nested Range Materialization

```hexen
// ✅ SUPPORTED: Range of ranges (if range[range[T]] is valid)
val ranges : [_]range[i32] = [1..10]  // Array of range? No!
```

**Analysis:** `[1..10]` materializes to array of **elements**, not ranges.
**Conclusion:** This is not a valid use case - ranges materialize to their elements.

### 4. Runtime Range Bounds

```hexen
// Size determined at runtime
val start : i32 = get_start()
val end : i32 = get_end()
val arr : [_]i32 = [start..end]       // Size = "_" (runtime-computed)
```

**Support:** ✅ Supported (array size inferred as `_` at compile time)

---

## Success Criteria

### Minimum Viable Implementation
- ✅ `[1..10]` materializes to `[9]i32` successfully
- ✅ `[1..=10]` materializes to `[10]i32` successfully
- ✅ `[0..100:10]` materializes with correct size
- ✅ `[0.0..1.0:0.1]` float range materializes
- ❌ `[5..]` unbounded range produces clear error
- ❌ `[0.0..1.0]` float without step produces clear error
- ✅ Comptime ranges adapt to target array type

### Full Implementation
- All error cases produce helpful, actionable error messages
- Range length computation correct for all cases (exclusive, inclusive, stepped)
- Comptime range flexibility fully functional
- Comprehensive test coverage (95%+ of range materialization code)
- Documentation updated and examples added

---

## References

- **RANGE_SYSTEM.md** - Authoritative specification for range semantics
- **ARRAY_TYPE_SYSTEM.md** - Array type system and materialization integration
- **TYPE_SYSTEM.md** - Comptime type adaptation rules
- **hexen.lark** - Current grammar (lines 50-77)
- **parser.py** - Current parser implementation (lines ~417-426)
- **ast_nodes.py** - AST node type definitions

---

**Document Version:** 1.0
**Created:** 2025-01-27
**Status:** Planning Phase
**Next Step:** Parser verification tests
