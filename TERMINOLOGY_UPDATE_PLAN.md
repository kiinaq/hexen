# Hexen Semantic Tests - Terminology Update Plan 📝

*Comprehensive plan to update outdated terminology in semantic tests*

## 🚨 **Critical Issues Found**

### **Outdated Terminology Summary**
- ❌ **"acknowledgment/acknowledge"** - 81 occurrences across 7 files
- ❌ **"type annotation"** - 11 occurrences across 5 files  
- ✅ **"context type"** - 0 occurrences (already clean!)

### **Root Cause**
These terms are from the earlier design phase before the current `value:type` explicit conversion syntax was finalized. The implementation is correct, but test documentation and comments use outdated terminology.

## 📊 **File-by-File Breakdown**

| File | "acknowledgment" | "type annotation" | Total Issues | Priority |
|------|------------------|-------------------|--------------|----------|
| `test_precision_loss.py` | 61 | 4 | **65** | 🔴 **Critical** |
| `test_comptime_types.py` | 7 | 0 | **7** | 🔴 **High** |
| `test_basic_semantics.py` | 7 | 0 | **7** | 🔴 **High** |
| `test_error_messages.py` | 3 | 2 | **5** | 🟡 **Medium** |
| `test_assignment.py` | 1 | 3 | **4** | 🟡 **Medium** |
| `test_binary_ops.py` | 0 | 1 | **1** | 🟢 **Low** |
| `test_bool.py` | 0 | 1 | **1** | 🟢 **Low** |
| `test_context_framework.py` | 1 | 0 | **1** | 🟢 **Low** |
| `test_type_coercion.py` | 1 | 0 | **1** | 🟢 **Low** |

## 🎯 **Terminology Mapping**

### **"acknowledgment/acknowledge" → "explicit conversion"**

```python
# ❌ OLD TERMINOLOGY:
"""Test that explicit acknowledgment allows i64 to i32 conversion"""
def test_i64_to_i32_truncation_with_acknowledgment(self):
    // ✅ Explicit acknowledgment of truncation
    # Should suggest explicit acknowledgment

# ✅ NEW TERMINOLOGY:
"""Test that explicit conversion allows i64 to i32 conversion"""  
def test_i64_to_i32_truncation_with_explicit_conversion(self):
    // ✅ Explicit conversion with visible cost
    # Should suggest explicit conversion (value:type syntax)
```

### **"type annotation" → Context-Specific Updates**

```python
# ❌ OLD TERMINOLOGY:
"""Test assignment with type annotations (for precision loss cases)"""
# Precision loss - should suggest type annotation

# ✅ NEW TERMINOLOGY:
"""Test assignment with explicit conversions (for precision loss cases)"""
# Precision loss - should suggest explicit conversion

# ❌ EXCEPTION - Variable declarations (keep "type annotation"):
"""Test explicit bool type annotation"""  # ✅ CORRECT - this IS a type annotation
val x : i32 = 42  // This IS a type annotation
```

## 🔧 **Specific Updates Needed**

### **Critical File: `test_precision_loss.py` (65 issues)**

**Function Names to Update:**
```python
# Current → Updated
test_i64_to_i32_truncation_with_acknowledgment → test_i64_to_i32_truncation_with_explicit_conversion
test_f64_to_f32_precision_loss_with_acknowledgment → test_f64_to_f32_precision_loss_with_explicit_conversion
test_val_integer_truncation_acknowledgment → test_val_integer_truncation_explicit_conversion
test_float_to_integer_with_acknowledgment → test_float_to_integer_with_explicit_conversion
test_binary_operation_precision_loss_with_acknowledgment → test_binary_operation_precision_loss_with_explicit_conversion
test_chained_precision_loss_with_acknowledgments → test_chained_precision_loss_with_explicit_conversions
test_expression_precision_loss_with_acknowledgment → test_expression_precision_loss_with_explicit_conversion
test_val_float_precision_loss_acknowledgment → test_val_float_precision_loss_explicit_conversion
```

**Comment Updates:**
```python
# Current → Updated
"// ✅ Explicit acknowledgment of truncation" → "// ✅ Explicit conversion with visible cost"
"// ❌ Should require explicit acknowledgment" → "// ❌ Should require explicit conversion"
"Safe operations are implicit (no explicit acknowledgment needed)" → "Safe operations are implicit (no explicit conversion needed)"
"Dangerous operations require explicit acknowledgment via type annotations" → "Dangerous operations require explicit conversions via value:type syntax"
```

