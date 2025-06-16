# Hexen Binary Operations 🦉

*Design and Implementation Specification*

## Overview

Hexen's binary operations system follows the **"Pedantic to write, but really easy to read"** philosophy with clear, predictable operators that eliminate ambiguity and make computational cost transparent. The system is built on top of our comptime type system, ensuring consistent type resolution across all operations.

### Key Design Principles

1. **Two Division Operators for Clarity**:
   - **`/`** = Float division (mathematical, always produces float results)
   - **`\`** = Integer division (efficient, integer-only computation)

2. **Comptime Type Foundation**: 
   - All literals start as comptime types
   - Operations preserve comptime types when possible
   - Context guides resolution to concrete types
   - Clear, predictable semantics

3. **Transparent Cost Model**:
   - Float result types reveal floating-point computation
   - Integer result types guarantee efficient integer math
   - User always knows what computation is happening

## Core Philosophy

### Context-Guided Resolution Strategy

Binary operations in Hexen follow a unified pattern that leverages our comptime type system:

1. **Comptime Types First**: All numeric operations start with comptime types
2. **Context Guides Resolution**: Target type or operation context determines final type
3. **No Hidden Promotions**: Mixed types or operations requiring promotion need explicit context
4. **Operator Determines Behavior**: Division operators (`/` and `\`) determine computation type, not operand types

This pattern is consistent with Hexen's broader design: **"Explicit Danger, Implicit Safety"** and **"Pedantic to write, but really easy to read"**.

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

// Division operators have same precedence level - but different precision!
val float_precise : i32 = (10 / 3) * 9  // (10 / 3) * 9 = (3.333... * 9) = 30.0 → 30 (preserves precision)
val int_truncated : i32 = (10 \ 3) * 9  // (10 \ 3) * 9 = (3 * 9) = 27 (early truncation)
val mixed : f64 = 20 * (3 / 2)          // 20 * (1.5) = 30.0

// Comparison precedence  
val check1 : bool = 5 > 3 && 2 < 4      // (5 > 3) && (2 < 4) = true
val check2 : bool = 5 > 3 == 2 < 4      // (5 > 3) == (2 < 4) = true

// Explicit grouping for clarity
val complex_float : f64 = (a + b) * (c - d) / (e + f)   // Float division
val complex_int : i32 = (a + b) * (c - d) \ (e + f)     // Integer division
```

## Type Resolution Rules

### 1. Safe Operations (No Context Required)

These operations preserve comptime types and resolve automatically:

#### Both Comptime Types
```hexen
// Comptime operations preserve comptime types
val result1 = 42 + 100          // comptime_int + comptime_int → comptime_int
val result2 = 42 * 100          // comptime_int * comptime_int → comptime_int
val result3 = 42 \ 100          // comptime_int \ comptime_int → comptime_int

// Float division requires explicit result type (would produce comptime_float)
// val result4 = 42 / 100       // ❌ Error: Float division requires explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_float : f64 = 3.14 + 2.71     // comptime_float + comptime_float → f64
val explicit_div : f64 = 42 / 100          // comptime_int / comptime_int → f64 (float division)
```

#### Mixed Comptime Types
Mixed comptime types require explicit result type (would produce comptime_float):
```hexen
// ❌ Mixed comptime types would produce comptime_float → require explicit type
// val auto_promote1 = 42 + 3.14   // Error: Mixed comptime types require explicit result type
// val auto_promote2 = 42 * 3.14   // Error: Mixed comptime types require explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_f64 : f64 = 42 + 3.14  // comptime_int + comptime_float → f64 (full precision)
val explicit_f32 : f32 = 42 * 3.14  // comptime_int * comptime_float → f32 (reduced precision)
```

#### One Comptime, One Concrete
The comptime type adapts to the concrete type's context:
```hexen
val x : i32 = 10
val y : f64 = 3.14

val result1 = x + 42            // i32 + comptime_int → comptime_int (adapts to i32 context)
// val result2 = y + 42         // ❌ Error: f64 + comptime_int requires explicit result type
val result2 : f64 = y + 42      // f64 + comptime_int → f64 (explicit context)
// val result3 = x / 2          // ❌ Error: Float division requires explicit result type
val result4 = x \ 2             // i32 \ comptime_int → comptime_int (adapts to i32 context)
```

