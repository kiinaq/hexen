"""
Performance and scalability tests for the function system.

Tests that function analysis scales well with increasing numbers of functions,
parameters, and complex call patterns without significant performance degradation.
"""

import time
from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestFunctionSystemPerformance:
    """Test performance characteristics of function system."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_many_simple_functions_performance(self):
        """Test performance with many simple functions."""
        # Generate code with 50 simple functions
        functions = []
        for i in range(50):
            functions.append(f"""
        func func_{i}(param: i32) : i32 = {{
            return param * {i + 1}
        }}""")

        # Add a main function that calls some of them
        functions.append("""
        func main() : i32 = {
            val result1 : i32 = func_0(10)
            val result2 : i32 = func_25(20)
            val result3 : i32 = func_49(30)
            return result1 + result2 + result3
        }""")

        code = "\n".join(functions)

        # Measure parsing time
        start_time = time.time()
        ast = self.parser.parse(code)
        parse_time = time.time() - start_time

        # Measure semantic analysis time
        start_time = time.time()
        errors = self.analyzer.analyze(ast)
        analysis_time = time.time() - start_time

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Performance assertions (should be fast)
        assert parse_time < 2.0, f"Parsing too slow: {parse_time:.3f}s"
        assert analysis_time < 2.0, f"Analysis too slow: {analysis_time:.3f}s"

        print(
            f"✅ 50 functions: Parse {parse_time:.3f}s, Analysis {analysis_time:.3f}s"
        )

    def test_complex_function_call_chains_performance(self):
        """Test performance with complex function call chains."""
        code = """
        func base_func(x: i32) : i32 = {
            return x + 1
        }

        func level1_func(x: i32) : i32 = {
            return base_func(x) * 2
        }

        func level2_func(x: i32) : i32 = {
            return level1_func(x) + level1_func(x + 1)
        }

        func level3_func(x: i32) : i32 = {
            return level2_func(x) * level2_func(x + 1)
        }

        func level4_func(x: i32) : i32 = {
            return level3_func(x) + level3_func(x + 1) + level3_func(x + 2)
        }

        func complex_chain(x: i32) : i32 = {
            val step1 : i32 = level4_func(x)
            val step2 : i32 = level4_func(step1)
            val step3 : i32 = level4_func(step2)
            val step4 : i32 = level4_func(step3)
            return step4
        }

        func main() : i32 = {
            return complex_chain(42)
        }
        """

        # Measure performance
        start_time = time.time()
        ast = self.parser.parse(code)
        parse_time = time.time() - start_time

        start_time = time.time()
        errors = self.analyzer.analyze(ast)
        analysis_time = time.time() - start_time

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Performance assertions
        assert parse_time < 1.0, f"Complex chains parsing too slow: {parse_time:.3f}s"
        assert analysis_time < 1.0, (
            f"Complex chains analysis too slow: {analysis_time:.3f}s"
        )

        print(
            f"✅ Complex chains: Parse {parse_time:.3f}s, Analysis {analysis_time:.3f}s"
        )

    def test_many_parameters_performance(self):
        """Test performance with functions having many parameters."""
        # Generate function with many parameters
        params = []
        args = []
        for i in range(20):
            params.append(f"param_{i}: i32")
            args.append(str(i))

        param_list = ", ".join(params)
        arg_list = ", ".join(args)

        code = f"""
        func many_params_func({param_list}) : i32 = {{
            return param_0 + param_19
        }}

        func caller() : i32 = {{
            return many_params_func({arg_list})
        }}
        """

        # Measure performance
        start_time = time.time()
        ast = self.parser.parse(code)
        parse_time = time.time() - start_time

        start_time = time.time()
        errors = self.analyzer.analyze(ast)
        analysis_time = time.time() - start_time

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Performance assertions
        assert parse_time < 1.0, f"Many parameters parsing too slow: {parse_time:.3f}s"
        assert analysis_time < 1.0, (
            f"Many parameters analysis too slow: {analysis_time:.3f}s"
        )

        print(
            f"✅ 20 parameters: Parse {parse_time:.3f}s, Analysis {analysis_time:.3f}s"
        )

    def test_nested_expression_blocks_performance(self):
        """Test performance with deeply nested expression blocks in functions."""
        code = """
        func deeply_nested(input: i32) : i32 = {
            val level1 : i32 = {
                val level2 : i32 = {
                    val level3 : i32 = {
                        val level4 : i32 = {
                            val level5 : i32 = {
                                val level6 : i32 = {
                                    val level7 : i32 = {
                                        val level8 : i32 = {
                                            val level9 : i32 = {
                                                val level10 : i32 = {
                                                    -> input * 2
                                                }
                                                -> level10 + 1
                                            }
                                            -> level9 + 2
                                        }
                                        -> level8 + 3
                                    }
                                    -> level7 + 4
                                }
                                -> level6 + 5
                            }
                            -> level5 + 6
                        }
                        -> level4 + 7
                    }
                    -> level3 + 8
                }
                -> level2 + 9
            }
            return level1 + 10
        }
        """

        # Measure performance
        start_time = time.time()
        ast = self.parser.parse(code)
        parse_time = time.time() - start_time

        start_time = time.time()
        errors = self.analyzer.analyze(ast)
        analysis_time = time.time() - start_time

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Performance assertions
        assert parse_time < 1.0, f"Nested blocks parsing too slow: {parse_time:.3f}s"
        assert analysis_time < 1.0, (
            f"Nested blocks analysis too slow: {analysis_time:.3f}s"
        )

        print(
            f"✅ Deeply nested: Parse {parse_time:.3f}s, Analysis {analysis_time:.3f}s"
        )

    def test_mixed_type_scenarios_performance(self):
        """Test performance with many mixed type scenarios."""
        code = """
        func type_mixer(
            i32_val: i32,
            i64_val: i64, 
            f32_val: f32,
            f64_val: f64,
            bool_val: bool,
            string_val: string
        ) : f64 = {
            val step1 : i64 = i32_val:i64 + i64_val
            val step2 : f64 = step1:f64 + f32_val:f64 + f64_val
            return step2
        }

        func conversion_heavy() : f64 = {
            mut accumulator : f64 = 0.0
            
            val result1 : f64 = type_mixer(10, 20, 3.14, 2.718, true, "test")
            val result2 : f64 = type_mixer(30, 40, 1.41, 1.732, false, "demo")
            val result3 : f64 = type_mixer(50, 60, 2.71, 3.141, true, "example")
            val result4 : f64 = type_mixer(70, 80, 1.23, 4.567, false, "sample")
            
            accumulator = result1 + result2
            accumulator = accumulator + result3 + result4
            
            return accumulator
        }
        """

        # Measure performance
        start_time = time.time()
        ast = self.parser.parse(code)
        parse_time = time.time() - start_time

        start_time = time.time()
        errors = self.analyzer.analyze(ast)
        analysis_time = time.time() - start_time

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Performance assertions
        assert parse_time < 1.0, f"Mixed types parsing too slow: {parse_time:.3f}s"
        assert analysis_time < 1.0, (
            f"Mixed types analysis too slow: {analysis_time:.3f}s"
        )

        print(f"✅ Mixed types: Parse {parse_time:.3f}s, Analysis {analysis_time:.3f}s")


class TestMemoryUsage:
    """Test memory usage characteristics of function system."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_symbol_table_growth_with_many_functions(self):
        """Test that symbol table doesn't grow excessively with many functions."""
        # Generate code with many functions to test symbol table growth
        functions = []
        for i in range(30):
            functions.append(f"""
        func symbol_test_{i}(a: i32, b: i32, c: i32) : i32 = {{
            val local1 : i32 = a + b
            val local2 : i32 = b + c
            val local3 : i32 = a + c
            return local1 + local2 + local3
        }}""")

        code = "\n".join(functions)

        # Parse and analyze
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check symbol table state
        assert len(self.analyzer.symbol_table.functions) == 30

        # Symbol table should be clean (no lingering function context)
        assert self.analyzer.symbol_table.current_function is None
        assert self.analyzer.symbol_table.current_function_signature is None
        assert len(self.analyzer.symbol_table.scopes) == 1  # Only global scope

        print(
            f"✅ Symbol table: {len(self.analyzer.symbol_table.functions)} functions stored"
        )

    def test_scope_cleanup_after_function_analysis(self):
        """Test that scopes are properly cleaned up after function analysis."""
        code = """
        func scope_test(param1: i32, param2: f64) : f64 = {
            val local1 : i32 = param1 * 2
            {
                val nested_local : f64 = param2 * 3.14
                mut nested_mut : f64 = 0.0
                nested_mut = nested_local + local1:f64
            }
            val local2 : f64 = param2 / 2.0
            return local2
        }
        """

        # Parse and analyze
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Verify scope cleanup
        assert len(self.analyzer.symbol_table.scopes) == 1  # Only global scope remains
        assert self.analyzer.symbol_table.current_function is None
        assert self.analyzer.symbol_table.current_function_signature is None

        print("✅ Scope cleanup: All function scopes properly cleaned up")


