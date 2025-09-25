# Hexen Array Type System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's array type system, integrating seamlessly with the existing comptime type system while following proven patterns from languages like Zig. Arrays maintain Hexen's core principle of "Ergonomic Literals + Transparent Runtime Costs".
> 
> **NOT YET IMPLEMENTED!**

## Overview

Hexen's array type system extends the language's comptime philosophy to collections, making array literals seamless to work with while keeping all runtime computational costs visible. Arrays follow the same ergonomic principles as individual values - comptime arrays adapt seamlessly while concrete array conversions require explicit conversions.

**Core Language Focus**: The array type system focuses purely on **type safety**, **memory layout**, and **element access**. Advanced array operations (filtering, mapping, sorting, etc.) are intentionally **not part of the core language** and will be provided by a future standard library to keep the language specification clean and focused.

## Core Philosophy

### Design Principle: Array Integration with Comptime Types and Reference System

Hexen's arrays follow the same **"Ergonomic Literals + Transparent Runtime Costs"** philosophy while integrating seamlessly with the reference system:

- **Ergonomic Array Literals**: Comptime array types adapt seamlessly (zero runtime cost)
- **Transparent Runtime Costs**: All concrete array conversions require explicit syntax (`value:type`)
- **Safe Array Data Sharing**: Array references (`&arr: [N]T`) enable efficient zero-copy data access
- **Explicit Copy vs Reference Choice**: Clear distinction between `arr` (copy) and `&arr` (share) in function parameters
- **Consistent with Individual Values**: Arrays follow identical patterns to single-value type system
- **Natural Usage**: Common array literal patterns work without ceremony (`[1, 2, 3]`, `[3.14, 2.71]`)
- **Size-as-Type**: Array size is part of the type itself, enabling compile-time safety
- **Reference-Only Flattening**: True zero-cost dimensional flattening only works with references
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

**Complex Comptime Computations - Future Standard Library:**
```hexen
// Note: Advanced array operations will be provided by future standard library - not yet specified
// The core language focuses on type safety and element access only

val complex_comptime = {
    val base = [1, 2, 3, 4, 5]
    val transformed = base * [10, 20, 30, 40, 50]          // Element-wise multiplication
    val filtered = transformed.filter(|x| x > 25)          // Filtering operation - 'filter' not yet specified
    val final = filtered.map(|x| x * x + 100)              // Complex transformation - 'map' not yet specified
    -> final                                            // Result: comptime_array_int
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

## Core Array Features

### Array Creation and Element Access

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

## Array Reference Parameters

Arrays integrate seamlessly with Hexen's reference system, enabling efficient data sharing for function parameters without copying large data structures.

### Basic Array Reference Syntax

Array references follow the same patterns as other reference types, with array-specific considerations:

```hexen
// Array reference parameter declarations
func process_array(&data: [_]i32) : i32 = {
    // Reference parameter provides direct access to original array (no copy)
    return data[0] + data[data.length - 1]  // Automatic dereferencing
}

func sum_large_dataset(&dataset: [10000]f64) : f64 = {
    // Efficient: no copying of 80KB of data
    val first : f64 = dataset[0]            // Direct access to original
    val last : f64 = dataset[9999]          // No memory allocation
    return first + last
}

// Mutable array reference parameters
func normalize_array(mut &array: [_]f64, factor: f64) : void = {
    // Modify original array in-place
    array[0] = array[0] / factor            // Direct modification
    array[1] = array[1] / factor            // No copying overhead
    // ... process remaining elements
}
```

### Array Reference Call Patterns

Array reference parameters require explicit reference passing with `&` syntax:

```hexen
// Calling functions with array references
val data : [1000]i32 = initialize_data()   // Concrete array required
val result : i32 = process_array(&data)    // ✅ Pass reference to concrete array

val large_set : [10000]f64 = load_scientific_data()
val sum : f64 = sum_large_dataset(&large_set)  // ✅ No copying - efficient!

