# Hexen Type System 🦉

*Design Exploration & Specification*

> **Experimental Note**: This document describes our exploration into type system design. We're experimenting with different approaches to type coercion and literal handling, documenting our journey to share with the community and gather insights. These ideas are part of our learning process in language design.

## Overview

Hexen's type system is designed around two core principles: **"Ergonomic Literals"** and **"Transparent Costs"** - making common literal usage seamless while keeping all computational costs visible. This philosophy aims to create a system where everyday coding feels natural, but performance-critical conversions are always explicit and visible.

## Core Philosophy

### Design Principle: Ergonomic Literals + Transparent Costs

Hexen follows a simple, unified pattern that makes common cases ergonomic while keeping all costs visible:

- **Ergonomic Literals**: Comptime types adapt seamlessly to context (no syntax burden)
- **Transparent Costs**: All concrete type mixing requires explicit syntax (`value:type`)
- **Natural Usage**: Common literal patterns work without ceremony (`42`, `3.14`)
- **Visible Conversions**: Performance costs are always explicit in the code
- **Predictable Rules**: Same simple pattern everywhere (minimal cognitive load)

This philosophy aims to ensure that **everyday coding feels natural**, while **performance-critical conversions** are always explicit and visible.

## Variable Declaration Keywords

Before diving into the type system, it's essential to understand Hexen's two variable declaration keywords that you'll see throughout this document:

### `val` - Immutable Variables (Values)
The `val` keyword declares **immutable variables** - variables that can only be assigned once at declaration:

```hexen
val message = "Hello, World!"    // ✅ Immutable variable
val count = 42                   // ✅ Single assignment at declaration
// count = 43                    // ❌ Error: Cannot reassign val variable
```

**Key characteristics:**
- **Single assignment**: Can only be set once (at declaration)
- **Type inference allowed**: Can omit type annotation when using comptime literals
- **Name origin**: "val" stands for **"value"** - representing a single, unchanging value

### `mut` - Mutable Variables
The `mut` keyword declares **mutable variables** - variables that can be reassigned after declaration:

```hexen
mut counter : i32 = 0           // ✅ Mutable variable with explicit type
counter = 42                    // ✅ Reassignment allowed
counter = 100                   // ✅ Multiple reassignments allowed
```

**Key characteristics:**
- **Multiple assignments**: Can be reassigned as many times as needed
- **Explicit type required**: Must specify type annotation to prevent action-at-a-distance effects
- **Name origin**: "mut" stands for **"mutable"** - representing a changeable variable

### Why Two Keywords?

This distinction serves important design goals:

1. **Safety by Default**: `val` encourages immutable-first programming
2. **Clear Intent**: The keyword immediately tells you if a variable can change
3. **Type System Benefits**: Different rules for type inference and comptime type preservation
4. **Performance**: Compiler can optimize better knowing what can/cannot change

### Usage Guidelines

- **Use `val`** for: Constants, computed results, configuration values that don't change
- **Use `mut`** for: Counters, accumulators, state variables that need updates

```hexen
// ✅ Good usage patterns
val config_file = "app.toml"        // Configuration - doesn't change
val result = compute_expensive()     // Computed result - doesn't change  
mut counter : i32 = 0               // Counter - will be incremented
mut buffer : string = ""            // Buffer - will be appended to

// ❌ Poor usage patterns  
mut constant_pi : f64 = 3.14159     // Should be val - never changes
val accumulator : i32 = 0           // Should be mut - probably needs updates
```

Now that you understand `val` and `mut`, let's explore how they interact with Hexen's type system.

## Type Hierarchy

### Concrete Types

| Type | Description | Size | Range |
|------|-------------|------|-------|
| `i32` | 32-bit signed integer | 4 bytes | -2,147,483,648 to 2,147,483,647 |
| `i64` | 64-bit signed integer | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 |
| `f32` | 32-bit IEEE 754 float | 4 bytes | ±1.18×10⁻³⁸ to ±3.40×10³⁸ |
| `f64` | 64-bit IEEE 754 float | 8 bytes | ±2.23×10⁻³⁰⁸ to ±1.80×10³⁰⁸ |
| `string` | UTF-8 string | Variable | Arbitrary length |
| `bool` | Boolean value | 1 byte | `true` or `false` |
| `void` | No value (functions only) | 0 bytes | N/A |

**⚠️ Overflow Protection**: Literals that exceed these ranges trigger compile-time errors. See **[LITERAL_OVERFLOW_BEHAVIOR.md](LITERAL_OVERFLOW_BEHAVIOR.md)** for details.

### Comptime Types (Compile-Time Only)

| Type | Description | Purpose |
|------|-------------|---------|
| `comptime_int` | Integer literals | Context-dependent coercion to any numeric type |
| `comptime_float` | Float literals | Context-dependent coercion to float types |

**📋 Important**: For detailed information about literal overflow behavior and compile-time safety guarantees, see **[LITERAL_OVERFLOW_BEHAVIOR.md](LITERAL_OVERFLOW_BEHAVIOR.md)**.

### Special Types (Internal)

| Type | Description | Usage |
|------|-------------|-------|
| `unknown` | Type inference failure | Error handling |
| `undef` | Uninitialized variable | Explicit uninitialized state |

## Comptime Type System

> **🚀 Quick Start**: New to comptime types? Check out the **[Comptime Quick Reference →](COMPTIME_QUICK_REFERENCE.md)** for essential patterns and mental models!

### The Problem: Literal Type Ambiguity

