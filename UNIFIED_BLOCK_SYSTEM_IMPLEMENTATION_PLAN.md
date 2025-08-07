# Unified Block System Implementation Plan

**Project**: Hexen Programming Language  
**Feature**: Enhanced Unified Block System (UNIFIED_BLOCK_SYSTEM.md compliance)  
**Date**: 2025-08-07  
**Based on**: UNIFIED_BLOCK_SYSTEM_GAP_ANALYSIS.md findings

## Overview

This implementation plan addresses the major gaps identified in the gap analysis by implementing the enhanced **compile-time vs runtime block semantics** from the updated `UNIFIED_BLOCK_SYSTEM.md` specification. The work is divided into manageable sessions designed to fit within typical Claude Code context windows.

## 🎯 Implementation Objectives

1. **Implement compile-time vs runtime block detection**
2. **Add function call runtime classification** 
3. **Enable comptime type preservation for compile-time evaluable blocks**
4. **Enhance error messages with context-specific guidance**
5. **Maintain backward compatibility with existing code**

## 📋 Session Structure

Each session is designed to:
- ✅ Fit within 8K-12K lines of code analysis/modification
- ✅ Have clear, testable deliverables
- ✅ Build incrementally on previous sessions
- ✅ Include comprehensive testing
- ✅ Maintain system stability

---

# Session 1: Block Evaluability Detection Infrastructure

**Duration**: 2-3 hours  
**Priority**: P0 (Critical Foundation)  
**Files to modify**: 2-3 core files  
**Lines of code**: ~200-300 new, ~100-150 modified

## 🎯 Session 1 Objectives

1. Create infrastructure to detect compile-time vs runtime evaluability
2. Add block classification enums and data structures
3. Implement basic evaluability detection without function call logic
4. Create foundation for comptime type preservation
5. Add basic tests for detection logic

## 📁 Files Involved

| File | Modification Type | Estimated Changes |
|------|------------------|-------------------|
| `src/hexen/semantic/block_analyzer.py` | Major Enhancement | +150 lines, ~50 modified |
| `src/hexen/semantic/types.py` | Minor Addition | +30 lines (enums) |
| `tests/semantic/test_block_evaluability.py` | New File | +200 lines |

## 🔧 Implementation Tasks

### Task 1.1: Add Block Evaluability Enums
```python
# In src/hexen/semantic/types.py
class BlockEvaluability(Enum):
    """Classification of block evaluability for type preservation"""
    COMPILE_TIME = "compile_time"      # Can preserve comptime types
    RUNTIME = "runtime"                # Requires explicit context (includes mixed operations)
```

### Task 1.2: Implement Basic Detection Infrastructure
```python
# In src/hexen/semantic/block_analyzer.py
def _classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
    """
    Classify block as compile-time or runtime evaluable.
    
    Compile-time evaluable criteria:
    - All operations involve only comptime literals
    - NO conditional expressions (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
    - No runtime function calls (Session 2)
    - No runtime variable usage
    - All computations can be evaluated at compile-time
    """
    
def _has_comptime_only_operations(self, statements: List[Dict]) -> bool:
    """Check if all operations use only comptime types"""
    
def _has_runtime_variables(self, statements: List[Dict]) -> bool:
    """Check for usage of concrete type variables"""
```

### Task 1.3: Update Block Analysis Flow
```python
# Modified: _analyze_statements_with_context
def _analyze_statements_with_context(self, statements: List[Dict], context: str, node: Dict):
    """Enhanced with evaluability classification"""
    if context == "expression":
        # NEW: Classify block evaluability
        evaluability = self._classify_block_evaluability(statements)
        return self._finalize_expression_block_with_evaluability(
            has_assign, has_return, last_statement, node, evaluability
        )
```

### Task 1.4: Create Test Infrastructure
```python
# New file: tests/semantic/test_block_evaluability.py
class TestBasicBlockClassification:
    """Test basic compile-time vs runtime classification"""
    
    def test_comptime_literal_only_block_classified_as_compiletime(self):
        """Test blocks with only comptime literals are compile-time evaluable"""
        
    def test_concrete_variable_usage_classified_as_runtime(self):
        """Test blocks using concrete variables are runtime evaluable"""
        
    def test_mixed_operations_classified_as_runtime(self):
        """Test blocks mixing comptime and concrete types are runtime evaluable"""
```

