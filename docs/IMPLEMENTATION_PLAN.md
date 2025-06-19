# Hexen Type System Implementation Plan

**Generated from comprehensive semantic test analysis**  
**Target**: Full TYPE_SYSTEM.md compliance with "Explicit Danger, Implicit Safety" philosophy

## 📋 Executive Summary

Based on comprehensive test analysis, this plan outlines the step-by-step implementation of Hexen's sophisticated type system. The failing tests reveal exactly what needs to be built, serving as both specification and validation.

**Current State**: ~40% implemented (basic types, coercion detection, val/mut)  
**Target State**: 100% TYPE_SYSTEM.md compliant with full test suite passing

---

## 🎯 Phase 1: Type Annotation System (HIGH PRIORITY)
**Estimated Effort**: 2-3 weeks  
**Test Coverage**: `test_type_annotations.py` (16 tests)

### 1.1 Parser Extensions
**Files to modify**: `src/hexen/parser.py`, grammar files

- [ ] **Type Annotated Expressions**: Implement `expression : type` syntax parsing
  - Add `type_annotated_expression` rule to grammar
  - Handle precedence and positioning (rightmost end requirement)
  - Parse but don't evaluate type annotations yet

- [ ] **Function Parameters**: Implement `func name(param: type)` syntax
  - Extend function definition grammar
  - Support multiple parameters with types
  - Handle parameter parsing in function declarations

### 1.2 Semantic Analyzer Core
**Files to modify**: `src/hexen/semantic_analyzer.py`

- [ ] **Type Annotation Processing**: Core acknowledgment logic
  ```python
  def process_type_annotation(self, expr, annotation):
      # Must match left-hand side type exactly
      # Serves as explicit acknowledgment of precision loss
      # Enable "dangerous" operations when acknowledged
  ```

- [ ] **Acknowledgment Validation**: 
  - Type annotation must match target type exactly
  - Enable precision loss operations when explicitly acknowledged
  - Reject type annotations without explicit left-side type context

- [ ] **Integration with Existing Systems**:
  - Connect with current precision loss detection
  - Override coercion errors when properly acknowledged
  - Maintain "Explicit Danger, Implicit Safety" principle

### 1.3 Expected Outcomes
- ✅ `val result : i32 = large_value : i32` works (with acknowledgment)
- ✅ `val wrong : i32 = value : f64` fails (annotation mismatch)
- ✅ `val bad = expr : i32` fails (no explicit left-side type)
- ✅ All precision loss scenarios work with proper acknowledgment

---

## 🎯 Phase 2: Precision Loss Acknowledgment (HIGH PRIORITY)
**Estimated Effort**: 1-2 weeks  
**Test Coverage**: `test_precision_loss.py` (21 tests)

### 2.1 Acknowledgment Logic Implementation
**Files to modify**: `src/hexen/semantic_analyzer.py`

- [ ] **Precision Loss Override**: When type annotation matches target
  ```python
  def check_precision_loss_with_acknowledgment(self, source_type, target_type, annotation):
      if annotation and annotation == target_type:
          return True  # Acknowledged, allow operation
      return False  # Require acknowledgment
  ```

- [ ] **Narrowing Operation Support**:
  - i64 → i32 with `: i32` acknowledgment
  - f64 → f32 with `: f32` acknowledgment  
  - float → integer with appropriate acknowledgment
  - Chained conversions with step-by-step acknowledgment

### 2.2 Error Message Enhancement
**Files to modify**: Error reporting in semantic analyzer

- [ ] **Consistent Error Formatting**:
  - "Potential truncation, add ': i32' to acknowledge"
  - "Potential precision loss, add ': f32' to acknowledge"
  - Include specific type names in suggestions

- [ ] **Context-Aware Messages**:
  - Different contexts (assignment, declaration, return) 
  - Maintain consistent messaging across all contexts

### 2.3 Expected Outcomes
- ✅ `small = large : i32` works (i64 → i32 with acknowledgment)
- ✅ `single = precise : f32` works (f64 → f32 with acknowledgment)
- ✅ `int_val = float_val : i32` works (float → int with acknowledgment)
- ✅ All "dangerous" operations require explicit acknowledgment

---

## 🎯 Phase 3: Enhanced Mutability System (MEDIUM PRIORITY)
**Estimated Effort**: 1-2 weeks  
**Test Coverage**: `test_mutability.py` (24 tests)

