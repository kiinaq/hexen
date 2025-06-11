# Hexen Binary Operations 🦉

## Overview

Hexen's binary operations system follows the **"Context-Guided Type Resolution"** philosophy, where assignment target types serve as anchors for resolving complex mixed-type expressions. This creates an elegant system that's both type-safe and ergonomic.

## Core Philosophy

### Context-Guided Resolution Strategy

Binary operations in Hexen follow a unified pattern that prioritizes consistency and explicitness:

1. **Safe Operations** (no context needed): Operations between identical types resolve automatically
2. **Ambiguous Operations** (context required): Mixed types (including mixed comptime types) need explicit target type
3. **Context Determines Behavior**: Target type guides the entire expression resolution (e.g., division behavior)
4. **No Hidden Defaults**: Operations maintain their operand types unless explicitly guided by context

This pattern is consistent with Hexen's broader design: **"Explicit Danger, Implicit Safety"** and **"Pedantic to write, but really easy to read"**.

## Operator Precedence

Binary operators follow standard mathematical precedence with explicit grouping for clarity.

### Precedence Levels (Highest to Lowest)

| Level | Operators | Associativity | Description |
|-------|-----------|---------------|-------------|
| 1 | `-`, `!` | Right | Unary minus, logical NOT |
| 2 | `*`, `/`, `%` | Left | Multiplication, division, modulo |
| 3 | `+`, `-` | Left | Addition, subtraction |
| 4 | `<`, `>`, `<=`, `>=` | Left | Relational comparison |
| 5 | `==`, `!=` | Left | Equality comparison |
| 6 | `&&` | Left | Logical AND |
| 7 | `\|\|` | Left | Logical OR |

### Precedence Examples

```hexen
// Mathematical precedence
val result1 : i32 = 2 + 3 * 4           // 2 + (3 * 4) = 14
val result2 : i32 = (2 + 3) * 4         // (2 + 3) * 4 = 20

// Comparison precedence  
val check1 : bool = 5 > 3 && 2 < 4      // (5 > 3) && (2 < 4) = true
val check2 : bool = 5 > 3 == 2 < 4      // (5 > 3) == (2 < 4) = true

// Explicit grouping for clarity
val complex : f64 = (a + b) * (c - d) / (e + f)
```

## Type Resolution Rules

### 1. Safe Operations (No Context Required)

These operations are unambiguous and resolve automatically:

#### Both Comptime Types
```hexen
val result1 = 42 + 100          // comptime_int + comptime_int = comptime_int
val result2 = 42 + 3.14         // comptime_int + comptime_float = comptime_float
val result3 = 3.14 + 2.71       // comptime_float + comptime_float = comptime_float
val result4 = 42 * 3.14         // comptime_int * comptime_float = comptime_float
```

#### One Comptime, One Concrete
The comptime type adapts to the concrete type:
```hexen
val x : i32 = 10
val y : f64 = 3.14

val result1 = x + 42            // i32 + comptime_int = i32
val result2 = y + 42            // f64 + comptime_int = f64  
val result3 = x + 3.14          // i32 + comptime_float = f64 (promotion)
val result4 = y * 2             // f64 * comptime_int = f64
```

#### Both Same Concrete Type
```hexen
val a : i32 = 10
val b : i32 = 20
val c : f64 = 3.14
val d : f64 = 2.71

val result1 = a + b             // i32 + i32 = i32
val result2 = c * d             // f64 * f64 = f64
```

### 2. Context-Required Operations

Mixed concrete types require explicit target context:

#### The Problem
```hexen
val a : i32 = 10
val b : i64 = 20

// ❌ Ambiguous - which type should win?
val result = a + b              // Error: "Mixed-type operation 'i32 + i64' requires explicit result type"
```

#### The Solution - Explicit Context
```hexen
val a : i32 = 10
val b : i64 = 20

// ✅ Context provides resolution
val as_i32 : i32 = a + b        // i64 → i32 coercion (may truncate)
val as_i64 : i64 = a + b        // i32 → i64 widening (safe)  
val as_f64 : f64 = a + b        // Both → f64 conversion
```

