# Hexen Function System 🦉

*Design Exploration & Specification*

## Overview

Hexen's function system extends the language's core philosophy of **"Explicit Danger, Implicit Safety"** to function declarations, parameters, and calls. Functions integrate seamlessly with the comptime type system, unified block system, and context-guided type resolution, providing a consistent and predictable programming model.

## Core Philosophy

### Design Principle: Ergonomic Literals + Transparent Costs

Functions in Hexen extend the language's core **"Ergonomic Literals + Transparent Costs"** philosophy to function declarations, parameters, and calls, integrating seamlessly with the comptime type system and unified type conversion rules.

- **Ergonomic Literals**: Function parameters provide type context for seamless comptime type adaptation
- **Transparent Costs**: All concrete type conversions in function arguments require explicit syntax (`value:type`)
- **Comptime Type Preservation**: Functions leverage the flexibility of comptime types until parameter context forces resolution
- **Unified Type Rules**: Same TYPE_SYSTEM.md conversion rules apply everywhere - no function-specific exceptions
- **Immutable by default** - parameters are read-only unless explicitly marked `mut`
- **Consistent with variable system** - same `val`/`mut` semantics apply to parameters

This pattern ensures that function calls provide clear, predictable type resolution while maintaining Hexen's cost transparency guarantees and maximizing the flexibility of comptime types.

## Function Declaration Syntax

### Basic Function Declaration

```hexen
// Basic function with parameters
func calculate(base: i32, multiplier: i32) : i32 = {
    return base * multiplier
}

// Void function with side effects
func log_message(message: string, level: string) : void = {
    // Simple void function - performs side effects, returns nothing
    return
}

// Function with mixed parameter types
func convert_and_scale(value: i64, scale: f64) : f64 = {
    // Mixed concrete types require explicit conversions (TYPE_SYSTEM.md rule)
    val result : f64 = value:f64 * scale  // ✅ Explicit conversion: i64 → f64, then f64 * f64 → f64
    return result
}
```

### Parameter Declaration Rules

1. **Syntax**: `parameter_name : parameter_type`
2. **Immutability**: Parameters are immutable by default (like `val` variables)
3. **Type Annotation**: Parameter types must be explicitly declared (no type inference for parameters)
4. **Multiple Parameters**: Comma-separated, no trailing comma allowed
5. **Naming**: Parameter names follow same rules as variable names

```hexen
// ✅ Valid parameter declarations
func process_data(input: string, format: string, debug: bool) : string = { ... }
func compute(x: f64, y: f64, z: f64) : f64 = { ... }
func setup(config_path: string) : void = { ... }

// ❌ Invalid parameter declarations
// func bad1(input) : void = { ... }                    // Error: Missing parameter type
// func bad2(input: string,) : void = { ... }           // Error: Trailing comma not allowed
// func bad3(123invalid: i32) : void = { ... }          // Error: Invalid parameter name
```

## Parameter Mutability System

### Immutable Parameters (Default)

By default, function parameters are **immutable** - they cannot be reassigned within the function body:

```hexen
func process_value(input: i32) : i32 = {
    val doubled : i32 = input * 2     // ✅ Explicit type required for concrete result (i32 * comptime_int → i32)
    // input = 42               // ❌ Error: Cannot reassign immutable parameter 'input'
    return doubled
}

func format_message(message: string, prefix: string) : string = {
    val formatted : string = prefix + ": " + message  // ✅ Explicit type required for concrete result (string + string + string → string)
    // message = "modified"     // ❌ Error: Cannot reassign immutable parameter 'message'
    return formatted
}
```

### Mutable Parameters (`mut`)

Functions can declare parameters as mutable using the `mut` keyword:

```hexen
func increment_and_return(mut counter: i32) : i32 = {
    counter = counter + 1       // ✅ OK: Mutable parameter can be reassigned
    return counter
}

func normalize_string(mut text: string) : string = {
    text = trim_whitespace(text)          // ✅ OK: Mutable parameter reassignment
    text = to_lowercase(text)             // ✅ OK: Subsequent reassignment
    return text
}

// Mutable parameters with type constraints (same rules as mut variables)
func process_with_precision_loss(mut result: f32, high_precision: f64) : f32 = {
    // result = high_precision              // ❌ Error: f64 → f32 requires explicit conversion
    result = high_precision:f32           // ✅ OK: Explicit conversion for precision loss
    return result
}
```