// Mutable array processing
mut values : [100]f64 = load_values()
normalize_array(&values, 2.0)              // ✅ Modify original array in-place

// ❌ Cannot pass comptime arrays by reference
val flexible_array = [1, 2, 3, 4, 5]       // comptime_array_int
// process_array(&flexible_array)          // Error: Cannot reference comptime type
```

### Performance Comparison: Copy vs Reference

Array references provide significant performance benefits for large data structures:

```hexen
// Value parameter approach (copying)
func process_by_copy(data: [10000]f64) : f64 = {
    // This function receives a COPY of 80KB of data
    return data[0] * data[9999]
}

// Reference parameter approach (zero-copy)
func process_by_reference(&data: [10000]f64) : f64 = {
    // This function receives a REFERENCE (~8 bytes)
    return data[0] * data[9999]             // Same computation, no copying
}

// Usage demonstrates performance difference
val scientific_data : [10000]f64 = load_experiment_results()

// Expensive: copies 80KB for each call
val result1 : f64 = process_by_copy(scientific_data)      // 80KB copied
val result2 : f64 = process_by_copy(scientific_data)      // Another 80KB copied

// Efficient: shares original data
val efficient1 : f64 = process_by_reference(&scientific_data)  // ~8 bytes reference
val efficient2 : f64 = process_by_reference(&scientific_data)  // ~8 bytes reference
```

### Array Reference Mutability

Array references follow the same mutability rules as other references:

```hexen
// Read-only array reference (default)
func analyze_data(&data: [_]i32, threshold: i32) : i32 = {
    val count : i32 = 0
    // data[0] = 999                        // ❌ Error: Cannot modify through read-only reference
    val analysis : i32 = data[0] + data[1] // ✅ Read access through reference
    return analysis
}

// Mutable array reference (explicit)
func scale_values(mut &values: [_]f64, factor: f64) : void = {
    values[0] = values[0] * factor          // ✅ Can modify through mutable reference
    values[1] = values[1] * factor          // ✅ Direct in-place processing
}

// Calling mutable array reference functions
val data : [100]i32 = load_data()
analyze_data(&data, 50)                     // ✅ Read-only access with immutable array

mut processable : [100]f64 = load_values()
scale_values(&processable, 1.5)             // ✅ In-place modification with mutable array

val immutable : [100]f64 = load_constants()
// scale_values(&immutable, 1.5)           // ❌ Error: Cannot create mutable reference to immutable array
```

### Array Reference with Multidimensional Arrays

Array references work seamlessly with multidimensional arrays and flattening:

```hexen
// 2D array reference parameters
func process_matrix(&matrix: [_][_]f64, factor: f64) : f64 = {
    // Direct access to 2D array without copying
    return matrix[0][0] * matrix[matrix.length-1][matrix[0].length-1] * factor
}

// In-place 2D array processing
func transform_matrix(mut &matrix: [_][_]f64, scale: f64) : void = {
    // Modify original 2D array in-place
    matrix[0][0] = matrix[0][0] * scale     // Direct modification
    matrix[1][1] = matrix[1][1] * scale     // No memory allocation
}

// Array flattening with references (zero-cost)
func process_flat_view(&matrix: [4][4]f64) : f64 = {
    val &flattened : [_]f64 = &matrix       // Zero-cost flattened view
    return flattened[0] + flattened[15]     // Access via flat view: matrix[0][0] + matrix[3][3]
}

// Usage with multidimensional arrays
val matrix_2d : [4][4]f64 = load_transformation_matrix()
val result : f64 = process_matrix(&matrix_2d, 2.0)     // No copying of 128 bytes
process_flat_view(&matrix_2d)                          // Zero-cost flattened access
```

## Integration with Expression Blocks

Arrays work seamlessly with Hexen's unified block system:

### Compile-Time Evaluable Array Blocks
Blocks containing only comptime array operations preserve flexibility:

```hexen
val flexible_array_computation = {
    val base = [1, 2, 3]                 // comptime_array_int
    val multiplier = [2, 2, 2]           // comptime_array_int
    val result = base.mul(multiplier)    // Element-wise multiplication → comptime_array_int - 'mul' not yet specified
    -> result                            // Preserves comptime_array_int (flexible!)
}

