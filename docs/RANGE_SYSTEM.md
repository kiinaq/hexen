# Hexen Range System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's range type system, which provides lazy sequence representations for iteration and array slicing. Ranges follow Hexen's core philosophy of "Ergonomic Literals + Transparent Costs" by enabling zero-cost view operations while making materialization costs explicit through assignment.

## Overview

Hexen's range system provides a **first-class lazy array type** that serves multiple purposes:

1. **Array slicing** - Extract sub-arrays with zero-cost views
2. **Iteration** (future) - Loop over sequences without materializing arrays
3. **Array generation** - Create arrays from numeric sequences

Ranges are **immutable, lazy sequences** that compute values on-demand. They act as **views** into data (zero-cost) until assignment to an array type triggers **materialization** (explicit copy).

## Core Philosophy

### Ranges as Lazy Arrays

```hexen
// Range is a lazy sequence specification
val r : range[i32] = 1..10           // Stores: start=1, end=10, step=1 (O(1) space)

// Materialization creates actual array
val arr : [_]i32 = [r]               // Generates: [1, 2, 3, 4, 5, 6, 7, 8, 9] (O(n) space)
```

**Key Principle:** Ranges describe sequences without storing elements. Cost is transparent through assignment.

### The View Model: Zero-Cost Slicing

```hexen
val src : [_]i32 = [10, 20, 30, 40, 50]

// Slicing creates view (zero-cost, just metadata)
src[1..4]                            // View: { ptr: &src[1], length: 3 }

// Assignment materializes view (explicit copy)
val slice : [_]i32 = src[1..4]       // NOW it copies: [20, 30, 40]

// Future: iteration over view (zero-copy)
for elem in src[1..4] {              // No materialization! Iterates over view
    print(elem)
}
```

**Key Principle:** The `[range]` operation is free (creates view), assignment triggers copy (visible cost).

## Type Definition

### Range Type Syntax

```hexen
range[T]                             // Range with element type T
```

**Supported element types:**
- Integer types: `i32`, `i64`
- Float types: `f32`, `f64` (step required!)
- Comptime types: `comptime_int`, `comptime_float`

### Internal Representation

Ranges are represented compactly regardless of sequence length:

```
Range {
    start: Option<T>      // None for ..end and ..
    end: Option<T>        // None for start.. and ..
    step: Option<T>       // None for integers (implicit 1), required for floats
    inclusive: bool       // false for .., true for ..=
}
```

**Memory efficiency:** A range storing 1 billion values uses the same memory as a range storing 10 values (O(1) space).

## Range Syntax

### Bounded Ranges

**Exclusive (default) - `..`**

```hexen
val r1 : range[i32] = 1..10              // [1, 2, 3, 4, 5, 6, 7, 8, 9]
val r2 : range[i32] = 1..10:2            // [1, 3, 5, 7, 9] (step 2)
val r3 : range[i32] = 10..1:-1           // [10, 9, 8, 7, 6, 5, 4, 3, 2] (reverse)

val r4 : range[f32] = 0.0..10.0:0.5      // [0.0, 0.5, 1.0, ..., 9.5] (step required!)
```

- **Syntax:** `start..end` or `start..end:step`
- **Semantics:** Includes `start`, excludes `end`
- **Step:** Optional for integers (default 1), required for floats
- **Negative step:** Allowed (reverses iteration direction)

**Inclusive - `..=`**

```hexen
val r1 : range[i32] = 1..=10             // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
val r2 : range[i32] = 1..=10:2           // [1, 3, 5, 7, 9] (stops before exceeding 10)
val r3 : range[i32] = 10..=1:-1          // [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

val r4 : range[f32] = 0.0..=10.0:0.5     // [0.0, 0.5, 1.0, ..., 10.0] (includes 10.0!)
```

- **Syntax:** `start..=end` or `start..=end:step`
- **Semantics:** Includes both `start` and `end`
- **Step behavior:** Stops when next value would exceed `end`
- **Example:** `1..=10:3` → `[1, 4, 7, 10]` (includes 10), `1..=11:3` → `[1, 4, 7, 10]` (stops at 10)

### Unbounded Ranges

