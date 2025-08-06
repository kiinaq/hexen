# Hexen Conditional System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's conditional system design, showcasing how unified block system principles apply to conditionals, creating both conditional statements and conditional expressions with consistent, context-driven behavior.

## Overview

Hexen's **Conditional System** applies the same **"One Syntax, Context-Driven Behavior"** philosophy as the unified block system. Conditionals use consistent `if`/`else if`/`else` syntax with `{}` blocks, but their behavior adapts based on context:

- **Conditional Statements**: Execute code conditionally, no value production
- **Conditional Expressions**: Produce values conditionally using `assign`, support `return` for early function exits
- **Unified Syntax**: Same `if {} else {}` pattern everywhere
- **Runtime Evaluation**: All conditionals treated as runtime (simplified cognitive model)

## Core Philosophy

### Design Principle: "Unified Conditional Syntax, Context-Driven Behavior"

All Hexen conditionals use the same syntax `if condition { }`, but context determines their specific behavior:

- **Statement Context**: Execute code branches, no value production required
- **Expression Context**: Must produce values via `assign`, support function `return` for control flow
- **Consistent Scoping**: All conditional blocks follow unified block scoping rules
- **Runtime Treatment**: All conditionals treated as runtime evaluation (no special compile-time cases)

This unification eliminates cognitive overhead while maintaining precise semantic control through context.

### Philosophy Alignment

The conditional system embodies Hexen's core principles:
- **"Clean: There is only one way to do a thing"** - Single conditional syntax for all contexts
- **"Logic: No tricks to remember, only natural approaches"** - Context determines behavior naturally
- **"Pedantic to write, but really easy to read"** - Explicit value production with `assign`
- **"Ergonomic Literals + Transparent Costs"** - Same type system rules apply in all branches

## Runtime Treatment Philosophy

### Simplified Cognitive Model: "All Conditionals Are Runtime"

To reduce cognitive load, **all conditionals in Hexen are treated as runtime evaluation**, even when checking compile-time constants:

```hexen
// All treated as runtime - no special cases to remember
if true {          // Runtime condition (even though constant)
    process_data()
}

val condition = 42 > 10    // comptime_int > comptime_int → bool (but...)
if condition {             // Runtime condition evaluation
    do_something()
}
```

**Rationale:**
1. **Cognitive Simplicity**: No need to distinguish compile-time vs runtime conditionals
2. **Consistent Behavior**: Same evaluation model everywhere
3. **Future-Proof**: Compiler optimizations can handle constant folding transparently
4. **Integration**: Matches unified block system's runtime distinction for mixed contexts

**Consequence:** Any expression block containing conditionals becomes **runtime evaluable** and requires explicit type context.

## Conditional Types and Contexts

### 1. Conditional Statements

**Purpose**: Execute code conditionally without producing values  
**Context**: Used as standalone statements  
**Scope**: Each branch creates isolated scope  
**Value Production**: None - focused on side effects  
**Branch Requirements**: No requirements - branches can be empty or incomplete

```hexen
// Basic conditional statement
if user_input > 0 {
    val positive_msg = "Positive number"
    log_message(positive_msg)
}

// Complete if-else statement
if balance > 0 {
    enable_premium_features()
} else {
    show_upgrade_prompt()
}

// Else-if chain
if score >= 90 {
    assign_grade("A")
} else if score >= 80 {
    assign_grade("B") 
} else if score >= 70 {
    assign_grade("C")
} else {
    assign_grade("F")
}

// Statement conditional with early function return
func validate_input(input: string) : bool = {
    if input == "" {
        log_error("Empty input")
        return false    // Early function exit
    }
    
    if input.length > 1000 {
        log_error("Input too long")
        return false    // Early function exit
    }
    
    return true
}
```

**Key Characteristics:**
- **No Value Production**: Conditional doesn't produce a value
- **Optional Branches**: `else` and `else if` branches are optional
- **Side Effect Focus**: Designed for actions and state changes
- **Function Returns**: Can contain `return` statements (exits containing function)
- **Scope Isolation**: Each branch has its own scope

### 2. Conditional Expressions

**Purpose**: Produce values conditionally using `assign`  
**Context**: Used in expression contexts (variable assignments, function arguments, etc.)  
**Scope**: Each branch creates isolated scope  
**Value Production**: Required via `assign` statements  
**Branch Requirements**: All paths must either `assign` a value or `return` from function

