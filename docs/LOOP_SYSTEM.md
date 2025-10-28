# Hexen Loop System 🦉

*Complete Specification*

> **Design Note**: This document describes Hexen's loop system, which provides both traditional iteration (for-in, while) and powerful loop expressions that generate arrays. Loops follow Hexen's core philosophy of "Ergonomic Literals + Transparent Costs" by enabling type inference for loop variables while making array generation costs explicit through type annotations.

## Overview

Hexen's loop system provides **two fundamental loop constructs**:

1. **For-in loops** - Iterate over ranges and array slices
2. **While loops** - Conditional iteration

Both support:
- **Statement mode** - Execute code without producing values
- **Expression mode** (for-in only) - Generate arrays of values

Loops integrate seamlessly with Hexen's **range system** for zero-cost iteration over array views and bounded/unbounded sequences.

## Core Philosophy

### Loops as Array Generators

```hexen
// Conditional → single value
val x : i32 = if condition { -> 1 } else { -> 2 }

// For-in loop → array of values
val xs : [_]i32 = for i in 1..10 { -> i * i }
```

**Key Principle:** Just as conditionals produce single values with `->`, for-in loops produce arrays of values with `->`.

### Statement vs Expression Detection

```hexen
// VALUE CONTEXT → Expression mode
val result : [_]i32 = for i in 1..10 { -> i }    // Expression
return for i in 1..10 { -> i }                   // Expression
process(for i in 1..10 { -> i })                 // Expression

// STANDALONE → Statement mode
for i in 1..10 {                                 // Statement
    print(i)
}
```

**Key Principle:** Context determines mode. Type annotation makes array generation cost visible.

### Safety: Preventing Infinite Materialization

```hexen
// ✅ Bounded range in expression context (safe)
val bounded : [_]i32 = for i in 1..100 { -> i }

// ❌ Unbounded range in expression context (error!)
val infinite : [_]i32 = for i in 5.. { -> i }   // Comptime error

// ✅ Unbounded range in statement context (safe)
for i in 5.. {                                   // Infinite loop (must break)
    if i > 100 { break }
    process(i)
}
```

**Key Principle:** Unbounded ranges cannot produce arrays (infinite materialization risk). Statement mode allows controlled infinite loops with explicit `break`.

## For-In Loops

### Syntax

```hexen
for variable in iterable {
    // body
}

// With optional explicit type annotation
for variable : type in iterable {
    // body
}
```

**Syntax rules:**
- **No parentheses** around iterable (consistent with conditionals)
- **Braces required** (no single-statement bodies)
- **Type annotation optional** (inferred from iterable)

### Loop Variable Type Inference

Loop variables automatically infer their type from the iterable:

| Iterable Type | Loop Variable Type | Example |
|---------------|-------------------|---------|
| **Comptime range** | `comptime_int` or `comptime_float` | `for i in 1..10 { }` → i is comptime_int |
| **Concrete range** | Matches range element type | `for i in range[i32] { }` → i is i32 |
| **Array slice** | Matches array element type | `for x in [_]f64[..] { }` → x is f64 |
| **Explicit type** | User-specified | `for i : i64 in 1..10 { }` → i is i64 |

#### Type Inference Examples

```hexen
// Comptime range (adapts to context)
for i in 1..10 {
    print(i)                        // i is comptime_int
}

// Concrete range (inferred from range type)
val r : range[i32] = 1..100
for i in r {
    print(i)                        // i is i32 (inferred from range[i32])
}

// Array iteration (inferred from element type)
val data : [_]f64 = [1.0, 2.0, 3.0]
for x in data[..] {
    print(x)                        // x is f64 (inferred from [_]f64)
}

// Explicit type annotation (always allowed)
for i : i64 in 1..10 {
    print(i)                        // i is i64 (explicit)
}

// Comptime range with explicit type
for i : i32 in 1..10 {
    print(i)                        // i is i32 (comptime_int adapts)
}
```

### Loop Variable Mutability

**Rule:** Loop variables are **always immutable**.

```hexen
for i in 1..10 {
    // i = 42                       // ❌ Error: loop variables are immutable
    val computed = i * 2            // ✅ Can read i

    mut local : i32 = i             // ✅ Can create mutable local if needed
    local = local * 2
}
```

**Rationale:**
- Prevents accidental mutation of iteration state
- Consistent with functional programming principles
- Users can create mutable locals when needed

### Range Iteration

#### Bounded Ranges (Finite Iteration)

```hexen
// Exclusive end
for i in 1..10 {
    print(i)                        // Prints: 1, 2, 3, ..., 9
}

// Inclusive end
for i in 1..=10 {
    print(i)                        // Prints: 1, 2, 3, ..., 10
}

// With step
for i in 0..100:10 {
    print(i)                        // Prints: 0, 10, 20, ..., 90
}

// Reverse iteration
for i in 10..0:-1 {
    print(i)                        // Prints: 10, 9, 8, ..., 1
}

// Float ranges (step required!)
for x in 0.0..10.0:0.5 {
    print(x)                        // Prints: 0.0, 0.5, 1.0, ..., 9.5
}
```

#### Unbounded Ranges (Infinite Iteration)

**Only `start..` can iterate** (infinite loop):

```hexen
// Unbounded FROM (infinite loop - must break!)
for i in 5.. {                      // [5, 6, 7, 8, ...]
    if i > 100 {
        break                       // Must explicitly break
    }
    process(i)
}

// Unbounded TO (no start point - error!)
for i in ..10 {                     // ❌ Comptime error: cannot iterate
    print(i)
}

// Full unbounded (no start or end - error!)
for i in .. {                       // ❌ Comptime error: cannot iterate
    print(i)
}
```

**Error messages:**

```
Error: Cannot iterate over range with no start point
  for i in ..10 {
           ^^^^
Help: Range ..10 has no defined start value
Note: Only ranges with start point (start..end, start..) can be iterated

Error: Cannot iterate over unbounded range
  for i in .. {
           ^^
Help: Range .. has no start or end bounds
Note: Use bounded range (start..end) or from-range (start..) for iteration
```

**Range iteration summary:**

| Range Type | Can Iterate? | Behavior | Example |
|------------|--------------|----------|---------|
| `start..end` | ✅ Yes | Bounded (finite) | `for i in 1..10 { }` |
| `start..=end` | ✅ Yes | Inclusive bounded | `for i in 1..=10 { }` |
| `start..` | ✅ Yes | **Infinite** (must break) | `for i in 5.. { if i > 100 { break } }` |
| `..end` | ❌ No | Error (no start) | `for i in ..10 { }` ❌ |
| `..` | ❌ No | Error (no bounds) | `for i in .. { }` ❌ |