### Parameter vs Local Variable Distinction

Parameters and local variables follow the same mutability semantics but serve different roles:

```hexen
func demonstrate_scoping(input: i32, mut output: i32) : i32 = {
    // Parameters are in function scope
    val local_immutable : i32 = input * 2         // ✅ Explicit type required for concrete result (i32 * comptime_int → i32)
    mut local_mutable : i32 = output        // ✅ OK: mut variable with explicit type required
    
    // local_immutable = 42                 // ❌ Error: Cannot reassign val variable
    local_mutable = 42                      // ✅ OK: Can reassign mut variable
    output = local_mutable                  // ✅ OK: Can reassign mut parameter
    
    return output
}
```

## Type System Integration

### Comptime Type Preservation in Function Calls

Function parameters provide **type context** for comptime type resolution, but the real power comes from **comptime type preservation** - the same flexibility benefits from TYPE_SYSTEM.md extend to function contexts:

```hexen
func calculate_area(width: f64, height: f64) : f64 = {
    return width * height
}

func process_count(items: i32, multiplier: i32) : i32 = {
    return items * multiplier
}

// ✨ Comptime type preservation provides maximum flexibility
val math_result = 42 + 100 * 5          // comptime_int (preserved until context forces resolution!)
val float_calc = 10.5 * 2.0             // comptime_float (preserved until context forces resolution!)

// Same expressions adapt to different function contexts (maximum flexibility!)
val area1 : f64 = calculate_area(math_result, float_calc)     // ✅ Explicit type required for concrete result (function returns f64)
val count1 : i32 = process_count(math_result, 5)             // ✅ Explicit type required for concrete result (function returns i32)
val area2 : f64 = calculate_area(10.5, 20.3)                 // ✅ Explicit type required for concrete result (function returns f64)

// Traditional approach (still works, but less flexible)
val area3 : f64 = calculate_area(42, 30)                     // ✅ Explicit type required for concrete result (function returns f64)
val count2 : i32 = process_count(100, 5)                     // ✅ Explicit type required for concrete result (function returns i32)
```

### Mixed Parameter Types and Explicit Conversions

When functions have parameters of different types, each argument adapts to its corresponding parameter type following TYPE_SYSTEM.md rules. **Crucially, mixed concrete types require explicit conversions** to maintain cost transparency:

```hexen
func mixed_calculation(base: i32, multiplier: f64, precision: f32) : f64 = {
    val scaled : f64 = base:f64 * multiplier      // ✅ Explicit conversion: i32 → f64, then f64 * f64 → f64
    return scaled * precision:f64                 // ✅ Explicit conversion: f32 → f64, then f64 * f64 → f64 (return type context)
 }

// 🎯 Key Insight: Mixed concrete types still require explicit conversions in return statements
// Following TYPE_SYSTEM.md rules, all mixed concrete operations require explicit syntax
// even in return statements to maintain transparent costs

// ✨ Comptime literals adapt seamlessly to parameter contexts (ergonomic)
val result1 : f64 = mixed_calculation(42, 3.14, 1.5)  // ✅ Explicit type required for concrete result (function returns f64)

// 🔧 Mixed concrete types require explicit conversions (transparent costs)
val int_val : i32 = 10
val large_val : i64 = 20
val float_val : f64 = 3.14

// ❌ Error: Mixed concrete types forbidden without explicit conversion
// mixed_calculation(large_val, float_val, float_val)

// ✅ Explicit conversions make all costs visible
mixed_calculation(large_val:i32, float_val, float_val:f32)
// Breakdown:
// - large_val:i32 (explicit i64 → i32 conversion, cost visible)
// - float_val (f64 → f64, no conversion needed)
// - float_val:f32 (explicit f64 → f32 conversion, precision loss visible)

// Example with precision loss - explicit conversion required
func mixed_calculation_f32(base: i32, multiplier: f64, precision: f32) : f32 = {
    val scaled : f64 = base:f64 * multiplier      // ✅ Explicit conversion: i32 → f64, then f64 * f64 → f64
    // return scaled * precision              // ❌ Error: f64 * f32 → f64, but function returns f32 (precision loss)
    return (scaled * precision:f64):f32     // ✅ Explicit conversion: f32 → f64, then f64 * f64 → f64, then f64 → f32 (explicit conversion)
}
```

