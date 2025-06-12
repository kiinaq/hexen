# Hexen Binary Operations 🦉

*Design and Implementation Specification*

## Overview

Hexen's binary operations system follows the **"Pedantic to write, but really easy to read"** philosophy with clear, predictable operators that eliminate ambiguity and make computational cost transparent. 

### Key Design Principles

1. **Two Division Operators for Clarity**:
   - **`/`** = Float division (mathematical, always produces float results)
   - **`\`** = Integer division (efficient, integer-only computation)

2. **No Magic Type Coercion**: 
   - Operator choice determines behavior, not context
   - Mixed types require explicit handling
   - Clear, predictable semantics

3. **Transparent Cost Model**:
   - Float result types reveal floating-point computation
   - Integer result types guarantee efficient integer math
   - User always knows what computation is happening

## Core Philosophy

### Context-Guided Resolution Strategy

Binary operations in Hexen follow a unified pattern that prioritizes system programming efficiency:

1. **Default to `i32`**: All numeric operations default to `i32` (system programmer friendly)
2. **Promotion Requires Explicit Type**: Any operation that would promote beyond `i32` requires explicit result type annotation
3. **No Hidden Promotions**: Float division, mixed types, or wider integers all require explicit intent
4. **Context Determines Behavior**: Target type guides the entire expression resolution when provided

This pattern is consistent with Hexen's broader design: **"Explicit Danger, Implicit Safety"** and **"Pedantic to write, but really easy to read"**.

## Operator Precedence

Binary operators follow standard mathematical precedence with explicit grouping for clarity.

### Precedence Levels (Highest to Lowest)

| Level | Operators | Associativity | Description |
|-------|-----------|---------------|-------------|
| 1 | `-`, `!` | Right | Unary minus, logical NOT |
| 2 | `*`, `/`, `\`, `%` | Left | Multiplication, float division, integer division, modulo |
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

// Division operators have same precedence level - but different precision!
val float_precise : i32 = (10 / 3) * 9  // (10 / 3) * 9 = (3.333... * 9) = 30.0 → 30 (preserves precision)
val int_truncated : i32 = (10 \ 3) * 9  // (10 \ 3) * 9 = (3 * 9) = 27 (early truncation)
val mixed : f64 = 20 * (3 / 2)          // 20 * (1.5) = 30.0

// Comparison precedence  
val check1 : bool = 5 > 3 && 2 < 4      // (5 > 3) && (2 < 4) = true
val check2 : bool = 5 > 3 == 2 < 4      // (5 > 3) == (2 < 4) = true

// Explicit grouping for clarity
val complex_float : f64 = (a + b) * (c - d) / (e + f)   // Float division
val complex_int : i32 = (a + b) * (c - d) \ (e + f)     // Integer division
```

## Type Resolution Rules

### 1. Safe Operations (No Context Required)

These operations are unambiguous and resolve automatically:

#### Both Comptime Types
```hexen
// Same comptime_int operations default to i32
val result1 = 42 + 100          // comptime_int + comptime_int = comptime_int → i32
val result2 = 42 * 100          // comptime_int * comptime_int = comptime_int → i32
val result5 = 42 \ 100          // comptime_int \ comptime_int = comptime_int → i32

// Operations that would promote beyond i32 require explicit type
// val result3 = 3.14 + 2.71    // ❌ Error: comptime_float operations require explicit result type
// val result4 = 42 / 100       // ❌ Error: Float division requires explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_float : f64 = 3.14 + 2.71     // comptime_float + comptime_float → f64
val explicit_div : f64 = 42 / 100          // comptime_int / comptime_int → f64 (float division)
```

#### Mixed Comptime Types
Mixed comptime types require explicit result type (would promote beyond i32):
```hexen
// ❌ Mixed comptime types would promote beyond i32 → require explicit type
// val auto_promote1 = 42 + 3.14   // Error: Mixed comptime types require explicit result type
// val auto_promote2 = 42 * 3.14   // Error: Mixed comptime types require explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_f64 : f64 = 42 + 3.14 // comptime_int + comptime_float → f64 (full precision)
val explicit_f32 : f32 = 42 * 3.14 // comptime_int * comptime_float → f32 (reduced precision)
val explicit_i32 : i32 = 42 * 3.14 // comptime_int * comptime_float → i32 (explicit truncation)
```

