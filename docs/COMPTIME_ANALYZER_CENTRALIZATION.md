# ComptimeAnalyzer Centralization Plan

## Overview

Analysis of opportunities to centralize comptime type logic from various semantic analyzers into the new `ComptimeAnalyzer` class to reduce code duplication and improve maintainability.

## Current State

The `ComptimeAnalyzer` (`src/hexen/semantic/comptime_analyzer.py`) was introduced to offload comptime-related methods from `BlockAnalyzer`. It currently provides:

- Comptime type preservation analysis
- Compile-time vs runtime block classification
- Comptime-only operation detection
- Runtime variable usage analysis
- Runtime operation context validation

## Analyzers Ready for Centralization

### 1. **BinaryOpsAnalyzer** (`src/hexen/semantic/binary_ops_analyzer.py`)
**Priority: HIGH** - Largest potential reduction (~80-100 lines)

**Comptime logic to extract:**
- Lines 121-154: Complex mixed type operation detection with comptime handling
- Lines 392-413: Extensive comptime type promotion rules
- Lines 202-221: Comptime type handling in equality comparisons  
- Lines 244-258: Comptime type handling in relational comparisons

**Methods to centralize:**
```python
# Add to ComptimeAnalyzer:
def is_mixed_comptime_operation(self, left_type: HexenType, right_type: HexenType) -> bool
def resolve_comptime_binary_operation(self, left_type: HexenType, right_type: HexenType, operator: str) -> HexenType
def can_comptime_types_mix_safely(self, left_type: HexenType, right_type: HexenType, target_type: Optional[HexenType]) -> bool
def get_comptime_promotion_result(self, left_type: HexenType, right_type: HexenType) -> HexenType
```

### 2. **ExpressionAnalyzer** (`src/hexen/semantic/expression_analyzer.py`)
**Priority: HIGH** - Significant reduction (~40-50 lines)

**Comptime logic to extract:**
- Lines 101-106: Direct comptime type handling (`COMPTIME_INT`, `COMPTIME_FLOAT`)
- Lines 277-311: Complex comptime type unification in conditionals
- Lines 294-304: Comptime type compatibility checking
- Lines 295-296: `all_comptime_int`/`all_comptime_float` logic

**Methods to centralize:**
```python
# Add to ComptimeAnalyzer:
def is_comptime_type(self, type: HexenType) -> bool
def unify_comptime_types(self, types: List[HexenType]) -> Optional[HexenType]
def are_all_comptime_compatible(self, types: List[HexenType]) -> bool
def resolve_conditional_comptime_types(self, branch_types: List[HexenType], target_type: Optional[HexenType]) -> HexenType
```

### 3. **DeclarationAnalyzer** (`src/hexen/semantic/declaration_analyzer.py`)
**Priority: MEDIUM** - Moderate reduction (~30-40 lines)

**Comptime logic to extract:**
- Lines 277-286: Comptime literal validation and coercion
- Lines 338-342: Comptime type preservation for `val` declarations
- General comptime type handling throughout variable declarations

**Methods to centralize:**
```python
# Add to ComptimeAnalyzer:
def should_preserve_comptime_type_in_declaration(self, mutability: Mutability, inferred_type: HexenType) -> bool
def validate_comptime_literal_coercion(self, literal_value: Any, from_type: HexenType, to_type: HexenType, source_text: str) -> None
```

### 4. **AssignmentAnalyzer** (`src/hexen/semantic/assignment_analyzer.py`)
**Priority: MEDIUM** - Moderate reduction (~30-40 lines)

**Comptime logic to extract:**
- Lines 134-153: Complex comptime operand detection in binary operations
- Lines 177-186: Comptime literal validation
- Lines 135-141: `has_comptime_operand` logic

**Methods to centralize:**
```python
# Add to ComptimeAnalyzer:
def has_comptime_operands(self, expression: Dict) -> bool
def can_safely_adapt_comptime_types(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool
def analyze_comptime_operands_in_binary_op(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool
```

### 5. **UnaryOpsAnalyzer** (`src/hexen/semantic/unary_ops_analyzer.py`)
**Priority: LOW** - Minimal reduction (~10-15 lines)

**Comptime logic to extract:**
- Lines 82-85: Comptime type preservation for unary minus
- Simple comptime type handling

