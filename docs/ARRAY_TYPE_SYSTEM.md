# Hexen Array Type System 🧮

*Design and Implementation Specification*

## Overview

Hexen's array type system extends the core type system with fixed-length arrays, following the principle of **"Explicit Danger, Implicit Safety"**. Arrays in Hexen are first-class types that combine element type and size information, providing both safety and flexibility.

## Core Philosophy

### Design Principle: Size-Aware Type Safety

Hexen's array system follows a unified pattern where **array types include both element type and size information**:

- **Fixed Size + Explicit Type = Safe** (`[N]T` with literal size)
- **Inferred Size + Literal = Safe** (`[]T` with array literal)
- **Runtime Size + Explicit Type = Dangerous** (`[size]T` with runtime value)
- **Ambiguous Size = Error** (require explicit type annotation)

This pattern ensures array operations are both safe and ergonomic.

## Type Hierarchy

### Array Types

| Type | Description | Usage |
|------|-------------|-------|
| `[N]T` | Fixed-length array of type T | Explicit size arrays |
| `[]T` | Inferred-length array of type T | Array literals |
| `comptime_array` | Array literal type | Compile-time only |

### Type Components

1. **Element Type (T)**
   - Any concrete type (`i32`, `i64`, `f32`, `f64`, `string`, `bool`)
   - Comptime types (`comptime_int`, `comptime_float`) through coercion
   - Future: User-defined types, generics

2. **Size (N)**
   - Literal integers
   - Runtime values (requires explicit type annotation)

## Array Declaration Patterns

### 1. Fixed-Length Arrays

```hexen
// Explicit size and type
val numbers : [5]i32 = [1, 2, 3, 4, 5]    // Must match size exactly
val floats : [3]f64 = [3.14, 2.718, 1.414] // Size is part of type

// Runtime size (explicit danger)
val size = 10
val arr : [size]i32 = undef               // Requires explicit type and size
```

### 2. Inferred-Length Arrays

```hexen
// Type and size inferred from literal
val numbers = [1, 2, 3]                   // Inferred as [3]i32
val floats = [3.14, 2.718]                // Inferred as [2]f64

// Explicit type, inferred size
val explicit : []i64 = [1000, 2000, 3000] // Type explicit, size inferred

// Comptime type coercion
val mixed : []f64 = [42, 3.14]            // comptime_int -> f64 coercion
```

### 3. Uninitialized Arrays

```hexen
// Fixed size with undef
val pending : [5]i32 = undef              // OK: Size and type explicit
val config : [3]string = undef            // OK: Size and type explicit

// Inferred size with undef (error)
val bad : []i32 = undef                   // Error: Cannot infer size from undef
```

## Type Coercion Rules

### 1. Array Literal Coercion

Array literals follow the same coercion rules as their element types:

```hexen
// Comptime integer coercion
val as_i32 : [3]i32 = [42, 43, 44]       // comptime_int -> i32
val as_i64 : [2]i64 = [1000, 2000]       // comptime_int -> i64
val as_f32 : [2]f32 = [42, 43]           // comptime_int -> f32

// Comptime float coercion
val as_f32 : [2]f32 = [3.14, 2.718]      // comptime_float -> f32
val as_f64 : [2]f64 = [3.14, 2.718]      // comptime_float -> f64

// Mixed types with coercion
val mixed : [2]f64 = [42, 3.14]          // comptime_int + comptime_float -> f64
```

### 2. Size Coercion Rules

- **Fixed to Fixed**: Must match exactly
- **Inferred to Fixed**: Must match exactly
- **Fixed to Inferred**: Not allowed (size information loss)
- **Runtime to Fixed**: Must be explicit

```hexen
// ❌ Size mismatch errors
val arr : [5]i32 = [1, 2, 3]             // Error: Expected 5 elements
val arr : [3]i32 = [1, 2, 3, 4]          // Error: Too many elements

// ❌ Runtime size errors
val size = 10
val arr = [0; size]                      // Error: Size must be literal

// ✅ Valid coercions
val arr : [3]i32 = [1, 2, 3]             // OK: Exact match
val arr = [1, 2, 3]                      // OK: Inferred as [3]i32
```

## Error Messages

### Consistency with Type System

Error messages follow the same pattern as the core type system:

#### Size Mismatch Errors
```
Array size mismatch: expected 5 elements but got 3
```

#### Type Mismatch Errors
```
Array element type mismatch: expected i32 but got string
```

#### Runtime Size Errors
```
Array size must be a literal integer
```

#### Undef Errors
```
Cannot infer array size from undef, explicit size required
```

## Implementation Guidelines

### Type System Extensions

```python
class HexenType(Enum):
    # ... existing types ...
    ARRAY = "array"           # Base array type
    COMPTIME_ARRAY = "comptime_array"  # For array literals

class ArrayType:
    def __init__(self, element_type: HexenType, size: Optional[int]):
        self.element_type = element_type
        self.size = size  # None for inferred size
```

### Semantic Analysis

The semantic analyzer should:

1. **Type Resolution**:
   - Resolve array element types with comptime coercion
   - Validate array sizes against literals
   - Handle runtime sizes with explicit type requirements

2. **Size Validation**:
   - Ensure sizes are literal integers
   - Validate literal sizes against type annotations
   - Prevent size information loss

3. **Coercion Rules**:
   - Apply element type coercion rules
   - Enforce size matching rules
   - Handle mixed-type array literals

## Examples

### Core Array Concepts

```hexen
func demonstrate_array_system() : void = {
    // ===== Fixed-Length Arrays =====
    val fixed : [5]i32 = [1, 2, 3, 4, 5]    // Explicit size
    val inferred = [1, 2, 3]                 // Inferred as [3]i32
    val explicit : []i64 = [1000, 2000, 3000] // Type explicit, size inferred
    
    // ===== Runtime Size =====
    val size = 10
    val buffer : [size]i32 = undef           // Runtime size requires explicit type
    
    // ===== Type Coercion =====
    val as_f32 : [2]f32 = [42, 3.14]         // comptime_int + comptime_float -> f32
    val as_f64 : [2]f64 = [42, 3.14]         // comptime_int + comptime_float -> f64
    
    // ===== Uninitialized Arrays =====
    val pending : [5]i32 = undef             // OK: Size and type explicit
}

// For array operations and indexing, see ARRAY_OPERATIONS.md
```

## Benefits

### Developer Experience

1. **Ergonomic**: Common array operations work seamlessly
2. **Predictable**: Size is part of the type system
3. **Safe**: Dangerous operations require explicit typing
4. **Consistent**: Follows core type system patterns

### Type Safety

1. **Compile-time validation**: All array operations checked at compile time
2. **Size safety**: Array sizes are part of the type system
3. **Element type safety**: Coercion rules apply to array elements
4. **Runtime safety**: Runtime sizes require explicit acknowledgment

### Future-Proof Design

1. **Extensible**: Pattern works with user-defined types and generics
2. **Composable**: Arrays can contain other arrays
3. **Maintainable**: Clear rules that are easy to understand
4. **Consistent**: Same philosophy extends to all array operations 