// Same computation, different target types
val as_i32 : [_]i32 = flexible_array_computation    // → [3]i32
val as_i64 : [_]i64 = flexible_array_computation    // Same source → [3]i64
val as_f64 : [_]f64 = flexible_array_computation    // Same source → [3]f64
```

### Runtime Evaluable Array Blocks
Blocks with function calls or concrete arrays require explicit context:

```hexen
val runtime_array_result : [_]i32 = {                   // Explicit context required
    val input_data : [_]i32 = load_array_data()         // Function call → runtime (explicit type required)
    val processed : [_]i32 = input_data.mul([2, 2, 2])  // Mixed: concrete + comptime - 'mul' not yet specified
    -> processed                                
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

#### Array Flattening: Reference-Only Zero-Cost Views
The row-major memory layout enables **true zero-cost array flattening** - but only through references, which provide different views of the same memory:

**❌ Value-Based Flattening (Copying - Not Zero Cost):**
```hexen
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]  // 6 elements total
val flattened : [_]i32 = matrix                   // ❌ Copies entire array! (24 bytes)
// This creates a NEW array in memory with a different layout
```

**✅ Reference-Based Flattening (True Zero Cost):**
```hexen
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]  // 6 elements total in row-major order
val &flattened : [_]i32 = &matrix                 // → &[6]i32 reference view!

// Memory layout unchanged: [1, 2, 3, 4, 5, 6]
// Same memory addresses, different type view - TRUE zero runtime cost
// flattened[0] == matrix[0][0], flattened[3] == matrix[1][0]
```

**Safe Alternative to Pointer Arithmetic:**
```hexen
// Traditional unsafe approach (what we replace):
// val ptr = &matrix[0][0]               // Raw pointer - dangerous!
// process_buffer(ptr, 6)                // Manual count - error prone!

// Hexen safe approach - Reference-based:
val matrix : [4][6]f32 = load_vertex_positions()
val &vertices : [_]f32 = &matrix         // Type-safe reference view, size-known automatically
process_buffer(&vertices)                // Pass reference - bounds checked, no copying
```

**Why References Are Required for Zero-Cost Flattening:**
- **Value assignment** (`val flat = matrix`) **must copy** because it creates a new variable with different memory layout
- **Reference view** (`val &flat = &matrix`) **shares memory** because it's just a different way to access the same data
- **True zero cost** is only achievable when no memory allocation or copying occurs

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
    val multiplied = m1.mul(m2)                    // Matrix multiplication - 'mul' not yet specified
    val transposed = multiplied.transpose()     // Matrix transposition - 'transpose' not yet specified
    val scaled = transposed.map(|row| row.map(|x| x * 2 + 10))  // Complex element transformation - 'map' not yet specified
    -> scaled                               // Result: comptime_array of comptime_array_int
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

#### Element and Row References
References to individual elements or rows from concrete arrays enable zero-copy access patterns:

**Single Element References:**
```hexen
val numbers : [_]i32 = [10, 20, 30, 40, 50]     // [5]i32

// Element references - zero copy access to individual elements
val &first_ref : i32 = &numbers[0]              // Reference to first element
val &last_ref : i32 = &numbers[4]               // Reference to last element

// Using element references
func process_element(&elem: i32) : i32 = {
    return elem * 2                              // Automatic dereferencing
}

val doubled : i32 = process_element(&numbers[2]) // Pass element by reference
```

**Row References from Multidimensional Arrays:**
```hexen
val matrix : [_][_]f64 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]  // [3][3]f64

// Row references - zero copy access to entire rows
val &first_row : [3]f64 = &matrix[0]            // Reference to [1.0, 2.0, 3.0]
val &middle_row : [3]f64 = &matrix[1]           // Reference to [4.0, 5.0, 6.0]

// Using row references in functions
func compute_row_sum(&row: [3]f64) : f64 = {
    return row[0] + row[1] + row[2]             // Automatic dereferencing
}

val sum1 : f64 = compute_row_sum(&matrix[0])    // Process first row by reference
val sum2 : f64 = compute_row_sum(&matrix[2])    // Process third row by reference

// Mutable element and row references
mut mutable_matrix : [_][_]i32 = [[1, 2], [3, 4]]  // [2][2]i32

func increment_element(mut &elem: i32) : void = {
    elem = elem + 1                             // Direct modification via reference
}

func scale_row(mut &row: [2]i32, factor: i32) : void = {
    row[0] = row[0] * factor                    // Direct row modification
    row[1] = row[1] * factor
}

increment_element(&mutable_matrix[0][0])        // Modify single element: [1,2] → [2,2]
scale_row(&mutable_matrix[1], 10)               // Modify entire row: [3,4] → [30,40]
```

**Element References with Mixed Types:**
```hexen
val mixed_data : [_]f64 = [1.5, 2.7, 3.9]      // [3]f64

// Element reference in different contexts
func process_as_int(mut &value: f64) : i32 = {
    value = value * 2.0                         // Modify original via reference
    return value:i32                            // Return converted copy
}

val result : i32 = process_as_int(&mixed_data[1])  // mixed_data[1] becomes 5.4, returns 5
```

**Benefits of Element and Row References:**
- **Zero Copy Access**: No data duplication when accessing array elements or rows
- **Efficient Processing**: Pass large rows to functions without copying
- **In-Place Modification**: Direct mutation of specific elements or rows
- **Memory Efficiency**: Work with subsets of large arrays without allocation
- **Cache Locality**: References maintain original memory layout for better performance

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
// Matrix type conversions - core language feature
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
    val result = base.mul(scale)         // Element-wise multiplication - 'mul' not yet specified
    -> result                    // Preserves comptime type (flexible!)
}

