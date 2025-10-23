# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🎯 Quick Reference

### Development Setup
```bash
# Setup development environment
uv sync --extra dev

# Install dependencies only
uv sync
```

### Testing
```bash
# Run complete test suite
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
│   ├── return_analyzer.py       # Return statement handling
│   ├── block_analyzer.py        # Block analysis
│   ├── function_analyzer.py     # Function analysis
│   └── symbol_table.py          # Scope management
└── cli.py                  # Command-line interface

tests/
├── parser/                 # Parser tests (syntax validation)
└── semantic/               # Semantic tests (type checking, validation)

docs/                       # Detailed language specifications
├── TYPE_SYSTEM.md
├── COMPTIME_QUICK_REFERENCE.md
├── FUNCTION_SYSTEM.md
├── UNIFIED_BLOCK_SYSTEM.md
├── BINARY_OPS.md
├── CONDITIONAL_SYSTEM.md
├── LITERAL_OVERFLOW_BEHAVIOR.md
└── ARRAY_TYPE_SYSTEM.md

examples/                   # Example programs with learning progression
```

### File Naming Conventions
- Hexen source files: `.hxn` extension
- Test files: `test_*.py` pattern
- Documentation: Descriptive names (e.g., `COMPTIME_QUICK_REFERENCE.md`)

---

## 🦉 Hexen Language Essentials

### Core Philosophy

**Ergonomic Literals + Transparent Costs**

Hexen follows two core principles:
1. **Ergonomic Literals**: Comptime types adapt seamlessly to context (zero runtime cost)
2. **Transparent Costs**: All concrete type mixing requires explicit `:type` syntax (costs visible)

### Key Language Features

- **Comptime Type System**: Literals like `42` and `3.14` are comptime types that adapt to context
- **Unified Block System**: All blocks use `{}` syntax with context-appropriate behavior
- **Memory Safety**: Immutable by default (`val`), explicit mutability (`mut`)
- **No Literal Suffixes**: Write `42` not `42i64` - context determines type
- **Size-as-Type Arrays**: Array size is part of the type for compile-time safety

### Type Categories

| Category | Types | Flexibility | When They Exist |
|----------|-------|-------------|-----------------|
| **Comptime Types** | `comptime_int`, `comptime_float`, `comptime_array_int`, `comptime_array_float` | Adapt to any compatible concrete type | Only at compile time |
| **Concrete Types** | `i32`, `i64`, `f32`, `f64`, `bool`, `string`, `[N]T` arrays | Fixed, require explicit conversions | Runtime values |

### Quick Syntax Overview

```hexen
// Variables
val immutable = 42              // Immutable, comptime type preserved
val typed : i64 = 42            // Immutable, explicit type
mut variable : i32 = 100        // Mutable (type required!)

// Functions
func name(param : type) : return_type = {
    return expression
}

// Arrays
val numbers = [1, 2, 3]         // Comptime array (flexible!)
val fixed : [3]i32 = [1, 2, 3]  // Fixed-size concrete array
val inferred : [_]i32 = [1, 2, 3]  // Inferred-size array

// Conditionals (no parentheses, braces required)
if condition {
    do_something()
} else {
    do_other_thing()
}

// Expression blocks
val result = {
    val temp = 42
    -> temp * 2        // -> produces block value
}
```

**For detailed specifications:** See `docs/` directory

---

## 📋 Type System Quick Guide

### The Four Patterns

This is the **core mental model** for all type conversions in Hexen:

| # | Pattern | Conversion | Syntax Example | Cost |
|---|---------|------------|----------------|------|
| 1 | **✨ Comptime + Comptime** | Preserved (flexible) | `val x = 42 + 100` | Zero (compile-time) |
| 2 | **🔄 Comptime + Concrete** | Adapts to concrete | `i32_val + 42` | Zero (adapts seamlessly) |
| 3 | **🔧 Concrete + Concrete (different)** | Explicit required | `i32_val:i64 + i64_val` | Visible (conversion explicit) |
| 4 | **⚡ Same Concrete + Same Concrete** | Identity (no conversion) | `i32_val + i32_val` | Zero (same type) |

