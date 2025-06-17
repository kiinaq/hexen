# Hexen Type System 🦉

*Design and Implementation Specification*

## Overview

Hexen's type system is designed around the principle of **"Explicit Danger, Implicit Safety"** - making dangerous or ambiguous operations explicit while keeping safe operations seamlessly implicit. This philosophy creates a system that is both ergonomic for common cases and safe for complex scenarios.

## Core Philosophy

### Design Principle: Context-Guided Type Resolution

Hexen follows a unified pattern where **assignment target types serve as context anchors** that guide the resolution of complex expressions. This pattern is consistent across all language features:

- **Safe + Unambiguous = Implicit** (comptime type coercion)
- **Dangerous + Explicit Context = Allowed** (`undef` with type annotation)  
- **Ambiguous = Error** (require explicit type context)

This same pattern extends to binary operations and mixed-type expressions.

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

### Comptime Types (Compile-Time Only)

| Type | Description | Purpose |
|------|-------------|---------|
| `comptime_int` | Integer literals | Context-dependent coercion to any numeric type |
| `comptime_float` | Float literals | Context-dependent coercion to float types |

### Special Types (Internal)

| Type | Description | Usage |
|------|-------------|-------|
| `unknown` | Type inference failure | Error handling |
| `undef` | Uninitialized variable | Explicit uninitialized state |

## Comptime Type System

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

### The Solution: Context-Adaptive Literals

Hexen solves this with **comptime types** - special types that literals have initially, which then adapt to their usage context:

```hexen
// ✨ Same literal, different contexts, no suffixes needed
val small : i32 = 42    // 42 is comptime_int → becomes i32
val large : i64 = 42    // 42 is comptime_int → becomes i64  
val precise : f64 = 42  // 42 is comptime_int → becomes f64
val single : f32 = 3.14 // 3.14 is comptime_float → becomes f32
val double : f64 = 3.14 // 3.14 is comptime_float → becomes f64
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
val counter : i32 = 42           // comptime_int sees i32 context → becomes i32
val big_counter : i64 = 42       // comptime_int sees i64 context → becomes i64
val percentage : f32 = 42        // comptime_int sees f32 context → becomes f32

// Context comes from function parameters
func process_data(count: i64) { ... }
process_data(1000)               // comptime_int sees i64 parameter → becomes i64

// Context comes from return types
func get_count() : i32 = 42      // comptime_int sees i32 return → becomes i32
```

#### Step 3: Default Resolution
When there's **no context**, comptime types use sensible defaults:

```hexen
val counter = 42      // No context → comptime_int becomes i32 (system default)
val pi = 3.14         // No context → comptime_float becomes f64 (precision default)
```

### Comptime Type Rules

#### comptime_int can become:
- `i32`, `i64` (integer types)
- `f32`, `f64` (float types - integer to float conversion)

#### comptime_float can become:
- `f32`, `f64` (float types only)
- **Cannot** become integers (would lose decimal part)

#### Safety Rules:
```hexen
// ✅ Safe conversions (implicit)
val int_var : i32 = 42      // comptime_int → i32 ✓
val float_var : f64 = 42    // comptime_int → f64 ✓  
val precise : f32 = 3.14    // comptime_float → f32 ✓

// ❌ Implicit conversions that lose data (compilation errors)
// val bad_int : i32 = 3.14    // Error: comptime_float → i32 requires explicit acknowledgment
// val bad_bool : bool = 42    // Error: comptime_int → bool not meaningful
// val bad_str : string = 3.14 // Error: comptime_float → string not meaningful

// ✅ Explicit conversions with precision loss (allowed with acknowledgment)
val explicit_int : i32 = 3.14 : i32    // comptime_float → i32 ✓ (explicit truncation)
val explicit_bool = if 42 != 0 { true } else { false }  // Explicit logic for bool conversion
```

### Real-World Benefits

#### Before (Traditional Languages)
```c
// C/C++ style - suffix hell
uint32_t small_timeout = 1000U;
uint64_t large_timeout = 1000UL;    // Change type = change suffix
float32_t ratio = 0.75f;
float64_t precise_ratio = 0.75;     // Inconsistent rules

// Changing i32 to i64 requires updating every literal
int32_t process_batch(int32_t count) {
    return count * 2;  // What if count overflows?
}
```

