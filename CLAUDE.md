# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Commands

### Development Setup
```bash
# Setup development environment
uv sync --extra dev

# Install dependencies only
uv sync
```

### Testing
```bash
# Run complete test suite (415 tests)
uv run pytest tests/ -v

# Run parser tests only
uv run pytest tests/parser/ -v

# Run semantic tests only
uv run pytest tests/semantic/ -v

# Run specific test file
uv run pytest tests/parser/test_minimal.py -v
```

## Architecture Overview

Hexen is an experimental system programming language implemented in Python 3.12+. The compiler follows a traditional two-phase architecture:

1. **Parser** (`src/hexen/parser.py`) - Lark-based PEG parser generating clean AST
2. **Semantic Analyzer** (`src/hexen/semantic/`) - Comprehensive type checking and validation

### Key Language Features

- **Comptime Type System**: Literals like `42` and `3.14` are comptime types that adapt to context
- **Unified Block System**: All blocks use `{}` syntax with context-appropriate behavior
- **Memory Safety**: Immutable by default (`val`), explicit mutability (`mut`)
- **No Literal Suffixes**: Write `42` not `42i64` - context determines type

## Language Syntax Reference

### Type System
- **Concrete types**: `i32`, `i64`, `f32`, `f64`, `string`, `bool`, `void`
- **Comptime types**: `comptime_int`, `comptime_float` (flexible until context resolution)
- **Type coercion**: `val x : i64 = 42` coerces `comptime_int` to `i64`

### Variable Declarations

#### `val` - Immutable Variables (Default)
- **Single Assignment**: Can only be assigned once at declaration
- **Type inference allowed**: Can omit type annotation when using comptime literals
- **Comptime preservation**: Preserves comptime types for maximum flexibility

```hexen
val immutable = 42          // Immutable by default (comptime_int preserved)
val typed : i64 = 42        // Explicit type annotation (forces i64)
val flexible = 42 + 100     // comptime_int (preserved - flexible!)
val as_i32 : i32 = flexible // SAME source → i32
val as_i64 : i64 = flexible // SAME source → i64
```

#### `mut` - Mutable Variables (Explicit)
- **Multiple assignments**: Can be reassigned as many times as needed
- **Explicit type required**: Must specify type annotation to prevent action-at-a-distance effects
- **Cannot preserve comptime types**: Sacrifice flexibility for safety

```hexen
mut variable : i32 = 100    // Explicit mutability + explicit type required
variable = 200              // ✅ Reassignment allowed
mut undefined : i32 = undef // Uninitialized variable (deferred initialization)
// mut bad_counter = 42     // ❌ Error: mut requires explicit type
```

### Functions

#### Basic Syntax
```hexen
func name(param : type) : return_type = {
    return expression
}

func void_func() : void = {
    return  // Bare return for void functions
}
```

#### Parameter Mutability
- **Immutable by default**: Parameters cannot be reassigned unless marked `mut`
- **Explicit mutability**: Use `mut` keyword for parameters that need modification
- **Type annotations required**: All parameters must have explicit type annotations

```hexen
// Immutable parameters (default)
func process(input: i32, threshold: f64) : bool = {
    // input = 42              // ❌ Error: Cannot reassign immutable parameter
    return input > threshold:i32  // ✅ Can read and use in expressions
}

// Mutable parameters (explicit)
func increment_and_return(mut counter: i32) : i32 = {
    counter = counter + 1       // ✅ OK: Mutable parameter can be reassigned
    return counter
}

func normalize_string(mut text: string) : string = {
    text = trim_whitespace(text)          // ✅ OK: Mutable parameter reassignment
    text = to_lowercase(text)             // ✅ OK: Subsequent reassignment
    return text
}
```

### Blocks
```hexen
// Expression blocks (must assign value)
val result = {
    val temp = 42
    -> temp * 2        // -> produces block value
}

// Expression blocks with control flow
val validated = {
    val input = get_input()
    if input < 0 {
        return -1          // return exits function early
    }
    -> input * 2       // -> produces block value
}

// Statement blocks (scoped execution)
{
    val scoped = "local"
    mut counter : i32 = 0  // explicit type required for mut
}
```

### Conditionals
```hexen
// No parentheses around conditions - required braces
if condition {              // ✅ Correct syntax
    do_something()
}

if user_input > 0 {         // ✅ Boolean-only conditions
    process_input()
} else if user_input == 0 {
    handle_zero()
} else {
    handle_negative()
}

// ❌ Common errors
// if (condition) { }       // Error: No parentheses around conditions
// if condition             // Error: Braces required
//     do_something()
// if count {               // Error: i32 cannot be used as bool
//     process()
// }

// ✅ Explicit boolean conversion required
val count : i32 = 5
if count > 0 {              // Explicit comparison produces bool
    process_count()
}
```

## Development Guidelines

### Code Style
- Use Ruff for formatting and linting (configured in `pyproject.toml`)
- Follow Python 3.12+ type hints throughout
- Maintain clean separation between parser and semantic analysis

### Testing Strategy
- **Parser tests**: Validate syntax and AST generation
- **Semantic tests**: Validate type checking and program semantics
- All tests use pytest framework

### File Naming Convention
- Hexen source files use `.hxn` extension
- Test files follow `test_*.py` pattern
- Documentation uses descriptive names (`COMPTIME_QUICK_REFERENCE.md`)

## Common Development Tasks

### Adding New Language Features
1. Update grammar in `hexen.lark`
2. Add AST nodes in `ast_nodes.py` if needed
3. Update parser logic in `parser.py`
4. Add semantic analysis in appropriate `semantic/` module
5. Write comprehensive tests in both `parser/` and `semantic/`

### Debugging Parse Issues
- Use `uv run hexen parse <file>` to see AST output
- Check grammar rules in `hexen.lark`
- Validate against existing examples in `examples/`

### Understanding Comptime Types
- Reference `docs/COMPTIME_QUICK_REFERENCE.md` for mental models
- Key insight: literals stay flexible until context forces resolution
- Four patterns: comptime+comptime, comptime+concrete, concrete+concrete, explicit conversions

## Important Notes