**Key Rule:** Only comptime types adapt implicitly. All concrete type mixing requires explicit `:type` syntax.

### Comptime Types Reference

| Comptime Type | Description | Adapts To | Example |
|---------------|-------------|-----------|---------|
| `comptime_int` | Integer literals | `i32`, `i64`, `f32`, `f64` | `42`, `-100`, `1024` |
| `comptime_float` | Float literals or mixed numeric | `f32`, `f64` | `3.14`, `42 + 3.14` (mixed) |
| `comptime_array_int` | Array of integer literals | `[N]i32`, `[N]i64`, `[N]f32`, `[N]f64` | `[1, 2, 3]` |
| `comptime_array_float` | Array of float/mixed literals | `[N]f32`, `[N]f64` | `[3.14, 2.71]`, `[42, 3.14]` |

### Concrete Types Reference

| Type | Range/Size | Use Case |
|------|------------|----------|
| `i32` | -2,147,483,648 to 2,147,483,647 | Default integer |
| `i64` | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | Large integers |
| `f32` | ±3.4028235e+38 (~7 decimal digits) | Graphics, fast math |
| `f64` | ±1.7976931e+308 (~15 decimal digits) | Scientific computing |
| `bool` | `true` or `false` | Boolean logic |
| `string` | Text data | Strings |
| `[N]T` | Fixed-size array of N elements of type T | Arrays with known size |

### When Do I Need `:type` Conversion?

| From Type | To Type | Syntax Required | Example | Notes |
|-----------|---------|-----------------|---------|-------|
| **Comptime → Concrete (Ergonomic)** |
| `comptime_int` | `i32`, `i64`, `f32`, `f64` | ✅ Implicit | `val x : i32 = 42` | No cost, ergonomic |
| `comptime_float` | `f32`, `f64` | ✅ Implicit | `val x : f32 = 3.14` | No cost, ergonomic |
| `comptime_int` | `comptime_int` | ✅ Preserved | `val x = 42` | Stays flexible! |
| **Concrete → Concrete (Explicit)** |
| `i32` | `i64` | 🔧 **Explicit** | `val x : i64 = i32_val:i64` | Conversion cost visible |
| `i64` | `i32` | 🔧 **Explicit** | `val x : i32 = i64_val:i32` | Data loss visible |
| `f32` | `f64` | 🔧 **Explicit** | `val x : f64 = f32_val:f64` | Conversion cost visible |
| `f64` | `f32` | 🔧 **Explicit** | `val x : f32 = f64_val:f32` | Precision loss visible |
| `i32` | `i32` | ⚡ Identity | `val x : i32 = i32_val` | No conversion |

### `val` vs `mut` Type Requirements

| Declaration | Type Annotation | Comptime Preservation | Example |
|-------------|-----------------|----------------------|---------|
| `val` with comptime | Optional | ✅ **YES** (flexible!) | `val x = 42` → stays `comptime_int` |
| `val` with concrete | Optional (explicit type) | No | `val x : i32 = 42` → becomes `i32` |
| `mut` | **Required** (mandatory!) | ❌ **NO** (immediate resolution) | `mut x : i32 = 42` → must specify type |

**Key Rule:** `mut` variables **always require explicit type annotations** and cannot preserve comptime types.

**For detailed type system:** See `docs/TYPE_SYSTEM.md` and `docs/COMPTIME_QUICK_REFERENCE.md`

---

## 🔧 Common Patterns for Code Generation

### Variable Declaration Patterns

| Pattern | Type Required? | Example | Behavior |
|---------|----------------|---------|----------|
| `val` with literal | ❌ No | `val count = 100` | Comptime type preserved (flexible!) |
| `val` with explicit type | ✅ Yes | `val count : i32 = 100` | Forces concrete type |
| `val` with function call | ✅ **YES** | `val result : i32 = get_value()` | Function returns concrete |
| `mut` (always) | ✅ **YES (mandatory)** | `mut counter : i32 = 0` | Type required for safety |

