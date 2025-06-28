# Hexen Binary Operations 🦉

*Design Specification*

## Overview

Hexen's binary operations system follows the **"Ergonomic Literals + Transparent Costs"** philosophy - making common operations seamless while keeping all computational costs visible. The system is built on top of our comptime type system, ensuring consistent type resolution across all operations with natural adaptation for literals and explicit syntax for concrete type mixing.

### Key Design Principles

1. **Ergonomic Comptime Literals**: 
   - All numeric literals start as adaptive comptime types
   - Operations preserve comptime types for maximum flexibility
   - Context guides resolution to concrete types seamlessly
   - Common patterns work without type ceremony

2. **Transparent Computational Costs**:
   - Two division operators for clear intent: `/` (mathematical) and `\` (efficient integer)
   - Float result types reveal floating-point computation
   - Integer result types guarantee efficient integer math
   - Mixed concrete types require explicit conversions for cost visibility

3. **Predictable Type Resolution**:
   - Same comptime types stay comptime (maximum flexibility)
   - Mixed comptime types adapt to context or preserve maximum flexibility until context forces resolution
   - Concrete type mixing requires explicit target types
   - Operator choice determines computation type (`/` vs `\`)

## Core Philosophy

### Four Core Principles Applied to Binary Operations

Binary operations in Hexen directly implement the four core principles from the type system:

1. **✨ Ergonomic Literals**: Comptime types adapt seamlessly (no conversion cost at runtime)
2. **🔧 Explicit Conversions**: All concrete type mixing requires visible syntax (`value:type`)
3. **👁️ Cost Visibility**: Every conversion is transparent in the code
4. **📐 Predictable Rules**: Simple, consistent behavior everywhere

**Translation Rule**: Binary operations follow the **exact same conversion rules** as the TYPE_SYSTEM.md Quick Reference Table - ensuring complete consistency across the language.

### Binary Operation Type Resolution Rules

Binary operations apply the TYPE_SYSTEM.md conversion rules to their results:

| Result Type | Conversion | Syntax | Notes |
|-------------|------------|--------|-------|
| **✅ Ergonomic (Comptime Results)** |
| `comptime_int` | ✅ Preserved | `val x = 42 + 100` | Comptime type preserved (maximum flexibility!) |
| `comptime_int` | ✅ Implicit | `val x : i32 = 42 + 100` | No cost, ergonomic adaptation |
| `comptime_float` | ✅ Preserved | `val x = 3.14 + 2.71` | Comptime type preserved (maximum flexibility!) |
| `comptime_float` | ✅ Implicit | `val x : f32 = 3.14 + 2.71` | No cost, ergonomic adaptation |
| **🔧 Explicit (Concrete Results)** |
| Mixed concrete | 🔧 Explicit | `val x : f64 = i32_val:f64 + f64_val` | Conversion cost visible via explicit syntax |
| Precision loss | 🔧 Explicit | `val x : i32 = f64_val:i32 + f32_val:i32` | Data loss visible via conversion |
| **❌ Forbidden** |
| No context | ❌ Forbidden | `val x = i32_val + f64_val` | Use explicit conversion: `i32_val:f64 + f64_val` |

### Legend

- **✅ Preserved**: Comptime type stays flexible, maximum adaptability (comptime types only)
- **✅ Implicit**: Happens automatically, no conversion cost (comptime types only)
- **🔧 Explicit**: Requires explicit syntax (`value:type`), conversion cost visible
- **❌ Forbidden**: Not allowed, compilation error

**Key Insight**: Binary operation results follow the **same conversion rules** as individual values - maintaining complete consistency.

## Operator Precedence

Binary operators follow standard mathematical precedence with explicit grouping for clarity.

### Precedence Levels (Highest to Lowest)

| Level | Operators | Associativity | Description |
|-------|-----------|---------------|-------------|
| 1 | `-`, `!` | Right | Unary minus, logical NOT |
| 2 | `*`, `/`, `\`, `%` | Left | Multiplication, float division, integer division, modulo |
| 3 | `+`, `-` | Left | Addition, subtraction |
| 4 | `<`, `>`, `<=`, `>=` | Left | Relational comparison |
| 5 | `==`, `!=` | Left | Equality comparison |
| 6 | `&&` | Left | Logical AND |
| 7 | `\|\|` | Left | Logical OR |

### Precedence Examples

```hexen
// Mathematical precedence
val result1 : i32 = 2 + 3 * 4           // 2 + (3 * 4) = 14
val result2 : i32 = (2 + 3) * 4         // (2 + 3) * 4 = 20