In most systems programming languages, numeric literals face a fundamental problem:

```c
// C/C++ - requires explicit suffixes or casting
int32_t a = 42;        // OK, but what if we want i64?
int64_t b = 42L;       // Requires suffix
float c = 42.0f;       // Requires suffix
double d = 42.0;       // OK, but inconsistent with int

// Rust - requires explicit types or suffixes
let a: i32 = 42;       // OK, but what if we want i64?
let b = 42i64;         // Requires suffix
let c = 42.0f32;       // Requires suffix
```

This creates three problems:
1. **Suffix Hell**: Remembering and typing suffixes for every literal
2. **Inflexibility**: Hard to change types without updating all literals
3. **Inconsistency**: Different rules for integers vs floats

### Our Experimental Solution: Adaptive Literals with Explicit Concrete Conversions

Hexen explores solving this with **comptime types** - special types that literals have initially, which adapt to context. For concrete types, all conversions are explicit:

**📋 Overflow Safety**: Hexen follows Zig's approach for literal overflow detection. See **[LITERAL_OVERFLOW_BEHAVIOR.md](LITERAL_OVERFLOW_BEHAVIOR.md)** for complete safety guarantees.

```hexen
// ✨ Comptime literals adapt seamlessly (ergonomic)
val small : i32 = 42    // comptime_int → i32 (implicit, no cost)
val large : i64 = 42    // comptime_int → i64 (implicit, no cost)
val precise : f64 = 42  // comptime_int → f64 (implicit, no cost)
val double : f64 = 3.14 // comptime_float → f64 (implicit, no cost)
val single : f32 = 3.14 // comptime_float → f32 (implicit, no cost)

// 🔧 All concrete conversions are explicit (transparent costs)
val converted : i32 = float_val:i32     // f64 → i32 (explicit conversion, visible cost)
val widened : i64 = int_val:i64         // i32 → i64 (explicit conversion, visible cost)
```

### How Comptime Types Work

#### Step 1: Literal Parsing
When the parser encounters a literal, it assigns a **comptime type**:

```hexen
42      // Gets type: comptime_int
-123    // Gets type: comptime_int
3.14    // Gets type: comptime_float
-2.5    // Gets type: comptime_float
```

#### Step 2: Context Resolution
During type checking, comptime types look at their **usage context** and adapt:

```hexen
// Context comes from variable declaration
val counter : i32 = 42       // comptime_int → i32 (safe, implicit)
val big_counter : i64 = 42   // comptime_int → i64 (safe, implicit)
val percentage : f32 = 42    // comptime_int → f32 (safe, implicit)

// Context comes from function parameters
func process_data(count: i64) { ... }
process_data(1000)               // comptime_int sees i64 parameter → becomes i64

// Context comes from return types
func get_count() : i32 = {       // return type provides context
    return 42                    // comptime_int sees i32 return → becomes i32
}
```

#### Step 3: Comptime Type Preservation
When there's **no explicit type context**, comptime types **preserve flexibility**:

```hexen
// val allows comptime type preservation (flexibility)
val flexible_int = 42      // comptime_int (preserved - can adapt to any numeric context later!)
val flexible_float = 3.14  // comptime_float (preserved - can adapt to f32/f64 context later!)

// Later usage provides context for resolution
val small : i32 = flexible_int     // NOW comptime_int → i32 (context-driven)
val large : i64 = flexible_int     // SAME source → i64 (different context!)
val precise : f64 = flexible_int   // SAME source → f64 (flexible adaptation!)

// mut requires explicit type (prevents action-at-a-distance)
mut counter : i32 = 42      // ✅ Explicit type required
mut pi : f64 = 3.14         // ✅ Explicit type required
// mut bad_counter = 42     // ❌ Error: mut requires explicit type
// mut bad_pi = 3.14        // ❌ Error: mut requires explicit type
```

**Key Insight**: Comptime types **stay flexible until forced** - they don't automatically become concrete types!

#### An Experimental Approach: Flexibility Preservation

We're exploring an approach that prioritizes **flexibility preservation over premature resolution**:

**❌ Traditional Approach**: "Literals have default types"
- `42` is always `int` (or requires suffixes like `42L`)
- Hard to change types without updating all literals
- Rigid, requires explicit casting everywhere

**✅ Our Experimental Approach**: "Literals preserve flexibility"
- `42` stays `comptime_int` until context forces resolution
- Same literal adapts to any compatible context
- Ergonomics with zero performance cost

**This enables interesting patterns:**
```hexen
val magic_number = 42 * 1000 + 500     // Stays comptime_int (flexible!)

// Later, same expression used in different contexts:
val config_id : i32 = magic_number     // Resolves to i32
val timestamp : i64 = magic_number     // Same expr, resolves to i64  
val ratio : f64 = magic_number         // Same expr, resolves to f64

// Function calls get the right types automatically:
process_i32(magic_number)              // Resolves to i32 for function parameter
process_i64(magic_number)              // Resolves to i64 for function parameter
```

**Result**: Write code once, use everywhere - the type system adapts to your needs instead of forcing you to adapt to the type system.

#### The Critical Boundary: Concrete Types Cannot Become Comptime

While comptime types can adapt to any compatible concrete type, **the reverse is forbidden**. Once a value becomes concrete (from function calls, runtime computation, etc.), it cannot be forced back into comptime:

