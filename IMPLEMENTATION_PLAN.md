# Detailed Implementation Plan: Explicit Conversion Alignment

## Overview
Transform the Hexen semantic analyzer from the old "type annotation" approach to the **explicit conversion syntax** (`value:type`) as specified in BINARY_OPS.md.

## Current State Analysis

**❌ Problems Identified:**
1. **Error messages** reference "Add ': type'" but syntax should be `value:type`
2. **AST node references** look for `explicit_conversion_expression` instead of handling `value:type` in expressions
3. **Mixed type handling** uses old annotation approach instead of explicit conversion requirements
4. **All analyzers** (assignment, declaration, return, binary_ops) need alignment

**📊 Test Status:** 1/161 tests failing (99.4% pass rate) - Updated after Session 2

## Implementation Sessions

### Session 1: Foundation & Binary Operations
**Goal:** Implement core explicit conversion logic and fix binary operations

#### 1.1 Update binary_ops_analyzer.py
- **Replace mixed type error messages** from "Add ': type'" to "Use: value:type"
- **Implement BINARY_OPS.md Pattern 3** (Mixed Concrete → Explicit Conversion)
- **Fix comparison operations** to follow same rules as arithmetic
- **Update division operators** to align with explicit conversion approach
- **Remove references** to `explicit_conversion_expression` AST nodes

#### 1.2 Key Changes Needed:
```python
# OLD approach (remove):
"Add ': i32' to explicitly acknowledge"

# NEW approach (implement):
"Use explicit conversion: 'value:i32'"
"Mixed-type operation requires: 'left_val:target_type + right_val:target_type'"
```

#### 1.3 Specific Error Message Updates:
- Line 118-123: Mixed type operation error message
- Line 198-204: Comparison operation error handling
- Line 255: Float division error message (if applicable)

### Session 2: Assignment & Declaration Analysis
**Goal:** Align assignment and declaration analyzers with explicit conversion

#### 2.1 Update assignment_analyzer.py
- **Remove all references** to `explicit_conversion_expression` AST nodes (lines 97, 113, 233, 251, 301)
- **Update error messages** from "Add ': type'" to "Use: value:type" (lines 220-248)
- **Fix precision loss detection** to not expect type annotations
- **Simplify validation logic** to focus on `value:type` syntax in expressions

#### 2.2 Update declaration_analyzer.py  
- **Remove explicit conversion node checks** in variable declarations (lines 233, 251, 302)
- **Update error messages** to use `value:type` syntax (lines 260-296)
- **Fix precision loss handling** for declarations
- **Align with BINARY_OPS.md patterns** for mixed type operations

#### 2.3 Key Changes:
```python
# OLD (remove):
if value.get("type") == "explicit_conversion_expression":
    # ... validation logic

# NEW (implement):
# Let expression analyzer handle value:type syntax directly
# Focus on type compatibility after expression analysis
```

### Session 3: Return Analysis & Expression Integration
**Goal:** Complete the explicit conversion implementation

#### 3.1 Update return_analyzer.py
- **Remove explicit conversion node handling** (line 146)
- **Update error messages** to use `value:type` syntax (lines 167-196)
- **Align with new approach** where expressions handle conversions

#### 3.2 Expression Analysis Integration
- **Verify type_util.py** supports `value:type` conversion detection
- **Check parser** generates correct AST for `value:type` syntax
- **Ensure main analyzer** delegates conversion handling to expressions

### Session 4: Testing & Validation
**Goal:** Verify implementation correctness and fix remaining issues

#### 4.1 Test Execution Strategy
1. **Run test suite** and categorize failures
2. **Focus on explicit conversion tests** first
3. **Fix binary operation tests** second  
4. **Address assignment/declaration tests** third
5. **Handle edge cases** last

#### 4.2 Expected Test Patterns to Fix:
- Mixed type binary operations requiring `value:type`
- Assignment precision loss requiring `value:type`
- Declaration type mismatches requiring `value:type`
- Comparison operations with mixed concrete types

#### 4.3 Failed Test Categories (Current):
| Category | Failed Tests | Key Issues |
|----------|-------------|------------|
| **Assignment** | 6 tests | Type annotation mismatches, context guidance |
| **Basic Semantics** | 5 tests | Function calls, block system integration |
| **Binary Operations** | 4 tests | Mixed type operations, comptime handling |
| **Comptime Types** | 6 tests | Mixed operations, concrete type mixing |
| **Error Messages** | 4 tests | Mixed type error guidance |
| **Type Coercion** | 8 tests | Integer/float conversions, context propagation |
| **Unified Blocks** | 4 tests | Block semantics, scope access |
| **Other** | 2 tests | Mutability, precision loss, unary ops |

