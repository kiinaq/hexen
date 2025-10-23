"""
Tests for Function Call & Conditional Detection and Runtime Classification

Tests the enhanced block evaluability detection that classifies blocks containing
function calls or conditionals as runtime evaluable.

Covers detection for runtime operations that require explicit type context
(function calls and conditionals).
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer
from src.hexen.semantic.types import BlockEvaluability


class TestRuntimeOperationsInfrastructure:
    """Test that runtime operation detection infrastructure is implemented"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_runtime_operation_detection_methods_exist(self):
        """Test that Runtime Operations runtime operation detection methods are available"""
        block_analyzer = self.analyzer.block_analyzer

        # Runtime Operations: Runtime operation detection infrastructure
        assert hasattr(block_analyzer, "_contains_runtime_operations")
        assert hasattr(block_analyzer, "_contains_function_calls")
        assert hasattr(block_analyzer, "_contains_conditionals")

        # Runtime Operations: Statement-level detection methods
        assert hasattr(block_analyzer, "_statement_contains_function_calls")
        assert hasattr(block_analyzer, "_statement_contains_conditionals")

        # Runtime Operations: Expression-level detection methods
        assert hasattr(block_analyzer, "_expression_contains_function_calls")
        assert hasattr(block_analyzer, "_expression_contains_conditionals")

        # Runtime Operations: Context validation methods (ready for Comptime Preservation)
        assert hasattr(block_analyzer, "_validate_runtime_block_context")
        assert hasattr(block_analyzer, "_get_runtime_operation_reason")


