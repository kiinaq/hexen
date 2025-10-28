# Hexen Loop System - Semantic Analysis Implementation Plan

**Status:** Planning Phase
**Last Updated:** 2025-10-28
**Prerequisites:** Parser implementation complete (AST nodes defined)
**Target:** Complete semantic validation for loop system

---

## Overview

This document outlines the **semantic analysis** implementation for Hexen's loop system, as specified in `LOOP_SYSTEM.md`. We'll implement type checking, control flow validation, label resolution, and loop expression analysis.

**Implementation Strategy:** Bottom-up, test-driven, following existing semantic analyzer patterns

---

## Architecture Overview

### Current Semantic Analyzer Structure

The semantic analyzer follows a modular callback-based architecture:

```
SemanticAnalyzer (main orchestrator)
├── BinaryOpsAnalyzer
├── UnaryOpsAnalyzer
├── RangeAnalyzer
├── BlockAnalyzer
├── DeclarationAnalyzer
├── AssignmentAnalyzer
├── ReturnAnalyzer
├── ConversionAnalyzer
├── FunctionAnalyzer
├── ExpressionAnalyzer
└── LoopAnalyzer (NEW - to be implemented)
```

### Loop Analyzer Responsibilities

The new `LoopAnalyzer` will handle:

1. **Loop variable type inference** (from iterables)
2. **Loop variable immutability** enforcement
3. **Break/continue validation** (must be inside loops)
4. **Label resolution and validation** (label scope management)
5. **Loop expression mode detection** (statement vs expression)
6. **Unbounded range safety** (forbid in expression mode)
7. **While loop restrictions** (no expression mode)
8. **Nested loop expression validation** (uniform dimensions)
9. **Type annotation requirements** (loop expressions need types)

---

## Phase 1: Loop Context Tracking (Foundation)

### 1.1 Loop Context Stack

**File:** `src/hexen/semantic/analyzer.py`

Add loop context tracking to main analyzer:

```python
class SemanticAnalyzer:
    def __init__(self):
        # ... existing initialization ...

        # Loop context tracking (NEW)
        self.loop_stack: List[LoopContext] = []  # Track nested loops
        self.label_stack: Dict[str, LoopContext] = {}  # Track labels in scope

@dataclass
class LoopContext:
    """Context information for a loop"""
    loop_type: str  # "for-in" or "while"
    label: Optional[str]  # Loop label (if any)
    is_expression_mode: bool  # True if loop produces array
    iterable_type: Optional[HexenType]  # For for-in loops
    variable_name: Optional[str]  # Loop variable name
    variable_type: Optional[HexenType]  # Loop variable type
```

**Test Plan:**
- Verify loop context creation/destruction
- Test nested loop tracking
- Test label scope management

---

## Phase 2: Loop Analyzer Implementation

### 2.1 LoopAnalyzer Class Structure

**File:** `src/hexen/semantic/loop_analyzer.py`

Create the loop analyzer following existing patterns:

```python
"""
Hexen Loop Analyzer

Handles semantic analysis of loop constructs following LOOP_SYSTEM.md.

Responsibilities:
- Loop variable type inference and validation
- Break/continue validation
- Label resolution and scope management
- Loop expression mode detection
- Unbounded range safety checking
- While loop restrictions
- Nested loop expression validation
"""

from typing import Dict, Optional, Callable, List
from .types import HexenType, ArrayType, RangeType
from .symbol_table import SymbolTable
from ..ast_nodes import NodeType


class LoopAnalyzer:
    """
    Analyzes loop constructs (for-in, while, break, continue, labels).

    Key responsibilities:
    1. Type inference for loop variables from iterables
    2. Immutability enforcement for loop variables
    3. Break/continue validation (inside loop check)
    4. Label resolution and validation
    5. Loop expression mode detection
    6. Unbounded range safety (no unbounded in expression mode)
    7. While loop restrictions (no expression mode)
    """

    def __init__(
        self,
        error_callback: Callable[[str, Optional[Dict]], None],
        analyze_expression_callback: Callable[[Dict, Optional[HexenType]], HexenType],
        analyze_statement_callback: Callable[[Dict], None],
        symbol_table: SymbolTable,
        loop_stack: List['LoopContext'],
        label_stack: Dict[str, 'LoopContext'],
        get_current_function_return_type_callback: Callable[[], Optional[HexenType]],
        comptime_analyzer: 'ComptimeAnalyzer',
    ):
        """Initialize loop analyzer with callbacks."""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback
        self._analyze_statement = analyze_statement_callback
        self.symbol_table = symbol_table
        self.loop_stack = loop_stack
        self.label_stack = label_stack
        self._get_current_function_return_type = get_current_function_return_type_callback
        self.comptime_analyzer = comptime_analyzer

    def analyze_for_in_loop(
        self,
        node: Dict,
        expected_type: Optional[HexenType] = None
    ) -> Optional[HexenType]:
        """
        Analyze for-in loop (both statement and expression modes).

        Statement mode: for i in 1..10 { print(i) }
        Expression mode: val arr : [_]i32 = for i in 1..10 { -> i }

        Returns:
            None for statement mode
            ArrayType for expression mode
        """
        pass  # Implementation below

    def analyze_while_loop(self, node: Dict) -> None:
        """
        Analyze while loop (statement mode only).

        While loops cannot be expressions (unbounded iteration risk).
        """
        pass  # Implementation below

    def analyze_break_statement(self, node: Dict) -> None:
        """
        Validate break statement.

        Rules:
        - Must be inside a loop
        - Label (if present) must refer to enclosing loop
        """
        pass  # Implementation below

    def analyze_continue_statement(self, node: Dict) -> None:
        """
        Validate continue statement.

        Rules:
        - Must be inside a loop
        - Label (if present) must refer to enclosing loop
        """
        pass  # Implementation below

    def analyze_labeled_statement(self, node: Dict) -> None:
        """
        Analyze labeled statement.

        Rules:
        - Label must be on a loop (for-in or while)
        - No duplicate labels in same scope
        - Label becomes available for break/continue
        """
        pass  # Implementation below
```

### 2.2 For-In Loop Analysis Implementation

**Key validation steps:**

```python
def analyze_for_in_loop(
    self,
    node: Dict,
    expected_type: Optional[HexenType] = None
) -> Optional[HexenType]:
    """Analyze for-in loop with full validation."""

    # Step 1: Determine loop mode (statement vs expression)
    is_expression_mode = expected_type is not None

    # Step 2: Analyze iterable expression
    variable_name = node.get("variable")
    iterable = node.get("iterable")
    iterable_type = self._analyze_expression(iterable, None)

    # Step 3: Infer loop variable type from iterable
    loop_var_type = self._infer_loop_variable_type(
        iterable_type,
        node.get("variable_type")
    )

    # Step 4: Validate unbounded range safety (expression mode)
    if is_expression_mode:
        self._validate_bounded_iterable(iterable_type, node)

    # Step 5: Create loop context and push to stack
    loop_context = LoopContext(
        loop_type="for-in",
        label=None,  # Labels handled by labeled_statement
        is_expression_mode=is_expression_mode,
        iterable_type=iterable_type,
        variable_name=variable_name,
        variable_type=loop_var_type,
    )
    self.loop_stack.append(loop_context)

    # Step 6: Enter new scope and declare loop variable (immutable!)
    self.symbol_table.enter_scope()
    self.symbol_table.declare_symbol(
        variable_name,
        loop_var_type,
        mutable=False,  # Loop variables always immutable
        node=node
    )

    try:
        # Step 7: Analyze loop body
        body = node.get("body")
        self._analyze_loop_body(body, is_expression_mode, expected_type)

        # Step 8: Validate expression mode requirements
        if is_expression_mode:
            return self._validate_loop_expression(body, expected_type, node)
        else:
            return None
    finally:
        # Step 9: Cleanup (scope and loop context)
        self.symbol_table.exit_scope()
        self.loop_stack.pop()


def _infer_loop_variable_type(
    self,
    iterable_type: HexenType,
    explicit_type_annotation: Optional[str]
) -> HexenType:
    """
    Infer loop variable type from iterable.

    Rules (LOOP_SYSTEM.md):
    - Comptime range → comptime_int or comptime_float
    - Concrete range[T] → T
    - Array [N]T slice → T
    - Explicit annotation → use annotation (with validation)
    """
    # If explicit type annotation, validate and use it
    if explicit_type_annotation:
        explicit_type = self._parse_type_annotation(explicit_type_annotation)
        self._validate_loop_variable_type_compatibility(
            explicit_type, iterable_type
        )
        return explicit_type

    # Infer from iterable type
    if isinstance(iterable_type, RangeType):
        return iterable_type.element_type
    elif isinstance(iterable_type, ArrayType):
        # Array slice returns element type
        return iterable_type.element_type
    elif iterable_type == HexenType.COMPTIME_RANGE:
        return HexenType.COMPTIME_INT
    else:
        self._error(f"Cannot iterate over type: {iterable_type}")
        return HexenType.UNKNOWN


def _validate_bounded_iterable(
    self,
    iterable_type: HexenType,
    node: Dict
) -> None:
    """
    Validate that iterable is bounded (for expression mode safety).

    Rule: Unbounded ranges cannot produce arrays (infinite allocation risk).
    """
    if isinstance(iterable_type, RangeType):
        if iterable_type.is_unbounded_from():
            self._error(
                "Unbounded loop cannot produce array\n"
                f"  Range {iterable_type} has no end bound\n"
                "Help: Use bounded range for array generation: for i in start..end\n"
                "Note: Unbounded ranges (start..) can iterate infinitely but cannot\n"
                "      materialize to arrays (infinite allocation risk)",
                node
            )
```

