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
   - Comparison operations preserve comptime types when comparing same types
   - No automatic type promotion or conversion
   - Clear, predictable semantics

3. **Intentionally More Restrictive Than Arithmetic Operations**:
   - **Arithmetic operations**: Allow mixed types with explicit context (e.g., `val result : f64 = int_val + float_val`)
   - **Comparison operations**: Require identical types for type safety
   - **Reason**: The `bool` result type cannot provide meaningful context for resolving operand type mismatches
   - **Design choice**: Eliminates ambiguity about which type conversion should occur in comparisons

4. **Type-Safe Comparisons**:
   - Only identical types can be compared directly
   - No automatic type promotion or conversion
   - Mixed types require separate type conversion handling before comparison
   - No comparison between fundamentally different types
   - Attempting to compare different types results in a compiler error

## Comparison Operations

### Basic Comparisons

Comparison operators produce boolean results and follow strict type matching:

```hexen
// Same type comparisons - comptime types preserved
val result1 = 10 < 20            // comptime_int < comptime_int → bool
val result2 = 42 == 42           // comptime_int == comptime_int → bool

// Same type float comparisons
val result3 = 3.14 > 2.71        // comptime_float > comptime_float → bool
val result4 = 3.14 == 3.14       // comptime_float == comptime_float → bool

// Same type string comparisons
val result5 = "hello" == "world" // string == string → bool

// Same concrete type comparisons
val a : i32 = 10
val b : i32 = 20
val result6 = a < b              // i32 < i32 → bool
```

### Mixed-Type Comparisons

Mixed-type comparisons require type conversion to be handled separately:

```hexen
val int_val : i32 = 10
val float_val : f64 = 10.0

// ❌ Type error - cannot compare different types directly
// val comparison1 = int_val < float_val       // Error: Cannot compare i32 and f64
// val comparison2 = 42 > 3.14                 // Error: Cannot compare comptime_int and comptime_float

// ❌ Type error - cannot compare different fundamental types
val str_val : string = "hello"
val int_val : i32 = 42
// val invalid = str_val == int_val            // Error: Cannot compare string and i32
```

### Why Comparisons Are More Restrictive Than Arithmetic

Unlike arithmetic operations, comparison operations cannot benefit from context-guided type resolution:

#### **Arithmetic Operations: Context Helps Resolve Type Conflicts**
```hexen
// ✅ Target type provides context for resolving mixed operands
val result : f64 = int_val + float_val  // The f64 target guides: int_val coerces to f64, then add
val sum : i64 = small_int + large_int   // The i64 target guides: small_int coerces to i64, then add
```

#### **Comparison Operations: No Meaningful Context Available**
```hexen
// ❌ The bool result type cannot guide operand resolution
// val result : bool = int_val < float_val  // Which should coerce? i32→f64 or f64→i32?
// val check : bool = small_int > large_int // Which should coerce? i32→i64 or i64→i32?

// ✅ Must handle type conversion explicitly before comparison
val int_as_float : f64 = int_val        // i32 → f64 (widening coercion)
val result : bool = int_as_float < float_val

val large_as_small : i32 = large_int : i32  // i64 → i32 (explicit truncation acknowledgment)
val check : bool = small_int < large_as_small
```

#### **Design Rationale**
1. **Eliminates Ambiguity**: No hidden decisions about which operand should coerce
2. **Prevents Subtle Bugs**: Avoids precision loss or overflow in implicit conversions  
3. **Makes Intent Explicit**: Developer must choose the comparison precision level
4. **Type Safety**: Catches potential logic errors at compile time

### Type Resolution Rules