#### Both Same Concrete Type
```hexen
val a : i32 = 10
val b : i32 = 20
val c : f64 = 3.14
val d : f64 = 2.71

val result1 = a + b             // i32 + i32 → comptime_int (adapts to i32 context)
// val result2 = c * d          // ❌ Error: f64 * f64 requires explicit result type
val result2 : f64 = c * d       // f64 * f64 → f64 (explicit context)
// val result3 = a / b          // ❌ Error: Float division requires explicit result type
val result4 = a \ b             // i32 \ i32 → comptime_int (adapts to i32 context)

// ✅ Explicit type for float division
val explicit_div : f64 = a / b  // i32 / i32 → f64 (float division)
```

### 2. Context-Required Operations

Mixed concrete types require explicit target context:

#### The Problem
```hexen
val a : i32 = 10
val b : i64 = 20

// ❌ Ambiguous - which type should win?
// val result = a + b              // Error: "Mixed-type operation 'i32 + i64' requires explicit result type"
```

#### The Solution - Explicit Context
```hexen
val a : i32 = 10
val b : i64 = 20

// ✅ Context provides resolution
val as_i32 : i32 = a + b        // i32 + i64 → comptime_int (adapts to i32 context)
val as_i64 : i64 = a + b        // i32 + i64 → comptime_int (adapts to i64 context)
val as_f64 : f64 = a + b        // i32 + i64 → comptime_int (adapts to f64 context)
```

### 3. Mutable Assignment with Precision Loss

When reassigning to a mutable variable with potential precision loss, explicit type annotation is required. The type annotation MUST match the mutable variable's declared type - it is not a conversion but an explicit acknowledgment of the operation:

```hexen
mut counter : i32 = 0
mut precise : f32 = 0.0

// Safe assignments - no type annotation needed
counter = 42                          // comptime_int (adapts to i32 context)
counter = 10 + 20                     // comptime_int + comptime_int → comptime_int (adapts to i32 context)
precise = 3.14                        // comptime_float (adapts to f32 context)

// ❌ Error: Type annotation must match mutable variable's type
// counter = some_i64 : i64              // Error: Type annotation must match mutable variable's type (i32)
// counter = some_i64 + some_f64 : f64   // Error: Type annotation must match mutable variable's type (i32)
// precise = 3.14159265359 : f64         // Error: Type annotation must match mutable variable's type (f32)

// ❌ Error: Potential precision loss/truncation - requires explicit type annotation
// counter = some_i64                     // Error: Potential truncation, add ': i32' to acknowledge
// counter = some_i64 + some_f64          // Error: Mixed types with potential truncation, add ': i32'
// precise = 3.14159265359                // Error: Potential precision loss, add ': f32'

// ✅ Explicit acknowledgment of precision loss/truncation (type matches mutable variable)
counter = some_i64 : i32              // Explicit: "I know this might truncate to i32"
counter = some_i64 + some_f64 : i32   // Explicit: "I know this might truncate to i32"
precise = 3.14159265359 : f32         // Explicit: "I know this will lose precision to f32"
```

### 4. Comptime Type Resolution Rules

Comptime types follow the **"i32 default, explicit promotion"** rule for system programming efficiency:

#### Same Comptime Type Operations
```hexen
// comptime_int operations default to i32 (system programmer friendly)
val add_ints = 42 + 100             // comptime_int + comptime_int = comptime_int → i32
val mul_ints = 42 * 100             // comptime_int * comptime_int = comptime_int → i32
val idiv_ints = 42 \ 100            // comptime_int \ comptime_int = comptime_int → i32

// Operations that would promote beyond i32 require explicit type
// val div_ints = 42 / 100          // ❌ Error: Float division requires explicit result type
// val add_floats = 3.14 + 2.71     // ❌ Error: comptime_float operations require explicit result type
// val mul_floats = 3.14 * 2.71     // ❌ Error: comptime_float operations require explicit result type
// val div_floats = 3.14 / 2.71     // ❌ Error: comptime_float operations require explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_div : f64 = 42 / 100   // comptime_int / comptime_int → f64 (float division)
val explicit_add : f64 = 3.14 + 2.71 // comptime_float + comptime_float → f64
val explicit_mul : f32 = 3.14 * 2.71 // comptime_float * comptime_float → f32
val explicit_fdiv : f64 = 3.14 / 2.71 // comptime_float / comptime_float → f64
```