### 2.3 While Loop Analysis Implementation

```python
def analyze_while_loop(self, node: Dict) -> None:
    """
    Analyze while loop (statement mode only).

    While loops are ALWAYS statements (never expressions).
    Rationale: No bounded iteration guarantee.
    """
    # Step 1: Validate condition type (must be bool)
    condition = node.get("condition")
    condition_type = self._analyze_expression(condition, HexenType.BOOL)

    if condition_type != HexenType.BOOL:
        self._error(
            f"While condition must be of type bool, got {condition_type}\n"
            f"Help: Use explicit comparison: while count > 0",
            condition
        )

    # Step 2: Create loop context
    loop_context = LoopContext(
        loop_type="while",
        label=None,
        is_expression_mode=False,  # Always statement mode
        iterable_type=None,
        variable_name=None,
        variable_type=None,
    )
    self.loop_stack.append(loop_context)

    # Step 3: Enter scope for body
    self.symbol_table.enter_scope()

    try:
        # Step 4: Analyze body statements
        body = node.get("body")
        self._analyze_loop_body(body, is_expression_mode=False, expected_type=None)
    finally:
        # Step 5: Cleanup
        self.symbol_table.exit_scope()
        self.loop_stack.pop()
```

### 2.4 Break/Continue Validation

```python
def analyze_break_statement(self, node: Dict) -> None:
    """
    Validate break statement.

    Rules:
    - Must be inside a loop
    - Label (if present) must refer to enclosing loop
    """
    # Check if inside any loop
    if not self.loop_stack:
        self._error(
            "break statement outside loop\n"
            "Note: break can only be used inside for-in or while loops",
            node
        )
        return

    # Check label (if present)
    label = node.get("label")
    if label:
        if label not in self.label_stack:
            self._error(
                f"Label '{label}' not found\n"
                f"Note: Labels must be defined on enclosing loops",
                node
            )


def analyze_continue_statement(self, node: Dict) -> None:
    """
    Validate continue statement.

    Rules:
    - Must be inside a loop
    - Label (if present) must refer to enclosing loop
    """
    # Check if inside any loop
    if not self.loop_stack:
        self._error(
            "continue statement outside loop\n"
            "Note: continue can only be used inside for-in or while loops",
            node
        )
        return

    # Check label (if present)
    label = node.get("label")
    if label:
        if label not in self.label_stack:
            self._error(
                f"Label '{label}' not found\n"
                f"Note: Labels must be defined on enclosing loops",
                node
            )
```

### 2.5 Label Analysis

