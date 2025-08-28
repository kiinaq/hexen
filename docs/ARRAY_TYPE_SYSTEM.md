# Hexen Array Type System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's array type system, integrating seamlessly with the existing comptime type system while following proven patterns from languages like Zig. Arrays maintain Hexen's core principle of "Ergonomic Literals + Transparent Runtime Costs".

## Overview

Hexen's array type system extends the language's comptime philosophy to collections, making array literals seamless to work with while keeping all runtime computational costs visible. Arrays follow the same ergonomic principles as individual values - comptime arrays adapt seamlessly while concrete array operations require explicit conversions.

## Core Philosophy

### Design Principle: Array Integration with Comptime Types

Hexen's arrays follow the same **"Ergonomic Literals + Transparent Runtime Costs"** philosophy:

- **Ergonomic Array Literals**: Comptime array types adapt seamlessly (zero runtime cost)
- **Transparent Runtime Costs**: All concrete array conversions require explicit syntax (`value:type`)
- **Consistent with Individual Values**: Arrays follow identical patterns to single-value type system
- **Natural Usage**: Common array literal patterns work without ceremony (`[1, 2, 3]`, `[3.14, 2.71]`)
- **Size-as-Type**: Array size is part of the type itself, enabling compile-time safety
- **Proven Approach**: Following Zig's successful array design patterns

This philosophy ensures that **everyday array usage feels natural**, while **runtime performance costs** are always explicit and visible.

## Array Syntax

### Array Literal Syntax
Array literals use square brackets with comma-separated elements:

```hexen
[1, 2, 3]              // Array literal with integer elements
[3.14, 2.71, 1.41]     // Array literal with float elements
[true, false, true]    // Array literal with boolean elements
["hello", "world"]     // Array literal with string elements
```

### Array Type Declarations

#### Fixed-Size Arrays
Following Zig's proven `[N]T` pattern for explicit size:

```hexen
val numbers : [3]i32 = [1, 2, 3]           // Fixed-size array: 3 elements of i32
val floats : [4]f64 = [3.14, 2.71, 1.41, 0.57]  // Fixed-size array: 4 elements of f64
val flags : [2]bool = [true, false]        // Fixed-size array: 2 elements of bool
```

#### Inferred-Size Arrays
Following Zig's proven `[_]T` pattern for inferred size:

```hexen
val numbers : [_]i32 = [1, 2, 3]           // Size inferred: [3]i32
val floats : [_]f64 = [3.14, 2.71]         // Size inferred: [2]f64
val mixed : [_]f64 = [42, 3.14, 100]       // All elements coerce to f64
```

**Rationale for `_` syntax:**
- **Proven Pattern**: Zig uses `_` successfully for inferred array sizes
- **Consistent Meaning**: `_` already represents "infer this" in many contexts
- **General Unused Placeholder**: Following established patterns for ignored/inferred values
- **Visual Clarity**: Clear distinction from fixed-size syntax

## Array Type Hierarchy

### Concrete Array Types
Array types with specific element types and known sizes:

| Array Type | Description | Example |
|------------|-------------|---------|
| `[N]i32` | N-element array of 32-bit signed integers | `[3]i32` |
| `[N]i64` | N-element array of 64-bit signed integers | `[5]i64` |
| `[N]f32` | N-element array of 32-bit floats | `[2]f32` |
| `[N]f64` | N-element array of 64-bit floats | `[4]f64` |
| `[N]string` | N-element array of strings | `[3]string` |
| `[N]bool` | N-element array of booleans | `[2]bool` |

### Comptime Array Types (Compile-Time Only)
Special array types that literals have initially, which adapt to context:

| Type | Description | Purpose |
|------|-------------|---------|
| `comptime_array_int` | Array of integer literals | Context-dependent coercion to any numeric array type |
| `comptime_array_float` | Array of float literals or mixed numerics | Context-dependent coercion to float array types |

