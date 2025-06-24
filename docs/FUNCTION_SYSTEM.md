# Hexen Function System 🦉

*Design and Implementation Specification*

## Overview

Hexen's function system extends the language's core philosophy of **"Explicit Danger, Implicit Safety"** to function declarations, parameters, and calls. Functions integrate seamlessly with the comptime type system, unified block system, and context-guided type resolution, providing a consistent and predictable programming model.

## Core Philosophy

### Design Principle: Parameter Context Anchoring

Functions in Hexen follow the same **context-guided resolution** pattern as other language features:

- **Function parameters provide type context** for comptime type resolution in function calls
- **Parameter types serve as context anchors** that guide argument type adaptation
- **Immutable by default** - parameters are read-only unless explicitly marked `mut`
- **Consistent with variable system** - same `val`/`mut` semantics apply to parameters

This pattern ensures that function calls provide clear, predictable type resolution while maintaining Hexen's safety guarantees.

## Function Declaration Syntax

### Basic Function Declaration

```hexen
// Basic function with parameters
func calculate(base: i32, multiplier: i32) : i32 = {
    return base * multiplier
}

// Void function with side effects
func log_message(message: string, level: string) : void = {
    // Simple void function - performs side effects, returns nothing
    return
}

// Function with mixed parameter types
func convert_and_scale(value: i64, scale: f64) : f64 = {
    // Mixed concrete types require explicit target type (return type provides context)
    val result : f64 = value * scale  // ✅ Explicit context for i64 * f64 → f64
    return result
}
```

### Parameter Declaration Rules

1. **Syntax**: `parameter_name : parameter_type`
2. **Immutability**: Parameters are immutable by default (like `val` variables)
3. **Type Annotation**: Parameter types must be explicitly declared (no type inference for parameters)
4. **Multiple Parameters**: Comma-separated, no trailing comma allowed
5. **Naming**: Parameter names follow same rules as variable names

```hexen
// ✅ Valid parameter declarations
func process_data(input: string, format: string, debug: bool) : string = { ... }
func compute(x: f64, y: f64, z: f64) : f64 = { ... }
func setup(config_path: string) : void = { ... }

// ❌ Invalid parameter declarations
// func bad1(input) : void = { ... }                    // Error: Missing parameter type
// func bad2(input: string,) : void = { ... }           // Error: Trailing comma not allowed
// func bad3(123invalid: i32) : void = { ... }          // Error: Invalid parameter name
```

## Parameter Mutability System

### Immutable Parameters (Default)

By default, function parameters are **immutable** - they cannot be reassigned within the function body:

```hexen
func process_value(input: i32) : i32 = {
    val doubled = input * 2     // ✅ OK: Reading parameter value
    // input = 42               // ❌ Error: Cannot reassign immutable parameter 'input'
    return doubled
}

func format_message(message: string, prefix: string) : string = {
    val formatted = prefix + ": " + message  // ✅ OK: Reading parameter values
    // message = "modified"     // ❌ Error: Cannot reassign immutable parameter 'message'
    return formatted
}
```

### Mutable Parameters (`mut`)

Functions can declare parameters as mutable using the `mut` keyword:

```hexen
func increment_and_return(mut counter: i32) : i32 = {
    counter = counter + 1       // ✅ OK: Mutable parameter can be reassigned
    return counter
}

func normalize_string(mut text: string) : string = {
    text = trim_whitespace(text)          // ✅ OK: Mutable parameter reassignment
    text = to_lowercase(text)             // ✅ OK: Subsequent reassignment
    return text
}

// Mutable parameters with type constraints (same rules as mut variables)
func process_with_precision_loss(mut result: f32, high_precision: f64) : f32 = {
    // result = high_precision              // ❌ Error: f64 → f32 requires explicit acknowledgment
    result = high_precision : f32           // ✅ OK: Explicit precision loss acknowledgment
    return result
}
```

### Parameter vs Local Variable Distinction

Parameters and local variables follow the same mutability semantics but serve different roles:

```hexen
func demonstrate_scoping(input: i32, mut output: i32) : i32 = {
    // Parameters are in function scope
    val local_immutable = input * 2         // ✅ OK: val variable from immutable parameter
    mut local_mutable : i32 = output        // ✅ OK: mut variable with explicit type required
    
    // local_immutable = 42                 // ❌ Error: Cannot reassign val variable
    local_mutable = 42                      // ✅ OK: Can reassign mut variable
    output = local_mutable                  // ✅ OK: Can reassign mut parameter
    
    return output
}
```

## Type System Integration

### Comptime Type Context Propagation

Function parameters provide **type context** for comptime type resolution in function calls:

```hexen
func calculate_area(width: f64, height: f64) : f64 = {
    return width * height
}

func process_count(items: i32, multiplier: i32) : i32 = {
    return items * multiplier
}

// Function calls provide parameter type context for comptime literals
val area = calculate_area(10.5, 20.3)      // f64 + f64 parameters (comptime literals adapt)
val area2 = calculate_area(42, 30)         // comptime_int → f64 (adapts to parameter types)
val count = process_count(100, 5)          // comptime_int → i32 (adapts to parameter types)
```

### Mixed Parameter Types

When functions have parameters of different types, each argument adapts to its corresponding parameter type:

```hexen
func mixed_calculation(base: i32, multiplier: f64, precision: f32) : f64 = {
    val scaled : f64 = base * multiplier      // ✅ Explicit context for i32 * f64 → f64
    return scaled * precision                 // ✅ Function return type f64 provides context for f64 * f32
    
    // ❌ ERROR: Type annotation must match function's declared return type (when used)
    // return scaled * precision : f32        // Error: Type annotation must match function return type (f64)
}

// Example with precision loss - type annotation required
func mixed_calculation_f32(base: i32, multiplier: f64, precision: f32) : f32 = {
    val scaled : f64 = base * multiplier      // ✅ Explicit context for i32 * f64 → f64
    // return scaled * precision              // ❌ Error: f64 * f32 → f64, but function returns f32 (precision loss)
    return scaled * precision : f32           // ✅ Explicit acknowledgment of precision loss f64 → f32
}

// Each argument adapts to its parameter type independently
val result = mixed_calculation(42, 3.14, 1.5)
// Breakdown:
// - 42 (comptime_int) → i32 (adapts to base parameter)
// - 3.14 (comptime_float) → f64 (adapts to multiplier parameter)  
// - 1.5 (comptime_float) → f32 (adapts to precision parameter)
// - Function return type f64 means result is f64
```

### Parameter Type Coercion Rules

Parameters follow the same type coercion rules as variable declarations:

```hexen
func process_numbers(small: i32, large: i64, precise: f64) : void = {
    // Parameters provide context for function calls
}

// ✅ Safe comptime type adaptations
process_numbers(42, 100, 3.14)         // All comptime literals adapt to parameter types

// ✅ Safe widening coercions
val small_val : i32 = 10
val medium_val : i32 = 20  
val large_val : i64 = 30
process_numbers(small_val, medium_val, large_val)  // i32 → i64, i64 → f64 (safe widenings)

// ❌ Unsafe narrowing requires explicit acknowledgment
val very_large : i64 = 9223372036854775807
// process_numbers(very_large, large_val, precise_val)  // Error: i64 → i32 requires ': i32'
process_numbers(very_large : i32, large_val, precise_val)  // ✅ Explicit truncation
```

## Function Calls and Context Resolution

### Argument-to-Parameter Mapping

Function calls map arguments to parameters positionally, with each argument evaluated in the context of its corresponding parameter type:

```hexen
func transform_data(
    input: string, 
    scale_factor: f32, 
    iterations: i32,
    debug_mode: bool
) : string = {
    // Function implementation
    return processed_result
}

// Positional argument mapping with type context
val result = transform_data(
    "hello world",      // string → input parameter (exact match)
    2.5,                // comptime_float → f32 parameter (adapts)
    10,                 // comptime_int → i32 parameter (adapts)
    true                // bool → debug_mode parameter (exact match)
)
```

### Complex Expression Arguments

Arguments can be complex expressions that benefit from parameter type context:

```hexen
func compute_result(base: f64, factor: f64) : f64 = {
    return base * factor
}

val x : i32 = 10
val y : i32 = 20

// Complex expressions adapt to parameter context
val result = compute_result(
    x + y,              // i32 + i32 → i32, then i32 → f64 (adapts to base parameter)
    3.14 * 2.0          // comptime_float * comptime_float → comptime_float → f64 (adapts to factor parameter)
)

// Mixed-type expressions in arguments benefit from parameter context
val a : i32 = 5
val b : f64 = 2.5
val result = compute_result(a + b, 1.0)             // ✅ Parameter type f64 provides context for i32 + f64
```

### Function Call Type Resolution Strategy

Function calls follow a **parameter-guided resolution approach**:

1. **Parameter Types as Context**: Each parameter type provides context for its corresponding argument
2. **Independent Resolution**: Each argument is resolved independently based on its parameter
3. **Expression Context**: Complex argument expressions use parameter type as target context
4. **Error Localization**: Type errors are reported per argument-parameter pair

### Type Annotations in Function Context

Type annotations in function calls follow the same rules as TYPE_SYSTEM.md:

```hexen
func process(value: f64) : f64 = { return value * 2.0 }

val int_val : i32 = 10
val large_val : i64 = 1000

// ✅ CORRECT: Type annotation matches target context when precision loss occurs
val result1 : f64 = process(large_val)          // i64 → f64 (safe widening, no annotation needed)

// ❌ ERROR: Direct precision loss without acknowledgment  
// val result2 : f32 = process(large_val)       // Error: f64 result → f32 requires ': f32'

// ✅ CORRECT: Explicit acknowledgment of precision loss
val result2 : f32 = process(large_val) : f32    // f64 → f32 (explicit precision loss acknowledgment)

// ✅ CORRECT: Parameter provides context for mixed expressions
val mixed_arg : f64 = int_val + 3.14            // Explicit context for i32 + comptime_float
val result3 = process(mixed_arg)                // f64 → f64 (exact match)
```

**Key Rule**: Type annotations are for **acknowledgment of precision loss**, not for **type conversion guidance**.

```hexen
func process(int_param: i32, float_param: f64, string_param: string) : void = { ... }

// Each argument resolved independently
process(
    42,                 // comptime_int → i32 (parameter context)
    3.14,               // comptime_float → f64 (parameter context)  
    "hello"             // string → string (exact match)
)

// Error localization per parameter
val mixed_val : f64 = 2.5
// process(mixed_val, 42, "test")       // ❌ Error: Argument 1: f64 cannot narrow to i32 without ': i32'
process(mixed_val : i32, 42, "test")   // ✅ Explicit narrowing for argument 1
```

## Integration with Unified Block System

### Function Bodies as Unified Blocks

Function bodies use the same unified block system as other Hexen constructs, with the function's return type providing context:

```hexen
func complex_computation(input: i32, threshold: f64) : f64 = {
    // Statement block for setup (scoped)
    {
        val config = load_configuration()
        validate_input(input, config)
    }
    
    // Expression block for intermediate calculation
    val intermediate = {
        val scaled = input * 2
        val adjusted = scaled + 10
        return adjusted       // Expression block requires return
    }
    
    // Function return (guided by f64 return type)
    if intermediate > threshold {
        return intermediate * 1.5    // comptime_float → f64 (return type context)
    } else {
        return threshold / 2.0       // f64 / comptime_float → f64 (float division defaults to f64)
    }
}
```

### Parameter Scope and Block Interaction

Parameters are accessible throughout the function body and all nested blocks:

```hexen
func nested_scope_demo(base: i32, multiplier: f64) : f64 = {
    val outer_scope = base * 2      // ✅ Parameters accessible in function scope
    
    {
        // Statement block - parameters still accessible
        val inner_calc = base + 10  // ✅ Parameter accessible in nested block
        val converted = multiplier * 3.14  // ✅ Parameter accessible in nested block
        log_debug("Inner calculation complete")
    }
    
    val final_result = {
        // Expression block - parameters accessible
        val result = base * multiplier  // ✅ Parameters accessible in expression block
        return result                   // Expression block return
    }
    
    return final_result    // Function return
}
```

## Error Handling and Messages

### Parameter-Related Error Messages

Hexen provides clear, actionable error messages for function parameter issues:

#### Parameter Declaration Errors
```hexen
// Missing parameter type
// func bad_func(input) : void = { ... }
// Error: Parameter 'input' missing type annotation
// Add explicit type: 'input: type'

// Invalid parameter name  
// func bad_func(123invalid: i32) : void = { ... }
// Error: Invalid parameter name '123invalid'
// Parameter names must start with a letter or underscore

// Trailing comma
// func bad_func(input: string,) : void = { ... }  
// Error: Trailing comma not allowed in parameter list
```

#### Parameter Assignment Errors
```hexen
func process(input: i32) : i32 = {
    // input = 42
    // Error: Cannot reassign immutable parameter 'input'
    // Parameters are immutable by default. Use 'mut input: i32' for mutable parameters
}
```

#### Function Call Argument Errors
```hexen
func calculate(base: i32, factor: f64) : f64 = { ... }

val large_val : i64 = 9223372036854775807
// calculate(large_val, 3.14)
// Error: Argument 1: Potential truncation from i64 to i32 parameter 'base'
// Add explicit truncation: 'calculate(large_val : i32, 3.14)'

val int_val : i32 = 10
val float_val : f64 = 2.5
// calculate(int_val + float_val, 3.14)
// Error: Argument 1: Mixed-type expression 'i32 + f64' requires explicit result type
// Add explicit context: 'val temp : f64 = int_val + float_val; calculate(temp, 3.14)'
// Or use explicit variable: 'calculate((int_val + float_val : f64), 3.14)' with matching result type
```

#### Mutable Parameter Type Errors
```hexen
func modify_value(mut result: f32, input: f64) : f32 = {
    // result = input
    // Error: Assignment to mutable parameter 'result': f64 cannot assign to f32 without ': f32'
    // Add explicit precision loss acknowledgment: 'result = input : f32'
}
```

## Advanced Usage Patterns

### Multi-Parameter Context Resolution

```hexen
func complex_transform(
    base: i64,
    scale: f32, 
    offset: f64,
    iterations: i32
) : f64 = {
    mut accumulator : f64 = base      // ✅ Explicit type required for mut (i64 → f64 widening)
    
    {
        mut i : i32 = 0               // ✅ Explicit type required for mut
        while i < iterations {
            // accumulator * scale produces f64, + offset produces f64 (no annotation needed)
            accumulator = accumulator * scale + offset
            i = i + 1
        }
    }
    
    return accumulator
}

// Complex call with mixed literal types
val result = complex_transform(
    1000,           // comptime_int → i64 (adapts to base parameter)
    2.5,            // comptime_float → f32 (adapts to scale parameter)
    10.0,           // comptime_float → f64 (adapts to offset parameter)
    5               // comptime_int → i32 (adapts to iterations parameter)
)
```

### Function Composition with Type Context

```hexen
func scale_value(value: f64, factor: f64) : f64 = {
    return value * factor
}

func truncate_to_int(value: f64) : i32 = {
    return value : i32      // Explicit truncation
}

func process_chain(input: i32) : i32 = {
    // Function composition with context propagation
    val scaled = scale_value(input, 2.5)        // i32 → f64 (parameter context)
    val final = truncate_to_int(scaled)         // f64 → i32 (explicit truncation)
    return final
}
```

### Division Operations in Function Context

```hexen
// Float division (/) - always produces float results
func calculate_average(total: i32, count: i32) : f64 = {
    return total / count    // comptime_int / comptime_int → comptime_float → f64 (return type context)
}

// Integer division (\) - efficient truncation, integer-only
func calculate_quotient(dividend: i32, divisor: i32) : i32 = {
    return dividend \ divisor    // i32 \ i32 → i32 (integer division)
}

// Mixed division operations
func complex_calculation(base: i64, factor: f32) : f64 = {
    val precise_result : f64 = base / factor    // ✅ Mixed concrete types: i64 / f32 → f64 (explicit context)
    // val truncated = base \ factor            // ❌ Error: Integer division requires integer operands
    return precise_result
}
```

### Comparison Operations in Function Context