// Division operators have same precedence but different semantics:
val float_precise : i32 = ((10 / 3) * 9):i32  // Float division: (3.333... * 9) = 30.0 → 30 (explicit conversion)
val int_preserved = (10 \ 3) * 9          // Integer division: (3 * 9) = 27 (comptime_int preserved until context)
val mixed : f64 = 20 * (3 / 2)            // 20 * (1.5) = 30.0

// Comparison precedence  
val check1 = 5 > 3 && 2 < 4      // (5 > 3) && (2 < 4) = true
val check2 = 5 > 3 == 2 < 4      // (5 > 3) == (2 < 4) = true

// Explicit grouping for clarity
val complex_float : f64 = (a + b) * (c - d) / (e + f)   // Float division
val complex_int : i32 = (a + b) * (c - d) \ (e + f)     // Integer division
```

## How Comptime Types Work in Binary Operations

### ✨ The Ergonomic Foundation: Smart Literal Adaptation

Hexen's binary operations start with a simple, powerful concept: **all numeric literals are "smart" and adapt to their context**. This creates natural, seamless usage for common cases while maintaining complete type safety.

```hexen
// Every numeric literal starts as a comptime type that can adapt
42        // comptime_int - can become i32, i64, f32, f64 as needed
3.14      // comptime_float - can become f32, f64 as needed
-100      // comptime_int - adapts to context seamlessly
2.5       // comptime_float - adapts to context seamlessly
```

**The Magic:** These smart literals make common operations feel natural with **zero runtime cost**:

```hexen
// ✨ Same literals, different contexts - zero runtime cost
val counter : i32 = 42 + 100        // comptime adapts to i32 (zero runtime cost)
val big_counter : i64 = 42 + 100     // comptime adapts to i64 (zero runtime cost)
val percentage : f32 = 42 + 100      // comptime adapts to f32 (zero runtime cost)
val precise : f64 = 42 + 100         // comptime adapts to f64 (zero runtime cost)

// ✨ Mixed comptime types adapt naturally with context (zero runtime cost)
val mixed : f64 = 42 + 3.14          // comptime_int + comptime_float → f64 (zero runtime cost)
val calculation : f32 = 22 / 7       // comptime division → f32 (zero runtime cost)
```

When these comptime types meet in binary operations, they follow the **same patterns** as the TYPE_SYSTEM.md Quick Reference Table for predictable, consistent behavior.

### 📐 Predictable Binary Operation Patterns

Binary operations follow four simple patterns derived from the TYPE_SYSTEM.md conversion rules:

#### Pattern 1: ✅ Comptime + Comptime → Comptime (Ergonomic)

When both operands are comptime types, the result **stays comptime** for maximum flexibility and zero runtime cost:

```hexen
// ✨ Ergonomic: comptime operations stay comptime (zero runtime cost)
val integers = 42 + 100         // comptime_int + comptime_int → comptime_int
val more_math = 10 * 5          // comptime_int * comptime_int → comptime_int  
val division = 20 \ 4           // comptime_int \ comptime_int → comptime_int (integer division)

