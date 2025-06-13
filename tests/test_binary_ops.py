"""
Tests for binary operations in Hexen.

Focuses on:
1. Division operators (/ and \)
2. Type resolution and coercion
3. Comptime type adaptation
4. Error cases
"""

from hexen.parser import HexenParser
from hexen.semantic import SemanticAnalyzer


def parse_and_check(source: str) -> tuple[dict, list]:
    """Helper to parse and check source code."""
    parser = HexenParser()
    ast = parser.parse(source)
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)
    return ast, errors


def test_float_division():
    """Test float division operator (/) with various types."""
    source = """
    func main(): i32 = {
        val x : f64 = 10 / 2
        val y : f32 = 5 / 2
        val z : f64 = 10.0 / 2
        val w : f64 = 10 / 2.0
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"


def test_integer_division():
    """Test integer division operator (\\) with various types."""
    source = """
    func main(): i32 = {
        val x : i32 = 10 \\ 2
        val y : i64 = 100 \\ 2
        val z : i32 = 10 \\ 3
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"


def test_division_type_errors():
    """Test error cases for division operators."""
    source = """
    func main(): i32 = {
        val x : i32 = 10.0 \\ 2  // Error: float in integer division
        val y : f64 = 10 \\ 2.0  // Error: float in integer division
        val z : i32 = "hello" / 2  // Error: string in division
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert len(errors) == 3, f"Expected 3 errors, got {len(errors)}"
    assert any("float in integer division" in str(e) for e in errors)
    assert any("string in division" in str(e) for e in errors)


def test_comptime_type_adaptation():
    """Test comptime type adaptation in binary operations."""
    source = """
    func main(): i32 = {
        // Comptime int adaptation
        val x : f64 = 10 + 20  // comptime_int -> f64
        val y : i64 = 10 * 20  // comptime_int -> i64
        val z : f32 = 10 / 2   // comptime_int -> f32
        
        // Comptime float adaptation
        val a : f64 = 10.0 + 20  // comptime_float -> f64
        val b : f32 = 10.0 * 2   // comptime_float -> f32
        
        // Mixed comptime types
        val c : f64 = 10 + 20.0  // comptime_int + comptime_float -> f64
        val d : f64 = 10.0 + 20  // comptime_float + comptime_int -> f64
        
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"


def test_arithmetic_type_resolution():
    """Test type resolution for arithmetic operations."""
    source = """
    func main(): i32 = {
        // Integer operations
        val x : i32 = 10 + 20
        val y : i64 = 100 + 200
        val z : i32 = 10 * 20
        
        // Float operations
        val a : f32 = 10.0 + 20.0
        val b : f64 = 100.0 + 200.0
        val c : f32 = 10.0 * 20.0
        
        // Mixed operations
        val d : f64 = 10 + 20.0  // int + float -> float
        val e : f64 = 10.0 + 20  // float + int -> float
        val f : f64 = 10 * 20.0  // int * float -> float
        
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"


def test_operator_precedence():
    """Test operator precedence in binary operations."""
    source = """
    func main(): i32 = {
        // Test precedence: * and / before + and -
        val x : i32 = 10 + 20 * 2  // Should be 10 + (20 * 2)
        val y : f64 = 10.0 + 20 / 2  // Should be 10.0 + (20 / 2)
        val z : i32 = 10 * 2 + 20  // Should be (10 * 2) + 20
        val w : f64 = 10 / 2 + 20.0  // Should be (10 / 2) + 20.0
        
        // Test precedence with parentheses
        val a : i32 = (10 + 20) * 2  // Should be (10 + 20) * 2
        val b : f64 = (10.0 + 20) / 2  // Should be (10.0 + 20) / 2
        
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"


def test_mixed_type_operations():
    """Test operations with mixed concrete types."""
    source = """
    func main(): i32 = {
        // Mixed integer types
        val x : i64 = 10 + 20  // i32 + i32 -> i64
        val y : i64 = 100 + 200  // i64 + i64 -> i64
        
        // Mixed float types
        val z : f64 = 10.0 + 20.0  // f32 + f32 -> f64
        val w : f64 = 100.0 + 200.0  // f64 + f64 -> f64
        
        // Mixed integer and float
        val a : f64 = 10 + 20.0  // i32 + f64 -> f64
        val b : f64 = 10.0 + 20  // f64 + i32 -> f64
        
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"


def test_type_coercion():
    """Test type coercion in binary operations."""
    source = """
    func main(): i32 = {
        // Integer to float coercion
        val x : f64 = 10 + 20.0  // i32 -> f64
        val y : f32 = 10 * 2.0   // i32 -> f32
        
        // Float to integer coercion (should fail)
        val z : i32 = 10.0 + 20  // Error: cannot coerce float to integer
        val w : i64 = 10.0 * 2   // Error: cannot coerce float to integer
        
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert len(errors) == 2, f"Expected 2 errors, got {len(errors)}"
    assert all("cannot coerce float to integer" in str(e) for e in errors)


def test_complex_expressions():
    """Test complex expressions with multiple operators."""
    source = """
    func main(): i32 = {
        // Complex integer expressions
        val x : i32 = 10 + 20 * 2 - 5 \\ 2
        val y : i64 = 100 + 200 * 3 - 50 \\ 2
        
        // Complex float expressions
        val z : f64 = 10.0 + 20.0 * 2.0 - 5.0 / 2.0
        val w : f32 = 100.0 + 200.0 * 3.0 - 50.0 / 2.0
        
        // Mixed expressions
        val a : f64 = 10 + 20.0 * 2 - 5.0 / 2
        val b : f64 = 100.0 + 200 * 3 - 50 / 2.0
        
        return 0
    }
    """
    ast, errors = parse_and_check(source)
    assert not errors, f"Unexpected errors: {errors}"