#### Variable Examples

```hexen
// ✅ Comptime preservation (flexible!)
val flexible = 42                    // comptime_int (can adapt later)
val as_i32 : i32 = flexible          // Same source → i32
val as_i64 : i64 = flexible          // Same source → i64 (flexible!)

// ✅ Explicit concrete type
val typed : i32 = 42                 // Immediately i32

// ✅ Mutable variables (type mandatory!)
mut counter : i32 = 0                // Type required
counter = 42                         // Reassignment OK

// ❌ Common mistakes
// mut bad = 42                      // Error: mut requires explicit type
// val result = get_value()          // Error: function call requires type annotation
```

### Function Patterns

#### Function Parameter & Return Types

| Component | Type Annotation | Example | Notes |
|-----------|-----------------|---------|-------|
| Parameters | **Always required** | `func process(input: i32) : i32` | Parameters must be typed |
| Return type | **Always required** | `func get_value() : i32` | Return type must be specified |
| Parameter mutability | Optional (`mut` keyword) | `func modify(mut x: i32) : i32` | Default: immutable |

#### Function Call Patterns

| Context | Type Annotation Required? | Example | Notes |
|---------|---------------------------|---------|-------|
| Argument (literal) | ❌ No | `calculate(42, 3.14)` | Adapts to parameter types |
| Argument (concrete) | Only for conversion | `calculate(i64_val:i32, f64_val:f32)` | Explicit if types differ |
| Return → `val` assignment | ✅ **YES (mandatory)** | `val result : i32 = get_value()` | Always require type |
| Return → `return` statement | ❌ No | `return get_value()` | Function return type provides context |
| Return → function argument | ❌ No | `process(get_value())` | Parameter type provides context |

#### Function Examples

```hexen
// ✅ Function definition
func calculate(x: i32, y: f64) : f64 = {
    return x:f64 * y              // Explicit conversion: i32 → f64
}

// ✅ Function calls with type context
val result : f64 = calculate(42, 3.14)       // Literals adapt to param types
val explicit : f64 = calculate(i32_val, f64_val)  // Same concrete types
val converted : f64 = calculate(i64_val:i32, f32_val:f64)  // Explicit conversions

// ✅ Function return assignments (type always required!)
val value : i32 = get_count()                // Type annotation mandatory
val processed : f64 = calculate(10, 2.5)     // Type annotation mandatory

// ✅ Return statements (no type needed - function type provides context)
func wrapper() : i32 = {
    return get_count()            // OK: function return type provides context
}

// ❌ Common mistakes
// val bad = get_count()          // Error: function call requires type annotation
// func missing(x, y) : i32 = {}  // Error: parameters must have types
```

### Array Patterns

#### Array Creation

| Syntax | Size | Element Type | Example | When to Use |
|--------|------|--------------|---------|-------------|
| Literal only | Inferred | Comptime | `[1, 2, 3]` | Flexible, can adapt |
| `[_]T` | Inferred | Concrete | `val x : [_]i32 = [1, 2, 3]` | Size auto-detected |
| `[N]T` | Fixed | Concrete | `val x : [3]i32 = [1, 2, 3]` | Explicit size |

#### Array Copy Syntax `[..]`

**Critical Rule:** ALL concrete array copying requires explicit `[..]` syntax to make performance costs visible.

| Operation | Syntax Required? | Example | Notes |
|-----------|------------------|---------|-------|
| Comptime → Concrete | ❌ No (first materialization) | `val arr : [_]i32 = [1, 2, 3]` | Comptime adapts (ergonomic!) |
| Concrete → Concrete | ✅ **YES** `[..]` | `val copy : [_]i32 = source[..]` | Explicit copy required |
| Row access for assignment | ✅ **YES** `[..]` | `val row : [_]i32 = matrix[0][..]` | Explicit copy required |
| Flattening (2D → 1D) | ✅ **YES** `[..]:[_]T` | `val flat : [_]i32 = matrix[..]:[_]i32` | Both copy + conversion explicit |