#### One Comptime, One Concrete
The comptime type adapts to the concrete type:
```hexen
val x : i32 = 10
val y : f64 = 3.14

val result1 = x + 42            // i32 + comptime_int = i32
// val result2 = y + 42         // f64 + comptime_int = f64  -> ❌ Error: Float result requires explicit type annotation
val result2_explicit : f64 = y + 42 // f64 + comptime_int = f64 (explicit type, allowed)
// val result3 = x / 2          // ❌ Error: Float division requires explicit result type
val result4 = x \ 2             // i32 \ comptime_int = i32 (integer division)
```

#### Both Same Concrete Type
```hexen
val a : i32 = 10
val b : i32 = 20
val c : f64 = 3.14
val d : f64 = 2.71

val result1 = a + b             // i32 + i32 = i32
// val result2 = c * d          // ❌ Error: Float result requires explicit type annotation
val result2_explicit : f64 = c * d // f64 * f64 = f64 (explicit type, allowed)
// val result3 = a / b          // ❌ Error: Float division requires explicit result type
val result4 = a \ b             // i32 \ i32 = i32 (integer division)

// ✅ Explicit type for float division
val explicit_div : f64 = a / b  // i32 / i32 → f64 (float division)
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

### 3. Comptime Type Resolution Rules

Comptime types follow the **"i32 default, explicit promotion"** rule for system programming efficiency:

#### Same Comptime Type Operations
```hexen
// comptime_int operations default to i32 (system programmer friendly)
val add_ints = 42 + 100             // comptime_int + comptime_int = comptime_int → i32
val mul_ints = 42 * 100             // comptime_int * comptime_int = comptime_int → i32
val idiv_ints = 42 \ 100            // comptime_int \ comptime_int = comptime_int → i32

// Operations that would promote beyond i32 require explicit type
// val div_ints = 42 / 100          // ❌ Error: Float division requires explicit result type
// val add_floats = 3.14 + 2.71     // ❌ Error: comptime_float operations require explicit result type
// val mul_floats = 3.14 * 2.71     // ❌ Error: comptime_float operations require explicit result type
// val div_floats = 3.14 / 2.71     // ❌ Error: comptime_float operations require explicit result type

// ✅ Explicit type annotations make intent clear
val explicit_div : f64 = 42 / 100   // comptime_int / comptime_int → f64 (float division)
val explicit_add : f64 = 3.14 + 2.71 // comptime_float + comptime_float → f64
val explicit_mul : f32 = 3.14 * 2.71 // comptime_float * comptime_float → f32
val explicit_fdiv : f64 = 3.14 / 2.71 // comptime_float / comptime_float → f64
```

#### Mixed Comptime Types (Require Explicit Type)
```hexen
// Mixed comptime types require explicit result type (would promote beyond i32)
// val auto_promote1 = 42 + 3.14    // ❌ Error: Mixed comptime types require explicit result type
// val auto_promote2 = 42 * 3.14    // ❌ Error: Mixed comptime types require explicit result type
// val auto_promote3 = 42 / 3.14    // ❌ Error: Mixed comptime types require explicit result type
// val auto_promote4 = 42 - 3.14    // ❌ Error: Mixed comptime types require explicit result type

// Complex expressions also require explicit type when they would promote
// val x = 10 + (10 / 2)            // ❌ Error: Contains float division, requires explicit result type
// val y = 42 * 3.14                // ❌ Error: Mixed comptime types require explicit result type
// val z = 100 - 3.14               // ❌ Error: Mixed comptime types require explicit result type

// ❌ Integer division with mixed comptime types is an error
// val invalid = 42 \ 3.14          // Error: Integer division (\) requires integer operands
// val also_bad = 3.14 \ 42         // Error: Integer division (\) requires integer operands

// ✅ Explicit type annotations make intent clear
val explicit_f32 : f32 = 42 + 3.14  // comptime_int + comptime_float → f32
val explicit_f64 : f64 = 42 * 3.14  // comptime_int * comptime_float → f64
val complex_expr : f64 = 10 + (10 / 2) // Explicit type for complex expression with float division