```hexen
// Comparison operations with function parameters (strict type matching)
func compare_values(a: i32, b: i32) : bool = {
    return a > b                // ✅ i32 > i32 (same concrete types)
}

func validate_range(value: f64, min: f64, max: f64) : bool = {
    return value >= min && value <= max    // ✅ f64 comparisons with logical operators
}

// Mixed-type comparisons require explicit type conversion
func mixed_comparison(int_val: i32, float_val: f64) : bool = {
    // return int_val < float_val            // ❌ Error: Cannot compare i32 and f64
    val int_as_float : f64 = int_val        // ✅ Explicit conversion before comparison
    return int_as_float < float_val         // ✅ f64 < f64 (same types after conversion)
}

// Function parameters in complex boolean expressions
func is_valid_user(age: i32, has_license: bool, credit_score: i32) : bool = {
    return age >= 18 && has_license && credit_score > 650
    // Each comparison: i32 >= i32, bool (direct use), i32 > i32
}
```

### Mutable Parameter Patterns

```hexen
// In-place modification pattern
func normalize_vector(mut x: f64, mut y: f64, mut z: f64) : void = {
    val length = sqrt(x * x + y * y + z * z)
    if length > 0.0 {
        x = x / length
        y = y / length  
        z = z / length
    }
}

// Accumulator pattern
func sum_with_transform(
    values: array<i32>, 
    mut accumulator: f64,
    transform_factor: f64
) : f64 = {
    {
        mut i = 0
        while i < length(values) {
            accumulator = accumulator + (values[i] * transform_factor)
            i = i + 1
        }
    }
    return accumulator
}
```

## Implementation Guidelines

### Function Declaration Analysis

The semantic analyzer should extend the unified declaration framework to handle function parameters:

```python
def _analyze_function_declaration(self, name: str, parameters: List[Dict], 
                                return_type: str, body: Dict, node: Dict) -> None:
    """Analyze function declaration with parameter type checking."""
    
    # Create function scope and add parameters
    self.symbol_table.enter_scope()
    
    # Process each parameter
    param_types = []
    for param in parameters:
        param_name = param["name"]
        param_type = self._parse_type(param["type"])
        is_mutable = param.get("mutable", False)
        
        # Add parameter to symbol table
        self.symbol_table.declare_symbol(param_name, param_type, is_mutable)
        param_types.append(param_type)
    
    # Set function context for return type validation
    func_return_type = self._parse_type(return_type)
    self.current_function_return_type = func_return_type
    
    # Analyze function body with unified block system
    self._analyze_block(body, node, context="function")
    
    # Clean up function context
    self.current_function_return_type = None
    self.symbol_table.exit_scope()
    
    # Register function in symbol table
    func_type = HexenFunctionType(param_types, func_return_type)
    self.symbol_table.declare_symbol(name, func_type, False)
```

### Function Call Analysis

```python
def _analyze_function_call(self, name: str, arguments: List[Dict], node: Dict) -> HexenType:
    """Analyze function call with parameter context propagation."""
    
    # Look up function type
    func_symbol = self.symbol_table.lookup_symbol(name)
    if not isinstance(func_symbol.type, HexenFunctionType):
        self._error(f"'{name}' is not a function", node)
        return HexenType.UNKNOWN
    
    func_type = func_symbol.type
    
    # Check argument count
    if len(arguments) != len(func_type.parameters):
        self._error(f"Function '{name}' expects {len(func_type.parameters)} arguments, got {len(arguments)}", node)
        return HexenType.UNKNOWN
    
    # Analyze each argument with parameter type context
    for i, (arg_node, param_type) in enumerate(zip(arguments, func_type.parameters)):
        arg_type = self._analyze_expression(arg_node, target_type=param_type)
        
        # Check type compatibility
        if not self._can_coerce_type(arg_type, param_type):
            self._error(f"Argument {i+1}: Cannot convert {arg_type} to parameter type {param_type}", node)
    
    return func_type.return_type
```

### Parameter Mutability Tracking

```python
def _analyze_parameter_assignment(self, name: str, value: Dict, node: Dict) -> None:
    """Analyze assignment to function parameter."""
    
    param_symbol = self.symbol_table.lookup_symbol(name)
    if param_symbol is None:
        self._error(f"Undefined parameter: '{name}'", node)
        return
    
    # Check if parameter is mutable
    if not param_symbol.is_mutable:
        self._error(f"Cannot reassign immutable parameter '{name}'\n"
                   f"Parameters are immutable by default. Use 'mut {name}: {param_symbol.type}' for mutable parameters", node)
        return
    
    # Analyze assignment with parameter type context
    value_type = self._analyze_expression(value, target_type=param_symbol.type)
    
    # Apply same rules as mutable variable assignment
    self._validate_mutable_assignment(param_symbol.type, value_type, node)
```

