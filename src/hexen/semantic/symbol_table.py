"""
Hexen Symbol Table Management

Symbol table implementation for managing variable declarations, scoping,
and symbol lookup during semantic analysis.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from .types import HexenType, Mutability


@dataclass
class Symbol:
    """
    Represents a symbol in the symbol table with full metadata.

    Tracks everything needed for semantic analysis:
    - Type information for type checking
    - Mutability for assignment validation
    - Initialization state for use-before-def checking
    - Usage tracking for dead code elimination

    Design note: Using dataclass for clean syntax while maintaining
    the ability to add computed properties later.
    """

    name: str
    type: HexenType
    mutability: Mutability
    declared_line: Optional[int] = None  # For better error reporting (future)
    initialized: bool = True  # False for undef variables - prevents use-before-init
    used: bool = False  # Track usage for dead code warnings


class SymbolTable:
    """
    Manages symbols and scopes using a scope stack.

    Implementation details:
    - Stack-based scope management (LIFO)
    - Inner scopes shadow outer scopes
    - Lexical scoping rules (can access outer scope variables)

    Scope lifecycle:
    1. enter_scope() - push new scope (function entry, block entry)
    2. declare_symbol() - add symbols to current scope
    3. lookup_symbol() - search from inner to outer scopes
    4. exit_scope() - pop current scope (function/block exit)

    Future extensions:
    - Nested function support
    - Module-level scopes
    - Import/export handling
    """

    def __init__(self):
        # Stack of scopes - each scope is a dict of name -> Symbol
        # Index 0 is global scope, higher indices are inner scopes
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Start with global scope
        self.current_function: Optional[str] = None  # Track current function context

    def enter_scope(self):
        """
        Enter a new scope (e.g., function body, block).

        Called when entering:
        - Function bodies
        - Block statements (future)
        - Loop bodies (future)
        """
        self.scopes.append({})

    def exit_scope(self):
        """
        Exit current scope and return to parent scope.

        Note: Never pop the global scope (index 0) to prevent stack underflow.
        This is a safety measure against malformed ASTs.
        """
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare_symbol(self, symbol: Symbol) -> bool:
        """
        Declare a symbol in the current scope.

        Returns False if symbol already exists in current scope.
        This prevents variable redeclaration within the same scope.

        Design decision: Shadowing is allowed across scopes but not within
        the same scope for clarity.
        """
        current_scope = self.scopes[-1]
        if symbol.name in current_scope:
            return False  # Already declared in this scope
        current_scope[symbol.name] = symbol
        return True

    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """
        Look up symbol in all scopes from innermost to outermost.

        Implements lexical scoping:
        - Search current scope first
        - Then parent scopes in reverse order
        - Return first match found
        - Return None if not found in any scope

        This allows inner scopes to shadow outer scopes naturally.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def mark_used(self, name: str) -> bool:
        """
        Mark a symbol as used for dead code analysis.

        Returns False if symbol not found.
        Used when analyzing identifier references to track which
        variables are actually used vs. just declared.
        """
        symbol = self.lookup_symbol(name)
        if symbol:
            symbol.used = True
            return True
        return False