// Same computation used in different contexts
val as_i32_matrix : [_][_]i32 = computed_matrix    // → [2][2]i32
val as_f64_matrix : [_][_]f64 = computed_matrix    // Same source → [2][2]f64

// Runtime evaluable matrix operations require explicit context
val runtime_matrix : [_][_]f32 = {                 // Context required
    val data : [_][_]f32 = load_matrix_data()      // Function call → runtime
    val processed = data.mul([[1.5, 1.5], [1.5, 1.5]]) // Mixed: concrete + comptime - 'mul' not yet specified
    -> processed
}
```

### Common Use Cases and Patterns

#### Array Flattening for Systems Programming
Leveraging row-major layout with reference-based flattening for true zero-cost performance:

**❌ Copy-Based Approach (Expensive):**
```hexen
// Graphics: Vertex data (positions + colors) - COPYING APPROACH
val vertex_data : [100][6]f32 = generate_vertices()  // 100 vertices, 6 components each
val gpu_buffer : [_]f32 = vertex_data                // ❌ Copies 2.4KB! Creates new flat array
upload_to_gpu(gpu_buffer)                            // Pass copy to GPU
```

**✅ Reference-Based Approach (Zero-Cost):**
```hexen
// Graphics: Vertex data (positions + colors) - REFERENCE APPROACH
val vertex_data : [100][6]f32 = generate_vertices()  // 100 vertices, 6 components each
val &gpu_buffer : [_]f32 = &vertex_data              // ✅ Zero cost! Same memory, flat view
upload_to_gpu(&gpu_buffer)                           // Pass reference to GPU

// Scientific computing: Matrix for linear algebra libraries
val matrix : [512][512]f64 = load_matrix()
val &linear_data : [_]f64 = &matrix                  // ✅ Zero-cost view of 2MB matrix
blas_gemv(&linear_data, &vector)                     // No copying - pass references