### Parameter Type Coercion Rules

Parameters follow the same type coercion rules as variable declarations:

```hexen
func process_numbers(small: i32, large: i64, precise: f64) : void = {
    // Parameters provide context for function calls
}

// ✅ Safe comptime type adaptations
process_numbers(42, 100, 3.14)         // All comptime literals adapt to parameter types

// ✅ All conversions require explicit syntax (TYPE_SYSTEM.md explicit rule)
val small_val : i32 = 10
val medium_val : i32 = 20  
val large_val : i64 = 30
process_numbers(small_val:i64, medium_val, large_val:f64)  // ✅ Explicit conversions: i32 → i64, i64 → f64

// ❌ Narrowing conversions require explicit conversion (TYPE_SYSTEM.md explicit rule)
val very_large : i64 = 9223372036854775807
val precise_val : f64 = 3.14159
// process_numbers(very_large, large_val, precise_val)  // Error: i64 → i32 requires ':i32'
process_numbers(very_large:i32, large_val, precise_val)  // ✅ Explicit narrowing conversion
```

## Function Calls and Unified Type Resolution

### Unified Type Resolution Strategy

Function calls follow the **exact same TYPE_SYSTEM.md conversion rules** as all other contexts - there are no function-specific type resolution rules:

1. **Unified Type Rules**: Each parameter type provides context following TYPE_SYSTEM.md Quick Reference Table
2. **Comptime Preservation**: Comptime types stay flexible until parameter context forces resolution  
3. **Explicit Conversions**: Mixed concrete types require `value:type` syntax (same as everywhere else)
4. **Independent Resolution**: Each argument resolves independently based on TYPE_SYSTEM.md rules
5. **Error Consistency**: Type errors follow the same patterns as variable declarations

```hexen
func process(small: i32, large: i64, precise: f64) : void = { return }

// ✅ Comptime literals adapt (TYPE_SYSTEM.md implicit rule - same as val x : i32 = 42)
process(42, 100, 3.14)

// ✅ Same concrete types work (TYPE_SYSTEM.md identity rule - same as val x : i32 = i32_val)  
val a : i32 = 10
val b : i64 = 20
val c : f64 = 3.14
process(a, b, c)                    // i32→i32, i64→i64, f64→f64 (identity)

// 🔧 Mixed concrete types need explicit conversion (TYPE_SYSTEM.md explicit rule - same as val x : i32 = i64_val:i32)
val large_val : i64 = 1000
// process(large_val, b, c)         // ❌ Error: i64 → i32 requires ':i32' 
process(large_val:i32, b, c)       // ✅ Explicit conversion (same pattern as variable assignment)

// ✅ Comptime type preservation works the same as with variables
val math_expr = 42 + 100           // comptime_int (preserved - same as variables!)
process(math_expr, math_expr, math_expr)  // Adapts to i32, i64, f64 respectively (maximum flexibility!)
```

### Complex Expression Arguments and Comptime Preservation

Arguments can be complex expressions that benefit from both **comptime type preservation** and **parameter type context**:

```hexen
func compute_result(base: f64, factor: f64) : f64 = {
    return base * factor
}

val x : i32 = 10
val y : i32 = 20

// ✨ Comptime expressions preserve flexibility until function call
val flexible_math : i32 = x + y           // ✅ Explicit type required for concrete result (i32 + i32 → i32)
val comptime_math = 42 + 100        // comptime_int + comptime_int → comptime_int (preserved!)

// Complex expressions adapt to parameter context
val result1 : f64 = compute_result(
    comptime_math,           // comptime_int → f64 (adapts to base parameter)
    3.14 * 2.0              // comptime_float * comptime_float → comptime_float → f64 (adapts to factor parameter)
)

// 🔧 Mixed-type expressions require explicit context (TYPE_SYSTEM.md rule)
val a : i32 = 5
val b : f64 = 2.5

// ❌ Error: Mixed concrete types in expression
// val result2 : f64 = compute_result(a + b, 1.0)

// ✅ Explicit conversion required for mixed concrete types
val result2 : f64 = compute_result(a:f64 + b, 1.0)
```

