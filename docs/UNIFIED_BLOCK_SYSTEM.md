# Hexen Unified Block System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's unified block system design, showcasing how a single syntax can provide context-driven behavior while maintaining semantic clarity and integrating seamlessly with the comptime type system.

## Overview

Hexen's **Unified Block System** represents one of the language's most elegant design decisions: using a single `{ }` block syntax for all contexts while providing context-appropriate behavior. This creates a consistent, learnable mental model where blocks behave predictably based on their usage context.

## Core Philosophy

### Design Principle: "One Syntax, Context-Driven Behavior"

All Hexen constructs use the same block syntax `{ statements }`, but context determines their specific behavior:

- **Expression blocks**: Produce values using `assign`, support function `return` for control flow
- **Statement blocks**: Execute code, allow function returns, no value production
- **Function bodies**: Unified with all other blocks, context provides return type validation
- **Scope isolation**: ALL blocks manage their own scope regardless of context

This unification eliminates cognitive overhead while maintaining precise semantic control through context.

### Philosophy Alignment

The unified block system embodies Hexen's core principles:
- **"Clean: There is only one way to do a thing"** - Single block syntax for all contexts
- **"Logic: No tricks to remember, only natural approaches"** - Context determines behavior naturally
- **"Pedantic to write, but really easy to read"** - Explicit context makes intent clear

## Compile-Time vs Runtime Expression Blocks

### The Fundamental Distinction

Expression blocks in Hexen fall into two critical categories based on their evaluability, which determines their interaction with the comptime type system:

#### **✅ Compile-Time Evaluable Blocks**
**Can preserve comptime types** - Maximum flexibility until context forces resolution

**Criteria**:
- All operations involve only comptime literals or constants
- All conditions are compile-time constants
- No runtime function calls (only pure comptime operations)
- All computations can be evaluated at compile-time

**Benefits**:
- **Comptime type preservation**: Block result stays flexible (follows [TYPE_SYSTEM.md](TYPE_SYSTEM.md) patterns)
- **Zero runtime cost**: All computation happens at compile-time
- **Context adaptation**: Same block result adapts to different target types
- **Maximum flexibility**: One expression, multiple concrete uses

> **💡 Quick Reference**: For essential comptime type patterns, see [COMPTIME_QUICK_REFERENCE.md](COMPTIME_QUICK_REFERENCE.md)

```hexen
// ✅ Compile-time evaluable (comptime type preservation)
val flexible_computation = {
    val base = 42              // comptime_int
    val multiplier = 100       // comptime_int  
    val factor = 3.14          // comptime_float
    val result = base * multiplier + factor  // All comptime operations → comptime_float
    assign result              // Block result: comptime_float (preserved!)
}

// Same block result adapts to different contexts (maximum flexibility!)
val as_f32 : f32 = flexible_computation    // comptime_float → f32 (implicit)
val as_f64 : f64 = flexible_computation    // SAME source → f64 (different context!)
val as_i32 : i32 = flexible_computation:i32  // SAME source → i32 (explicit conversion)
```

#### **❌ Runtime Evaluable Blocks**
**Require explicit context** - Cannot preserve comptime types due to runtime operations

**Criteria**:
- Contains runtime function calls or computations (**functions always return concrete types**) 
- Involves runtime conditions or control flow
- Mixes comptime and runtime values
- Cannot be fully evaluated at compile-time

**Requirements**:
- **Explicit type annotation required**: Target variable must specify concrete type
- **No comptime type preservation**: Block result immediately resolves to concrete type
- **Transparent costs**: All type conversions must be explicit

```hexen
// ❌ Runtime evaluable (explicit context required)
val runtime_result : f64 = {              // Context REQUIRED! Cannot preserve comptime types
    val user_input = get_user_input()     // Runtime function call → concrete type (functions always return concrete types)
    val base = 42                         // comptime_int
    if user_input > 0 {                   // Runtime condition
        assign base * user_input:f64      // Mixed: comptime_int * concrete → explicit conversion needed
    } else {
        assign 0.0                        // All paths must resolve to target type (f64)
    }
}
```

#### **🔄 Mixed Blocks (Runtime Category)**
Blocks that combine comptime and runtime operations are treated as **runtime evaluable**:

```hexen
// 🔄 Mixed (comptime + runtime = runtime, explicit context required)
val mixed_result : f64 = {                // Context REQUIRED!
    val comptime_calc = 42 * 3.14         // comptime_int * comptime_float → comptime_float
    val runtime_multiplier = get_multiplier()  // Runtime function call → concrete type (functions always return concrete types)
    assign comptime_calc * runtime_multiplier:f64  // Mixed → explicit conversion needed
}
```