#### Mixed Comptime Types (Require Explicit Type)
```hexen
// Mixed comptime types require explicit result type (would promote beyond i32)
// val auto_promote1 = 42 + 3.14    // ❌ Error: Mixed comptime types require explicit result type
// val auto_promote2 = 42 * 3.14    // ❌ Error: Mixed comptime types require explicit result type
// val auto_promote3 = 42 / 3.14    // ❌ Error: Mixed comptime types require explicit result type
// val auto_promote4 = 42 - 3.14    // ❌ Error: Mixed comptime types require explicit result type

// Complex expressions also require explicit type when they would promote
// val x = 10 + (10 / 2)            // ❌ Error: Contains float division, requires explicit result type
// val y = 42 * 3.14                // ❌ Error: Mixed comptime types require explicit result type
// val z = 100 - 3.14               // ❌ Error: Mixed comptime types require explicit result type

// ❌ Integer division with mixed comptime types is an error
// val invalid = 42 \ 3.14          // Error: Integer division (\) requires integer operands
// val also_bad = 3.14 \ 42         // Error: Integer division (\) requires integer operands

// ✅ Explicit type annotations make intent clear
val explicit_f32 : f32 = 42 + 3.14  // comptime_int + comptime_float → f32
val explicit_f64 : f64 = 42 * 3.14  // comptime_int * comptime_float → f64
val complex_expr : f64 = 10 + (10 / 2) // Explicit type for complex expression with float division

// ✅ Showing the precision difference between division operators
val precise_calc : i32 = (10 / 3) * 9        // Float division: (3.333... * 9) = 30.0 → 30
val truncated_calc : i32 = (10 \ 3) * 9      // Integer division: (3 * 9) = 27 (early truncation)
```

#### Comptime with Concrete Types
```hexen
val concrete_int : i32 = 10
val concrete_float : f64 = 3.14

// Comptime types adapt to concrete types when result stays i32
val adapt1 = concrete_int + 42       // i32 + comptime_int = i32
// val adapt2 = concrete_float * 2   // ❌ Error: f64 result requires explicit result type
// val adapt3 = concrete_int / 2     // ❌ Error: Float division requires explicit result type
val adapt4 = concrete_int \ 2        // i32 \ comptime_int = i32 (integer division)

// ✅ Explicit type for operations that would promote beyond i32
val explicit_f64 : f64 = concrete_float * 2  // f64 + comptime_int → f64

// ✅ Explicit type for float division
val explicit_adapt : f64 = concrete_int / 2  // i32 / comptime_int → f64 (float division)
```

### 4. Concrete Type Mixing Rules

Different concrete numeric types require **explicit handling** - no automatic promotion:

#### Mixed Concrete Types (Require Explicit Context)
```hexen
val int_val : i32 = 10
val long_val : i64 = 20
val float_val : f32 = 3.14

// ❌ Mixed concrete types are not automatically promoted
// val auto_promo = int_val + long_val     // Error: Mixed concrete types need explicit handling
// val mixed_math = int_val + float_val    // Error: Mixed concrete types need explicit handling

// ✅ Explicit target type guides resolution
val as_i64 : i64 = int_val + long_val     // Mixed concrete types → explicit target type
val as_f32 : f32 = int_val + float_val    // Mixed concrete types → explicit target type
val as_f64 : f64 = int_val + long_val     // Mixed concrete types → explicit target type
```

#### Division with Concrete Types
```hexen
val a : i32 = 10
val b : i32 = 3

// Division behavior determined by operator, not operand types
// val float_result = a / b     // ❌ Error: Float division requires explicit result type
val int_result = a \ b          // i32 \ i32 = i32 (integer division)

// ✅ Explicit type for float division
val explicit_float : f64 = a / b // i32 / i32 → f64 (float division)

// Mixed concrete division
val c : i64 = 20
// val mixed_div = a / c        // ❌ Error: Mixed concrete types need explicit handling
val explicit_div : f64 = a / c  // ✅ Mixed concrete types → explicit target type
```