### Array Iteration

**Arrays are iterated via range slicing syntax:**

```hexen
val data : [_]i32 = [10, 20, 30, 40, 50]

// Full array iteration (unbounded range)
for elem in data[..] {              // View: {ptr: &data[0], length: 5}
    print(elem)                     // Prints: 10, 20, 30, 40, 50
}

// Partial array iteration (bounded range)
for elem in data[2..5] {            // View: {ptr: &data[2], length: 3}
    print(elem)                     // Prints: 30, 40, 50
}

// Stepped iteration (every 2nd element)
for elem in data[0..:2] {           // View with stride: {stride: 2}
    print(elem)                     // Prints: 10, 30, 50
}

// Reverse iteration
for elem in data[4..0:-1] {         // View with negative stride
    print(elem)                     // Prints: 50, 40, 30, 20, 10
}
```

**Key principle:** `array[range]` creates **zero-cost views** (no materialization), and iteration happens directly over the view.

**View metadata (compiler internal):**
```
ArrayView {
    source: *Array       // Pointer to source array
    offset: usize        // Start offset in elements
    length: usize        // Number of elements
    stride: isize        // Step (can be negative for reverse)
}
```

**Cost:** O(1) space (view metadata), O(n) time (iteration)

### For-In Statement Mode

When a for-in loop appears standalone (not in value context), it operates in **statement mode**:

```hexen
// Statement mode: no value production
for i in 1..10 {
    print(i)                        // No -> needed
    process(i)
}

// Statement with break
for i in 1..100 {
    if i > 50 {
        break                       // Exit loop
    }
    print(i)
}

// Statement with continue
for i in 1..10 {
    if i % 2 == 0 {
        continue                    // Skip evens
    }
    print(i)                        // Only prints odds
}
```

**Characteristics:**
- No `->` required (or allowed without value context)
- No array generation
- Can use `break`, `continue`, `return`

### For-In Expression Mode

When a for-in loop appears in **value context** (assigned to variable, function return, function argument), it operates in **expression mode** and generates an array:

```hexen
// Expression mode: produces array
val squares : [_]i32 = for i in 1..10 {
    -> i * i                        // Must -> values
}
// Result: [1, 4, 9, 16, 25, 36, 49, 64, 81]

// Function return context
func get_evens() : [_]i32 = {
    return for i in 1..10 {
        if i % 2 == 0 {
            -> i
        }
    }
}
// Returns: [2, 4, 6, 8]

// Function argument context
func process(data : [_]i32) : i32 = { return 0 }
val result : i32 = process(for i in 1..5 { -> i })
// Passes: [1, 2, 3, 4]
```

**Type annotation requirement:**

```hexen
// ✅ Type annotation required (loop expression is runtime operation)
val result : [_]i32 = for i in 1..10 {
    -> i * i
}

// ❌ Missing type annotation (error)
val bad = for i in 1..10 { -> i }  // ❌ Error: loop expression requires type

// Rationale: Consistent with conditionals and function calls
val x : i32 = if cond { -> 1 } else { -> 2 }     // Type required
val y : i32 = get_value()                        // Type required
val z : [_]i32 = for i in 1..10 { -> i }         // Type required
```

**Error message:**

```
Error: Loop expression requires explicit type annotation
  val result = for i in 1..10 { -> i }
               ^^^^^^^^^^^^^^^^^^^^^^^^
Help: Add type annotation: val result : [_]i32 = for ...
Note: Loop expressions are runtime operations and require explicit types
      (consistent with conditionals and function calls)
```

#### Filtering (Skip Iterations Without `->`)

When an iteration doesn't execute a `->` statement, **no value is produced** for that iteration (filter behavior):

```hexen
// Only produce values for even numbers
val evens : [_]i32 = for i in 1..10 {
    if i % 2 == 0 {
        -> i                        // Produce value for evens
    }
    // Odd numbers: no -> executed → skip
}
// Result: [2, 4, 6, 8] (length = 4, not 9!)

// Complex filtering with multiple conditions
val filtered : [_]i32 = for i in 1..100 {
    if i % 3 == 0 {
        continue                    // Skip multiples of 3
    }
    if i % 5 == 0 {
        -> i * 2                    // Double multiples of 5
    } else {
        -> i                        // Keep others
    }
}
// Skips: 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, ...
// Doubles: 5 → 10, 10 → 20, 20 → 40, 25 → 50, ...
// Keeps: 1, 2, 4, 7, 8, 11, 13, 14, ...
```

**Key insight:** Filtering is built-in. Iterations without `->` are simply skipped (not added to result array).

#### Early Termination With `break`

`break` in a loop expression **stops iteration and returns the partial array** built so far:

```hexen
// Collect until condition met
val partial : [_]i32 = for i in 1..100 {
    if i > 10 {
        break                       // Stop here, return [1..10]
    }
    -> i
}
// Result: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Find all elements until target
val until_target : [_]i32 = for i in 1..1000 {
    if i * i > 500 {
        break                       // Stop when square exceeds 500
    }
    -> i * i
}
// Result: [1, 4, 9, 16, 25, ..., 484] (stops at 22*22=484)

// Combine break with filtering
val complex : [_]i32 = for i in 1..100 {
    if i > 50 {
        break                       // Stop at 50
    }
    if i % 2 == 0 {
        -> i                        // Only collect evens
    }
}
// Result: [2, 4, 6, 8, ..., 48, 50]
```

**Key insight:** `break` returns the **partial array** built up to that point (not an error).

#### Skip Iterations With `continue`

`continue` in a loop expression **skips to the next iteration without producing a value**:

```hexen
// Skip odd numbers using continue
val evens : [_]i32 = for i in 1..10 {
    if i % 2 != 0 {
        continue                    // Skip odd (no value produced)
    }
    -> i
}
// Result: [2, 4, 6, 8]

// Continue vs no-op (equivalent)
val same : [_]i32 = for i in 1..10 {
    if i % 2 == 0 {
        -> i                        // Produce evens
    }
    // Implicitly skip odds (same as continue)
}
// Result: [2, 4, 6, 8] (identical to above)

// Continue after processing
val processed : [_]i32 = for i in 1..20 {
    if i % 3 == 0 {
        continue                    // Skip multiples of 3
    }
    if i % 5 == 0 {
        -> i * 10                   // Multiply by 10
    } else {
        -> i                        // Keep as-is
    }
}
// Skips: 3, 6, 9, 12, 15, 18
// Multiplies: 5 → 50, 10 → 100
// Keeps: 1, 2, 4, 7, 8, 11, 13, 14, 16, 17, 19
```