// ✅ Implicit adaptation following TYPE_SYSTEM.md rules
val small : i32 = integers      // comptime_int → i32 (implicit, no cost)
val large : i64 = integers      // comptime_int → i64 (implicit, no cost)
val precise : f64 = integers    // comptime_int → f64 (implicit, no cost)
```

### **🔄 Comptime Type Propagation: The Compiler's Computational Capacity**

**The fundamental principle**: The compiler has the capacity to **resolve operations between comptime types** and **propagate the results through chains of operations** until a concrete type boundary is encountered.

#### **Comptime Operation Chains**
The compiler can evaluate arbitrarily complex comptime expressions without premature resolution:

```hexen
// ✅ Compiler propagates comptime operations through multiple steps
val step1 = 42 + 100              // comptime_int + comptime_int → comptime_int
val step2 = step1 * 2             // comptime_int * comptime_int → comptime_int
val step3 = step2 + 3.14          // comptime_int + comptime_float → comptime_float (promotion in comptime space)
val step4 = step3 / 2.0           // comptime_float / comptime_float → comptime_float
val step5 = step4 + (50 \ 7)      // comptime_float + comptime_int → comptime_float

// ✅ All steps happen in "comptime space" - no concrete resolution yet!
// Only when we provide concrete context does resolution occur:
val final_f64 : f64 = step5       // NOW: comptime_float → f64 (single resolution point)
val final_f32 : f32 = step5       // SAME source, different target (maximum flexibility!)
val final_i32 : i32 = step5:i32   // Explicit conversion needed
```

#### **Complex Expression Propagation**
Even complex expressions stay in comptime space until forced to resolve:

```hexen
// ✅ Entire expression evaluated in comptime space
val complex_math = (42 + 100) * 3.14 + (50 / 7) - (25 \ 4)
// Breakdown: 
//   (142) * 3.14 + (7.14...) - (6) 
//   445.88 + 7.14... - 6 
//   → comptime_float (stays flexible!)

// ✅ Same expression, multiple concrete resolutions
val as_precise : f64 = complex_math      // comptime_float → f64
val as_single : f32 = complex_math       // comptime_float → f32  
val as_integer : i32 = complex_math:i32  // comptime_float → i32 (explicit conversion)
```

#### **🎯 Comptime Propagation Rules (Formalized)**
1. **`comptime_int ○ comptime_int`** → **`comptime_int`** (except `/` which produces `comptime_float`)
2. **`comptime_int ○ comptime_float`** → **`comptime_float`** (natural mathematical promotion in comptime space)
3. **`comptime_float ○ comptime_float`** → **`comptime_float`** (stays in comptime space)
4. **Operations chain indefinitely** → **Compiler resolves entire expression trees in comptime space**
5. **Resolution only at boundaries** → **Concrete types or explicit annotations (developer requests concrete type) force resolution**

#### **Resolution Boundaries**
Comptime propagation continues until the compiler encounters a **resolution boundary**:

**What stays in comptime space:**
- **Literals**: `42`, `3.14`, `true`
- **Comptime operations**: `42 + 100`, `3.14 * 2.5`, `100 / 7`
- **Comptime variables**: `val x = 42 + 3.14` (result of comptime operations)

**What creates resolution boundaries:**
- **Function calls**: `sqrt(5.0)`, `compute_value()` (return concrete types)
- **Concrete variables**: `val x : i32 = 50` (explicitly typed variables)
- **Mixed operations**: `comptime_type + concrete_type` → concrete result
- **Explicit type annotations**: `val x : f64 = comptime_expr` (developer requests concrete type)

```hexen
// ✅ Stays in comptime space
val flexible = 42 + 3.14 * 2.5 + 100    // All literals → comptime_float
val derived = flexible / 2.0 + 50        // comptime_float operations → comptime_float

// 🚧 Resolution boundaries
val concrete : i32 = 50                 // Explicit concrete type
val boundary : i32 = flexible + concrete       // BOUNDARY: comptime_float + i32 → i32 (concrete result)
val function_result : f64 = sqrt(25.0)        // BOUNDARY: function call → f64 (concrete result)

// ✅ Function parameters create boundaries
func process(value: f64) : void = { /* implementation */ }
process(42 + 3.14 * 2.0)                // BOUNDARY: comptime_float resolves to f64 for parameter

// ✅ Developer requests concrete type
val result : f32 = 42 + 3.14 + 100 * 2.5  // BOUNDARY: developer requests f32, forces resolution
```

#### **The Revolutionary Advantage**
This approach provides **unprecedented flexibility**:

```hexen
// ✅ Define complex mathematical constants once (pure comptime operations)
val math_constant = (1.0 + 2.236) / 2.0           // comptime_float (flexible!)
val complex_calc = math_constant * math_constant + 1.0  // Still comptime_float!
val big_calculation = 42 * 3.14159 + 100 / 7      // All comptime operations → comptime_float