**From (start to infinity) - `start..`**

```hexen
val r1 : range[i32] = 5..                // [5, 6, 7, 8, ...] (infinite)
val r2 : range[i32] = 5..:2              // [5, 7, 9, 11, ...] (step 2, infinite)
val r3 : range[f32] = 5.0..:0.1          // [5.0, 5.1, 5.2, ...] (step required for float!)
```

- **Syntax:** `start..` or `start..:step`
- **Semantics:** Starts at `start`, continues indefinitely
- **Use cases:** Iteration (future), array slicing (from index to end)
- **Step:** Optional for integers, required for floats

**To (beginning to end) - `..end`**

```hexen
val r1 : range[i32] = ..10               // Undefined start, ends before 10
val r2 : range[i32] = ..=10              // Undefined start, ends at 10
```

- **Syntax:** `..end` or `..=end`
- **Semantics:** No defined start point, ends before/at `end`
- **Step:** ❌ **NOT allowed** (ambiguous start point!)
- **Use cases:** Array slicing only (from beginning to index)
- **Cannot iterate:** No start point defined

**Full (unbounded both ends) - `..`**

```hexen
val r : range[i32] = ..                  // Unbounded both directions
```

- **Syntax:** `..`
- **Semantics:** No start or end
- **Step:** ❌ **NOT allowed** (no start or end!)
- **Use cases:** Array slicing only (full array copy)
- **Cannot iterate:** No start point defined

### Step Syntax Summary

| Range Form | Step Allowed? | Example | Notes |
|------------|---------------|---------|-------|
| `start..end` | ✅ Yes | `0..100:2` | Bounded range with step |
| `start..=end` | ✅ Yes | `0..=100:2` | Inclusive bounded with step |
| `start..` | ✅ Yes | `5..:2` | Unbounded from with step (infinite) |
| `..end` | ❌ No | `..10:2` ❌ | Ambiguous start point! |
| `..=end` | ❌ No | `..=10:2` ❌ | Ambiguous start point! |
| `..` | ❌ No | `..:2` ❌ | No start or end! |

## Integer vs Float Ranges

### Integer Ranges

**Step is optional (default 1):**

```hexen
// Implicit step of 1
val r1 : range[i32] = 1..10              // [1, 2, 3, 4, 5, 6, 7, 8, 9]
val r2 : range[i64] = 0..100             // [0, 1, 2, ..., 99]

// Explicit step
val evens : range[i32] = 0..100:2        // [0, 2, 4, 6, ..., 98]
val tens : range[i32] = 0..100:10        // [0, 10, 20, ..., 90]

// Negative step (reverse)
val reverse : range[i32] = 10..0:-1      // [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
```

**Why implicit step works:**
- Default step of 1 is universally expected
- No precision issues (integers are exact)
- Iteration count is deterministic

### Float Ranges

**Step is REQUIRED:**

```hexen
// ❌ ERROR: Float range without step
val bad : range[f32] = 0.0..10.0         // ❌ Comptime error: float range requires explicit step

// ✅ CORRECT: Explicit step
val good : range[f32] = 0.0..10.0:0.1    // [0.0, 0.1, 0.2, ..., 9.9]
val precise : range[f64] = 0.0..=1.0:0.01  // [0.0, 0.01, 0.02, ..., 1.00]

// Negative step for floats
val rev : range[f32] = 10.0..0.0:-0.5    // [10.0, 9.5, 9.0, ..., 0.5]
```

**Why step is required:**
- **Ambiguous iteration count:** How many elements in `0.0..1.0`? 10? 100? 1000?
- **Floating-point precision:** Accumulated errors from repeated addition
- **Transparent Costs:** Step makes iteration count visible

**Error message:**
```
Error: Float range requires explicit step
  val r : range[f32] = 0.0..10.0
                       ^^^^^^^^^^^
Help: Specify step size: 0.0..10.0:0.1
Note: Float ranges cannot have implicit step due to precision ambiguity
```

### Comptime Ranges

**Comptime int ranges (flexible!):**