**Methods to centralize:**
```python
# Add to ComptimeAnalyzer:
def preserve_comptime_type_in_unary_op(self, operand_type: HexenType, operator: str) -> HexenType
```

## Proposed New ComptimeAnalyzer Methods

### Core Type Classification
```python
def is_comptime_type(self, type: HexenType) -> bool:
    """Check if type is a comptime type (COMPTIME_INT or COMPTIME_FLOAT)."""

def is_mixed_comptime_operation(self, left_type: HexenType, right_type: HexenType) -> bool:
    """Detect operations mixing comptime and concrete types."""

def has_comptime_operands(self, expression: Dict) -> bool:
    """Check if expression contains any comptime operands."""
```

### Type Unification & Resolution
```python
def unify_comptime_types(self, types: List[HexenType]) -> Optional[HexenType]:
    """Unify multiple comptime types following promotion rules."""

def resolve_comptime_binary_operation(self, left_type: HexenType, right_type: HexenType, operator: str) -> HexenType:
    """Resolve result type for comptime binary operations."""

def get_comptime_promotion_result(self, left_type: HexenType, right_type: HexenType) -> HexenType:
    """Get promotion result for comptime types (int + float = float)."""
```

### Safety & Validation
```python
def can_comptime_types_mix_safely(self, left_type: HexenType, right_type: HexenType, target_type: Optional[HexenType]) -> bool:
    """Check if comptime types can mix safely with given target context."""

def are_all_comptime_compatible(self, types: List[HexenType]) -> bool:
    """Check if all types are comptime-compatible for unification."""

def requires_explicit_comptime_context(self, expression: Dict) -> bool:
    """Determine if expression requires explicit context for comptime resolution."""
```

### Declaration-Specific
```python
def should_preserve_comptime_type_in_declaration(self, mutability: Mutability, inferred_type: HexenType) -> bool:
    """Determine if comptime type should be preserved in variable declaration."""

def validate_comptime_literal_coercion(self, literal_value: Any, from_type: HexenType, to_type: HexenType, source_text: str) -> None:
    """Validate comptime literal can coerce to target type (move from type_util)."""
```

### Expression Analysis Helpers
```python
def resolve_conditional_comptime_types(self, branch_types: List[HexenType], target_type: Optional[HexenType]) -> HexenType:
    """Resolve comptime types across conditional branches."""

def analyze_comptime_operands_in_binary_op(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool:
    """Analyze if comptime operands in binary operation make it safe."""

def preserve_comptime_type_in_unary_op(self, operand_type: HexenType, operator: str) -> HexenType:
    """Preserve comptime type through unary operations."""
```

## Implementation Priority

### Phase 1: High Impact (Immediate)
1. **BinaryOpsAnalyzer** - Largest code reduction, complex logic centralization
2. **ExpressionAnalyzer** - Significant conditional comptime unification logic

### Phase 2: Medium Impact 
3. **DeclarationAnalyzer** - Comptime preservation and validation logic
4. **AssignmentAnalyzer** - Comptime operand detection logic

### Phase 3: Low Impact
5. **UnaryOpsAnalyzer** - Simple comptime preservation logic

## Estimated Benefits

### Code Reduction
- **Total estimated reduction**: ~180-230 lines across 4 main analyzers
- **BinaryOpsAnalyzer**: ~80-100 lines reduction
- **ExpressionAnalyzer**: ~40-50 lines reduction  
- **DeclarationAnalyzer**: ~30-40 lines reduction
- **AssignmentAnalyzer**: ~30-40 lines reduction
- **UnaryOpsAnalyzer**: ~10-15 lines reduction

### Maintainability Improvements
- **Centralized comptime logic**: All comptime type handling in one place
- **Consistent behavior**: Same logic used across all analyzers
- **Easier testing**: Comptime logic can be unit tested in isolation
- **Reduced duplication**: No more repeated comptime type handling patterns
- **Better documentation**: All comptime rules documented in one class

## Migration Strategy

### Step 1: Add New Methods to ComptimeAnalyzer
- Add all the proposed methods to `ComptimeAnalyzer`
- Include comprehensive unit tests for each method
- Document the centralized comptime logic

### Step 2: Refactor Analyzers (One at a Time)
- Start with `BinaryOpsAnalyzer` (highest impact)
- Replace inline comptime logic with `ComptimeAnalyzer` method calls
- Ensure tests still pass after each analyzer refactor
- Update existing delegation methods as needed