- This is a Python-first implementation for rapid prototyping
- Architecture designed for future LLVM backend via llvmlite
- Focus on language design experimentation over performance
- Comprehensive documentation in `docs/` directory provides deep technical details

---

# Type System Deep Dive

## Core Philosophy: Ergonomic Literals + Transparent Costs

Hexen's type system follows two core principles:
- **Ergonomic Literals**: Comptime types adapt seamlessly to context (no syntax burden)
- **Transparent Costs**: All concrete type mixing requires explicit syntax (`value:type`)

### Comptime Type System

**Key Insight**: Literals stay flexible until context forces them to become concrete.

```hexen
42        // comptime_int (flexible!)
3.14      // comptime_float (flexible!)
val x = 42   // Still comptime_int (preserved!)
val y : i32 = 42   // NOW becomes i32 (context forces resolution)
```

### The Four Patterns

#### 1. ✨ Comptime + Comptime = Comptime (Flexible)
```hexen
val math = 42 + 100 * 3.14    // comptime_float (stays flexible!)
val as_f32 : f32 = math       // Same source → f32
val as_f64 : f64 = math       // Same source → f64
val as_i32 : i32 = math:i32   // Same source → i32 (explicit conversion)
```

#### 2. 🔄 Comptime + Concrete = Concrete (Adapts)
```hexen
val count : i32 = 100
val result : i32 = count + 42    // i32 + comptime_int → i32 (adapts)
val bigger : i64 = count + 42    // i32 + comptime_int → i64 (context guides)
```

#### 3. 🔧 Concrete + Concrete = Explicit (Visible Costs)
```hexen
val a : i32 = 10
val b : i64 = 20
// val mixed = a + b         // ❌ Error: requires explicit conversion
val explicit : i64 = a:i64 + b  // ✅ Explicit: i32 → i64 (cost visible)
```

#### 4. ⚡ Same Concrete = Same Concrete (Identity)
```hexen
val a : i32 = 10
val b : i32 = 20
val result : i32 = a + b        // i32 + i32 → i32 (identity, no conversion)
```


### Type Conversion Rules

| From Type | To Type | Conversion | Required Syntax | Notes |
|-----------|---------|------------|-----------------|-------|
| **Comptime Types (Ergonomic Literals)** |
| `comptime_int` | `comptime_int` | ✅ Preserved | `val x = 42` | Comptime type preserved (flexible adaptation!) |
| `comptime_int` | `i32` | ✅ Implicit | `val x : i32 = 42` | No cost, ergonomic |
| `comptime_int` | `i64` | ✅ Implicit | `val x : i64 = 42` | No cost, ergonomic |
| `comptime_int` | `f32` | ✅ Implicit | `val x : f32 = 42` | No cost, ergonomic |
| `comptime_int` | `f64` | ✅ Implicit | `val x : f64 = 42` | No cost, ergonomic |
| `comptime_float` | `f32` | ✅ Implicit | `val x : f32 = 3.14` | No cost, ergonomic |
| `comptime_float` | `f64` | ✅ Implicit | `val x : f64 = 3.14` | No cost, ergonomic |
| `comptime_float` | `i32` | 🔧 Explicit | `val x : i32 = 3.14:i32` | Conversion cost visible |
| **Concrete Types (All Explicit)** |
| `i32` | `i64` | 🔧 Explicit | `val x : i64 = i32_val:i64` | Conversion cost visible |
| `i64` | `i32` | 🔧 Explicit | `val x : i32 = i64_val:i32` | Conversion + data loss visible |
| `f32` | `f64` | 🔧 Explicit | `val x : f64 = f32_val:f64` | Conversion cost visible |
| `f64` | `f32` | 🔧 Explicit | `val x : f32 = f64_val:f32` | Conversion + precision loss visible |

**Legend:**
- **✅ Preserved**: Comptime type stays flexible, maximum adaptability
- **✅ Implicit**: Happens automatically, no conversion cost
- **🔧 Explicit**: Requires explicit syntax (`value:type`), conversion cost visible

### Literal Overflow Behavior & Safety

Hexen provides **compile-time overflow detection** to prevent silent data loss:

#### Type Range Limits
| Type | Minimum Value | Maximum Value |
|------|---------------|---------------|
| `i32` | -2,147,483,648 | 2,147,483,647 |
| `i64` | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,807 |
| `f32` | ±3.4028235e+38 | ~7 decimal digits precision |
| `f64` | ±1.7976931e+308 | ~15 decimal digits precision |

#### Overflow Detection Examples
```hexen
// ✅ Valid literals within range
val valid_i32 : i32 = 2147483647      // Max i32 value
val valid_i64 : i64 = 9223372036854775807  // Max i64 value

// ❌ Compile-time overflow errors
// val overflow_i32 : i32 = 4294967296     // Error: Literal overflows i32 range
// val overflow_i64 : i64 = 18446744073709551616  // Error: Literal overflows i64 range
// val overflow_f32 : f32 = 3.5e+38        // Error: Literal overflows f32 range

// ✅ Comptime type preservation avoids premature overflow
val flexible = 4294967296          // comptime_int (no overflow yet)
val as_i64 : i64 = flexible        // ✅ Fits in i64
// val as_i32 : i32 = flexible     // ❌ Error: Would overflow i32

// 🔧 Future: Explicit truncation (if implemented)
// val intended : i32 = 4294967296:i32   // Explicit truncation acknowledgment
```

#### Error Message Format
```
Error: Literal 4294967296 overflows i32 range
  Expected: -2147483648 to 2147483647
  Suggestion: Use explicit conversion if truncation is intended: 4294967296:i32
```

### Uninitialized Variables (`undef`)

```hexen
// ❌ val + undef creates unusable variable
// val config : string = undef        // Error: cannot be assigned later

// ✅ mut + undef enables proper deferred initialization
mut config : string = undef        // OK: deferred initialization
config = "production"              // OK: first real assignment

// ❌ No type context
// mut bad = undef                 // Error: Cannot infer type

// ✅ Explicit type required
mut pending : i32 = undef         // OK: Type explicitly provided
```

## Unified Block System Deep Dive

### Core Philosophy: One Syntax, Context-Driven Behavior