## Division Operations: Float vs Integer

Hexen provides **two distinct division operators** to eliminate ambiguity and make computational cost transparent. The operators determine the computation type, not the operand types:

### Float Division (`/`) - Mathematical Division
**Always produces floating-point results**, preserving mathematical precision:

```hexen
// Float division always produces float results and requires explicit result type
// val precise1 = 10 / 3        // ❌ Error: Float division requires explicit result type
// val precise2 = 7 / 2         // ❌ Error: Float division requires explicit result type
// val float_calc = 10.5 / 2.1  // ❌ Error: comptime_float operations require explicit result type

// ✅ Explicit type annotations make intent clear
val precise1 : f64 = 10 / 3     // comptime_int / comptime_int → f64 (3.333...)
val precise2 : f64 = 7 / 2      // comptime_int / comptime_int → f64 (3.5)
val precise3 : f32 = 22 / 7     // comptime_int / comptime_int → f32 (3.142857...)
val float_calc : f64 = 10.5 / 2.1 // comptime_float / comptime_float → f64 (5.0)

// Mixed concrete types require explicit handling
val int_val : i32 = 10
val float_val : f64 = 3.0
// val mixed = int_val / float_val  // ❌ Error: Mixed concrete types need explicit handling
val explicit_mixed : f64 = int_val / float_val  // ✅ Mixed concrete types → explicit target type

// Mutable assignment with float division
mut result : i32 = 0
// result = 10 / 3               // ❌ Error: Float division requires explicit result type
result = (10 / 3) : i32         // ✅ Explicit truncation from float division
```

### Integer Division (`\`) - Efficient Truncation
**Only works with integer types**, produces integer results with truncation:

```hexen
// Integer division (efficient, no floating-point computation)
val fast1 = 10 \ 3              // comptime_int \ comptime_int → comptime_int (adapts to i32 context)
val fast2 = 7 \ 2               // comptime_int \ comptime_int → comptime_int (adapts to i32 context)
val fast3 : i64 = 22 \ 7        // comptime_int \ comptime_int → comptime_int (adapts to i64 context)

// Integer division with concrete types
val a : i32 = 10
val b : i32 = 3
val efficient = a \ b           // i32 \ i32 → comptime_int (adapts to i32 context)

// ❌ Float operands with integer division is an error
// val invalid = 10.5 \ 2.1     // Error: Integer division requires integer operands
// val also_bad = 3.14 \ 42     // Error: Integer division requires integer operands

// Mixed integer types require explicit handling
val c : i64 = 20
// val mixed = a \ c            // ❌ Error: Mixed concrete types need explicit handling
val explicit_mixed : i64 = a \ c  // ✅ Mixed concrete types → explicit target type

// Mutable assignment with integer division
mut result : i32 = 0
result = a \ b                  // ✅ Safe: comptime_int adapts to i32 context
// result = c \ b               // ❌ Error: Mixed concrete types need explicit handling
result = c \ b : i32            // ✅ Explicit truncation from i64
```

### Design Philosophy

#### **Transparent Cost Model**
- **`/` → Float result**: User sees floating-point type, knows FP computation occurred
- **`\` → Integer result**: User sees integer type, knows efficient integer operation

#### **Mathematical Honesty** 
- **`10 / 3`** naturally produces a fraction → requires explicit float type
- **`10 \ 3`** explicitly requests truncation → produces comptime_int that adapts to context

#### **No Hidden Magic**
- Division behavior determined by **operator choice**, not operand types
- Comptime types adapt to context consistently
- Clear, predictable semantics

### Truncation Rules

Float-to-integer conversion follows standard truncation rules:

```hexen
// Truncation towards zero
mut result : i32 = 0
result = (10.9 / 2.0) : i32    // 5.45 → 5 
result = (-10.9 / 2.0) : i32   // -5.45 → -5

// Exact conversions when possible
result = (20.0 / 4.0) : i32    // 5.0 → 5 (exact)
```

## Complex Expression Resolution

The target type guides the **entire expression tree**, not just individual operations. All expressions start with comptime types and adapt to their context.

### Nested Operations with Context

```hexen
val a : i32 = 10
val b : i64 = 20
val c : f32 = 3.14