### 3.1 `undef` Value Implementation
**Files to modify**: `src/hexen/semantic_analyzer.py`, type system

- [ ] **`undef` Semantic Handling**:
  ```python
  def handle_undef_value(self, var_type, is_mutable):
      if not is_mutable:
          raise SemanticError("val + undef creates unusable variable, use mut instead")
      if not var_type:
          raise SemanticError("undef requires explicit type annotation")
      return UndefValue(var_type)
  ```

- [ ] **Deferred Initialization**:
  - `mut var : type = undef` → valid deferred initialization
  - `val var : type = undef` → error with helpful message
  - Track uninitialized variables until first assignment

### 3.2 Enhanced Validation Rules
**Files to modify**: Variable declaration and assignment logic

- [ ] **val + undef Prohibition**:
  - Clear error: "val + undef creates unusable variable"
  - Suggestion: "Consider using 'mut' for deferred initialization"
  - Rationale explanation in error messages

- [ ] **mut + undef Requirements**:
  - Require explicit type annotation
  - Track initialization state
  - Validate first assignment matches declared type

### 3.3 Integration with Type Coercion
- [ ] **Mutability + Precision Loss**: 
  - val variables support precision loss acknowledgment
  - mut reassignments support precision loss acknowledgment
  - Consistent behavior across declaration and assignment contexts

### 3.4 Expected Outcomes
- ✅ `mut config : string = undef` works (deferred initialization)
- ❌ `val config : string = undef` fails with helpful error
- ❌ `mut config = undef` fails (requires explicit type)
- ✅ Conditional initialization patterns work correctly

---

## 🎯 Phase 4: Advanced Type Coercion (MEDIUM PRIORITY)
**Estimated Effort**: 1-2 weeks  
**Test Coverage**: `test_type_coercion.py` (25 tests)

### 4.1 Enhanced Coercion Rules
**Files to modify**: Type coercion logic in semantic analyzer

- [ ] **Complete Widening Implementation**:
  - i32 → {i64, f32, f64} (safe, automatic)
  - i64 → {f32, f64} (safe, automatic)  
  - f32 → f64 (safe, automatic)

- [ ] **Narrowing with Acknowledgment**:
  - All narrowing operations require explicit acknowledgment
  - Integration with Phase 2 acknowledgment system
  - Proper error messages for each narrowing scenario

### 4.2 Context-Guided Resolution
**Files to modify**: Expression evaluation and type inference

- [ ] **Assignment Context**: Target type guides coercion
- [ ] **Return Context**: Function return type guides coercion
- [ ] **Declaration Context**: Variable type annotation guides coercion
- [ ] **Mixed-Type Expression Handling**: Require explicit result type

### 4.3 Complex Scenario Support
- [ ] **Chained Coercions**: Multi-step type conversions
- [ ] **Expression Type Resolution**: Complex expressions with mixed types
- [ ] **Integration with comptime Types**: Seamless comptime → concrete coercion

### 4.4 Expected Outcomes
- ✅ All safe widening operations work automatically
- ✅ All narrowing operations require and accept acknowledgment
- ✅ Context-guided coercion works in all scenarios
- ✅ Mixed-type expressions handled correctly

---

## 🎯 Phase 5: Comprehensive Error Messages (MEDIUM PRIORITY)
**Estimated Effort**: 1 week  
**Test Coverage**: `test_error_messages.py` (21 tests)

### 5.1 Message Standardization
**Files to modify**: Error reporting throughout semantic analyzer

- [ ] **Consistent Formatting**:
  ```python
  ERROR_TEMPLATES = {
      'precision_loss': "Potential {loss_type}, add ': {target_type}' to acknowledge",
      'type_mismatch': "Type annotation must match variable's declared type",
      'mixed_types': "Mixed-type operation requires explicit result type",
      'val_undef': "val + undef creates unusable variable, use mut instead"
  }
  ```

- [ ] **Context-Aware Messaging**: Same error type, consistent message across contexts
- [ ] **Actionable Guidance**: Every error suggests specific solution

### 5.2 Enhanced Error Information
- [ ] **Type Information**: Include relevant types in all error messages
- [ ] **Suggestion System**: Provide concrete fix suggestions
- [ ] **Rationale Explanation**: Explain why operation is dangerous/forbidden

