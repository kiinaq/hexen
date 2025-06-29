# Hexen Unified Block System 🦉

*Design Exploration & Specification*

> **Experimental Note**: This document describes our exploration into unified block system design. We're experimenting with context-driven behavior patterns and documenting our journey to share with the community and gather insights. These ideas are part of our learning process in language design.

## Overview

Hexen's **Unified Block System** represents one of the language's most elegant design decisions: using a single `{ }` block syntax for all contexts while providing context-appropriate behavior. This creates a consistent, learnable mental model where blocks behave predictably based on their usage context.

## Core Philosophy

### Design Principle: "One Syntax, Context-Driven Behavior"

All Hexen constructs use the same block syntax `{ statements }`, but context determines their specific behavior:

- **Expression blocks**: Produce values, require final return statement
- **Statement blocks**: Execute code, allow function returns, no value production
- **Function bodies**: Unified with all other blocks, context provides return type validation
- **Scope isolation**: ALL blocks manage their own scope regardless of context

This unification eliminates cognitive overhead while maintaining precise semantic control through context.

### Philosophy Alignment

The unified block system embodies Hexen's core principles:
- **"Clean: There is only one way to do a thing"** - Single block syntax for all contexts
- **"Logic: No tricks to remember, only natural approaches"** - Context determines behavior naturally
- **"Pedantic to write, but really easy to read"** - Explicit context makes intent clear

## Block Types and Contexts

### 1. Expression Blocks