// Image processing: RGB pixel data
val image : [height][width][3]u8 = load_image()
val &pixel_buffer : [_]u8 = &image                   // ✅ Zero-cost flat view
compress_jpeg(&pixel_buffer)                         // Process via reference

// Game development: 3D world serialization
val chunk : [16][16][16]u8 = generate_chunk()
val &serialized : [_]u8 = &chunk                     // ✅ Zero-cost flat view of 4KB
save_chunk_data(&serialized)                         // Serialize via reference
```

**Comptime Flattening with Type Flexibility (Copy-Based):**
```hexen
// Comptime arrays can be materialized as different flattened types (copying)
val comptime_matrix = [[42, 100], [200, 300]]        // comptime 2D array
val flat_i32 : [_]i32 = comptime_matrix              // → [4]i32 (materialized copy)
val flat_f64 : [_]f64 = comptime_matrix              // → [4]f64 (different materialized copy)
val flat_f32 : [_]f32 = comptime_matrix              // → [4]f32 (another materialized copy)

// Multiple runtime materializations from single comptime source
// Each creates a separate concrete array in memory
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
    
    // ===== Array Type Conversions =====
    val numbers1 : [_]i32 = [1, 2, 3]           // [3]i32
    val numbers2 : [_]i32 = [4, 5, 6]           // [3]i32

    val floats1 : [_]f32 = [1.1, 2.2]           // [2]f32
    val floats2 : [_]f64 = [3.3, 4.4]           // [2]f64
    val converted: [_]f64  = floats1:[_]f64               // Explicit array type conversion
    
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
        val scaled = base.mul([2, 2, 2, 2])       // comptime array ops - 'mul' not yet specified
        -> scaled                           // Preserves comptime_array_int
    }
    val comp_as_i32 : [_]i32 = flexible_computation  // → [4]i32
    val comp_as_f64 : [_]f64 = flexible_computation  // Same source → [4]f64

    // Runtime evaluable (requires explicit context)
    val runtime_result : [_]f64 = {             // Context required
        val data = load_data_array()            // Function call → runtime
        val processed = data.mul([1.5, 1.5, 1.5]) // Mixed concrete + comptime - 'mul' not yet specified
        -> processed
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
    
    // ===== Array Flattening (Reference-Based Zero-Cost) =====
    // True zero-cost flattening only works with references
    val matrix_3d : [2][3][4]i32 = generate_3d_data()  // 24 elements total
    val &flattened_24 : [_]i32 = &matrix_3d             // ✅ Zero cost! Reference view → &[24]i32

    // True zero runtime cost - same memory, reference view
    val matrix_2d : [4][6]f32 = load_vertex_positions()
    val &vertex_buffer : [_]f32 = &matrix_2d            // ✅ Zero cost! → &[24]f32 reference
    render_vertices(&vertex_buffer)                      // Pass reference - no copying

    // ===== Copy-Based vs Reference-Based Comparison =====
    val large_matrix : [100][100]f64 = load_matrix()    // 80KB matrix

    // Copy-based (expensive):
    val copied_flat : [_]f64 = large_matrix             // ❌ Copies 80KB!
    process_flat_copy(copied_flat)                       // Process copy

    // Reference-based (zero-cost):
    val &ref_flat : [_]f64 = &large_matrix             // ✅ Zero cost! Same memory
    process_flat_reference(&ref_flat)                   // Process original via reference

    // ===== Comptime Arrays (Copy-Based Materialization) =====
    // Comptime arrays create copies when materialized as concrete types
    val comptime_3x3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  // comptime 2D array
    val flat_i32 : [_]i32 = comptime_3x3                   // → [9]i32 (materialized copy)
    val flat_f64 : [_]f64 = comptime_3x3                   // → [9]f64 (different materialized copy)
    val flat_f32 : [_]f32 = comptime_3x3                   // → [9]f32 (another materialized copy)

    // Element count validation at compile time (reference-based)
    val small_matrix : [2][2]i32 = [[1, 2], [3, 4]]        // 4 elements total
    val &flattened_4 : [_]i32 = &small_matrix               // ✅ Zero cost → &[4]i32
    // val &wrong_size : [3]i32 = &small_matrix             // ❌ Compile error: &[4]i32 ≠ &[3]i32
}
```

## Array Reference Safety and Error Handling

### Array Reference Safety Guarantees

Array references maintain all safety guarantees from the reference system while adding array-specific protections:

```hexen
// ✅ Safe array reference patterns
func safe_array_processing() : f64 = {
    val data : [1000]f64 = load_scientific_data()      // Concrete array in function scope

    // Reference stays within data's lifetime - compiler ensures safety
    val result : f64 = process_by_reference(&data)     // ✅ Safe: reference doesn't escape

    // Array flattening with references is also safe
    val matrix : [10][100]f64 = reshape_data(&data)    // Create 2D view
    val &flattened : [_]f64 = &matrix                  // ✅ Zero-cost flat view

    return result
    // data and matrix destroyed here, but references already used - no dangling reference risk
}

