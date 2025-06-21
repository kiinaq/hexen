# Detailed Parser Tests Consolidation Plan 🔧

## 📋 Session-by-Session Implementation Guide

This detailed plan breaks down the consolidation into discrete, manageable sessions that can be executed independently across multiple chat windows.

---

## 🎯 Session 1: Import Standardization & Analysis
**Estimated Time**: 30 minutes  
**Risk Level**: Very Low  
**Dependencies**: None  

### Goals
- Fix import statement inconsistencies
- Create detailed analysis of current test coverage
- Set up validation baseline

### Tasks

#### 1.1 Fix Import Statements
**Files to modify**: `test_binary_ops.py`, `test_unary_ops.py`

```python
# CHANGE IN test_binary_ops.py (line ~8):
# FROM:
from hexen.parser import HexenParser

# TO:
from src.hexen.parser import HexenParser
```

```python
# CHANGE IN test_unary_ops.py (line ~8):
# FROM: 
from hexen.parser import HexenParser

# TO:
from src.hexen.parser import HexenParser
```

#### 1.2 Validation Commands
```bash
# Run these commands to validate fixes
cd tests/parser
python -m pytest test_binary_ops.py -v
python -m pytest test_unary_ops.py -v
```

#### 1.3 Create Test Coverage Baseline
Document current test counts per file:
- `test_minimal.py`: ~15 test methods
- `test_variables.py`: ~20 test methods  
- `test_binary_ops.py`: ~12 test functions
- `test_unary_ops.py`: ~15 test methods
- `test_bool.py`: ~12 test methods
- And so on...

### Session 1 Deliverables
- [ ] Import statements standardized
- [ ] All tests still pass
- [ ] Coverage baseline documented
- [ ] Ready for Session 2

---

## 🔄 Session 2: Boolean Test Consolidation
**Estimated Time**: 45 minutes  
**Risk Level**: Low  
**Dependencies**: Session 1 complete  

### Goals
- Move all boolean-related tests to `test_bool.py`
- Remove duplicates from other files
- Create comprehensive boolean test suite

### Tasks

#### 2.1 Extract Logical Operators from `test_binary_ops.py`
**Functions to MOVE** (lines ~215-282):
```python
# MOVE these functions FROM test_binary_ops.py TO test_bool.py:

def test_logical_operators():
    """Test parsing of logical operators (&&, ||)."""
    # Line ~215-250

def test_logical_operator_precedence():
    """Test precedence of logical operators."""  
    # Line ~251-275

def test_logical_operator_syntax_errors():
    """Test syntax errors in logical operations."""
    # Line ~276-282
```

#### 2.2 Extract Logical NOT from `test_unary_ops.py`
**Class to MOVE** (lines ~75-120):
```python
# MOVE this class FROM test_unary_ops.py TO test_bool.py:

class TestLogicalNot:
    """Test parsing of logical not operator (!)"""
    # Entire class with all methods (lines ~75-120)
```

#### 2.3 Remove Boolean Duplicates from `test_variables.py`
**Lines to MODIFY** in `test_val_with_explicit_type_annotations()`:
```python
# REMOVE this test case (keep others):
val flag : bool = true

# CHANGE expected_values array from:
expected_values = [42, 123, 3.14, 2.718, "hello", True]

# TO:
expected_values = [42, 123, 3.14, 2.718, "hello"]

# And adjust the test loop accordingly
```

#### 2.4 Enhance `test_bool.py` Structure
Add new test classes:
```python
class TestBooleanOperators:
    """Test boolean logical operators (&&, ||, !)"""
    # Moved content from other files

class TestBooleanPrecedence:
    """Test operator precedence with boolean operators"""
    # Moved content from other files

class TestBooleanErrors:
    """Test error cases for boolean operations"""
    # Moved content from other files
```

### Session 2 Validation
```bash
# Validate each step:
python -m pytest test_bool.py -v
python -m pytest test_binary_ops.py -v  # Should still pass
python -m pytest test_unary_ops.py -v   # Should still pass
python -m pytest test_variables.py -v   # Should still pass
```

### Session 2 Deliverables
- [ ] All boolean tests consolidated in `test_bool.py`
- [ ] Logical operators removed from `test_binary_ops.py`
- [ ] Logical NOT removed from `test_unary_ops.py`
- [ ] Boolean duplicates removed from `test_variables.py`
- [ ] All tests still pass
- [ ] Ready for Session 3