All Hexen constructs use the same `{}` block syntax, but context determines behavior:
- **Expression blocks**: Produce values using `->`, support `return` for function exits
- **Statement blocks**: Execute code with scope isolation, no value production
- **Function bodies**: Unified with other blocks, context provides return type validation

### The `->` + `return` Dual Capability

Expression blocks support **both** statement types for maximum expressiveness:

#### `->` - Produces Block Value
```hexen
val computation = {
    val base = 42
    val result = base * 2
    -> result              // Assigns result to computation
}
```

#### `return` - Early Function Exit
```hexen
val validated_input = {
    val raw_input = get_user_input()
    if raw_input < 0 {
        return -1              // Early function exit with error
    }
    if raw_input > 1000 {
        return -2              // Early function exit with different error
    }
    -> sanitize(raw_input) // Success: assign sanitized input
}
```

### Powerful Patterns Enabled

#### Error Handling with Guards
```hexen
func safe_divide(a: f64, b: f64) : f64 = {
    val result = {
        if b == 0.0 {
            return 0.0         // Early exit: division by zero
        }
        -> a / b           // Normal case: assign division result
    }
    return result
}
```

#### Performance Optimization with Caching
```hexen
func expensive_calc(key: string) : f64 = {
    val result = {
        val cached = lookup_cache(key)
        if cached != null {
            return cached      // Early exit: cache hit
        }
        
        val computed = very_expensive_operation(key)
        save_to_cache(key, computed)
        -> computed        // Cache miss: assign computed value
    }
    
    log_cache_miss(key)        // Only executes on cache miss
    return result
}
```

### Block Types by Context

#### Expression Blocks (Value Production)
- **Must end with**: `-> expression` for value production
- **Control flow**: `return value` for early function exits
- **Scope**: Isolated variables
- **Type**: Determined by `->` expression type

#### Statement Blocks (Code Execution)
- **No value production**: Cannot use `->`
- **Control flow**: `return` for function exits allowed
- **Scope**: Isolated variables
- **Purpose**: Side effects and code organization

#### Function Body Blocks
- **Return requirements**: Type-dependent (`void` vs value-returning)
- **Scope**: Function scope management
- **Behavior**: Unified with other block types

---

# Binary Operations Deep Dive

## Core Philosophy: Same Rules as Individual Values

**Key Insight**: All binary operations (arithmetic, comparison, logical) follow the **same type resolution rules** as individual values - no special restrictions.

### Operator Categories

#### Arithmetic Operators
- `+`, `-`, `*`: Standard mathematical operations
- `/`: Float division (mathematical, produces floating-point results)
- `\`: Integer division (efficient truncation, integer results only)
- `%`: Modulo

#### Comparison Operators
- `<`, `>`, `<=`, `>=`: Relational comparison (always produce `bool`)
- `==`, `!=`: Equality comparison (always produce `bool`)

#### Logical Operators
- `&&`: Logical AND (short-circuit evaluation)
- `||`: Logical OR (short-circuit evaluation)
- `!`: Logical NOT

### Division Operations: Float vs Integer

#### Float Division (`/`) - Mathematical Division
```hexen
val precise = 10 / 3             // comptime_int / comptime_int → comptime_float
val as_f32 : f32 = 22 / 7        // comptime_float → f32 (implicit)
val as_f64 : f64 = 10 / 3        // comptime_float → f64 (implicit)

// Mixed concrete types require explicit conversions
val int_val : i32 = 10
val float_val : f64 = 3.0
val explicit : f64 = int_val:f64 / float_val  // i32 → f64 (explicit)
```

#### Integer Division (`\`) - Efficient Truncation
```hexen
val fast = 10 \ 3                // comptime_int \ comptime_int → comptime_int
val as_i64 : i64 = 22 \ 7        // comptime_int → i64 (implicit)

// Integer division requires integer operands
val a : i32 = 10
val b : i32 = 3
val efficient : i32 = a \ b      // i32 \ i32 → i32 (identity)

// ❌ Float operands with integer division is an error
// val invalid = 10.5 \ 2.1      // Error: Integer division requires integer operands
```

### Binary Operation Type Resolution

| Operation Pattern | Result Type | Syntax | Notes |
|-------------------|-------------|---------|-------|
| `comptime + comptime` (same type) | ✅ Preserved | `val x = 42 + 100` | Comptime type preserved (maximum flexibility!) |
| `comptime + comptime` (context provided) | ✅ Implicit | `val x : i32 = 42 + 100` | No cost, ergonomic adaptation |
| `comptime + concrete` | ✅ Implicit | `i32_val + 42` | No cost, comptime adapts |
| `same_concrete + same_concrete` | ✅ Identity | `i32_val + i32_val` | No conversion needed |
| `mixed_concrete + mixed_concrete` | 🔧 Explicit | `val x : f64 = i32_val:f64 + f64_val` | Conversion cost visible |

### Comparison Operations

Comparison operations follow **identical type resolution rules** as arithmetic operations:

```hexen
// ✅ Comptime types work naturally
val is_greater = 42 > 30              // comptime_int > comptime_int → bool
val mixed_comp = 42 < 3.14            // comptime_int < comptime_float → bool

// ✅ Same concrete types
val a : i32 = 10
val b : i32 = 20
val result = a < b                    // i32 < i32 → bool

// ❌ Mixed concrete types require explicit conversions (same as arithmetic)
val int_val : i32 = 10
val float_val : f64 = 3.14
// val comparison = int_val < float_val  // Error: mixed concrete types
val explicit_comp = int_val:f64 < float_val  // ✅ Explicit conversion required
```

### Logical Operations

```hexen
// ✅ Boolean operations with short-circuit evaluation
val true_val : bool = true
val false_val : bool = false
val and_result = true_val && false_val    // bool && bool → bool (false)
val or_result = true_val || false_val     // bool || bool → bool (true)

// ✅ No implicit boolean coercion - explicit comparisons required
val count : i32 = 5
// val is_truthy = count                 // ❌ Error: i32 cannot be used as bool
val is_positive = count > 0             // ✅ Explicit comparison produces bool
```

### Complex Expressions

```hexen
// ✅ Comptime operations stay comptime through complex chains
val step1 = 42 + 100              // comptime_int + comptime_int → comptime_int
val step2 = step1 * 2             // comptime_int * comptime_int → comptime_int
val step3 = step2 + 3.14          // comptime_int + comptime_float → comptime_float
val step4 = step3 / 2.0           // comptime_float / comptime_float → comptime_float

