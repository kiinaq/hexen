"""
Test suite for loop parser transformers

This module tests that the parser correctly transforms loop grammar
into AST nodes with the proper structure and fields.
"""

import pytest
from src.hexen.parser import HexenParser
from src.hexen.ast_nodes import NodeType


@pytest.fixture
def parser():
    """Create a fresh parser instance"""
    return HexenParser()


class TestForInLoopTransformer:
    """Test for-in loop transformer"""

    def test_basic_for_in_loop(self, parser):
        """Test: for i in 1..10 { }"""
        code = """
        for i in 1..10 {
        }
        """
        ast = parser.parse(code)

        # Verify program structure
        assert ast["type"] == NodeType.PROGRAM.value
        assert "statements" in ast
        assert len(ast["statements"]) == 1

        # Verify for-in loop structure
        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "i"
        assert loop["variable_type"] is None
        assert loop["iterable"]["type"] == NodeType.RANGE_EXPR.value
        assert loop["body"]["type"] == NodeType.BLOCK.value

    def test_for_in_with_type_annotation(self, parser):
        """Test: for i : i32 in 1..10 { }"""
        code = """
        for i : i32 in 1..10 {
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "i"
        assert loop["variable_type"] == "i32"
        assert loop["iterable"]["type"] == NodeType.RANGE_EXPR.value

    def test_for_in_with_body_statements(self, parser):
        """Test: for i in 1..10 { val x = i }"""
        code = """
        for i in 1..10 {
            val x = i
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["body"]["type"] == NodeType.BLOCK.value
        assert len(loop["body"]["statements"]) == 1
        assert loop["body"]["statements"][0]["type"] == NodeType.VAL_DECLARATION.value

    def test_for_in_expression_mode(self, parser):
        """Test: val result : [_]i32 = for i in 1..10 { -> i }"""
        code = """
        val result : [_]i32 = for i in 1..10 {
            -> i
        }
        """
        ast = parser.parse(code)

        # Verify variable declaration with for-in as value
        decl = ast["statements"][0]
        assert decl["type"] == NodeType.VAL_DECLARATION.value
        assert decl["name"] == "result"

        # Verify for-in loop is the value
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "i"

        # Verify body contains assign statement
        assert len(loop["body"]["statements"]) == 1
        assert loop["body"]["statements"][0]["type"] == NodeType.ASSIGN_STATEMENT.value

    def test_nested_for_in_loops(self, parser):
        """Test: for i in 1..3 { for j in 1..4 { } }"""
        code = """
        for i in 1..3 {
            for j in 1..4 {
            }
        }
        """
        ast = parser.parse(code)

        outer = ast["statements"][0]
        assert outer["type"] == NodeType.FOR_IN_LOOP.value
        assert outer["variable"] == "i"

        # Verify nested loop
        inner = outer["body"]["statements"][0]
        assert inner["type"] == NodeType.FOR_IN_LOOP.value
        assert inner["variable"] == "j"


class TestWhileLoopTransformer:
    """Test while loop transformer"""

    def test_basic_while_loop(self, parser):
        """Test: while condition { }"""
        code = """
        val condition : bool = true
        while condition {
        }
        """
        ast = parser.parse(code)

        # Get the while loop (second statement)
        loop = ast["statements"][1]
        assert loop["type"] == NodeType.WHILE_LOOP.value
        assert loop["condition"]["type"] == NodeType.IDENTIFIER.value
        assert loop["condition"]["name"] == "condition"
        assert loop["body"]["type"] == NodeType.BLOCK.value

    def test_while_true(self, parser):
        """Test: while true { }"""
        code = """
        while true {
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        assert loop["type"] == NodeType.WHILE_LOOP.value
        assert loop["condition"]["type"] == NodeType.LITERAL.value
        assert loop["condition"]["value"] is True

    def test_while_with_body(self, parser):
        """Test: while condition { val x = 42 }"""
        code = """
        while true {
            val x : i32 = 42
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        assert loop["type"] == NodeType.WHILE_LOOP.value
        assert len(loop["body"]["statements"]) == 1
        assert loop["body"]["statements"][0]["type"] == NodeType.VAL_DECLARATION.value


class TestBreakContinueTransformer:
    """Test break and continue statement transformers"""

    def test_simple_break(self, parser):
        """Test: break"""
        code = """
        for i in 1..10 {
            break
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        break_stmt = loop["body"]["statements"][0]
        assert break_stmt["type"] == NodeType.BREAK_STATEMENT.value
        assert break_stmt["label"] is None

    def test_labeled_break(self, parser):
        """Test: break outer"""
        code = """
        for i in 1..10 {
            break outer
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        break_stmt = loop["body"]["statements"][0]
        assert break_stmt["type"] == NodeType.BREAK_STATEMENT.value
        assert break_stmt["label"] == "outer"

    def test_simple_continue(self, parser):
        """Test: continue"""
        code = """
        for i in 1..10 {
            continue
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        continue_stmt = loop["body"]["statements"][0]
        assert continue_stmt["type"] == NodeType.CONTINUE_STATEMENT.value
        assert continue_stmt["label"] is None

    def test_labeled_continue(self, parser):
        """Test: continue outer"""
        code = """
        for i in 1..10 {
            continue outer
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        continue_stmt = loop["body"]["statements"][0]
        assert continue_stmt["type"] == NodeType.CONTINUE_STATEMENT.value
        assert continue_stmt["label"] == "outer"


class TestLabeledStatementTransformer:
    """Test labeled statement transformer"""

    def test_labeled_for_in(self, parser):
        """Test: outer: for i in 1..10 { }"""
        code = """
        outer: for i in 1..10 {
        }
        """
        ast = parser.parse(code)

        labeled = ast["statements"][0]
        assert labeled["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled["label"] == "outer"

        # Verify inner statement is for-in loop
        loop = labeled["statement"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "i"

    def test_labeled_while(self, parser):
        """Test: outer: while condition { }"""
        code = """
        outer: while true {
        }
        """
        ast = parser.parse(code)

        labeled = ast["statements"][0]
        assert labeled["type"] == NodeType.LABELED_STATEMENT.value
        assert labeled["label"] == "outer"

        # Verify inner statement is while loop
        loop = labeled["statement"]
        assert loop["type"] == NodeType.WHILE_LOOP.value

    def test_nested_labeled_loops(self, parser):
        """Test: outer: for { inner: for { } }"""
        code = """
        outer: for i in 1..10 {
            inner: for j in 1..10 {
            }
        }
        """
        ast = parser.parse(code)

        outer_labeled = ast["statements"][0]
        assert outer_labeled["type"] == NodeType.LABELED_STATEMENT.value
        assert outer_labeled["label"] == "outer"

        outer_loop = outer_labeled["statement"]
        assert outer_loop["type"] == NodeType.FOR_IN_LOOP.value

        # Verify inner labeled statement
        inner_labeled = outer_loop["body"]["statements"][0]
        assert inner_labeled["type"] == NodeType.LABELED_STATEMENT.value
        assert inner_labeled["label"] == "inner"

        inner_loop = inner_labeled["statement"]
        assert inner_loop["type"] == NodeType.FOR_IN_LOOP.value


class TestComplexLoopPatterns:
    """Test complex loop patterns from specification"""

    def test_filtering_pattern(self, parser):
        """Test: for with conditional filtering"""
        code = """
        val evens : [_]i32 = for i in 1..10 {
            if true {
                -> i
            }
        }
        """
        ast = parser.parse(code)

        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

        # Verify conditional in body
        assert len(loop["body"]["statements"]) == 1
        assert loop["body"]["statements"][0]["type"] == NodeType.CONDITIONAL_STATEMENT.value

    def test_early_termination(self, parser):
        """Test: for with break"""
        code = """
        val partial : [_]i32 = for i in 1..100 {
            if true {
                break
            }
            -> i
        }
        """
        ast = parser.parse(code)

        decl = ast["statements"][0]
        loop = decl["value"]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

        # Verify conditional and assign statements
        assert len(loop["body"]["statements"]) == 2

    def test_labeled_break_in_nested(self, parser):
        """Test: break outer from inner loop"""
        code = """
        outer: for i in 1..10 {
            inner: for j in 1..10 {
                break outer
            }
        }
        """
        ast = parser.parse(code)

        outer_labeled = ast["statements"][0]
        outer_loop = outer_labeled["statement"]
        inner_labeled = outer_loop["body"]["statements"][0]
        inner_loop = inner_labeled["statement"]

        # Verify break references outer label
        break_stmt = inner_loop["body"]["statements"][0]
        assert break_stmt["type"] == NodeType.BREAK_STATEMENT.value
        assert break_stmt["label"] == "outer"

    def test_nested_loop_expression(self, parser):
        """Test: val matrix = for i { -> for j { -> i*j } }"""
        code = """
        val matrix : [_][_]i32 = for i in 1..3 {
            -> for j in 1..4 {
                -> i
            }
        }
        """
        ast = parser.parse(code)

        decl = ast["statements"][0]
        outer_loop = decl["value"]
        assert outer_loop["type"] == NodeType.FOR_IN_LOOP.value

        # Verify assign statement contains inner loop
        assign_stmt = outer_loop["body"]["statements"][0]
        assert assign_stmt["type"] == NodeType.ASSIGN_STATEMENT.value

        inner_loop = assign_stmt["value"]
        assert inner_loop["type"] == NodeType.FOR_IN_LOOP.value


class TestLoopIntegration:
    """Integration tests with other language features"""

    def test_loop_with_function_call(self, parser):
        """Test: for loop with function calls in body"""
        code = """
        func print(x : i32) : void = {
        }

        for i in 1..10 {
            print(i)
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][0]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value

        call_stmt = loop["body"]["statements"][0]
        assert call_stmt["type"] == NodeType.FUNCTION_CALL_STATEMENT.value

    def test_loop_with_array_iteration(self, parser):
        """Test: for loop iterating over array"""
        code = """
        val data : [_]i32 = [1, 2, 3]
        for elem in data {
            val x = elem
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][1]
        assert loop["type"] == NodeType.FOR_IN_LOOP.value
        assert loop["variable"] == "elem"
        assert loop["iterable"]["type"] == NodeType.IDENTIFIER.value
        assert loop["iterable"]["name"] == "data"

    def test_while_with_comparison(self, parser):
        """Test: while loop with comparison condition"""
        code = """
        val count : i32 = 0
        while count < 10 {
            val x = count
        }
        """
        ast = parser.parse(code)

        loop = ast["statements"][1]
        assert loop["type"] == NodeType.WHILE_LOOP.value
        assert loop["condition"]["type"] == NodeType.BINARY_OPERATION.value
        assert loop["condition"]["operator"] == "<"