### 3. Comptime Type Promotion Rules

When comptime types are mixed in expressions, promotion follows a hierarchy that preserves maximum precision:

#### Comptime Type Hierarchy
```hexen
// Safe comptime operations (same type)
comptime_int + comptime_int = comptime_int
comptime_int * comptime_int = comptime_int
comptime_int / comptime_int = comptime_int      // Integer division
comptime_float + comptime_float = comptime_float
comptime_float * comptime_float = comptime_float
comptime_float / comptime_float = comptime_float  // Float division

// Mixed comptime operations require explicit context
val mixed1 : f64 = 42 + 3.14        // ✅ Explicit context: comptime_int + comptime_float → f64
val mixed2 : f32 = 42 * 3.14        // ✅ Explicit context: comptime_int * comptime_float → f32
val ambiguous = 42 + 3.14           // ❌ Error: Mixed comptime types require explicit result type

// Comparisons promote to most precise type for comparison only
val compared = 42 > 3.14            // ✅ OK: comparison promotes comptime_int → comptime_float, result is bool
```

#### Mixed Comptime and Concrete Types
```hexen
val concrete_int : i32 = 10
val concrete_float : f64 = 3.14

// Comptime types adapt to concrete types
val adapt1 = concrete_int + 42     // i32 + comptime_int = i32
val adapt2 = concrete_float * 2    // f64 + comptime_int = f64
val adapt3 = concrete_int + 3.14   // i32 + comptime_float = f64 (promotion)
```

### 4. Regular Type Promotion Rules

When combining different concrete numeric types, promotion follows these rules:

#### Automatic Promotion (Safe Operations)
```hexen
val int_val : i32 = 10
val float_val : f32 = 3.14

// Integer + Float = Float (promotion)
val promoted = int_val + float_val  // i32 + f32 = f32
```

#### Widening Hierarchy
For widening coercion:
- `i32` → `{i64, f32, f64}`
- `i64` → `{f32, f64}` (may lose precision for very large integers)
- `f32` → `{f64}`

## Context-Dependent Division

Division behavior in Hexen follows the **explicit context requirement** pattern: mixed operations require explicit context, while safe operations resolve automatically.

### Division Type Resolution Rules

#### Safe Division (No Context Required)
```hexen
// Both operands are same comptime type - operation matches operand type
val default1 = 7 / 3            // comptime_int / comptime_int → comptime_int (integer division: 2)
val default2 = 10 / 4           // comptime_int / comptime_int → comptime_int (integer division: 2)
val default3 = 10.5 / 2.1       // comptime_float / comptime_float → comptime_float (float division: 5.0)

// Same concrete types - operation type matches operands
val int_only : i32 = 10
val other_int : i32 = 3
val same_type = int_only / other_int  // i32 / i32 → i32 (integer division: 3)
```

#### Context-Required Division
```hexen
// Mixed concrete types require explicit context
val int_val : i32 = 10
val float_val : f64 = 3.0
val ambiguous1 = int_val / float_val  // ❌ Error: Mixed-type division requires explicit result type

// Mixed comptime types require explicit context
val ambiguous2 = 42 / 3.14            // ❌ Error: comptime_int / comptime_float requires explicit result type

// ✅ Explicit context resolves the ambiguity
val as_float : f64 = int_val / float_val  // Both coerce to f64, float division: 3.333...
val as_int : i32 = int_val / float_val    // Both coerce to i32, integer division: 3
val mixed_as_float : f64 = 42 / 3.14      // comptime types coerce to f64, float division: 13.375...
val mixed_as_int : i32 = 42 / 3.14        // comptime types coerce to i32, integer division: 13
```

### Context-Dependent Division Behavior

When explicit context is provided, division behavior adapts to the target type:

#### Integer Division (Target Type is Integer)
```hexen
val quotient1 : i32 = 7 / 3     // comptime division → i32: integer division = 2
val quotient2 : i64 = 10 / 4    // comptime division → i64: integer division = 2  
val quotient3 : i32 = 9 / 2     // comptime division → i32: integer division = 4
```

#### Float Division (Target Type is Float)
```hexen
val precise1 : f64 = 7 / 3      // comptime division → f64: float division = 2.333...
val precise2 : f32 = 10 / 4     // comptime division → f32: float division = 2.5
val precise3 : f64 = 9 / 2      // comptime division → f64: float division = 4.5
```

### Complex Division Examples

```hexen
// Context guides entire expression including division
val complex_int : i32 = (20 + 10) / (2 + 1)    // All comptime → i32: integer division = 10
val complex_float : f64 = (20 + 10) / (2 + 1)  // All comptime → f64: float division = 10.0

// Mixed expressions with explicit context
val mixed_int : i32 = (20 * 3.6) / 2           // Float computation then truncate: 36
val mixed_float : f64 = (20 * 3.6) / 2         // Float computation: 36.0
```

## Complex Float-to-Integer Conversion

When complex expressions involving float operations target integer types, Hexen uses a **two-phase resolution strategy**: compute the entire expression using the most appropriate numeric semantics, then convert the final result to the target type.

### Resolution Strategy

```hexen
// Complex float expression targeting integer type
val result : i32 = (10.5 * 20.3) / 2.1
// Resolution process:
// 1. Expression analysis: All operands are comptime_float
// 2. Computation: Float semantics throughout (10.5 * 20.3 = 213.15, then 213.15 / 2.1 = 101.5)
// 3. Final conversion: 101.5 → i32 = 101 (truncation)
```

### Mixed Comptime and Concrete Types

```hexen
val int_var : i32 = 20
val result : i32 = (int_var * 3.6) / 2.1
// Resolution process:
// 1. Mixed types: i32 and comptime_float 
// 2. Target context: i32
// 3. Computation strategy: Promote to float for accuracy (20 * 3.6 = 72.0, then 72.0 / 2.1 = 34.285...)
// 4. Final conversion: 34.285... → i32 = 34 (truncation)
```

### Precision Loss and Truncation Rules

```hexen
// Float-to-integer conversion always truncates (towards zero)
val truncated1 : i32 = 10.9 / 2.0   // 5.45 → 5 (truncation)
val truncated2 : i32 = -10.9 / 2.0  // -5.45 → -5 (truncation towards zero)

// Large float values
val large : i32 = (1.5 * 1000.0)    // 1500.0 → 1500 (exact conversion)
val precise : i32 = (22.0 / 7.0)    // 3.142857... → 3 (truncation)
```

### Overflow and Range Checking

```hexen
// Compile-time overflow detection for constant expressions
val overflow : i32 = (1.0e10 * 1.0e10) / 1.0e5  // Error: Result 1.0e15 exceeds i32 range

// Runtime overflow behavior (implementation-defined)
val runtime_calc : i32 = (some_float * large_float) / divisor
// Note: Runtime overflow behavior follows platform conventions
```

## Complex Expression Resolution

The target type guides the **entire expression tree**, not just individual operations.

### Nested Operations with Context

```hexen
val a : i32 = 10
val b : i64 = 20
val c : f32 = 3.14

// Target type guides all operations in the expression
val result : f64 = a + b * c    // All types coerce to f64 context
//                 ^   ^   ^
//                i32 i64 f32 → all become f64 for computation

val result : i32 = a + b        // i64 coerces to i32 context
val result : f64 = (a + 42) * (b + 3.14)  // Complex nested expression, f64 context
```

### Expression Resolution Strategy

Hexen uses a **two-phase resolution approach** that balances precision with target type requirements:

#### Phase 1: Semantic Analysis
1. **Determine expression semantics** based on operand types
2. **Apply promotion rules** for comptime and mixed types
3. **Choose computation strategy** for maximum precision