## ✅ Session 1 Success Criteria

- [ ] Block evaluability classification working for basic cases
- [ ] Comptime-only blocks correctly identified
- [ ] Concrete variable usage correctly triggers runtime classification
- [ ] Test coverage >95% for basic detection logic
- [ ] No regressions in existing block functionality
- [ ] Foundation ready for Session 2 function call detection

## 📊 Session 1 Verification

```bash
# Run existing tests (should all pass)
uv run pytest tests/semantic/blocks/ -v

# Run new tests
uv run pytest tests/semantic/test_block_evaluability.py -v

# Integration test
uv run pytest tests/semantic/test_unified_block_system.py -v
```

---

# Session 2: Function Call & Conditional Detection and Runtime Classification

**Duration**: 3-4 hours  
**Priority**: P0 (Critical)  
**Files to modify**: 3-4 files  
**Lines of code**: ~200-350 new, ~150 modified

## 🎯 Session 2 Objectives

1. Implement function call detection in expressions
2. Implement conditional expression detection in blocks
3. Automatically classify blocks with function calls OR conditionals as runtime evaluable  
4. Add recursive expression analysis for nested function calls and conditionals
5. Enhance error messages for function call and conditional contexts
6. Add comprehensive tests for both function call and conditional scenarios

## 📁 Files Involved

| File | Modification Type | Estimated Changes |
|------|------------------|-------------------|
| `src/hexen/semantic/block_analyzer.py` | Enhancement | +100 lines, ~50 modified |
| `src/hexen/semantic/expression_analyzer.py` | Minor Addition | +50 lines (helper methods) |
| `tests/semantic/test_block_evaluability.py` | Enhancement | +150 lines |
| `tests/semantic/test_function_call_classification.py` | New File | +200 lines |

## 🔧 Implementation Tasks

### Task 2.1: Add Function Call & Conditional Detection
```python
# In src/hexen/semantic/block_analyzer.py
def _contains_runtime_operations(self, statements: List[Dict]) -> bool:
    """
    Detect runtime operations that trigger runtime classification.
    
    Runtime operations include:
    - Function calls (functions always return concrete types)
    - Conditional expressions (all conditionals are runtime per spec)
    - Runtime variable usage (concrete types)
    """
    
def _contains_function_calls(self, statements: List[Dict]) -> bool:
    """Recursively detect function calls in block statements"""
    
def _contains_conditionals(self, statements: List[Dict]) -> bool:
    """Recursively detect conditional expressions in block statements"""
    
def _expression_contains_runtime_operations(self, expression: Dict) -> bool:
    """Recursively analyze expression for function calls and conditionals"""
```

### Task 2.2: Integrate Runtime Operation Detection into Classification
```python
# Enhanced: _classify_block_evaluability
def _classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
    """Enhanced classification with runtime operation detection"""
    
    # Existing logic: check comptime operations, concrete variables
    
    # NEW: Check for runtime operations
    if self._contains_function_calls(statements):
        return BlockEvaluability.RUNTIME  # Functions always return concrete types
        
    if self._contains_conditionals(statements):
        return BlockEvaluability.RUNTIME  # All conditionals are runtime per specification
        
    # Rest of existing logic...
```

### Task 2.3: Add Runtime Operation Context Validation
```python
# New method: _validate_runtime_block_context
def _validate_runtime_block_context(self, node: Dict, reason: str) -> bool:
    """
    Validate that runtime blocks have explicit type context.
    Provides helpful error messages explaining why context is required.
    
    Reasons include:
    - "Contains function calls (functions always return concrete types)"
    - "Contains conditional expressions (all conditionals are runtime)"
    - "Contains runtime variable usage"
    """
```

### Task 2.4: Comprehensive Runtime Operation Tests
```python
# Enhanced file: tests/semantic/test_function_call_classification.py
class TestRuntimeOperationClassification:
    """Test runtime operation detection and classification"""
    
    def test_function_calls_trigger_runtime_classification(self):
        """Test function calls make blocks runtime evaluable"""
        
    def test_conditionals_trigger_runtime_classification(self):
        """Test conditional expressions make blocks runtime evaluable"""
        
    def test_nested_runtime_operations_detected(self):
        """Test nested function calls and conditionals detected"""
        
    def test_combined_runtime_operations(self):
        """Test blocks with both function calls and conditionals"""
```

