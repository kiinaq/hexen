# Label Syntax Decision: Resolving Parser Ambiguity

**Status:** Discussion Document
**Date:** 2025-10-29
**Issue:** `label:` syntax creates parsing ambiguity in expression contexts

---

## Problem Statement

The current `label:` syntax works in **statement contexts** but fails in **expression contexts**:

```hexen
// ✅ Works: Label in statement context
outer: for i in 1..10 {
    break outer
}

// ❌ Fails: Label in expression context
val matrix : [_][_]i32 = outer: for i in 1..10 {
    -> for j in 1..10 {
        if i * j > 50 { break outer }
        -> i * j
    }
}
```

**Root Cause:** The parser sees `outer:` after `=` and tries to parse it as:
1. A labeled statement (because of `IDENTIFIER ":"`)
2. But labeled statements can't appear in expression position
3. The grammar rule `labeled_stmt: IDENTIFIER ":" statement` only works at statement level

---

## Failed Tests (19 total)

Tests failing due to label syntax in expression contexts:
- `test_label_on_loop_expression`
- `test_label_on_nested_loop_expressions`
- `test_break_to_outer_expression_from_inner`
- Several tests using `for i : type in range` syntax (confused with labels)

**Critical Observation:** Some tests are failing because `for i : i32 in range` is being confused with label syntax!

---

## Solution Options

### Option 1: Rust-Style `'label:` Syntax (RECOMMENDED)

**Syntax:**
```hexen
'outer: for i in 1..10 {
    'inner: for j in 1..10 {
        if condition { break 'outer }
    }
}
```

**Pros:**
- ✅ **Syntactically unambiguous** (no conflict with `:` in other contexts)
- ✅ **Works in both statement and expression contexts**
- ✅ **Proven solution** (Rust has validated this design)
- ✅ **Visually distinctive** (labels stand out clearly)
- ✅ **Easy to parse** (dedicated token `LABEL`)

**Cons:**
- ⚠️ Requires updating grammar and all tests
- ⚠️ Different from C/C++/Go style

**Grammar Changes:**
```lark
// Add LABEL terminal
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

// Update labeled_stmt
labeled_stmt: LABEL ":" statement

// Update break/continue
break_stmt: BREAK LABEL?
continue_stmt: CONTINUE LABEL?

// Allow labeled loops in expressions
primary: ... | labeled_for_expr | ...
labeled_for_expr: LABEL ":" for_in_loop
```

---

### Option 2: Keep `label:` But Fix Grammar

**Strategy:** Make labeled loops valid as expressions (not just statements)

**Grammar Changes:**
```lark
// Allow labeled_stmt in primary expressions
primary: ... | labeled_expr | ...
labeled_expr: IDENTIFIER ":" for_in_loop

// Keep labeled_stmt for statement contexts
labeled_stmt: IDENTIFIER ":" statement
```

**Pros:**
- ✅ Keeps current syntax (`label:`)
- ✅ No test updates needed (syntax-wise)

**Cons:**
- ⚠️ **Still ambiguous** with type annotations in some contexts
- ⚠️ Harder to parse (requires more lookahead)
- ⚠️ May confuse `for i : type in range` with `label: for i in range`
- ⚠️ Less clear visually

---

### Option 3: Use `@label` Syntax

**Syntax:**
```hexen
@outer for i in 1..10 {
    @inner for j in 1..10 {
        if condition { break @outer }
    }
}
```

**Pros:**
- ✅ Syntactically unambiguous
- ✅ No `:` conflict
- ✅ Works in all contexts
- ✅ Decorators/annotations are familiar (Python, Java)

**Cons:**
- ⚠️ Less common for loop labels
- ⚠️ May be confused with future annotation features

---

### Option 4: Use `#label` Syntax

**Syntax:**
```hexen
#outer for i in 1..10 {
    break #outer
}
```

**Pros:**
- ✅ Syntactically unambiguous
- ✅ Reminiscent of C macros (familiar)

**Cons:**
- ⚠️ May conflict with future preprocessor features
- ⚠️ Less clear visually

---

## Recommendation: Option 1 (`'label:` Rust-Style)

**Reasons:**
1. **Proven Design:** Rust faced the exact same ambiguity and solved it with `'label:`
2. **Zero Ambiguity:** `'` makes labels syntactically distinct from all other constructs
3. **Future-Proof:** Won't conflict with type annotations, decorators, or other features
4. **Clear Intent:** Labels are visually distinctive and easy to spot
5. **Parser Simplicity:** Single dedicated token (`LABEL`), no lookahead needed

**Migration Impact:**
- Update grammar (5 lines)
- Update parser transformer (label extraction logic)
- Update 23 label tests (mechanical find-replace: `label:` → `'label:`)
- Update loop system documentation
- Update semantic analyzer (label storage uses same string, just different syntax)

---

## Implementation Plan

If we choose Option 1 (`'label:`):

### Phase 1: Grammar Update
```lark
// Add label token
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

// Update rules
labeled_stmt: LABEL statement
labeled_expr: LABEL for_in_loop

break_stmt: BREAK LABEL?
continue_stmt: CONTINUE LABEL?

// Add to primary for expression contexts
primary: ... | labeled_expr | ...
```

### Phase 2: Parser Transformer Update
Update `HexenTransformer` to extract label names (strip `'` prefix):
```python
def labeled_stmt(self, items):
    label = items[0].value[1:]  # Strip leading '
    stmt = items[1]
    return {
        "type": NodeType.LABELED_STATEMENT,
        "label": label,
        "statement": stmt,
    }
```

### Phase 3: Test Updates
Mechanical replacement in all test files:
- `outer: for` → `'outer: for`
- `break outer` → `break 'outer`
- `continue outer` → `continue 'outer`

### Phase 4: Documentation Updates
- Update `LOOP_SYSTEM.md` with new syntax
- Update examples in documentation
- Add note about Rust inspiration

---

## Alternative: Keep Both Syntaxes?

We could support **both** `label:` and `'label:` if we want:
- `label:` for statement contexts (backwards compatible)
- `'label:` for expression contexts (unambiguous)

**Not recommended:** Adds complexity for marginal benefit.

---

## Decision Timeline

1. **Discuss with team** (Today)
2. **Choose syntax** (Today)
3. **Implement grammar changes** (1 hour)
4. **Update tests** (2 hours - mechanical)
5. **Verify all tests pass** (30 minutes)

**Total estimated time:** ~4 hours for complete migration

---

## Questions for Discussion

1. Do we prefer `'label:` (Rust-style) or another syntax?
2. Should we support both syntaxes for backwards compatibility?
3. Any concerns about the `'` prefix conflicting with future features?
4. Should we update immediately or defer to next semantic phase?

---

## Conclusion

The `'label:` syntax (Option 1) is the **strongly recommended solution** based on:
- Proven design (Rust)
- Zero ambiguity
- Parser simplicity
- Clear visual distinction

**Next Steps:** Get confirmation on syntax choice, then proceed with implementation.