#### Phase 2: Target Type Conversion
1. **Compute expression** using determined semantics
2. **Convert final result** to target type if needed
3. **Apply truncation/rounding** rules as appropriate

### Resolution Examples

#### Comptime Expression with Target Context
```hexen
val complex : f32 = ((10 + 20) * 3.14) / (5 + 2)
// Phase 1 - Semantic Analysis:
// - (10 + 20): comptime_int + comptime_int = comptime_int
// - 3.14: comptime_float 
// - comptime_int * comptime_float = comptime_float (promotion)
// - (5 + 2): comptime_int + comptime_int = comptime_int
// - comptime_float / comptime_int = comptime_float
// Expression type: comptime_float

// Phase 2 - Target Conversion:
// - Compute: ((30) * 3.14) / (7) = 94.2 / 7 = 13.457...
// - Convert: comptime_float → f32 = 13.457...f32
```

#### Mixed Concrete Types with Context
```hexen
val a : i32 = 10
val b : i64 = 20
val result : f64 = a + b
// Phase 1 - Semantic Analysis:
// - Mixed concrete types (i32 + i64) require context
// - Target type f64 provides context
// - Both operands can coerce to f64

// Phase 2 - Target Conversion:
// - Convert operands: i32(10) → f64(10.0), i64(20) → f64(20.0)  
// - Compute: f64(10.0) + f64(20.0) = f64(30.0)
```

## Comparison Operations

Comparison operators produce boolean results and have special type resolution rules.

### Basic Comparisons

```hexen
val result1 : bool = 10 < 20            // comptime_int < comptime_int = bool
val result2 : bool = 3.14 > 2.71        // comptime_float > comptime_float = bool
val result3 : bool = 42 == 42           // comptime_int == comptime_int = bool
val result4 : bool = "hello" == "world" // string == string = bool
```

### Mixed-Type Comparisons

Mixed-type comparisons follow promotion rules:

```hexen
val int_val : i32 = 10
val float_val : f64 = 10.0

val comparison1 : bool = int_val < float_val    // i32 promotes to f64 for comparison
val comparison2 : bool = 42 > 3.14              // comptime_int vs comptime_float = comptime_float
```

### Equality with Type Safety

```hexen
val str_val : string = "hello"
val int_val : i32 = 42

// ❌ Type error - cannot compare different fundamental types
val invalid : bool = str_val == int_val  // Error: Cannot compare string and i32
```

## Logical Operations

Logical operators work exclusively with boolean values.

### Basic Logical Operations

```hexen
val and_result : bool = true && false   // false
val or_result : bool = true || false    // true
val not_result : bool = !true           // false
```

### Short-Circuit Evaluation

Logical operators use short-circuit evaluation:

```hexen
val a : bool = false
val b : bool = true

// Short-circuit: if a is false, b is never evaluated
val result1 : bool = a && expensive_function()  // expensive_function() not called

// Short-circuit: if a is false, b is evaluated  
val result2 : bool = a || expensive_function()  // expensive_function() is called
```

### Logical with Comparisons

```hexen
val age : i32 = 25
val has_license : bool = true

val can_drive : bool = age >= 18 && has_license
val needs_permission : bool = age < 18 || !has_license
```

## Arithmetic Operations

### Addition and Subtraction

```hexen
// Basic arithmetic with context
val sum : i32 = 10 + 20          // comptime_int + comptime_int → i32
val diff : f64 = 10.5 - 3.2     // comptime_float - comptime_float → f64

// Mixed arithmetic with context
val a : i32 = 10
val b : i64 = 20
val mixed : i64 = a + b          // i32 → i64 (widening)
```

### Multiplication and Division

```hexen
// Multiplication
val product : f32 = 3.14 * 2     // comptime_float * comptime_int → f32

// Division (context-dependent behavior)
val int_division : i32 = 10 / 3  // comptime division → i32: integer division = 3 (truncated)
val float_division : f64 = 10 / 3 // comptime division → f64: float division = 3.333...
```