**Key insight:** `continue` is equivalent to reaching end of iteration without executing `->`  (both skip the value).

#### Safety: Unbounded Ranges Forbidden in Expression Mode

**Comptime error** if unbounded range used in expression context:

```hexen
// ❌ Unbounded range in expression context (error!)
val infinite : [_]i32 = for i in 5.. {
    if i > 100 { break }
    -> i
}
// ❌ Comptime error: unbounded loop cannot produce array

// ✅ Unbounded range in statement context (OK)
for i in 5.. {
    if i > 100 { break }            // Explicit break required
    process(i)
}

// ✅ Bounded range in expression context (OK)
val bounded : [_]i32 = for i in 5..101 {
    -> i
}
// ✅ Safe: bounded range → finite array
```

**Error message:**

```
Error: Unbounded loop cannot produce array
  val result : [_]i32 = for i in 5.. { -> i }
                                 ^^^
Help: Use bounded range: for i in 5..end { }
Note: Unbounded ranges (start..) can iterate infinitely but cannot
      materialize to arrays (infinite allocation risk)
```

**Rationale:**
- Prevents accidental infinite array allocation
- Forces explicit bounds for array generation
- Unbounded ranges still allowed in statement mode (controlled infinite loops)

## While Loops

### Syntax

```hexen
while condition {
    // body
}
```

**Syntax rules:**
- **No parentheses** around condition (consistent with conditionals)
- **Braces required** (no single-statement bodies)
- **Condition must be `bool` type** (no implicit conversions)

### Condition Type Requirements

**Rule:** While loop conditions must be `bool` type.

```hexen
mut count : i32 = 0

// ✅ Explicit boolean condition
while count < 10 {
    count = count + 1
}

// ❌ Non-bool condition (error)
// while count {                    // ❌ Error: i32 cannot be used as bool
//     count = count - 1
// }

// ✅ Explicit comparison produces bool
while count > 0 {
    count = count - 1
}
```

**Error message:**

```
Error: While condition must be of type bool, got i32
  while count {
        ^^^^^
Help: Use explicit comparison: while count > 0 {
Note: Hexen does not allow implicit conversion of numeric types to bool
```

**Rationale:** Consistent with conditional expressions (`if` also requires `bool`).

### Infinite Loops

**Use `while true` for explicit infinite loops:**

```hexen
// Infinite loop (must break explicitly)
while true {
    val input = get_user_input()
    if input == "quit" {
        break                       // Exit loop
    }
    process(input)
}

// Infinite loop with continue
while true {
    val data = fetch_data()
    if data.is_empty() {
        continue                    // Skip this iteration
    }
    process(data)
}
```

**Alternative considered:** Dedicated `loop` keyword (like Rust):

```hexen
// NOT SUPPORTED (for now)
// loop {                          // Dedicated infinite loop construct
//     if should_exit() { break }
//     do_work()
// }
```

**Decision:** Use `while true` (simpler, one less keyword). Can add `loop` later if needed.

### While Loops Are Always Statements

**Rule:** While loops **cannot produce values** (statement mode only).

```hexen
// ✅ While statement (no value production)
while condition {
    do_work()                       // Statement mode
}

// ❌ While expression (error!)
val result : [_]i32 = while condition {  // ❌ Error: while cannot produce array
    -> value
}
```

**Error message:**

```
Error: While loops cannot be used in expression context
  val result : [_]i32 = while condition { -> value }
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Help: Use for-in loop for array generation: for i in range { -> value }
Note: While loops are statements only (cannot produce values)
      Rationale: Unbounded iteration risk (no comptime-checkable bounds)
```

**Rationale:**
- While loops have no bounded iteration guarantee (infinite risk)
- For-in loops with bounded ranges are safe for array generation
- Prevents accidental infinite materialization

### Do-While Loops

**Not supported** in initial version.

**Workaround** (if needed):

```hexen
// Emulate do-while with while + flag
mut first : bool = true
while first || condition {
    first = false
    process()                       // Executes at least once
}
```

**Rationale:** Most use cases covered by regular `while`. Can add `do-while` later if demand arises.

## Loop Control Flow

### Break Statement

**Exits the innermost loop immediately:**

```hexen
// Exit for-in loop
for i in 1..100 {
    if i > 50 {
        break                       // Exit loop at i=51
    }
    print(i)
}
// Prints: 1, 2, 3, ..., 50

// Exit while loop
mut count : i32 = 0
while true {
    if count > 10 {
        break                       // Exit infinite loop
    }
    count = count + 1
}
```

**In loop expressions** (returns partial array):

```hexen
val partial : [_]i32 = for i in 1..100 {
    if i > 10 {
        break                       // Returns [1, 2, ..., 10]
    }
    -> i
}
```

### Continue Statement

**Skips to next iteration of innermost loop:**

```hexen
// Skip even numbers
for i in 1..10 {
    if i % 2 == 0 {
        continue                    // Skip to next iteration
    }
    print(i)                        // Only prints odds: 1, 3, 5, 7, 9
}

// Continue in while loop
mut count : i32 = 0
while count < 10 {
    count = count + 1
    if count % 3 == 0 {
        continue                    // Skip multiples of 3
    }
    print(count)                    // Prints: 1, 2, 4, 5, 7, 8, 10
}
```

**In loop expressions** (skips value production):

```hexen
val filtered : [_]i32 = for i in 1..10 {
    if i % 2 == 0 {
        continue                    // Skip evens (no value produced)
    }
    -> i
}
// Result: [1, 3, 5, 7, 9]
```

### Return Statement

**Exits containing function** (not just the loop):

```hexen
func find_first_positive(data : [_]i32) : i32 = {
    for elem in data[..] {
        if elem > 0 {
            return elem             // Exit function (not just loop)
        }
    }
    return -1                       // Not found
}
```

**Difference from `break`:**

| Statement | Scope | Effect |
|-----------|-------|--------|
| `break` | Current loop | Exit loop, continue function |
| `return` | Containing function | Exit function immediately |

```hexen
func example() : i32 = {
    for i in 1..10 {
        if i == 3 {
            break                   // Exit loop, continue to line after loop
        }
        if i == 5 {
            return i                // Exit function immediately
        }
    }
    print("After loop")             // Executes after break, not after return
    return 0
}
```

### Error Cases (Break/Continue/Return)