### The Ambiguity Solution

This compile-time vs runtime distinction solves the **"untyped literal problem"** that exists in many systems programming languages:

#### **Traditional Problem**: Untyped Expressions
```c
// Traditional languages: ambiguous without explicit types
auto result = complex_calculation();  // What type? Depends on hidden defaults
```

#### **Hexen's Solution**: Context-Driven Resolution
```hexen
// ✅ Compile-time case: No ambiguity (compiler evaluates everything)
val flexible = { assign 42 + 100 * 3.14 }  // All comptime → comptime_float (flexible!)
val as_needed : f32 = flexible             // Context provides resolution when needed

// ✅ Runtime case: Explicit context required (eliminates ambiguity)  
val concrete : f64 = { assign get_value() + 42 }  // Runtime → explicit type required
```

**Key Insights**:
1. **Compile-time cases**: No ambiguity because compiler can evaluate everything
2. **Runtime cases**: Explicit context required, eliminating ambiguity at source
3. **No default types needed**: Context is always available when type resolution is required
4. **Best of both worlds**: Ergonomic literals + explicit runtime costs
5. **Function calls**: Any block containing function calls becomes runtime evaluable (functions always return concrete types)

### Integration with Type System

This distinction perfectly aligns with Hexen's **"Ergonomic Literals + Transparent Runtime Costs"** philosophy from [TYPE_SYSTEM.md](TYPE_SYSTEM.md):

- **Compile-time blocks**: Follow comptime type flexibility patterns (ergonomic literals)
- **Runtime blocks**: Require explicit type context (transparent runtime costs)
- **Same conversion rules**: Both categories use identical explicit conversion syntax for mixed concrete types

## Block Types and Contexts

### 1. Expression Blocks