#### Array Examples

```hexen
// ✅ Comptime arrays (flexible!)
val flexible = [1, 2, 3]                     // comptime_array_int
val as_i32 : [_]i32 = flexible               // → [3]i32 (first materialization)
val as_i64 : [_]i64 = flexible               // Same source → [3]i64 (flexible!)

// ✅ Concrete arrays
val numbers : [_]i32 = [10, 20, 30]          // [3]i32
val fixed : [3]i32 = [10, 20, 30]            // [3]i32 with explicit size

// ✅ Array copying (explicit [..] required!)
val source : [_]i32 = [1, 2, 3]
val copy : [_]i32 = source[..]               // Explicit copy

// ✅ Array element access
val elem : i32 = numbers[0]                  // Element type required (concrete array)
val comptime_elem = flexible[0]              // comptime_int (from comptime array)

// ✅ Multidimensional arrays
val matrix : [_][_]i32 = [[1, 2], [3, 4]]    // [2][2]i32
val row : [_]i32 = matrix[0][..]             // Copy row (explicit [..])
val flat : [_]i32 = matrix[..]:[_]i32        // Flatten (explicit [..] + :type)

// ❌ Common mistakes
// val implicit_copy = source                // Error: missing [..] for copy
// val implicit_row = matrix[0]              // Error: missing [..] for row copy
// val implicit_flatten = matrix[..]         // Error: missing :type for dimension change
```

### Expression Block Patterns

#### Type Annotation Requirements

**CRITICAL RULE:** Expression blocks assigned to variables **ALWAYS require explicit type annotations** (just like functions and conditionals).

| Context | Type Annotation Required? | Example |
|---------|---------------------------|---------|
| Assigned to `val` | ✅ **YES (mandatory)** | `val x : i32 = { -> 42 }` |
| Assigned to `mut` | ✅ **YES (mandatory)** | `mut x : i32 = { -> 42 }` |
| Function return | ❌ No | `return { -> 42 }` (function return type provides context) |
| Function argument | ❌ No | `process({ -> 42 })` (parameter type provides context) |

#### Expression Block Examples

```hexen
// ✅ Expression block with explicit type (ALWAYS required for variable assignment!)
val result : i32 = {
    val base = 42                    // comptime_int adapts to i32
    val computed = base * 2          // comptime_int adapts to i32
    -> computed                      // Resolves to i32 (explicit type)
}

// ✅ Expression block with function calls (explicit type required)
val processed : i32 = {
    val input = get_input()          // Function call returns concrete type
    -> input * 2
}

// ✅ Expression block with conditionals (explicit type required)
val conditional_result : i32 = {
    val value : i32 = if true {      // Type REQUIRED (conditional = runtime)!
        -> 42
    } else {
        -> 100
    }
    -> value
}

// ✅ Expression block in function return (no type annotation needed - context provided!)
func calculate() : i32 = {
    return {                         // Function return type provides context
        val temp = 42
        -> temp * 2
    }
}

// ❌ Common mistake: Missing type annotation on variable assignment
// val missing = {                   // ❌ Error: Missing explicit type annotation
//     val temp = 42
//     -> temp * 2
// }
//
// Fix: Add explicit type annotation
// val correct : i32 = {             // ✅ Explicit type annotation required
//     val temp = 42
//     -> temp * 2
// }
```

#### `->` vs `return`

| Statement | Purpose | Scope | Example |
|-----------|---------|-------|---------|
| `->` | Produces block value | Assigns to variable | `val x = { -> 42 }` |
| `return` | Early function exit | Exits containing function | `if error { return -1 }` |

### Binary Operation Patterns

#### Arithmetic Operators

