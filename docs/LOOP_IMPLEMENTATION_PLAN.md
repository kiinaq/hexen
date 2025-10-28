# Hexen Loop System - Parser Implementation Plan

**Status:** Planning Phase
**Last Updated:** 2025-10-28
**Target:** Parser + AST + Tests (Semantic analysis comes later)

---

## Overview

This document outlines the implementation plan for the **parser side** of Hexen's loop system, as specified in `LOOP_SYSTEM.md`. We'll implement grammar rules, AST nodes, parser logic, and comprehensive tests.

**Implementation Strategy:** Bottom-up, incremental, test-driven

---

## Phase 1: Core AST Nodes (Foundation)

### 1.1 Loop AST Node Types

**File:** `src/hexen/ast_nodes.py`

Add the following AST node classes:

```python
@dataclass
class ForInLoop:
    """For-in loop: for variable in iterable { body }"""
    variable: str                    # Loop variable name
    variable_type: Optional[str]     # Optional type annotation (e.g., "i32")
    iterable: Any                    # Expression (range, array slice, etc.)
    body: List[Any]                  # Loop body statements
    label: Optional[str] = None      # Optional loop label
    line: int = 0
    column: int = 0

@dataclass
class WhileLoop:
    """While loop: while condition { body }"""
    condition: Any                   # Boolean expression
    body: List[Any]                  # Loop body statements
    label: Optional[str] = None      # Optional loop label
    line: int = 0
    column: int = 0

@dataclass
class BreakStatement:
    """Break statement: break or break label"""
    label: Optional[str] = None      # Optional label to break to
    line: int = 0
    column: int = 0

@dataclass
class ContinueStatement:
    """Continue statement: continue or continue label"""
    label: Optional[str] = None      # Optional label to continue to
    line: int = 0
    column: int = 0

@dataclass
class LabeledStatement:
    """Labeled statement: label: statement"""
    label: str                       # Label name
    statement: Any                   # The statement being labeled
    line: int = 0
    column: int = 0
```

**Test Plan:**
- Verify AST nodes can be instantiated with correct fields
- Test optional fields (label, variable_type)
- Test default values

---

## Phase 2: Grammar Rules (Syntax Definition)

### 2.1 For-In Loop Grammar

**File:** `src/hexen/hexen.lark`

Add grammar rules for for-in loops:

```lark
// For-in loop syntax
for_in_loop: "for" IDENTIFIER [":" type_annotation] "in" expression block

// Type annotation for loop variable (optional)
type_annotation: IDENTIFIER ("[" ("_" | NUMBER) "]")*
```

**Examples to Support:**
```hexen
for i in 1..10 { }                  // Basic for-in
for i : i32 in 1..10 { }            // With type annotation
for elem in data[..] { }            // Array iteration
for i in 1..10 { -> i }             // Expression mode
```

### 2.2 While Loop Grammar

```lark
// While loop syntax
while_loop: "while" expression block
```

**Examples to Support:**
```hexen
while condition { }                 // Basic while
while true { }                      // Infinite loop
while count < 10 { }                // Conditional
```

### 2.3 Break/Continue Grammar

```lark
// Control flow statements
break_stmt: "break" [IDENTIFIER]    // break or break label
continue_stmt: "continue" [IDENTIFIER]  // continue or continue label
```

**Examples to Support:**
```hexen
break                               // Simple break
break outer                         // Labeled break
continue                            // Simple continue
continue outer                      // Labeled continue
```

### 2.4 Label Grammar

```lark
// Labeled statements
labeled_stmt: IDENTIFIER ":" statement

// Statement needs to be updated to include loops
statement: labeled_stmt
         | for_in_loop
         | while_loop
         | break_stmt
         | continue_stmt
         | ... (existing statements)
```

**Examples to Support:**
```hexen
outer: for i in 1..10 { }           // Labeled for-in
outer: while condition { }          // Labeled while
```