```python
def analyze_labeled_statement(self, node: Dict) -> None:
    """
    Analyze labeled statement.

    Rules:
    - Label must be on a loop (for-in or while)
    - No duplicate labels in same scope
    - Label becomes available for break/continue
    """
    label = node.get("label")
    statement = node.get("statement")
    stmt_type = statement.get("type")

    # Validate label is on a loop
    if stmt_type not in [NodeType.FOR_IN_LOOP.value, NodeType.WHILE_LOOP.value]:
        self._error(
            "Labels can only be applied to loops\n"
            f"  {label}: ...\n"
            "Help: Remove label or apply to for-in/while loop",
            node
        )
        return

    # Check for duplicate label
    if label in self.label_stack:
        self._error(
            f"Label '{label}' already defined in this scope\n"
            "Help: Use different label name for inner loop",
            node
        )
        return

    # Add label to stack before analyzing loop
    # (so break/continue inside can reference it)
    loop_context = LoopContext(
        loop_type="for-in" if stmt_type == NodeType.FOR_IN_LOOP.value else "while",
        label=label,
        is_expression_mode=False,  # Will be updated by loop analysis
        iterable_type=None,
        variable_name=None,
        variable_type=None,
    )
    self.label_stack[label] = loop_context

    try:
        # Analyze the loop statement
        if stmt_type == NodeType.FOR_IN_LOOP.value:
            self.analyze_for_in_loop(statement)
        else:
            self.analyze_while_loop(statement)
    finally:
        # Remove label from scope
        del self.label_stack[label]
```

---

## Phase 3: Loop Expression Validation

### 3.1 Type Annotation Requirements

**Rule:** Loop expressions ALWAYS require explicit type annotations (runtime operation).

```python
def _validate_loop_expression_type_annotation(
    self,
    expected_type: Optional[HexenType],
    node: Dict
) -> None:
    """
    Validate that loop expression has explicit type annotation.

    Rule: Loop expressions are runtime operations and require explicit types
    (consistent with functions and conditionals).
    """
    if expected_type is None:
        self._error(
            "Loop expression requires explicit type annotation\n"
            f"  val result = for i in ... {{ -> i }}\n"
            f"               ^^^^^^^^^^^^^^^^^^^^^^^^\n"
            "Help: Add type annotation: val result : [_]i32 = for ...\n"
            "Note: Loop expressions are runtime operations and require explicit types\n"
            "      (consistent with conditionals and function calls)",
            node
        )
```

### 3.2 Loop Body Analysis (Expression Mode)

```python
def _analyze_loop_body(
    self,
    body: Dict,
    is_expression_mode: bool,
    expected_type: Optional[HexenType]
) -> None:
    """
    Analyze loop body with mode-specific validation.

    Statement mode: No special requirements
    Expression mode: Must contain -> statements (value production)
    """
    if body.get("type") != NodeType.BLOCK.value:
        self._error(f"Expected block for loop body")
        return

    statements = body.get("statements", [])

    for stmt in statements:
        stmt_type = stmt.get("type")

        # In expression mode, track -> statements
        if is_expression_mode and stmt_type == "assign_statement":
            # Validate value type matches expected array element type
            if isinstance(expected_type, ArrayType):
                value_expr = stmt.get("expression")
                value_type = self._analyze_expression(
                    value_expr,
                    expected_type.element_type
                )
                # Type validation handled by analyze_expression

        # Analyze statement normally
        self._analyze_statement(stmt)


def _validate_loop_expression(
    self,
    body: Dict,
    expected_type: Optional[HexenType],
    node: Dict
) -> ArrayType:
    """
    Validate loop expression produces correct array type.

    Returns: The array type produced by loop expression
    """
    if not isinstance(expected_type, ArrayType):
        self._error(
            f"Loop expression must have array type annotation, got {expected_type}",
            node
        )
        return ArrayType(HexenType.UNKNOWN, None)

    # Loop expressions produce arrays
    return expected_type
```

### 3.3 Nested Loop Expression Validation