```hexen
// ✅ Comptime → Concrete (Always Allowed)
val flexible = 42           // comptime_int
val concrete : i32 = flexible   // comptime_int → i32 (✅ context-driven)

// ❌ Concrete → Comptime (Always Forbidden)
val runtime_result : i32 = compute_value()  // Explicit type required for concrete values!
// comptime val bad = runtime_result        // ❌ Error: Cannot use runtime value in comptime context
// val bad : comptime_int = runtime_result  // ❌ Error: Cannot coerce concrete i32 to comptime_int

// ✅ Concrete → Concrete (Explicit Types Required)
val runtime_result : i32 = compute_value()  // ✅ Explicit type required for concrete values
val another : i32 = runtime_result          // i32 → i32 (identity, no conversion)
val widened : i64 = runtime_result:i64      // i32 → i64 (explicit conversion required)

// ✅ Mixed: Concrete + Comptime (Comptime Adapts)
val runtime_result : i32 = compute_value()  // ✅ Explicit type required for concrete values
val mixed : i32 = runtime_result + 100      // i32 + comptime_int → i32 (comptime adapts to i32)
```

**Comparison Example - Comptime vs Concrete Sources:**
```hexen
// ===== COMPTIME SOURCE (Flexible Adaptation) =====
val flexible_math = 42 + 100               // comptime_int (stays flexible!)
val as_i32 : i32 = flexible_math           // comptime_int → i32 ✅
val as_i64 : i64 = flexible_math           // Same source → i64 ✅
val as_f64 : f64 = flexible_math           // Same source → f64 ✅

// ===== CONCRETE SOURCE (No Flexibility) =====
val concrete_math : i32 = compute_value() + other_value()  // Explicit type required! i32 + i32 → i32 (concrete result)
val copy : i32 = concrete_math             // i32 → i32 ✅ (identity)
val widened : i64 = concrete_math:i64      // i32 → i64 ✅ (explicit conversion required)
// val bad : comptime_int = concrete_math  // ❌ Error: Cannot force concrete into comptime
```

**Key Insights**: 
1. **Flexibility flows one direction only** - from comptime to concrete, never the reverse
2. **Comptime types**: Get type inference (`val x = 42`) - flexible adaptation  
3. **Concrete types**: Require explicit types (`val x : i32 = compute()`) - transparent costs
4. This maintains the compile-time/runtime boundary while maximizing ergonomics

### Design Philosophy

The comptime system embodies Hexen's **"Ergonomic Literals + Transparent Costs"** principle:

- **Ergonomic Literals**: Comptime types adapt seamlessly (no conversion cost at runtime)
- **Explicit Conversions**: All concrete type mixing requires visible syntax
- **Cost Visibility**: Every conversion is transparent in the code
- **Predictable Rules**: Simple, consistent behavior everywhere

#### **The Safe vs Unsafe Conversion Rule**

Comptime types can coerce **implicitly** to all types in their allowed table:

**comptime_int → All Numeric Types (Implicit)**
```hexen
val a : i32 = 42    // ✅ Safe: comptime_int → i32 (implicit)
val b : i64 = 42    // ✅ Safe: comptime_int → i64 (implicit)
val c : f32 = 42    // ✅ Safe: comptime_int → f32 (implicit)
val d : f64 = 42    // ✅ Safe: comptime_int → f64 (implicit)
```

**comptime_float → Float Types Only (Implicit)**
```hexen
val e : f32 = 3.14  // ✅ Safe: comptime_float → f32 (implicit)
val f : f64 = 3.14  // ✅ Safe: comptime_float → f64 (implicit)
```

**Outside the Table = Explicit Conversion Required**
```hexen
// ❌ Unsafe conversions require explicit conversion
// val g : i32 = 3.14      // Error: comptime_float → i32 requires ':i32'
// val h : i64 = 3.14      // Error: comptime_float → i64 requires ':i64'

// ✅ Explicit conversion of unsafe operations
val g : i32 = 3.14:i32   // comptime_float → i32 (explicit truncation)
val h : i64 = 3.14:i64   // comptime_float → i64 (explicit truncation)
```

**Why this rule matters:**
- **Clear Safety Boundary**: Everything in the table is guaranteed safe
- **Explicit Danger**: Conversions that lose data require explicit conversion
- **No Arbitrary Restrictions**: All safe conversions work seamlessly
- **Consistent Pattern**: Same explicit conversion pattern for all unsafe operations

### Implementation Mental Model

Think of comptime types as "adaptive literals" that preserve flexibility: *"I'll stay flexible until you need me to be concrete!"*

1. **Parser**: Creates comptime_int/comptime_float for all numeric literals
2. **Type Checker**: Preserves comptime types until explicit context forces resolution
3. **Resolution**: Only happens when comptime meets concrete type or explicit annotation
4. **Error**: If conversion is unsafe or context requires explicit choice, compilation fails with helpful message

Think of comptime types as "maximally flexible values":
```hexen
val flexible = 42 + 100    // Stays comptime_int (preserved!)
val small : i32 = flexible    // NOW resolves to i32 (context forces resolution)
val large : i64 = flexible    // SAME source, different target (flexible adaptation!)
```

**Key insight**: Comptime types **preserve flexibility** rather than resolve to defaults. The same comptime expression can resolve to different concrete types based on usage context.

This aims to create a clean, consistent system where literals stay flexible until context demands specificity, balancing both ergonomics and type safety.

### Context Propagation Examples

Comptime types work seamlessly in function calls and complex expressions:

```hexen
// Function parameters provide context for literals
func process_data(count: i64, threshold: f32) : void = {
    // Function body uses parameters (implementation not shown)
}

// Literals adapt to parameter types automatically
process_data(1000, 2.5)       // 1000→i64, 2.5→f32 (comptime adaptation)

// Return type provides context too
func get_count() : i32 = {             // return type provides context
    return 42                          // comptime_int adapts to i32 return type
}
func get_ratio() : f64 = {             // return type provides context
    return 3.14                        // comptime_float adapts to f64 return type
}

// Variable declarations provide context
val precise : f64 = 42 + 100           // comptime_int + comptime_int → comptime_int → f64 (context-driven)
val integer : i32 = 42 + 100           // comptime_int + comptime_int → comptime_int → i32 (context-driven)

// Same expression, different contexts - demonstrating flexibility!
val arithmetic = 10 * 20 + 5           // comptime_int (preserved until context forces resolution)
val as_small : i32 = arithmetic        // NOW resolves to i32 based on target type
val as_precise : f64 = arithmetic      // SAME expr, different resolution!
```

## Type Conversion Rules

### 1. Identity (No Conversion Needed)
Same types work automatically:
```hexen
val x : i32 = some_i32_value  // i32 → i32 (no conversion)
val y : f64 = some_f64_value  // f64 → f64 (no conversion)
```

### 2. Comptime Type Magic (Ergonomic Literals)

**comptime_int** can adapt to:
- `i32`, `i64` (integer types)
- `f32`, `f64` (float types)
- **Cannot** adapt to `bool`, `string` (not meaningful)

**comptime_float** can adapt to:
- `f32`, `f64` (float types)
- **Cannot** adapt to `bool`, `string`, `i32`, `i64` (not meaningful without explicit conversion)

```hexen
// ✅ Comptime literals adapt seamlessly (ergonomic)
val int_var : i32 = 42      // comptime_int → i32 (implicit, no cost)
val float_var : f64 = 42    // comptime_int → f64 (implicit, no cost)
val precise : f32 = 3.14    // comptime_float → f32 (implicit, no cost)

// ❌ Comptime types that don't make sense (compilation errors)
// val bad_bool : bool = 42        // Error: use explicit logic instead
// val bad_string : string = 3.14  // Error: not meaningful
// val bad_int : i32 = 3.14        // Error: use explicit conversion

// ✅ Explicit conversions when needed
val explicit_int : i32 = 3.14:i32   // comptime_float → i32 (explicit conversion)
val explicit_logic : bool = (42 != 0)  // Explicit boolean logic
```

### 3. Concrete Type Conversions (All Explicit)

For concrete (non-comptime) types, **all conversions require explicit syntax**:

```hexen
// 🔧 All concrete conversions are explicit (transparent costs)
val widened : i64 = i32_value:i64       // i32 → i64 (explicit widening)
val precise : f64 = f32_value:f64       // f32 → f64 (explicit widening)
val converted : f32 = i32_value:f32     // i32 → f32 (explicit conversion)
val narrowed : i32 = i64_value:i32      // i64 → i32 (explicit narrowing, potential data loss)
val truncated : i32 = f64_value:i32     // f64 → i32 (explicit truncation, data loss)

// ❌ No automatic widening or conversion
// val auto_wide : i64 = i32_value      // Error: use i32_value:i64
// val auto_convert : f64 = f32_value   // Error: use f32_value:f64
```

**Conversion Philosophy:**
- **All costs visible**: Every conversion is explicit in the code
- **No surprises**: No hidden performance costs or data loss
- **Uniform syntax**: `value:target_type` for all concrete conversions

## Type Conversion Rules Summary

### Quick Reference Table

