# Literal Overflow Behavior in Hexen 🦉

## Philosophy

Hexen follows a philosophy of compile-time safety and the "Transparent Costs" principle when handling literal overflow. The language is designed to:

- **Detect overflow at compile time** for comptime literals
- **Prevent silent data loss** through explicit conversion requirements
- **Provide clear error messages** with guidance for resolution
- **Make costs transparent** by requiring explicit acknowledgment of truncation

## Current Behavior Analysis

### Problematic Case
```hexen
val truncated:i32 = 4294967296  // 2^32, too large for i32
```

**Current Status**: Implementation dependent behavior that contradicts Hexen's safety principles.

**Issue**: The current implementation has ambiguous behavior for literals that exceed the target type's range, leading to inconsistent results.

## Specification

### Overflow Detection Rules

#### ✅ Valid Cases
```hexen
// Comptime literals within range
val valid_i32:i32 = 2147483647     // Max i32 value
val valid_i64:i64 = 9223372036854775807  // Max i64 value

// Comptime type preservation (stays flexible)
val flexible = 4294967296          // comptime_int (no overflow yet)
val as_i64:i64 = flexible          // comptime_int → i64 (fits)
```

#### ❌ Overflow Errors
```hexen
// Compile-time overflow detection
val overflow_i32:i32 = 4294967296     // Error: Literal overflows i32 range
val overflow_i64:i64 = 18446744073709551616  // Error: Literal overflows i64 range

// Float precision overflow
val overflow_f32:f32 = 3.4028235e+39  // Error: Literal overflows f32 range
```

#### 🔧 Explicit Conversion (Future Consideration)
```hexen
// If truncation is truly intended (requires explicit acknowledgment)
val intended:i32 = 4294967296:i32   // Explicit truncation
```

## Type Range Reference

### Integer Types
| Type | Minimum Value | Maximum Value |
|------|---------------|---------------|
| `i32` | -2,147,483,648 | 2,147,483,647 |
| `i64` | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,807 |

### Float Types
| Type | Approximate Range | Precision |
|------|------------------|-----------|
| `f32` | ±3.4028235e+38 | ~7 decimal digits |
| `f64` | ±1.7976931e+308 | ~15 decimal digits |

### Common Overflow Examples
```hexen
// Integer overflow examples
val i32_overflow:i32 = 2147483648     // Error: Exceeds i32 max by 1
val i32_underflow:i32 = -2147483649   // Error: Below i32 min by 1

// Float overflow examples  
val f32_overflow:f32 = 3.5e+38        // Error: Exceeds f32 range
val f32_precision:f32 = 1.23456789012345  // Error: Exceeds f32 precision
```

## Error Messages

### Standard Format
```
Error: Literal [value] overflows [target_type] range
  Expected: [min_value] to [max_value]
  Suggestion: Use explicit conversion if truncation is intended: value:[target_type]
```

### Examples
```
Error: Literal 4294967296 overflows i32 range
  Expected: -2147483648 to 2147483647
  Suggestion: Use explicit conversion if truncation is intended: 4294967296:i32

Error: Literal 3.5e+38 overflows f32 range  
  Expected: approximately ±3.4028235e+38
  Suggestion: Use f64 for extended range or explicit conversion: 3.5e+38:f32
```

## Language Comparison

### How Major Languages Handle Literal Overflow

| Language | Behavior | Safety Level |
|----------|----------|--------------|
| **Hexen** | ❌ Compile error (recommended) | 🟢 Very Safe |
| **Zig** | ❌ Compile error | 🟢 Very Safe |
| **Rust** | ❌ Compile error | 🟢 Very Safe |
| **Java** | ❌ Compile error | 🟢 Very Safe |
| **Go** | ❌ Compile error | 🟢 Very Safe |
| **C#** | ❌ Compile error | 🟢 Very Safe |
| **C/C++** | ⚠️ Warning + truncation | 🔴 Unsafe |
| **Python** | ✅ Arbitrary precision | 🟡 Different paradigm |

### Rationale for Hexen's Approach

Hexen follows the **modern systems programming language approach** (similar to Rust and other safety-focused languages) rather than the legacy C/C++ approach:

- **Compile-time safety** prevents runtime surprises
- **Explicit conversion syntax** makes truncation intentional and visible
- **Clear error messages** guide developers toward correct solutions
- **Consistency** with Hexen's "Transparent Costs" principle

## Implementation Notes

### Where Overflow Checking Occurs

1. **Comptime literal analysis** in `infer_type_from_value()`
2. **Type coercion** in `can_coerce()` when comptime types resolve to concrete types
3. **Assignment validation** in assignment and declaration analyzers

### Performance Implications

- **Compile-time only** - no runtime performance impact
- **Range checking** adds minimal compilation overhead
- **Early error detection** prevents runtime debugging sessions

### Edge Cases

```hexen
// Boundary values (should work)
val max_i32:i32 = 2147483647     // ✅ Exactly at boundary
val min_i32:i32 = -2147483648    // ✅ Exactly at boundary

// Hexadecimal literals
val hex_overflow:i32 = 0x100000000  // ❌ Error: 2^32 in hex

// Binary literals  
val bin_overflow:i32 = 0b100000000000000000000000000000000  // ❌ Error: 2^32 in binary

// Negative overflow
val neg_overflow:i32 = -2147483649   // ❌ Error: Below i32 minimum
```

## Integration with Type System

### Relationship to Comptime Types

Literal overflow checking integrates seamlessly with Hexen's comptime type system:

```hexen
// Comptime types remain flexible until forced to resolve
val flexible = 4294967296        // comptime_int (no error yet)
val as_i32:i32 = flexible        // Error: NOW detects overflow during coercion
val as_i64:i64 = flexible        // ✅ Coercion succeeds (fits in i64)
```

### Consistency with Explicit Conversion Rules

Overflow detection maintains consistency with Hexen's explicit conversion requirements:

```hexen
// All concrete conversions require explicit syntax
val small:i32 = 42
val large:i64 = small:i64         // ✅ Explicit conversion required

// Overflow detection follows same principle  
val overflow:i32 = 4294967296:i32 // 🔧 Explicit truncation (if implemented)
```

## Future Considerations

### Explicit Truncation Syntax

A future language enhancement might allow explicit truncation acknowledgment:

```hexen
// Hypothetical explicit truncation syntax
val truncated:i32 = 4294967296:i32   // Explicitly acknowledge truncation
val masked:i32 = 4294967296 & 0xFFFFFFFF  // Bitwise masking alternative
```

### Configurable Overflow Behavior

Advanced use cases might benefit from configurable overflow handling:

```hexen
// Hypothetical pragma for specific contexts
@allow_truncation
val legacy_compat:i32 = some_large_value:i32
```

## Conclusion

Hexen's literal overflow behavior prioritizes **compile-time safety** and **explicit intent** over convenience. This approach prevents entire classes of bugs while maintaining the language's core principle of transparent costs.

By following this proven safety model, Hexen ensures that:
- **No data is lost silently**
- **Programmer intent is explicit** 
- **Errors are caught early** in the development cycle
- **Code behavior is predictable** across all platforms

This specification eliminates the current "implementation dependent" ambiguity and establishes clear, safe behavior for all literal overflow scenarios.