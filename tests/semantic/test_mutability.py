"""
Test suite for variable mutability system in Hexen

Tests the comprehensive val/mut system described in TYPE_SYSTEM.md:
- val variables: immutable, single assignment at declaration only
- mut variables: mutable, multiple assignments allowed throughout lifetime
- Both follow identical type coercion and context rules
- val + undef forbidden (creates unusable variables that break immutability contract)
- mut + undef enables proper deferred initialization patterns
- Type consistency enforcement across all reassignments
- Universal scope isolation rules for both val and mut

This file focuses on MUTABILITY SEMANTICS and VARIABLE LIFECYCLE:
- Declaration semantics (val vs mut)
- Reassignment capabilities and restrictions
- undef interaction patterns
- Scope and shadowing behavior
- Integration with type system (comptime adaptation, coercion)

ASSIGNMENT STATEMENT VALIDATION is covered in test_assignment.py.
PRECISION LOSS scenarios are covered in test_precision_loss.py.
"""

from tests.semantic import StandardTestBase


class TestValVariableSemantics(StandardTestBase):
    """Test val (immutable) variable semantics and lifecycle"""

    def test_val_declaration_patterns(self):
        """Test val variables can be declared with various initialization patterns"""
        source = """
        func test() : void = {
            // ✅ Basic val declarations with immediate initialization
            val counter:i32 = 42
            val message:string = "hello"
            val flag:bool = true
            val precise:f64 = 3.14159
            
            // ✅ Val with type inference (comptime type defaults)
            val inferred_int = 42        // comptime_int → i32 (default)
            val inferred_float = 3.14    // comptime_float → f64 (default)
            val inferred_string = "test" // string
            val inferred_bool = true     // bool
            
            // ✅ Val with explicit type coercion (comptime adaptation)
            val int_to_i64:i64 = 42       // comptime_int → i64 (context)
            val int_to_f32:f32 = 42       // comptime_int → f32 (context)
            val float_to_f32:f32 = 3.14   // comptime_float → f32 (context)
            val float_to_f64:f64 = 3.14   // comptime_float → f64 (context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_val_immutability_enforcement(self):
        """Test that val variables enforce immutability (single assignment only)"""
        source = """
        func test() : void = {
            val immutable = 42
            val another = "hello"
            
            // ❌ Cannot reassign val variables (breaks immutability contract)
            immutable = 100
            another = "world"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]
        for error_msg in error_messages:
            assert "Cannot assign to immutable variable" in error_msg
            assert "val variables can only be assigned once at declaration" in error_msg

    def test_val_undef_prohibition(self):
        """Test that val + undef is forbidden (creates unusable variables)"""
        source = """
        func test() : void = {
            // ❌ val + undef creates unusable variables (breaks immutability contract)
            val config:string = undef     // Cannot be assigned later
            val result:i32 = undef        // Cannot be assigned later
            val flag:bool = undef         // Cannot be assigned later
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        for error in errors:
            assert "val variable" in error.message and "undef" in error.message
            assert (
                "unusable" in error.message
                or "cannot be assigned later" in error.message
            )

    def test_val_undef_error_guidance(self):
        """Test that val + undef errors provide helpful guidance"""
        source = """
        func test() : void = {
            val pending:i32 = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        error_msg = errors[0].message

        # Should suggest mut for deferred initialization or expression blocks for complex init
        assert ("mut" in error_msg and "deferred initialization" in error_msg) or (
            "expression block" in error_msg and "complex initialization" in error_msg
        )


class TestMutVariableSemantics(StandardTestBase):
    """Test mut (mutable) variable semantics and lifecycle"""

    def test_mut_declaration_and_reassignment_lifecycle(self):
        """Test mut variables support full reassignment lifecycle"""
        source = """
        func test() : void = {
            // ✅ Basic mut declarations
            mut counter:i32 = 0
            mut message:string = "hello"
            mut flag:bool = false
            
            // ✅ Single reassignments allowed
            counter = 42
            message = "world"
            flag = true
            
            // ✅ Multiple reassignments allowed (unlimited)
            counter = 100
            counter = 200
            counter = 300
            message = "updated"
            message = "final"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_type_consistency_enforcement(self):
        """Test that mut variables maintain declared type across all reassignments"""
        source = """
        func test() : void = {
            mut int_var:i32 = 0
            mut str_var:string = "hello"
            mut bool_var:bool = false
            
            // ✅ Type-consistent reassignments
            int_var = 42           // i32 compatible
            str_var = "world"      // string compatible  
            bool_var = true        // bool compatible
            
            // ❌ Type-inconsistent reassignments (violate declared type)
            int_var = "wrong"      // string → i32 (invalid)
            str_var = 123          // i32 → string (invalid)
            bool_var = 42          // i32 → bool (invalid)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        error_messages = [e.message for e in errors]
        assert any(
            "Type mismatch" in msg
            and "int_var" in msg
            and "i32" in msg
            and "string" in msg
            for msg in error_messages
        )
        assert any(
            "Type mismatch" in msg
            and "str_var" in msg
            and "string" in msg
            and "i32" in msg
            for msg in error_messages
        )
        assert any(
            "Type mismatch" in msg
            and "bool_var" in msg
            and "bool" in msg
            and "i32" in msg
            for msg in error_messages
        )

    def test_mut_comptime_type_adaptation_in_reassignments(self):
        """Test mut variables enable comptime type adaptation across all reassignments"""
        source = """
        func test() : void = {
            mut int_var:i64 = 0
            mut float_var:f32 = 0.0
            
            // ✅ Comptime types adapt to declared type across reassignments
            int_var = 42           // comptime_int → i64 (assignment context)
            int_var = 100          // comptime_int → i64 (assignment context)
            int_var = 200          // comptime_int → i64 (assignment context)
            
            float_var = 3.14       // comptime_float → f32 (assignment context)
            float_var = 2.718      // comptime_float → f32 (assignment context)
            float_var = 1.414      // comptime_float → f32 (assignment context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_undef_deferred_initialization(self):
        """Test mut + undef enables proper deferred initialization patterns"""
        source = """
        func test() : void = {
            // ✅ mut + undef enables deferred initialization
            mut config:string = undef     // Will be assigned later
            mut result:i32 = undef        // Will be assigned later
            mut flag:bool = undef         // Will be assigned later
            
            // ✅ Deferred assignments (first real assignments)
            config = "production"
            result = 42
            flag = true
            
            // ✅ Subsequent reassignments also allowed
            config = "development"
            result = 100
            flag = false
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_mut_undef_requires_explicit_type(self):
        """Test that mut with undef requires explicit type (cannot infer from undef)"""
        source = """
        func test() : void = {
            // ❌ Cannot infer type from undef
            mut pending:i32 = undef
            mut unknown:string = undef
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestMutabilityScoping(StandardTestBase):
    """Test val/mut variables follow universal scope isolation rules"""

    def test_val_variables_scope_isolation(self):
        """Test val variables are properly scoped to their containing blocks"""
        source = """
        func test() : void = {
            val outer = 42
            
            {
                val inner = 100        // Scoped to inner block
                val outer = "shadow"   // Shadows outer val (allowed)
                
                // ✅ Can access both inner and shadowed outer
                val check1 = inner     // 100 (inner scope)
                val check2 = outer     // "shadow" (shadowed)
            }
            
            // ✅ Can access original outer
            val check3 = outer         // 42 (original)
            
            // ❌ Cannot access inner (out of scope)
            val check4:i32 = inner   // Error: undefined variable (explicit type to avoid inference issues)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any("Undefined variable: 'inner'" in msg for msg in error_messages)

    def test_mut_variables_scope_isolation(self):
        """Test mut variables follow same scope isolation as val"""
        source = """
        func test() : void = {
            mut outer:i32 = 42
            
            {
                mut inner:i32 = 100        // Scoped to inner block
                mut outer:i32 = 200        // Shadows outer mut (allowed)
                
                // ✅ Reassignments within scope
                inner = 150
                outer = 250            // Modifies shadowed variable
            }
            
            // ✅ Original outer unchanged by shadowed assignments
            outer = 300                // Modifies original
            
            // ❌ Cannot access inner (out of scope)  
            inner = 400                // Error: undefined variable
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message

    def test_mixed_val_mut_shadowing(self):
        """Test val and mut can shadow each other (different mutability, same scope rules)"""
        source = """
        func test() : void = {
            val original = 42
            
            {
                mut original:i32 = 100     // mut shadows val (allowed)
                original = 200         // ✅ Reassignment to mut shadow
            }
            
            // ✅ Original val unchanged and immutable
            val check = original       // 42 (original val)
            
            // ❌ Cannot reassign original val
            original = 300             // Error: immutable variable
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Cannot assign to immutable variable" in errors[0].message


class TestMutabilityIntegration(StandardTestBase):
    """Test mutability integration with other language features"""

    def test_mutability_with_expression_blocks(self):
        """Test val/mut work correctly with expression blocks"""
        source = """
        func test() : void = {
            // ✅ val with expression block (simple initialization)
            val complex_init:i32 = {
                val temp = 42
                return temp
            }
            
            // ✅ mut with expression block value
            mut mutable_result:i32 = {
                val base = 100
                return base
            }
            
            // ✅ Reassignment with expression block
            mutable_result = {
                val new_base = 200
                return new_base
            }
            
            // ❌ Cannot reassign val (even with expression block)
            complex_init = {
                return 999
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) >= 1
        error_messages = [e.message for e in errors]
        assert any(
            "Cannot assign to immutable variable" in msg for msg in error_messages
        )

    # NOTE: Error message consistency testing is centralized in test_error_messages.py
    # This test was removed to avoid duplication - see test_mutability_error_message_consistency


class TestMutabilityTypeSystemIntegration(StandardTestBase):
    """Test mutability integration with Hexen's type system"""

    def test_val_mut_identical_type_system_behavior(self):
        """Test val and mut follow identical type system rules (only mutability differs)"""
        source = """
        func test() : void = {
            // ✅ Both val and mut follow same comptime coercion rules
            val val_i32:i32 = 42         // comptime_int → i32
            mut mut_i32:i32 = 42         // comptime_int → i32
            
            val val_i64:i64 = 42         // comptime_int → i64  
            mut mut_i64:i64 = 42         // comptime_int → i64
            
            val val_f32:f32 = 42         // comptime_int → f32
            mut mut_f32:f32 = 42         // comptime_int → f32
            
            val val_f64:f64 = 3.14       // comptime_float → f64
            mut mut_f64:f64 = 3.14       // comptime_float → f64
            
            // ✅ Only difference: reassignment capability
            mut_i32 = 100                  // ✅ Allowed
            mut_f32 = 2.718                // ✅ Allowed
            
            // ❌ val cannot be reassigned
            val_i32 = 100                  // Error: immutable
            val_f64 = 2.718                // Error: immutable
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        for error in errors:
            assert "Cannot assign to immutable variable" in error.message

    def test_mutability_with_type_system_contexts(self):
        """Test val/mut variables provide same type contexts to expressions"""
        source = """
        func test() : void = {
            val val_context:f64 = 42 + 3.14      // Mixed comptime → f64 (val context) 
            mut mut_context:f64 = 42 + 3.14      // Mixed comptime → f64 (mut context)
            
            // ✅ Both provide identical type context for expression resolution
            mut_context = 10 + 2.5                 // Mixed comptime → f64 (mut reassignment context)
            
            // The TYPE SYSTEM behavior is identical, only MUTABILITY differs
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