## Grammar Extensions

### Lark Grammar for Function Parameters

```lark
// Enhanced function declaration rule
function: "func" IDENTIFIER "(" parameter_list? ")" ":" type "=" block

// Parameter list grammar
parameter_list: parameter ("," parameter)*
parameter: ("mut")? IDENTIFIER ":" type

// Updated parameter extraction
parameter_name: IDENTIFIER
parameter_type: type
parameter_mutability: "mut"?
```

### AST Node Structure

Function declarations create AST nodes with this structure:

```python
{
    "type": "function",
    "name": "function_name",
    "parameters": [
        {
            "name": "param1",
            "type": "i32", 
            "mutable": False
        },
        {
            "name": "param2",
            "type": "f64",
            "mutable": True
        }
    ],
    "return_type": "f64",
    "body": {...}  # Block AST node
}
```

Function calls create AST nodes with this structure:

```python
{
    "type": "function_call",
    "name": "function_name",
    "arguments": [
        {...},  # Expression AST nodes
        {...}
    ]
}
```

## Benefits and Trade-offs

### Benefits

1. **Type Safety**: Compile-time parameter type checking prevents runtime errors
2. **Context Clarity**: Parameter types provide clear context for function calls
3. **Consistent Semantics**: Same mutability model as variables
4. **Composability**: Functions integrate seamlessly with other language features
5. **Performance**: No runtime type checking overhead

### Trade-offs  

1. **Verbosity**: Requires explicit parameter type annotations
2. **Learning Curve**: Must understand parameter context propagation
3. **Flexibility vs Safety**: More restrictive than dynamically typed languages

### Comparison with Other Languages

| Feature | Hexen | Rust | C++ | Python |
|---------|-------|------|-----|--------|
| **Parameter Types** | Explicit, required | Explicit, required | Explicit, required | Optional hints |
| **Mutability** | `mut` keyword | `mut` keyword | Manual references | No built-in concept |
| **Type Context** | Parameters provide context | Limited inference | Manual casting | Dynamic typing |
| **Safety** | Compile-time checks | Memory safe | Manual management | Runtime checking |

## Future Extensions

### Default Parameters (Phase II)

```hexen
// Future: Default parameter values
func setup_connection(host: string = "localhost", port: i32 = 8080) : bool = {
    return connect(host, port)
}

// Calls with defaults
val success1 = setup_connection()                    // Uses both defaults
val success2 = setup_connection("production.com")   // Uses port default
val success3 = setup_connection("staging.com", 9090) // No defaults
```

### Generic Functions (Phase III)

```hexen
// Future: Generic function parameters  
func transform<T>(input: T, processor: func(T) : T) : T = {
    return processor(input)
}
```

### Function Overloading (Future)

```hexen
// Future: Function overloading based on parameter types
func process(input: i32) : i32 = { ... }
func process(input: f64) : f64 = { ... }
func process(input: string) : string = { ... }
```

## Conclusion

The Function System extends Hexen's core philosophy to function declarations and calls, providing type-safe parameter handling with context-guided resolution. By integrating seamlessly with the comptime type system and unified block system, functions maintain the language's consistency while enabling powerful composition patterns.

The parameter system's emphasis on explicit type annotations and immutability by default reinforces Hexen's safety-first approach, while the context propagation mechanism ensures that function calls provide natural, predictable type resolution for arguments.

This foundation is extensible and ready to support advanced features like default parameters, generics, and function overloading in future language phases.

---

## **🚨 DOCUMENTATION REVIEW NOTES - ISSUES TO FIX**

*The following inconsistencies were identified during comprehensive review against core Hexen documentation (TYPE_SYSTEM.md, BINARY_OPS.md, COMPARISON_OPS.md, UNIFIED_BLOCK_SYSTEM.md). These need to be addressed in a future revision:*

### **1. CRITICAL: Undefined Functions Used in Examples**

**Lines 309-311:**
```hexen
val config = load_configuration()      // ❌ ISSUE: Undefined function
validate_input(input, config)         // ❌ ISSUE: Undefined function
```
**Fix needed**: Replace with simple, self-contained examples using only documented Hexen features.