**Test Plan:**
- Parse basic loop syntax (no labels)
- Parse loops with type annotations
- Parse nested loops
- Parse break/continue statements
- Parse labeled statements
- Test error cases (syntax errors)

---

## Phase 3: Parser Logic (AST Construction)

### 3.1 Parser Transformer Methods

**File:** `src/hexen/parser.py`

Add transformer methods to construct AST nodes:

```python
class HexenTransformer(Transformer):
    # ... existing methods ...

    def for_in_loop(self, items):
        """Transform for-in loop grammar rule to ForInLoop AST node"""
        # items structure:
        # [variable, type_annotation?, iterable, block]
        variable = str(items[0])

        # Check if type annotation present
        if len(items) == 4:  # Has type annotation
            variable_type = str(items[1])
            iterable = items[2]
            body = items[3]
        else:  # No type annotation
            variable_type = None
            iterable = items[1]
            body = items[2]

        return ForInLoop(
            variable=variable,
            variable_type=variable_type,
            iterable=iterable,
            body=body,
            line=items[0].line,
            column=items[0].column
        )

    def while_loop(self, items):
        """Transform while loop grammar rule to WhileLoop AST node"""
        # items structure: [condition, block]
        condition = items[0]
        body = items[1]

        return WhileLoop(
            condition=condition,
            body=body,
            line=items[0].line,
            column=items[0].column
        )

    def break_stmt(self, items):
        """Transform break statement to BreakStatement AST node"""
        label = str(items[0]) if items else None
        return BreakStatement(
            label=label,
            line=items[0].line if items else 0,
            column=items[0].column if items else 0
        )

    def continue_stmt(self, items):
        """Transform continue statement to ContinueStatement AST node"""
        label = str(items[0]) if items else None
        return ContinueStatement(
            label=label,
            line=items[0].line if items else 0,
            column=items[0].column if items else 0
        )

    def labeled_stmt(self, items):
        """Transform labeled statement to LabeledStatement AST node"""
        # items structure: [label, statement]
        label = str(items[0])
        statement = items[1]

        return LabeledStatement(
            label=label,
            statement=statement,
            line=items[0].line,
            column=items[0].column
        )
```

**Test Plan:**
- Verify correct AST node construction for each loop type
- Test optional fields (type annotations, labels)
- Test nested structures
- Verify line/column tracking

---

## Phase 4: Parser Tests (Comprehensive Coverage)

### 4.1 Test File Structure

**Directory:** `tests/parser/`

Create test files:

```
tests/parser/
├── test_for_in_loops.py          # For-in loop parsing
├── test_while_loops.py            # While loop parsing
├── test_loop_control_flow.py      # break/continue
├── test_loop_labels.py            # Labeled loops
└── test_loop_expressions.py       # Loop expressions (-> syntax)
```

### 4.2 For-In Loop Tests

**File:** `tests/parser/test_for_in_loops.py`

Test cases to cover:

```python
def test_basic_for_in_loop():
    """Test: for i in 1..10 { }"""
    code = """
    for i in 1..10 {
        print(i)
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[0], ForInLoop)
    assert ast.statements[0].variable == "i"
    assert ast.statements[0].variable_type is None

def test_for_in_with_type_annotation():
    """Test: for i : i32 in 1..10 { }"""
    code = """
    for i : i32 in 1..10 {
        print(i)
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[0], ForInLoop)
    assert ast.statements[0].variable == "i"
    assert ast.statements[0].variable_type == "i32"

def test_for_in_array_iteration():
    """Test: for elem in data[..] { }"""
    code = """
    val data : [_]i32 = [1, 2, 3]
    for elem in data[..] {
        print(elem)
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[1], ForInLoop)
    assert ast.statements[1].variable == "elem"

def test_for_in_expression_mode():
    """Test: val result : [_]i32 = for i in 1..10 { -> i }"""
    code = """
    val result : [_]i32 = for i in 1..10 {
        -> i
    }
    """
    ast = parse(code)
    # Verify for-in appears as expression in variable declaration

def test_for_in_with_filtering():
    """Test: for i in 1..10 { if i % 2 == 0 { -> i } }"""
    code = """
    val evens : [_]i32 = for i in 1..10 {
        if i % 2 == 0 {
            -> i
        }
    }
    """
    ast = parse(code)
    # Verify filtering logic in body

def test_nested_for_in_loops():
    """Test: for i in 1..3 { for j in 1..4 { } }"""
    code = """
    for i in 1..3 {
        for j in 1..4 {
            print(i, j)
        }
    }
    """
    ast = parse(code)
    # Verify nested structure
```