```hexen
// Comptime range preserves flexibility
val flexible = 1..10                     // range[comptime_int]

// Adapts to context
val i32_slice : [_]i32 = arr[flexible]   // Adapts to i32 indices
val i64_slice : [_]i64 = arr_i64[flexible]  // Same range adapts to i64 indices

// Can materialize to different types
val as_i32 : [_]i32 = [flexible]         // [1, 2, ..., 9] as i32
val as_i64 : [_]i64 = [flexible]         // [1, 2, ..., 9] as i64
```

**Comptime float ranges (step required!):**

```hexen
// ❌ ERROR: Even comptime float ranges need step
val bad = 0.0..10.0                      // ❌ Comptime error: step required

// ✅ CORRECT: Explicit step
val good = 0.0..10.0:0.1                 // range[comptime_float]

// Adapts to context
val f32_arr : [_]f32 = [good]            // Adapts to f32
val f64_arr : [_]f64 = [good]            // Same range adapts to f64
```

## Range Operations

### Valid Operations by Range Type

| Operation | Bounded | From (`start..`) | To (`..end`) | Full (`..`) |
|-----------|---------|------------------|--------------|-------------|
| **Materialize to array** | ✅ Yes | ❌ No (infinite) | ❌ No (no start) | ❌ No (unbounded) |
| **Iterate** (future) | ✅ Yes | ✅ Yes (infinite) | ❌ No (no start) | ❌ No (no start) |
| **Slice array** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Get length** | ✅ Yes | ❌ No (infinite) | ❌ No (no start) | ❌ No (unbounded) |
| **Contains check** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes (always true) |
| **Index into range** | ✅ Yes | ✅ Yes | ❌ No (no start) | ❌ No (no start) |

### Materialization (Range → Array)

**Syntax:** `[range]`

```hexen
val r : range[i32] = 1..10
val arr : [_]i32 = [r]                   // Materialize to [9]i32 = [1, 2, ..., 9]

// Comptime error for unbounded ranges
val infinite : range[i32] = 5..
val bad : [_]i32 = [infinite]            // ❌ Error: cannot materialize unbounded range
```

**Error messages:**

```
Error: Cannot materialize unbounded range to array
  val arr : [_]i32 = [r]
                      ^
Help: Range 5.. has no end bound
Note: Only bounded ranges (start..end) can be converted to arrays
```

### Indexing (Future)

Ranges support O(1) indexing by computing the value at position:

```hexen
val r : range[i32] = 10..20:2            // [10, 12, 14, 16, 18]

val first : i32 = r[0]                   // 10 (start + 0 * step)
val second : i32 = r[1]                  // 12 (start + 1 * step)
val third : i32 = r[2]                   // 14 (start + 2 * step)
```

**Formula:** `value = start + (index * step)`

**Bounds checking:** Index must be within `[0, length)` where `length = (end - start) / step`

### Length (Future)

Bounded ranges have O(1) computed length:

```hexen
val r1 : range[i32] = 1..10              // Length: 9
val r2 : range[i32] = 1..10:2            // Length: 5 ([1, 3, 5, 7, 9])
val r3 : range[i32] = 1..=10:2           // Length: 5 ([1, 3, 5, 7, 9])

val len1 : i32 = r1.length()             // 9
val len2 : i32 = r2.length()             // 5
```

**Formula (exclusive):** `length = ceil((end - start) / step)`
**Formula (inclusive):** `length = floor((end - start) / step) + 1`

**Unbounded ranges:**
```hexen
val infinite : range[i32] = 5..
val len : i32 = infinite.length()        // ❌ Comptime error: unbounded range has no length
```

### Contains (Future)

O(1) membership test:

```hexen
val r : range[i32] = 10..20:2            // [10, 12, 14, 16, 18]

val has_12 : bool = r.contains(12)       // true
val has_13 : bool = r.contains(13)       // false (not on step boundary)
val has_20 : bool = r.contains(20)       // false (exclusive end)

// Unbounded ranges
val from : range[i32] = 5..
val has : bool = from.contains(100)      // true (all values >= 5)
```

**Algorithm:**
1. Check if value is within bounds
2. Check if `(value - start) % step == 0` (on step boundary)

## Array Slicing with Ranges