// ✅ Use in different precision contexts without modification
val high_precision : f64 = math_constant          // Resolves to f64
val fast_compute : f32 = math_constant            // Same calc, resolves to f32
val for_display : i32 = math_constant:i32         // Same calc, explicit to i32

// ✅ Complex expressions adapt to usage context
func get_f64_physics() : f64 = {
    return 9.81 * 2.5 + 100.0                     // Pure comptime operations → resolves to f64
}
func get_f32_physics() : f32 = {
    return 9.81 * 2.5 + 100.0                     // Same calc → resolves to f32
}

// ❌ Function calls break comptime propagation (create resolution boundaries)
// val bad_example = (1.0 + sqrt(5.0)) / 2.0      // sqrt() returns concrete f64, not comptime
// val physics_calc = 9.81 * mass_factor + offset // Variables are concrete types, not comptime
```

#### Pattern 2: 🔄 Comptime + Concrete → Concrete (Ergonomic Adaptation)

When a comptime type meets a concrete type, the **comptime type adapts** following TYPE_SYSTEM.md rules (implicit, no cost):

```hexen
val count : i32 = 100
val ratio : f64 = 2.5

// ✨ Ergonomic: comptime adapts to concrete type (implicit, no cost)
val result1 = count + 42        // i32 + comptime_int → i32 (comptime adapts following TYPE_SYSTEM.md)
val result2 = count * 2         // i32 * comptime_int → i32 (comptime adapts following TYPE_SYSTEM.md)
val result3 = count \ 10        // i32 \ comptime_int → i32 (comptime adapts following TYPE_SYSTEM.md)

// 🔧 Explicit conversions when result differs from target (TYPE_SYSTEM.md rule)
val result4 : f64 = ratio + 42  // f64 + comptime_int → f64 (comptime adapts, no conversion needed)
// val narrow : i32 = ratio + 42 // ❌ Error: f64 → i32 requires explicit conversion (TYPE_SYSTEM.md rule)
val narrow : i32 = (ratio + 42):i32  // ✅ Explicit: f64 → i32 (conversion cost visible)
```

#### Pattern 3: 🔧 Mixed Concrete → Requires Explicit Syntax (Cost Visibility)

When two different concrete types meet, **explicit syntax is required** following TYPE_SYSTEM.md rules:

```hexen
val small : i32 = 10
val large : i64 = 20
val precise : f64 = 3.14

// ❌ Mixed concrete types require explicit syntax (TYPE_SYSTEM.md rule)
// val mixed1 = small + large   // Error: i32 + i64 requires explicit type annotation
// val mixed2 = small + precise // Error: i32 + f64 requires explicit type annotation

// ✅ Explicit syntax makes conversion costs visible (TYPE_SYSTEM.md rule)
val as_i64 : i64 = small + large           // 🔧 Explicit: i32 → i64 (conversion cost visible)
val as_f64 : f64 = small + precise         // 🔧 Explicit: i32 → f64 (conversion cost visible)

// 🔧 Data loss requires explicit acknowledgment (TYPE_SYSTEM.md rule)
// val lose_precision : i32 = large + small  // Error: i64 → i32 needs ':i32' (data loss)
val with_truncation : i32 = (large + small):i32  // ✅ Explicit: i64 → i32 (data loss visible)
```

#### Pattern 4: ⚡ Same Concrete → Same Concrete (Identity)

When both operands are the **same concrete type**, the result is that same concrete type (identity rule from TYPE_SYSTEM.md):

```hexen
val a : i32 = 10
val b : i32 = 20

// ⚡ Identity: same concrete types produce same concrete type (no conversion)
val result1 = a + b             // i32 + i32 → i32 (identity, no conversion needed)
val result2 = a * b             // i32 * i32 → i32 (identity, no conversion needed)
val result3 = a \ b             // i32 \ i32 → i32 (identity, no conversion needed)