### **High Priority Files: `test_comptime_types.py` & `test_basic_semantics.py`**

**Function Names:**
```python
test_comptime_float_to_int_requires_acknowledgment → test_comptime_float_to_int_requires_explicit_conversion
test_comptime_float_to_int_with_acknowledgment → test_comptime_float_to_int_with_explicit_conversion
test_explicit_acknowledgment_integration → test_explicit_conversion_integration
```

## 📋 **Automated Update Plan**

### **Phase 1: Function and Variable Names**
```bash
# Update function names containing "acknowledgment"
find tests/semantic/ -name "*.py" -exec sed -i 's/acknowledgment/explicit_conversion/g' {} \;

# Update specific method names
find tests/semantic/ -name "*.py" -exec sed -i 's/def test_.*acknowledgment/def test_.*explicit_conversion/g' {} \;
```

### **Phase 2: Comments and Docstrings**
```bash
# Update comment patterns
find tests/semantic/ -name "*.py" -exec sed -i 's/Explicit acknowledgment/Explicit conversion/g' {} \;
find tests/semantic/ -name "*.py" -exec sed -i 's/explicit acknowledgment/explicit conversion/g' {} \;
find tests/semantic/ -name "*.py" -exec sed -i 's/require.*acknowledgment/require explicit conversion/g' {} \;
```

### **Phase 3: Context-Specific "type annotation" Updates**
```bash
# Update precision loss contexts (NOT variable declaration contexts)
find tests/semantic/ -name "*.py" -exec sed -i 's/type annotation (for precision loss)/explicit conversion (for precision loss)/g' {} \;
find tests/semantic/ -name "*.py" -exec sed -i 's/suggest type annotation/suggest explicit conversion/g' {} \;
```

## ⚠️ **Manual Review Required**

### **Preserve Correct "type annotation" Usage**
These should **NOT** be changed:
```python
# ✅ KEEP - These are actual type annotations:
"""Test explicit bool type annotation"""
val x : i32 = 42  // Type annotation
mut y : f64 = 3.14  // Type annotation  
```

### **Context-Sensitive Updates**
```python
# ❌ OLD - Incorrect usage:
"precision loss via type annotations" → "precision loss via explicit conversions"
"should suggest type annotation" → "should suggest explicit conversion"

# ✅ KEEP - Correct usage:
"bool type annotation" (referring to `: bool` in variable declaration)
"explicit type annotation" (referring to variable declaration syntax)
```

## 🧪 **Verification Plan**

### **After Updates - Verify:**
1. **All tests still pass** - 428/428 tests should continue passing
2. **Function names are consistent** - No mixed terminology
3. **Comments are accurate** - Reflect current `value:type` syntax
4. **Documentation alignment** - Matches TYPE_SYSTEM.md terminology

### **Test Commands:**
```bash
# Verify all semantic tests pass after updates
uv run pytest tests/semantic/ -v

# Check for remaining outdated terminology
grep -r "acknowledgment\|acknowledge" tests/semantic/
grep -r "type annotation" tests/semantic/ | grep -v "bool type annotation"
```

## 🎯 **Expected Outcome**

### **Before:**
- ❌ 81 instances of "acknowledgment" (outdated)
- ❌ 11 instances of "type annotation" (mixed usage)
- ❌ Inconsistent with TYPE_SYSTEM.md documentation

### **After:**
- ✅ 0 instances of "acknowledgment" in conversion contexts
- ✅ Correct "explicit conversion" terminology throughout
- ✅ Preserved "type annotation" for variable declarations only
- ✅ Perfect alignment with current documentation

## 🚀 **Implementation Priority**

### **Immediate (Critical):**
1. **`test_precision_loss.py`** - 65 instances (most impacted)
2. **`test_comptime_types.py`** - 7 instances
3. **`test_basic_semantics.py`** - 7 instances

### **Soon (Medium):**
4. **`test_error_messages.py`** - 5 instances
5. **`test_assignment.py`** - 4 instances

### **When Convenient (Low):**
6. **Remaining files** - 1 instance each

## 📝 **Conclusion**

This terminology update is **essential for consistency** with the current implementation and documentation. The updates are mostly **search-and-replace** operations with some **manual review** needed to preserve correct "type annotation" usage in variable declaration contexts.

**Estimated Effort:** 2-3 hours (mostly automated with manual verification)
**Risk Level:** Low (no functional changes, only terminology)
**Impact:** High (consistency with documentation and implementation)