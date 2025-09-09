"""
Test module for Function System parsing

Comprehensive testing of function declaration and call parsing implementation.
Tests all function syntax variations before semantic analysis.
"""

import pytest

from src.hexen.ast_nodes import NodeType
from src.hexen.parser import HexenParser


class TestFunctionDeclarations:
    """Test function declaration parsing"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_basic_function_declaration(self):
        """Test basic function with no parameters"""
        source = """
        func simple() : i32 = {
            return 42
        }
        """

        ast = self.parser.parse(source)

        assert ast["type"] == NodeType.PROGRAM.value
        assert len(ast["functions"]) == 1

        func = ast["functions"][0]
        assert func["type"] == NodeType.FUNCTION.value
        assert func["name"] == "simple"
        assert func["parameters"] == []
        assert func["return_type"] == "i32"
        assert func["body"]["type"] == NodeType.BLOCK.value

    def test_function_with_single_parameter(self):
        """Test function with single parameter"""
        source = """
        func process(input: string) : bool = {
            return true
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        assert len(func["parameters"]) == 1
        param = func["parameters"][0]
        assert param["type"] == NodeType.PARAMETER.value
        assert param["name"] == "input"
        assert param["param_type"] == "string"
        assert not param["is_mutable"]

    def test_function_with_multiple_parameters(self):
        """Test function with multiple parameters"""
        source = """
        func calculate(x: i32, y: f64, name: string) : f64 = {
            return y
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        assert len(func["parameters"]) == 3

        # First parameter
        param1 = func["parameters"][0]
        assert param1["name"] == "x"
        assert param1["param_type"] == "i32"
        assert not param1["is_mutable"]

        # Second parameter
        param2 = func["parameters"][1]
        assert param2["name"] == "y"
        assert param2["param_type"] == "f64"
        assert not param2["is_mutable"]

        # Third parameter
        param3 = func["parameters"][2]
        assert param3["name"] == "name"
        assert param3["param_type"] == "string"
        assert not param3["is_mutable"]

    def test_function_with_mutable_parameters(self):
        """Test function with mutable parameters"""
        source = """
        func modify(mut counter: i32, mut result: f64) : void = {
            return
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        assert len(func["parameters"]) == 2

        # First mutable parameter
        param1 = func["parameters"][0]
        assert param1["name"] == "counter"
        assert param1["param_type"] == "i32"
        assert param1["is_mutable"]

        # Second mutable parameter
        param2 = func["parameters"][1]
        assert param2["name"] == "result"
        assert param2["param_type"] == "f64"
        assert param2["is_mutable"]

    def test_function_with_mixed_mutability(self):
        """Test function with mixed mutable and immutable parameters"""
        source = """
        func process(input: string, mut output: string, debug: bool) : void = {
            return
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        assert len(func["parameters"]) == 3

        # Immutable parameter
        assert not func["parameters"][0]["is_mutable"]
        # Mutable parameter
        assert func["parameters"][1]["is_mutable"]
        # Immutable parameter
        assert not func["parameters"][2]["is_mutable"]

    def test_all_parameter_types(self):
        """Test all supported parameter types"""
        source = """
        func all_types(
            a: i32,
            b: i64,
            c: f32,
            d: f64,
            e: string,
            f: bool
        ) : void = {
            return
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        expected_types = ["i32", "i64", "f32", "f64", "string", "bool"]
        assert len(func["parameters"]) == len(expected_types)

        for i, expected_type in enumerate(expected_types):
            param = func["parameters"][i]
            assert param["param_type"] == expected_type

    def test_all_return_types(self):
        """Test all supported return types"""
        return_types = ["i32", "i64", "f32", "f64", "string", "bool", "void"]

        for return_type in return_types:
            source = f"""
            func test() : {return_type} = {{
                {"return" if return_type == "void" else "return 42"}
            }}
            """

            ast = self.parser.parse(source)
            func = ast["functions"][0]
            assert func["return_type"] == return_type

    def test_function_names_variations(self):
        """Test various valid function names"""
        valid_names = [
            "simple",
            "camelCase",
            "snake_case",
            "_private",
            "func123",
            "get_user_input",
            "validateData",
        ]

        for name in valid_names:
            source = f"""
            func {name}() : void = {{
                return
            }}
            """

            ast = self.parser.parse(source)
            func = ast["functions"][0]
            assert func["name"] == name

    def test_complex_function_body(self):
        """Test function with complex body structure"""
        source = """
        func complex_function(base: i32, scale: f64) : f64 = {
            val intermediate = {
                val temp = base * 2
                -> temp:f64 + scale
            }
            
            {
                val debug = "processing"
                val step = intermediate + 1.0
            }
            
            return intermediate * 2.0
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        assert func["name"] == "complex_function"
        assert len(func["parameters"]) == 2
        assert func["return_type"] == "f64"
        assert func["body"]["type"] == NodeType.BLOCK.value
        assert len(func["body"]["statements"]) == 3  # val, block, return


class TestFunctionCalls:
    """Test function call parsing"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_function_call_no_arguments(self):
        """Test function call with no arguments"""
        source = """
        val result = get_value()
        """

        ast = self.parser.parse(source)

        # Navigate to the function call
        val_decl = ast["statements"][0]
        func_call = val_decl["value"]

        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert func_call["function_name"] == "get_value"
        assert func_call["arguments"] == []

    def test_function_call_single_argument(self):
        """Test function call with single argument"""
        source = """
        val result = process(42)
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        func_call = val_decl["value"]

        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert func_call["function_name"] == "process"
        assert len(func_call["arguments"]) == 1

        arg = func_call["arguments"][0]
        assert arg["type"] == NodeType.COMPTIME_INT.value
        assert arg["value"] == 42

    def test_function_call_multiple_arguments(self):
        """Test function call with multiple arguments"""
        source = """
        val result = calculate(10, 3.14, "test")
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        func_call = val_decl["value"]

        assert len(func_call["arguments"]) == 3

        # First argument (comptime_int)
        arg1 = func_call["arguments"][0]
        assert arg1["type"] == NodeType.COMPTIME_INT.value
        assert arg1["value"] == 10

        # Second argument (comptime_float)
        arg2 = func_call["arguments"][1]
        assert arg2["type"] == NodeType.COMPTIME_FLOAT.value
        assert arg2["value"] == 3.14

        # Third argument (string literal)
        arg3 = func_call["arguments"][2]
        assert arg3["type"] == NodeType.LITERAL.value
        assert arg3["value"] == "test"

    def test_function_call_with_variable_arguments(self):
        """Test function call with variable arguments"""
        source = """
        val x = 10
        val y = 20.5
        val result = add(x, y)
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][2]  # Third statement
        func_call = val_decl["value"]

        assert len(func_call["arguments"]) == 2

        # Both arguments should be identifiers
        arg1 = func_call["arguments"][0]
        assert arg1["type"] == NodeType.IDENTIFIER.value
        assert arg1["name"] == "x"

        arg2 = func_call["arguments"][1]
        assert arg2["type"] == NodeType.IDENTIFIER.value
        assert arg2["name"] == "y"

    def test_function_call_with_expression_arguments(self):
        """Test function call with complex expression arguments"""
        source = """
        val result = calculate(10 + 5, 3.14 * 2.0, x + y)
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        func_call = val_decl["value"]

        assert len(func_call["arguments"]) == 3

        # All arguments should be binary operations
        for arg in func_call["arguments"]:
            assert arg["type"] == NodeType.BINARY_OPERATION.value
            assert arg["operator"] in ["+", "*"]

    def test_nested_function_calls(self):
        """Test nested function calls"""
        source = """
        val result = outer(inner(42), middle(10, 20))
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        outer_call = val_decl["value"]

        assert outer_call["function_name"] == "outer"
        assert len(outer_call["arguments"]) == 2

        # First argument is inner function call
        inner_call = outer_call["arguments"][0]
        assert inner_call["type"] == NodeType.FUNCTION_CALL.value
        assert inner_call["function_name"] == "inner"
        assert len(inner_call["arguments"]) == 1

        # Second argument is middle function call
        middle_call = outer_call["arguments"][1]
        assert middle_call["type"] == NodeType.FUNCTION_CALL.value
        assert middle_call["function_name"] == "middle"
        assert len(middle_call["arguments"]) == 2

    def test_function_call_with_conversions(self):
        """Test function call with explicit type conversions"""
        source = """
        val result = process(x:i64, y:f32)
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        func_call = val_decl["value"]

        assert len(func_call["arguments"]) == 2

        # Both arguments should be explicit conversions
        arg1 = func_call["arguments"][0]
        assert arg1["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        assert arg1["target_type"] == "i64"

        arg2 = func_call["arguments"][1]
        assert arg2["type"] == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        assert arg2["target_type"] == "f32"

    def test_function_call_as_expression_block_argument(self):
        """Test function call with expression block as argument"""
        source = """
        val result = process({
            val temp = 42
            -> temp + 10
        })
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        func_call = val_decl["value"]

        assert len(func_call["arguments"]) == 1

        # Argument should be an expression block
        arg = func_call["arguments"][0]
        assert arg["type"] == NodeType.BLOCK.value
        assert len(arg["statements"]) == 2  # val declaration and assign

    def test_function_call_in_return_statement(self):
        """Test function call within return statement"""
        source = """
        func main() : i32 = {
            return calculate(10, 20)
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value

        func_call = return_stmt["value"]
        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert func_call["function_name"] == "calculate"
        assert len(func_call["arguments"]) == 2


class TestReturnStatements:
    """Test return statement parsing in function contexts"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_return_with_literal(self):
        """Test return with literal values"""
        test_cases = [
            ("42", NodeType.COMPTIME_INT.value, 42),
            ("3.14", NodeType.COMPTIME_FLOAT.value, 3.14),
            ("true", NodeType.LITERAL.value, True),
            ("false", NodeType.LITERAL.value, False),
            ('"hello"', NodeType.LITERAL.value, "hello"),
        ]

        for literal, expected_type, expected_value in test_cases:
            source = f"""
            func test() : string = {{
                return {literal}
            }}
            """

            ast = self.parser.parse(source)
            func = ast["functions"][0]
            return_stmt = func["body"]["statements"][0]

            assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
            assert return_stmt["value"]["type"] == expected_type
            assert return_stmt["value"]["value"] == expected_value

    def test_return_with_identifier(self):
        """Test return with identifier"""
        source = """
        func test() : i32 = {
            val result = 42
            return result
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][1]  # Second statement

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.IDENTIFIER.value
        assert return_stmt["value"]["name"] == "result"

    def test_return_with_expression(self):
        """Test return with complex expressions"""
        source = """
        func test() : i32 = {
            return x + y * 2
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.BINARY_OPERATION.value

    def test_return_with_function_call(self):
        """Test return with function call"""
        source = """
        func test() : i32 = {
            return calculate(10, 20)
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"]["type"] == NodeType.FUNCTION_CALL.value

    def test_bare_return_void(self):
        """Test bare return for void functions"""
        source = """
        func test() : void = {
            return
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert return_stmt["value"] is None

    def test_return_with_conversion(self):
        """Test return with explicit type conversion"""
        source = """
        func test() : f64 = {
            val x = 42
            return x:f64
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][1]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        assert (
            return_stmt["value"]["type"]
            == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value
        )
        assert return_stmt["value"]["target_type"] == "f64"

    def test_multiple_returns_in_function(self):
        """Test function with multiple return statements"""
        source = """
        func test() : i32 = {
            return 1
            return 2
            return 3
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        assert len(func["body"]["statements"]) == 3
        for stmt in func["body"]["statements"]:
            assert stmt["type"] == NodeType.RETURN_STATEMENT.value

    def test_return_in_expression_block(self):
        """Test return statement in expression block (without if - not yet implemented)"""
        source = """
        func test() : i32 = {
            val result = {
                val temp = 42
                -> temp
            }
            return result
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        # Function should parse successfully with expression block
        assert func["name"] == "test"
        assert len(func["body"]["statements"]) == 2


class TestErrorRecovery:
    """Test parser error recovery and error messages"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_missing_parameter_type(self):
        """Test error for missing parameter type"""
        source = """
        func bad(input) : void = {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_missing_return_type(self):
        """Test error for missing return type"""
        source = """
        func bad(input: i32) = {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_missing_function_body(self):
        """Test error for missing function body"""
        source = """
        func bad(input: i32) : void
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_missing_function_name(self):
        """Test error for missing function name"""
        source = """
        func (input: i32) : void = {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_malformed_parameter_list(self):
        """Test error for malformed parameter list"""
        source = """
        func bad(input: i32,) : void = {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_invalid_function_name(self):
        """Test error for invalid function name"""
        source = """
        func 123invalid() : void = {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_missing_parentheses(self):
        """Test error for missing parentheses"""
        source = """
        func bad : void = {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_wrong_assignment_operator(self):
        """Test error for wrong assignment operator"""
        source = """
        func bad() : void {
            return
        }
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)

    def test_function_call_missing_parentheses(self):
        """Test error for function call missing parentheses"""
        source = """
        val result = function_name
        """

        # This should parse as identifier, not function call
        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]

        # Should be identifier, not function call
        assert val_decl["value"]["type"] == NodeType.IDENTIFIER.value

    def test_unclosed_argument_list(self):
        """Test error for unclosed argument list"""
        source = """
        val result = func_call(42, 3.14
        """

        with pytest.raises(SyntaxError):
            self.parser.parse(source)


class TestComplexIntegration:
    """Test complex integration scenarios"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_function_declarations_and_calls_mixed(self):
        """Test mixed function declarations and function calls"""
        source = """
        func helper(x: i32) : i32 = {
            return x * 2
        }
        
        val global_var = helper(42)
        
        func main() : i32 = {
            val local_result = helper(global_var)
            return local_result
        }
        
        val another_global = main()
        """

        ast = self.parser.parse(source)

        # Should have 2 functions and 2 global statements
        assert len(ast["functions"]) == 2
        assert len(ast["statements"]) == 2

        # Verify function structures
        helper_func = ast["functions"][0]
        assert helper_func["name"] == "helper"
        assert len(helper_func["parameters"]) == 1

        main_func = ast["functions"][1]
        assert main_func["name"] == "main"
        assert len(main_func["parameters"]) == 0

        # Verify global statements contain function calls
        global_var = ast["statements"][0]
        assert global_var["value"]["type"] == NodeType.FUNCTION_CALL.value

        another_global = ast["statements"][1]
        assert another_global["value"]["type"] == NodeType.FUNCTION_CALL.value

    def test_deeply_nested_function_calls(self):
        """Test deeply nested function calls"""
        source = """
        val result = a(b(c(d(e(42)))))
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]

        # Navigate through nested calls
        current_call = val_decl["value"]
        function_names = []

        while current_call["type"] == NodeType.FUNCTION_CALL.value:
            function_names.append(current_call["function_name"])
            if current_call["arguments"]:
                current_call = current_call["arguments"][0]
            else:
                break

        assert function_names == ["a", "b", "c", "d", "e"]

    def test_function_with_all_features(self):
        """Test function using all available features"""
        source = """
        func comprehensive(
            immutable_int: i32,
            mut mutable_float: f64,
            debug_flag: bool,
            mut output_string: string
        ) : f64 = {
            val local_calculation = {
                val base = immutable_int:f64
                val scaled = base * mutable_float
                -> scaled + 1.0
            }
            
            {
                val validation = debug_flag && true
                val message = "processing"
            }
            
            val final_result = nested_call(
                local_calculation,
                simple_func(),
                complex_expr(immutable_int + 1, mutable_float * 2.0)
            )
            
            return final_result:f64
        }
        """

        ast = self.parser.parse(source)
        func = ast["functions"][0]

        # Verify comprehensive function structure
        assert func["name"] == "comprehensive"
        assert len(func["parameters"]) == 4
        assert func["return_type"] == "f64"

        # Verify parameter mutability
        params = func["parameters"]
        assert not params[0]["is_mutable"]  # immutable_int
        assert params[1]["is_mutable"]  # mut mutable_float
        assert not params[2]["is_mutable"]  # debug_flag
        assert params[3]["is_mutable"]  # mut output_string

        # Verify complex body structure
        assert len(func["body"]["statements"]) == 4  # val, block, val, return

    def test_function_calls_in_expression_blocks(self):
        """Test function calls within expression blocks"""
        source = """
        val result = {
            val step1 = calculate(10, 20)
            val step2 = process(step1, helper())
            -> finalize(step2)
        }
        """

        ast = self.parser.parse(source)
        val_decl = ast["statements"][0]
        expr_block = val_decl["value"]

        assert expr_block["type"] == NodeType.BLOCK.value
        assert len(expr_block["statements"]) == 3

        # Each statement should involve function calls
        statements = expr_block["statements"]

        # First val declaration with function call
        assert statements[0]["value"]["type"] == NodeType.FUNCTION_CALL.value

        # Second val declaration with nested function calls
        step2_call = statements[1]["value"]
        assert step2_call["type"] == NodeType.FUNCTION_CALL.value
        assert len(step2_call["arguments"]) == 2
        assert step2_call["arguments"][1]["type"] == NodeType.FUNCTION_CALL.value

        # Assign statement with function call
        assign_call = statements[2]["value"]
        assert assign_call["type"] == NodeType.FUNCTION_CALL.value