### Function Call Type Resolution Strategy

Function calls follow a **parameter-guided resolution approach**:

1. **Parameter Types as Context**: Each parameter type provides context for its corresponding argument
2. **Independent Resolution**: Each argument is resolved independently based on its parameter
3. **Expression Context**: Complex argument expressions use parameter type as target context
4. **Error Localization**: Type errors are reported per argument-parameter pair

### Type Annotations in Function Context

Type annotations in function calls follow the same rules as TYPE_SYSTEM.md - they use explicit conversion syntax for all type changes:

```hexen
func process(value: f64) : f64 = { return value * 2.0 }

val int_val : i32 = 10
val large_val : i64 = 1000

// ✅ CORRECT: All conversions require explicit syntax (TYPE_SYSTEM.md explicit rule)
val result1 : f64 = process(large_val:f64)          // ✅ Explicit conversion required (i64 → f64)

// ❌ ERROR: Direct precision loss without explicit conversion (TYPE_SYSTEM.md explicit rule)  
// val result2 : f32 = process(large_val)       // Error: f64 result → f32 requires explicit conversion

// ✅ CORRECT: Explicit conversion for precision loss (TYPE_SYSTEM.md explicit rule)
val result2 : f32 = process(large_val:f64):f32    // ✅ Explicit conversions: i64 → f64, then f64 → f32

// ✅ CORRECT: Mixed expressions with explicit conversion (TYPE_SYSTEM.md explicit rule)
val mixed_arg : f64 = int_val:f64 + 3.14        // i32 → f64 + comptime_float → f64 (explicit conversion)
val result3 : f64 = process(mixed_arg)                // ✅ Explicit type required for concrete result (function returns f64)

// Each argument resolved using TYPE_SYSTEM.md rules
func process_multi(int_param: i32, float_param: f64, string_param: string) : void = { 
    return
}

// ✅ Comptime literals adapt (TYPE_SYSTEM.md implicit rule)
process_multi(
    42,                 // comptime_int → i32 (parameter context)
    3.14,               // comptime_float → f64 (parameter context)  
    "hello"             // string → string (exact match)
)

// 🔧 Mixed concrete types require explicit conversion (TYPE_SYSTEM.md explicit rule)
val mixed_val : f64 = 2.5
// process_multi(mixed_val, 42, "test")       // ❌ Error: Argument 1: f64 → i32 requires ':i32'
process_multi(mixed_val:i32, 42, "test")     // ✅ Explicit conversion for argument 1
```

**Key Rule**: All type conversions use explicit `value:type` syntax - there are no special type annotation patterns for specific cases.

## Integration with Unified Block System

### Function Bodies as Unified Blocks

Function bodies use the same unified block system as other Hexen constructs, with the function's return type providing context. Expression blocks within functions follow the dual capability model from UNIFIED_BLOCK_SYSTEM.md:

- **`->`**: Produces the block's value (assigns to target variable)
- **`return`**: Early function exit (bypasses assignment, exits containing function)

This dual capability enables powerful patterns for validation, error handling, and optimization within function contexts.

```hexen
func simple_computation(input: i32, threshold: f64) : f64 = {
    // Statement block for setup (scoped)
    {
        val config_value = 100      // ✅ Comptime literal (comptime_int can be inferred)
        val is_valid : bool = input > 0    // ✅ Explicit type required for concrete result (i32 > comptime_int → bool)
    }
    
    // Expression block for intermediate calculation
    val intermediate = {
        val scaled : i32 = input * 2      // ✅ Explicit type required for concrete result (i32 * comptime_int → i32)
        val adjusted : i32 = scaled + 10  // ✅ Explicit type required for concrete result (i32 + comptime_int → i32)
        -> adjusted       // Expression block assigns value to intermediate
    }
    
    // Function return (explicit conversions required for mixed concrete types)
    // All mixed concrete operations require explicit conversions (TYPE_SYSTEM.md rule)
    return intermediate:f64 * threshold + 1.5    // i32 → f64 (explicit) * f64 + comptime_float → f64
}
```

