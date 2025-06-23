# 📋 **Hexen Semantic Tests Refactoring Plan**

*A multi-session roadmap for consolidating and standardizing semantic tests*

---

## 🎯 **Overall Objectives**

1. **Eliminate redundant test coverage** across 16 test files
2. **Standardize test structure** and coding patterns
3. **Create logical test organization** that matches the type system design
4. **Improve maintainability** and reduce cognitive overhead
5. **Ensure comprehensive coverage** without overlap

---

## 📊 **Current State Summary**

- **16 test files** with significant overlap
- **~3,000+ lines** of test code with redundancy
- **Inconsistent patterns** in imports, setup, assertions
- **Scattered coverage** of the same features across multiple files

**Target State**: **~10 focused test files** with clear boundaries and comprehensive coverage

---

## 🗂️ **Session Breakdown**

### **SESSION 1: Foundation & Standardization** 🏗️
*Estimated Time: 1-2 hours*

#### **Objectives**
- Fix all structural inconsistencies 
- Establish standard patterns for future sessions
- Create test utilities and common patterns

#### **Tasks**
1. **Standardize import statements** across all files
2. **Unify setup_method patterns** 
3. **Create shared test utilities** in `__init__.py`
4. **Standardize error assertion patterns**
5. **Fix naming conventions** for test methods

#### **Files to Modify**
- `tests/semantic/__init__.py` - Add test utilities
- `tests/semantic/test_unary_ops.py` - Fix import inconsistency
- `tests/semantic/test_assignment.py` - Add setup_method
- All other files - Standardize patterns

#### **Deliverables**
- ✅ Consistent import statements across all files
- ✅ Shared test utility functions
- ✅ Standardized setup_method usage
- ✅ Common error assertion patterns
- ✅ Updated documentation in `__init__.py`

#### **Validation**
```bash
# All tests should still pass
python -m pytest tests/semantic/ -v
```

---

### **SESSION 2: Core Type System Consolidation** 🔧
*Estimated Time: 2-3 hours*

#### **Objectives**
- Consolidate comptime type testing into a single comprehensive file
- Eliminate overlap between type coercion files
- Create clear boundaries between comptime and concrete type testing

#### **Tasks**
1. **Create new file**: `test_comptime_types.py` (comprehensive comptime testing)
2. **Refactor** `test_f32_comptime.py` → merge relevant tests into new file
3. **Clean up** `test_type_coercion.py` → focus only on concrete type coercion
4. **Remove duplicates** from `test_context_framework.py`
5. **Update** `test_basic_semantics.py` → remove comptime overlaps

#### **Files Created**
- `tests/semantic/test_comptime_types.py` *(NEW)*

#### **Files Modified**
- `tests/semantic/test_type_coercion.py` - Remove comptime overlaps
- `tests/semantic/test_context_framework.py` - Remove basic comptime tests
- `tests/semantic/test_basic_semantics.py` - Remove comptime tests

#### **Files Deleted**
- `tests/semantic/test_f32_comptime.py` *(DELETED - content merged)*

#### **New File Structure**
```python
# test_comptime_types.py - NEW COMPREHENSIVE FILE
class TestComptimeIntCoercion:
    """All comptime_int coercion scenarios"""
    
class TestComptimeFloatCoercion:
    """All comptime_float coercion scenarios"""
    
class TestComptimeMixedOperations:
    """Mixed comptime type operations"""
    
class TestComptimeDefaults:
    """Default type resolution for comptime types"""
    
class TestComptimeEdgeCases:
    """Edge cases and error scenarios"""
```

#### **Validation**
```bash
# Ensure no functionality lost
python -m pytest tests/semantic/test_comptime_types.py -v
python -m pytest tests/semantic/test_type_coercion.py -v
```

---

### **SESSION 3: Precision Loss & Type Annotations** ⚠️
*Estimated Time: 2-3 hours*

#### **Objectives**
- Consolidate all precision loss testing into a focused file
- Clean up type annotation testing to avoid overlap
- Eliminate redundant precision loss tests from other files

#### **Tasks**
1. **Enhance** `test_precision_loss.py` → comprehensive precision loss testing
2. **Clean up** `test_type_annotations.py` → focus on syntax and rules, not precision loss
3. **Remove precision loss tests** from `test_mutability.py`
4. **Remove precision loss overlaps** from `test_type_coercion.py`

