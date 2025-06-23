# Hexen Test Suite 🧪

Comprehensive test coverage for the Hexen programming language compiler. This test suite validates every aspect of Hexen from syntax parsing to semantic analysis, ensuring language correctness and reliability.

## 📊 Test Overview

**Total Coverage**: **415 tests** across 2 main categories
- **Parser Tests**: 113 tests validating syntax and AST generation
- **Semantic Tests**: 302 tests validating type checking and program semantics

**Success Rate**: ✅ **415/415 passing** (100% success rate)

## 🏗️ Test Architecture

The test suite follows a clean separation between parsing (syntax) and semantic analysis (meaning):

```
tests/
├── parser/          # Syntax validation & AST generation (113 tests)
├── semantic/        # Type checking & semantic analysis (302 tests) 
└── README.md        # This documentation
```

### 🔍 Parser Tests (113 tests)
*Validates syntax parsing and Abstract Syntax Tree (AST) generation*

```
tests/parser/
├── test_minimal.py                     # Core function syntax & basic features (26 tests)
├── test_expressions.py                 # Expression parsing and precedence (24 tests)
├── test_bool.py                        # Boolean literals and operators (17 tests)
├── test_comments.py                    # Comment parsing & integration (14 tests)
├── test_variables.py                   # val/mut variable declarations (11 tests)
├── test_expression_type_annotations.py # Expression type annotations (11 tests)
├── test_type_annotation_errors.py     # Type annotation error detection (10 tests)
├── test_undef.py                       # Uninitialized variable syntax (9 tests)
├── test_binary_ops.py                  # Binary operator parsing (5 tests)
├── test_unary_ops.py                   # Unary operator parsing (4 tests)
└── test_errors.py                      # Syntax error detection (4 tests)
```

**Parser Test Responsibilities:**
- ✅ Function declarations and signatures
- ✅ Variable declarations (`val`/`mut`)
- ✅ All type annotations (`i32`, `i64`, `f32`, `f64`, `string`, `bool`, `void`)
- ✅ Literal parsing (numbers, strings, booleans)
- ✅ Expression parsing with correct precedence
- ✅ Binary and unary operators
- ✅ Block structure and nesting
- ✅ Return statements (value and bare returns)
- ✅ Assignment statements
- ✅ Comment handling (`// comments`)
- ✅ `undef` keyword parsing
- ✅ Type annotation positioning and syntax
- ✅ Syntax error detection and reporting

### 🧠 Semantic Tests (302 tests - **FULLY REFACTORED**)
*Validates type checking, scope management, and program semantics*

**🎯 Refactored in 7-Session Project - Zero Overlap, Complete Coverage**

```
tests/semantic/
├── test_comptime_types.py        # Comprehensive comptime type system (38 tests)
├── test_precision_loss.py        # "Explicit Danger, Implicit Safety" (36 tests)
├── test_unified_blocks.py        # Unified block system (34 tests)
├── test_assignment.py            # Assignment validation & context (31 tests)
├── test_error_messages.py        # Error message consistency (24 tests)
├── test_type_annotations.py      # Type annotation syntax & rules (23 tests)
├── test_type_coercion.py         # Concrete type coercion (23 tests)
├── test_binary_ops.py            # Binary operations (20 tests)
├── test_context_framework.py     # Context-guided resolution (19 tests)
├── test_basic_semantics.py       # Cross-feature integration (18 tests)
├── test_mutability.py            # val/mut variable system (18 tests)
├── test_unary_ops.py             # Unary operations (18 tests)
├── test_bare_returns.py          # Bare return handling (16 tests)
└── test_bool.py                  # Boolean type semantics (12 tests)
```

**Core Type System Tests:**
- **test_comptime_types.py**: Complete Zig-style comptime type system with context-dependent coercion
- **test_type_coercion.py**: Concrete type coercion and safe widening rules  
- **test_precision_loss.py**: "Explicit Danger, Implicit Safety" enforcement with acknowledgment patterns
- **test_type_annotations.py**: Type annotation syntax, positioning, and validation rules

**Operation Tests:**
- **test_binary_ops.py**: Binary operations, mixed-type expressions, division operators
- **test_unary_ops.py**: Unary operations and negative literals (consolidated from deleted files)

**Language Feature Tests:**
- **test_mutability.py**: val (immutable) vs mut (mutable) variable system semantics
- **test_assignment.py**: Assignment statement validation and context-guided resolution
- **test_unified_blocks.py**: Universal block system (statement/expression/function bodies)

**Integration & Quality Tests:**
- **test_basic_semantics.py**: Cross-feature integration scenarios
- **test_context_framework.py**: Context propagation mechanisms throughout the language
- **test_error_messages.py**: Comprehensive error message consistency and helpfulness

**Specialized Tests:**
- **test_bool.py**: Boolean type semantics and validation
- **test_bare_returns.py**: Bare return statement handling in void functions

## 🎯 Key Features Tested

### Advanced Type System
- **Comptime Types**: `42` automatically becomes the right numeric type based on context
- **Context-Guided Resolution**: Same literal works as `i32`, `i64`, `f32`, or `f64` based on usage
- **"Explicit Danger, Implicit Safety"**: Precision loss requires explicit acknowledgment (`: type`)
- **Type Safety**: Prevents invalid coercions while allowing safe ones
- **No Suffixes Needed**: Write `42`, not `42i64` - context determines type

### Unified Block System  
- **Expression Blocks**: `val x = { return 42 }` - blocks that compute values
- **Statement Blocks**: `{ val temp = 100 }` - scoped execution without returns
- **Function Bodies**: Same syntax for void and value-returning functions
- **Context-Aware Validation**: Block behavior determined by usage context
- **Universal Scoping**: Consistent scope and shadowing rules across all block types

### Memory Safety & Mutability
- **Immutable by Default**: `val` variables prevent accidental changes
- **Explicit Mutability**: `mut` variables require opt-in for reassignment
- **Scope Safety**: Variables don't leak between scopes
- **Use-Before-Init**: Prevents using `undef` variables
- **Assignment Validation**: Type compatibility and mutability enforcement

### Error Quality & Recovery
- **Helpful Messages**: Clear, actionable error messages with context
- **Error Recovery**: Continued analysis after errors (doesn't stop at first error)
- **Consistency**: Uniform error message format across all language features
- **Educational**: Error messages teach users about the type system

## 🚀 Running Tests

### Run All Tests
```bash
# Complete test suite (415 tests)
uv run pytest tests/ -v

# Quick summary 
uv run pytest tests/
```

### Run Specific Test Categories  
```bash
# Parser tests only (113 tests)
uv run pytest tests/parser/ -v

# Semantic tests only (302 tests) 
uv run pytest tests/semantic/ -v
```

### Run Individual Test Files
```bash
# Test specific features
uv run pytest tests/parser/test_minimal.py -v
uv run pytest tests/semantic/test_comptime_types.py -v

# Test with detailed output
uv run pytest tests/semantic/test_precision_loss.py -v --tb=short
```

### Test Performance
```bash
# Run with timing information
uv run pytest tests/ --durations=10

# Parallel execution (if available)
uv run pytest tests/ -n auto
```