```python
def _validate_nested_loop_expression(
    self,
    outer_type: ArrayType,
    inner_loop: Dict,
    node: Dict
) -> None:
    """
    Validate nested loop expression dimensions.

    Rules:
    - Type context flows inward: [_][_]i32 → outer produces [_]i32
    - Inner loop produces element type
    - All rows must have uniform dimensions (runtime check)
    """
    if not isinstance(outer_type, ArrayType):
        return

    # Inner type context = outer element type
    inner_expected_type = outer_type.element_type

    # Validate inner loop matches expected type
    inner_result = self.analyze_for_in_loop(inner_loop, inner_expected_type)

    # Uniform dimension validation happens at runtime
    # (we can't check statically with filtering/break)
```

---

## Phase 4: Integration with Main Analyzer

### 4.1 Add LoopAnalyzer to SemanticAnalyzer

**File:** `src/hexen/semantic/analyzer.py`

```python
def _initialize_analyzers(self):
    """Initialize all specialized analyzers with callbacks."""
    # ... existing analyzers ...

    # Initialize loop analyzer (NEW)
    self.loop_analyzer = LoopAnalyzer(
        error_callback=self._error,
        analyze_expression_callback=self._analyze_expression,
        analyze_statement_callback=self._analyze_statement,
        symbol_table=self.symbol_table,
        loop_stack=self.loop_stack,
        label_stack=self.label_stack,
        get_current_function_return_type_callback=lambda: self.current_function_return_type,
        comptime_analyzer=self.comptime_analyzer,
    )
```

### 4.2 Add Loop Analysis to Statement Handler

```python
def _analyze_statement(self, stmt: Dict):
    """Analyze a statement node."""
    stmt_type = stmt.get("type")

    # ... existing statement types ...

    # Loop statements (NEW)
    elif stmt_type == NodeType.FOR_IN_LOOP.value:
        self.loop_analyzer.analyze_for_in_loop(stmt)

    elif stmt_type == NodeType.WHILE_LOOP.value:
        self.loop_analyzer.analyze_while_loop(stmt)

    elif stmt_type == NodeType.BREAK_STATEMENT.value:
        self.loop_analyzer.analyze_break_statement(stmt)

    elif stmt_type == NodeType.CONTINUE_STATEMENT.value:
        self.loop_analyzer.analyze_continue_statement(stmt)

    elif stmt_type == NodeType.LABELED_STATEMENT.value:
        self.loop_analyzer.analyze_labeled_statement(stmt)
```

### 4.3 Add Loop Expression Support

```python
def _analyze_expression(
    self,
    expr: Dict,
    expected_type: Optional[HexenType] = None
) -> HexenType:
    """Analyze an expression and return its type."""
    expr_type = expr.get("type")

    # ... existing expression types ...

    # Loop expressions (NEW)
    if expr_type == NodeType.FOR_IN_LOOP.value:
        return self.loop_analyzer.analyze_for_in_loop(expr, expected_type)

    # While loops cannot be expressions
    if expr_type == NodeType.WHILE_LOOP.value:
        self._error(
            "While loops cannot be used in expression context\n"
            "Help: Use for-in loop for array generation: for i in range { -> value }\n"
            "Note: While loops are statements only (cannot produce values)\n"
            "      Rationale: Unbounded iteration risk (no comptime-checkable bounds)",
            expr
        )
        return HexenType.UNKNOWN
```

---

## Phase 5: Semantic Tests (Comprehensive Coverage)

### 5.1 Test File Structure

**Directory:** `tests/semantic/`

Create comprehensive test files:

```
tests/semantic/
├── test_for_in_semantics.py           # For-in loop validation
├── test_while_semantics.py            # While loop validation
├── test_loop_control_flow.py          # break/continue validation
├── test_loop_labels.py                # Label resolution
├── test_loop_expressions.py           # Loop expression type checking
├── test_loop_variables.py             # Loop variable type inference
└── test_nested_loop_expressions.py    # Nested loops and matrices
```

### 5.2 For-In Loop Semantic Tests

**File:** `tests/semantic/test_for_in_semantics.py`

