# Hexen Array System Implementation Plan 🦉

*Implementation Roadmap for Array Type System Integration*

> **Purpose**: This document provides a detailed implementation plan for updating the Hexen array system to align with the enhanced specifications in ARRAY_TYPE_SYSTEM.md, FUNCTION_SYSTEM.md, and UNIFIED_BLOCK_SYSTEM.md.

## 🎯 Implementation Progress

**Current Status**: Week 2 Partially Complete ✅ (6 of 9 tasks done)

| Phase | Status | Tests | Notes |
|-------|--------|-------|-------|
| Week 0: Parser Extensions | ✅ Complete | 21/21 passing | `[..]` and `.length` syntax working |
| Week 1: Semantic Analysis | ✅ Complete | 22/22 passing | Copy/property analysis implemented |
| Week 2: Array-Function Integration | 🔄 In Progress | 95/95 passing | 6 of 9 tasks complete (see below) |
| Week 3: Block Evaluation | ⏳ Pending | - | - |
| Week 4: Integration + Testing | ⏳ Pending | - | - |

**Overall Test Results**: 1081/1081 passing (100% success rate)

**Week 2 Progress Breakdown** (6/9 tasks complete):

✅ **Completed Tasks:**
1. **Multidimensional Array Support** - ConcreteArrayType dimension reduction working
   - Enabled 5 previously skipped tests
   - `matrix[0][..]` and `matrix[0].length` fully functional
2. **Explicit `[..]` for Function Arguments** - "Explicit Danger, Implicit Safety" enforcement
   - 13 comprehensive tests covering all argument scenarios
   - Clear error messages for missing `[..]` on concrete arrays
3. **Explicit `[..]` for Array Flattening** - Missing specification requirement discovered and fixed
   - 23 flattening tests (20 updated + 3 new error tests)
   - `val flat : [6]i32 = matrix[..]` now required (was silently allowed)
4. **Fixed-size array parameter matching** - Exact size validation complete
   - 24 total tests in test_array_parameters.py (13 explicit copy + 11 size matching)
   - Validates exact size equality across all dimensions ([3]i32 ≠ [4]i32)
   - Includes element type validation and dimension count checking
   - Comptime arrays adapt to target size seamlessly
5. **Inferred-size `[_]T` parameter support** - Accept any size, provide compile-time `.length`
   - 13 comprehensive tests covering all inferred-size scenarios
   - Single dimension inferred-size ([_]i32 accepts any size)
   - Multidimensional inferred dimensions ([_][4]i32, [3][_]i32, [_][_]i32)
   - `.length` property available within function scope
   - Comptime arrays work seamlessly with inferred-size parameters
6. **Explicit type conversion for all concrete array operations** - 35 comprehensive tests for array conversions
   - Element type conversions (same dimensions, requires `:[N]T` syntax)
   - Dimension flattening (calculated size match, e.g., [2][3] → [6])
   - Combined conversions (flattening + element type change)
   - Inferred-size wildcard `[_]T` accepts any size
   - Size validation (fixed sizes must match exactly)
   - Comprehensive error messages for all failure cases

⏳ **Remaining Tasks:**
7. **Pass-by-value parameter semantics** - Scalar parameter value copying
8. **`mut` parameter local copy behavior** - Design A enforcement with return value requirement
9. **Comptime array parameter adaptation** - Flexible comptime → concrete type materialization

## Overview

This plan captures the delta between the current array implementation and the updated specifications across three key areas:

1. **Pass-by-Value Semantics** for function parameters (FUNCTION_SYSTEM.md updates)
2. **Array-Function Integration** (new comprehensive section in FUNCTION_SYSTEM.md)
3. **Array Operations in Expression Blocks** (UNIFIED_BLOCK_SYSTEM.md enhancements)

## Summary of Documentation Changes

### FUNCTION_SYSTEM.md Changes
- **+440 lines** of new content
- Added "Parameter Passing Semantics: Pass-by-Value" section
- Clarified `mut` parameter behavior (local copies, not side effects)
- **NEW: Array-Function Integration** section (360+ lines)
- Updated all error messages for Design A consistency

### UNIFIED_BLOCK_SYSTEM.md Changes
- **+280 lines** of new content
- **NEW: Array Operations in Expression Blocks** section
- Compile-time vs runtime array block distinction
- Array-specific dual capability patterns (validation, caching, error handling)

### ARRAY_TYPE_SYSTEM.md Changes
- **~207 lines** modified (refinements and clarifications)
- Focus on core language features (no advanced operations yet)
- Explicit copy philosophy reinforced

## Source Code Structure Mapping

### Current Implementation Layout

```
src/hexen/semantic/
├── arrays/                          # Array-specific analyzers
│   ├── __init__.py
│   ├── array_types.py              # Core array type structures (ArrayDimension, ArrayTypeInfo)
│   ├── error_messages.py           # Array error message formatting
│   ├── literal_analyzer.py         # Array literal analysis
│   └── multidim_analyzer.py        # Multidimensional array handling
│
├── comptime/                        # Comptime type system
│   ├── __init__.py
│   ├── binary_operations.py        # Comptime binary op resolution
│   ├── block_evaluation.py         # Expression block compile-time evaluation
│   ├── declaration_support.py      # Comptime var declaration support
│   ├── literal_validation.py       # Comptime literal validation
│   └── type_operations.py          # Comptime type manipulation
│
├── function_analyzer.py             # Function call analysis
├── block_analyzer.py                # Block scope and control flow
├── return_analyzer.py               # Return statement validation
├── assignment_analyzer.py           # Assignment and type coercion
└── errors.py                        # Error reporting infrastructure
```

### Implementation Change Mapping

| Documentation Section | Target Source File | New Components |
|----------------------|-------------------|----------------|
| **Pass-by-Value Semantics** | `function_analyzer.py` | Parameter passing logic |
| **Fixed-Size Array Params** | `function_analyzer.py` | Exact size matching |
| **Inferred-Size Params** | `arrays/array_types.py` | `.length` property support |
| **Comptime Array Adaptation** | `comptime/type_operations.py` | Parameter context resolution |
| **Explicit Copy Enforcement** | `arrays/literal_analyzer.py` | `[..]` syntax validation |
| **Array Return Values** | `return_analyzer.py` | RVO preparation |
| **Compile-Time Array Blocks** | `comptime/block_evaluation.py` | Array block classification |
| **Runtime Array Blocks** | `comptime/block_evaluation.py` | Context requirement |
| **Array Validation Patterns** | `block_analyzer.py` | Dual capability support |
| **Error Messages** | `arrays/error_messages.py` | New array-function errors |

## Implementation Phases

---

## Phase 1: Pass-by-Value Semantics Foundation

### 1.1 Parameter Passing Implementation

**Current State**: Unclear parameter passing semantics
**Target State**: Explicit pass-by-value with stack-based copying

**Target File**: `src/hexen/semantic/function_analyzer.py`

#### Implementation Tasks:

```python
# In semantic analyzer - parameter passing
class ParameterPassingAnalyzer:
    """
    Implement pass-by-value semantics for all parameter types
    """

    def analyze_parameter_passing(self, param_type, arg_value):
        """
        Key decisions:
        1. All parameters copied to function stack frame
        2. mut parameters allow local reassignment
        3. Caller's values never modified
        4. Arrays require explicit [..] for concrete arrays
        5. Comptime arrays materialize (not copy) on first use
        """

        if is_array_type(param_type):
            # Array parameter handling
            if is_comptime_array(arg_value):
                # First materialization - no copy needed
                return self.materialize_comptime_array(arg_value, param_type)
            else:
                # Concrete array - must have explicit [..]
                if not has_explicit_copy_syntax(arg_value):
                    raise SemanticError(
                        "Missing explicit copy syntax for array argument",
                        suggestion=f"Use {arg_value}[..] for explicit copy"
                    )
                return self.copy_array_to_param(arg_value, param_type)
        else:
            # Scalar parameter - copy value
            return self.copy_value_to_param(arg_value, param_type)
```

#### Error Messages to Implement:

```
Error: Missing explicit copy syntax for array argument
  Function: analyze(data: [100]f64)
  Argument: measurements (concrete array [100]f64)
  Arrays require explicit copy syntax to make performance costs visible
  Suggestion: analyze(measurements[..])
```

### 1.2 Mutable Parameter Semantics

**Current State**: Unclear mut parameter behavior
**Target State**: Local copy modification only

#### Implementation Tasks:

```python
# In semantic analyzer - mutable parameters
class MutableParameterAnalyzer:
    """
    Enforce Design A: mut parameters modify local copies
    """

    def validate_mut_parameter_function(self, func_decl):
        """
        Validate that mut parameter functions return modified values
        """

        for param in func_decl.parameters:
            if param.is_mutable:
                # Check if function returns appropriate type
                if func_decl.return_type == 'void':
                    # Check if parameter is actually modified
                    if self.is_parameter_modified(func_decl.body, param.name):
                        raise SemanticError(
                            "Mutable parameter function must return modified value",
                            location=func_decl.location,
                            suggestion=f"Change return type to {param.type} and add 'return {param.name}'"
                        )
```

#### Error Messages to Implement:

```
Error: Mutable array parameter function must return array
  Function: scale_vector(mut data: [3]f64, factor: f64) : void
  Mutable array parameters modify local copies due to pass-by-value semantics
  To communicate changes, function must return the modified array
  Suggestion: Change return type to [3]f64 and add 'return data'
```

---

## Phase 2: Array-Function Integration

### 2.1 Fixed-Size Array Parameters

**Current State**: Basic array parameter support
**Target State**: Exact size matching with clear error messages

**Target Files**:
- `src/hexen/semantic/function_analyzer.py` (size matching logic)
- `src/hexen/semantic/arrays/error_messages.py` (size mismatch errors)

#### Implementation Tasks:

```python
# In semantic analyzer - array parameters
class ArrayParameterAnalyzer:
    """
    Implement fixed-size array parameter matching
    """

    def check_array_parameter_match(self, param_type, arg_type):
        """
        Fixed-size arrays must match exactly: [3]i32 != [4]i32
        """

        if param_type.is_fixed_size and arg_type.is_fixed_size:
            if param_type.size != arg_type.size:
                raise SemanticError(
                    f"Array size mismatch in function call",
                    expected=f"[{param_type.size}]{param_type.element_type}",
                    found=f"[{arg_type.size}]{arg_type.element_type}",
                    message="Array sizes must match exactly for fixed-size parameters"
                )
```

#### Test Cases:

```hexen
// Should pass
func process_triple(values: [3]i32) : i32 = { ... }
val triple : [3]i32 = [10, 20, 30]
process_triple(triple[..])  // ✅ Exact size match

// Should fail
val quad : [4]i32 = [10, 20, 30, 40]
process_triple(quad[..])  // ❌ Error: [4]i32 != [3]i32
```

### 2.2 Inferred-Size Array Parameters `[_]T`

**Current State**: May not be implemented
**Target State**: Accept any size, provide `.length` compile-time constant

**Target Files**:
- `src/hexen/semantic/arrays/array_types.py` (ArrayDimension already has `is_inferred()`)
- `src/hexen/semantic/function_analyzer.py` (parameter resolution)
- `src/hexen/semantic/expression_analyzer.py` (`.length` property)

#### Implementation Tasks:

```python
# In semantic analyzer - inferred-size parameters
class InferredSizeParameterAnalyzer:
    """
    Implement [_]T parameter type that accepts any size
    """

    def resolve_inferred_parameter_type(self, param_type, arg_type):
        """
        [_]T accepts any [N]T, with .length known at compile-time
        """

        if param_type.is_inferred_size:
            # Accept any size, but track actual size for .length
            if not is_array_type(arg_type):
                raise SemanticError(
                    f"Expected array type for [_] parameter, got {arg_type}"
                )

            # The actual size becomes known within the function
            return ArrayType(
                element_type=param_type.element_type,
                size=arg_type.size,  # Known at compile-time
                is_inferred=True
            )
```

#### `.length` Property Implementation:

```python
# In expression analyzer - array length property
class ArrayLengthAnalyzer:
    """
    Implement .length as compile-time constant
    """

    def analyze_length_property(self, array_expr):
        """
        array.length returns compile-time constant i32
        """

        array_type = self.get_type(array_expr)

        if not array_type.size_is_known:
            raise SemanticError(
                "Cannot access .length on array with unknown size"
            )

        # Return comptime_int with known value
        return ComptimeIntLiteral(value=array_type.size)
```

#### Test Cases:

```hexen
// Should pass
func sum_array(numbers: [_]i32) : i32 = {
    mut total : i32 = 0
    mut i : i32 = 0
    while i < numbers.length {  // .length is compile-time constant
        total = total + numbers[i]
        i = i + 1
    }
    return total
}

sum_array([1, 2, 3][..])      // [_]i32 with .length = 3
sum_array([1, 2, 3, 4, 5][..]) // [_]i32 with .length = 5
```

### 2.3 Comptime Array Type Preservation in Functions

**Current State**: May not preserve comptime array types
**Target State**: Comptime arrays adapt to parameter types

#### Implementation Tasks:

```python
# In type system - comptime array parameter resolution
class ComptimeArrayParameterResolver:
    """
    Comptime arrays adapt seamlessly to parameter types
    """

    def resolve_comptime_array_to_parameter(self, comptime_array, param_type):
        """
        comptime_array_int → [N]i32 / [N]i64 / [N]f64 based on parameter
        """

        if not isinstance(comptime_array, ComptimeArrayType):
            return comptime_array  # Not comptime, use normal rules

        # Comptime array materializes to match parameter type
        if is_array_parameter(param_type):
            return self.materialize_comptime_array(
                comptime_array,
                target_element_type=param_type.element_type,
                target_size=param_type.size
            )
```

#### Test Cases:

```hexen
// Should preserve flexibility
val flexible_data = [42, 100, 200]  // comptime_array_int

func process_f64(data: [_]f64) : f64 = { ... }
func process_i32(data: [_]i32) : i32 = { ... }

val stats : f64 = process_f64(flexible_data)  // comptime → [3]f64
val sum : i32 = process_i32(flexible_data)    // Same source → [3]i32
```

### 2.4 Array Return Values and RVO

**Current State**: Basic array returns
**Target State**: Semantic copies with RVO optimization potential

#### Implementation Tasks:

```python
# In code generation - RVO preparation
class ArrayReturnOptimizer:
    """
    Prepare for Return Value Optimization

    Note: Initial implementation may not optimize, but structure
    should allow future RVO implementation
    """

    def analyze_array_return(self, return_stmt, func_return_type):
        """
        Structure return for potential RVO:
        1. Identify return value source
        2. Check if direct return (no copy needed)
        3. Mark for future optimization
        """

        if is_array_type(func_return_type):
            return_value = return_stmt.value

            # Case 1: Returning local array directly
            if is_local_variable(return_value):
                # Mark for RVO: can write directly to caller's space
                return_value.rvo_candidate = True

            # Case 2: Returning expression block result
            elif is_expression_block(return_value):
                # Mark for RVO: block can build in caller's space
                return_value.rvo_candidate = True

            # Case 3: Returning explicit copy
            elif has_explicit_copy_operator(return_value):
                # Semantic copy - may optimize later
                pass
```

**Note**: Initial implementation may perform actual copies. RVO optimization can be added later as a performance enhancement without changing language semantics.

---

## Phase 3: Expression Block Array Integration

### 3.1 Compile-Time Array Blocks

**Current State**: Basic expression blocks
**Target State**: Preserve comptime array types in compile-time evaluable blocks

**Target Files**:
- `src/hexen/semantic/comptime/block_evaluation.py` (already handles block classification)
- `src/hexen/semantic/arrays/literal_analyzer.py` (array literal handling in blocks)

**Note**: The file `block_evaluation.py` is substantial (38KB), suggesting it already has sophisticated block analysis. We need to extend it to handle array-specific compile-time evaluation.

#### Implementation Tasks:

```python
# In block analyzer - compile-time array blocks
class ComptimeArrayBlockAnalyzer:
    """
    Implement compile-time evaluable array blocks
    """

    def analyze_array_expression_block(self, block):
        """
        Determine if array block is compile-time evaluable
        """

        # Check block contents for runtime operations
        if self.has_function_calls(block):
            return RuntimeEvaluableBlock(block)

        if self.has_runtime_conditions(block):
            return RuntimeEvaluableBlock(block)

        # All array operations are comptime
        if self.all_arrays_are_comptime(block):
            return ComptimeEvaluableBlock(block)

        # Mixed comptime + concrete = runtime
        if self.has_concrete_arrays(block):
            return RuntimeEvaluableBlock(block)
```

#### Test Cases:

```hexen
// Should preserve comptime array type
val flexible_array = {
    val base = [1, 2, 3, 4, 5]  // comptime_array_int
    -> base                      // Preserves comptime_array_int
}

val as_i32 : [_]i32 = flexible_array  // → [5]i32
val as_f64 : [_]f64 = flexible_array  // Same source → [5]f64
```

### 3.2 Runtime Array Blocks

**Current State**: Basic expression blocks
**Target State**: Require explicit context for runtime array operations

#### Implementation Tasks:

```python
# In block analyzer - runtime array blocks
class RuntimeArrayBlockAnalyzer:
    """
    Enforce explicit context for runtime array blocks
    """

    def validate_runtime_array_block(self, block, target_var):
        """
        Runtime array blocks must have explicit type annotation
        """

        if self.is_runtime_evaluable(block):
            if not target_var.has_explicit_type:
                raise SemanticError(
                    "Runtime array block requires explicit type context",
                    location=block.location,
                    reason="Block contains function calls or concrete arrays",
                    suggestion=f"Add explicit type: val {target_var.name} : [_]T = {{ ... }}"
                )
```

#### Error Messages:

```
Error: Runtime array block requires explicit type context
  Block contains function calls (functions always return concrete types)
  Suggestion: val result : [_]f64 = { ... }
```

### 3.3 Array Dual Capability Patterns

**Current State**: Basic `->` and `return` support
**Target State**: Powerful array validation and error handling patterns

#### Implementation Tasks:

```python
# In block analyzer - array validation patterns
class ArrayValidationPatternAnalyzer:
    """
    Support array validation with early returns
    """

    def analyze_array_validation_block(self, block):
        """
        Support patterns like:

        val validated : [_]i32 = {
            val input = get_array()
            if input.length == 0 {
                return [0, 0, 0]  // Early function exit
            }
            -> input[..]  // Explicit copy
        }
        """

        # Validate that all return paths:
        # 1. Return correct type (array matching function return)
        # 2. -> paths have explicit copy syntax for concrete arrays
        # 3. Paths are exhaustive or have -> fallback
```

#### Test Cases:

```hexen
// Should support validation with early returns
func process_user_array() : [_]i32 = {
    val validated : [_]i32 = {
        val input = get_input()
        if input.length == 0 {
            return [0, 0, 0]  // Early function exit
        }
        if input.length > 1000 {
            return [-1]  // Early function exit
        }
        -> input[..]  // Success: explicit copy
    }
    return process_array(validated)
}
```

---

## Phase 4: Error Message Enhancements

### 4.1 Array-Specific Error Messages

#### Implementation Tasks:

Create comprehensive, actionable error messages for:

1. **Array size mismatch**:
```
Error: Array size mismatch in function call
  Function: process_triple(values: [3]i32)
  Argument: quad of type [4]i32
  Expected: [3]i32
  Found: [4]i32
  Array sizes must match exactly for fixed-size parameters
```

2. **Missing explicit copy**:
```
Error: Missing explicit copy syntax for array argument
  Function: analyze(data: [100]f64)
  Argument: measurements (concrete array [100]f64)
  Arrays require explicit copy syntax to make performance costs visible
  Suggestion: analyze(measurements[..])
```

3. **Mutable array parameter without return**:
```
Error: Mutable array parameter function must return array
  Function: scale_vector(mut data: [3]f64, factor: f64) : void
  Mutable array parameters modify local copies due to pass-by-value semantics
  To communicate changes, function must return the modified array
  Suggestion: Change return type to [3]f64 and add 'return data'
```

4. **Runtime array block without context**:
```
Error: Runtime array block requires explicit type context
  Block contains function calls (functions always return concrete types)
  Suggestion: val result : [_]f64 = { ... }
```

---

## Phase 5: Testing Strategy

### 5.1 Unit Tests

#### Parameter Passing Tests:

```python
# tests/semantic/test_array_parameters.py

def test_fixed_size_parameter_exact_match():
    """Fixed-size parameters require exact size match"""
    code = """
    func process(data: [3]i32) : i32 = { return data[0] }
    val arr : [3]i32 = [1, 2, 3]
    process(arr[..])
    """
    assert_compiles(code)

def test_fixed_size_parameter_size_mismatch():
    """Fixed-size parameters reject wrong size"""
    code = """
    func process(data: [3]i32) : i32 = { return data[0] }
    val arr : [4]i32 = [1, 2, 3, 4]
    process(arr[..])
    """
    assert_error(code, "Array size mismatch")

def test_inferred_size_parameter_any_size():
    """Inferred-size parameters accept any size"""
    code = """
    func sum(data: [_]i32) : i32 = {
        mut total : i32 = 0
        mut i : i32 = 0
        while i < data.length {
            total = total + data[i]
            i = i + 1
        }
        return total
    }
    sum([1, 2, 3][..])
    sum([1, 2, 3, 4, 5][..])
    """
    assert_compiles(code)
```

#### Comptime Array Tests:

```python
def test_comptime_array_parameter_adaptation():
    """Comptime arrays adapt to parameter types"""
    code = """
    func process_f64(data: [_]f64) : f64 = { return data[0] }
    func process_i32(data: [_]i32) : i32 = { return data[0] }

    val flexible = [42, 100, 200]
    val f : f64 = process_f64(flexible)
    val i : i32 = process_i32(flexible)
    """
    assert_compiles(code)
```

#### Mutable Parameter Tests:

```python
def test_mut_array_parameter_requires_return():
    """Mutable array parameters that modify must return"""
    code = """
    func scale(mut data: [_]f64, factor: f64) : void = {
        data[0] = data[0] * factor
        return
    }
    """
    assert_error(code, "Mutable array parameter function must return")

def test_mut_array_parameter_with_return():
    """Mutable array parameters with return are valid"""
    code = """
    func scale(mut data: [_]f64, factor: f64) : [_]f64 = {
        mut i : i32 = 0
        while i < data.length {
            data[i] = data[i] * factor
            i = i + 1
        }
        return data
    }
    """
    assert_compiles(code)
```

### 5.2 Integration Tests

#### End-to-End Scenarios:

```python
def test_array_processing_pipeline():
    """Complete array processing with functions"""
    code = """
    func normalize(data: [_]f64) : [_]f64 = {
        val max = find_max(data)
        return scale_by_max(data, max)
    }

    val sensor_data : [1000]f64 = load_sensors()
    val normalized : [1000]f64 = normalize(sensor_data[..])
    """
    assert_compiles(code)

def test_array_validation_with_early_returns():
    """Array validation using dual capability"""
    code = """
    func safe_process(input: [_]i32) : [_]i32 = {
        val validated : [_]i32 = {
            if input.length == 0 {
                return [0, 0, 0]
            }
            if input.length > 1000 {
                return [-1]
            }
            -> input[..]
        }
        return transform(validated)
    }
    """
    assert_compiles(code)
```


---

## Implementation Checklist

### Parser Extensions (Week 0) ✅ COMPLETED
- [x] Grammar extensions for `[..]` copy operator
- [x] Grammar extensions for `.length` property access
- [x] AST node types: `ARRAY_COPY`, `PROPERTY_ACCESS`
- [x] Parser transformers implementation
- [x] Parser unit tests (21 tests)

### Semantic Analysis (Week 1) ✅ COMPLETED
- [x] Array copy semantic analysis (`analyze_array_copy`)
- [x] Property access semantic analysis (`analyze_property_access`)
- [x] Error messages for non-array copy operations
- [x] Error messages for property access on non-arrays
- [x] Expression dispatcher integration
- [x] Semantic unit tests (22 tests passing, all enabled)

### Core Functionality (Week 2 - 🔄 In Progress: 6/9 Complete)
- [x] **ConcreteArrayType implementation** - Multidimensional array support complete
- [x] **Explicit `[..]` copy syntax enforcement for function args** - 13 tests passing
- [x] **Explicit `[..]` copy syntax enforcement for array flattening** - 23 tests passing (discovered missing requirement)
- [x] **Fixed-size array parameter matching** - 11 tests passing (exact size validation across all dimensions)
- [x] **Inferred-size `[_]T` parameter support** - 13 tests passing (accepts any size, provides `.length`)
- [x] **Explicit type conversion for all concrete array operations** - 35 comprehensive tests covering:
  - [x] Element type conversions (`[N]i32→[N]i64`) - 8 tests
  - [x] Inferred-size wildcard behavior (`[_]T` accepts any size) - 5 tests
  - [x] Dimension conversions/flattening (`[2][3]i32→[6]i32`) - 5 tests
  - [x] Combined conversions (`[2][3]i32→[6]i64`) - 5 tests
  - [x] Conversion error cases (size mismatches, invalid types) - 5 tests
  - [x] Comptime array conversions (ergonomic adaptation) - 3 tests
  - [x] Conversions in various expression contexts - 4 tests
- [ ] Pass-by-value parameter semantics
- [ ] `mut` parameter local copy behavior
- [ ] Comptime array parameter adaptation

### Expression Block Integration (Week 3)
- [ ] Compile-time array block detection
- [ ] Runtime array block context requirement
- [ ] Array validation with early returns
- [ ] Array caching patterns
- [ ] Bounds checking with fallbacks

### Error Messages (Week 2-4)
- [x] Array copy operation errors (Week 1)
- [x] Property access errors (Week 1)
- [x] Missing explicit copy errors for function arguments (Week 2)
- [x] Missing explicit copy errors for array flattening (Week 2)
- [x] Array size mismatch errors (Week 2 Part 4)
- [ ] Mutable array parameter errors
- [ ] Runtime block context errors
- [ ] All error messages with actionable suggestions

### Testing (Week 0-2)
- [x] Parser unit tests (Week 0) - 21 tests
- [x] Semantic tests for copy/property (Week 1) - 22 tests
- [x] Multidimensional array tests (Week 2) - 5 tests enabled
- [x] Array parameter explicit copy tests (Week 2) - 13 tests
- [x] Array flattening tests (Week 2) - 23 tests (20 updated + 3 new)
- [x] Fixed-size array parameter matching tests (Week 2 Part 4) - 11 tests
- [x] Inferred-size parameter tests (Week 2 Part 5) - 13 tests
- [x] Array type conversion tests (Week 2 Part 6) - 35 comprehensive tests
- [ ] Unit tests for all parameter types (remaining: mut behavior, comptime adaptation)
- [ ] Mutable parameter tests
- [ ] Comptime array adaptation tests
- [ ] Expression block array tests
- [ ] Integration tests for complete scenarios

### Documentation
- [x] Implementation plan tracking (this document)
- [ ] Implementation notes in all three docs
- [ ] Code examples validated
- [ ] Error message reference complete
- [ ] Developer guidance comprehensive

---

## Future Enhancements (Post Phase I)

### Potential Optimizations:
1. **RVO Implementation**: Eliminate physical copies for array returns
2. **Copy Elision**: Optimize away explicit [..] when safe
3. **Reference Parameters**: Add `&` and `&mut` for zero-copy (Phase II)
4. **SIMD Support**: Vectorize array operations when beneficial

### Language Extensions:
1. **Default Parameters**: Array parameters with defaults
2. **Generic Functions**: `func process<T>(data: [_]T) : T`
3. **Function Overloading**: Multiple signatures based on array types
4. **Advanced Array Operations**: map, filter, reduce (standard library)

---

## Success Criteria

Implementation is complete when:

1. ✅ All tests pass (unit + integration)
2. ✅ All error messages match specification
3. ✅ Documentation aligned with implementation
4. ✅ Examples from docs compile correctly
5. ✅ Performance characteristics documented
6. ✅ Pass-by-value semantics fully enforced
7. ✅ Comptime array flexibility preserved
8. ✅ Array-function integration seamless

## File-Specific Implementation Priorities

### High Priority Files (Core Changes)

#### 1. `src/hexen/semantic/function_analyzer.py`
**Current**: ~200 lines, already handles function call analysis
**Changes Needed**:
- Add parameter passing pass-by-value logic
- Implement fixed-size array parameter exact matching
- Add inferred-size parameter resolution
- Enforce explicit `[..]` for concrete array arguments
- Add comptime array parameter adaptation