### Comptime Array Type Rules

#### Homogeneous Arrays (Single Comptime Type)
Arrays with all elements of the same comptime type preserve maximum flexibility:

```hexen
// All integer literals → comptime_array_int
val int_array = [42, 100, -25]          // comptime_array_int (flexible!)
val as_i32 : [_]i32 = int_array         // → [3]i32 (implicit)
val as_i64 : [_]i64 = int_array         // Same source → [3]i64 (flexible!)
val as_f64 : [_]f64 = int_array         // Same source → [3]f64 (flexible!)

// All float literals → comptime_array_float
val float_array = [3.14, 2.71, 1.41]    // comptime_array_float (flexible!)
val as_f32 : [_]f32 = float_array       // → [3]f32 (implicit)
val as_f64 : [_]f64 = float_array       // Same source → [3]f64 (flexible!)
```

#### Mixed Arrays (Multiple Comptime Types)
Arrays with mixed comptime numeric types use **minimum type coercion** and become `comptime_array_float`:

```hexen
// Mixed int + float literals → comptime_array_float (minimum type that holds all)
val mixed = [42, 3.14, 100]             // comptime_array_float
val as_f32 : [_]f32 = mixed             // → [3]f32 (all elements fit in f32)
val as_f64 : [_]f64 = mixed             // → [3]f64 (all elements fit in f64)
// val as_i32 : [_]i32 = mixed          // ❌ Error: 3.14 doesn't fit in i32 without truncation

// Explicit conversion for truncation
val as_i32 : [_]i32 = mixed:[_]i32      // Explicit conversion (truncation visible)
```

#### Size-as-Part-of-Type
Array size is always part of the type, whether comptime or concrete:

```hexen
val short = [1, 2]           // comptime_array_int with size 2
val long = [1, 2, 3, 4]      // comptime_array_int with size 4

// Different sizes = different types
val short_i32 : [_]i32 = short    // → [2]i32
val long_i32 : [_]i32 = long      // → [4]i32

// Arrays of different sizes cannot be assigned (mut required for reassignment)
mut short_mut : [_]i32 = short    // → [2]i32
// short_mut = long_i32           // ❌ Error: [2]i32 ≠ [4]i32
```

## Array Element Access

### Element Access Syntax
Array elements are accessed using square bracket notation with zero-based indexing:

```hexen
val numbers : [_]i32 = [10, 20, 30]
val first_element : i32 = numbers[0]    // Access first element: 10
val second_element : i32 = numbers[1]   // Access second element: 20
val last_element : i32 = numbers[2]     // Access third element: 30
```

### Comptime vs Concrete Element Access

#### Comptime Array Elements
Elements from comptime arrays inherit the comptime type:

```hexen
val flexible_array = [42, 100, 200]     // comptime_array_int
val flexible_element = flexible_array[0] // comptime_int (preserved flexibility!)

// Same element adapts to different contexts
val as_i32 : i32 = flexible_element     // comptime_int → i32
val as_i64 : i64 = flexible_element     // Same source → i64
val as_f64 : f64 = flexible_element     // Same source → f64
```

#### Concrete Array Elements
Elements from concrete arrays require explicit type annotations per TYPE_SYSTEM.md rules:

```hexen
val concrete : [_]i32 = [42, 100, 200]  // Concrete [3]i32 array
val concrete_elem : i32 = concrete[0]   // Explicit type required: i32
val widened_elem : i64 = concrete[0]:i64 // Explicit conversion: i32 → i64
```

## Array Type Conversion Rules

### The Four Patterns Applied to Arrays

Arrays follow the same four-pattern system as individual values:

#### 1. ✨ Comptime + Comptime = Comptime (Flexible)
```hexen
val array1 = [1, 2, 3]          // comptime_array_int
val array2 = [4, 5, 6]          // comptime_array_int
val combined = array1 + array2   // comptime_array_int (concatenation - flexible!)

val as_i32 : [_]i32 = combined  // → [6]i32
val as_i64 : [_]i64 = combined  // Same source → [6]i64
val as_f64 : [_]f64 = combined  // Same source → [6]f64
```