**Purpose**: Compute and assign a value to target  
**Context**: Used in expressions where a value is expected  
**Scope**: Isolated (variables don't leak)  
**Assignment Requirements**: Must end with `assign` statement for value production  
**Control Flow**: Support `return` statements for function exits  
**Type Behavior**: Follows compile-time vs runtime distinction (see above)

#### Compile-Time Expression Block Examples
```hexen
// ✅ Compile-time evaluable (can preserve comptime types)
val comptime_result = {
    val temp = 42          // comptime_int
    val computed = temp * 2  // comptime_int * comptime_int → comptime_int
    assign computed        // Block result: comptime_int (preserved!)
}

// ✅ Complex compile-time operations  
val comptime_complex = ({
    val base = 100         // comptime_int
    assign base / 2        // comptime_int / comptime_int → comptime_float
} + {
    val other = 50         // comptime_int
    assign other * 3.14    // comptime_int * comptime_float → comptime_float
}) // comptime_float + comptime_float → comptime_float (preserved!)
```

#### Runtime Expression Block Examples  
```hexen
// ❌ Runtime evaluable (explicit context required)
val runtime_result : i32 = {               // Context REQUIRED!
    val intermediate = compute_value()     // Runtime function call → concrete type (functions always return concrete types)
    assign intermediate * 2                // All operations resolve to i32
}

// ❌ Runtime block with control flow (explicit context required)
val validated_input : i32 = {             // Context REQUIRED!
    val raw_input = get_user_input()      // Runtime function call
    if raw_input < 0 {                    // Runtime condition
        return -1                         // Early function exit - invalid input  
    }
    assign raw_input                      // Valid input assigned (i32)
}
```

**Key Characteristics:**
- **Value Assignment**: Produces value via `assign` statement (assigns to target variable)
- **Control Flow**: Supports `return` statements for function exits (early returns, error handling)
- **Dual Capability**: Can either assign a value OR exit the function
- **Final Statement**: Must end with `assign expression` for value production
- **Type Behavior**: Compile-time blocks preserve comptime types; runtime blocks require explicit context
- **Context Requirements**: Runtime blocks need explicit type annotation on target variable
- **Scope Isolation**: Inner variables not accessible outside block

### 2. Statement Blocks

**Purpose**: Execute code without producing a value  
**Context**: Used as standalone statements  
**Scope**: Isolated (variables don't leak)  
**Return Requirements**: No return required, function returns allowed  
**Type Behavior**: Not applicable (no value production, unaffected by compile-time vs runtime distinction)

```hexen
// Statement block for scoped execution
{
    val temp_config = "setup"
    val processed_data : string = process(temp_config)  // Explicit type required for function result
    save_to_cache(processed_data)
    // No return statement needed
}

// Statement block within function
func setup_environment() : void = {
    // Outer function scope
    val global_config = "production"
    
    {
        // Inner statement block scope
        val local_temp = "temp_data"
        val processed : string = transform(local_temp)  // Explicit type required for function result
        // local_temp not accessible outside this block
    }
    
    // Function returns are allowed in statement blocks
    {
        val should_exit : bool = check_early_exit()  // Explicit type required for function result
        return    // Exits the function, not just the block
    }
    
    finalize_setup(global_config)
}
```

**Key Characteristics:**
- **No Value Production**: Block doesn't produce a value
- **Optional Returns**: Can contain function returns (exits containing function)
- **Scope Isolation**: Variables are scoped to the block
- **Execution Focus**: Designed for side effects and code organization

### 3. Function Body Blocks

**Purpose**: Function implementation with return type validation  
**Context**: Function body (unified with other block types)  
**Scope**: Function scope (managed like all other blocks)  
**Return Requirements**: Context-dependent based on return type  
**Type Behavior**: Function return type provides explicit context for all comptime types

```hexen
// Void function - no return value required
func setup() : void = {
    val config : string = initialize()  // Explicit type required for function result
    apply_settings(config)
    return    // Bare return allowed
}

// Value-returning function - return type validation
func compute() : i32 = {
    val base = 100
    val multiplier = 2
    return base * multiplier    // Must return i32-compatible value
}

// Complex function with nested blocks
func process_data() : string = {
    val input : string = load_data()  // Explicit type required for function result
    
    // Statement block for preprocessing
    {
        val temp : string = validate(input)  // Explicit type required for function result
        normalize(temp)
    }
    
    // Expression block for computation
    val result : string = {
        val processed : string = transform(input)  // Explicit type required for function result
        assign format(processed)  // format() returns string, assigned to block result
    }
    
    return result    // Function return
}
```

**Key Characteristics:**
- **Unified Behavior**: Same as other blocks, with function context
- **Return Type Validation**: Returns must match function signature
- **Scope Management**: Managed identically to other block types
- **Context Integration**: Function context provides return type information

## Dual Capability: `assign` + `return` in Expression Blocks

### Design Rationale: Maximum Expressiveness with Semantic Clarity

Expression blocks support **both** statement types to provide maximum flexibility while maintaining clear semantics:

- **`assign`**: Assigns the computed value to the expression block's target (variable, function parameter, etc.)
- **`return`**: Exits the containing function early (control flow, error handling, optimization)

This dual capability enables natural patterns for validation, error handling, and performance optimization within expression contexts.

### Semantic Consistency: `return` Always Means "Function Exit"

The `return` keyword has **consistent semantics everywhere** in Hexen:
- **Function bodies**: `return value` exits function with value
- **Statement blocks**: `return` exits function (early return)  
- **Expression blocks**: `return value` exits function with value (skips assign)

The `assign` keyword is **expression-block specific**:
- **Expression blocks only**: `assign value` produces the block's value
- **Clear purpose**: Assigns computed value to the expression's target

### Powerful Usage Patterns

#### **1. Validation with Early Returns**
```hexen
func process_user_data() : string = {
    // ❌ Runtime evaluable block (explicit context required)
    val validated_input : string = {           // Context REQUIRED!
        val raw_input = get_user_input()      // Runtime function call
        if raw_input == "" {                  // Runtime condition
            return "ERROR: Empty input"       // Early function exit
        }
        if raw_input.length > 1000 {          // Runtime condition
            return "ERROR: Input too long"    // Early function exit
        }
        assign sanitize(raw_input)            // Success: assign sanitized input (string)
    }
    
    // This code only runs if validation succeeded
    return format_output(validated_input)
}
```

#### **2. Performance Optimization with Caching**
```hexen
func expensive_calculation(key: string) : f64 = {
    // ❌ Runtime evaluable block (explicit context required)
    val result : f64 = {                      // Context REQUIRED!
        val cached_value = lookup_cache(key)  // Runtime function call
        if cached_value != null {             // Runtime condition
            return cached_value               // Early function exit with cached result
        }
        
        val computed = very_expensive_operation(key)  // Runtime function call
        save_to_cache(key, computed)          // Runtime side effect
        assign computed                       // Cache miss: assign computed value (f64)
    }
    
    // This logging only happens for cache misses
    log_cache_miss(key)
    return result
}
```

#### **3. Error Handling with Fallbacks**
```hexen
func load_configuration() : Config = {
    // ❌ Runtime evaluable block (explicit context required)
    val config : Config = {                   // Context REQUIRED!
        val primary_config = try_load_primary_config()  // Runtime function call
        if primary_config != null {           // Runtime condition
            assign primary_config             // Success: use primary config (Config)
        }
        
        val fallback_config = try_load_fallback_config()  // Runtime function call
        if fallback_config != null {          // Runtime condition
            assign fallback_config            // Fallback: use backup config (Config)
        }
        
        return get_default_config()           // Complete failure: function exit with defaults
    }
    
    // This validation only runs if we loaded a config file
    validate_configuration(config)
    return config
}
```

#### **4. Complex Computations with Guards**
```hexen
func safe_divide(numerator: f64, denominator: f64) : f64 = {
    // 🔄 Mixed block (concrete parameters + comptime literal = runtime, explicit context required)
    val result : f64 = {              // Context REQUIRED!
        if denominator == 0.0 {       // Runtime condition (concrete parameter)
            return 0.0                // Early exit: division by zero
        }
        if numerator == 0.0 {          // Runtime condition (concrete parameter)
            assign 0.0                // Optimization: zero numerator (f64)
        } else {
            val division = numerator / denominator  // f64 / f64 → f64 (concrete arithmetic)
            assign division               // Normal case (f64)
        }
    }
    
    return result
}
```

### Benefits of Dual Capability

1. **🎯 Natural Error Handling**: Guards and validation fit naturally within computation contexts
2. **⚡ Performance Optimizations**: Caching and short-circuits work seamlessly  
3. **🧠 Reduced Nesting**: Avoid deeply nested if-else structures
4. **📖 Clear Intent**: `assign` = block value, `return` = function exit
5. **🔄 Consistent Semantics**: `return` means the same thing everywhere
6. **🛡️ Powerful Abstractions**: Complex logic encapsulated within expression contexts

### Mental Model

Think of expression blocks as "smart assignment operators" that can:
- **Compute and assign** a value to their target (`assign`)
- **Bypass assignment** and exit the function directly (`return`)

This provides the expressiveness of full statement capabilities within assignment contexts, while maintaining clear semantic boundaries.

## Block System + Type System Integration

### Unified Design Philosophy

The unified block system works seamlessly with Hexen's comptime type system and binary operations, following the same **"Ergonomic Literals + Transparent Runtime Costs"** philosophy established in [TYPE_SYSTEM.md](TYPE_SYSTEM.md) and [BINARY_OPS.md](BINARY_OPS.md).

### Expression Blocks + Comptime Type Preservation

**Compile-time evaluable** expression blocks preserve comptime types, enabling maximum flexibility until context forces resolution:

```hexen
// ✨ Expression block preserves comptime flexibility (TYPE_SYSTEM.md pattern)
val flexible_computation = {
    val base = 42              // comptime_int
    val multiplier = 100       // comptime_int  
    val result = base * multiplier  // comptime_int * comptime_int → comptime_int (BINARY_OPS.md)
    assign result              // Block assigns: comptime_int (preserved!)
}

// ✅ Same block result adapts to different contexts (TYPE_SYSTEM.md flexibility)
val as_i32 : i32 = flexible_computation    // comptime_int → i32 (context-driven)
val as_i64 : i64 = flexible_computation    // SAME source → i64 (different context!)
val as_f64 : f64 = flexible_computation    // SAME source → f64 (maximum flexibility!)
```

### Division Operators in Expression Blocks

Expression blocks work naturally with both division operators from [BINARY_OPS.md](BINARY_OPS.md):

```hexen
// Float division in expression blocks
val precise_calc = {
    val numerator = 22         // comptime_int
    val denominator = 7        // comptime_int
    assign numerator / denominator  // comptime_int / comptime_int → comptime_float (BINARY_OPS.md)
}

// Integer division in expression blocks  
val efficient_calc = {
    val total = 100            // comptime_int
    val parts = 3              // comptime_int
    assign total \ parts       // comptime_int \ comptime_int → comptime_int (BINARY_OPS.md)
}

// Same expressions, different target types
val precise_f32 : f32 = precise_calc      // comptime_float → f32
val precise_f64 : f64 = precise_calc      // comptime_float → f64
val efficient_i32 : i32 = efficient_calc  // comptime_int → i32
val efficient_i64 : i64 = efficient_calc  // comptime_int → i64
```

### Mixed Type Operations in Blocks

When blocks contain mixed concrete types, they follow [TYPE_SYSTEM.md](TYPE_SYSTEM.md) explicit conversion rules:

```hexen
func demonstrate_mixed_types() : void = {
    val int_val : i32 = 10
    val float_val : f64 = 3.14
    
    // 🔄 Mixed block (concrete types = runtime, explicit context required)
    val mixed_result : f64 = {
        val converted : f64 = int_val:f64 + float_val  // Explicit conversion required
        val scaled = converted * 2.5                   // f64 * comptime_float → f64
        assign scaled                                   // Block assigns concrete f64, explicit type required
    }
    
    // Statement block for scoped conversions
    {
        val temp_result : f32 = mixed_result:f32       // Explicit precision loss (TYPE_SYSTEM.md)
        save_result(temp_result)
        // temp_result not accessible outside block
    }
}
```

### Variable Declaration Context in Blocks

Blocks integrate with [TYPE_SYSTEM.md](TYPE_SYSTEM.md) variable declaration rules:

```hexen
func demonstrate_variable_context() : void = {
    // ✅ Compile-time evaluable block (preserves comptime flexibility)
    val flexible_math = {
        val step1 = 42 + 100      // comptime_int + comptime_int → comptime_int
        val step2 = step1 * 3.14  // comptime_int * comptime_float → comptime_float
        assign step2              // Preserves comptime_float flexibility
    }
    
    // Statement block with mut (requires explicit type)
    {
        mut accumulator : f64 = 0.0           // Explicit type required (TYPE_SYSTEM.md)
        accumulator = flexible_math           // comptime_float → f64 (adapts to mut type)
        accumulator = accumulator + 1.5       // f64 + comptime_float → f64
        process_accumulator(accumulator)
        // accumulator scoped to this block
    }
}
```

### Function Integration Pattern

Expression blocks work seamlessly with function calls, following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) parameter context rules:

```hexen
func process_data(input: f64) : f64 = {
    return input * 2.0
}

func demonstrate_function_integration() : void = {
    // ✅ Compile-time evaluable block result used as function argument
    val computation = {
        val base = 42             // comptime_int
        val adjusted = base / 3   // comptime_int / comptime_int → comptime_float
        assign adjusted
    }
    
    // Function parameter provides context (TYPE_SYSTEM.md pattern)
    val result : f64 = process_data(computation)  // Function returns concrete f64, explicit type required
    
    // ✅ Compile-time evaluable block in nested pattern
    val complex_result : f64 = process_data({
        val temp = 100 + 50      // comptime_int + comptime_int → comptime_int
        assign temp * 3.14       // comptime_int * comptime_float → comptime_float
    })  // Expression block → comptime_float → f64 (parameter context), function returns concrete f64
}
```

### Critical Insight: `mut` Variables Cannot Preserve Block Comptime Types

Following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) safety rules, `mut` variables cannot preserve comptime types from expression blocks:

```hexen
// ✅ val with compile-time evaluable block preserves comptime types (maximum flexibility)
val flexible_block = {
    val calc = 42 + 100 * 3    // All comptime operations
    assign calc / 2            // comptime_int / comptime_int → comptime_float
}
val as_f32 : f32 = flexible_block  // comptime_float → f32 (preserved until now!)
val as_f64 : f64 = flexible_block  // SAME source → f64 (different context!)

// 🔴 mut with compile-time evaluable block cannot preserve comptime types (safety over flexibility)
mut concrete_result : f64 = {
    val calc = 42 + 100 * 3    // Same comptime operations
    assign calc / 2            // comptime_float → f64 (immediately resolved!)
}
// No flexibility preserved - concrete_result is concrete f64

// Explicit conversions required for mut results (TYPE_SYSTEM.md pattern)
mut narrow_result : f32 = concrete_result:f32  // f64 → f32 (explicit conversion)
```

### Design Consistency Benefits

This integration demonstrates Hexen's unified design philosophy:

1. **Same Conversion Rules**: Blocks follow identical TYPE_SYSTEM.md conversion patterns
2. **Consistent Flexibility**: Compile-time evaluable expression blocks preserve comptime types like `val` declarations
3. **Explicit Costs**: Mixed concrete types require visible conversions everywhere
4. **Context Propagation**: Parameter types provide context through block boundaries
5. **Predictable Behavior**: Same simple patterns work across all language features

