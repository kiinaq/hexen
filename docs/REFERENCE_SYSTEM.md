# Hexen Reference System 🦉

*Design Exploration & Specification*

> **Design Note**: This document describes Hexen's reference system for achieving "pointers without pointers" - providing safe, efficient data sharing and access patterns without exposing dangerous low-level pointer syntax. References work exclusively with concrete types, maintaining Hexen's fundamental comptime/concrete type boundary.
>
> **NOT YET IMPLEMENTED!**

## Overview

Hexen's reference system introduces safe data sharing capabilities without traditional pointer syntax. The system provides memory-efficient data access while maintaining Hexen's core safety and transparency principles. References serve as a safe alternative to raw pointers, enabling efficient function parameter passing and data aliasing without memory management complexity.

**Core Design Constraint**: References work **exclusively with concrete types** - they cannot reference comptime types, maintaining the clean separation between compile-time and runtime data.

## Core Philosophy

### Design Principle: Safe Data Access for Concrete Types Only

Hexen's reference system follows the established **"Ergonomic Literals + Transparent Runtime Costs"** philosophy while introducing a critical constraint:

- **Concrete Types Only**: References can only point to runtime-allocated, concrete data
- **Transparent Access Costs**: Reference operations are explicit and visible
- **Safe by Default**: No null pointer dereferences or dangling references
- **Memory Efficient**: Share data without copying large structures
- **Lifetime Managed**: Compiler prevents references from outliving their targets
- **Explicit Syntax**: All reference operations use clear, visible syntax (`&`)

This philosophy ensures that **data sharing is efficient and safe**, while **all reference operations are explicit and visible** in the code.

### The Fundamental Boundary: Comptime vs Concrete

**Key Insight**: References exist in **runtime memory** and can only point to **runtime-allocated data**. Comptime types live in **compiler memory** during compilation and cannot be referenced.

```hexen
// ❌ INVALID: Cannot reference comptime types
val flexible = 42           // comptime_int (compiler memory only)
val &invalid = &flexible    // Error: Cannot reference comptime type

// ✅ VALID: References only to concrete types
val concrete : i32 = 42     // concrete i32 (runtime memory)
val &valid : i32 = &concrete   // OK: Reference to concrete i32
```

**Why this boundary matters:**
- **Memory Reality**: References need actual memory addresses (runtime concept)
- **Lifetime Safety**: Comptime values have no runtime lifetime to manage
- **Type System Integrity**: Maintains clean separation between compile-time and runtime
- **Performance Clarity**: Reference costs are always runtime costs (visible and explicit)

## Fundamental Mechanism

Before diving into syntax details, it's essential to understand the basic referencing and dereferencing mechanism that forms the foundation of Hexen's reference system.

### What is a Reference?

A **reference** is essentially **another name for the same data**. Instead of copying data, a reference provides direct access to the original variable's memory location. Think of it as creating an "alias" or "nickname" for existing data.

```hexen
// Without references: Data copying
val original : i32 = 42
val copy : i32 = original           // Creates a separate copy (different memory)
// Now we have TWO i32 values in memory: original and copy

// With references: Data sharing
val original : i32 = 42
val &alias : i32 = &original        // Creates alias to same data (same memory)
// We still have ONE i32 value in memory, but TWO names: original and alias
```

### The Two Operations: Referencing and Dereferencing

#### **Referencing (`&variable`)**: Creating Access to Data
The `&` operator **creates a reference** to existing concrete data:

```hexen
val data : i32 = 42                 // Concrete data in memory
val &ref : i32 = &data              // &data creates reference to that memory location
```

**Mental Model**: `&data` means "create access path to the memory where `data` lives"

#### **Dereferencing: Automatic in Hexen**
Unlike C/C++ where you need `*pointer` to access data through a pointer, Hexen performs **automatic dereferencing**. When you use a reference in an expression, it automatically accesses the underlying data:

```hexen
val number : i32 = 42
val &number_ref : i32 = &number

// Automatic dereferencing - no special syntax needed
val doubled : i32 = number_ref * 2  // Automatically reads through reference: 42 * 2 = 84
val comparison : bool = number_ref > 30  // Automatically reads through reference: 42 > 30 = true

// In C, you would need: *number_ref * 2
// In Hexen: Just use the reference name naturally
```

### Basic Mental Model