```hexen
// Basic conditional expression
val result = if user_input > 0 {
    assign user_input * 2
} else {
    assign 0
}

// Conditional expression with early function return
func process_data(input: i32) : i32 = {
    val processed = if input < 0 {
        return -1          // Early function exit with error
    } else if input == 0 {
        assign 1           // Special case
    } else {
        assign input * 2   // Normal processing
    }
    
    return processed
}

// Complex conditional expression with validation
val validated_result : string = {           // Context REQUIRED (runtime block)!
    val user_data = get_user_input()       // Runtime function call
    val result = if user_data.is_valid() { // Runtime condition
        if user_data.length > 100 {        // Nested conditional
            return "ERROR: Too long"       // Early function exit
        } else {
            assign sanitize(user_data)     // Success path
        }
    } else {
        return "ERROR: Invalid data"       // Early function exit  
    }
    assign format_output(result)           // Final processing
}
```

**Key Characteristics:**
- **Value Production**: Must produce value via `assign` statement in each branch
- **Complete Coverage**: All execution paths must either `assign` or `return`
- **Function Returns**: Support `return` statements for early function exits
- **Branch Requirements**: Every branch that doesn't return must assign
- **Type Context**: When used in expression blocks, follows runtime evaluation rules

### 3. Integration with Expression Blocks

Conditional expressions work seamlessly within expression blocks, following the same runtime evaluation rules:

```hexen
// Expression block with conditional (runtime evaluable - explicit context required)
val complex_calculation : f64 = {        // Context REQUIRED!
    val base_value = get_base_value()    // Runtime function call
    val multiplier = if base_value > 100 {
        assign 2.5                       // High value multiplier
    } else if base_value > 50 {
        assign 1.8                       // Medium value multiplier  
    } else {
        return 0.0                       // Early exit for low values
    }
    
    assign base_value:f64 * multiplier   // Final calculation with explicit conversion
}
```

## Syntax Specification

### Basic Syntax Pattern

```hexen
// Conditional statement
if condition {
    // statements
}

// Conditional statement with else
if condition {
    // statements
} else {
    // statements  
}

// Conditional statement with else-if chain
if condition1 {
    // statements
} else if condition2 {
    // statements
} else if condition3 {
    // statements
} else {
    // statements
}
```

### Conditional Expression Syntax

```hexen
// Conditional expression (must assign in all non-returning branches)
val result = if condition {
    assign value1
} else {
    assign value2
}

// Conditional expression with else-if
val result = if condition1 {
    assign value1
} else if condition2 {
    assign value2
} else {
    assign default_value
}

// Conditional expression with early returns
val result = if error_condition {
    return error_value    // Early function exit
} else {
    assign normal_value   // Success path
}
```

### Syntax Rules

1. **No Parentheses**: Conditions are not wrapped in parentheses
2. **Required Braces**: All branches must use `{}` blocks (no single statements)
3. **Boolean Conditions**: Conditions must evaluate to `bool` type
4. **Explicit Comparisons**: No implicit boolean conversion from numeric types

```hexen
// ✅ Correct syntax
if value > 0 {
    do_something()
}

// ✅ Explicit boolean condition
val is_ready : bool = check_status()
if is_ready {
    proceed()
}

// ❌ Incorrect - no parentheses
if (value > 0) {
    do_something()
}

// ❌ Incorrect - no braces
if value > 0
    do_something()

// ❌ Incorrect - implicit boolean conversion  
val count : i32 = 5
if count {        // Error: i32 cannot be used as bool
    do_something()
}

// ✅ Correct - explicit comparison
if count > 0 {    // Explicit: i32 > comptime_int → bool
    do_something()
}
```

## Type System Integration

### Condition Type Requirements

All condition expressions must evaluate to `bool` type:

```hexen
// ✅ Valid boolean conditions
if user_input > 0 { }              // i32 > comptime_int → bool
if name == "admin" { }             // string == string → bool  
if is_valid && is_ready { }        // bool && bool → bool
if !(condition) { }                // !bool → bool

// ❌ Invalid - requires explicit boolean conversion
val count : i32 = 5
// if count { }                    // Error: i32 is not bool
if count != 0 { }                  // ✅ Correct: explicit comparison

val pointer : SomePointer = get_ptr()
// if pointer { }                  // Error: SomePointer is not bool  
if pointer != null { }             // ✅ Correct: explicit null check
```

### Branch Type Resolution

Each branch in conditional expressions must resolve to compatible types:

```hexen
// ✅ Compatible branch types
val result : f64 = if condition {
    assign 42                      // comptime_int → f64
} else {
    assign 3.14                    // comptime_float → f64
}

// ✅ Explicit conversions for mixed concrete types
func get_mixed_result() : f64 = {
    val int_val : i32 = get_int()
    val float_val : f32 = get_float()
    
    val result : f64 = if use_int {
        assign int_val:f64         // Explicit: i32 → f64
    } else {
        assign float_val:f64       // Explicit: f32 → f64  
    }
    
    return result
}

// ❌ Incompatible types without explicit conversion
// val bad_result : f64 = if condition {
//     assign int_val             // Error: i32 cannot auto-convert to f64
// } else {
//     assign float_val           // Error: f32 cannot auto-convert to f64
// }
```