## Scope Management

### Universal Scope Rules

ALL blocks in Hexen follow identical scope management rules:

1. **Scope Creation**: Every block creates a new scope upon entry
2. **Scope Isolation**: Variables declared in block are not accessible outside
3. **Lexical Scoping**: Inner blocks can access outer scope variables
4. **Scope Cleanup**: Scope is destroyed when block exits
5. **Shadowing Allowed**: Inner blocks can shadow outer variables

```hexen
val outer = "global"

func demonstrate_scoping() : void = {
    val function_scope = "function"
    
    {
        // Statement block scope
        val block_scope = "block"
        val outer = "shadowed"    // Shadows outer 'outer'
        
        // Can access: block_scope, outer (shadowed), function_scope
        println(outer)            // "shadowed"
        println(function_scope)   // "function"
    }
    
    // Can access: function_scope, outer (original)
    // Cannot access: block_scope (out of scope)
    println(outer)              // "global"
}
```

### Summary of Scope Rules

The unified block system provides consistent scope behavior:

**Key Benefits:**
- **Consistent Mental Model**: Same scoping rules everywhere
- **Predictable Behavior**: No special cases to remember  
- **Clean Design**: Unified approach eliminates complexity

## Context-Dependent Behavior

### Block Behavior Summary

| Context | Scope Management | Assignment Requirements | Value Production | Function Returns |
|---------|------------------|------------------------|------------------|------------------|
| **Expression** | ✅ Isolated | ✅ Required (`assign`) | ✅ Yes | ✅ Allowed (`return`) |
| **Statement** | ✅ Isolated | ❌ None | ❌ No | ✅ Allowed (`return`) |
| **Function** | ✅ Isolated | 🔄 Type-dependent | 🔄 Type-dependent | ✅ Expected (`return`) |

