# Hexen Array System Implementation Plan 🦉

*Implementation Roadmap for Array Type System Integration*

> **Purpose**: This document provides a detailed implementation plan for updating the Hexen array system to align with the enhanced specifications in ARRAY_TYPE_SYSTEM.md, FUNCTION_SYSTEM.md, and UNIFIED_BLOCK_SYSTEM.md.

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

### Core Functionality
- [ ] Pass-by-value parameter semantics
- [ ] `mut` parameter local copy behavior
- [ ] Fixed-size array parameter matching
- [ ] Inferred-size `[_]T` parameter support
- [ ] Array `.length` property (compile-time constant)
- [ ] Comptime array parameter adaptation
- [ ] Explicit `[..]` copy syntax enforcement
- [ ] Array return value handling (prepare for RVO)

### Expression Block Integration
- [ ] Compile-time array block detection
- [ ] Runtime array block context requirement
- [ ] Array validation with early returns
- [ ] Array caching patterns
- [ ] Bounds checking with fallbacks

### Error Messages
- [ ] Array size mismatch errors
- [ ] Missing explicit copy errors
- [ ] Mutable array parameter errors
- [ ] Runtime block context errors
- [ ] All error messages with actionable suggestions

### Testing
- [ ] Unit tests for all parameter types
- [ ] Comptime array adaptation tests
- [ ] Mutable parameter tests
- [ ] Expression block array tests
- [ ] Integration tests for complete scenarios
- [ ] Error message tests

### Documentation
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

### **Week 0 (Prerequisite): Parser Extensions**
   - **Days 1-2**: Grammar + AST changes (`hexen.lark`, `ast_nodes.py`)
   - **Days 3-4**: Parser transformers (`parser.py`)
   - **Day 5**: Parser unit tests
   - **Deliverable**: `[..]` and `.length` syntax working in parser

### **Week 1: Function Analyzer + Error Messages**
   - `function_analyzer.py` - Pass-by-value semantics
   - `arrays/error_messages.py` - Array-specific errors
   - **Deliverable**: Basic parameter passing + error messages

### **Week 2: Array Types + Property Access**
   - `arrays/array_types.py` - `.length` property support
   - Expression analyzer - Property access handling
   - **Deliverable**: Inferred-size parameters working

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
