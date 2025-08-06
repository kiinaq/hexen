# Hexen Conditional System Implementation Plan 🦉

*Multi-Session Implementation Strategy*

> **Implementation Note**: This document provides a detailed implementation plan for Hexen's conditional system, broken into manageable sessions that fit within context size windows while ensuring comprehensive test coverage and systematic progress.

## Overview

This plan implements the conditional system as specified in [CONDITIONAL_SYSTEM.md](CONDITIONAL_SYSTEM.md), following Hexen's unified design philosophy. The implementation spans grammar updates, parser enhancements, semantic analysis, and comprehensive testing.

## Implementation Architecture

### Core Components to Implement

1. **Grammar Extensions** (`hexen.lark`)
   - Conditional statement syntax (`if`, `else if`, `else`)
   - Boolean expression parsing
   - Integration with existing block syntax

2. **AST Node Extensions** (`ast_nodes.py`)
   - `IfStatement` node for conditional statements
   - `ConditionalExpression` node for conditional expressions
   - Condition and branch representation

3. **Parser Extensions** (`parser.py`)
   - Conditional syntax parsing
   - Context detection (statement vs expression)
   - Error handling for malformed conditionals

4. **Semantic Analysis Extensions** (`semantic/`)
   - Condition type validation (must be `bool`)
   - Branch analysis for statements vs expressions
   - Scope management for conditional branches
   - Type resolution across branches

5. **Test Coverage** (`tests/`)
   - Parser tests for syntax validation
   - Semantic tests for type checking and scoping
   - Integration tests with unified block system
   - Error condition testing

## Session-Based Implementation Plan

### Session 1: Grammar and Basic AST (Foundation) ✅ COMPLETED
**Context Usage**: ~3,000 tokens  
**Goal**: Establish basic conditional syntax parsing

#### Tasks Completed:
1. **✅ Updated Grammar** (`hexen.lark`)
   - Added conditional_stmt rule for if/else if/else syntax
   - Added else_clause rule supporting both else-if and final else
   - Integrated conditional statements with existing statement grammar
   - Added if/else keywords to reserved identifier list

2. **✅ Created AST Nodes** (`ast_nodes.py`)
   - Added CONDITIONAL_STATEMENT node type for if statements
   - Added ELSE_CLAUSE node type for else and else-if clauses

3. **✅ Implemented Parser Support** (`parser.py`)
   - Added conditional_stmt transformer for parsing if statements
   - Added else_clause transformer for parsing else/else-if branches
   - Handles both conditional statements and else-if chains
   - Proper error handling for malformed conditional syntax

4. **✅ Foundation Tests** (`tests/parser/test_conditionals.py`)
   - **Parser Tests**: 14 comprehensive tests covering all conditional syntax variations
   - **Semantic Foundation Tests**: AST node creation, visitor pattern integration
   - **Error Handling Tests**: Malformed syntax, missing braces, invalid structure
   - **Advanced Tests**: Nested conditionals, logical conditions, empty branches

**Success Criteria - All Met**:
- ✅ Can parse: `if condition { statements }`
- ✅ Can parse: `if condition { } else { }`
- ✅ Can parse: `if condition1 { } else if condition2 { } else { }`
- ✅ All parser tests pass for basic syntax (14/14)
- ✅ Zero regressions (224/224 existing parser tests still pass)

**Session 1 Results**:
- **Conditional Tests**: 14/14 passing ✅
- **Total Parser Tests**: 224/224 passing ✅
- **Commit**: b721d34 - Session 1: Conditional System Foundation completed

### Session 2: Statement Context Analysis (Core Semantics) ✅ COMPLETED
**Context Usage**: ~3,500 tokens  
**Goal**: Implement conditional statements with proper semantic analysis

#### Tasks Completed:
1. **✅ Semantic Analyzer Core** (`semantic/analyzer.py`)
   - Added conditional statement handler to statement dispatch (analyzer.py:240)
   - Implemented `_analyze_conditional_statement()` method with full branch analysis
   - Integrated with existing unified block system patterns

2. **✅ Condition Analysis** 
   - Boolean condition type checking with clear error messages
   - Proper integration with expression analysis framework
   - Type validation for all conditional expressions (comparisons, logical ops)

3. **✅ Statement Branch Analysis**
   - Each branch analyzed as statement block with scope isolation
   - Scope management using `enter_scope()/exit_scope()` pattern
   - Support for early returns within branches
   - Integration with existing block analysis system

