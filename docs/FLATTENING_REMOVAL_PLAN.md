# Array Flattening Removal Plan

**Date:** 2025-10-25
**Status:** Planning Phase
**Reason:** Moving array dimension transformations to future standard library (per ARRAY_TYPE_SYSTEM.md design decision)

---

## Executive Summary

This document outlines the complete removal of array flattening functionality from the Hexen core language. Array flattening (transforming multidimensional arrays like `[2][3]i32` → `[6]i32`) was originally implemented as a core language feature but has been redesigned as a future standard library concern to keep the core language focused on **type safety**, **memory layout**, and **element access**.

### Impact Overview

| Metric | Value |
|--------|-------|
| **Lines Removed** | ~860-1,010 lines |
| **Files Modified** | 8 core files + tests |
| **Tests Removed** | ~25-30 flattening tests |
| **Tests Remaining** | ~1,330+ (from current 1,354) |
| **Complexity Reduction** | High (removes entire subsystem) |

---

## Background & Rationale

### Design Decision Context

From **ARRAY_TYPE_SYSTEM.md** (current specification):

> **Core Language Focus**: The array type system focuses purely on **type safety**, **memory layout**, and **element access**. Advanced array operations (filtering, mapping, sorting, etc.) are intentionally **not part of the core language** and will be provided by a future standard library to keep the language specification clean and focused.

**Key Distinctions** (from ARRAY_TYPE_SYSTEM.md):
- The `[..]` operator copies the **entire array with the same type** (e.g., `[3]i32` → `[3]i32`, `[2][3]i32` → `[2][3]i32`)
- Range-based slicing (covered in RANGE_SYSTEM.md) extracts **sub-arrays** using start/end indices
- **Dimension transformations** (like flattening 2D → 1D) will be provided by the future standard library

### What We're Keeping

✅ **Core array features remain:**
- Multidimensional array structure (`[N][M]T` syntax)
- Row access (`matrix[0]` returns view)
- Element access (`matrix[0][1]` returns element)
- Comptime array flexibility
- Full-range slice operator `[..]` (unified with range system)
- Array type conversions (element type changes with same dimensions)

### What We're Removing

❌ **Flattening-specific features:**
- Dimension transformation logic (`[2][3]i32` → `[6]i32`)
- `[..]:[type]` syntax for dimension changes
- Comptime array "on-the-fly" flattening in function calls
- Flattening-specific error messages and validations
- Element count validation for dimension changes

---

## Phase 1: Test File Removal 🗑️

**Goal:** Remove flattening test files to prevent false failures during implementation removal.

### 1.1 Primary Flattening Test File

**File:** `tests/semantic/arrays/test_array_flattening.py`

**Details:**
- **Lines:** 463 lines
- **Test Classes:** 4 classes
- **Test Methods:** ~25 methods
- **Action:** **DELETE ENTIRE FILE**

**Test Classes to Remove:**
- `TestArrayFlatteningCore` - Core flattening operations (2D→1D, 3D→1D, size inference)
- `TestArrayFlatteningErrorHandling` - Error validation and edge cases
- `TestArrayFlatteningComplexScenarios` - Complex dimensional combinations
- `TestArrayFlatteningIntegration` - Integration with val/mut, expression blocks
- `TestBothOperatorsMandatory` - `[..]:[type]` requirement enforcement

### 1.2 Tests to Review in Other Files

**Files to check for flattening-related tests:**

| File | Search Pattern | Action |
|------|----------------|--------|
| `test_array_parameters.py` | "on-the-fly flattening", "flatten" | Remove flattening tests, keep regular parameter tests |
| `test_array_conversions.py` | "dimension change", "flatten" | Remove dimension change tests, keep element type conversion tests |
| `test_multidim_arrays.py` | "flatten" | Likely clean (structural tests only) - verify |
| `test_comptime_array_type.py` | "flatten" | Remove comptime flattening tests, keep comptime flexibility tests |

**Validation Command:**
```bash
grep -r "flatten" tests/semantic/arrays/*.py --exclude=test_array_flattening.py
```

---

## Phase 2: Implementation Removal 🔧

**Goal:** Remove flattening logic from semantic analyzers in dependency order.

### 2.1 Utility & Helper Removal (Leaf Dependencies)