// ❌ Unsafe patterns caught at compile-time
func create_dangling_array_ref() : &[100]i32 = {
    val local_array : [100]i32 = initialize_array()
    return &local_array                                // ❌ Error: Reference to local array escaping scope
}
```

### Array Reference Lifetime Management

Array references follow strict lifetime rules to prevent memory safety issues:

```hexen
// ✅ Valid: Reference lifetime within target scope
val global_data : [1000]i32 = load_global_data()
val &global_ref : [_]i32 = &global_data               // ✅ Valid: both have same lifetime

// ✅ Valid: Reference passed to function, used immediately
func process_immediately(&data: [_]f64) : f64 = {
    return data[0] + data[data.length - 1]             // ✅ Valid: immediate use
}

// ❌ Invalid: Reference escaping its target's scope
val &escaped_ref : [_]i32 = {
    val temp_array : [100]i32 = create_temp_array()
    -> &temp_array                                     // ❌ Error: Reference escaping block scope
}
```

### Array Reference Error Messages

Hexen provides clear, actionable error messages for array reference issues:

#### Array Reference Declaration Errors
```
Error: Cannot create reference to comptime array type 'comptime_array_int'
  Array reference '&flexible_ref' requires concrete array type
  Comptime arrays exist only during compilation and cannot be referenced
  Suggestion: Use explicit type annotation to create concrete array:
    val concrete : [_]i32 = [1, 2, 3]
    val &array_ref : [_]i32 = &concrete
```

#### Array Reference Assignment Errors
```
Error: Cannot create mutable reference to immutable array
  Array 'immutable_data' is declared with 'val' (immutable)
  Cannot create 'mut &array_ref' (writable view) of immutable array
  Suggestion: Use read-only reference instead:
    val &readonly_ref : [_]i32 = &immutable_data
```

#### Array Flattening Reference Errors
```
Error: Array flattening requires reference syntax for zero-cost operation
  Assignment 'val flat = matrix' would copy entire array (expensive)
  For true zero-cost flattening, use reference syntax:
    val &flat : [_]i32 = &matrix
```

#### Array Reference Function Call Errors
```
Error: Function expects array reference parameter, got array value
  Function 'process_array' expects '&data: [_]i32' but received array value
  Use reference syntax in function call:
    process_array(&my_array)  // Pass reference to array
```

#### Array Reference Size Mismatch Errors
```
Error: Array reference size mismatch in flattening operation
  Cannot create reference '&flat : [10]i32' to array '[2][3]i32'
  Source has 6 elements but target expects 10 elements
  Suggestion: Use inferred size for automatic calculation:
    val &flat : [_]i32 = &matrix  // Automatically infers [6]i32
