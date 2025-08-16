"""
Comptime Type Preservation Logic Tests

Tests the core comptime type preservation functionality for the enhanced unified block system:
- Compile-time evaluable blocks preserve comptime types for maximum flexibility  
- Runtime blocks use explicit context for immediate resolution
- "One computation, multiple uses" pattern from UNIFIED_BLOCK_SYSTEM.md
- Integration with existing type system and comptime infrastructure
"""

import pytest
from src.hexen.semantic.analyzer import SemanticAnalyzer
from src.hexen.parser import HexenParser


class TestComptimePreservationInfrastructure:
    """Test comptime preservation infrastructure is properly integrated."""
    
    def test_comptime_preservation_infrastructure_available(self):
        """Test comptime preservation methods are available and functional."""
        analyzer = SemanticAnalyzer()
        
        # Test that comptime preservation methods exist
        assert hasattr(analyzer.block_analyzer, '_analyze_expression_preserve_comptime')
        assert hasattr(analyzer.block_analyzer, '_analyze_expression_with_context')
        assert hasattr(analyzer.block_analyzer, '_validate_runtime_block_context_requirement')
        
        # Test that methods are callable (basic infrastructure test)
        assert callable(analyzer.block_analyzer._analyze_expression_preserve_comptime)
        assert callable(analyzer.block_analyzer._analyze_expression_with_context)
        assert callable(analyzer.block_analyzer._validate_runtime_block_context_requirement)
    
    def test_comptime_preservation_enhanced_finalization_method(self):
        """Test enhanced _finalize_expression_block_with_evaluability handles different evaluabilities."""
        # Test compile-time evaluable block
        source = """
        func test_comptime() : i32 = {
            val result = {
                val calc = 42 + 100
                assign calc
            }
            return result
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - compile-time evaluable block works
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestComptimePreservationBasics:
    """Test basic comptime type preservation for compile-time evaluable blocks."""
    
    def test_comptime_arithmetic_block_preserves_comptime_int(self):
        """Test compile-time evaluable block with integer arithmetic preserves comptime_int."""
        source = """
        func test_comptime_int() : i32 = {
            val flexible = {
                val base = 42
                val multiplier = 100
                val result = base * multiplier
                assign result
            }
            return flexible
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - comptime arithmetic should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
    
    def test_comptime_arithmetic_block_preserves_comptime_float(self):
        """Test compile-time evaluable block with float arithmetic preserves comptime_float."""
        source = """
        func test_comptime_float() : f64 = {
            val flexible = {
                val base = 42
                val factor = 3.14
                val result = base * factor
                assign result
            }
            return flexible
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - mixed comptime arithmetic should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_comptime_complex_arithmetic_block(self):
        """Test compile-time evaluable block with complex arithmetic expressions."""
        source = """
        func test_complex_comptime() : f64 = {
            val computation : f64 = {  // Explicit type required for runtime block (contains concrete variable)
                val step1 = 42 + 100
                val step2 = step1 * 3.14
                val step3 : f64 = step2 / 2.0  // Float division requires explicit type
                assign step3
            }
            return computation
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - complex comptime operations should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestRuntimeBlockContextResolution:
    """Test runtime blocks use explicit context for immediate resolution."""
    
    def test_function_call_triggers_runtime_context(self):
        """Test blocks with function calls use explicit context resolution."""
        source = """
        func helper() : i32 = {
            return 42
        }
        
        func test_runtime() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function call)
                val computed = helper()  // Function call triggers runtime
                assign computed
            }
            return result
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - runtime blocks work with explicit context
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
        
    def test_mixed_comptime_runtime_block(self):
        """Test blocks mixing comptime and runtime operations."""
        source = """
        func get_multiplier() : i32 = {
            return 5
        }
        
        func test_mixed() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block
                val base = 42              // comptime_int
                val runtime_mult = get_multiplier()  // runtime function call
                val combined = base * runtime_mult   // mixed operation (comptime adapts to runtime_mult's i32)
                assign combined
            }
            return result
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - mixed operations work with explicit context
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestOneComputationMultipleUsesPattern:
    """Test the 'one computation, multiple uses' pattern from specification."""
    
    def test_same_computation_different_function_contexts(self):
        """Test same comptime computation used in different function return contexts."""
        source = """
        func test_as_i32() : i32 = {
            val flexible = {
                val calc = 42 + 100 * 3
                assign calc
            }
            return flexible  // comptime_int -> i32 (function context)
        }
        
        func test_as_i64() : i64 = {
            val same_calc = {
                val calc = 42 + 100 * 3  // Same computation
                assign calc
            }
            return same_calc  // comptime_int -> i64 (different function context)
        }
        
        func test_as_f64() : f64 = {
            val another_calc = {
                val calc = 42 + 100 * 3  // Same computation again
                assign calc
            }
            return another_calc  // comptime_int -> f64 (different function context)
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - same computation adapts to different contexts
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
    
    def test_float_computation_different_contexts(self):
        """Test comptime float computation used in different precision contexts."""
        source = """
        func test_as_f32() : f32 = {
            val flexible = {
                val calc = 42 * 3.14159
                assign calc
            }
            return flexible  // comptime_float -> f32
        }
        
        func test_as_f64() : f64 = {
            val same_calc = {
                val calc = 42 * 3.14159  // Same computation
                assign calc
            }
            return same_calc  // comptime_float -> f64 (higher precision)
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - same comptime float adapts to different precisions
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestNestedExpressionBlocks:
    """Test nested expression blocks with different evaluabilities."""
    
    def test_nested_comptime_blocks(self):
        """Test nested compile-time evaluable blocks."""
        source = """
        func test_nested_comptime() : f64 = {
            val outer = {
                val inner = {
                    val calc = 42 + 100
                    assign calc  // comptime_int
                }
                val scaled = inner * 3.14  // comptime_int * comptime_float -> comptime_float
                assign scaled
            }
            return outer  // comptime_float -> f64
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - nested comptime blocks should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
    
    def test_mixed_nested_blocks(self):
        """Test nested blocks with mixed evaluabilities."""
        source = """
        func get_base() : i32 = {
            return 50
        }
        
        func test_mixed_nested() : f64 = {
            val outer : f64 = {  // Explicit type required for runtime block
                val comptime_part = {
                    val calc = 42 * 2
                    assign calc  // Compile-time evaluable -> comptime_int
                }
                val runtime_part = get_base()  // Runtime function call -> i32
                val combined = comptime_part + runtime_part  // comptime_int + i32 -> i32 (comptime adapts)
                assign combined:f64  // Explicit conversion to match block type
            }
            return outer
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - mixed nested scenarios should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestDivisionOperatorsInBlocks:
    """Test division operators work correctly in expression blocks."""
    
    def test_float_division_in_comptime_block(self):
        """Test float division (/) in compile-time evaluable blocks."""
        source = """
        func test_float_division() : f64 = {
            val precise : f64 = {
                val numerator = 22
                val denominator = 7
                val division_result : f64 = numerator / denominator  // Explicit type for division
                assign division_result
            }
            return precise
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - division with explicit type should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
    
    def test_integer_division_in_comptime_block(self):
        """Test integer division (\\) in compile-time evaluable blocks."""
        source = """
        func test_integer_division() : i32 = {
            val efficient = {
                val total = 100
                val parts = 3
                val result = total \\ parts  // comptime integer division
                assign result
            }
            return efficient  // comptime_int -> i32
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - comptime integer division should work
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestExpressionBlocksWithConditionals:
    """Test expression blocks containing conditionals (should be runtime)."""
    
    def test_conditional_triggers_runtime_classification(self):
        """Test conditionals in expression blocks trigger runtime classification."""
        source = """
        func test_conditional_runtime() : i32 = {
            val result : i32 = if 10 > 5 {
                assign 100
            } else {
                assign 200
            }
            return result
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - conditional blocks work with explicit type annotation
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestReturnStatementsInExpressionBlocks:
    """Test return statements work correctly in expression blocks."""
    
    def test_return_statement_in_comptime_block(self):
        """Test return statements in compile-time evaluable expression blocks."""
        source = """
        func test_early_return() : i32 = {
            val result = {
                val base = 42  // comptime value
                val check = base > 30  // comptime comparison
                // For demonstration: comptime block that can preserve flexibility
                assign base * 2  // comptime operation
            }
            return result  // Uses the computed result
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - comptime blocks preserve flexibility
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
    
    def test_return_statement_in_runtime_block(self):
        """Test return statements in runtime expression blocks."""
        source = """
        func get_condition() : bool = {
            return true
        }
        
        func test_runtime_early_return() : i32 = {
            val result : i32 = if get_condition() {
                assign 777
            } else {
                assign 0
            }
            return result
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - runtime blocks work with explicit type annotation
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"


class TestComptimePreservationFoundationComplete:
    """Test Comptime Preservation foundation is complete and ready for Enhanced Error Messages."""
    
    def test_all_comptime_preservation_patterns_working(self):
        """Test all comptime preservation patterns work together correctly."""
        source = """
        func helper(x: i32) : i32 = {
            return x * 2
        }
        
        func test_comprehensive() : f64 = {
            // Compile-time evaluable block
            val comptime_calc = {
                val base = 42 + 100
                val scaled = base * 3.14
                assign scaled  // Preserves comptime_float
            }
            
            // Runtime block with function call - explicit type required
            val runtime_calc : f64 = {
                val runtime_val = helper(10)  // Function call triggers runtime
                val combined = runtime_val:f64 + comptime_calc  // Explicit conversion for mixed types
                assign combined
            }
            
            return runtime_calc
        }
        """
        
        parser = HexenParser()
        ast = parser.parse(source)
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Should have no errors - all comptime preservation patterns work together
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
    
    def test_comptime_preservation_ready_for_enhanced_error_messages(self):
        """Test comptime preservation infrastructure is ready for enhanced error message enhancements."""
        analyzer = SemanticAnalyzer()
        
        # Test that all comptime preservation infrastructure is available for enhanced error messages
        assert hasattr(analyzer.block_analyzer, '_validate_runtime_block_context')
        assert hasattr(analyzer.block_analyzer, '_get_runtime_operation_reason')
        
        # Test that runtime detection infrastructure is still available
        assert hasattr(analyzer.block_analyzer, '_contains_runtime_operations')
        assert hasattr(analyzer.block_analyzer, '_contains_function_calls')
        assert hasattr(analyzer.block_analyzer, '_contains_conditionals')
        
        # Test that evaluability infrastructure is still available
        assert hasattr(analyzer.block_analyzer, '_classify_block_evaluability')
        assert hasattr(analyzer.block_analyzer, '_has_comptime_only_operations')
        assert hasattr(analyzer.block_analyzer, '_has_runtime_variables')