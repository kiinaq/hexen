"""
Hexen Comptime Analyzer

Specialized analyzer for comptime type analysis and block evaluability detection.
Supports the enhanced unified block system with compile-time vs runtime classification.

This module provides:
- Comptime type preservation analysis
- Compile-time vs runtime block classification
- Comptime-only operation detection
- Runtime variable usage analysis
"""

from typing import Dict, List, Optional, Union, Any

from ..ast_nodes import NodeType
from .types import HexenType, BlockEvaluability, Mutability
from .symbol_table import SymbolTable
from .type_util import (
    is_concrete_type, 
    is_numeric_type, 
    is_float_type, 
    is_integer_type,
    validate_literal_range,
    TYPE_RANGES
)


class ComptimeAnalyzer:
    """
    Analyzer for comptime type operations and block evaluability classification.
    
    Provides utilities for:
    - Comptime type preservation analysis
    - Compile-time vs runtime block classification  
    - Comptime-only operation detection
    - Runtime variable usage analysis
    
    This class encapsulates the logic needed for the enhanced unified block system
    that determines whether expression blocks can preserve comptime types or require
    explicit context for immediate resolution.
    """
    
    def __init__(self, symbol_table: SymbolTable):
        """
        Initialize the comptime analyzer.
        
        Args:
            symbol_table: Symbol table for variable type lookups
        """
        self.symbol_table = symbol_table
    
    # =========================================================================
    # COMPTIME TYPE PRESERVATION LOGIC
    # =========================================================================
    
    def should_preserve_comptime_types(self, evaluability: BlockEvaluability) -> bool:
        """
        Determine if comptime types should be preserved based on evaluability.
        
        Args:
            evaluability: Block evaluability classification
            
        Returns:
            True if comptime types should be preserved for flexibility
        """
        return evaluability == BlockEvaluability.COMPILE_TIME
    
    def requires_explicit_context(self, evaluability: BlockEvaluability) -> bool:
        """
        Determine if explicit type context is required for runtime blocks.
        
        Args:
            evaluability: Block evaluability classification
            
        Returns:
            True if explicit context is required for immediate resolution
        """
        return evaluability == BlockEvaluability.RUNTIME
    
    # =========================================================================
    # CENTRALIZED COMPTIME TYPE OPERATIONS
    # =========================================================================
    
    def is_comptime_type(self, type_: HexenType) -> bool:
        """
        Check if type is a comptime type (COMPTIME_INT or COMPTIME_FLOAT).
        
        Args:
            type_: The type to check
            
        Returns:
            True if type is comptime (COMPTIME_INT or COMPTIME_FLOAT)
        """
        return type_ in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}
    
    def is_mixed_comptime_operation(self, left_type: HexenType, right_type: HexenType) -> bool:
        """
        Detect operations mixing comptime and concrete types.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            
        Returns:
            True if operation mixes comptime and concrete types
        """
        left_is_comptime = self.is_comptime_type(left_type)
        right_is_comptime = self.is_comptime_type(right_type)
        
        # Mixed if exactly one operand is comptime
        return left_is_comptime != right_is_comptime
    
    def has_comptime_operands(self, expression: Dict) -> bool:
        """
        Check if expression contains any comptime operands.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression contains comptime operands
        """
        expr_type = expression.get("type")
        
        # Direct comptime literals
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value]:
            return True
            
        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and self.has_comptime_operands(left):
                return True
            if right and self.has_comptime_operands(right):
                return True
                
        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand and self.has_comptime_operands(operand):
                return True
                
        # Variable references: check if variable has comptime type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info and self.is_comptime_type(symbol_info.type):
                    return True
                    
        return False
    
    def unify_comptime_types(self, types: List[HexenType]) -> Optional[HexenType]:
        """
        Unify multiple comptime types following promotion rules.
        
        Args:
            types: List of types to unify
            
        Returns:
            Unified comptime type or None if unification not possible
        """
        if not types:
            return None
            
        # Filter to only comptime types
        comptime_types = [t for t in types if self.is_comptime_type(t)]
        
        if not comptime_types:
            return None
            
        # All comptime_int -> comptime_int
        if all(t == HexenType.COMPTIME_INT for t in comptime_types):
            return HexenType.COMPTIME_INT
            
        # All comptime_float -> comptime_float  
        if all(t == HexenType.COMPTIME_FLOAT for t in comptime_types):
            return HexenType.COMPTIME_FLOAT
            
        # Mixed comptime types -> comptime_float (promotion rule)
        if (HexenType.COMPTIME_INT in comptime_types and 
            HexenType.COMPTIME_FLOAT in comptime_types):
            return HexenType.COMPTIME_FLOAT
            
        return None
    
    def get_comptime_promotion_result(self, left_type: HexenType, right_type: HexenType) -> HexenType:
        """
        Get promotion result for comptime types (int + float = float).
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            
        Returns:
            Promoted comptime type
        """
        # Both comptime_int -> comptime_int
        if left_type == HexenType.COMPTIME_INT and right_type == HexenType.COMPTIME_INT:
            return HexenType.COMPTIME_INT
            
        # Both comptime_float -> comptime_float
        if left_type == HexenType.COMPTIME_FLOAT and right_type == HexenType.COMPTIME_FLOAT:
            return HexenType.COMPTIME_FLOAT
            
        # Mixed comptime types -> comptime_float (promotion)
        if ((left_type == HexenType.COMPTIME_INT and right_type == HexenType.COMPTIME_FLOAT) or
            (left_type == HexenType.COMPTIME_FLOAT and right_type == HexenType.COMPTIME_INT)):
            return HexenType.COMPTIME_FLOAT
            
        # Default fallback
        return left_type
    
    def resolve_comptime_binary_operation(self, left_type: HexenType, right_type: HexenType, operator: str) -> HexenType:
        """
        Resolve result type for comptime binary operations.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            operator: Binary operator
            
        Returns:
            Result type for comptime binary operation
        """
        # Only handle if both are comptime types
        if not (self.is_comptime_type(left_type) and self.is_comptime_type(right_type)):
            return HexenType.UNKNOWN
            
        # Comparison operators always produce bool
        if operator in {"<", ">", "<=", ">=", "==", "!="}:
            return HexenType.BOOL
            
        # Logical operators always produce bool  
        if operator in {"&&", "||"}:
            return HexenType.BOOL
            
        # Arithmetic operators follow promotion rules
        if operator in {"+", "-", "*", "/", "\\"}:
            return self.get_comptime_promotion_result(left_type, right_type)
            
        return HexenType.UNKNOWN
    
    def can_comptime_types_mix_safely(self, left_type: HexenType, right_type: HexenType, target_type: Optional[HexenType]) -> bool:
        """
        Check if comptime types can mix safely with given target context.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type  
            target_type: Target type providing context
            
        Returns:
            True if comptime types can mix safely
        """
        # If both are comptime, they can always mix
        if self.is_comptime_type(left_type) and self.is_comptime_type(right_type):
            return True
            
        # If one is comptime and we have target context
        if target_type is not None:
            # Comptime type can adapt to concrete type with context
            if (self.is_comptime_type(left_type) and not self.is_comptime_type(right_type)) or \
               (not self.is_comptime_type(left_type) and self.is_comptime_type(right_type)):
                return True
                
        return False
    
    def are_all_comptime_compatible(self, types: List[HexenType]) -> bool:
        """
        Check if all types are comptime-compatible for unification.
        
        Args:
            types: List of types to check
            
        Returns:
            True if all types are comptime-compatible
        """
        if not types:
            return True
            
        # All types must be comptime types for compatibility
        return all(self.is_comptime_type(t) for t in types)
    
    def should_preserve_comptime_type_in_declaration(self, mutability: Mutability, inferred_type: HexenType) -> bool:
        """
        Determine if comptime type should be preserved in variable declaration.
        
        Args:
            mutability: Variable mutability (val vs mut)
            inferred_type: Inferred type from expression
            
        Returns:
            True if comptime type should be preserved for flexibility
        """
        # Only preserve comptime types for immutable (val) declarations
        # Per TYPE_SYSTEM.md: val declarations preserve comptime types for later adaptation
        if mutability == Mutability.IMMUTABLE and self.is_comptime_type(inferred_type):
            return True
            
        return False
    
    def resolve_conditional_comptime_types(self, branch_types: List[HexenType], target_type: Optional[HexenType]) -> HexenType:
        """
        Resolve comptime types across conditional branches.
        
        Args:
            branch_types: Types from all conditional branches
            target_type: Target type for context-guided resolution
            
        Returns:
            Unified type for conditional expression
        """
        if not branch_types:
            return HexenType.UNKNOWN
            
        # If we have target context, use it for resolution
        if target_type:
            # Check if all branches are comptime-compatible with target
            all_compatible = True
            for branch_type in branch_types:
                if self.is_comptime_type(branch_type):
                    # Comptime types adapt to target context
                    continue
                elif branch_type != target_type:
                    all_compatible = False
                    break
                    
            if all_compatible:
                return target_type
                
        # Without target context, try to unify comptime types
        unified = self.unify_comptime_types(branch_types)
        if unified:
            return unified
            
        # Check if all branches have same type
        first_type = branch_types[0]
        if all(t == first_type for t in branch_types):
            return first_type
            
        return HexenType.UNKNOWN
    
    def analyze_comptime_operands_in_binary_op(self, left_type: HexenType, right_type: HexenType, target_type: HexenType) -> bool:
        """
        Analyze if comptime operands in binary operation make it safe.
        
        Args:
            left_type: Left operand type
            right_type: Right operand type
            target_type: Target type for the operation
            
        Returns:
            True if comptime operands make the operation safe
        """
        # If either operand is comptime and can adapt to target, it's safe
        if self.is_comptime_type(left_type):
            # Check if comptime type can coerce to target (basic check)
            if target_type in {HexenType.I32, HexenType.I64, HexenType.F32, HexenType.F64}:
                return True
                
        if self.is_comptime_type(right_type):
            # Check if comptime type can coerce to target (basic check)
            if target_type in {HexenType.I32, HexenType.I64, HexenType.F32, HexenType.F64}:
                return True
                
        return False
    
    def preserve_comptime_type_in_unary_op(self, operand_type: HexenType, operator: str) -> HexenType:
        """
        Preserve comptime type through unary operations.
        
        Args:
            operand_type: Operand type
            operator: Unary operator
            
        Returns:
            Result type preserving comptime nature where appropriate
        """
        # For comptime types with unary minus, preserve the comptime type
        if operator == "-":
            if operand_type == HexenType.COMPTIME_INT:
                return HexenType.COMPTIME_INT
            elif operand_type == HexenType.COMPTIME_FLOAT:
                return HexenType.COMPTIME_FLOAT
                
        # For logical not, always return bool
        if operator == "!":
            return HexenType.BOOL
            
        # Default: return operand type unchanged
        return operand_type
    
    def requires_explicit_comptime_context(self, expression: Dict) -> bool:
        """
        Determine if expression requires explicit context for comptime resolution.
        
        Args:
            expression: Expression AST node
            
        Returns:
            True if expression requires explicit context
        """
        # Mixed comptime operations typically require context
        expr_type = expression.get("type")
        
        if expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                # This is a simplified check - would need full type analysis
                return True  # Conservative: assume binary ops need context
                
        return False
    
    # =========================================================================
    # METHODS MOVED FROM TYPE_UTIL.PY
    # =========================================================================
    
    def resolve_comptime_type(self, comptime_type: HexenType, target_type: Optional[HexenType] = None) -> HexenType:
        """
        Resolve a comptime type to a concrete type based on context.

        Used when we have a comptime_int or comptime_float that needs to become
        a concrete type. Falls back to default types if no target is provided.

        Args:
            comptime_type: The comptime type to resolve
            target_type: Optional target type for context-guided resolution

        Returns:
            The resolved concrete type
        """
        if comptime_type == HexenType.COMPTIME_INT:
            if target_type and is_numeric_type(target_type):
                return target_type
            return HexenType.I32  # Default integer type

        if comptime_type == HexenType.COMPTIME_FLOAT:
            if target_type and is_float_type(target_type):
                return target_type
            return HexenType.F64  # Default float type

        return comptime_type  # Not a comptime type, return as-is
    
    def is_mixed_type_operation(self, left_type: HexenType, right_type: HexenType) -> bool:
        """
        Check if an operation involves mixed types that require explicit handling.

        Returns True ONLY for Pattern 3 (Mixed Concrete → Explicit Required):
        - Operation between different concrete integer types (e.g. i32 + i64)
        - Operation between different concrete float types (e.g. f32 + f64)
        - Operation between concrete float and concrete integer types

        Returns False for all other patterns:
        - Pattern 1: Comptime + Comptime → Comptime (e.g. comptime_int + comptime_float)
        - Pattern 2: Comptime + Concrete → Concrete (e.g. i64 + comptime_int, f32 + comptime_float)
        - Pattern 4: Same Concrete → Same Concrete (e.g. i32 + i32)
        """
        # Pattern 1 & 2: Any operation involving comptime types should be handled elsewhere (not mixed)
        if left_type in {
            HexenType.COMPTIME_INT,
            HexenType.COMPTIME_FLOAT,
        } or right_type in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            return False

        # Pattern 4: Same concrete types are not mixed
        if left_type == right_type:
            return False

        # Pattern 3: Mixed concrete types - require explicit conversions
        return (
            # Different concrete integer types
            (is_integer_type(left_type) and is_integer_type(right_type))
            or
            # Different concrete float types
            (is_float_type(left_type) and is_float_type(right_type))
            or
            # Concrete float + concrete integer (either direction)
            (is_float_type(left_type) and is_integer_type(right_type))
            or (is_integer_type(left_type) and is_float_type(right_type))
        )
    
    def validate_comptime_literal_coercion(
        self,
        value: Union[int, float],
        from_type: HexenType,
        to_type: HexenType,
        source_text: str = None,
    ) -> None:
        """
        Validate comptime literal can be safely coerced to target type.

        This function implements the overflow detection during comptime type coercion
        as specified in LITERAL_OVERFLOW_BEHAVIOR.md. It should be called when
        comptime_int or comptime_float literals are being coerced to concrete types.

        Args:
            value: The literal value from the AST node
            from_type: The source comptime type (COMPTIME_INT or COMPTIME_FLOAT)
            to_type: The target concrete type
            source_text: Original literal text for error messages

        Raises:
            TypeError: If literal overflows target type range

        Returns:
            None if coercion is safe
        """
        # Only validate comptime type coercions to concrete types
        if from_type not in {HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT}:
            return

        if to_type not in TYPE_RANGES:
            return

        # Special handling for comptime_float → integer coercion
        if from_type == HexenType.COMPTIME_FLOAT and to_type in {
            HexenType.I32,
            HexenType.I64,
        }:
            # This should require explicit conversion per TYPE_SYSTEM.md
            # But if we get here, validate the conversion is at least in range
            validate_literal_range(int(value), to_type, source_text)
        else:
            # Standard range validation
            validate_literal_range(value, to_type, source_text)
    
    def extract_literal_info(self, node: Dict) -> tuple[Union[int, float], str]:
        """
        Extract literal value and source text from AST node.

        Args:
            node: AST node representing a literal (comptime_int, comptime_float, etc.)

        Returns:
            Tuple of (value, source_text) or (None, None) if not a literal
        """
        if node.get("type") in {NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value}:
            value = node.get("value")
            source_text = node.get("source_text", str(value) if value is not None else None)
            return value, source_text
        return None, None
    
    # =========================================================================
    # BLOCK EVALUABILITY CLASSIFICATION
    # =========================================================================
    
    def classify_block_evaluability(self, statements: List[Dict]) -> BlockEvaluability:
        """
        Classify block as compile-time or runtime evaluable.
        
        This is the foundation for the enhanced unified block system that determines
        whether expression blocks can preserve comptime types or require explicit context.
        
        Compile-time evaluable criteria (ALL must be true):
        - All operations involve only comptime literals
        - NO conditional expressions (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
        - NO runtime function calls (functions always return concrete types)
        - NO runtime variable usage (concrete types)
        - All computations can be evaluated at compile-time
        
        Runtime evaluable triggers (ANY triggers runtime):
        - Function calls: Functions always return concrete types
        - Conditionals: All conditionals are runtime per specification
        - Concrete variable usage: Mixing comptime + concrete types
        
        Args:
            statements: List of statements in the block
            
        Returns:
            BlockEvaluability.COMPILE_TIME if block can preserve comptime types
            BlockEvaluability.RUNTIME if block requires explicit context
        """
        # Enhanced detection with function calls and conditionals
        
        # Priority 1: Check for runtime operations (function calls, conditionals)
        if self._contains_runtime_operations(statements):
            return BlockEvaluability.RUNTIME
        
        # Priority 2: Check for concrete variable usage (mixing comptime + concrete = runtime)
        if self.has_runtime_variables(statements):
            return BlockEvaluability.RUNTIME
            
        # Priority 3: If all operations are comptime-only, block is compile-time evaluable
        if self.has_comptime_only_operations(statements):
            return BlockEvaluability.COMPILE_TIME
            
        # Default to runtime for safety (unknown cases should require explicit context)
        return BlockEvaluability.RUNTIME
    
    def _contains_runtime_operations(self, statements: List[Dict]) -> bool:
        """
        Detect runtime operations that trigger runtime classification.
        
        Runtime operations include:
        - Function calls (functions always return concrete types)
        - Conditional expressions (all conditionals are runtime per CONDITIONAL_SYSTEM.md)
        - Runtime variable usage (concrete types) - handled by existing logic
        
        This enhances the block evaluability system with comprehensive runtime detection.
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if any runtime operations found, False if all operations are comptime
        """
        return (self._contains_function_calls(statements) or 
                self._contains_conditionals(statements))
    
    def _contains_function_calls(self, statements: List[Dict]) -> bool:
        """
        Recursively detect function calls in block statements.
        
        Function calls always trigger runtime classification because:
        1. Functions always return concrete types (never comptime types)
        2. Function execution happens at runtime
        3. Results cannot be computed at compile-time
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if any function calls found in statements or sub-expressions
        """
        for statement in statements:
            if self._statement_contains_function_calls(statement):
                return True
        return False
    
    def _contains_conditionals(self, statements: List[Dict]) -> bool:
        """
        Recursively detect conditional expressions in block statements.
        
        Conditionals always trigger runtime classification per CONDITIONAL_SYSTEM.md:
        1. All conditionals are runtime (specification requirement)
        2. Condition evaluation happens at runtime
        3. Branch selection cannot be determined at compile-time
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if any conditionals found in statements or sub-expressions
        """
        for statement in statements:
            if self._statement_contains_conditionals(statement):
                return True
        return False
    
    def _statement_contains_function_calls(self, statement: Dict) -> bool:
        """
        Check if a single statement contains function calls.
        
        Args:
            statement: Statement AST node to analyze
            
        Returns:
            True if statement contains function calls, False otherwise
        """
        stmt_type = statement.get("type")
        
        # Function call statements are direct function calls
        if stmt_type == NodeType.FUNCTION_CALL_STATEMENT.value:
            return True
            
        # Check expressions in declaration statements
        if stmt_type in [NodeType.VAL_DECLARATION.value, NodeType.MUT_DECLARATION.value]:
            value = statement.get("value")
            if value and value != "undef":
                return self._expression_contains_function_calls(value)
                
        # Check expressions in assign/assignment statements
        elif stmt_type in [NodeType.ASSIGN_STATEMENT.value, NodeType.ASSIGNMENT_STATEMENT.value]:
            value = statement.get("value")
            if value:
                return self._expression_contains_function_calls(value)
                
        # Check expressions in return statements
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_contains_function_calls(value)
                
        return False
    
    def _statement_contains_conditionals(self, statement: Dict) -> bool:
        """
        Check if a single statement contains conditionals.
        
        Args:
            statement: Statement AST node to analyze
            
        Returns:
            True if statement contains conditionals, False otherwise
        """
        stmt_type = statement.get("type")
        
        # Direct conditional statements
        if stmt_type == NodeType.CONDITIONAL_STATEMENT.value:
            return True
            
        # Check expressions in declaration statements
        if stmt_type in [NodeType.VAL_DECLARATION.value, NodeType.MUT_DECLARATION.value]:
            value = statement.get("value")
            if value and value != "undef":
                return self._expression_contains_conditionals(value)
                
        # Check expressions in assign/assignment statements  
        elif stmt_type in [NodeType.ASSIGN_STATEMENT.value, NodeType.ASSIGNMENT_STATEMENT.value]:
            value = statement.get("value")
            if value:
                return self._expression_contains_conditionals(value)
                
        # Check expressions in return statements
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self._expression_contains_conditionals(value)
                
        return False
    
    def _expression_contains_function_calls(self, expression: Dict) -> bool:
        """
        Recursively analyze expression for function calls.
        
        This performs deep analysis of expression trees to find any nested
        function calls that would trigger runtime classification.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression contains function calls, False otherwise
        """
        expr_type = expression.get("type")
        
        # Direct function call expression
        if expr_type == NodeType.FUNCTION_CALL.value:
            return True
            
        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and self._expression_contains_function_calls(left):
                return True
            if right and self._expression_contains_function_calls(right):
                return True
                
        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand and self._expression_contains_function_calls(operand):
                return True
                
        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand and self._expression_contains_function_calls(operand):
                return True
                
        # Block expressions: recursively analyze (nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self._contains_function_calls(statements)
            
        return False
    
    def _expression_contains_conditionals(self, expression: Dict) -> bool:
        """
        Recursively analyze expression for conditionals.
        
        This performs deep analysis of expression trees to find any nested
        conditionals that would trigger runtime classification.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression contains conditionals, False otherwise
        """
        expr_type = expression.get("type")
        
        # Note: Based on the grammar, conditionals are statements not expressions
        # But we check anyway for future extensibility
        
        # Binary operations: check both operands
        if expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and self._expression_contains_conditionals(left):
                return True
            if right and self._expression_contains_conditionals(right):
                return True
                
        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand and self._expression_contains_conditionals(operand):
                return True
                
        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand and self._expression_contains_conditionals(operand):
                return True
                
        # Block expressions: recursively analyze (nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self._contains_conditionals(statements)
            
        return False
    
    # =========================================================================
    # COMPTIME-ONLY OPERATION DETECTION
    # =========================================================================
    
    def has_comptime_only_operations(self, statements: List[Dict]) -> bool:
        """
        Check if all operations in the block use only comptime types.
        
        Comptime operations include:
        - Literal values (42, 3.14, "string", true/false)
        - Arithmetic on comptime types (42 + 100, 3.14 * 2.0)
        - Variable declarations with comptime initializers
        - Variable references to other comptime-only variables
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if all operations are comptime-only, False otherwise
        """
        for statement in statements:
            if not self.statement_has_comptime_only_operations(statement):
                return False
        return True
    
    def statement_has_comptime_only_operations(self, statement: Dict) -> bool:
        """
        Check if a single statement contains only comptime operations.
        
        Args:
            statement: Statement AST node to analyze
            
        Returns:
            True if statement uses only comptime operations, False otherwise
        """
        stmt_type = statement.get("type")
        
        # Variable declarations: check initializer
        if stmt_type in [NodeType.VAL_DECLARATION.value, NodeType.MUT_DECLARATION.value]:
            value = statement.get("value")
            if value and value != "undef":
                return self.expression_has_comptime_only_operations(value)
            return True  # undef is considered comptime
            
        # Assign statements: check the assigned expression  
        elif stmt_type == NodeType.ASSIGN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_comptime_only_operations(value)
            return False
            
        # Assignment statements: check the assigned expression
        elif stmt_type == NodeType.ASSIGNMENT_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_comptime_only_operations(value)
            return False
            
        # Return statements: check the returned expression
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_comptime_only_operations(value)
            return True  # bare return is comptime
            
        # Other statement types are handled by runtime operation detection
        # For safety, assume they're runtime if not explicitly comptime
        return False
    
    def expression_has_comptime_only_operations(self, expression: Dict) -> bool:
        """
        Check if an expression contains only comptime operations.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression is comptime-only, False otherwise
        """
        expr_type = expression.get("type")
        
        # Comptime literals
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value]:
            return True
            
        # Other literals (string, bool) are concrete but considered comptime for this analysis
        if expr_type == NodeType.LITERAL.value:
            return True
            
        # Variable references: check if variable has comptime type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info:
                    # If variable has comptime type, it's comptime-only
                    var_type = symbol_info.type
                    return var_type in [HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT]
            return False
            
        # Binary operations: both operands must be comptime-only
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                return (self.expression_has_comptime_only_operations(left) and
                       self.expression_has_comptime_only_operations(right))
            return False
            
        # Unary operations: operand must be comptime-only
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand:
                return self.expression_has_comptime_only_operations(operand)
            return False
            
        # Explicit conversions: operand must be comptime-only (though result becomes concrete)
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand:
                return self.expression_has_comptime_only_operations(operand)
            return False
            
        # Block expressions: recursively analyze (this enables nested expression blocks)
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self.has_comptime_only_operations(statements)
            
        # Function calls and conditionals are handled by runtime operation detection
        # For safety, assume they're runtime if not explicitly comptime
        return False
    
    # =========================================================================
    # RUNTIME VARIABLE DETECTION
    # =========================================================================
    
    def has_runtime_variables(self, statements: List[Dict]) -> bool:
        """
        Check if the block uses variables with concrete (runtime) types.
        
        This detects mixing of comptime and concrete types, which requires
        explicit type context for proper resolution.
        
        Args:
            statements: List of statements to analyze
            
        Returns:
            True if block uses concrete variables, False if only comptime variables
        """
        for statement in statements:
            if self.statement_has_runtime_variables(statement):
                return True
        return False
    
    def statement_has_runtime_variables(self, statement: Dict) -> bool:
        """
        Check if a statement uses concrete (runtime) variables.
        
        Args:
            statement: Statement AST node to analyze
            
        Returns:
            True if statement uses concrete variables, False otherwise  
        """
        stmt_type = statement.get("type")
        
        # Variable declarations: check if explicitly typed with concrete type
        if stmt_type in [NodeType.VAL_DECLARATION.value, NodeType.MUT_DECLARATION.value]:
            # If explicit type annotation is concrete, it's runtime
            type_annotation = statement.get("type_annotation")
            if type_annotation:
                # Parse type annotation to check if it's concrete
                return is_concrete_type(type_annotation)
                
            # Check initializer expression for concrete variable usage
            value = statement.get("value")
            if value and value != "undef":
                return self.expression_has_runtime_variables(value)
            return False
            
        # Assign and assignment statements: check expressions
        elif stmt_type in [NodeType.ASSIGN_STATEMENT.value, NodeType.ASSIGNMENT_STATEMENT.value]:
            value = statement.get("value")
            if value:
                return self.expression_has_runtime_variables(value)
            return False
            
        # Return statements: check expression
        elif stmt_type == NodeType.RETURN_STATEMENT.value:
            value = statement.get("value")
            if value:
                return self.expression_has_runtime_variables(value)
            return False
            
        return False
    
    def expression_has_runtime_variables(self, expression: Dict) -> bool:
        """
        Check if an expression uses concrete (runtime) variables.
        
        Args:
            expression: Expression AST node to analyze
            
        Returns:
            True if expression uses concrete variables, False otherwise
        """
        expr_type = expression.get("type")
        
        # Literals are not runtime variables
        if expr_type in [NodeType.COMPTIME_INT.value, NodeType.COMPTIME_FLOAT.value, 
                        NodeType.LITERAL.value]:
            return False
            
        # Variable references: check if variable has concrete type
        elif expr_type == NodeType.IDENTIFIER.value:
            var_name = expression.get("name")
            if var_name:
                symbol_info = self.symbol_table.lookup_symbol(var_name)
                if symbol_info:
                    var_type = symbol_info.type
                    # Concrete types indicate runtime variables
                    return var_type not in [HexenType.COMPTIME_INT, HexenType.COMPTIME_FLOAT]
            return False
            
        # Binary operations: check both operands
        elif expr_type == NodeType.BINARY_OPERATION.value:
            left = expression.get("left")
            right = expression.get("right")
            if left and right:
                return (self.expression_has_runtime_variables(left) or
                       self.expression_has_runtime_variables(right))
            return False
            
        # Unary operations: check operand
        elif expr_type == NodeType.UNARY_OPERATION.value:
            operand = expression.get("operand")
            if operand:
                return self.expression_has_runtime_variables(operand)
            return False
            
        # Explicit conversions: check operand
        elif expr_type == NodeType.EXPLICIT_CONVERSION_EXPRESSION.value:
            operand = expression.get("expression")
            if operand:
                return self.expression_has_runtime_variables(operand)
            return False
            
        # Block expressions: recursively analyze
        elif expr_type == NodeType.BLOCK.value:
            statements = expression.get("statements", [])
            return self.has_runtime_variables(statements)
            
        return False
    
    # =========================================================================
    # RUNTIME OPERATION CONTEXT VALIDATION
    # =========================================================================
    
    def validate_runtime_block_context(self, statements: List[Dict], evaluability: BlockEvaluability) -> Optional[str]:
        """
        Validate that runtime blocks have appropriate context and generate helpful error messages.
        
        This provides detailed error messages explaining why blocks require
        runtime context when they contain function calls or conditionals.
        
        Args:
            statements: List of statements in the block
            evaluability: Block evaluability classification
            
        Returns:
            Error message string if validation fails, None if validation passes
        """
        if evaluability != BlockEvaluability.RUNTIME:
            return None  # Compile-time blocks don't need validation
            
        # Generate helpful error messages explaining why runtime context is required
        reasons = []
        
        # Check for function calls
        if self._contains_function_calls(statements):
            reasons.append("contains function calls (functions always return concrete types)")
            
        # Check for conditionals  
        if self._contains_conditionals(statements):
            reasons.append("contains conditional expressions (all conditionals are runtime per specification)")
            
        # Check for concrete variable usage
        if self.has_runtime_variables(statements):
            reasons.append("uses concrete type variables")
            
        if reasons:
            reason_text = " and ".join(reasons)
            return f"Runtime block requires explicit type context because it {reason_text}. " \
                   f"Suggestion: Add explicit type annotation to the target variable."
                   
        return None
    
    def get_runtime_operation_reason(self, statements: List[Dict]) -> str:
        """
        Get a detailed reason why the block is classified as runtime.
        
        This helps generate specific error messages for different types of runtime operations.
        
        Args:
            statements: List of statements in the block
            
        Returns:
            Human-readable string explaining the runtime classification reason
        """
        reasons = []
        
        # Check for function calls
        if self._contains_function_calls(statements):
            reasons.append("Function calls detected (functions always return concrete types)")
            
        # Check for conditionals  
        if self._contains_conditionals(statements):
            reasons.append("Conditional expressions detected (all conditionals are runtime per CONDITIONAL_SYSTEM.md)")
            
        # Check for concrete variable usage
        if self.has_runtime_variables(statements):
            reasons.append("Concrete type variables detected (mixing comptime and concrete types)")
            
        if not reasons:
            return "Unknown runtime operations detected"
            
        return ". ".join(reasons) + "."