### Step 3: Remove Duplicated Code
- Remove the extracted comptime logic from original analyzers
- Update method signatures to use centralized logic
- Clean up imports and dependencies

### Step 4: Integration Testing
- Run full test suite to ensure no regressions
- Test comptime type behavior across all analyzers
- Validate that centralized logic maintains same semantics

## Methods to Move from type_util.py

The following comptime-specific methods from `src/hexen/semantic/type_util.py` should be moved to `ComptimeAnalyzer` to maintain cohesion and centralize all comptime logic:

### High Priority - Core Comptime Logic
```python
# Lines 183-210: Move to ComptimeAnalyzer
def resolve_comptime_type(self, comptime_type: HexenType, target_type: Optional[HexenType] = None) -> HexenType:
    """Resolve a comptime type to a concrete type based on context."""

# Lines 444-487: Move to ComptimeAnalyzer  
def validate_comptime_literal_coercion(self, value: Union[int, float], from_type: HexenType, to_type: HexenType, source_text: str = None) -> None:
    """Validate comptime literal can be safely coerced to target type."""

# Lines 489-504: Move to ComptimeAnalyzer (used with validate_comptime_literal_coercion)
def extract_literal_info(self, node: Dict) -> tuple[Union[int, float], str]:
    """Extract literal value and source text from AST node."""
```

### Medium Priority - Type Classification 
```python
# Lines 105-116: Consider moving to ComptimeAnalyzer
def is_numeric_type(self, type_: HexenType) -> bool:
    """Check if a type is numeric (integer or float)."""
    
# Lines 118-129: Consider moving to ComptimeAnalyzer
def is_float_type(self, type_: HexenType) -> bool:
    """Check if a type is a float type."""
    
# Lines 131-142: Consider moving to ComptimeAnalyzer  
def is_integer_type(self, type_: HexenType) -> bool:
    """Check if a type is an integer type."""

# Lines 293-330: Move to ComptimeAnalyzer
def is_mixed_type_operation(self, left_type: HexenType, right_type: HexenType) -> bool:
    """Check if an operation involves mixed types that require explicit handling."""
```

### Low Priority - Supporting Functions
```python
# Lines 144-181: Consider moving to ComptimeAnalyzer
def can_coerce(self, from_type: HexenType, to_type: HexenType) -> bool:
    """Check if from_type can be automatically coerced to to_type."""

# Lines 212-223: Keep in type_util or move to ComptimeAnalyzer
def to_float_type(self, type_: HexenType) -> HexenType:
    """Convert a type to its float equivalent."""

# Lines 225-236: Keep in type_util or move to ComptimeAnalyzer
def to_integer_type(self, type_: HexenType) -> HexenType:
    """Convert a type to its integer equivalent."""
```

### Definite Keep in type_util.py
```python
# These should remain in type_util.py as they're general utilities:
def parse_type(type_str: str) -> HexenType  # Line 92
def get_wider_type(left_type: HexenType, right_type: HexenType) -> HexenType  # Line 238
def infer_type_from_value(value: Dict) -> HexenType  # Line 258
def is_string_type(type_: HexenType) -> bool  # Line 332
def is_boolean_type(type_: HexenType) -> bool  # Line 337
def is_concrete_type(type_annotation: str) -> bool  # Line 342
def is_precision_loss_operation(from_type: HexenType, to_type: HexenType) -> bool  # Line 359
def validate_literal_range(value: Union[int, float], target_type: HexenType, source_text: str = None) -> None  # Line 398
```

### Constants to Consider
```python
# These module-level constants may need to be accessible to ComptimeAnalyzer:
COMPTIME_INT_TARGETS: FrozenSet[HexenType]  # Lines 43-50
COMPTIME_FLOAT_TARGETS: FrozenSet[HexenType]  # Lines 52-57
TO_FLOAT_TYPE_MAP: Dict[HexenType, HexenType]  # Lines 60-65
TO_INTEGER_TYPE_MAP: Dict[HexenType, HexenType]  # Lines 67-69
```

## Updated Migration Strategy

### Step 1: Prepare ComptimeAnalyzer
- Add all proposed new methods to `ComptimeAnalyzer`
- **Move core comptime methods from `type_util.py`:**
  - `resolve_comptime_type()` → `ComptimeAnalyzer.resolve_comptime_type()`
  - `validate_comptime_literal_coercion()` → `ComptimeAnalyzer.validate_comptime_literal_coercion()`
  - `extract_literal_info()` → `ComptimeAnalyzer.extract_literal_info()`
  - `is_mixed_type_operation()` → `ComptimeAnalyzer.is_mixed_type_operation()`