#### 2. 🔄 Comptime + Concrete = Concrete (Adapts)
```hexen
val concrete : [_]i32 = [10, 20, 30]    // Concrete [3]i32
val comptime_array = [1, 2, 3]          // comptime_array_int
val mixed_result = concrete + comptime_array  // Comptime adapts to i32 → [6]i32
```

#### 3. 🔧 Concrete + Concrete = Explicit (Visible Costs)
```hexen
val array_i32 : [_]i32 = [1, 2, 3]      // [3]i32
val array_i64 : [_]i64 = [4, 5, 6]      // [3]i64

// val mixed = array_i32 + array_i64    // ❌ Error: requires explicit conversion
val explicit = array_i32:[_]i64 + array_i64  // ✅ Explicit: [3]i32 → [3]i64
```

#### 4. ⚡ Same Concrete = Same Concrete (Identity)
```hexen
val array1 : [_]i32 = [1, 2, 3]         // [3]i32
val array2 : [_]i32 = [4, 5, 6]         // [3]i32
val result = array1 + array2             // [3]i32 + [3]i32 → [6]i32 (identity)
```

### Element-Level Conversions
For mixed-type array construction, conversions happen at the element level:

```hexen
val int_array : [_]i32 = [10, 20, 30]   // [3]i32
val float_array : [_]f64 = [1.1, 2.2]   // [2]f64

// Element-level conversion (efficient)
val mixed_array : [_]f64 = [int_array[0]:f64, float_array[0]]  // [2]f64

// Array-level conversion (less efficient alternative)
val converted_array : [_]f64 = int_array:[_]f64               // [3]f64
```

## Variable Declaration with Arrays

### `val` - Immutable Arrays
Following the same principles as individual values:

```hexen
val fixed_numbers : [3]i32 = [1, 2, 3]        // ✅ Fixed-size array
val inferred_numbers : [_]i32 = [1, 2, 3]     // ✅ Inferred-size array
val flexible_numbers = [1, 2, 3]              // ✅ Comptime array (flexible!)

// Same flexible array in different contexts
val as_i32_array : [_]i32 = flexible_numbers  // → [3]i32
val as_i64_array : [_]i64 = flexible_numbers  // Same source → [3]i64
val as_f64_array : [_]f64 = flexible_numbers  // Same source → [3]f64
```

### `mut` - Mutable Arrays
Mutable arrays require explicit type annotations, same as individual values:

```hexen
mut dynamic : [_]i32 = [1, 2, 3]             // ✅ Explicit type required
dynamic[0] = 42                               // ✅ Element reassignment
dynamic[1] = large_value:i32                  // ✅ Explicit conversion

// mut flexible = [1, 2, 3]                  // ❌ Error: mut requires explicit type
```

### Array Element Reassignment
Element reassignment follows standard assignment rules:

```hexen
mut numbers : [_]i32 = [10, 20, 30]
numbers[0] = 42              // comptime_int → i32 (adapts)
numbers[1] = other_val:i32   // Explicit conversion if needed

mut floats : [_]f32 = [1.1, 2.2, 3.3]
floats[0] = 3.14             // comptime_float → f32 (adapts)
floats[1] = double_val:f32   // f64 → f32 (explicit conversion)
```

## Array Operations

### Basic Array Operations

```hexen
// Array creation
val numbers = [1, 2, 3, 4, 5]           // comptime_array_int
val fixed : [5]i32 = numbers            // → [5]i32
val inferred : [_]i32 = numbers         // → [5]i32

// Element access
val first : i32 = fixed[0]              // Access first element
val last : i32 = fixed[4]               // Access last element

// Size information (compile-time constant)
val size = fixed.length                 // Compile-time constant: 5
```