#### **Files Modified**
- `tests/semantic/test_precision_loss.py` - Expand to be comprehensive
- `tests/semantic/test_type_annotations.py` - Focus on annotation syntax/rules
- `tests/semantic/test_mutability.py` - Remove precision loss duplicates
- `tests/semantic/test_type_coercion.py` - Remove precision loss duplicates

#### **Enhanced File Structure**
```python
# test_precision_loss.py - ENHANCED
class TestIntegerPrecisionLoss:
    """i64→i32, large literal truncation"""
    
class TestFloatPrecisionLoss:
    """f64→f32, double precision scenarios"""
    
class TestMixedTypePrecisionLoss:
    """i64→f32, float→int conversions"""
    
class TestPrecisionLossInAssignments:
    """Precision loss in mut variable assignments"""
    
class TestPrecisionLossInExpressions:
    """Precision loss in complex expressions"""

# test_type_annotations.py - FOCUSED  
class TestTypeAnnotationSyntax:
    """Annotation positioning, matching, syntax rules"""
    
class TestTypeAnnotationRequirements:
    """When annotations are required vs optional"""
    
class TestTypeAnnotationErrorMessages:
    """Error messages specific to annotation syntax"""
```

#### **Validation**
```bash
python -m pytest tests/semantic/test_precision_loss.py -v
python -m pytest tests/semantic/test_type_annotations.py -v
python -m pytest tests/semantic/test_mutability.py -v
```

---

### **SESSION 4: Operations Consolidation** 🔢
*Estimated Time: 1-2 hours*

#### **Objectives**
- Consolidate binary and unary operations testing
- Eliminate operational overlap from other files
- Create comprehensive operations test coverage

#### **Tasks**
1. **Enhance** `test_binary_ops.py` → remove overlaps, ensure comprehensive
2. **Merge relevant content** from `test_negative_numbers.py` into `test_unary_ops.py`
3. **Remove operation tests** from `test_type_coercion.py` and other files
4. **Create unified operations structure**

#### **Files Modified**
- `tests/semantic/test_binary_ops.py` - Remove overlaps, ensure comprehensive
- `tests/semantic/test_unary_ops.py` - Merge negative number content

#### **Files Deleted**
- `tests/semantic/test_negative_numbers.py` *(DELETED - content merged)*

#### **Enhanced Structure**
```python
# test_binary_ops.py - COMPREHENSIVE
class TestComptimeBinaryOperations:
    """Comptime + comptime operations"""
    
class TestConcreteBinaryOperations:  
    """Concrete + concrete operations"""
    
class TestMixedTypeBinaryOperations:
    """Mixed type operations requiring context"""
    
class TestDivisionOperators:
    """Float (/) vs Integer (\) division"""
    
class TestLogicalOperations:
    """&&, ||, comparison operations"""

# test_unary_ops.py - COMPREHENSIVE
class TestUnaryMinus:
    """Unary minus with all numeric types"""
    
class TestUnaryMinusWithNegativeLiterals:
    """Negative number literals (merged from test_negative_numbers.py)"""
    
class TestLogicalNot:
    """Logical not operations"""
```

#### **Validation**
```bash
python -m pytest tests/semantic/test_binary_ops.py -v
python -m pytest tests/semantic/test_unary_ops.py -v
```

---

### **SESSION 5: Mutability & Assignment Cleanup** 🔄
*Estimated Time: 1-2 hours*

#### **Objectives**
- Clean up overlap between mutability and assignment testing
- Focus each file on its core responsibility
- Eliminate assignment duplicates from other files

#### **Tasks**
1. **Focus** `test_mutability.py` → val/mut semantics, undef patterns
2. **Focus** `test_assignment.py` → assignment statement validation
3. **Remove assignment overlaps** from other files
4. **Create clear boundaries** between the two files

#### **Files Modified**
- `tests/semantic/test_mutability.py` - Focus on val/mut/undef semantics
- `tests/semantic/test_assignment.py` - Focus on assignment statement validation
- Remove assignment tests from context framework and other files

