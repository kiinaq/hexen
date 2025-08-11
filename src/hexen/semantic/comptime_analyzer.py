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

from typing import Dict, List, Optional

from ..ast_nodes import NodeType
from .types import HexenType, BlockEvaluability
from .symbol_table import SymbolTable
from .type_util import is_concrete_type


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