Think of references as **transparent windows** to data:

```hexen
val original_data : i32 = 100       // A box containing the number 100
val &window : i32 = &original_data  // A window looking into that same box

// Looking through the window (reading)
val value : i32 = window            // Sees 100 (same as original_data)

// Changing through the window (writing - if mutable)
mut original_data : i32 = 100
mut &window : i32 = &original_data
window = 200                        // Changes the box to contain 200
// Now original_data is also 200 - same box, different access paths
```

### Why References Are Useful

#### **Problem**: Expensive Data Copying
```hexen
// Without references: Expensive copying
val large_array : [10000]f64 = load_scientific_data()

func process_slowly(data: [10000]f64) : f64 = {
    // This function receives a COPY of all 10,000 numbers!
    // Memory usage: Original + Copy = 160KB
    return data[0] + data[9999]
}

val result : f64 = process_slowly(large_array)  // Copies 80KB of data!
```

#### **Solution**: Efficient Data Sharing
```hexen
// With references: Efficient sharing
val large_array : [10000]f64 = load_scientific_data()

func process_efficiently(&data: [10000]f64) : f64 = {
    // This function receives a REFERENCE to the original data!
    // Memory usage: Just original = 80KB
    return data[0] + data[9999]  // Automatic dereferencing
}

val result : f64 = process_efficiently(&large_array)  // No copying!
```

### Simple Before/After Comparison

#### **Traditional Approach (Data Copying)**
```hexen
val config : [1000]string = load_configuration()

func validate_config(cfg: [1000]string) : bool = {
    // Receives COPY of 1000 strings - expensive!
    return cfg[0] != "" && cfg[999] != ""
}

func process_config(cfg: [1000]string) : void = {
    // Another COPY of 1000 strings!
    // Total memory: Original + Copy1 + Copy2
}

validate_config(config)         // Copy 1000 strings
process_config(config)          // Copy 1000 strings again!
```

#### **Reference Approach (Data Sharing)**
```hexen
val config : [1000]string = load_configuration()

func validate_config(&cfg: [1000]string) : bool = {
    // Receives REFERENCE to original - efficient!
    return cfg[0] != "" && cfg[999] != ""  // Automatic dereferencing
}

func process_config(&cfg: [1000]string) : void = {
    // Another REFERENCE to same data!
    // Total memory: Just original
}

validate_config(&config)        // Share original data
process_config(&config)         // Share same original data!
```

**Key Benefits**:
- **Memory Efficient**: One copy of data, multiple access paths
- **Performance**: No expensive copying operations
- **Automatic**: Dereferencing happens transparently
- **Safe**: No manual pointer arithmetic or null pointer risks

This fundamental mechanism enables efficient data sharing while maintaining Hexen's safety and clarity principles. Now let's explore the specific syntax patterns for implementing this mechanism.

## Basic Reference Syntax

### Reference Variable Declaration

References are declared using the `&` operator in both the identifier and the assignment:

#### **Syntax Pattern: Explicit Types Required**
```hexen
val &reference_name : concrete_type = &target_variable
mut &reference_name : concrete_type = &target_variable
```

**Critical Requirement**: Both the reference and its target must have **explicit concrete types**.

#### **Basic Reference Examples**
```hexen
// ✅ Valid reference declarations (explicit concrete types)
val data : i32 = 42                 // Concrete i32 variable
val &data_ref : i32 = &data         // Reference to concrete i32

val array : [5]f64 = [1.0, 2.0, 3.0, 4.0, 5.0]  // Concrete array
val &array_ref : [5]f64 = &array    // Reference to concrete array

val message : string = "hello"      // Concrete string
val &msg_ref : string = &message    // Reference to concrete string
```

#### **Invalid Reference Attempts**
```hexen
// ❌ ERRORS: Cannot reference comptime types
val flexible_int = 42               // comptime_int
// val &bad_ref = &flexible_int     // Error: Cannot reference comptime type
// val &bad_ref : i32 = &flexible_int  // Error: &flexible_int is not concrete

val flexible_array = [1, 2, 3]      // comptime_array_int
// val &bad_array_ref = &flexible_array // Error: Cannot reference comptime type

// ❌ ERRORS: Missing explicit types
val concrete : i32 = 42
// val &missing_type = &concrete    // Error: Reference requires explicit type
```

### Reference Function Parameters

