"""
Hexen CLI

Command-line interface for Hexen compiler.
"""

import sys
import json
from pathlib import Path
from .parser import HexenParser


def main():
    """Main CLI entry point"""
    if len(sys.argv) != 3:
        print("Usage: hexen parse <file.hx>")
        sys.exit(1)
    
    command = sys.argv[1]
    file_path = sys.argv[2]
    
    if command != "parse":
        print("Only 'parse' command supported for now")
        sys.exit(1)
    
    if not Path(file_path).exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    try:
        parser = HexenParser()
        ast = parser.parse_file(file_path)
        
        print("✅ Parse successful!")
        print("\n🌳 Abstract Syntax Tree:")
        print(json.dumps(ast, indent=2))
        
    except SyntaxError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 