- Update imports across the codebase

### Step 2: Update All Analyzers
- Update all analyzers to use `ComptimeAnalyzer` methods instead of `type_util` imports
- Replace direct `type_util` calls with `self.comptime_analyzer` calls
- Update method signatures and delegation patterns

### Step 3: Refactor Individual Analyzers
- Apply the analyzer-specific refactoring as outlined in previous sections
- Ensure all comptime logic uses centralized methods

### Step 4: Clean Up type_util.py
- Remove moved methods from `type_util.py`
- Update any remaining references
- Ensure backward compatibility where needed

## Impact Summary

**Additional Lines Moved from type_util.py**: ~100-120 lines
- Core comptime methods: ~60-80 lines
- Type classification methods: ~40-50 lines

**Total Centralization Impact**:
- **From Analyzers**: ~180-230 lines
- **From type_util.py**: ~100-120 lines  
- **Total**: ~280-350 lines of comptime logic centralized

This creates a comprehensive `ComptimeAnalyzer` that serves as the single source of truth for all comptime type behavior in the Hexen compiler.

## Notes

- The `ComptimeAnalyzer` already has access to `SymbolTable` which is needed for most comptime operations
- Moving methods from `type_util.py` maintains cohesion by centralizing all comptime logic in one place
- Some type utility functions should remain in `type_util.py` as they're general-purpose utilities
- The centralization will make the comptime type system more maintainable and consistent across the codebase
- This refactoring aligns with the goal of making comptime behavior predictable and well-documented

## Current Implementation Status

### ✅ COMPLETED: Steps 1-2 Implementation (Session 4)

**Step 1: Core Infrastructure ✅ COMPLETE**
- ✅ Added 15+ new methods to `ComptimeAnalyzer` for type classification, unification, and validation
- ✅ Moved 4 core comptime methods from `type_util.py`:
  - `resolve_comptime_type()` → `ComptimeAnalyzer.resolve_comptime_type()`
  - `validate_comptime_literal_coercion()` → `ComptimeAnalyzer.validate_comptime_literal_coercion()`
  - `extract_literal_info()` → `ComptimeAnalyzer.extract_literal_info()`
  - `is_mixed_type_operation()` → `ComptimeAnalyzer.is_mixed_type_operation()`
- ✅ Updated imports across codebase and fixed dependency chains
- ✅ All 807 tests passing after infrastructure setup

**Step 2: Analyzer Refactoring ✅ COMPLETE**

🎯 **BinaryOpsAnalyzer ✅ COMPLETE**
- ✅ Added `handle_mixed_type_binary_operation()` - centralizes Pattern 2 & 3 logic 
- ✅ Added `resolve_arithmetic_operation_type()` - handles comptime-specific arithmetic
- ✅ Added `resolve_context_guided_arithmetic()` - manages context-guided resolution
- ✅ Added `handle_mixed_type_comparison()` - centralizes mixed type comparison validation
- ✅ **Reduced complexity by ~60-80 lines** of comptime-specific logic
- ✅ All 18 binary operation tests passing

🎯 **ExpressionAnalyzer ✅ COMPLETE**
- ✅ Added `validate_conditional_branch_compatibility()` - centralizes conditional branch type unification
- ✅ Added `analyze_conditional_branch_with_target_context()` - handles target type propagation
- ✅ Added `check_branch_uses_assign()` - determines assign vs return statement usage
- ✅ Added `_unify_branch_types_without_context()` - private helper for type unification
- ✅ **Reduced complexity by ~40-50 lines** of comptime-specific conditional logic
- ✅ All 59 conditional expression tests passing

🎯 **DeclarationAnalyzer ✅ COMPLETE**
- ✅ Added `validate_variable_declaration_type_compatibility()` - centralizes declaration type validation
- ✅ Added `should_preserve_comptime_for_declaration()` - implements comptime preservation rules  
- ✅ Added `analyze_declaration_type_inference_error()` - provides specific error handling
- ✅ Added `_generate_declaration_precision_loss_error()` - private helper for error messages
- ✅ **Reduced complexity by ~30-40 lines** of comptime-specific declaration logic
- ✅ All 33 declaration and mutability tests passing