```hexen
// ❌ Break outside loop
val x : i32 = if condition {
    break                           // ❌ Error: break outside loop
} else {
    -> 42
}

// ❌ Continue outside loop
val y : i32 = {
    continue                        // ❌ Error: continue outside loop
}

// ✅ Return outside loop (valid - exits function)
val z : i32 = if condition {
    return -1                       // ✅ OK: early function exit
} else {
    -> 42
}
```

**Error messages:**

```
Error: break statement outside loop
  break
  ^^^^^
Note: break can only be used inside for-in or while loops

Error: continue statement outside loop
  continue
  ^^^^^^^^
Note: continue can only be used inside for-in or while loops
```

## Loop Labels

### Label Syntax

**Labels use simple identifier syntax** (no special prefix):

```hexen
// Label before loop
outer: for i in 1..10 {
    inner: for j in 1..10 {
        if i * j > 50 {
            break outer             // Break outer loop
        }
        print(i, j)
    }
}
```

**Syntax rules:**
- Labels are identifiers followed by `:`
- Labels must immediately precede a loop (`for` or `while`)
- Labels can be referenced by `break` or `continue` statements

### Label Scope (Cross Loop Types)

**Labels work across all loop types** (for-in and while):

```hexen
// Break while from inside for-in
outer: while condition {
    inner: for i in 1..10 {
        if i > 5 {
            break outer             // ✅ Break the outer while loop
        }
    }
}

// Break for-in from inside while
outer: for i in 1..10 {
    inner: while condition {
        if should_exit {
            break outer             // ✅ Break the outer for loop
        }
    }
}

// Continue outer loop from nested loop
outer: for i in 1..10 {
    inner: for j in 1..10 {
        if j > 5 {
            continue outer          // ✅ Continue outer for loop
        }
        print(i, j)
    }
}
```

**Rationale:** Labels identify loops (not loop types), enabling flexible control flow across any loop combination.

### Break/Continue With Labels

```hexen
// Break outer loop
outer: for i in 1..10 {
    inner: for j in 1..10 {
        if i * j > 50 {
            break outer             // Exit outer loop
        }
        print(i, j)
    }
    print("After inner")            // Never executes after break outer
}
print("After outer")                // Executes after break outer

// Continue outer loop
outer: for i in 1..10 {
    inner: for j in 1..10 {
        if j > 5 {
            continue outer          // Skip to next i
        }
        print(i, j)
    }
    print("After inner")            // Never executes after continue outer
}
```

### Labels on Loop Expressions

**Labels work with loop expressions** that produce arrays:

```hexen
// Label on outer statement loop
outer: for i in 1..10 {
    // Label on inner expression loop
    val inner_data : [_]i32 = inner: for j in 1..10 {
        if i * j > 50 {
            break outer             // ✅ Break outer loop, stop all
        }
        -> j
    }
    process(inner_data)
}

// Label on expression loop with early termination
val result : [_]i32 = labeled: for i in 1..100 {
    if i > 50 {
        break labeled               // ✅ Early termination (returns partial array)
    }
    -> i * i
}
// Result: [1, 4, 9, ..., 2500]
```

**Note:** Labels on expression loops enable control flow from nested loops.

### Three-Level Nesting Example

```hexen
// Complex nested loop with labels
outer: for i in 1..10 {
    middle: for j in 1..10 {
        inner: for k in 1..10 {
            if i + j + k > 20 {
                break outer         // Exit all loops
            }
            if j * k > 25 {
                continue middle     // Skip to next j
            }
            if k > 5 {
                continue inner      // Skip to next k (same as continue)
            }
            print(i, j, k)
        }
    }
}
```

### Error Cases (Labels)

```hexen
// ❌ Label not defined
for i in 1..10 {
    if i > 5 {
        break nonexistent           // ❌ Error: label 'nonexistent' not found
    }
}

// ❌ Label on non-loop construct
mylabel: val x : i32 = 42           // ❌ Error: labels only on loops
for i in 1..10 {
    break mylabel
}

// ❌ Label shadowing (same label on nested loops)
outer: for i in 1..10 {
    outer: for j in 1..10 {         // ❌ Error: label 'outer' already defined
        break outer
    }
}

// ✅ Reusing label in sibling loops (OK - different scopes)
outer: for i in 1..10 {
    // First use of 'outer'
}
outer: for i in 1..10 {             // ✅ OK: previous label out of scope
    // Second use of 'outer'
}
```

**Error messages:**

```
Error: Label 'nonexistent' not found
  break nonexistent
        ^^^^^^^^^^^
Note: Labels must be defined on enclosing loops

Error: Labels can only be applied to loops
  mylabel: val x : i32 = 42
  ^^^^^^^^
Help: Remove label or apply to for-in/while loop

Error: Label 'outer' already defined in this scope
  outer: for j in 1..10 {
  ^^^^^
Note: Previous definition:
      outer: for i in 1..10 {
      ^^^^^
Help: Use different label name for inner loop
```

## Type System Integration

### Loop Variable Type Inference

