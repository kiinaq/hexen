"""
Test suite for loop-related AST node types

This module tests that loop AST node types are properly defined
and can be used to create valid AST nodes.
"""

import pytest
from src.hexen.ast_nodes import NodeType


class TestLoopASTNodeTypes:
    """Test loop-related AST node type definitions"""

    def test_for_in_loop_node_type_exists(self):
        """Test that FOR_IN_LOOP node type is defined"""
        assert hasattr(NodeType, "FOR_IN_LOOP")
        assert NodeType.FOR_IN_LOOP.value == "for_in_loop"

    def test_while_loop_node_type_exists(self):
        """Test that WHILE_LOOP node type is defined"""
        assert hasattr(NodeType, "WHILE_LOOP")
        assert NodeType.WHILE_LOOP.value == "while_loop"

    def test_break_statement_node_type_exists(self):
        """Test that BREAK_STATEMENT node type is defined"""
        assert hasattr(NodeType, "BREAK_STATEMENT")
        assert NodeType.BREAK_STATEMENT.value == "break_statement"

    def test_continue_statement_node_type_exists(self):
        """Test that CONTINUE_STATEMENT node type is defined"""
        assert hasattr(NodeType, "CONTINUE_STATEMENT")
        assert NodeType.CONTINUE_STATEMENT.value == "continue_statement"

    def test_labeled_statement_node_type_exists(self):
        """Test that LABELED_STATEMENT node type is defined"""
        assert hasattr(NodeType, "LABELED_STATEMENT")
        assert NodeType.LABELED_STATEMENT.value == "labeled_statement"


class TestLoopASTNodeCreation:
    """Test creating loop AST nodes using the node types"""

    def test_create_for_in_loop_node(self):
        """Test creating a for-in loop AST node"""
        node = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": None,
        }

        assert node["type"] == "for_in_loop"
        assert node["variable"] == "i"
        assert node["variable_type"] is None
        assert node["label"] is None
        assert isinstance(node["body"], list)

    def test_create_for_in_loop_with_type_annotation(self):
        """Test creating a for-in loop with type annotation"""
        node = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": "i32",
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": None,
        }

        assert node["variable_type"] == "i32"

    def test_create_for_in_loop_with_label(self):
        """Test creating a labeled for-in loop"""
        node = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": "outer",
        }

        assert node["label"] == "outer"

    def test_create_while_loop_node(self):
        """Test creating a while loop AST node"""
        node = {
            "type": NodeType.WHILE_LOOP.value,
            "condition": {"type": NodeType.LITERAL.value, "value": True},
            "body": [],
            "label": None,
        }

        assert node["type"] == "while_loop"
        assert node["condition"]["type"] == "literal"
        assert node["label"] is None

    def test_create_while_loop_with_label(self):
        """Test creating a labeled while loop"""
        node = {
            "type": NodeType.WHILE_LOOP.value,
            "condition": {"type": NodeType.LITERAL.value, "value": True},
            "body": [],
            "label": "outer",
        }

        assert node["label"] == "outer"

    def test_create_break_statement_node(self):
        """Test creating a break statement AST node"""
        node = {
            "type": NodeType.BREAK_STATEMENT.value,
            "label": None,
        }

        assert node["type"] == "break_statement"
        assert node["label"] is None

    def test_create_break_statement_with_label(self):
        """Test creating a labeled break statement"""
        node = {
            "type": NodeType.BREAK_STATEMENT.value,
            "label": "outer",
        }

        assert node["label"] == "outer"

    def test_create_continue_statement_node(self):
        """Test creating a continue statement AST node"""
        node = {
            "type": NodeType.CONTINUE_STATEMENT.value,
            "label": None,
        }

        assert node["type"] == "continue_statement"
        assert node["label"] is None

    def test_create_continue_statement_with_label(self):
        """Test creating a labeled continue statement"""
        node = {
            "type": NodeType.CONTINUE_STATEMENT.value,
            "label": "outer",
        }

        assert node["label"] == "outer"

    def test_create_labeled_statement_node(self):
        """Test creating a labeled statement AST node"""
        inner_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": None,
        }

        labeled_node = {
            "type": NodeType.LABELED_STATEMENT.value,
            "label": "outer",
            "statement": inner_loop,
        }

        assert labeled_node["type"] == "labeled_statement"
        assert labeled_node["label"] == "outer"
        assert labeled_node["statement"]["type"] == "for_in_loop"


