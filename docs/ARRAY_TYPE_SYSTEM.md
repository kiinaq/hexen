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
- **Safe Memory Layout Access**: Row-major layout enables zero-cost dimensional flattening
- **Proven Approach**: Following some Zig's successful array design patterns

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
Following `[N]T` pattern for explicit size:

```hexen
val numbers : [3]i32 = [1, 2, 3]           // Fixed-size array: 3 elements of i32
val floats : [4]f64 = [3.14, 2.71, 1.41, 0.57]  // Fixed-size array: 4 elements of f64
val flags : [2]bool = [true, false]        // Fixed-size array: 2 elements of bool
```

#### Inferred-Size Arrays
Following `[_]T` pattern for inferred size:

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

> **🔑 Key Insight - Compile-time vs Runtime Materialization**: Comptime arrays exist only in **compiler memory** during compilation. Each assignment to a concrete type **materializes** the required data in **runtime memory** with the specific concrete type. The same comptime source can be materialized multiple times with different concrete types.

#### Comptime Array Elements
Elements from comptime arrays inherit the comptime type:

```hexen
val flexible_array = [42, 100, 200]     // comptime_array_int
val flexible_element = flexible_array[0] // comptime_int (preserved flexibility!)

// Same element adapts to different contexts
val as_i32 : i32 = flexible_element     // comptime_int → i32
val as_i64 : i64 = flexible_element     // Same source → i64
val as_f64 : f64 = flexible_element     // Same source → f64

// Different elements from same array can resolve to different types
val elem1_as_i32 : i32 = flexible_array[0]   // First element → i32
val elem2_as_f64 : f64 = flexible_array[1]   // Second element → f64 (same source!)
val elem3_as_i64 : i64 = flexible_array[2]   // Third element → i64 (same source!)
```

**Runtime Materialization Process:**
```hexen
val comptime_array = [42, 100, 200]    // Exists ONLY in compiler memory

// Each assignment materializes data in runtime memory:
val materialized_i32 : [_]i32 = comptime_array    // → Runtime: [42, 100, 200] as i32 values
val materialized_f64 : [_]f64 = comptime_array    // → Runtime: [42.0, 100.0, 200.0] as f64 values  
val materialized_i64 : [_]i64 = comptime_array    // → Runtime: [42, 100, 200] as i64 values

// Three separate runtime arrays in memory, each with different concrete types!
// comptime_array itself never exists at runtime - only materialized versions do
```

**Complex Comptime Operations - Zero Runtime Cost:**
```hexen
// Complex computation at compile time
val complex_comptime = {
    val base = [1, 2, 3, 4, 5]
    val transformed = base * [10, 20, 30, 40, 50]          // Element-wise multiplication
    val filtered = transformed.filter(|x| x > 25)          // Filtering operation - 'filter' not yet specified
    val final = filtered.map(|x| x * x + 100)              // Complex transformation - 'map' not yet specified
    assign final                                            // Result: comptime_array_int
}

// All the above operations happen at COMPILE TIME - zero runtime cost!
// Runtime only sees the pre-computed results:

val as_i32 : [_]i32 = complex_comptime    // → Runtime: [1130, 1600, 2500] (pre-computed!)
val as_f64 : [_]f64 = complex_comptime    // → Runtime: [1130.0, 1600.0, 2500.0] (same pre-computed values!)

// No multiplication, filtering, mapping, or arithmetic happens at runtime
// Just direct loading of pre-computed constant values
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

// Size mismatch errors (mut required for reassignment)
mut short_mut : [_]i32 = short          // [2]i32
// short_mut = long                      // ❌ Error: [2]i32 ≠ [4]i32

// Element type compatibility
val int_array : [_]i32 = [1, 2, 3]      // [3]i32
val float_array : [_]f64 = [1.1, 2.2, 3.3]  // [3]f64

// Type conversion required
val converted : [_]f64 = int_array:[_]f64    // [3]i32 → [3]f64 (explicit)
```

### Multidimensional Arrays
Hexen supports multidimensional arrays following `[N][M]T` syntax pattern with full comptime type integration:

```hexen
// 2D Arrays with comptime flexibility
val matrix = [[1, 2, 3], [4, 5, 6]]     // comptime_array of comptime_array_int
val as_i32_matrix : [_][_]i32 = matrix   // → [2][3]i32
val as_f64_matrix : [_][_]f64 = matrix   // Same source → [2][3]f64

// Mixed dimensions with explicit sizing
val fixed_matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]    // Fixed dimensions
val mixed_size : [_][3]i32 = [[7, 8, 9], [10, 11, 12]]   // Inferred rows, fixed columns
val fully_inferred : [_][_]i32 = [[13, 14], [15, 16]]    // Both dimensions inferred
```

## Multidimensional Arrays Deep Dive

### Syntax and Type System

Hexen's multidimensional arrays follow `[N][M]T` syntax while fully integrating with the comptime type system:

#### Dimension Specification Patterns
```hexen
// Fixed dimensions (compile-time known sizes)
val matrix_fixed : [3][4]i32 = [
    [1, 2, 3, 4],
    [5, 6, 7, 8], 
    [9, 10, 11, 12]
]

// Fully inferred dimensions
val matrix_inferred : [_][_]i32 = [
    [1, 2, 3],
    [4, 5, 6]
]  // Infers [2][3]i32

// Mixed specification (outer fixed, inner inferred)
val matrix_mixed1 : [2][_]i32 = [
    [1, 2, 3, 4],    // Inner dimension inferred from first row: [4]i32
    [5, 6, 7, 8]     // Must match: [4]i32
]

// Mixed specification (outer inferred, inner fixed)
val matrix_mixed2 : [_][3]i32 = [
    [1, 2, 3],       // Must be exactly 3 elements
    [4, 5, 6],       // Must be exactly 3 elements
    [7, 8, 9]        // Must be exactly 3 elements
]  // Infers [3][3]i32
```

#### Comptime Type Integration
Multidimensional arrays fully integrate with Hexen's comptime type system:

```hexen
// Comptime multidimensional arrays preserve flexibility
val flexible_2d = [[42, 100], [200, 300]]   // comptime_array of comptime_array_int

// Same source adapts to different target types
val as_i32_2d : [_][_]i32 = flexible_2d     // → [2][2]i32
val as_i64_2d : [_][_]i64 = flexible_2d     // Same source → [2][2]i64
val as_f32_2d : [_][_]f32 = flexible_2d     // Same source → [2][2]f32

// Mixed numeric types resolve to comptime_array_float
val mixed_2d = [[42, 3.14], [2.71, 100]]    // comptime_array of comptime_array_float
val as_f64_2d : [_][_]f64 = mixed_2d        // All elements fit → [2][2]f64
val as_i32_2d : [_][_]i32 = mixed_2d:[_][_]i32  // Explicit conversion (truncation)
```

### Memory Layout and Performance

Hexen multidimensional arrays use **row-major memory layout**:

#### Memory Organization
```hexen
val matrix : [3][4]i32 = [
    [1,  2,  3,  4 ],    // Row 0
    [5,  6,  7,  8 ],    // Row 1  
    [9,  10, 11, 12]     // Row 2
]

// Memory layout: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
// Contiguous storage with rows stored sequentially
```

#### Performance Characteristics
- **Cache-friendly**: Row-major layout optimizes sequential row access
- **Compile-time size**: All dimensions known at compile time enable optimizations
- **No indirection**: Single contiguous memory block, not array of pointers

#### Array Flattening: Leveraging Row-Major Layout
The row-major memory layout enables **safe array flattening** - converting multidimensional arrays to 1D arrays without runtime cost:

```hexen
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]  // 6 elements total in row-major order
val flattened : [_]i32 = matrix                   // → [6]i32 automatically inferred!

// Memory layout unchanged: [1, 2, 3, 4, 5, 6]
// Same memory addresses, different type view - zero runtime cost
```