// 🔧 Assignment to different types requires explicit conversion (TYPE_SYSTEM.md rule)
val c : f64 = 3.14
val d : f64 = 2.71
val result4 = c + d             // f64 + f64 → f64 (identity, no conversion needed)
// val narrow : f32 = c + d     // ❌ Error: f64 → f32 requires ':f32' (TYPE_SYSTEM.md rule)
val narrow : f32 = (c + d):f32 // ✅ Explicit: f64 → f32 (conversion cost visible)
```

### 🎯 Pattern Summary: Complete TYPE_SYSTEM.md Alignment

| Binary Operation Pattern | Conversion | Syntax | Notes |
|---------------------------|------------|---------|-------|
| `comptime + comptime` (same type) | ✅ Preserved | `val x = 42 + 100` | Comptime type preserved (maximum flexibility!) |
| `comptime + comptime` (context provided) | ✅ Implicit | `val x : i32 = 42 + 100` | No cost, ergonomic adaptation |
| `comptime + concrete` | ✅ Implicit | `i32_val + 42` | No cost, comptime adapts |
| `same_concrete + same_concrete` | ✅ Identity | `i32_val + i32_val` | No conversion needed |
| `mixed_concrete + mixed_concrete` | 🔧 Explicit | `val x : f64 = i32_val:f64 + f64_val` | Conversion cost visible via explicit syntax |

**Key Insight**: Binary operations are **not special** - they follow the **exact same conversion rules** as individual values, ensuring complete consistency across Hexen.

## Visual Mental Model

Think of it like **smart literal adaptation in different "worlds"**:

```
🌍 i32 World          🌍 i64 World          🌍 f64 World
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   10 + 42   │      │   10 + 42   │      │   10 + 42   │
│      ↓      │      │      ↓      │      │      ↓      │
│  comptime   │      │  comptime   │      │  comptime   │  
│   adapts    │      │   adapts    │      │   adapts    │
│   to i32    │      │   to i64    │      │   to f64    │
└─────────────┘      └─────────────┘      └─────────────┘

// Same literals, different worlds, different results!
val small : i32 = 10 + 42    // comptime → i32
val large : i64 = 10 + 42    // comptime → i64  
val float : f64 = 10 + 42    // comptime → f64
```

## Type Resolution Rules Summary

### ✅ **Safe Operations (No Explicit Type Needed)**
1. **comptime + comptime** → preserves maximum flexibility until context forces resolution
2. **comptime + concrete** → result is concrete (comptime adapts)
3. **same concrete + same concrete** → result is same concrete type

### 🔧 **Explicit-Required Operations (Conversion Costs Must Be Visible)**
1. **different concrete + different concrete** → requires explicit conversions (mixed concrete types)
2. **concrete result assigned to different type** → may need ': type' for precision loss (TYPE_SYSTEM.md rule)

### 🎯 **Key Principle: Only Comptime Types Can Adapt**
Following TYPE_SYSTEM.md's core rule:
- **Comptime types** (literals) → can adapt to any numeric type seamlessly
- **Concrete types** (variables, operation results) → require explicit type annotations for precision loss
- **Binary operation results involving concrete types** → are always concrete, never comptime

### 3. Mutable Assignment Rules

Mutable variable assignment follows the same TYPE_SYSTEM.md conversion rules as immutable variables. The mutable variable's declared type provides context for all subsequent assignments.

```hexen
mut counter : i32 = 0
mut precise : f32 = 0.0

// ✅ Safe assignments - comptime types adapt to context (TYPE_SYSTEM.md implicit rule)
counter = 42                          // comptime_int adapts to i32 context
counter = 10 + 20                     // comptime_int + comptime_int → comptime_int adapts to i32 context
precise = 3.14                        // comptime_float adapts to f32 context

// ✅ Same concrete types work seamlessly (TYPE_SYSTEM.md identity rule)
counter = some_i32 + other_i32        // i32 + i32 → i32 (identity, no conversion)
precise = some_f32 * other_f32        // f32 * f32 → f32 (identity, no conversion)