### Expression Block Dual Capability in Functions

Expression blocks in function contexts support both `->` and `return` following UNIFIED_BLOCK_SYSTEM.md patterns:

```hexen
// Expression blocks with validation and early returns
func validate_and_process(input: i32) : i32 = {
    val processed = {
        if input < 0 {
            return -1           // Early function exit with error code
        }
        if input > 1000 {
            return -2           // Early function exit with different error
        }
        -> input * 2        // Success: -> processed value
    }
    
    // This code only runs if validation succeeded
    return processed + 10
}

// Expression blocks with performance optimization
func cached_calculation(key: string) : f64 = {
    val result = {
        val cached = lookup_cache(key)
        if cached != null {
            return cached       // Early function exit with cached result
        }
        
        val computed = expensive_operation(key)
        save_to_cache(key, computed)
        -> computed         // Cache miss: -> computed value
    }
    
    // This logging only happens for cache misses
    log_cache_miss(key)
    return result
}
```

### Parameter Scope and Block Interaction

Parameters are accessible throughout the function body and all nested blocks:

```hexen
func nested_scope_demo(base: i32, multiplier: f64) : f64 = {
    val outer_scope : i32 = base * 2      // ✅ Explicit type required for concrete result (i32 * comptime_int → i32)
    
    {
        // Statement block - parameters still accessible
        val inner_calc : i32 = base + 10  // ✅ Explicit type required for concrete result (i32 + comptime_int → i32)
        val converted : f64 = multiplier * 3.14  // ✅ Explicit type required for concrete result (f64 * comptime_float → f64)
        val debug_message = "calculation complete"  // ✅ String literal (comptime_string can be inferred)
    }
    
    val final_result = {
        // Expression block - parameters accessible
        val result : f64 = base:f64 * multiplier  // ✅ Explicit type and conversion required (i32 → f64 * f64 → f64)
        -> result                   // Expression block assigns value to final_result
    }
    
    return final_result    // Function return
}
```

## Error Handling and Messages

### Parameter-Related Error Messages

Hexen provides clear, actionable error messages for function parameter issues:

#### Parameter Declaration Errors
```hexen
// Missing parameter type
// func bad_func(input) : void = { ... }
// Error: Parameter 'input' missing type annotation
// Add explicit type: 'input: type'

// Invalid parameter name  
// func bad_func(123invalid: i32) : void = { ... }
// Error: Invalid parameter name '123invalid'
// Parameter names must start with a letter or underscore

// Trailing comma
// func bad_func(input: string,) : void = { ... }  
// Error: Trailing comma not allowed in parameter list
```

#### Parameter Assignment Errors
```hexen
func process(input: i32) : i32 = {
    // input = 42
    // Error: Cannot reassign immutable parameter 'input'
    // Parameters are immutable by default. Use 'mut input: i32' for mutable parameters
}
```

#### Function Call Argument Errors (TYPE_SYSTEM.md Consistency)
```hexen
func calculate(base: i32, factor: f64) : f64 = { 
    return base:f64 * factor        // ✅ Explicit conversion for mixed concrete types
}

val large_val : i64 = 9223372036854775807
// calculate(large_val, 3.14)
// Error: Argument 1: i64 → i32 requires explicit conversion (TYPE_SYSTEM.md explicit rule)
// Use explicit conversion: 'calculate(large_val:i32, 3.14)'

val int_val : i32 = 10
val float_val : f64 = 2.5
// calculate(int_val + float_val, 3.14)
// Error: Argument 1: Mixed concrete types 'i32 + f64' require explicit conversion (TYPE_SYSTEM.md explicit rule)
// Use explicit conversion: 'calculate(int_val:f64 + float_val, 3.14)'
// Or assign with explicit type: 'val temp : f64 = int_val:f64 + float_val; calculate(temp, 3.14)'

// ✅ Correct patterns following TYPE_SYSTEM.md rules
calculate(large_val:i32, 3.14)              // Explicit i64 → i32 conversion
calculate(int_val:f64 + float_val, 3.14)    // Explicit i32 → f64 conversion
val temp : f64 = int_val:f64 + float_val    // Alternative: explicit type assignment
calculate(temp, 3.14)                       // f64 → f64 (identity)
```

