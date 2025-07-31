# Hexen Test Suite 🧪

Test coverage for the Hexen programming language compiler. This test suite covers Hexen features from syntax parsing to semantic analysis.

## 📊 Test Overview

**Total Coverage**: **682 tests** across 2 main categories
- **Parser Tests**: 250 tests covering syntax and AST generation
- **Semantic Tests**: 432 tests covering type checking and program semantics

**Success Rate**: ✅ **682/682 passing**

## 🏗️ Test Architecture

The test suite follows a clean separation between parsing (syntax) and semantic analysis (meaning):

```
tests/
├── parser/          # Syntax validation & AST generation (250 tests)
├── semantic/        # Type checking & semantic analysis (432 tests) 
└── README.md        # This documentation
```

### 🔍 Parser Tests (250 tests)
*Covers syntax parsing and Abstract Syntax Tree (AST) generation*

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

### 🧠 Semantic Tests (432 tests)
*Covers type checking, scope management, and program semantics*

```
tests/semantic/
├── functions/                        # Function system features (7 files)
│   ├── test_function_declarations.py # Function declaration validation (39 tests)
│   ├── test_function_calls.py        # Function call resolution (36 tests)
│   ├── test_return_type_context.py   # Return type validation (31 tests)
│   ├── test_mutable_parameters.py    # Mutable parameter support (19 tests)
│   ├── test_comprehensive_integration.py # Function integration testing (18 tests)
│   ├── test_error_message_quality.py # Function error message quality (17 tests)
│   └── test_performance_scalability.py # Function performance testing (9 tests)
├── integration/                       # Cross-feature integration tests (4 files)
│   ├── test_basic_semantics.py        # Language integration scenarios (16 tests)
│   ├── test_binary_ops.py            # Multi-operator + type system integration (32 tests)
│   ├── test_comptime_adaptation.py   # Comptime across multiple contexts (27 tests)
│   └── test_error_messages.py        # Error consistency across features (21 tests)
├── blocks/                           # Block system features (4 files)
│   ├── test_block_scoping.py         # Universal scoping rules (10 tests)
│   ├── test_expression_blocks.py     # Expression blocks (15 tests)
│   ├── test_function_blocks.py       # Function body blocks (8 tests)
│   └── test_statement_blocks.py      # Statement blocks (7 tests)
├── precision/                        # Numeric precision features (4 files)
│   ├── test_integer_precision.py     # Integer overflow/precision (14 tests)
│   ├── test_float_precision.py       # Float precision handling (10 tests)
│   ├── test_mixed_precision.py       # Mixed-type precision (8 tests)
│   └── test_safe_operations.py       # Safe numeric operations (6 tests)
├── test_assignment.py               # Assignment statement validation (31 tests)
├── test_bare_returns.py            # Bare return handling (16 tests)
├── test_bool.py                     # Boolean type semantics (12 tests)
├── test_comptime_types.py           # Comptime type system (38 tests)
├── test_explicit_conversions.py     # Explicit type conversions (16 tests)
├── test_literal_overflow.py         # Literal overflow detection (11 tests)
├── test_mutability.py               # val/mut variable system (15 tests)
├── test_unary_ops.py                # Unary operations (16 tests)
├── test_unified_block_system.py     # Unified block system (additional tests)
└── test_utils.py                    # Testing utilities and mixins
```

**🚀 Function System Tests (functions/):**
- **test_function_declarations.py**: Function declaration validation and error handling
- **test_function_calls.py**: Function call resolution and parameter type checking
- **test_return_type_context.py**: Return type validation and consistency
- **test_mutable_parameters.py**: Mutable parameter support and reassignment validation
- **test_comprehensive_integration.py**: Function integration with all language features
- **test_error_message_quality.py**: Function-specific error message quality and consistency
- **test_performance_scalability.py**: Function system performance and scalability testing

**🎯 Integration Tests (integration/):**
- **test_basic_semantics.py**: Cross-feature language integration scenarios
- **test_binary_ops.py**: Multi-operator integration with type system (arithmetic, comparison, logical)
- **test_comptime_adaptation.py**: Comptime type adaptation across multiple contexts
- **test_error_messages.py**: Error message consistency across all language features

