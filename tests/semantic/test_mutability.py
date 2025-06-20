"""
Test suite for variable mutability system in Hexen

Tests the comprehensive val/mut system described in TYPE_SYSTEM.md:
- val variables: immutable, single assignment at declaration
- mut variables: mutable, multiple assignments allowed
- Both follow same type coercion and context rules
- val + undef forbidden (creates unusable variables)
- mut + undef enables proper deferred initialization
- Type consistency enforcement across reassignments
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestValVariableBasics:
    """Test basic val (immutable) variable functionality"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_val_declaration_with_immediate_initialization(self):
        """Test val variables can be declared with immediate initialization"""
        source = """
        func test() : void = {
            val counter : i32 = 42
            val message : string = "hello"
            val flag : bool = true
            val precise : f64 = 3.14159
            
            // ✅ All valid val declarations
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_val_type_inference(self):
        """Test val variables work with type inference"""
        source = """
        func test() : void = {
            // ✅ Type inference works with val
            val inferred_int = 42        // comptime_int → i32
            val inferred_float = 3.14    // comptime_float → f64
            val inferred_string = "test" // string
            val inferred_bool = true     // bool
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_val_comptime_type_coercion(self):
        """Test val variables follow same comptime type coercion as mut"""
        source = """
        func test() : void = {
            // ✅ Same comptime coercion rules as mut
            val int_to_i64 : i64 = 42       // comptime_int → i64
            val int_to_f32 : f32 = 42       // comptime_int → f32
            val float_to_f32 : f32 = 3.14   // comptime_float → f32
            val float_to_f64 : f64 = 3.14   // comptime_float → f64
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_val_reassignment_forbidden(self):
        """Test that val variables cannot be reassigned"""
        source = """
        func test() : void = {
            val immutable = 42
            
            // ❌ Cannot reassign val variable
            immutable = 100
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Cannot assign to immutable variable 'immutable'" in errors[0].message
        assert (
            "val variables can only be assigned once at declaration"
            in errors[0].message
        )


class TestMutVariableBasics:
    """Test basic mut (mutable) variable functionality"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mut_declaration_and_reassignment(self):
        """Test mut variables can be declared and reassigned"""
        source = """
        func test() : void = {
            mut counter : i32 = 0
            mut message : string = "hello"
            mut flag : bool = false
            
            // ✅ Reassignments allowed
            counter = 42
            message = "world"
            flag = true
            
            // ✅ Multiple reassignments allowed
            counter = 100
            counter = 200
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_type_consistency_enforcement(self):
        """Test that mut variables must maintain their declared type"""
        source = """
        func test() : void = {
            mut counter : i32 = 0
            mut message : string = "hello"
            
            // ✅ Type-consistent reassignments
            counter = 42        // i32 compatible
            message = "world"   // string compatible
            
            // ❌ Type-inconsistent reassignments
            counter = "wrong"   // string to i32 - error
            message = 123       // i32 to string - error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]
        assert any("Type mismatch in assignment" in msg for msg in error_messages)
        assert any(
            "variable 'counter' is i32, but assigned value is string" in msg
            for msg in error_messages
        )
        assert any(
            "variable 'message' is string, but assigned value is i32" in msg
            for msg in error_messages
        )

    def test_mut_comptime_type_coercion_in_reassignment(self):
        """Test mut variables accept comptime type coercion in reassignments"""
        source = """
        func test() : void = {
            mut int_var : i64 = 0
            mut float_var : f32 = 0.0
            
            // ✅ Comptime types adapt to variable's declared type
            int_var = 42        // comptime_int → i64 (assignment context)
            float_var = 3.14    // comptime_float → f32 (assignment context)
            
            // ✅ Multiple reassignments with comptime coercion
            int_var = 100
            int_var = 200
            float_var = 2.718
            float_var = 1.414
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestValWithUndefForbidden:
    """Test that val + undef combinations are forbidden"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_val_undef_declaration_forbidden(self):
        """Test that val variables cannot be declared with undef"""
        source = """
        func test() : void = {
            // ❌ val + undef creates unusable variable
            val config : string = undef
            val result : i32 = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        for error in errors:
            assert (
                "val variable" in error.message
                and "undef" in error.message
                and "unusable" in error.message
            )

    def test_val_undef_rationale_in_error_message(self):
        """Test that error messages explain why val + undef is forbidden"""
        source = """
        func test() : void = {
            val pending : i32 = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "val" in error_msg and "undef" in error_msg
        assert (
            "cannot be assigned later" in error_msg or "unusable variable" in error_msg
        )
        assert "Consider using 'mut'" in error_msg


class TestMutWithUndefDeferred:
    """Test that mut + undef enables proper deferred initialization"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mut_undef_declaration_allowed(self):
        """Test that mut variables can be declared with undef"""
        source = """
        func test() : void = {
            // ✅ mut + undef enables deferred initialization
            mut config : string = undef
            mut result : i32 = undef
            mut flag : bool = undef
            
            // ✅ Later assignments are allowed
            config = "production"
            result = 42
            flag = true
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_undef_requires_explicit_type(self):
        """Test that mut + undef requires explicit type annotation"""
        source = """
        func test() : void = {
            // ❌ undef requires explicit type context
            mut pending = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Cannot infer type" in errors[0].message
        assert "undef" in errors[0].message

    def test_mut_undef_deferred_initialization_patterns(self):
        """Test common deferred initialization patterns with mut + undef"""
        # Note: This test is simplified to avoid IF statement parsing requirements
        # The core mutability logic is tested without conditional branches
        source = """
        func test() : void = {
            mut config : string = undef
            mut counter : i32 = undef
            
            // Deferred initialization (simulating conditional logic)
            config = "development"
            counter = 0
            
            // Alternative path (simulating else branch)
            config = "production"  
            counter = 100
            
            // Later reassignments still work
            counter = counter + 1
            config = config + "_mode"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should have no mutability errors - all operations are valid mut reassignments
        assert errors == []

    def test_use_of_undef_variable_before_initialization(self):
        """Test that using undef variables before initialization is caught"""
        source = """
        func test() : void = {
            mut pending : i32 = undef
            mut other : i32 = 0
            
            // ❌ Using undef variable before initialization
            other = pending  // Error: use of uninitialized variable
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Use of uninitialized variable: 'pending'" in errors[0].message


class TestMutabilityWithTypeCoercion:
    """Test mutability system integration with type coercion rules"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_val_with_precision_loss_acknowledgment(self):
        """Test val variables work with precision loss acknowledgments"""
        source = """
        func test() : void = {
            val large : i64 = 9223372036854775807
            val precise : f64 = 3.141592653589793
            
            // ✅ val variables support precision loss acknowledgment
            val truncated : i32 = large : i32    // Acknowledge truncation
            val reduced : f32 = precise : f32     // Acknowledge precision loss
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_with_precision_loss_acknowledgment_in_reassignment(self):
        """Test mut variables support precision loss acknowledgment in reassignments"""
        source = """
        func test() : void = {
            val large : i64 = 9223372036854775807
            val precise : f64 = 3.141592653589793
            
            mut small : i32 = 0
            mut single : f32 = 0.0
            
            // ✅ mut reassignment supports precision loss acknowledgment
            small = large : i32      // Acknowledge truncation
            single = precise : f32   // Acknowledge precision loss
            
            // ✅ Multiple reassignments with acknowledgment
            small = (large * 2) : i32
            single = (precise + 1.0) : f32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mutability_type_annotation_consistency(self):
        """Test that type annotations must match variable's declared type consistently"""
        source = """
        func test() : void = {
            val large : i64 = 1000
            
            // For val variables
            val val_result : i32 = large : i32     // ✅ Both sides i32
            
            // For mut variables  
            mut mut_result : i32 = 0
            mut_result = large : i32               // ✅ Both sides i32
            
            // ❌ Wrong annotation types
            val bad_val : i32 = large : i64        // Error: annotation doesn't match
            mut bad_mut : i32 = 0
            bad_mut = large : i64                  // Error: annotation doesn't match
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        for error in errors:
            assert "Type annotation must match" in error.message


class TestMutabilityScoping:
    """Test mutability rules work correctly with scoping"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_val_variables_in_nested_scopes(self):
        """Test val variables work correctly in nested scopes"""
        source = """
        func test() : void = {
            val outer : i32 = 42
            
            {
                val inner : string = "hello"
                
                // ✅ Can access outer val variable
                val combined : i32 = outer + 1
                
                {
                    val deep : bool = true
                    
                    // ✅ Can access both outer scopes
                    val result : i32 = outer + 10
                }
                
                // ❌ Cannot reassign val variables
                // outer = 100  // Would be error
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_variables_across_scopes(self):
        """Test mut variables can be modified across scopes"""
        source = """
        func test() : void = {
            mut counter : i32 = 0
            mut message : string = "start"
            
            {
                // ✅ Can modify outer mut variables
                counter = 10
                message = "middle"
                
                {
                    // ✅ Can continue modifying from deeper scopes
                    counter = counter + 5
                    message = message + "_deep"
                }
            }
            
            // ✅ Variables retain modifications
            counter = counter + 100
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_shadowing_mutability_rules(self):
        """Test that variable shadowing respects mutability rules"""
        source = """
        func test() : void = {
            val outer : i32 = 42
            mut mutable : i32 = 0
            
            {
                // ✅ Shadowing creates new variables with own mutability
                val outer : string = "shadow"  // New immutable variable
                mut mutable : string = "shadow" // New mutable variable
                
                // ✅ Shadow variables follow their own mutability rules
                // outer = "changed"          // Would be error - val cannot be reassigned
                mutable = "changed"           // OK - mut can be reassigned
            }
            
            // ✅ Original variables unaffected by shadows
            // outer = 100                   // Would be error - original val
            mutable = 200                    // OK - original mut
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestMutabilityIntegration:
    """Test mutability system integration with other language features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mutability_with_expression_blocks(self):
        """Test mutability rules work in expression blocks"""
        source = """
        func test() : i32 = {
            mut accumulator : i32 = 0
            
            val result : i32 = {
                // ✅ Can modify outer mut variables in expression blocks
                accumulator = 100
                
                val local : i32 = 50
                // accumulator = accumulator + local  // Would be valid
                
                return accumulator + local
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    # COMMENTED OUT: Requires function parameters (Phase 1.1 Parser Extensions)
    # def test_mutability_with_function_parameters(self):
    #     """Test that function parameters are immutable by default"""
    #     source = """
    #     func process(input: i32, config: string) : i32 = {
    #         // ✅ Can read parameters
    #         val doubled = input * 2
    #         val length = config.length()  // Hypothetical string method
    #
    #         // ❌ Cannot modify parameters (they're like val variables)
    #         input = 100       // Error: parameters are immutable
    #         config = "new"    // Error: parameters are immutable
    #
    #         return doubled
    #     }
    #     """
    #     ast = self.parser.parse(source)
    #     errors = self.analyzer.analyze(ast)
    #     # Should have 2 errors for parameter modification attempts
    #     parameter_errors = [
    #         e
    #         for e in errors
    #         if "parameter" in e.message.lower() or "immutable" in e.message.lower()
    #     ]
    #     assert len(parameter_errors) >= 2

    def test_mutability_error_message_consistency(self):
        """Test that mutability error messages are consistent and helpful"""
        source = """
        func test() : void = {
            val immutable = 42
            mut mutable = 0
            
            immutable = 100  // Should give clear error about val reassignment
            mutable = "wrong" // Should give clear error about type mismatch
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        # Check for specific error message patterns
        error_messages = [e.message for e in errors]
        assert any(
            "Cannot assign to immutable variable" in msg for msg in error_messages
        )
        assert any(
            "val variables can only be assigned once" in msg for msg in error_messages
        )
        assert any("Type mismatch in assignment" in msg for msg in error_messages)


class TestComplexMutabilityScenarios:
    """Test complex scenarios combining multiple mutability features"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_mixed_val_mut_declarations(self):
        """Test programs with mixed val and mut declarations"""
        source = """
        func test() : void = {
            // Mixed declarations
            val config : string = "production"
            mut counter : i32 = 0
            val max_count : i32 = 100
            mut message : string = undef
            
            // Various operations
            counter = counter + 1           // ✅ mut reassignment
            message = config + "_active"    // ✅ mut deferred initialization
            
            // Type coercion in mixed context
            val large : i64 = 1000000
            counter = large : i32           // ✅ val source, mut target with acknowledgment
            
            // ❌ Invalid operations
            config = "development"          // Error: val reassignment
            max_count = 200                 // Error: val reassignment
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2  # Two val reassignment errors

        for error in errors:
            assert "Cannot assign to immutable variable" in error.message

    def test_mutability_with_complex_expressions(self):
        """Test mutability rules with complex expressions"""
        source = """
        func test() : void = {
            val base : i32 = 10
            mut accumulator : i64 = 0
            val multiplier : f32 = 2.5
            
            // Complex expressions with mixed mutability
            accumulator = (base * 2) + accumulator        // ✅ Using val and mut
            
            // Precision loss in complex expressions with mut target
            mut result : i32 = 0
            result = (accumulator + multiplier) : i32     // ✅ Complex expression with acknowledgment
            
            // Multiple mut variables in expression
            mut temp1 : i32 = 5
            mut temp2 : i32 = 10
            temp1 = temp2 + temp1                         // ✅ Self-reference in assignment
            temp2 = temp1                                 // ✅ Cross-reference
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
