# Hexen

A laboratory for learning and designing Hexen, a system programming language.

## Project Goals

The primary goal of Hexen is not to create the next mainstream programming language, but to:

- **Learn** by doing: understand language design principles through hands-on experience
- **Design** a system programming language by combining the best ideas
- **Build** a complete compiler toolchain from scratch
- **Document** the entire process to share knowledge and insights

## Philosophy

Hexen emerges from the belief that the best programming languages are born from deep understanding, not just clever ideas. This project is both a learning laboratory and a design workshop — a place where we can explore fundamental questions about how code should be written, read, and reasoned about.

We reject the notion that complexity is inevitable in system programming. Instead, Hexen is built on the conviction that powerful tools can also be simple, predictable, and enjoyable to use. Every language feature is deliberately chosen and carefully crafted, with the understanding that what we leave out is often as important as what we include.

This is not just an academic exercise, but a practical exploration of what programming could feel like when guided by clear principles rather than historical accidents. Through building Hexen, we document not just the "what" and "how" of language design, but more importantly, the "why" behind every decision.

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

---

*"The best way to understand how something works is to build it yourself."*