#### Mutable Parameter Type Errors
```hexen
func modify_value(mut result: f32, input: f64) : f32 = {
    // result = input
    // Error: Assignment to mutable parameter 'result': f64 cannot assign to f32 without explicit conversion
    // Add explicit conversion: 'result = input:f32'
}
```

## Advanced Usage Patterns

### Comptime Type Preservation in Complex Function Calls

Functions work seamlessly with comptime type preservation, enabling maximum flexibility:

```hexen
func complex_transform(
    base: i64,
    scale: f32, 
    offset: f64,
    iterations: i32
) : f64 = {
    mut accumulator : f64 = base:f64      // ✅ Explicit type required for mut (i64 → f64 conversion)
    
    {
        // Mixed concrete types require explicit context (BINARY_OPS.md rule)
        accumulator = (accumulator * scale:f64 + offset) // ✅ Explicit f32 → f64 conversion
    }
    
    return accumulator
}

// ✨ Comptime type preservation provides maximum flexibility
val comptime_base = 1000 + 500          // comptime_int (preserved!)
val comptime_scale = 2.0 + 0.5          // comptime_float (preserved!)
val comptime_offset = 10.0 * 3.14       // comptime_float (preserved!)
val comptime_iterations = 5 + 0         // comptime_int (preserved!)

// Same comptime expressions adapt to different parameter types!
val result1 : f64 = complex_transform(
    comptime_base,          // comptime_int → i64 (adapts to base parameter)
    comptime_scale,         // comptime_float → f32 (adapts to scale parameter)
    comptime_offset,        // comptime_float → f64 (adapts to offset parameter)
    comptime_iterations     // comptime_int → i32 (adapts to iterations parameter)
)

// Alternative: Direct comptime literals (traditional approach, still works)
val result2 : f64 = complex_transform(
    1000,           // comptime_int → i64 (adapts to base parameter)
    2.5,            // comptime_float → f32 (adapts to scale parameter)
    10.0,           // comptime_float → f64 (adapts to offset parameter)
    5               // comptime_int → i32 (adapts to iterations parameter)
)

// 🔧 Mixed concrete types require explicit conversions (TYPE_SYSTEM.md explicit rule)
val concrete_base : i32 = 1000      // Concrete type
val concrete_scale : f64 = 2.5      // Different concrete type

// ❌ Error: Mixed concrete types
// complex_transform(concrete_base, concrete_scale, 10.0, 5)

// ✅ Explicit conversions required
complex_transform(
    concrete_base:i64,      // i32 → i64 (explicit conversion)
    concrete_scale:f32,     // f64 → f32 (explicit conversion)
    10.0,                   // comptime_float → f64 (adapts)
    5                       // comptime_int → i32 (adapts)
)
```

## Return Statement Type Rules

**Return statements in Hexen follow the same TYPE_SYSTEM.md conversion rules as all other contexts** - mixed concrete types require explicit conversions:

```hexen
// Return statements require explicit conversions for mixed concrete types
func demonstrate_return_rules(a: i32, b: f64, c: f32) : f64 = {
    // Mixed concrete types require explicit conversions (TYPE_SYSTEM.md rule):
    
    // return a + b                          // ❌ Error: Mixed concrete types i32 + f64 require explicit conversion
    // return b * c                          // ❌ Error: Mixed concrete types f64 * f32 require explicit conversion
    // return a + b * c                      // ❌ Error: Mixed concrete types require explicit conversion
    
    // ✅ Explicit conversions required for mixed concrete types:
    return a:f64 + b                        // ✅ Explicit conversion: i32 → f64 + f64 → f64
    // return b * c:f64                     // ✅ Explicit conversion: f64 * (f32 → f64) → f64
    // return a:f64 + b * c:f64             // ✅ All conversions explicit
}

// Consistent with other contexts - explicit conversions always required:
func consistent_rules(a: i32, b: f64) : void = {
    // val result = a + b                   // ❌ Error: Mixed concrete types need explicit conversion
    val result : f64 = a:f64 + b           // ✅ Explicit conversion required everywhere
    return
}
```