Functions can declare parameters that expect references, requiring callers to pass references explicitly:

#### **Function Parameter Syntax**
```hexen
func function_name(&param_name: concrete_type) : return_type = {
    // Function body using param_name (automatically dereferenced)
}
```

#### **Function Parameter Examples**
```hexen
// Function accepting reference to i32
func increment(&value: i32) : void = {
    value = value + 1           // Automatic dereferencing - modifies original
}

// Function accepting reference to array (efficient - no copy)
func sum_array(&data: [_]i32) : i32 = {
    val total : i32 = 0
    // Array iteration would access data directly (no copy)
    return total
}

// Function accepting reference to large structure (efficient)
func process_config(&config: [1000]f64) : f64 = {
    return config[0] * config[999]  // Direct access to original data
}
```

### Function Call Syntax

When calling functions with reference parameters, use `&` to pass references to concrete variables:

```hexen
val number : i32 = 10               // Concrete i32
increment(&number)                  // Pass reference to concrete variable

val data : [5]i32 = [1, 2, 3, 4, 5] // Concrete array
val result : i32 = sum_array(&data) // Pass reference to concrete array

// ❌ ERRORS: Cannot pass comptime types by reference
val flexible = 42                   // comptime_int
// increment(&flexible)             // Error: Cannot reference comptime type

// ❌ ERRORS: Cannot pass non-references to reference parameters
val concrete : i32 = 42
// increment(concrete)              // Error: Function expects reference, got value
```

## Integration with Existing Type System

### Explicit Type Requirement

References require explicit concrete types to prevent collision with Hexen's comptime type system:

```hexen
// ===== COMPTIME TYPES (No References Allowed) =====
val flexible = 42                   // comptime_int (stays flexible)
val flexible_array = [1, 2, 3]      // comptime_array_int (stays flexible)

// These preserve comptime flexibility for later context-dependent resolution
val as_i32 : i32 = flexible         // comptime_int → i32
val as_i64 : i64 = flexible         // Same source → i64
val as_f64 : f64 = flexible         // Same source → f64

// ===== CONCRETE TYPES (References Allowed) =====
val concrete : i32 = 42             // Explicit concrete i32
val concrete_array : [_]i32 = [1, 2, 3]  // Explicit concrete array

// References work with concrete types only
val &ref_int : i32 = &concrete      // ✅ OK: Reference to concrete i32
val &ref_array : [3]i32 = &concrete_array  // ✅ OK: Reference to concrete array

// ===== THE BOUNDARY IS CLEAR =====
// Comptime types: Flexible, no references, compile-time evaluation
// Concrete types: Fixed, can be referenced, runtime memory allocation
```

### Mutability Semantics

References work with Hexen's `val`/`mut` mutability system through a **view-based approach**: reference mutability determines the **permissions of the view**, while target mutability determines the **underlying data constraints**.

#### **The Fundamental Rule: Reference Mutability = View Permissions**

- **`val &ref`** = **Read-only view** (regardless of target mutability)
- **`mut &ref`** = **Read-write view** (requires mutable target)

#### **Mutability Compatibility Matrix**

| Target Data | Reference Type | Result | Explanation |
|-------------|---------------|---------|-------------|
| `val data` | `val &ref` | ✅ **Valid** | Read-only view of immutable data |
| `val data` | `mut &ref` | ❌ **Compile Error** | Can't create writable view of immutable data |
| `mut data` | `val &ref` | ✅ **Valid** | Read-only view of mutable data |
| `mut data` | `mut &ref` | ✅ **Valid** | Read-write view of mutable data |

#### **Practical Examples**

