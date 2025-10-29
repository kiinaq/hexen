# Label Syntax: `'label` vs `'label:`

**Date:** 2025-10-29
**Question:** Should we use `'label` (no colon) or `'label:` (with colon)?

---

## Option A: `'label` (NO trailing colon)

**Syntax:**
```hexen
'outer for i in 1..10 {
    'inner for j in 1..10 {
        if condition { break 'outer }
    }
}
```

**In expression context:**
```hexen
val matrix : [_][_]i32 = 'outer for i in 1..10 {
    -> 'inner for j in 1..10 {
        if i * j > 50 { break 'outer }
        -> i * j
    }
}
```

---

## Option B: `'label:` (WITH trailing colon)

**Syntax:**
```hexen
'outer: for i in 1..10 {
    'inner: for j in 1..10 {
        if condition { break 'outer }
    }
}
```

**In expression context:**
```hexen
val matrix : [_][_]i32 = 'outer: for i in 1..10 {
    -> 'inner: for j in 1..10 {
        if i * j > 50 { break 'outer }
        -> i * j
    }
}
```

---

## Comparison

### Visual Clarity

**Option A (`'label`):**
```hexen
'outer for i in 1..10 {           // ✅ Cleaner, less punctuation
    'inner for j in 1..10 {
        break 'outer              // ✅ Consistent: no colon anywhere
    }
}
```

**Option B (`'label:`):**
```hexen
'outer: for i in 1..10 {          // ⚠️ Colon on definition
    'inner: for j in 1..10 {
        break 'outer              // ⚠️ No colon on usage (asymmetric)
    }
}
```

**Winner:** Option A (more consistent, less punctuation)

---

### Familiarity

**Rust uses `'label:` (with colon):**
```rust
'outer: for i in 1..10 {
    'inner: for j in 1..10 {
        break 'outer;
    }
}
```

**But Rust's reason:** Historical compatibility with C/Go `label:` style
- Rust kept the `:` to maintain visual similarity with traditional labels
- Not strictly necessary for parsing

**Hexen has no legacy constraint!** We can optimize for clarity.