### The Unified `[..]` Operator

**Key Insight:** The `[..]` operator is actually `[range_full]` - slicing with the unbounded range `..`!

```hexen
val src : [_]i32 = [10, 20, 30, 40, 50]

// These are equivalent:
val copy1 : [_]i32 = src[..]             // Full-range slice
val copy2 : [_]i32 = src[0..5]           // Explicit bounded range

// Both create views, then materialize on assignment
```

### Slicing Creates Views (Zero-Cost)

```hexen
val src : [_]i32 = [10, 20, 30, 40, 50]

// Slicing creates ephemeral view (just metadata)
src[1..4]        // View { ptr: &src[1], length: 3 } - no allocation!
src[2..]         // View { ptr: &src[2], length: 3 }
src[..3]         // View { ptr: &src[0], length: 3 }
src[..]          // View { ptr: &src[0], length: 5 }
```

**View metadata:**
- Pointer to source array
- Start offset
- Length
- Stride (for stepped slices)

**Cost:** O(1) - just pointer arithmetic, no allocation or copying

### Assignment Materializes Views (Explicit Copy)

```hexen
val src : [_]i32 = [10, 20, 30, 40, 50]

// Assignment triggers materialization
val slice : [_]i32 = src[1..4]           // NOW it copies: [20, 30, 40]

// Why is this allowed without explicit copy syntax?
// Because src[1..4] is an OPERATION (slice extraction)
// The operation produces a new array (view → materialized)
// Assignment receives this new array (no double-copy!)
```

**Cost Transparency:**
- The cost is visible through **assignment to array type**
- `val x : [_]i32 = ...` signals "materializing an array"
- Slicing itself is free, assignment materializes

### Direct Array Assignment (Still Forbidden)

```hexen
val src : [_]i32 = [10, 20, 30]

// ❌ Direct assignment forbidden (ambiguous intent)
val copy : [_]i32 = src                  // ❌ Error: implicit array copy not allowed

// ✅ Must use full-range slice (explicit operation)
val copy : [_]i32 = src[..]              // ✅ OK: slice operation makes intent clear
```

**Rationale:**
- `src` alone is ambiguous (copy? alias? reference?)
- `src[..]` is unambiguous (slice all elements → new array)
- Maintains "Transparent Costs" principle

### Complete Slicing Syntax

```hexen
val src : [_]i32 = [10, 20, 30, 40, 50]
//       indices:  [0]  [1]  [2]  [3]  [4]

// ============================================
// BOUNDED RANGES
// ============================================

val s1 : [_]i32 = src[1..4]              // [20, 30, 40] - indices 1,2,3
val s2 : [_]i32 = src[1..=4]             // [20, 30, 40, 50] - indices 1,2,3,4
val s3 : [_]i32 = src[0..5]              // [10, 20, 30, 40, 50] - all elements
val s4 : [_]i32 = src[2..2]              // [] - empty slice

// ============================================
// UNBOUNDED RANGES
// ============================================

val s5 : [_]i32 = src[2..]               // [30, 40, 50] - from index 2 to end
val s6 : [_]i32 = src[..3]               // [10, 20, 30] - from start to index 2
val s7 : [_]i32 = src[..=3]              // [10, 20, 30, 40] - from start to index 3
val s8 : [_]i32 = src[..]                // [10, 20, 30, 40, 50] - full copy

// ============================================
// STEPPED SLICES
// ============================================

val s9 : [_]i32 = src[0..5:2]            // [10, 30, 50] - every 2nd element
val s10 : [_]i32 = src[1..:2]            // [20, 40] - from index 1, every 2nd
val s11 : [_]i32 = src[4..0:-1]          // [50, 40, 30, 20, 10] - reverse
val s12 : [_]i32 = src[4..=0:-1]         // [50, 40, 30, 20, 10] - reverse inclusive
```

### Out-of-Bounds Behavior

**Comptime checking (when possible):**

```hexen
val src : [5]i32 = [10, 20, 30, 40, 50]  // Fixed-size array

val bad : [_]i32 = src[10..]             // ❌ Comptime error: index 10 > length 5
val oob : [_]i32 = src[3..100]           // ❌ Comptime error: index 100 > length 5
```