```hexen
// ===== ✅ VALID: Read-only view of immutable data =====
val immutable_data : i32 = 42           // Immutable data
val &readonly_ref : i32 = &immutable_data  // Read-only view

val value : i32 = readonly_ref          // ✅ Can read through view
// readonly_ref = 10                   // ❌ Error: Read-only view cannot modify
// readonly_ref = &other_data          // ❌ Error: val reference cannot be rebound

// ===== ❌ INVALID: Cannot create writable view of immutable data =====
val immutable_data : i32 = 42           // Immutable data
// mut &invalid_ref : i32 = &immutable_data  // ❌ COMPILE ERROR!
// Error: Cannot create mutable reference to immutable data

// ===== ✅ VALID: Read-only view of mutable data =====
mut mutable_data : i32 = 42             // Mutable data
val &readonly_view : i32 = &mutable_data   // Read-only view of mutable data

val value : i32 = readonly_view         // ✅ Can read through view
// readonly_view = 10                  // ❌ Error: Read-only view cannot modify
// (but mutable_data = 10 would work)  // ✅ Original can still be modified directly

// ===== ✅ VALID: Read-write view of mutable data =====
mut mutable_data : i32 = 42             // Mutable data
mut other_mutable : i32 = 100           // Another mutable variable
mut &writable_view : i32 = &mutable_data   // Read-write view

val value : i32 = writable_view         // ✅ Can read through view
writable_view = 10                      // ✅ Can modify through view (mutable_data becomes 10)
writable_view = &other_mutable          // ✅ Can rebind mutable reference
```

#### **Key Design Benefits**

1. **Consistency**: Reference mutability works exactly like variable mutability
2. **Safety**: Compiler prevents contradictions (writable views of immutable data)
3. **Clarity**: `val &ref` always means "read-only", `mut &ref` always means "read-write"
4. **Flexibility**: Can create read-only views of mutable data for safety

### Automatic Dereferencing

References are automatically dereferenced in expressions - no explicit dereference operator needed:

```hexen
val data : i32 = 42
val &ref : i32 = &data

// Automatic dereferencing in expressions
val doubled : i32 = ref * 2         // Automatically reads data through reference
val comparison : bool = ref > 30    // Automatic dereferencing for comparisons

// Assignment through mutable references
mut value : i32 = 10
mut &value_ref : i32 = &value
value_ref = 20                      // Automatically writes through reference (value is now 20)

// Function calls with automatic dereferencing
func process_number(num: i32) : i32 = { return num * 2 }  // Function expects VALUE
val result : i32 = process_number(ref)  // Pass reference → automatically dereferences to i32 value

// Function calls with reference parameters
func process_reference(&num: i32) : i32 = { return num * 2 }  // Function expects REFERENCE
val ref_result : i32 = process_reference(&data)  // Pass reference to original data
```

### Type Conversions with References

References follow the same explicit conversion rules as other concrete types:

```hexen
val int_data : i32 = 42
val float_data : f64 = 3.14
val &int_ref : i32 = &int_data
val &float_ref : f64 = &float_data

// ❌ ERRORS: No automatic conversions between reference types
// val &mixed_ref : f64 = &int_data      // Error: i32 reference ≠ f64 reference
// val mixed_val : f64 = int_ref         // Error: i32 ≠ f64 (use int_ref:f64)

// ✅ Explicit conversions (on dereferenced values)
val converted : f64 = int_ref:f64       // Explicit: i32 → f64 conversion
val back_converted : i32 = float_ref:i32  // Explicit: f64 → i32 conversion

// ✅ Assignment context with explicit conversion
mut target : f64 = 0.0
target = int_ref:f64                    // Explicit conversion required
```

## Scope and Lifetime Safety

### Basic Lifetime Rules

References cannot outlive the variables they reference. The compiler enforces this through scope analysis:

```hexen
// ✅ VALID: Reference stays within scope of target
val data : i32 = 42
val &data_ref : i32 = &data
// Both data and data_ref valid until end of current scope

// ❌ INVALID: Reference escaping target scope
func create_dangling_ref() : &i32 = {
    val local_data : i32 = 42
    return &local_data                  // Error: Reference to local variable escaping scope
}

// ❌ INVALID: Reference outliving target in expression blocks
val &dangling_ref : i32 = {
    val temp_data : i32 = 42
    -> &temp_data                       // Error: Reference to local variable escaping block
}
```

## Error Messages

Reference-specific error messages provide clear guidance following Hexen's consistent error message patterns:

### Comptime Type Reference Errors
```
Error: Cannot create reference to comptime type 'comptime_int'
  Variable 'flexible' has comptime type that exists only during compilation
  Suggestion: Use explicit type annotation to create concrete variable:
    val concrete : i32 = 42
    val &ref : i32 = &concrete
```

### Missing Type Annotation Errors
```
Error: Reference declaration requires explicit type annotation
  Reference '&data_ref' must specify target type
  Suggestion: Add explicit type annotation:
    val &data_ref : i32 = &data
```