**Line 347:**
```hexen
log_debug("Inner calculation complete") // ❌ ISSUE: Undefined function
```
**Fix needed**: Remove or replace with documented operations.

**Lines 524-526:**
```hexen
val length = sqrt(x * x + y * y + z * z)  // ❌ ISSUE: Undefined function sqrt()
```
**Fix needed**: Replace with simple arithmetic that doesn't require undefined math functions.

**Lines 538-544:**
```hexen
while i < length(values) {             // ❌ ISSUE: 'while' loops not defined in UNIFIED_BLOCK_SYSTEM.md
    accumulator = accumulator + (values[i] * transform_factor)  // ❌ ISSUE: length() undefined
    i = i + 1
}
```
**Fix needed**: Replace `while` loops with documented control structures or simple sequential operations.

**Line 233:**
```hexen
return processed_result                // ❌ ISSUE: Undefined variable
```
**Fix needed**: Replace with actual computation or simple return value.

### **2. CRITICAL: Mixed Concrete Types Without Proper Context**

**Lines 405-407:**
```hexen
// accumulator * scale produces f64, + offset produces f64 (no annotation needed)
accumulator = accumulator * scale + offset  // ❌ ISSUE: f64 * f32 is mixed concrete types
```
**Problem**: According to BINARY_OPS.md, mixed concrete types (`f64 * f32`) require explicit context.
**Fix needed**: Either add explicit type annotation or restructure to avoid mixed concrete types.

### **3. Type Annotation Inconsistencies**

**Line 284:**
```hexen
val mixed_arg : f64 = int_val + 3.14   // ❌ ISSUE: Unnecessary type annotation
```
**Problem**: `i32 + comptime_float → f64` is safe widening, no precision loss.
**Fix needed**: Remove `: f64` as it's optional (no precision loss).

### **4. Missing Required Type Annotations**

**Line 538:**
```hexen
mut i = 0                              // ❌ ISSUE: Missing explicit type for mut variable
```
**Problem**: Violates TYPE_SYSTEM.md rule that all `mut` variables require explicit type.
**Fix needed**: Change to `mut i : i32 = 0`.

### **5. Undefined Syntax and Types**

**Lines 533-534:**
```hexen
values: array<i32>,                    // ❌ ISSUE: array<T> syntax not defined in specs
```
**Problem**: Array types and syntax not documented in core specifications.
**Fix needed**: Either define array syntax in specs or remove from examples.

**Lines 718-725 (Future section):**
```hexen
func setup_connection(host: string = "localhost", port: i32 = 8080) : bool = {
    return connect(host, port)         // ❌ ISSUE: Undefined function connect()
}
```
**Problem**: Uses undefined function and default parameter syntax not defined.
**Fix needed**: Mark clearly as future syntax or use placeholder implementations.

### **6. Comment Accuracy Issues**

**Line 347:**
```hexen
val converted = multiplier * 3.14      // Comment should explain f64 * comptime_float resolution
```
**Fix needed**: Clarify that `multiplier` (f64) * `3.14` (comptime_float) → f64.

### **Review Summary**
- **8 undefined functions** used in examples
- **2 mixed concrete type operations** without proper context handling  
- **1 unnecessary type annotation** case
- **1 missing explicit type** for `mut` variable
- **3 undefined syntax** cases (`array<T>`, `while` loops, default parameters)
- **Multiple undefined variables** and inconsistent comments

### **Recommended Fix Strategy**
1. **Phase 1**: Remove all undefined functions and replace with self-contained examples
2. **Phase 2**: Fix all type annotation issues to align with TYPE_SYSTEM.md rules
3. **Phase 3**: Fix mixed concrete type operations to follow BINARY_OPS.md rules
4. **Phase 4**: Ensure all `mut` variables have explicit types per TYPE_SYSTEM.md
5. **Phase 5**: Remove or clearly mark all undefined syntax as future features
6. **Phase 6**: Verify all examples compile against the documented language specification

*This review ensures FUNCTION_SYSTEM.md is fully consistent with Hexen's core documentation and follows the "Explicit Danger, Implicit Safety" philosophy throughout.* 