| From Type | To Type | Conversion | Required Syntax | Notes |
|-----------|---------|------------|-----------------|-------|
| **Comptime Types (Ergonomic Literals)** |
| `comptime_int` | `comptime_int` | ✅ Preserved | `val x = 42` | Comptime type preserved (flexible adaptation!) |
| `comptime_int` | `i32` | ✅ Implicit | `val x : i32 = 42` | No cost, ergonomic |
| `comptime_int` | `i64` | ✅ Implicit | `val x : i64 = 42` | No cost, ergonomic |
| `comptime_int` | `f32` | ✅ Implicit | `val x : f32 = 42` | No cost, ergonomic |
| `comptime_int` | `f64` | ✅ Implicit | `val x : f64 = 42` | No cost, ergonomic |
| `comptime_int` | `bool` | ❌ Forbidden | N/A | Use explicit logic: `(42 != 0)` |
| `comptime_int` | `string` | ❌ Forbidden | N/A | Not meaningful |
| `comptime_float` | `comptime_float` | ✅ Preserved | `val x = 3.14` | Comptime type preserved (flexible adaptation!) |
| `comptime_float` | `f32` | ✅ Implicit | `val x : f32 = 3.14` | No cost, ergonomic |
| `comptime_float` | `f64` | ✅ Implicit | `val x : f64 = 3.14` | No cost, ergonomic |
| `comptime_float` | `i32` | 🔧 Explicit | `val x : i32 = 3.14:i32` | Conversion cost visible |
| `comptime_float` | `i64` | 🔧 Explicit | `val x : i64 = 3.14:i64` | Conversion cost visible |
| `comptime_float` | `bool` | ❌ Forbidden | N/A | Use explicit logic: `(3.14 != 0.0)` |
| `comptime_float` | `string` | ❌ Forbidden | N/A | Not meaningful |
| **Concrete Types (All Explicit)** |
| `i32` | `i64` | 🔧 Explicit | `val x : i64 = i32_val:i64` | Conversion cost visible |
| `i32` | `f32` | 🔧 Explicit | `val x : f32 = i32_val:f32` | Conversion cost visible |
| `i32` | `f64` | 🔧 Explicit | `val x : f64 = i32_val:f64` | Conversion cost visible |
| `i64` | `i32` | 🔧 Explicit | `val x : i32 = i64_val:i32` | Conversion + data loss visible |
| `i64` | `f32` | 🔧 Explicit | `val x : f32 = i64_val:f32` | Conversion + precision loss visible |
| `i64` | `f64` | 🔧 Explicit | `val x : f64 = i64_val:f64` | Conversion cost visible |
| `f32` | `f64` | 🔧 Explicit | `val x : f64 = f32_val:f64` | Conversion cost visible |
| `f64` | `f32` | 🔧 Explicit | `val x : f32 = f64_val:f32` | Conversion + precision loss visible |
| `f32` | `i32` | 🔧 Explicit | `val x : i32 = f32_val:i32` | Conversion + data loss visible |
| `f64` | `i32` | 🔧 Explicit | `val x : i32 = f64_val:i32` | Conversion + data loss visible |
| `f32` | `i64` | 🔧 Explicit | `val x : i64 = f32_val:i64` | Conversion + data loss visible |
| `f64` | `i64` | 🔧 Explicit | `val x : i64 = f64_val:i64` | Conversion + data loss visible |
| **Identity (No Conversion)** |
| Any type | Same type | ✅ Identity | `val x : i32 = i32_val` | No conversion needed |
| **Forbidden Conversions** |
| Any numeric | `bool` | ❌ Forbidden | N/A | Use explicit comparison: `(value != 0)` |
| Any numeric | `string` | ❌ Forbidden | N/A | Use string formatting functions |
| `bool` | Any numeric | ❌ Forbidden | N/A | Use conditional expression |
| `string` | Any numeric | ❌ Forbidden | N/A | Use parsing functions |

### Legend

- **✅ Preserved**: Comptime type stays flexible, maximum adaptability (comptime types only)
- **✅ Implicit**: Happens automatically, no conversion cost (comptime types only)
- **🔧 Explicit**: Requires explicit syntax (`value:type`), conversion cost visible
- **❌ Forbidden**: Not allowed, compilation error

## Binary Operations

Binary operations in Hexen follow the **explicit conversion** strategy with transparent cost visibility. All concrete type mixing requires explicit conversions. Due to the complexity and importance of this topic, it has been moved to a dedicated specification:

**→ See [BINARY_OPS.md](BINARY_OPS.md) for complete binary operations specification**

Key highlights:
- **Explicit conversions**: All concrete type mixing requires `value:type` syntax
- **Cost transparency**: Every conversion is visible in the code
- **Comptime adaptation**: Literals adapt seamlessly (ergonomic for common cases)
- **No hidden costs**: No automatic widening or promotion
- **Predictable rules**: Simple, consistent behavior everywhere
- **Implementation guidelines** for semantic analyzer

## Assignment and Context

### Variable Declaration Types: `val` vs `mut`

Hexen provides two variable declaration keywords with distinct mutability characteristics:

#### **`val` - Immutable Variables**
- **Single Assignment**: Can only be assigned once at declaration
- **Compile-time Enforcement**: Reassignment attempts cause compilation errors
- **Type Context**: Target type provides context for comptime literal adaptation
- **Use Case**: Constants, configuration values, computed results that shouldn't change

```hexen
val config : string = "production"     // ✅ OK: initialization
val result : i32 = compute_value()     // ✅ OK: initialization with function call
val derived : f64 = result * 2.5       // ✅ OK: initialization with expression

// config = "development"              // ❌ Error: Cannot reassign val variable
// result = 42                         // ❌ Error: Cannot reassign val variable
```

#### **`mut` - Mutable Variables**
- **Multiple Assignment**: Can be reassigned after declaration
- **Explicit Type Required**: Must have explicit type annotation to prevent action-at-a-distance issues
- **Type Preservation**: Must maintain the same declared type across reassignments
- **Type Context**: Explicit type provides context for all reassignments
- **Use Case**: Counters, accumulators, state variables that need to change

```hexen
mut counter : i32 = 0                  // ✅ OK: explicit type required
counter = 42                           // ✅ OK: comptime_int adapts to i32 context
counter = compute_value()              // ✅ OK: if compute_value() returns i32
counter = large_value:i32              // ✅ OK: explicit conversion (e.g., i64 → i32)

// mut bad_counter = 0                 // ❌ Error: mut requires explicit type
// counter = "text"                    // ❌ Error: Cannot change type (i32 → string)
// counter = float_val                 // ❌ Error: use float_val:i32 for explicit conversion
```

#### **Key Principle: Different Safety Models for Different Use Cases**
- **`val` variables**: Type inference allowed since declaration = only use (enables comptime type preservation)
- **`mut` variables**: Explicit type required since type affects all future reassignments (prevents comptime type preservation)

**Design rationale**: `mut` variables require explicit types to prevent "action at a distance" where changing the initial assignment value could silently change the meaning of all subsequent reassignments.

**🔴 Critical Consequence**: This design choice means **`mut` variables can never preserve comptime types** - they sacrifice flexibility for safety. Only `val` declarations can preserve comptime types for later context-dependent resolution.

### Variable Declaration with Context

