# Hexen Unified Block System 🦉

*Design and Implementation Specification*

## Overview

Hexen's **Unified Block System** represents one of the language's most elegant design decisions: using a single `{ }` block syntax for all contexts while providing context-appropriate behavior. This creates a consistent, learnable mental model where blocks behave predictably based on their usage context.

## Core Philosophy

### Design Principle: "One Syntax, Context-Driven Behavior"

All Hexen constructs use the same block syntax `{ statements }`, but context determines their specific behavior:

- **Expression blocks**: Produce values, require final return statement
- **Statement blocks**: Execute code, allow function returns, no value production
- **Function bodies**: Unified with all other blocks, context provides return type validation
- **Scope isolation**: ALL blocks manage their own scope regardless of context

This unification eliminates cognitive overhead while maintaining precise semantic control through context.

### Philosophy Alignment

The unified block system embodies Hexen's core principles:
- **"Clean: There is only one way to do a thing"** - Single block syntax for all contexts
- **"Logic: No tricks to remember, only natural approaches"** - Context determines behavior naturally
- **"Pedantic to write, but really easy to read"** - Explicit context makes intent clear

## Block Types and Contexts

### 1. Expression Blocks

**Purpose**: Compute and return a value  
**Context**: Used in expressions where a value is expected  
**Scope**: Isolated (variables don't leak)  
**Return Requirements**: Must end with `return` statement

```hexen
// Expression block in variable assignment
val result = {
    val temp = 42
    val computed = temp * 2
    return computed        // Required: must return a value
}

// Expression block in function return
func calculate() : i32 = {
    return {
        val intermediate = 10 + 20
        return intermediate * 2    // Nested expression block
    }
}

// Expression block in complex expressions
val complex = ({
    val base = 100
    return base / 2
} + {
    val other = 50
    return other * 3
}) / 4
```

**Key Characteristics:**
- **Value Production**: Always produces a value via return statement
- **Final Return Required**: Last statement must be `return expression`
- **Type Inference**: Block type determined by return expression type
- **Scope Isolation**: Inner variables not accessible outside block

### 2. Statement Blocks

**Purpose**: Execute code without producing a value  
**Context**: Used as standalone statements  
**Scope**: Isolated (variables don't leak)  
**Return Requirements**: No return required, function returns allowed

```hexen
// Statement block for scoped execution
{
    val temp_config = "setup"
    val processed_data = process(temp_config)
    save_to_cache(processed_data)
    // No return statement needed
}

// Statement block within function
func setup_environment() : void = {
    // Outer function scope
    val global_config = "production"
    
    {
        // Inner statement block scope
        val local_temp = "temp_data"
        val processed = transform(local_temp)
        // local_temp not accessible outside this block
    }
    
    // Function returns are allowed in statement blocks
    if early_exit_condition {
        return    // Exits the function, not just the block
    }
    
    finalize_setup(global_config)
}
```

**Key Characteristics:**
- **No Value Production**: Block doesn't produce a value
- **Optional Returns**: Can contain function returns (exits containing function)
- **Scope Isolation**: Variables are scoped to the block
- **Execution Focus**: Designed for side effects and code organization

### 3. Function Body Blocks

**Purpose**: Function implementation with return type validation  
**Context**: Function body (unified with other block types)  
**Scope**: Function scope (managed like all other blocks)  
**Return Requirements**: Context-dependent based on return type

```hexen
// Void function - no return value required
func setup() : void = {
    val config = initialize()
    apply_settings(config)
    return    // Bare return allowed
}

// Value-returning function - return type validation
func compute() : i32 = {
    val base = 100
    val multiplier = 2
    return base * multiplier    // Must return i32-compatible value
}

// Complex function with nested blocks
func process_data() : string = {
    val input = load_data()
    
    // Statement block for preprocessing
    {
        val temp = validate(input)
        normalize(temp)
    }
    
    // Expression block for computation
    val result = {
        val processed = transform(input)
        return format(processed)
    }
    
    return result    // Function return
}
```

**Key Characteristics:**
- **Unified Behavior**: Same as other blocks, with function context
- **Return Type Validation**: Returns must match function signature
- **Scope Management**: Managed identically to other block types
- **Context Integration**: Function context provides return type information

## Scope Management

### Universal Scope Rules

ALL blocks in Hexen follow identical scope management rules:

1. **Scope Creation**: Every block creates a new scope upon entry
2. **Scope Isolation**: Variables declared in block are not accessible outside
3. **Lexical Scoping**: Inner blocks can access outer scope variables
4. **Scope Cleanup**: Scope is destroyed when block exits
5. **Shadowing Allowed**: Inner blocks can shadow outer variables

```hexen
val outer = "global"

func demonstrate_scoping() : void = {
    val function_scope = "function"
    
    {
        // Statement block scope
        val block_scope = "block"
        val outer = "shadowed"    // Shadows outer 'outer'
        
        // Can access: block_scope, outer (shadowed), function_scope
        println(outer)            // "shadowed"
        println(function_scope)   // "function"
    }
    
    // Can access: function_scope, outer (original)
    // Cannot access: block_scope (out of scope)
    println(outer)              // "global"
}
```

### Scope Stack Implementation

The semantic analyzer maintains a scope stack for all block types:

```python
# Scope management (from semantic.py)
def _analyze_block(self, body: Dict, node: Dict, context: str = None):
    # ALL blocks manage their own scope (unified)
    self.symbol_table.enter_scope()
    
    # Context-specific behavior while maintaining unified scope management
    # ... analyze statements ...
    
    # ALL blocks clean up their own scope (unified)
    self.symbol_table.exit_scope()
```

**Key Benefits:**
- **Consistent Mental Model**: Same scoping rules everywhere
- **Predictable Behavior**: No special cases to remember
- **Clean Implementation**: Single code path for all block types

## Context Determination

### Context Flow

Context information flows through the analysis pipeline to determine block behavior:

```python
# Context determination examples
self._analyze_block(body, node)                      # Function body (default context)
self._analyze_block(node, node, context="expression")  # Expression block
self._analyze_block(node, node, context="statement")   # Statement block
```

### Context-Specific Behaviors

| Context | Scope Management | Return Requirements | Value Production | Function Returns |
|---------|------------------|---------------------|------------------|------------------|
| **Expression** | ✅ Isolated | ✅ Required (final) | ✅ Yes | ❌ Not allowed |
| **Statement** | ✅ Isolated | ❌ Optional | ❌ No | ✅ Allowed |
| **Function** | ✅ Isolated | 🔄 Type-dependent | 🔄 Type-dependent | ✅ Expected |

### Return Statement Validation

Return statements are validated based on context:

```hexen
// Expression block context
val value = {
    val temp = 42
    return temp    // ✅ Required and valid
}

// Statement block context  
{
    val temp = 42
    if condition {
        return    // ✅ Function return (exits containing function)
    }
    // No return required
}

// Function context (void)
func work() : void = {
    val setup = initialize()
    return    // ✅ Bare return in void function
}

// Function context (value-returning)
func calculate() : i32 = {
    val result = 42
    return result    // ✅ Must return i32-compatible value
}
```

## Implementation Architecture

### Unified Declaration Framework

The block system integrates with Hexen's unified declaration framework:

```python
def _analyze_declaration(self, node: Dict) -> None:
    """Unified analysis for all declaration types"""
    # Extract components (works for functions, val, mut)
    name, type_annotation, value = self._extract_declaration_components(node)
    
    # Type-specific handling
    if decl_type == "function":
        self._analyze_function_declaration(name, type_annotation, value, node)
        # value is the function body block - analyzed like any other block
```

### Block Analysis Pipeline

```python
def _analyze_block(self, body: Dict, node: Dict, context: str = None) -> Optional[HexenType]:
    """Smart unified block analysis"""
    
    # 1. Universal scope management
    self.symbol_table.enter_scope()
    
    # 2. Context determination
    is_expression_block = context == "expression"
    is_statement_block = context == "statement"
    is_void_function = self.current_function_return_type == HexenType.VOID
    
    # 3. Statement analysis with context-specific return validation
    for stmt in statements:
        self._analyze_statement(stmt)
    
    # 4. Context-specific validation
    if is_expression_block and not last_return_stmt:
        self._error("Expression block must end with a return statement", node)
    
    # 5. Universal scope cleanup
    self.symbol_table.exit_scope()
    
    # 6. Context-dependent return value
    return block_return_type if is_expression_block else None
```

### Context Tracking

```python
# Context stack for nested blocks
self.block_context: List[str] = []  # Track: "expression", "statement", etc.

# Expression context tracking
if is_expression_block:
    self.block_context.append("expression")
    # ... analysis ...
    self.block_context.pop()
```

## Advanced Usage Patterns

### Nested Block Compositions

```hexen
func complex_computation() : f64 = {
    val base_value = {
        // Expression block for base computation
        val raw = load_data()
        val processed = validate(raw)
        return processed * 2.5
    }
    
    // Statement block for side effects
    {
        val log_entry = format("Processing: {}", base_value)
        write_log(log_entry)
        update_metrics()
    }
    
    val final_result = {
        // Another expression block
        val multiplier = get_multiplier()
        val adjusted = base_value * multiplier
        return adjusted + bias_correction()
    }
    
    return final_result
}
```

### Conditional Block Usage

```hexen
val result = if condition {
    // Expression block in conditional
    val temp = expensive_computation()
    return temp * 2
} else {
    // Alternative expression block
    val fallback = default_value()
    return fallback
}

// Statement blocks for conditional side effects
if should_cleanup {
    // Statement block
    {
        val temp_files = list_temp_files()
        remove_files(temp_files)
        clear_cache()
    }
}
```

### Block-Based Error Handling (Future)

```hexen
// Future: try-catch blocks using unified block system
val safe_result = try {
    val risky = dangerous_operation()
    return process(risky)
} catch error {
    val fallback = handle_error(error)
    return fallback
}
```

## Benefits and Trade-offs

### Benefits

1. **Cognitive Simplicity**: One syntax to learn, context provides behavior
2. **Consistent Scoping**: Same rules everywhere, no special cases
3. **Composability**: Blocks can be nested and combined naturally
4. **Implementation Elegance**: Single code path for scope management
5. **Future-Proof**: Pattern extends to new language constructs

### Trade-offs

1. **Context Dependency**: Behavior depends on usage context
2. **Learning Curve**: Must understand context implications
3. **Analysis Complexity**: Implementation requires context tracking

### Comparison with Other Languages

| Language | Block Types | Scope Rules | Context Dependency |
|----------|-------------|-------------|--------------------|
| **Hexen** | Unified `{}` | Consistent | Context-driven |
| **Rust** | Multiple syntaxes | Varied | Syntax-specific |
| **C/Java** | Statement blocks only | Consistent | Limited |
| **JavaScript** | Multiple patterns | Inconsistent | Syntax-specific |

## Error Handling

### Context-Specific Error Messages

```hexen
// Expression block without return
val invalid = {
    val temp = 42
    // Error: "Expression block must end with a return statement"
}

// Void function with return value
func work() : void = {
    return 42    // Error: "Void function cannot return a value"
}

// Return outside valid context
return 42        // Error: "Return statement outside valid context"
```

### Scope-Related Errors

```hexen
{
    val scoped = "local"
}
val access = scoped    // Error: "Undefined variable: 'scoped'"

// Redeclaration in same scope
{
    val name = "first"
    val name = "second"    // Error: "Variable 'name' already declared in this scope"
}
```

## Future Extensions

### Pattern Matching Blocks

```hexen
// Future: match expressions using unified blocks
val result = match value {
    Pattern1 => {
        val processed = handle_pattern1(value)
        return processed
    }
    Pattern2 => {
        val alternative = handle_pattern2(value)
        return alternative
    }
}
```

### Async Blocks

```hexen
// Future: async blocks using unified syntax
val async_result = async {
    val data = await fetch_data()
    val processed = await process(data)
    return processed
}
```

### Generic Blocks

```hexen
// Future: generic function bodies
func transform<T>(value: T) : T = {
    val processed = apply_transformation(value)
    return processed
}
```

## Implementation Guidelines

### For Language Implementers

1. **Unified Scope Management**: All blocks use identical scope creation/destruction
2. **Context Propagation**: Pass context information through analysis pipeline
3. **Return Validation**: Implement context-specific return statement validation
4. **Error Recovery**: Continue analysis after block-related errors
5. **Consistent Semantics**: Same rules apply regardless of block usage

### For Tool Developers

1. **Syntax Highlighting**: Same highlighting rules for all `{}` blocks
2. **Code Completion**: Context-aware suggestions based on block type
3. **Error Reporting**: Block-context-specific error messages
4. **Refactoring**: Understand scope boundaries for safe transformations

### For Hexen Developers

1. **Mental Model**: Think "block = scope + context-specific behavior"
2. **Scope Awareness**: Variables are always scoped to their containing block
3. **Context Clarity**: Understand how block usage determines behavior
4. **Composition**: Combine blocks naturally for complex logic

## Conclusion

The Unified Block System represents a fundamental design achievement in Hexen: taking the complexity of different execution contexts and providing a single, elegant syntax that adapts naturally to its usage. This system embodies the language's core philosophy of being "pedantic to write, but really easy to read" - developers must be explicit about context, but the resulting code is immediately understandable.

By unifying scope management across all contexts while allowing context-specific behaviors, Hexen achieves both implementation elegance and developer ergonomics. The system is extensible, consistent, and provides a solid foundation for future language features.

The unified block system is not just a syntactic convenience - it's a fundamental architectural decision that influences how developers think about code organization, scope management, and expression composition in Hexen. 