1. **Comparison Operations**:
   - Only identical types can be compared directly
   - No automatic type promotion or conversion
   - Mixed types require separate type conversion handling before comparison
   - Always produce boolean result
   - **Contrast with arithmetic**: Arithmetic operations allow mixed types with explicit target context, comparisons do not

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
   - Only identical types can be compared directly
   - Mixed types require separate type conversion handling
   ```hexen
   val int_val : i32 = 10
   val float_val : f64 = 10.0
   
   // ❌ Invalid: Cannot compare different types
   // val comparison1 = int_val < float_val        // Error: Cannot compare i32 and f64
   
   // ❌ Invalid: Cannot compare different fundamental types
   val str_val : string = "hello"
   // val invalid = str_val == int_val            // Error: Cannot compare string and i32
   ```

### Basic Logical Operations

```hexen
// Basic boolean operations
val and_result = true && false   // bool && bool → bool
val or_result = true || false    // bool || bool → bool
val not_result = !true           // !bool → bool

// Complex boolean expressions with explicit type handling
val age : i32 = 25
val has_license : bool = true
val has_car : bool = false

val can_drive = age >= 18 && has_license
val needs_permission = age < 18 || !has_license
val can_borrow_car = has_license && !has_car
```

### Short-Circuit Evaluation

Logical operators use short-circuit evaluation to optimize performance:

```hexen
val a : bool = false
val b : bool = true

// Short-circuit AND: if a is false, b is never evaluated
val result1 = a && expensive_function()  // expensive_function() not called

// Short-circuit OR: if a is true, b is never evaluated
val result2 = a || expensive_function()  // expensive_function() is called

// Complex short-circuit example
val age : i32 = 25
val has_license : bool = false

// If age < 18 is false, has_license is never checked
val needs_permission = age < 18 || !has_license
```

### Logical Operator Precedence

Logical operators have lower precedence than comparison operators:

```hexen
// These are equivalent:
val result1 = (age >= 18) && (has_license == true)
val result2 = age >= 18 && has_license == true

// Complex precedence example
val result3 = age >= 18 && has_license || age < 18 && !has_license
// Equivalent to:
// (age >= 18 && has_license) || (age < 18 && !has_license)
```

### Mutable Assignment with Logical Operations

```hexen
mut status : bool = false

// Safe assignments - boolean expressions only
status = true
status = age >= 18 && has_license

// ❌ Error: Non-boolean value
// status = 42                         // Error: i32 cannot be assigned to bool
// status = "yes"                      // Error: string cannot be assigned to bool

// ✅ Valid: Complex boolean expressions
status = age >= 18 && (has_license || has_car)
status = !status || (age < 18 && has_license)
```

## Implementation Guidelines

### Expression Analysis with Context

The semantic analyzer should handle comparison and logical operations following our strict type system:

```python
def _analyze_comparison(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze comparison operation with strict type checking."""
    
def _analyze_logical_operation(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze logical operation with strict boolean type checking."""
```

### Type Resolution Rules

1. **Comparison Operations**:
   - Only identical types can be compared directly
   - No automatic type promotion or conversion
   - Mixed types require separate type conversion handling before comparison
   - Always produce boolean result
   - **Intentionally more restrictive than arithmetic operations** for type safety

2. **Logical Operations**:
   - Require boolean operands
   - No type coercion
   - Always produce boolean result
   - Follow short-circuit evaluation

3. **Assignment Context**:
   - Target type must be bool for logical/comparison operations
   - The `bool` result type cannot provide meaningful context for resolving operand type mismatches
   - Explicit type conversion required for mixed-type operands before comparison

## Benefits

### Developer Experience

1. **Ergonomic**: Common boolean operations work seamlessly
2. **Predictable**: Strict type rules apply everywhere
3. **Safe**: No implicit type coercion
4. **Consistent**: One mental model for all operations

### Type Safety

1. **Compile-time validation**: All type compatibility checked at compile time
2. **No silent bugs**: Ambiguous operations cause compilation errors
3. **Clear semantics**: Boolean operations are always explicit
4. **Type clarity**: Type conversion is handled separately from comparison operations

### Future-Proof Design

1. **Extensible**: Pattern works with user-defined types
2. **Composable**: Operations can be nested arbitrarily
3. **Maintainable**: Clear rules that are easy to understand
4. **Consistent**: Same philosophy extends to all language features 