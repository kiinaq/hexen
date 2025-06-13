# Hexen Comparison Operations 🦉

*Design and Implementation Specification*

## Overview

Hexen's comparison and logical operations system follows the same **"Explicit Danger, Implicit Safety"** philosophy as our type system, with clear rules for type resolution and boolean operations. The system is built on top of our comptime type system, ensuring consistent behavior across all comparison and logical expressions.

### Key Design Principles

1. **Boolean Result Type**:
   - All comparison operations produce boolean results
   - No implicit coercion to boolean from other types
   - Clear, predictable boolean semantics

2. **Comptime Type Foundation**: 
   - All literals start as comptime types
   - Comparison operations preserve comptime types when possible
   - Context guides resolution to concrete types
   - Clear, predictable semantics

3. **Type-Safe Comparisons**:
   - Only comparable types can be compared
   - Mixed numeric types follow comptime promotion rules
   - No comparison between fundamentally different types

## Comparison Operations

### Basic Comparisons

Comparison operators produce boolean results and follow our comptime type system:

```hexen
// Comptime integer comparisons
val result1 : bool = 10 < 20            // comptime_int < comptime_int → bool
val result2 : bool = 42 == 42           // comptime_int == comptime_int → bool

// Comptime float comparisons
val result3 : bool = 3.14 > 2.71        // comptime_float > comptime_float → bool
val result4 : bool = 3.14 == 3.14       // comptime_float == comptime_float → bool

// String comparisons
val result5 : bool = "hello" == "world" // string == string → bool
```

### Mixed-Type Comparisons

Mixed-type comparisons follow our comptime promotion rules:

```hexen
val int_val : i32 = 10
val float_val : f64 = 10.0

// Comptime with concrete types
val comparison1 : bool = int_val < 42              // i32 < comptime_int → bool
val comparison2 : bool = 3.14 > float_val          // comptime_float > f64 → bool

// Mixed concrete types
val comparison3 : bool = int_val < float_val       // i32 < f64 → bool (comptime_float adapts to f64)
val comparison4 : bool = 42 > 3.14                 // comptime_int > comptime_float → bool

// ❌ Type error - cannot compare different fundamental types
val str_val : string = "hello"
val int_val : i32 = 42
// val invalid = str_val == int_val                // Error: Cannot compare string and i32
```

### Comparison Operator Precedence

Comparison operators have lower precedence than arithmetic operators but higher than logical operators:

```hexen
// These are equivalent:
val result1 : bool = (a + b) < (c + d)            // Parentheses for clarity
val result2 : bool = a + b < c + d                // Same precedence as above

// Complex precedence example
val result3 : bool = a + b < c + d && e > f       // (a + b) < (c + d) && (e > f)
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
   // val invalid1 = age && has_license            // Error: i32 cannot be used in logical operation
   // val invalid2 = "yes" || has_license          // Error: string cannot be used in logical operation
   ```

2. **Comparison Results**:
   - Comparison operators produce boolean results
   - Mixed type comparisons follow comptime promotion rules
   ```hexen
   val int_val : i32 = 10
   val float_val : f64 = 10.0
   
   // ✅ Valid: comptime_float adapts to f64 for comparison
   val comparison1 : bool = int_val < float_val
   
   // ✅ Valid: comptime_int adapts to f64 for comparison
   val comparison2 : bool = 42 > 3.14
   
   // ❌ Invalid: Cannot compare different fundamental types
   val str_val : string = "hello"
   // val invalid = str_val == int_val            // Error: Cannot compare string and i32
   ```

### Basic Logical Operations

```hexen
// Basic boolean operations
val and_result : bool = true && false   // bool && bool → bool
val or_result : bool = true || false    // bool || bool → bool
val not_result : bool = !true           // !bool → bool

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

// Safe assignments - comptime types adapt to context
status = true                          // bool → bool
status = age >= 18 && has_license      // bool → bool

// ❌ Error: Non-boolean value
// status = 42                         // Error: i32 cannot be assigned to bool
// status = "yes"                      // Error: string cannot be assigned to bool

// ✅ Valid: Complex boolean expressions
status = age >= 18 && (has_license || has_car)
status = !status || (age < 18 && has_license)
```

## Implementation Guidelines

### Expression Analysis with Context

The semantic analyzer should handle comparison and logical operations following our comptime system:

```python
def _analyze_comparison(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze comparison operation with optional target type context."""
    
def _analyze_logical_operation(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze logical operation with context-guided type resolution."""
```

### Type Resolution Rules

1. **Comparison Operations**:
   - Start with comptime types for literals
   - Apply comptime promotion rules for mixed types
   - Always produce boolean result
   - Require comparable types

2. **Logical Operations**:
   - Require boolean operands
   - No type coercion
   - Always produce boolean result
   - Follow short-circuit evaluation

3. **Assignment Context**:
   - Target type guides expression resolution
   - Comptime types adapt to boolean context
   - No implicit coercion to boolean

## Benefits

### Developer Experience

1. **Ergonomic**: Common boolean operations work seamlessly
2. **Predictable**: Same context pattern applies everywhere
3. **Safe**: No implicit boolean coercion
4. **Consistent**: One mental model for all operations

### Type Safety

1. **Compile-time validation**: All type compatibility checked at compile time
2. **No silent bugs**: Ambiguous operations cause compilation errors
3. **Clear semantics**: Boolean operations are always explicit
4. **Context clarity**: Assignment target type makes intent clear

### Future-Proof Design

1. **Extensible**: Pattern works with user-defined types
2. **Composable**: Operations can be nested arbitrarily
3. **Maintainable**: Clear rules that are easy to understand
4. **Consistent**: Same philosophy extends to all language features 