### Array Bounds Checking Philosophy

Following Hexen's safety-first approach:

```hexen
val numbers : [_]i32 = [10, 20, 30]
val valid : i32 = numbers[0]            // ✅ Index 0: valid
val also_valid : i32 = numbers[2]       // ✅ Index 2: valid
// val invalid : i32 = numbers[3]       // ❌ Compile-time error: index 3 out of bounds for [3]i32

// Runtime bounds checking for dynamic indices
val dynamic_index : i32 = get_user_input()
val element : i32 = numbers[dynamic_index]  // Runtime bounds check inserted
```

**Bounds Checking Strategy:**
- **Compile-time bounds checking**: For constant indices
- **Runtime bounds checking**: For dynamic indices (inserted automatically)
- **Safety by default**: Following Hexen's safety-first philosophy

## Integration with Expression Blocks

Arrays work seamlessly with Hexen's unified block system:

### Compile-Time Evaluable Array Blocks
Blocks containing only comptime array operations preserve flexibility:

```hexen
val flexible_array_computation = {
    val base = [1, 2, 3]                 // comptime_array_int
    val multiplier = [2, 2, 2]           // comptime_array_int
    val result = base * multiplier        // Element-wise multiplication → comptime_array_int
    assign result                        // Preserves comptime_array_int (flexible!)
}

// Same computation, different target types
val as_i32 : [_]i32 = flexible_array_computation    // → [3]i32
val as_i64 : [_]i64 = flexible_array_computation    // Same source → [3]i64
val as_f64 : [_]f64 = flexible_array_computation    // Same source → [3]f64
```

### Runtime Evaluable Array Blocks
Blocks with function calls or concrete arrays require explicit context:

```hexen
val runtime_array_result : [_]i32 = {               // Explicit context required
    val input_data : [_]i32 = load_array_data()    // Function call → runtime (explicit type required)
    val processed = input_data * [2, 2, 2]          // Mixed: concrete + comptime
    assign processed                                // Result type determined by context
}
```

## Advanced Patterns

### Mixed-Type Array Construction
Constructing arrays from different source types:

```hexen
// All comptime types
val mixed_comptime = [42, 3.14, 100]        // comptime_array_float (mixed → float)
val as_f64 : [_]f64 = mixed_comptime        // All elements fit → [3]f64

// Mixed concrete and comptime types
val int_val : i32 = 10
val mixed_concrete : [_]f64 = [int_val:f64, 3.14, 100]  // [3]f64
```

### Array Type Constraints
Size compatibility and type matching:

```hexen
val short : [_]i32 = [1, 2]             // [2]i32
val long : [_]i32 = [1, 2, 3, 4]        // [4]i32

// Size mismatch errors
// short = long                          // ❌ Error: [2]i32 ≠ [4]i32

// Element type compatibility
val int_array : [_]i32 = [1, 2, 3]      // [3]i32
val float_array : [_]f64 = [1.1, 2.2, 3.3]  // [3]f64

// Type conversion required
val converted : [_]f64 = int_array:[_]f64    // [3]i32 → [3]f64 (explicit)
```

### Nested Array Patterns
Arrays of arrays following the same principles:

```hexen
// Arrays of arrays with comptime flexibility
val matrix = [[1, 2], [3, 4], [5, 6]]   // comptime_array of comptime_array_int
val as_i32_matrix : [_][_]i32 = matrix   // → [3][2]i32
val as_f64_matrix : [_][_]f64 = matrix   // Same source → [3][2]f64
```

## Error Messages

Array-specific error messages follow Hexen's consistent pattern:

### Size Mismatch Errors
```
Error: Cannot assign [4]i32 to variable of type [3]i32
Array sizes must match exactly: expected 3 elements, got 4 elements
```