## ✅ Session 2 Success Criteria

- [ ] All function calls correctly detected in expressions
- [ ] All conditional expressions correctly detected in expressions
- [ ] Blocks with function calls OR conditionals automatically classified as runtime
- [ ] Nested and complex runtime operation patterns handled
- [ ] Error messages explain why runtime context is required (function calls/conditionals)
- [ ] Test coverage >95% for runtime operation detection
- [ ] All existing tests still pass
- [ ] Specification examples with conditionals work correctly

---

# Session 3: Comptime Type Preservation Logic

**Duration**: 3-4 hours  
**Priority**: P0 (Critical)  
**Files to modify**: 4-5 files  
**Lines of code**: ~300-400 new, ~150 modified

## 🎯 Session 3 Objectives

1. Implement comptime type preservation for compile-time evaluable blocks
2. Enable "one computation, multiple uses" pattern from specification
3. Integrate with existing type system and comptime type infrastructure
4. Add explicit context requirement for runtime blocks  
5. Create comprehensive tests for type preservation scenarios

## 📁 Files Involved

| File | Modification Type | Estimated Changes |
|------|------------------|-------------------|
| `src/hexen/semantic/block_analyzer.py` | Major Enhancement | +150 lines, ~75 modified |
| `src/hexen/semantic/expression_analyzer.py` | Enhancement | +100 lines, ~50 modified |
| `src/hexen/semantic/types.py` | Minor Addition | +30 lines |
| `tests/semantic/test_comptime_preservation.py` | New File | +300 lines |
| `tests/semantic/test_unified_block_system.py` | Enhancement | +100 lines |

## 🔧 Implementation Tasks

### Task 3.1: Implement Comptime Type Preservation
```python
# In src/hexen/semantic/block_analyzer.py
def _finalize_expression_block_with_evaluability(
    self, has_assign: bool, has_return: bool, 
    last_statement: Dict, node: Dict, evaluability: BlockEvaluability
) -> HexenType:
    """
    Finalize expression block with evaluability-aware type resolution.
    
    Compile-time evaluable: Preserve comptime types
    Runtime evaluable: Require explicit context, resolve immediately
    """
    
def _analyze_expression_preserve_comptime(self, expression: Dict) -> HexenType:
    """Analyze expression while preserving comptime types"""
    
def _analyze_expression_with_context(self, expression: Dict, target_type: HexenType) -> HexenType:
    """Analyze expression with explicit target context"""
```

### Task 3.2: Add Runtime Block Context Validation
```python
# New validation logic
def _require_explicit_context_for_runtime_block(self, node: Dict, reason: str) -> None:
    """
    Validate runtime blocks have explicit type context.
    Generate helpful error messages with suggestions.
    """
```

### Task 3.3: Integration with Expression Analyzer
```python
# In src/hexen/semantic/expression_analyzer.py
def analyze_block_expression(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """
    Enhanced block expression analysis with comptime preservation.
    Coordinates with block_analyzer for proper type handling.
    """
```

### Task 3.4: Comprehensive Type Preservation Tests
```python
# New file: tests/semantic/test_comptime_preservation.py
class TestComptimePreservation:
    """Test comptime type preservation in compile-time evaluable blocks"""
    
    def test_comptime_block_preserves_flexibility(self):
        """Test compile-time blocks preserve comptime types"""
        source = """
        func test_i32() : i32 = {
            val flexible = {
                val calc = 42 + 100
                assign calc  // Should preserve comptime_int
            }
            return flexible  // comptime_int -> i32
        }
        
        func test_f64() : f64 = {
            val same_calc = {
                val calc = 42 + 100  
                assign calc  // Same source
            }
            return same_calc  // Same source -> f64 (different context!)
        }
        """
        
    def test_runtime_block_requires_context(self):
        """Test runtime blocks require explicit context"""
```

## ✅ Session 3 Success Criteria

- [ ] Compile-time evaluable blocks preserve comptime types
- [ ] Runtime blocks require and validate explicit context
- [ ] "One computation, multiple uses" pattern working
- [ ] Integration with existing type system seamless
- [ ] Test coverage >95% for type preservation logic
- [ ] Performance impact minimal

---

# Session 4: Enhanced Error Messages and Validation

