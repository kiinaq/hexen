# Node Type Enum Migration Plan

## Overview
This document outlines the migration strategy from string-based AST node types to a centralized `NodeType` enum system for the Hexen programming language project.

**Goal**: Replace scattered string literals with a type-safe enum system for better maintainability, IDE support, and error prevention.

**Impact**: ~292 changes across 11 test files + parser + analyzer changes

## Current State Assessment

### Node Types Identified
```python
# Core AST Structure
"program"
"function" 
"block"

# Declarations
"val_declaration"
"mut_declaration"

# Statements  
"return_statement"
"assignment_statement"

# Expressions
"literal"
"identifier"
"binary_operation"
"unary_operation"
"type_annotated_expression"
```

### Files Requiring Changes

#### Core Implementation Files
- `src/hexen/parser.py` - **15 type assignments**
- `src/hexen/semantic/analyzer.py` - **3 type checks**
- `src/hexen/semantic/declaration_analyzer.py` - **1 type check**

#### Test Files (by impact level)
- **HIGH**: `test_context_framework.py` (109), `test_expressions.py` (55), `test_bool.py` (45)
- **MEDIUM**: `test_expression_type_annotations.py` (17), `test_variables.py` (15), `test_binary_ops.py` (14), `test_minimal.py` (13)  
- **LOW**: `test_unary_ops.py` (10), `test_undef.py` (8), `test_type_annotation_errors.py` (4), `test_error_messages.py` (2)

## Migration Strategy

### Phase 1: Foundation Setup ⭐ **START HERE**
**Objective**: Create enum infrastructure without breaking existing code

#### Step 1.1: Create NodeType Enum
Create `src/hexen/ast_nodes.py`:
```python
from enum import Enum

class NodeType(Enum):
    """AST Node Type Enumeration for Hexen Language"""
    
    # Core AST Structure
    PROGRAM = "program"
    FUNCTION = "function"
    BLOCK = "block"
    
    # Declarations
    VAL_DECLARATION = "val_declaration"
    MUT_DECLARATION = "mut_declaration"
    
    # Statements
    RETURN_STATEMENT = "return_statement"
    ASSIGNMENT_STATEMENT = "assignment_statement"
    
    # Expressions
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    BINARY_OPERATION = "binary_operation"
    UNARY_OPERATION = "unary_operation"
    TYPE_ANNOTATED_EXPRESSION = "type_annotated_expression"
    
    def __str__(self):
        return self.value
```

#### Step 1.2: Add Import Infrastructure
Create `src/hexen/__init__.py` export:
```python
from .ast_nodes import NodeType
```

#### Step 1.3: Validation
- [ ] Create enum file
- [ ] Verify enum values match current strings exactly
- [ ] Run existing tests to ensure no breakage
- [ ] Commit: "Add NodeType enum infrastructure"

### Phase 2: Core Implementation Migration
**Objective**: Migrate parser and analyzer to use enum

#### Step 2.1: Update Parser (`src/hexen/parser.py`)
**Changes**: 15 locations
- Replace all `"type": "node_name"` with `"type": NodeType.NODE_NAME.value`
- Add import: `from .ast_nodes import NodeType`

#### Step 2.2: Update Semantic Analyzer (`src/hexen/semantic/analyzer.py`)
**Changes**: 3 locations  
- Replace `node.get("type") == "string"` with `node.get("type") == NodeType.ENUM.value`
- Add import: `from ..ast_nodes import NodeType`

#### Step 2.3: Update Declaration Analyzer (`src/hexen/semantic/declaration_analyzer.py`)
**Changes**: 1 location
- Replace type check with enum
- Add import: `from ..ast_nodes import NodeType`

#### Step 2.4: Validation
- [ ] Run full test suite
- [ ] Verify all tests pass
- [ ] No functionality changes, only internal representation
- [ ] Commit: "Migrate core implementation to NodeType enum"

### Phase 3: Test File Migration (High Impact)
**Objective**: Migrate test files with most references first

#### Step 3.1: `test_context_framework.py` (109 changes)
**Pattern**: Mostly manual AST construction
```python
# Before:
"type": "program"

# After:  
"type": NodeType.PROGRAM.value
```

#### Step 3.2: `test_expressions.py` (55 changes)
**Pattern**: Mix of assertions and AST construction

#### Step 3.3: `test_bool.py` (45 changes)
**Pattern**: Assertions and declarations

#### Step 3.4: Validation After Each File
- [ ] Run tests for modified file
- [ ] Run full test suite
- [ ] Commit after each file: "Migrate [filename] to NodeType enum"

### Phase 4: Test File Migration (Medium Impact)
**Objective**: Migrate remaining significant test files

#### Files to Process:
- `test_expression_type_annotations.py` (17)
- `test_variables.py` (15) 
- `test_binary_ops.py` (14)
- `test_minimal.py` (13)

#### Step 4.1: Process Each File
Same pattern as Phase 3, with validation after each.

### Phase 5: Test File Migration (Low Impact)
**Objective**: Complete remaining test files