```

### Array Reference Integration with Comptime Types

Array references maintain the clean separation between comptime and concrete types:

```hexen
// ===== COMPTIME ARRAYS (No References Allowed) =====
val flexible_array = [1, 2, 3, 4, 5]           // comptime_array_int (flexible!)
// val &invalid_ref = &flexible_array          // ❌ Error: Cannot reference comptime type

// These preserve comptime flexibility for later materialization
val as_i32 : [_]i32 = flexible_array           // comptime_array_int → [5]i32 (copy)
val as_i64 : [_]i64 = flexible_array           // Same source → [5]i64 (different copy)
val as_f64 : [_]f64 = flexible_array           // Same source → [5]f64 (another copy)

// ===== CONCRETE ARRAYS (References Allowed) =====
val concrete : [_]i32 = [1, 2, 3, 4, 5]        // Explicit concrete array
val concrete_2d : [_][_]i32 = [[1, 2], [3, 4]] // Explicit concrete 2D array

// References work with concrete arrays only
val &ref_1d : [_]i32 = &concrete                // ✅ OK: Reference to concrete 1D array
val &ref_2d : [_][_]i32 = &concrete_2d          // ✅ OK: Reference to concrete 2D array
val &ref_flat : [_]i32 = &concrete_2d           // ✅ OK: Zero-cost flattened reference view

// ===== THE BOUNDARY IS CLEAR =====
// Comptime arrays: Flexible, no references, compile-time evaluation
// Concrete arrays: Fixed, can be referenced, runtime memory allocation
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
6. **Zero-Cost Array References**: Reference-based array sharing (`&arr`) with no copying overhead
7. **Reference-Only Flattening**: True zero-cost dimensional flattening only with references (`&arr`)
8. **Copy vs Reference Choice**: Explicit distinction between copying (`arr`) and sharing (`&arr`) data
9. **Safe Pointer Replacement**: Eliminates unsafe pointer arithmetic patterns with automatic dereferencing
10. **Efficient Large Array Processing**: References enable processing of large arrays without memory duplication

### Type Safety

1. **Compile-Time Size Checking**: Array size mismatches caught at compile time
2. **Element Type Safety**: All element conversions follow standard type rules
3. **Bounds Safety**: Index out of bounds errors caught early
4. **No Silent Coercion**: All array type changes require explicit syntax
5. **Array Reference Safety**: Immutable references prevent accidental mutation (`val &arr`)
6. **Mutable Reference Requirements**: Mutable array references require explicit mutable targets (`mut &arr`)
7. **Automatic Dereferencing Safety**: References work like values with compile-time lifetime checking
8. **Integration Safety**: Arrays integrate seamlessly with expression blocks

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
- **Element Access**: Individual array elements follow binary operation rules
- **Type Conversions**: Same explicit conversion requirements for array types
- **Transparent Costs**: All array type conversion costs visible

### Compatibility with UNIFIED_BLOCK_SYSTEM.md
- **Expression Block Integration**: Arrays work seamlessly in expression blocks
- **Compile-time vs Runtime**: Same classification rules for array operations
- **Block Type Preservation**: Comptime arrays preserve flexibility through blocks

### Compatibility with REFERENCE_SYSTEM.md
- **Unified Reference Syntax**: Arrays use same reference syntax (`&arr: [N]T`)
- **Automatic Dereferencing**: Array references work transparently like values
- **Mutability Rules**: Same `val &` vs `mut &` patterns for array references
- **Safety Guarantees**: Same compile-time lifetime and mutability checking
- **Function Integration**: Array references integrate seamlessly with function parameters

This array type system extends Hexen's proven comptime philosophy to collections, maintaining consistency with existing language patterns while focusing on the core essentials: **type safety**, **memory layout**, and **element access**. Advanced array operations are intentionally left to a future standard library, keeping the core language clean and focused.

The result is a minimal yet powerful array system that provides the ergonomics and safety that developers expect from a modern systems programming language, without bloating the core language specification.