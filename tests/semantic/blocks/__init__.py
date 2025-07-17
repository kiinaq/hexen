"""
Unified Block System test suite for Hexen semantic analysis

This module contains tests for Hexen's unified block system, described in
UNIFIED_BLOCK_SYSTEM.md. The system uses single { } syntax for all contexts
with context-driven behavior determination.

Test files:
- test_statement_blocks.py: Statement block semantics and scoping
- test_expression_blocks.py: Expression block semantics and returns
- test_function_blocks.py: Function body blocks with validation
- test_block_scoping.py: Universal scope management and complex scenarios

Key features tested:
- Universal scope isolation across all block types
- Context-driven behavior determination
- Integration with variable declarations and assignments
- Complex nested block scenarios
"""