#### File: `src/hexen/semantic/arrays/error_messages.py`

**Remove:**
- `flattening_element_count_mismatch()` (lines ~96-101)
- `cannot_flatten_inferred_dimensions()` (lines ~155-159)

**Impact:** 2 methods, ~10 lines

---

#### File: `src/hexen/semantic/arrays/array_types.py`

**Remove:**
- `can_flatten_to_1d()` method (line ~57+)

**Impact:** 1 method, ~5 lines

---

### 2.2 Multidimensional Analyzer Cleanup

#### File: `src/hexen/semantic/arrays/multidim_analyzer.py`

**Remove:**
- `analyze_array_flattening()` method (lines ~88-125)
- `ArrayFlattening` utility class (lines ~343-381)
  - `can_flatten()` static method
  - `calculate_flattened_size()` static method

**Update:**
- Module docstring (remove "flattening operations" reference, line ~4-5)
- Class docstring (remove "Safe array flattening" reference, line ~10)

**Impact:** 2 major methods + 1 utility class, ~100-150 lines

---

### 2.3 Declaration Analyzer Cleanup

#### File: `src/hexen/semantic/declaration_analyzer.py`

**Remove:**
- `_is_flattening_assignment()` method (line ~562+)
- `_handle_flattening_assignment()` method (line ~581+)

**Update in `analyze_declaration()` method:**
- Remove flattening detection/handling block (lines ~322-335):
  ```python
  # Check for array flattening before type compatibility validation
  flattening_handled = False
  if self._is_flattening_assignment(var_type, value_type):
      if self._handle_flattening_assignment(...):
          flattening_handled = True
      else:
          return

  # Use centralized declaration type compatibility validation only if not flattening
  if not flattening_handled:
      # ... existing type compatibility check
  ```

**Replace with:**
  ```python
  # Use centralized declaration type compatibility validation
  if not self._is_declaration_type_compatible(...):
      return
  ```

**Remove:**
- Multidim analyzer initialization comment (line ~84)
- Allow `[_]` dimensions comment for flattening context (line ~530)

**Impact:** 2 methods + integration logic, ~150-200 lines

---

### 2.4 Function Analyzer Cleanup

#### File: `src/hexen/semantic/function_analyzer.py`

**Remove:**
- `_can_flatten_comptime_array_to_parameter()` method (line ~434+)
- `_validate_flattening_element_count()` method (line ~486+)

**Update in parameter validation:**
- Remove flattening checks (lines ~394-405):
  ```python
  # Check if this is a valid flattening scenario
  if self._can_flatten_comptime_array_to_parameter(comptime_type, target_type):
      # Valid comptime array flattening - validate element counts
      if not self._validate_flattening_element_count(...):
          return
      # Flattening validation successful - allow materialization
      return
  # Not a valid flattening scenario - report error
  ```

**Replace with:**
  ```python
  # Report dimension mismatch error
  self._error(...dimension mismatch error...)
  return
  ```

**Update error messages:**
- Remove "Note: Comptime arrays can flatten to 1D parameters..." suggestion (line ~565)

**Impact:** 2 methods + validation logic, ~100-150 lines

---

### 2.5 Conversion Analyzer Simplification

#### File: `src/hexen/semantic/conversion_analyzer.py`

**Remove:**
- Dimension change detection for flattening (lines ~81-92)
- Flattening-specific dimension handling (lines ~322-370)

**Simplify array conversion logic:**
- Remove `is_dimension_change` variable and checks
- Remove inferred dimension flattening calculation
- Require **exact dimension match** for all array conversions

**Before (lines ~322-370):**
```python
is_dimension_change = len(source.dimensions) != len(target.dimensions)

# Complex logic for:
# - Dimension count validation
# - Inferred dimension flattening calculation
# - Partial flattening support
# - Fixed dimension matching after flattening
```

**After (simplified):**
```python
# Require exact dimension match for array conversions
if len(source.dimensions) != len(target.dimensions):
    self._error(
        f"Array dimension mismatch: cannot convert {source} to {target}\n"
        f"Array conversions require matching dimensions\n"
        f"For dimension transformations, use the standard library",
        node
    )
    return None

# Validate each dimension matches (with [_] inference support)
for src_dim, tgt_dim in zip(source.dimensions, target.dimensions):
    if tgt_dim == -1:  # Inferred dimension [_]
        continue  # Accept any source dimension size
    if src_dim != tgt_dim:
        self._error(
            f"Array dimension size mismatch: expected [{tgt_dim}], got [{src_dim}]",
            node
        )
        return None
```