4. **✅ Comprehensive Statement Context Tests** (`tests/semantic/test_conditionals.py`)
   - **TestConditionalStatements**: Basic if/else/else-if functionality (4 tests)
   - **TestConditionValidation**: Boolean type checking and error cases (4 tests)
   - **TestScopeManagement**: Variable isolation and lexical scoping (4 tests)
   - **TestIntegrationWithFunctions**: Function context and return statements (3 tests)
   - **TestErrorConditions**: Error handling and validation (2 tests)
   - **TestAdvancedPatterns**: Complex conditional patterns (2 tests)

**Success Criteria - All Met**:
- ✅ Conditional statements work in function bodies
- ✅ Boolean conditions are properly validated (with helpful error messages)
- ✅ Variables are scoped correctly within branches (enter/exit scope isolation)
- ✅ Non-boolean conditions produce helpful errors
- ✅ Early returns work within conditional branches
- ✅ Full integration with existing semantic analysis framework

**Session 2 Results**:
- **Conditional Tests**: 19/19 passing ✅
- **Total Semantic Tests**: 491/491 passing ✅ (no regressions)
- **Total Parser Tests**: 224/224 passing ✅ (foundation preserved)
- **Commit**: b153b0f - Session 2: Statement Context Analysis completed

### Session 3: Expression Context Analysis (Advanced Semantics) ✅ COMPLETED
**Context Usage**: ~4,000 tokens  
**Goal**: Implement conditional expressions with assign/return semantics

#### Tasks Completed:
1. **✅ Expression Context Detection**
   - Added conditional expressions to expression analyzer dispatch method
   - Implemented `_analyze_conditional_expression()` method in ExpressionAnalyzer
   - Added conditional_stmt to primary rule in grammar for expression parsing

2. **✅ Expression Branch Analysis**
   - Implemented sophisticated branch type analysis distinguishing assign vs return branches
   - Added `_branch_uses_assign()` helper method to detect branch termination type
   - Type compatibility validation across only assign branches (return branches exit early)
   - Full integration with existing unified block system assign/return validation