```python
def test_loop_variable_type_inference_from_range():
    """Test: for i in range[i32] { } → i is i32"""
    code = """
    val r : range[i32] = 1..10
    for i in r {
        val x : i32 = i  // i should be i32
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_loop_variable_immutability():
    """Test: Loop variables are immutable"""
    code = """
    for i in 1..10 {
        i = 42  // Error: loop variable immutable
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "immutable" in errors[0].message.lower()


def test_loop_variable_explicit_type_annotation():
    """Test: for i : i64 in 1..10 { } → i is i64"""
    code = """
    for i : i64 in 1..10 {
        val x : i64 = i  // i should be i64
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_comptime_range_adapts_to_loop_variable():
    """Test: Comptime range adapts to explicit type"""
    code = """
    for i : i32 in 1..10 {
        val x : i32 = i  // Should work
    }
    for j : i64 in 1..10 {
        val y : i64 = j  // Should also work
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_array_iteration_infers_element_type():
    """Test: for elem in data[..] → elem type = array element type"""
    code = """
    val data : [_]f64 = [1.0, 2.0, 3.0]
    for elem in data[..] {
        val x : f64 = elem  // elem should be f64
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_unbounded_range_forbidden_in_expression_mode():
    """Test: Unbounded range cannot produce array"""
    code = """
    val infinite : [_]i32 = for i in 5.. {  // Error!
        if i > 100 { break }
        -> i
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "unbounded" in errors[0].message.lower()


def test_unbounded_range_allowed_in_statement_mode():
    """Test: Unbounded range OK in statement mode"""
    code = """
    for i in 5.. {
        if i > 100 { break }
        print(i)
    }
    """
    errors = analyze(code)
    assert len(errors) == 0
```

### 5.3 Loop Expression Tests

**File:** `tests/semantic/test_loop_expressions.py`

```python
def test_loop_expression_requires_type_annotation():
    """Test: Loop expression must have explicit type"""
    code = """
    val result = for i in 1..10 { -> i }  // Error: missing type
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "type annotation" in errors[0].message.lower()


def test_loop_expression_with_type_annotation():
    """Test: Loop expression with type annotation"""
    code = """
    val result : [_]i32 = for i in 1..10 {
        -> i * i
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_loop_expression_value_type_mismatch():
    """Test: Loop expression value must match element type"""
    code = """
    val result : [_]i32 = for i in 1..10 {
        -> i:f64  // Error: expected i32, got f64
    }
    """
    errors = analyze(code)
    assert len(errors) == 1


def test_loop_expression_filtering():
    """Test: Filtering in loop expressions"""
    code = """
    val evens : [_]i32 = for i in 1..20 {
        if i % 2 == 0 {
            -> i
        }
        // Odd numbers skipped (no value produced)
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_loop_expression_with_break():
    """Test: Break in loop expression returns partial array"""
    code = """
    val partial : [_]i32 = for i in 1..100 {
        if i > 50 {
            break
        }
        -> i
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_loop_expression_with_continue():
    """Test: Continue skips value production"""
    code = """
    val filtered : [_]i32 = for i in 1..10 {
        if i % 2 == 0 {
            continue
        }
        -> i
    }
    """
    errors = analyze(code)
    assert len(errors) == 0
```

### 5.4 While Loop Tests

**File:** `tests/semantic/test_while_semantics.py`

```python
def test_while_condition_must_be_bool():
    """Test: While condition must be bool type"""
    code = """
    val count : i32 = 10
    while count {  // Error: i32 cannot be bool
        count = count - 1
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "bool" in errors[0].message.lower()


def test_while_explicit_bool_condition():
    """Test: Explicit bool condition works"""
    code = """
    mut count : i32 = 0
    while count < 10 {
        count = count + 1
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_while_true_infinite_loop():
    """Test: while true { } is valid"""
    code = """
    while true {
        break
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_while_cannot_be_expression():
    """Test: While loops cannot produce values"""
    code = """
    val result : [_]i32 = while condition {  // Error!
        -> value
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "expression" in errors[0].message.lower()
```

### 5.5 Break/Continue Tests

**File:** `tests/semantic/test_loop_control_flow.py`

