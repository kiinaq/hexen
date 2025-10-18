"""
Comprehensive Integration Tests for Enhanced Unified Block System

Tests the complete implementation of Sessions 1-4 including:
- Block evaluability classification (Session 1)
- Function call & conditional runtime detection (Session 2)
- Comptime type preservation & runtime context validation (Session 3)
- Enhanced error messages & validation (Session 4)

This validates that all specification examples from UNIFIED_BLOCK_SYSTEM.md work correctly
and that the enhanced unified block system provides the expected behavior.
"""

import pytest

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from tests.semantic import assert_no_errors


class TestUnifiedBlockSystemIntegration:
    """Comprehensive integration tests for enhanced unified block system."""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_complete_specification_examples(self):
        """Test all examples from UNIFIED_BLOCK_SYSTEM.md work correctly."""
        # Example 1: Compile-time evaluable block preserves comptime types
        source = """
        func test_comptime_preservation() : void = {
            val flexible_computation = {
                val base = 42              // comptime_int
                val multiplier = 100       // comptime_int  
                val factor = 3.14          // comptime_float
                val result = base * multiplier + factor  // All comptime operations → comptime_float
                -> result              // Block result: comptime_float (preserved!)
            }
            
            // Same block result adapts to different contexts (maximum flexibility!)
            val as_f32 : f32 = flexible_computation    // comptime_float → f32 (implicit)
            val as_f64 : f64 = flexible_computation    // SAME source → f64 (different context!)
            val as_i32 : i32 = flexible_computation:i32  // SAME source → i32 (explicit conversion)
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_runtime_blocks_require_explicit_type_annotation(self):
        """Test runtime blocks with mixed concrete types require explicit type annotation."""
        # Runtime block with function call and mixed concrete types should require explicit type annotation
        source = """
        func get_user_input() : i64 = { return 42 }
        
        func test_runtime_type_annotation_required() : void = {
            val runtime_result = {              // Should require explicit type annotation
                val user_input : i64 = get_user_input()     // Function call -> runtime block returns i64
                val base : i32 = 42                   // concrete i32
                -> base + user_input              // Mixed concrete types i32 + i64 should error
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should have error about mixed concrete types requiring explicit conversion
        assert len(errors) >= 1
        error_messages = [str(e) for e in errors]
        assert any("Mixed concrete types" in msg for msg in error_messages), (
            f"Expected mixed concrete types error, got: {error_messages}"
        )

    def test_conditional_runtime_classification(self):
        """Test conditional expressions trigger runtime classification."""
        source = """
        func test_conditional_runtime() : void = {
            val result : i32 = {
                val condition = true
                val value = if condition {
                    -> 42
                } else {
                    -> 100
                }  // Conditional -> runtime
                -> value
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # This should work with explicit type annotation
        assert_no_errors(errors)

    def test_complex_nested_scenarios(self):
        """Test complex nesting with mixed evaluability - should error without explicit type annotation."""
        source = """
        func helper() : i32 = { return 42 }
        
        func test_complex_nesting() : void = {
            // Nested blocks with different evaluability
            val outer_result = {     // Missing explicit type annotation - should error!
                val comptime_block = {
                    val calc = 42 + 100
                    -> calc  // Compile-time evaluable
                }
                
                val runtime_block : i32 = {
                    val helper_result : i32 = helper()  // Function call -> runtime
                    -> helper_result
                }
                
                -> comptime_block + runtime_block  // Mixed types - makes block runtime
            }
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should have error about runtime block requiring explicit type annotation
        assert len(errors) >= 1
        error_messages = [str(e) for e in errors]
        # Check for either runtime type annotation error or mixed concrete types error
        assert any(
            "explicit type annotation" in msg.lower() or "mixed concrete" in msg.lower()
            for msg in error_messages
        ), (
            f"Expected runtime type annotation or mixed concrete types error, got: {error_messages}"
        )

    def test_performance_optimization_patterns(self):
        """Test caching and optimization patterns work correctly."""
        source = """
        func lookup_cache(key: string) : f64 = { return 0.0 }
        func very_expensive_operation(key: string) : f64 = { return 42.0 }
        func save_to_cache(key: string, value: f64) : void = { return }
        func log_cache_miss(key: string) : void = { return }
        
        func expensive_calc(key: string) : f64 = {
            val result : f64 = {
                val cached : f64 = lookup_cache(key)
                if cached != 0.0 {
                    return cached      // Early exit: cache hit
                }

                val computed : f64 = very_expensive_operation(key)
                save_to_cache(key, computed)
                -> computed        // Cache miss: -> computed value
            }

            log_cache_miss(key)        // Only executes on cache miss
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_error_handling_with_guards(self):
        """Test error handling patterns with early returns."""
        source = """
        func get_user_input() : f64 = { return 42.0 }
        func sanitize(input: f64) : f64 = { return input }
        
        func safe_processing() : f64 = {
            val validated_input : f64 = {
                val raw_input : f64 = get_user_input()
                if raw_input < 0.0 {
                    return -1.0        // Early function exit with error
                }
                if raw_input > 1000.0 {
                    return -2.0        // Early function exit with different error
                }
                -> sanitize(raw_input) // Success: assign sanitized input
            }
            return validated_input
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_real_world_usage_scenarios(self):
        """Test realistic usage patterns developers might use."""
        source = """
        func calculate_tax(income: f64) : f64 = { return income * 0.2 }
        func get_deductions() : f64 = { return 1000.0 }
        
        func tax_calculation(income: f64) : f64 = {
            // Mix of comptime and runtime calculations
            val base_calculations = {
                val standard_deduction = 12000.0  // comptime_float
                val rate = 0.22                    // comptime_float
                -> standard_deduction * rate   // comptime calculation
            }
            
            val runtime_calculations : f64 = {
                val user_deductions : f64 = get_deductions()  // Function call -> runtime
                val taxable = income - user_deductions
                -> calculate_tax(taxable)
            }
            
            val final_tax : f64 = runtime_calculations - base_calculations
            return final_tax
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_enhanced_error_message_integration(self):
        """Test enhanced error messages provide actionable guidance in real scenarios."""
        # Test mixed concrete types with enhanced error message
        source = """
        func test_enhanced_errors() : void = {
            val a : i32 = 10
            val b : f64 = 20.0
            val result = a + b  // Should trigger enhanced error message
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) >= 1
        error_message = str(errors[0])
        assert "Mixed concrete types" in error_message
        assert "Transparent costs principle" in error_message
        assert "Use explicit conversion syntax: value:" in error_message


class TestBackwardCompatibilityValidation:
    """Test that enhanced block system maintains backward compatibility."""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_existing_expression_blocks_still_work(self):
        """Test that existing expression block patterns continue to work."""
        source = """
        func test_existing_patterns() : i32 = {
            // Simple expression block
            val simple = {
                val x = 42
                -> x * 2
            }
            
            // Block with explicit type
            val explicit : i32 = {
                val calc = 100 + 200
                -> calc
            }
            
            return simple + explicit
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_existing_statement_blocks_unchanged(self):
        """Test that statement blocks behavior is unchanged."""
        source = """
        func test_statement_blocks() : void = {
            // Statement block with scope isolation
            {
                val scoped = "local variable"
                mut counter : i32 = 0
                counter = counter + 1
            }
            
            // Nested statement blocks
            {
                val outer = 42
                {
                    val inner = outer * 2
                }
            }
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_existing_function_blocks_unchanged(self):
        """Test that function block behavior is unchanged."""
        source = """
        func simple_function(x: i32) : i32 = {
            return x * 2
        }
        
        func void_function() : void = {
            val temp = 42
            return
        }
        
        func complex_function(a: i32, b: i32) : i32 = {
            val sum = a + b
            val product = a * b
            if sum > product {
                return sum
            }
            return product
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestSpecificationComplianceValidation:
    """Test complete compliance with UNIFIED_BLOCK_SYSTEM.md specification."""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_compile_time_vs_runtime_distinction(self):
        """Test the core compile-time vs runtime distinction works correctly."""
        source = """
        func test_distinction() : void = {
            // Compile-time evaluable: only comptime operations
            val comptime_block = {
                val a = 42        // comptime_int
                val b = 3.14      // comptime_float
                -> a + b      // comptime_int + comptime_float → comptime_float
            }
            
            // Same source, different targets (flexibility preserved)
            val as_f32 : f32 = comptime_block
            val as_f64 : f64 = comptime_block
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_function_call_runtime_treatment(self):
        """Test that function calls trigger runtime classification."""
        source = """
        func get_value() : i32 = { return 42 }
        
        func test_function_calls() : void = {
            // Block with function call requires explicit type annotation
            val runtime_block : i32 = {
                val value : i32 = get_value()  // Function call → runtime
                -> value
            }
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_mixed_block_classification(self):
        """Test mixed comptime/runtime operations are classified as runtime."""
        source = """
        func get_runtime_value() : i32 = { return 42 }
        
        func test_mixed_blocks() : void = {
            val mixed_block : i32 = {
                val comptime_val = 42              // comptime_int
                val runtime_val : i32 = get_runtime_value() // Function call → concrete i32
                -> comptime_val + runtime_val   // Mixed: comptime + concrete
            }
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_dual_capability_semantics(self):
        """Test -> + return dual capability in expression blocks."""
        source = """
        func test_dual_capability(condition: bool) : i32 = {
            val result : i32 = {
                if condition {
                    return 42  // Early function exit
                }
                val computation = 100 + 200
                -> computation  // Block value assignment
            }
            
            // This line only executes if condition is false
            return result + 1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)


class TestSessionIntegrationValidation:
    """Test that all Sessions 1-4 work together correctly."""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_session1_infrastructure_integration(self):
        """Test Session 1 block evaluability detection integrates correctly."""
        source = """
        func test_session1() : void = {
            // This should be detected as compile-time evaluable
            val comptime_only = {
                val a = 42
                val b = 100
                -> a + b
            }
            
            val as_different_types_f32 : f32 = comptime_only
            val as_different_types_i64 : i64 = comptime_only
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_session2_runtime_detection_integration(self):
        """Test Session 2 function call and conditional detection integrates correctly."""
        source = """
        func helper() : i32 = { return 42 }
        
        func test_session2() : void = {
            // Function call detection
            val with_function : i32 = {
                val result : i32 = helper()
                -> result
            }
            
            // Conditional detection
            val with_conditional : i32 = {
                val value = if true {
                    -> 42
                } else {
                    -> 100
                }
                -> value
            }
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_session3_comptime_preservation_integration(self):
        """Test Session 3 comptime type preservation integrates correctly."""
        source = """
        func test_session3() : void = {
            val preserved_comptime = {
                val calculation = 42 * 3.14  // comptime_int * comptime_float → comptime_float
                -> calculation            // Preserved as comptime_float
            }
            
            // Multiple uses of same preserved computation
            val use1 : f32 = preserved_comptime
            val use2 : f64 = preserved_comptime
            val use3 : i32 = preserved_comptime:i32  // Explicit conversion
            
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)

    def test_session4_enhanced_errors_integration(self):
        """Test Session 4 enhanced error messages integrate correctly with analysis."""
        # This tests that enhanced errors work but don't break analysis
        source = """
        func test_session4() : void = {
            val valid_block = {
                val computation = 42 + 100
                -> computation
            }
            
            val valid_typed : i32 = valid_block
            return
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert_no_errors(errors)