class TestFunctionCallDetection:
    """Test function call detection in expression blocks"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_function_call_in_expression_triggers_runtime(self):
        """Test blocks with function calls analyze correctly (Runtime Operations infrastructure test)"""
        source = """
        func helper() : i32 = {
            return 42
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block
                val computed : i32 = helper()  // Function call should trigger runtime
                -> computed
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []

    def test_nested_function_calls_detected(self):
        """Test nested function calls in expressions are detected"""
        source = """
        func add(a: i32, b: i32) : i32 = {
            return a + b
        }
        
        func multiply(a: i32, b: i32) : i32 = {
            return a * b
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function calls)
                val computed : i32 = add(multiply(2, 3), 4)  // Nested function calls
                -> computed
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []

    def test_function_call_in_binary_operation(self):
        """Test function calls within binary operations are detected"""
        source = """
        func getValue() : i32 = {
            return 10
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function call)
                val computed : i32 = getValue() + 42  // Function call in binary operation
                -> computed
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors (infrastructure doesn't break functionality)
        assert errors == []

    def test_function_call_in_assign_statement(self):
        """Test function calls in -> statements are detected"""
        source = """
        func calculate() : i32 = {
            return 100
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function call)
                val temp = 42
                -> calculate()  // Function call directly in assign
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors (infrastructure doesn't break functionality)
        assert errors == []

    def test_function_call_in_return_statement(self):
        """Test function calls in return statements are detected"""
        source = """
        func helper() : i32 = {
            return 42
        }
        
        func test() : i32 = {
            val result = {
                val temp = 10
                return helper()  // Function call in return (early exit)
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors (infrastructure doesn't break functionality)
        assert errors == []

    def test_function_call_statement_detected(self):
        """Test direct function call statements are detected"""
        source = """
        func doSomething() : void = {
            return
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains function call)
                doSomething()  // Direct function call statement
                -> 42
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors (infrastructure doesn't break functionality)
        assert errors == []


class TestConditionalDetection:
    """Test conditional detection in expression blocks"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_if_statement_triggers_runtime(self):
        """Test blocks with if statements analyze correctly (Runtime Operations infrastructure test)"""
        source = """
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block (contains conditional)
                val input = 5
                if input > 3 {
                    val temp = 100
                }
                -> input * 2
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors (infrastructure doesn't break functionality)
        assert errors == []

    def test_if_else_chain_detected(self):
        """Test if-else chains are detected"""
        source = """
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block with conditionals
                val input = 5
                if input > 10 {
                    val high = 100
                } else if input > 5 {
                    val medium = 50
                } else {
                    val low = 10
                }
                -> input
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []

    def test_nested_conditionals_detected(self):
        """Test nested conditionals are detected"""
        source = """
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block with conditionals
                val x = 5
                val y = 3
                if x > 0 {
                    if y > 0 {
                        val both_positive = true
                    }
                }
                -> x + y
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []


class TestCombinedRuntimeOperations:
    """Test blocks with both function calls and conditionals"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_function_calls_and_conditionals_together(self):
        """Test blocks with both function calls and conditionals analyze correctly"""
        source = """
        func getValue() : i32 = {
            return 42
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block
                val input : i32 = getValue()  // Function call
                if input > 20 {         // Conditional
                    val adjusted = input * 2
                } else {
                    val adjusted = input
                }
                -> input
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []

    def test_function_call_in_conditional_condition(self):
        """Test function calls within conditional conditions are detected"""
        source = """
        func shouldProcess() : bool = {
            return true
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block
                val input = 42
                if shouldProcess() {  // Function call in condition
                    val processed = input * 2
                }
                -> input
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []

    def test_complex_runtime_operation_combinations(self):
        """Test complex combinations of runtime operations"""
        source = """
        func calculate(x: i32) : i32 = {
            return x * 2
        }
        
        func validate(x: i32) : bool = {
            return x > 0
        }
        
        func test() : i32 = {
            val concrete_input : i32 = 10  // Concrete variable
            val result : i32 = {  // Explicit type required for runtime block
                val computed : i32 = calculate(concrete_input)  // Function call with concrete arg
                if validate(computed) {                    // Function call in condition
                    val final_result = computed + concrete_input  // Uses concrete variable
                } else {
                    val final_result = 0
                }
                -> computed
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []


class TestRuntimeOperationValidation:
    """Test the runtime operation validation infrastructure"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_validation_methods_work_without_errors(self):
        """Test that validation methods can be called without breaking analysis"""
        source = """
        func helper() : i32 = {
            return 42
        }
        
        func test() : i32 = {
            val result : i32 = {  // Explicit type required for runtime block
                val computed : i32 = helper()
                if computed > 20 {
                    val adjusted = computed * 2
                }
                -> computed
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: Should analyze without errors with explicit type annotation
        assert errors == []

        # Test that validation infrastructure exists and can be used
        block_analyzer = self.analyzer.block_analyzer

        # Test validation method with empty statements (safe for Runtime Operations)
        validation_result = block_analyzer._validate_runtime_block_context(
            [], BlockEvaluability.COMPILE_TIME
        )
        assert validation_result is None  # Compile-time blocks don't need validation

        # Test reason method with empty statements (safe for Runtime Operations)
        reason = block_analyzer._get_runtime_operation_reason([])
        assert isinstance(reason, str)  # Should return a string


class TestRuntimeOperationsFoundationComplete:
    """Test that Runtime Operations foundation is complete and ready for Comptime Preservation"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_session2_infrastructure_ready_for_session3(self):
        """Test that Runtime Operations infrastructure is complete and ready for Comptime Preservation"""
        block_analyzer = self.analyzer.block_analyzer

        # Evaluability Infrastructure infrastructure still exists
        assert hasattr(block_analyzer, "_classify_block_evaluability")
        assert hasattr(block_analyzer, "_has_comptime_only_operations")
        assert hasattr(block_analyzer, "_has_runtime_variables")

        # Runtime Operations infrastructure is complete
        assert hasattr(block_analyzer, "_contains_runtime_operations")
        assert hasattr(block_analyzer, "_contains_function_calls")
        assert hasattr(block_analyzer, "_contains_conditionals")
        assert hasattr(block_analyzer, "_statement_contains_function_calls")
        assert hasattr(block_analyzer, "_statement_contains_conditionals")
        assert hasattr(block_analyzer, "_expression_contains_function_calls")
        assert hasattr(block_analyzer, "_expression_contains_conditionals")

        # Runtime Operations validation infrastructure ready for Comptime Preservation
        assert hasattr(block_analyzer, "_validate_runtime_block_context")
        assert hasattr(block_analyzer, "_get_runtime_operation_reason")

        # BlockEvaluability enum ready
        assert BlockEvaluability.COMPILE_TIME
        assert BlockEvaluability.RUNTIME

    def test_no_regressions_from_session2_changes(self):
        """Verify that Runtime Operations doesn't break any existing functionality"""
        # Test that complex Evaluability Infrastructure functionality still works with Runtime Operations enhancements
        source = """
        func test() : i32 = {
            val comptime_only : i32 = {  // Explicit type required for ALL expression blocks
                val a = 42          // comptime_int
                val b = 100         // comptime_int
                val c = a * b       // comptime operation
                -> c            // Adapts to i32
            }

            val concrete_mixed : i32 = {  // Explicit type required for runtime block (concrete variables)
                val explicit : i32 = 42    // Concrete type
                val doubled = explicit * 2  // Mixed operation
                -> doubled
            }

            return comptime_only + concrete_mixed  // i32 + i32 -> i32
        }
        """

        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)

        # Runtime Operations: All Evaluability Infrastructure functionality should continue working
        assert errors == []