// Complex expression resolution with comptime types
// 1. b * c: i64 * f32 → comptime_float (requires explicit type)
// 2. a + (b * c): i32 + comptime_float → comptime_float (requires explicit type)
// 3. Final result is coerced to target type
val result_f64 : f64 = a + b * c    // Explicit context guides entire expression

// ❌ Error: Mixed types require explicit result type
// val result = a + b

// ✅ Explicit target type for mixed types
val result_i32 : i32 = a + b        // comptime_int adapts to i32 context
val result_f64_2 : f64 = (a + 42) * (b + 3.14)  // comptime_float adapts to f64 context
```

### Expression Resolution Strategy

Hexen uses a **two-phase resolution approach** that leverages our comptime type system:

#### Phase 1: Comptime Type Analysis
1. **Start with comptime types** for all literals and operations
2. **Preserve comptime types** through operations when possible
3. **Identify promotion points** where comptime types would change

#### Phase 2: Context-Guided Resolution
1. **Apply target context** to guide type resolution
2. **Convert comptime types** to concrete types based on context
3. **Handle precision/truncation** explicitly when needed

### Resolution Examples

#### Comptime Expression with Target Context
```hexen
val complex : f32 = ((10 + 20) * 3.14) / (5 + 2)
// Phase 1 - Comptime Analysis:
// - (10 + 20): comptime_int + comptime_int = comptime_int
// - 3.14: comptime_float 
// - comptime_int * comptime_float = comptime_float (promotion)
// - (5 + 2): comptime_int + comptime_int = comptime_int
// - comptime_float / comptime_int = comptime_float
// Expression type: comptime_float

// Phase 2 - Context Resolution:
// - Target type: f32
// - Convert comptime_float → f32
// - Result: 13.457...f32
```

#### Mixed Concrete Types with Context
```hexen
val a : i32 = 10
val b : i64 = 20
// ❌ Error without explicit type:
// val result = a + b   // Error: Mixed concrete types require explicit result type

// ✅ With explicit type:
val result : f64 = a + b // comptime_int adapts to f64 context
// Stepwise:
// 1. a (i32) + b (i64) → comptime_int
// 2. comptime_int adapts to f64 context
// Result: 30.0f64
```

## Assignment Context Propagation

Assignment context in Hexen follows the **"Pedantic to write, but really easy to read"** philosophy, where the target type explicitly guides expression resolution while maintaining clear, predictable behavior.

### Assignment Statement Context

Assignment statements use the target variable's type as context for expression resolution. For mutable variables (`mut`), the target type remains constant throughout the variable's lifetime. Comptime types adapt to this context naturally.

#### Mutable Assignment Behavior

```hexen
mut counter : i32 = 0
mut precise : f32 = 0.0

// Safe assignments - comptime types adapt to context
counter = 42                          // comptime_int adapts to i32 context
counter = 10 + 20                     // comptime_int + comptime_int → comptime_int adapts to i32 context
precise = 3.14                        // comptime_float adapts to f32 context

// Safe mixed types - comptime types adapt to context
precise = some_i32 + some_f64         // comptime_float adapts to f32 context
counter = some_i32 + 42               // comptime_int adapts to i32 context

// ❌ Error: Type annotation must match mutable variable's type
// counter = some_i64 : i64              // Error: Type annotation must match mutable variable's type (i32)
// counter = some_i64 + some_f64 : f64   // Error: Type annotation must match mutable variable's type (i32)
// precise = 3.14159265359 : f64         // Error: Type annotation must match mutable variable's type (f32)

// ✅ Explicit acknowledgment of precision loss/truncation (type matches mutable variable)
counter = some_i64 : i32              // Explicit: "I know this might truncate to i32"
counter = some_i64 + some_f64 : i32   // Explicit: "I know this might truncate to i32"
precise = 3.14159265359 : f32         // Explicit: "I know this will lose precision to f32"
```

#### Type Annotation Precedence

When required, the type annotation has highest precedence and applies to the entire expression:

```hexen
mut result : i32 = 0

// These are equivalent - type annotation applies to whole expression
result = a + b : i32                  // (a + b) : i32
result = a + b * c : i32              // (a + b * c) : i32
result = (a + b) * c : i32            // ((a + b) * c) : i32