### Type Conversion Errors
```
Error: Cannot assign comptime_array_float to [_]i32 without explicit conversion
Float elements require truncation to integer types
Suggestion: Use explicit conversion: array:[_]i32
```

### Index Out of Bounds Errors
```
Error: Array index 5 out of bounds for array of size 3
Valid indices for [3]i32 are 0, 1, 2
```

### Mixed Type Construction Errors
```
Error: Mixed array elements [i32, f64] require explicit target type
Cannot infer common type for concrete element types
Suggestion: Specify target type: val array : [_]f64 = [elem1:f64, elem2]
```

## Examples

### Comprehensive Array Usage

```hexen
func demonstrate_array_system() : void = {
    // ===== Comptime Array Magic (Ergonomic Literals) =====
    val flexible_ints = [1, 2, 3, 4, 5]         // comptime_array_int (flexible!)
    val flexible_floats = [3.14, 2.71, 1.41]    // comptime_array_float (flexible!)
    val flexible_mixed = [42, 3.14, 100]        // comptime_array_float (mixed → float)
    
    // Same flexible arrays adapt to different contexts
    val ints_as_i32 : [_]i32 = flexible_ints    // → [5]i32
    val ints_as_i64 : [_]i64 = flexible_ints    // Same source → [5]i64  
    val ints_as_f64 : [_]f64 = flexible_ints    // Same source → [5]f64
    
    val floats_as_f32 : [_]f32 = flexible_floats   // → [3]f32
    val floats_as_f64 : [_]f64 = flexible_floats   // Same source → [3]f64
    
    val mixed_as_f64 : [_]f64 = flexible_mixed     // → [3]f64 (all fit)
    val mixed_as_i32 : [_]i32 = flexible_mixed:[_]i32  // Explicit conversion (truncation)
    
    // ===== Element Access Patterns =====
    // Comptime array elements stay flexible
    val flexible_element = flexible_ints[0]      // comptime_int (flexible!)
    val elem_as_i32 : i32 = flexible_element     // comptime_int → i32
    val elem_as_i64 : i64 = flexible_element     // Same source → i64
    
    // Concrete array elements need explicit types
    val concrete : [_]i32 = [10, 20, 30]        // [3]i32
    val concrete_elem : i32 = concrete[0]       // Explicit type required
    val widened_elem : i64 = concrete[0]:i64    // Explicit conversion
    
    // ===== Array Operations =====
    val numbers1 : [_]i32 = [1, 2, 3]           // [3]i32
    val numbers2 : [_]i32 = [4, 5, 6]           // [3]i32
    val combined = numbers1 + numbers2           // [3]i32 + [3]i32 → [6]i32
    
    val floats1 : [_]f32 = [1.1, 2.2]           // [2]f32
    val floats2 : [_]f64 = [3.3, 4.4]           // [2]f64
    val converted = floats1:[_]f64 + floats2     // Explicit conversion then combine
    
    // ===== Mutable Arrays =====
    mut dynamic : [_]i32 = [10, 20, 30]         // Explicit type required
    dynamic[0] = 42                              // comptime_int → i32 (adapts)
    dynamic[1] = big_value:i32                   // Explicit conversion
    dynamic[2] = flexible_element                // comptime_int → i32 (adapts)
    
    mut float_array : [_]f32 = [1.1, 2.2, 3.3] // Explicit type required
    float_array[0] = 3.14                       // comptime_float → f32 (adapts)
    float_array[1] = double_precision:f32       // f64 → f32 (explicit)
    
    // ===== Expression Blocks with Arrays =====
    // Compile-time evaluable (preserves flexibility)
    val flexible_computation = {
        val base = [1, 2, 3, 4]                 // comptime_array_int
        val scaled = base * [2, 2, 2, 2]        // comptime array ops
        assign scaled                           // Preserves comptime_array_int
    }
    val comp_as_i32 : [_]i32 = flexible_computation  // → [4]i32
    val comp_as_f64 : [_]f64 = flexible_computation  // Same source → [4]f64
    
    // Runtime evaluable (requires explicit context)
    val runtime_result : [_]f64 = {             // Context required
        val data = load_data_array()            // Function call → runtime
        val processed = data * [1.5, 1.5, 1.5] // Mixed concrete + comptime
        assign processed
    }
    
    // ===== Size and Type Safety =====
    val short_array : [_]i32 = [1, 2]           // [2]i32
    val long_array : [_]i32 = [1, 2, 3, 4]      // [4]i32
    
    // Size compatibility checked at compile time
    // short_array = long_array                  // ❌ Error: [2]i32 ≠ [4]i32
    
    // Element type safety
    val int_arr : [_]i32 = [10, 20, 30]         // [3]i32
    val float_arr : [_]f64 = [1.1, 2.2, 3.3]    // [3]f64
    val converted_arr : [_]f64 = int_arr:[_]f64  // Explicit array conversion
    
    // ===== Nested Arrays =====
    val matrix = [[1, 2], [3, 4]]               // comptime 2D array
    val as_i32_matrix : [_][_]i32 = matrix      // → [2][2]i32
    val as_f64_matrix : [_][_]f64 = matrix      // Same source → [2][2]f64
    
    val matrix_elem : i32 = as_i32_matrix[0][1] // Access nested element: 2
    val flexible_nested = matrix[1][0]          // comptime_int (flexible!)
}
```

