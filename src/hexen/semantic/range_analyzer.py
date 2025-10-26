"""
Range Expression Analysis for Hexen Language

Handles semantic analysis of range expressions and types:
- Range bound type validation
- Step requirement checking
- Range type inference
- Comptime range adaptation
- Array indexing validation
"""

from typing import Dict, Optional, Union
from .types import HexenType, RangeType, ComptimeRangeType
from .type_util import (
    resolve_range_element_type,
    can_convert_to_usize,
    is_numeric_type,
)
from ..ast_nodes import NodeType


class RangeAnalyzer:
    """
    Specialized analyzer for range expression validation.

    Implements range system semantics from RANGE_SYSTEM.md:
    - Type consistency checking (start, end, step must match)
    - Float step requirement enforcement
    - Unbounded range step restrictions
    - Comptime range type preservation
    - User type vs index type distinction
    """

    def __init__(
        self,
        error_callback,
        analyze_expression_callback,
    ):
        """Initialize with callbacks to main analyzer"""
        self._error = error_callback
        self._analyze_expression = analyze_expression_callback

    def analyze_range_expr(
        self,
        node: Dict,
        target_type: Optional[Union[HexenType, RangeType]] = None,
    ) -> Union[RangeType, ComptimeRangeType]:
        """
        Analyze a range expression and return its type.

        Validates:
        - Bound type consistency
        - Step requirements (floats, unbounded ranges)
        - Target type compatibility

        Args:
            node: RangeExpr AST node
            target_type: Optional target for context-guided resolution

        Returns:
            RangeType or ComptimeRangeType
        """
        # Extract range components
        start_node = node.get("start")
        end_node = node.get("end")
        step_node = node.get("step")
        inclusive = node.get("inclusive", False)

        # Track what bounds exist
        has_start = start_node is not None
        has_end = end_node is not None
        has_step = step_node is not None

        # VALIDATION 1: Check step restrictions on unbounded ranges
        if has_step and not has_start:
            # Step on ..end or .. is forbidden (grammar should prevent this)
            self._error(
                "Step not allowed on unbounded ranges without start",
                node,
            )
            return RangeType(
                element_type=HexenType.UNKNOWN,
                has_start=False,
                has_end=has_end,
                has_step=has_step,
                inclusive=inclusive,
            )

        # Analyze bound expressions
        start_type = None
        end_type = None
        step_type = None

        # Extract target element type if provided
        target_element_type = None
        if isinstance(target_type, RangeType):
            target_element_type = target_type.element_type
        elif isinstance(target_type, HexenType):
            # Direct type like i32 - this is the element type
            target_element_type = target_type

        if has_start:
            start_type = self._analyze_expression(start_node, target_element_type)
            if not is_numeric_type(start_type):
                self._error(
                    f"Range start must be numeric, got {start_type}",
                    start_node,
                )

        if has_end:
            end_type = self._analyze_expression(end_node, target_element_type)
            if not is_numeric_type(end_type):
                self._error(
                    f"Range end must be numeric, got {end_type}",
                    end_node,
                )

        if has_step:
            step_type = self._analyze_expression(step_node, target_element_type)
            if not is_numeric_type(step_type):
                self._error(
                    f"Range step must be numeric, got {step_type}",
                    step_node,
                )

        # VALIDATION 2: Resolve element type (checks type consistency)
        try:
            element_type = resolve_range_element_type(
                start_type,
                end_type,
                step_type,
                target_element_type,
            )
        except (TypeError, ValueError) as e:
            self._error(str(e), node)
            return RangeType(
                element_type=HexenType.UNKNOWN,
                has_start=has_start,
                has_end=has_end,
                has_step=has_step,
                inclusive=inclusive,
            )

        # VALIDATION 3: Check float step requirement
        if element_type in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}:
            if has_start and has_end and not has_step:
                self._error(
                    f"Float range requires explicit step (got range[{element_type.value}] without step)",
                    node,
                )
                # Continue with error, but return type for further analysis

        # Create appropriate range type
        if element_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            # Comptime range - preserves flexibility
            return ComptimeRangeType(
                element_comptime_type=element_type,
                has_start=has_start,
                has_end=has_end,
                has_step=has_step,
                inclusive=inclusive,
            )
        else:
            # Concrete range type
            return RangeType(
                element_type=element_type,
                has_start=has_start,
                has_end=has_end,
                has_step=has_step,
                inclusive=inclusive,
            )

    def analyze_range_type_annotation(self, node: Dict) -> RangeType:
        """
        Analyze a range type annotation (e.g., range[i32]).

        Args:
            node: RangeType AST node

        Returns:
            RangeType with specified element type
        """
        # Extract element type from annotation
        element_type_node = node.get("element_type")

        # Parse element type (should be a type annotation)
        element_type = self._parse_type_annotation(element_type_node)

        # Validate element type is numeric
        if element_type not in {
            HexenType.I32,
            HexenType.I64,
            HexenType.F32,
            HexenType.F64,
            HexenType.USIZE,
        }:
            self._error(
                f"Range element type must be numeric, got {element_type}",
                element_type_node,
            )
            element_type = HexenType.UNKNOWN

        # Create range type (bounds unknown from annotation alone)
        return RangeType(
            element_type=element_type,
            has_start=True,  # Annotation doesn't specify bounds
            has_end=True,
            has_step=False,
            inclusive=False,
        )

    def validate_range_indexing(
        self,
        array_type,
        range_type: Union[RangeType, ComptimeRangeType],
        node: Dict,
    ) -> bool:
        """
        Validate that range can be used for array indexing.

        Rules from RANGE_SYSTEM.md:
        - Only usize or comptime_int ranges can index arrays
        - User type ranges (i32, i64) require explicit :range[usize] conversion
        - Float ranges CANNOT index arrays (even with conversion)

        Args:
            array_type: Type of array being indexed
            range_type: Type of range index
            node: AST node for error reporting

        Returns:
            True if valid, False if error reported
        """
        # Check if range element type is valid for indexing
        element_type = range_type.element_type

        # Comptime int can adapt to usize (ergonomic!)
        if element_type == HexenType.COMPTIME_INT:
            return True

        # Usize is the only valid concrete index type
        if element_type == HexenType.USIZE:
            return True

        # Float types CANNOT be used for indexing
        if element_type in {HexenType.F32, HexenType.F64, HexenType.COMPTIME_FLOAT}:
            self._error(
                f"Float ranges cannot be used for array indexing (got range[{element_type.value}])",
                node,
            )
            return False

        # User types (i32, i64) require explicit conversion
        if element_type in {HexenType.I32, HexenType.I64}:
            self._error(
                f"Array indexing requires range[usize], found range[{element_type.value}]",
                node,
                extra={
                    "help": f"Convert to usize: range_value:range[usize]",
                    "note": f"range[{element_type.value}] is for iteration/materialization, not indexing",
                },
            )
            return False

        # Unknown or other types
        self._error(
            f"Invalid range element type for indexing: {element_type}",
            node,
        )
        return False

    def _parse_type_annotation(self, node: Dict) -> HexenType:
        """Parse a type annotation node and return HexenType"""
        # This should delegate to type annotation parsing
        # Simplified for now
        if node.get("type") == "primitive_type":
            type_name = node.get("name")
            return HexenType(type_name)

        return HexenType.UNKNOWN