#### After (Hexen with Comptime)
```hexen
// ✨ Hexen style - no suffixes needed
val small_timeout : i32 = 1000     // Clean and clear
val large_timeout : i64 = 1000     // Same literal, different type
val ratio : f32 = 0.75             // Consistent syntax
val precise_ratio : f64 = 0.75     // Same literal, different precision

// Changing i32 to i64 only requires changing the type annotation
func process_batch(count: i64) : i64 = {
    return count * 2               // All literals adapt automatically
}
```

### Context Propagation Examples

Comptime types work seamlessly in complex expressions:

```hexen
// Function parameters provide context
func calculate(base: i64, multiplier: f32) : f64 = {
    return base * multiplier
}

// All literals adapt to their context automatically
val result = calculate(1000, 2.5)    // 1000→i64, 2.5→f32, result is f64

// Array context
val numbers : [i64; 3] = [10, 20, 30]   // All comptime_int → i64

// Mixed operations with explicit context
val mixed : f64 = 42 + 3.14             // 42→f64, 3.14→f64, result is f64
```

### Design Philosophy

The comptime system embodies Hexen's **"Explicit Danger, Implicit Safety"** principle:

- **Implicit Safety**: Common, safe literal usage requires no extra syntax
- **Explicit Context**: When you need specific types, you provide explicit context
- **No Hidden Behavior**: Type resolution is predictable and visible
- **Fail Fast**: Unsafe conversions are caught at compile time

### Implementation Mental Model

Think of comptime types as "smart literals" that ask their context: *"What type do you need me to be?"*

1. **Parser**: Creates comptime_int/comptime_float for all numeric literals
2. **Type Checker**: Propagates target types as context through expressions  
3. **Resolution**: Comptime types check if they can safely become the target type
4. **Error**: If conversion is unsafe or no context exists, compilation fails with helpful message

This creates a clean, consistent system where the same literal works everywhere without sacrificing type safety.

## Type Coercion Rules

### 1. Identity Coercion
Any type can coerce to itself:
```hexen
val x : i32 = some_i32_value  // i32 → i32
```

### 2. Comptime Type Coercion (The Magic)

**comptime_int** can coerce to:
- `i32`, `i64` (integer types)
- `f32`, `f64` (float types)
- **Cannot** coerce to `bool`, `string` (type safety)

**comptime_float** can coerce to:
- `f32`, `f64` (float types - implicit, safe)
- `i32`, `i64` (integer types - **explicit only**, requires `: i32` or `: i64` annotation)
- **Cannot** coerce to `bool`, `string` (not meaningful)

```hexen
// ✅ Safe implicit comptime coercions
val int_var : i32 = 42      // comptime_int → i32 (implicit, safe)
val float_var : f64 = 42    // comptime_int → f64 (implicit, safe)
val precise : f32 = 3.14    // comptime_float → f32 (implicit, safe)

// ❌ Implicit coercions that lose data or meaning (compilation errors)
// val bad_bool : bool = 42    // Error: comptime_int → bool requires explicit logic
// val bad_string : string = 3.14 // Error: comptime_float → string not meaningful
// val bad_int : i32 = 3.14    // Error: comptime_float → i32 requires explicit ': i32'

// ✅ Explicit coercions with precision loss (allowed with acknowledgment)
val explicit_int : i32 = 3.14 : i32    // comptime_float → i32 (explicit truncation)
val explicit_logic : bool = if 42 != 0 { true } else { false }  // Explicit boolean logic

// 🎯 Critical Pattern: Type annotation ALWAYS at end, ALWAYS matches left side
//    └─ target type ─┘   └─ expression ─┘ : └─ SAME type ─┘
//    This is NOT conversion - it's explicit acknowledgment of result type
```

### 3. Regular Type Widening

For concrete (non-comptime) types, widening coercion is allowed:

```hexen
// Integer widening
val wide : i64 = i32_value  // i32 → i64

// Float widening  
val precise : f64 = f32_value  // f32 → f64

// Integer to float conversion
val as_float : f32 = i32_value  // i32 → f32
val as_double : f64 = i64_value // i64 → f64
```