**Safe Alternative to Pointer Arithmetic:**
```hexen
// Traditional unsafe approach (what we replace):
// val ptr = &matrix[0][0]               // Raw pointer - dangerous!
// process_buffer(ptr, 6)                // Manual count - error prone!

// Hexen safe approach:
val vertices : [_]f32 = matrix           // Type-safe, size-known automatically
process_buffer(vertices)                 // Bounds checked, no manual calculations
```

### Element Access and Indexing

#### Basic Access Patterns
```hexen
val matrix : [_][_]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

// Element access using double indexing
val element : i32 = matrix[1][2]        // Access row 1, column 2 → 6
val first_row : [3]i32 = matrix[0]      // Access entire first row → [1, 2, 3]

// Comptime bounds checking for constant indices
val valid : i32 = matrix[0][0]          // ✅ Compile-time verified
val last : i32 = matrix[2][2]           // ✅ Compile-time verified  
// val invalid : i32 = matrix[3][0]     // ❌ Compile-time error: row 3 out of bounds

// Runtime bounds checking for dynamic indices
val row_idx : i32 = get_user_input()
val col_idx : i32 = get_user_input()
val dynamic : i32 = matrix[row_idx][col_idx]  // Runtime bounds checks inserted
```

#### Comptime vs Concrete Element Access
Elements from multidimensional arrays follow the same comptime preservation rules:

```hexen
// Comptime matrix elements preserve flexibility
val flexible_matrix = [[42, 100], [200, 300]]   // comptime_array of comptime_array_int
val flexible_elem = flexible_matrix[0][1]       // comptime_int (preserved!)
val flexible_row = flexible_matrix[0]           // comptime_array_int (preserved!)

// Same element adapts to different contexts
val as_i32 : i32 = flexible_elem               // comptime_int → i32
val as_f64 : f64 = flexible_elem               // Same source → f64

// Same row adapts to different contexts
val row_as_i32 : [_]i32 = flexible_row         // comptime_array_int → [2]i32
val row_as_f64 : [_]f64 = flexible_row         // Same source → [2]f64

// Different elements from same matrix can resolve to different types
val elem1_as_i32 : i32 = flexible_matrix[0][0]   // First element → i32
val elem2_as_f64 : f64 = flexible_matrix[0][1]   // Second element → f64 (same source!)
val elem3_as_i64 : i64 = flexible_matrix[1][0]   // Third element → i64 (same source!)

// Different rows from same matrix can resolve to different types  
val row0_as_i32 : [_]i32 = flexible_matrix[0]    // First row → [2]i32
val row1_as_f64 : [_]f64 = flexible_matrix[1]    // Second row → [2]f64 (same matrix!)
```

**Multidimensional Runtime Materialization:**
```hexen
val comptime_matrix = [[42, 100], [200, 300]]  // Exists ONLY in compiler memory

// Each assignment materializes the required portion in runtime memory:
val full_i32 : [_][_]i32 = comptime_matrix     // → Runtime: [[42, 100], [200, 300]] as i32 values
val full_f64 : [_][_]f64 = comptime_matrix     // → Runtime: [[42.0, 100.0], [200.0, 300.0]] as f64 values

val row_i32 : [_]i32 = comptime_matrix[0]      // → Runtime: [42, 100] as i32 values
val row_f64 : [_]f64 = comptime_matrix[1]      // → Runtime: [200.0, 300.0] as f64 values

val elem_i32 : i32 = comptime_matrix[0][0]     // → Runtime: 42 as i32 value  
val elem_f64 : f64 = comptime_matrix[1][1]     // → Runtime: 300.0 as f64 value

// Multiple runtime materializations from single comptime source!
// comptime_matrix itself never exists at runtime - only materialized portions do
```

**Complex Matrix Operations - Zero Runtime Cost:**
```hexen
// Complex matrix computation at compile time  
val complex_matrix = {
    val m1 = [[1, 2], [3, 4]]
    val m2 = [[5, 6], [7, 8]] 
    val multiplied = m1 * m2                    // Matrix multiplication
    val transposed = multiplied.transpose()     // Matrix transposition
    val scaled = transposed.map(|row| row.map(|x| x * 2 + 10))  // Complex element transformation
    assign scaled                               // Result: comptime_array of comptime_array_int
}

// All matrix operations happen at COMPILE TIME - zero runtime cost!
// Runtime only sees the final pre-computed matrix:

val as_i32_matrix : [_][_]i32 = complex_matrix  // → Runtime: pre-computed result matrix
val as_f64_matrix : [_][_]f64 = complex_matrix  // → Runtime: same pre-computed values as f64

// No matrix multiplication, transposition, or transformations at runtime
// Just direct loading of pre-computed constant matrix data
```

