"""
Parser tests for array copy operations and property access.

Tests array copy syntax and property access parsing including:
- Array copy syntax: arr[..]
- Property access: arr.length
- Chained operations: matrix[0][..], matrix[0].length
- Combined patterns: arr[..].length (future semantic error, but should parse)
"""

import pytest

from src.hexen.ast_nodes import NodeType
from src.hexen.parser import HexenParser


class TestArrayCopy:
    """Test array copy operation parsing ([..] syntax)"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_simple_array_copy(self):
        """Test simple array copy: source[..] (now unified as range indexing)"""
        source = """
        func test() : void = {
            val copy : [3]i32 = source[..]
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]

        # Verify array indexing with range (unified model!)
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value

        # Check array (should be an identifier)
        assert array_access["array"]["type"] == NodeType.IDENTIFIER.value
        assert array_access["array"]["name"] == "source"

        # Check index is a full unbounded range
        range_index = array_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

    def test_array_copy_in_function_call(self):
        """Test array copy as function argument: process(arr[..])"""
        source = """
        func test() : void = {
            process(arr[..])
        }
        """
        ast = self.parser.parse(source)

        # Navigate to function call
        func = ast["functions"][0]
        func_call_stmt = func["body"]["statements"][0]
        func_call = func_call_stmt["function_call"]

        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert func_call["function_name"] == "process"
        assert len(func_call["arguments"]) == 1

        # First argument: arr[..] (now unified as range indexing)
        arg = func_call["arguments"][0]
        assert arg["type"] == NodeType.ARRAY_ACCESS.value
        assert arg["array"]["type"] == NodeType.IDENTIFIER.value
        assert arg["array"]["name"] == "arr"

        # Check index is a full unbounded range
        range_index = arg["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

    def test_array_copy_in_return_statement(self):
        """Test array copy in return: return data[..]"""
        source = """
        func clone_array() : [5]i32 = {
            return data[..]
        }
        """
        ast = self.parser.parse(source)

        # Navigate to return statement
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value

        # data[..] is now unified as range indexing
        array_access = return_stmt["value"]
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["array"]["type"] == NodeType.IDENTIFIER.value
        assert array_access["array"]["name"] == "data"

        # Check index is a full unbounded range
        range_index = array_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

    def test_array_copy_of_array_access(self):
        """Test copying array element (row copy): matrix[0][..]"""
        source = """
        func test() : void = {
            val row : [4]i32 = matrix[0][..]
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        outer_access = val_decl["value"]

        # Outer operation: [..] (now unified as range indexing)
        assert outer_access["type"] == NodeType.ARRAY_ACCESS.value

        # Check outer index is a full unbounded range
        range_index = outer_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

        # Inner operation: matrix[0]
        inner_access = outer_access["array"]
        assert inner_access["type"] == NodeType.ARRAY_ACCESS.value
        assert inner_access["index"]["type"] == NodeType.COMPTIME_INT.value
        assert inner_access["index"]["value"] == 0

        # Base array
        base_array = inner_access["array"]
        assert base_array["type"] == NodeType.IDENTIFIER.value
        assert base_array["name"] == "matrix"

    def test_array_copy_of_function_call(self):
        """Test copying function result: get_array()[..]"""
        source = """
        func test() : void = {
            val copy : [10]f64 = get_array()[..]
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_access = val_decl["value"]

        # get_array()[..] is now unified as range indexing
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value

        # Check index is a full unbounded range
        range_index = array_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

        # Check array (should be a function call)
        function_call = array_access["array"]
        assert function_call["type"] == NodeType.FUNCTION_CALL.value
        assert function_call["function_name"] == "get_array"

    def test_array_copy_multiple_arguments(self):
        """Test multiple array copies in function call: merge(a[..], b[..])"""
        source = """
        func test() : void = {
            merge(a[..], b[..])
        }
        """
        ast = self.parser.parse(source)

        # Navigate to function call
        func = ast["functions"][0]
        func_call_stmt = func["body"]["statements"][0]
        func_call = func_call_stmt["function_call"]

        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert len(func_call["arguments"]) == 2

        # First argument: a[..] (now unified as range indexing)
        arg1 = func_call["arguments"][0]
        assert arg1["type"] == NodeType.ARRAY_ACCESS.value
        assert arg1["array"]["name"] == "a"

        range_index1 = arg1["index"]
        assert range_index1["type"] == NodeType.RANGE_EXPR.value
        assert range_index1["start"] is None
        assert range_index1["end"] is None
        assert range_index1["step"] is None
        assert range_index1["inclusive"] is False

        # Second argument: b[..] (now unified as range indexing)
        arg2 = func_call["arguments"][1]
        assert arg2["type"] == NodeType.ARRAY_ACCESS.value
        assert arg2["array"]["name"] == "b"

        range_index2 = arg2["index"]
        assert range_index2["type"] == NodeType.RANGE_EXPR.value
        assert range_index2["start"] is None
        assert range_index2["end"] is None
        assert range_index2["step"] is None
        assert range_index2["inclusive"] is False

    def test_nested_array_copy(self):
        """Test copy of multidimensional array row: matrix[i][j][..]"""
        source = """
        func test() : void = {
            val slice = matrix[i][j][..]
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        access3 = val_decl["value"]

        # Outermost operation: [..] (now unified as range indexing)
        assert access3["type"] == NodeType.ARRAY_ACCESS.value

        range_index = access3["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

        # Second access: [j]
        access2 = access3["array"]
        assert access2["type"] == NodeType.ARRAY_ACCESS.value
        assert access2["index"]["name"] == "j"

        # First access: [i]
        access1 = access2["array"]
        assert access1["type"] == NodeType.ARRAY_ACCESS.value
        assert access1["index"]["name"] == "i"

        # Base array
        base = access1["array"]
        assert base["type"] == NodeType.IDENTIFIER.value
        assert base["name"] == "matrix"


class TestPropertyAccess:
    """Test property access parsing (.length syntax)"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_simple_length_property(self):
        """Test simple .length property: arr.length"""
        source = """
        func test() : void = {
            val size : i32 = arr.length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        property_access = val_decl["value"]

        # Verify property access node structure
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # Check object (should be an identifier)
        assert property_access["object"]["type"] == NodeType.IDENTIFIER.value
        assert property_access["object"]["name"] == "arr"

    def test_length_in_expression(self):
        """Test .length in expression: arr.length > 0"""
        source = """
        func test() : void = {
            val is_empty : bool = arr.length > 0
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        binary_op = val_decl["value"]

        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == ">"

        # Left side: arr.length
        property_access = binary_op["left"]
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"
        assert property_access["object"]["name"] == "arr"

        # Right side: 0
        assert binary_op["right"]["type"] == NodeType.COMPTIME_INT.value
        assert binary_op["right"]["value"] == 0

    def test_length_in_function_call(self):
        """Test .length as function argument: process(arr.length)"""
        source = """
        func test() : void = {
            process(arr.length)
        }
        """
        ast = self.parser.parse(source)

        # Navigate to function call
        func = ast["functions"][0]
        func_call_stmt = func["body"]["statements"][0]
        func_call = func_call_stmt["function_call"]

        assert func_call["type"] == NodeType.FUNCTION_CALL.value
        assert len(func_call["arguments"]) == 1

        # Argument: arr.length
        arg = func_call["arguments"][0]
        assert arg["type"] == NodeType.PROPERTY_ACCESS.value
        assert arg["property"] == "length"
        assert arg["object"]["name"] == "arr"

    def test_length_in_return_statement(self):
        """Test .length in return: return arr.length"""
        source = """
        func get_size() : i32 = {
            return arr.length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to return statement
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]

        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value

        property_access = return_stmt["value"]
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"
        assert property_access["object"]["name"] == "arr"

    def test_length_of_array_access(self):
        """Test .length of array element (row length): matrix[0].length"""
        source = """
        func test() : void = {
            val row_len : i32 = matrix[0].length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        property_access = val_decl["value"]

        # Outer operation: .length
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # Inner operation: matrix[0]
        array_access = property_access["object"]
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["index"]["type"] == NodeType.COMPTIME_INT.value
        assert array_access["index"]["value"] == 0

        # Base array
        base_array = array_access["array"]
        assert base_array["type"] == NodeType.IDENTIFIER.value
        assert base_array["name"] == "matrix"

    def test_length_of_function_call(self):
        """Test .length of function result: get_array().length"""
        source = """
        func test() : void = {
            val size : i32 = get_array().length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        property_access = val_decl["value"]

        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # Check object (should be a function call)
        function_call = property_access["object"]
        assert function_call["type"] == NodeType.FUNCTION_CALL.value
        assert function_call["function_name"] == "get_array"

    def test_length_in_if_condition(self):
        """Test .length in if condition: if i < data.length"""
        source = """
        func test() : void = {
            mut i : i32 = 0
            if i < data.length {
                i = i + 1
            }
        }
        """
        ast = self.parser.parse(source)

        # Navigate to if statement (conditional_stmt)
        func = ast["functions"][0]
        if_stmt = func["body"]["statements"][1]

        assert if_stmt["type"] == NodeType.CONDITIONAL_STATEMENT.value

        # Condition: i < data.length
        condition = if_stmt["condition"]
        assert condition["type"] == NodeType.BINARY_OPERATION.value
        assert condition["operator"] == "<"

        # Right side: data.length
        property_access = condition["right"]
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"
        assert property_access["object"]["name"] == "data"

    def test_length_in_arithmetic(self):
        """Test .length in arithmetic: i < arr.length - 1"""
        source = """
        func test() : void = {
            val check : bool = i < arr.length - 1
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        comparison = val_decl["value"]

        assert comparison["type"] == NodeType.BINARY_OPERATION.value
        assert comparison["operator"] == "<"

        # Right side: arr.length - 1
        subtraction = comparison["right"]
        assert subtraction["type"] == NodeType.BINARY_OPERATION.value
        assert subtraction["operator"] == "-"

        # Left of subtraction: arr.length
        property_access = subtraction["left"]
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"


class TestCombinedOperations:
    """Test combined array operations (chaining copy, access, and properties)"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_copy_then_length(self):
        """Test chained copy and length: arr[..].length (parses, semantic error later)"""
        source = """
        func test() : void = {
            val size = arr[..].length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        property_access = val_decl["value"]

        # Outer operation: .length
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # Inner operation: arr[..] (now unified as range indexing)
        array_access = property_access["object"]
        assert array_access["type"] == NodeType.ARRAY_ACCESS.value
        assert array_access["array"]["name"] == "arr"

        range_index = array_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

    def test_access_then_copy_then_length(self):
        """Test complex chain: matrix[i][..].length"""
        source = """
        func test() : void = {
            val row_size = matrix[i][..].length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        property_access = val_decl["value"]

        # Outermost: .length
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # Middle: [..] (now unified as range indexing)
        outer_access = property_access["object"]
        assert outer_access["type"] == NodeType.ARRAY_ACCESS.value

        range_index = outer_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

        # Innermost: matrix[i]
        inner_access = outer_access["array"]
        assert inner_access["type"] == NodeType.ARRAY_ACCESS.value
        assert inner_access["index"]["name"] == "i"
        assert inner_access["array"]["name"] == "matrix"

    def test_multidimensional_access_then_length(self):
        """Test multidimensional access then length: matrix[i][j].length"""
        source = """
        func test() : void = {
            val size = matrix[i][j].length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        property_access = val_decl["value"]

        # Outermost: .length
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # Second access: [j]
        access2 = property_access["object"]
        assert access2["type"] == NodeType.ARRAY_ACCESS.value
        assert access2["index"]["name"] == "j"

        # First access: [i]
        access1 = access2["array"]
        assert access1["type"] == NodeType.ARRAY_ACCESS.value
        assert access1["index"]["name"] == "i"
        assert access1["array"]["name"] == "matrix"

    def test_function_result_copy(self):
        """Test copying function result then access: get_matrix()[..][0]"""
        source = """
        func test() : void = {
            val element = get_matrix()[..][0]
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        outer_access = val_decl["value"]

        # Outermost: [0]
        assert outer_access["type"] == NodeType.ARRAY_ACCESS.value
        assert outer_access["index"]["value"] == 0

        # Middle: [..] (now unified as range indexing)
        middle_access = outer_access["array"]
        assert middle_access["type"] == NodeType.ARRAY_ACCESS.value

        range_index = middle_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

        # Innermost: get_matrix()
        function_call = middle_access["array"]
        assert function_call["type"] == NodeType.FUNCTION_CALL.value
        assert function_call["function_name"] == "get_matrix"

    def test_complex_chain_in_expression(self):
        """Test complex chain in expression: matrix[0][..].length > 5"""
        source = """
        func test() : void = {
            val check : bool = matrix[0][..].length > 5
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        binary_op = val_decl["value"]

        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == ">"

        # Left side: matrix[0][..].length
        property_access = binary_op["left"]
        assert property_access["type"] == NodeType.PROPERTY_ACCESS.value
        assert property_access["property"] == "length"

        # matrix[0][..] (now unified as range indexing)
        outer_access = property_access["object"]
        assert outer_access["type"] == NodeType.ARRAY_ACCESS.value

        range_index = outer_access["index"]
        assert range_index["type"] == NodeType.RANGE_EXPR.value
        assert range_index["start"] is None
        assert range_index["end"] is None
        assert range_index["step"] is None
        assert range_index["inclusive"] is False

        inner_access = outer_access["array"]
        assert inner_access["type"] == NodeType.ARRAY_ACCESS.value
        assert inner_access["array"]["name"] == "matrix"

    def test_multiple_properties_different_arrays(self):
        """Test multiple property accesses: a.length + b.length"""
        source = """
        func test() : void = {
            val total : i32 = a.length + b.length
        }
        """
        ast = self.parser.parse(source)

        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        binary_op = val_decl["value"]

        assert binary_op["type"] == NodeType.BINARY_OPERATION.value
        assert binary_op["operator"] == "+"

        # Left: a.length
        left_prop = binary_op["left"]
        assert left_prop["type"] == NodeType.PROPERTY_ACCESS.value
        assert left_prop["property"] == "length"
        assert left_prop["object"]["name"] == "a"

        # Right: b.length
        right_prop = binary_op["right"]
        assert right_prop["type"] == NodeType.PROPERTY_ACCESS.value
        assert right_prop["property"] == "length"
        assert right_prop["object"]["name"] == "b"
