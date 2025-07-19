# Comptime Types Quick Reference 🚀

*Essential patterns for Hexen's comptime type system*

## 🧠 Mental Model

**Key Insight**: Literals stay flexible until context forces them to become concrete.

```hexen
42        // comptime_int (flexible!)
3.14      // comptime_float (flexible!)
val x = 42   // Still comptime_int (preserved!)
val y : i32 = 42   // NOW becomes i32 (context forces resolution)
```

**⚠️ Overflow Safety**: Large literals that exceed type ranges trigger compile-time errors. See **[LITERAL_OVERFLOW_BEHAVIOR.md](LITERAL_OVERFLOW_BEHAVIOR.md)** for safety guarantees.

## 📊 The Three Type Categories

| Category | Examples | Behavior |
|----------|----------|----------|
| **Comptime** | `42`, `3.14`, `val x = 42` | Adapts to context seamlessly |
| **Concrete** | `val x : i32 = 42`, function results | Requires explicit conversions |
| **Mixed** | `comptime + concrete` | Comptime adapts, result is concrete |

## ⚡ Quick Decision Tree

```
Is it a literal (42, 3.14)?
├─ YES → comptime type (flexible)
└─ NO → Is it from a function call or explicitly typed?
   ├─ YES → concrete type (fixed)
   └─ NO → Is it arithmetic between comptime types only?
      ├─ YES → comptime type (flexible)
      └─ NO → concrete type (fixed)
```

## 🔄 The Four Patterns

### 1. ✨ Comptime + Comptime = Comptime (Flexible)
```hexen
val math = 42 + 100 * 3.14    // comptime_float (stays flexible!)
val as_f32 : f32 = math       // Same source → f32
val as_f64 : f64 = math       // Same source → f64
val as_i32 : i32 = math:i32   // Same source → i32 (explicit conversion)
```

### 2. 🔄 Comptime + Concrete = Concrete (Adapts)
```hexen
val count : i32 = 100
val result : i32 = count + 42    // i32 + comptime_int → i32 (adapts)
val bigger : i64 = count + 42    // i32 + comptime_int → i64 (context guides)
```

### 3. 🔧 Concrete + Concrete = Explicit Required
```hexen
val a : i32 = 10
val b : i64 = 20
// val mixed = a + b           // ❌ Error: mixed concrete types
// val result : i64 = a + b    // ❌ Still error: context doesn't help with mixed concrete
val explicit : i64 = a:i64 + b // ✅ Explicit conversion required
```

### 4. ⚡ Same + Same = Same (Identity)
```hexen
val a : i32 = 10
val b : i32 = 20
val result : i32 = a + b       // i32 + i32 → i32 (no conversion)
```

## 🎯 Context Sources (What Forces Resolution)

| Context Source | Example | Effect |
|---------------|---------|--------|
| **Type Annotation** | `val x : i64 = 42` | comptime_int → i64 |
| **Function Parameter** | `process(42)` where `process(x: i32)` | comptime_int → i32 |
| **Function Return** | `return 42` in `func() : f32` | comptime_int → f32 |
| **Assignment Target** | `counter = 42` where `counter : i32` | comptime_int → i32 |
| **Mixed Operation** | `concrete_var + 42` | comptime_int → concrete_var's type |

## 🔐 val vs mut: Flexibility Rules

```hexen
// ✅ val preserves comptime types (maximum flexibility)
val flexible = 42 + 100        // comptime_int (flexible!)
val as_i32 : i32 = flexible    // Can adapt to i32
val as_f64 : f64 = flexible    // Same source adapts to f64

// 🔒 mut requires explicit types (safety over flexibility)
mut counter : i32 = 42 + 100   // Must specify type, becomes concrete i32
// val cant_adapt : i64 = counter  // ❌ No flexibility left
val converted : i64 = counter:i64  // ✅ Explicit conversion required
```

## 🔧 Explicit Conversion Syntax

**Pattern**: `value:target_type`

```hexen
val widened : i64 = i32_val:i64        // i32 → i64
val narrowed : i32 = i64_val:i32       // i64 → i32 (data loss visible)
val as_float : f64 = int_val:f64       // i32 → f64
val truncated : i32 = float_val:i32    // f64 → i32 (truncation visible)
```

## 🚨 Common Gotchas

### ❌ Expecting comptime types to become concrete automatically
```hexen
val x = 42              // This is comptime_int, not i32!
val y = 3.14            // This is comptime_float, not f64!
```

### ❌ Mixing concrete types without explicit conversion
```hexen
val a : i32 = 10
val b : i64 = 20
// val result = a + b   // ❌ Error: mixed concrete types need explicit conversion
// val result : i64 = a + b   // ❌ Still error: context doesn't help
val result : i64 = a:i64 + b   // ✅ Explicit conversion required
```

### ❌ Trying to make concrete types flexible again
```hexen
val concrete : i32 = compute_value()
// val flexible = concrete  // ❌ No, concrete stays concrete
```

## ✅ Common Success Patterns

### 🎯 Define flexible constants
```hexen
val CONFIG_SIZE = 1024 * 1024           // comptime_int (flexible!)
val small_buffer : i32 = CONFIG_SIZE    // Adapts to i32
val large_buffer : i64 = CONFIG_SIZE    // Same constant, different type
```

### 🎯 Use explicit conversions for mixed concrete operations
```hexen
val int_val : i32 = 42
val float_val : f64 = 3.14
// val result : f64 = int_val + float_val  // ❌ Error: mixed concrete types
val result : f64 = int_val:f64 + float_val  // ✅ Explicit conversion required
```

### 🎯 Preserve flexibility with val
```hexen
val math_expr = 42 * 3.14 + 100        // comptime_float (flexible!)
// Use in different contexts later...
val precise : f64 = math_expr           // High precision
val fast : f32 = math_expr             // Fast computation
```

## 🎓 Learning Progression

1. **Start Simple**: Use literals with explicit types (`val x : i32 = 42`)
2. **Learn Flexibility**: Try `val x = 42` and use in different contexts
3. **Understand Boundaries**: Learn when comptime becomes concrete
4. **Master Conversions**: Practice explicit conversion syntax
5. **Apply Patterns**: Use the four patterns in real code

## 🔍 Debugging Tips

### When things don't work as expected:
1. **Check if types are comptime or concrete**: `val x = 42` vs `val x : i32 = 42`
2. **Look for resolution boundaries**: Function calls, explicit types, mixed operations
3. **Add explicit context**: Use `: type` annotations to guide resolution
4. **Use explicit conversions**: When mixing concrete types, use `value:type`

---

**Remember**: Comptime types are your friend! They adapt to make your code more flexible while keeping all costs visible. 🦉 