#### Concrete Matrix Access
Elements from concrete matrices need explicit types:  
```hexen
val concrete_matrix : [_][_]i32 = [[1, 2], [3, 4]]  // [2][2]i32
val concrete_elem : i32 = concrete_matrix[1][0]     // Explicit type required: i32
val concrete_row : [2]i32 = concrete_matrix[0]      // Explicit type required: [2]i32
val widened_elem : i64 = concrete_matrix[1][0]:i64  // Explicit conversion: i32 → i64
```

### Advanced Multidimensional Patterns

#### 3D and Higher Dimensions
```hexen
// 3D arrays for volumetric data
val cube : [_][_][_]i32 = [
    [[1, 2], [3, 4]],      // Layer 0: 2x2
    [[5, 6], [7, 8]]       // Layer 1: 2x2  
]  // Infers [2][2][2]i32

val element_3d : i32 = cube[1][0][1]  // Access layer 1, row 0, column 1 → 6

// 4D arrays for batch processing
val batch : [_][_][_][_]f32 = [
    [[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]],  // Batch 0
    [[[9.0, 10.0], [11.0, 12.0]], [[13.0, 14.0], [15.0, 16.0]]]  // Batch 1
]  // Infers [2][2][2][2]f32
```

#### Dimension Mismatch Detection
```hexen
// ❌ Inconsistent inner dimensions caught at compile time
// val irregular = [
//     [1, 2, 3],      // 3 elements
//     [4, 5]          // 2 elements - Error: inconsistent dimensions
// ]

// ✅ Type mismatch across dimensions
// val type_mismatch = [
//     [1, 2],         // comptime_int
//     [3.14, 2.71]    // comptime_float - combined into comptime_array_float
// ]  // ✅ This actually works - resolves to comptime_array_float

// ✅ Uniform dimensions required for rectangular arrays
val uniform : [_][3]i32 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]  // ✅ All rows have exactly 3 elements
```

#### Matrix Operations and Transformations
```hexen
// Matrix with explicit conversions
val int_matrix : [_][_]i32 = [[1, 2], [3, 4]]
val float_matrix : [_][_]f64 = [[1.1, 2.2], [3.3, 4.4]]

// Element-wise operations with mixed types require explicit conversions
val mixed_result : [_][_]f64 = [
    [int_matrix[0][0]:f64 + float_matrix[0][0], int_matrix[0][1]:f64 + float_matrix[0][1]],
    [int_matrix[1][0]:f64 + float_matrix[1][0], int_matrix[1][1]:f64 + float_matrix[1][1]]
]

// Matrix conversion (whole array)
val converted_matrix : [_][_]f64 = int_matrix:[_][_]f64  // [2][2]i32 → [2][2]f64
```

### Multidimensional Array Mutability

#### Mutable Multidimensional Arrays
```hexen
// Mutable 2D array requires explicit type
mut grid : [_][_]i32 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  // [3][3]i32

// Element reassignment
grid[1][1] = 42                    // comptime_int → i32 (adapts)
grid[0][2] = big_value:i32         // Explicit conversion if needed

// Row reassignment  
grid[2] = [7, 8, 9]                // comptime_array_int → [3]i32 (adapts)

// Dimension constraints maintained
// grid[0] = [1, 2]                // ❌ Error: [2]i32 ≠ [3]i32 (size mismatch)
```

### Integration with Expression Blocks