**Estimated Impact**: +150-200 lines

#### 2. `src/hexen/semantic/arrays/error_messages.py`
**Current**: ~9KB, handles array error formatting
**Changes Needed**:
- Add array size mismatch error message
- Add missing explicit copy error message
- Add mutable array parameter error message
- Add runtime array block context error message

**Estimated Impact**: +100-150 lines

#### 3. `src/hexen/semantic/comptime/block_evaluation.py`
**Current**: ~38KB, sophisticated block evaluation logic
**Changes Needed**:
- Extend compile-time evaluability check for arrays
- Add runtime array block detection
- Implement array-specific context requirements

**Estimated Impact**: +200-300 lines (extension of existing logic)

#### 4. `src/hexen/semantic/arrays/array_types.py`
**Current**: ~93 lines, core array type structures
**Changes Needed**:
- Add `.length` property support to ArrayTypeInfo
- Extend ArrayDimension with size resolution logic

**Estimated Impact**: +50-100 lines

### Medium Priority Files (Integration)

#### 5. `src/hexen/semantic/return_analyzer.py`
**Changes**: Add array return RVO preparation markers
**Estimated Impact**: +50-100 lines

#### 6. `src/hexen/semantic/comptime/type_operations.py`
**Changes**: Add comptime array → parameter type materialization
**Estimated Impact**: +100-150 lines

#### 7. `src/hexen/semantic/arrays/literal_analyzer.py`
**Current**: ~19KB, handles array literal analysis
**Changes**: Extend for expression block context
**Estimated Impact**: +100-150 lines

### Low Priority Files (Minor Extensions)

#### 8. `src/hexen/semantic/block_analyzer.py`
**Changes**: Support array validation dual capability patterns
**Estimated Impact**: +50-100 lines

#### 9. `src/hexen/semantic/assignment_analyzer.py`
**Changes**: Validate array assignment explicit copy syntax
**Estimated Impact**: +50 lines

## Parser Extensions Required

### Grammar Changes (`src/hexen/hexen.lark`)

**Current State**: Grammar supports basic array access `[index]`
**Target State**: Support `[..]` copy operator and `.length` property

#### 1. Array Copy Operator `[..]`

**Location**: Extend `postfix` rule (line 55)

**Current**:
```lark
postfix: primary (array_access)*
array_access: "[" expression "]"
```

**Proposed**:
```lark
postfix: primary (array_suffix)*
array_suffix: array_access | array_copy
array_access: "[" expression "]"
array_copy: "[" ".." "]"
```

**Rationale**: `[..]` is syntactically similar to array access but semantically distinct (copies entire array vs accessing element). Separating into `array_suffix` allows both operations on the same expression.

#### 2. Property Access `.length`

**Location**: Extend `postfix` rule to include property access

**Proposed**:
```lark
postfix: primary (array_suffix | property_access)*
property_access: "." IDENTIFIER
```

**Considerations**:
- `.length` is currently the only property, but this syntax allows future properties
- Property access has lower precedence than array access: `arr[0].length` works
- Chaining works naturally: `matrix[0].length` (row length)

### AST Node Changes (`src/hexen/ast_nodes.py`)

**New Node Types Required**:

```python
# In ast_nodes.py NodeType enum
class NodeType(Enum):
    # ... existing types ...
    ARRAY_COPY = "array_copy"            # [..] operator
    PROPERTY_ACCESS = "property_access"   # .property operator
```

### Parser Implementation (`src/hexen/parser.py`)

#### 1. Array Copy Transformer

**Add to `HexenTransformer` class** (around line 389):

```python
def array_copy(self, children):
    # array_copy: "[" ".." "]"
    # No children - the ".." is implicit
    return {
        "type": NodeType.ARRAY_COPY.value,
        "array": None,  # Will be set by postfix handler
    }

def array_suffix(self, children):
    # array_suffix: array_access | array_copy
    return children[0]  # Pass through the child node
```

#### 2. Property Access Transformer

**Add to `HexenTransformer` class**:

```python
def property_access(self, children):
    # property_access: "." IDENTIFIER
    property_name = children[0]  # IDENTIFIER node
    return {
        "type": NodeType.PROPERTY_ACCESS.value,
        "object": None,  # Will be set by postfix handler
        "property": property_name["name"],
    }
```

#### 3. Update Postfix Handler

**Modify existing `postfix` method** (line 367):

```python
def postfix(self, children):
    # postfix: primary (array_suffix | property_access)*
    if len(children) == 1:
        return children[0]  # No suffixes

    # Chain array access, array copy, and property access
    expr = children[0]  # Base expression
    for suffix in children[1:]:
        if suffix["type"] == NodeType.ARRAY_ACCESS.value:
            suffix["array"] = expr
            expr = suffix
        elif suffix["type"] == NodeType.ARRAY_COPY.value:
            suffix["array"] = expr
            expr = suffix
        elif suffix["type"] == NodeType.PROPERTY_ACCESS.value:
            suffix["object"] = expr
            expr = suffix

    return expr
```

### Semantic Analysis Integration

Once parser changes are complete, semantic analyzers must handle new node types:

**Files to Update**:
1. `src/hexen/semantic/arrays/literal_analyzer.py` - Handle `ARRAY_COPY` nodes
2. `src/hexen/semantic/expression_analyzer.py` - Handle `PROPERTY_ACCESS` nodes (`.length`)

### Example AST Output

#### Array Copy Example
```hexen
val source : [3]i32 = [1, 2, 3]
val copy : [3]i32 = source[..]
```

**Expected AST** (relevant portion):
```python
{
    "type": "val_declaration",
    "name": "copy",
    "value": {
        "type": "array_copy",
        "array": {
            "type": "identifier",
            "name": "source"
        }
    }
}
```

#### Property Access Example
```hexen
val numbers : [5]i32 = [1, 2, 3, 4, 5]
val size : i32 = numbers.length
```

**Expected AST** (relevant portion):
```python
{
    "type": "val_declaration",
    "name": "size",
    "value": {
        "type": "property_access",
        "object": {
            "type": "identifier",
            "name": "numbers"
        },
        "property": "length"
    }
}
```

#### Combined Example
```hexen
val matrix : [3][4]i32 = [[1,2,3,4], [5,6,7,8], [9,10,11,12]]
val row_size : i32 = matrix[0].length  // Access first row, then get length
val copied_row : [4]i32 = matrix[1][..]  // Copy second row
```

### Testing Strategy for Parser

#### Unit Tests (`tests/parser/test_array_operations.py`)

```python
def test_array_copy_syntax():
    """Test [..] copy operator parsing"""
    code = "val copy : [3]i32 = source[..]"
    ast = parser.parse(code)
    # Verify ARRAY_COPY node structure
    assert ast['value']['type'] == 'array_copy'

def test_property_access_syntax():
    """Test .length property parsing"""
    code = "val size : i32 = arr.length"
    ast = parser.parse(code)
    # Verify PROPERTY_ACCESS node structure
    assert ast['value']['type'] == 'property_access'
    assert ast['value']['property'] == 'length'

def test_chained_array_operations():
    """Test array[index].length pattern"""
    code = "val row_len : i32 = matrix[0].length"
    ast = parser.parse(code)
    # Verify chained operations
    property_node = ast['value']
    assert property_node['type'] == 'property_access'
    assert property_node['object']['type'] == 'array_access'

def test_multidimensional_copy():
    """Test matrix[0][..] pattern"""
    code = "val row : [3]i32 = matrix[0][..]"
    ast = parser.parse(code)
    # Verify copy of array access result
    copy_node = ast['value']
    assert copy_node['type'] == 'array_copy'
    assert copy_node['array']['type'] == 'array_access'
```