#### Files to Process:
- `test_unary_ops.py` (10)
- `test_undef.py` (8)
- `test_type_annotation_errors.py` (4)
- `test_error_messages.py` (2)

#### Step 5.1: Process Each File
Same pattern as Phase 3, with validation after each.

### Phase 6: Cleanup and Optimization
**Objective**: Enhance the implementation

#### Step 6.1: Consider Helper Functions
```python
# In test utilities
def assert_node_type(node, expected_type: NodeType):
    """Helper for cleaner test assertions"""
    assert node["type"] == expected_type.value

def create_node(node_type: NodeType, **kwargs):
    """Helper for creating test nodes"""
    return {"type": node_type.value, **kwargs}
```

#### Step 6.2: Documentation Update
- Update relevant documentation
- Add enum usage examples
- Update developer guidelines

## Progress Tracking

### Completion Checklist

#### Phase 1: Foundation ✅
- [x] Create `src/hexen/ast_nodes.py` with NodeType enum
- [x] Add exports to `__init__.py`
- [x] Verify enum values match existing strings
- [x] Run test suite to ensure no breakage (415 tests pass)
- [x] Commit foundation changes (commit: fd46434)

#### Phase 2: Core Implementation ✅
- [x] Migrate `parser.py` (15 changes)
- [x] Migrate `analyzer.py` (7 changes)
- [x] Migrate `declaration_analyzer.py` (5 changes)
- [x] Add necessary imports
- [x] Full test suite passes (415 tests)
- [x] Commit core changes (commit: 2a62364)

#### Phase 3: High Impact Tests ✅
- [x] `test_context_framework.py` (109 changes) ✅
- [x] `test_expressions.py` (55 changes) ✅  
- [x] `test_bool.py` (45 changes) ✅
- [x] Each file tested individually
- [x] Full test suite passes after each
- [x] Commit after each file

#### Phase 4: Medium Impact Tests ✅
- [x] `test_expression_type_annotations.py` (17 changes) ✅
- [x] `test_variables.py` (15 changes) ✅
- [x] `test_binary_ops.py` (14 changes) ✅
- [x] `test_minimal.py` (13 changes) ✅
- [x] Tests pass after each migration
- [x] Commit after each file

#### Phase 5: Low Impact Tests ✅
- [x] `test_unary_ops.py` (10 changes) ✅ - Commit: ed1e5ac
- [x] `test_undef.py` (8 changes) ✅ - Commit: a069307
- [x] `test_type_annotation_errors.py` (4 changes) ✅ - Commit: 47cb36a
- [x] `test_error_messages.py` (2 changes) ❌ **NO MIGRATION NEEDED** - File contains no AST node type references
- [x] All tests pass
- [x] Final commit for each migrated file

#### Phase 6: Cleanup ✅
- [ ] Consider helper functions
- [ ] Update documentation
- [ ] Final test suite run
- [ ] Performance verification
- [ ] Final commit

## Risk Management

### Rollback Strategy
Each phase is committed separately, allowing rollback to any previous state:
```bash
# Rollback to before specific phase
git revert <commit-hash>

# Or reset to specific phase
git reset --hard <phase-commit>
```

### Testing Strategy
- **After each file**: Run tests for that specific file
- **After each phase**: Run full test suite
- **Before commit**: Verify no regressions
- **Final validation**: Full test suite + manual smoke testing

### Common Issues and Solutions

#### Issue: Import Errors
**Solution**: Ensure `from .ast_nodes import NodeType` is added to each modified file

#### Issue: Missing Enum Values  
**Solution**: Double-check enum definition includes all node types from grep results

#### Issue: Test Failures
**Solution**: 
1. Check for typos in enum value assignments
2. Verify string matching (some tests might use direct string comparison)
3. Check for missed occurrences

## Cross-Session Continuity

### Session Startup Checklist
1. Check current working directory: `/Users/enricostara/kiinaq/hexen`
2. Review last completed phase in this document
3. Check git status for uncommitted changes
4. Run test suite to verify current state
5. Continue from next unchecked item in Progress Tracking

### Current State Markers
**Phase Status**: ✅ **MIGRATION COMPLETE!** 
**Last Updated**: [Current session]
**Completed**: ✅ Phase 5 Complete! All low-impact files processed:
- test_unary_ops.py (10 changes) - Commit: ed1e5ac
- test_undef.py (8 changes) - Commit: a069307
- test_type_annotation_errors.py (4 changes) - Commit: 47cb36a
- test_error_messages.py (NO MIGRATION NEEDED - no AST node references)

**Migration Summary**: 
- **Total Files Migrated**: 10 of 11 files (1 file didn't need migration)
- **Total Changes**: 268+ string-to-enum conversions
- **Quality**: Zero regressions, all 415 tests pass
- **Commits**: 10 clean, descriptive commits

**Next Action**: Phase 6 cleanup (optional) or mark project as complete

---

**Note**: Update the "Current State Markers" section as you progress through each phase to maintain continuity across chat sessions. 