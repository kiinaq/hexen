# Hexen Programming Language 🦉

*An experimental journey into what system programming could become when guided by principles rather than precedent.*

## Project Goals

Hexen is not an attempt to create the next mainstream programming language. Instead, it's a deliberate exploration of what's possible when language design is guided by principles rather than compromise:

- **Learn** through experimentation: Discover how design decisions cascade through every layer of a language, from syntax to runtime behavior, by building each piece ourselves

- **Design** with intention: Challenge conventional wisdom by asking "what if?" instead of accepting "that's how it's done"-combining proven concepts in new ways while discarding historical baggage

- **Build** without shortcuts: Create a complete toolchain that embodies our principles, proving that simplicity and power aren't mutually exclusive

- **Document** the journey: Share not just the final result, but the reasoning, experiments, and insights that shaped every decision-creating a resource for future language designers

## Philosophy

Hexen emerges from the belief that the best programming languages are born from deep understanding, not just clever ideas. This project is both a learning laboratory and a design workshop - a place where we can explore fundamental questions about how code should be written, read, and reasoned about.

We reject the notion that complexity is inevitable in system programming. Instead, Hexen is built on the conviction that powerful tools can also be simple, predictable, and enjoyable to use. Every language feature is deliberately chosen and carefully crafted, with the understanding that what we leave out is often as important as what we include.

This is not just an academic exercise, but a practical exploration of what programming could feel like when guided by clear principles rather than historical accidents. Through building Hexen, we document not just the "what" and "how" of language design, but more importantly, the "why" behind every decision.

## Contents

- [Quick Start](#quick-start) - Get up and running with Hexen in minutes
- [Design Principles](#design-principles) - The four core principles guiding every language decision

### 📚 Documentation

Hexen provides comprehensive specification documents covering language design and implementation:

#### **Core Language Systems**
- **[TYPE_SYSTEM.md](docs/TYPE_SYSTEM.md)** - Comptime type system with "Ergonomic Literals + Transparent Costs"
- **[UNIFIED_BLOCK_SYSTEM.md](docs/UNIFIED_BLOCK_SYSTEM.md)** - Single syntax, context-driven behavior
- **[FUNCTION_SYSTEM.md](docs/FUNCTION_SYSTEM.md)** - Parameters, returns, and mutable parameters

#### **Type-Specific Features**
- **[ARRAY_TYPE_SYSTEM.md](docs/ARRAY_TYPE_SYSTEM.md)** - Array syntax, slicing, and multidimensional arrays
- **[RANGE_SYSTEM.md](docs/RANGE_SYSTEM.md)** - Range syntax, materialization, and array slicing

#### **Operations & Control Flow**
- **[BINARY_OPS.md](docs/BINARY_OPS.md)** - Dual division operators with unified type rules
- **[CONDITIONAL_SYSTEM.md](docs/CONDITIONAL_SYSTEM.md)** - Unified if/else syntax with runtime treatment

#### **Safety & Validation**
- **[LITERAL_OVERFLOW_BEHAVIOR.md](docs/LITERAL_OVERFLOW_BEHAVIOR.md)** - Compile-time overflow detection

#### **Quick Reference & Implementation**
- **[COMPTIME_QUICK_REFERENCE.md](docs/COMPTIME_QUICK_REFERENCE.md)** - Essential patterns and mental models ⚡
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Compiler pipeline, project structure, and roadmap

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

### Run Tests
```bash
# Run the complete test suite
uv run pytest tests/ -v
```

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

Language features build upon each other naturally. Complex concepts emerge from simpler principles: the same type conversion rules apply everywhere (variables, functions, binary operations), and the same `->`/`return` semantics work consistently across all contexts. Understanding one concept helps you understand related concepts.

### ⚡ Pragmatic
*"Focus on what works better, not on covering everything"*

Hexen chooses features that work exceptionally well together. Rather than trying to be everything to everyone, we deliberately select capabilities like dual division operators (`/` for mathematical precision, `\` for efficient integer division) that solve real problems with transparent costs. Every feature justifies its existence by making programming both safer and more expressive.

## File Extension

Hexen source files use the **`.hxn`** extension, reflecting the language's clean and focused approach to naming conventions.

---

**📖 For compiler architecture, and development roadmap, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).**

---

## License

Hexen is released under the [MIT License](LICENSE) by [kiinaq](https://github.com/kiinaq). This permissive license encourages experimentation and learning while ensuring attribution for the project's contributions to the programming language community.

---

*"The best way to understand how something works is to build it yourself."*