#### Multidimensional Arrays in Expression Blocks
```hexen
// Compile-time evaluable matrix computation
val computed_matrix = {
    val base = [[1, 2], [3, 4]]      // comptime_array of comptime_array_int
    val scale = [[2, 2], [2, 2]]     // comptime_array of comptime_array_int  
    val result = base * scale         // Element-wise multiplication
    assign result                    // Preserves comptime type (flexible!)
}

// Same computation used in different contexts
val as_i32_matrix : [_][_]i32 = computed_matrix    // → [2][2]i32
val as_f64_matrix : [_][_]f64 = computed_matrix    // Same source → [2][2]f64

// Runtime evaluable matrix operations require explicit context
val runtime_matrix : [_][_]f32 = {                 // Context required
    val data : [_][_]f32 = load_matrix_data()      // Function call → runtime
    val processed = data * [[1.5, 1.5], [1.5, 1.5]] // Mixed: concrete + comptime
    assign processed
}
```

### Common Use Cases and Patterns

#### Array Flattening for Systems Programming
Leveraging row-major layout for safe pointer replacement:

```hexen
// Graphics: Vertex data (positions + colors)
val vertex_data : [100][6]f32 = generate_vertices()  // 100 vertices, 6 components each
val gpu_buffer : [_]f32 = vertex_data                // → [600]f32 for GPU upload
upload_to_gpu(gpu_buffer)                            // Type-safe, size-automatic

// Scientific computing: Matrix for linear algebra libraries
val matrix : [512][512]f64 = load_matrix()
val linear_data : [_]f64 = matrix                    // → [262144]f64 for BLAS/LAPACK
blas_gemv(linear_data, vector)

// Image processing: RGB pixel data
val image : [height][width][3]u8 = load_image()
val pixel_buffer : [_]u8 = image                     // Flat buffer for codecs
compress_jpeg(pixel_buffer)

// Game development: 3D world serialization
val chunk : [16][16][16]u8 = generate_chunk()
val serialized : [_]u8 = chunk                       // → [4096]u8 for disk/network
save_chunk_data(serialized)
```

**Comptime Flattening with Type Flexibility:**
```hexen
val comptime_matrix = [[42, 100], [200, 300]]        // comptime 2D array
val flat_i32 : [_]i32 = comptime_matrix              // → [4]i32 
val flat_f64 : [_]f64 = comptime_matrix              // Same source → [4]f64
val flat_f32 : [_]f32 = comptime_matrix              // Same source → [4]f32

// One comptime source, multiple flattened materializations!
```

**Element Count Validation (Compile-time Safety):**
```hexen
val matrix_2x3 : [2][3]i32 = data                    // 6 elements total
val cube_2x2x2 : [2][2][2]i32 = data                 // 8 elements total

val flat_6 : [_]i32 = matrix_2x3                     // ✅ → [6]i32
val flat_8 : [_]i32 = cube_2x2x2                     // ✅ → [8]i32

// val wrong : [5]i32 = matrix_2x3                   // ❌ Compile error: 6 ≠ 5
```

#### Graphics and Game Development
```hexen
// Transformation matrices for graphics
val identity_4x4 : [4][4]f32 = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]
]

// Game grid/tilemap
val game_map : [_][_]i32 = [
    [0, 0, 1, 0],    // 0 = empty, 1 = wall
    [0, 1, 1, 0],
    [0, 0, 0, 0],
    [1, 0, 0, 0]
]  // → [4][4]i32
```

#### Scientific Computing
```hexen
// Lookup tables for scientific calculations
val sine_table : [_][2]f64 = [
    [0.0, 0.0],       // [angle, sin(angle)]
    [0.785, 0.707],   // π/4, sin(π/4)  
    [1.57, 1.0]       // π/2, sin(π/2)
]  // → [3][2]f64

// Multi-channel data processing
val sensor_data : [_][_][3]f32 = [  // [time][sensor][x,y,z]
    [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], // Time 0: sensor 0 & 1
    [[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]] // Time 1: sensor 0 & 1  
]  // → [2][2][3]f32
```

### Error Handling for Multidimensional Arrays

#### Dimension Mismatch Errors
```
Error: Inconsistent inner array dimensions in multidimensional array literal
Expected: [3]i32 (from first row)
Found: [2]i32 (at row 2)
All inner arrays must have the same length for rectangular arrays
```

