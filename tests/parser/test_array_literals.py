"""
Parser tests for array literal expressions.

Tests array literal syntax parsing including:
- Empty arrays: []
- Single element arrays: [42]
- Multiple element arrays: [1, 2, 3]
- Nested array literals: [[1, 2], [3, 4]]
- Mixed-type array literals: [42, 3.14, true]
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestArrayLiterals:
    """Test array literal expression parsing"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_empty_array_literal(self):
        """Test empty array literal: []"""
        source = """
        func test() : void = {
            val empty = []
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert array_literal["elements"] == []

    def test_single_element_array_literal(self):
        """Test single element array literals"""
        test_cases = [
            ("[42]", NodeType.COMPTIME_INT.value, 42),
            ("[3.14]", NodeType.COMPTIME_FLOAT.value, 3.14),
            ("[true]", NodeType.LITERAL.value, True),
            ("[\"hello\"]", NodeType.LITERAL.value, "hello"),
        ]
        
        for array_str, expected_element_type, expected_value in test_cases:
            source = f"""
            func test() : void = {{
                val arr = {array_str}
            }}
            """
            ast = self.parser.parse(source)
            
            # Navigate to array literal
            func = ast["functions"][0]
            val_decl = func["body"]["statements"][0]
            array_literal = val_decl["value"]
            
            assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
            assert len(array_literal["elements"]) == 1
            
            element = array_literal["elements"][0]
            assert element["type"] == expected_element_type
            assert element["value"] == expected_value

    def test_multiple_element_array_literal_integers(self):
        """Test multiple integer elements: [1, 2, 3, 4, 5]"""
        source = """
        func test() : void = {
            val numbers = [1, 2, 3, 4, 5]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 5
        
        expected_values = [1, 2, 3, 4, 5]
        for i, element in enumerate(array_literal["elements"]):
            assert element["type"] == NodeType.COMPTIME_INT.value
            assert element["value"] == expected_values[i]

    def test_multiple_element_array_literal_floats(self):
        """Test multiple float elements: [3.14, 2.71, 1.41]"""
        source = """
        func test() : void = {
            val floats = [3.14, 2.71, 1.41]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        expected_values = [3.14, 2.71, 1.41]
        for i, element in enumerate(array_literal["elements"]):
            assert element["type"] == NodeType.COMPTIME_FLOAT.value
            assert element["value"] == expected_values[i]

    def test_multiple_element_array_literal_strings(self):
        """Test multiple string elements: ["hello", "world", "!"]"""
        source = """
        func test() : void = {
            val words = ["hello", "world", "!"]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        expected_values = ["hello", "world", "!"]
        for i, element in enumerate(array_literal["elements"]):
            assert element["type"] == NodeType.LITERAL.value
            assert element["value"] == expected_values[i]

    def test_multiple_element_array_literal_booleans(self):
        """Test multiple boolean elements: [true, false, true]"""
        source = """
        func test() : void = {
            val flags = [true, false, true]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        expected_values = [True, False, True]
        for i, element in enumerate(array_literal["elements"]):
            assert element["type"] == NodeType.LITERAL.value
            assert element["value"] == expected_values[i]

    def test_mixed_type_array_literal(self):
        """Test mixed types: [42, 3.14, true, "hello"]"""
        source = """
        func test() : void = {
            val mixed = [42, 3.14, true, "hello"]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 4
        
        # Check each element type and value
        elements = array_literal["elements"]
        
        assert elements[0]["type"] == NodeType.COMPTIME_INT.value
        assert elements[0]["value"] == 42
        
        assert elements[1]["type"] == NodeType.COMPTIME_FLOAT.value
        assert elements[1]["value"] == 3.14
        
        assert elements[2]["type"] == NodeType.LITERAL.value
        assert elements[2]["value"] == True
        
        assert elements[3]["type"] == NodeType.LITERAL.value
        assert elements[3]["value"] == "hello"

    def test_nested_array_literal_2d(self):
        """Test 2D nested array literals: [[1, 2], [3, 4]]"""
        source = """
        func test() : void = {
            val matrix = [[1, 2], [3, 4]]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 2
        
        # First row: [1, 2]
        row1 = array_literal["elements"][0]
        assert row1["type"] == NodeType.ARRAY_LITERAL.value
        assert len(row1["elements"]) == 2
        assert row1["elements"][0]["type"] == NodeType.COMPTIME_INT.value
        assert row1["elements"][0]["value"] == 1
        assert row1["elements"][1]["type"] == NodeType.COMPTIME_INT.value
        assert row1["elements"][1]["value"] == 2
        
        # Second row: [3, 4]
        row2 = array_literal["elements"][1]
        assert row2["type"] == NodeType.ARRAY_LITERAL.value
        assert len(row2["elements"]) == 2
        assert row2["elements"][0]["type"] == NodeType.COMPTIME_INT.value
        assert row2["elements"][0]["value"] == 3
        assert row2["elements"][1]["type"] == NodeType.COMPTIME_INT.value
        assert row2["elements"][1]["value"] == 4

    def test_nested_array_literal_3x3(self):
        """Test 3x3 nested array literals"""
        source = """
        func test() : void = {
            val matrix = [
                [1, 2, 3],
                [4, 5, 6], 
                [7, 8, 9]
            ]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        expected_values = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        
        for i, row in enumerate(array_literal["elements"]):
            assert row["type"] == NodeType.ARRAY_LITERAL.value
            assert len(row["elements"]) == 3
            
            for j, element in enumerate(row["elements"]):
                assert element["type"] == NodeType.COMPTIME_INT.value
                assert element["value"] == expected_values[i][j]

    def test_nested_array_literal_3d(self):
        """Test 3D nested array literals: [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]"""
        source = """
        func test() : void = {
            val cube = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 2
        
        expected_values = [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]]
        ]
        
        for layer_idx, layer in enumerate(array_literal["elements"]):
            assert layer["type"] == NodeType.ARRAY_LITERAL.value
            assert len(layer["elements"]) == 2
            
            for row_idx, row in enumerate(layer["elements"]):
                assert row["type"] == NodeType.ARRAY_LITERAL.value
                assert len(row["elements"]) == 2
                
                for col_idx, element in enumerate(row["elements"]):
                    assert element["type"] == NodeType.COMPTIME_INT.value
                    assert element["value"] == expected_values[layer_idx][row_idx][col_idx]

    def test_array_literal_with_expressions(self):
        """Test array literals containing expressions: [1 + 2, 3 * 4, 5 / 2]"""
        source = """
        func test() : void = {
            val computed = [1 + 2, 3 * 4, 5 / 2]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        # Each element should be a binary operation
        for element in array_literal["elements"]:
            assert element["type"] == NodeType.BINARY_OPERATION.value

    def test_array_literal_with_identifiers(self):
        """Test array literals containing identifiers: [x, y, z]"""
        source = """
        func test(x: i32, y: i32, z: i32) : void = {
            val vars = [x, y, z]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        expected_names = ["x", "y", "z"]
        for i, element in enumerate(array_literal["elements"]):
            assert element["type"] == NodeType.IDENTIFIER.value
            assert element["name"] == expected_names[i]

    def test_array_literal_with_function_calls(self):
        """Test array literals containing function calls: [func1(), func2()]"""
        source = """
        func test() : void = {
            val results = [func1(), func2()]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 2
        
        expected_names = ["func1", "func2"]
        for i, element in enumerate(array_literal["elements"]):
            assert element["type"] == NodeType.FUNCTION_CALL.value
            assert element["function_name"] == expected_names[i]

    def test_array_literal_in_function_calls(self):
        """Test array literals as function arguments: process([1, 2, 3])"""
        source = """
        func test() : void = {
            process([1, 2, 3])
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
        
        array_literal = func_call["arguments"][0]
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3

    def test_array_literal_in_return_statements(self):
        """Test array literals in return statements: return [1, 2, 3]"""
        source = """
        func create_array() : [3]i32 = {
            return [1, 2, 3]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to return statement
        func = ast["functions"][0]
        return_stmt = func["body"]["statements"][0]
        
        assert return_stmt["type"] == NodeType.RETURN_STATEMENT.value
        
        array_literal = return_stmt["value"]
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3

    def test_array_literal_mixed_nested_types(self):
        """Test mixed nested array literals with different element types"""
        source = """
        func test() : void = {
            val mixed_nested = [
                [1, 2], 
                ["hello", "world"],
                [true, false]
            ]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to array literal
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_literal = val_decl["value"]
        
        assert array_literal["type"] == NodeType.ARRAY_LITERAL.value
        assert len(array_literal["elements"]) == 3
        
        # First sub-array: [1, 2]
        row1 = array_literal["elements"][0]
        assert row1["type"] == NodeType.ARRAY_LITERAL.value
        assert row1["elements"][0]["type"] == NodeType.COMPTIME_INT.value
        assert row1["elements"][1]["type"] == NodeType.COMPTIME_INT.value
        
        # Second sub-array: ["hello", "world"]
        row2 = array_literal["elements"][1]
        assert row2["type"] == NodeType.ARRAY_LITERAL.value
        assert row2["elements"][0]["type"] == NodeType.LITERAL.value
        assert row2["elements"][1]["type"] == NodeType.LITERAL.value
        
        # Third sub-array: [true, false]
        row3 = array_literal["elements"][2]
        assert row3["type"] == NodeType.ARRAY_LITERAL.value
        assert row3["elements"][0]["type"] == NodeType.LITERAL.value
        assert row3["elements"][1]["type"] == NodeType.LITERAL.value

    def test_array_literal_edge_cases(self):
        """Test edge cases for array literals"""
        # Single element with trailing comma (if supported by grammar)
        source1 = """
        func test() : void = {
            val single = [42]
        }
        """
        ast1 = self.parser.parse(source1)
        func1 = ast1["functions"][0]
        val_decl1 = func1["body"]["statements"][0]
        array_literal1 = val_decl1["value"]
        assert len(array_literal1["elements"]) == 1

        # Large number of elements
        source2 = """
        func test() : void = {
            val many = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        }
        """
        ast2 = self.parser.parse(source2)
        func2 = ast2["functions"][0]
        val_decl2 = func2["body"]["statements"][0]
        array_literal2 = val_decl2["value"]
        assert len(array_literal2["elements"]) == 10