### Modulo Operation

```hexen
val remainder : i32 = 17 % 5     // Integer modulo: 2

// Modulo requires integer operands
val a : f64 = 17.5
val b : f64 = 5.0
// val invalid = a % b           // ❌ Error: Modulo requires integer types
```

## Assignment Context Propagation

The assignment target type provides context that flows through the entire expression.

### Variable Declaration Context

```hexen
// Target type guides expression resolution
val precise : f64 = (20 * 3.6) / 2     // Float math: 36.0
val truncated : i32 = (20 * 3.6) / 2   // Float math then truncate: 36
val integer : i32 = 20 * 3 / 2         // Integer math: 30
```

### Assignment Statement Context

```hexen
mut flexible : f64 = 0.0

// Assignment target provides context
flexible = 42                   // comptime_int → f64
flexible = (10 + 20) / 3        // Expression resolves in f64 context
flexible = some_i32 + some_i64  // Would need: flexible = f64_context(some_i32 + some_i64)
```

### Function Return Context

```hexen
func calculate() : f32 = {
    val a : i32 = 10
    val b : i64 = 20
    
    // Return type provides context for mixed expression
    return a + b                // i32 + i64 → f32 (return type context)
}
```

## Error Handling and Messages

### Mixed-Type Operation Errors

When mixed concrete types are used without context:

```
Error: Mixed-type operation 'i32 + i64' requires explicit result type annotation
  --> src/example.hxn:5:17
   |
5  |     val result = a + b
   |                  ^^^^^
   |
Help: Add type annotation to specify result type:
      val result : i64 = a + b    // Widen i32 to i64
   or val result : f32 = a + b    // Convert both to f32
   or val result : f64 = a + b    // Convert both to f64
```

### Invalid Type Combination Errors

```
Error: Cannot apply operator '+' to types 'string' and 'i32'
  --> src/example.hxn:3:25
   |
3  |     val invalid = "hello" + 42
   |                   ^^^^^^^^^^^
   |
Note: String concatenation requires both operands to be strings
      Consider: "hello" + string_representation(42)
```

### Division by Zero (Future)

```
Warning: Potential division by zero detected
  --> src/example.hxn:7:19
   |
7  |     val result = x / y
   |                  ^^^^^
   |
Note: Consider adding runtime check: if y != 0 { x / y } else { ... }
```

## Grammar Extensions

### Lark Grammar for Binary Operations

```lark
// Current expression rule
expression: NUMBER | STRING | BOOLEAN | IDENTIFIER | block

// Extended expression rule with binary operations
expression: binary_expr

binary_expr: logical_or

logical_or: logical_and (("||") logical_and)*
logical_and: equality (("&&") equality)*
equality: relational (("==" | "!=") relational)*
relational: additive (("<" | ">" | "<=" | ">=") additive)*
additive: multiplicative (("+" | "-") multiplicative)*
multiplicative: unary (("*" | "/" | "%") unary)*
unary: ("-" | "!")? primary
primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")"
```

### AST Node Structure

Binary operations create AST nodes with this structure:

```python
{
    "type": "binary_operation",
    "operator": "+",  # The operator: +, -, *, /, %, <, >, <=, >=, ==, !=, &&, ||
    "left": {...},    # Left operand (expression)
    "right": {...},   # Right operand (expression)
}
```

## Implementation Guidelines

### Semantic Analyzer Extensions

#### Expression Analysis with Context

```python
def _analyze_expression(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze expression with optional target type context for mixed operations."""
    expr_type = node.get("type")
    
    if expr_type == "binary_operation":
        return self._analyze_binary_operation(node, target_type)
    elif expr_type == "literal":
        return self._infer_type_from_value(node)
    # ... other expression types
```

#### Binary Operation Analysis