3. **✅ Return Statement Integration**  
   - Complete support for `return` statements in conditional expression branches
   - Early function exit semantics properly handled (branches with return don't contribute to conditional type)
   - Seamless integration with existing return analysis and type validation

4. **✅ Expression Context Tests** (15 comprehensive tests added)
   - **TestConditionalExpressions**: Basic conditional expressions, comptime values, variables, early returns, else-if chains, mixed return/assign (6 tests)
   - **TestConditionalExpressionErrors**: Non-boolean conditions and error validation (1 test)
   - **TestConditionalExpressionTypeResolution**: Comptime type unification, context propagation, nested conditionals (3 tests)
   - **TestConditionalIntegrationPatterns**: Expression blocks, function calls, binary operations (3 tests)

**Success Criteria - All Met**:
- ✅ Conditional expressions work: `val x = if cond { assign y } else { assign z }`
- ✅ Mixed assign/return branches work: `val x = if error { return early } else { assign value }`  
- ✅ Early returns work: branches with `return` exit function early and don't contribute to conditional type
- ✅ Type compatibility enforced across assign branches only
- ✅ Full integration with comptime type system and context-guided resolution
- ✅ Comprehensive error handling and validation

**Session 3 Results**:
- **Conditional Tests**: 32/32 passing ✅ (19 existing + 13 new expression tests)
- **Total Semantic Tests**: 504/504 passing ✅ (no regressions)
- **Total Parser Tests**: 224/224 passing ✅ (grammar changes work correctly)
- **Implementation**: Expression context analysis fully working with assign/return dual capability

### Session 4: Type System Integration (Advanced Types)
**Estimated Context Usage**: ~3,500 tokens  
**Goal**: Full integration with comptime types and explicit conversions

#### Tasks:
1. **Comptime Type Integration**
   - Runtime treatment of all conditionals
   - Explicit context requirements for conditional expressions
   - Integration with existing comptime type rules

2. **Mixed Type Branch Analysis**
   - Explicit conversion requirements across branches
   - Comptime type adaptation within branches
   - Error messages for incompatible branch types

3. **Context Propagation**
   - Target type context propagation to branches
   - Integration with variable declaration context
   - Function parameter context integration

4. **Type Integration Tests**
   - **Comptime Type Tests**: Runtime treatment of all conditionals, comptime literal handling within branches
   - **Mixed Type Tests**: Concrete type mixing across branches, explicit conversion requirements
   - **Context Propagation Tests**: Target type context to branches, variable declaration context integration
   - **Type Compatibility Tests**: Cross-branch type validation, type unification algorithms
   - **Conversion Requirement Tests**: Mixed concrete types needing explicit conversions, error messages for missing conversions
   - **Integration Tests**: Conditionals with `val`/`mut` declarations, function parameter contexts

**Success Criteria**:
- Conditional expressions require explicit context when runtime
- Comptime types work properly within branches
- Explicit conversions required for mixed concrete types
- Type context propagates correctly from target

### Session 5: Advanced Patterns and Integration (Polish)
**Estimated Context Usage**: ~3,000 tokens
**Goal**: Support advanced patterns and comprehensive integration

#### Tasks:
1. **Nested Conditional Support**
   - Conditionals within expression blocks
   - Nested conditional expressions
   - Complex scoping scenarios

2. **Error Message Improvement**
   - Context-specific error messages
   - Helpful suggestions for common mistakes
   - Integration with existing error patterns

3. **Integration Testing**
   - Conditionals with unified block system
   - Conditionals with binary operations
   - Conditionals with function calls

4. **Advanced Pattern Tests**
   - **Validation Pattern Tests**: Early return error handling, input validation chains
   - **Caching Pattern Tests**: Performance optimization patterns, conditional computation caching
   - **Fallback Pattern Tests**: Configuration loading, graceful degradation patterns
   - **Complex Nesting Tests**: Deeply nested conditionals, mixed statement/expression contexts
   - **Integration Pattern Tests**: Conditionals with binary operations, function calls, expression blocks
   - **Real-World Scenario Tests**: All patterns from CONDITIONAL_SYSTEM.md specification

**Success Criteria**:
- All advanced patterns from CONDITIONAL_SYSTEM.md work
- Error messages are helpful and consistent
- Full integration with existing language features
- Comprehensive test coverage achieved

## Detailed Implementation Specifications

### Grammar Extensions Required

```lark
// Add to hexen.lark

// Conditional Statement
conditional_stmt: "if" expression "{" statement* "}" else_clause*

else_clause: "else" "if" expression "{" statement* "}"
           | "else" "{" statement* "}"

// Integration with existing statement rule
statement: variable_declaration
         | assignment
         | expression_stmt
         | return_stmt
         | block_stmt
         | conditional_stmt    // New addition

// Boolean expressions (if not already comprehensive)
comparison: expression ("==" | "!=" | "<" | ">" | "<=" | ">=") expression
logical_and: expression "&&" expression  
logical_or: expression "||" expression
logical_not: "!" expression
```

### AST Node Structure

```python
# Add to ast_nodes.py

@dataclass
class ConditionalStatement(ASTNode):
    """Conditional statement (if/else if/else)"""
    condition: ASTNode
    if_branch: ASTNode  # Block node
    else_clauses: List['ElseClause']
    
    def accept(self, visitor):
        return visitor.visit_conditional_statement(self)

@dataclass 
class ElseClause(ASTNode):
    """Else or else-if clause"""
    condition: Optional[ASTNode]  # None for final else
    branch: ASTNode  # Block node
    
    def accept(self, visitor):
        return visitor.visit_else_clause(self)
```

### Semantic Analysis Integration Points

```python
# Add to semantic/analyzer.py

def visit_conditional_statement(self, node: ConditionalStatement):
    """Analyze conditional statement"""
    # 1. Analyze condition - must be bool
    # 2. Create new scope for if branch  
    # 3. Analyze if branch as statement block
    # 4. Analyze each else clause similarly
    # 5. Restore previous scope

def analyze_conditional_expression(self, node: ConditionalStatement, target_type: Optional[Type]):
    """Analyze conditional in expression context"""
    # 1. Analyze condition - must be bool
    # 2. Analyze each branch as expression block
    # 3. Validate all branches assign or return
    # 4. Check type compatibility across branches
    # 5. Return unified type
```

### Comprehensive Test Structure

```python
# tests/semantic/test_conditionals.py

class TestConditionalStatements:
    # Basic functionality tests
    def test_basic_if_statement(self):
        # Test: if condition { statements }
        
    def test_if_else_statement(self):
        # Test: if condition { } else { }
        
    def test_else_if_chain(self):
        # Test: if { } else if { } else { }
        
    def test_nested_conditionals(self):
        # Test: conditionals within conditionals
        
    # Condition validation tests
    def test_boolean_condition_validation(self):
        # Test: condition must be bool type
        
    def test_comparison_conditions(self):
        # Test: x > 0, name == "admin", etc.
        
    def test_logical_conditions(self):
        # Test: cond1 && cond2, cond1 || cond2, !cond
        
    def test_invalid_condition_types(self):
        # Test: error for i32, string, etc. as conditions
        
    # Scope management tests
    def test_scope_isolation(self):
        # Test: variables scoped to branches
        
    def test_variable_shadowing(self):
        # Test: inner variables shadow outer variables
        
    def test_lexical_scoping(self):
        # Test: access to outer scope variables
        
    def test_scope_cleanup(self):
        # Test: variables cleaned up after branch exit
        
    # Integration tests
    def test_conditionals_in_functions(self):
        # Test: conditionals within function bodies
        
    def test_return_statements_in_conditionals(self):
        # Test: early returns from within conditionals
        
    def test_empty_branches(self):
        # Test: branches with no statements

class TestConditionalExpressions:
    # Basic expression functionality
    def test_basic_conditional_expression(self):
        # Test: val x = if cond { assign y } else { assign z }
        
    def test_conditional_with_comptime_values(self):
        # Test: if cond { assign 42 } else { assign 100 }
        
    def test_conditional_with_variables(self):
        # Test: if cond { assign var1 } else { assign var2 }
        
    # Branch coverage validation
    def test_all_branches_must_assign(self):
        # Test: error if branch doesn't assign
        
    def test_missing_else_branch_error(self):
        # Test: error for incomplete branch coverage
        
    def test_partial_assignment_error(self):
        # Test: error when some branches don't assign
        
    # Early return support
    def test_early_return_support(self):
        # Test: return statements in branches
        
    def test_return_vs_assign_mixing(self):
        # Test: some branches return, others assign
        
    def test_return_type_validation(self):
        # Test: return types match function signature
        
    # Type compatibility
    def test_type_compatibility_across_branches(self):
        # Test: branch types must be compatible
        
    def test_compatible_comptime_types(self):
        # Test: comptime_int + comptime_float compatibility
        
    def test_incompatible_concrete_types(self):
        # Test: error for i32 vs string without conversion
        
    # Context detection
    def test_expression_context_detection(self):
        # Test: proper detection of expression context
        
    def test_statement_vs_expression_disambiguation(self):
        # Test: same syntax, different contexts
        
    # Nested expressions
    def test_nested_conditional_expressions(self):
        # Test: conditionals within conditionals in expression context
        
    def test_conditionals_in_expression_blocks(self):
        # Test: conditionals within { assign ... } blocks

class TestTypeSystemIntegration:
    # Comptime type integration
    def test_comptime_types_in_conditionals(self):
        # Test: comptime_int, comptime_float handling
        
    def test_runtime_treatment_of_conditionals(self):
        # Test: all conditionals treated as runtime
        
    def test_comptime_literal_adaptation(self):
        # Test: literals adapt within branches
        
    # Mixed concrete types
    def test_explicit_conversions_required(self):
        # Test: mixed concrete types need conversions
        
    def test_conversion_error_messages(self):
        # Test: helpful error messages for missing conversions
        
    def test_cross_branch_conversion_consistency(self):
        # Test: consistent conversion requirements across branches
        
    # Context propagation
    def test_target_type_context_propagation(self):
        # Test: target type propagates to branches
        
    def test_variable_declaration_context(self):
        # Test: val x : i32 = if... provides i32 context
        
    def test_function_parameter_context(self):
        # Test: function(if...) provides parameter type context
        
    def test_function_return_context(self):
        # Test: return if... uses function return type context
        
    # Val vs mut integration
    def test_val_with_conditional_expressions(self):
        # Test: val preserves comptime flexibility where possible
        
    def test_mut_with_conditional_expressions(self):
        # Test: mut requires explicit type context
        
    def test_conditional_expression_runtime_blocks(self):
        # Test: runtime conditionals require explicit context

class TestAdvancedPatterns:
    # Validation patterns
    def test_input_validation_pattern(self):
        # Test: early return validation chains
        
    def test_guard_clause_pattern(self):
        # Test: if error { return ... } patterns
        
    def test_nested_validation_pattern(self):
        # Test: multiple validation levels
        
    # Performance patterns
    def test_caching_pattern(self):
        # Test: if cached { return ... } else { assign compute() }
        
    def test_short_circuit_pattern(self):
        # Test: optimization via early returns
        
    def test_conditional_computation_pattern(self):
        # Test: expensive operations only when needed
        
    # Configuration patterns
    def test_fallback_configuration_pattern(self):
        # Test: primary -> fallback -> default patterns
        
    def test_conditional_feature_selection(self):
        # Test: feature flags controlling behavior
        
    # Error handling patterns
    def test_graceful_degradation_pattern(self):
        # Test: fallback to simpler behavior on errors
        
    def test_error_propagation_pattern(self):
        # Test: error values bubbling up through returns
        
    # Integration patterns
    def test_conditionals_with_binary_operations(self):
        # Test: if (a + b) > c { ... }
        
    def test_conditionals_with_function_calls(self):
        # Test: if validate(input) { ... }
        
    def test_conditionals_with_expression_blocks(self):
        # Test: complex integration scenarios
        
    # Real-world scenarios
    def test_complete_validation_function(self):
        # Test: full function using validation patterns
        
    def test_complete_configuration_loader(self):
        # Test: full function using fallback patterns
        
    def test_complete_calculation_function(self):
        # Test: full function using conditional computation

class TestErrorHandling:
    # Syntax error handling
    def test_missing_braces_error(self):
        # Test: helpful error for missing { }
        
    def test_malformed_else_if_error(self):
        # Test: error for malformed else-if chains
        
    def test_invalid_condition_syntax_error(self):
        # Test: error for malformed conditions
        
    # Semantic error handling
    def test_non_boolean_condition_error(self):
        # Test: clear error message for wrong condition types
        
    def test_missing_assign_error(self):
        # Test: helpful error for missing assign in expressions
        
    def test_type_mismatch_across_branches_error(self):
        # Test: clear error for incompatible branch types
        
    def test_undefined_variable_in_condition_error(self):
        # Test: error for undefined variables in conditions
        
    # Context error handling
    def test_missing_explicit_context_error(self):
        # Test: error when runtime conditional needs explicit context
        
    def test_context_propagation_failure_error(self):
        # Test: error when context cannot be determined
        
    # Error message quality
    def test_error_message_suggestions(self):
        # Test: error messages include helpful suggestions
        
    def test_error_location_accuracy(self):
        # Test: errors point to correct source locations
        
    def test_error_message_consistency(self):
        # Test: consistent error message formatting

class TestRegressionPrevention:
    # Existing functionality preservation
    def test_unified_block_system_still_works(self):
        # Test: no breaking changes to block system
        
    def test_expression_blocks_still_work(self):
        # Test: existing expression block patterns work
        
    def test_type_system_still_works(self):
        # Test: existing type system patterns work
        
    def test_binary_operations_still_work(self):
        # Test: existing binary operation patterns work
        
    # Performance regression
    def test_parsing_performance_maintained(self):
        # Test: no significant parsing slowdown
        
    def test_semantic_analysis_performance_maintained(self):
        # Test: no significant semantic analysis slowdown
```

## Implementation Dependencies

### Prerequisites
- Unified block system must be working
- Expression analysis must support `assign` statements
- Return statement analysis must be complete
- Boolean operations and comparisons must work

### Integration Points
- **Type System**: Follow [TYPE_SYSTEM.md](TYPE_SYSTEM.md) rules for explicit conversions
- **Block System**: Use [UNIFIED_BLOCK_SYSTEM.md](UNIFIED_BLOCK_SYSTEM.md) scope patterns
- **Binary Operations**: Integrate with [BINARY_OPS.md](BINARY_OPS.md) for condition expressions

## Error Handling Strategy

### Error Categories to Handle

1. **Syntax Errors**
   - Missing braces in conditional branches
   - Malformed else-if chains
   - Invalid condition syntax

2. **Semantic Errors**
   - Non-boolean conditions
   - Missing assign in expression branches
   - Type incompatibility across branches
   - Undefined variables in conditions

3. **Context Errors**
   - Conditional expressions without proper context
   - Mixed runtime/comptime without explicit types

### Error Message Templates

```python
# Condition type error
f"Condition must be of type bool, got {condition_type}"

# Missing assign in expression branch
f"All branches in conditional expression must assign a value or return from function"

# Type incompatibility across branches  
f"Incompatible types across conditional branches: {branch1_type} vs {branch2_type}"

# Context requirement for runtime conditionals
f"Conditional expression with runtime elements requires explicit type context"
```

## Testing Strategy

### Test Categories

1. **Unit Tests** (per session)
   - Parser unit tests for syntax
   - Semantic analyzer unit tests for logic
   - AST node creation tests

2. **Integration Tests** (session 5)
   - Conditionals with expression blocks
   - Conditionals with function calls
   - Conditionals with binary operations

3. **Pattern Tests** (session 5)
   - Validation patterns from CONDITIONAL_SYSTEM.md
   - Error handling patterns
   - Advanced usage patterns

4. **Regression Tests** (all sessions)
   - Ensure existing functionality still works
   - No breaking changes to unified block system

### Coverage Targets
- **Parser**: 100% coverage of conditional syntax variations (if, if-else, else-if chains)
- **Semantics**: 100% coverage of error conditions, type checking, and scope management
- **Type Integration**: 100% coverage of comptime/runtime interaction and explicit conversions
- **Pattern Coverage**: All patterns from CONDITIONAL_SYSTEM.md specification implemented and tested
- **Error Handling**: 100% coverage of error cases with quality message validation
- **Regression Prevention**: No degradation in existing functionality performance or correctness

## Success Metrics

### Per-Session Metrics
- All session tests pass (100%)
- No regression in existing tests
- Code quality maintained (type hints, documentation)

### Overall Success Criteria
- All examples from CONDITIONAL_SYSTEM.md work correctly
- Conditional statements integrate seamlessly with existing code
- Conditional expressions work in all documented contexts
- Error messages are helpful and consistent
- Performance impact is minimal (no significant slowdown)

## Risk Mitigation

### Known Risks
1. **Scope Complexity**: Conditional scoping interacts with existing block scoping
2. **Type System Integration**: Complex interaction with comptime/runtime distinction  
3. **Parser Ambiguity**: Conditional expressions vs statements context detection

### Mitigation Strategies  
1. **Incremental Testing**: Each session has comprehensive tests
2. **Existing Pattern Reuse**: Leverage unified block system patterns
3. **Clear Context Rules**: Well-defined rules for statement vs expression context

## Session Progress Tracking

### ✅ Session 1 - COMPLETED (b721d34)
**Foundation**: Grammar, AST, and Parser Implementation
- **Status**: All tasks completed successfully
- **Tests**: 14/14 conditional parser tests passing
- **Regressions**: 0 (224/224 existing parser tests still pass)
- **Commit**: b721d34 - Session 1: Conditional System Foundation

### ✅ Session 2 - COMPLETED (b153b0f)
**Core Semantics**: Statement Context Analysis
- **Status**: All tasks completed successfully
- **Tests**: 19/19 conditional semantic tests passing
- **Regressions**: 0 (491/491 semantic tests + 224/224 parser tests still pass)
- **Commit**: b153b0f - Session 2: Statement Context Analysis

### ✅ Session 3 - COMPLETED 
**Advanced Semantics**: Expression Context Analysis  
- **Status**: All tasks completed successfully
- **Tests**: 32/32 conditional tests passing (19 existing + 13 new)
- **Regressions**: 0 (504/504 semantic tests + 224/224 parser tests still pass)
- **Implementation**: Expression context analysis with assign/return dual capability working perfectly

### ⏳ Session 4 - PENDING  
**Type Integration**: Advanced Types
- **Prerequisites**: Sessions 1-3 completed

### ⏳ Session 5 - PENDING
**Polish**: Advanced Patterns and Integration
- **Prerequisites**: Sessions 1-4 completed

## Implementation Approach

### Session Coordination
- **Single Branch**: All sessions use `conditional-system-implementation` branch
- **Complete Coverage**: Each session has full test coverage for its scope  
- **Independent Commits**: Each session commits separately for progress tracking
- **Incremental Integration**: Each session builds on previous work

---

**Next Step**: Begin Session 3 - Expression Context Analysis (Advanced Semantics)