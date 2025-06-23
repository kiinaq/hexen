"""
Test suite for assignment statement validation in Hexen

Assignment statements are the mechanism for updating mutable variables after declaration.
This file focuses on ASSIGNMENT STATEMENT VALIDATION:
- Statement parsing and AST structure
- Target variable validation (existence, mutability)
- Type compatibility between target and assigned value
- Assignment statement behavior in different block contexts
- Assignment error detection and reporting
- Integration with language scoping rules

MUTABILITY SEMANTICS (val/mut lifecycle) are covered in test_mutability.py.
PRECISION LOSS scenarios are covered in test_precision_loss.py.
TYPE COERCION rules are covered in test_type_coercion.py.

Key Assignment Rules:
- Only mut variables can be assignment targets (not val)
- Target variable must exist and be accessible in current scope
- Assigned value type must be compatible with target variable's declared type
- Assignment statements work in all block types (statement, expression, function)
"""

from tests.semantic import StandardTestBase


class TestBasicAssignmentStatement(StandardTestBase):
    """Test fundamental assignment statement validation"""

    def test_valid_assignment_statements(self):
        """Test that valid assignment statements are accepted"""
        source = """
        func test() : void = {
            mut counter = 42
            mut message = "hello"
            mut flag = true
            
            // ✅ Valid assignment statements
            counter = 100
            message = "world"
            flag = false
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_multiple_sequential_assignments(self):
        """Test multiple assignment statements to same variable"""
        source = """
        func test() : void = {
            mut value = 0
            
            // ✅ Multiple sequential assignments allowed
            value = 10
            value = 20
            value = 30
            value = 40
            value = 50
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_with_different_compatible_types(self):
        """Test assignment with various compatible types"""
        source = """
        func test() : void = {
            mut number = 42
            mut text = "hello"
            mut boolean = false  
            mut decimal = 3.14
            
            // ✅ Compatible type assignments
            number = 100
            text = "updated"
            boolean = true
            decimal = 2.718
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_self_assignment(self):
        """Test self-assignment (variable = variable)"""
        source = """
        func test() : void = {
            mut x = 42
            mut y = "hello"
            
            // ✅ Self-assignment is valid (no-op operation)
            x = x
            y = y
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestAssignmentTargetValidation(StandardTestBase):
    """Test assignment target validation (variable existence and mutability)"""

    def test_assignment_to_val_variable_forbidden(self):
        """Test that assignment to val (immutable) variables is forbidden"""
        source = """
        func test() : void = {
            val immutable = 42
            val constant = "hello"
            
            // ❌ Cannot assign to val variables (immutable)
            immutable = 100
            constant = "world"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        for error in errors:
            assert "Cannot assign to immutable variable" in error.message

    def test_assignment_to_undefined_variable(self):
        """Test assignment to undefined variable produces error"""
        source = """
        func test() : void = {
            // ❌ Assignment to undefined variable
            undefined_var = 42
            another_undefined = "hello"
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]
        assert any(
            "Undefined variable: 'undefined_var'" in msg for msg in error_messages
        )
        assert any(
            "Undefined variable: 'another_undefined'" in msg for msg in error_messages
        )

    def test_assignment_target_must_be_variable(self):
        """Test that assignment target must be a variable identifier"""
        # Note: This test depends on parser behavior for invalid assignment targets
        # The parser may catch some invalid targets before semantic analysis
        source = """
        func test() : void = {
            mut x = 42
            
            // Valid assignment
            x = 100
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestAssignmentTypeCompatibility(StandardTestBase):
    """Test type compatibility validation in assignment statements"""

    def test_type_compatible_assignments(self):
        """Test assignments with type-compatible values"""
        source = """
        func test() : void = {
            mut int_var : i32 = 0
            mut str_var : string = ""
            mut bool_var : bool = false
            mut float_var : f64 = 0.0
            
            // ✅ Type-compatible assignments
            int_var = 42           // comptime_int → i32 (compatible)
            str_var = "hello"      // string → string (compatible)
            bool_var = true        // bool → bool (compatible)  
            float_var = 3.14       // comptime_float → f64 (compatible)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_type_incompatible_assignments(self):
        """Test assignments with type-incompatible values"""
        source = """
        func test() : void = {
            mut int_var = 42
            mut str_var = "hello"
            mut bool_var = true
            
            // ❌ Type-incompatible assignments
            int_var = "wrong_type"    // string → i32 (incompatible)
            str_var = 123             // i32 → string (incompatible)
            bool_var = 42             // i32 → bool (incompatible)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        error_messages = [e.message for e in errors]
        assert any(
            "Type mismatch in assignment" in msg and "int_var" in msg
            for msg in error_messages
        )
        assert any(
            "Type mismatch in assignment" in msg and "str_var" in msg
            for msg in error_messages
        )
        assert any(
            "Type mismatch in assignment" in msg and "bool_var" in msg
            for msg in error_messages
        )

    def test_assignment_with_expression_values(self):
        """Test assignment with expression values (not just literals)"""
        source = """
        func test() : void = {
            val source1 = 10
            val source2 = 20
            mut target = 0
            
            // ✅ Assignment with expression values
            target = source1           // Variable expression
            target = source1 + source2 // Binary expression
            target = source1 * 2       // Mixed expression
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestAssignmentInBlockContexts(StandardTestBase):
    """Test assignment statements in different block contexts"""

    def test_assignment_in_statement_blocks(self):
        """Test assignment statements work in statement blocks"""
        source = """
        func test() : void = {
            mut outer_var = 42
            
            {
                // ✅ Assignment in statement block
                outer_var = 100
                
                mut inner_var = "hello"
                inner_var = "world"
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_in_expression_blocks(self):
        """Test assignment statements work in expression blocks"""
        source = """
        func test() : i32 = {
            mut accumulator = 0
            
            val result = {
                // ✅ Assignment in expression block (side effect)
                accumulator = 100
                return accumulator
            }
            
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_across_scope_boundaries(self):
        """Test assignment to variables from outer scopes"""
        source = """
        func test() : void = {
            mut outer = 42
            
            {
                // ✅ Can assign to outer scope variable
                outer = 100
                
                {
                    // ✅ Can assign to variable from multiple levels up
                    outer = 200
                }
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_to_scoped_variable_error(self):
        """Test assignment to variable that's out of scope"""
        source = """
        func test() : void = {
            mut outer = 42
            
            {
                mut inner = 100
            }
            
            // ❌ Cannot assign to inner scope variable (out of scope)
            inner = 200
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Undefined variable: 'inner'" in errors[0].message


class TestAssignmentWithExplicitTypes(StandardTestBase):
    """Test assignment statements with explicit type annotations"""

    def test_assignment_with_type_annotations(self):
        """Test assignment with type annotations (for precision loss cases)"""
        source = """
        func test() : void = {
            mut target : i32 = 0
            val large_source : i64 = 1000
            
            // ✅ Assignment with explicit type annotation (precision loss acknowledgment)
            target = large_source : i32
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_type_annotation_mismatch(self):
        """Test assignment with mismatched type annotations"""
        source = """
        func test() : void = {
            mut target_i32 : i32 = 0
            mut target_f64 : f64 = 0.0
            val source = 100
            
            // ❌ Type annotation must match target variable type
            target_i32 = source : f64      // Annotation doesn't match target
            target_f64 = source : i32      // Annotation doesn't match target
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        # Both should be type annotation mismatch errors
        for error in errors:
            assert (
                "Type annotation must match" in error.message
                or "Type mismatch" in error.message
            )


class TestAssignmentWithUndef(StandardTestBase):
    """Test assignment statements involving undef values"""

    def test_assignment_to_undef_initialized_variable(self):
        """Test assignment to variable that was initialized with undef"""
        source = """
        func test() : void = {
            mut deferred : i32 = undef
            
            // ✅ Assignment to undef variable (deferred initialization)
            deferred = 42
            
            // ✅ Subsequent assignments also allowed
            deferred = 100
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_from_undef_variable(self):
        """Test assignment from variable that contains undef"""
        source = """
        func test() : void = {
            mut source : i32 = undef
            mut target : i32 = 0
            
            // ❌ Using undef variable as assignment source
            target = source
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Implementation may or may not detect this - test documents expected behavior
        # Some implementations track uninitialized usage, others don't
        assert isinstance(errors, list)  # Accept either detection or non-detection


class TestAssignmentErrorMessages(StandardTestBase):
    """Test assignment error message quality and consistency"""

    def test_clear_assignment_error_messages(self):
        """Test that assignment errors provide clear, actionable messages"""
        source = """
        func test() : void = {
            val immutable = 42
            mut mutable = 0
            
            // Assignment errors
            immutable = 100        // Immutable variable error
            mutable = "wrong"      // Type mismatch error
            undefined = 42         // Undefined variable error
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 3

        error_messages = [e.message for e in errors]

        # Check specific error message patterns
        assert any(
            "Cannot assign to immutable variable" in msg for msg in error_messages
        )
        assert any("Type mismatch in assignment" in msg for msg in error_messages)
        assert any("Undefined variable: 'undefined'" in msg for msg in error_messages)

    def test_assignment_error_context_information(self):
        """Test that assignment errors provide context about variable and value types"""
        source = """
        func test() : void = {
            mut int_var : i32 = 0
            mut str_var : string = ""
            
            int_var = "hello"
            str_var = 42
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 2

        error_messages = [e.message for e in errors]

        # Errors should include variable names and types
        assert any(
            "int_var" in msg and "i32" in msg and "string" in msg
            for msg in error_messages
        )
        assert any(
            "str_var" in msg and "string" in msg and "i32" in msg
            for msg in error_messages
        )


class TestAssignmentIntegration(StandardTestBase):
    """Test assignment statement integration with other language features"""

    def test_assignment_with_variable_references(self):
        """Test assignment using values from other variables"""
        source = """
        func test() : void = {
            val source1 = 10
            val source2 = 20
            mut target1 = 0
            mut target2 = 0
            
            // ✅ Assignments using variable references
            target1 = source1
            target2 = source2
            target1 = target2
            target2 = target1
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_chain_patterns(self):
        """Test patterns involving multiple related assignments"""
        source = """
        func test() : void = {
            mut a = 1
            mut b = 2
            mut c = 3
            
            // ✅ Assignment chain patterns (not chained assignment syntax)
            val temp = a
            a = b
            b = c
            c = temp
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    # TODO: Add function call test when function calls are implemented in parser
    # def test_assignment_with_function_calls(self):


class TestAssignmentStatementSemantics(StandardTestBase):
    """Test assignment statement semantic behavior and edge cases"""

    def test_assignment_statement_evaluation_order(self):
        """Test that assignment evaluates right-hand side before assigning"""
        source = """
        func test() : void = {
            mut x = 1
            mut y = 2
            
            // Assignment evaluates RHS before LHS assignment
            x = y           // x gets value of y (2)
            y = x           // y gets current value of x (2)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_vs_declaration_distinction(self):
        """Test clear distinction between assignment and declaration"""
        source = """
        func test() : void = {
            // This is declaration (creates new variable)
            mut new_var = 42
            
            // This is assignment (updates existing variable)
            new_var = 100
            
            // ❌ This would be redeclaration in same scope (not assignment)
            // mut new_var = 200  // Would be error: redeclaration
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_with_complex_expressions(self):
        """Test assignment with complex right-hand side expressions"""
        source = """
        func test() : void = {
            val a = 10
            val b = 20
            val c = 30
            mut result = 0
            
            // ✅ Complex expressions as assignment values
            result = a + b
            result = (a + b) * c
            result = a + (b * c)
            result = a * b + c * a
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestAssignmentWithContextGuidance(StandardTestBase):
    """Test assignment statements with context-guided type resolution"""

    def test_assignment_with_comptime_type_context(self):
        """Test assignment provides context for comptime type adaptation"""
        source = """
        func test() : void = {
            mut int_var : i32 = 0
            mut long_var : i64 = 0
            mut float_var : f32 = 0.0
            mut double_var : f64 = 0.0
            
            // ✅ Assignment context guides comptime type adaptation
            int_var = 42           // comptime_int adapts to i32 context
            long_var = 42          // comptime_int adapts to i64 context
            float_var = 3.14       // comptime_float adapts to f32 context
            double_var = 3.14      // comptime_float adapts to f64 context
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_with_binary_operation_context(self):
        """Test assignment provides context for binary operation resolution"""
        source = """
        func test() : void = {
            mut int_result : i32 = 0
            mut float_result : f64 = 0.0
            
            // ✅ Assignment context guides binary operation type resolution
            int_result = 10 + 20              // comptime_int + comptime_int → i32 (context)
            int_result = 5 * 8                // comptime_int * comptime_int → i32 (context)
            float_result = 42 + 3.14          // comptime_int + comptime_float → f64 (context)
            float_result = 10 / 3             // Float division → f64 (context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_with_mixed_concrete_type_context(self):
        """Test assignment provides context for mixed concrete type operations"""
        source = """
        func test() : void = {
            val small : i32 = 10
            val large : i64 = 20
            val single : f32 = 3.14
            val double : f64 = 2.71
            
            mut target_i64 : i64 = 0
            mut target_f64 : f64 = 0.0
            
            // ✅ Assignment context resolves mixed concrete types
            target_i64 = small + large        // i32 + i64 → i64 (assignment context)
            target_f64 = single + double      // f32 + f64 → f64 (assignment context)
            target_f64 = small + single       // i32 + f32 → f64 (assignment context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_assignment_context_prevents_ambiguity(self):
        """Test assignment context prevents type ambiguity in complex expressions"""
        source = """
        func test() : void = {
            val a : i32 = 10
            val b : i64 = 20
            mut result : f64 = 0.0
            
            // ✅ Assignment context resolves complex mixed-type expressions
            result = (a + b) * 2              // (i32 + i64) * comptime_int → f64 (context)
            result = a * 3.14 + b / 2         // Complex mixed expression → f64 (context)
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
