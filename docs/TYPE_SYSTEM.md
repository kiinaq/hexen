# Hexen Type System

*Version 1.0 - Complete Design Specification*

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

Integer and float literals have special "comptime" types that adapt to their usage context, eliminating the need for literal suffixes while maintaining type safety.

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
// Same literal, different target types
val as_i32 : i32 = 42   // comptime_int → i32
val as_i64 : i64 = 42   // comptime_int → i64  
val as_f32 : f32 = 42   // comptime_int → f32
val as_f64 : f64 = 42   // comptime_int → f64

// Same literal, different float precisions
val single : f32 = 3.14 // comptime_float → f32
val double : f64 = 3.14 // comptime_float → f64
```

### Default Type Resolution

When no explicit context is provided, comptime types resolve to default concrete types:

- `comptime_int` → `i32` (default integer type)
- `comptime_float` → `f64` (default float type)

```hexen
val default_int = 42    // i32 (inferred default)
val default_float = 3.14 // f64 (inferred default)
```

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

Binary operations in Hexen follow the **context-guided resolution** strategy with sophisticated precedence and type promotion rules. Due to the complexity and importance of this topic, it has been moved to a dedicated specification:

**→ See [BINARY_OPS.md](BINARY_OPS.md) for complete binary operations specification**

Key highlights:
- **Context-dependent division** (integer vs float based on target type)
- **Mixed-type expression resolution** with explicit context requirements
- **Precedence hierarchy** following mathematical conventions
- **Type promotion rules** for safe automatic coercion
- **Implementation guidelines** for semantic analyzer

## Assignment and Context

### Variable Declaration with Context

```hexen
// Target type provides context for expression analysis
val precise : f64 = (20 * 3.6) / 2     // Float math: 36.0
val truncated : i32 = (20 * 3.6) / 2   // Float math → integer: 36
val integer : i32 = 20 * 3 / 2         // Integer math: 30
```

### Assignment with Context

```hexen
mut flexible : f64 = 0.0
flexible = 42                   // comptime_int → f64 (assignment context)
flexible = (10 + 20) / 3        // Expression resolves to f64 context
```

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

### Complete Type System in Action

```hexen
func demonstrate_type_system() : void = {
    // ===== Comptime Type Magic =====
    val default_int = 42        // comptime_int → i32 (default)
    val explicit_i64 : i64 = 42 // comptime_int → i64 (context)
    val as_float : f32 = 42     // comptime_int → f32 (context)
    val precise : f64 = 3.14    // comptime_float → f64 (default)
    val single : f32 = 3.14     // comptime_float → f32 (context)
    
    // ===== Binary Operations =====
    val safe_ops = 42 + 100     // comptime_int + comptime_int = comptime_int
    val mixed_safe = 42 + 3.14  // comptime_int + comptime_float = comptime_float
    
    // ===== Context-Dependent Division =====
    val int_div : i32 = 7 / 3   // Integer division: 2
    val float_div : f64 = 7 / 3 // Float division: 2.333...
    val default_div = 7 / 3     // Default: 2.333... (float)
    
    // ===== Complex Expressions with Context =====
    val complex_int : i32 = (20 * 3) / 2       // All integer math: 30
    val complex_float : f64 = (20 * 3.6) / 2   // Float math: 36.0
    val complex_mixed : i32 = (20 * 3.6) / 2   // Float math → int: 36
    
    // ===== Mixed Concrete Types (Context Required) =====
    val a : i32 = 10
    val b : i64 = 20
    
    // val ambiguous = a + b                    // ❌ Error: needs context
    val as_i64 : i64 = a + b                   // ✅ OK: i32 → i64 widening
    val as_f64 : f64 = a + b                   // ✅ OK: both → f64
    
    // ===== undef with Type Safety =====
    val pending : i32 = undef                  // ✅ OK: explicit type
    // val bad = undef                          // ❌ Error: no type context
    
    // ===== Assignment Context =====
    mut flexible : f64 = 0.0
    flexible = 42                              // comptime_int → f64
    flexible = (a + b)                         // Would need: flexible = f64(a + b) concept
}

func main() : i32 = {
    // The beauty of Hexen's type system:
    // - Safe operations are implicit and ergonomic
    // - Dangerous operations require explicit context  
    // - One mental model applies everywhere
    // - No surprises, maximum safety
    
    return 0  // comptime_int → i32 (return type context)
}
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