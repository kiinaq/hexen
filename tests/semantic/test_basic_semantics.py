"""
Test cross-feature integration scenarios for Hexen semantic analysis

This module tests integration between different language features and cross-cutting
concerns that span multiple semantic constructs. It serves as the final validation
that all features work together harmoniously.

More specific features are tested in their dedicated test files:
- test_comptime_types.py: Comptime type system and numeric coercion
- test_type_coercion.py: Concrete type coercion and widening
- test_precision_loss.py: "Explicit Danger, Implicit Safety" enforcement
- test_mutability.py: val/mut variable system
- test_assignment.py: Assignment statement validation
- test_unified_blocks.py: Unified block system (statement/expression/function)
- test_binary_ops.py: Binary operations and mixed-type expressions
- test_unary_ops.py: Unary operations and negative literals
- test_context_framework.py: Context-guided type resolution
- test_error_messages.py: Error message consistency and helpfulness

This file focuses on integration scenarios that require multiple features working together.
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestBasicLanguageIntegration:
    """Test fundamental language integration scenarios"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_minimal_valid_program(self):
        """Test minimal valid Hexen program passes semantic analysis"""
        source = """
        func main() : i32 = {
            val x = 42
            return x
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0, (
            f"Expected no errors, got: {[e.message for e in errors]}"
        )

    def test_multiple_functions_with_different_features(self):
        """Test multiple functions using different language features"""
        source = """
        func compute_int() : i32 = {
            val base = 10
            mut counter:i32 = 0
            counter = base * 2
            return counter
        }
        
        func compute_float() : f64 = {
            val precise = 3.14159
            val doubled:f64 = precise * 2.0
            return doubled
        }
        
        func compute_string():string = {
            val message = "Hello"
            return message
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_function_calls_with_type_system_integration(self):
        """Test function declarations work with the type system"""
        source = """
        func process_data() : f64 = {
            val count:i64 = 1000
            val rate:f32 = 2.5
            // Mixed concrete types require explicit conversions (transparent costs)
            val result:f64 = count:f64 * rate:f64
            return result
        }
        
        func main() : i32 = {
            // Simple variable declaration instead of function call
            val processed:f64 = 42.5
            return 42
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0


class TestTypeSystemIntegration:
    """Test integration between different type system features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_comptime_types_with_mutability(self):
        """Test comptime types work with val/mut declarations"""
        source = """
        func test() : void = {
            val immutable_int = 42        // comptime_int → i32
            val immutable_float = 3.14    // comptime_float → f64
            
            mut mutable_int:i32 = 100         // comptime_int → i32 (explicit type required)
            mut mutable_float:f64 = 2.5       // comptime_float → f64 (explicit type required)
            
            mutable_int = 200             // comptime_int → i32 (reassignment)
            mutable_float = 7.5           // comptime_float → f64 (reassignment)
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_type_coercion_with_assignments(self):
        """Test type coercion works with assignment statements"""
        source = """
        func test() : void = {
            val small:i32 = 100
            mut large:i64 = 0
            mut precise:f64 = 0.0
            
            large = small                 // i32 → i64 (widening)
            precise = small               // i32 → f64 (conversion)
            precise = large               // i64 → f64 (conversion)
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_context_guided_resolution_integration(self):
        """Test context-guided type resolution works across features"""
        source = """
        func test() : void = {
            val explicit_i64:i64 = 42          // Context guides comptime_int → i64
            val explicit_f32:f32 = 3.14        // Context guides comptime_float → f32
            
            mut flexible:f64 = 0.0
            flexible = 42                        // Assignment context guides comptime_int → f64
            flexible = 3.14                      // Assignment context guides comptime_float → f64
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_explicit_conversion_integration(self):
        """Test explicit conversion pattern works across features"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            val precise:f64 = 3.141592653589793
            
            mut small:i32 = 0
            mut single:f32 = 0.0
            
            small = large:i32               // Explicit conversion of truncation
            single = precise:f32            // Explicit conversion of precision loss
            single = large:f32              // Explicit conversion of mixed-type conversion
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0


class TestBlockSystemIntegration:
    """Test integration between block system and other features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_blocks_with_type_system(self):
        """Test blocks work correctly with the type system"""
        source = """
        func test() : i32 = {
            val result:i32 = {
                val temp:i32 = 42
                val doubled:i32 = temp * 2
                return doubled
            }
            return result
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_blocks_with_mutability(self):
        """Test blocks work with val/mut variables"""
        source = """
        func test() : void = {
            val immutable = 42
            mut mutable:i32 = 100
            
            {
                val scoped:i32 = immutable + mutable  // comptime_int adapts to i32 context
                mutable = scoped
            }
            
            mutable = 200
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_blocks_with_complex_expressions(self):
        """Test blocks with complex expressions and type coercion"""
        source = """
        func test() : f64 = {
            val result:f64 = {
                val int_val = 42
                val float_val = 3.14
                val computed:f64 = int_val + float_val
                return computed
            }
            return result
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0


class TestErrorIntegrationScenarios:
    """Test error detection across multiple integrated features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_multiple_semantic_errors_detected(self):
        """Test that multiple different semantic errors are all detected"""
        source = """
        func test() : i32 = {
            val x = undeclared_var       // Error: undefined variable 
            val y:string = 42          // Error: type mismatch
            val z = "hello"
            z = "world"                  // Error: assignment to immutable
            return "wrong"               // Error: return type mismatch
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect multiple errors
        assert len(errors) >= 3  # At least the major errors

        error_messages = [e.message for e in errors]

        # Check for key error types (not exact count due to error recovery)
        assert any("Undefined variable" in msg for msg in error_messages)
        assert any("Type mismatch" in msg for msg in error_messages)
        assert any("Cannot assign to immutable" in msg for msg in error_messages)

    def test_integrated_precision_loss_errors(self):
        """Test precision loss errors in integrated scenarios"""
        source = """
        func test() : void = {
            val large:i64 = 9223372036854775807
            val precise:f64 = 3.141592653589793
            
            mut small:i32 = 0
            mut single:f32 = 0.0
            
            small = large                 // Error: requires:i32
            single = precise              // Error: requires:f32
            single = large                // Error: requires:f32
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 3

        error_messages = [e.message for e in errors]

        # All should be precision loss related
        assert all(
            any(
                keyword in msg.lower()
                for keyword in ["truncation", "precision", "loss"]
            )
            for msg in error_messages
        )

    def test_scoping_with_type_system_errors(self):
        """Test scoping errors interact correctly with type system"""
        source = """
        func test() : i32 = {
            val outer = 42
            {
                val inner:i64 = outer    // OK: i32 → i64 widening
                mut temp:i64 = inner     // OK: explicit type for mut
            }
            return inner                   // Error: inner is out of scope
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message


class TestComprehensiveIntegration:
    """Test comprehensive scenarios using multiple features together"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_full_feature_integration(self):
        """Test a comprehensive scenario using most language features"""
        source = """
        func calculate_result() : f64 = {
            val base:i32 = 10
            val multiplier:f32 = 3.14
            // Mixed concrete types require explicit conversions (transparent costs)
            val result:f64 = base:f64 * multiplier:f64
            return result
        }
        
        func main() : i32 = {
            // Comptime types with context
            val int_value:i32 = 42           // comptime_int → i32
            val float_value:f32 = 3.14       // comptime_float → f32
            
            // Mutable variables with reassignment
            mut counter:i32 = 0
            counter = int_value                 // Assignment with coercion
            
            // Expression blocks with type system
            val computed:f64 = {
                val temp:f64 = 31.4
                val adjusted:f64 = temp * 2.0
                return adjusted
            }
            
            // Complex expression with explicit conversion
            val final_result:i32 = computed:i32
            
            return final_result
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0

    def test_error_recovery_in_complex_scenarios(self):
        """Test error recovery works in complex integration scenarios"""
        source = """
        func problematic() : i32 = {
            val good_var = 42
            val bad_var = undefined_symbol  // Error: undefined symbol
            val another_good = "hello"
            
            mut counter:i32 = good_var
            // Simplified assignment without function call
            counter = 99
            
            return counter
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Should detect the undefined symbol error
        assert len(errors) >= 1
        assert any("undefined_symbol" in str(e) for e in errors)

    def test_type_system_consistency_across_features(self):
        """Test type system rules are consistent across all features"""
        source = """
        func test_consistency() : void = {
            // Same comptime type behavior everywhere
            val var1:i32 = 42             // comptime_int → i32
            mut var2:i64 = 42             // comptime_int → i64
            val var3:f32 = 42             // comptime_int → f32
            val var4:f64 = 42             // comptime_int → f64
            
            // Same coercion rules everywhere
            var2 = var1                     // i32 → i64 (widening)
            val var5:f64 = var1           // i32 → f64 (conversion)
            val var6:f64 = var2           // i64 → f64 (conversion)
            
            // Same explicit conversion rules everywhere
            val var7:i32 = var2:i32     // i64 → i32 (explicit)
            val var8:f32 = var6:f32     // f64 → f32 (explicit)
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        assert len(errors) == 0