---

## 📝 Session 3: Type Annotation Consolidation
**Estimated Time**: 40 minutes  
**Risk Level**: Low  
**Dependencies**: Session 2 complete  

### Goals
- Merge `test_types.py` content into appropriate files
- Delete `test_types.py`
- Maintain all test coverage

### Tasks

#### 3.1 Move Function Return Type Tests to `test_minimal.py`
**Functions to MOVE** from `test_types.py` (entire file):
```python
# ADD to test_minimal.py - TestMinimalHexen class:

def test_function_return_type_i32(self):
    """Test i32 return type annotation"""
    # Move from test_types.py line ~15

def test_function_return_type_i64(self):
    """Test i64 return type annotation"""  
    # Move from test_types.py line ~25

def test_function_return_type_f64(self):
    """Test f64 return type annotation"""
    # Move from test_types.py line ~35

def test_function_return_type_string(self):
    """Test string return type annotation"""
    # Move from test_types.py line ~45

def test_function_return_type_bool(self):
    """Test bool return type annotation"""
    # Move from test_types.py line ~60

def test_function_return_type_f32(self):
    """Test f32 return type annotation"""
    # Move from test_types.py line ~70

def test_function_return_type_void(self):
    """Test void return type annotation"""  
    # Move from test_types.py line ~80

def test_all_type_annotations_work(self):
    """Test that all type annotations parse correctly"""
    # Move from test_types.py line ~90
```

#### 3.2 Delete `test_types.py`
After moving all content, delete the file entirely.

### Session 3 Validation
```bash
# Validate migration:
python -m pytest test_minimal.py -v
# Should not exist anymore:
python -m pytest test_types.py -v  # Should fail - file deleted
```

### Session 3 Deliverables
- [ ] All function return type tests moved to `test_minimal.py`
- [ ] `test_types.py` deleted
- [ ] All tests still pass in `test_minimal.py`
- [ ] Ready for Session 4

---

## 🏗️ Session 4: Create Unified Expression Tests
**Estimated Time**: 60 minutes  
**Risk Level**: Medium  
**Dependencies**: Session 3 complete  

### Goals
- Create new `test_expressions.py` file
- Move expression-related tests from multiple files
- Consolidate parentheses and complex expression parsing

### Tasks

#### 4.1 Create `test_expressions.py` Structure
```python
"""
Unified expression parsing tests for Hexen parser.

Consolidates:
- Basic expression parsing
- Parentheses handling  
- Complex nested expressions
- Expression precedence validation
"""

from src.hexen.parser import HexenParser

class TestBasicExpressions:
    """Test basic expression parsing"""

class TestParenthesesExpressions:
    """Test parenthesized expressions"""

class TestComplexExpressions:
    """Test complex nested expressions"""

class TestExpressionPrecedence:
    """Test operator precedence in expressions"""

class TestExpressionErrors:
    """Test expression syntax errors"""
```

#### 4.2 Move from `test_parentheses.py`
**Classes to MOVE** (entire file content):
```python
# MOVE these classes FROM test_parentheses.py TO test_expressions.py:

class TestBasicParentheses:  → class TestParenthesesExpressions:
class TestNestedParentheses: → merge into TestParenthesesExpressions  
class TestParenthesesInBlocks: → merge into TestParenthesesExpressions
class TestParenthesesWithTypes: → merge into TestParenthesesExpressions
class TestParenthesesEdgeCases: → class TestExpressionErrors:
```

#### 4.3 Move Complex Expression Tests from `test_binary_ops.py`
**Functions to MOVE**:
```python
# MOVE FROM test_binary_ops.py TO test_expressions.py:

def test_operator_precedence():
    """Test operator precedence in AST construction."""
    # Lines ~70-120

def test_parenthesized_expressions():
    """Test parsing of parenthesized expressions."""
    # Lines ~121-150

def test_complex_expressions():
    """Test parsing of complex nested expressions."""
    # Lines ~190-214
```

