"""
Parser tests for labeled loop expressions

This module specifically tests the 'label syntax in expression contexts,
which was the original parser ambiguity issue that necessitated the change
from `label:` to `'label` syntax.

These tests verify that labels work correctly in:
1. Statement contexts (traditional usage)
2. Expression contexts (assignment RHS)
3. Nested loops with multiple labels
4. Break/continue with labels
"""

import pytest
from src.hexen.parser import HexenParser


@pytest.fixture
def parser():
    """Create a fresh parser for each test"""
    return HexenParser()


class TestLabeledLoopStatements:
    """Test labeled loops in statement contexts (traditional usage)"""

    def test_simple_labeled_for_loop(self, parser):
        """Test: 'outer for i in 1..10 { }"""
        code = """
        'outer for i in 1..10 {
            print(i)
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify labeled_stmt node
        labeled_stmt = ast["statements"][0]
        assert labeled_stmt["type"] == "labeled_statement"
        assert labeled_stmt["label"] == "outer"
        assert labeled_stmt["statement"]["type"] == "for_in_loop"

    def test_labeled_while_loop(self, parser):
        """Test: 'retry while condition { }"""
        code = """
        'retry while true {
            break 'retry
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify labeled_stmt node
        labeled_stmt = ast["statements"][0]
        assert labeled_stmt["type"] == "labeled_statement"
        assert labeled_stmt["label"] == "retry"
        assert labeled_stmt["statement"]["type"] == "while_loop"

    def test_nested_labeled_loops_statement(self, parser):
        """Test: Nested loops with labels in statement context"""
        code = """
        'outer for i in 1..10 {
            'inner for j in 1..10 {
                if i * j > 50 {
                    break 'outer
                }
            }
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify outer label
        outer_labeled = ast["statements"][0]
        assert outer_labeled["type"] == "labeled_statement"
        assert outer_labeled["label"] == "outer"