| Operator | Name | Result Type Rule | Example |
|----------|------|------------------|---------|
| `+`, `-`, `*` | Add, subtract, multiply | Follows Four Patterns | `42 + 100`, `i32_val + i32_val` |
| `/` | Float division | Always produces float type | `10 / 3` → `comptime_float` |
| `\` | Integer division | Produces integer type | `10 \ 3` → `comptime_int` |
| `%` | Modulo | Follows Four Patterns | `10 % 3` |

#### Comparison & Logical Operators

| Operator Type | Operators | Result Type | Mixed Concrete? |
|---------------|-----------|-------------|-----------------|
| Comparison | `<`, `>`, `<=`, `>=`, `==`, `!=` | Always `bool` | 🔧 Requires explicit conversion |
| Logical | `&&`, `\|\|`, `!` | Always `bool` | N/A (bool only) |

#### Binary Operation Examples

```hexen
// ✅ Comptime operations (flexible!)
val math = 42 + 100 * 3              // comptime_int (preserved)
val division = 10 / 3                // comptime_float (division produces float)
val int_div = 10 \ 3                 // comptime_int (integer division)

// ✅ Comparison operations
val is_greater = 42 > 30             // bool
val is_equal = 3.14 == 3.14          // bool

// ✅ Mixed concrete types (explicit conversion required)
val a : i32 = 10
val b : i64 = 20
val sum : i64 = a:i64 + b            // Explicit: i32 → i64
val compare = a:i64 < b              // Explicit conversion for comparison

// ❌ Common mistakes
// val bad_mix = a + b               // Error: mixed concrete types require explicit conversion
// val bad_compare = a < b           // Error: comparison also requires explicit conversion
```

### Conditional Patterns

#### Type Annotation Requirements

**CRITICAL RULE:** Conditional expressions are **runtime operations** (just like function calls) and **ALWAYS require explicit type annotations** when assigned to variables.

| Context | Type Annotation Required? | Example | Reason |
|---------|---------------------------|---------|--------|
| Conditional statement | ❌ No | `if cond { do() }` | No value produced |
| Conditional expression | ✅ **YES (mandatory)** | `val x : i32 = if cond { -> 1 } else { -> 2 }` | Runtime operation (like function call) |
| In expression block | ✅ **YES (mandatory)** | `val x : i32 = { val y : i32 = if cond { -> 1 } else { -> 2 }; -> y }` | Each conditional needs type |

#### Syntax Rules

| Feature | Required Syntax | Example |
|---------|----------------|---------|
| Condition | No parentheses | `if value > 0 { }` |
| Braces | Always required | `if cond { } else { }` |
| Condition type | Must be `bool` | `if count > 0 { }` (not `if count { }`) |

#### Conditional Examples

```hexen
// ✅ Conditional statement
if user_input > 0 {
    process_positive()
} else {
    handle_negative()
}

// ✅ Conditional expression (type annotation REQUIRED - runtime operation!)
val result : i32 = if condition {
    -> value1
} else {
    -> value2
}

// ✅ Early return in conditional expression (type REQUIRED - conditional = runtime!)
val validated : i32 = if input < 0 {
    return -1                        // Early function exit
} else {
    -> input * 2                     // Success path
}

