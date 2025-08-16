# Hexen Programming Language 🦉

*An experimental journey into what system programming could become when guided by principles rather than precedent.*

## Project Goals

Hexen is not an attempt to create the next mainstream programming language. Instead, it's a deliberate exploration of what's possible when language design is guided by principles rather than compromise:

- **Learn** through experimentation: Discover how design decisions cascade through every layer of a language, from syntax to runtime behavior, by building each piece ourselves

- **Design** with intention: Challenge conventional wisdom by asking "what if?" instead of accepting "that's how it's done"—combining proven concepts in new ways while discarding historical baggage

- **Build** without shortcuts: Create a complete toolchain that embodies our principles, proving that simplicity and power aren't mutually exclusive

- **Document** the journey: Share not just the final result, but the reasoning, experiments, and insights that shaped every decision—creating a resource for future language designers

## Philosophy

Hexen emerges from the belief that the best programming languages are born from deep understanding, not just clever ideas. This project is both a learning laboratory and a design workshop — a place where we can explore fundamental questions about how code should be written, read, and reasoned about.

We reject the notion that complexity is inevitable in system programming. Instead, Hexen is built on the conviction that powerful tools can also be simple, predictable, and enjoyable to use. Every language feature is deliberately chosen and carefully crafted, with the understanding that what we leave out is often as important as what we include.

This is not just an academic exercise, but a practical exploration of what programming could feel like when guided by clear principles rather than historical accidents. Through building Hexen, we document not just the "what" and "how" of language design, but more importantly, the "why" behind every decision.

## Contents