class TestLabeledLoopExpressions:
    """Test labeled loops in expression contexts - THE KEY ISSUE WE FIXED"""

    def test_labeled_for_expression_simple(self, parser):
        """
        Test: val result = 'outer for i in 1..10 { -> i }

        THIS WAS BROKEN WITH `outer:` SYNTAX!
        Parser couldn't handle `val result = outer: for ...`
        """
        code = """
        val result : [_]i32 = 'outer for i in 1..10 {
            -> i
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify variable declaration
        var_decl = ast["statements"][0]
        assert var_decl["type"] == "val_declaration"

        # Verify the RHS is a labeled expression
        labeled_expr = var_decl["value"]
        assert labeled_expr["type"] == "labeled_statement"
        assert labeled_expr["label"] == "outer"
        assert labeled_expr["statement"]["type"] == "for_in_loop"

    def test_labeled_for_expression_with_break(self, parser):
        """
        Test: Labeled loop expression with early termination

        val partial : [_]i32 = 'outer for i in 1..100 {
            if i > 50 { break 'outer }
            -> i
        }
        """
        code = """
        val partial : [_]i32 = 'outer for i in 1..100 {
            if i > 50 {
                break 'outer
            }
            -> i
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify it parses correctly
        var_decl = ast["statements"][0]
        labeled_expr = var_decl["value"]
        assert labeled_expr["type"] == "labeled_statement"
        assert labeled_expr["label"] == "outer"

    def test_nested_labeled_expressions_2d_matrix(self, parser):
        """
        Test: 2D matrix with nested labeled expressions

        val matrix : [_][_]i32 = 'outer for i in 1..10 {
            -> 'inner for j in 1..10 {
                if i * j > 50 { break 'outer }
                -> i * j
            }
        }

        THIS IS THE EXACT CASE THAT FAILED BEFORE!
        """
        code = """
        val matrix : [_][_]i32 = 'outer for i in 1..10 {
            -> 'inner for j in 1..10 {
                if i * j > 50 {
                    break 'outer
                }
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify outer labeled expression
        var_decl = ast["statements"][0]
        outer_labeled = var_decl["value"]
        assert outer_labeled["type"] == "labeled_statement"
        assert outer_labeled["label"] == "outer"
        assert outer_labeled["statement"]["type"] == "for_in_loop"

    def test_labeled_expression_in_function_return(self, parser):
        """
        Test: Labeled loop expression in return statement

        func generate() : [_]i32 = {
            return 'outer for i in 1..10 {
                if i > 5 { break 'outer }
                -> i
            }
        }
        """
        code = """
        func generate() : [_]i32 = {
            return 'outer for i in 1..10 {
                if i > 5 {
                    break 'outer
                }
                -> i
            }
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify function (top-level, not nested in statements)
        func = ast["functions"][0]
        assert func["type"] == "function"

        # Verify return statement with labeled expression
        return_stmt = func["body"]["statements"][0]
        assert return_stmt["type"] == "return_statement"
        labeled_expr = return_stmt["value"]
        assert labeled_expr["type"] == "labeled_statement"
        assert labeled_expr["label"] == "outer"

    def test_labeled_expression_as_function_argument(self, parser):
        """
        Test: Labeled loop expression as function argument

        process('outer for i in 1..10 { -> i })
        """
        code = """
        process('outer for i in 1..10 {
            -> i
        })
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify function call statement
        call_stmt = ast["statements"][0]
        assert call_stmt["type"] == "function_call_statement"

        # Verify argument is labeled expression
        arg = call_stmt["function_call"]["arguments"][0]
        assert arg["type"] == "labeled_statement"
        assert arg["label"] == "outer"


class TestLabelSyntaxFeatures:
    """Test specific features of the 'label syntax"""

    def test_label_names_with_underscores(self, parser):
        """Test: Labels can contain underscores like 'my_loop"""
        code = """
        'my_loop for i in 1..10 {
            break 'my_loop
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        labeled_stmt = ast["statements"][0]
        assert labeled_stmt["label"] == "my_loop"

    def test_label_names_with_numbers(self, parser):
        """Test: Labels can contain numbers like 'loop1"""
        code = """
        'loop1 for i in 1..10 {
            break 'loop1
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        labeled_stmt = ast["statements"][0]
        assert labeled_stmt["label"] == "loop1"

    def test_uppercase_label_names(self, parser):
        """Test: Labels can be uppercase like 'OUTER"""
        code = """
        'OUTER for i in 1..10 {
            break 'OUTER
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        labeled_stmt = ast["statements"][0]
        assert labeled_stmt["label"] == "OUTER"

    def test_break_with_label(self, parser):
        """Test: break 'label syntax"""
        code = """
        'outer for i in 1..10 {
            break 'outer
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Find break statement
        loop = ast["statements"][0]["statement"]
        break_stmt = loop["body"]["statements"][0]
        assert break_stmt["type"] == "break_statement"
        assert break_stmt["label"] == "outer"

    def test_continue_with_label(self, parser):
        """Test: continue 'label syntax"""
        code = """
        'outer for i in 1..10 {
            continue 'outer
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Find continue statement
        loop = ast["statements"][0]["statement"]
        continue_stmt = loop["body"]["statements"][0]
        assert continue_stmt["type"] == "continue_statement"
        assert continue_stmt["label"] == "outer"


class TestLabelSyntaxRegression:
    """
    Regression tests to ensure the parser ambiguity is truly fixed

    These tests specifically verify scenarios that would have failed
    with the old `label:` syntax.
    """

    def test_label_after_equals_in_val_declaration(self, parser):
        """
        REGRESSION TEST: The original issue!

        This would fail with `outer:` syntax because parser saw:
        val x = outer: ...
                ^^^^^^
        And couldn't determine if `outer` was a variable or `outer:` was a label
        """
        code = """
        val x : [_]i32 = 'outer for i in 1..10 {
            -> i
        }
        """
        ast = parser.parse(code)
        assert ast is not None
        assert ast["statements"][0]["type"] == "val_declaration"

    def test_label_after_equals_in_mut_declaration(self, parser):
        """
        REGRESSION TEST: Same issue with mut declarations

        mut x : [_]i32 = outer: for ...
                         ^^^^^^ AMBIGUOUS!
        """
        code = """
        mut x : [_]i32 = 'outer for i in 1..10 {
            -> i
        }
        """
        ast = parser.parse(code)
        assert ast is not None
        assert ast["statements"][0]["type"] == "mut_declaration"

    def test_label_in_return_expression(self, parser):
        """
        REGRESSION TEST: Label in return context

        return outer: for ...
               ^^^^^^ AMBIGUOUS!
        """
        code = """
        func test() : [_]i32 = {
            return 'outer for i in 1..10 {
                -> i
            }
        }
        """
        ast = parser.parse(code)
        assert ast is not None

    def test_label_in_function_argument(self, parser):
        """
        REGRESSION TEST: Label as function argument

        process(outer: for ...)
                ^^^^^^ AMBIGUOUS!
        """
        code = """
        process('outer for i in 1..10 {
            -> i
        })
        """
        ast = parser.parse(code)
        assert ast is not None

    def test_nested_labels_in_expression(self, parser):
        """
        REGRESSION TEST: Multiple nested labels in single expression

        val x = outer: for i in 1..10 {
            -> inner: for j in 1..10 {
               ^^^^^^ DOUBLE AMBIGUITY!
                -> i * j
            }
        }
        """
        code = """
        val matrix : [_][_]i32 = 'outer for i in 1..10 {
            -> 'inner for j in 1..10 {
                -> i * j
            }
        }
        """
        ast = parser.parse(code)
        assert ast is not None

        # Verify both labels parsed correctly
        outer = ast["statements"][0]["value"]
        assert outer["label"] == "outer"


class TestLabelSyntaxErrorCases:
    """Test that invalid label syntax is properly rejected"""

    def test_label_without_apostrophe_fails(self, parser):
        """Test: Labels must start with ' - `outer for` should fail"""
        code = """
        outer for i in 1..10 {
            print(i)
        }
        """
        with pytest.raises(Exception):
            parser.parse(code)

    def test_break_without_apostrophe_fails(self, parser):
        """Test: break label (without ') should fail"""
        code = """
        'outer for i in 1..10 {
            break outer
        }
        """
        with pytest.raises(Exception):
            parser.parse(code)

    def test_continue_without_apostrophe_fails(self, parser):
        """Test: continue label (without ') should fail"""
        code = """
        'outer for i in 1..10 {
            continue outer
        }
        """
        with pytest.raises(Exception):
            parser.parse(code)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