### Statement Examples by Context

Hexen's unified block system provides two distinct statement types for different purposes:

#### **Expression Blocks: `assign` and `return`**
```hexen
// Normal case: assign value to target
val computation = {
    val base = 42
    val multiplied = base * 2
    assign multiplied    // ✅ Assigns multiplied to computation
}

// Control flow case: early function exit  
val validated_data : ProcessedData = {    // Context REQUIRED for runtime block!
    val raw_data = get_input()           // Runtime function call
    if raw_data == null {                // Runtime condition
        return null                      // ✅ Exits function early with null
    }
    if !validate(raw_data) {             // Runtime condition
        return null                      // ✅ Exits function early with null  
    }
    assign process(raw_data)             // ✅ Success path assigns processed data
}
```

#### **Statement Blocks: `return` only**
```hexen
// Statement block context  
{
    val temp = 42
    val should_exit : bool = check_condition()  // Explicit type required for function result
    if should_exit {
        return    // ✅ Function return (exits containing function)
    }
    // No assign statement - statement blocks don't produce values
}
```

#### **Function Blocks: `return` for completion**
```hexen
// Function context (void)
func work() : void = {
    val setup : string = initialize()  // Explicit type required for function result
    return    // ✅ Bare return in void function
}

// Function context (value-returning)
func calculate() : i32 = {
    val result = 42
    return result    // ✅ Must return i32-compatible value
}
```

## Advanced Usage Patterns

### Nested Block Compositions with Type System Integration

```hexen
func complex_computation() : f64 = {
    // ✅ Compile-time evaluable block preserving comptime flexibility (TYPE_SYSTEM.md pattern)
    val base_computation = {
        val raw_data = 42           // comptime_int
        val scale_factor = 2.5      // comptime_float
        val result = raw_data * scale_factor  // comptime_int * comptime_float → comptime_float (BINARY_OPS.md)
        assign result               // Preserves comptime_float flexibility
    }
    
    // Statement block for scoped concrete operations
    {
        val concrete_base : f64 = base_computation  // comptime_float → f64 (explicit context)
        val log_message : string = format_value(concrete_base)  // Explicit type required for function result
        write_log(log_message)
        // concrete_base and log_message scoped to this block
    }
    
    // 🔄 Mixed block (comptime + runtime = runtime, explicit context required)
    val final_computation : f64 = {
        val multiplier : f64 = get_multiplier()     // Explicit type required for function result
        val bias = 1.05                             // comptime_float
        val mixed : f64 = base_computation:f64 * multiplier + bias  // Explicit conversion needed for mixed types
        assign mixed                                // Block assigns concrete f64, explicit type required
    }
    
    return final_computation
}
```

### Function-Based Block Usage with Type System Integration