// ✅ Showing the precision difference between division operators
val precise_calc : i32 = (10 / 3) * 9        // Float division: (3.333... * 9) = 30.0 → 30
val truncated_calc : i32 = (10 \ 3) * 9      // Integer division: (3 * 9) = 27 (early truncation)
```

#### Comptime with Concrete Types
```hexen
val concrete_int : i32 = 10
val concrete_float : f64 = 3.14

// Comptime types adapt to concrete types when result stays i32
val adapt1 = concrete_int + 42       // i32 + comptime_int = i32
// val adapt2 = concrete_float * 2   // ❌ Error: f64 result requires explicit result type
// val adapt3 = concrete_int / 2     // ❌ Error: Float division requires explicit result type
val adapt4 = concrete_int \ 2        // i32 \ comptime_int = i32 (integer division)

// ✅ Explicit type for operations that would promote beyond i32
val explicit_f64 : f64 = concrete_float * 2  // f64 + comptime_int → f64

// ✅ Explicit type for float division
val explicit_adapt : f64 = concrete_int / 2  // i32 / comptime_int → f64 (float division)
```

### 4. Concrete Type Mixing Rules

Different concrete numeric types require **explicit handling** - no automatic promotion:

#### Mixed Concrete Types (Require Explicit Context)
```hexen
val int_val : i32 = 10
val long_val : i64 = 20
val float_val : f32 = 3.14

// ❌ Mixed concrete types are not automatically promoted
// val auto_promo = int_val + long_val     // Error: Mixed concrete types need explicit handling
// val mixed_math = int_val + float_val    // Error: Mixed concrete types need explicit handling

// ✅ Explicit target type guides resolution
val as_i64 : i64 = int_val + long_val     // Mixed concrete types → explicit target type
val as_f32 : f32 = int_val + float_val    // Mixed concrete types → explicit target type
val as_f64 : f64 = int_val + long_val     // Mixed concrete types → explicit target type
```

#### Division with Concrete Types
```hexen
val a : i32 = 10
val b : i32 = 3

// Division behavior determined by operator, not operand types
// val float_result = a / b     // ❌ Error: Float division requires explicit result type
val int_result = a \ b          // i32 \ i32 = i32 (integer division)

// ✅ Explicit type for float division
val explicit_float : f64 = a / b // i32 / i32 → f64 (float division)

// Mixed concrete division
val c : i64 = 20
// val mixed_div = a / c        // ❌ Error: Mixed concrete types need explicit handling
val explicit_div : f64 = a / c  // ✅ Mixed concrete types → explicit target type
```

## Division Operations: Float vs Integer

Hexen provides **two distinct division operators** to eliminate ambiguity and make computational cost transparent:

### Float Division (`/`) - Mathematical Division
**Always produces floating-point results**, preserving mathematical precision:

```hexen
// Float division requires explicit result type (would promote beyond i32)
// val precise1 = 10 / 3        // ❌ Error: Float division requires explicit result type
// val precise2 = 7 / 2         // ❌ Error: Float division requires explicit result type
// val float_calc = 10.5 / 2.1  // ❌ Error: comptime_float operations require explicit result type

// ✅ Explicit type annotations make intent clear
val precise1 : f64 = 10 / 3     // comptime_int / comptime_int → f64 (3.333...)
val precise2 : f64 = 7 / 2      // comptime_int / comptime_int → f64 (3.5)
val precise3 : f32 = 22 / 7     // comptime_int / comptime_int → f32 (3.142857...)
val float_calc : f64 = 10.5 / 2.1 // comptime_float / comptime_float → f64 (5.0)

// Mixed concrete types require explicit handling
val int_val : i32 = 10
val float_val : f64 = 3.0
// val mixed = int_val / float_val  // ❌ Error: Mixed concrete types need explicit handling
val explicit_mixed : f64 = int_val / float_val  // ✅ Mixed concrete types → explicit target type
```

### Integer Division (`\`) - Efficient Truncation
**Only works with integer types**, produces integer results with truncation:

```hexen
// Integer division (efficient, no floating-point computation)
val fast1 = 10 \ 3              // comptime_int = 3 (default: i32, truncated)
val fast2 = 7 \ 2               // comptime_int = 3 (default: i32, truncated)  
val fast3 : i64 = 22 \ 7        // i64 = 3 (explicit width)

