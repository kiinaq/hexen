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

### Code Quality
```bash
# Format code with Ruff
uv run ruff format .

# Lint code with Ruff
uv run ruff check .

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Hexen Compiler Usage
```bash
# Parse and analyze a Hexen program
uv run hexen parse examples/01_getting_started/hello_world.hxn

# Parse with JSON output
uv run hexen parse examples/02_types/comptime_types.hxn --json
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

### Project Structure
```
src/hexen/
├── hexen.lark              # PEG grammar (76 lines)
├── parser.py               # Syntax analysis (356 lines)
├── ast_nodes.py            # AST definitions (73 lines)
├── semantic/               # Semantic analysis (2,580+ lines)
│   ├── analyzer.py         # Main orchestrator
│   ├── type_util.py        # Type system utilities
│   ├── declaration_analyzer.py  # Variable/function declarations
│   ├── expression_analyzer.py   # Expressions & type annotations
│   ├── binary_ops_analyzer.py   # Binary operations
│   ├── assignment_analyzer.py   # Assignment validation
│   ├── return_analyzer.py      # Return statement handling
│   ├── block_analyzer.py       # Block analysis
│   └── symbol_table.py         # Scope management
└── cli.py                  # Command-line interface
```

## Language Syntax Reference

### Type System
- **Concrete types**: `i32`, `i64`, `f32`, `f64`, `string`, `bool`, `void`
- **Comptime types**: `comptime_int`, `comptime_float` (flexible until context resolution)
- **Type coercion**: `val x : i64 = 42` coerces `comptime_int` to `i64`

### Variable Declarations
```hexen
val immutable = 42          // Immutable by default
mut variable = 100          // Explicit mutability
val typed : i64 = 42        // Explicit type annotation
val undefined : i32 = undef // Uninitialized variable
```

### Functions
```hexen
func name(param : type) : return_type = {
    return expression
}

func void_func() : void = {
    return  // Bare return for void functions
}
```

### Blocks
```hexen
// Expression blocks (must assign value)
val result = {
    val temp = 42
    assign temp * 2        // assign produces block value
}

// Expression blocks with control flow
val validated = {
    val input = get_input()
    if input < 0 {
        return -1          // return exits function early
    }
    assign input * 2       // assign produces block value
}

// Statement blocks (scoped execution)
{
    val scoped = "local"
    mut counter : i32 = 0  // explicit type required for mut
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
- Current: 415/415 tests passing (100% success rate)

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
- Examples in `examples/` demonstrate all language features with learning progression

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

### Variable Declaration Types

#### `val` - Immutable Variables (Values)
- **Single Assignment**: Can only be assigned once at declaration
- **Type inference allowed**: Can omit type annotation when using comptime literals
- **Comptime preservation**: Preserves comptime types for maximum flexibility

```hexen
val message = "Hello, World!"    // ✅ Immutable variable
val flexible = 42 + 100          // comptime_int (preserved - flexible!)
val as_i32 : i32 = flexible      // SAME source → i32
val as_i64 : i64 = flexible      // SAME source → i64
```

#### `mut` - Mutable Variables
- **Multiple assignments**: Can be reassigned as many times as needed
- **Explicit type required**: Must specify type annotation to prevent action-at-a-distance effects
- **Cannot preserve comptime types**: Sacrifice flexibility for safety

```hexen
mut counter : i32 = 0           // ✅ Mutable variable with explicit type
counter = 42                    // ✅ Reassignment allowed
// mut bad_counter = 42         // ❌ Error: mut requires explicit type
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
- **Expression blocks**: Produce values using `assign`, support `return` for function exits
- **Statement blocks**: Execute code with scope isolation, no value production
- **Function bodies**: Unified with other blocks, context provides return type validation

### The `assign` + `return` Dual Capability

Expression blocks support **both** statement types for maximum expressiveness:

#### `assign` - Produces Block Value
```hexen
val computation = {
    val base = 42
    val result = base * 2
    assign result              // Assigns result to computation
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
    assign sanitize(raw_input) // Success: assign sanitized input
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
        assign a / b           // Normal case: assign division result
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
        assign computed        // Cache miss: assign computed value
    }
    
    log_cache_miss(key)        // Only executes on cache miss
    return result
}
```