**Winner:** Option A (we're not bound by history)

---

### Parsing Simplicity

**Option A (`'label`):**
```lark
// Single token, no special handling
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

labeled_stmt: LABEL statement
labeled_for_expr: LABEL for_in_loop

break_stmt: BREAK LABEL?
continue_stmt: CONTINUE LABEL?
```

**Option B (`'label:`):**
```lark
// Need to handle colon separately or include in token
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

labeled_stmt: LABEL ":" statement
labeled_for_expr: LABEL ":" for_in_loop

break_stmt: BREAK LABEL?  // No colon here!
continue_stmt: CONTINUE LABEL?
```

**Winner:** Option A (simpler, no colon handling)

---

### Consistency

**Option A (`'label`):**
- Definition: `'outer for ...`
- Usage: `break 'outer`
- ✅ **SYMMETRIC** - Label looks the same everywhere

**Option B (`'label:`):**
- Definition: `'outer: for ...`
- Usage: `break 'outer` (no colon!)
- ⚠️ **ASYMMETRIC** - Colon only at definition

**Winner:** Option A (perfectly symmetric)

---

### Disambiguation from Other Constructs

Both options are equally unambiguous:

**Option A:**
- `'label for` - Cannot be confused with anything else

**Option B:**
- `'label: for` - Also cannot be confused with anything else

**Winner:** TIE (both work)

---

### Real-World Examples

**Option A (`'label`):**

```hexen
// Simple labeled loop
'outer for i in 1..10 {
    if i > 5 { break 'outer }
}

// Nested loops
'outer for i in 1..10 {
    'inner for j in 1..10 {
        if i * j > 50 { break 'outer }
        if j > 7 { continue 'inner }
    }
}

// Loop expression with label
val matrix : [_][_]i32 = 'outer for i in 1..10 {
    -> 'inner for j in 1..10 {
        if i == j { break 'outer }
        -> i * j
    }
}

// While loop with label
'retry while attempts < 5 {
    if try_connect() {
        break 'retry
    }
    attempts = attempts + 1
}
```

**Observation:** Flows naturally, minimal punctuation clutter.

---

**Option B (`'label:`):**

```hexen
// Simple labeled loop
'outer: for i in 1..10 {
    if i > 5 { break 'outer }
}

// Nested loops
'outer: for i in 1..10 {
    'inner: for j in 1..10 {
        if i * j > 50 { break 'outer }
        if j > 7 { continue 'inner }
    }
}

// Loop expression with label
val matrix : [_][_]i32 = 'outer: for i in 1..10 {
    -> 'inner: for j in 1..10 {
        if i == j { break 'outer }
        -> i * j
    }
}

// While loop with label
'retry: while attempts < 5 {
    if try_connect() {
        break 'retry
    }
    attempts = attempts + 1
}
```

**Observation:** Extra `:` adds visual noise, asymmetric with usage.

---

## Syntax Comparison: Definition vs Usage

### Traditional C/Go Style

**C/Go uses `label:` (colon required):**
```c
outer:                    // Definition: label:
for (int i = 0; i < 10; i++) {
    for (int j = 0; j < 10; j++) {
        goto outer;       // Usage: just label
    }
}
```

**Why the colon?**
- Historical: distinguish label from variable name
- `goto label` vs `label: statement`
- The colon is part of the **label declaration**, not the label itself

---

### Rust Style

**Rust uses `'label:` (lifetime syntax + colon):**
```rust
'outer: for i in 1..10 {   // Definition: 'label:
    break 'outer;          // Usage: 'label (no colon!)
}
```

**Why the colon?**
- Visual consistency with C/Go `label:` style
- But `'` prefix removes ambiguity, making `:` optional
- Rust kept it for familiarity

---

### Hexen's Choice

**We have no legacy constraints!** We can choose the cleaner syntax:

**Option A: `'label` (NO colon)**
```hexen
'outer for i in 1..10 {    // Definition: 'label
    break 'outer           // Usage: 'label
}
```

**Benefits:**
- ✅ **Perfectly symmetric** - Label is `'outer` everywhere
- ✅ **Less punctuation** - Easier to read
- ✅ **Simpler grammar** - No colon handling needed
- ✅ **Still unambiguous** - `'` prefix does all the work

---

## Grammar Comparison

### Option A: `'label` (Simpler)

```lark
// Terminals
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

// Statement rules
labeled_stmt: LABEL statement
labeled_for_expr: LABEL for_in_loop
labeled_while: LABEL while_loop

// Control flow
break_stmt: BREAK LABEL?
continue_stmt: CONTINUE LABEL?

// Expressions
primary: ... | labeled_for_expr | ...
```

**Parser transformer:**
```python
def LABEL(self, token):
    """Extract label name (strip leading ')"""
    return token.value[1:]  # Remove '

def labeled_stmt(self, items):
    label = items[0]      # Just the label
    stmt = items[1]       # The statement
    return {
        "type": NodeType.LABELED_STATEMENT,
        "label": label,
        "statement": stmt,
    }
```

---

### Option B: `'label:` (More Complex)

```lark
// Terminals
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

// Statement rules (need explicit colon)
labeled_stmt: LABEL ":" statement
labeled_for_expr: LABEL ":" for_in_loop
labeled_while: LABEL ":" while_loop

// Control flow (NO colon!)
break_stmt: BREAK LABEL?
continue_stmt: CONTINUE LABEL?

// Expressions
primary: ... | labeled_for_expr | ...
```

**Parser transformer:**
```python
def LABEL(self, token):
    """Extract label name (strip leading ')"""
    return token.value[1:]  # Remove '

def labeled_stmt(self, items):
    label = items[0]      # The label
    # items[1] is the colon (skip it)
    stmt = items[2]       # The statement
    return {
        "type": NodeType.LABELED_STATEMENT,
        "label": label,
        "statement": stmt,
    }
```

**Notice:** Extra colon handling, more complex.

---

## Other Languages Comparison

| Language | Label Syntax | Definition | Usage | Colon at Definition? | Colon at Usage? |
|----------|--------------|------------|-------|---------------------|-----------------|
| **C** | `label:` | `outer: stmt;` | `goto outer;` | ✅ Yes | ❌ No |
| **Go** | `label:` | `outer: for { }` | `break outer` | ✅ Yes | ❌ No |
| **Rust** | `'label:` | `'outer: for { }` | `break 'outer;` | ✅ Yes | ❌ No |
| **Java** | `label:` | `outer: for { }` | `break outer;` | ✅ Yes | ❌ No |
| **JavaScript** | `label:` | `outer: for { }` | `break outer;` | ✅ Yes | ❌ No |
| **Python** | N/A | (no labels) | (no labels) | N/A | N/A |
| **Swift** | (no prefix) | `outer: for { }` | `break outer` | ✅ Yes | ❌ No |
| **Hexen A** | `'label` | `'outer for { }` | `break 'outer` | ❌ No | ❌ No |
| **Hexen B** | `'label:` | `'outer: for { }` | `break 'outer` | ✅ Yes | ❌ No |

**Pattern:** ALL languages use colon **only at definition**, never at usage.

**But:** C/Go/Java need the colon to distinguish labels from identifiers.

**Rust/Hexen:** The `'` prefix already distinguishes labels! Colon is redundant.

---

## Community Familiarity

**Option B (`'label:`) advantages:**
- Developers from C/Go/Java/Rust will recognize the pattern
- Follows established convention (label definitions have colons)

**Option A (`'label`) advantages:**
- Simpler, more consistent (no asymmetry)
- Natural for developers who think "the label IS `'outer`, everywhere"

**Conclusion:** Option B has slight familiarity edge, but Option A is more logical.

---

## Recommendation Matrix

| Criterion | `'label` (A) | `'label:` (B) | Winner |
|-----------|-------------|--------------|--------|
| **Visual clarity** | ⭐⭐⭐⭐⭐ Less clutter | ⭐⭐⭐⭐ Extra colon | **A** |
| **Consistency** | ⭐⭐⭐⭐⭐ Symmetric | ⭐⭐⭐ Asymmetric | **A** |
| **Parsing simplicity** | ⭐⭐⭐⭐⭐ Simpler | ⭐⭐⭐⭐ Slightly complex | **A** |
| **Familiarity** | ⭐⭐⭐ Novel | ⭐⭐⭐⭐ Rust-like | **B** |
| **Disambiguation** | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐⭐⭐⭐ Perfect | **TIE** |
| **Future-proof** | ⭐⭐⭐⭐⭐ Yes | ⭐⭐⭐⭐⭐ Yes | **TIE** |

**Score:** Option A wins 4-1 (with 1 tie)

---

## Final Recommendation: `'label` (NO colon)

**Reasons:**
1. ✅ **More consistent** - Label is `'outer` everywhere (definition and usage)
2. ✅ **Simpler grammar** - No colon handling needed
3. ✅ **Cleaner syntax** - Less punctuation clutter
4. ✅ **Still unambiguous** - `'` prefix does all the work
5. ✅ **More logical** - Why have `:` only at definition but not usage?

**The colon in `'label:` is redundant** - it was needed in C/Go to disambiguate, but Hexen's `'` prefix already handles that!

---

## Counter-Argument: Why Keep the Colon?

**Argument FOR `'label:`:**
- Follows Rust convention (familiarity for Rust developers)
- Visual consistency with other languages (C, Go, Java, JavaScript)
- The colon "feels right" for label declarations (psychological consistency)

**Counter-argument:**
- Rust kept the colon for **historical reasons** (transitioning from C-style labels)
- Hexen has **no such constraint** - we can optimize for clarity
- The colon creates **asymmetry** (`'label:` at definition, `'label` at usage)
- **Simpler is better** when there's no functional difference

---

## Example Migration

**Current (broken):**
```hexen
outer: for i in 1..10 {
    break outer
}
```

**Option A (`'label`):**
```hexen
'outer for i in 1..10 {
    break 'outer
}
```

**Option B (`'label:`):**
```hexen
'outer: for i in 1..10 {
    break 'outer
}
```

**Both work, but Option A is cleaner!**

---

## Implementation Recommendation

**Use `'label` (no colon)** for these reasons:

1. **Hexen's philosophy: "Ergonomic Literals + Transparent Costs"**
   - Remove unnecessary syntax (the colon adds no value)
   - Make intent clear (the label is `'outer`, period)

2. **Consistency principle**
   - If the label is `'outer`, it should be `'outer` everywhere
   - No special syntax at definition vs usage

3. **Simplicity principle**
   - Fewer rules = easier to learn
   - Less punctuation = easier to read

---

## Decision Summary

| Aspect | `'label` | `'label:` |
|--------|---------|----------|
| **Syntax at definition** | `'outer for ...` | `'outer: for ...` |
| **Syntax at usage** | `break 'outer` | `break 'outer` |
| **Consistency** | ✅ Symmetric | ⚠️ Asymmetric |
| **Simplicity** | ✅ Simpler | ⚠️ Extra colon |
| **Familiarity** | ⚠️ Novel | ✅ Rust-like |
| **Parsing** | ✅ Easier | ⚠️ Slightly harder |
| **Recommended?** | ✅ **YES** | ⚠️ Only if familiarity is critical |

---

## Final Answer

**Recommended syntax: `'label` (WITHOUT trailing colon)**

```hexen
// Definition and usage are symmetric
'outer for i in 1..10 {
    'inner for j in 1..10 {
        if condition { break 'outer }
    }
}

// Works in expression contexts too
val result : [_]i32 = 'outer for i in 1..100 {
    if i > 50 { break 'outer }
    -> i
}
```

**Advantages over `'label:`:**
- ✅ Perfectly consistent (label is `'outer` everywhere)
- ✅ Less punctuation clutter
- ✅ Simpler grammar and parsing
- ✅ More logical (no asymmetry)
- ✅ Still 100% unambiguous

**Only disadvantage:** Slightly less familiar to Rust developers (but Rust's colon is historical baggage, not a design choice we need to inherit).

---

**Next step:** Confirm this syntax choice, then implement in ~3-4 hours!
