"""
Hexen Parser

Parser for Hexen language with variable declarations using Lark.
"""

from pathlib import Path
from lark import Lark, Transformer, v_args
from typing import Dict, Any


class HexenTransformer(Transformer):
    """Transform parse tree into meaningful AST nodes"""

    @v_args(inline=True)
    def function(self, name, return_type, body):
        return {
            "type": "function",
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
                "type": "val_declaration",
                "name": name["name"],
                "type_annotation": None,
                "value": value,
            }
        else:
            # With type annotation: val name : type = value
            val_token, name, type_annotation, value = args
            return {
                "type": "val_declaration",
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
                "type": "mut_declaration",
                "name": name["name"],
                "type_annotation": None,
                "value": value,
            }
        else:
            # With type annotation: mut name : type = value
            mut_token, name, type_annotation, value = args
            return {
                "type": "mut_declaration",
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
            return {"type": "return_statement", "value": None}
        else:
            # Return with expression
            return {"type": "return_statement", "value": args[0]}

    @v_args(inline=True)
    def assignment_stmt(self, target, value):
        # Handle: IDENTIFIER "=" expression
        return {
            "type": "assignment_statement",
            "target": target["name"],  # Extract name from identifier dict
            "value": value,
        }

    def expression(self, children):
        # expression: NUMBER | STRING | IDENTIFIER | block
        return children[0]

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
        return {"type": "block", "statements": list(statements)}

    def program(self, functions):
        return {"type": "program", "functions": list(functions)}

    # Terminal handlers for new grammar elements (Phase 1 additions)
    def STRING(self, token):
        # Parse string literals: "hello" -> {type: "literal", value: "hello"}
        # Remove surrounding quotes from the token
        return {"type": "literal", "value": str(token)[1:-1]}

    def IDENTIFIER(self, token):
        # Parse identifiers: myVar -> {type: "identifier", name: "myVar"}
        # Used for variable names and references
        return {"type": "identifier", "name": str(token)}

    def NUMBER(self, token):
        # Parse number literals with support for both integers and floats
        # 42 -> {type: "literal", value: 42} (int)
        # 3.14 -> {type: "literal", value: 3.14} (float)
        token_str = str(token)
        if "." in token_str:
            # Float literal
            return {"type": "literal", "value": float(token_str)}
        else:
            # Integer literal
            return {"type": "literal", "value": int(token_str)}

    def BOOLEAN(self, token):
        # Parse boolean literals: true -> {type: "literal", value: true}
        return {"type": "literal", "value": str(token) == "true"}


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
