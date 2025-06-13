# Hexen Binary Operations Implementation Plan 🦉

*Comprehensive roadmap for implementing binary operations with context-guided type resolution*

## Overview

This document outlines the complete implementation strategy for adding binary operations to Hexen, following the **"Context-Guided Type Resolution"** philosophy established in [BINARY_OPS.md](BINARY_OPS.md). The plan is designed to be AI context-manageable with clear phases, comprehensive testing, and minimal risk.

## Table of Contents

- [Current State Analysis](#current-state-analysis)
- [Implementation Phases](#implementation-phases)
- [Testing Strategy](#testing-strategy) 
- [Technical Implementation Details](#technical-implementation-details)
- [Success Criteria](#success-criteria)
- [Risk Management](#risk-management)

## Current State Analysis

### ✅ **Existing Foundation (Strong)**

#### **Semantic Analyzer (`semantic.py`)**
- **Complete Type System**: `HexenType` enum with comptime types (`COMPTIME_INT`, `COMPTIME_FLOAT`)
- **Sophisticated Coercion**: `_can_coerce()` method with comptime type support
- **Context-Aware Framework**: Methods designed for extensibility
- **Expression Analysis**: `_analyze_expression()` with dispatch pattern
- **Symbol Table**: Complete scope management and variable tracking
- **Error Handling**: Centralized error collection with `_error()` method

#### **Parser (`parser.py`)**
- **Lark-based PEG Parser**: Robust foundation with `HexenTransformer`
- **AST Generation**: Clean node structure for expressions
- **Terminal Handling**: Complete support for literals and identifiers
- **Error Recovery**: Proper syntax error reporting

#### **Testing Infrastructure**
- **164 Comprehensive Tests** across parser and semantic analysis
- **Well-organized Structure**: `tests/parser/`, `tests/semantic/`
- **Good Coverage**: Variables, types, blocks, comptime types
- **Clear Patterns**: Established testing conventions and utilities

### ❌ **Missing for Binary Operations**

#### **Grammar (`hexen.lark`)**
```lark
// Current (flat structure)
expression: NUMBER | STRING | BOOLEAN | IDENTIFIER | block

// Required (precedence hierarchy with division operators)  
expression: logical_or
logical_or: logical_and (("||") logical_and)*
logical_and: equality (("&&") equality)*
equality: relational (("==" | "!=") relational)*
relational: additive (("<" | ">" | "<=" | ">=") additive)*
additive: multiplicative (("+" | "-") multiplicative)*
multiplicative: unary (("*" | "/" | "\\" | "%") unary)*  // Note: Two division operators
unary: ("-" | "!")? primary
primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")"
```

#### **Semantic Analysis**
- **No binary operation handling** in `_analyze_expression()`
- **No context passing** to expression analysis methods
- **No operator-specific type resolution** logic
- **No mixed-type operation validation**
- **No division operator specific handling** for `/` vs `\`

#### **Parser Transformer**
- **No binary operation AST generation**
- **No operator precedence handling** 
- **No parenthesized expression support**
- **No left-associative tree construction**

## Implementation Phases

### Phase 1: Foundation Enhancement (Context Framework)
*Goal: Add context-passing capability AND basic binary operation grammar*

#### **1.1 Grammar Changes** (`hexen.lark`)
```lark
// Replace current expression rule with complete operator hierarchy
expression: logical_or
logical_or: logical_and (("||") logical_and)*
logical_and: equality (("&&") equality)*
equality: relational (("==" | "!=") relational)*
relational: additive (("<" | ">" | "<=" | ">=") additive)*
additive: multiplicative (("+" | "-") multiplicative)*
multiplicative: unary (("*" | "/" | "\\" | "%") unary)*  // Two division operators
unary: ("-" | "!")? primary
primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")"
```

#### **1.2 Parser Changes** (`parser.py`)
```python
# Add parentheses handling to transformer
def primary(self, children):
    if len(children) == 1:
        return children[0]  # Direct primary
    else:
        return children[1]  # Parenthesized expression (skip parens)

# Add division operator handling
def multiplicative(self, args):
    """Handle multiplicative operations including both division operators."""
    return self._build_binary_operation_tree(args, ["*", "/", "\\", "%"])
```

#### **1.3 Semantic Changes** (`semantic.py`)
```python
def _analyze_expression(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """
    Analyze an expression and return its type.
    
    Args:
        node: Expression AST node
        target_type: Optional target type for context-guided resolution
    """

def _analyze_variable_declaration_unified(self, ...):
    # Pass target type as context when analyzing value
    if value:
        value_type = self._analyze_expression(value, var_type)  # <- Add context

def _analyze_assignment_statement(self, node: Dict):
    # Pass symbol type as context
    value_type = self._analyze_expression(value, symbol.type)  # <- Add context
```

#### **1.4 Testing Requirements**
- **Parser Tests**: 
  - `test_parentheses.py` (20 tests)
  - `test_division_operators.py` (15 tests)  # New: Test both division operators
- **Semantic Tests**: 
  - `test_context_framework.py` (15 tests)
  - `test_comptime_adaptation.py` (20 tests)  # New: Test comptime type adaptation
- **Integration Tests**: Ensure all existing tests still pass (164 tests)

**Estimated Effort**: 3-4 hours, ~100 lines of changes

---

### Phase 2: Arithmetic Operations
*Goal: Implement +, -, *, /, \, % with precedence and context*

#### **2.1 Grammar Extension** (Already in Phase 1)

#### **2.2 Parser Transformer Methods**
```python
def additive(self, args):
    return self._build_binary_operation_tree(args, ["+", "-"])

def multiplicative(self, args):
    return self._build_binary_operation_tree(args, ["*", "/", "\\", "%"])

def _build_binary_operation_tree(self, args, operators):
    """Build left-associative binary operation tree from flat args list."""
    if len(args) == 1:
        return args[0]  # Single operand
    
    # Build left-associative tree: ((a + b) + c) + d
    result = args[0]
    for i in range(1, len(args), 2):
        operator = str(args[i])
        right_operand = args[i + 1]
        result = {
            "type": "binary_operation",
            "operator": operator,
            "left": result,
            "right": right_operand,
        }
    return result
```

#### **2.3 Semantic Analysis**
```python
def _analyze_expression(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    expr_type = node.get("type")
    
    if expr_type == "binary_operation":
        return self._analyze_binary_operation(node, target_type)
    # ... existing cases

def _analyze_binary_operation(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze binary operation with context-guided type resolution."""
    operator = node.get("operator")
    left_node = node.get("left")
    right_node = node.get("right")
    
    # Analyze operands (recursive context passing)
    left_type = self._analyze_expression(left_node, target_type)
    right_type = self._analyze_expression(right_node, target_type)
    
    # Special handling for division operators
    if operator in {"/", "\\"}:
        return self._analyze_division_operation(left_type, right_type, operator, target_type, node)
    
    # Delegate to specific handler based on operator category
    if operator in {"+", "-", "*", "%"}:
        return self._resolve_arithmetic_operation(left_type, right_type, operator, target_type, node)
    else:
        self._error(f"Unknown binary operator: {operator}", node)
        return HexenType.UNKNOWN

def _analyze_division_operation(self, left: HexenType, right: HexenType, 
                              operator: str, target_type: Optional[HexenType], 
                              node: Dict) -> HexenType:
    """Special handling for division operators."""
    if operator == "/":  # Float division
        if target_type is None:
            self._error("Float division (/) requires explicit result type annotation", node)
            return HexenType.UNKNOWN
        if not self._is_float_type(target_type):
            self._error(f"Float division (/) requires float result type, got {target_type}", node)
            return HexenType.UNKNOWN
        return target_type
    
    if operator == "\\":  # Integer division
        if not self._are_integer_types(left, right):
            self._error("Integer division (\\) requires integer operands", node)
            return HexenType.UNKNOWN
        # Integer division preserves comptime types when possible
        if self._is_comptime_operation(left, right):
            return self._preserve_comptime_type(left, right, operator)
        return self._resolve_integer_operation(left, right, operator, target_type, node)
```

#### **2.4 Testing Requirements**
- **Parser Tests**: 
  - `test_arithmetic_precedence.py` (30 tests)
  - `test_division_operators.py` (25 tests)  # New: Specific division operator tests
- **Semantic Tests**: 
  - `test_arithmetic_types.py` (40 tests)
  - `test_division_types.py` (35 tests)  # New: Division type resolution tests
- **Integration Tests**: 
  - `test_arithmetic_context.py` (25 tests)
  - `test_comptime_division.py` (20 tests)  # New: Comptime division tests

**Estimated Effort**: 5-6 hours, ~250 lines of changes

---

### Phase 3: Comparison Operations
*Goal: Implement <, >, <=, >=, ==, != with type promotion*

#### **3.1 Grammar Extension**
```lark
expression: equality
equality: relational (("==" | "!=") relational)*
relational: additive (("<" | ">" | "<=" | ">=") additive)*
additive: multiplicative (("+" | "-") multiplicative)*
multiplicative: primary (("*" | "/" | "%") primary)*
```

#### **3.2 Testing Requirements**
- **Parser Tests**: `test_comparison_precedence.py` (20 tests)
- **Semantic Tests**: `test_comparison_types.py` (30 tests)
- **Integration Tests**: `test_comparison_mixed_types.py` (20 tests)

**Estimated Effort**: 3-4 hours, ~150 lines of changes

---

### Phase 4: Logical Operations + Unary
*Goal: Complete operator set with &&, ||, !, unary minus*

#### **4.1 Complete Grammar**
```lark
expression: logical_or
logical_or: logical_and (("||") logical_and)*
logical_and: equality (("&&") equality)*
equality: relational (("==" | "!=") relational)*
relational: additive (("<" | ">" | "<=" | ">=") additive)*
additive: multiplicative (("+" | "-") multiplicative)*
multiplicative: unary (("*" | "/" | "%") unary)*
unary: ("-" | "!")? primary
primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")"
```

#### **4.2 Testing Requirements**
- **Parser Tests**: `test_logical_precedence.py` (25 tests)
- **Semantic Tests**: `test_logical_types.py` (30 tests)
- **Integration Tests**: `test_unary_operations.py` (20 tests)

**Estimated Effort**: 3-4 hours, ~120 lines of changes

---

### Phase 5: Error Messages + Edge Cases
*Goal: Production-ready error handling and comprehensive validation*

#### **5.1 Enhanced Error Messages**
```python
def _error_mixed_type_operation(self, left_type: HexenType, right_type: HexenType, operator: str, node: Dict):
    """Generate helpful error message for mixed-type operations."""
    self._error(
        f"Mixed-type operation '{left_type.value} {operator} {right_type.value}' requires explicit result type annotation\n"
        f"Help: Add type annotation to specify result type:\n"
        f"      val result : i64 = a {operator} b    // Widen to i64\n"
        f"   or val result : f32 = a {operator} b    // Convert both to f32",
        node
    )
```

#### **5.2 Testing Requirements**
- **Error Tests**: `test_binary_op_errors.py` (20 tests)
- **Edge Case Tests**: `test_binary_op_edge_cases.py` (25 tests)
- **Performance Tests**: `test_binary_op_performance.py` (10 tests)

**Estimated Effort**: 2-3 hours, ~100 lines of changes

---

## Testing Strategy

### Test Distribution by Phase

| Phase | Parser Tests | Semantic Tests | Integration Tests | Total |
|-------|-------------|----------------|------------------|-------|
| Phase 1 | 35 | 35 | 10 | 80 |
| Phase 2 | 55 | 75 | 45 | 175 |
| Phase 3 | 20 | 30 | 20 | 70 |
| Phase 4 | 25 | 30 | 20 | 75 |
| Phase 5 | 20 | 25 | 10 | 55 |
| **Total** | **155** | **195** | **105** | **455** |

### Testing Principles

#### ✅ **Per-Phase Gate Requirements**
1. **All new tests pass** (100% success rate)
2. **All existing tests still pass** (no regressions)  
3. **Code coverage maintained** (>90% for new code)
4. **Performance benchmarks met** (no significant slowdown)

#### ✅ **Test Categories**

**Parser Tests**:
- Grammar correctness and precedence
- AST structure validation  
- Left-associativity verification
- Error handling (malformed syntax)
- Parentheses and grouping
- Division operator validation

**Semantic Tests**:
- Type resolution accuracy
- Context propagation validation
- Comptime type coercion
- Mixed-type operation detection
- Error message quality
- Division operator type rules
- Comptime type adaptation

**Integration Tests**:
- End-to-end parsing + semantic analysis
- Complex nested expressions
- Backward compatibility verification
- Real-world usage patterns
- Performance regression testing
- Division operator behavior
- Comptime type context flow

## Technical Implementation Details

### AST Node Structures

#### **Binary Operation Node**
```python
{
    "type": "binary_operation",
    "operator": "+",  # The operator: +, -, *, /, %, <, >, <=, >=, ==, !=, &&, ||
    "left": {...},    # Left operand (expression)
    "right": {...},   # Right operand (expression)
}
```

#### **Unary Operation Node**
```python
{
    "type": "unary_operation", 
    "operator": "-",  # The operator: -, !
    "operand": {...}, # Operand (expression)
}
```

### Context Propagation Pattern

```python
# Variable declarations pass target type as context
def _analyze_variable_declaration_unified(self, name, type_annotation, value, mutability, node):
    if type_annotation:
        var_type = self._parse_type(type_annotation)
        if value:
            # Context flows to expression analysis
            value_type = self._analyze_expression(value, var_type)

# Assignments pass symbol type as context  
def _analyze_assignment_statement(self, node):
    symbol = self.symbol_table.lookup_symbol(target_name)
    # Context flows to expression analysis
    value_type = self._analyze_expression(value, symbol.type)
```

## Success Criteria

### Phase Completion Gates

Each phase must meet these criteria before proceeding:

#### **✅ Functional Requirements**
- All new functionality works as specified
- All test cases pass (100% success rate)
- No regressions in existing functionality
- Error messages are helpful and actionable

#### **✅ Quality Requirements**
- Code coverage >90% for new code
- Performance within 10% of baseline
- Documentation updated for new features
- Code review completed and approved

## Risk Management

### Identified Risks and Mitigations

#### **🔴 High Risk: Division Operator Complexity**
- **Risk**: Two division operators could lead to confusion or misuse
- **Mitigation**: 
  - Clear error messages for operator misuse
  - Comprehensive testing of both operators
  - Explicit type requirements for float division
- **Detection**: Division operator specific test suite

#### **🔴 High Risk: Comptime Type Adaptation**
- **Risk**: Context-guided resolution might not handle all cases correctly
- **Mitigation**: 
  - Systematic testing of comptime type adaptation
  - Clear rules for type resolution
  - Explicit error messages for ambiguous cases
- **Detection**: Comptime type adaptation test suite

#### **🟡 Medium Risk: Context Propagation Bugs**
- **Risk**: Target type context might not flow correctly through nested expressions
- **Mitigation**: Systematic testing of context flow patterns
- **Detection**: Integration tests with deeply nested expressions

#### **🟢 Low Risk: Performance Regression**
- **Risk**: Additional analysis might slow down compilation
- **Mitigation**: Performance benchmarks and optimization where needed
- **Detection**: Performance test suite and monitoring

## Development Workflow

### Recommended Implementation Order

1. **Start with Phase 1** - provides maximum foundation with minimal risk
2. **Validate thoroughly** - ensure all 80 new tests pass plus 164 existing tests
3. **Proceed incrementally** - only move to next phase when current phase is complete
4. **Maintain quality gates** - never compromise on testing or code quality
5. **Document progress** - update this plan as implementation proceeds

### AI Context Management

This plan is designed to be AI context-manageable:

- **Small focused phases** (80-250 lines each)
- **Clear success criteria** for each phase
- **Independent development** (can pause/resume at any phase boundary)
- **Comprehensive documentation** of all implementation details
- **Test-driven approach** with clear validation at each step

### Next Steps

**Immediate Action**: Begin with **Phase 1** implementation:

1. **Create feature branch**: `feature/binary-operations-phase-1`
2. **Implement grammar changes**: Update `hexen.lark` with complete operator hierarchy
3. **Update parser transformer**: Add division operator handling
4. **Enhance semantic analyzer**: Add context parameter and division handling
5. **Create comprehensive tests**: 80 new tests for Phase 1
6. **Validate integration**: Ensure all 164 existing tests still pass

This updated plan provides a solid foundation for implementing Hexen's binary operations system while maintaining the language's core principles of safety, clarity, and elegance. 