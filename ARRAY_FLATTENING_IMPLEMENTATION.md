# Array Flattening Implementation Plan 🚀

*Complete implementation guide for Hexen array flattening feature*

## Overview 📋

Array flattening enables safe, zero-cost conversion from multidimensional arrays to 1D arrays, leveraging Hexen's row-major memory layout. This feature is currently **designed and scaffolded** but needs **integration with the type system**.

### Current Status
- **Design**: ✅ Complete (ARRAY_TYPE_SYSTEM.md specification)
- **Infrastructure**: ✅ Complete (analysis functions, error messages, utilities)
- **Tests**: ✅ Conceptual test exists
- **Integration**: ❌ **Missing** (assignment logic doesn't support flattening yet)

## Target Functionality 🎯

### Basic Array Flattening
```hexen
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
val flattened : [6]i32 = matrix                    // → [1, 2, 3, 4, 5, 6]
val inferred : [_]i32 = matrix                     // → [6]i32 (size inferred)
```

### Comptime Array Flattening  
```hexen
val comptime_matrix = [[42, 100], [200, 300]]      // comptime_array of comptime_array_int
val flat_i32 : [_]i32 = comptime_matrix            // → [4]i32 
val flat_f64 : [_]f64 = comptime_matrix            // Same source → [4]f64
val flat_f32 : [_]f32 = comptime_matrix            // Same source → [4]f32
```

### Error Cases
```hexen
val matrix_2x3 : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]   // 6 elements total
val wrong_size : [5]i32 = matrix_2x3                   // ❌ Error: 6 ≠ 5 elements

val mixed_types : [2][2]f64 = [[1.1, 2.2], [3.3, 4.4]]
val no_conversion : [_]i32 = mixed_types                // ❌ Error: f64 → i32 needs explicit conversion
val explicit : [_]i32 = mixed_types:[_]i32             // ✅ Explicit conversion
```

## Implementation Strategy 🔧

### Phase 1: Core Integration (1-2 days)
Connect existing flattening infrastructure to the type system.

### Phase 2: Size Inference (1 day)  
Enable `[_]` size inference from source array dimensions.

### Phase 3: Testing & Validation (1 day)
Comprehensive test suite covering all flattening scenarios.

## Detailed Implementation Plan 📝

### 1. Core Integration - Assignment Analysis

**File**: `src/hexen/semantic/declaration_analyzer.py`

**Objective**: Detect and handle flattening assignments during variable declaration.

#### Current Assignment Flow
```python
def analyze_val_declaration(self, node: Dict) -> bool:
    # ... existing code ...
    # Missing: Array flattening detection and handling
```

#### Required Changes
```python
def analyze_val_declaration(self, node: Dict) -> bool:
    """Enhanced to support array flattening assignments"""
    # ... existing code ...
    
    # Add flattening detection after type resolution
    if self._is_flattening_assignment(target_type, value_type):
        return self._handle_flattening_assignment(node, target_type, value_type)
    
    # ... rest of existing logic ...

def _is_flattening_assignment(self, target_type: HexenType, source_type: HexenType) -> bool:
    """Detect if assignment is array flattening operation"""
    return (
        isinstance(target_type, ConcreteArrayType) and
        isinstance(source_type, ConcreteArrayType) and 
        len(target_type.dimensions) == 1 and  # Target is 1D
        len(source_type.dimensions) > 1       # Source is multidimensional
    )

def _handle_flattening_assignment(self, node: Dict, target_type: HexenType, source_type: HexenType) -> bool:
    """Handle array flattening assignment using existing infrastructure"""
    # Use existing MultidimensionalArrayAnalyzer
    flattening_result = self.array_analyzer.multidim_analyzer.analyze_array_flattening(
        source_array_info=self._extract_array_info(source_type),
        target_type=target_type
    )
    
    if not flattening_result.get("valid", False):
        return False
    
    # Store flattening metadata for code generation
    self._register_flattening_operation(node, flattening_result)
    return True
```

### 2. Size Inference Enhancement

**File**: `src/hexen/semantic/type_util.py`

**Objective**: Enable `[_]` to infer size from multidimensional source arrays.

#### Current Size Inference
```python
# Missing: Multidimensional → 1D size calculation
```

#### Required Enhancement  
```python
def infer_array_dimensions_from_source(target_type: ConcreteArrayType, source_type: ConcreteArrayType) -> ConcreteArrayType:
    """Infer target array dimensions from source array for flattening"""
    if not _is_flattening_context(target_type, source_type):
        return target_type
    
    # Calculate flattened size
    total_elements = 1
    for dim_size in source_type.dimensions:
        if dim_size == "_":
            # Cannot flatten from inferred source dimensions
            raise ArrayAnalysisError("Cannot flatten array with inferred source dimensions")
        total_elements *= dim_size
    
    # Create new type with inferred size
    return ConcreteArrayType(
        element_type=target_type.element_type,
        dimensions=[total_elements]  # Flattened to 1D with calculated size
    )
```

### 3. Expression Context Integration

**File**: `src/hexen/semantic/expression_analyzer.py`

**Objective**: Support flattening in expression contexts (not just declarations).

#### Integration Point
```python
def analyze_expression(self, node: Dict, target_type: Optional[HexenType] = None) -> HexenType:
    """Enhanced to support array flattening in expressions"""
    # ... existing dispatch logic ...
    
    # After getting expression type, check for flattening context
    expr_result = self._dispatch_expression_analysis(expr_type, node, target_type)
    
    # Post-process for potential flattening
    if target_type and self._should_attempt_flattening(expr_result, target_type):
        return self._apply_flattening_coercion(expr_result, target_type)
    
    return expr_result
```

## Test Implementation Plan 🧪

### Test File Structure
```
tests/semantic/arrays/test_array_flattening.py
├── TestBasicArrayFlattening
├── TestComptimeArrayFlattening  
├── TestFlatteningErrorCases
├── TestFlatteningSizeInference
├── TestFlatteningExpressionContexts
└── TestFlatteningIntegration
```

### Comprehensive Test Cases

#### TestBasicArrayFlattening
```python
def test_2d_to_1d_fixed_size(self):
    """Test basic 2D → 1D flattening with fixed sizes"""
    source = """
    func test() : void = {
        val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
        val flattened : [6]i32 = matrix
        return
    }
    """
    assert_no_errors(source)

def test_3d_to_1d_flattening(self):
    """Test 3D → 1D flattening with size calculation"""
    source = """
    func test() : void = {
        val cube : [2][2][2]i32 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        val flattened : [8]i32 = cube
        return
    }
    """
    assert_no_errors(source)

def test_size_inference_basic(self):
    """Test size inference in flattening: [_] infers correct size"""
    source = """
    func test() : void = {
        val matrix : [3][4]i32 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        val inferred : [_]i32 = matrix  // Should infer [12]i32
        return
    }
    """
    assert_no_errors(source)
```

#### TestComptimeArrayFlattening
```python
def test_comptime_2d_flexibility(self):
    """Test comptime 2D arrays flatten to different 1D types"""
    source = """
    func test() : void = {
        val flexible_2d = [[42, 100], [200, 300]]  // comptime_array of comptime_array_int
        val as_i32 : [_]i32 = flexible_2d          // → [4]i32
        val as_f64 : [_]f64 = flexible_2d          // Same source → [4]f64
        val as_f32 : [_]f32 = flexible_2d          // Same source → [4]f32
        return
    }
    """
    assert_no_errors(source)

def test_comptime_mixed_numeric_flattening(self):
    """Test comptime mixed numeric arrays (int+float) flatten to float types"""
    source = """
    func test() : void = {
        val mixed_2d = [[42, 3.14], [2.71, 100]]   // comptime_array of comptime_array_float
        val as_f64 : [_]f64 = mixed_2d              // All elements fit → [4]f64
        val as_f32 : [_]f32 = mixed_2d              // All elements fit → [4]f32
        return
    }
    """
    assert_no_errors(source)
```

#### TestFlatteningErrorCases
```python
def test_element_count_mismatch_error(self):
    """Test error when flattened size doesn't match target size"""
    source = """
    func test() : void = {
        val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]  // 6 elements total
        val wrong_size : [5]i32 = matrix                   // ❌ Error: 6 ≠ 5
        return
    }
    """
    errors = get_errors(source)
    assert len(errors) == 1
    assert "element count mismatch" in errors[0].lower()
    assert "expected 5 elements, got 6" in errors[0]

def test_type_conversion_required_error(self):
    """Test error when element types need explicit conversion"""
    source = """
    func test() : void = {
        val matrix : [2][2]f64 = [[1.1, 2.2], [3.3, 4.4]]
        val no_conversion : [_]i32 = matrix  // ❌ Error: f64 → i32 needs explicit conversion
        return
    }
    """
    errors = get_errors(source)
    assert len(errors) == 1
    assert "requires explicit conversion" in errors[0].lower()
    assert "f64" in errors[0] and "i32" in errors[0]

def test_inferred_source_dimensions_error(self):
    """Test error when trying to flatten array with inferred source dimensions"""
    source = """
    func test() : void = {
        val source : [_][_]i32 = [[1, 2], [3, 4]]  // Inferred source dimensions
        val target : [4]i32 = source                // ❌ Cannot calculate size from inferred source
        return
    }
    """
    errors = get_errors(source)
    assert len(errors) == 1
    assert "inferred dimensions" in errors[0].lower()

def test_non_rectangular_array_error(self):
    """Test error when trying to flatten non-rectangular arrays"""
    source = """
    func test() : void = {
        // This should be caught during array literal analysis, not flattening
        val irregular = [[1, 2, 3], [4, 5]]        // ❌ Error: non-rectangular
        val flattened : [_]i32 = irregular
        return
    }
    """
    errors = get_errors(source)
    assert len(errors) >= 1
    assert any("inconsistent" in error.lower() or "irregular" in error.lower() for error in errors)
```

#### TestFlatteningSizeInference  
```python
def test_complex_size_calculations(self):
    """Test size inference for complex multidimensional arrays"""
    test_cases = [
        ("[2][3]i32", 6),      # 2×3 = 6
        ("[4][5]i32", 20),     # 4×5 = 20  
        ("[2][2][2]i32", 8),   # 2×2×2 = 8
        ("[3][4][5]i32", 60),  # 3×4×5 = 60
        ("[1][10]i32", 10),    # 1×10 = 10
        ("[10][1]i32", 10),    # 10×1 = 10
    ]
    
    for source_type, expected_size in test_cases:
        source = f"""
        func test() : void = {{
            val matrix : {source_type} = create_matrix()
            val flattened : [{expected_size}]i32 = matrix
            return
        }}
        func create_matrix() : {source_type} = {{ 
            return undef  // Implementation not needed for this test
        }}
        """
        assert_no_errors(source, f"Failed for {source_type} → [{expected_size}]i32")

def test_size_inference_with_different_element_types(self):
    """Test size inference works with different element types"""
    element_types = ["i32", "i64", "f32", "f64", "bool"]
    
    for element_type in element_types:
        source = f"""
        func test() : void = {{
            val matrix : [3][3]{element_type} = create_matrix()
            val flattened : [_]{element_type} = matrix  // Should infer [9]{element_type}
            return
        }}
        func create_matrix() : [3][3]{element_type} = {{ 
            return undef 
        }}
        """
        assert_no_errors(source, f"Failed for element type {element_type}")
```

#### TestFlatteningExpressionContexts
```python
def test_flattening_in_function_parameters(self):
    """Test array flattening when passing to function parameters"""
    source = """
    func process_1d_array(data: [_]i32) : i32 = {
        return data[0]
    }
    
    func test() : void = {
        val matrix : [2][2]i32 = [[1, 2], [3, 4]]
        val result : i32 = process_1d_array(matrix)  // Should flatten matrix → [4]i32
        return
    }
    """
    assert_no_errors(source)

def test_flattening_in_return_statements(self):
    """Test array flattening in return statements"""
    source = """
    func get_flattened() : [4]i32 = {
        val matrix : [2][2]i32 = [[1, 2], [3, 4]]
        return matrix  // Should flatten [2][2]i32 → [4]i32
    }
    """
    assert_no_errors(source)

def test_flattening_in_expression_blocks(self):
    """Test array flattening within expression blocks"""
    source = """
    func test() : void = {
        val result : [6]i32 = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
            -> matrix  // Should flatten within expression block
        }
        return
    }
    """
    assert_no_errors(source)
```

#### TestFlatteningIntegration
```python
def test_flattening_with_assignment_chains(self):
    """Test flattening in assignment chains"""
    source = """
    func test() : void = {
        val matrix1 : [2][2]i32 = [[1, 2], [3, 4]]
        val matrix2 : [2][2]i32 = [[5, 6], [7, 8]]
        
        val flat1 : [_]i32 = matrix1           // [4]i32
        val flat2 : [_]i32 = matrix2           // [4]i32
        val elem1 : i32 = flat1[0]             // Access flattened elements
        val elem2 : i32 = flat2[3]             // Access flattened elements
        return
    }
    """
    assert_no_errors(source)

def test_nested_flattening_operations(self):
    """Test multiple flattening operations in sequence"""  
    source = """
    func test() : void = {
        val cube : [2][2][2]i32 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        val intermediate : [_][_]i32 = cube[0]  // Extract 2D slice: [2][2]i32
        val final : [_]i32 = intermediate       // Flatten to 1D: [4]i32
        return
    }
    """
    assert_no_errors(source)

def test_flattening_with_type_annotations(self):
    """Test flattening with explicit type annotations and conversions"""
    source = """
    func test() : void = {
        val float_matrix : [2][2]f64 = [[1.1, 2.2], [3.3, 4.4]]
        val int_flattened : [_]i32 = float_matrix:[_]i32  // Explicit conversion + flattening
        val same_type : [_]f64 = float_matrix             // Same type flattening  
        return
    }
    """
    assert_no_errors(source)
```

## Performance Considerations 🚀

### Zero-Cost Flattening
Array flattening leverages Hexen's **row-major memory layout** to provide zero runtime cost:

```hexen
val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
// Memory layout: [1, 2, 3, 4, 5, 6] (contiguous)

val flattened : [6]i32 = matrix
// Same memory address, different type view - NO DATA COPYING!
```

### Compile-Time Validation
- **Element count validation**: `2×3 = 6` calculated at compile time
- **Type compatibility**: Element type matching verified at compile time  
- **Bounds safety**: All size mismatches caught during compilation

### Memory Safety Benefits
- **Replaces unsafe pointer arithmetic**: No more `&matrix[0][0]` patterns
- **Maintains bounds checking**: Flattened arrays retain full bounds safety
- **Type safety**: Compiler ensures size and type correctness

## Implementation Checklist ✅

### Core Integration
- [ ] Add `_is_flattening_assignment()` to `declaration_analyzer.py`
- [ ] Add `_handle_flattening_assignment()` to `declaration_analyzer.py`
- [ ] Integrate existing `MultidimensionalArrayAnalyzer.analyze_array_flattening()`
- [ ] Add flattening detection to expression contexts

### Size Inference  
- [ ] Implement `infer_array_dimensions_from_source()` in `type_util.py`
- [ ] Add element count calculation for multidimensional arrays
- [ ] Handle `[_]` → calculated size conversion
- [ ] Add error handling for inferred source dimensions

### Testing
- [ ] Create `tests/semantic/arrays/test_array_flattening.py`
- [ ] Implement all test classes (6 test classes, ~20 test methods)
- [ ] Add edge case testing for complex scenarios
- [ ] Verify error message quality and consistency

### Documentation
- [ ] Update error messages in `error_messages.py`
- [ ] Add flattening examples to code comments
- [ ] Update ARRAY_TYPE_SYSTEM.md if needed
- [ ] Document performance characteristics

## Timeline Estimate ⏱️

**Total Estimated Time**: 3-4 days

- **Day 1**: Core integration (assignment analysis)
- **Day 2**: Size inference and expression contexts  
- **Day 3**: Comprehensive testing implementation
- **Day 4**: Testing, debugging, and polish

## Success Criteria 🎯

### Functional Requirements
- [ ] Basic flattening: `val flat : [6]i32 = matrix_2x3` works
- [ ] Size inference: `val flat : [_]i32 = matrix_2x3` infers `[6]i32`
- [ ] Comptime flexibility: Same comptime source → multiple target types
- [ ] Error handling: Clear messages for all failure cases
- [ ] Expression contexts: Flattening in functions, returns, blocks

### Quality Requirements  
- [ ] All tests passing (100% success rate)
- [ ] Zero performance regression
- [ ] Clear, actionable error messages
- [ ] Documentation complete and accurate

### Integration Requirements
- [ ] No breaking changes to existing array functionality
- [ ] Seamless integration with unified block system
- [ ] Compatible with existing type conversion patterns
- [ ] Maintains Hexen's "Ergonomic Literals + Transparent Costs" philosophy

---

This implementation plan provides a complete roadmap for making array flattening fully functional in Hexen, building on the excellent infrastructure that's already in place! 🚀

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create array flattening implementation plan document", "status": "completed", "activeForm": "Creating array flattening implementation plan document"}, {"content": "Add comprehensive test cases for array flattening", "status": "in_progress", "activeForm": "Adding comprehensive test cases for array flattening"}]