### Block Types by Context

#### Expression Blocks (Value Production)
- **Must end with**: `assign expression` for value production
- **Control flow**: `return value` for early function exits
- **Scope**: Isolated variables
- **Type**: Determined by `assign` expression type

#### Statement Blocks (Code Execution)
- **No value production**: Cannot use `assign`
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
    assign scaled / 2.0           // comptime_float / comptime_float → comptime_float (preserved!)
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
    assign scaled                 // Preserves comptime_float flexibility
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
        assign input * 2          // Success: assign processed input
    }
    
    // This only executes if validation succeeded
    return validated + 10
}

// 🔴 mut variables cannot preserve expression block comptime types
mut concrete_result : f64 = {
    val calc = 42 + 100 * 3       // Same comptime operations
    assign calc / 2               // comptime_float → f64 (immediately resolved!)
}
// No flexibility preserved - concrete_result is concrete f64

// ✅ Expression blocks with mixed concrete types (explicit conversions)
func mixed_computation() : f64 = {
    val int_val : i32 = 10
    val float_val : f64 = 3.14
    
    val result : f64 = {
        val converted = int_val:f64 + float_val  // Explicit conversion required
        val scaled = converted * 2.5             // f64 * comptime_float → f64
        assign scaled                            // Block assigns concrete f64
    }
    
    return result
}
```

---

# Enhanced Unified Block System Deep Dive

## Core Philosophy: Compile-Time vs Runtime Block Classification

The enhanced unified block system introduces sophisticated **compile-time vs runtime distinction** that determines whether expression blocks can preserve comptime types for maximum flexibility or require explicit context for immediate resolution.

**Key Insight**: Expression blocks fall into two categories based on their contents:
- **Compile-time evaluable**: Preserve comptime types for maximum flexibility (one computation, multiple uses)
- **Runtime evaluable**: Require explicit context due to runtime operations (functions, conditionals, mixed types)

### The Two-Tier Classification System

#### Compile-Time Evaluable Blocks ✨
**Contains only comptime operations** - preserves comptime types for maximum adaptability:

```hexen
// ✨ Compile-time evaluable block preserves comptime types
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

#### Runtime Evaluable Blocks 🔧
**Contains runtime operations** - requires explicit context for immediate resolution:

```hexen
// 🔧 Runtime evaluable block requires explicit context
func get_user_input() : f64 = { return 42.0 }

val runtime_result : f64 = {              // Context REQUIRED! (explicit type annotation)
    val user_input = get_user_input()     // Function call → runtime operation
    val base = 42                         // comptime_int  
    assign base * user_input              // Mixed: comptime + concrete → needs context
}
```

### Runtime Operation Detection

The system automatically detects runtime operations that trigger runtime classification:

#### Function Calls → Runtime Classification
**All function calls return concrete types**, making blocks runtime evaluable:

```hexen
func helper() : i32 = { return 42 }

// Function call detection
val with_function : i32 = {        // Explicit context required
    val result = helper()          // Function call → runtime
    assign result
}
```

#### Conditional Expressions → Runtime Classification  
**All conditionals are runtime per specification**, even with comptime branches:

```hexen
// Conditional detection
val with_conditional : i32 = {     // Explicit context required
    val value = if true {
        assign 42
    } else {
        assign 100
    }                              // Conditional → runtime
    assign value
}
```

#### Mixed Concrete Types → Runtime Classification
**Mixing concrete types** requires explicit conversions and context:

```hexen
// Mixed concrete types
val mixed_block : f64 = {          // Explicit context required
    val a : i32 = 10               // concrete i32
    val b : f64 = 20.0             // concrete f64
    assign a:f64 + b               // Mixed concrete → explicit conversion required
}
```

### Enhanced Error Messages and Validation

The system provides context-specific error messages with actionable guidance:

#### "Context REQUIRED!" Messages
Runtime blocks explain why explicit context is needed:

```hexen
// ❌ Missing explicit context
val problematic = {
    val input = get_input()        // Function call → runtime
    assign input * 2
}
// Error: Context REQUIRED! Runtime block requires explicit type annotation because it 
// contains function calls (functions always return concrete types). 
// Suggestion: val problematic : i32 = { ... }
```

#### Explicit Conversion Guidance
Mixed concrete types get detailed conversion suggestions:

```hexen
// ❌ Mixed concrete types without conversion
val a : i32 = 10
val b : f64 = 20.0
val mixed = a + b
// Error: Mixed concrete types in arithmetic operation '+': i32 incompatible with f64. 
// Transparent costs principle requires explicit conversion. 
// Use explicit conversion syntax: value:f64
```

### Advanced Patterns Enabled

#### One Computation, Multiple Uses Pattern
Compile-time evaluable blocks enable flexible reuse:

```hexen
// Single computation, multiple contexts
val complex_math = {
    val x = 42 + 100               // comptime_int
    val y = 3.14 * 2.0             // comptime_float  
    assign x * y                   // comptime_int * comptime_float → comptime_float
}

// Same computation used in different contexts
val for_graphics : f32 = complex_math      // → f32
val for_physics : f64 = complex_math       // → f64 (higher precision)
val for_indexing : i32 = complex_math:i32  // → i32 (explicit conversion)
```

#### Runtime Optimization with Early Exits
Runtime blocks support performance optimization patterns:

```hexen
func expensive_calc(key: string) : f64 = {
    val result : f64 = {
        val cached = lookup_cache(key)
        if cached != 0.0 {
            return cached          // Early function exit: cache hit
        }
        
        val computed = very_expensive_operation(key)
        save_to_cache(key, computed)
        assign computed            // Cache miss: assign computed value
    }
    
    log_cache_miss(key)            // Only executes on cache miss
    return result
}
```

#### Error Handling with Validation Guards
Expression blocks enable comprehensive validation patterns:

```hexen
func safe_processing(input: f64) : f64 = {
    val validated : f64 = {
        if input < 0.0 {
            return -1.0            // Early function exit: invalid input
        }
        if input > 1000.0 {
            return -2.0            // Early function exit: out of range
        }
        assign sanitize(input)     // Success: assign sanitized value
    }
    
    return validated
}
```

### Integration with Existing Type System

The enhanced block system seamlessly integrates with existing comptime types and `val`/`mut` semantics:

#### `val` + Compile-Time Blocks = Maximum Flexibility
```hexen
val preserved_comptime = {         // No explicit type needed
    val calc = 42 * 3.14          // comptime operations
    assign calc                   // Preserved as comptime_float
}

// Multiple uses with different types
val use1 : f32 = preserved_comptime
val use2 : f64 = preserved_comptime
```

#### `mut` + Runtime Blocks = Immediate Resolution
```hexen
mut immediate_resolution : f64 = { // Explicit type required for mut
    val calc = 42 * 3.14          // Same comptime operations
    assign calc                   // Immediately resolved to f64
}
// No flexibility preserved - immediate_resolution is concrete f64
```

### Specification Compliance

The enhanced unified block system fully complies with:
- **UNIFIED_BLOCK_SYSTEM.md**: Compile-time vs runtime distinction
- **CONDITIONAL_SYSTEM.md**: All conditionals treated as runtime
- **TYPE_SYSTEM.md**: Transparent costs principle with explicit conversions
- **BINARY_OPS.md**: Consistent type resolution across all operations

### Development Guidelines

#### When to Use Compile-Time Blocks
- Pure mathematical computations with comptime literals
- Calculations that might be used in multiple type contexts
- Configuration values that adapt to usage context

#### When to Use Runtime Blocks (with explicit context)
- Any computation involving function calls
- Blocks containing conditional expressions
- Operations mixing concrete types
- Cases where immediate type resolution is desired

#### Best Practices
1. **Let the system guide you**: Error messages provide specific guidance for required annotations
2. **Preserve flexibility when possible**: Use compile-time blocks for reusable computations
3. **Be explicit about costs**: Use type annotations when mixing concrete types
4. **Leverage early returns**: Use `return` for error handling and optimization patterns