**Additional Test Categories:**
- Range iteration (bounded, inclusive, stepped)
- Array slicing (full, partial, reverse)
- Float ranges (with step)
- Nested loops (2D, 3D, 4D)
- Loop expressions producing arrays
- Early termination (break)

### 4.3 While Loop Tests

**File:** `tests/parser/test_while_loops.py`

Test cases to cover:

```python
def test_basic_while_loop():
    """Test: while condition { }"""
    code = """
    while count < 10 {
        count = count + 1
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[0], WhileLoop)

def test_while_true_infinite_loop():
    """Test: while true { }"""
    code = """
    while true {
        break
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[0], WhileLoop)
    # Verify condition is BoolLiteral(true)

def test_while_with_complex_condition():
    """Test: while x > 0 && y < 100 { }"""
    code = """
    while x > 0 && y < 100 {
        do_work()
    }
    """
    ast = parse(code)
    # Verify complex boolean condition
```

**Additional Test Categories:**
- Simple conditions
- Complex boolean expressions
- Infinite loops (while true)
- Nested while loops
- While with break/continue

### 4.4 Loop Control Flow Tests

**File:** `tests/parser/test_loop_control_flow.py`

Test cases to cover:

```python
def test_simple_break():
    """Test: break"""
    code = """
    for i in 1..100 {
        if i > 50 {
            break
        }
    }
    """
    ast = parse(code)
    # Verify BreakStatement in body

def test_labeled_break():
    """Test: break outer"""
    code = """
    outer: for i in 1..10 {
        inner: for j in 1..10 {
            break outer
        }
    }
    """
    ast = parse(code)
    # Verify BreakStatement with label

def test_simple_continue():
    """Test: continue"""
    code = """
    for i in 1..10 {
        if i % 2 == 0 {
            continue
        }
        print(i)
    }
    """
    ast = parse(code)
    # Verify ContinueStatement in body

def test_labeled_continue():
    """Test: continue outer"""
    code = """
    outer: for i in 1..10 {
        inner: for j in 1..10 {
            continue outer
        }
    }
    """
    ast = parse(code)
    # Verify ContinueStatement with label
```

**Additional Test Categories:**
- Break in for-in loops
- Break in while loops
- Continue in for-in loops
- Continue in while loops
- Labeled break/continue
- Nested loop control flow

### 4.5 Loop Label Tests

**File:** `tests/parser/test_loop_labels.py`

Test cases to cover:

```python
def test_labeled_for_in_loop():
    """Test: outer: for i in 1..10 { }"""
    code = """
    outer: for i in 1..10 {
        print(i)
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[0], LabeledStatement)
    assert ast.statements[0].label == "outer"
    assert isinstance(ast.statements[0].statement, ForInLoop)

def test_labeled_while_loop():
    """Test: outer: while condition { }"""
    code = """
    outer: while condition {
        do_work()
    }
    """
    ast = parse(code)
    assert isinstance(ast.statements[0], LabeledStatement)
    assert ast.statements[0].label == "outer"
    assert isinstance(ast.statements[0].statement, WhileLoop)

def test_nested_labeled_loops():
    """Test: outer: for { inner: while { } }"""
    code = """
    outer: for i in 1..10 {
        inner: while condition {
            break outer
        }
    }
    """
    ast = parse(code)
    # Verify nested label structure
```