**Widening Rules:**
- `i32` → `{i64, f32, f64}`
- `i64` → `{f32, f64}` (may lose precision for very large integers)
- `f32` → `{f64}`

## Binary Operations

Binary operations in Hexen follow the **context-guided resolution** strategy with consistent, pedantic rules that eliminate hidden behaviors. Due to the complexity and importance of this topic, it has been moved to a dedicated specification:

**→ See [BINARY_OPS.md](BINARY_OPS.md) for complete binary operations specification**

Key highlights:
- **Consistent type preservation**: Operations maintain operand types unless explicitly guided by context
- **No hidden promotions**: Mixed comptime types (42 + 3.14) require explicit context
- **Context-dependent division**: integer vs float division based on target type
- **Explicit mixed-type resolution**: All ambiguous operations require type annotations
- **Precedence hierarchy** following mathematical conventions
- **Implementation guidelines** for semantic analyzer

## Assignment and Context

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

### Type Annotations for Precision Loss

When reassignment might cause precision loss or truncation, explicit type annotations are required. This follows our "Explicit Danger, Implicit Safety" principle. **Important**: The type annotation must match the mutable variable's declared type - it is not a conversion but an explicit acknowledgment of the variable's type.

#### Integer Precision Loss

```hexen
mut small : i32 = 0
val large : i64 = 9223372036854775807  // Maximum i64 value

// ❌ Error: Potential truncation
// small = large                        // Error: Potential truncation, add ': i32' to acknowledge
// small = large : i64                  // Error: Type annotation must match variable's type (i32)

// ✅ Explicit acknowledgment of truncation
small = large : i32                    // Explicit: "I know this will truncate to i32"
small = 9223372036854775807 : i32      // Explicit: "I know this will truncate to i32"
```

#### Float Precision Loss

```hexen
mut single : f32 = 0.0
val double : f64 = 3.141592653589793   // More precise than f32 can represent

// ❌ Error: Potential precision loss
// single = double                      // Error: Potential precision loss, add ': f32' to acknowledge
// single = double : f64                // Error: Type annotation must match variable's type (f32)

// ✅ Explicit acknowledgment of precision loss
single = double : f32                   // Explicit: "I know this will lose precision to f32"
single = 3.141592653589793 : f32        // Explicit: "I know this will lose precision to f32"
```

#### Mixed Type Precision Loss

```hexen
mut precise : f32 = 0.0
val big_int : i64 = 9223372036854775807

// ❌ Error: Mixed types with potential precision loss
// precise = big_int                    // Error: Mixed types with potential precision loss, add ': f32'
// precise = big_int : i64              // Error: Type annotation must match variable's type (f32)

// ✅ Explicit acknowledgment
precise = big_int : f32                 // Explicit: "I know this will lose precision to f32"
precise = 9223372036854775807 : f32     // Explicit: "I know this will lose precision to f32"
```

### Type Annotation Rules

Type annotations (`: type`) follow a strict, consistent pattern throughout Hexen:

#### **Fundamental Rule: Explicit Result Type Declaration**
Type annotations are **always** an explicit remark of the **result type**:
- **Position**: Must be at the end of the right-hand side expression
- **Match Requirement**: Must exactly match the left-hand side type  
- **Purpose**: Explicit acknowledgment, not type conversion

```hexen
// ✅ Correct pattern: result type explicitly declared at end
val variable : i32 = expression : i32
mut variable : f32 = expression : f32

// ❌ Wrong patterns
// val variable : i32 = expression : f64    // Error: annotation doesn't match left side
// val variable : i32 = : i32 expression    // Error: annotation not at end
// val variable : i32 = (expression : f64)  // Error: nested annotation doesn't match
// val variable = expression : i32          // Error: type annotation requires explicit left side type
```

#### **Design Philosophy**
1. **Type Match**: Type annotations must match the target variable's declared type
2. **Not Conversion**: Type annotations are not conversions but explicit acknowledgments  
3. **Scope**: Type annotations apply to the entire expression on the right
4. **Precedence**: Type annotations have highest precedence in expressions
5. **Documentation**: They serve as explicit acknowledgment of precision loss
6. **Safety**: They prevent accidental precision loss or truncation
7. **Consistency**: Same rule applies everywhere - declarations, assignments, function returns