**🧱 Block System Tests (blocks/):**
- **test_block_scoping.py**: Universal scoping and shadowing rules
- **test_expression_blocks.py**: Blocks that compute and return values
- **test_function_blocks.py**: Function body validation and contexts
- **test_statement_blocks.py**: Scoped execution blocks without returns

**🔢 Precision Tests (precision/):**
- **test_integer_precision.py**: Integer overflow detection and validation
- **test_float_precision.py**: Floating-point precision handling
- **test_mixed_precision.py**: Mixed-type precision loss scenarios
- **test_safe_operations.py**: Safe numeric operations validation

**⚙️ Core Feature Tests:**
- **test_comptime_types.py**: Complete comptime type system with context-dependent adaptation
- **test_explicit_conversions.py**: Explicit type conversion syntax and validation (`:type`)
- **test_mutability.py**: val (immutable) vs mut (mutable) variable semantics
- **test_assignment.py**: Assignment statement validation and type compatibility
- **test_unary_ops.py**: Unary operations and negative literals
- **test_bool.py**: Boolean type semantics and validation
- **test_bare_returns.py**: Bare return statement handling in void functions
- **test_literal_overflow.py**: Literal overflow detection at parse time

## 🎯 Key Features Tested

### Type System
- **Comptime Types**: `42` automatically becomes the right numeric type based on context
- **Context-Guided Resolution**: Same literal works as `i32`, `i64`, `f32`, or `f64` based on usage
- **"Explicit Danger, Implicit Safety"**: Precision loss requires explicit acknowledgment (`: type`)
- **Type Safety**: Prevents invalid coercions while allowing safe ones
- **No Suffixes Needed**: Write `42`, not `42i64` - context determines type

### Function System
- **Function Declarations**: Full function syntax with parameters and return types
- **Function Calls**: Parameter type checking and argument resolution
- **Mutable Parameters**: Support for `mut` parameters with reassignment validation
- **Return Type Validation**: Type consistency checking for all return paths

### Unified Block System  
- **Expression Blocks**: `val x = { assign 42 }` - blocks that compute values
- **Statement Blocks**: `{ val temp = 100 }` - scoped execution without returns
- **Function Bodies**: Same syntax for void and value-returning functions
- **Context-Aware Validation**: Block behavior determined by usage context
- **Scoping**: Consistent scope and shadowing rules across all block types

### Memory Safety & Mutability
- **Immutable by Default**: `val` variables prevent accidental changes
- **Explicit Mutability**: `mut` variables require opt-in for reassignment
- **Scope Safety**: Variables don't leak between scopes
- **Use-Before-Init**: Prevents using `undef` variables
- **Assignment Validation**: Type compatibility and mutability enforcement

### Error Handling
- **Error Messages**: Clear, actionable error messages with context
- **Error Recovery**: Continued analysis after errors (doesn't stop at first error)
- **Consistency**: Uniform error message format across all language features

## 🚀 Running Tests

### Run All Tests
```bash
# Complete test suite (682 tests)
uv run pytest tests/ -v

# Quick summary 
uv run pytest tests/
```

### Run Specific Test Categories  
```bash
# Parser tests only (250 tests)
uv run pytest tests/parser/ -v

# Semantic tests only (432 tests) 
uv run pytest tests/semantic/ -v

# Function tests only
uv run pytest tests/semantic/functions/ -v

# Integration tests only
uv run pytest tests/semantic/integration/ -v

# Block system tests only
uv run pytest tests/semantic/blocks/ -v

# Precision tests only
uv run pytest tests/semantic/precision/ -v
```

### Run Individual Test Files
```bash
# Test specific features
uv run pytest tests/parser/test_functions.py -v
uv run pytest tests/semantic/functions/test_function_declarations.py -v
uv run pytest tests/semantic/test_comptime_types.py -v
uv run pytest tests/semantic/integration/test_basic_semantics.py -v
uv run pytest tests/semantic/blocks/test_expression_blocks.py -v
uv run pytest tests/semantic/precision/test_integer_precision.py -v

# Test with detailed output
uv run pytest tests/semantic/test_explicit_conversions.py -v --tb=short
```

### Test Performance
```bash
# Run with timing information
uv run pytest tests/ --durations=10

# Parallel execution (if available)
uv run pytest tests/ -n auto
```
