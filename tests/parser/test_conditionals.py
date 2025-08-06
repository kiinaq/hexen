"""
Test module for Hexen conditional statement parsing

Tests basic conditional syntax parsing, AST node creation, and error handling
for the foundation of the conditional system implementation.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


class TestConditionalParsing:
    """Test conditional statement parsing foundations"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_basic_if_statement(self):
        """Test basic if statement parsing"""
        source = """
        func test() : void = {
            if true {
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to the conditional statement
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Verify conditional structure
        assert conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        assert conditional["condition"]["type"] == NodeType.LITERAL.value
        assert conditional["condition"]["value"] == True
        assert conditional["if_branch"]["type"] == NodeType.BLOCK.value
        assert len(conditional["else_clauses"]) == 0

    def test_if_else_statement(self):
        """Test if-else statement parsing"""
        source = """
        func test() : void = {
            if false {
                return
            } else {
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to the conditional statement
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Verify conditional structure
        assert conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        assert conditional["condition"]["type"] == NodeType.LITERAL.value
        assert conditional["condition"]["value"] == False
        assert conditional["if_branch"]["type"] == NodeType.BLOCK.value
        assert len(conditional["else_clauses"]) == 1
        
        # Verify else clause
        else_clause = conditional["else_clauses"][0]
        assert else_clause["type"] == NodeType.ELSE_CLAUSE.value
        assert else_clause["condition"] is None  # Final else has no condition
        assert else_clause["branch"]["type"] == NodeType.BLOCK.value

    def test_else_if_chain(self):
        """Test else-if chain parsing"""
        source = """
        func test() : void = {
            if false {
                return
            } else if true {
                return  
            } else {
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to the conditional statement
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Verify conditional structure
        assert conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        assert len(conditional["else_clauses"]) == 2
        
        # Verify else-if clause
        else_if_clause = conditional["else_clauses"][0]
        assert else_if_clause["type"] == NodeType.ELSE_CLAUSE.value
        assert else_if_clause["condition"] is not None
        assert else_if_clause["condition"]["type"] == NodeType.LITERAL.value
        assert else_if_clause["condition"]["value"] == True
        assert else_if_clause["branch"]["type"] == NodeType.BLOCK.value
        
        # Verify final else clause
        final_else_clause = conditional["else_clauses"][1]
        assert final_else_clause["type"] == NodeType.ELSE_CLAUSE.value
        assert final_else_clause["condition"] is None
        assert final_else_clause["branch"]["type"] == NodeType.BLOCK.value

    def test_conditional_with_comparison_condition(self):
        """Test conditional with comparison expression as condition"""
        source = """
        func test(x : i32) : void = {
            if x > 0 {
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to the conditional statement
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Verify condition is a binary operation
        condition = conditional["condition"]
        assert condition["type"] == NodeType.BINARY_OPERATION.value
        assert condition["operator"] == ">"
        assert condition["left"]["type"] == NodeType.IDENTIFIER.value
        assert condition["left"]["name"] == "x"
        assert condition["right"]["type"] == NodeType.COMPTIME_INT.value
        assert condition["right"]["value"] == 0

    def test_conditional_with_logical_condition(self):
        """Test conditional with logical expression as condition"""
        source = """
        func test(a : bool, b : bool) : void = {
            if a && b {
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to the conditional statement
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Verify condition is a logical operation
        condition = conditional["condition"]
        assert condition["type"] == NodeType.BINARY_OPERATION.value
        assert condition["operator"] == "&&"
        assert condition["left"]["type"] == NodeType.IDENTIFIER.value
        assert condition["left"]["name"] == "a"
        assert condition["right"]["type"] == NodeType.IDENTIFIER.value
        assert condition["right"]["name"] == "b"

    def test_nested_conditionals(self):
        """Test nested conditional statements"""
        source = """
        func test(x : i32) : void = {
            if x > 0 {
                if x > 10 {
                    return
                }
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to outer conditional
        func = ast["functions"][0]
        block = func["body"]
        outer_conditional = block["statements"][0]
        
        assert outer_conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        
        # Navigate to inner conditional
        outer_if_branch = outer_conditional["if_branch"]
        inner_conditional = outer_if_branch["statements"][0]
        
        assert inner_conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        assert inner_conditional["condition"]["operator"] == ">"

    def test_conditional_with_multiple_statements_in_branches(self):
        """Test conditionals with multiple statements in branches"""
        source = """
        func test(x : i32) : void = {
            if x > 0 {
                val positive = true
                return
            } else {
                val negative = false  
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to conditional
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Check if branch has multiple statements
        if_branch = conditional["if_branch"]
        assert len(if_branch["statements"]) == 2
        assert if_branch["statements"][0]["type"] == NodeType.VAL_DECLARATION.value
        assert if_branch["statements"][1]["type"] == NodeType.RETURN_STATEMENT.value
        
        # Check else branch has multiple statements  
        else_clause = conditional["else_clauses"][0]
        else_branch = else_clause["branch"]
        assert len(else_branch["statements"]) == 2
        assert else_branch["statements"][0]["type"] == NodeType.VAL_DECLARATION.value
        assert else_branch["statements"][1]["type"] == NodeType.RETURN_STATEMENT.value

    def test_empty_conditional_branches(self):
        """Test conditionals with empty branches"""
        source = """
        func test() : void = {
            if true {
            } else {
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to conditional
        func = ast["functions"][0]
        block = func["body"]
        conditional = block["statements"][0]
        
        # Verify empty branches parse correctly
        assert conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        assert len(conditional["if_branch"]["statements"]) == 0
        
        else_clause = conditional["else_clauses"][0]
        assert len(else_clause["branch"]["statements"]) == 0


class TestConditionalParsingErrors:
    """Test conditional parsing error handling"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_missing_condition_braces(self):
        """Test error for missing braces around condition - should parse fine with current grammar"""
        # Note: Our grammar doesn't require parentheses around conditions, so this should parse
        source = """
        func test() : void = {
            if true {
                return
            }
        }
        """
        
        # This should parse successfully since we don't require parentheses
        ast = self.parser.parse(source)
        assert ast is not None

    def test_missing_block_braces(self):
        """Test error for missing braces around blocks"""
        source = """
        func test() : void = {
            if true
                return
        }
        """
        
        # This should fail to parse due to missing braces
        with pytest.raises((Exception, SyntaxError)):
            self.parser.parse(source)

    def test_malformed_else_if(self):
        """Test error for malformed else-if syntax"""
        source = """
        func test() : void = {
            if true {
                return
            } else if false
                return
            }
        }
        """
        
        # Should fail because missing braces in else-if branch
        with pytest.raises((Exception, SyntaxError)):
            ast = self.parser.parse(source)

    def test_else_without_if(self):
        """Test error for else without preceding if"""
        source = """
        func test() : void = {
            else {
                return
            }
        }
        """
        
        # Should fail because else without if is invalid
        with pytest.raises((Exception, SyntaxError)):
            self.parser.parse(source)


class TestConditionalSemanticFoundation:
    """Test basic semantic integration for conditionals"""

    def setup_method(self):
        self.parser = HexenParser()

    def test_conditional_ast_node_creation(self):
        """Test that conditional AST nodes are created correctly"""
        source = """
        func test() : void = {
            if true {
                return
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Verify AST structure
        func = ast["functions"][0]
        conditional = func["body"]["statements"][0]
        
        # Test node type constants
        assert conditional["type"] == NodeType.CONDITIONAL_STATEMENT.value
        assert conditional["type"] == "conditional_statement"
        
        # Verify all required fields are present
        required_fields = ["type", "condition", "if_branch", "else_clauses"]
        for field in required_fields:
            assert field in conditional

    def test_else_clause_ast_node_creation(self):
        """Test that else clause AST nodes are created correctly"""
        source = """
        func test() : void = {
            if true {
                return
            } else if false {
                return
            } else {
                return  
            }
        }
        """
        
        ast = self.parser.parse(source)
        
        # Navigate to else clauses
        func = ast["functions"][0]
        conditional = func["body"]["statements"][0]
        
        # Test else-if clause
        else_if_clause = conditional["else_clauses"][0]
        assert else_if_clause["type"] == NodeType.ELSE_CLAUSE.value
        assert else_if_clause["type"] == "else_clause"
        assert else_if_clause["condition"] is not None
        
        # Test final else clause
        final_else_clause = conditional["else_clauses"][1]
        assert final_else_clause["type"] == NodeType.ELSE_CLAUSE.value
        assert final_else_clause["condition"] is None
        
        # Verify all required fields are present
        required_fields = ["type", "condition", "branch"]
        for clause in conditional["else_clauses"]:
            for field in required_fields:
                assert field in clause