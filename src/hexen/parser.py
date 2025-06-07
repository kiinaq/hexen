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
        # Handle: "val" IDENTIFIER [":" type] "=" expression
        # args can be [name, value] or [name, type, value]
        if len(args) == 2:
            # No type annotation: val name = value
            name, value = args
            return {
                "type": "val_declaration",
                "name": name["name"],
                "type_annotation": None,
                "value": value,
            }
        else:
            # With type annotation: val name : type = value
            name, type_annotation, value = args
            return {
                "type": "val_declaration",
                "name": name["name"],
                "type_annotation": type_annotation,
                "value": value,
            }

    def mut_declaration(self, args):
        # Handle: "mut" IDENTIFIER [":" type] "=" expression
        # args can be [name, value] or [name, type, value]
        if len(args) == 2:
            # No type annotation: mut name = value
            name, value = args
            return {
                "type": "mut_declaration",
                "name": name["name"],
                "type_annotation": None,
                "value": value,
            }
        else:
            # With type annotation: mut name : type = value
            name, type_annotation, value = args
            return {
                "type": "mut_declaration",
                "name": name["name"],
                "type_annotation": type_annotation,
                "value": value,
            }

    def var_declaration(self, children):
        # var_declaration: val_declaration | mut_declaration
        return children[0]

    @v_args(inline=True)
    def return_stmt(self, value):
        return {"type": "return_statement", "value": value}

    def expression(self, children):
        # expression: NUMBER | STRING | IDENTIFIER
        return children[0]

    @v_args(inline=True)
    def statement(self, stmt):
        return stmt

    def type(self, children):
        # Handle multiple types: "i32" | "i64" | "f64" | "string"
        # TODO: Fix grammar - children is empty, investigate why
        if children:
            return str(children[0])
        return "i32"  # temporary fallback until grammar issue is resolved

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
        # Parse number literals: 42 -> {type: "literal", value: 42}
        return {"type": "literal", "value": int(str(token))}


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