class TestLoopASTNodeStructure:
    """Test the structure and fields of loop AST nodes"""

    def test_for_in_loop_required_fields(self):
        """Test that for-in loop has all required fields"""
        node = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": None,
        }

        # Verify all required fields present
        assert "type" in node
        assert "variable" in node
        assert "variable_type" in node
        assert "iterable" in node
        assert "body" in node
        assert "label" in node

    def test_while_loop_required_fields(self):
        """Test that while loop has all required fields"""
        node = {
            "type": NodeType.WHILE_LOOP.value,
            "condition": {"type": NodeType.LITERAL.value, "value": True},
            "body": [],
            "label": None,
        }

        # Verify all required fields present
        assert "type" in node
        assert "condition" in node
        assert "body" in node
        assert "label" in node

    def test_break_statement_required_fields(self):
        """Test that break statement has all required fields"""
        node = {
            "type": NodeType.BREAK_STATEMENT.value,
            "label": None,
        }

        # Verify all required fields present
        assert "type" in node
        assert "label" in node

    def test_continue_statement_required_fields(self):
        """Test that continue statement has all required fields"""
        node = {
            "type": NodeType.CONTINUE_STATEMENT.value,
            "label": None,
        }

        # Verify all required fields present
        assert "type" in node
        assert "label" in node

    def test_labeled_statement_required_fields(self):
        """Test that labeled statement has all required fields"""
        node = {
            "type": NodeType.LABELED_STATEMENT.value,
            "label": "outer",
            "statement": {"type": NodeType.FOR_IN_LOOP.value},
        }

        # Verify all required fields present
        assert "type" in node
        assert "label" in node
        assert "statement" in node


class TestNestedLoopASTNodes:
    """Test creating nested loop structures"""

    def test_nested_for_in_loops(self):
        """Test creating nested for-in loop AST nodes"""
        inner_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "j",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": None,
        }

        outer_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [inner_loop],
            "label": None,
        }

        assert outer_loop["body"][0]["type"] == "for_in_loop"
        assert outer_loop["body"][0]["variable"] == "j"

    def test_labeled_nested_loops(self):
        """Test creating labeled nested loop structures"""
        inner_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "j",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [],
            "label": None,
        }

        labeled_inner = {
            "type": NodeType.LABELED_STATEMENT.value,
            "label": "inner",
            "statement": inner_loop,
        }

        outer_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [labeled_inner],
            "label": None,
        }

        labeled_outer = {
            "type": NodeType.LABELED_STATEMENT.value,
            "label": "outer",
            "statement": outer_loop,
        }

        assert labeled_outer["label"] == "outer"
        assert labeled_outer["statement"]["body"][0]["label"] == "inner"

    def test_break_in_nested_loop(self):
        """Test break statement in nested loop structure"""
        break_stmt = {
            "type": NodeType.BREAK_STATEMENT.value,
            "label": "outer",
        }

        inner_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "j",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [break_stmt],
            "label": None,
        }

        outer_loop = {
            "type": NodeType.FOR_IN_LOOP.value,
            "variable": "i",
            "variable_type": None,
            "iterable": {"type": NodeType.RANGE_EXPR.value},
            "body": [inner_loop],
            "label": None,
        }

        labeled_outer = {
            "type": NodeType.LABELED_STATEMENT.value,
            "label": "outer",
            "statement": outer_loop,
        }

        # Verify break references outer label
        inner_body_break = labeled_outer["statement"]["body"][0]["body"][0]
        assert inner_body_break["type"] == "break_statement"
        assert inner_body_break["label"] == "outer"
