# Hexen Binary Operations 🦉

*Design and Implementation Specification*

## Overview

Hexen's binary operations system follows the **"Pedantic to write, but really easy to read"** philosophy with clear, predictable operators that eliminate ambiguity and make computational cost transparent. 

### Key Design Principles

1. **Two Division Operators for Clarity**:
   - **`/`** = Float division (mathematical, always produces float results)
   - **`\`** = Integer division (efficient, integer-only computation)

2. **No Magic Type Coercion**: 
   - Operator choice determines behavior, not context
   - Mixed types require explicit handling
   - Clear, predictable semantics

3. **Transparent Cost Model**:
   - Float result types reveal floating-point computation
   - Integer result types guarantee efficient integer math
   - User always knows what computation is happening

## Core Philosophy

### Context-Guided Resolution Strategy

Binary operations in Hexen follow a unified pattern that prioritizes system programming efficiency:

1. **Default to `i32`**: All numeric operations default to `i32` (system programmer friendly)
2. **Promotion Requires Explicit Type**: Any operation that would promote beyond `i32` requires explicit result type annotation
3. **No Hidden Promotions**: Float division, mixed types, or wider integers all require explicit intent
4. **Context Determines Behavior**: Target type guides the entire expression resolution when provided

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

These operations are unambiguous and resolve automatically:

#### Both Comptime Types
```hexen
// Same comptime_int operations default to i32
val result1 = 42 + 100          // comptime_int + comptime_int → i32
val result2 = 42 * 100          // comptime_int + comptime_int → i32
val result3 = 42 \ 100          // comptime_int \ comptime_int → i32

// Operations that would promote beyond i32 require explicit type
// val result4 = 3.14 + 2.71    // ❌ Error: comptime_float operations require explicit result type
// val result5 = 42 / 100       // ❌ Error: Float division requires explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_float : f64 = 3.14 + 2.71     // comptime_float + comptime_float → f64
val explicit_div : f64 = 42 / 100          // comptime_int / comptime_int → f64 (float division)
```

#### Mixed Comptime Types
Mixed comptime types require explicit result type (would promote beyond i32):
```hexen
// ❌ Mixed comptime types would promote beyond i32 → require explicit type
// val auto_promote1 = 42 + 3.14   // Error: Mixed comptime types require explicit result type
// val auto_promote2 = 42 * 3.14   // Error: Mixed comptime types require explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_f64 : f64 = 42 + 3.14  // comptime_int + comptime_float → f64 (full precision)
val explicit_f32 : f32 = 42 * 3.14  // comptime_int * comptime_float → f32 (reduced precision)
```

#### One Comptime, One Concrete
The comptime type adapts to the concrete type when result stays within i32:
```hexen
val x : i32 = 10
val y : f64 = 3.14

val result1 = x + 42            // i32 + comptime_int → i32
// val result2 = y + 42         // ❌ Error: f64 + comptime_int requires explicit result type
val result2 : f64 = y + 42      // f64 + comptime_int → f64 (explicit type required)
// val result3 = x / 2          // ❌ Error: Float division requires explicit result type
val result4 = x \ 2             // i32 \ comptime_int → i32 (integer division)
```

#### Both Same Concrete Type
```hexen
val a : i32 = 10
val b : i32 = 20
val c : f64 = 3.14
val d : f64 = 2.71

val result1 = a + b             // i32 + i32 → i32
// val result2 = c * d          // ❌ Error: f64 * f64 requires explicit result type
val result2 : f64 = c * d       // f64 * f64 → f64 (explicit type required)
// val result3 = a / b          // ❌ Error: Float division requires explicit result type
val result4 = a \ b             // i32 \ i32 → i32 (integer division)

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
val as_i32 : i32 = a + b        // i64 → i32 coercion (may truncate)
val as_i64 : i64 = a + b        // i32 → i64 widening (safe)  
val as_f64 : f64 = a + b        // Both → f64 conversion
```

### 3. Mutable Assignment with Precision Loss

When reassigning to a mutable variable with potential precision loss, explicit type annotation is required:

```hexen
mut counter : i32 = 0
mut precise : f32 = 0.0