### ✅ COMPLETED: Step 2 - Final Analyzers  

🎯 **AssignmentAnalyzer ✅ COMPLETE**
- ✅ Added `can_safely_adapt_comptime_types()` - centralizes comptime adaptation logic from lines 144-153
- ✅ Added `should_skip_precision_loss_check_for_mixed_concrete()` - handles mixed concrete safety checking
- ✅ Added `analyze_assignment_comptime_operands()` - combines complete operand analysis logic  
- ✅ Added `validate_assignment_comptime_literal()` - centralizes literal validation from lines 177-186
- ✅ **Reduced complexity by ~30-40 lines** of comptime-specific assignment logic
- ✅ All 583 semantic tests passing

🎯 **UnaryOpsAnalyzer ✅ COMPLETE**  
- ✅ Refactored to use existing `preserve_comptime_type_in_unary_op()` method
- ✅ **Reduced complexity by ~10-15 lines** of comptime preservation logic (lines 82-85)
- ✅ All 18 unary operation tests passing

### 📊 FINAL Progress Statistics

**Code Centralization Achieved:**
- **Infrastructure**: 19+ new centralized methods + 4 moved from type_util.py
- **BinaryOpsAnalyzer**: ~60-80 lines centralized ✅
- **ExpressionAnalyzer**: ~40-50 lines centralized ✅  
- **DeclarationAnalyzer**: ~30-40 lines centralized ✅
- **AssignmentAnalyzer**: ~30-40 lines centralized ✅
- **UnaryOpsAnalyzer**: ~10-15 lines centralized ✅
- **Total centralized**: ~180-230 lines

**Test Validation:**
- ✅ **807/807 total tests passing** (100% pass rate maintained)
- ✅ **583/583 semantic tests passing** (100% pass rate maintained)
- ✅ **18/18 binary operation tests** passing
- ✅ **59/59 conditional expression tests** passing  
- ✅ **33/33 declaration/mutability tests** passing
- ✅ **36/36 precision loss/conversion tests** passing
- ✅ **18/18 unary operation tests** passing

**Final Status:**
- ✅ **All 5 analyzers refactored successfully** 
- ✅ **All target methods implemented** in ComptimeAnalyzer
- ✅ **100% test success rate** maintained throughout

## ✅ CENTRALIZATION COMPLETE

### 🎉 Project Success Summary

**The Comptime Analyzer Centralization project has been successfully completed!**

All 5 target analyzers have been refactored to use centralized comptime logic:
- **BinaryOpsAnalyzer**: Complex mixed-type operation handling centralized
- **ExpressionAnalyzer**: Conditional branch type unification centralized  
- **DeclarationAnalyzer**: Variable declaration comptime preservation centralized
- **AssignmentAnalyzer**: Comptime operand detection and literal validation centralized
- **UnaryOpsAnalyzer**: Comptime type preservation centralized

### 🎯 Achievements

1. **Code Centralization**: ~180-230 lines of comptime logic centralized into ComptimeAnalyzer
2. **Method Implementation**: 19+ specialized methods added to ComptimeAnalyzer  
3. **Type Utility Migration**: 4 core methods moved from type_util.py for better cohesion
4. **Test Validation**: 100% test success rate maintained (807/807 tests passing)
5. **Code Quality**: All refactoring done without breaking existing functionality
6. **Documentation**: Comprehensive documentation of centralized methods and patterns

### 🚀 Impact

**Maintainability Improvements:**
- **Centralized comptime logic**: All comptime type handling in one place
- **Consistent behavior**: Same logic used across all analyzers  
- **Easier testing**: Comptime logic can be unit tested in isolation
- **Reduced duplication**: No more repeated comptime type handling patterns
- **Better documentation**: All comptime rules documented in one class

**Development Benefits:**
- **Single source of truth**: ComptimeAnalyzer is the definitive source for comptime behavior
- **Extensible design**: Easy to add new comptime features
- **Clear responsibilities**: Each analyzer focuses on its core domain
- **Improved debugging**: Centralized logic easier to trace and fix

---

*Generated during Sessions 1-5 - Complete Comptime Analyzer Centralization Project*  
*Final Update: Session 5 - All analyzers refactored successfully*  
*Status: ✅ 100% COMPLETE - 5/5 analyzers refactored with full test validation*