class TestScalabilityLimits:
    """Test scalability limits of function system."""

    def setup_method(self):
        """Set up fresh parser and analyzer for each test."""
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_reasonable_scalability_100_functions(self):
        """Test that system handles 100 functions reasonably well."""
        # Generate 100 functions with moderate complexity
        functions = []
        for i in range(100):
            functions.append(f"""
        func scale_test_{i}(x: i32, y: f64) : f64 = {{
            val intermediate : f64 = x:f64 * y
            return intermediate + {i}.0
        }}""")

        # Add main function that calls some of them
        functions.append("""
        func main() : f64 = {
            val r1 : f64 = scale_test_0(10, 2.0)
            val r2 : f64 = scale_test_50(20, 3.0)
            val r3 : f64 = scale_test_99(30, 4.0)
            return r1 + r2 + r3
        }""")

        code = "\n".join(functions)

        # Measure total time
        start_time = time.time()
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        total_time = time.time() - start_time

        # Verify correctness
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Performance should be reasonable
        assert total_time < 5.0, f"100 functions too slow: {total_time:.3f}s"

        print(f"✅ 100 functions: Total time {total_time:.3f}s")

    def test_stress_test_recursive_calls(self):
        """Test recursive function calls don't cause excessive overhead."""
        code = """
        func factorial_test(n: i32) : i32 = {
            return n * factorial_test(n - 1)
        }

        func fibonacci_test(n: i32) : i32 = {
            return fibonacci_test(n - 1) + fibonacci_test(n - 2)
        }

        func simple_recursive(n: i32) : i32 = {
            return n + simple_recursive(n - 1)
        }

        func test_all_recursive() : i32 = {
            val f : i32 = factorial_test(5)
            val fib : i32 = fibonacci_test(6)
            val simple : i32 = simple_recursive(3)
            return f + fib + simple
        }
        """

        # Measure performance
        start_time = time.time()
        ast = self.parser.parse(code)
        errors = self.analyzer.analyze(ast)
        total_time = time.time() - start_time

        # Verify correctness (recursive calls should be allowed syntactically)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Should not cause excessive overhead during analysis
        assert total_time < 1.0, f"Recursive analysis too slow: {total_time:.3f}s"

        print(f"✅ Recursive functions: Total time {total_time:.3f}s")
