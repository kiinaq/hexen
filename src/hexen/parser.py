"""
Hexen Parser

Parser for Hexen language with variable declarations using Lark.
"""

from pathlib import Path
from lark import Lark, Transformer, v_args
from typing import Dict, Any

from .ast_nodes import NodeType


class HexenTransformer(Transformer):
    """Transform parse tree into meaningful AST nodes"""

    def function(self, args):
        """Transform function: FUNC IDENTIFIER ( parameter_list? ) : type = block"""
        if len(args) == 4:
            # No parameters: func_token, name, return_type, body
            func_token, name, return_type, body = args
            return {
                "type": NodeType.FUNCTION.value,
                "name": name["name"],
                "parameters": [],
                "return_type": return_type,
                "body": body,
            }
        else:
            # With parameters: func_token, name, parameter_list, return_type, body
            func_token, name, parameter_list, return_type, body = args
            return {
                "type": NodeType.FUNCTION.value,
                "name": name["name"],
                "parameters": parameter_list if parameter_list is not None else [],
                "return_type": return_type,
                "body": body,
            }

    def parameter_list(self, args):
        """Transform parameter list"""
        return list(args)

    def parameter(self, args):
        """Transform parameter: [MUT?] IDENTIFIER : type"""
        if len(args) == 2:
            # Regular parameter: IDENTIFIER : type
            name, param_type = args
            return {
                "type": NodeType.PARAMETER.value,
                "name": name["name"],
                "param_type": param_type,
                "is_mutable": False,
            }
        else:
            # Mutable parameter: MUT IDENTIFIER : type
            mut_token, name, param_type = args
            return {
                "type": NodeType.PARAMETER.value,
                "name": name["name"],
                "param_type": param_type,
                "is_mutable": True,
            }

    def val_declaration(self, args):
        # Handle: VAL IDENTIFIER [":" type] "=" expression
        # args can be [val_token, name, value] or [val_token, name, type, value]
        if len(args) == 3:
            # No type annotation: val name = value
            val_token, name, value = args
            return {
                "type": NodeType.VAL_DECLARATION.value,
                "name": name["name"],
                "type_annotation": None,
                "value": value,
            }
        else:
            # With type annotation: val name : type = value
            val_token, name, type_annotation, value = args
            return {
                "type": NodeType.VAL_DECLARATION.value,
                "name": name["name"],
                "type_annotation": type_annotation,
                "value": value,
            }

    def mut_declaration(self, args):
        # Handle: MUT IDENTIFIER [":" type] "=" expression
        # args can be [mut_token, name, value] or [mut_token, name, type, value]
        if len(args) == 3:
            # No type annotation: mut name = value
            mut_token, name, value = args
            return {
                "type": NodeType.MUT_DECLARATION.value,
                "name": name["name"],
                "type_annotation": None,
                "value": value,
            }
        else:
            # With type annotation: mut name : type = value
            mut_token, name, type_annotation, value = args
            return {
                "type": NodeType.MUT_DECLARATION.value,
                "name": name["name"],
                "type_annotation": type_annotation,
                "value": value,
            }

    def var_declaration(self, children):
        # var_declaration: val_declaration | mut_declaration
        return children[0]

    def return_stmt(self, args):
        # Handle: "return" [expression]
        # args can be empty (bare return) or [expression]
        if len(args) == 0:
            # Bare return statement
            return {"type": NodeType.RETURN_STATEMENT.value, "value": None}
        else:
            # Return with expression
            return {"type": NodeType.RETURN_STATEMENT.value, "value": args[0]}

    def assign_stmt(self, args):
        # Handle: "->" expression
        if len(args) == 1:
            # Just the expression after "->" token
            return {
                "type": NodeType.ASSIGN_STATEMENT.value,
                "value": args[0],
            }
        else:
            # Error case - should not happen with correct grammar
            raise SyntaxError(f"Invalid assign statement structure: {args}")

    @v_args(inline=True)
    def assignment_stmt(self, target, value):
        # Handle: IDENTIFIER "=" expression
        return {
            "type": NodeType.ASSIGNMENT_STATEMENT.value,
            "target": target["name"],  # Extract name from identifier dict
            "value": value,
        }

    def conditional_stmt(self, args):
        # Handle: "if" expression block else_clause*
        # args: [condition, if_branch, *else_clauses] (keywords are consumed by grammar)
        condition = args[0]
        if_branch = args[1]
        else_clauses = args[2:] if len(args) > 2 else []
        
        return {
            "type": NodeType.CONDITIONAL_STATEMENT.value,
            "condition": condition,
            "if_branch": if_branch,
            "else_clauses": list(else_clauses),
        }

    def else_clause(self, args):
        # Handle: "else" "if" expression block | "else" block
        # Keywords are consumed by grammar, so we only get the meaningful parts
        if len(args) == 2:
            # else if case: [condition, block] (from "else if" production)
            condition = args[0]
            branch = args[1]
            return {
                "type": NodeType.ELSE_CLAUSE.value,
                "condition": condition,
                "branch": branch,
            }
        elif len(args) == 1:
            # final else case: [block] (from "else" production)
            branch = args[0]
            return {
                "type": NodeType.ELSE_CLAUSE.value,
                "condition": None,  # No condition for final else
                "branch": branch,
            }
        else:
            raise SyntaxError(f"Invalid else clause structure: {args}")

    def function_call_stmt(self, args):
        """Transform function call statement: function_call"""
        # Function call statements just wrap the function call in a statement node
        function_call = args[0]
        return {
            "type": NodeType.FUNCTION_CALL_STATEMENT.value,
            "function_call": function_call,
        }

    def function_call(self, args):
        """Transform function call: IDENTIFIER ( argument_list? )"""
        if len(args) == 1:
            # No arguments: function_name
            function_name = args[0]
            return {
                "type": NodeType.FUNCTION_CALL.value,
                "function_name": function_name["name"],
                "arguments": [],
            }
        else:
            # With arguments: function_name, argument_list
            function_name, argument_list = args
            return {
                "type": NodeType.FUNCTION_CALL.value,
                "function_name": function_name["name"],
                "arguments": argument_list if argument_list is not None else [],
            }

    def argument_list(self, args):
        """Transform argument list"""
        return list(args)

    def expression(self, children):
        # Handle: logical_or
        return children[0]

    def conversion(self, children):
        # Handle: primary [CONVERSION_OP type]
        if len(children) == 1:
            return children[0]
        elif len(children) == 3:
            # Expression with explicit type conversion: expr, conversion_op_token, target_type
            expr, conversion_token, target_type = children
            return {
                "type": NodeType.EXPLICIT_CONVERSION_EXPRESSION.value,
                "expression": expr,
                "target_type": target_type,
            }
        else:
            # Expression with explicit type conversion: expr, target_type
            expr, target_type = children
            return {
                "type": NodeType.EXPLICIT_CONVERSION_EXPRESSION.value,
                "expression": expr,
                "target_type": target_type,
            }

    def logical_or(self, children):
        # print("[DEBUG] logical_or children:", children)
        if len(children) == 1:
            return children[0]
        left = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            left = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": str(op),
                "left": left,
                "right": right,
            }
            i += 2
        return left

    def logical_and(self, children):
        # print("[DEBUG] logical_and children:", children)
        if len(children) == 1:
            return children[0]
        left = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            left = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": str(op),
                "left": left,
                "right": right,
            }
            i += 2
        return left

    def equality(self, children):
        # print("[DEBUG] equality children:", children)
        if len(children) == 1:
            return children[0]
        left = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            left = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": str(op),
                "left": left,
                "right": right,
            }
            i += 2
        return left

    def relational(self, children):
        # print("[DEBUG] relational children:", children)
        if len(children) == 1:
            return children[0]
        left = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            left = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": str(op),
                "left": left,
                "right": right,
            }
            i += 2
        return left

    def additive(self, children):
        # print("[DEBUG] additive children:", children)
        if len(children) == 1:
            return children[0]
        left = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            left = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": str(op),
                "left": left,
                "right": right,
            }
            i += 2
        return left

    def multiplicative(self, children):
        # print("[DEBUG] multiplicative children:", children)
        if len(children) == 1:
            return children[0]
        left = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            left = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": str(op),
                "left": left,
                "right": right,
            }
            i += 2
        return left

    def unary(self, children):
        # unary: ("-" | "!")? primary
        if len(children) == 1:
            return children[0]
        # Handle unary operators
        op = str(children[0])
        operand = children[1]
        return {
            "type": NodeType.UNARY_OPERATION.value,
            "operator": op,
            "operand": operand,
        }

    def primary(self, children):
        # primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")" | array_literal
        if len(children) == 1:
            return children[0]  # Direct primary expression
        else:
            # Parenthesized expression: "(" expression ")"
            return children[1]

    def postfix(self, children):
        # postfix: primary (array_access)*
        if len(children) == 1:
            return children[0]  # No array access
        
        # Chain array accesses: arr[i][j][k]
        expr = children[0]  # Base expression
        for access in children[1:]:
            # Each array_access contains the index, we need to set the array
            access["array"] = expr
            expr = access
        
        return expr

    def array_access(self, children):
        # array_access: "[" expression "]"
        index = children[0]  # The expression inside brackets
        return {
            "type": NodeType.ARRAY_ACCESS.value,
            "array": None,  # Will be set by postfix handler
            "index": index,
        }

    def array_literal(self, children):
        # array_literal: "[" [expression ("," expression)*] "]"
        # Filter out None values that might come from empty optional groups
        elements = [child for child in children if child is not None] if children else []
        return {
            "type": NodeType.ARRAY_LITERAL.value,
            "elements": elements,
        }

    def array_type(self, children):
        # array_type: array_dimension+ primitive_type
        dimensions = children[:-1]  # All but the last item are dimensions
        element_type = children[-1]  # Last item is the primitive type
        return {
            "type": NodeType.ARRAY_TYPE.value,
            "dimensions": dimensions,
            "element_type": element_type,
        }

    def array_dimension(self, children):
        # array_dimension: "[" (INTEGER | "_") "]"
        # Handle both INTEGER tokens and "_" literal
        if len(children) == 0:
            # This means we got a "_" literal which is not processed as a child
            return {
                "type": NodeType.ARRAY_DIMENSION.value,
                "size": "_",
            }
        else:
            # We got an INTEGER token
            size = children[0]
            return {
                "type": NodeType.ARRAY_DIMENSION.value,
                "size": size,
            }

    def primitive_type(self, children):
        # primitive_type: TYPE_I32 | TYPE_I64 | ...
        return children[0]

    def _build_binary_operation_tree(self, children):
        # print("[DEBUG] _build_binary_operation_tree children:", children)
        if len(children) == 1:
            return children[0]  # Single operand
        result = children[0]
        for i in range(1, len(children) - 1, 2):
            operator = str(children[i])
            right_operand = children[i + 1]
            # print(
            #     f"[DEBUG] Building node: left={result}, op={operator}, right={right_operand}"
            # )
            result = {
                "type": NodeType.BINARY_OPERATION.value,
                "operator": operator,
                "left": result,
                "right": right_operand,
            }
        return result

    @v_args(inline=True)
    def statement(self, stmt):
        return stmt

    def type(self, children):
        # Handle multiple types through terminal tokens
        return children[0]

    # Terminal handlers for type tokens
    def TYPE_I32(self, token):
        return "i32"

    def TYPE_I64(self, token):
        return "i64"

    def TYPE_F32(self, token):
        return "f32"

    def TYPE_F64(self, token):
        return "f64"

    def TYPE_STRING(self, token):
        return "string"

    def TYPE_BOOL(self, token):
        return "bool"

    def TYPE_VOID(self, token):
        return "void"

    def VAL(self, token):
        return "val"

    def MUT(self, token):
        return "mut"

    def block(self, statements):
        # Always return consistent block structure with statements array
        return {"type": NodeType.BLOCK.value, "statements": list(statements)}

    def program(self, items):
        """Transform program: (function | statement)+"""
        functions = []
        statements = []

        for item in items:
            if item["type"] == NodeType.FUNCTION.value:
                functions.append(item)
            else:
                statements.append(item)

        result = {"type": NodeType.PROGRAM.value, "functions": functions}
        if statements:
            result["statements"] = statements
        return result

    # Terminal handlers for new grammar elements
    def STRING(self, token):
        # Parse string literals: "hello" -> {type: "literal", value: "hello"}
        # Remove surrounding quotes from the token
        return {"type": NodeType.LITERAL.value, "value": str(token)[1:-1]}

    def IDENTIFIER(self, token):
        # Parse identifiers: myVar -> {type: "identifier", name: "myVar"}
        # Used for variable names and references
        return {"type": NodeType.IDENTIFIER.value, "name": str(token)}

    def NUMBER(self, token):
        """Enhanced number parser supporting all literal formats with overflow detection"""
        token_str = str(token).strip()

        try:
            # Handle negative sign
            is_negative = token_str.startswith("-")
            if is_negative or token_str.startswith("+"):
                token_str = token_str[1:]

            # Determine literal type and parse
            if token_str.startswith(("0x", "0X")):
                # Hexadecimal literal
                value = self._parse_hex_literal(token_str[2:], is_negative)
                return self._create_comptime_int(
                    value, f"{'-' if is_negative else ''}{token_str}"
                )

            elif token_str.startswith(("0b", "0B")):
                # Binary literal
                value = self._parse_binary_literal(token_str[2:], is_negative)
                return self._create_comptime_int(
                    value, f"{'-' if is_negative else ''}{token_str}"
                )

            elif "e" in token_str.lower():
                # Scientific notation
                value = self._parse_scientific_literal(token_str, is_negative)
                return self._create_comptime_number(
                    value, f"{'-' if is_negative else ''}{token_str}"
                )

            elif "." in token_str:
                # Decimal float
                full_token = f"{'-' if is_negative else ''}{token_str}"
                value = float(full_token)
                return self._create_comptime_float(value, full_token)

            else:
                # Integer
                full_token = f"{'-' if is_negative else ''}{token_str}"
                value = int(full_token)
                return self._create_comptime_int(value, full_token)

        except (ValueError, OverflowError) as e:
            raise SyntaxError(f"Invalid number literal '{str(token)}': {e}")

    def _parse_hex_literal(self, hex_str: str, is_negative: bool) -> int:
        """Parse hexadecimal literal with validation"""
        try:
            value = int(hex_str, 16)
            if is_negative:
                value = -value
            return value
        except ValueError:
            raise SyntaxError(f"Invalid hexadecimal literal: 0x{hex_str}")

    def _parse_binary_literal(self, bin_str: str, is_negative: bool) -> int:
        """Parse binary literal with validation"""
        try:
            value = int(bin_str, 2)
            if is_negative:
                value = -value
            return value
        except ValueError:
            raise SyntaxError(f"Invalid binary literal: 0b{bin_str}")

    def _parse_scientific_literal(self, sci_str: str, is_negative: bool):
        """Parse scientific notation with validation"""
        try:
            value = float(f"{'-' if is_negative else ''}{sci_str}")
            # Determine if result should be comptime_int or comptime_float
            if value.is_integer() and abs(value) <= 2**63 - 1:
                return int(value)
            return value
        except (ValueError, OverflowError):
            raise SyntaxError(f"Invalid scientific literal: {sci_str}")

    def _create_comptime_int(self, value: int, source_text: str) -> dict:
        """Create comptime_int with overflow detection"""
        # Check against absolute bounds for any integer type
        MAX_SAFE_INT = 2**63 - 1  # Largest safe integer (i64 max)
        MIN_SAFE_INT = -(2**63)  # Smallest safe integer (i64 min)

        if not (MIN_SAFE_INT <= value <= MAX_SAFE_INT):
            raise SyntaxError(
                f"Integer literal {source_text} exceeds maximum safe range for any integer type"
            )

        return {
            "type": NodeType.COMPTIME_INT.value,
            "value": value,
            "source_text": source_text,  # Preserve original format for error messages
        }

    def _create_comptime_float(self, value: float, source_text: str) -> dict:
        """Create comptime_float with overflow detection"""
        # Check against f64 bounds (largest float type)
        import sys

        if not (-sys.float_info.max <= value <= sys.float_info.max):
            raise SyntaxError(
                f"Float literal {source_text} exceeds maximum safe range for any float type"
            )

        return {
            "type": NodeType.COMPTIME_FLOAT.value,
            "value": value,
            "source_text": source_text,  # Preserve original format for error messages
        }

    def _create_comptime_number(self, value, source_text: str) -> dict:
        """Create appropriate comptime type for scientific notation"""
        if isinstance(value, int):
            return self._create_comptime_int(value, source_text)
        else:
            return self._create_comptime_float(value, source_text)

    def BOOLEAN(self, token):
        # Parse boolean literals: true -> {type: "literal", value: true}
        return {"type": NodeType.LITERAL.value, "value": str(token) == "true"}

    def INTEGER(self, token):
        # Parse integer literals for array dimensions: 3 -> 3
        return int(str(token))


class HexenParser:
    """Main parser class for Hexen language"""

    def __init__(self):
        # Load grammar from file
        grammar_path = Path(__file__).parent / "hexen.lark"
        with open(grammar_path, "r") as f:
            grammar = f.read()

        # Create parser with Earley algorithm
        self.parser = Lark(grammar, start="program", parser="earley")
        self.transformer = HexenTransformer()

    def parse(self, source_code: str) -> Dict[str, Any]:
        """Parse Hexen source code into AST"""
        try:
            # Parse source code
            parse_tree = self.parser.parse(source_code)

            # Transform into AST
            ast = self.transformer.transform(parse_tree)

            return ast

        except Exception as e:
            raise SyntaxError(f"Parse error: {e}")

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse Hexen source file"""
        with open(file_path, "r") as f:
            source_code = f.read()
        return self.parse(source_code)