- [Quick Start](#quick-start) — Get up and running with Hexen in minutes
- [Design Principles](#design-principles) — The four core principles guiding every language decision
- [Core Features](#core-features) — Hexen's foundational capabilities and identity
- [Project Architecture](#project-architecture) — Current implementation structure and design
- [Architecture Roadmap](#architecture-roadmap) — Implementation strategy and evolution path

### 📚 Comprehensive Design Documentation
Hexen provides extensive specification documents covering every aspect of the language design philosophy:

#### **Core System Specifications**
- **[TYPE_SYSTEM.md](docs/TYPE_SYSTEM.md)** - Comptime type system with "Ergonomic Literals + Transparent Costs"
- **[UNIFIED_BLOCK_SYSTEM.md](docs/UNIFIED_BLOCK_SYSTEM.md)** - Single syntax, context-driven behavior
- **[BINARY_OPS.md](docs/BINARY_OPS.md)** - Dual division operators with unified type rules
- **[FUNCTION_SYSTEM.md](docs/FUNCTION_SYSTEM.md)** - Complete function system with mutable parameters

#### **Specialized Features**
- **[CONDITIONAL_SYSTEM.md](docs/CONDITIONAL_SYSTEM.md)** - Unified conditional syntax with runtime treatment
- **[LITERAL_OVERFLOW_BEHAVIOR.md](docs/LITERAL_OVERFLOW_BEHAVIOR.md)** - Compile-time safety guarantees

#### **Quick Reference**
- **[COMPTIME_QUICK_REFERENCE.md](docs/COMPTIME_QUICK_REFERENCE.md)** - Essential patterns and mental models ⚡

These documents provide the foundational design philosophy and detailed behavioral specifications that guide Hexen's implementation.

## Quick Start

Ready to try Hexen? Here's how to get started in just a few commands:

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup & First Parse
```bash
# Clone and setup
git clone https://github.com/kiinaq/hexen.git
cd hexen

# Install dependencies
uv sync --extra dev

# Parse and analyze a Hexen program (create a sample file first)
echo 'func main() : i32 = { return 42 }' > hello.hxn
uv run hexen parse hello.hxn
```

**Note**: Hexen source files use the `.hxn` extension.

### Example Hexen Code
```hexen
func main() : i32 = {
    val greeting = "Hello, Hexen!"
    
    // Comptime type adaptation - same literals, different types
    val default_int = 42        // comptime_int (flexible until context forces resolution)
    val explicit_i64 : i64 = 42 // comptime_int → i64 (context-guided)
    val as_float : f32 = 42     // comptime_int → f32 (seamless adaptation)
    val precise : f64 = 3.14    // comptime_float → f64 (implicit)
    val single : f32 = 3.14     // comptime_float → f32 (implicit)
    
    // Unified block system - expression block with dual capability
    val result = {
        val computed = 42 + 100  // comptime_int + comptime_int → comptime_int
        assign computed          // assign: produces block value
    }
    
    // Statement block for scoped execution
    {
        val temp = result        // Scoped variables
        val processed = "done"
        // Variables don't leak outside block
    }
    
    // Dual division operators - transparent costs
    val mathematical = 10 / 3    // Float division → comptime_float 
    val efficient = 10 \ 3       // Integer division → comptime_int
    
    return result  // comptime_int → i32 (return type context)
}

// Function with mutable parameters and early returns
func process_data(input: string, mut counter: i32) : string = {
    counter = counter + 1        // Mutable parameters can be reassigned
    
    // Expression block with validation and early returns  
    val validated = {
        if input == "" {
            return "ERROR"       // return: early function exit
        }
        assign input + "!"       // assign: success path value
    }
    
    return validated
}

// Void function with bare return
func setup() : void = {
    val config = "ready"
    return  // Bare return in void function
}
```

### Run Tests
```bash
# Run the complete test suite
uv run pytest tests/ -v
```

### What's Working
- ✅ **Complete Parser**: Lark-based PEG parser with comprehensive syntax support
- ✅ **Semantic Analyzer**: Full type checking, symbol tables, scope management
- ✅ **Unified Block System**: Expression blocks with dual capability (`assign`/`return`), statement blocks, function bodies
- ✅ **Comptime Type System**: "Ergonomic Literals + Transparent Costs" with `comptime_int`/`comptime_float` adaptation
- ✅ **Complete Type System**: All numeric types (`i32`, `i64`, `f32`, `f64`), `string`, `bool`, `void` with safety guarantees
- ✅ **Function System**: Declarations, calls, parameters, mutable parameters, return type validation
- ✅ **Binary Operations**: Dual division operators (`/` mathematical, `\` integer) with unified type rules  
- ✅ **Variable System**: `val`/`mut` declarations with comptime type preservation and explicit conversion requirements
- ✅ **Conditional System**: Unified `if`/`else` syntax with runtime treatment and expression/statement modes
- ✅ **CLI Interface**: `hexen parse` with JSON AST output and comprehensive error reporting
- ✅ **Comprehensive Testing**: Complete test coverage across parser and semantic analysis
- ✅ **Complete Documentation**: Comprehensive specification documents covering all design decisions

### 📚 Explore Further
- **[Type System →](docs/TYPE_SYSTEM.md)** - Deep dive into comptime types and "Ergonomic Literals + Transparent Costs"
- **[Design Documentation →](#comprehensive-design-documentation)** - Complete specification and philosophy

**Next**: Explore the design principles below to understand Hexen's philosophy! 🦉

## Design Principles

Hexen follows four core design principles that guide every language feature and implementation decision:

### 🎯 Ergonomic
*"Pedantic to write, but really easy to read"*

The language syntax should prioritize clarity and readability over brevity. This manifests in Hexen's **"Ergonomic Literals + Transparent Costs"** philosophy - comptime types make common patterns feel natural (`42` adapts to `i32`, `i64`, `f32`, or `f64` based on context) while all runtime conversion costs remain visible through explicit syntax (`value:type`).

### 🧹 Clean
*"There is only one way to do a thing"*

For any given task, Hexen provides exactly one idiomatic way to accomplish it. This is exemplified by the **unified block system** - all constructs use the same `{}` syntax but adapt their behavior based on context (expression blocks, statement blocks, function bodies). When there's only one syntax to learn, there's no wrong way.

### 🧠 Logic
*"No tricks to remember, only natural approaches"*

Language features build upon each other naturally. Complex concepts emerge from simpler principles: the same type conversion rules apply everywhere (variables, functions, binary operations), and the same `assign`/`return` semantics work consistently across all contexts. Understanding one concept helps you understand related concepts.

### ⚡ Pragmatic
*"Focus on what works better, not on covering everything"*

Hexen chooses features that work exceptionally well together. Rather than trying to be everything to everyone, we deliberately select capabilities like dual division operators (`/` for mathematical precision, `\` for efficient integer division) that solve real problems with transparent costs. Every feature justifies its existence by making programming both safer and more expressive.

## File Extension

Hexen source files use the **`.hxn`** extension, reflecting the language's clean and focused approach to naming conventions.

## Core Features

Hexen's current implementation includes unified language constructs:

### 🎯 Unified Block System with Dual Capability
Every construct uses the same `{ }` block syntax with context-driven behavior:
- **Expression blocks**: Produce values via `assign`, support early function exits via `return`
- **Statement blocks**: Scoped execution without value production, allow function returns  
- **Function bodies**: Unified syntax with return type validation
- **Compile-time vs Runtime**: Expression blocks preserve comptime types when evaluable at compile-time

### 🧠 Comptime Type System with "Ergonomic Literals + Transparent Costs"
- **Comptime adaptation**: `42` adapts to `i32`, `i64`, `f32`, or `f64` based on context (zero runtime cost)
- **No literal suffixes**: Write `42`, not `42i64` - context determines type
- **Flexibility preservation**: `val x = 42` stays flexible (`comptime_int`) until context forces resolution
- **Explicit conversions**: All concrete type mixing requires visible syntax (`value:type`)
- **Complete type system**: `i32`, `i64`, `f32`, `f64`, `string`, `bool`, `void` with safety guarantees
- **Dual division operators**: `/` for mathematical precision, `\` for efficient integer division
- **Variable mutability**: `val` (immutable) vs `mut` (mutable with explicit types)
- **Context propagation**: Function parameters, return types, and assignments provide type context

### 🔒 Memory & Mutability Control
- **Immutable by default**: `val` variables cannot be reassigned
- **Explicit mutability**: `mut` variables require opt-in for reassignment  
- **Scope isolation**: Block variables don't leak to outer scopes
- **Variable shadowing**: Inner scopes can redefine outer variables safely

### 🎨 Expressive Return System
- **Value returns**: `return expression` for returning computed values
- **Bare returns**: `return` for early exit in void functions
- **Context awareness**: Expression blocks require values, statement blocks allow function returns
- **Type validation**: All returns checked against function signatures

### 🛡️ Safety by Design, Unsafety by Choice
Memory safety, type safety, and thread safety are the default—without garbage collection or runtime overhead. Safety is achieved through compile-time analysis and ownership systems, not managed memory. Unsafe operations are possible but require explicit opt-in, making dangerous code visible and intentional.

### 🧩 Incremental Building
The language is designed from the ground up for incremental compilation. Changes to a single file or module trigger rebuilds only of affected dependencies, not the entire project. This enables fast development cycles even for large codebases.

### 📦 Integrated Module System
Dependencies are tracked at the language level, not just at the build level. The module system understands what each piece of code actually needs, enabling precise dependency resolution and better optimization opportunities.

### 🔗 Unified Build System
No external build tools required. The compiler includes everything needed to manage dependencies, perform dynamic linking, and produce optimized binaries or shared libraries. One tool, one command, one clear path from source to executable or library.

## Project Architecture

Hexen follows a clean, modular architecture that separates concerns and enables systematic development. The implementation reflects our design principles through clear component boundaries and well-defined interfaces.

### 🏗️ Compiler Pipeline

```
Source Code (.hxn)     ← Hexen source files with .hxn extension
       ↓
   📝 Parser           ← Syntax analysis, AST generation
       ↓
   🧠 Semantic Analyzer ← Type checking, symbol resolution, scope management
       ↓
   ⚙️ Code Generator    ← LLVM IR emission (future)
       ↓
   🎯 Executable
```

### 📁 Project Structure

```
hexen/
├── src/hexen/              # Core compiler implementation
├── tests/                  # Comprehensive test suite
└── docs/                  # Design documentation & specifications
```

**Detailed documentation**: See [Design Documentation](#comprehensive-design-documentation) below for complete specifications

### 🎯 Current Status

- **Phase I: Language Foundation** ✅ **Complete** - Full parser and semantic analyzer with comprehensive feature set
- **Complete Test Coverage** - All implemented language features validated through extensive testing
- **Comprehensive Documentation** - Complete specification documents covering all design decisions
- **LLVM Ready** - Architecture prepared for LLVM backend integration

*All core language features are implemented and validated through extensive testing and documentation.*

## Architecture Roadmap

Hexen's development follows a pragmatic, evolution-driven approach that prioritizes rapid iteration while building toward long-term goals:

### 🐍 Python-First Implementation
The initial compiler is implemented in Python, enabling rapid prototyping and experimentation with syntax and semantics. Python's expressiveness lets us focus on language design rather than implementation complexity, accelerating the iteration cycle during Hexen's formative phase.

### 🔗 LLVM Backend via llvmlite
We leverage LLVM as our code generation backend through [llvmlite](https://llvmlite.readthedocs.io/en/latest/)—a lightweight Python binding designed specifically for JIT compilers. This approach provides:
- **Pure Python IR construction** for maximum flexibility during development
- **Production-grade optimization** through LLVM's mature toolchain
- **Target independence** across multiple architectures from day one

### 🔄 Bootstrap Evolution Path
The architecture supports natural evolution from prototype to production:

1. **Phase I: Language Foundation** 🚧 — Complete parser, semantic analyzer, unified block system, comptime types
2. **Phase II: Code Generation** — LLVM IR emission and executable generation
3. **Phase III: Self-Hosting** — Hexen compiler written in Hexen, proving the language's capabilities  
4. **Phase IV: Complete Toolchain** — Entire development environment implemented in Hexen

This progression embodies our core principle: build tools that work exceptionally well, then use those tools to build even better tools.

## License

Hexen is released under the [MIT License](LICENSE) by [kiinaq](https://github.com/kiinaq). This permissive license encourages experimentation and learning while ensuring attribution for the project's contributions to the programming language community.

---

*"The best way to understand how something works is to build it yourself."*