// Safe assignments - no type annotation needed
counter = 42                          // comptime_int → i32 (safe)
counter = 10 + 20                     // comptime_int + comptime_int → i32 (safe)
precise = 3.14                        // comptime_float → f32 (safe)

// ❌ Error: Potential precision loss/truncation - requires explicit type annotation
// counter = some_i64                  // Error: Potential truncation, add ': i32' to acknowledge
// counter = some_i64 + some_f64       // Error: Mixed types with potential truncation, add ': i32'
// precise = 3.14159265359             // Error: Potential precision loss, add ': f32'

// ✅ Explicit acknowledgment of precision loss/truncation
counter = some_i64 : i32              // Explicit: "I know this might truncate"
counter = some_i64 + some_f64 : i32   // Explicit: "I know this might truncate"
precise = 3.14159265359 : f32         // Explicit: "I know this will lose precision"
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

Hexen provides **two distinct division operators** to eliminate ambiguity and make computational cost transparent:

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
val fast1 = 10 \ 3              // comptime_int \ comptime_int → i32 (3, truncated)
val fast2 = 7 \ 2               // comptime_int \ comptime_int → i32 (3, truncated)  
val fast3 : i64 = 22 \ 7        // comptime_int \ comptime_int → i64 (3, truncated)

// Integer division with concrete types
val a : i32 = 10
val b : i32 = 3
val efficient = a \ b           // i32 \ i32 → i32 (3, truncated)

// ❌ Float operands with integer division is an error
// val invalid = 10.5 \ 2.1     // Error: Integer division requires integer operands
// val also_bad = 3.14 \ 42     // Error: Integer division requires integer operands

// Mixed integer types require explicit handling
val c : i64 = 20
// val mixed = a \ c            // ❌ Error: Mixed concrete types need explicit handling
val explicit_mixed : i64 = a \ c  // ✅ Mixed concrete types → explicit target type

// Mutable assignment with integer division
mut result : i32 = 0
result = a \ b                  // ✅ Safe: same type
// result = c \ b               // ❌ Error: Mixed concrete types need explicit handling
result = c \ b : i32            // ✅ Explicit truncation from i64
```

### Design Philosophy

#### **Transparent Cost Model**
- **`/` → Float result**: User sees floating-point type, knows FP computation occurred
- **`\` → Integer result**: User sees integer type, knows efficient integer operation

#### **Mathematical Honesty** 
- **`10 / 3`** naturally produces a fraction → `f64` type reveals this
- **`10 \ 3`** explicitly requests truncation → `i32` type shows the loss

#### **No Hidden Magic**
- Division behavior determined by **operator choice**, not context
- No complex coercion rules or context-dependent behavior
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

The target type guides the **entire expression tree**, not just individual operations.

### Nested Operations with Context

```hexen
val a : i32 = 10
val b : i64 = 20
val c : f32 = 3.14

// Stepwise (local) promotion: each binary op is resolved using its operands' types
// 1. b * c: i64 * f32 → f32 (requires explicit type if not allowed by default)
// 2. a + (b * c): i32 + f32 → f32 (requires explicit type if not allowed by default)
// 3. Final result is coerced to target type (if provided)
val result_f64 : f64 = a + b * c    // Stepwise: b * c → f32, then a + (b * c) → f32, then final result coerced to f64

// ❌ Error: Mixed types require explicit result type
// val result = a + b