**Duration**: 2-3 hours  
**Priority**: P1 (Important)  
**Files to modify**: 4-6 files  
**Lines of code**: ~200-300 new, ~100 modified

## 🎯 Session 4 Objectives

1. Implement context-specific error messages with actionable guidance
2. Add "Context REQUIRED!" messages for runtime blocks
3. Provide explicit conversion suggestions
4. Enhance validation with specification examples
5. Create comprehensive error message tests

## 📁 Files Involved

| File | Modification Type | Estimated Changes |
|------|------------------|-------------------|
| `src/hexen/semantic/block_analyzer.py` | Enhancement | +100 lines, ~50 modified |
| `src/hexen/semantic/errors.py` | Enhancement | +50 lines |
| `src/hexen/semantic/analyzer.py` | Minor Enhancement | +30 lines |
| `tests/semantic/test_enhanced_error_messages.py` | New File | +250 lines |
| `tests/semantic/test_unified_block_system.py` | Enhancement | +50 lines |

## 🔧 Implementation Tasks

### Task 4.1: Context-Specific Error Messages
```python
# Enhanced error messages with actionable guidance
class BlockAnalysisError:
    @staticmethod
    def runtime_context_required(reason: str, suggestion: str) -> str:
        """Generate context requirement error with suggestion"""
        return f"Runtime block requires explicit type context. {reason}. Suggestion: {suggestion}"
    
    @staticmethod  
    def mixed_types_need_conversion(from_type: str, to_type: str) -> str:
        """Generate conversion requirement error"""
        return f"Branch type {from_type} incompatible with target type {to_type}. Use explicit conversion: value:{to_type}"
```

### Task 4.2: Enhanced Validation Logic
```python
# In src/hexen/semantic/block_analyzer.py
def _validate_runtime_block_with_helpful_errors(self, node: Dict, evaluability: BlockEvaluability) -> None:
    """Provide context-specific error messages for runtime blocks"""
    
    if evaluability == BlockEvaluability.RUNTIME:
        # Check if explicit context provided
        # Generate helpful error message explaining why context needed
        # Suggest specific type annotation syntax
```

### Task 4.3: Comprehensive Error Message Tests
```python
# New file: tests/semantic/test_enhanced_error_messages.py
class TestEnhancedErrorMessages:
    """Test enhanced error messages provide actionable guidance"""
    
    def test_function_call_context_required_message(self):
        """Test runtime block error explains function call requirement"""
        
    def test_mixed_types_conversion_suggestion(self):
        """Test error suggests explicit conversion syntax"""
        
    def test_ambiguity_resolution_guidance(self):
        """Test error explains ambiguity and provides resolution"""
```

## ✅ Session 4 Success Criteria

- [ ] Error messages provide specific, actionable guidance
- [ ] Context requirement errors explain the "why"
- [ ] Conversion suggestions use correct syntax
- [ ] Error messages match specification examples
- [ ] Test coverage >95% for error conditions
- [ ] Error messages help developers understand system

---

# Session 5: Integration Testing and Documentation Updates

**Duration**: 2-3 hours  
**Priority**: P1 (Important)  
**Files to modify**: 5-8 files  
**Lines of code**: ~200-400 new, ~100 modified

## 🎯 Session 5 Objectives

1. Create comprehensive integration tests covering all new features
2. Update documentation with new semantics
3. Add performance benchmarks  
4. Create advanced pattern examples
5. Verify backward compatibility

## 📁 Files Involved

| File | Modification Type | Estimated Changes |
|------|------------------|-------------------|
| `tests/semantic/test_unified_block_integration.py` | New File | +400 lines |
| `CLAUDE.md` | Enhancement | +200 lines |
| `examples/` | New Examples | +300 lines (multiple files) |
| `tests/performance/test_block_performance.py` | New File | +100 lines |

## 🔧 Implementation Tasks

### Task 5.1: Integration Tests
```python
# New file: tests/semantic/test_unified_block_integration.py
class TestUnifiedBlockSystemIntegration:
    """Comprehensive integration tests for enhanced block system"""
    
    def test_complete_specification_examples(self):
        """Test all examples from UNIFIED_BLOCK_SYSTEM.md work correctly"""
        
    def test_complex_nested_scenarios(self):
        """Test complex nesting with mixed evaluability"""
        
    def test_performance_optimization_patterns(self):
        """Test caching and optimization patterns"""
        
    def test_real_world_usage_scenarios(self):
        """Test realistic usage patterns"""
```

