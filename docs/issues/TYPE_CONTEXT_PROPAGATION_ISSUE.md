# Type Context Propagation Issue in Conditional Expression Blocks

**Status:** In Progress
**Discovered:** 2025-10-30
**Affects:** Conditional expressions with division operators in expression blocks

---

## Summary

When a conditional expression is used within a variable assignment with an explicit type annotation, the type context (`target_type`) is not propagating to expressions within the conditional branches. This causes division operations on concrete types to fail with "Concrete type division requires explicit result type" even when the outer variable provides clear type context.

---

## Example Code That Fails

```hexen
func safe_divide(a: f64, b: f64) : f64 = {
    val result : f64 = if b == 0.0 {
        return 0.0
    } else {
        -> a / b       // ERROR: Concrete type division requires explicit result type
    }
    return result
}
```

**Expected Behavior:** The `f64` type annotation on `result` should provide type context for `a / b`, allowing the division to succeed.

**Actual Behavior:** Division analysis sees `target_type=None` and rejects the operation.

---

## Root Cause Analysis

### Architecture Overview

The type context propagation chain should work as follows:

1. **Variable Declaration** (`val result : f64 = ...`)
   - Provides `target_type = f64` to expression analyzer

2. **Conditional Expression** (`if ... { -> expr }`)
   - Receives `target_type` and passes it to branch analysis

3. **Branch Analysis** (`_analyze_conditional_branch`)
   - Receives `target_type` and passes it to block analyzer

4. **Block Analysis** (`analyze_block`)
   - Receives `target_type` and passes it to statement analysis

5. **Expression Block Finalization** (`_finalize_expression_block`)
   - Uses `target_type` when analyzing the assign expression

### The Problem: Premature Expression Analysis

The issue occurs in `BlockAnalyzer._analyze_statements_with_context()`:

```python
def _analyze_statements_with_context(
    self, statements: List[Dict], context: str, node: Dict, target_type: Optional[HexenType] = None
) -> Optional[HexenType]:
    # ...
    for stmt in statements:
        # ...
        # Line 188: This analyzes the assign statement IMMEDIATELY
        self._analyze_statement(stmt)  # ❌ Analyzes -> a / b without target_type!

    # Later, line 194-196:
    if is_expression_block:
        return self._finalize_expression_block(
            has_assign, has_return, last_statement, node, target_type  # ✅ target_type available here
        )
```

**Timeline of Events:**

1. **Line 188:** `self._analyze_statement(stmt)` is called for the assign statement
2. This delegates to the main analyzer's statement handler
3. Which analyzes the assign statement's value expression (`a / b`)
4. **At this point, `target_type` is not yet available to the expression**
5. Division check fails: `target_type=None` for `f64 / f64`
6. **Line 194-196:** `_finalize_expression_block` is called with `target_type=f64`
7. But the expression was already analyzed - too late!

### Debug Output Confirms

```
DEBUG: Division f64 / f64, target_type=None              # ❌ During statement loop
DEBUG: _finalize_expression_block: target_type=f64, context_type=f64  # ✅ But too late!
```

---

## Affected Test Cases

1. **test_guard_clause_pattern** - Division in conditional else branch
2. **test_conditionals_with_complex_binary_operations** - Division in conditional expression
3. **test_nested_conditionals_with_type_propagation** - Mixed comptime types in nested conditionals

All 3 tests fail with the same root cause: expressions analyzed before `target_type` is available.

---

## Changes Already Made (Partial Fix)

### Files Modified

1. **`src/hexen/semantic/analyzer.py`**
   - Added `target_type` parameter to `_analyze_block()` method
   - Signature: `def _analyze_block(self, body, node, context=None, target_type=None)`

2. **`src/hexen/semantic/block_analyzer.py`**
   - Added `target_type` parameter to `analyze_block()` method
   - Added `target_type` parameter to `_analyze_statements_with_context()` method
   - Added `target_type` parameter to `_finalize_expression_block()` method
   - Modified `_finalize_expression_block()` to use `target_type` when analyzing assign expressions

3. **`src/hexen/semantic/expression_analyzer.py`**
   - Updated `_analyze_conditional_branch()` to pass `target_type` to `_analyze_block()`
   - Updated expression block analysis to pass `target_type`

### What Works Now

- Type context DOES flow from variable declaration → conditional → branch → block analyzer
- `_finalize_expression_block` DOES receive the correct `target_type`

### What Doesn't Work

- Assign statement expressions are analyzed in the statement loop BEFORE finalization
- By the time `_finalize_expression_block` runs with `target_type`, the division was already checked

---

## Proposed Solutions

### Option 1: Delayed Expression Analysis (Architecturally Correct)

**Approach:** Defer analyzing assign statement expressions until `_finalize_expression_block`.

**Changes Required:**

