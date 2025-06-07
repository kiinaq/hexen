"""
Hexen CLI

Command-line interface for Hexen compiler.
"""

import sys
import json
from pathlib import Path
from .parser import HexenParser
from .semantic import SemanticAnalyzer


def main():
    """Main CLI entry point"""
    if len(sys.argv) != 3:
        print("Usage:")
        print("  hexen parse <file.hxn>     - Parse and show AST")
        print("  hexen check <file.hxn>     - Parse and run semantic analysis")
        sys.exit(1)

    command = sys.argv[1]
    file_path = sys.argv[2]

    if command not in ["parse", "check"]:
        print("Commands: 'parse' or 'check'")
        sys.exit(1)

    if not Path(file_path).exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    try:
        parser = HexenParser()
        ast = parser.parse_file(file_path)

        print("✅ Parse successful!")

        if command == "parse":
            # Just show the AST
            print("\n🌳 Abstract Syntax Tree:")
            print(json.dumps(ast, indent=2))

        elif command == "check":
            # Run semantic analysis
            analyzer = SemanticAnalyzer()
            errors = analyzer.analyze(ast)

            if errors:
                print(f"\n❌ Semantic errors found ({len(errors)}):")
                for error in errors:
                    print(f"   • {error.message}")
                sys.exit(1)
            else:
                print("\n✅ Semantic analysis passed - no errors found!")
                print("\n📊 Symbol Information:")
                _show_symbol_table(analyzer.symbol_table)

    except SyntaxError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def _show_symbol_table(symbol_table):
    """Display symbol table information"""
    # Note: After analysis, we're back to global scope, but we can show
    # what was analyzed. For now, let's just indicate analysis completed.
    print("   Analysis completed successfully")


if __name__ == "__main__":
    main()