**Impact:** Significant simplification, ~150-200 lines removed/simplified

---

### 2.6 Type Utility Cleanup

#### File: `src/hexen/semantic/type_util.py`

**Remove:**
- `is_valid_flattening` logic (lines ~189-207)

**Before (lines ~189-207):**
```python
# Check if this is a valid flattening operation (multidim → 1D)
is_valid_flattening = False
if len(type1.dimensions) > len(type2.dimensions):
    if len(type2.dimensions) == 1:
        if type2.dimensions[0] == -1:
            # Inferred size always allows flattening
            is_valid_flattening = True
        elif self._calculate_total_elements(type1.dimensions) == type2.dimensions[0]:
            is_valid_flattening = True

# Allow coercion if dimensions match exactly OR if valid flattening
if not (dimensions_match_exactly or is_valid_flattening):
    return False
```

**After (simplified):**
```python
# Array coercion requires exact dimension match
if not dimensions_match_exactly:
    return False
```

**Impact:** ~20-30 lines removed, logic simplified

---

## Phase 3: Documentation Updates 📝

**Goal:** Update documentation to reflect flattening removal.

### 3.1 Code Documentation

| File | Line(s) | Update |
|------|---------|--------|
| `src/hexen/semantic/arrays/__init__.py` | ~13 | Remove "Multidimensional array support with flattening" |
| `src/hexen/semantic/types.py` | ~284 | Remove "Array flattening with size inference" comment |

### 3.2 Test Documentation

| File | Action |
|------|--------|
| `tests/semantic/arrays/ARRAY_TEST_COVERAGE_MATRIX.md` | Update coverage matrix to remove flattening rows |
| `tests/semantic/arrays/WEEK2_TASK9_SUMMARY.md` | Add note: "Flattening removed per ARRAY_TYPE_SYSTEM.md design decision" |

### 3.3 Main Documentation

**No changes needed** - `docs/ARRAY_TYPE_SYSTEM.md` already reflects the new design (flattening removed in previous update).

---

## Phase 4: Validation ✅

**Goal:** Ensure removal is complete and test suite is healthy.

### 4.1 Test Suite Validation

**Command:**
```bash
uv run pytest tests/ -v
```

**Expected Results:**
- ✅ **Tests removed:** ~25-30 flattening tests
- ✅ **Tests remaining:** ~1,330+ tests
- ✅ **Pass rate:** 100% (all remaining tests pass)

**Critical Validations:**
- ✅ Multidimensional array structure tests pass
- ✅ Row access tests pass (`matrix[0]`)
- ✅ Element access tests pass (`matrix[0][1]`)
- ✅ Array copying with `[..]` tests pass (same dimensions)
- ✅ Comptime array flexibility tests pass

### 4.2 Code Quality Checks

**Commands:**
```bash
# Format check
uv run ruff format . --check

# Lint check
uv run ruff check .

# Type check (if applicable)
# mypy src/hexen/semantic/
```

### 4.3 Search for Remaining References

**Search for any missed flattening references:**
```bash
# Search Python files
grep -r "flatten" src/hexen/semantic/ --exclude-dir=__pycache__

# Search test files (should only return non-flattening tests)
grep -r "flatten" tests/semantic/ --exclude-dir=__pycache__

# Search documentation
grep -r "flatten" docs/ --exclude=FLATTENING_REMOVAL_PLAN.md
```

**Expected:** No references found (except this plan document)

---

## Implementation Checklist

Use this checklist during implementation:

### Phase 1: Test Removal
- [ ] Delete `tests/semantic/arrays/test_array_flattening.py`
- [ ] Review and clean `test_array_parameters.py`
- [ ] Review and clean `test_array_conversions.py`
- [ ] Review and clean `test_comptime_array_type.py`
- [ ] Verify `test_multidim_arrays.py` is clean

