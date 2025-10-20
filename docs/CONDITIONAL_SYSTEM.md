# Hexen Conditional System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's conditional system design, showcasing how unified block system principles apply to conditionals, creating both conditional statements and conditional expressions with consistent, context-driven behavior.

## Overview

Hexen's **Conditional System** applies the same **"One Syntax, Context-Driven Behavior"** philosophy as the unified block system. Conditionals use consistent `if`/`else if`/`else` syntax with `{}` blocks, but their behavior adapts based on context:

- **Conditional Statements**: Execute code conditionally, no value production
- **Conditional Expressions**: Produce values conditionally using `->`, support `return` for early function exits
- **Unified Syntax**: Same `if {} else {}` pattern everywhere
- **Runtime Evaluation**: All conditionals treated as runtime (simplified cognitive model)

## Core Philosophy

### Design Principle: "Unified Conditional Syntax, Context-Driven Behavior"

All Hexen conditionals use the same syntax `if condition { }`, but context determines their specific behavior:

- **Statement Context**: Execute code branches, no value production required
- **Expression Context**: Must produce values via `->`, support function `return` for control flow
- **Consistent Scoping**: All conditional blocks follow unified block scoping rules
- **Runtime Treatment**: All conditionals treated as runtime evaluation (no special compile-time cases)

This unification eliminates cognitive overhead while maintaining precise semantic control through context.

### Philosophy Alignment

The conditional system embodies Hexen's core principles:
- **"Clean: There is only one way to do a thing"** - Single conditional syntax for all contexts
- **"Logic: No tricks to remember, only natural approaches"** - Context determines behavior naturally
- **"Pedantic to write, but really easy to read"** - Explicit value production with `->`
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

**Purpose**: Produce values conditionally using `->`  
**Context**: Used in expression contexts (variable assignments, function arguments, etc.)  
**Scope**: Each branch creates isolated scope  
**Value Production**: Required via `->` statements  
**Branch Requirements**: All paths must either `->` a value or `return` from function

```hexen
// Basic conditional expression (type annotation REQUIRED - runtime operation!)
val result : i32 = if user_input > 0 {
    -> user_input * 2
} else {
    -> 0
}

// Conditional expression with early function return
func process_data(input: i32) : i32 = {
    val processed : i32 = if input < 0 {  // Type REQUIRED (conditional = runtime)
        return -1          // Early function exit with error
    } else if input == 0 {
        -> 1           // Special case
    } else {
        -> input * 2   // Normal processing
    }

    return processed
}

// Complex conditional expression with validation
val validated_result : string = {           // Context REQUIRED (runtime block)!
    val user_data : string = get_user_input()       // Type REQUIRED (function call)
    val result : string = if user_data.is_valid() { // Type REQUIRED (conditional = runtime)
        if user_data.length > 100 {        // Nested conditional
            return "ERROR: Too long"       // Early function exit
        } else {
            -> sanitize(user_data)     // Success path
        }
    } else {
        return "ERROR: Invalid data"       // Early function exit
    }
    -> format_output(result)           // Final processing
}
```

**Key Characteristics:**
- **Type Annotation Required**: Conditional expressions are **runtime operations** and ALWAYS require explicit type annotations (like function calls)
- **Value Production**: Must produce value via `->` statement in each branch
- **Complete Coverage**: All execution paths must either `->` or `return`
- **Function Returns**: Support `return` statements for early function exits
- **Branch Requirements**: Every branch that doesn't return must ->
- **No Comptime Preservation**: Conditionals produce concrete types, never comptime types (runtime barrier)

### 3. Integration with Expression Blocks

Conditional expressions work seamlessly within expression blocks, following the same runtime evaluation rules:

```hexen
// Expression block with conditional (runtime evaluable - explicit context required)
val complex_calculation : f64 = {        // Context REQUIRED!
    val base_value : f64 = get_base_value()    // Type REQUIRED (function call)
    val multiplier : f64 = if base_value > 100 {  // Type REQUIRED (conditional = runtime)
        -> 2.5                       // High value multiplier
    } else if base_value > 50 {
        -> 1.8                       // Medium value multiplier
    } else {
        return 0.0                       // Early exit for low values
    }

    -> base_value * multiplier       // Final calculation (both f64)
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
// Conditional expression (type annotation REQUIRED - runtime operation!)
val result : i32 = if condition {
    -> value1
} else {
    -> value2
}

// Conditional expression with else-if
val result : i32 = if condition1 {
    -> value1
} else if condition2 {
    -> value2
} else {
    -> default_value
}

// Conditional expression with early returns
val result : i32 = if error_condition {
    return error_value    // Early function exit
} else {
    -> normal_value   // Success path
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
    -> 42                      // comptime_int → f64
} else {
    -> 3.14                    // comptime_float → f64
}

// ✅ Explicit conversions for mixed concrete types
func get_mixed_result() : f64 = {
    val int_val : i32 = get_int()
    val float_val : f32 = get_float()
    
    val result : f64 = if use_int {
        -> int_val:f64         // Explicit: i32 → f64
    } else {
        -> float_val:f64       // Explicit: f32 → f64  
    }
    
    return result
}

// ❌ Incompatible types without explicit conversion
// val bad_result : f64 = if condition {
//     -> int_val             // Error: i32 cannot auto-convert to f64
// } else {
//     -> float_val           // Error: f32 cannot auto-convert to f64
// }
```

### Integration with Comptime Types

**Critical Rule:** Since conditionals are **runtime operations**, conditional expressions **always produce concrete types** and **always require explicit type context** - even when all branches contain comptime values.

**Think of conditionals like function calls:** A function computing `42 + 100` internally still returns a concrete type, not comptime. Conditional expressions work the same way.

```hexen
// ✅ Conditional expression ALWAYS requires explicit type (runtime operation)
val result : f64 = if true {       // Runtime conditional (even with constant condition)
    -> 42                          // comptime_int adapts to f64 via context
} else {
    -> 100                         // comptime_int adapts to f64 via context
}
// Result is f64 (concrete), NOT comptime_float!

// ❌ This is INVALID - no implicit comptime preservation
// val bad_result = if true {
//     -> 42                       // Error: conditional is runtime, needs explicit type
// } else {
//     -> 100
// }

// ✅ Expression block with conditional (nested type requirements)
val complex_result : i32 = {       // Context REQUIRED (runtime block)!
    val base = 42                  // comptime_int (literal)
    val multiplier : i32 = if base > 50 {  // Type REQUIRED (conditional = runtime)!
        -> 2                       // comptime_int adapts to i32 via context
    } else {
        -> 3                       // comptime_int adapts to i32 via context
    }
    // multiplier is i32 (concrete), NOT comptime_int!
    -> base * multiplier           // comptime_int * i32 → i32 (via outer context)
}
```