### Task 5.2: Documentation Updates
```python
# Update CLAUDE.md with new semantics
## Enhanced Unified Block System

### Compile-Time vs Runtime Distinction

**Key Insight**: Expression blocks fall into two categories:
- **Compile-time evaluable**: Preserve comptime types for maximum flexibility
- **Runtime evaluable**: Require explicit context due to runtime operations

### Function Call Runtime Treatment

All blocks containing function calls are automatically runtime evaluable...
```

### Task 5.3: Advanced Examples
```hexen
// examples/unified_blocks/comptime_preservation.hxn
func demonstrate_comptime_preservation() : void = {
    // Compile-time evaluable block preserves flexibility
    val flexible = {
        val calc = 42 + 100 * 3.14
        assign calc
    }
    
    // Same computation, multiple uses
    val as_f32 : f32 = flexible
    val as_f64 : f64 = flexible  
    val as_i32 : i32 = flexible:i32
}
```

### Task 5.4: Performance Validation
```python
# Performance tests to ensure no regression
def test_block_analysis_performance():
    """Ensure new classification logic doesn't significantly impact performance"""
```

## ✅ Session 5 Success Criteria

- [ ] All specification examples work correctly
- [ ] Documentation accurately reflects new semantics
- [ ] Performance impact <5% regression
- [ ] Backward compatibility maintained 100%
- [ ] Advanced patterns documented with examples
- [ ] Integration test coverage >98%

---

# 📊 Overall Implementation Timeline

| Session | Duration | Cumulative Time | Key Deliverable |
|---------|----------|-----------------|-----------------|
| Session 1 | 2-3 hours | 2-3 hours | Block evaluability detection |
| Session 2 | 3-4 hours | 5-7 hours | Function call & conditional classification |
| Session 3 | 3-4 hours | 8-11 hours | Comptime type preservation |
| Session 4 | 2-3 hours | 10-14 hours | Enhanced error messages |
| Session 5 | 2-3 hours | 12-17 hours | Integration and docs |

**Total Estimated Time**: 12-17 hours across 5 focused sessions

---

# 🔧 Technical Prerequisites

## Before Starting Session 1
1. ✅ Existing codebase analysis complete (gap analysis done)
2. ✅ Current tests all passing (415/415)  
3. ✅ Understanding of existing type system (`HexenType`, comptime types)
4. ✅ Familiarity with current block_analyzer.py structure

## Development Environment
```bash
# Ensure development setup
uv sync --extra dev

# Baseline test run (should be 415/415 passing)
uv run pytest tests/ -v

# Code formatting
uv run ruff format .
uv run ruff check .
```

---

# 🎯 Success Metrics

## Code Quality Metrics
- **Test Coverage**: Maintain >95% for new code
- **Performance**: <5% regression in block analysis
- **Backwards Compatibility**: 100% of existing tests pass
- **Code Quality**: Pass all ruff checks

## Feature Completeness Metrics  
- **Specification Coverage**: All UNIFIED_BLOCK_SYSTEM.md examples work
- **Error Quality**: Error messages provide actionable guidance
- **Type System Integration**: Seamless integration with existing comptime types
- **Documentation Accuracy**: CLAUDE.md reflects actual implementation

## Validation Criteria
- [ ] All 415 existing tests continue to pass
- [ ] New tests achieve >95% coverage
- [ ] All specification examples work correctly
- [ ] Performance benchmarks show <5% regression
- [ ] Error messages match specification guidance
- [ ] Documentation is accurate and comprehensive

---

# 📋 Session Checklist Template

## Pre-Session Setup
- [ ] Previous session tests passing
- [ ] Clean working directory
- [ ] Development environment ready
- [ ] Relevant files identified and reviewed

## During Session
- [ ] Implement core functionality
- [ ] Write comprehensive tests  
- [ ] Validate against specification
- [ ] Check performance impact
- [ ] Update documentation

## Post-Session Validation
- [ ] All new tests passing
- [ ] All existing tests still passing
- [ ] Code quality checks pass
- [ ] Integration tests work
- [ ] Ready for next session

---

This implementation plan provides a clear roadmap for implementing the enhanced unified block system in manageable sessions. Each session builds on the previous one while maintaining system stability and comprehensive test coverage.