// Complex expressions with potential precision loss
result = some_i64 * some_f64 : i32    // (some_i64 * some_f64) : i32
result = (a + b) * (c + d) : i32      // ((a + b) * (c + d)) : i32
```

#### When Type Annotations Are Required

The compiler requires explicit type annotations in these cases, and the type annotation MUST match the mutable variable's declared type:

1. **Integer Truncation**:
```hexen
mut counter : i32 = 0
// ❌ Error: Type annotation must match mutable variable's type
// counter = some_i64 : i64              // Error: Type annotation must match mutable variable's type (i32)
// counter = 0xFFFFFFFF + 1 : i64        // Error: Type annotation must match mutable variable's type (i32)

// ❌ Error: Potential truncation without type annotation
// counter = some_i64                     // Error: Add ': i32' to acknowledge truncation
// counter = 0xFFFFFFFF + 1               // Error: Add ': i32' to acknowledge truncation

// ✅ Explicit acknowledgment (type matches mutable variable)
counter = some_i64 : i32              // Explicit truncation to i32
counter = 0xFFFFFFFF + 1 : i32        // Explicit truncation to i32
```

2. **Float Precision Loss**:
```hexen
mut precise : f32 = 0.0
// ❌ Error: Type annotation must match mutable variable's type
// precise = 3.14159265359 : f64         // Error: Type annotation must match mutable variable's type (f32)
// precise = some_f64 * 2.0 : f64        // Error: Type annotation must match mutable variable's type (f32)

// ❌ Error: Potential precision loss without type annotation
// precise = 3.14159265359                // Error: Add ': f32' to acknowledge precision loss
// precise = some_f64 * 2.0               // Error: Add ': f32' to acknowledge precision loss

// ✅ Explicit acknowledgment (type matches mutable variable)
precise = 3.14159265359 : f32         // Explicit precision loss to f32
precise = some_f64 * 2.0 : f32        // Explicit precision loss to f32
```

3. **Mixed Types with Potential Issues**:
```hexen
mut result : i32 = 0
// ❌ Error: Type annotation must match mutable variable's type
// result = some_i64 + some_f64 : f64    // Error: Type annotation must match mutable variable's type (i32)
// result = some_f64 * some_i32 : f64    // Error: Type annotation must match mutable variable's type (i32)

// ❌ Error: Mixed types with potential truncation without type annotation
// result = some_i64 + some_f64           // Error: Add ': i32' to acknowledge truncation
// result = some_f64 * some_i32           // Error: Add ': i32' to acknowledge truncation