**Key Insight:** Runtime operations form a "barrier" - comptime types can flow *into* them (via adaptation), but concrete types flow *out* of them. This maintains Hexen's core principle: runtime costs are always explicit and visible.

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
    val result : string = if input == "" {  // Type REQUIRED (conditional = runtime)
        return "ERROR: Empty input"        // Early function exit
    } else if input.length > 1000 {
        return "ERROR: Input too long"     // Early function exit
    } else if contains_invalid_chars(input) {
        return "ERROR: Invalid characters" // Early function exit
    } else {
        -> sanitize(input)             // Success: processed input
    }

    // Additional processing only happens for valid input
    log_success("Input validated successfully")
    return format_output(result)
}
```

### 2. Conditional Processing with Fallbacks

```hexen
func load_config_with_fallback() : Config = {
    val config : Config = if primary_config_exists() {  // Type REQUIRED (conditional = runtime)
        val primary : Config = load_primary_config()
        if primary.is_valid() {
            -> primary                 // Use primary config
        } else {
            log_warning("Primary config invalid, trying fallback")
            if fallback_config_exists() {
                -> load_fallback_config()  // Use fallback
            } else {
                return get_default_config()    // Early exit with defaults
            }
        }
    } else {
        log_info("No primary config, using defaults")
        -> get_default_config()       // Use defaults
    }

    validate_config(config)
    return config
}
```

### 3. Complex Conditional Expressions in Expression Blocks

```hexen
func calculate_pricing() : f64 = {
    val final_price : f64 = {              // Context REQUIRED (runtime block)!
        val base_price : f64 = get_base_price()  // Type REQUIRED (function call)
        val user_tier : string = get_user_tier()    // Type REQUIRED (function call)

        val discount_multiplier : f64 = if user_tier == "premium" {  // Type REQUIRED (conditional = runtime)
            -> 0.8                     // 20% discount
        } else if user_tier == "gold" {
            -> 0.9                     // 10% discount
        } else if is_first_time_user() {   // Runtime condition
            -> 0.95                    // 5% new user discount
        } else {
            -> 1.0                     // No discount
        }

        val discounted : f64 = base_price * discount_multiplier  // Type inferred (f64 * f64)

        val final_adjustment : f64 = if discounted < 10.0 {  // Type REQUIRED (conditional = runtime)
            return 0.0                     // Early exit: too cheap, make it free
        } else if discounted > 1000.0 {
            -> 1000.0                  // Cap at maximum price
        } else {
            -> discounted              // Use calculated price
        }

        -> final_adjustment
    }

    return final_price
}
```

## Error Handling

### Expression Context Requirements

```hexen
// ❌ Error: Missing type annotation
// val no_type = if condition {
//     -> value1
// } else {
//     -> value2
// }
// Error: "Conditional expressions require explicit type annotation (runtime operation)"

// ❌ Error: Not all paths ->
// val incomplete : i32 = if condition {
//     -> value1
// }
// Error: "All branches in conditional expression must -> a value or return from function"

// ✅ Correct: All paths covered
val complete : i32 = if condition {
    -> value1
} else {
    -> value2
}

// ✅ Correct: Early return is valid
val with_return : i32 = if error_condition {
    return error_value             // Early function exit
} else {
    -> normal_value
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

1. **Mental Model**: Think "conditional = runtime operation, like a function call"
2. **Type Annotations Required**: Conditional expressions ALWAYS require explicit type annotations (runtime barrier)
3. **Boolean Clarity**: Always use explicit boolean comparisons
4. **Expression Coverage**: Ensure all branches in conditional expressions -> or return
5. **Scope Awareness**: Variables are scoped to their containing branch
6. **No Comptime Preservation**: Conditionals consume comptime inputs but produce concrete outputs

## Conclusion

The Conditional System demonstrates Hexen's unified design philosophy in action: taking a fundamental programming construct and providing consistent, context-driven behavior that integrates seamlessly with the type system and unified block system.

### Key Innovations

1. **Context-Driven Behavior**: Same syntax works as both statements and expressions
2. **Runtime Simplification**: All conditionals treated uniformly as runtime operations (no compile-time special cases)
3. **Runtime Barrier Semantics**: Conditionals consume comptime inputs but always produce concrete outputs (type annotations required)
4. **Type System Integration**: Explicit boolean conditions and mandatory type annotations for expressions
5. **Block System Harmony**: Same scoping and evaluation rules throughout

### Architectural Coherence

The conditional system reinforces Hexen's core design principles:

- **"One Syntax, Multiple Contexts"**: Conditionals adapt to their usage context
- **"Explicit Over Implicit"**: Boolean conditions, type annotations, and conversions are always visible
- **"Consistent Mental Models"**: Conditionals behave like function calls (runtime barrier)
- **"Ergonomic + Transparent"**: Natural syntax with clear cost visibility (runtime operations explicit)

**The Runtime Barrier Concept:** Conditionals form a "type barrier" where comptime flexibility ends. This maintains Hexen's core principle: comptime types flow *into* runtime operations via adaptation, but concrete types flow *out* - making runtime costs always explicit and visible.

This creates a conditional system that is both **powerful and predictable** - enabling complex control flow patterns while maintaining the simplicity and consistency that defines Hexen's approach to language design.