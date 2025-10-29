"""
Tests for loop context tracking infrastructure (Phase 1).

These tests verify that the foundational loop tracking system is working:
- LoopContext creation and initialization
- Loop stack management
- Label stack management
"""

import pytest
from src.hexen.semantic.types import HexenType, LoopContext, RangeType
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestLoopContextCreation:
    """Test LoopContext dataclass creation and initialization."""

    def test_loop_context_for_in_basic(self):
        """Test: Create basic for-in loop context"""
        context = LoopContext(
            loop_type="for-in",
            variable_name="i",
            variable_type=HexenType.I32,
        )

        assert context.loop_type == "for-in"
        assert context.variable_name == "i"
        assert context.variable_type == HexenType.I32
        assert context.label is None
        assert context.is_expression_mode is False
        assert context.iterable_type is None

    def test_loop_context_for_in_with_label(self):
        """Test: Create labeled for-in loop context"""
        context = LoopContext(
            loop_type="for-in",
            label="outer",
            variable_name="i",
            variable_type=HexenType.I64,
        )

        assert context.loop_type == "for-in"
        assert context.label == "outer"
        assert context.variable_name == "i"
        assert context.variable_type == HexenType.I64

    def test_loop_context_for_in_expression_mode(self):
        """Test: Create for-in loop context in expression mode"""
        context = LoopContext(
            loop_type="for-in",
            is_expression_mode=True,
            variable_name="i",
            variable_type=HexenType.COMPTIME_INT,
        )

        assert context.loop_type == "for-in"
        assert context.is_expression_mode is True
        assert context.variable_name == "i"
        assert context.variable_type == HexenType.COMPTIME_INT

    def test_loop_context_while_basic(self):
        """Test: Create basic while loop context"""
        context = LoopContext(loop_type="while")

        assert context.loop_type == "while"
        assert context.label is None
        assert context.is_expression_mode is False
        assert context.variable_name is None
        assert context.variable_type is None

    def test_loop_context_while_with_label(self):
        """Test: Create labeled while loop context"""
        context = LoopContext(
            loop_type="while",
            label="retry",
        )

        assert context.loop_type == "while"
        assert context.label == "retry"

    def test_loop_context_str_representation(self):
        """Test: LoopContext string representation"""
        context1 = LoopContext(loop_type="for-in", variable_name="i", variable_type=HexenType.I32)
        assert "for-in" in str(context1)
        assert "statement" in str(context1)

        context2 = LoopContext(
            loop_type="for-in",
            label="outer",
            is_expression_mode=True,
            variable_name="x",
            variable_type=HexenType.F64,
        )
        assert "outer" in str(context2)
        assert "expression" in str(context2)
        assert "x" in str(context2)

    def test_loop_context_repr(self):
        """Test: LoopContext repr for debugging"""
        context = LoopContext(
            loop_type="for-in",
            label="outer",
            is_expression_mode=True,
            variable_name="i",
        )

        repr_str = repr(context)
        assert "LoopContext" in repr_str
        assert "for-in" in repr_str
        assert "outer" in repr_str


class TestLoopStackInitialization:
    """Test loop stack initialization in SemanticAnalyzer."""

    def test_analyzer_has_loop_stack(self):
        """Test: SemanticAnalyzer initializes with empty loop stack"""
        analyzer = SemanticAnalyzer()

        assert hasattr(analyzer, "loop_stack")
        assert isinstance(analyzer.loop_stack, list)
        assert len(analyzer.loop_stack) == 0

    def test_analyzer_has_label_stack(self):
        """Test: SemanticAnalyzer initializes with empty label stack"""
        analyzer = SemanticAnalyzer()

        assert hasattr(analyzer, "label_stack")
        assert isinstance(analyzer.label_stack, dict)
        assert len(analyzer.label_stack) == 0

    def test_loop_stack_append_and_pop(self):
        """Test: Loop stack supports basic push/pop operations"""
        analyzer = SemanticAnalyzer()

        context = LoopContext(loop_type="for-in", variable_name="i", variable_type=HexenType.I32)

        # Push context
        analyzer.loop_stack.append(context)
        assert len(analyzer.loop_stack) == 1
        assert analyzer.loop_stack[0] == context

        # Pop context
        popped = analyzer.loop_stack.pop()
        assert popped == context
        assert len(analyzer.loop_stack) == 0

    def test_label_stack_add_and_remove(self):
        """Test: Label stack supports add/remove operations"""
        analyzer = SemanticAnalyzer()

        context = LoopContext(
            loop_type="for-in", label="outer", variable_name="i", variable_type=HexenType.I32
        )

        # Add label
        analyzer.label_stack["outer"] = context
        assert len(analyzer.label_stack) == 1
        assert analyzer.label_stack["outer"] == context

        # Remove label
        del analyzer.label_stack["outer"]
        assert len(analyzer.label_stack) == 0

    def test_nested_loop_stack(self):
        """Test: Loop stack handles nested loops"""
        analyzer = SemanticAnalyzer()

        outer_context = LoopContext(
            loop_type="for-in", label="outer", variable_name="i", variable_type=HexenType.I32
        )

        inner_context = LoopContext(
            loop_type="for-in", label="inner", variable_name="j", variable_type=HexenType.I32
        )

        # Push outer loop
        analyzer.loop_stack.append(outer_context)
        assert len(analyzer.loop_stack) == 1

        # Push inner loop
        analyzer.loop_stack.append(inner_context)
        assert len(analyzer.loop_stack) == 2
        assert analyzer.loop_stack[0] == outer_context
        assert analyzer.loop_stack[1] == inner_context

        # Pop inner loop
        analyzer.loop_stack.pop()
        assert len(analyzer.loop_stack) == 1
        assert analyzer.loop_stack[0] == outer_context

        # Pop outer loop
        analyzer.loop_stack.pop()
        assert len(analyzer.loop_stack) == 0

    def test_multiple_labels_in_scope(self):
        """Test: Label stack handles multiple labels simultaneously"""
        analyzer = SemanticAnalyzer()

        outer_context = LoopContext(
            loop_type="for-in", label="outer", variable_name="i", variable_type=HexenType.I32
        )

        inner_context = LoopContext(
            loop_type="while", label="inner"
        )

        # Add both labels
        analyzer.label_stack["outer"] = outer_context
        analyzer.label_stack["inner"] = inner_context

        assert len(analyzer.label_stack) == 2
        assert "outer" in analyzer.label_stack
        assert "inner" in analyzer.label_stack
        assert analyzer.label_stack["outer"] == outer_context
        assert analyzer.label_stack["inner"] == inner_context


class TestLoopContextWithIterableTypes:
    """Test LoopContext with various iterable types."""

    def test_loop_context_with_range_type(self):
        """Test: LoopContext with RangeType iterable"""
        range_type = RangeType(
            element_type=HexenType.I32,
            has_start=True,
            has_end=True,
            has_step=False,
            inclusive=False,
        )

        context = LoopContext(
            loop_type="for-in",
            iterable_type=range_type,
            variable_name="i",
            variable_type=HexenType.I32,
        )

        assert context.iterable_type == range_type
        assert isinstance(context.iterable_type, RangeType)
        assert context.iterable_type.element_type == HexenType.I32

    def test_loop_context_with_comptime_int(self):
        """Test: LoopContext with comptime_int iterable"""
        context = LoopContext(
            loop_type="for-in",
            iterable_type=HexenType.COMPTIME_INT,
            variable_name="i",
            variable_type=HexenType.COMPTIME_INT,
        )

        assert context.iterable_type == HexenType.COMPTIME_INT
        assert context.variable_type == HexenType.COMPTIME_INT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