```python
def _analyze_binary_operation(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Analyze binary operation with context-guided type resolution."""
    operator = node.get("operator")
    left_node = node.get("left")
    right_node = node.get("right")
    
    # Analyze operands (may need context for nested operations)
    left_type = self._analyze_expression(left_node, target_type)
    right_type = self._analyze_expression(right_node, target_type)
    
    # Resolve operation type based on operator and operands
    return self._resolve_binary_operation(left_type, right_type, operator, target_type, node)
```

#### Type Resolution Logic

```python
def _resolve_binary_operation(self, left: HexenType, right: HexenType, op: str, 
                             target_type: Optional[HexenType], node: Dict) -> HexenType:
    """Resolve binary operation type with context guidance."""
    
    # 1. Handle comparison operators (always return bool)
    if op in {"<", ">", "<=", ">=", "==", "!="}:
        if self._can_compare_types(left, right):
            return HexenType.BOOL
        else:
            self._error(f"Cannot compare types {left.value} and {right.value}", node)
            return HexenType.UNKNOWN
    
    # 2. Handle logical operators (require bool operands)
    if op in {"&&", "||"}:
        if left == HexenType.BOOL and right == HexenType.BOOL:
            return HexenType.BOOL
        else:
            self._error(f"Logical operator {op} requires boolean operands", node)
            return HexenType.UNKNOWN
    
    # 3. Handle arithmetic operators with context
    if op in {"+", "-", "*", "/", "%"}:
        return self._resolve_arithmetic_operation(left, right, op, target_type, node)
    
    # 4. Unknown operator
    self._error(f"Unknown binary operator: {op}", node)
    return HexenType.UNKNOWN
```

#### Arithmetic Resolution with Context

```python
def _resolve_arithmetic_operation(self, left: HexenType, right: HexenType, op: str,
                                target_type: Optional[HexenType], node: Dict) -> HexenType:
    """Resolve arithmetic operation with context-dependent behavior."""
    
    # Safe operations (no context needed)
    if self._is_safe_arithmetic_operation(left, right):
        result_type = self._resolve_safe_arithmetic(left, right, op)
        
        # Special case: Division behavior depends on target type
        if op == "/" and target_type:
            return target_type  # Division adapts to target type
        
        return result_type
    
    # Ambiguous operations (context required)
    if target_type is None:
        self._error(
            f"Mixed-type operation '{left.value} {op} {right.value}' requires explicit result type annotation",
            node
        )
        return HexenType.UNKNOWN
    
    # Context provided - validate coercion and return target type
    if self._can_coerce(left, target_type) and self._can_coerce(right, target_type):
        return target_type
    else:
        self._error(
            f"Cannot coerce operands {left.value} and {right.value} to target type {target_type.value}",
            node
        )
        return HexenType.UNKNOWN
```

### Variable Declaration Enhancement

Pass target type context to expression analysis:

```python
def _analyze_variable_declaration_unified(self, name: str, type_annotation: str, value: Dict, ...):
    if type_annotation:
        var_type = self._parse_type(type_annotation)
        if value:
            # Pass target type as context for expression analysis
            value_type = self._analyze_expression(value, var_type)
            # Validate coercion as before...
```

## Examples

### Complete Binary Operations Showcase