// ❌ Common mistakes
// if (condition) { }                // Error: no parentheses around condition
// if count { }                      // Error: i32 cannot be used as bool
// if condition                      // Error: braces required
//     do_something()
```

**For detailed patterns:** See respective documentation in `docs/`

---

## ⚠️ Error Prevention Guide

### Common Mistakes Checklist

#### ❌ Mistake 1: Forgetting Explicit Type Conversions (Concrete Types)

**Problem:**
```hexen
val a : i32 = 10
val b : i64 = 20
val result = a + b              // ❌ Error!
```

**Error:** `Mixed concrete types in arithmetic operation '+': i32 incompatible with i64`

**Fix:**
```hexen
val result : i64 = a:i64 + b    // ✅ Explicit conversion
```

**Rule:** ALL concrete type mixing needs `:type` syntax (Transparent Costs principle)

---

#### ❌ Mistake 2: Missing Array Copy Syntax `[..]`

**Problem:**
```hexen
val source : [_]i32 = [1, 2, 3]
val copy = source               // ❌ Error!
```

**Error:** `Implicit array copying not allowed`

**Fix:**
```hexen
val copy : [_]i32 = source[..]  // ✅ Explicit copy with [..]
```

**Rule:** Array copying always requires `[..]` operator to make performance costs visible

---

#### ❌ Mistake 3: Missing Type Annotation for `mut`

**Problem:**
```hexen
mut counter = 0                 // ❌ Error!
```

**Error:** `mut variables require explicit type annotation`

**Fix:**
```hexen
mut counter : i32 = 0           // ✅ Type required for mut
```

**Rule:** `mut` variables ALWAYS require explicit type annotations (safety requirement)

---

#### ❌ Mistake 4: Missing Type Annotation for Function Returns

**Problem:**
```hexen
val result = get_value()        // ❌ Error!
```

**Error:** `Function call assignments require explicit type annotation`

**Fix:**
```hexen
val result : i32 = get_value()  // ✅ Type required for function returns
```

**Rule:** Function call return values assigned to `val` ALWAYS require explicit type annotations

---

#### ❌ Mistake 5: Missing Type Annotation for Expression Blocks

**Problem:**
```hexen
val block_result = {
    val input = get_user_input()  // Function call
    -> input * 2                  // ❌ Error!
}
```

**Error:** `Expression blocks require explicit type annotation when assigned to variables`

**Fix:**
```hexen
val block_result : i32 = {        // ✅ Explicit type annotation required
    val input = get_user_input()
    -> input * 2
}
```

**Rule:** ALL expression blocks assigned to variables require explicit type annotations (consistent with functions and conditionals)

---

#### ❌ Mistake 6: Missing Type Annotation for Conditional Expressions

**Problem:**
```hexen
val result = if condition {         // ❌ Error!
    -> value1
} else {
    -> value2
}
```

**Error:** `Conditional expressions require explicit type annotation (runtime operation)`

**Fix:**
```hexen
val result : i32 = if condition {   // ✅ Type required (conditional = runtime)
    -> value1
} else {
    -> value2
}
```

**Rule:** Conditional expressions are **runtime operations** (like function calls) and ALWAYS require explicit type annotations

---

#### ❌ Mistake 7: Using Non-Bool in Conditionals

**Problem:**
```hexen
val count : i32 = 5
if count {                      // ❌ Error!
    do_something()
}
```

**Error:** `Condition must be of type bool, got i32`

**Fix:**
```hexen
if count > 0 {                  // ✅ Explicit comparison produces bool
    do_something()
}
```

**Rule:** Conditions must be `bool` type - no implicit conversion from numeric types

---

#### ❌ Mistake 8: Missing Explicit Conversion for Array Flattening

**Problem:**
```hexen
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
val flat = matrix[..]           // ❌ Error!
```

**Error:** `Array dimension change requires explicit type conversion`

**Fix:**
```hexen
val flat : [_]i32 = matrix[..]:[_]i32  // ✅ Both [..] and :type explicit
```

**Rule:** Dimension changes (like 2D → 1D flattening) require BOTH `[..]` (copy) AND `:type` (conversion)

---

#### ❌ Mistake 9: Parentheses Around Conditionals

**Problem:**
```hexen
if (condition) {                // ❌ Error!
    do_something()
}
```

**Error:** `Unexpected token: '(' - conditions should not be wrapped in parentheses`

**Fix:**
```hexen
if condition {                  // ✅ No parentheses
    do_something()
}
```

**Rule:** Hexen conditionals don't use parentheses around conditions

---

#### ❌ Mistake 10: Missing Braces in Conditionals

**Problem:**
```hexen
if condition                    // ❌ Error!
    do_something()