```hexen
// Expression blocks in functions showing different calculation approaches
func get_performance_calculation() : f64 = {
    // ✅ Compile-time evaluable block with comptime operations → f64 return type
    val base = 100             // comptime_int
    val factor = 1.5           // comptime_float
    return base * factor       // comptime_int * comptime_float → comptime_float → f64 (function return context)
}

func get_conservative_calculation() : f64 = {
    // ✅ Compile-time evaluable block with different operations → f64 return type
    val conservative = 42      // comptime_int
    val adjustment = 2         // comptime_int
    return conservative / adjustment  // comptime_int / comptime_int → comptime_float → f64 (function return context)
}

// Function call results are concrete (TYPE_SYSTEM.md rule)
val calculation_result : f64 = get_performance_calculation()  // Function returns concrete f64

// ✅ Compile-time evaluable block with comptime operations showing flexibility
val flexible_calc = {
    val base = 50              // comptime_int
    val multiplier = 2.25      // comptime_float
    assign base * multiplier   // comptime_int * comptime_float → comptime_float (preserved!)
}

// Same comptime result adapts to different contexts (TYPE_SYSTEM.md flexibility)
val as_precise : f64 = flexible_calc    // comptime_float → f64
val as_single : f32 = flexible_calc     // comptime_float → f32

// Statement blocks for scoped operations with explicit type conversions
func cleanup_operation() : void = {
    // Statement block with explicit type conversions when needed
    {
        val threshold : f32 = flexible_calc:f32  // Explicit conversion (TYPE_SYSTEM.md)
        val cleanup_result : string = cleanup_files_above_threshold(threshold)  // Explicit type required for function result
        log_cleanup_result(cleanup_result)
        clear_cache()
        // threshold and cleanup_result scoped to this block
    }
}

// Function with mixed types requiring explicit conversions
func get_complex_calculation() : f64 = {
    // 🔄 Mixed block (concrete runtime value + comptime = runtime, explicit context required)
    val runtime_val : i64 = get_runtime_value()  // Concrete type from function
    val comptime_multiplier = 3.14                // comptime_float
    val result : f64 = runtime_val:f64 * comptime_multiplier  // Explicit conversion (TYPE_SYSTEM.md)
    return result
}

func get_fallback_calculation() : f64 = {
    // ✅ Compile-time evaluable block (fallback calculation)
    val default_calc = 42 * 2.5  // comptime_int * comptime_float → comptime_float
    return default_calc          // comptime_float → f64 (function return context)
}
```

## Benefits and Trade-offs

### Benefits

1. **Cognitive Simplicity**: One syntax to learn, context provides behavior
2. **Consistent Scoping**: Same rules everywhere, no special cases
3. **Composability**: Blocks can be nested and combined naturally
4. **Design Elegance**: Unified syntax eliminates syntactic complexity
5. **Type System Integration**: Compile-time evaluable blocks preserve comptime types; runtime blocks require explicit context, following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) patterns
6. **Extensible Design**: Pattern can accommodate new language constructs

### Trade-offs

1. **Context Dependency**: Behavior depends on usage context
2. **Learning Curve**: Must understand context implications and different block behaviors

### Comparison with Other Languages

| Language | Block Types | Scope Rules | Context Dependency |
|----------|-------------|-------------|--------------------|
| **Hexen** | Unified `{}` | Consistent | Context-driven |
| **Rust** | Multiple syntaxes | Varied | Syntax-specific |
| **C/Java** | Statement blocks only | Consistent | Limited |
| **JavaScript** | Multiple patterns | Inconsistent | Syntax-specific |

## Error Handling

### Context-Specific Error Messages

```hexen
// Expression block without assign
val invalid = {
    val temp = 42
    // Error: "Expression block must end with an assign statement"
}

// Expression block with return but no assign (function exit)
val computation : i32 = {          // Context REQUIRED for runtime blocks!
    val input = get_input()       // Runtime function call
    if input < 0 {                // Runtime condition
        return -1                 // ✅ Valid: function exit with error value
    }
    // Error: "Expression block must end with assign statement or return from function"
    // Missing: assign input or another return statement
}

// Runtime vs compile-time context confusion
val mixed_context_error = {
    val temp = 42             // comptime_int
    val runtime_val = get_value()  // Runtime function call
    assign temp + runtime_val // Error: "Runtime block requires explicit type context"
}  // Should be: val mixed_context_error : i32 = { ... }

// Void function with return value
func work() : void = {
    return 42    // Error: "Void function cannot return a value"
}

// assign outside expression block
{
    val temp = 42
    assign temp      // Error: "assign statement only valid in expression blocks"
}
```