// 🔧 Mixed concrete types require explicit conversions (TYPE_SYSTEM.md explicit rule)
// counter = some_i64                     // ❌ Error: i64 → i32 requires explicit conversion
// counter = some_i64 + some_f64          // ❌ Error: Mixed types require explicit conversion
// precise = some_f64                     // ❌ Error: f64 → f32 requires explicit conversion

counter = some_i64:i32               // ✅ Explicit: i64 → i32 (conversion cost visible)
counter = some_i64:i32 + some_f64:i32  // ✅ Explicit: convert both operands
precise = some_f64:f32               // ✅ Explicit: f64 → f32 (conversion cost visible)

// 🔧 Explicit conversions required for mixed concrete types
mut result : f64 = 0.0
result = some_i32:f64 + some_i64:f64  // ✅ Explicit: i32 → f64 + i64 → f64 (conversion costs visible)
```

#### Key Mutable Assignment Rules

1. **Type Consistency**: The target type of a mutable variable cannot change after declaration
2. **Context Priority**: The mutable variable's type provides the primary context for all assignments
3. **TYPE_SYSTEM.md Alignment**: All assignment rules follow the exact same conversion table
4. **Comptime Adaptation**: Comptime types adapt implicitly to the mutable variable's type (no cost)
5. **Explicit Conversions**: Concrete type mixing requires explicit `value:type` syntax (cost visible)
6. **Predictable Behavior**: The same expression will resolve consistently based on the mutable variable's type

## Division Operations: Float vs Integer

Hexen provides **two distinct division operators** that make computational intent clear and costs transparent, following the TYPE_SYSTEM.md conversion patterns:

### Float Division (`/`) - Mathematical Division
**Produces floating-point results** for mathematical precision:

```hexen
// ✅ Preserved resolution (TYPE_SYSTEM.md preservation rule)
val precise1 = 10 / 3        // comptime_int / comptime_int → comptime_float (preserved until context)
val precise2 = 7 / 2         // comptime_int / comptime_int → comptime_float (preserved until context)
val float_calc = 10.5 / 2.1  // comptime_float / comptime_float → comptime_float (preserved until context)

// ✅ Implicit adaptation to different float types (TYPE_SYSTEM.md implicit rule)
val precise3 : f32 = 22 / 7     // comptime_float → f32 (implicit, no cost)
val explicit_f64 : f64 = 10 / 3 // comptime_float → f64 (implicit, no cost)

// 🔧 Mixed concrete types require explicit conversions (TYPE_SYSTEM.md explicit rule)
val int_val : i32 = 10
val float_val : f64 = 3.0
// val mixed = int_val / float_val  // ❌ Error: mixed concrete requires explicit conversion
val explicit_mixed : f64 = int_val:f64 / float_val  // ✅ Explicit: i32 → f64 (conversion cost visible)

// 🔧 Assignment to different types requires explicit conversion (TYPE_SYSTEM.md explicit rule)
mut result : i32 = 0
// result = 10 / 3               // ❌ Error: f64 → i32 requires explicit conversion
result = (10 / 3):i32           // ✅ Explicit: f64 → i32 (conversion cost visible)
```

### Integer Division (`\`) - Efficient Truncation
**Works naturally with integer types**, producing efficient integer results:

```hexen
// ✅ Preserved resolution (TYPE_SYSTEM.md preservation rule)
val fast1 = 10 \ 3              // comptime_int \ comptime_int → comptime_int (preserved until context)
val fast2 = 7 \ 2               // comptime_int \ comptime_int → comptime_int (preserved until context)

// ✅ Implicit adaptation to different integer types (TYPE_SYSTEM.md implicit rule)
val fast3 : i64 = 22 \ 7        // comptime_int → i64 (implicit, no cost)

// ✅ Integer division with concrete types
val a : i32 = 10
val b : i32 = 3
val efficient = a \ b           // i32 \ i32 → i32 (identity, no conversion)

// ❌ Float operands with integer division is an error
// val invalid = 10.5 \ 2.1     // Error: Integer division requires integer operands
// val also_bad = 3.14 \ 42     // Error: Integer division requires integer operands