```

**Error:** `Expected '{' after condition`

**Fix:**
```hexen
if condition {                  // ✅ Braces required
    do_something()
}
```

**Rule:** All conditional branches must use `{}` blocks (no single statements)

---

#### ❌ Mistake 11: Incomplete Conditional Expressions

**Problem:**
```hexen
val result : i32 = if condition {
    -> value1
}                               // ❌ Error!
```

**Error:** `All branches in conditional expression must -> a value or return from function`

**Fix:**
```hexen
val result : i32 = if condition {
    -> value1
} else {
    -> value2                   // ✅ All paths covered
}
```

**Rule:** Conditional expressions must have all branches produce values (-> or return)

---

### Quick Decision Trees

#### Do I Need Explicit `:type` Conversion?

```
Is the value a comptime type? (literal, comptime operation)
  ├─ YES → ✅ Implicit conversion OK (ergonomic!)
  └─ NO → Is it a concrete type?
      ├─ YES → Are you mixing with different concrete type?
      │   ├─ YES → 🔧 Explicit :type required (transparent costs!)
      │   └─ NO (same type) → ⚡ No conversion needed (identity)
      └─ NO → Check if it's an array/special case
```

#### Do I Need `[..]` for Arrays?

```
What are you doing with the array?
  ├─ First materialization (comptime → concrete) → ❌ No [..] needed
  ├─ Copying concrete array → ✅ YES, [..] required
  ├─ Accessing element → ❌ No [..] needed (use [index])
  ├─ Copying matrix row → ✅ YES, [..] required
  └─ Flattening array → ✅ YES, both [..] AND :type required
```

#### Does This Expression Block Need Type Annotation?

```
Is the expression block assigned to a variable?
  ├─ YES → ✅ ALWAYS requires explicit type annotation (universal rule!)
  │         Examples:
  │         - val result : i32 = { -> 42 }              ✅ Explicit type required
  │         - val result = { -> 42 }                    ❌ Error!
  │
  └─ NO (used in other contexts) → Check context:
      ├─ Function return → ❌ No annotation (function return type provides context)
      │   Example: return { -> 42 }
      └─ Function argument → ❌ No annotation (parameter type provides context)
          Example: process({ -> 42 })
```

#### Does This Conditional Expression Need Type Annotation?

```
Is it a conditional expression (assigned to a variable)?
  ├─ YES → ✅ ALWAYS requires explicit type annotation (runtime operation!)
  │         Examples:
  │         - val result : i32 = if cond { -> 1 } else { -> 2 }  ✅
  │         - val result = if cond { -> 1 } else { -> 2 }        ❌ Error!
  │
  └─ NO (conditional statement only) → ❌ No type annotation
            Example: if cond { do_something() } else { do_other() }