### Implementation Priority

**Parser changes must be completed BEFORE semantic analysis work begins**, as the semantic analyzer depends on correct AST structure.

**Recommended Order**:
1. **Day 1**: Grammar file changes (`hexen.lark`)
2. **Day 2**: AST node types (`ast_nodes.py`)
3. **Day 3**: Parser transformers (`parser.py`)
4. **Day 4**: Parser unit tests
5. **Day 5**: Semantic analyzer integration

**Estimated Impact**: ~150-200 lines total
- Grammar: ~10 lines
- AST nodes: ~5 lines
- Parser: ~50-100 lines (including tests)
- Integration: ~50-100 lines

## Quick Start Implementation Order

For fastest results, implement in this order:

### ✅ **Week 0 (Prerequisite): Parser Extensions** [COMPLETED]
   - **Days 1-2**: Grammar + AST changes (`hexen.lark`, `ast_nodes.py`)
   - **Days 3-4**: Parser transformers (`parser.py`)
   - **Day 5**: Parser unit tests
   - **Deliverable**: `[..]` and `.length` syntax working in parser
   - **Status**: All 21 parser tests passing (292/292 total parser tests)
   - **Files changed**:
     - `src/hexen/hexen.lark` - Grammar extensions
     - `src/hexen/ast_nodes.py` - New AST node types
     - `src/hexen/parser.py` - Parser transformers
     - `tests/parser/test_array_operations.py` - Parser test suite

### ✅ **Week 1: Semantic Analysis for Array Operations** [COMPLETED]
   - `arrays/error_messages.py` - Array copy and property access errors
   - `arrays/literal_analyzer.py` - Array copy and property access semantic analysis
   - `expression_analyzer.py` - Expression dispatcher integration
   - **Deliverable**: Semantic analysis for `[..]` and `.length`
   - **Status**: 17/17 tests passing, 5 tests skipped (1001/1001 total tests)
   - **Files changed**:
     - `src/hexen/semantic/arrays/error_messages.py` - New error messages
     - `src/hexen/semantic/arrays/literal_analyzer.py` - Analyzers implemented
     - `src/hexen/semantic/expression_analyzer.py` - Dispatcher wiring
     - `tests/semantic/arrays/test_array_operations.py` - Semantic test suite

   **Skipped Tests (5) - Require ConcreteArrayType Implementation**:
   - `test_array_copy_of_array_access` - Copying result of array access (row copy)
   - `test_length_of_array_access` - Getting length of array access result
   - `test_access_then_copy_then_length` - Complex chaining: `matrix[i][..].length`
   - `test_multidimensional_access_then_length` - 3D array access then length
   - `test_unknown_property_error` - Property error on concrete arrays

   **Note**: These 5 tests require implementing `ConcreteArrayType` class for proper multidimensional array type handling. They test advanced array access patterns where array access returns another array type, which then needs property/copy operations. This should be addressed in **Week 2** during array-function integration when we implement proper array type structures.

### **Week 2: Array-Function Integration** - 🔄 In Progress (5/9 tasks complete)

#### **Week 2 Part 1: Multidimensional Array Support** ✅ COMPLETED
   - **Status**: Complete (1006/1006 tests passing)
   - **Files changed**:
     - `src/hexen/semantic/arrays/literal_analyzer.py` - Fixed duplicate import bug
     - `src/hexen/semantic/type_util.py` - Fixed error formatter for ConcreteArrayType
     - `tests/semantic/arrays/test_array_operations.py` - Enabled 5 skipped tests
   - **Achievement**: ConcreteArrayType infrastructure already existed and works correctly
   - **Impact**: All 22 array operations tests now passing

#### **Week 2 Part 2: Explicit Copy Requirement for Function Arguments** ✅ COMPLETED
   - **Status**: Complete (1019/1019 tests passing)
   - **Files changed**:
     - `src/hexen/semantic/function_analyzer.py` - Added `_check_array_argument_copy_requirement()` (+87 lines)
     - `src/hexen/semantic/arrays/error_messages.py` - Added `missing_explicit_copy_for_array_argument()`
     - `tests/semantic/arrays/test_array_parameters.py` - NEW FILE (298 lines, 13 tests)
   - **Implementation**: AST-based validation distinguishing safe cases (comptime arrays, fresh arrays) from dangerous cases (concrete variables)
   - **Design**: "Explicit Danger, Implicit Safety" principle - concrete arrays require `arr[..]`, comptime arrays adapt seamlessly

#### **Week 2 Part 3: Explicit Copy Requirement for Array Flattening** ✅ COMPLETED
   - **Status**: Complete (1022/1022 tests passing)
   - **Discovery**: Missing specification requirement found during implementation review
   - **Files changed**:
     - `src/hexen/semantic/declaration_analyzer.py` - Added explicit copy check in `_handle_flattening_assignment()` (+48 lines)
     - `tests/semantic/arrays/test_array_flattening.py` - Updated 20 tests + added 3 new error tests
   - **Specification Gap Fixed**: Array flattening (`val flat : [6]i32 = matrix`) was silently allowed without `[..]` operator
   - **Implementation**: Validates that flattening uses `array_copy` AST nodes, not plain `identifier` nodes
   - **Result**: `val flat : [6]i32 = matrix[..]` now required (consistent with function arguments and general array copying)

#### **Week 2 Part 4: Fixed-Size Array Parameter Matching** ✅ COMPLETED
   - **Status**: Complete (1033/1033 tests passing)
   - **Files changed**:
     - `src/hexen/semantic/function_analyzer.py` - Added `_check_array_size_compatibility()` method
     - `tests/semantic/arrays/test_array_parameters.py` - Added 11 comprehensive size matching tests (24 total tests)
   - **Implementation**: Validates exact size equality across all dimensions for fixed-size arrays
   - **Coverage**:
     - Exact size match validation ([3]i32 ≠ [4]i32)
     - Multidimensional array matching (both dimensions must match)
     - Element type validation (i32 ≠ f64)
     - Dimension count checking (1D ≠ 2D)
     - Comptime array adaptation to target size
   - **Error Messages**: Clear, actionable messages showing expected vs actual sizes

#### **Week 2 Part 5: Inferred-Size `[_]T` Parameter Support** ✅ COMPLETED
   - **Status**: Complete (1046/1046 tests passing)
   - **Files changed**:
     - `src/hexen/semantic/function_analyzer.py` - Enhanced `_check_array_size_compatibility()` to handle inferred dimensions
     - `src/hexen/semantic/symbol_table.py` - Added inferred-size parameter tracking in function scope
     - `tests/semantic/arrays/test_inferred_size_parameters.py` - NEW FILE (13 comprehensive tests)
   - **Implementation**: Inferred-size parameters accept any array size while providing compile-time `.length` access
   - **Coverage**:
     - Single dimension inferred-size ([_]i32 accepts [3]i32, [5]i32, etc.)
     - Multidimensional partial inference ([_][4]i32, [3][_]i32)
     - Multidimensional full inference ([_][_]i32)
     - Element type validation (must match exactly)
     - `.length` property available within function scope
     - Comptime arrays work seamlessly with inferred-size parameters
   - **Design**: Inferred dimensions (`_`) match any size, while fixed dimensions must match exactly

