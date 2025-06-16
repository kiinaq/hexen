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

### Core Concept

Integer and float literals have special "comptime" types that adapt to their usage context, eliminating the need for literal suffixes while maintaining type safety. This design follows Hexen's core principles:

- **Clean**: One clear default type (i32) for system programming
- **Ergonomic**: No need for type suffixes, but explicit when needed
- **Logic**: Natural progression from comptime to concrete types
- **Pragmatic**: Optimized for the most common system programming needs

### Default Type Resolution

The comptime type system provides a foundation for context-guided type resolution:

1. **System Programming Efficiency**
   - Comptime types adapt to their usage context
   - When no context is provided, `i32` is often the most efficient choice for system programming
   - This matches the natural word size of most modern systems
   - Aligns with system call interfaces and memory layouts
   - Balances range with memory efficiency

2. **Clean Design**
   - Comptime types eliminate choice paralysis
   - No need to remember multiple default types
   - Consistent behavior across all literals
   - Predictable performance characteristics through context

3. **Explicit Promotion**
   - When wider range is needed, explicit type annotation required
   - Makes performance implications visible in the code
   - Encourages conscious decisions about integer width
   - Prevents accidental use of wider types

```hexen
// Comptime types adapt to context
val default_int = 42    // comptime_int (no context, will be i32 in system programming)
val counter = 1000      // comptime_int (no context, will be i32 in system programming)

// Explicit context guides type resolution
val large_num : i64 = 0xFFFFFFFF + 1  // comptime_int → i64 (explicit context)
val precise : f64 = 3.14159265359     // comptime_float → f64 (explicit context)
```

### Literal Type Inference

```hexen
// Integer literals become comptime_int
val a = 42              // comptime_int literal
val b = -123            // comptime_int literal  
val c = 0               // comptime_int literal

// Float literals become comptime_float
val x = 3.14            // comptime_float literal
val y = -2.5            // comptime_float literal
val z = 0.0             // comptime_float literal
```

### Context-Dependent Resolution

The comptime system allows the same literal to become different types based on context:

```hexen
// Same literal, different target types - guided by context
val as_i32 : i32 = 42   // comptime_int → i32 (context-guided)
val as_i64 : i64 = 42   // comptime_int → i64 (context-guided)
val as_f32 : f32 = 42   // comptime_int → f32 (context-guided)
val as_f64 : f64 = 42   // comptime_int → f64 (context-guided)

// Float literals follow same context-guided pattern
val single : f32 = 3.14 // comptime_float → f32 (context-guided)
val double : f64 = 3.14 // comptime_float → f64 (context-guided)
```

### Design Rationale

The comptime type system embodies Hexen's core principles:

1. **Clean & Predictable**
   - One default type (i32) for integers
   - One default type (f64) for floats
   - No hidden type promotions
   - Explicit when deviating from defaults

2. **System Programming Focus**
   - i32 as default matches system interfaces
   - Efficient memory usage by default
   - Explicit promotion when needed
   - No performance surprises

3. **Ergonomic & Safe**
   - No type suffixes needed
   - Context guides type resolution
   - Explicit annotations for non-default types
   - Clear performance implications

4. **Pragmatic & Practical**
   - Optimized for common use cases
   - Explicit when performance characteristics change
   - No complex type inference rules
   - Clear upgrade path when needed

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
- `f32`, `f64` (float types only)
- **Cannot** coerce to integer types (precision loss prevention)
- **Cannot** coerce to `bool`, `string` (type safety)

```hexen
// ✅ Safe comptime coercions
val int_var : i32 = 42      // comptime_int → i32
val float_var : f64 = 42    // comptime_int → f64
val precise : f32 = 3.14    // comptime_float → f32

// ❌ Unsafe comptime coercions (compilation errors)
val bad_bool : bool = 42       // comptime_int cannot → bool
val bad_string : string = 3.14 // comptime_float cannot → string
val bad_int : i32 = 3.14       // comptime_float cannot → i32 (precision loss)
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

When reassignment might cause precision loss or truncation, explicit type annotations are required. This follows our "Explicit Danger, Implicit Safety" principle.

#### Integer Precision Loss

```hexen
mut small : i32 = 0
val large : i64 = 9223372036854775807  // Maximum i64 value

// ❌ Error: Potential truncation
// small = large                        // Error: Potential truncation, add ': i32' to acknowledge

// ✅ Explicit acknowledgment of truncation
small = large : i32                    // Explicit: "I know this will truncate"
small = 9223372036854775807 : i32      // Explicit truncation of literal
```

#### Float Precision Loss

```hexen
mut single : f32 = 0.0
val double : f64 = 3.141592653589793   // More precise than f32 can represent

// ❌ Error: Potential precision loss
// single = double                      // Error: Potential precision loss, add ': f32' to acknowledge

// ✅ Explicit acknowledgment of precision loss
single = double : f32                   // Explicit: "I know this will lose precision"
single = 3.141592653589793 : f32        // Explicit precision loss of literal
```

#### Mixed Type Precision Loss

```hexen
mut precise : f32 = 0.0
val big_int : i64 = 9223372036854775807

// ❌ Error: Mixed types with potential precision loss
// precise = big_int                    // Error: Mixed types with potential precision loss, add ': f32'

// ✅ Explicit acknowledgment
precise = big_int : f32                 // Explicit: "I know this will lose precision"
precise = 9223372036854775807 : f32     // Explicit precision loss of literal
```

### Type Annotation Rules

1. **Scope**: Type annotations apply to the entire expression
2. **Precedence**: Type annotations have highest precedence in expressions
3. **Documentation**: They serve as explicit acknowledgment of precision loss
4. **Safety**: They prevent accidental precision loss or truncation

```hexen
mut result : i32 = 0
val a : i64 = 1000
val b : f64 = 3.14

// These are equivalent - type annotation applies to whole expression
result = a : i32                        // (a) : i32
result = a + b : i32                    // (a + b) : i32
result = (a + b) : i32                  // ((a + b)) : i32

// Complex expressions with potential precision loss
result = a * b : i32                    // (a * b) : i32
result = (a + b) * (a - b) : i32        // ((a + b) * (a - b)) : i32
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

// small = 3.14159
// Error: Mixed types with potential truncation in assignment to i32 variable
// Add ': i32' to explicitly acknowledge truncation

// ✅ Following the guidance
small = large : i32                     // Explicit acknowledgment
small = 3.14159 : i32                   // Explicit acknowledgment
```

### Benefits

1. **Type Safety**: All type conversions are explicit and intentional
2. **Code Clarity**: Type annotations document potential precision loss
3. **Error Prevention**: Accidental precision loss is caught at compile time
4. **Maintainability**: Clear documentation of type conversion intent
5. **Consistency**: Follows the "Explicit Danger, Implicit Safety" principle

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