```hexen
func demonstrate_binary_operations() : void = {
    // ===== Safe Operations (No Context Required) =====
    
    // Safe comptime operations (same type)
    val safe1 = 42 + 100           // comptime_int + comptime_int = comptime_int
    val safe2 = 3.14 * 2.71        // comptime_float * comptime_float = comptime_float
    val safe3 = 10 / 2             // comptime_int / comptime_int = comptime_int (integer division: 5)
    
    // One comptime, one concrete
    val x : i32 = 10
    val y : f64 = 3.14
    val safe4 = x + 42             // i32 + comptime_int = i32
    val safe5 = y * 2              // f64 * comptime_int = f64
    
    // ===== Context-Dependent Division =====
    
    val int_div : i32 = 7 / 3      // comptime division → i32: integer division = 2
    val float_div : f64 = 7 / 3    // comptime division → f64: float division = 2.333...
    val default_div = 7 / 3        // comptime_int / comptime_int → comptime_int: integer division = 2
    
    // ===== Complex Expressions with Context =====
    
    val complex_int : i32 = (20 + 10) * 3 / 2       // All integer: 45
    val complex_float : f64 = (20 + 10) * 3.0 / 2   // Mixed: 45.0
    val complex_mixed : i32 = (20 * 3.6) / 2        // Float calc → int: 36
    
    // ===== Mixed Types (Context Required) =====
    
    // Mixed comptime types require explicit context
    val mixed_explicit : f64 = 42 + 3.14      // ✅ Explicit context
    val mixed_explicit2 : i32 = 42 + 3.14     // ✅ Explicit context (truncation)
    // val mixed_ambiguous = 42 + 3.14        // ❌ Error: requires explicit result type
    
    // Mixed concrete types require explicit context
    val a : i32 = 10
    val b : i64 = 20
    val c : f32 = 3.14
    
    val as_i64 : i64 = a + b       // i32 → i64 widening
    val as_f32 : f32 = a + c       // i32 → f32 conversion
    val as_f64 : f64 = a + b + c   // All → f64 conversion
    
    // ===== Comparison Operations =====
    
    val cmp1 : bool = 10 < 20      // comptime_int comparison
    val cmp2 : bool = x > y        // i32 vs f64 (promotion)
    val cmp3 : bool = a == b       // i32 vs i64 (promotion)
    
    // ===== Logical Operations =====
    
    val logic1 : bool = true && false
    val logic2 : bool = (x > 5) || (y < 10.0)
    val logic3 : bool = !(x == 0) && (y != 0.0)
    
    // ===== Nested Complex Expressions =====
    
    val nested : f64 = ((a + b) * c) / (x + y)
    //                   ^^^^^^^^^     ^^^^^^^
    //                   i32+i64=i64   i32+f64=f64
    //                   i64*f32=f32   
    //                   f32/f64=f64 (final result)
    
    // With explicit context guidance:
    val guided : f32 = ((a + b) * c) / (x + y)
    //                   All operations resolve in f32 context
}

func demonstrate_precedence() : void = {
    // Mathematical precedence
    val math1 : i32 = 2 + 3 * 4        // 2 + (3 * 4) = 14
    val math2 : i32 = (2 + 3) * 4      // Explicit grouping = 20
    
    // Comparison precedence
    val bool1 : bool = 5 > 3 && 2 < 4  // (5 > 3) && (2 < 4) = true
    val bool2 : bool = 5 > 3 == 2 < 4  // (5 > 3) == (2 < 4) = true
    
    // Mixed precedence with explicit grouping
    val mixed : bool = (x + y) > (a * b) && (c / 2.0) < 10.0
}

func main() : i32 = {
    // The elegance of Hexen's binary operations:
    // - Safe operations work seamlessly
    // - Ambiguous operations require explicit context
    // - Context flows through entire expressions  
    // - Division behavior adapts to target type
    // - One mental model for all operations
    
    return 0
}
```

## Future Extensions

### Operator Overloading

Binary operations are designed to support future operator overloading:

```hexen
// Future: User-defined types with custom operators
struct Vector2 = {
    x : f32,
    y : f32,
}

// Future: Operator overloading
func +(left : Vector2, right : Vector2) : Vector2 = {
    return Vector2{x: left.x + right.x, y: left.y + right.y}
}
```

### Generic Operations

The context-guided system extends naturally to generics:

```hexen
// Future: Generic operations
func add<T>(a : T, b : T) : T = {
    return a + b  // Type T guides the operation
}
```

### Compound Assignment

```hexen
// Future: Compound assignment operators
mut x : i32 = 10
x += 5    // Equivalent to: x = x + 5
x *= 2    // Equivalent to: x = x * 2
```

This binary operations system provides a solid foundation that's both immediately useful and extensible for future language features. 