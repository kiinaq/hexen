"""
Semantic analysis test package for Hexen

Contains comprehensive tests for semantic analysis functionality organized by feature:

Core Integration Tests:
- test_basic_semantics.py - Cross-cutting semantic validation and integration tests

Feature-Specific Tests:
- test_assignment.py - Assignment statement validation and mutability enforcement
- test_f32_comptime.py - Numeric types and comptime type coercion system
- test_bool.py - Boolean type semantics and validation
- test_bare_returns.py - Bare return statement handling in void functions
- test_statement_blocks.py - Statement block scoping and execution
- test_expression_blocks.py - Expression block evaluation and return requirements

These tests operate on ASTs produced by the parser and validate the semantic
correctness of Hexen programs including type checking, symbol resolution,
scope management, and use-before-definition detection.
"""