```python
def test_break_outside_loop_error():
    """Test: break outside loop is error"""
    code = """
    val x : i32 = if true {
        break  // Error!
    } else {
        -> 42
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "outside loop" in errors[0].message.lower()


def test_continue_outside_loop_error():
    """Test: continue outside loop is error"""
    code = """
    func test() : i32 = {
        continue  // Error!
        return 42
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "outside loop" in errors[0].message.lower()


def test_break_in_for_in_loop():
    """Test: break works in for-in loop"""
    code = """
    for i in 1..100 {
        if i > 50 {
            break
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_continue_in_while_loop():
    """Test: continue works in while loop"""
    code = """
    mut i : i32 = 0
    while i < 20 {
        i = i + 1
        if i % 3 == 0 {
            continue
        }
        print(i)
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_labeled_break():
    """Test: Labeled break to outer loop"""
    code = """
    outer: for i in 1..10 {
        inner: for j in 1..10 {
            if i * j > 50 {
                break outer
            }
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_break_to_nonexistent_label():
    """Test: break to undefined label is error"""
    code = """
    for i in 1..10 {
        break nonexistent  // Error!
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "not found" in errors[0].message.lower()
```

### 5.6 Label Tests

**File:** `tests/semantic/test_loop_labels.py`

```python
def test_label_on_for_in_loop():
    """Test: Label on for-in loop"""
    code = """
    outer: for i in 1..10 {
        print(i)
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_label_on_while_loop():
    """Test: Label on while loop"""
    code = """
    outer: while condition {
        break outer
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_label_on_non_loop_error():
    """Test: Label on non-loop statement is error"""
    code = """
    mylabel: val x : i32 = 42  // Error!
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "only be applied to loops" in errors[0].message.lower()


def test_duplicate_label_error():
    """Test: Duplicate labels in nested loops"""
    code = """
    outer: for i in 1..10 {
        outer: for j in 1..10 {  // Error: duplicate label
            break outer
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 1
    assert "already defined" in errors[0].message.lower()


def test_reuse_label_in_sibling_loops():
    """Test: Reusing label in sibling loops is OK"""
    code = """
    outer: for i in 1..10 {
        // First use of 'outer'
    }
    outer: for i in 1..10 {  // OK: previous label out of scope
        // Second use of 'outer'
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_label_scope_ends_after_loop():
    """Test: Label goes out of scope after loop"""
    code = """
    outer: for i in 1..10 {
        break outer  // OK
    }
    break outer  // Error: label no longer in scope
    """
    errors = analyze(code)
    assert len(errors) == 1
```

### 5.7 Nested Loop Expression Tests

**File:** `tests/semantic/test_nested_loop_expressions.py`

```python
def test_nested_loop_expression_2d():
    """Test: 2D array generation"""
    code = """
    val matrix : [_][_]i32 = for i in 1..3 {
        -> for j in 1..4 {
            -> i * j
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_nested_loop_expression_3d():
    """Test: 3D tensor generation"""
    code = """
    val tensor : [_][_][_]i32 = for i in 1..2 {
        -> for j in 1..3 {
            -> for k in 1..4 {
                -> i * j * k
            }
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_nested_loop_type_mismatch():
    """Test: Inner loop type must match outer element type"""
    code = """
    val bad : [_][_]i32 = for i in 1..3 {
        -> for j in 1..4 {
            -> j:f64  // Error: expected i32, got f64
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 1


def test_nested_loop_dimension_mismatch():
    """Test: Nesting level must match type"""
    code = """
    val bad : [_][_]i32 = for i in 1..3 {
        -> i  // Error: expected [_]i32, got i32
    }
    """
    errors = analyze(code)
    assert len(errors) == 1


def test_filtered_outer_loop():
    """Test: Filtering outer loop (skip rows)"""
    code = """
    val filtered : [_][_]i32 = for i in 1..10 {
        if i % 2 == 0 {
            -> for j in 1..5 {
                -> i * j
            }
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 0


def test_identity_matrix_generation():
    """Test: Identity matrix with conditionals"""
    code = """
    val identity : [_][_]i32 = for i in 0..5 {
        -> for j in 0..5 {
            if i == j {
                -> 1
            } else {
                -> 0
            }
        }
    }
    """
    errors = analyze(code)
    assert len(errors) == 0
```

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Add loop context tracking to `SemanticAnalyzer`
- [ ] Define `LoopContext` dataclass
- [ ] Add `loop_stack` and `label_stack` to analyzer
- [ ] Test context creation/destruction