#### **The Universal Pattern**
```hexen
// Every type annotation follows this exact pattern:
target_variable : target_type = expression : SAME_target_type

// Examples across all contexts:
val number : i32 = 3.14 : i32           // Variable declaration
mut counter : i32 = large_value : i32   // Reassignment
func process() : f64 = calculation : f64 // Function return
array[index] : i32 = mixed_expr : i32   // Array assignment
```

**Key Points:**
- `: type` is **always** at the rightmost end of the expression
- `: type` **always** matches the left-hand side target type exactly
- `: type` is an **explicit acknowledgment**, not a type conversion
- `: type` **requires** an explicit type on the left side to match against
- This pattern works **everywhere** in Hexen - no exceptions

#### **Critical Rule: No Type Annotation Without Explicit Left Side Type**

Type annotations can **only** be used when there's an explicit type declaration on the left side:

```hexen
// ❌ FORBIDDEN: Type annotation without explicit left side type
// val result = 42 + 3.14 : f64        // Error: No explicit left side type to match
// val mixed = some_expr : i32         // Error: No explicit left side type to match
// mut counter = large_value : i32     // Error: No explicit left side type to match

// ✅ CORRECT: Explicit left side type that matches right side annotation
val result : f64 = (42 + 3.14) : f64   // Both sides have f64
val mixed : i32 = some_expr : i32       // Both sides have i32
mut counter : i32 = large_value : i32   // Both sides have i32

// ✅ CORRECT: No type annotation needed when left side provides context
val result : f64 = 42 + 3.14           // Left side provides f64 context
val mixed : i32 = some_expr             // Left side provides i32 context
```

**Why this rule exists:**
- **Consistency**: Type annotations are acknowledgments, not inference hints
- **Clarity**: The left side type must be explicit to make the contract clear
- **Safety**: Prevents ambiguous type annotation usage
- **Predictability**: Same pattern everywhere - no special cases

```hexen
mut result : i32 = 0
val a : i64 = 1000
val b : f64 = 3.14

// ❌ Error: Wrong type annotation
// result = a : i64                     // Error: Type annotation must match variable's type (i32)
// result = b : f64                     // Error: Type annotation must match variable's type (i32)

// ✅ Correct: Type annotation matches variable's type
result = a : i32                        // Explicit: "I know this will truncate to i32"
result = b : i32                        // Explicit: "I know this will truncate to i32"
result = (a + b) : i32                  // Explicit: "I know this will truncate to i32"
```

### Error Messages

Error messages for reassignment follow a consistent pattern, providing clear guidance:

```hexen
mut small : i32 = 0
val large : i64 = 9223372036854775807

// ❌ Error messages with guidance
// small = large
// Error: Potential truncation in assignment to i32 variable
// Add ': i32' to explicitly acknowledge truncation

// small = large : i64
// Error: Type annotation must match variable's type (i32)

// small = 3.14159
// Error: Mixed types with potential truncation in assignment to i32 variable
// Add ': i32' to explicitly acknowledge truncation

// ✅ Following the guidance
small = large : i32                     // Explicit acknowledgment of i32 type
small = 3.14159 : i32                   // Explicit acknowledgment of i32 type
```

### Benefits

1. **Type Safety**: All type conversions are explicit and intentional
2. **Code Clarity**: Type annotations document potential precision loss
3. **Error Prevention**: Accidental precision loss is caught at compile time
4. **Maintainability**: Clear documentation of type conversion intent
5. **Consistency**: Follows the "Explicit Danger, Implicit Safety" principle
6. **Type Integrity**: Type annotations enforce the mutable variable's declared type

## Uninitialized Variables (`undef`)

### Philosophy Consistency

The `undef` system follows the same **"explicit danger, implicit safety"** principle:

```hexen
// ❌ Implicit undef (dangerous - no type info)
val pending = undef             // Error: Cannot infer type

// ✅ Explicit undef (safe - type specified)
val pending : i32 = undef       // OK: Type explicitly provided
val config : string = undef     // OK: Type explicitly provided
```

