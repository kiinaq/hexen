"""
Precision loss test suite for Hexen semantic analysis

This module contains tests for precision loss detection, following the
"Explicit Danger, Implicit Safety" principle:
- Safe operations are implicit (no explicit conversion needed)
- Dangerous operations require explicit conversion via value:type syntax

Test files:
- test_integer_precision.py: Integer precision loss scenarios
- test_float_precision.py: Float precision loss scenarios
- test_mixed_precision.py: Mixed-type precision loss scenarios
- test_safe_operations.py: Safe operations requiring no conversion
"""
