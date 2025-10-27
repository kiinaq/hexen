# Hexen Architecture

Hexen follows a clean, modular architecture that separates concerns and enables systematic development. The implementation reflects our design principles through clear component boundaries and well-defined interfaces.

## 🏗️ Compiler Pipeline

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

## 📁 Project Structure

```
hexen/
├── src/hexen/              # Core compiler implementation
├── tests/                  # Comprehensive test suite
└── docs/                  # Design documentation & specifications
```


## 🎯 Current Status

- **Phase I: Language Foundation** 🚧 **In Progress** - Parser and semantic analyzer with core feature set
- **Active Development** - Implementing and refining language features
- **Comprehensive Documentation** - Specification documents guide implementation decisions
- **LLVM Ready** - Architecture designed for future LLVM backend integration

## Architecture Roadmap

Hexen's development follows a pragmatic, evolution-driven approach that prioritizes rapid iteration while building toward long-term goals:

### 🐍 Python-First Implementation
The initial compiler is implemented in Python, enabling rapid prototyping and experimentation with syntax and semantics. Python's expressiveness lets us focus on language design rather than implementation complexity, accelerating the iteration cycle during Hexen's formative phase.

### 🔗 LLVM Backend via llvmlite
We leverage LLVM as our code generation backend through [llvmlite](https://llvmlite.readthedocs.io/en/latest/) - a lightweight Python binding designed specifically for JIT compilers. This approach provides:
- **Pure Python IR construction** for maximum flexibility during development
- **Production-grade optimization** through LLVM's mature toolchain
- **Target independence** across multiple architectures from day one

### 🔄 Bootstrap Evolution Path
The architecture supports natural evolution from prototype to production:

1. **Phase I: Language Foundation** 🚧 **In Progress** - Parser, semantic analyzer, unified block system, comptime types
2. **Phase II: Code Generation** 📋 **Planned** - LLVM IR emission and executable generation
3. **Phase III: Self-Hosting** 📋 **Planned** - Hexen compiler written in Hexen, proving the language's capabilities
4. **Phase IV: Complete Toolchain** 📋 **Planned** - Entire development environment implemented in Hexen

This progression embodies our core principle: build tools that work exceptionally well, then use those tools to build even better tools.