// ✅ All steps happen in "comptime space" until context forces resolution
val final_f64 : f64 = step4       // NOW: comptime_float → f64
val final_f32 : f32 = step4       // SAME source, different target
val final_i32 : i32 = step4:i32   // Explicit conversion needed

// ✅ Expression blocks preserve comptime flexibility
val complex_calc = {
    val base = 42 + 100           // comptime_int + comptime_int → comptime_int
    val scaled = base * 3.14      // comptime_int * comptime_float → comptime_float
    -> scaled / 2.0               // comptime_float / comptime_float → comptime_float (preserved!)
}
val as_f64 : f64 = complex_calc   // SAME source → f64
val as_f32 : f32 = complex_calc   // SAME source → f32

// 🔧 Mixed concrete types require explicit conversions
val a : i32 = 10
val b : i64 = 20
val c : f32 = 3.14
val result : f64 = a:f64 + (b:f64 * c:f64)  // All conversions explicit
```

### Operator Precedence

| Level | Operators | Associativity | Description |
|-------|-----------|---------------|-------------|
| 1 | `-`, `!` | Right | Unary minus, logical NOT |
| 2 | `*`, `/`, `\`, `%` | Left | Multiplication, float division, integer division, modulo |
| 3 | `+`, `-` | Left | Addition, subtraction |
| 4 | `<`, `>`, `<=`, `>=` | Left | Relational comparison |
| 5 | `==`, `!=` | Left | Equality comparison |
| 6 | `&&` | Left | Logical AND |
| 7 | `\|\|` | Left | Logical OR |

### Key Design Principles

1. **Unified Type Resolution**: Same rules for all operations (arithmetic, comparison, logical)
2. **Transparent Costs**: All concrete type mixing requires explicit conversions
3. **Ergonomic Literals**: Comptime types adapt seamlessly with zero runtime cost
4. **Predictable Behavior**: Division behavior determined by operator choice (`/` vs `\`)
5. **Boolean Clarity**: Comparison operations always produce `bool`, no implicit coercion

### Integration with Expression Blocks

Expression blocks work seamlessly with the type system and binary operations:

```hexen
// ✅ Expression blocks + comptime type preservation
val flexible_math = {
    val base = 42 + 100 * 3       // All comptime operations
    val scaled = base * 2.5       // comptime_int * comptime_float → comptime_float
    -> scaled                     // Preserves comptime_float flexibility
}
val as_i32 : i32 = flexible_math:i32  // Explicit conversion needed
val as_f32 : f32 = flexible_math      // Same source → f32
val as_f64 : f64 = flexible_math      // Same source → f64

// ✅ Expression blocks with control flow and validation
func process_data(input: i32) : i32 = {
    val validated = {
        if input < 0 {
            return -1             // Early function exit: invalid input
        }
        if input > 1000 {
            return -2             // Early function exit: input too large
        }
        -> input * 2          // Success: assign processed input
    }
    
    // This only executes if validation succeeded
    return validated + 10
}

// 🔴 mut variables cannot preserve expression block comptime types
mut concrete_result : f64 = {
    val calc = 42 + 100 * 3       // Same comptime operations
    -> calc / 2               // comptime_float → f64 (immediately resolved!)
}
// No flexibility preserved - concrete_result is concrete f64

// ✅ Expression blocks with mixed concrete types (explicit conversions)
func mixed_computation() : f64 = {
    val int_val : i32 = 10
    val float_val : f64 = 3.14
    
    val result : f64 = {
        val converted = int_val:f64 + float_val  // Explicit conversion required
        val scaled = converted * 2.5             // f64 * comptime_float → f64
        -> scaled                            // Block assign concrete f64
    }
    
    return result
}
```

---

# Function System Deep Dive

## Function Calls & Comptime Type Context

Function parameters provide **type context** for comptime type resolution, enabling maximum flexibility:

```hexen
func calculate_area(width: f64, height: f64) : f64 = {
    return width * height
}

func process_count(items: i32, multiplier: i32) : i32 = {
    return items * multiplier
}

// ✨ Comptime type preservation + function context
val math_result = 42 + 100 * 5          // comptime_int (preserved!)
val float_calc = 10.5 * 2.0             // comptime_float (preserved!)

// Same expressions adapt to different function contexts
val area : f64 = calculate_area(math_result, float_calc)    // comptime types adapt to f64 parameters
val count : i32 = process_count(math_result, 5)            // comptime types adapt to i32 parameters

// Traditional literals also work
val area2 : f64 = calculate_area(42, 30)        // comptime_int → f64 for parameters
val count2 : i32 = process_count(100, 5)        // comptime_int → i32 for parameters
```

### Mixed Parameter Types & Explicit Conversions

When functions have mixed parameter types, each argument adapts independently but concrete type mixing still requires explicit conversions:

```hexen
func mixed_calculation(base: i32, multiplier: f64, precision: f32) : f64 = {
    val scaled : f64 = base:f64 * multiplier      // ✅ Explicit conversion: i32 → f64
    return scaled * precision:f64                 // ✅ Explicit conversion: f32 → f64
}

// ✨ Comptime literals adapt seamlessly to parameter contexts
val result1 : f64 = mixed_calculation(42, 3.14, 1.5)  // All comptime → adapt to parameter types

// 🔧 Mixed concrete types require explicit conversions
val int_val : i32 = 10
val large_val : i64 = 20
val float_val : f64 = 3.14

// ❌ Error: Mixed concrete types
// mixed_calculation(large_val, float_val, float_val)

// ✅ Explicit conversions make costs visible
val result2 : f64 = mixed_calculation(large_val:i32, float_val, float_val:f32)
```

### Integration with Return Types

Function return types provide context for comptime type resolution in return statements:

```hexen
// Return type provides context for comptime literals
func get_count() : i32 = {
    return 42 + 100                      // comptime_int adapts to i32 return type
}

func get_ratio() : f64 = {
    return 42 + 3.14                     // comptime_float adapts to f64 return type
}