### Scope-Related Errors

```hexen
{
    val scoped = "local"
}
val access = scoped    // Error: "Undefined variable: 'scoped'"

// Redeclaration in same scope
{
    val name = "first"
    val name = "second"    // Error: "Variable 'name' already declared in this scope"
}
```

## Usage Guidelines

### For Hexen Developers

1. **Mental Model**: Think "block = scope + context-specific behavior"
2. **Scope Awareness**: Variables are always scoped to their containing block  
3. **Context Clarity**: Understand how block usage determines behavior
4. **Type System Consistency**: Compile-time evaluable blocks preserve comptime types; runtime blocks require explicit context, following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) patterns
5. **Composition**: Combine blocks naturally for complex logic

## Conclusion

The Unified Block System represents a fundamental design breakthrough in Hexen: taking the complexity of different execution contexts and providing a single, elegant syntax that adapts naturally to its usage while maintaining precise semantic control. The introduction of the `assign` keyword alongside `return` creates a system that is both **"pedantic to write"** (explicit about intent) and **"really easy to read"** (semantically clear).

### The `assign` + `return` Innovation

The dual capability system solves a critical cognitive load problem:

**Before**: `return` had context-dependent meanings (block value vs function exit)
**After**: `assign` = block value, `return` = function exit (consistent semantics everywhere)

This creates **maximum expressiveness** within expression contexts while maintaining **crystal-clear intent** - developers can use expression blocks for complex validation, error handling, and optimization patterns while never being confused about what each statement accomplishes.

### Seamless Integration with Core Type System

The enhanced unified block system works in perfect harmony with Hexen's type system features:

- **Comptime Type Preservation**: Compile-time evaluable expression blocks with `assign` preserve comptime types following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) flexibility patterns
- **Explicit Conversion Requirements**: Mixed concrete types in blocks require the same explicit conversion syntax established in the type system  
- **Variable Declaration Consistency**: The same `val`/`mut` rules apply within blocks, maintaining consistent behavior
- **Binary Operations Integration**: Division operators and arithmetic work identically inside blocks as specified in [BINARY_OPS.md](BINARY_OPS.md)
- **Control Flow Integration**: `return` statements work consistently across all block types for function exits

### Design Philosophy Coherence

The `assign` + `return` enhancement demonstrates Hexen's design philosophy in action:

1. **🎯 Ergonomic**: "Pedantic to write, but really easy to read"
   - `assign` makes value production explicit and pedantic
   - `return` makes function exits clear and readable
   - Dual capability provides expressiveness without ambiguity

2. **🧹 Clean**: "There is only one way to do a thing"  
   - `assign` = block value production (only way)
   - `return` = function exit (only way, consistent everywhere)
   - No semantic overloading or context confusion

3. **🧠 Logic**: "No tricks to remember, only natural approaches"
   - `assign` naturally maps to assignment semantics
   - `return` has consistent meaning across all contexts
   - Usage patterns emerge naturally from semantic clarity

4. **⚡ Pragmatic**: "Focus on what works better"
   - Enables powerful patterns (validation, caching, error handling)
   - Reduces cognitive load through semantic consistency
   - Eliminates artificial limitations in expression contexts

### Architectural Excellence

This system demonstrates how unified design principles create both elegance and power:

1. **"One Syntax, Dual Semantics"** (blocks) + **"Ergonomic Literals + Transparent Costs"** (types) = **Expressive, Predictable Language**
2. **Semantic Consistency**: `return` means the same thing everywhere, `assign` has clear purpose
3. **Composable Design**: Expression blocks with dual capability integrate seamlessly with all language features
4. **Cognitive Clarity**: No overloaded keywords, no context-dependent meanings

### Extensible Foundation for Language Evolution

The enhanced unified block system is not just a syntactic improvement - it's a fundamental architectural decision that demonstrates how thoughtful language design can:

- **Solve Real Problems**: Eliminates cognitive load while adding expressiveness
- **Maintain Consistency**: Same semantic rules across all language features  
- **Enable Innovation**: Dual capability opens new patterns without complexity
- **Guide Development**: Clear principles inform future language evolution

This system serves as a concrete example of how consistent design principles can create both **design elegance** and **developer ergonomics** - proving that languages can be both powerful and simple when guided by clear philosophy rather than accumulated complexity. 