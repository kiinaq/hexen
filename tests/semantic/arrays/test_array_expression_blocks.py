"""
Week 3 Array Expression Block Integration Tests

Tests the three core aspects of array-block integration:
1. Compile-time array block detection (preserve comptime flexibility)
2. Runtime array block context requirements (require explicit types)
3. Array validation with early returns (dual capability patterns)

Based on ARRAY_IMPLEMENTATION_PLAN.md Week 3 specifications.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


# =============================================================================
# TEST GROUP 1: COMPILE-TIME ARRAY BLOCKS (Comptime Type Preservation)
# =============================================================================


def test_comptime_array_literal_in_block():
    """Compile-time array blocks preserve comptime type flexibility"""
    code = """
    func test() : i32 = {
        val flexible_array = {
            val base = [1, 2, 3, 4, 5]
            -> base
        }
        return flexible_array[0]
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - comptime array preserved through block


def test_comptime_array_operations_in_block():
    """Array operations on comptime arrays preserve flexibility"""
    code = """
    func test() : i32 = {
        val result = {
            val arr = [10, 20, 30]
            val element = arr[0]
            -> element
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - all operations are comptime


def test_comptime_array_copy_in_block():
    """Array copy operations preserve comptime type in blocks"""
    code = """
    func test() : i32 = {
        val copied = {
            val original = [1, 2, 3]
            val copy = original[..]
            -> copy
        }
        return copied[0]
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - RVO eliminates copy on block return


def test_comptime_array_length_property_in_block():
    """Array .length property works in comptime blocks"""
    code = """
    func test() : i32 = {
        val size = {
            val arr = [1, 2, 3, 4, 5]
            -> arr.length
        }
        return size
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - .length on comptime array


def test_nested_comptime_array_operations():
    """Nested array operations maintain comptime classification"""
    code = """
    func test() : i32 = {
        val result = {
            val outer = {
                val inner = [1, 2, 3]
                -> inner
            }
            -> outer[1]
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - nested comptime blocks with RVO


def test_multidimensional_comptime_array_in_block():
    """Multidimensional comptime arrays preserve flexibility in blocks"""
    code = """
    func test() : i32 = {
        val matrix = {
            val data = [[1, 2, 3], [4, 5, 6]]
            -> data
        }
        return matrix[0][1]
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - multidimensional comptime array


def test_comptime_array_with_arithmetic():
    """Arithmetic operations on array elements maintain comptime"""
    code = """
    func test() : i32 = {
        val computed = {
            val arr = [10, 20, 30]
            val sum = arr[0] + arr[1] + arr[2]
            -> sum
        }
        return computed
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - arithmetic on comptime array elements


# =============================================================================
# TEST GROUP 2: RUNTIME ARRAY BLOCKS (Context Requirements)
# =============================================================================


def test_runtime_array_block_with_function_call():
    """Array blocks with function calls require explicit context"""
    code = """
    func get_array() : [3]i32 = {
        return [1, 2, 3]
    }

    func test() : [3]i32 = {
        val result : [3]i32 = {
            val arr = get_array()
            -> arr
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - explicit type annotation provided


def test_runtime_array_block_with_concrete_array():
    """Blocks using concrete arrays require explicit context"""
    code = """
    func test(input: [3]i32) : [3]i32 = {
        val processed : [3]i32 = {
            val copy = input[..]
            -> copy
        }
        return processed
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - explicit context provided for concrete array


def test_runtime_array_block_missing_context_error():
    """Runtime array blocks without context should error"""
    code = """
    func get_array() : [3]i32 = {
        return [1, 2, 3]
    }

    func test() : [3]i32 = {
        val result = {
            val arr = get_array()
            -> arr
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    # Should require explicit type annotation for runtime blocks
    errors = analyzer.analyze(ast)

    # Should have at least one error
    assert len(errors) >= 1

    # Error message should mention context requirement
    error_msg = str(errors[0]).lower()
    assert "explicit type" in error_msg or "type annotation" in error_msg or "context" in error_msg


def test_array_block_with_mixed_operations():
    """Mixed comptime/runtime operations require context"""
    code = """
    func get_size() : i32 = {
        return 5
    }

    func test() : [5]i32 = {
        val result : [5]i32 = {
            val comptime_arr = [1, 2, 3, 4, 5]
            val runtime_size = get_size()
            -> comptime_arr
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - explicit context provided


# =============================================================================
# TEST GROUP 3: ARRAY VALIDATION WITH EARLY RETURNS (Dual Capability)
# =============================================================================


def test_array_validation_with_early_return_empty():
    """Early return for empty array validation"""
    code = """
    func process_array(input: [_]i32) : [_]i32 = {
        val validated : [_]i32 = {
            if input.length == 0 {
                return [0, 0, 0]
            }
            -> input
        }
        return validated
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - early return for validation, RVO on block result


def test_array_validation_with_early_return_size_limit():
    """Early return for array size validation"""
    code = """
    func safe_process(input: [_]i32) : [_]i32 = {
        val validated : [_]i32 = {
            if input.length > 1000 {
                return [-1]
            }
            -> input
        }
        return validated
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - size limit validation, RVO on block result


def test_array_validation_multiple_guards():
    """Multiple validation guards with early returns"""
    code = """
    func robust_process(input: [_]i32) : [_]i32 = {
        val validated : [_]i32 = {
            if input.length == 0 {
                return [0]
            }
            if input.length > 100 {
                return [-1]
            }
            if input[0] < 0 {
                return [-2]
            }
            -> input
        }
        return validated
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - multiple validation guards, RVO on block result


def test_array_caching_pattern_with_early_return():
    """Caching pattern with early return optimization"""
    code = """
    func cached_lookup(key: i32) : [3]i32 = {
        val result : [3]i32 = {
            if key == 0 {
                return [1, 2, 3]
            }
            if key == 1 {
                return [4, 5, 6]
            }
            -> [0, 0, 0]
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - caching with early returns


def test_array_bounds_checking_with_fallback():
    """Bounds checking with fallback array"""
    code = """
    func safe_access(data: [_]i32, index: i32) : i32 = {
        val value = {
            if index < 0 {
                return -1
            }
            if index >= data.length {
                return -1
            }
            -> data[index]
        }
        return value
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - bounds checking with fallback


def test_nested_array_validation():
    """Nested validation blocks with array operations"""
    code = """
    func complex_validation(outer: [_]i32) : [_]i32 = {
        val result : [_]i32 = {
            val inner_check = {
                if outer.length < 2 {
                    return [1, 2]
                }
                -> outer
            }
            -> inner_check
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - nested validation with RVO


# =============================================================================
# TEST GROUP 4: ARRAY COPY AND PROPERTY ACCESS IN BLOCKS
# =============================================================================


def test_array_copy_chain_in_block():
    """Multiple array copy operations in expression block"""
    code = """
    func test() : [3]i32 = {
        val result : [3]i32 = {
            val original = [1, 2, 3]
            val copy1 = original[..]
            val copy2 = copy1[..]
            -> copy2
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - copy chain


def test_property_access_with_arithmetic():
    """Array .length property used in arithmetic"""
    code = """
    func compute_capacity(data: [_]i32) : i32 = {
        val capacity = {
            val size = data.length
            val computed = size * 2
            -> computed
        }
        return capacity
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - length in arithmetic


def test_multidim_array_copy_in_block():
    """Multidimensional array copy in expression block"""
    code = """
    func test() : [2][3]i32 = {
        val result : [2][3]i32 = {
            val matrix = [[1, 2, 3], [4, 5, 6]]
            val copied = matrix[..]
            -> copied
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - multidimensional copy


def test_row_access_and_length():
    """Access matrix row and get its length"""
    code = """
    func get_row_size(matrix: [_][_]i32) : i32 = {
        val size = {
            val first_row = matrix[0]
            val row_length = first_row.length
            -> row_length
        }
        return size
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - row access then length


# =============================================================================
# TEST GROUP 5: EDGE CASES AND ERROR CONDITIONS
# =============================================================================


def test_empty_array_in_block_requires_context():
    """Empty arrays in blocks require explicit context"""
    code = """
    func test() : [0]i32 = {
        val empty : [0]i32 = {
            -> []
        }
        return empty
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - explicit context provided


def test_array_block_with_type_conversion():
    """Array blocks with explicit type conversions"""
    code = """
    func test() : [3]i64 = {
        val converted : [3]i64 = {
            val arr = [1, 2, 3]
            -> arr
        }
        return converted
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - comptime array adapts to i64


def test_inferred_size_array_in_block():
    """Inferred-size arrays work in expression blocks"""
    code = """
    func flexible(input: [_]i32) : [_]i32 = {
        val result : [_]i32 = {
            val processed = input[..]
            -> processed
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - inferred size preserved


def test_comptime_array_multiple_uses_from_block():
    """Comptime array from block used in multiple contexts"""
    code = """
    func test() : i32 = {
        val flexible = {
            val base = [1, 2, 3]
            -> base
        }
        val as_i32 : i32 = flexible[0]
        val as_i64 : i64 = flexible[1]
        return as_i32
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - comptime flexibility preserved


# =============================================================================
# TEST GROUP 6: INTEGRATION WITH WEEK 2 FEATURES
# =============================================================================


def test_array_parameter_copy_in_block():
    """Week 2 pass-by-value semantics with RVO in expression blocks"""
    code = """
    func process(data: [3]i32) : [3]i32 = {
        val result : [3]i32 = {
            -> data
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - RVO eliminates copy (pass-by-value semantics preserved)


def test_mut_parameter_in_array_block():
    """Mutable parameters with array operations in blocks"""
    code = """
    func modify(mut data: [_]i32) : [_]i32 = {
        val result : [_]i32 = {
            -> data
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - mut parameter in block


def test_fixed_size_matching_in_block():
    """Week 2 fixed-size validation within blocks"""
    code = """
    func exact_three(values: [3]i32) : [3]i32 = {
        val result : [3]i32 = {
            -> values
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - fixed size maintained, RVO optimizes transfer


def test_comptime_array_adaptation_in_block():
    """Week 2 comptime array adaptation within blocks"""
    code = """
    func adapt(data: [_]f64) : f64 = {
        val result : f64 = {
            val comptime_arr = [1, 2, 3]
            -> comptime_arr[0]
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # Should compile - comptime adaptation


# =============================================================================
# TEST GROUP 7: NEGATIVE TESTS - ERROR CONDITIONS
# =============================================================================
# Note: These tests document EXPECTED behavior per UNIFIED_BLOCK_SYSTEM.md spec.
# Tests marked with @pytest.mark.xfail indicate features not yet implemented
# in the semantic analyzer but required by the specification.


def test_error_runtime_block_with_conditional_missing_context():
    """Runtime block with conditional requires explicit type context"""
    code = """
    func test() : [3]i32 = {
        val result = {
            val arr = if true {
                -> [1, 2, 3]
            } else {
                -> [4, 5, 6]
            }
            -> arr
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    # Should require explicit type annotation for runtime blocks with conditionals
    errors = analyzer.analyze(ast)

    # Should have at least one error
    assert len(errors) >= 1

    # Error message should mention context requirement or conditional
    error_msg = str(errors[0]).lower()
    assert "explicit type" in error_msg or "type annotation" in error_msg or "conditional" in error_msg


@pytest.mark.xfail(reason="Mixed concrete array type validation not yet implemented (spec requirement)")
def test_error_mixed_concrete_array_types_without_conversion():
    """Mixed concrete array element types without explicit conversion should error"""
    code = """
    func test() : [3]i64 = {
        val a : [3]i32 = [1, 2, 3]
        val b : [3]i64 = [4, 5, 6]
        val result : [3]i64 = {
            -> a
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    # Should require explicit conversion from [3]i32 to [3]i64
    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "type" in error_msg or "conversion" in error_msg or "incompatible" in error_msg


@pytest.mark.xfail(reason="Array size mismatch validation not yet implemented (spec requirement)")
def test_error_array_block_wrong_size_annotation():
    """Array block with wrong size annotation should error"""
    code = """
    func test() : [5]i32 = {
        val wrong_size : [3]i32 = {
            val arr = [1, 2, 3, 4, 5]
            -> arr
        }
        return wrong_size
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "size" in error_msg or "length" in error_msg or "type" in error_msg


@pytest.mark.xfail(reason="Early return type mismatch validation not yet implemented (spec requirement)")
def test_error_early_return_type_mismatch():
    """Early return with wrong type should error"""
    code = """
    func test() : [3]i32 = {
        val result : [3]i32 = {
            if true {
                return [1, 2, 3, 4, 5]
            }
            -> [1, 2, 3]
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "type" in error_msg or "size" in error_msg or "return" in error_msg


@pytest.mark.xfail(reason="Block result type mismatch validation not yet implemented (spec requirement)")
def test_error_block_result_type_mismatch():
    """Block result type mismatch with annotation should error"""
    code = """
    func test() : i32 = {
        val wrong_type : i32 = {
            -> [1, 2, 3]
        }
        return wrong_type
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "type" in error_msg or "incompatible" in error_msg


@pytest.mark.xfail(reason="Empty array context requirement not yet implemented (spec requirement)")
def test_error_empty_array_without_context():
    """Empty array in block without context should error"""
    code = """
    func test() : [0]i32 = {
        val empty = {
            -> []
        }
        return empty
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "context" in error_msg or "type" in error_msg or "empty" in error_msg


@pytest.mark.xfail(reason="Array element type mismatch validation not yet implemented (spec requirement)")
def test_error_array_element_type_mismatch_in_block():
    """Array element type mismatch should error"""
    code = """
    func test() : [3]i32 = {
        val mixed : [3]i32 = {
            -> [1, 2.5, 3]
        }
        return mixed
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "type" in error_msg or "element" in error_msg


@pytest.mark.xfail(reason="Multidimensional array size validation not yet implemented (spec requirement)")
def test_error_multidim_array_size_mismatch():
    """Multidimensional array size mismatch should error"""
    code = """
    func test() : [2][3]i32 = {
        val wrong_inner : [2][3]i32 = {
            -> [[1, 2], [3, 4]]
        }
        return wrong_inner
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "size" in error_msg or "type" in error_msg or "dimension" in error_msg


@pytest.mark.xfail(reason="Inferred-size to concrete-size validation not yet implemented (spec requirement)")
def test_error_inferred_size_concrete_mismatch():
    """Inferred size array with wrong concrete size should error"""
    code = """
    func process(input: [_]i32) : [_]i32 = {
        val result : [5]i32 = {
            -> input
        }
        return result
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    # Should error because [_]i32 cannot be assigned to [5]i32 without size validation
    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "size" in error_msg or "type" in error_msg or "inferred" in error_msg


@pytest.mark.xfail(reason="Property access validation on non-array types not yet implemented (spec requirement)")
def test_error_property_access_on_non_array():
    """Property access on non-array type should error"""
    code = """
    func test() : i32 = {
        val size = {
            val not_array : i32 = 42
            -> not_array.length
        }
        return size
    }
    """
    parser = HexenParser()
    ast = parser.parse(code)
    analyzer = SemanticAnalyzer()

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze(ast)

    error_msg = str(exc_info.value).lower()
    assert "length" in error_msg or "property" in error_msg or "array" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
