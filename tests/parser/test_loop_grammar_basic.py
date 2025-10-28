"""
Basic grammar tests for loop system

This module verifies that the Lark grammar can parse basic loop constructs
without errors. It focuses on grammar-level parsing, not AST transformation.
"""

import pytest
from lark import Lark
from pathlib import Path


@pytest.fixture
def grammar():
    """Load the Hexen grammar"""
    grammar_path = Path(__file__).parent.parent.parent / "src" / "hexen" / "hexen.lark"
    with open(grammar_path) as f:
        return Lark(f.read(), start="program", parser="lalr")


class TestForInLoopGrammar:
    """Test for-in loop grammar parsing"""

    def test_basic_for_in_loop(self, grammar):
        """Test: for i in 1..10 { }"""
        code = """
        for i in 1..10 {
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_for_in_with_type_annotation(self, grammar):
        """Test: for i : i32 in 1..10 { }"""
        code = """
        for i : i32 in 1..10 {
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_for_in_with_body(self, grammar):
        """Test: for i in 1..10 { val x = i }"""
        code = """
        for i in 1..10 {
            val x = i
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_for_in_expression_mode(self, grammar):
        """Test: val result : [_]i32 = for i in 1..10 { -> i }"""
        code = """
        val result : [_]i32 = for i in 1..10 {
            -> i
        }
        """
        tree = grammar.parse(code)
        assert tree is not None


class TestWhileLoopGrammar:
    """Test while loop grammar parsing"""

    def test_basic_while_loop(self, grammar):
        """Test: while condition { }"""
        code = """
        val condition : bool = true
        while condition {
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_while_true(self, grammar):
        """Test: while true { }"""
        code = """
        while true {
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_while_with_body(self, grammar):
        """Test: while condition { val x = 42 }"""
        code = """
        val condition : bool = true
        while condition {
            val x : i32 = 42
        }
        """
        tree = grammar.parse(code)
        assert tree is not None


class TestBreakContinueGrammar:
    """Test break and continue statement grammar"""

    def test_simple_break(self, grammar):
        """Test: break"""
        code = """
        for i in 1..10 {
            break
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_labeled_break(self, grammar):
        """Test: break outer"""
        code = """
        for i in 1..10 {
            break outer
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_simple_continue(self, grammar):
        """Test: continue"""
        code = """
        for i in 1..10 {
            continue
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_labeled_continue(self, grammar):
        """Test: continue outer"""
        code = """
        for i in 1..10 {
            continue outer
        }
        """
        tree = grammar.parse(code)
        assert tree is not None


class TestLabeledStatementGrammar:
    """Test labeled statement grammar"""

    def test_labeled_for_in(self, grammar):
        """Test: outer: for i in 1..10 { }"""
        code = """
        outer: for i in 1..10 {
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_labeled_while(self, grammar):
        """Test: outer: while condition { }"""
        code = """
        outer: while true {
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_nested_labeled_loops(self, grammar):
        """Test: outer: for { inner: for { } }"""
        code = """
        outer: for i in 1..10 {
            inner: for j in 1..10 {
            }
        }
        """
        tree = grammar.parse(code)
        assert tree is not None


class TestNestedLoopGrammar:
    """Test nested loop structures"""

    def test_nested_for_in_loops(self, grammar):
        """Test: for i in 1..3 { for j in 1..4 { } }"""
        code = """
        for i in 1..3 {
            for j in 1..4 {
            }
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_for_in_while_nested(self, grammar):
        """Test: for i in 1..10 { while condition { } }"""
        code = """
        for i in 1..10 {
            while true {
                break
            }
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_nested_loop_expression(self, grammar):
        """Test: val matrix = for i { -> for j { -> i*j } }"""
        code = """
        val matrix : [_][_]i32 = for i in 1..3 {
            -> for j in 1..4 {
                -> i
            }
        }
        """
        tree = grammar.parse(code)
        assert tree is not None


class TestComplexLoopPatterns:
    """Test complex loop patterns from LOOP_SYSTEM.md"""

    def test_filtering_pattern(self, grammar):
        """Test: for with conditional filtering"""
        code = """
        val evens : [_]i32 = for i in 1..10 {
            if true {
                -> i
            }
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_early_termination(self, grammar):
        """Test: for with break"""
        code = """
        val partial : [_]i32 = for i in 1..100 {
            if true {
                break
            }
            -> i
        }
        """
        tree = grammar.parse(code)
        assert tree is not None

    def test_labeled_break_in_nested(self, grammar):
        """Test: break outer from inner loop"""
        code = """
        outer: for i in 1..10 {
            inner: for j in 1..10 {
                break outer
            }
        }
        """
        tree = grammar.parse(code)
        assert tree is not None