func precise_calc() : f32 = {
    return 10 / 3                        // Float division → comptime_float → f32
}

// Mixed concrete types in return statements require explicit conversions
func mixed_return(a: i32, b: f64) : f64 = {
    // return a + b                      // ❌ Error: Mixed concrete types
    return a:f64 + b                     // ✅ Explicit conversion required
}
```

---

# Literal Overflow Protection Deep Dive

## Safety Philosophy: Compile-Time Detection

Hexen follows a **"safety-first"** approach to literal overflow, similar to modern systems languages like Rust and Zig:

### Detection Points
- **Literal parsing**: When comptime literals are assigned explicit types
- **Type coercion**: When comptime types resolve to concrete types
- **Assignment validation**: During variable declaration and assignment

### Comparison with Other Languages

| Language | Behavior | Safety Level |
|----------|----------|--------------|
| **Hexen** | ❌ Compile error | 🟢 Very Safe |
| **Zig** | ❌ Compile error | 🟢 Very Safe |
| **Rust** | ❌ Compile error | 🟢 Very Safe |
| **Java** | ❌ Compile error | 🟢 Very Safe |
| **Go** | ❌ Compile error | 🟢 Very Safe |
| **C/C++** | ⚠️ Warning + truncation | 🔴 Unsafe |
| **Python** | ✅ Arbitrary precision | 🟡 Different paradigm |

### Edge Cases & Special Literals

```hexen
// Boundary values (should work)
val max_i32 : i32 = 2147483647     // ✅ Exactly at boundary
val min_i32 : i32 = -2147483648    // ✅ Exactly at boundary

// Hexadecimal literals
// val hex_overflow : i32 = 0x100000000  // ❌ Error: 2^32 in hex

// Binary literals
// val bin_overflow : i32 = 0b100000000000000000000000000000000  // ❌ Error: 2^32 in binary

// Negative overflow
// val neg_overflow : i32 = -2147483649   // ❌ Error: Below i32 minimum
```

### Implementation Integration

The overflow detection integrates seamlessly with the comptime type system:

```hexen
// Comptime types stay flexible until forced to resolve
val flexible = 4294967296        // comptime_int (no error yet)
val as_i32 : i32 = flexible      // ❌ Error: NOW detects overflow during coercion
val as_i64 : i64 = flexible      // ✅ Coercion succeeds (fits in i64)

// Consistency with explicit conversion requirements
val small : i32 = 42
val large : i64 = small:i64      // ✅ Explicit conversion required (type system rule)

// Overflow follows same explicit pattern (future enhancement)
// val truncated : i32 = 4294967296:i32  // 🔧 Explicit truncation (if implemented)
```

---

# Reference System Deep Dive

## Core Philosophy: Safe Data Sharing for Concrete Types Only

Hexen's reference system enables safe, efficient data sharing while maintaining the clean separation between comptime and runtime. References work **exclusively with concrete types**, preserving Hexen's fundamental type system boundaries.

**Design Principles:**
- **Concrete Types Only**: References can only point to runtime-allocated, concrete data
- **Transparent Access Costs**: Reference operations are explicit and visible (`&` syntax)
- **Safe by Default**: No null pointer dereferences or dangling references
- **Memory Efficient**: Share data without copying large structures
- **Lifetime Managed**: Compiler prevents references from outliving their targets
- **Automatic Dereferencing**: References work transparently like values

## Basic Reference Syntax

### Reference Variable Declaration
```hexen
val &reference_name : concrete_type = &target_variable
mut &reference_name : concrete_type = &target_variable
```

**Critical Requirement**: Both reference and target must have **explicit concrete types**.

### Reference Examples
```hexen
// ✅ Valid reference declarations
val data : i32 = 42                     // Concrete i32 variable
val &data_ref : i32 = &data             // Reference to concrete i32

val array : [5]f64 = [1.0, 2.0, 3.0, 4.0, 5.0]    // Concrete array
val &array_ref : [5]f64 = &array        // Reference to concrete array

// ❌ ERRORS: Cannot reference comptime types
val flexible = 42                       // comptime_int
// val &bad_ref : i32 = &flexible       // Error: Cannot reference comptime type

// ❌ ERRORS: Missing explicit types
val concrete : i32 = 42
// val &missing_type = &concrete        // Error: Reference requires explicit type
```

## Reference Functions

### Function Parameter Syntax
```hexen
func function_name(&param_name: concrete_type) : return_type = {
    // Function body using param_name (automatically dereferenced)
}
```

### Function Examples
```hexen
// Efficient array processing without copying
func sum_array(&data: [_]i32) : i32 = {
    // Direct access to original array (no copy)
    return data[0] + data[data.length - 1]  // Automatic dereferencing
}

// Mutable reference parameters
func increment(&value: i32) : void = {
    value = value + 1               // Modifies original through reference
}

// Large data processing without memory overhead
func process_large_dataset(&dataset: [10000]f64) : f64 = {
    // Efficient: no copying of 80KB of data
    return dataset[0] * dataset[9999]   // Direct access to original
}
```

### Function Call Syntax
```hexen
val data : [1000]i32 = initialize_data()
val result : i32 = sum_array(&data)        // ✅ Pass reference to concrete array

mut number : i32 = 10
increment(&number)                          // ✅ Pass reference to mutable variable

// ❌ ERRORS: Cannot pass comptime types by reference
val flexible = [1, 2, 3]                   // comptime_array_int
// sum_array(&flexible)                     // Error: Cannot reference comptime type
```

## Mutability System: View-Based Approach

Reference mutability determines **view permissions**, while target mutability determines **underlying data constraints**.

**The Fundamental Rule**: Reference mutability = View permissions
- **`val &ref`** = **Read-only view** (regardless of target mutability)
- **`mut &ref`** = **Read-write view** (requires mutable target)

### Mutability Compatibility Matrix

| Target Data | Reference Type | Result | Explanation |
|-------------|---------------|---------|-------------|
| `val data` | `val &ref` | ✅ **Valid** | Read-only view of immutable data |
| `val data` | `mut &ref` | ❌ **Compile Error** | Can't create writable view of immutable data |
| `mut data` | `val &ref` | ✅ **Valid** | Read-only view of mutable data |
| `mut data` | `mut &ref` | ✅ **Valid** | Read-write view of mutable data |

### Practical Mutability Examples
```hexen
// ✅ VALID: Read-only view of immutable data
val immutable_data : i32 = 42
val &readonly_ref : i32 = &immutable_data
val value : i32 = readonly_ref              // ✅ Can read
// readonly_ref = 10                        // ❌ Error: Read-only view cannot modify

