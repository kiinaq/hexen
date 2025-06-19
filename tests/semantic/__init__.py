"""
Semantic analysis test package for Hexen

Contains comprehensive tests for semantic analysis functionality organized by feature:

Core Integration Tests:
- test_basic_semantics.py - Cross-cutting semantic validation and integration tests

Core Type System Tests (NEW - Complete TYPE_SYSTEM.md Coverage):
- test_type_annotations.py - Type annotation system and explicit acknowledgment rules
- test_precision_loss.py - "Explicit Danger, Implicit Safety" principle enforcement
- test_mutability.py - Comprehensive val/mut variable system testing
- test_type_coercion.py - Regular type coercion and widening rules
- test_error_messages.py - Error message consistency and helpfulness

Advanced Type System Tests:
- test_f32_comptime.py - Numeric types and comptime type coercion system
- test_context_framework.py - Context-guided type resolution framework
- test_binary_ops.py - Binary operations and mixed-type expression handling
- test_unary_ops.py - Unary operations semantic analysis
- test_negative_numbers.py - Negative number literal handling

Feature-Specific Tests:
- test_assignment.py - Assignment statement validation and mutability enforcement
- test_bool.py - Boolean type semantics and validation
- test_bare_returns.py - Bare return statement handling in void functions
- test_statement_blocks.py - Statement block scoping and execution
- test_expression_blocks.py - Expression block evaluation and return requirements

These tests operate on ASTs produced by the parser and validate the semantic
correctness of Hexen programs including type checking, symbol resolution,
scope management, and use-before-definition detection. The new type system tests
provide comprehensive coverage of the sophisticated type system described in
TYPE_SYSTEM.md, ensuring full compliance with the "Explicit Danger, Implicit Safety"
design philosophy.
"""
