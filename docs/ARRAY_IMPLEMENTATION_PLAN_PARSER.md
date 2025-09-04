# Array Type System - Parser Implementation Plan 🦉

*Phase 1: Grammar and Parser Implementation*

## Overview

This document outlines the implementation plan for Phase 1 of Hexen's array type system - focusing exclusively on **grammar definition and parser implementation**. This phase will handle syntax recognition and AST generation, leaving semantic analysis for a separate implementation plan.

## Context & Background

Based on the comprehensive [ARRAY_TYPE_SYSTEM.md](ARRAY_TYPE_SYSTEM.md) specification, arrays in Hexen follow these key design principles:

- **Integration with Comptime Types**: Arrays work seamlessly with `comptime_array_int` and `comptime_array_float`
- **Flexible Sizing**: `[N]T` (fixed), `[_]T` (inferred), with multidimensional support `[N][M]T`
- **Consistent with Core Language**: Same `val`/`mut` rules, same type conversion patterns
- **Unified Block System Integration**: Arrays work in expression blocks following compile-time vs runtime classification

## Parser Implementation Scope

### What This Phase Covers ✅
1. **Grammar Definition**: Array literal syntax, type declarations, element access
2. **AST Node Creation**: New AST nodes for array constructs
3. **Parser Logic**: Recognition and tree building for array syntax
4. **Unit Tests**: Comprehensive parser test coverage
5. **Example Programs**: Working `.hxn` files demonstrating array syntax

### What This Phase Does NOT Cover ❌
- Semantic analysis (type checking, bounds checking)
- Comptime type resolution (`comptime_array_int` → `[3]i32`)
- Integration with expression blocks
- Error handling beyond syntax errors
- Array operations (concatenation, element-wise operations)

## Implementation Tasks

### Task 1: Grammar Extensions (`hexen.lark`)

**File**: `src/hexen/hexen.lark`

Add grammar rules for array syntax:

```lark
// Array type declarations
array_type: "[" (INTEGER | "_") "]" type

// Multidimensional array types  
multidim_array_type: ("[" (INTEGER | "_") "]")+ type

// Array literals
array_literal: "[" [expression ("," expression)*] "]"

// Array element access
array_access: postfix_expr "[" expression "]"

// Update type rule to include arrays
type: primitive_type | array_type | multidim_array_type

// Update postfix expressions to include array access
postfix_expr: primary_expr (array_access)*
```

**Estimated Complexity**: Medium
**Lines Added**: ~15-20

### Task 2: AST Node Definitions (`ast_nodes.py`)

**File**: `src/hexen/ast_nodes.py`

Create AST nodes for array constructs:

```python
@dataclass
class ArrayType(ASTNode):
    """Array type declaration: [N]T or [_]T"""
    size: Union[IntegerLiteral, str]  # IntegerLiteral or "_"
    element_type: ASTNode
    location: Location

@dataclass  
class MultidimArrayType(ASTNode):
    """Multidimensional array type: [N][M]T"""
    dimensions: List[Union[IntegerLiteral, str]]  # [size1, size2, ...] 
    element_type: ASTNode
    location: Location

@dataclass
class ArrayLiteral(ASTNode):
    """Array literal: [1, 2, 3]"""
    elements: List[ASTNode]
    location: Location

@dataclass
class ArrayAccess(ASTNode):
    """Array element access: arr[index]"""
    array: ASTNode
    index: ASTNode
    location: Location
```

**Estimated Complexity**: Low-Medium
**Lines Added**: ~40-50

### Task 3: Parser Logic Updates (`parser.py`)

**File**: `src/hexen/parser.py`

Add transformation methods for new grammar rules:

```python
def array_type(self, items):
    """Transform array type: [N]T"""
    size = items[0]  # INTEGER or "_" 
    element_type = items[1]
    return ArrayType(
        size=size,
        element_type=element_type,
        location=self._get_location(items)
    )

def multidim_array_type(self, items):
    """Transform multidimensional array type: [N][M]T"""
    # Extract dimensions and element type
    dimensions = []
    element_type = items[-1]  # Last item is always element type
    
    for item in items[:-1]:
        dimensions.append(item)
    
    return MultidimArrayType(
        dimensions=dimensions,
        element_type=element_type,
        location=self._get_location(items)
    )

def array_literal(self, items):
    """Transform array literal: [1, 2, 3]"""
    elements = list(items) if items else []
    return ArrayLiteral(
        elements=elements,
        location=self._get_location(items)
    )

def array_access(self, items):
    """Transform array access: arr[index]"""
    array = items[0]
    index = items[1]
    return ArrayAccess(
        array=array,
        index=index,
        location=self._get_location(items)
    )
```

**Estimated Complexity**: Medium
**Lines Added**: ~60-80

### Task 4: Postfix Expression Handling

Update existing postfix expression parsing to handle array access chaining:

```python
def postfix_expr(self, items):
    """Handle postfix expressions including array access"""
    expr = items[0]  # Base expression
    
    # Chain array accesses: arr[i][j][k]
    for access in items[1:]:
        if isinstance(access, ArrayAccess):
            access.array = expr
            expr = access
    
    return expr
```

**Estimated Complexity**: Medium (integration with existing code)
**Lines Added**: ~15-20

### Task 5: Parser Test Suite

**Files**: `tests/parser/test_array_types.py`, `tests/parser/test_array_literals.py`, `tests/parser/test_array_access.py`

Comprehensive test coverage for all array syntax:

#### `test_array_types.py`:
```python
def test_fixed_size_array_type():
    """Test [N]T syntax"""
    # Test cases: [3]i32, [10]f64, [1]bool, etc.

def test_inferred_size_array_type():
    """Test [_]T syntax"""  
    # Test cases: [_]i32, [_]f64, [_]string, etc.

def test_multidimensional_array_types():
    """Test [N][M]T syntax"""
    # Test cases: [3][4]i32, [_][_]f64, [2][_]string, etc.

def test_nested_array_types():
    """Test arrays of arrays vs multidimensional"""
    # Edge cases and complex nesting
```

#### `test_array_literals.py`:
```python
def test_empty_array_literal():
    """Test [] syntax"""

def test_single_element_array():
    """Test [42] syntax"""

def test_multiple_element_array():
    """Test [1, 2, 3] syntax"""

def test_nested_array_literals():
    """Test [[1, 2], [3, 4]] syntax"""

def test_mixed_type_array_literals():
    """Test [42, 3.14, true] syntax"""
```

#### `test_array_access.py`:
```python  
def test_single_array_access():
    """Test arr[0] syntax"""

def test_chained_array_access():
    """Test arr[0][1][2] syntax"""

def test_complex_array_access():
    """Test arr[i + j][compute()] syntax"""
```

**Estimated Complexity**: High (comprehensive coverage)
**Lines Added**: ~300-400

### Task 6: Example Programs

**Files**: `examples/arrays/basic_arrays.hxn`, `examples/arrays/multidim_arrays.hxn`

Create working Hexen programs demonstrating array syntax:

#### `basic_arrays.hxn`:
```hexen
func demonstrate_basic_arrays() : void = {
    // Array type declarations (parser should recognize syntax)
    val numbers : [3]i32 = [1, 2, 3]
    val floats : [_]f64 = [3.14, 2.71, 1.41]
    val inferred = [42, 100, 200]
    
    // Array element access (parser should recognize syntax)
    val first : i32 = numbers[0]
    val computed_index : i32 = numbers[1 + 1]
    
    // Mutable arrays (parser should recognize syntax)
    mut dynamic : [_]i32 = [10, 20, 30]
    dynamic[0] = 42
}
```

#### `multidim_arrays.hxn`:
```hexen
func demonstrate_multidim_arrays() : void = {
    // 2D array syntax (parser should recognize)
    val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
    val inferred_2d : [_][_]f64 = [[1.1, 2.2], [3.3, 4.4]]
    
    // Element access (parser should recognize)
    val element : i32 = matrix[1][2]
    val row : [3]i32 = matrix[0]
    
    // 3D arrays (parser should recognize)
    val cube : [2][2][2]i32 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
}
```