// ✅ Explicit target type for mixed types
val result_i32 : i32 = a + b        // i64 coerces to i32 context (may truncate)
val result_f64_2 : f64 = (a + 42) * (b + 3.14)  // Stepwise: (a+42):i32, (b+3.14):f64, then i32*f64 → f64
```

### Expression Resolution Strategy

Hexen uses a **two-phase resolution approach** that balances precision with target type requirements:

#### Phase 1: Semantic Analysis
1. **Determine expression semantics** based on operand types
2. **Apply promotion rules** for comptime and mixed types
3. **Choose computation strategy** for maximum precision

#### Phase 2: Target Type Conversion
1. **Compute expression** using determined semantics
2. **Convert final result** to target type if needed
3. **Apply truncation/rounding** rules as appropriate

### Resolution Examples

#### Comptime Expression with Target Context
```hexen
val complex : f32 = ((10 + 20) * 3.14) / (5 + 2)
// Phase 1 - Semantic Analysis:
// - (10 + 20): comptime_int + comptime_int = comptime_int
// - 3.14: comptime_float 
// - comptime_int * comptime_float = comptime_float (promotion)
// - (5 + 2): comptime_int + comptime_int = comptime_int
// - comptime_float / comptime_int = comptime_float
// Expression type: comptime_float

// Phase 2 - Target Conversion:
// - Compute: ((30) * 3.14) / (7) = 94.2 / 7 = 13.457...
// - Convert: comptime_float → f32 = 13.457...f32
```

#### Mixed Concrete Types with Context
```hexen
val a : i32 = 10
val b : i64 = 20
// ❌ Error without explicit type:
// val result = a + b   // Error: Mixed concrete types require explicit result type

// ✅ With explicit type:
val result : f64 = a + b // Both operands promoted to f64 for this operation, result is f64
// Stepwise: a (i32) + b (i64) → both promoted to f64 for this operation
// Result: f64(10.0) + f64(20.0) = f64(30.0)
```

## Comparison Operations

Comparison operators produce boolean results and have special type resolution rules.

### Basic Comparisons

```hexen
val result1 : bool = 10 < 20            // comptime_int < comptime_int = bool
val result2 : bool = 3.14 > 2.71        // comptime_float > comptime_float = bool
val result3 : bool = 42 == 42           // comptime_int == comptime_int = bool
val result4 : bool = "hello" == "world" // string == string = bool
```

### Mixed-Type Comparisons

Mixed-type comparisons follow promotion rules:

```hexen
val int_val : i32 = 10
val float_val : f64 = 10.0

val comparison1 : bool = int_val < float_val    // i32 promotes to f64 for comparison
val comparison2 : bool = 42 > 3.14              // comptime_int vs comptime_float = comptime_float
```

### Equality with Type Safety

```hexen
val str_val : string = "hello"
val int_val : i32 = 42

// ❌ Type error - cannot compare different fundamental types
val invalid : bool = str_val == int_val  // Error: Cannot compare string and i32
```

## Logical Operations

Logical operators work exclusively with boolean values and follow strict type rules.

### Type Rules

1. **Boolean Context**:
   - Only boolean values are allowed in logical operations
   - No implicit coercion from other types
   ```hexen
   val age : i32 = 25
   val has_license : bool = true
   
   // ✅ Valid: Comparison produces boolean
   val can_drive : bool = age >= 18 && has_license
   
   // ❌ Invalid: No implicit coercion
   // val invalid1 = age && has_license        // Error: i32 cannot be used in logical operation
   // val invalid2 = "yes" || has_license     // Error: string cannot be used in logical operation
   ```

2. **Comparison Results**:
   - Comparison operators (`<`, `>`, `<=`, `>=`, `==`, `!=`) produce boolean results
   - Mixed type comparisons follow promotion rules
   ```hexen
   val int_val : i32 = 10
   val float_val : f64 = 10.0
   
   // ✅ Valid: i32 promotes to f64 for comparison
   val comparison1 : bool = int_val < float_val
   
   // ✅ Valid: comptime_int promotes to f64 for comparison
   val comparison2 : bool = 42 > 3.14
   
   // ❌ Invalid: Cannot compare different fundamental types
   val str_val : string = "hello"
   // val invalid = str_val == int_val        // Error: Cannot compare string and i32
   ```

### Basic Logical Operations

```hexen
// Basic boolean operations
val and_result : bool = true && false   // false
val or_result : bool = true || false    // true
val not_result : bool = !true           // false