#### **Week 2 Part 6: Explicit Type Conversion for All Concrete Array Operations** ✅ COMPLETED
   - **Status**: Complete (1081/1081 tests passing)
   - **Files changed**:
     - `src/hexen/semantic/conversion_analyzer.py` - Extended for array type conversions (+160 lines)
     - `src/hexen/semantic/analyzer.py` - Wired up array type parsing callback
     - `tests/semantic/arrays/test_array_conversions.py` - NEW FILE (640 lines, 35 comprehensive tests)
   - **Implementation**: Full array-to-array conversion support with size validation, element type conversion, and dimension flattening
   - **Scope**: Enforce explicit `:type` syntax for ALL concrete array type conversions (not just flattening)
   - **Core Principle**: Following TYPE_SYSTEM.md's "Transparent Costs" principle - ANY type change requires explicit syntax
   - **Critical Rule**: **Array sizes are structural, not convertible** - sizes must match exactly (cannot convert `[3]i32 → [4]i32`)

   **Three Categories of Array Type Conversions:**

   **1. Element Type Conversion (SAME Size & Dimensions)**
   ```hexen
   // 1D arrays - SAME fixed size (3 elements)
   val source : [3]i32 = [1, 2, 3]
   // val widened : [3]i64 = source[..]          // ❌ Error: Missing explicit type conversion
   val widened : [3]i64 = source[..]:[3]i64      // ✅ Explicit element type conversion (i32→i64, SAME size 3)

   // 1D arrays - inferred size (accepts any size)
   val source : [3]i32 = [1, 2, 3]
   // val widened : [_]i64 = source[..]          // ❌ Error: Missing explicit type conversion
   val widened : [_]i64 = source[..]:[_]i64      // ✅ Explicit element type conversion (i32→i64, inferred size matches 3)

   // 2D arrays - SAME fixed dimensions (2×3)
   val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
   // val wider : [2][3]i64 = matrix[..]         // ❌ Error: Missing explicit type conversion
   val wider : [2][3]i64 = matrix[..]:[2][3]i64  // ✅ Explicit element type conversion (SAME dims 2×3)

   // 2D arrays - inferred dimensions (accepts any dimensions)
   // val wider : [_][_]i64 = matrix[..]         // ❌ Error: Missing explicit type conversion
   val wider : [_][_]i64 = matrix[..]:[_][_]i64  // ✅ Explicit element type conversion (inferred dims match 2×3)
   ```

   **2. Dimension Flattening (CALCULATED Size Match)**
   ```hexen
   val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]

   // Fixed-size target - exact size match required
   // val flat : [6]i32 = matrix[..]             // ❌ Error: Missing explicit type conversion
   val flat : [6]i32 = matrix[..]:[6]i32         // ✅ Flattening with exact size match (2×3=6)

   // Inferred-size target - accepts calculated size
   // val flat : [_]i32 = matrix[..]             // ❌ Error: Missing explicit type conversion
   val flat : [_]i32 = matrix[..]:[_]i32         // ✅ Flattening with inferred size (accepts 2×3=6)

   val cube : [2][2][2]i32 = [[[1,2],[3,4]], [[5,6],[7,8]]]
   // val flat : [8]i32 = cube[..]               // ❌ Error: Missing explicit type conversion
   val flat : [8]i32 = cube[..]:[8]i32           // ✅ Flattening with exact size match (2×2×2=8)
   // val flat : [_]i32 = cube[..]               // ❌ Error: Missing explicit type conversion
   val flat : [_]i32 = cube[..]:[_]i32           // ✅ Flattening with inferred size (accepts 2×2×2=8)

   // ❌ Fixed-size mismatch is ALWAYS an error
   // val wrong : [5]i32 = matrix[..]:[5]i32     // ❌ ERROR: 2×3=6 ≠ 5 (fixed size must match exactly)
   // val wrong : [7]i32 = matrix[..]:[7]i32     // ❌ ERROR: 2×3=6 ≠ 7 (fixed size must match exactly)
   ```

   **3. Combined Conversion (Flattening + Element Type, CALCULATED Size Match)**
   ```hexen
   val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]

   // Fixed-size target - exact size match required
   // val flat_wide : [6]i64 = matrix[..]        // ❌ Error: Missing explicit type conversion
   val flat_wide : [6]i64 = matrix[..]:[6]i64    // ✅ Both: exact size match (2×3=6) AND i32→i64

   // Inferred-size target - accepts calculated size
   // val flat_wide : [_]i64 = matrix[..]        // ❌ Error: Missing explicit type conversion
   val flat_wide : [_]i64 = matrix[..]:[_]i64    // ✅ Both: inferred size (accepts 2×3=6) AND i32→i64

   // ❌ Fixed-size mismatch remains invalid even with element type conversion
   // val wrong : [5]i64 = matrix[..]:[5]i64     // ❌ ERROR: 2×3=6 ≠ 5 (fixed size must match exactly)
   ```

   **Special Case: Same Type Copy (No Conversion)**
   ```hexen
   val source : [3]i32 = [1, 2, 3]
   val copy : [3]i32 = source[..]                 // ✅ Same type & size: only copy needed

   val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
   val matrix_copy : [2][3]i32 = matrix[..]       // ✅ Same type & dimensions: only copy needed
   ```

   **Invalid: Fixed-Size Mismatch (Structural Incompatibility)**
   ```hexen
   val source : [3]i32 = [1, 2, 3]
   // val wrong : [4]i32 = source[..]:[4]i32     // ❌ ERROR: Fixed-size mismatch (3 ≠ 4)
   // val wrong : [5]i64 = source[..]:[5]i64     // ❌ ERROR: Fixed-size mismatch (3 ≠ 5)

   // Note: Fixed-size arrays cannot be resized through conversion
   // But inferred-size [_]T always accepts any matching element type:
   val flexible : [_]i32 = source[..]:[_]i32     // ✅ Inferred size accepts 3 (same element type, no conversion)
   val wider : [_]i64 = source[..]:[_]i64        // ✅ Inferred size accepts 3 with element type conversion
   ```

   **Comptime Arrays (Always Ergonomic - No Explicit Conversion Needed)**
   ```hexen
   val comptime_arr = [1, 2, 3]                   // comptime_array_int
   val as_i32 : [3]i32 = comptime_arr             // ✅ First materialization (ergonomic!)
   val as_i64 : [3]i64 = comptime_arr             // ✅ Same source, different element type (flexible!)

   val comptime_2d = [[1, 2, 3], [4, 5, 6]]       // comptime 2D array
   val flat_i32 : [6]i32 = comptime_2d            // ✅ Flattening during materialization (2×3=6)
   val matrix_i64 : [2][3]i64 = comptime_2d       // ✅ Element type change during materialization
   val flat_i64 : [6]i64 = comptime_2d            // ✅ Both changes during materialization (2×3=6)
   ```

   - **Implementation Target Files**:
     - `src/hexen/semantic/declaration_analyzer.py` - Enhance array assignment validation for all type conversions
     - `src/hexen/semantic/function_analyzer.py` - Add type conversion validation for function arguments
     - `src/hexen/semantic/arrays/error_messages.py` - Add comprehensive type conversion error messages
     - `tests/semantic/arrays/test_array_type_conversions.py` - NEW comprehensive test file
     - `tests/semantic/arrays/test_array_flattening.py` - Update existing tests for new requirements

   - **Implementation Strategy**:
     1. **Validate size compatibility FIRST**:
        - **Inferred-size target `[_]T`**: Always accepts any size (wildcard match)
        - **Fixed-size target `[N]T`**: Calculate total element count for source and target
          - Reject if sizes don't match (arrays cannot be resized)
          - For flattening: verify calculated size matches target (2×3=6)
     2. **Detect type changes** (after size validation passes):
        - Element type differences (`i32` vs `i64`, `f32` vs `f64`)
        - Dimension count differences (1D vs 2D vs 3D)
        - Both combined
     3. **Validate explicit conversion**: Check for `:type` syntax on concrete array operations
        - **Exception for inferred-size**: `:[_]T` is considered explicit even though size is inferred
     4. **Allow comptime flexibility**: Skip validation for comptime arrays (first materialization)
     5. **Allow same-type copies**: Skip validation when source and target types match exactly

   - **Error Message Examples**:
     ```
     Error: Array size mismatch in type conversion
       Source: [3]i32 (3 elements)
       Target: [4]i32 (4 elements)
       Array sizes must match exactly (cannot resize arrays through conversion)
       Note: The :type syntax changes element types or flattens dimensions, not array sizes

     Error: Array size mismatch in flattening conversion
       Source: [2][3]i32 (6 elements total: 2×3)
       Target: [5]i32 (5 elements)
       Flattening requires calculated size match (2×3=6 ≠ 5)
       Suggestion: Use :[6]i32 for flattening this 2×3 matrix

     Error: Missing explicit type conversion for array operation
       Source type: [3]i32
       Target type: [3]i64
       Element type conversion (i32 → i64) requires explicit syntax
       Suggestion: source[..]:[3]i64

     Error: Missing explicit type conversion for array operation
       Source type: [2][3]i32
       Target type: [6]i32
       Dimension conversion (2D → 1D) with size match (2×3=6) requires explicit syntax
       Suggestion: matrix[..]:[6]i32

     Error: Missing explicit type conversion for array operation
       Source type: [2][3]i32
       Target type: [6]i64
       Multiple conversions required:
         - Element type: i32 → i64
         - Dimensions: [2][3] → [6] (flattening with size match 2×3=6)
       Both conversions require explicit syntax
       Suggestion: matrix[..]:[6]i64
     ```

   - **Test Coverage Required**:
     - **Fixed-size mismatch errors** (must reject):
       - `[3]i32→[4]i32` (different fixed sizes, same element type)
       - `[3]i32→[5]i64` (different fixed sizes, different element type)
       - `[2][3]i32→[5]i32` (flattening with size mismatch: 2×3=6 ≠ 5)
       - `[2][3]i32→[7]i32` (flattening with size mismatch: 2×3=6 ≠ 7)
     - **Inferred-size acceptance** (should succeed with `:type`):
       - `[3]i32→[_]i32` (inferred size accepts any size, same element type)
       - `[3]i32→[_]i64` (inferred size accepts any size, element type conversion)
       - `[2][3]i32→[_]i32` (flattening to inferred size: accepts 2×3=6)
       - `[2][3]i32→[_]i64` (flattening to inferred size with element type conversion)
       - `[2][3]i32→[_][_]i64` (inferred dimensions accept 2×3, element type conversion)
     - **Element type conversions** (require `:type`, same size):
       - `[3]i32→[3]i64`, `[3]i32→[3]f64`, `[3]f32→[3]f64` (fixed sizes)
       - `[2][3]i32→[2][3]i64` (multidimensional, same dimensions)
     - **Dimension conversions** (require `:type`, calculated size match):
       - `[2][3]T→[6]T` (2×3=6), `[2][2][2]T→[8]T` (2×2×2=8), `[3][4][5]T→[60]T` (3×4×5=60)
     - **Combined conversions** (require `:type`, size match + element type change):
       - `[2][3]i32→[6]i64`, `[2][2][2]i32→[8]f64`
     - **Same-type copies** (no `:type` needed):
       - `[3]i32→[3]i32`, `[2][3]i32→[2][3]i32` (should succeed)
     - **Comptime arrays** (always succeed, no `:type` needed):
       - All conversions during materialization (should succeed without `:type`)
     - **Context coverage**:
       - Function argument contexts
       - Assignment contexts

   - **Design Rationale**:
     - **Size is structural, not convertible**: Array size is part of type identity (like Rust, Zig)
       - **Fixed sizes** cannot be resized through conversion syntax
       - **Inferred size `[_]T`** acts as a wildcard accepting any size (flexibility!)
       - Fixed sizes must match exactly: same dimensions OR calculated flattening match
       - Prevents accidental data loss or truncation (when using fixed sizes)
     - **Uniform with TYPE_SYSTEM.md**: Array conversions follow identical rules to scalar conversions
       - Scalar: `i32 → i64` requires `:i64`
       - Array element type: `[3]i32 → [3]i64` requires `:[3]i64` (SAME size)
       - Array element type (inferred): `[3]i32 → [_]i64` requires `:[_]i64` (wildcard accepts 3)
       - Array dimensions: `[2][3]i32 → [6]i32` requires `:[6]i32` (calculated match 2×3=6)
       - Array flattening (inferred): `[2][3]i32 → [_]i32` requires `:[_]i32` (wildcard accepts 6)
     - **Inferred-size flexibility**: `[_]T` provides same adaptability as comptime for concrete arrays
     - **No special cases**: Arrays don't introduce exceptions to type system rules
     - **Comptime ergonomics preserved**: First materialization remains seamless
     - **Concrete costs visible**: All runtime type conversions require explicit syntax