#### **Clear Boundaries**
```python
# test_mutability.py - FOCUSED
class TestValVariableSemantics:
    """val declaration, immutability, undef prohibition"""
    
class TestMutVariableSemantics:
    """mut declaration, reassignment, undef support"""
    
class TestMutabilityWithTypeSystem:
    """Interaction with comptime types, coercion"""

# test_assignment.py - FOCUSED  
class TestAssignmentStatementValidation:
    """Assignment statement parsing and validation"""
    
class TestAssignmentTypeChecking:
    """Type compatibility in assignments"""
    
class TestAssignmentScoping:
    """Variable existence and scope in assignments"""
```

#### **Validation**
```bash
python -m pytest tests/semantic/test_mutability.py -v
python -m pytest tests/semantic/test_assignment.py -v
```

---

### **SESSION 6: Block System Unification** 🧱
*Estimated Time: 2-3 hours*

#### **Objectives**
- Unify block-related testing to match UNIFIED_BLOCK_SYSTEM.md
- Eliminate block testing overlap from multiple files
- Create comprehensive block system coverage

#### **Tasks**
1. **Create new file**: `test_unified_blocks.py`
2. **Merge content** from `test_statement_blocks.py` and `test_expression_blocks.py`
3. **Add comprehensive block testing** following the unified block system design
4. **Remove block tests** from other files

#### **Files Created**
- `tests/semantic/test_unified_blocks.py` *(NEW)*

#### **Files Deleted**
- `tests/semantic/test_statement_blocks.py` *(DELETED - content merged)*
- `tests/semantic/test_expression_blocks.py` *(DELETED - content merged)*

#### **Files Modified**
- Remove block testing overlap from `test_basic_semantics.py` and others

#### **New Unified Structure**
```python
# test_unified_blocks.py - NEW COMPREHENSIVE FILE
class TestStatementBlocks:
    """Statement block semantics and scoping"""
    
class TestExpressionBlocks:
    """Expression block semantics and return requirements"""
    
class TestFunctionBodyBlocks:
    """Function body as unified block type"""
    
class TestBlockScoping:
    """Universal scope management across all block types"""
    
class TestBlockContextDetermination:
    """Context-driven behavior in blocks"""
    
class TestNestedBlocks:
    """Complex nested block scenarios"""
```

#### **Validation**
```bash
python -m pytest tests/semantic/test_unified_blocks.py -v
```

---

### **SESSION 7: Integration & Final Cleanup** 🎯
*Estimated Time: 1-2 hours*

#### **Objectives**
- Final cleanup and integration
- Ensure comprehensive coverage without gaps
- Update documentation and validate entire suite

#### **Tasks**
1. **Enhance** `test_basic_semantics.py` → focus on cross-feature integration
2. **Enhance** `test_context_framework.py` → focus purely on context propagation
3. **Enhance** `test_error_messages.py` → comprehensive error message testing
4. **Update** `tests/semantic/__init__.py` documentation
5. **Run full validation** and coverage analysis

#### **Files Modified**
- `tests/semantic/test_basic_semantics.py` - Focus on integration scenarios
- `tests/semantic/test_context_framework.py` - Focus on context propagation
- `tests/semantic/test_error_messages.py` - Comprehensive error testing
- `tests/semantic/__init__.py` - Update documentation
- `tests/semantic/test_bool.py` - Minor cleanup if needed
- `tests/semantic/test_bare_returns.py` - Minor cleanup if needed

#### **Final File Structure**
```python
# Updated __init__.py documentation
"""
Semantic analysis test package for Hexen - REFACTORED

Core Type System Tests:
- test_comptime_types.py - Comprehensive comptime type system
- test_type_coercion.py - Concrete type coercion and widening  
- test_precision_loss.py - "Explicit Danger, Implicit Safety" enforcement
- test_type_annotations.py - Type annotation syntax and rules

Operation Tests:
- test_binary_ops.py - Binary operations and mixed-type expressions
- test_unary_ops.py - Unary operations and negative literals

Feature Tests:
- test_mutability.py - val/mut variable system
- test_assignment.py - Assignment statement validation
- test_unified_blocks.py - Unified block system (statement/expression/function)

Specialized Tests:
- test_bool.py - Boolean type semantics
- test_bare_returns.py - Bare return statement handling

Integration Tests:
- test_basic_semantics.py - Cross-cutting integration scenarios  
- test_context_framework.py - Context-guided type resolution
- test_error_messages.py - Error message consistency and helpfulness
"""
```