Loop variables infer types from iterables (consistent with Hexen's philosophy):

```hexen
// Comptime range → comptime_int (adapts to context)
for i in 1..10 {
    val squared : i32 = i * i       // i adapts to i32 context
}

// Concrete range → concrete type (inferred)
val r : range[i64] = 1..100
for i in r {
    print(i)                        // i is i64 (inferred from range[i64])
}

// Array slice → element type (inferred)
val data : [_]f64 = [1.0, 2.0, 3.0]
for x in data[..] {
    print(x)                        // x is f64 (inferred from [_]f64)
}

// Explicit type annotation (override inference)
for i : i32 in 1..10 {
    print(i)                        // i is i32 (explicit)
}
```

### Comptime Type Preservation in Loops

**Comptime types are preserved in loop bodies:**

```hexen
// Loop variable is comptime_int
for i in 1..10 {
    val x = i * 2                   // x is comptime_int (preserved!)
    val y : i32 = i * 2             // y is i32 (explicit type)
    val z : i64 = i * 2             // z is i64 (explicit type)
}
```

**Key insight:** Comptime types flow through loops just like other expressions (Ergonomic Literals principle).

### Array Size Inference

Loop expressions produce arrays with **inferred size** (`[_]T` notation):

```hexen
// Size inferred from loop (bounded range)
val squares : [_]i32 = for i in 1..10 {
    -> i * i
}
// Type: [9]i32 (9 elements: 1, 4, 9, ..., 81)

// Size inferred from filtering (runtime determined)
val evens : [_]i32 = for i in 1..10 {
    if i % 2 == 0 {
        -> i
    }
}
// Type: [_]i32 (size determined at runtime: 4 elements)

// Size inferred from early break (runtime determined)
val partial : [_]i32 = for i in 1..100 {
    if i > 50 {
        break
    }
    -> i
}
// Type: [_]i32 (size determined at runtime: 50 elements)
```

**Key principle:** Array size is inferred (using `[_]T` notation) because loop expressions can filter or break early.

## Nested Loop Expressions (Multidimensional Arrays)

### Overview

Nested loop expressions enable **matrix and tensor generation** by producing arrays of arrays. The outer loop generates rows (or higher-dimensional slices), while inner loops generate elements.

**Key principles:**
- **Type context flows inward** - Outer type annotation provides context to nested loops
- **All syntax variants supported** - Intermediate variables, direct nesting, or compact form
- **Uniform dimensions enforced** - All rows must have same length (runtime validation)
- **Empty rows skipped** - Filtering produces uniform results
- **Arbitrary nesting** - No depth limits (2D, 3D, 4D, ...)

### Syntax Variants (All Supported)

All three syntax styles are supported for nested loop expressions:

```hexen
// Option A: Explicit intermediate variable
val matrix_a : [_][_]i32 = for i in 1..3 {
    val row : [_]i32 = for j in 1..4 {
        -> i * j
    }
    -> row
}

// Option B: Direct nesting (no intermediate)
val matrix_b : [_][_]i32 = for i in 1..3 {
    -> for j in 1..4 {
        -> i * j
    }
}

// Option C: Compact single-line
val matrix_c : [_][_]i32 = for i in 1..3 { -> for j in 1..4 { -> i * j } }

// All three produce identical results:
// [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

**Programmer's choice:** Use the style that best fits the situation (clarity vs. brevity).

### Type Context Flow

Type annotations provide context that flows inward through nesting levels:

```hexen
// Type flows inward
val matrix : [_][_]i32 = for i in 1..3 {
//           ^^^^^^^^^^
//           Outer context: produce [_]i32 elements (rows)

    -> for j in 1..4 {
//     ^^^^^^^^^^^^
//     Inner context: produce i32 elements (from [_]i32)

        -> i * j
//         ^^^^^
//         Must be i32 (from context)
    }
}
```

**Type context resolution table:**

| Nesting Level | Array Type | Loop Context | Element Type Produced |
|---------------|------------|--------------|----------------------|
| Outer (1D) | `[_][_]i32` | Outer for | `[_]i32` (rows) |
| Inner (2D) | `[_]i32` | Inner for | `i32` (elements) |

**Three-dimensional example:**

```hexen
val tensor : [_][_][_]i32 = for i in 1..2 {
//           ^^^^^^^^^^^^
//           Outer: produces [_][_]i32 (matrices)

    -> for j in 1..3 {
//     ^^^^^^^^^^^^
//     Middle: produces [_]i32 (rows)

        -> for k in 1..4 {
//         ^^^^^^^^^^^^
//         Inner: produces i32 (elements)

            -> i * j * k
        }
    }
}
// Type: [2][3][4]i32 (2 matrices, each 3x4)
```

### Runtime Uniform Dimension Validation

**Critical rule:** All rows (inner arrays) at the same nesting level **must have the same length**. This is enforced at runtime (like array bounds checking).

```hexen
// ✅ Uniform dimensions (all rows length 3)
val uniform : [_][_]i32 = for i in 1..3 {
    -> for j in 1..4 {
        -> i * j
    }
}
// Result: [[1,2,3], [2,4,6], [3,6,9]] ✅ All rows length 3

// ❌ Non-uniform dimensions (runtime panic!)
val ragged : [_][_]i32 = for i in 1..4 {
    -> for j in 1..10 {
        if j % i == 0 {
            -> j                    // Different lengths per row!
        }
    }
}
// Row 0: [1,2,3,4,5,6,7,8,9,10] (length 10)
// Row 1: [2,4,6,8,10]           (length 5)  ← DIFFERENT LENGTH!
// Runtime panic: Non-uniform array dimensions
```

**Runtime panic message:**

```
Runtime panic: Non-uniform array dimensions in nested loop expression
  val matrix : [_][_]i32 = for i in 1..4 { -> for j in ... }
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Expected all rows to have same length
  Row 0 length: 10
  Row 1 length: 5

  Location: for i in 1..4 (iteration i=2)

Help: Ensure all inner loop expressions produce same number of elements
Note: Use break in all iterations at same point, or filter outer loop
```

**Why runtime validation?**
- Inner loop length often depends on runtime values (filtering, break conditions)
- Consistent with array bounds checking (also runtime)
- Comptime checking when possible (bounded ranges without filtering/break)

**Comptime validation (when possible):**

```hexen
// Comptime validation (no filtering, no break, bounded ranges)
val static_matrix : [_][_]i32 = for i in 1..3 {
    -> for j in 1..4 {              // Always produces 4 elements
        -> i * j
    }
}
// ✅ Comptime verified: all rows length 4 (type: [3][4]i32)

// Runtime validation (filtering present)
val filtered : [_][_]i32 = for i in 1..3 {
    -> for j in 1..10 {
        if j % 2 == 0 {
            -> j                    // Runtime-dependent length
        }
    }
}
// All rows produce same elements (2,4,6,8,10) ✅
// But length determined at runtime (cannot verify at comptime)
```

### Filtering: Skip Empty Rows Automatically

**Rule:** If an inner loop produces **no elements** (empty array), the **outer loop skips that row automatically**.

```hexen
// Inner loop filtering (some rows empty)
val no_empty : [_][_]i32 = for i in 1..10 {
    -> for j in 1..5 {
        if i % 2 == 0 {
            -> j                    // Even rows: all produce [1,2,3,4]
        }
    }
}
// i=1: []     → SKIPPED (empty row)
// i=2: [1,2,3,4]
// i=3: []     → SKIPPED (empty row)
// i=4: [1,2,3,4]
// i=5: []     → SKIPPED (empty row)
// i=6: [1,2,3,4]
// ...
// Result: [[1,2,3,4], [1,2,3,4], [1,2,3,4], ...] ✅ Uniform!
```

**Key insight:** Empty rows are skipped automatically, and **remaining rows must still have uniform length**.

**Correct filtering example:**

```hexen
// Filter evens, all remaining rows uniform
val evens_matrix : [_][_]i32 = for i in 1..10 {
    if i % 2 == 0 {                 // Only even rows
        -> for j in 1..5 {
            -> i * j
        }
    }
}
// i=1: skipped (outer filter)
// i=2: [2,4,6,8]
// i=3: skipped (outer filter)
// i=4: [4,8,12,16]
// ...
// Result: [[2,4,6,8], [4,8,12,16], [6,12,18,24], ...] ✅ Uniform!
```

**Invalid example (non-uniform after skipping):**

```hexen
val invalid : [_][_]i32 = for i in 1..5 {
    -> for j in 1..10 {
        if j > i * 2 && j < i * 3 {
            -> j
        }
    }
}
// i=1: []        → SKIPPED
// i=2: [5]       (length 1)
// i=3: [7,8]     (length 2)  ← DIFFERENT LENGTH!
// ❌ Runtime panic: Non-uniform dimensions
```

### Break/Continue in Nested Expressions

#### Break Inner Loop (Partial Row)

```hexen
val partial_rows : [_][_]i32 = for i in 1..3 {
    -> for j in 1..10 {
        if j > 5 {
            break                   // All rows break at same point
        }
        -> j
    }
}
// Result: [[1,2,3,4,5], [1,2,3,4,5], [1,2,3,4,5]] ✅ Uniform!
```

#### Break Outer Loop (Partial Matrix)

```hexen
val partial_matrix : [_][_]i32 = for i in 1..10 {
    if i > 3 {
        break                       // Stop at 3 rows
    }
    -> for j in 1..4 {
        -> j
    }
}
// Result: [[1,2,3], [1,2,3], [1,2,3]] (3 rows only)
```

#### Break Outer From Inner (With Labels!)

```hexen
val early_exit : [_][_]i32 = outer: for i in 1..10 {
    -> for j in 1..10 {
        if i * j > 20 {
            break outer             // Stop entire matrix generation!
        }
        -> i * j
    }
}
// i=1: [1,2,3,4,5,6,7,8,9,10]      (length 10)
// i=2: [2,4,6,8,10,12,14,16,18,20] (length 10)
// i=3: [3,6,9,12,15,18]            (stops at j=7: 3*7=21>20)
// ❌ Runtime panic: Non-uniform lengths (10, 10, 6)
```

**Better approach: ensure uniform break**

```hexen
val uniform_exit : [_][_]i32 = outer: for i in 1..10 {
    -> inner: for j in 1..10 {
        if i * j > 20 {
            if j == 1 {
                break outer         // Break outer if first element exceeds
            } else {
                break inner         // Otherwise just break inner (partial row)
            }
        }
        -> i * j
    }
}
```

#### Continue in Nested Loops

```hexen
// Continue inner (skip elements)
val skip_inner : [_][_]i32 = for i in 1..3 {
    -> for j in 1..10 {
        if j % 2 == 0 {
            continue                // Skip evens
        }
        -> j
    }
}
// Result: [[1,3,5,7,9], [1,3,5,7,9], [1,3,5,7,9]] ✅ Uniform!

// Continue outer (skip rows)
val skip_outer : [_][_]i32 = for i in 1..10 {
    if i % 2 == 0 {
        continue                    // Skip even rows
    }
    -> for j in 1..4 {
        -> j
    }
}
// Result: [[1,2,3], [1,2,3], [1,2,3], [1,2,3], [1,2,3]] (i=1,3,5,7,9)
```

### Arbitrary Nesting Depth (No Limits)

**2D (Matrix):**

```hexen
val matrix : [_][_]i32 = for i in 1..3 {
    -> for j in 1..4 {
        -> i * j
    }
}
// Type: [3][4]i32
```

**3D (Tensor/Cube):**

```hexen
val tensor : [_][_][_]i32 = for i in 1..2 {
    -> for j in 1..3 {
        -> for k in 1..4 {
            -> i * j * k
        }
    }
}
// Type: [2][3][4]i32
```

**4D (Hypercube):**

```hexen
val hypercube : [_][_][_][_]i32 = for i in 1..2 {
    -> for j in 1..2 {
        -> for k in 1..2 {
            -> for l in 1..2 {
                -> i + j + k + l
            }
        }
    }
}
// Type: [2][2][2][2]i32
```

**Key principle:** Nesting works to arbitrary depth (consistent with array system supporting N-dimensional arrays).

### Mixed Syntax in One Program

```hexen
// Mix all three syntax styles
val mixed : [_][_][_]i32 = for i in 1..2 {
    // Option A: intermediate variable
    val matrix : [_][_]i32 = for j in 1..3 {
        // Option B: direct nesting
        -> for k in 1..4 { -> i * j * k }
    }
    -> matrix
}

// Or fully compact (Option C)
val compact : [_][_][_]i32 = for i in 1..2 { -> for j in 1..3 { -> for k in 1..4 { -> i*j*k } } }

// Both produce identical results!
```

### Nested Loop Expression Examples

#### Example 1: Identity Matrix

```hexen
// Generate 5x5 identity matrix
val identity : [_][_]i32 = for i in 0..5 {
    -> for j in 0..5 {
        if i == j {
            -> 1                    // Diagonal
        } else {
            -> 0                    // Off-diagonal
        }
    }
}
// Result:
// [[1,0,0,0,0],
//  [0,1,0,0,0],
//  [0,0,1,0,0],
//  [0,0,0,1,0],
//  [0,0,0,0,1]]
```

#### Example 2: Multiplication Table

```hexen
// 10x10 multiplication table
val mult_table : [_][_]i32 = for i in 1..=10 {
    -> for j in 1..=10 {
        -> i * j
    }
}
// Result:
// [[1,2,3,...,10],
//  [2,4,6,...,20],
//  ...
//  [10,20,30,...,100]]
```

#### Example 3: Upper Triangular Matrix (Padding)

```hexen
// Upper triangular with zero padding
val upper_triangular : [_][_]i32 = for i in 0..5 {
    -> for j in 0..5 {
        if j >= i {
            -> i * 10 + j           // Upper triangle
        } else {
            -> 0                    // Pad with zeros (uniform!)
        }
    }
}
// Result:
// [[0,1,2,3,4],
//  [0,10,11,12,13],
//  [0,0,20,21,22],
//  [0,0,0,30,31],
//  [0,0,0,0,40]]
```

#### Example 4: 3D RGB Image

```hexen
// Generate 2x3 RGB image (height=2, width=3, channels=3)
val image : [_][_][_]i32 = for y in 0..2 {      // Height
    -> for x in 0..3 {                          // Width
        -> for c in 0..3 {                      // RGB channels
            -> (y * 100) + (x * 10) + c
        }
    }
}
// Type: [2][3][3]i32
// Result:
// [[[0,1,2],   [10,11,12],   [20,21,22]],      ← Row y=0
//  [[100,101,102], [110,111,112], [120,121,122]]] ← Row y=1
```

#### Example 5: Filtered Matrix (Skip Empty Rows)

```hexen
// Only include even-indexed rows
val filtered : [_][_]i32 = for i in 0..10 {
    if i % 2 == 0 {                 // Only even indices
        -> for j in 0..5 {
            -> i * 10 + j
        }
    }
}
// i=0: [0,1,2,3,4]
// i=1: skipped (odd)
// i=2: [20,21,22,23,24]
// i=3: skipped (odd)
// i=4: [40,41,42,43,44]
// ...
// Result: [[0,1,2,3,4], [20,21,22,23,24], [40,41,42,43,44], ...]
```

### Error Cases and Validation

#### Error 1: Non-Uniform Row Lengths

```hexen
val bad : [_][_]i32 = for i in 1..4 {
    -> for j in 1..10 {
        if j % i == 0 {
            -> j
        }
    }
}
// Runtime panic: Row 0 length 10, Row 1 length 5
```

**Fix:** Ensure all rows produce same length (break at same point, or pad/filter).

#### Error 2: Type Mismatch in Nesting

```hexen
val wrong : [_][_]i32 = for i in 1..3 {
    -> for j in 1..4 {
        -> j:f64                    // ❌ Error: expected i32, got f64
    }
}
```

**Error message:**

```
Error: Type mismatch in nested loop expression
  -> j:f64
     ^^^^^
Expected: i32 (from array type [_][_]i32)
Got:      f64

Help: Inner loop must produce elements matching array element type
Note: Type context flows from outer annotation [_][_]i32:
      - Outer loop produces: [_]i32
      - Inner loop produces: i32
```

#### Error 3: Dimension Mismatch

```hexen
val dimensions : [_][_]i32 = for i in 1..3 {
    -> i                            // ❌ Error: expected [_]i32, got i32
}
```

**Error message:**

```
Error: Dimension mismatch in nested loop expression
  -> i
     ^
Expected: [_]i32 (array of i32 - one dimension)
Got:      i32 (scalar - zero dimensions)

Help: Outer loop should produce arrays, not scalars
Note: For [_][_]i32, outer loop must -> [_]i32 values
      Use nested loop: -> for j in ... { -> value }
```

## Complete Examples

### Example 1: Simple Iteration

```hexen
// Iterate over range (statement mode)
for i in 1..10 {
    print(i)
}

// Iterate over array (statement mode)
val data : [_]i32 = [10, 20, 30, 40, 50]
for elem in data[..] {
    print(elem)
}

// Iterate with step
for i in 0..100:10 {
    print(i)                        // Prints: 0, 10, 20, ..., 90
}
```

### Example 2: Loop Expressions (Array Generation)

```hexen
// Generate array of squares
val squares : [_]i32 = for i in 1..10 {
    -> i * i
}
// Result: [1, 4, 9, 16, 25, 36, 49, 64, 81]

// Filter evens
val evens : [_]i32 = for i in 1..20 {
    if i % 2 == 0 {
        -> i
    }
}
// Result: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

// Map and filter
val processed : [_]i32 = for i in 1..20 {
    if i % 3 == 0 {
        continue                    // Skip multiples of 3
    }
    -> i * 10
}
// Result: [10, 20, 40, 50, 70, 80, 100, 110, ...]
```

### Example 3: Early Termination

```hexen
// Collect until condition
val until_fifty : [_]i32 = for i in 1..1000 {
    if i > 50 {
        break
    }
    -> i
}
// Result: [1, 2, 3, ..., 50]

// Find first N elements matching condition
val first_ten_evens : [_]i32 = {
    mut count : i32 = 0
    for i in 1..1000 {
        if i % 2 == 0 {
            if count >= 10 {
                break
            }
            count = count + 1
            -> i
        }
    }
}
// Result: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
```

### Example 4: Nested Loops with Labels

```hexen
// Break outer loop from inner
outer: for i in 1..10 {
    inner: for j in 1..10 {
        if i * j > 50 {
            break outer             // Exit both loops
        }
        print(i, j)
    }
}

// Continue outer loop from inner
outer: for i in 1..10 {
    inner: for j in 1..10 {
        if j > 5 {
            continue outer          // Skip to next i
        }
        print(i, j)
    }
}

// Generate nested array with early termination
val matrix : [_][_]i32 = outer: for i in 1..10 {
    val row : [_]i32 = inner: for j in 1..10 {
        if i + j > 15 {
            break outer             // Stop all generation
        }
        -> i * j
    }
    -> row
}
```

### Example 5: While Loop Patterns

```hexen
// Conditional iteration
mut count : i32 = 0
while count < 10 {
    print(count)
    count = count + 1
}

// Infinite loop with break
while true {
    val input = get_user_input()
    if input == "quit" {
        break
    }
    process(input)
}

// While with continue
mut i : i32 = 0
while i < 20 {
    i = i + 1
    if i % 3 == 0 {
        continue
    }
    print(i)
}
```

### Example 6: Combining Loops and Ranges

```hexen
// Iterate over array slice
val data : [_]i32 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

// Process middle section
for elem in data[2..8] {
    print(elem)                     // Prints: 30, 40, 50, 60, 70, 80
}

// Process every other element
for elem in data[0..:2] {
    print(elem)                     // Prints: 10, 30, 50, 70, 90
}

// Generate new array from slice
val doubled : [_]i32 = for elem in data[2..8] {
    -> elem * 2
}
// Result: [60, 80, 100, 120, 140, 160]
```

### Example 7: Functional Patterns

```hexen
// Map: transform each element
val doubled : [_]i32 = for i in 1..10 {
    -> i * 2
}

// Filter: select elements
val evens : [_]i32 = for i in 1..20 {
    if i % 2 == 0 {
        -> i
    }
}

// Map + Filter: transform and select
val even_squares : [_]i32 = for i in 1..20 {
    if i % 2 == 0 {
        -> i * i
    }
}

// Reduce (manual): accumulate values
val sum : i32 = {
    mut total : i32 = 0
    for i in 1..100 {
        total = total + i
    }
    -> total
}
```

## Implementation Notes

### Loop Expression Compilation

When compiling loop expressions that generate arrays:

1. **Pre-allocate array** (if size known at comptime)
2. **Dynamic growth** (if size unknown - filtering/break)
3. **Append values** as iterations produce them via `->`
4. **Return final array** (potentially resized)

**Pseudocode:**

```python
# Bounded range without filtering (size known)
def compile_loop_expr_bounded(range, body):
    size = compute_range_length(range)
    array = allocate_array(size)
    index = 0
    for value in range:
        result = execute_body(body, value)
        if result is not None:  # -> executed
            array[index] = result
            index += 1
    return array[:index]  # Return actual size (may be less if filtering)

# Unbounded/unknown size (dynamic growth)
def compile_loop_expr_dynamic(iterable, body):
    array = []  # Dynamic array
    for value in iterable:
        result = execute_body(body, value)
        if result is not None:  # -> executed
            array.append(result)
        if should_break():
            break
    return array  # Return final array
```

### Zero-Cost Array View Iteration

When iterating over `array[range]`:

1. **Create view** (O(1) - just metadata)
2. **Iterate view** (O(n) - direct memory access)
3. **No materialization** (no array copy)

**View structure:**

```
ArrayView {
    source: *Array       // Pointer to source
    offset: usize        // Start index
    length: usize        // Number of elements
    stride: isize        // Step (can be negative)
}

for elem in array[2..8:2] {
    // View: {source: &array, offset: 2, length: 3, stride: 2}
    // Iteration: array[2], array[4], array[6]
}
```

### Comptime Loop Detection

The semantic analyzer tracks:

```python
@dataclass
class LoopContext:
    loop_type: str              # "for-in" or "while"
    is_expression: bool         # True if in value context
    is_bounded: bool            # True if range has end bound
    label: Optional[str]        # Loop label (if any)

    def can_produce_array(self) -> bool:
        """Check if loop can produce array."""
        return (
            self.loop_type == "for-in" and
            self.is_expression and
            self.is_bounded
        )

    def requires_type_annotation(self) -> bool:
        """Check if loop expression requires type annotation."""
        return self.is_expression
```

## Design Rationale

### Why Loop Expressions (Not Just Map/Filter)?

**Loop expressions provide:**
- **Unified syntax** - Same `->` as conditionals and blocks
- **Full control flow** - break, continue, early return
- **Imperative feel** - Familiar to all programmers
- **Zero syntax overhead** - No special comprehension syntax

**Compared to functional methods:**

```hexen
// Loop expression (Hexen)
val result : [_]i32 = for i in 1..20 {
    if i % 3 == 0 { continue }
    if i > 15 { break }
    -> i * 2
}

// Functional equivalent (hypothetical)
val result : [_]i32 = (1..20)
    .filter(|i| i % 3 != 0)
    .take_while(|i| i <= 15)
    .map(|i| i * 2)
    .collect()
```

**Loop expressions are simpler** - No method chaining, closures, or collection step needed.

### Why Forbid While Loop Expressions?

**Rationale:**
- While loops have no bounded iteration guarantee
- Unbounded iteration → infinite array allocation risk
- For-in loops with bounded ranges provide safe array generation

**Comparison:**

```hexen
// ✅ For-in with bounded range (safe)
val safe : [_]i32 = for i in 1..100 { -> i }    // Known max size: 99

// ❌ While loop (unsafe - unbounded)
val unsafe : [_]i32 = while condition { -> value }  // Unknown size!
```

**If truly needed**, while-style iteration can use explicit array building:

```hexen
// Manual array building with while
val result : [_]i32 = {
    mut temp : [_]i32 = []          // Dynamic array
    while condition {
        val value = compute()
        temp.push(value)            // Explicit append
    }
    -> temp
}
```

### Why No Do-While?

**Rationale:**
- Most use cases covered by regular `while`
- Can emulate with `while` + flag (see earlier example)
- Keeps language simpler (fewer loop constructs)
- Can add later if demand arises

### Why Simple Label Syntax?

**Comparison:**

```hexen
// Option A: Simple identifier (Hexen choice)
outer: for i in 1..10 {
    break outer
}

// Option B: Tick-prefixed (Rust style)
'outer: for i in 1..10 {
    break 'outer
}
```

**Rationale:**
- Simpler syntax (no special characters)
- Labels already distinguished by `:` suffix
- Consistent with Hexen's clean syntax philosophy
- Less visual noise

### Why Allow Labels Across Loop Types?

**Rationale:**
- Labels identify loops (not loop types)
- More flexible (any loop can be outer/inner)
- Consistent with other languages (Rust, Java)
- No implementation complexity

**Example:**

```hexen
// Label flexibility (any combination works)
outer: while condition1 {
    inner: for i in 1..10 {
        break outer                 // ✅ Works across types
    }
}