**Estimated Complexity**: Low-Medium
**Files Created**: 2-3 example files

## Testing Strategy

### Parser-Only Tests
Since this phase focuses on parsing, all tests verify AST generation correctness:

1. **Syntax Recognition**: Ensure all array syntax is parsed without errors
2. **AST Structure**: Verify correct AST node types and relationships
3. **Location Tracking**: Ensure accurate source location information
4. **Error Cases**: Test malformed syntax produces appropriate parse errors

### Test Categories
1. **Unit Tests**: Individual grammar rules in isolation
2. **Integration Tests**: Array syntax within larger programs
3. **Edge Case Tests**: Complex nesting, unusual combinations
4. **Error Tests**: Malformed syntax, incomplete expressions

### Success Criteria
- All array syntax from ARRAY_TYPE_SYSTEM.md parses correctly
- Generated AST nodes match expected structure
- Parser handles complex nested and multidimensional cases
- Comprehensive test coverage (aim for >95%)
- Example programs parse successfully

## Implementation Order

### Phase 1a: Basic Array Support (Week 1)
1. Add basic array grammar rules (`[N]T`, `[_]T`)
2. Create basic AST nodes (`ArrayType`, `ArrayLiteral`)
3. Implement basic parser transformations
4. Write unit tests for basic cases

### Phase 1b: Array Access (Week 1)
1. Add array access grammar (`arr[index]`)
2. Create `ArrayAccess` AST node
3. Integrate with postfix expression handling
4. Write unit tests for access patterns

### Phase 1c: Multidimensional Support (Week 2)
1. Extend grammar for multidimensional arrays
2. Create `MultidimArrayType` AST node
3. Handle complex parsing cases (`[N][M][K]T`)
4. Write comprehensive multidimensional tests

### Phase 1d: Integration & Polish (Week 2)
1. Create example programs
2. Run comprehensive test suite
3. Fix any parsing edge cases
4. Document parser behavior

## File Modifications Summary

### New Files:
- `tests/parser/test_array_types.py`
- `tests/parser/test_array_literals.py` 
- `tests/parser/test_array_access.py`
- `examples/arrays/basic_arrays.hxn`
- `examples/arrays/multidim_arrays.hxn`

### Modified Files:
- `src/hexen/hexen.lark` (~15-20 lines added)
- `src/hexen/ast_nodes.py` (~40-50 lines added)
- `src/hexen/parser.py` (~75-100 lines added)

### Total Lines Added: ~430-570 lines
### Total Files Modified: 3
### Total Files Created: 5

## Risk Analysis

### Low Risk:
- Basic array type syntax (`[N]T`, `[_]T`)
- Array literal parsing (`[1, 2, 3]`)
- Simple element access (`arr[0]`)

### Medium Risk:
- Multidimensional array parsing (`[N][M]T`)
- Chained array access (`arr[i][j][k]`)
- Integration with existing postfix expressions

### High Risk:
- Complex nested expressions in array contexts
- Performance with deeply nested multidimensional syntax
- Ensuring all edge cases are covered

## Success Metrics

### Functional:
- [ ] All array syntax from specification parses correctly
- [ ] AST nodes accurately represent parsed structure
- [ ] Chained array access works (`arr[i][j][k]`)
- [ ] Multidimensional arrays parse correctly
- [ ] Example programs run through parser successfully

### Quality:
- [ ] >95% test coverage on new parser code
- [ ] All tests pass consistently
- [ ] No performance regressions in parser
- [ ] Clean, maintainable code structure

### Documentation:
- [ ] Parser behavior documented
- [ ] Example programs demonstrate all features
- [ ] Test suite documents expected behavior
- [ ] Integration points with semantic analysis identified

## Next Phase Preview

After completing the parser implementation, **Phase 2** will focus on semantic analysis:
- Comptime array type system (`comptime_array_int`, `comptime_array_float`)
- Array type checking and bounds validation
- Integration with expression blocks and unified block system
- Array operations and element-wise computation
- Memory layout and flattening semantics

This parser-focused approach ensures a solid foundation for the complete array type system while maintaining manageable implementation scope.