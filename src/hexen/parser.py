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
            # Handle both old string names and new identifier dict format
            "name": name["name"] if isinstance(name, dict) else str(name),
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
        # Handle multiple types: "i32" | "i64" | "f64" | "string"
        # Note: In Lark, terminal-only rules may not always have children
        # so we provide a safe fallback to maintain backward compatibility
        if children:
            return str(children[0])
        return "i32"  # fallback for backward compatibility

    def block(self, statements):
        # Handle multiple statements in blocks (Phase 1 grammar extension)
        # Maintain backward compatibility: single statement returns as-is
        # Multiple statements return as block object with statements array
        if len(statements) == 1:
            return statements[
                0
            ]  # Backward compatibility with old single-statement blocks
        return {"type": "block", "statements": list(statements)}

    @v_args(inline=True)
    def statement(self, stmt):
        return stmt

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