**Runtime checking (dynamic arrays):**

```hexen
val dyn : [_]i32 = get_array()           // Unknown size at comptime

val slice : [_]i32 = dyn[10..]           // Runtime panic if 10 > length
val range : [_]i32 = dyn[5..100]         // Runtime panic if 100 > length
```

**Behavior:** Runtime panic with clear error message (Rust-style, not Python clamping)

**Error message:**
```
Runtime panic: Slice index out of bounds
  Array length: 5
  Attempted index: 10
  At: src[10..]
```

### Integer Index vs Range Slicing

**Single integer index:** Extracts element (1D) or row (2D+)

```hexen
// 1D array: element extraction (materializes element)
val arr : [_]i32 = [10, 20, 30, 40, 50]
val elem : i32 = arr[2]                  // 30 (copies i32 value)

// 2D array: row extraction (materializes row)
val matrix : [_][_]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
val row : [_]i32 = matrix[1]             // [4, 5, 6] (copies row array)
```

**Range index:** Extracts slice (creates view → materializes)

```hexen
// 1D array: sub-array extraction
val arr : [_]i32 = [10, 20, 30, 40, 50]
val slice : [_]i32 = arr[1..4]           // [20, 30, 40] (view → materialize)

// 2D array: multiple rows extraction
val matrix : [_][_]i32 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
val rows : [_][_]i32 = matrix[0..2]      // [[1,2,3], [4,5,6]] (view → materialize)
```

### Multidimensional Array Slicing

**Current (Zig-style sequential indexing):**

```hexen
val matrix : [_][_]i32 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]

// ✅ SUPPORTED: Sequential indexing

// Single index: extract row
val row : [_]i32 = matrix[1]             // [5, 6, 7, 8]

// Range on outer dimension: extract multiple rows
val rows : [_][_]i32 = matrix[1..3]      // [[5,6,7,8], [9,10,11,12]]

// Sequential: row then element
val elem : i32 = matrix[1][2]            // 7

// Sequential: row then slice
val row_slice : [_]i32 = matrix[1][2..4] // [7, 8]

// Full-range copy
val copy : [_][_]i32 = matrix[..]        // Full matrix copy
```

**Future (NumPy-style comma syntax):**

```hexen
// ❌ NOT YET SUPPORTED (future extension)

// Multi-dimensional range
// val sub : [_][_]i32 = matrix[1..3, 2..4]  // Rows 1-2, columns 2-3

// Column extraction
// val col : [_]i32 = matrix[.., 2]           // All rows, column 2

// Mixed single + range
// val row : [_]i32 = matrix[1, ..]           // Row 1, all columns
```

**Design rationale:**
- Start simple (Zig-style) for initial implementation
- Comma syntax is backward-compatible extension
- Most use cases covered by sequential indexing

### Iteration Over Views (Future)

**Zero-copy iteration:**

```hexen
val src : [_]i32 = [10, 20, 30, 40, 50]

// Iterate over view (no materialization!)
for elem in src[1..4] {                  // View only: { ptr: &src[1], length: 3 }
    print(elem)                          // Prints: 20, 30, 40
}

// No array allocated, no copy performed
// Loop iterates directly over source array elements
```

**Cost:** O(1) space (just view metadata), O(n) time (iteration)

## Float Range Restrictions

### Forbidden: Float Ranges for Slicing

Array indices must be integers. Float ranges cannot be used for array slicing:

```hexen
val arr : [_]i32 = [10, 20, 30, 40, 50]

// ❌ ERROR: Float range for slicing
val float_r : range[f32] = 1.5..3.7:0.1
val bad : [_]i32 = arr[float_r]          // ❌ Comptime error: array indices must be integers

// ✅ CORRECT: Integer range for slicing
val int_r : range[i32] = 1..4
val good : [_]i32 = arr[int_r]           // ✅ OK: [20, 30, 40]
```

**Error message:**
```
Error: Array slicing requires integer range, found range[f32]
  val slice : [_]i32 = arr[float_r]
                           ^^^^^^^^
Help: Array indices must be integers (i32 or i64), not floats
Note: Float ranges are only valid for iteration, not indexing
```