outer: for i in 1..10 {
    inner: while condition2 {
        continue outer              // ✅ Works across types
    }
}
```

## Summary

**Loop Types:**
- **For-in loops** - Iterate ranges and arrays
- **While loops** - Conditional iteration
- **No do-while** - Not supported initially

**Loop Modes:**
- **Statement mode** - Execute code (no value production)
- **Expression mode** - Generate arrays (for-in only, bounded ranges)

**Loop Variables:**
- **Type inference** - Inferred from iterable (comptime, concrete, array)
- **Always immutable** - Cannot mutate loop variable
- **Optional type annotation** - Explicit type override allowed

**Control Flow:**
- **break** - Exit loop (returns partial array in expressions)
- **continue** - Skip iteration (no value produced in expressions)
- **return** - Exit containing function
- **Labels** - Control nested loops (simple identifier syntax)

**Loop Expressions:**
- **Filtering** - Skip iterations without `->`
- **Early termination** - `break` returns partial array
- **Type annotation required** - Consistent with runtime operations
- **Safety** - Unbounded ranges forbidden in expression context

**Nested Loop Expressions:**
- **Matrix/tensor generation** - Produce multidimensional arrays
- **Three syntax variants** - Intermediate variables, direct nesting, compact form
- **Type context flow** - Outer type annotation provides inner context
- **Uniform dimensions** - Runtime validation ensures all rows same length
- **Empty row skipping** - Automatic filtering of empty inner loops
- **Arbitrary depth** - No nesting limits (2D, 3D, 4D, ...)

**Integration:**
- **Range system** - Zero-cost views via `array[range]`
- **Type system** - Comptime type preservation and adaptation
- **Array generation** - Inferred size `[_]T` notation

**Key Principles:**
- **Ergonomic Literals** - Comptime types adapt in loops
- **Transparent Costs** - Type annotations make array generation visible
- **Zero-Cost Abstractions** - Views instead of copies for iteration
- **Explicit Operations** - Break/continue/return make control flow clear
- **Type Safety** - Immutable loop variables, bounded ranges for arrays

---

**Last Updated:** 2025-10-27
**Version:** 1.0 (Initial Specification)