The target type of a variable declaration provides context for expression analysis:

```hexen
// Target type guides expression resolution
val precise : f64 = 42      // comptime_int → f64
val integer : i32 = 42      // comptime_int → i32
val float_val : f32 = 3.14  // comptime_float → f32
```

### Assignment with Context

Assignment statements use the target variable's type as context:

```hexen
mut flexible : f64 = 0.0
flexible = 42               // comptime_int → f64 (assignment context)
```

For detailed rules about assignment context, type annotations, and mixed type operations, see [BINARY_OPS.md](BINARY_OPS.md).

## Reassignment and Type Annotations

### Mutable Variable Reassignment

Mutable variables (`mut`) can be reassigned while maintaining their declared type. The target type provides context for all assignments, and comptime types adapt naturally to this context.

#### Basic Reassignment

```hexen
// Integer reassignment
mut counter : i32 = 0
counter = 42                // comptime_int → i32
counter = -100             // comptime_int → i32
counter = 65535            // comptime_int → i32

// Float reassignment
mut precise : f32 = 0.0
precise = 3.14             // comptime_float → f32
precise = -2.5             // comptime_float → f32
precise = 0.0001           // comptime_float → f32

// String reassignment
mut message : string = ""
message = "hello"          // string → string
message = "world"          // string → string

// Boolean reassignment
mut flag : bool = false
flag = true                // bool → bool
flag = false               // bool → bool
```

#### Type-Specific Rules

Each type has specific reassignment rules:

```hexen
// Integer types
mut small : i32 = 0
mut large : i64 = 0

// Safe integer reassignments
small = 42                 // comptime_int → i32
large = 42                 // comptime_int → i64
large = 4294967295        // comptime_int → i64

// Float types
mut single : f32 = 0.0
mut double : f64 = 0.0

// Safe float reassignments
single = 3.14              // comptime_float → f32
double = 3.14              // comptime_float → f64
double = 3.14159265359     // comptime_float → f64
```

### Explicit Conversions for Mixed Types  

When reassignment involves different concrete types, explicit conversions are required. This makes all computational costs visible and prevents accidental data loss.

#### Integer Conversions

```hexen
mut small : i32 = 0
val large : i64 = 9223372036854775807  // Maximum i64 value

// ❌ Error: No automatic conversion between concrete types
// small = large                        // Error: use explicit conversion large:i32

// ✅ Explicit conversion with visible cost
small = large:i32                      // Explicit: i64 → i32 conversion (potential data loss)
small = 9223372036854775807:i32        // Explicit: comptime_int → i32 conversion
```

#### Float Conversions

```hexen
mut single : f32 = 0.0
val double : f64 = 3.141592653589793   // More precise than f32 can represent

// ❌ Error: No automatic conversion between concrete types
// single = double                      // Error: use explicit conversion double:f32

// ✅ Explicit conversion with visible cost
single = double:f32                    // Explicit: f64 → f32 conversion (precision loss)
single = 3.141592653589793:f32         // Explicit: comptime_float → f32 conversion
```

#### Cross-Type Conversions

```hexen
mut precise : f32 = 0.0
val big_int : i64 = 9223372036854775807

// ❌ Error: No automatic conversion between different concrete types
// precise = big_int                    // Error: use explicit conversion big_int:f32

// ✅ Explicit conversion with visible cost
precise = big_int:f32                  // Explicit: i64 → f32 conversion (precision loss)
precise = 9223372036854775807:f32      // Explicit: comptime_int → f32 conversion
```

### Explicit Conversion Syntax

All concrete type conversions use the `value:type` syntax for maximum transparency:

#### **Fundamental Rule: Visible Conversion Costs**
The `value:type` syntax makes every conversion explicit and visible:
- **Position**: Immediately after the value being converted
- **Purpose**: Transparent type conversion with visible cost
- **Scope**: Applies to the value immediately before the colon

```hexen
// ✅ Explicit conversion syntax
val widened : i64 = i32_val:i64         // i32 → i64 conversion (visible cost)
val converted : f32 = i64_val:f32       // i64 → f32 conversion (visible cost)
val narrowed : i32 = i64_val:i32        // i64 → i32 conversion (visible data loss)

// ❌ No automatic conversions
// val auto_wide : i64 = i32_val        // Error: use i32_val:i64
// val auto_narrow : i32 = i64_val      // Error: use i64_val:i32
```

#### **Design Philosophy**
1. **Cost Transparency**: Every conversion is visible in the code
2. **No Hidden Behavior**: No automatic conversions between concrete types
3. **Explicit Choice**: Developer must consciously choose all conversions
4. **Uniform Syntax**: Same `value:type` pattern everywhere
5. **Performance Clarity**: Conversion costs are obvious
6. **Safety**: Prevents accidental data loss through explicit conversion
7. **Simplicity**: One rule, no exceptions

#### **The Universal Pattern**
```hexen
// Every conversion follows this exact pattern:
target_variable : target_type = source_value:target_type

// Examples across all contexts:
val converted : f32 = int_val:f32       // Variable declaration
mut counter : i32 = large_val:i32       // Reassignment
func process(x: i32) = big_val:i32      // Function argument
array[index] = float_val:i32            // Array assignment
```

#### **Expression Context**
Conversions work naturally in complex expressions:

```hexen
// Conversions in expressions
val result : f64 = (int_val:f64 + float_val:f64) / 2.0:f64
val mixed : i32 = (a:i32 + b:i32) * c:i32
val complex : f32 = sqrt(x:f32 * x:f32 + y:f32 * y:f32)

// Conversions with function calls
val processed : i64 = compute_value():i64
val formatted : string = format_number(value:f64)
```