### Integration with Comptime Types

Conditional expressions containing only comptime operations still require explicit context due to runtime treatment:

```hexen
// Conditional treated as runtime (even with comptime values)
val result : f64 = if true {       // Runtime condition (even though constant)
    assign 42                      // comptime_int → f64 (context provided)
} else {
    assign 100                     // comptime_int → f64 (context provided)
}

// Expression block with conditional requires explicit context
val complex_result : i32 = {       // Context REQUIRED!
    val base = 42                  // comptime_int
    val multiplier = if base > 50 {
        assign 2                   // comptime_int
    } else {
        assign 3                   // comptime_int  
    }
    assign base * multiplier       // comptime_int * comptime_int → comptime_int → i32
}
```

## Scope Management

### Branch Scoping Rules

Each conditional branch creates its own isolated scope, following unified block system rules:

```hexen
func demonstrate_conditional_scoping() : void = {
    val outer_var = "function scope"
    
    if condition {
        val branch_var = "if branch"       // Scoped to if branch
        val outer_var = "shadowed"         // Shadows function scope var
        log_message(outer_var)             // "shadowed"
        log_message(branch_var)            // "if branch"
    } else {
        val branch_var = "else branch"     // Different scope, same name OK
        log_message(outer_var)             // "function scope" (original)
        log_message(branch_var)            // "else branch"
    }
    
    // branch_var not accessible here (out of scope)
    log_message(outer_var)                 // "function scope" (original)
}
```

### Nested Conditional Scoping

```hexen
func demonstrate_nested_scoping() : void = {
    val level1 = "outer"
    
    if condition1 {
        val level2 = "first if"
        
        if condition2 {
            val level3 = "nested if"
            // Can access: level3, level2, level1
            log_all(level1, level2, level3)
        } else {
            val level3 = "nested else"     // Different scope, same name OK
            // Can access: level3, level2, level1
            log_all(level1, level2, level3)
        }
        
        // level3 not accessible here
        // Can access: level2, level1
    }
    
    // Only level1 accessible here
}
```

## Advanced Usage Patterns

### 1. Validation Chains with Early Returns

```hexen
func validate_and_process(input: string) : string = {
    val result = if input == "" {
        return "ERROR: Empty input"        // Early function exit
    } else if input.length > 1000 {
        return "ERROR: Input too long"     // Early function exit
    } else if contains_invalid_chars(input) {
        return "ERROR: Invalid characters" // Early function exit
    } else {
        assign sanitize(input)             // Success: processed input
    }
    
    // Additional processing only happens for valid input
    log_success("Input validated successfully")
    return format_output(result)
}
```

### 2. Conditional Processing with Fallbacks

```hexen
func load_config_with_fallback() : Config = {
    val config = if primary_config_exists() {
        val primary = load_primary_config()
        if primary.is_valid() {
            assign primary                 // Use primary config
        } else {
            log_warning("Primary config invalid, trying fallback")
            if fallback_config_exists() {
                assign load_fallback_config()  // Use fallback
            } else {
                return get_default_config()    // Early exit with defaults
            }
        }
    } else {
        log_info("No primary config, using defaults")
        assign get_default_config()       // Use defaults
    }
    
    validate_config(config)
    return config
}
```

### 3. Complex Conditional Expressions in Expression Blocks

```hexen
func calculate_pricing() : f64 = {
    val final_price : f64 = {              // Context REQUIRED (runtime block)!
        val base_price = get_base_price()  // Runtime function call
        val user_tier = get_user_tier()    // Runtime function call
        
        val discount_multiplier = if user_tier == "premium" {
            assign 0.8                     // 20% discount
        } else if user_tier == "gold" {
            assign 0.9                     // 10% discount  
        } else if is_first_time_user() {   // Runtime condition
            assign 0.95                    // 5% new user discount
        } else {
            assign 1.0                     // No discount
        }
        
        val discounted = base_price * discount_multiplier
        
        val final_adjustment = if discounted < 10.0 {
            return 0.0                     // Early exit: too cheap, make it free
        } else if discounted > 1000.0 {
            assign 1000.0                  // Cap at maximum price
        } else {
            assign discounted              // Use calculated price
        }
        
        assign final_adjustment
    }
    
    return final_price
}
```

## Error Handling