#### 4.4 Move Expression Tests from `test_unary_ops.py`
**Classes to MOVE**:
```python
# MOVE FROM test_unary_ops.py TO test_expressions.py:

class TestUnaryOperatorPrecedence:
    """Test operator precedence with unary operators"""
    # Lines ~140-200 (minus logical NOT parts)
```

### Session 4 Validation
```bash
# Validate new file:
python -m pytest test_expressions.py -v
# Validate reduced files still work:
python -m pytest test_binary_ops.py -v
python -m pytest test_unary_ops.py -v
```

### Session 4 Deliverables
- [ ] `test_expressions.py` created with comprehensive expression tests
- [ ] Expression tests moved from `test_parentheses.py`
- [ ] Complex expression tests moved from `test_binary_ops.py`
- [ ] Expression precedence tests moved from `test_unary_ops.py`
- [ ] All tests still pass
- [ ] Ready for Session 5

---

## 🧹 Session 5: Final Cleanup & Validation
**Estimated Time**: 45 minutes  
**Risk Level**: Low  
**Dependencies**: Session 4 complete  

### Goals
- Delete consolidated files
- Standardize remaining test structures
- Run comprehensive validation
- Update documentation

### Tasks

#### 5.1 Delete Consolidated Files
```bash
# Delete these files (content moved to other files):
rm tests/parser/test_parentheses.py
```

#### 5.2 Standardize Test Class Structures
**Pattern to apply** to all remaining files:
```python
class TestFeatureName:
    """Clear description of what's being tested"""
    
    def setup_method(self):
        self.parser = HexenParser()
    
    def test_specific_case(self):
        """Clear description of specific test case"""
        source = """
        // Hexen code here
        """
        
        ast = self.parser.parse(source)
        
        # Consistent assertion patterns
        assert ast["type"] == "program"
        # ... specific assertions
```

#### 5.3 Update File Headers
Add consistent headers to all test files:
```python
"""
Test module for [FEATURE NAME]

Part of the consolidated Hexen parser test suite.
Tests: [specific responsibilities]
"""
```

### Session 5 Validation
```bash
# Run full test suite:
python -m pytest tests/parser/ -v

# Verify file count (should be 10 files):
ls tests/parser/*.py | wc -l

# Check for any import errors:
python -c "import tests.parser.*"
```

### Session 5 Deliverables
- [ ] All unnecessary files deleted
- [ ] Test structures standardized
- [ ] Headers updated
- [ ] Full test suite passes
- [ ] Documentation updated

---

## 📊 Final File Structure

### Remaining Files (10 total):
1. `test_minimal.py` - Basic functionality + function return types
2. `test_variables.py` - Variable declarations (no boolean duplicates)  
3. `test_undef.py` - Undefined variables
4. `test_comments.py` - Comment parsing
5. `test_errors.py` - Error handling
6. `test_expression_type_annotations.py` - Expression type annotations
7. `test_type_annotation_errors.py` - Type annotation errors
8. `test_bool.py` - **Comprehensive boolean suite**
9. `test_binary_ops.py` - **Arithmetic operations only** 
10. `test_unary_ops.py` - **Arithmetic unary operations only**
11. `test_expressions.py` - **NEW: Unified expression parsing**

### Deleted Files (2 total):
- ~~`test_types.py`~~ - Content moved to `test_minimal.py`
- ~~`test_parentheses.py`~~ - Content moved to `test_expressions.py`

---

## 🎯 Recovery/Resume Points

Each session is designed to be independently resumable:

- **After Session 1**: Import statements fixed, baseline established
- **After Session 2**: Boolean tests consolidated
- **After Session 3**: Type annotation tests consolidated  
- **After Session 4**: Expression tests unified
- **After Session 5**: Full consolidation complete

### Validation at Each Point
Each session includes specific validation commands to ensure no regression before proceeding to the next session.

---

## 📈 Success Metrics

### Quantitative Goals:
- **Files reduced**: 12 → 10 (17% reduction)
- **Import consistency**: 100% standardized
- **Test coverage**: 100% maintained
- **Duplicate tests**: 0 remaining

### Qualitative Goals:
- Single responsibility per test file
- Clear test organization
- Consistent code patterns
- Improved maintainability

---

**Total Estimated Time**: 3.5 hours across 5 sessions  
**Risk Level**: Low (incremental with validation at each step)  
**Rollback Strategy**: Each session can be reversed independently 