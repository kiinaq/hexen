# Hexen Compiler Source Code 🦉

Complete implementation of the Hexen programming language compiler. This directory contains a sophisticated compiler pipeline from source code parsing to comprehensive semantic analysis, built with Python for rapid prototyping while maintaining production-quality architecture.

## 📊 Implementation Overview

**Total Implementation**: **3,028 lines** across 16 specialized components  
**Language**: Python 3.12+ with complete typing and modern architecture  
**Dependencies**: [Lark](https://lark-parser.readthedocs.io/) for PEG parsing, standard library only  
**Test Coverage**: 415 comprehensive tests validating all language features

### **Core Components**
- **🔍 Parser**: 356 lines - Syntax analysis with clean AST generation
- **🧠 Semantic Analysis**: 2,580+ lines - Advanced modular semantic analysis system
- **🎛️ CLI Interface**: 75 lines - User-friendly command-line tools
- **📝 Grammar**: 76 lines - Precise PEG grammar definition
- **🏗️ Supporting Infrastructure**: 73+ lines - AST nodes, package organization

## 🏗️ Sophisticated Architecture

Hexen implements a **production-quality compiler architecture** with advanced language features:

```
src/hexen/
├── hexen.lark              # ─┐ Syntax Analysis (432 lines)
├── parser.py               #  ├─ PEG grammar + AST generation
├── ast_nodes.py            # ─┘ Clean AST node definitions
├── semantic/               # ─┐ Advanced Semantic Analysis (2,580+ lines)
│   ├── analyzer.py         #  ├─ Main semantic orchestrator (262 lines)
│   ├── expression_analyzer.py    # ├─ Expression & type annotation analysis (210 lines)
│   ├── binary_ops_analyzer.py    # ├─ Binary operations with dual division (376 lines)
│   ├── declaration_analyzer.py   # ├─ Unified declaration framework (344 lines)
│   ├── assignment_analyzer.py    # ├─ Context-guided assignments (235 lines)
│   ├── return_analyzer.py        # ├─ Return statement validation (196 lines)
│   ├── block_analyzer.py         # ├─ Unified block system (186 lines)
│   ├── unary_ops_analyzer.py     # ├─ Unary operations (102 lines)
│   ├── type_util.py        #  ├─ Advanced type system utilities (371 lines)
│   ├── symbol_table.py     #  ├─ Lexical scoping & symbol management (130 lines)
│   ├── types.py            #  ├─ Comptime type system (65 lines)
│   ├── errors.py           #  ├─ Structured error reporting (29 lines)
│   └── __init__.py         # ─┘ Clean public API (32 lines)
├── cli.py                  # ─── Command-line interface (75 lines)
└── __init__.py             # ─── Package metadata (12 lines)
```

## 🎯 Advanced Language Features Implemented

### **🧩 Comptime Type System** (TYPE_SYSTEM.md)
*Zig-inspired compile-time type adaptation without literal suffixes*

```hexen
// Smart literal adaptation based on context
val default_int = 42        // comptime_int → i32 (system default)  
val explicit_i64 : i64 = 42 // comptime_int → i64 (context-guided)
val as_float : f32 = 42     // comptime_int → f32 (safe conversion)
val precise : f64 = 3.14    // comptime_float → f64 (precision default)

// "Explicit Danger, Implicit Safety" - precision loss requires acknowledgment
val truncated : i32 = large_value : i32  // Explicit truncation
```

**Implementation**: 371 lines of sophisticated type coercion logic with context-guided resolution

### **⚡ Dual Division Operators** (BINARY_OPS.md)  
*Transparent cost model with clear computational semantics*

```hexen
// Two division operators for clarity and performance
val precise = 10 / 3        // Float division → 3.333... (mathematical)
val efficient = 10 \ 3      // Integer division → 3 (truncated, efficient)

// Context-guided mixed-type resolution
val result : f64 = int_val + float_val  // Context resolves type ambiguity
```

**Implementation**: 376 lines handling complex binary operations with operator-specific semantics

### **🏗️ Unified Block System** (UNIFIED_BLOCK_SYSTEM.md)
*Single syntax, context-driven behavior for all code blocks*

```hexen
func complex_computation() : i32 = {     // Function body block
    val result = {                       // Expression block (returns value)
        val temp = expensive_calc()
        return temp * 2                  // Required return for value production
    }
    
    {                                    // Statement block (scoped execution)
        val debug = "Processing..."      // Variables scoped to block
        log_info(debug)
    }
    
    return result                        // Function return
}
```

**Implementation**: 186 lines of context-aware block analysis with unified scope management

### **🔒 Advanced Type Safety** (COMPARISON_OPS.md)
*Compile-time prevention of type-related runtime errors*

```hexen
// Strict comparison rules - only identical types can be compared
val a : i32 = 10
val b : i64 = 20
// val invalid = a < b              // ❌ Compile error: mixed types
val valid = a < (b : i32)           // ✅ Explicit conversion required

// Memory safety with immutable-by-default variables
val immutable = 42                  // Cannot be reassigned
mut counter : i32 = 0               // Explicit mutability declaration
counter = 100                       // ✅ Allowed: explicit mut
```

**Implementation**: Comprehensive type checking across 210 lines of expression analysis

### **🎨 Sophisticated Error Recovery**
*Production-quality error reporting with batch collection*

```hexen
// Multiple errors detected in single compilation pass
// Error: Undefined variable: 'unknown_var'
// Error: Type mismatch: expected bool, got comptime_int  
// Error: Cannot assign to immutable variable 'config'
// Error: Mixed-type operation 'i32 + f64' requires explicit result type annotation
```

**Implementation**: 29 lines of structured error handling with comprehensive context

## 🔧 Modular Semantic Analysis System

The semantic analyzer is **architecturally sophisticated** with clean separation of concerns:

### **🎯 Specialized Analyzer Components**

| Analyzer | Responsibility | Lines | Key Features |
|----------|---------------|--------|--------------|
| **Main Analyzer** | Orchestration & error collection | 262 | Pure coordination logic |
| **Expression Analyzer** | Type annotations & identifiers | 210 | "Explicit Danger, Implicit Safety" |
| **Binary Ops Analyzer** | Arithmetic & dual division | 376 | Context-guided resolution |
| **Declaration Analyzer** | Functions, val, mut declarations | 344 | Unified declaration framework |
| **Assignment Analyzer** | Variable assignments | 235 | Context-aware type validation |
| **Return Analyzer** | Return statement validation | 196 | Context-specific rules |
| **Block Analyzer** | Unified block system | 186 | Expression vs statement blocks |
| **Unary Ops Analyzer** | Unary operations | 102 | Negative literals, logical NOT |

### **🔄 Callback-Based Architecture**
Clean dependency injection enables focused testing and maintainability:

```python
# Each analyzer receives only the callbacks it needs
expression_analyzer = ExpressionAnalyzer(
    error_callback=self._error,
    analyze_block_callback=self._analyze_block,
    lookup_symbol_callback=self.symbol_table.lookup_symbol,
)
```

## 📝 Grammar and Parsing

### **Unified Syntax Philosophy**
```lark
// Single declaration pattern: name : type = value
val_declaration: VAL IDENTIFIER ":" type "=" (expression | "undef")
mut_declaration: MUT IDENTIFIER ":" type "=" (expression | "undef")  
function: "func" IDENTIFIER "(" ")" ":" type "=" block

// Dual division operators in grammar
MUL_OP: "*" | "/" | "\\" | "%"  // / = float, \ = integer

// Expression blocks with type annotations
expression: logical_or (":" type)?  // Type annotation support
```

**Features**:
- ✅ **Dual Division**: `/` (float) and `\` (integer) operators
- ✅ **Type Annotations**: `expression : type` for precision loss acknowledgment  
- ✅ **Unified Blocks**: Same `{}` syntax for all contexts
- ✅ **Mutability Keywords**: `val` (immutable) vs `mut` (mutable)
- ✅ **Comment Support**: `//` comments with proper whitespace handling

## 🧪 Comprehensive Testing

### **Test Coverage: 415 Tests Across 28 Test Files**

**Test Categories**:
- **Parser Tests**: Syntax validation and AST generation
- **Type System Tests**: Comptime types, coercion, precision loss
- **Binary Operations**: Dual division, mixed types, context resolution
- **Comparison Operations**: Type safety, boolean semantics
- **Unified Blocks**: Expression blocks, statement blocks, scoping
- **Mutability**: val vs mut semantics, reassignment validation
- **Error Handling**: Comprehensive error message validation
- **Integration**: End-to-end compiler pipeline validation

**Quality Assurance**:
- 🎯 **Specification Compliance**: Tests validate implementation against design documents
- 🔧 **Regression Protection**: Comprehensive coverage prevents breaking changes
- 📋 **Error Message Quality**: Tests ensure helpful, actionable error messages
- 🧪 **Modular Testing**: Each analyzer component tested independently

## 🚀 Usage Examples

### **Command-Line Interface**
```bash
# Install and run
uv sync                                    # Install dependencies
uv run hexen parse examples/hello_world.hxn    # Parse and show AST
uv run hexen check examples/comprehensive_demo.hxn  # Full semantic analysis

# Development workflow  
uv run pytest tests/                      # Run 415 comprehensive tests
uv run hexen check myfile.hxn             # Validate Hexen source code
```

### **Programmatic API**
```python
from src.hexen.parser import HexenParser  
from src.hexen.semantic import SemanticAnalyzer

# Complete compilation pipeline
parser = HexenParser()
analyzer = SemanticAnalyzer()

# Parse source to AST
ast = parser.parse_file("program.hxn")

# Advanced semantic analysis  
errors = analyzer.analyze(ast)

if not errors:
    print("✅ Program is semantically valid!")
else:
    for error in errors:
        print(f"❌ {error.message}")
```

## 🎖️ Technical Achievements

### **Language Design Excellence**
- **🧠 Comptime Types**: Eliminates literal suffixes while maintaining type safety
- **⚡ Dual Division**: Transparent cost model with `/` (float) vs `\` (integer)  
- **🏗️ Unified Blocks**: Single syntax adapts to context (expression/statement/function)
- **🔒 Memory Safety**: Immutable-by-default with explicit mutability (`val` vs `mut`)
- **🎯 Precision Control**: Type annotations for explicit precision loss acknowledgment

### **Compiler Architecture Excellence**  
- **🧩 Modular Design**: 8 specialized analyzers with clean separation of concerns
- **🔄 Callback Architecture**: Dependency injection enables focused testing
- **🛡️ Error Recovery**: Batch error collection with comprehensive context
- **📊 Comprehensive Testing**: 415 tests validating all language features
- **🎨 Clean APIs**: Well-designed interfaces for external integration

### **Implementation Quality**
- **📋 Complete Typing**: Full Python type hints for IDE support and correctness
- **📚 Comprehensive Documentation**: Detailed docstrings explaining design decisions  
- **🧪 Test-Driven Development**: Specification compliance validated through testing
- **🔧 Maintainable Code**: Clear responsibilities and minimal coupling
- **⚡ Performance-Conscious**: Efficient algorithms with minimal memory overhead

## 🎯 Specification Compliance

Hexen's implementation closely follows its comprehensive specification documents:

- **✅ TYPE_SYSTEM.md**: Complete comptime type system with context-guided resolution
- **✅ BINARY_OPS.md**: Dual division operators with transparent cost model  
- **✅ UNIFIED_BLOCK_SYSTEM.md**: Context-driven block behavior with unified syntax
- **✅ COMPARISON_OPS.md**: Type-safe comparisons with strict boolean semantics

**Implementation Status**: **Phase I Complete** - Sophisticated semantic analysis ready for code generation

## 🔮 Architecture Readiness

### **Phase II: Code Generation** (Ready)
- **Clean AST**: Well-structured for LLVM IR generation
- **Complete Type Information**: Full type resolution for code generation
- **Symbol Tables**: Ready for variable allocation and scoping
- **Error-Free Validation**: Semantically validated programs guaranteed

### **Phase III: Self-Hosting** (Foundation Ready)
- **Robust Parser**: Production-quality syntax analysis
- **Advanced Type System**: Sophisticated type safety and inference
- **Modular Architecture**: Clean interfaces for gradual rewriting
- **Comprehensive Testing**: Regression protection during migration

---

**Current Status**: ✅ **Production-Quality Semantic Analysis** | **Ready for Code Generation** | **Sophisticated Foundation Complete**

*Hexen demonstrates that a language can be both sophisticated in design and elegant in implementation, providing advanced features through clean, well-architected code.* 🦉 