**Rationale:**
- Array indices are positions (discrete integers)
- Float indices have no meaningful interpretation
- No mainstream language allows float array indices

### Float Ranges for Iteration Only

Float ranges are designed for **iteration** (future), not **indexing**:

```hexen
// ✅ VALID: Float range for iteration (future)
for x in 0.0..10.0:0.1 {                 // 100 iterations: 0.0, 0.1, 0.2, ..., 9.9
    process(x)
}

// ❌ INVALID: Float range for array indexing
val arr : [_]i32 = [1, 2, 3, 4, 5]
val bad : [_]i32 = arr[0.0..5.0:0.5]     // ❌ Error: float indices forbidden
```

## Comptime Range Semantics

### Comptime Type Preservation

```hexen
// Comptime int range (flexible)
val flexible = 1..10                     // range[comptime_int]

// Adapts to different contexts
val i32_range : range[i32] = flexible    // → range[i32]
val i64_range : range[i64] = flexible    // → range[i64]

// Slicing adapts to array type
val i32_arr : [_]i32 = [10, 20, 30, 40, 50]
val i64_arr : [_]i64 = [10, 20, 30, 40, 50]

val slice1 : [_]i32 = i32_arr[flexible]  // Adapts to i32 indices
val slice2 : [_]i64 = i64_arr[flexible]  // Same range adapts to i64 indices
```

### Comptime Float Ranges

**Step still required:**

```hexen
// ❌ ERROR: Even comptime float ranges need step
val bad = 0.0..10.0                      // ❌ Error: float range requires step

// ✅ CORRECT: Comptime float range with step
val good = 0.0..10.0:0.1                 // range[comptime_float]

// Adapts to concrete float types
val f32_range : range[f32] = good        // → range[f32]
val f64_range : range[f64] = good        // → range[f64]
```

**Rationale:** Comptime flexibility doesn't bypass semantic constraints (step requirement).

### Comptime Validation

The semantic analyzer validates range operations at comptime when possible:

```hexen
// ✅ Comptime validation catches errors early
val r : range[i32] = 5..

val bad : [_]i32 = [r]                   // ❌ Comptime error: unbounded range

// Error caught during semantic analysis, not at runtime!
```

## Type Conversion Rules

### Explicit Type Conversions

**Concrete to concrete (requires `:type`):**

```hexen
val r_i32 : range[i32] = 1..10
val r_i64 : range[i64] = r_i32:range[i64]     // Explicit conversion

// Element-wise conversion happens during materialization
val arr : [_]i64 = [r_i32:range[i64]]         // [1i64, 2i64, ..., 9i64]
```

**Comptime to concrete (implicit):**

```hexen
val flexible = 1..10                     // range[comptime_int]
val concrete : range[i32] = flexible     // Implicit conversion (ergonomic!)
```

### Range Element Type Must Match Array

When slicing, range element type must be compatible with array index type:

```hexen
val arr : [_]i32 = [10, 20, 30, 40, 50]

// ✅ Compatible types
val r_i32 : range[i32] = 1..4
val slice1 : [_]i32 = arr[r_i32]         // ✅ OK: i32 indices

val r_comptime = 1..4                    // range[comptime_int]
val slice2 : [_]i32 = arr[r_comptime]    // ✅ OK: comptime adapts

// ❌ Incompatible types
val r_f32 : range[f32] = 1.0..4.0:0.1
val bad : [_]i32 = arr[r_f32]            // ❌ Error: float indices forbidden
```

## Examples

### Basic Range Usage

```hexen
// Integer ranges
val r1 : range[i32] = 1..10              // [1, 2, 3, 4, 5, 6, 7, 8, 9]
val r2 : range[i32] = 1..=10             // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
val r3 : range[i32] = 0..100:10          // [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

// Float ranges (step required!)
val r4 : range[f32] = 0.0..1.0:0.1       // [0.0, 0.1, 0.2, ..., 0.9]
val r5 : range[f64] = 0.0..=1.0:0.01     // [0.00, 0.01, 0.02, ..., 1.00]

// Unbounded ranges
val r6 : range[i32] = 5..                // [5, 6, 7, 8, ...] (infinite)
val r7 : range[i32] = ..10               // [?, ?, ..., 9] (for slicing only)
val r8 : range[i32] = ..                 // [?, ..., ?] (full range)

// Reverse ranges
val r9 : range[i32] = 10..0:-1           // [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
val r10 : range[f32] = 1.0..0.0:-0.1     // [1.0, 0.9, 0.8, ..., 0.1]
```