// Integer division requires integer operands
val a : i32 = 10
val b : i32 = 3
val efficient = a \ b           // i32 = 3 (no type promotion needed)

// ❌ Float operands with integer division is an error
// val invalid = 10.5 \ 2.1     // Error: Integer division requires integer operands
```

### Design Philosophy

#### **Transparent Cost Model**
- **`/` → Float result**: User sees floating-point type, knows FP computation occurred
- **`\` → Integer result**: User sees integer type, knows efficient integer operation

#### **Mathematical Honesty** 
- **`10 / 3`** naturally produces a fraction → `f64` type reveals this
- **`10 \ 3`** explicitly requests truncation → `i32` type shows the loss

#### **No Hidden Magic**
- Division behavior determined by **operator choice**, not context
- No complex coercion rules or context-dependent behavior
- Clear, predictable semantics


### Truncation Rules

Float-to-integer conversion follows standard truncation rules:

```hexen
// Truncation towards zero
val pos_trunc : i32 = 10.9 / 2.0    // 5.45 → 5 
val neg_trunc : i32 = -10.9 / 2.0   // -5.45 → -5

// Exact conversions when possible
val exact : i32 = 20.0 / 4.0        // 5.0 → 5 (exact)
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
multiplicative: unary (("*" | "/" | "\\" | "%") unary)*
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
    // ===== Safe Operations (Clear, Predictable Behavior) =====
    
    // Safe arithmetic operations
    val safe1 = 42 + 100           // comptime_int + comptime_int = comptime_int
    val safe2 = 3.14 * 2.71        // comptime_float * comptime_float = comptime_float
    val safe3 = 10 / 2             // comptime_int / comptime_int = comptime_float (float division: 5.0)
    val safe4 = 10 \ 2             // comptime_int \ comptime_int = comptime_int (integer division: 5)
    
    // One comptime, one concrete
    val x : i32 = 10
    val y : f64 = 3.14
    val safe5 = x + 42             // i32 + comptime_int = i32
    val safe6 = y * 2              // f64 * comptime_int = f64
    
    // ===== Division Operators: Transparent Choice =====
    
    // Float division (mathematical, produces fractions)
    val float_div1 = 7 / 3         // comptime_float = 2.333... (default: f64)
    val float_div2 : f32 = 7 / 3   // f32 = 2.333... (explicit precision)
    val float_div3 = x / 3         // f64 = 3.333... (concrete int promotes to float)
    
    // Integer division (efficient, truncates)
    val int_div1 = 7 \ 3           // comptime_int = 2 (default: i32, truncated)
    val int_div2 : i64 = 7 \ 3     // i64 = 2 (explicit width)
    val int_div3 = x \ 3           // i32 = 3 (pure integer computation)
    
    // ===== Complex Expressions: Operator Choice Matters =====
    
    val precise_calc : i32 = (10 / 3) * 9       // Float: (3.333... * 9) = 30.0 → 30
    val truncated_calc : i32 = (10 \ 3) * 9     // Integer: (3 * 9) = 27
    val mixed_float : f64 = (20 + 10) / 2       // Float division: 15.0
    val mixed_int : i32 = (20 + 10) \ 2         // Integer division: 15
    
    // ===== Mixed Types: Explicit When Needed =====
    
    // Mixed comptime types require explicit context
    val mixed_explicit : f64 = 42 + 3.14      // ✅ Explicit context guides resolution
    val mixed_explicit2 : f32 = 42 * 3.14     // ✅ Explicit context guides resolution
    // val mixed_ambiguous = 42 + 3.14        // ❌ Error: Mixed comptime types need explicit result type
    
    // Mixed concrete types require explicit context (no magic coercion)
    val a : i32 = 10
    val b : i64 = 20
    val c : f32 = 3.14
    
    // val ambiguous = a + b                  // ❌ Error: Mixed concrete types need explicit handling
    val explicit_wide : i64 = a + b           // ✅ Mixed concrete types → explicit target type
    val explicit_narrow : i32 = a + b         // ✅ Mixed concrete types → explicit target type
    
    // Division behavior is always clear from operator choice
    val div_clear1 = a / 3          // i32 / comptime_int = f64 (float division)
    val div_clear2 = a \ 3          // i32 \ comptime_int = i32 (integer division)
    
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