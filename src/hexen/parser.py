"""
Hexen Parser

Ultra-minimal parser for Hexen language using Lark.
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
            "name": str(name),
            "return_type": return_type,
            "body": body,
        }

    @v_args(inline=True)
    def return_stmt(self, value):
        return {"type": "return_statement", "value": value}

    @v_args(inline=True)
    def expression(self, value):
        return {"type": "literal", "value": int(str(value))}

    def type(self, children):
        # type rule: "i32" - no children, just return the literal
        return "i32"

    @v_args(inline=True)
    def block(self, statement):
        return statement

    @v_args(inline=True)
    def statement(self, stmt):
        return stmt

    def program(self, functions):
        return {"type": "program", "functions": list(functions)}


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