### Array Slicing Examples

```hexen
val arr : [_]i32 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

// Basic slicing
val s1 : [_]i32 = arr[2..5]              // [30, 40, 50]
val s2 : [_]i32 = arr[2..=5]             // [30, 40, 50, 60]

// Unbounded slicing
val s3 : [_]i32 = arr[5..]               // [60, 70, 80, 90, 100]
val s4 : [_]i32 = arr[..5]               // [10, 20, 30, 40, 50]
val s5 : [_]i32 = arr[..]                // [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

// Stepped slicing
val evens : [_]i32 = arr[0..:2]          // [10, 30, 50, 70, 90]
val odds : [_]i32 = arr[1..:2]           // [20, 40, 60, 80, 100]

// Reverse slicing
val rev : [_]i32 = arr[9..0:-1]          // [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
```

### Comptime Range Examples

```hexen
// Comptime range preserves flexibility
val flexible = 1..5                      // range[comptime_int]

// Use in different contexts
val i32_arr : [_]i32 = [10, 20, 30, 40, 50]
val i64_arr : [_]i64 = [10, 20, 30, 40, 50]

val slice1 : [_]i32 = i32_arr[flexible]  // Adapts to i32
val slice2 : [_]i64 = i64_arr[flexible]  // Adapts to i64

// Materialize to different types
val as_i32 : [_]i32 = [flexible]         // [1, 2, 3, 4] as i32
val as_i64 : [_]i64 = [flexible]         // [1, 2, 3, 4] as i64
```

### Future Iteration Examples

```hexen
// Integer range iteration
for i in 0..10 {                         // 10 iterations
    print(i)
}

// Float range iteration (step required!)
for x in 0.0..10.0:0.5 {                 // 20 iterations
    print(x)
}

// Unbounded range iteration
for i in 5.. {                           // Infinite loop!
    if i > 100 {
        break
    }
    print(i)
}

// Array slice iteration (zero-copy!)
val arr : [_]i32 = [10, 20, 30, 40, 50]
for elem in arr[1..4] {                  // No array allocation!
    print(elem)                          // Prints: 20, 30, 40
}
```

## Implementation Notes

### Internal View Representation

When slicing creates a view, the compiler internally uses:

```
ArrayView {
    source: *Array       // Pointer to source array
    offset: usize        // Start offset in elements
    length: usize        // Number of elements
    stride: isize        // Step (can be negative for reverse)
}
```

**Memory:** 4 pointer-sized values (32 bytes on 64-bit systems), regardless of view size.

### Materialization Process

When a view is assigned to an array variable:

1. **Allocate** new array with computed size
2. **Iterate** over view using `offset`, `length`, `stride`
3. **Copy** elements from source to destination
4. **Return** new array

**Complexity:**
- Time: O(n) where n = view length
- Space: O(n) for new array

### Comptime Range Tracking

The semantic analyzer tracks:

```python
@dataclass
class RangeType:
    element_type: str           # "i32", "f32", "comptime_int", etc.
    has_start: bool            # False for ..end and ..
    has_end: bool              # False for start.. and ..
    step: Optional[Expression] # None for integers (implicit 1), required for floats
    inclusive: bool            # False for .., true for ..=

    def is_bounded(self) -> bool:
        return self.has_start and self.has_end

    def can_materialize(self) -> bool:
        return self.is_bounded()

    def can_iterate(self) -> bool:
        return self.has_start

    def can_slice(self) -> bool:
        """Only integer-type ranges can be used for slicing."""
        return is_integer_type(self.element_type)

    def requires_step(self) -> bool:
        """Float ranges require explicit step."""
        return is_float_type(self.element_type)
```

## Design Rationale