### undef with Binary Operations

Uninitialized variables follow the same coercion rules once assigned:

```hexen
mut value : i32 = undef
value = 42                      // comptime_int → i32 (assignment context)
value = 10 + 20                 // comptime_int + comptime_int → i32 (assignment context)
```

## Error Messages

### Consistency with undef Pattern

Error messages follow the same pattern as `undef` errors, pointing to the same solution:

#### Type Coercion Errors
```
Type mismatch: variable 'x' declared as i32 but assigned value of type comptime_float
```

#### Mixed Operation Errors  
```
Mixed-type operation 'i32 + i64' requires explicit result type annotation
Add type annotation: 'val result : i64 = ...' or 'val result : f64 = ...'
```

#### undef Errors
```
Variable 'pending' must have either explicit type or value
```

All errors suggest the same solution: **add explicit type annotation**.

## Implementation Guidelines

### Expression Analysis with Context

The semantic analyzer should pass target type context through expression analysis:

```python
def _analyze_expression(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze expression with optional target type context for mixed operations."""
    
def _analyze_binary_operation(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze binary operation with context-guided type resolution."""
```

### Variable Declaration Enhancement

Variable declarations should pass their target type as context:

```python
def _analyze_variable_declaration_unified(self, name: str, type_annotation: str, value: Dict, ...):
    if type_annotation:
        var_type = self._parse_type(type_annotation)
        if value:
            # Pass target type as context for expression analysis
            value_type = self._analyze_expression(value, var_type)
```

### Context-Guided Resolution

Binary operations should use target context to resolve ambiguous type combinations:

```python
def _resolve_binary_operation_with_context(self, left: HexenType, right: HexenType, 
                                         op: str, target_type: Optional[HexenType], node: Dict) -> HexenType:
    # Safe cases (no context needed)
    if self._is_safe_binary_operation(left, right, op):
        return self._resolve_safe_binary_operation(left, right, op, node)
    
    # Ambiguous cases - need context
    if target_type is None:
        self._error(f"Mixed-type operation '{left.value} {op} {right.value}' requires explicit result type annotation", node)
        return HexenType.UNKNOWN
    
    # Context provided - guide the resolution
    return self._resolve_with_target_context(left, right, op, target_type, node)
```

## Examples

### Core Type System Concepts

```hexen
func demonstrate_type_system() : void = {
    // ===== Comptime Type Magic =====
    val default_int = 42        // comptime_int → i32 (default)
    val explicit_i64 : i64 = 42 // comptime_int → i64 (context)
    val as_float : f32 = 42     // comptime_int → f32 (context)
    val precise : f64 = 3.14    // comptime_float → f64 (default)
    val single : f32 = 3.14     // comptime_float → f32 (context)
    
    // ===== Type Coercion =====
    val wide : i64 = i32_value  // i32 → i64 (widening)
    val precise : f64 = f32_value  // f32 → f64 (widening)
    val as_float : f32 = i32_value  // i32 → f32 (conversion)
    
    // ===== undef with Type Safety =====
    val pending : i32 = undef   // ✅ OK: explicit type
    // val bad = undef          // ❌ Error: no type context
}

// For binary operations examples, see BINARY_OPS.md
```

## Benefits

### Developer Experience

1. **Ergonomic**: Common operations work seamlessly without explicit casting
2. **Predictable**: Same context pattern applies everywhere (variables, returns, assignments)
3. **Safe**: Dangerous operations require conscious choice through explicit typing
4. **Consistent**: One mental model for the entire type system

### Type Safety

1. **Compile-time validation**: All type compatibility checked at compile time
2. **No silent bugs**: Ambiguous operations cause compilation errors with helpful messages
3. **Precision preservation**: Developers must explicitly choose when to lose precision
4. **Context clarity**: Assignment target type makes developer intent explicit

### Future-Proof Design

1. **Extensible**: Pattern works with user-defined types, generics, and operator overloading
2. **Composable**: Binary operations can be nested arbitrarily with context guidance
3. **Maintainable**: Clear rules that are easy to understand and implement
4. **Consistent**: Same philosophy extends to all language features 