**Key Points:**
- `value:type` is **always** a conversion operation
- Conversions can be **chained**: `value:intermediate:final`
- **Comptime types** don't need conversion syntax (they adapt automatically)
- **Same types** don't need conversion syntax (identity is free)
- This pattern works **everywhere** in Hexen - no exceptions

### Error Messages

Error messages for type mismatches follow a consistent pattern, providing clear guidance:

```hexen
mut small : i32 = 0
val large : i64 = 9223372036854775807

// ❌ Error messages with guidance
// small = large
// Error: Cannot assign i64 to i32 variable
// Use explicit conversion: large:i32

// small = 3.14159
// Error: Cannot assign comptime_float to i32 variable
// Use explicit conversion: 3.14159:i32

// ✅ Following the guidance
small = large:i32                       // Explicit conversion (potential data loss)
small = 3.14159:i32                     // Explicit conversion (truncation)
```

### Benefits

1. **Cost Transparency**: All conversion costs are visible in the code
2. **Type Safety**: All type conversions are explicit and intentional
3. **Performance Clarity**: No hidden conversions or unexpected costs
4. **Error Prevention**: Accidental type mismatches caught at compile time
5. **Maintainability**: Clear documentation of every conversion
6. **Predictability**: Simple, consistent rules with no exceptions
7. **Ergonomic Literals**: Comptime types adapt seamlessly for common cases

## Uninitialized Variables (`undef`)

### Philosophy Consistency

The `undef` system follows the same **"cost transparency"** principle:

```hexen
// ❌ Implicit undef (ambiguous - no type info)
mut pending = undef             // Error: Cannot infer type

// ✅ Explicit undef (clear - type specified)
mut pending : i32 = undef       // OK: Type explicitly provided
mut config : string = undef     // OK: Type explicitly provided
```

### undef with Type Conversions

Uninitialized variables follow the same conversion rules once assigned:

```hexen
mut value : i32 = undef
value = 42                      // comptime_int adapts to i32 (ergonomic)
value = large_val:i32          // explicit conversion (visible cost)
value = 10 + 20                // comptime arithmetic adapts to i32 (ergonomic)
```

### `undef` with `val` vs `mut` Variables

The `undef` keyword works differently with immutable and mutable variables:

#### **`val` with `undef` - Not Allowed (Use Expression Blocks Instead)**
```hexen
val config : string = undef        // ❌ Error: val + undef creates unusable variable
val result : i32 = undef           // ❌ Error: val + undef creates unusable variable

// Later assignments would break immutability:
// config = "production"           // ❌ Error: val variables cannot be reassigned
// result = compute_value()        // ❌ Error: val variables cannot be reassigned
```

**Why this is forbidden**: `val` variables with `undef` create a contradiction:
- `val` variables can only be assigned once (at declaration)
- `undef` requires a later assignment to become usable
- This breaks the immutability contract

**✅ Use Expression Blocks Instead**: For complex initialization, use Hexen's expression blocks:
```hexen
// ✅ Complex initialization with expression blocks
val config : string = {
    if development_mode {
        return "development"
    } else {
        return "production"
    }
}

val result : i32 = {
    // Setup work in statement block (scoped)
    {
        val temp_data : string = load_data()  // Explicit type required for concrete values!
        validate(temp_data)                   // Runtime function call
    }
    
    // Complex computation with concrete values
    val base : i32 = expensive_computation()  // Explicit type required for concrete values!
    val factor : i32 = multiplier_factor()    // Explicit type required for concrete values!
    return base * factor                       // i32 * i32 → i32 (concrete arithmetic)
}
```

**→ See [UNIFIED_BLOCK_SYSTEM.md](UNIFIED_BLOCK_SYSTEM.md) for complete details on expression blocks and complex initialization patterns**

#### **`mut` with `undef` - Proper Deferred Initialization**
```hexen
mut config : string = undef        // ✅ OK: deferred initialization
mut result : i32 = undef           // ✅ OK: deferred initialization

// Later assignments are allowed:
config = "production"              // ✅ OK: first real assignment
result = compute_value()           // ✅ OK: first real assignment
result = 42                        // ✅ OK: subsequent reassignment
```

#### **Design Rationale**
- **`val` + `undef`**: Creates an unusable variable (cannot be assigned later)
- **`mut` + `undef`**: Enables proper deferred initialization patterns
- **Type Safety**: Both require explicit type annotation (`undef` alone is not allowed)
- **Consistency**: Follows the mutability contract - `val` = single assignment, `mut` = multiple assignments

## Error Messages

### Consistency with undef Pattern

Error messages follow the same pattern as `undef` errors, pointing to the same solution:

#### Type Coercion Errors
```
Type mismatch: variable 'x' declared as i32 but assigned value of type comptime_float
```

#### Mixed Operation Errors  
```
Mixed-type operation 'i32 + i64' requires explicit conversions
Use explicit conversions: 'val result = i32_val:i64 + i64_val' or 'val result = i32_val:f64 + i64_val:f64'
```

#### undef Errors
```
Variable 'pending' must have either explicit type or value
```

#### val Reassignment Errors
```
Cannot reassign immutable variable 'config': val variables can only be assigned once at declaration
```

#### val + undef Errors
```
Invalid usage: val variable 'result' declared with undef cannot be assigned later
Consider using 'mut result : i32 = undef' for deferred initialization
```