### Function Composition with Type Context

```hexen
func scale_value(value: f64, factor: f64) : f64 = {
    return value * factor
}

func truncate_to_int(value: f64) : i32 = {
    return value:i32      // Explicit conversion
}

func process_chain(input: i32) : i32 = {
    // Function composition with explicit conversions
    val scaled : f64 = scale_value(input:f64, 2.5)        // ✅ Explicit conversion: i32 → f64 for parameter
    val final : i32 = truncate_to_int(scaled)         // ✅ Explicit type required for concrete result (function returns i32)
    return final
}
```

### Division Operations in Function Context

```hexen
// Float division (/) - always produces float results
func calculate_average(total: i32, count: i32) : f64 = {
    return total / count    // comptime_int / comptime_int → comptime_float → f64 (return type context)
}

// Integer division (\) - efficient truncation, integer-only
func calculate_quotient(dividend: i32, divisor: i32) : i32 = {
    return dividend \ divisor    // i32 \ i32 → i32 (integer division)
}

// Mixed division operations
func complex_calculation(base: i64, factor: f32) : f64 = {
    val precise_result : f64 = base:f64 / factor:f64    // ✅ Explicit conversions: i64 → f64 / f32 → f64 → f64
    // val truncated = base \ factor            // ❌ Error: Integer division requires integer operands
    return precise_result
}
```

### Comparison Operations in Function Context

```hexen
// Comparison operations with function parameters (strict type matching)
func compare_values(a: i32, b: i32) : bool = {
    return a > b                // ✅ i32 > i32 (same concrete types)
}

func validate_range(value: f64, min: f64, max: f64) : bool = {
    return value >= min && value <= max    // ✅ f64 comparisons with logical operators
}

// Mixed-type comparisons require explicit type conversion
func mixed_comparison(int_val: i32, float_val: f64) : bool = {
    // return int_val < float_val            // ❌ Error: Cannot compare i32 and f64
    val int_as_float : f64 = int_val:f64    // ✅ Explicit conversion before comparison
    return int_as_float < float_val         // ✅ f64 < f64 (same types after conversion)
}

// Function parameters in complex boolean expressions
func is_valid_user(age: i32, has_license: bool, credit_score: i32) : bool = {
    return age >= 18 && has_license && credit_score > 650
    // Each comparison: i32 >= i32, bool (direct use), i32 > i32
}
```

### Mutable Parameter Patterns

```hexen
// In-place modification pattern
func scale_vector(mut x: f64, mut y: f64, mut z: f64, scale_factor: f64) : void = {
    // Direct modifications using mutable parameters
    x = x * scale_factor      // ✅ Mutable parameter allows reassignment
    y = y * scale_factor      // ✅ f64 * f64 → f64 (same type assignment)
    z = z * scale_factor      // ✅ All operations use same concrete types
}

// Computation and modification pattern
func transform_values(mut result: f64, input1: i32, input2: f32) : f64 = {
    // Mutable parameter accumulates results
    result = result + input1:f64         // ✅ Explicit conversion: i32 → f64, then f64 + f64 → f64
    result = result * input2:f64         // ✅ Explicit conversion: f32 → f64, then f64 * f64 → f64
    return result                        // ✅ Return the accumulated result
}
```

## Benefits and Trade-offs

### Benefits

