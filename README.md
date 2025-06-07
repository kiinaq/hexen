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

# Parse the example Hexen program
uv run hexen parse examples/hello.hxn
```

### Example Hexen Code
```hexen
func main() -> i32 {
    return 0
}
```

### Run Tests
```bash
# Run the complete test suite
uv run pytest tests/ -v
```

### What's Working
- ✅ **Parser**: Complete Lark-based PEG parser
- ✅ **CLI**: `hexen parse` command with JSON AST output  
- ✅ **Grammar**: Ultra-minimal but extensible syntax
- ✅ **Tests**: Comprehensive validation of language rules
- ✅ **Examples**: Ready-to-run `.hxn` files

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

## Core Features

Hexen's identity is built around four foundational capabilities that work together to create a coherent development experience:

### 🛡️ Safety by Design, Unsafety by Choice
Memory safety, type safety, and thread safety are the default—without garbage collection or runtime overhead. Safety is achieved through compile-time analysis and ownership systems, not managed memory. Unsafe operations are possible but require explicit opt-in, making dangerous code visible and intentional.

### 🧩 Incremental Building
The language is designed from the ground up for incremental compilation. Changes to a single file or module trigger rebuilds only of affected dependencies, not the entire project. This enables fast development cycles even for large codebases.

### 📦 Integrated Module System
Dependencies are tracked at the language level, not just at the build level. The module system understands what each piece of code actually needs, enabling precise dependency resolution and better optimization opportunities.

### 🔗 Unified Build System
No external build tools required. The compiler includes everything needed to manage dependencies, perform dynamic linking, and produce optimized binaries or shared libraries. One tool, one command, one clear path from source to executable or library.

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

1. **Phase I: Python Prototype** — Rapid iteration on language design and core features
2. **Phase II: Self-Hosting** — Hexen compiler written in Hexen, proving the language's capabilities  
3. **Phase III: Complete Toolchain** — Entire development environment implemented in Hexen

This progression embodies our core principle: build tools that work exceptionally well, then use those tools to build even better tools.

## License

Hexen is released under the [MIT License](LICENSE) by [kiinaq](https://github.com/kiinaq). This permissive license encourages experimentation and learning while ensuring attribution for the project's contributions to the programming language community.

---

*"The best way to understand how something works is to build it yourself."*