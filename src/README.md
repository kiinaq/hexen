# Hexen Compiler Source Code 🦉

Complete implementation of the Hexen programming language compiler. This directory contains the core compiler pipeline from source code parsing to semantic analysis, built with Python for rapid prototyping and clear architecture.

## 📊 Source Overview

**Total Implementation**: **1,219 lines** across 4 core modules
- **Semantic Analyzer**: 939 lines - Advanced type checking and program validation
- **Parser**: 197 lines - Syntax analysis and AST generation  
- **CLI**: 75 lines - Command-line interface and user interaction
- **Package Init**: 8 lines - Module organization and metadata

**Language**: Python 3.12+ with modern typing and dataclasses
**Dependencies**: [Lark](https://lark-parser.readthedocs.io/) for PEG parsing, standard library only

## 🏗️ Architecture

The Hexen compiler follows a clean multi-stage pipeline with clear separation of concerns:

```
src/hexen/
├── hexen.lark           # Grammar definition (PEG format, 63 lines)
├── parser.py            # Syntax analysis & AST generation (197 lines)
├── semantic.py          # Type checking & semantic analysis (939 lines)
├── cli.py               # Command-line interface (75 lines)
└── __init__.py          # Package metadata (8 lines)
```

### 🔄 Compiler Pipeline

```
Source Code (.hxn)
       ↓
   📝 Parser (parser.py + hexen.lark)
       ├─ Lark PEG parsing
       ├─ AST transformation
       └─ Syntax validation
       ↓
   🧠 Semantic Analyzer (semantic.py)  
       ├─ Symbol table management
       ├─ Type checking & inference
       ├─ Scope validation
       ├─ Mutability enforcement
       └─ Error collection
       ↓
   🎯 Valid Program (ready for code generation)
```

## 📁 Component Details

### 🔍 Parser (`parser.py` - 197 lines)
*Transforms Hexen source code into structured Abstract Syntax Trees*

**Core Classes:**
- **`HexenTransformer`** - Converts parse tree to clean AST nodes
- **`HexenParser`** - Main parser interface with Lark integration

**Key Features:**
- ✅ **PEG Grammar**: Uses `hexen.lark` for precise syntax definition
- ✅ **AST Generation**: Clean, JSON-serializable Abstract Syntax Trees
- ✅ **Error Recovery**: Helpful syntax error reporting
- ✅ **All Language Features**: Functions, variables, types, blocks, returns, assignments
- ✅ **Comment Handling**: Supports `// comments` without AST pollution

**Public API:**
```python
parser = HexenParser()
ast = parser.parse(source_code)     # Parse from string
ast = parser.parse_file(file_path)  # Parse from file
```

### 🧠 Semantic Analyzer (`semantic.py` - 939 lines)
*Advanced semantic analysis with sophisticated type system and comprehensive validation*

**Core Architecture:**
- **`HexenType`** - Complete type system with Zig-style comptime types
- **`SymbolTable`** - Lexical scoping with symbol tracking
- **`SemanticAnalyzer`** - Main analysis engine with error collection
- **`Symbol`** - Rich variable metadata (type, mutability, initialization)

**Advanced Features:**
- ✅ **Comptime Type System**: `comptime_int` and `comptime_float` with context-dependent coercion
- ✅ **Unified Block Analysis**: Expression blocks, statement blocks, function bodies
- ✅ **Type Safety**: Prevents `val x : bool = 42` while allowing `val x : f32 = 42`
- ✅ **Memory Safety**: Immutable-by-default with explicit mutability (`val` vs `mut`)
- ✅ **Scope Management**: Lexical scoping with variable shadowing
- ✅ **Use-Before-Definition**: Prevents accessing uninitialized variables
- ✅ **Error Recovery**: Collects all errors before stopping (batch reporting)

**Public API:**
```python
analyzer = SemanticAnalyzer()
errors = analyzer.analyze(ast)      # Returns List[SemanticError]
```

### 🎛️ CLI (`cli.py` - 75 lines)
*User-friendly command-line interface for the Hexen compiler*

**Commands:**
- **`hexen parse <file.hxn>`** - Parse source and display AST  
- **`hexen check <file.hxn>`** - Full parsing + semantic analysis

**Features:**
- ✅ **Clear Output**: Emoji-enhanced status messages and error reporting
- ✅ **Error Handling**: Graceful handling of file not found, syntax errors, semantic errors
- ✅ **JSON AST Display**: Pretty-printed Abstract Syntax Trees
- ✅ **Comprehensive Validation**: Shows both syntax and semantic analysis results

**Usage Examples:**
```bash
# Parse and show AST
uv run hexen parse examples/hello_world.hxn

# Full semantic analysis  
uv run hexen check examples/comprehensive_demo.hxn
```

### 📝 Grammar (`hexen.lark` - 63 lines)
*Precise PEG grammar definition for Hexen's unified syntax*

**Grammar Highlights:**
- **Unified Declaration Syntax**: `name : type = value` pattern across all declarations
- **Block-Based Structure**: Consistent `{}` blocks for all contexts
- **Type System**: Complete coverage of `i32`, `i64`, `f32`, `f64`, `string`, `bool`, `void`
- **Comments**: Built-in `//` comment support with whitespace ignoring
- **Assignment**: Separate assignment syntax (`target = value`)

## 🎯 Key Technical Achievements

### Zig-Inspired Comptime Types
```python
# Elegant type coercion without literal suffixes
val default_int = 42        # comptime_int → i32 (default)
val explicit_i64 : i64 = 42 # comptime_int → i64 (coerced)  
val as_float : f32 = 42     # comptime_int → f32 (coerced)
val precise : f64 = 3.14    # comptime_float → f64 (default)
```

### Unified Block System
```python
# Same {} syntax, context-aware validation
func compute() : i32 = {                    # Function body
    val result = {                          # Expression block  
        val temp = 42
        return temp                         # Required final return
    }
    {                                       # Statement block
        val debug = "processing"            # Scoped execution
    }
    return result                           # Function return
}
```

### Advanced Error Recovery
```python
# Multiple errors detected in single pass
errors = [
    "Undefined variable: 'unknown'",
    "Type mismatch: expected bool, got comptime_int", 
    "Cannot assign to immutable variable 'x'",
    "Return type mismatch: expected i32, got string"
]
```

## 🔧 Development Standards

### Code Quality
- **Type Hints**: Complete Python typing for IDE support and correctness
- **Documentation**: Comprehensive docstrings explaining design decisions
- **Error Handling**: Robust error collection and user-friendly messages
- **Separation of Concerns**: Clear boundaries between parsing and semantic analysis

### Design Principles
- **🎯 Ergonomic**: Clear error messages and intuitive API design
- **🧹 Clean**: Single responsibility for each component
- **🧠 Logical**: Features build upon each other naturally
- **⚡ Pragmatic**: Focus on what works best, not covering everything

### Performance Characteristics
- **Fast Parsing**: PEG parsing with Lark optimization
- **Efficient Analysis**: Single-pass semantic analysis with symbol tables
- **Memory Efficient**: Minimal AST overhead, garbage-collected Python
- **Scalable Architecture**: Clean interfaces ready for LLVM backend integration

## 🚀 Usage Examples

### Basic Parsing
```python
from src.hexen.parser import HexenParser

parser = HexenParser()
ast = parser.parse('''
    func main() : i32 = {
        val x = 42
        return x
    }
''')
```

### Full Semantic Analysis
```python
from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer

# Parse source code
parser = HexenParser()
ast = parser.parse_file("program.hxn")

# Analyze semantics
analyzer = SemanticAnalyzer() 
errors = analyzer.analyze(ast)

if errors:
    for error in errors:
        print(f"Error: {error.message}")
else:
    print("Program is semantically valid!")
```

### Command-Line Usage
```bash
# Install and run
uv sync
uv run hexen parse examples/hello_world.hxn
uv run hexen check examples/comprehensive_demo.hxn

# Development workflow
uv run pytest tests/           # Run all tests
uv run hexen check myfile.hxn  # Validate your code
```

## 🔮 Future Architecture

### Phase II: Code Generation
- **LLVM Backend**: Integration with `llvmlite` for IR generation
- **Optimization**: LLVM optimization passes for performance
- **Target Support**: Cross-compilation to multiple architectures

### Phase III: Self-Hosting
- **Hexen-in-Hexen**: Compiler written in Hexen itself
- **Bootstrap Process**: Gradual migration from Python implementation
- **Native Performance**: Compiled Hexen compiler for production use

### Phase IV: Complete Toolchain
- **Language Server**: IDE support with autocomplete and error highlighting
- **Debugger Integration**: Source-level debugging support
- **Package Manager**: Dependency management and distribution

## 🛡️ Quality Assurance

### Testing Integration
- **164 comprehensive tests** validate every compiler component
- **Parser tests** ensure correct AST generation for all syntax
- **Semantic tests** validate type checking and error detection
- **Integration tests** verify complete pipeline functionality

### Error Handling Philosophy
- **User-Friendly**: Clear, actionable error messages
- **Comprehensive**: Multiple error detection in single pass  
- **Context-Aware**: Error messages include relevant source context
- **Recovery-Oriented**: Analysis continues after errors when possible

### Documentation Standards
- **Design Rationale**: Every major decision documented with reasoning
- **API Documentation**: Complete function and class documentation
- **Usage Examples**: Practical examples for all major features
- **Architecture Decisions**: Clear explanation of design tradeoffs

---

**Implementation Status**: ✅ **Phase I In Progress** | **Ready for Phase II** | **Production-Quality Foundation**

*The Hexen compiler implements a sophisticated, well-architected foundation ready for code generation and self-hosting evolution.* 🦉 