1. **Unified Type System**: Functions follow the exact same TYPE_SYSTEM.md conversion rules - no special cases or exceptions
2. **Comptime Type Flexibility**: Function calls leverage comptime type preservation for maximum adaptability
3. **Cost Transparency**: All concrete type conversions require explicit `value:type` syntax (same as everywhere else)
4. **Ergonomic Literals**: Comptime types adapt seamlessly to parameter contexts (zero runtime cost)
5. **Predictable Behavior**: Same conversion patterns work identically in all contexts
6. **Type Safety**: Compile-time parameter type checking prevents runtime errors
7. **Consistent Semantics**: Same `val`/`mut` mutability model as variables
8. **Performance Clarity**: No hidden conversions or unexpected computational costs
9. **Composability**: Functions integrate seamlessly with other language features

### Trade-offs  

1. **Learning Curve**: Must understand comptime type system and unified conversion rules
2. **Explicit Conversions**: All concrete type mixing requires visible `value:type` syntax
3. **Type Annotation Requirements**: Parameter types must be explicitly declared
4. **Complexity**: More sophisticated than simple parameter context systems
5. **Flexibility vs Safety**: More restrictive than dynamically typed languages, but safer

**Design Philosophy**: These trade-offs are intentional - they prioritize **predictability, safety, and cost transparency** over **implicit convenience**. The unified approach reduces cognitive load by applying the same rules everywhere, even though those rules have some complexity.

### Comparison with Other Languages

| Feature | Hexen | Rust | C++ | Python |
|---------|-------|------|-----|--------|
| **Parameter Types** | Explicit, required | Explicit, required | Explicit, required | Optional hints |
| **Mutability** | `mut` keyword | `mut` keyword | Manual references | No built-in concept |
| **Type Context** | Parameters provide context | Limited inference | Manual casting | Dynamic typing |
| **Safety** | Compile-time checks | Memory safe | Manual management | Runtime checking |

## Future Extensions

### Default Parameters (Phase II)

```hexen
// Future: Default parameter values
func setup_connection(host: string = "localhost", port: i32 = 8080) : bool = {
    // Placeholder implementation for future syntax demonstration
    val connection_established : bool = host != "" && port > 0  // ✅ Explicit type required for concrete result (string != string && i32 > comptime_int → bool)
    return connection_established
}

// Calls with defaults
val success1 : bool = setup_connection()                    // ✅ Explicit type required for concrete result (function returns bool)
val success2 : bool = setup_connection("production.com")   // ✅ Explicit type required for concrete result (function returns bool)
val success3 : bool = setup_connection("staging.com", 9090) // ✅ Explicit type required for concrete result (function returns bool)
```

### Generic Functions (Phase III)

```hexen
// Future: Generic function parameters  
func transform<T>(input: T, processor: func(T) : T) : T = {
    return processor(input)
}
```

### Function Overloading (Future)

```hexen
// Future: Function overloading based on parameter types
func process(input: i32) : i32 = { ... }
func process(input: f64) : f64 = { ... }
func process(input: string) : string = { ... }
```

## Conclusion

The Function System extends Hexen's **"Ergonomic Literals + Transparent Costs"** philosophy to function declarations and calls, providing type-safe parameter handling with seamless comptime type integration. By working within the unified TYPE_SYSTEM.md conversion rules, functions maintain complete consistency while leveraging the flexibility and cost transparency of the type system.

The function system's key contributions:

- **Ergonomic Function Calls**: Comptime types preserve flexibility until parameter context forces resolution
- **Transparent Conversion Costs**: All concrete type mixing requires explicit `value:type` syntax  
- **Unified Type Rules**: Same TYPE_SYSTEM.md conversion rules apply everywhere - no function-specific exceptions
- **Comptime Type Preservation**: Functions leverage the full flexibility of comptime types for maximum adaptability
- **Consistent Safety**: Same `val`/`mut` semantics and immutability patterns throughout

By integrating seamlessly with the comptime type system and unified block system, functions enable powerful composition patterns while maintaining Hexen's core design principles. The emphasis on explicit type annotations and immutable-by-default parameters reinforces the language's safety-first approach, while comptime type preservation ensures that function calls provide natural, predictable type resolution without sacrificing flexibility.

This foundation is extensible and ready to support advanced features like default parameters, generics, and function overloading in future language phases, all while maintaining the unified **"Ergonomic Literals + Transparent Costs"** philosophy.

---