// ✅ Explicit acknowledgment (type matches mutable variable)
result = some_i64 + some_f64 : i32    // Explicit truncation to i32
result = some_f64 * some_i32 : i32    // Explicit truncation to i32
```

#### Mutable Assignment Rules

1. **Type Consistency**: The target type of a mutable variable cannot change
2. **Context Priority**: The mutable variable's type provides the primary context for all assignments
3. **Comptime Adaptation**: Comptime types naturally adapt to the target type's context
4. **Explicit Precision Loss**: Type annotations are required only when there's potential precision loss or truncation
5. **Type Annotation Match**: Type annotations MUST match the mutable variable's declared type - they are not conversions but explicit acknowledgments
6. **Highest Precedence**: When used, type annotations apply to the entire expression
7. **Predictable Behavior**: The same expression will resolve consistently based on the mutable variable's type

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

## Implementation Guidelines

### Semantic Analysis Strategy

The semantic analyzer should implement a two-phase approach for binary operations:

1. **Comptime Type Analysis Phase**
```python
def analyze_binary_operation(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze binary operation with optional target type context."""
    left_type = self.analyze_expression(node["left"])
    right_type = self.analyze_expression(node["right"])
    op = node["operator"]
    
    # Phase 1: Comptime Type Analysis
    if self._is_comptime_operation(left_type, right_type, op):
        return self._analyze_comptime_operation(left_type, right_type, op, target_type)
    
    # Phase 2: Concrete Type Resolution
    return self._resolve_concrete_operation(left_type, right_type, op, target_type, node)
```

2. **Context-Guided Resolution Phase**
```python
def _resolve_concrete_operation(self, left: HexenType, right: HexenType, 
                              op: str, target_type: Optional[HexenType], 
                              node: Dict) -> HexenType:
    """Resolve concrete types with context guidance."""
    # Safe cases (no context needed)
    if self._is_safe_operation(left, right, op):
        return self._resolve_safe_operation(left, right, op)
    
    # Context-required cases
    if target_type is None:
        self._error(f"Mixed-type operation '{left} {op} {right}' requires explicit result type", node)
        return HexenType.UNKNOWN
    
    return self._resolve_with_context(left, right, op, target_type, node)
```

### Key Implementation Functions

1. **Comptime Type Analysis**
```python
def _analyze_comptime_operation(self, left: HexenType, right: HexenType, 
                              op: str, target_type: Optional[HexenType]) -> HexenType:
    """Analyze operations involving comptime types."""
    # Preserve comptime types when possible
    if self._is_safe_comptime_operation(left, right, op):
        return self._preserve_comptime_type(left, right, op)
    
    # Handle promotion cases
    if self._would_promote_comptime(left, right, op):
        if target_type is None:
            return HexenType.UNKNOWN  # Requires explicit type
        return self._promote_to_target(left, right, op, target_type)
```

2. **Division Operator Handling**
```python
def _analyze_division(self, left: HexenType, right: HexenType, 
                     op: str, target_type: Optional[HexenType]) -> HexenType:
    """Special handling for division operators."""
    if op == "/":  # Float division
        if target_type is None:
            return HexenType.UNKNOWN  # Always requires explicit type
        return self._validate_float_division(left, right, target_type)
    
    if op == "\\":  # Integer division
        if not self._are_integer_types(left, right):
            return HexenType.UNKNOWN  # Integer division requires integer operands
        return self._resolve_integer_division(left, right, target_type)
```

3. **Type Adaptation**
```python
def _adapt_to_context(self, type: HexenType, target_type: HexenType, 
                     node: Dict) -> HexenType:
    """Adapt comptime types to target context."""
    if not self._is_comptime_type(type):
        return type
    
    if self._is_safe_adaptation(type, target_type):
        return target_type
    
    if self._would_lose_precision(type, target_type):
        self._error(f"Potential precision loss in adaptation to {target_type}", node)
        return HexenType.UNKNOWN
    
    return target_type
```

### Error Handling

The semantic analyzer should provide clear, actionable error messages:

```python
def _error(self, message: str, node: Dict) -> None:
    """Generate helpful error messages for binary operations."""
    if "requires explicit result type" in message:
        self.errors.append(f"{message}\nAdd type annotation: 'val result : type = ...'")
    elif "potential precision loss" in message:
        self.errors.append(f"{message}\nAdd explicit type annotation to acknowledge: 'val result : type = ...'")
    elif "integer division requires integer operands" in message:
        self.errors.append(f"{message}\nUse float division (/) for non-integer operands")
    else:
        self.errors.append(message)
```

### Testing Strategy

Implement comprehensive tests for:

1. **Comptime Type Preservation**
   - Same comptime type operations
   - Mixed comptime type operations
   - Comptime with concrete types

2. **Context Resolution**
   - Target type guidance
   - Mixed concrete types
   - Precision loss cases

3. **Division Operators**
   - Float division behavior
   - Integer division behavior
   - Mixed type division

4. **Error Cases**
   - Missing type annotations
   - Invalid type combinations
   - Precision loss without acknowledgment

Example test structure:
```python
def test_binary_operations():
    # Comptime preservation
    assert_type("42 + 100", "comptime_int")
    assert_type("3.14 + 2.71", "comptime_float")
    
    # Context resolution
    assert_type("val x : i32 = 42 + 100", "i32")
    assert_type("val x : f64 = 42 + 3.14", "f64")
    
    # Division operators
    assert_type("val x : f64 = 10 / 3", "f64")
    assert_type("val x : i32 = 10 \\ 3", "i32")
    
    # Error cases
    assert_error("42 + 3.14", "requires explicit result type")
    assert_error("10.5 \\ 2.1", "integer division requires integer operands")
```

These implementation guidelines ensure consistent behavior across the compiler while maintaining the language's core principles of explicit danger and implicit safety.
