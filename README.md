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

# Parse and analyze a Hexen program
uv run hexen parse examples/hello.hxn
```

**Note**: Hexen source files use the `.hxn` extension.

### Example Hexen Code
```hexen
func main() : i32 = {
    val greeting = "Hello, Hexen!"
    val result = {
        val computed = 42
        return computed
    }
    
    // Void function with early exit
    func setup() : void = {
        val config = "ready"
        return  // Bare return in void function
    }
    
    // Statement block for scoped computation
    {
        val temp = result
        val processed = "done"
    }
    
    return result
}
```

### Run Tests
```bash
# Run the complete test suite (92 comprehensive tests)
uv run pytest tests/ -v
```

### What's Working
- ✅ **Complete Parser**: Lark-based PEG parser with sophisticated syntax support
- ✅ **Semantic Analyzer**: Full type checking, symbol tables, scope management
- ✅ **Unified Block System**: Expression blocks, statement blocks, and void functions  
- ✅ **Type System**: i32, i64, f64, string, void with inference and explicit annotations
- ✅ **Variable System**: `val`/`mut` declarations with `undef` support
- ✅ **Return Statements**: Both value returns and bare returns (`return;`)
- ✅ **CLI Interface**: `hexen parse` with JSON AST output and error reporting
- ✅ **Comprehensive Tests**: 92 tests covering all language features
- ✅ **Error Handling**: Detailed semantic error reporting with context

**Next**: Explore the design principles below to understand Hexen's philosophy! 🦉

## Design Principles

Hexen follows four core design principles that guide every language feature and implementation decision:

### 🎯 Ergonomic
*"Pedantic to write, but really easy to read"*

The language syntax should prioritize clarity and readability over brevity. While it may require more explicit code when writing, the result should be immediately understandable to anyone reading it. Code is read far more often than it's written, so we optimize for the reader's experience.

### 🧹 Clean
*"There is only one way to do a thing"*

For any given task, Hexen provides exactly one idiomatic way to accomplish it. This eliminates choice paralysis, reduces cognitive load, and ensures consistency across codebases. When there's only one way, there's no wrong way.

### 🧠 Logic
*"No tricks to remember, only natural approaches"*

Language features should build upon each other naturally and logically. Complex concepts should emerge from the combination of simpler, more general principles rather than being special cases or syntactic sugar. Understanding one concept should help you understand related concepts.

### ⚡ Pragmatic
*"Focus on what works better, not on covering everything"*

Hexen chooses only the features that matter most for achieving results. Rather than trying to be everything to everyone, we deliberately select a focused set of capabilities that work exceptionally well together. Every feature must justify its existence by solving real problems effectively.

## File Extension

Hexen source files use the **`.hxn`** extension, reflecting the language's clean and focused approach to naming conventions.

## Core Features

Hexen's current implementation showcases a sophisticated foundation built around unified, powerful language constructs:

### 🎯 Unified Block System
Every construct uses the same `{ }` block syntax but with context-appropriate behavior:
- **Expression blocks**: `val x = { return 42 }` - produce values, require final return
- **Statement blocks**: `{ val temp = 100 }` - scoped execution, allow function returns  
- **Function bodies**: Same syntax, unified scope management
- **Void functions**: `func work() : void = { return }` - support bare returns

### 🧠 Intelligent Type System  
- **Type inference**: `val x = 42` automatically becomes `i32`
- **Explicit annotations**: `val x : i64 = 42` for precise control
- **Multiple types**: `i32`, `i64`, `f64`, `string`, `void` with seamless interop
- **`undef` support**: `val x : i32 = undef` for uninitialized variables
- **Comprehensive validation**: Use-before-definition prevention, type mismatch detection

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
│   ├── parser.py          # Lark-based PEG parser + AST transformer
│   ├── semantic.py        # Type checking & semantic analysis
│   ├── hexen.lark         # Grammar definition (PEG format)
│   └── cli.py             # Command-line interface
├── tests/                  # Comprehensive test suite
│   ├── parser/            # Parser & syntax tests (34 tests)
│   └── semantic/          # Semantic analysis tests (58 tests)
│       ├── test_semantic.py        # Core semantic features
│       ├── test_expression_blocks.py # Expression block system
│       ├── test_statement_blocks.py  # Statement block system  
│       └── test_bare_returns.py     # Bare return statements
├── examples/              # Sample Hexen programs
└── docs/                  # Documentation & design notes
```

### 🔧 Component Responsibilities

**Parser (`parser.py`)**
- Converts source code to Abstract Syntax Tree (AST)
- Handles syntax validation and error reporting
- Transforms grammar rules into structured data
- Supports unified block syntax and bare returns
- **Input**: Hexen source code  
- **Output**: JSON-serializable AST

**Semantic Analyzer (`semantic.py`)**
- Validates program semantics and type correctness
- Manages symbol tables and scope resolution
- Enforces mutability rules (`val` vs `mut`)
- Implements unified block system with context-aware validation
- Handles type inference and explicit type annotations
- Detects use-before-definition and type mismatch errors
- Validates return statements against function signatures
- **Input**: Parser AST  
- **Output**: Validated AST + comprehensive error reports

**Grammar (`hexen.lark`)**
- Defines Hexen's syntax using PEG (Parsing Expression Grammar)
- Specifies tokens, rules, and precedence
- Supports unified block syntax across all constructs
- Enables bare return statements (`return` without expression)
- **Current scope**: Functions, variables, types, unified blocks, return statements

### 🧪 Testing Strategy

**Parser Tests** (`tests/parser/` - 34 tests)**
- Syntax validation and AST structure verification
- Error handling for invalid syntax
- Whitespace and edge case handling
- Variable declarations, type annotations, `undef` support
- Function definitions and multiple function support

**Semantic Tests** (`tests/semantic/` - 58 tests)**
- **Core Semantics** (10 tests): Type inference, symbol tables, basic validation
- **Expression Blocks** (10 tests): Value-producing blocks with return requirements
- **Statement Blocks** (18 tests): Scoped execution blocks with function returns
- **Bare Returns** (14 tests): Return statements without expressions
- **Error Cases** (6 tests): Comprehensive error detection and reporting

**Test Results**: 92/92 passing ✅ - Complete validation from syntax to semantics

### 🎯 Architecture Benefits

**Unified Design**: Single block syntax works across all language constructs
**Comprehensive Validation**: Full semantic analysis with detailed error reporting  
**Separation of Concerns**: Clear boundaries between parsing and semantic analysis
**Testability**: Independent validation of each language feature
**Extensibility**: Clean architecture supports rapid feature development
**Type Safety**: Complete type checking with inference and explicit annotations
**Scope Safety**: Proper variable scoping with shadowing and isolation

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

1. **Phase I: Language Foundation** ✅ — Complete parser, semantic analyzer, unified block system
2. **Phase II: Code Generation** — LLVM IR emission and executable generation
3. **Phase III: Self-Hosting** — Hexen compiler written in Hexen, proving the language's capabilities  
4. **Phase IV: Complete Toolchain** — Entire development environment implemented in Hexen

This progression embodies our core principle: build tools that work exceptionally well, then use those tools to build even better tools.

## License

Hexen is released under the [MIT License](LICENSE) by [kiinaq](https://github.com/kiinaq). This permissive license encourages experimentation and learning while ensuring attribution for the project's contributions to the programming language community.

---

*"The best way to understand how something works is to build it yourself."*