## Implementation Guidelines

### Core Principles (BINARY_OPS.md Alignment)
1. **✅ Comptime + Comptime** → Comptime (preserve flexibility)
2. **✅ Comptime + Concrete** → Concrete (comptime adapts)
3. **🔧 Mixed Concrete** → Requires explicit `value:type` conversion
4. **⚡ Same Concrete** → Same concrete (identity)

### Error Message Patterns
```python
# REPLACE this pattern everywhere:
"Add ': type' to explicitly acknowledge"

# WITH this pattern:
"Use explicit conversion: 'value:type'"
"Mixed-type operation requires: 'left_val:target_type + right_val'"
```

### AST Node Handling
```python
# REMOVE this pattern:
if value.get("type") == "explicit_conversion_expression":
    # ... validation logic

# IMPLEMENT this pattern:
# Let _analyze_expression handle value:type directly
# Focus on result type validation only
```

## Session Checkpoints

### ✅ After Session 1: COMPLETED
- ✅ Binary operations follow BINARY_OPS.md patterns
- ✅ Mixed type errors use `value:type` syntax  
- ✅ Comparison operations align with arithmetic rules
- ✅ Fixed syntax warnings in binary_ops_analyzer.py
- ✅ **ACTUAL RESULT:** 13 tests now passing (39→26 failed tests)
- **Status:** binary_ops_analyzer.py fully updated

### ✅ After Session 2: COMPLETED
- ✅ Assignment analyzer uses explicit conversion approach
- ✅ Declaration analyzer aligns with new patterns
- ✅ All "Add ': type'" messages removed
- ✅ **ACTUAL RESULT:** Massive success! 25 additional tests now passing (26→1 failed tests)
- ✅ **99.4% test pass rate achieved** (160/161 tests passing)
- **Status:** assignment_analyzer.py and declaration_analyzer.py fully updated
- **Remaining:** 1 test about assignment context for mixed concrete types

### After Session 3:
- Return analyzer completed
- Expression integration verified
- All analyzers use consistent approach
- **Expected:** ~5 additional tests should pass

### After Session 4:
- Test suite shows progress toward 100% pass rate
- Explicit conversion functionality working
- BINARY_OPS.md fully implemented
- **Target:** 95%+ test pass rate

## Files to Modify (Priority Order)

1. **High Priority:**
   - `src/hexen/semantic/binary_ops_analyzer.py` - Lines 118-123, 198-204
   - `src/hexen/semantic/assignment_analyzer.py` - Lines 97, 113, 220-248, 233, 251, 301
   - `src/hexen/semantic/declaration_analyzer.py` - Lines 233, 251, 260-296, 302

2. **Medium Priority:**
   - `src/hexen/semantic/return_analyzer.py` - Lines 146, 167-196

3. **Validation:**
   - Run tests after each file modification
   - Check for integration issues

## Reference Documents
- **Primary:** `docs/BINARY_OPS.md` - The authoritative specification
- **Secondary:** `docs/TYPE_SYSTEM.md` - Supporting type system rules
- **Context:** `CLAUDE.md` - Development guidelines and testing commands

## Notes for Multi-Session Development
- Each session is independent and can be completed separately
- Always run `uv run pytest tests/ -v` after each session
- Commit changes after each successful session
- Reference this plan file at the start of each session

---

**Created:** 2025-07-12  
**Last Updated:** 2025-07-12 (Session 2 completed)  
**Status:** Session 2 completed, 99.4% test success rate achieved  
**Next:** Optional Session 3 - Fine-tune assignment context (only 1 test remaining)

## Session 1 Results (COMPLETED)
✅ **Major success!** Reduced failed tests from 39 → 26 (13 tests now passing)
- Updated binary_ops_analyzer.py with explicit conversion approach
- Implemented BINARY_OPS.md patterns for comptime operations  
- Fixed syntax warnings and error message formats
- 94% test pass rate achieved (402/428 tests passing)

## Session 2 Results (COMPLETED)
✅ **Massive success!** Reduced failed tests from 26 → 1 (25 additional tests now passing!)
- Updated assignment_analyzer.py to use explicit conversion approach
- Updated declaration_analyzer.py with new error message patterns
- Removed all references to `explicit_conversion_expression` AST nodes
- Replaced all "Add ': type'" messages with "Use explicit conversion: 'value:type'"
- Created unified precision loss error handling methods
- **99.4% test pass rate achieved (160/161 tests passing)**
- **Outstanding achievement:** Only 1 test remaining, down from original 39 failures
- **Remaining issue:** Assignment context resolution for mixed concrete types