// ❌ INVALID: Cannot create writable view of immutable data
val immutable_data : i32 = 42
// mut &invalid_ref : i32 = &immutable_data // ❌ COMPILE ERROR!

// ✅ VALID: Read-write view of mutable data
mut mutable_data : i32 = 42
mut &writable_view : i32 = &mutable_data
val value : i32 = writable_view             // ✅ Can read
writable_view = 10                          // ✅ Can modify (mutable_data becomes 10)
```

## Automatic Dereferencing

References are automatically dereferenced in expressions - no explicit dereference operator needed:

```hexen
val data : i32 = 42
val &ref : i32 = &data

// Automatic dereferencing in expressions
val doubled : i32 = ref * 2                 // Automatically reads through reference
val comparison : bool = ref > 30            // Automatic dereferencing for comparisons

// Assignment through mutable references
mut value : i32 = 10
mut &value_ref : i32 = &value
value_ref = 20                              // Automatically writes through reference

// Function calls with automatic dereferencing
func process_number(num: i32) : i32 = { return num * 2 }       // Expects VALUE
val result : i32 = process_number(ref)      // Reference automatically dereferenced

func process_reference(&num: i32) : i32 = { return num * 2 }   // Expects REFERENCE
val ref_result : i32 = process_reference(&data)  // Pass reference directly
```

## Integration with Array System

References integrate seamlessly with arrays for efficient data processing:

### Array Reference Parameters
```hexen
// Zero-copy array processing
func process_array(&data: [_]i32) : i32 = {
    // No copying - direct access to original array
    return data[0] + data[data.length - 1]
}

// Mutable array references
func normalize_array(mut &array: [_]f64, factor: f64) : void = {
    array[0] = array[0] / factor            // Direct modification
}

// Element and row references
val matrix : [_][_]f64 = [[1.0, 2.0], [3.0, 4.0]]
val &first_element : f64 = &matrix[0][0]    // Reference to single element
val &first_row : [2]f64 = &matrix[0]        // Reference to entire row

// Array flattening with references (zero-cost)
val matrix_2d : [4][4]f64 = load_matrix()
val &flattened : [_]f64 = &matrix_2d        // Zero-cost flat view
```

### Performance Benefits with Arrays
```hexen
// Value parameter approach (copying) - EXPENSIVE
func process_by_copy(data: [10000]f64) : f64 = {
    // Receives COPY of 80KB of data
    return data[0] * data[9999]
}

// Reference parameter approach (zero-copy) - EFFICIENT
func process_by_reference(&data: [10000]f64) : f64 = {
    // Receives REFERENCE (~8 bytes)
    return data[0] * data[9999]             // Same computation, no copying
}

val scientific_data : [10000]f64 = load_data()
val expensive : f64 = process_by_copy(scientific_data)      // 80KB copied
val efficient : f64 = process_by_reference(&scientific_data) // ~8 bytes reference
```

## Safety Guarantees

### Lifetime Safety
References cannot outlive the variables they reference:

```hexen
// ✅ VALID: Reference stays within scope of target
val data : i32 = 42
val &data_ref : i32 = &data     // Both valid until end of current scope

// ❌ INVALID: Reference escaping target scope
func create_dangling_ref() : &i32 = {
    val local_data : i32 = 42
    return &local_data          // Error: Reference to local variable escaping scope
}
```

### Type Safety
- **No Null References**: All references must point to valid, concrete variables
- **Type Compatibility**: References maintain strict type compatibility with targets
- **Explicit Conversions**: Reference conversions follow same rules as concrete types

```hexen
val int_data : i32 = 42
val &int_ref : i32 = &int_data

// ❌ No automatic conversions between reference types
// val &float_ref : f64 = &int_data     // Error: i32 reference ≠ f64 reference

// ✅ Explicit conversions on dereferenced values
val converted : f64 = int_ref:f64       // Explicit: i32 → f64 conversion
```

## Error Messages

Hexen provides clear, actionable error messages for reference issues:

### Comptime Type Reference Errors
```
Error: Cannot create reference to comptime type 'comptime_int'
  Variable 'flexible' has comptime type that exists only during compilation
  Suggestion: Use explicit type annotation to create concrete variable:
    val concrete : i32 = 42
    val &ref : i32 = &concrete
```

### Mutability Mismatch Errors
```
Error: Cannot create mutable reference to immutable data
  Variable 'immutable_data' is declared with 'val' (immutable)
  Cannot create 'mut &ref' (writable view) of immutable data
  Suggestion: Use read-only reference instead:
    val &readonly_ref : i32 = &immutable_data