### Phase 2: Implementation Removal
- [ ] Remove methods from `arrays/error_messages.py`
- [ ] Remove method from `arrays/array_types.py`
- [ ] Clean `arrays/multidim_analyzer.py` (methods + class)
- [ ] Clean `declaration_analyzer.py` (methods + integration)
- [ ] Clean `function_analyzer.py` (methods + validation)
- [ ] Simplify `conversion_analyzer.py` (dimension logic)
- [ ] Simplify `type_util.py` (coercion logic)

### Phase 3: Documentation
- [ ] Update `arrays/__init__.py` docstring
- [ ] Update `types.py` comment
- [ ] Update `ARRAY_TEST_COVERAGE_MATRIX.md`
- [ ] Update `WEEK2_TASK9_SUMMARY.md`

### Phase 4: Validation
- [ ] Run full test suite (`pytest tests/ -v`)
- [ ] Verify ~1,330+ tests pass
- [ ] Run code quality checks (`ruff format`, `ruff check`)
- [ ] Search for remaining "flatten" references
- [ ] Manual testing of multidim arrays
- [ ] Manual testing of array copying

---

## Rollback Plan

If issues arise during removal:

1. **Git Reset:** Use version control to revert changes
   ```bash
   git checkout -- <file>
   ```

2. **Incremental Rollback:** Revert phases in reverse order:
   - Phase 4 → Phase 3 → Phase 2 → Phase 1

3. **Test-Driven Recovery:** After any rollback, run test suite to verify stability

---

## Post-Removal Verification

After completion, verify the following behaviors:

### ✅ What Should Still Work

```hexen
// Multidimensional array creation
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
val cube : [2][2][2]i32 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]

// Row access (returns view)
val row : [3]i32 = matrix[0]         // ✅ Works

// Element access
val elem : i32 = matrix[1][2]        // ✅ Works

// Full-array copy (same dimensions)
val matrix_copy : [_][_]i32 = matrix[..]  // ✅ Works

// Comptime array flexibility
val flexible = [[1, 2], [3, 4]]
val as_i32 : [_][_]i32 = flexible    // ✅ Works
val as_i64 : [_][_]i64 = flexible    // ✅ Works
```

### ❌ What Should Error

```hexen
// Dimension transformation (now library concern)
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
val flattened : [6]i32 = matrix[..]:[6]i32
// ❌ Error: Array dimension mismatch
//    For dimension transformations, use the standard library

// Direct dimension mismatch
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
val wrong : [4]i32 = matrix
// ❌ Error: Array dimension mismatch
```

---

## Timeline Estimate

| Phase | Estimated Time | Complexity |
|-------|---------------|------------|
| Phase 1: Test Removal | 15-30 minutes | Low (file deletion) |
| Phase 2: Implementation | 1-2 hours | Medium (careful edits) |
| Phase 3: Documentation | 15-30 minutes | Low (comment updates) |
| Phase 4: Validation | 30-60 minutes | Medium (thorough testing) |
| **Total** | **2.5-4 hours** | **Medium** |

---

## Success Criteria

✅ **Removal is successful when:**
1. All flattening tests removed (~25-30 tests)
2. All flattening implementation removed (~860-1,010 lines)
3. Test suite passes with ~1,330+ tests
4. No "flatten" references in codebase (except this document)
5. Multidimensional array core features work correctly
6. Code quality checks pass (ruff, format)

---

## Next Steps After Removal

Once flattening is removed, the codebase will be ready for:

1. **Range System Implementation** (RANGE_SYSTEM.md)
   - Unified view model for array slicing
   - `[..]` as full-range slice operator
   - Zero-cost view semantics

2. **Array-Range Integration**
   - Slicing with `array[start..end]`
   - View materialization on assignment
   - Cost transparency through assignment

3. **Standard Library Planning**
   - Array transformation functions (flatten, reshape, etc.)
   - Advanced array operations (filter, map, reduce)
   - Dimension manipulation utilities

---

## References

- **ARRAY_TYPE_SYSTEM.md** - Current array specification (flattening removed)
- **RANGE_SYSTEM.md** - Range system specification with view model
- **TYPE_SYSTEM.md** - Core type system philosophy
- **CLAUDE.md** - Development guidelines and conventions

---

**Document Status:** ✅ Ready for implementation
**Approval:** Pending user review
**Implementation:** Not started