### Lifetime/Scope Errors
```
Error: Reference to local variable 'temp' escaping scope
  Local variable will be destroyed when leaving block/function
  Suggestion: Return copy of data instead of reference:
    return temp  // Returns copy of value
```

### Mutability Mismatch Errors
```
Error: Cannot create mutable reference to immutable data
  Variable 'immutable_data' is declared with 'val' (immutable)
  Cannot create 'mut &ref' (writable view) of immutable data
  Suggestion: Use read-only reference instead:
    val &readonly_ref : i32 = &immutable_data

Error: Cannot modify data through read-only reference '&readonly_ref'
  Reference declared with 'val' provides read-only view
  Suggestion: Use mutable reference for modification:
    mut &writable_ref : i32 = &mutable_data
```

## Examples

### Basic Reference Usage

```hexen
// Basic reference to integer
val number : i32 = 42
val &number_ref : i32 = &number
val doubled : i32 = number_ref * 2      // Automatic dereferencing

// Reference to array
val data : [3]f64 = [1.0, 2.0, 3.0]
val &data_ref : [3]f64 = &data          // Reference to array
val first : f64 = data_ref[0]           // Access through reference

// Mutable references
mut counter : i32 = 0
mut &counter_ref : i32 = &counter
counter_ref = 10                        // Modifies original counter
counter_ref = counter_ref + 5           // counter is now 15
```

### Comptime vs Concrete Boundary

```hexen
// ❌ Cannot reference comptime types
val flexible = 42                       // comptime_int
// val &bad_ref = &flexible             // Error: Cannot reference comptime type

// ✅ Can reference concrete types
val concrete : i32 = 42                 // Concrete i32
val &good_ref : i32 = &concrete         // OK: Reference to concrete type
```

### Common Error Patterns

```hexen
// ❌ Missing explicit type
val data : i32 = 42
// val &missing_type = &data            // Error: Reference requires explicit type

// ❌ Mutability mismatch
val immutable : i32 = 42
// mut &invalid = &immutable            // Error: Cannot create writable view of immutable data

// ✅ Correct patterns
val &readonly : i32 = &immutable        // Read-only view of immutable data
mut mutable : i32 = 42
mut &writable : i32 = &mutable          // Read-write view of mutable data
```

## Benefits

### Developer Experience

1. **Safe Data Sharing**: Efficient access to large data structures without copying
2. **Clear Syntax**: `&` operator provides familiar, readable reference semantics
3. **Automatic Dereferencing**: No manual pointer arithmetic or dereferencing operators
4. **Explicit Costs**: All reference operations are visible in the code
5. **Type Safety**: References cannot be null or point to invalid memory

### Performance Benefits

1. **Zero-Copy Access**: Large arrays and structures can be shared without duplication
2. **Function Parameter Efficiency**: Pass large data by reference instead of copying
3. **Memory Efficiency**: Multiple names for same data without memory overhead
4. **Compile-Time Optimization**: Compiler can optimize knowing reference relationships

### Safety Guarantees

1. **No Null References**: All references must point to valid, concrete variables
2. **Lifetime Safety**: References cannot outlive their target variables
3. **No Dangling References**: Scope analysis prevents references to destroyed data
4. **Type Safety**: References maintain strict type compatibility with their targets
5. **Mutability Safety**: Reference mutability interacts safely with target mutability

### Integration Benefits

1. **Comptime Boundary Preservation**: References only work with concrete types
2. **Consistent with Hexen Philosophy**: Explicit costs, transparent operations
3. **Type System Harmony**: References integrate with existing conversion rules
4. **Error Message Consistency**: Clear, actionable guidance following Hexen patterns
5. **Mental Model Simplicity**: References as "access mechanism, not types"

## Future Considerations

This initial reference system establishes the foundation for potential future enhancements:

1. **Array Slicing**: `&array[start:end]` for efficient sub-array access
2. **Optional References**: Safe handling of references that might not point to data
3. **Function References**: Safe function pointer equivalents
4. **Resource Management**: Automatic cleanup patterns using reference lifetimes

However, the current specification focuses on the essential, proven patterns that integrate cleanly with Hexen's existing type system and philosophy.

---

This reference system extends Hexen's "Ergonomic Literals + Transparent Costs" philosophy to data sharing, providing safe and efficient alternatives to traditional pointer operations while maintaining the language's commitment to safety, clarity, and performance transparency.