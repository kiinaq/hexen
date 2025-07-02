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
// Expression blocks (must return value)
val result = {
    val temp = 42
    return temp * 2
}

// Statement blocks (scoped execution)
{
    val scoped = "local"
    mut counter = 0
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