```

## Benefits

### Performance Benefits
- **Zero-Copy Access**: Large arrays and structures shared without duplication
- **Function Parameter Efficiency**: Pass large data by reference instead of copying
- **Memory Efficiency**: Multiple names for same data without memory overhead
- **Compile-Time Optimization**: Compiler can optimize knowing reference relationships

### Safety Guarantees
- **No Null References**: All references must point to valid, concrete variables
- **Lifetime Safety**: References cannot outlive their target variables
- **No Dangling References**: Scope analysis prevents references to destroyed data
- **Type Safety**: References maintain strict type compatibility with their targets
- **Mutability Safety**: Reference mutability interacts safely with target mutability

### Developer Experience
- **Safe Data Sharing**: Efficient access to large data structures without copying
- **Clear Syntax**: `&` operator provides familiar, readable reference semantics
- **Automatic Dereferencing**: No manual pointer arithmetic or dereferencing operators
- **Explicit Costs**: All reference operations are visible in the code
- **Integration**: Seamless integration with arrays, functions, and type system

---

# Array Type System Deep Dive

## Core Philosophy: Arrays + Comptime Types + References

Hexen's array type system extends the language's **"Ergonomic Literals + Transparent Runtime Costs"** philosophy to collections while integrating seamlessly with the reference system:

**Design Principles:**
- **Ergonomic Array Literals**: Comptime array types adapt seamlessly (zero runtime cost)
- **Transparent Runtime Costs**: All concrete array conversions require explicit syntax (`value:type`)
- **Safe Array Data Sharing**: Array references (`&arr: [N]T`) enable efficient zero-copy data access
- **Explicit Copy vs Reference Choice**: Clear distinction between `arr` (copy) and `&arr` (share) in function parameters
- **Consistent with Individual Values**: Arrays follow identical patterns to single-value type system
- **Reference-Only Flattening**: True zero-cost dimensional flattening only works with references
- **Size-as-Type**: Array size is part of the type itself, enabling compile-time safety

## Basic Array Syntax

### Array Literals and Type Inference
```hexen
// ✨ Comptime array literals (flexible!)
val flexible_ints = [1, 2, 3, 4, 5]         // comptime_array_int (flexible!)
val flexible_floats = [3.14, 2.71, 1.41]    // comptime_array_float (flexible!)
val mixed_array = [42, 3.14, 100]           // comptime_array_float (mixed → float)

// Same flexible arrays adapt to different contexts
val ints_as_i32 : [_]i32 = flexible_ints    // → [5]i32
val ints_as_i64 : [_]i64 = flexible_ints    // Same source → [5]i64
val ints_as_f64 : [_]f64 = flexible_ints    // Same source → [5]f64

// Explicit concrete arrays
val concrete_ints : [_]i32 = [1, 2, 3]      // [3]i32 (concrete)
val typed_array : [5]f64 = [1.0, 2.0, 3.0, 4.0, 5.0]  // [5]f64 (explicit size)
```

### Array Access and Mutability
```hexen
// Immutable arrays
val numbers : [_]i32 = [10, 20, 30, 40, 50]     // [5]i32
val first : i32 = numbers[0]                    // Element access: 10
val length = numbers.length                     // Array length: 5

// Mutable arrays (explicit type required)
mut counters : [_]i32 = [0, 1, 2, 3, 4]        // [5]i32
counters[0] = 100                               // Element reassignment
counters[1] = counters[1] + 10                  // Element modification
```

## Array References: Zero-Copy Data Sharing

### Basic Array Reference Syntax
Array references follow the same patterns as other reference types:

```hexen
// Array reference declarations
val data : [1000]i32 = initialize_data()       // Concrete array
val &data_ref : [1000]i32 = &data              // Reference to entire array

// Function parameters with array references
func process_array(&data: [_]i32) : i32 = {
    // Direct access to original array (no copy)
    return data[0] + data[data.length - 1]      // Automatic dereferencing
}

func sum_large_dataset(&dataset: [10000]f64) : f64 = {
    // Efficient: no copying of 80KB of data
    return dataset[0] * dataset[9999]           // Direct access to original
}
```

### Performance: Copy vs Reference Comparison
```hexen
// Value parameter approach (copying) - EXPENSIVE
func process_by_copy(data: [10000]f64) : f64 = {
    // Receives COPY of 80KB of data
    return data[0] * data[9999]
}

// Reference parameter approach (zero-copy) - EFFICIENT
func process_by_reference(&data: [10000]f64) : f64 = {
    // Receives REFERENCE (~8 bytes)
    return data[0] * data[9999]             // Same computation, no copying
}

val scientific_data : [10000]f64 = load_data()
val expensive : f64 = process_by_copy(scientific_data)      // 80KB copied
val efficient : f64 = process_by_reference(&scientific_data) // ~8 bytes reference
```

### Element and Row References
References to individual elements or rows from concrete arrays enable zero-copy access patterns:

```hexen
// Single element references
val numbers : [_]i32 = [10, 20, 30, 40, 50]     // [5]i32
val &first_ref : i32 = &numbers[0]              // Reference to first element
val &last_ref : i32 = &numbers[4]               // Reference to last element

// Using element references in functions
func process_element(&elem: i32) : i32 = {
    return elem * 2                              // Automatic dereferencing
}
val doubled : i32 = process_element(&numbers[2]) // Pass element by reference

// Row references from multidimensional arrays
val matrix : [_][_]f64 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]  // [2][3]f64
val &first_row : [3]f64 = &matrix[0]            // Reference to entire first row
val &second_row : [3]f64 = &matrix[1]           // Reference to entire second row

func compute_row_sum(&row: [3]f64) : f64 = {
    return row[0] + row[1] + row[2]             // Automatic dereferencing
}
val sum1 : f64 = compute_row_sum(&matrix[0])    // Process first row by reference
```

## Multidimensional Arrays

### Array Flattening: Reference-Only Zero-Cost Views
The row-major memory layout enables **true zero-cost array flattening** - but only through references:

```hexen
// ❌ Value-Based Flattening (Copying - Not Zero Cost)
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]  // 6 elements total
val flattened_copy : [_]i32 = matrix             // ❌ Copies entire array! (24 bytes)
// This creates a NEW array in memory with a different layout

// ✅ Reference-Based Flattening (True Zero Cost)
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]  // 6 elements total in row-major order
val &flattened : [_]i32 = &matrix                 // ✅ Zero cost! Same memory, different view
// Memory layout unchanged: [1, 2, 3, 4, 5, 6]
// Same memory addresses, different type view - TRUE zero runtime cost
```

### Multidimensional Array Processing
```hexen
// 2D array reference parameters
func process_matrix(&matrix: [_][_]f64, factor: f64) : f64 = {
    // Direct access to 2D array without copying
    return matrix[0][0] * matrix[matrix.length-1][matrix[0].length-1] * factor
}

// In-place 2D array processing
func transform_matrix(mut &matrix: [_][_]f64, scale: f64) : void = {
    matrix[0][0] = matrix[0][0] * scale     // Direct modification
    matrix[1][1] = matrix[1][1] * scale     // No memory allocation
}

// Array flattening with references (zero-cost)
func process_flat_view(&matrix: [4][4]f64) : f64 = {
    val &flattened : [_]f64 = &matrix       // Zero-cost flattened view
    return flattened[0] + flattened[15]     // Access via flat view: matrix[0][0] + matrix[3][3]
}

