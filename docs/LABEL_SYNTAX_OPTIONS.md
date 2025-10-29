# Label Syntax Options - Comprehensive Analysis

**Date:** 2025-10-29
**Goal:** Find the best unambiguous label syntax for Hexen

---

## Requirements

A good label syntax must:
1. ✅ **Be unambiguous** - No conflict with existing syntax (`:`, types, identifiers)
2. ✅ **Work in all contexts** - Statements AND expressions
3. ✅ **Be visually distinctive** - Easy to spot at a glance
4. ✅ **Be easy to parse** - Simple lexer/parser implementation
5. ✅ **Feel natural** - Not too foreign to C-family language users
6. ✅ **Be future-proof** - Won't conflict with planned features

---

## Option 1: `'label:` (Rust-Style)

**Syntax:**
```hexen
'outer: for i in 1..10 {
    'inner: for j in 1..10 {
        if condition { break 'outer }
    }
}
```

**Character:** `'` (single quote / apostrophe, U+0027)

**Pros:**
- ✅ **Proven in production** (Rust has validated this design)
- ✅ **Zero ambiguity** (can't be confused with anything)
- ✅ **Visually distinctive** (labels stand out clearly)
- ✅ **Natural for lifetimes concept** (if Hexen adds them later)
- ✅ **Easy to parse** (single dedicated token)

**Cons:**
- ⚠️ May look unusual to C/Go/JavaScript developers initially
- ⚠️ Could conflict if we want single-char literals later (`'a'`)
  - But: Hexen already uses `"` for strings, unlikely to need char literals

**Grammar:**
```lark
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐⭐⭐⭐ (5/5) - **BEST CHOICE**

---

## Option 2: `@label:` (Decorator-Style)

**Syntax:**
```hexen
@outer: for i in 1..10 {
    @inner: for j in 1..10 {
        if condition { break @outer }
    }
}
```

**Character:** `@` (at sign, U+0040)

**Pros:**
- ✅ **Familiar from annotations** (Java, Python decorators)
- ✅ **Zero ambiguity**
- ✅ **Visually distinctive**
- ✅ **Clean appearance**

**Cons:**
- ⚠️ **May conflict with future decorator features** (if we add @decorators)
- ⚠️ **Semantically confusing** (@annotation vs label)
- ⚠️ Less common for loop labels specifically

**Grammar:**
```lark
LABEL: /@[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐⭐⭐ (4/5) - Good alternative, but may conflict with decorators

---

## Option 3: `#label:` (Preprocessor-Style)

**Syntax:**
```hexen
#outer: for i in 1..10 {
    #inner: for j in 1..10 {
        if condition { break #outer }
    }
}
```

**Character:** `#` (hash/pound, U+0023)

**Pros:**
- ✅ **Familiar from C macros/preprocessor**
- ✅ **Zero ambiguity**
- ✅ **Visually distinctive**

**Cons:**
- ⚠️ **Strong association with preprocessor/macros** (misleading)
- ⚠️ **Could conflict with future preprocessor directives** (#if, #define, etc.)
- ⚠️ **Could conflict with comments** (if we want # for line comments)

**Grammar:**
```lark
LABEL: /#[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐⭐ (3/5) - Works but semantically misleading

---

## Option 4: `$label:` (Sigil-Style)

**Syntax:**
```hexen
$outer: for i in 1..10 {
    $inner: for j in 1..10 {
        if condition { break $outer }
    }
}
```

**Character:** `$` (dollar sign, U+0024)

**Pros:**
- ✅ **Zero ambiguity**
- ✅ **Used for labels in assembly** (familiar to low-level programmers)
- ✅ **Visually distinctive**

**Cons:**
- ⚠️ **Strong association with variables** (Perl, PHP, shell scripts use $ for vars)
- ⚠️ **Could conflict with string interpolation** (if we add `"Hello $name"` syntax)
- ⚠️ **Potentially confusing** (label vs variable)

**Grammar:**
```lark
LABEL: /\$[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐⭐ (3/5) - Works but easily confused with variables

---

## Option 5: `^label:` (Caret-Style)

**Syntax:**
```hexen
^outer: for i in 1..10 {
    ^inner: for j in 1..10 {
        if condition { break ^outer }
    }
}
```

**Character:** `^` (caret/circumflex, U+005E)

**Pros:**
- ✅ **Zero ambiguity**
- ✅ **Visually distinctive** (arrow-like, points to target)
- ✅ **Uncommon in most languages** (less likely to conflict)

**Cons:**
- ⚠️ **Used for XOR operator** (in C, Rust, etc.) - but we likely won't use it for that
- ⚠️ **Less familiar** (not widely used for labels anywhere)
- ⚠️ **Could conflict with exponentiation** (if we add `2^8` syntax)

**Grammar:**
```lark
LABEL: /\^[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐⭐ (3/5) - Unusual but unambiguous

---

## Option 6: `&label:` (Reference-Style)

**Syntax:**
```hexen
&outer: for i in 1..10 {
    &inner: for j in 1..10 {
        if condition { break &outer }
    }
}
```

**Character:** `&` (ampersand, U+0026)

**Pros:**
- ✅ **Zero ambiguity**
- ✅ **Conceptual fit** (label = reference to a loop)

**Cons:**
- ⚠️ **Strong association with pointers/references** (C, C++, Rust)
- ⚠️ **Used for bitwise AND** (in most languages)
- ⚠️ **Semantically confusing** (reference vs label)

**Grammar:**
```lark
LABEL: /&[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐ (2/5) - Too strongly associated with pointers

---

## Option 7: `~label:` (Tilde-Style)

**Syntax:**
```hexen
~outer: for i in 1..10 {
    ~inner: for j in 1..10 {
        if condition { break ~outer }
    }
}
```

**Character:** `~` (tilde, U+007E)

**Pros:**
- ✅ **Zero ambiguity**
- ✅ **Uncommon** (less likely to conflict)

**Cons:**
- ⚠️ **Used for bitwise NOT** (in C, C++, etc.)
- ⚠️ **Used for home directory** (in Unix shells)
- ⚠️ **No clear semantic connection** to labels

**Grammar:**
```lark
LABEL: /~[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐ (2/5) - No semantic meaning

---

## Option 8: `.label:` (Dot-Prefix)

**Syntax:**
```hexen
.outer: for i in 1..10 {
    .inner: for j in 1..10 {
        if condition { break .outer }
    }
}
```

**Character:** `.` (period/dot, U+002E)

**Pros:**
- ✅ **Used for local labels in assembly** (familiar to low-level programmers)
- ✅ **Visually subtle** (doesn't distract)

**Cons:**
- ❌ **STRONG CONFLICT with property access** (`.field`, `.method()`)
- ❌ **Ambiguous in many contexts**
- ⚠️ **Used for ranges** (already in Hexen: `..`, `..=`)

**Grammar:**
```lark
LABEL: /\.[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐ (1/5) - **TOO AMBIGUOUS** (conflicts with member access)

---

## Option 9: `::label:` (Scope-Style)

**Syntax:**
```hexen
::outer: for i in 1..10 {
    ::inner: for j in 1..10 {
        if condition { break ::outer }
    }
}
```

**Characters:** `::` (double colon, U+003A U+003A)

**Pros:**
- ✅ **Semantic fit** (scope/namespace marker)
- ✅ **Used in C++, Rust** (familiar)

**Cons:**
- ⚠️ **May conflict with namespace operators** (if we add modules later)
- ⚠️ **Two characters** (slightly less elegant)
- ⚠️ **Heavy visual weight**

**Grammar:**
```lark
LABEL: /::[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐⭐⭐ (3/5) - Works but may conflict with future namespaces

---

## Option 10: `%label:` (Modulo-Style)

**Syntax:**
```hexen
%outer: for i in 1..10 {
    %inner: for j in 1..10 {
        if condition { break %outer }
    }
}
```

**Character:** `%` (percent, U+0025)

**Pros:**
- ✅ **Zero ambiguity** (in label position)

**Cons:**
- ❌ **CONFLICT: Already used for modulo operator** (`i % 2`)
- ⚠️ **Semantically confusing**

**Grammar:**
```lark
LABEL: /%[a-zA-Z_][a-zA-Z0-9_]*/
```

**Rating:** ⭐ (1/5) - **CONFLICTS WITH MODULO**

---

## Option 11: `*label:` (Star/Asterisk-Style)

**Syntax:**
```hexen
*outer: for i in 1..10 {
    *inner: for j in 1..10 {
        if condition { break *outer }
    }
}
```

**Character:** `*` (asterisk, U+002A)

**Pros:**
- ✅ **Visually distinctive** (star stands out)

**Cons:**
- ❌ **CONFLICT: Used for multiplication** (`a * b`)
- ❌ **CONFLICT: Used for pointers/dereferencing** (C, C++)
- ⚠️ **Highly ambiguous**

**Rating:** ⭐ (1/5) - **TOO AMBIGUOUS**

---

## Option 12: `:label:` (Double-Colon Wrapper)

**Syntax:**
```hexen
:outer: for i in 1..10 {
    :inner: for j in 1..10 {
        if condition { break :outer: }
    }
}
```

**Characters:** `:` prefix AND suffix

**Pros:**
- ✅ **Visually balanced**
- ✅ **Reminiscent of Ruby symbols** (`:symbol`)

**Cons:**
- ⚠️ **Requires suffix in break/continue** (`:outer:` vs just `outer`)
- ⚠️ **Verbose**
- ⚠️ **Still has `:` ambiguity**

**Rating:** ⭐⭐ (2/5) - Awkward and verbose

---

## Option 13: `label::` (Suffix-Style)

**Syntax:**
```hexen
outer:: for i in 1..10 {
    inner:: for j in 1..10 {
        if condition { break outer:: }
    }
}
```

**Characters:** `::` suffix instead of `:` suffix

**Pros:**
- ✅ **Different from current syntax**
- ✅ **May be less ambiguous**

**Cons:**
- ⚠️ **Uncommon pattern** (most languages use prefix or `:` suffix)
- ⚠️ **Visually awkward** (`break outer::` looks incomplete)
- ⚠️ **May still conflict with type annotations in some contexts**

**Rating:** ⭐⭐ (2/5) - Unusual and awkward

---

## Comparison Matrix

| Option | Char | Ambiguity | Familiarity | Semantic Fit | Future-Proof | Rating |
|--------|------|-----------|-------------|--------------|--------------|---------|
| `'label:` | `'` | ✅ None | ⭐⭐⭐⭐ (Rust) | ⭐⭐⭐⭐⭐ (lifetimes) | ✅ Yes | ⭐⭐⭐⭐⭐ |
| `@label:` | `@` | ✅ None | ⭐⭐⭐⭐ (decorators) | ⭐⭐⭐ (annotation-like) | ⚠️ Decorators? | ⭐⭐⭐⭐ |
| `#label:` | `#` | ✅ None | ⭐⭐⭐ (preprocessor) | ⭐⭐ (confusing) | ⚠️ Preprocessor? | ⭐⭐⭐ |
| `$label:` | `$` | ✅ None | ⭐⭐⭐ (assembly) | ⭐⭐ (variable-like) | ⚠️ Interpolation? | ⭐⭐⭐ |
| `^label:` | `^` | ✅ None | ⭐⭐ (unusual) | ⭐⭐ (arrow-ish) | ⚠️ XOR? | ⭐⭐⭐ |
| `&label:` | `&` | ✅ None | ⭐⭐ (pointers) | ⭐⭐ (confusing) | ⚠️ References? | ⭐⭐ |
| `~label:` | `~` | ✅ None | ⭐⭐ (bitwise) | ⭐ (none) | ⚠️ Bitwise NOT? | ⭐⭐ |
| `.label:` | `.` | ❌ High | ⭐⭐⭐ (assembly) | ⭐⭐ (scope-ish) | ❌ Member access | ⭐ |
| `::label:` | `::` | ⚠️ Medium | ⭐⭐⭐⭐ (C++, Rust) | ⭐⭐⭐⭐ (scope) | ⚠️ Namespaces? | ⭐⭐⭐ |
| `%label:` | `%` | ❌ High | ⭐⭐ (registers) | ⭐ (none) | ❌ Modulo | ⭐ |
| `*label:` | `*` | ❌ High | ⭐⭐ (pointers) | ⭐ (none) | ❌ Multiply | ⭐ |
| `:label:` | `:` wrap | ⚠️ Medium | ⭐⭐ (Ruby) | ⭐⭐ (symbol-like) | ⚠️ Verbose | ⭐⭐ |
| `label::` | `::` suffix | ⚠️ Medium | ⭐ (unusual) | ⭐⭐ (awkward) | ⚠️ Namespaces? | ⭐⭐ |

---

## Top 3 Recommendations

### 🥇 #1: `'label:` (Rust-Style)

**Best overall choice:**
- ✅ **Zero ambiguity**
- ✅ **Proven in production** (Rust validation)
- ✅ **Future-proof** (unlikely to conflict with anything)
- ✅ **Visually distinctive**
- ✅ **Easy to parse**

**Only concern:** May conflict with single-char literals (`'a'`), but:
- Hexen uses `"strings"` and doesn't need char types
- Even if we add chars later, we can use `'a'` for chars and `'label:` for labels (different contexts)

---

### 🥈 #2: `@label:` (Decorator-Style)

**Strong alternative:**
- ✅ **Zero ambiguity**
- ✅ **Familiar syntax** (@annotations)
- ✅ **Visually clean**

**Concern:** May want `@` for decorators/attributes later:
```hexen
@inline
func fast_path() : i32 = { ... }
```

**Decision factor:** Do we plan to add decorators/attributes? If yes, avoid `@label:`.

---

### 🥉 #3: `::label:` (Scope-Style)

**Semantic alternative:**
- ✅ **Semantically meaningful** (labels define scope targets)
- ✅ **Familiar from C++/Rust** (scope resolution)
- ✅ **Zero ambiguity** (in label context)

**Concern:** May want `::` for namespaces/modules later:
```hexen
std::io::print("Hello")
```

**Decision factor:** Do we plan to add modules/namespaces? If yes, avoid `::label:`.

---

## Recommendation: `'label:` (Option 1)

**Final recommendation: Use Rust-style `'label:` syntax.**

**Rationale:**
1. **Proven design** - Rust faced the exact same problem and validated this solution
2. **Minimal conflicts** - Unlikely to need char literals (we have strings)
3. **Future-proof** - Won't interfere with decorators, namespaces, or operators
4. **Best parsing** - Single character, completely unambiguous
5. **Clear visual distinction** - Labels are immediately recognizable

**If `'` is unavailable (need char literals):**
- **Second choice: `@label:`** (if we don't plan decorators)
- **Third choice: `::label:`** (if we don't plan namespaces)

---

## Implementation Plan for `'label:`

### Step 1: Update Grammar
```lark
// Add LABEL terminal
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*/

// Update rules
labeled_stmt: LABEL statement
labeled_for_expr: LABEL for_in_loop

break_stmt: BREAK LABEL?
continue_stmt: CONTINUE LABEL?

// Allow in expressions
primary: ... | labeled_for_expr | ...
```

### Step 2: Update Parser Transformer
```python
def LABEL(self, token):
    """Extract label name (strip leading ')"""
    return token.value[1:]  # Remove '

def labeled_stmt(self, items):
    label = items[0]  # Already stripped by LABEL transformer
    stmt = items[1]
    return {
        "type": NodeType.LABELED_STATEMENT,
        "label": label,
        "statement": stmt,
    }
```

### Step 3: Update Tests (Mechanical)
```bash
# In all test files, replace:
# - "outer:" → "'outer:"
# - "inner:" → "'inner:"
# - "break outer" → "break 'outer"
# - "continue outer" → "continue 'outer"

# Example:
sed -i 's/outer: for/'outer: for/g' tests/**/*.py
sed -i 's/break outer/break '\''outer/g' tests/**/*.py
```

### Step 4: Update Documentation
- Update `LOOP_SYSTEM.md` with new syntax
- Add migration note for any existing code

**Estimated Time:** 4 hours total

---

## Alternative: Character Literal Solution

If we **DO** want char literals (`'a'`, `'b'`, etc.) in the future:

**Solution:** Use **context-based disambiguation**:
- `'a'` = char literal (single character, surrounded by quotes)
- `'label:` = label (followed by `:`, must be identifier)

**Lexer can distinguish:**
```python
# Regex patterns
CHAR_LITERAL: /'[^']'/        # Single char between quotes
LABEL: /'[a-zA-Z_][a-zA-Z0-9_]*(?=:)/  # Identifier after ', followed by :
```

This allows both features to coexist! But adds lexer complexity.

---

## Questions to Answer

1. **Do we plan to add char literals?** (`'a'`, `'b'`)
   - If NO → `'label:` is perfect ✅
   - If YES → Can still use `'label:` with disambiguation, or choose `@label:`

2. **Do we plan to add decorators/attributes?** (`@inline`, `@test`)
   - If NO → `@label:` is good alternative ✅
   - If YES → Avoid `@label:`, stick with `'label:`

3. **Do we plan to add modules/namespaces?** (`std::io::print`)
   - If NO → `::label:` is viable ✅
   - If YES → Avoid `::label:`, stick with `'label:`

**Most future-proof choice: `'label:`** (least likely to conflict)