// Complex boolean expressions
val age : i32 = 25
val has_license : bool = true
val has_car : bool = false

val can_drive : bool = age >= 18 && has_license
val needs_permission : bool = age < 18 || !has_license
val can_borrow_car : bool = has_license && !has_car
```

### Short-Circuit Evaluation

Logical operators use short-circuit evaluation to optimize performance:

```hexen
val a : bool = false
val b : bool = true

// Short-circuit AND: if a is false, b is never evaluated
val result1 : bool = a && expensive_function()  // expensive_function() not called

// Short-circuit OR: if a is true, b is never evaluated
val result2 : bool = a || expensive_function()  // expensive_function() is called

// Complex short-circuit example
val age : i32 = 25
val has_license : bool = false

// If age < 18 is false, has_license is never checked
val needs_permission : bool = age < 18 || !has_license
```

### Logical Operator Precedence

Logical operators have lower precedence than comparison operators:

```hexen
// These are equivalent:
val result1 : bool = (age >= 18) && (has_license == true)
val result2 : bool = age >= 18 && has_license == true

// Complex precedence example
val result3 : bool = age >= 18 && has_license || age < 18 && !has_license
// Equivalent to:
// (age >= 18 && has_license) || (age < 18 && !has_license)
```

### Mutable Assignment with Logical Operations

```hexen
mut status : bool = false

// Safe assignments - no type annotation needed
status = true                          // bool → bool (safe)
status = age >= 18 && has_license      // bool → bool (safe)

// ❌ Error: Non-boolean value
// status = 42                         // Error: i32 cannot be assigned to bool
// status = "yes"                      // Error: string cannot be assigned to bool

// ✅ Valid: Complex boolean expressions
status = age >= 18 && (has_license || has_car)
status = !status || (age < 18 && has_license)
```

## Arithmetic Operations

### Addition and Subtraction

```hexen
// Basic arithmetic with context
val sum : i32 = 10 + 20          // comptime_int + comptime_int → i32
val diff : f64 = 10.5 - 3.2     // comptime_float - comptime_float → f64

// Mixed arithmetic with context
val a : i32 = 10
val b : i64 = 20
val mixed : i64 = a + b          // i32 → i64 (widening)
```

### Multiplication and Division

```hexen
// Multiplication
val product : f32 = 3.14 * 2     // comptime_float * comptime_int → f32

// Division (context-dependent behavior)
val int_division : i32 = 10 / 3  // comptime division → i32: integer division = 3 (truncated)
val float_division : f64 = 10 / 3 // comptime division → f64: float division = 3.333...
```

### Modulo Operation

```hexen
val remainder : i32 = 17 % 5     // Integer modulo: 2

// Modulo requires integer operands
val a : f64 = 17.5
val b : f64 = 5.0
// val invalid = a % b           // ❌ Error: Modulo requires integer types
```

## Assignment Context Propagation

Assignment context in Hexen follows the **"Pedantic to write, but really easy to read"** philosophy, where the target type explicitly guides expression resolution while maintaining clear, predictable behavior.


### Assignment Statement Context

Assignment statements in Hexen use the target variable's type as context for expression resolution. For mutable variables (`mut`), the target type remains constant throughout the variable's lifetime. To maintain safety while keeping the code readable, explicit type annotations are only required when there's potential precision loss or truncation.

#### Mutable Assignment Behavior

```hexen
mut counter : i32 = 0
mut precise : f32 = 0.0

// Safe assignments - no type annotation needed
counter = 42                          // comptime_int → i32 (safe)
counter = 10 + 20                     // comptime_int + comptime_int → i32 (safe)
precise = 3.14                        // comptime_float → f32 (safe)

// Safe mixed types - no type annotation needed
precise = some_i32 + some_f64         // i32 + f64 → f32 (safe promotion)
counter = some_i32 + 42               // i32 + comptime_int → i32 (safe)