// Usage with multidimensional arrays
val matrix_2d : [4][4]f64 = load_transformation_matrix()
val result : f64 = process_matrix(&matrix_2d, 2.0)     // No copying of 128 bytes
process_flat_view(&matrix_2d)                          // Zero-cost flattened access
```

## Array Type System Integration

### Arrays Follow the Four Patterns
Arrays follow the same type resolution rules as individual values:

```hexen
// 1. ✨ Comptime + Comptime = Comptime (Flexible)
val flexible_array = [1, 2, 3] + [4, 5, 6]     // comptime_array_int (preserved!)
val as_i32 : [_]i32 = flexible_array           // → [6]i32
val as_i64 : [_]i64 = flexible_array           // Same source → [6]i64

// 2. 🔄 Comptime + Concrete = Concrete (Adapts)
val concrete : [3]i32 = [10, 20, 30]
val mixed : [_]i32 = concrete + [40, 50, 60]   // Adapts to i32 context

// 3. 🔧 Concrete + Concrete = Explicit (Visible Costs)
val arr1 : [3]i32 = [1, 2, 3]
val arr2 : [3]i64 = [4, 5, 6]
// val combined = arr1 + arr2                  // ❌ Error: requires explicit conversion
val explicit : [_]i64 = arr1:[_]i64 + arr2     // ✅ Explicit conversion required

// 4. ⚡ Same Concrete = Same Concrete (Identity)
val a : [3]i32 = [1, 2, 3]
val b : [3]i32 = [4, 5, 6]
val result : [_]i32 = a + b                    // i32 arrays → i32 result
```

### Array References with Mutability
Array references follow the same mutability rules as other references:

```hexen
// Read-only array reference (default)
func analyze_data(&data: [_]i32, threshold: i32) : i32 = {
    // data[0] = 999                        // ❌ Error: Cannot modify through read-only reference
    val analysis : i32 = data[0] + data[1] // ✅ Read access through reference
    return analysis
}

// Mutable array reference (explicit)
func scale_values(mut &values: [_]f64, factor: f64) : void = {
    values[0] = values[0] * factor          // ✅ Can modify through mutable reference
    values[1] = values[1] * factor          // ✅ Direct in-place processing
}

// Calling mutable array reference functions
val data : [100]i32 = load_data()
analyze_data(&data, 50)                     // ✅ Read-only access with immutable array

mut processable : [100]f64 = load_values()
scale_values(&processable, 1.5)             // ✅ In-place modification with mutable array

val immutable : [100]f64 = load_constants()
// scale_values(&immutable, 1.5)           // ❌ Error: Cannot create mutable reference to immutable array
```

## Common Array Patterns

### Systems Programming with Arrays
```hexen
// Graphics: Vertex data processing with zero-copy references
val vertex_data : [100][6]f32 = generate_vertices()  // 100 vertices, 6 components each
val &gpu_buffer : [_]f32 = &vertex_data              // ✅ Zero cost! Same memory, flat view
upload_to_gpu(&gpu_buffer)                           // Pass reference to GPU

// Scientific computing: Matrix operations without copying
val matrix : [512][512]f64 = load_matrix()
val &linear_data : [_]f64 = &matrix                  // ✅ Zero-cost view of 2MB matrix
blas_gemv(&linear_data, &vector)                     // No copying - pass references

// Image processing: RGB pixel data
val image : [height][width][3]u8 = load_image()
val &pixel_buffer : [_]u8 = &image                   // ✅ Zero-cost flat view
compress_jpeg(&pixel_buffer)                         // Process via reference
```

### Comptime Array Flexibility
```hexen
// Comptime arrays adapt to different materializations
val comptime_matrix = [[42, 100], [200, 300]]        // comptime 2D array
val flat_i32 : [_]i32 = comptime_matrix              // → [4]i32 (materialized copy)
val flat_f64 : [_]f64 = comptime_matrix              // → [4]f64 (different materialized copy)
val flat_f32 : [_]f32 = comptime_matrix              // → [4]f32 (another materialized copy)

// Multiple runtime materializations from single comptime source
// Each creates a separate concrete array in memory
```

## Array Type Safety

### Compile-Time Size Checking
```hexen
val matrix_2x3 : [2][3]i32 = data                    // 6 elements total
val cube_2x2x2 : [2][2][2]i32 = data                 // 8 elements total

val flat_6 : [_]i32 = matrix_2x3                     // ✅ → [6]i32
val flat_8 : [_]i32 = cube_2x2x2                     // ✅ → [8]i32

// val wrong : [5]i32 = matrix_2x3                   // ❌ Compile error: 6 ≠ 5
```

### Array Reference Safety
- **No Null References**: All array references must point to valid, concrete arrays
- **Lifetime Safety**: Array references cannot outlive their target arrays
- **Size Safety**: Array bounds checking prevents runtime errors
- **Type Safety**: Array references maintain strict type compatibility

## Benefits

### Performance Benefits
- **Zero-Copy Array References**: Reference-based array sharing (`&arr`) with no copying overhead
- **Reference-Only Flattening**: True zero-cost dimensional flattening only with references (`&arr`)
- **Copy vs Reference Choice**: Explicit distinction between copying (`arr`) and sharing (`&arr`) data
- **Efficient Large Array Processing**: References enable processing of large arrays without memory duplication

### Type Safety Benefits
- **Compile-Time Size Checking**: Array size mismatches caught at compile time
- **Element Type Safety**: All element conversions follow standard type rules
- **Array Reference Safety**: Immutable references prevent accidental mutation (`val &arr`)
- **Mutable Reference Requirements**: Mutable array references require explicit mutable targets (`mut &arr`)
- **Automatic Dereferencing Safety**: References work like values with compile-time lifetime checking

### Developer Experience
- **Ergonomic Array Literals**: Comptime arrays adapt seamlessly to context
- **Consistent with Values**: Same patterns as individual value type system
- **Predictable Rules**: Arrays follow the same four-pattern system
- **Clear Intent**: All array conversions are explicit and visible
- **Integration**: Seamless integration with references, functions, and expression blocks