**Purpose**: Compute and return a value  
**Context**: Used in expressions where a value is expected  
**Scope**: Isolated (variables don't leak)  
**Return Requirements**: Must end with `return` statement

```hexen
// Expression block in variable assignment
val result = {
    val temp = 42
    val computed = temp * 2
    return computed        // Required: must return a value
}

// Expression block in function return
func calculate() : i32 = {
    return {
        val intermediate = 10 + 20
        return intermediate * 2    // Nested expression block
    }
}

// Expression block in complex expressions
val complex = ({
    val base = 100
    return base / 2
} + {
    val other = 50
    return other * 3
}) / 4
```

**Key Characteristics:**
- **Value Production**: Always produces a value via return statement
- **Final Return Required**: Last statement must be `return expression`
- **Type Inference**: Block type determined by return expression type
- **Scope Isolation**: Inner variables not accessible outside block

### 2. Statement Blocks

**Purpose**: Execute code without producing a value  
**Context**: Used as standalone statements  
**Scope**: Isolated (variables don't leak)  
**Return Requirements**: No return required, function returns allowed

```hexen
// Statement block for scoped execution
{
    val temp_config = "setup"
    val processed_data = process(temp_config)
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
        val processed = transform(local_temp)
        // local_temp not accessible outside this block
    }
    
    // Function returns are allowed in statement blocks
    {
        val should_exit = check_early_exit()
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

```hexen
// Void function - no return value required
func setup() : void = {
    val config = initialize()
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
    val input = load_data()
    
    // Statement block for preprocessing
    {
        val temp = validate(input)
        normalize(temp)
    }
    
    // Expression block for computation
    val result = {
        val processed = transform(input)
        return format(processed)
    }
    
    return result    // Function return
}
```

**Key Characteristics:**
- **Unified Behavior**: Same as other blocks, with function context
- **Return Type Validation**: Returns must match function signature
- **Scope Management**: Managed identically to other block types
- **Context Integration**: Function context provides return type information

## Block System + Type System Integration

### Unified Design Philosophy

The unified block system works seamlessly with Hexen's comptime type system and binary operations, following the same **"Ergonomic Literals + Transparent Costs"** philosophy established in [TYPE_SYSTEM.md](TYPE_SYSTEM.md) and [BINARY_OPS.md](BINARY_OPS.md).

### Expression Blocks + Comptime Type Preservation

Expression blocks naturally preserve comptime types, enabling maximum flexibility until context forces resolution:

```hexen
// ✨ Expression block preserves comptime flexibility (TYPE_SYSTEM.md pattern)
val flexible_computation = {
    val base = 42              // comptime_int
    val multiplier = 100       // comptime_int  
    val result = base * multiplier  // comptime_int * comptime_int → comptime_int (BINARY_OPS.md)
    return result              // Block result: comptime_int (preserved!)
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
    return numerator / denominator  // comptime_int / comptime_int → comptime_float (BINARY_OPS.md)
}

// Integer division in expression blocks  
val efficient_calc = {
    val total = 100            // comptime_int
    val parts = 3              // comptime_int
    return total \ parts       // comptime_int \ comptime_int → comptime_int (BINARY_OPS.md)
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
    
    // Expression block with explicit conversions (TYPE_SYSTEM.md pattern)
    val mixed_result : f64 = {
        val converted : f64 = int_val:f64 + float_val  // Explicit conversion required
        val scaled = converted * 2.5                   // f64 * comptime_float → f64
        return scaled                                   // Block returns concrete f64, explicit type required
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
    // Expression block with val (preserves comptime flexibility)
    val flexible_math = {
        val step1 = 42 + 100      // comptime_int + comptime_int → comptime_int
        val step2 = step1 * 3.14  // comptime_int * comptime_float → comptime_float
        return step2              // Preserves comptime_float flexibility
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
    // Expression block result used as function argument
    val computation = {
        val base = 42             // comptime_int
        val adjusted = base / 3   // comptime_int / comptime_int → comptime_float
        return adjusted
    }
    
    // Function parameter provides context (TYPE_SYSTEM.md pattern)
    val result = process_data(computation)  // comptime_float → f64 (parameter context)
    
    // Complex nested pattern
    val complex_result : f64 = process_data({
        val temp = 100 + 50      // comptime_int + comptime_int → comptime_int
        return temp * 3.14       // comptime_int * comptime_float → comptime_float
    })  // Expression block → comptime_float → f64 (parameter context), function returns concrete f64
}
```

### Critical Insight: `mut` Variables Cannot Preserve Block Comptime Types

Following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) safety rules, `mut` variables cannot preserve comptime types from expression blocks:

```hexen
// ✅ val preserves expression block comptime types (maximum flexibility)
val flexible_block = {
    val calc = 42 + 100 * 3    // All comptime operations
    return calc / 2            // comptime_int / comptime_int → comptime_float
}
val as_f32 : f32 = flexible_block  // comptime_float → f32 (preserved until now!)
val as_f64 : f64 = flexible_block  // SAME source → f64 (different context!)

// 🔴 mut cannot preserve expression block comptime types (safety over flexibility)
mut concrete_result : f64 = {
    val calc = 42 + 100 * 3    // Same comptime operations
    return calc / 2            // comptime_float → f64 (immediately resolved!)
}
// No flexibility preserved - concrete_result is concrete f64

// Explicit conversions required for mut results (TYPE_SYSTEM.md pattern)
mut narrow_result : f32 = concrete_result:f32  // f64 → f32 (explicit conversion)
```

### Design Consistency Benefits

This integration demonstrates Hexen's unified design philosophy:

1. **Same Conversion Rules**: Blocks follow identical TYPE_SYSTEM.md conversion patterns
2. **Consistent Flexibility**: Expression blocks preserve comptime types like `val` declarations
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

| Context | Scope Management | Return Requirements | Value Production | Function Returns |
|---------|------------------|---------------------|------------------|------------------|
| **Expression** | ✅ Isolated | ✅ Required (final) | ✅ Yes | ❌ Not allowed |
| **Statement** | ✅ Isolated | ❌ Optional | ❌ No | ✅ Allowed |
| **Function** | ✅ Isolated | 🔄 Type-dependent | 🔄 Type-dependent | ✅ Expected |

### Return Statement Examples

Return statements work differently based on block context:

```hexen
// Expression block context
val value = {
    val temp = 42
    return temp    // ✅ Required and valid
}

// Statement block context  
{
    val temp = 42
    val should_exit = check_condition()
    return    // ✅ Function return (exits containing function)
    // No return required for statement blocks in general
}

// Function context (void)
func work() : void = {
    val setup = initialize()
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
    // Expression block preserving comptime flexibility (TYPE_SYSTEM.md pattern)
    val base_computation = {
        val raw_data = 42           // comptime_int
        val scale_factor = 2.5      // comptime_float
        val result = raw_data * scale_factor  // comptime_int * comptime_float → comptime_float (BINARY_OPS.md)
        return result               // Preserves comptime_float flexibility
    }
    
    // Statement block for scoped concrete operations
    {
        val concrete_base : f64 = base_computation  // comptime_float → f64 (explicit context)
        val log_message = format_value(concrete_base)
        write_log(log_message)
        // concrete_base and log_message scoped to this block
    }
    
    // Expression block with mixed comptime and concrete types
    val final_computation : f64 = {
        val multiplier = get_multiplier()           // Returns concrete f64
        val bias = 1.05                             // comptime_float
        val mixed : f64 = base_computation * multiplier + bias  // comptime_float * f64 + comptime_float → explicit f64 needed
        return mixed                                // Block returns concrete f64, explicit type required
    }
    
    return final_computation
}
```

### Function-Based Block Usage with Type System Integration

```hexen
// Expression blocks in functions showing different calculation approaches
func get_performance_calculation() : f64 = {
    // Expression block with comptime operations → f64 return type
    val base = 100             // comptime_int
    val factor = 1.5           // comptime_float
    return base * factor       // comptime_int * comptime_float → comptime_float → f64 (function return context)
}

func get_conservative_calculation() : f64 = {
    // Expression block with different operations → f64 return type
    val conservative = 42      // comptime_int
    val adjustment = 2         // comptime_int
    return conservative / adjustment  // comptime_int / comptime_int → comptime_float → f64 (function return context)
}

// Function call results are concrete (TYPE_SYSTEM.md rule)
val calculation_result : f64 = get_performance_calculation()  // Function returns concrete f64

// Expression blocks with comptime operations showing flexibility
val flexible_calc = {
    val base = 50              // comptime_int
    val multiplier = 2.25      // comptime_float
    return base * multiplier   // comptime_int * comptime_float → comptime_float (preserved!)
}

// Same comptime result adapts to different contexts (TYPE_SYSTEM.md flexibility)
val as_precise : f64 = flexible_calc    // comptime_float → f64
val as_single : f32 = flexible_calc     // comptime_float → f32

// Statement blocks for scoped operations with explicit type conversions
func cleanup_operation() : void = {
    // Statement block with explicit type conversions when needed
    {
        val threshold : f32 = flexible_calc:f32  // Explicit conversion (TYPE_SYSTEM.md)
        val temp_files = get_files_above_threshold(threshold)
        remove_files(temp_files)
        clear_cache()
        // threshold and temp_files scoped to this block
    }
}

// Function with mixed types requiring explicit conversions
func get_complex_calculation() : f64 = {
    // Expression block requiring explicit type management
    val runtime_val : i64 = get_runtime_value()  // Concrete type from function
    val comptime_multiplier = 3.14                // comptime_float
    val result : f64 = runtime_val:f64 * comptime_multiplier  // Explicit conversion (TYPE_SYSTEM.md)
    return result
}

func get_fallback_calculation() : f64 = {
    // Fallback expression block
    val default_calc = 42 * 2.5  // comptime_int * comptime_float → comptime_float
    return default_calc          // comptime_float → f64 (function return context)
}
```

### Block-Based Error Handling (Future)

```hexen
// Future: try-catch blocks using unified block system
val safe_result = try {
    val risky = dangerous_operation()
    return process(risky)
} catch error {
    val fallback = handle_error(error)
    return fallback
}
```

## Benefits and Trade-offs

### Benefits

1. **Cognitive Simplicity**: One syntax to learn, context provides behavior
2. **Consistent Scoping**: Same rules everywhere, no special cases
3. **Composability**: Blocks can be nested and combined naturally
4. **Design Elegance**: Unified syntax eliminates syntactic complexity
5. **Type System Integration**: Seamlessly works with comptime types and explicit conversions (see [TYPE_SYSTEM.md](TYPE_SYSTEM.md))
6. **Future-Proof**: Pattern extends to new language constructs

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
// Expression block without return
val invalid = {
    val temp = 42
    // Error: "Expression block must end with a return statement"
}

// Void function with return value
func work() : void = {
    return 42    // Error: "Void function cannot return a value"
}

// Return outside valid context
return 42        // Error: "Return statement outside valid context"
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

## Future Extensions

### Pattern Matching Blocks

```hexen
// Future: match expressions using unified blocks
val result = match value {
    Pattern1 => {
        val processed = handle_pattern1(value)
        return processed
    }
    Pattern2 => {
        val alternative = handle_pattern2(value)
        return alternative
    }
}
```

### Async Blocks

```hexen
// Future: async blocks using unified syntax
val async_result = async {
    val data = await fetch_data()
    val processed = await process(data)
    return processed
}
```

### Generic Blocks

```hexen
// Future: generic function bodies
func transform<T>(value: T) : T = {
    val processed = apply_transformation(value)
    return processed
}
```

## Usage Guidelines

### For Hexen Developers

1. **Mental Model**: Think "block = scope + context-specific behavior"
2. **Scope Awareness**: Variables are always scoped to their containing block  
3. **Context Clarity**: Understand how block usage determines behavior
4. **Type System Consistency**: Blocks follow the same comptime type and conversion rules as other language features (see [TYPE_SYSTEM.md](TYPE_SYSTEM.md))
5. **Composition**: Combine blocks naturally for complex logic

## Conclusion

The Unified Block System represents a fundamental design exploration in Hexen: taking the complexity of different execution contexts and providing a single, elegant syntax that adapts naturally to its usage. This system embodies the language's core philosophy of being "pedantic to write, but really easy to read" - developers must be explicit about context, but the resulting code is immediately understandable.

### Seamless Integration with Core Type System

The unified block system works in perfect harmony with Hexen's type system features:

- **Comptime Type Preservation**: Expression blocks naturally preserve comptime types following [TYPE_SYSTEM.md](TYPE_SYSTEM.md) flexibility patterns
- **Explicit Conversion Requirements**: Mixed concrete types in blocks require the same explicit conversion syntax established in the type system
- **Variable Declaration Consistency**: The same `val`/`mut` rules apply within blocks, maintaining consistent behavior
- **Binary Operations Integration**: Division operators and arithmetic work identically inside blocks as specified in [BINARY_OPS.md](BINARY_OPS.md)

### Design Philosophy Coherence

By unifying scope management across all contexts while allowing context-specific behaviors, Hexen achieves both design elegance and developer ergonomics. The system demonstrates how experimental language features can work together cohesively:

1. **"One Syntax, Context-Driven Behavior"** (blocks) + **"Ergonomic Literals + Transparent Costs"** (types) = **Consistent, Predictable Language**
2. **Same Rules Everywhere**: No special cases or exceptions between different language features
3. **Composable Design**: Blocks, types, and operations combine naturally without syntactic friction

### Extensible Foundation

The unified block system is not just a syntactic convenience - it's a fundamental architectural decision that influences how developers think about code organization, scope management, and expression composition in Hexen. This foundation integrates seamlessly with the type system and provides a solid base for future language features.

As we continue exploring these design patterns, the unified block system serves as a concrete example of how consistent design principles can create both design elegance and developer ergonomics - a key goal in our language design journey. 