## Benefits

### Developer Experience

1. **Ergonomic Array Literals**: Comptime arrays adapt seamlessly to context
2. **Consistent with Values**: Same patterns as individual value type system  
3. **Predictable Rules**: Arrays follow the same four-pattern system
4. **Size Safety**: Array bounds checking prevents runtime errors
5. **Clear Intent**: All array conversions are explicit and visible

### Performance Clarity

1. **Cost Transparency**: Every array conversion is visible in the code
2. **Compile-Time Optimization**: Comptime arrays evaluated at compile time
3. **No Hidden Allocations**: All array operations are explicit
4. **Bounds Check Optimization**: Compile-time bounds checking where possible
5. **Memory Layout Predictable**: Fixed-size arrays have predictable layout

### Type Safety

1. **Compile-Time Size Checking**: Array size mismatches caught at compile time
2. **Element Type Safety**: All element conversions follow standard type rules
3. **Bounds Safety**: Index out of bounds errors caught early
4. **No Silent Coercion**: All array type changes require explicit syntax
5. **Integration Safety**: Arrays integrate seamlessly with expression blocks

### Maintainability

1. **Consistent Mental Model**: Same patterns as individual value system
2. **Readable Code**: All array operations visible in source code
3. **Size Documentation**: Array types document their size constraints
4. **Clear Conversions**: All type changes are explicit and searchable
5. **Proven Approach**: Following successful patterns from Zig

## Integration with Existing Systems

### Compatibility with TYPE_SYSTEM.md
- **Four-Pattern System**: Arrays follow identical conversion patterns
- **Comptime Flexibility**: Same comptime type preservation rules
- **Explicit Conversions**: Same `value:type` conversion syntax
- **val/mut Semantics**: Same mutability rules apply to arrays

### Compatibility with BINARY_OPS.md  
- **Element-wise Operations**: Array operations follow binary operation rules
- **Mixed-Type Operations**: Same explicit conversion requirements
- **Transparent Costs**: All array arithmetic costs visible

### Compatibility with UNIFIED_BLOCK_SYSTEM.md
- **Expression Block Integration**: Arrays work seamlessly in expression blocks
- **Compile-time vs Runtime**: Same classification rules for array operations
- **Block Type Preservation**: Comptime arrays preserve flexibility through blocks

This array type system extends Hexen's proven comptime philosophy to collections, maintaining consistency with existing language patterns while providing the ergonomics and safety that developers expect from a modern systems programming language.