// 🔧 Mixed integer types require explicit conversions (TYPE_SYSTEM.md explicit rule)
val c : i64 = 20
// val mixed = a \ c            // ❌ Error: Mixed concrete types need explicit conversion
val explicit_mixed : i64 = a:i64 \ c  // ✅ Explicit: i32 → i64 (conversion cost visible)

// Mutable assignment with integer division
mut result : i32 = 0
result = a \ b                  // ✅ Identity: i32 \ i32 → i32 (no conversion)
// result = c \ b               // ❌ Error: Mixed concrete types need explicit conversion
result = (c:i32) \ b            // ✅ Explicit conversion then identity
```

### Design Philosophy

#### **Transparent Cost Model**
- **`/` → Float result**: User sees floating-point type, knows FP computation occurred
- **`\` → Integer result**: User sees integer type, knows efficient integer operation

#### **Mathematical Honesty** 
- **`10 / 3`** naturally produces a fraction → comptime_float preserved until context forces resolution
- **`10 \ 3`** explicitly requests truncation → comptime_int preserved until context forces resolution

#### **No Hidden Magic**
- Division behavior determined by **operator choice**, not operand types
- Comptime types adapt to context following TYPE_SYSTEM.md rules
- All conversions follow the same patterns as individual values

### Truncation Rules

Float-to-integer conversion follows standard truncation rules from TYPE_SYSTEM.md:

```hexen
// Truncation towards zero (TYPE_SYSTEM.md explicit conversion rule)
mut result : i32 = 0
result = (10.9 / 2.0):i32     // 5.45 → 5 (explicit conversion)
result = (-10.9 / 2.0):i32    // -5.45 → -5 (explicit conversion)

// Exact conversions when possible
result = (20.0 / 4.0):i32     // 5.0 → 5 (exact, but still explicit)
```

## Function Return Context

Function return types provide context for binary operations, following TYPE_SYSTEM.md patterns:

```hexen
// Return type provides context for binary operations
func get_count() : i32 = {
    return 42 + 100                      // comptime_int + comptime_int → i32 (implicit)
}
func get_ratio() : f64 = {
    return 42 + 3.14                     // comptime_int + comptime_float → f64 (implicit)
}
func precise_calc() : f32 = {
    return 10 / 3                        // Float division → f32 (implicit)
}

// Mixed concrete types require explicit conversions
func mixed_sum(a: i32, b: i64) : f64 = {
    return a:f64 + b:f64                 // Explicit: i32 → f64 + i64 → f64
}
```

## Complex Expression Resolution

Complex expressions follow the same TYPE_SYSTEM.md patterns as simple operations:

```hexen
val a : i32 = 10
val b : i64 = 20
val c : f32 = 3.14

// ❌ Error: Mixed types require explicit conversions
// val result = a + b * c

// ✅ Explicit conversions for mixed concrete types
val result : f64 = a:f64 + (b:f64 * c:f64)  // Explicit: i32 → f64 + (i64 → f64 * f32 → f64)

// ✅ Explicit conversions work too
val result2 = a:f64 + b:f64 * c:f64  // All explicit conversions
```

## Grammar Extensions

### Lark Grammar for Binary Operations

```lark
// Current expression rule
expression: NUMBER | STRING | BOOLEAN | IDENTIFIER | block

// Extended expression rule with binary operations
expression: binary_expr

binary_expr: logical_or

logical_or: logical_and (("||") logical_and)*
logical_and: equality (("&&") equality)*
equality: relational (("==" | "!=") relational)*
relational: additive (("<" | ">" | "<=" | ">=") additive)*
additive: multiplicative (("+" | "-") multiplicative)*
multiplicative: unary (("*" | "/" | "\\" | "%") unary)*
unary: ("-" | "!")? primary
primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")"
```

### AST Node Structure

Binary operations create AST nodes with this structure:

```python
{
    "type": "binary_operation",
    "operator": "+",  # The operator: +, -, *, /, %, <, >, <=, >=, ==, !=, &&, ||
    "left": {...},    # Left operand (expression)
    "right": {...},   # Right operand (expression)
}
```


