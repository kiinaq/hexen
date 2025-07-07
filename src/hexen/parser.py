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

    @v_args(inline=True)
    def function(self, name, return_type, body):
        return {
            "type": NodeType.FUNCTION.value,
            "name": name["name"],  # Extract name from identifier dict
            "return_type": return_type,
            "body": body,
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

    @v_args(inline=True)
    def assignment_stmt(self, target, value):
        # Handle: IDENTIFIER "=" expression
        return {
            "type": NodeType.ASSIGNMENT_STATEMENT.value,
            "target": target["name"],  # Extract name from identifier dict
            "value": value,
        }

    def expression(self, children):
        # Handle: expression [CONVERSION_OP type]
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
        # primary: NUMBER | STRING | BOOLEAN | IDENTIFIER | block | "(" expression ")"
        if len(children) == 1:
            return children[0]  # Direct primary expression
        else:
            # Parenthesized expression: "(" expression ")"
            return children[1]

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

    def program(self, functions):
        return {"type": NodeType.PROGRAM.value, "functions": list(functions)}

    # Terminal handlers for new grammar elements (Phase 1 additions)
    def STRING(self, token):
        # Parse string literals: "hello" -> {type: "literal", value: "hello"}
        # Remove surrounding quotes from the token
        return {"type": NodeType.LITERAL.value, "value": str(token)[1:-1]}

    def IDENTIFIER(self, token):
        # Parse identifiers: myVar -> {type: "identifier", name: "myVar"}
        # Used for variable names and references
        return {"type": NodeType.IDENTIFIER.value, "name": str(token)}

    def NUMBER(self, token):
        # Parse number literals as comptime types that adapt to context
        # 42 -> {type: "comptime_int", value: 42} (comptime_int)
        # 3.14 -> {type: "comptime_float", value: 3.14} (comptime_float)
        token_str = str(token)
        if "." in token_str:
            # Float literal → comptime_float
            return {"type": NodeType.COMPTIME_FLOAT.value, "value": float(token_str)}
        else:
            # Integer literal → comptime_int
            return {"type": NodeType.COMPTIME_INT.value, "value": int(token_str)}

    def BOOLEAN(self, token):
        # Parse boolean literals: true -> {type: "literal", value: true}
        return {"type": NodeType.LITERAL.value, "value": str(token) == "true"}


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