### Why Lazy Ranges?

**Memory efficiency:**
```hexen
val small = 1..10                        // 32 bytes (view metadata)
val huge = 1..1_000_000_000              // 32 bytes (same metadata!)

val small_arr : [_]i32 = [small]         // 36 bytes (9 elements * 4 bytes)
val huge_arr : [_]i32 = [huge]           // 4GB (1 billion elements * 4 bytes)
```

Ranges enable working with large sequences without memory overhead until materialization.

### Why Require Step for Floats?

**Precision issues:**
```python
# Python example showing float iteration problem
for i, x in enumerate(np.arange(0.0, 1.0, 0.1)):
    print(f"{i}: {x}")

# Output:
# 0: 0.0
# 1: 0.1
# 2: 0.2
# ...
# 9: 0.9
# 10: 1.0  ← Unexpected! Should stop before 1.0

# Accumulated error: 0.1 * 10 = 0.9999999999999999 ≈ 1.0
```

**Ambiguity:**
- How many elements in `0.0..1.0`? 10? 100? 1000?
- Implicit step leads to surprising behavior

**Solution:** Require explicit step to make iteration count visible (Transparent Costs).

### Why Views Over Separate Slice Type?

**Rust/Zig approach:** Separate slice type (`&[T]`, `[]T`)
**Hexen approach:** Ephemeral views (compiler internal)

**Rationale:**
- Simpler user-facing model (no second "array-like" type to learn)
- Cost transparency through assignment (not through type system)
- Consistent with "single array type" philosophy
- Views are implementation detail, not language concept

### Why Forbid Direct Array Assignment?

```hexen
val src : [_]i32 = [10, 20, 30]

val copy : [_]i32 = src                  // ❌ Forbidden
val copy : [_]i32 = src[..]              // ✅ Required
```

**Rationale:**
- `src` is ambiguous (copy? alias? reference?)
- `src[..]` is explicit (slice operation, clear intent)
- Maintains consistency with "operations make costs visible"
- Prevents accidental expensive copies

## Future Extensions

### Iteration Protocol (Planned)

```hexen
// Future: for loops consume ranges
for i in 1..10 {
    print(i)
}

// Range-based algorithms
val sum : i32 = (1..100).sum()           // Sum of 1 to 99
val filtered : [_]i32 = [(1..100).filter(|x| x % 2 == 0)]  // Evens
```

### Multi-Dimensional Slicing (Future)

```hexen
// Future: NumPy-style comma syntax
val matrix : [_][_]i32 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]

val sub : [_][_]i32 = matrix[1..3, 2..4]     // Rows 1-2, cols 2-3
val col : [_]i32 = matrix[.., 2]             // All rows, column 2
val row : [_]i32 = matrix[1, ..]             // Row 1, all columns
```

### Range Methods (Future)

```hexen
// Future: methods on range type
val r : range[i32] = 1..10

val len : i32 = r.length()               // 9
val has : bool = r.contains(5)           // true
val elem : i32 = r[3]                    // 4
val rev : range[i32] = r.reverse()       // 9..0:-1
val stepped : range[i32] = r.step(2)     // 1..10:2
```

## Summary

**Range as First-Class Type:**
- Single `range[T]` type for all use cases
- Lazy sequences (O(1) space)
- Comptime-aware (adapts to context)

**Integer vs Float Ranges:**
- Integers: step optional (default 1)
- Floats: step required (transparent iteration count)

**Bounded vs Unbounded:**
- Bounded: Can materialize, iterate, slice
- From: Can iterate (infinite), slice
- To/Full: Can slice only

**View Model:**
- Slicing creates views (zero-cost)
- Assignment materializes (explicit copy)
- Cost visible through array type assignment

**Array Slicing:**
- Unified `[..]` operator (full range)
- All slice operations return views
- Integer ranges only (no float indices)
- Zig-style sequential indexing (now)
- NumPy-style comma syntax (future)

**Key Principles:**
- Ergonomic Literals: Comptime ranges adapt
- Transparent Costs: Assignment signals materialization
- Lazy by Default: Views until materialization needed
- Explicit Operations: Costs visible through syntax