#### **Final Validation**
```bash
# Full test suite validation
python -m pytest tests/semantic/ -v --coverage
python -m pytest tests/ -v  # Ensure parser tests still work

# Coverage analysis
python -m pytest tests/semantic/ --cov=src/hexen/semantic --cov-report=html
```

---

## 📈 **Progress Tracking**

### **Session Completion Checklist**

- [ ] **Session 1**: Foundation & Standardization ✅
- [ ] **Session 2**: Core Type System Consolidation ✅
- [ ] **Session 3**: Precision Loss & Type Annotations ✅
- [ ] **Session 4**: Operations Consolidation ✅
- [ ] **Session 5**: Mutability & Assignment Cleanup ✅
- [ ] **Session 6**: Block System Unification ✅
- [ ] **Session 7**: Integration & Final Cleanup ✅

### **Files Summary**

| **Before** | **After** | **Change** |
|------------|-----------|------------|
| 16 files | 10 files | -6 files |
| ~3000+ lines | ~2500 lines | -500+ lines |
| Multiple overlaps | Clear boundaries | Organized |

### **Quality Metrics**

- **Redundancy Elimination**: Target 80% reduction in duplicate tests
- **Coverage Maintenance**: 100% coverage preservation  
- **Code Clarity**: Clear file boundaries and responsibilities
- **Maintainability**: Standardized patterns across all files

---

## 🚀 **Getting Started**

1. **Create a new branch**: `git checkout -b refactor-semantic-tests`
2. **Start with Session 1**: Begin with foundation and standardization
3. **Test after each session**: Ensure all tests pass before proceeding
4. **Document changes**: Update commit messages with session progress
5. **Validate coverage**: Run coverage analysis after major changes

---

## 📚 **Reference Materials**

- **TYPE_SYSTEM.md** - Core type system principles
- **BINARY_OPS.md** - Binary operations specification  
- **COMPARISON_OPS.md** - Comparison operations specification
- **UNIFIED_BLOCK_SYSTEM.md** - Block system design
- **Current test files** - Existing functionality to preserve

---

## 🔍 **Key Inconsistencies Found**

### **Import Statement Inconsistencies**
```python
# Most files use:
from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer

# But test_unary_ops.py uses:
from hexen.parser import HexenParser
from hexen.semantic.analyzer import SemanticAnalyzer
```

### **Setup Method Inconsistencies**
```python
# Most files:
def setup_method(self):
    self.parser = HexenParser()
    self.analyzer = SemanticAnalyzer()

# test_assignment.py:
def test_simple_mut_assignment(self):
    parser = HexenParser()  # Local variables instead
    analyzer = SemanticAnalyzer()
```

### **Error Assertion Inconsistencies**
```python
# Different approaches:
assert len(errors) == 1              # Exact count
assert len(errors) >= 1              # Minimum count  
assert errors == []                  # Empty check
assert any("text" in msg for msg in error_messages)  # Content check
```

---

## 📋 **Major Overlaps Identified**

### **1. Comptime Type Testing Overlap**
- **`test_f32_comptime.py`** - Tests comptime_int and comptime_float coercion
- **`test_type_coercion.py`** - Tests regular type coercion including comptime
- **`test_context_framework.py`** - Tests context-guided comptime resolution
- **`test_binary_ops.py`** - Tests comptime types in binary operations

### **2. Precision Loss Testing Overlap**
- **`test_precision_loss.py`** - Dedicated precision loss tests
- **`test_type_annotations.py`** - Tests type annotations for precision loss
- **`test_mutability.py`** - Tests precision loss in mut assignments
- **`test_type_coercion.py`** - Tests precision loss in coercion

### **3. Assignment Testing Overlap**
- **`test_assignment.py`** - Dedicated assignment tests
- **`test_mutability.py`** - Assignment to mut variables
- **`test_type_coercion.py`** - Assignment context coercion
- **`test_context_framework.py`** - Context propagation to assignments

### **4. Block Testing Overlap**
- **`test_statement_blocks.py`** - Statement block scoping
- **`test_expression_blocks.py`** - Expression block scoping
- **`test_basic_semantics.py`** - Cross-feature scoping

---

*This plan ensures manageable, iterative progress while maintaining test coverage and avoiding breaking changes. Each session builds on the previous work and can be completed independently in separate chat contexts.* 