```

---

## 📚 Deep Dive References

### Documentation Map

For detailed specifications, consult the following documents:

| Topic | Document | Key Sections |
|-------|----------|--------------|
| **Type System Philosophy** | `docs/TYPE_SYSTEM.md` | Core Philosophy, Four Patterns, Conversion Rules |
| **Comptime Type Mental Models** | `docs/COMPTIME_QUICK_REFERENCE.md` | Mental Models, Comptime Propagation |
| **Function Parameters & Returns** | `docs/FUNCTION_SYSTEM.md` | Parameter System, Type Context, Return Annotations |
| **Expression & Statement Blocks** | `docs/UNIFIED_BLOCK_SYSTEM.md` | Block Types, Runtime Detection, -> vs return |
| **Binary Operations (All Types)** | `docs/BINARY_OPS.md` | Type Resolution, Division Operators, Comparisons |
| **Conditionals (if/else)** | `docs/CONDITIONAL_SYSTEM.md` | Syntax, Type Integration, Runtime Treatment |
| **Literal Overflow Safety** | `docs/LITERAL_OVERFLOW_BEHAVIOR.md` | Detection Rules, Type Ranges, Error Messages |
| **Arrays (All Dimensions)** | `docs/ARRAY_TYPE_SYSTEM.md` | Array Syntax, Comptime Arrays, Flattening, Multidimensional |

### When to Consult Which Doc

- **Type conversion questions?** → `TYPE_SYSTEM.md` + `COMPTIME_QUICK_REFERENCE.md`
- **Why does my array operation fail?** → `ARRAY_TYPE_SYSTEM.md` (sections on copy syntax `[..]` and flattening)
- **Binary operation type errors?** → `BINARY_OPS.md` (section on type resolution rules)
- **Expression block type requirements?** → `UNIFIED_BLOCK_SYSTEM.md` (expression block type annotations)
- **Function parameter/return rules?** → `FUNCTION_SYSTEM.md` (parameter context, return annotations)
- **Conditional expression patterns?** → `CONDITIONAL_SYSTEM.md` (conditional expressions, -> vs return)
- **Literal overflow errors?** → `LITERAL_OVERFLOW_BEHAVIOR.md` (type ranges, overflow detection)
- **Adding new array features?** → `ARRAY_TYPE_SYSTEM.md` (comprehensive array specification)

### Cross-Reference Guide

**Comptime Type System:**
- Core concepts: `TYPE_SYSTEM.md`, `COMPTIME_QUICK_REFERENCE.md`
- In binary operations: `BINARY_OPS.md` (comptime propagation)
- In arrays: `ARRAY_TYPE_SYSTEM.md` (comptime arrays)
- In blocks: `UNIFIED_BLOCK_SYSTEM.md` (expression block type requirements)

**Explicit Conversions (`:type`):**
- General rules: `TYPE_SYSTEM.md` (Transparent Costs principle)
- In operations: `BINARY_OPS.md` (mixed concrete types)
- In arrays: `ARRAY_TYPE_SYSTEM.md` (array type conversions, flattening)
- In functions: `FUNCTION_SYSTEM.md` (parameter conversions)

**Type Annotation Requirements:**
- Expression blocks: `UNIFIED_BLOCK_SYSTEM.md` (all expression blocks require explicit types)
- Conditionals: `CONDITIONAL_SYSTEM.md` (all conditionals require explicit types)
- Type resolution: `TYPE_SYSTEM.md` (comptime type adaptation)

---

## 🧪 Testing & Development Guidelines

### Testing Strategy

- **Parser tests** (`tests/parser/`): Validate syntax and AST generation
- **Semantic tests** (`tests/semantic/`): Validate type checking and program semantics
- **Current status**: 1,354/1,354 tests passing (100% success rate)
- All tests use pytest framework

### Code Style

- Use Ruff for formatting and linting (configured in `pyproject.toml`)
- Follow Python 3.12+ type hints throughout
- Maintain clean separation between parser and semantic analysis

### Adding New Language Features

1. **Update grammar** in `src/hexen/hexen.lark`
2. **Add AST nodes** in `src/hexen/ast_nodes.py` (if needed)
3. **Update parser logic** in `src/hexen/parser.py`
4. **Add semantic analysis** in appropriate `src/hexen/semantic/` module
5. **Write comprehensive tests** in both `tests/parser/` and `tests/semantic/`
6. **Update documentation** in `docs/` (detailed specs)
7. **Update CLAUDE.md** (only if common patterns change)

### Debugging Tips

- **Parse issues**: Use `uv run hexen parse <file>` to see AST output
- **Check grammar**: Review rules in `src/hexen/hexen.lark`
- **Validate syntax**: Compare against examples in `examples/`
- **Type errors**: Consult `docs/TYPE_SYSTEM.md` for conversion rules
- **Array issues**: Check `docs/ARRAY_TYPE_SYSTEM.md` for copy/flatten syntax

---

## Important Notes

- **Python-first implementation**: Designed for rapid language design prototyping
- **Future LLVM backend**: Architecture designed for llvmlite backend
- **Focus**: Language design experimentation over performance
- **Documentation**: `docs/` contains authoritative specifications
- **Examples**: `examples/` demonstrates all features with learning progression
- **Architecture**: Traditional two-phase (parser → semantic analyzer)

---

**Last Updated:** 2025-10-19
**Version:** 2.0 (Redesigned for AI-first usage)