#### Size Constraint Violations  
```
Error: Cannot assign [2][3]i32 to variable of type [3][2]i32
Matrix dimensions must match exactly: expected [3][2], got [2][3]
```

#### Index Out of Bounds
```
Error: Matrix index [2][5] out of bounds for array of size [3][4]
Valid indices: rows 0-2, columns 0-3
```

### Performance Considerations

#### Memory Access Patterns
```hexen
// ✅ Cache-friendly row-major traversal
for matrix |row, row_idx| {
    for row |element, col_idx| {
        process(element)  // Sequential memory access
    }
}

// ⚠️ Less cache-friendly column-major access
for col_idx in 0..matrix[0].length {
    for row_idx in 0..matrix.length {
        process(matrix[row_idx][col_idx])  // Non-sequential access
    }
}
```

#### Compile-time Optimizations
- **Bounds checking elimination**: Constant indices checked at compile time
- **Memory layout optimization**: Contiguous storage enables vectorization
- **Size-based optimizations**: Known dimensions enable loop unrolling

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
    
    // ===== Multidimensional Arrays =====
    val matrix_2d = [[1, 2, 3], [4, 5, 6]]     // comptime_array of comptime_array_int
    val as_i32_matrix : [_][_]i32 = matrix_2d   // → [2][3]i32
    val as_f64_matrix : [_][_]f64 = matrix_2d   // Same source → [2][3]f64
    
    // Element access patterns
    val matrix_elem : i32 = as_i32_matrix[1][2] // Access row 1, column 2: 6
    val flexible_elem = matrix_2d[0][1]         // comptime_int (flexible!)
    val whole_row : [3]i32 = as_i32_matrix[0]   // Access entire first row: [1, 2, 3]
    
    // 3D array example  
    val cube_3d = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]  // [2][2][2] comptime
    val as_i32_cube : [_][_][_]i32 = cube_3d    // → [2][2][2]i32
    val cube_elem : i32 = as_i32_cube[1][0][1]  // Access layer 1, row 0, col 1: 6
    
    // Mixed dimensions
    val mixed_matrix : [_][3]i32 = [            // Outer inferred, inner fixed
        [1, 2, 3],
        [4, 5, 6],  
        [7, 8, 9]
    ]  // → [3][3]i32
    
    // Mutable multidimensional arrays
    mut grid : [_][_]i32 = [[0, 0], [0, 0]]     // [2][2]i32
    grid[0][1] = 42                              // Element assignment
    grid[1] = [7, 8]                             // Row assignment
    
    // ===== Array Flattening (Safe Pointer Replacement) =====
    // Multidimensional → 1D flattening leverages row-major layout
    val matrix_3d : [2][3][4]i32 = generate_3d_data()  // 24 elements total
    val flattened_24 : [_]i32 = matrix_3d               // → [24]i32 (automatic size!)
    
    // Zero runtime cost - same memory, different type view
    val matrix_2d : [4][6]f32 = load_vertex_positions()
    val vertex_buffer : [_]f32 = matrix_2d              // → [24]f32 for GPU
    render_vertices(vertex_buffer)                       // Type-safe, bounds-checked
    
    // Comptime flattening with type flexibility
    val comptime_3x3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  // comptime 2D array
    val flat_i32 : [_]i32 = comptime_3x3                   // → [9]i32
    val flat_f64 : [_]f64 = comptime_3x3                   // Same source → [9]f64
    val flat_f32 : [_]f32 = comptime_3x3                   // Same source → [9]f32
    
    // Element count validation at compile time
    val small_matrix : [2][2]i32 = [[1, 2], [3, 4]]        // 4 elements total
    val flattened_4 : [_]i32 = small_matrix                 // ✅ → [4]i32
    // val wrong_size : [3]i32 = small_matrix               // ❌ Compile error: 4 ≠ 3
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
6. **Zero-Cost Flattening**: Multidimensional → 1D conversion with no runtime overhead
7. **Safe Pointer Replacement**: Eliminates unsafe pointer arithmetic patterns

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