**Additional Test Categories:**
- Labels on for-in loops
- Labels on while loops
- Nested labeled loops
- Labels on expression loops
- Multiple labels (sibling loops)

### 4.6 Loop Expression Tests

**File:** `tests/parser/test_loop_expressions.py`

Test cases to cover:

```python
def test_loop_expression_basic():
    """Test: val x : [_]i32 = for i in 1..10 { -> i }"""
    code = """
    val squares : [_]i32 = for i in 1..10 {
        -> i * i
    }
    """
    ast = parse(code)
    # Verify for-in as expression in VarDeclaration

def test_nested_loop_expression_2d():
    """Test: val matrix : [_][_]i32 = for i { -> for j { -> i*j } }"""
    code = """
    val matrix : [_][_]i32 = for i in 1..3 {
        -> for j in 1..4 {
            -> i * j
        }
    }
    """
    ast = parse(code)
    # Verify nested loop expression structure

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
    ast = parse(code)
    # Verify 3-level nesting

def test_loop_expression_with_filtering():
    """Test: Filtering in loop expressions"""
    code = """
    val evens : [_]i32 = for i in 1..20 {
        if i % 2 == 0 {
            -> i
        }
    }
    """
    ast = parse(code)
    # Verify filtering logic

def test_loop_expression_with_break():
    """Test: Early termination in loop expressions"""
    code = """
    val partial : [_]i32 = for i in 1..100 {
        if i > 50 {
            break
        }
        -> i
    }
    """
    ast = parse(code)
    # Verify break in expression mode
```

**Additional Test Categories:**
- Loop expressions in function returns
- Loop expressions as function arguments
- Nested loop expressions (2D, 3D, 4D)
- Loop expressions with filtering
- Loop expressions with break
- Loop expressions with labels

---

## Phase 5: Error Handling Tests

### 5.1 Syntax Error Tests

**Test cases to cover:**

```python
def test_missing_braces():
    """Test: for i in 1..10 print(i)  // Error!"""
    code = "for i in 1..10 print(i)"
    with pytest.raises(ParseError):
        parse(code)

def test_missing_in_keyword():
    """Test: for i 1..10 { }  // Error!"""
    code = "for i 1..10 { }"
    with pytest.raises(ParseError):
        parse(code)

def test_parentheses_around_condition():
    """Test: while (condition) { }  // Error!"""
    code = "while (condition) { }"
    with pytest.raises(ParseError):
        parse(code)

def test_invalid_label_syntax():
    """Test: 'outer: for i in 1..10 { }  // Error!"""
    code = "'outer: for i in 1..10 { }"
    with pytest.raises(ParseError):
        parse(code)
```

**Additional Error Categories:**
- Missing keywords
- Invalid syntax
- Mismatched braces
- Invalid label syntax
- Break/continue outside loops (semantic, not parser)

---

## Phase 6: Integration Tests

### 6.1 Complex Real-World Examples

Test realistic code patterns:

```python
def test_multiplication_table():
    """Test: Generate 10x10 multiplication table"""
    code = """
    val table : [_][_]i32 = for i in 1..=10 {
        -> for j in 1..=10 {
            -> i * j
        }
    }
    """
    ast = parse(code)
    # Verify complete structure

def test_matrix_operations():
    """Test: Identity matrix generation"""
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
    ast = parse(code)
    # Verify conditional in nested loop

def test_filtered_nested_loops():
    """Test: Skip empty rows"""
    code = """
    val filtered : [_][_]i32 = for i in 1..10 {
        if i % 2 == 0 {
            -> for j in 1..5 {
                -> i * j
            }
        }
    }
    """
    ast = parse(code)
    # Verify outer filtering

def test_labeled_nested_break():
    """Test: Break outer from inner loop"""
    code = """
    outer: for i in 1..10 {
        inner: for j in 1..10 {
            if i * j > 50 {
                break outer
            }
            print(i, j)
        }
    }
    """
    ast = parse(code)
    # Verify labeled break
```