### Expression Context Requirements

```hexen
// ❌ Error: Not all paths assign
val incomplete = if condition {
    assign value1
}
// Error: "All branches in conditional expression must assign a value or return from function"

// ✅ Correct: All paths covered
val complete = if condition {
    assign value1
} else {
    assign value2
}

// ✅ Correct: Early return is valid
val with_return = if error_condition {
    return error_value             // Early function exit
} else {
    assign normal_value
}
```

### Condition Type Errors

```hexen
// ❌ Error: Non-boolean condition
val count : i32 = 5
// if count {                     // Error: "Condition must be of type bool, got i32"
//     do_something()
// }

// ✅ Correct: Explicit boolean comparison
if count > 0 {                     // i32 > comptime_int → bool
    do_something()
}

// ❌ Error: String as condition  
val name = "admin"
// if name {                      // Error: "Condition must be of type bool, got string"
//     grant_access()
// }

// ✅ Correct: String comparison
if name == "admin" {               // string == string → bool
    grant_access()
}
```

### Scope-Related Errors

```hexen
if condition {
    val scoped_var = "local"
}
// val access = scoped_var        // Error: "Undefined variable: 'scoped_var'"

// Branch variable conflicts
if condition1 {
    val name = "first"
    val name = "second"            // Error: "Variable 'name' already declared in this scope"
}
```

## Benefits and Design Rationale

### Benefits

1. **Cognitive Simplicity**: One syntax pattern for all conditional usage
2. **Context Clarity**: Clear distinction between statements and expressions  
3. **Type Safety**: Explicit boolean conditions prevent common errors
4. **Consistent Scoping**: Same block scoping rules everywhere
5. **Expressive Power**: Early returns enable complex control flow patterns
6. **Integration**: Seamless integration with unified block system and type system

### Design Rationale

1. **No Parentheses**: Reduces syntactic noise, follows "clean" philosophy
2. **Required Braces**: Prevents dangling else problems, improves readability
3. **Runtime Treatment**: Simplified mental model, no special cases
4. **Explicit Boolean**: Prevents implicit conversions that hide bugs
5. **Unified Behavior**: Same scoping and evaluation rules as block system

## Comparison with Other Languages

| Language | Syntax | Expression Form | Boolean Conversion | Scoping |
|----------|--------|----------------|-------------------|---------|
| **Hexen** | `if cond { }` | Context-driven | Explicit only | Block-scoped |
| **Rust** | `if cond { }` | Expression-first | Explicit only | Block-scoped |
| **C/Java** | `if (cond) { }` | Statement-only | Implicit allowed | Block-scoped |
| **Python** | `if cond:` | Statement-only | Implicit allowed | Function-scoped |
| **JavaScript** | `if (cond) { }` | Ternary operator | Implicit allowed | Block-scoped |

## Future Extensibility

The conditional system provides a foundation for future language features:

1. **Pattern Matching**: Could extend conditional syntax with pattern matching capabilities
2. **Guard Clauses**: Could add guard clause syntax building on conditional expressions
3. **Exhaustiveness Checking**: Could add compile-time verification for enum conditionals
4. **Optimization**: Runtime treatment allows for transparent compiler optimizations

## Usage Guidelines

### For Hexen Developers

1. **Mental Model**: Think "conditional = scoped branches + context-specific behavior"
2. **Boolean Clarity**: Always use explicit boolean comparisons
3. **Expression Coverage**: Ensure all branches in conditional expressions assign or return
4. **Scope Awareness**: Variables are scoped to their containing branch
5. **Type Consistency**: Follow same explicit conversion rules as rest of language

## Conclusion

The Conditional System demonstrates Hexen's unified design philosophy in action: taking a fundamental programming construct and providing consistent, context-driven behavior that integrates seamlessly with the type system and unified block system.

### Key Innovations

1. **Context-Driven Behavior**: Same syntax works as both statements and expressions
2. **Runtime Simplification**: All conditionals treated uniformly (no compile-time special cases)
3. **Type System Integration**: Explicit boolean conditions and type conversions
4. **Block System Harmony**: Same scoping and evaluation rules throughout

### Architectural Coherence

The conditional system reinforces Hexen's core design principles:

- **"One Syntax, Multiple Contexts"**: Conditionals adapt to their usage context
- **"Explicit Over Implicit"**: Boolean conditions and type conversions are always visible  
- **"Consistent Mental Models"**: Same patterns work across all language features
- **"Ergonomic + Transparent"**: Natural syntax with clear cost visibility

This creates a conditional system that is both **powerful and predictable** - enabling complex control flow patterns while maintaining the simplicity and consistency that defines Hexen's approach to language design.