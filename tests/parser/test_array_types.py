"""
Parser tests for array type declarations.

Tests array type syntax parsing including:
- Fixed-size arrays: [N]T
- Inferred-size arrays: [_]T  
- Multidimensional arrays: [N][M]T
- Complex nested cases
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestArrayTypes:
    """Test array type declaration parsing"""

    def setup_method(self):
        """Set up parser for each test"""
        self.parser = HexenParser()

    def test_fixed_size_array_type_basic(self):
        """Test basic fixed-size array types: [3]i32"""
        source = """
        func test() : void = {
            val numbers : [3]i32 = [1, 2, 3]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_type = val_decl["type_annotation"]
        
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(array_type["dimensions"]) == 1
        assert array_type["dimensions"][0]["type"] == NodeType.ARRAY_DIMENSION.value
        assert array_type["dimensions"][0]["size"] == 3
        assert array_type["element_type"] == "i32"

    def test_fixed_size_array_types_all_primitives(self):
        """Test fixed-size arrays with all primitive types"""
        test_cases = [
            ("[5]i32", "i32"),
            ("[10]i64", "i64"),
            ("[4]f32", "f32"),
            ("[8]f64", "f64"),
            ("[2]string", "string"),
            ("[1]bool", "bool"),
        ]
        
        for array_type_str, expected_element_type in test_cases:
            source = f"""
            func test() : void = {{
                val arr : {array_type_str} = []
            }}
            """
            ast = self.parser.parse(source)
            
            # Navigate to array type
            func = ast["functions"][0]
            val_decl = func["body"]["statements"][0]
            array_type = val_decl["type_annotation"]
            
            assert array_type["type"] == NodeType.ARRAY_TYPE.value
            assert array_type["element_type"] == expected_element_type

    def test_inferred_size_array_type_basic(self):
        """Test basic inferred-size array types: [_]T"""
        source = """
        func test() : void = {
            val numbers : [_]i32 = [1, 2, 3]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_type = val_decl["type_annotation"]
        
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(array_type["dimensions"]) == 1
        assert array_type["dimensions"][0]["type"] == NodeType.ARRAY_DIMENSION.value
        assert array_type["dimensions"][0]["size"] == "_"
        assert array_type["element_type"] == "i32"

    def test_inferred_size_array_types_all_primitives(self):
        """Test inferred-size arrays with all primitive types"""
        test_cases = [
            ("[_]i32", "i32"),
            ("[_]i64", "i64"),
            ("[_]f32", "f32"),
            ("[_]f64", "f64"),
            ("[_]string", "string"),
            ("[_]bool", "bool"),
        ]
        
        for array_type_str, expected_element_type in test_cases:
            source = f"""
            func test() : void = {{
                val arr : {array_type_str} = []
            }}
            """
            ast = self.parser.parse(source)
            
            # Navigate to array type
            func = ast["functions"][0]
            val_decl = func["body"]["statements"][0]
            array_type = val_decl["type_annotation"]
            
            assert array_type["type"] == NodeType.ARRAY_TYPE.value
            assert array_type["element_type"] == expected_element_type

    def test_multidimensional_array_type_2d_fixed(self):
        """Test 2D fixed-size multidimensional arrays: [2][3]i32"""
        source = """
        func test() : void = {
            val matrix : [2][3]i32 = [[1, 2, 3], [4, 5, 6]]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_type = val_decl["type_annotation"]
        
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(array_type["dimensions"]) == 2
        
        # First dimension [2]
        assert array_type["dimensions"][0]["type"] == NodeType.ARRAY_DIMENSION.value
        assert array_type["dimensions"][0]["size"] == 2
        
        # Second dimension [3]
        assert array_type["dimensions"][1]["type"] == NodeType.ARRAY_DIMENSION.value
        assert array_type["dimensions"][1]["size"] == 3
        
        assert array_type["element_type"] == "i32"

    def test_multidimensional_array_type_2d_inferred(self):
        """Test 2D inferred-size multidimensional arrays: [_][_]f64"""
        source = """
        func test() : void = {
            val matrix : [_][_]f64 = [[1.1, 2.2], [3.3, 4.4]]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_type = val_decl["type_annotation"]
        
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(array_type["dimensions"]) == 2
        
        # Both dimensions inferred
        assert array_type["dimensions"][0]["size"] == "_"
        assert array_type["dimensions"][1]["size"] == "_"
        
        assert array_type["element_type"] == "f64"

    def test_multidimensional_array_type_mixed_sizes(self):
        """Test mixed fixed/inferred sizes: [2][_]i32, [_][3]f32"""
        test_cases = [
            ("[2][_]i32", [2, "_"], "i32"),
            ("[_][3]f32", ["_", 3], "f32"),
            ("[5][_]string", [5, "_"], "string"),
        ]
        
        for array_type_str, expected_sizes, expected_element_type in test_cases:
            source = f"""
            func test() : void = {{
                val arr : {array_type_str} = []
            }}
            """
            ast = self.parser.parse(source)
            
            # Navigate to array type
            func = ast["functions"][0]
            val_decl = func["body"]["statements"][0]
            array_type = val_decl["type_annotation"]
            
            assert array_type["type"] == NodeType.ARRAY_TYPE.value
            assert len(array_type["dimensions"]) == len(expected_sizes)
            
            for i, expected_size in enumerate(expected_sizes):
                assert array_type["dimensions"][i]["size"] == expected_size
            
            assert array_type["element_type"] == expected_element_type

    def test_multidimensional_array_type_3d(self):
        """Test 3D arrays: [2][2][2]i32"""
        source = """
        func test() : void = {
            val cube : [2][2][2]i32 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_type = val_decl["type_annotation"]
        
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(array_type["dimensions"]) == 3
        
        # All dimensions should be size 2
        for dim in array_type["dimensions"]:
            assert dim["type"] == NodeType.ARRAY_DIMENSION.value
            assert dim["size"] == 2
        
        assert array_type["element_type"] == "i32"

    def test_multidimensional_array_type_4d(self):
        """Test 4D arrays: [_][_][_][_]f32"""
        source = """
        func test() : void = {
            val batch : [_][_][_][_]f32 = []
        }
        """
        ast = self.parser.parse(source)
        
        # Navigate to variable declaration
        func = ast["functions"][0]
        val_decl = func["body"]["statements"][0]
        array_type = val_decl["type_annotation"]
        
        assert array_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(array_type["dimensions"]) == 4
        
        # All dimensions should be inferred
        for dim in array_type["dimensions"]:
            assert dim["type"] == NodeType.ARRAY_DIMENSION.value
            assert dim["size"] == "_"
        
        assert array_type["element_type"] == "f32"

    def test_array_type_in_function_parameters(self):
        """Test array types as function parameters"""
        source = """
        func process_array(data: [_]i32, matrix: [3][4]f64) : void = {
            return
        }
        """
        ast = self.parser.parse(source)
        
        func = ast["functions"][0]
        parameters = func["parameters"]
        
        # First parameter: data: [_]i32
        data_param = parameters[0]
        assert data_param["name"] == "data"
        data_type = data_param["param_type"]
        assert data_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(data_type["dimensions"]) == 1
        assert data_type["dimensions"][0]["size"] == "_"
        assert data_type["element_type"] == "i32"
        
        # Second parameter: matrix: [3][4]f64
        matrix_param = parameters[1]
        assert matrix_param["name"] == "matrix"
        matrix_type = matrix_param["param_type"]
        assert matrix_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(matrix_type["dimensions"]) == 2
        assert matrix_type["dimensions"][0]["size"] == 3
        assert matrix_type["dimensions"][1]["size"] == 4
        assert matrix_type["element_type"] == "f64"

    def test_array_type_in_function_return_type(self):
        """Test array types as function return types"""
        source = """
        func create_matrix() : [2][3]i32 = {
            return [[1, 2, 3], [4, 5, 6]]
        }
        """
        ast = self.parser.parse(source)
        
        func = ast["functions"][0]
        return_type = func["return_type"]
        
        assert return_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(return_type["dimensions"]) == 2
        assert return_type["dimensions"][0]["size"] == 2
        assert return_type["dimensions"][1]["size"] == 3
        assert return_type["element_type"] == "i32"

    def test_array_type_edge_cases(self):
        """Test edge cases for array types"""
        # Large dimension sizes
        source1 = """
        func test() : void = {
            val big_array : [1000]i64 = []
        }
        """
        ast1 = self.parser.parse(source1)
        func1 = ast1["functions"][0]
        val_decl1 = func1["body"]["statements"][0]
        array_type1 = val_decl1["type_annotation"]
        assert array_type1["dimensions"][0]["size"] == 1000

        # Single element arrays
        source2 = """
        func test() : void = {
            val single : [1]string = ["hello"]
        }
        """
        ast2 = self.parser.parse(source2)
        func2 = ast2["functions"][0]
        val_decl2 = func2["body"]["statements"][0]
        array_type2 = val_decl2["type_annotation"]
        assert array_type2["dimensions"][0]["size"] == 1
        assert array_type2["element_type"] == "string"

    def test_complex_nested_array_types(self):
        """Test complex combinations of array types"""
        source = """
        func complex_arrays() : void = {
            val arr1 : [5][_][3]f32 = []
            val arr2 : [_][10][_][2]i64 = []
        }
        """
        ast = self.parser.parse(source)
        
        func = ast["functions"][0]
        statements = func["body"]["statements"]
        
        # First array: [5][_][3]f32
        arr1_type = statements[0]["type_annotation"]
        assert arr1_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(arr1_type["dimensions"]) == 3
        assert arr1_type["dimensions"][0]["size"] == 5
        assert arr1_type["dimensions"][1]["size"] == "_"
        assert arr1_type["dimensions"][2]["size"] == 3
        assert arr1_type["element_type"] == "f32"
        
        # Second array: [_][10][_][2]i64
        arr2_type = statements[1]["type_annotation"]
        assert arr2_type["type"] == NodeType.ARRAY_TYPE.value
        assert len(arr2_type["dimensions"]) == 4
        assert arr2_type["dimensions"][0]["size"] == "_"
        assert arr2_type["dimensions"][1]["size"] == 10
        assert arr2_type["dimensions"][2]["size"] == "_"
        assert arr2_type["dimensions"][3]["size"] == 2
        assert arr2_type["element_type"] == "i64"