All errors suggest appropriate solutions: **add explicit type annotation** or **choose correct mutability keyword**.

## Examples

### Core Type System Concepts

```hexen
func demonstrate_type_system() : void = {
    // ===== Comptime Type Magic (Ergonomic Literals) =====
    val flexible_int = 42       // comptime_int (preserved - flexible adaptation!)
    val explicit_i64 : i64 = 42 // comptime_int → i64 (context-driven, no cost)
    val as_float : f32 = 42     // comptime_int → f32 (context-driven, no cost)
    val flexible_float = 3.14   // comptime_float (preserved - flexible adaptation!)
    val single : f32 = 3.14     // comptime_float → f32 (context-driven, no cost)
    
    // ===== Critical Difference: val vs mut Comptime Type Preservation =====
    // ✅ val preserves comptime types (flexible adaptation)
    val preserved_math = 42 + 100 * 5      // comptime_int (stays flexible!)
    val as_different_i32 : i32 = preserved_math    // SAME source → i32
    val as_different_i64 : i64 = preserved_math    // SAME source → i64 
    val as_different_f64 : f64 = preserved_math    // SAME source → f64
    
    // 🔴 mut cannot preserve comptime types (immediate resolution required)
    mut counter : i32 = 42 + 100 * 5       // comptime_int → i32 (immediately resolved!)
    // val cant_adapt : i64 = counter      // ❌ Error: counter is concrete i32, needs counter:i64
    val must_convert : i64 = counter:i64   // ✅ Explicit conversion required (no flexibility left)
    
    // ===== Demonstrating Comptime Type Flexibility =====
    // Same flexible variable used in different contexts!
    val small_version : i32 = flexible_int    // comptime_int → i32 (same source!)
    val large_version : i64 = flexible_int    // comptime_int → i64 (same source!)
    val float_version : f64 = flexible_int    // comptime_int → f64 (same source!)
    
    // Same comptime arithmetic in different contexts
    val math_expr = 42 + 100 * 5              // comptime_int (stays flexible!)
    val as_i32 : i32 = math_expr              // NOW resolves to i32
    val as_f64 : f64 = math_expr              // SAME expr resolves to f64
    
    // ===== Explicit Concrete Conversions (Visible Costs) =====
    val wide : i64 = i32_value:i64      // i32 → i64 (explicit conversion)
    val precise : f64 = f32_value:f64   // f32 → f64 (explicit conversion)
    val as_float : f32 = i32_value:f32  // i32 → f32 (explicit conversion)
    val narrowed : i32 = i64_value:i32  // i64 → i32 (explicit, potential data loss)
    
    // ===== Mutable Variables with Explicit Conversions =====
    mut counter : i32 = 0       // Mutable integer
    counter = 42                // ✅ OK: comptime_int adapts (no cost)
    counter = large_value:i32   // ✅ OK: explicit conversion (visible cost)
    
    mut accumulator : f64 = 0.0 // Mutable float
    accumulator = 3.14          // ✅ OK: comptime_float adapts (no cost)
    accumulator = counter:f64   // ✅ OK: explicit conversion (visible cost)
    
    // ===== Mixed Type Operations (All Explicit) =====
    val result1 : f64 = int_val:f64 + float_val:f64  // All conversions visible
    val result2 : i32 = (big_val:i32 + small_val:i32) * multiplier:i32
    val complex : f32 = sqrt(x:f32 * x:f32 + y:f32 * y:f32)
    
    // ===== Complex Initialization with Expression Blocks =====
    val complex_init : i32 = {
        // Setup work (scoped)
        {
            val config = load_config()
            validate_system(config)
        }
        
        // Complex computation with explicit conversions
        val base = expensive_computation():i32
        val factor = get_dynamic_factor():i32
        return base * factor
    }
    
    // ===== undef with Different Mutability =====
    // val pending : i32 = undef   // ❌ Error: val + undef creates unusable variable
    mut pending : i32 = undef   // ✅ OK: mut allows later assignment
    pending = compute_value()   // ✅ OK: if compute_value() returns i32
    pending = other_value:i32   // ✅ OK: explicit conversion if needed
    
    // val bad = undef          // ❌ Error: no type context
}

// For binary operations examples, see BINARY_OPS.md
```

## Benefits

### Developer Experience

1. **Ergonomic**: Comptime literals adapt seamlessly (no casting for common cases)
2. **Predictable**: Simple, consistent rules with no exceptions
3. **Transparent**: All conversion costs are visible in the code
4. **Intentional**: Every type conversion is an explicit developer choice

### Performance Clarity

1. **Cost Transparency**: Every conversion is visible in the code
2. **No Hidden Costs**: No automatic conversions or unexpected operations
3. **Performance Predictable**: Developers can easily reason about runtime costs
4. **Optimization Friendly**: Compilers can optimize knowing all conversions are explicit

### Type Safety

1. **Compile-time validation**: All type compatibility checked at compile time
2. **No silent bugs**: Type mismatches cause compilation errors with clear guidance
3. **Explicit data loss**: Developers must consciously acknowledge potential data loss
4. **Clear intent**: Every conversion documents the developer's intention

### Maintainability

1. **Simple mental model**: One rule for all conversions (`value:type`)
2. **Readable code**: All type operations are visible in the source
3. **Easy debugging**: No hidden conversions to trace through
4. **Consistent everywhere**: Same philosophy extends to all language features 