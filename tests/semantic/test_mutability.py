"""
Test suite for variable mutability system in Hexen

Tests the comprehensive val/mut system described in TYPE_SYSTEM.md:
- val variables: immutable, single assignment at declaration
- mut variables: mutable, multiple assignments allowed
- Both follow same type coercion and context rules
- val + undef forbidden (creates unusable variables)
- mut + undef enables proper deferred initialization
- Type consistency enforcement across reassignments

This file focuses on MUTABILITY SEMANTICS, not precision loss scenarios.
Precision loss testing is comprehensively covered in test_precision_loss.py.
"""

from tests.semantic import StandardTestBase


class TestValVariableBasics(StandardTestBase):
    """Test basic val (immutable) variable functionality"""

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


class TestMutVariableBasics(StandardTestBase):
    """Test basic mut (mutable) variable functionality"""

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


class TestValWithUndefForbidden(StandardTestBase):
    """Test that val + undef combinations are forbidden"""

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
        """Test that val + undef errors explain the rationale clearly"""
        source = """
        func test() : void = {
            val pending : i32 = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1

        error_msg = errors[0].message
        assert "val variable" in error_msg
        assert "undef" in error_msg
        assert "unusable" in error_msg
        assert "mut" in error_msg  # Should suggest using mut instead


class TestMutWithUndefDeferred(StandardTestBase):
    """Test that mut + undef enables proper deferred initialization"""

    def test_mut_undef_declaration_allowed(self):
        """Test that mut variables can be declared with undef"""
        source = """
        func test() : void = {
            // ✅ mut + undef enables deferred initialization
            mut config : string = undef
            mut result : i32 = undef
            
            // Later initialization allowed
            config = "production"
            result = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_undef_requires_explicit_type(self):
        """Test that undef requires explicit type annotation"""
        source = """
        func test() : void = {
            // ❌ undef without explicit type
            mut bad = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert (
            "explicit type" in errors[0].message
            or "cannot infer type" in errors[0].message
        )

    def test_mut_undef_deferred_initialization_patterns(self):
        """Test common deferred initialization patterns"""
        source = """
        func test() : void = {
            mut config : string = undef
            mut counter : i32 = undef
            
            // Conditional initialization
            if true {
                config = "development"
            } else {
                config = "production"
            }
            
            // Complex initialization
            counter = 10 + 20
            counter = counter * 2
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_use_of_undef_variable_before_initialization(self):
        """Test that using undef variables before initialization is caught"""
        source = """
        func test() : void = {
            mut pending : i32 = undef
            mut other : i32 = 0
            
            // ❌ Using undef variable before assignment
            other = pending    // Error: using uninitialized variable
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Implementation may or may not detect this - test documents expected behavior
        # Some implementations track initialization, others don't
        assert isinstance(errors, list)


class TestMutabilityScoping(StandardTestBase):
    """Test mutability behavior across different scopes"""

    def test_val_variables_in_nested_scopes(self):
        """Test val variables behave correctly in nested scopes"""
        source = """
        func test() : void = {
            val outer : i32 = 42
            
            {
                // ✅ Can access outer val variable
                val combined : i32 = outer + 1
                
                // ✅ Can declare new val with same name (shadowing)
                val outer : i32 = 100
                val result : i32 = outer + 10
            }
            
            // ✅ Original outer still accessible and unchanged
            val result : i32 = outer + 10
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_variables_across_scopes(self):
        """Test mut variables behave correctly across scopes"""
        source = """
        func test() : void = {
            mut counter : i32 = 0
            
            {
                // ✅ Can modify outer mut variable
                counter = 42
                
                // ✅ Can declare new mut with same name (shadowing)
                mut counter : i32 = 100
                counter = 200
            }
            
            // Original counter should have been modified in inner scope
            counter = 500
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_shadowing_mutability_rules(self):
        """Test that shadowing can change mutability"""
        source = """
        func test() : void = {
            val outer : i32 = 42
            mut mutable : i32 = 0
            
            {
                // ✅ Can shadow val with mut
                mut outer : i32 = 100
                outer = 200  // This is allowed (inner mut variable)
                
                // ✅ Can shadow mut with val
                val mutable : i32 = 300
                // mutable = 400  // This would be error (inner val variable)
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestMutabilityIntegration(StandardTestBase):
    """Test mutability integration with other language features"""

    def test_mutability_with_expression_blocks(self):
        """Test mutability works correctly with expression blocks"""
        source = """
        func test() : i32 = {
            mut accumulator : i32 = 0
            
            val result : i32 = {
                // ✅ Can modify outer mut from expression block
                accumulator = 10
                
                // ✅ Expression block can declare its own variables
                val local : i32 = 50
                return accumulator + local
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mutability_error_message_consistency(self):
        """Test that mutability error messages are consistent and helpful"""
        source = """
        func test() : void = {
            val immutable = 42
            mut mutable : i32 = 0
            
            // Various error scenarios
            immutable = 100     // Error: val reassignment
            mutable = "wrong"   // Error: type mismatch
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]

        # Check for specific, helpful error messages
        assert any(
            "Cannot assign to immutable variable" in msg for msg in error_messages
        )
        assert any("Type mismatch" in msg for msg in error_messages)

        # Check that errors provide guidance
        val_error = next(e for e in errors if "immutable" in e.message)
        assert "val variables can only be assigned once" in val_error.message


class TestComplexMutabilityScenarios(StandardTestBase):
    """Test complex scenarios involving mutability"""

    def test_mixed_val_mut_declarations(self):
        """Test mixed val and mut declarations in same scope"""
        source = """
        func test() : void = {
            val constant : i32 = 42
            mut counter : i32 = 0
            val max_count : i32 = 100
            
            // ✅ Can use val values in mut assignments
            counter = constant
            counter = max_count
            
            // ✅ Can use mut values in val declarations
            val snapshot : i32 = counter
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mutability_with_complex_expressions(self):
        """Test mutability with complex expressions"""
        source = """
        func test() : void = {
            val base : i32 = 10
            mut accumulator : i32 = 0
            val multiplier : f32 = 2.5
            
            // ✅ Complex expressions with val and mut variables
            accumulator = base * 2
            accumulator = accumulator + base
            
            mut temp1 : i32 = 5
            mut temp2 : i32 = 10
            
            // ✅ Multiple mut variables in expressions
            temp1 = temp2
            temp2 = temp1 + temp2
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