### 5.3 Expected Outcomes
- ✅ All error messages are consistent and helpful
- ✅ Users receive actionable guidance for every error
- ✅ Error messages include relevant type information
- ✅ Complex scenarios provide clear guidance

---

## 🎯 Phase 6: Parser Infrastructure (SUPPORTING)
**Estimated Effort**: 2-3 weeks  
**Test Coverage**: Multiple test files with parsing failures

### 6.1 Control Flow Parsing
**Files to modify**: Parser grammar and AST generation

- [ ] **Conditional Statements**: `if condition { } else { }` syntax
- [ ] **Block Expressions**: Nested block support
- [ ] **Expression Blocks**: `{ statements; return expr }` syntax

### 6.2 Enhanced Expression Parsing
- [ ] **Function Calls**: `func(arg1, arg2)` syntax
- [ ] **Method Calls**: `object.method()` syntax (if needed)
- [ ] **Complex Expressions**: Nested operations with type annotations

### 6.3 Expected Outcomes
- ✅ All test cases parse successfully
- ✅ Control flow constructs work in semantic tests
- ✅ Complex expressions supported throughout

---

## 📊 Implementation Priority Matrix

| Phase | Priority | Complexity | Test Impact | Dependencies |
|-------|----------|------------|-------------|--------------|
| 1. Type Annotations | **HIGH** | Medium | 16 tests | None |
| 2. Precision Loss | **HIGH** | Low | 21 tests | Phase 1 |
| 3. Mutability | **MEDIUM** | Medium | 24 tests | Phase 1 |
| 4. Type Coercion | **MEDIUM** | High | 25 tests | Phase 1, 2 |
| 5. Error Messages | **MEDIUM** | Low | 21 tests | All phases |
| 6. Parser Infrastructure | **SUPPORTING** | High | All tests | None |

---

## 🧪 Test-Driven Development Strategy

### Validation Approach
1. **Phase Completion Criteria**: All tests in phase's test file pass
2. **Integration Testing**: Run full semantic test suite after each phase
3. **Regression Prevention**: Existing functionality must remain working
4. **Documentation Updates**: Update TYPE_SYSTEM.md examples as implemented

### Test Execution Commands
```bash
# Phase-specific testing
python -m pytest tests/semantic/test_type_annotations.py -v
python -m pytest tests/semantic/test_precision_loss.py -v
python -m pytest tests/semantic/test_mutability.py -v
python -m pytest tests/semantic/test_type_coercion.py -v
python -m pytest tests/semantic/test_error_messages.py -v

# Full semantic validation
python -m pytest tests/semantic/ -v

# Regression testing
python -m pytest tests/ -v
```

---

## 🎯 Success Metrics

### Phase Completion Indicators
- [ ] **Phase 1**: All type annotation tests pass (16/16)
- [ ] **Phase 2**: All precision loss tests pass (21/21)  
- [ ] **Phase 3**: All mutability tests pass (24/24)
- [ ] **Phase 4**: All type coercion tests pass (25/25)
- [ ] **Phase 5**: All error message tests pass (21/21)
- [ ] **Phase 6**: All parsing issues resolved

### Final Success Criteria
- [ ] **100% Semantic Test Coverage**: All 107 new semantic tests pass
- [ ] **TYPE_SYSTEM.md Compliance**: Full implementation of specification
- [ ] **"Explicit Danger, Implicit Safety"**: Philosophy correctly implemented
- [ ] **Regression-Free**: All existing tests continue to pass

---

## 📝 Notes for Implementation

### Key Design Principles
1. **Explicit Danger, Implicit Safety**: Safe operations implicit, dangerous require acknowledgment
2. **Context-Guided Resolution**: Assignment targets provide type context
3. **Type Annotation Precision**: Annotations must match left-hand side exactly
4. **Helpful Error Messages**: Every error provides actionable guidance

### Implementation Tips
- Start with failing tests as specifications
- Implement incrementally within each phase
- Use test-driven development approach
- Maintain backward compatibility
- Document design decisions

### Future Considerations
- Performance optimization after correctness
- Additional type system features beyond TYPE_SYSTEM.md
- Integration with broader language features
- Tooling and IDE support

---

**This implementation plan transforms the comprehensive test failures into a clear roadmap for achieving full TYPE_SYSTEM.md compliance. Each phase builds upon previous work, with tests serving as both specification and validation.** 