1. **Skip assign expression analysis in statement loop**
   ```python
   # In _analyze_statements_with_context, line ~145-165
   if stmt_type == "assign_statement":
       if is_expression_block:
           # Validate structure but DON'T analyze expression yet
           if not is_last_statement:
               self._error("'assign' statement must be the last statement", stmt)
           # Skip self._analyze_statement(stmt) for assign statements
           continue  # Expression will be analyzed in _finalize_expression_block
   ```

2. **Update _finalize_expression_block to handle full analysis**
   - Already has `assign_value = last_statement.get("value")`
   - Already calls `self._analyze_expression(assign_value, context_type)`
   - This would now be the FIRST (and only) time the expression is analyzed

**Pros:**
- Architecturally correct solution
- Ensures expressions always have proper type context
- Consistent with the principle that expression blocks need explicit types

**Cons:**
- More invasive change
- Need to carefully handle validation vs. analysis separation
- May affect other code paths

---

### Option 2: Relaxed Division Checking (Quick Workaround)

**Approach:** Allow concrete/concrete division without explicit `target_type` when inside an expression block context.

**Changes Required:**

1. **Pass block context to division analyzer**
   - Thread block context through expression analyzer
   - Or use a context manager/stack to track current block type

2. **Relax division check conditionally**
   ```python
   # In binary_ops_analyzer.py, _analyze_float_division()
   if not one_comptime and target_type is None and node is not None:
       # Allow if we're in an expression block (will be validated at block level)
       if not self._in_expression_block_context():
           self._error("Concrete type division requires explicit result type", node)
           return HexenType.UNKNOWN
   ```

**Pros:**
- Minimal code changes
- Quick fix that unblocks tests
- Less risky in the short term

**Cons:**
- Doesn't address root cause
- Weakens type checking guarantees
- May hide other issues
- Not consistent with Hexen's "explicit is better" philosophy

---

### Option 3: Hybrid Approach (Recommended)

**Approach:** Implement delayed analysis (Option 1) but with careful incremental changes.

**Phase 1: Minimal Changes**
1. Add a flag to assign statements: `analyzed: bool = False`
2. In statement loop, mark assign statements but skip expression analysis
3. In `_finalize_expression_block`, check if already analyzed

**Phase 2: Cleanup**
1. Remove the flag once confident
2. Simplify the statement analysis logic
3. Add comprehensive tests

**Pros:**
- Architecturally correct
- Incremental, testable changes
- Easy to debug and revert if needed

**Cons:**
- Takes more time than Option 2
- Requires careful testing

---

## Testing Strategy

### Manual Test Case

```hexen
func test(a: f64, b: f64) : f64 = {
    val result : f64 = if b == 0.0 {
        return 0.0
    } else {
        -> a / b
    }
    return result
}
```

Run with:
```bash
uv run python -c "
from tests.semantic import parse_and_analyze
code = '''[paste code above]'''
ast, errors = parse_and_analyze(code)
for e in errors: print(f'Error: {e}')
"
```

### Automated Tests

All tests in `tests/semantic/test_conditionals.py`:
- `TestAdvancedValidationPatterns::test_guard_clause_pattern`
- `TestComplexIntegrationPatterns::test_conditionals_with_complex_binary_operations`
- `TestTypeSystemIntegration::test_nested_conditionals_with_type_propagation`

Run with:
```bash
uv run pytest tests/semantic/test_conditionals.py::TestAdvancedValidationPatterns::test_guard_clause_pattern -v
```

---

## Current Status

### Completed
- ✅ Fixed all 14 label syntax parser test failures
- ✅ Added `target_type` parameter throughout the block analysis chain
- ✅ Verified type context reaches `_finalize_expression_block`
- ✅ Identified root cause: premature expression analysis

### Remaining
- ❌ 3 conditional expression tests still failing
- ⏳ Need to implement delayed expression analysis
- ⏳ Need to remove debug print statements added during investigation

### Files with Debug Code (Remove Before Committing)
- `src/hexen/semantic/binary_ops_analyzer.py:279` - Debug print
- `src/hexen/semantic/block_analyzer.py:260` - Debug print

---

## Related Documentation

- **TYPE_SYSTEM.md** - Type system philosophy and rules
- **UNIFIED_BLOCK_SYSTEM.md** - Block analysis architecture
- **BINARY_OPS.md** - Binary operation type rules including division
- **CONDITIONAL_SYSTEM.md** - Conditional expression semantics

---

## Next Steps

1. **Decision:** Choose solution approach (Option 1, 2, or 3)
2. **Implementation:** Implement chosen solution
3. **Testing:** Verify all 3 conditional tests pass
4. **Regression Testing:** Run full test suite (currently 1933/1936 passing)
5. **Cleanup:** Remove debug print statements
6. **Documentation:** Update if new patterns emerge

---

**Last Updated:** 2025-10-30
**Author:** Investigation by Claude Code