### Phase 2: LoopAnalyzer
- [ ] Create `loop_analyzer.py` file
- [ ] Implement `LoopAnalyzer` class structure
- [ ] Implement `analyze_for_in_loop()`
- [ ] Implement `analyze_while_loop()`
- [ ] Implement `analyze_break_statement()`
- [ ] Implement `analyze_continue_statement()`
- [ ] Implement `analyze_labeled_statement()`
- [ ] Implement loop variable type inference
- [ ] Implement unbounded range validation
- [ ] Implement loop body analysis

### Phase 3: Loop Expressions
- [ ] Implement loop expression type validation
- [ ] Implement type annotation requirement check
- [ ] Implement nested loop expression validation
- [ ] Implement filtering support
- [ ] Implement break/continue in expressions

### Phase 4: Integration
- [ ] Add `LoopAnalyzer` to `_initialize_analyzers()`
- [ ] Add loop statement handlers to `_analyze_statement()`
- [ ] Add loop expression handler to `_analyze_expression()`
- [ ] Test integration with existing analyzers

### Phase 5: Semantic Tests
- [ ] Write for-in loop tests (30+ tests)
- [ ] Write while loop tests (15+ tests)
- [ ] Write control flow tests (20+ tests)
- [ ] Write label tests (15+ tests)
- [ ] Write loop expression tests (25+ tests)
- [ ] Write loop variable tests (15+ tests)
- [ ] Write nested loop tests (20+ tests)
- [ ] Achieve 100% coverage of loop features

---

## Success Criteria

**Semantic analysis is complete when:**

1. ✅ All loop AST nodes properly validated
2. ✅ Loop variable type inference working
3. ✅ Loop variable immutability enforced
4. ✅ Break/continue validation working
5. ✅ Label resolution and validation working
6. ✅ Loop expression mode detection working
7. ✅ Unbounded range safety enforced
8. ✅ While loop restrictions enforced
9. ✅ Nested loop expressions validated
10. ✅ 140+ semantic tests passing
11. ✅ All examples from `LOOP_SYSTEM.md` validate correctly
12. ✅ Error messages match specification
13. ✅ No regressions in existing tests

---

## Timeline Estimate

| Phase | Estimated Time | Complexity |
|-------|---------------|------------|
| Phase 1: Foundation | 2-3 hours | Low-Medium |
| Phase 2: LoopAnalyzer | 8-12 hours | High |
| Phase 3: Loop Expressions | 4-6 hours | Medium-High |
| Phase 4: Integration | 2-3 hours | Medium |
| Phase 5: Semantic Tests | 10-15 hours | High |
| **Total** | **26-39 hours** | **High** |

---

## Next Steps

1. **Phase 1:** Add loop context tracking infrastructure
2. **Phase 2:** Implement `LoopAnalyzer` with all validation logic
3. **Phase 3:** Add loop expression support
4. **Phase 4:** Integrate with main semantic analyzer
5. **Phase 5:** Write comprehensive semantic tests

**After semantic analysis is complete:**
- Update documentation with any implementation insights
- Consider codegen implementation (LLVM IR generation)
- Explore optimization opportunities (loop unrolling, etc.)

---

`★ Insight ─────────────────────────────────────`
**Loop System Semantic Complexity:**

1. **Dual-Mode Analysis** - For-in loops operate in two modes (statement vs expression), requiring careful context detection and different validation rules for each mode.

2. **Type Flow Architecture** - Loop variable types flow FROM iterables TO loop bodies, creating a dependency chain that must be properly tracked through the type system.

3. **Safety Through Constraints** - The unbounded range restriction in expression mode exemplifies Hexen's philosophy: prevent footguns at compile time rather than runtime.
`─────────────────────────────────────────────────`

**Last Updated:** 2025-10-28
**Status:** Ready to implement semantic analysis!