// ❌ Error: Potential precision loss/truncation - requires explicit type annotation
// counter = some_i64                  // Error: Potential truncation, add ': i32' to acknowledge
// counter = some_i64 + some_f64       // Error: Mixed types with potential truncation, add ': i32'
// precise = 3.14159265359             // Error: Potential precision loss, add ': f32'

// ✅ Explicit acknowledgment of precision loss/truncation
counter = some_i64 : i32              // Explicit: "I know this might truncate"
counter = some_i64 + some_f64 : i32   // Explicit: "I know this might truncate"
precise = 3.14159265359 : f32         // Explicit: "I know this will lose precision"
```

#### Type Annotation Precedence

When required, the type annotation has highest precedence and applies to the entire expression:

```hexen
mut result : i32 = 0

// These are equivalent - type annotation applies to whole expression
result = a + b : i32                  // (a + b) : i32
result = a + b * c : i32              // (a + (b * c)) : i32
result = (a + b) * c : i32            // ((a + b) * c) : i32

// Complex expressions with potential precision loss
result = some_i64 * some_f64 : i32    // ((some_i64 * some_f64)) : i32
result = (a + b) * (c + d) : i32      // ((a + b) * (c + d)) : i32
```

#### When Type Annotations Are Required

The compiler requires explicit type annotations in these cases:

1. **Integer Truncation**:
```hexen
mut counter : i32 = 0
// ❌ Error: Potential truncation
// counter = some_i64                  // Error: Add ': i32' to acknowledge truncation
// counter = 0xFFFFFFFF + 1            // Error: Add ': i32' to acknowledge truncation

// ✅ Explicit acknowledgment
counter = some_i64 : i32              // Explicit truncation
counter = 0xFFFFFFFF + 1 : i32        // Explicit truncation
```

2. **Float Precision Loss**:
```hexen
mut precise : f32 = 0.0
// ❌ Error: Potential precision loss
// precise = 3.14159265359             // Error: Add ': f32' to acknowledge precision loss
// precise = some_f64 * 2.0            // Error: Add ': f32' to acknowledge precision loss

// ✅ Explicit acknowledgment
precise = 3.14159265359 : f32         // Explicit precision loss
precise = some_f64 * 2.0 : f32        // Explicit precision loss
```

3. **Mixed Types with Potential Issues**:
```hexen
mut result : i32 = 0
// ❌ Error: Mixed types with potential truncation
// result = some_i64 + some_f64        // Error: Add ': i32' to acknowledge truncation
// result = some_f64 * some_i32        // Error: Add ': i32' to acknowledge truncation

// ✅ Explicit acknowledgment
result = some_i64 + some_f64 : i32    // Explicit truncation
result = some_f64 * some_i32 : i32    // Explicit truncation
```

#### Safe Operations (No Annotation Required)

Type annotations are not required for these safe operations:

```hexen
mut counter : i32 = 0
mut precise : f32 = 0.0

// Safe integer operations
counter = 42                          // comptime_int → i32
counter = 10 + 20                     // comptime_int + comptime_int → i32
counter = some_i32 + 42               // i32 + comptime_int → i32

// Safe float operations
precise = 3.14                        // comptime_float → f32
precise = 2.0 * 3.0                   // comptime_float * comptime_float → f32
precise = some_f32 * 2.0              // f32 * comptime_float → f32

// Safe mixed types
precise = some_i32 + some_f32         // i32 + f32 → f32 (safe promotion)
precise = some_i32 * 2.0              // i32 * comptime_float → f32 (safe promotion)
```

#### Mutable Assignment Rules

1. **Type Consistency**: The target type of a mutable variable cannot change
2. **Context Priority**: The mutable variable's type provides the primary context for all assignments
3. **Explicit Precision Loss**: Type annotations are required only when there's potential precision loss or truncation
4. **Highest Precedence**: When used, type annotations apply to the entire expression
5. **Predictable Behavior**: The same expression will resolve consistently based on the mutable variable's type


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