#### **Week 2 Remaining Tasks** (4 tasks):
   - `declaration_analyzer.py` + `function_analyzer.py` - Explicit type conversion for all concrete array operations (Part 6)
   - `function_analyzer.py` - Pass-by-value parameter semantics (Part 7)
   - `function_analyzer.py` - `mut` parameter local copy behavior (Part 8)
   - `comptime/type_operations.py` - Comptime array parameter adaptation (Part 9)

### **Week 3: Block Evaluation**
   - `comptime/block_evaluation.py` - Array block classification
   - **Deliverable**: Compile-time vs runtime distinction working

### **Week 4: Integration + Testing**
   - Complete remaining files
   - Full test suite validation
   - Documentation alignment verification
   - **Deliverable**: Feature-complete array system

## Conclusion

This implementation plan provides a structured path from the current array system to the enhanced specification. By following these phases, we ensure:

- **Consistency**: All features align with Design A (pass-by-value)
- **Safety**: Explicit copy syntax prevents accidental performance costs
- **Flexibility**: Comptime arrays preserve maximum adaptability
- **Clarity**: Comprehensive error messages guide developers
- **Extensibility**: Foundation ready for future optimizations
- **Traceability**: Clear mapping from specs to source files

The result will be a robust, predictable array system that integrates seamlessly with Hexen's function system and unified block architecture.