---

## Implementation Checklist

### Phase 1: AST Nodes
- [ ] Add `ForInLoop` node
- [ ] Add `WhileLoop` node
- [ ] Add `BreakStatement` node
- [ ] Add `ContinueStatement` node
- [ ] Add `LabeledStatement` node
- [ ] Test AST node instantiation

### Phase 2: Grammar Rules
- [ ] Add for-in loop grammar
- [ ] Add while loop grammar
- [ ] Add break/continue grammar
- [ ] Add label grammar
- [ ] Test basic parsing

### Phase 3: Parser Logic
- [ ] Implement `for_in_loop()` transformer
- [ ] Implement `while_loop()` transformer
- [ ] Implement `break_stmt()` transformer
- [ ] Implement `continue_stmt()` transformer
- [ ] Implement `labeled_stmt()` transformer
- [ ] Test AST construction

### Phase 4: Parser Tests
- [ ] Write for-in loop tests (20+ tests)
- [ ] Write while loop tests (10+ tests)
- [ ] Write control flow tests (15+ tests)
- [ ] Write label tests (10+ tests)
- [ ] Write loop expression tests (15+ tests)
- [ ] Achieve 100% parser test coverage

### Phase 5: Error Handling
- [ ] Write syntax error tests (10+ tests)
- [ ] Test edge cases
- [ ] Verify error messages

### Phase 6: Integration
- [ ] Write complex example tests (10+ tests)
- [ ] Test all features together
- [ ] Verify parser completeness

---

## Testing Strategy

### Test Organization

1. **Unit Tests:** Each loop feature tested independently
2. **Integration Tests:** Complex nested scenarios
3. **Error Tests:** Invalid syntax and edge cases

### Coverage Goals

- **Parser coverage:** 100% of loop-related grammar rules
- **AST coverage:** All loop AST nodes thoroughly tested
- **Feature coverage:** All loop features from `LOOP_SYSTEM.md`

### Test Naming Convention

```python
# Pattern: test_<feature>_<scenario>_<expected>
def test_for_in_basic_parsing_succeeds():
def test_while_missing_braces_fails():
def test_labeled_break_nested_parsing_succeeds():
```

---

## Success Criteria

**Parser implementation is complete when:**

1. ✅ All AST nodes defined and tested
2. ✅ Grammar rules cover all loop syntax
3. ✅ Parser logic constructs correct AST
4. ✅ 100+ parser tests passing
5. ✅ All examples from `LOOP_SYSTEM.md` parse correctly
6. ✅ Error cases properly rejected
7. ✅ No regressions in existing tests

---

## Timeline Estimate

| Phase | Estimated Time | Complexity |
|-------|---------------|------------|
| Phase 1: AST Nodes | 1-2 hours | Low |
| Phase 2: Grammar Rules | 2-3 hours | Medium |
| Phase 3: Parser Logic | 3-4 hours | Medium |
| Phase 4: Parser Tests | 4-6 hours | High |
| Phase 5: Error Handling | 2-3 hours | Medium |
| Phase 6: Integration | 2-3 hours | Medium |
| **Total** | **14-21 hours** | **Medium-High** |

---

## Next Steps

1. **Start with Phase 1** (AST Nodes) - Foundation
2. **Move to Phase 2** (Grammar Rules) - Syntax
3. **Implement Phase 3** (Parser Logic) - AST Construction
4. **Write Phase 4 tests** (Parser Tests) - Verification
5. **Add Phase 5** (Error Handling) - Robustness
6. **Complete Phase 6** (Integration) - Real-world scenarios

**After parser is complete:**
- Move to semantic analysis (separate plan)
- Type checking for loop expressions
- Validation of break/continue/labels
- Runtime mode detection (statement vs expression)

---

**Last Updated:** 2025-10-28
**Status:** Ready to implement!
