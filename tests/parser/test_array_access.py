"""
Parser tests for array element access expressions.

Tests array access syntax parsing including:
- Single array access: arr[0]
- Chained array access: arr[i][j][k]
- Complex index expressions: arr[i + j]
- Array access with function calls: arr[compute_index()]
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestArrayAccess:
    """Test array element access expression parsing"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_single_array_access_literal_index(self):
        """Test single array access with literal index: arr[0]"""
        source = """
        func test() : void = {
            val element = arr[0]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        
        # Check array (should be an identifier)
        assert array_access["array"]["type"] == NodeType.IDENTIFIER.value
        assert array_access["array"]["name"] == "arr"
        
        # Check index (should be a comptime_int)
        assert array_access["index"]["type"] == NodeType.COMPTIME_INT.value
        assert array_access["index"]["value"] == 0

    def test_single_array_access_various_literal_indices(self):
        """Test array access with various literal indices"""
        test_cases = [
            ("arr[1]", 1),
            ("arr[5]", 5),
            ("arr[10]", 10),
            ("arr[100]", 100),
        ]
        
        for access_expr, expected_index in test_cases:
            source = f"""
            func test() : void = {{
                val element = {access_expr}
            }}
            """
            ast = self.parser.parse(source)
            
            # Navigate to array access
            func = ast["functions"][0]
            val_decl = func["body"]["statements"][0]
            array_access = val_decl["value"]
            
            assert array_access["type"] == NodeType.ARRAY_ACCESS.value
            assert array_access["array"]["name"] == "arr"
            assert array_access["index"]["type"] == NodeType.COMPTIME_INT.value
            assert array_access["index"]["value"] == expected_index

    def test_single_array_access_identifier_index(self):
        """Test single array access with identifier index: arr[i]"""
        source = """
        func test() : void = {
            val element = arr[i]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        
        # Check array
        assert array_access["array"]["type"] == NodeType.IDENTIFIER.value
        assert array_access["array"]["name"] == "arr"
        
        # Check index (should be an identifier)
        assert array_access["index"]["type"] == NodeType.IDENTIFIER.value
        assert array_access["index"]["name"] == "i"

    def test_single_array_access_expression_index(self):
        """Test array access with expression index: arr[i + 1]"""
        source = """
        func test() : void = {
            val element = arr[i + 1]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["array"]["name"] == "arr"
        
        # Check index (should be a binary operation)
        index = array_access["index"]
        assert index["type"] == NodeType.BINARY_OPERATION.value
        assert index["operator"] == "+"
        assert index["left"]["type"] == NodeType.IDENTIFIER.value
        assert index["left"]["name"] == "i"
        assert index["right"]["type"] == NodeType.COMPTIME_INT.value
        assert index["right"]["value"] == 1

    def test_single_array_access_complex_expression_index(self):
        """Test array access with complex expression index: arr[i * 2 + j]"""
        source = """
        func test() : void = {
            val element = arr[i * 2 + j]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array access
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["array"]["name"] == "arr"
        
        # Check complex index expression structure
        index = array_access["index"]
        assert index["type"] == NodeType.BINARY_OPERATION.value
        assert index["operator"] == "+"

    def test_single_array_access_function_call_index(self):
        """Test array access with function call index: arr[compute_index()]"""
        source = """
        func test() : void = {
            val element = arr[compute_index()]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array access
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["array"]["name"] == "arr"
        
        # Check index (should be a function call)
        index = array_access["index"]
        assert index["type"] == NodeType.FUNCTION_CALL.value
        assert index["function_name"] == "compute_index"
        assert index["arguments"] == []

    def test_chained_array_access_2d(self):
        """Test chained array access for 2D: arr[i][j]"""
        source = """
        func test() : void = {
            val element = arr[i][j]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        outer_access = val_decl["value"]
        
        # Outer access: arr[i][j] - the [j] part
        assert outer_access["type"] == NodeType.ARRAY_ACCESS.value
        assert outer_access["index"]["type"] == NodeType.IDENTIFIER.value
        assert outer_access["index"]["name"] == "j"
        
        # Inner access: arr[i] - the first part
        inner_access = outer_access["array"]
        assert inner_access["type"] == NodeType.ARRAY_ACCESS.value
        assert inner_access["index"]["type"] == NodeType.IDENTIFIER.value
        assert inner_access["index"]["name"] == "i"
        
        # Base array
        base_array = inner_access["array"]
        assert base_array["type"] == NodeType.IDENTIFIER.value
        assert base_array["name"] == "arr"

    def test_chained_array_access_3d(self):
        """Test chained array access for 3D: arr[i][j][k]"""
        source = """
        func test() : void = {
            val element = arr[i][j][k]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        access3 = val_decl["value"]
        
        # Third access: [k]
        assert access3["type"] == NodeType.ARRAY_ACCESS.value
        assert access3["index"]["name"] == "k"
        
        # Second access: [j]
        access2 = access3["array"]
        assert access2["type"] == NodeType.ARRAY_ACCESS.value
        assert access2["index"]["name"] == "j"
        
        # First access: [i]
        access1 = access2["array"]
        assert access1["type"] == NodeType.ARRAY_ACCESS.value
        assert access1["index"]["name"] == "i"
        
        # Base array
        base_array = access1["array"]
        assert base_array["type"] == NodeType.IDENTIFIER.value
        assert base_array["name"] == "arr"

    def test_chained_array_access_4d(self):
        """Test chained array access for 4D: arr[a][b][c][d]"""
        source = """
        func test() : void = {
            val element = arr[a][b][c][d]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        access4 = val_decl["value"]
        
        # Follow the chain back to verify structure
        current_access = access4
        expected_indices = ["d", "c", "b", "a"]
        
        for expected_index in expected_indices:
            assert current_access["type"] == NodeType.ARRAY_ACCESS.value
            assert current_access["index"]["type"] == NodeType.IDENTIFIER.value
            assert current_access["index"]["name"] == expected_index
            
            if expected_index != "a":  # Not the last one
                current_access = current_access["array"]
            else:  # Last one should have the base array
                base_array = current_access["array"]
                assert base_array["type"] == NodeType.IDENTIFIER.value
                assert base_array["name"] == "arr"

    def test_chained_array_access_mixed_indices(self):
        """Test chained access with mixed index types: arr[0][i][j + 1]"""
        source = """
        func test() : void = {
            val element = arr[0][i][j + 1]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        access3 = val_decl["value"]
        
        # Third access: [j + 1]
        assert access3["type"] == NodeType.ARRAY_ACCESS.value
        assert access3["index"]["type"] == NodeType.BINARY_OPERATION.value
        
        # Second access: [i]
        access2 = access3["array"]
        assert access2["type"] == NodeType.ARRAY_ACCESS.value
        assert access2["index"]["type"] == NodeType.IDENTIFIER.value
        assert access2["index"]["name"] == "i"
        
        # First access: [0]
        access1 = access2["array"]
        assert access1["type"] == NodeType.ARRAY_ACCESS.value
        assert access1["index"]["type"] == NodeType.COMPTIME_INT.value
        assert access1["index"]["value"] == 0
        
        # Base array
        base_array = access1["array"]
        assert base_array["type"] == NodeType.IDENTIFIER.value
        assert base_array["name"] == "arr"

    def test_array_access_of_array_literal(self):
        """Test array access of array literal: [1, 2, 3][0]"""
        source = """
        func test() : void = {
            val element = [1, 2, 3][0]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        
        # Check array (should be an array literal)
        array_literal = array_access["array"]
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        # Check index
        assert array_access["index"]["type"] == NodeType.COMPTIME_INT.value
        assert array_access["index"]["value"] == 0

    def test_array_access_of_function_call(self):
        """Test array access of function call result: get_array()[i]"""
        source = """
        func test() : void = {
            val element = get_array()[i]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]
        
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        
        # Check array (should be a function call)
        function_call = array_access["array"]
        assert function_call["type"] == NodeType.FUNCTION_CALL.value
        assert function_call["function_name"] == "get_array"
        
        # Check index
        assert array_access["index"]["type"] == NodeType.IDENTIFIER.value
        assert array_access["index"]["name"] == "i"

    def test_array_access_in_expressions(self):
        """Test array access within larger expressions: arr[i] + arr[j]"""
        source = """
        func test() : void = {
            val sum = arr[i] + arr[j]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        binary_op = val_decl["value"]
        
        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == "+"
        
        # Left side: arr[i]
        left_access = binary_op["left"]
        assert left_access["type"] == NodeType.ARRAY_ACCESS.value
        assert left_access["array"]["name"] == "arr"
        assert left_access["index"]["name"] == "i"
        
        # Right side: arr[j]
        right_access = binary_op["right"]
        assert right_access["type"] == NodeType.ARRAY_ACCESS.value
        assert right_access["array"]["name"] == "arr"
        assert right_access["index"]["name"] == "j"

    def test_array_access_in_function_calls(self):
        """Test array access as function arguments: process(arr[i], matrix[j][k])"""
        source = """
        func test() : void = {
            process(arr[i], matrix[j][k])
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to function call
        func = ast["functions"][0]
        func_call_stmt = func["body"]["statements"][0]
        func_call = func_call_stmt["function_call"]
        
        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert func_call["function_name"] == "process"
        assert len(func_call["arguments"]) == 2
        
        # First argument: arr[i]
        arg1 = func_call["arguments"][0]
        assert arg1["type"] == NodeType.ARRAY_ACCESS.value
        assert arg1["array"]["name"] == "arr"
        assert arg1["index"]["name"] == "i"
        
        # Second argument: matrix[j][k]
        arg2 = func_call["arguments"][1]
        assert arg2["type"] == NodeType.ARRAY_ACCESS.value
        assert arg2["index"]["name"] == "k"
        
        inner_access = arg2["array"]
        assert inner_access["type"] == NodeType.ARRAY_ACCESS.value
        assert inner_access["array"]["name"] == "matrix"
        assert inner_access["index"]["name"] == "j"

    def test_array_access_in_return_statements(self):
        """Test array access in return statements: return arr[i]"""
        source = """
        func get_element() : i32 = {
            return arr[i]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to return statement
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]
        
        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        
        array_access = return_stmt["value"]
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["array"]["name"] == "arr"
        assert array_access["index"]["name"] == "i"

    def test_complex_nested_array_access_with_expressions(self):
        """Test complex nested access: matrix[i * 2 + 1][j / 2][compute(k)]"""
        source = """
        func test() : void = {
            val element = matrix[i * 2 + 1][j / 2][compute(k)]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        access3 = val_decl["value"]
        
        # Third access: [compute(k)]
        assert access3["type"] == NodeType.ARRAY_ACCESS.value
        assert access3["index"]["type"] == NodeType.FUNCTION_CALL.value
        assert access3["index"]["function_name"] == "compute"
        
        # Second access: [j / 2]
        access2 = access3["array"]
        assert access2["type"] == NodeType.ARRAY_ACCESS.value
        assert access2["index"]["type"] == NodeType.BINARY_OPERATION.value
        assert access2["index"]["operator"] == "/"
        
        # First access: [i * 2 + 1]
        access1 = access2["array"]
        assert access1["type"] == NodeType.ARRAY_ACCESS.value
        assert access1["index"]["type"] == NodeType.BINARY_OPERATION.value
        assert access1["index"]["operator"] == "+"
        
        # Base array
        base_array = access1["array"]
        assert base_array["type"] == NodeType.IDENTIFIER.value
        assert base_array["name"] == "matrix"

    def test_array_access_edge_cases(self):
        """Test edge cases for array access"""
        # Array access with negative index (should parse as unary minus)
        source1 = """
        func test() : void = {
            val element = arr[-1]
        }
        """
        ast1 = self.parser.parse(source1)
        func1 = ast1["functions"][0]
        val_decl1 = func1["body"]["statements"][0]
        array_access1 = val_decl1["value"]
        assert array_access1["type"] == NodeType.ARRAY_ACCESS.value
        # Index should be a unary operation with negative sign
        assert array_access1["index"]["type"] == NodeType.UNARY_OPERATION.value

        # Array access with parenthesized expression
        source2 = """
        func test() : void = {
            val element = arr[(i + j)]
        }
        """
        ast2 = self.parser.parse(source2)
        func2 = ast2["functions"][0]
        val_decl2 = func2["body"]["statements"][0]
        array_access2 = val_decl2["value"]
        assert array_access2["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access2["index"]["type"] == NodeType.BINARY_OPERATION.value