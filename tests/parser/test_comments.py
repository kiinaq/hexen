"""
Test suite for comment parsing

Comments should:
- Be ignored during parsing (not part of AST)
- Work as single-line // comments
- Work at start of line, end of line, and standalone
- Not interfere with semantic analysis
- Work in all contexts (functions, blocks, statements)
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic import SemanticAnalyzer


class TestBasicComments:
    """Test basic comment functionality"""

    def test_single_line_comment_standalone(self):
        """Test standalone single-line comments"""
        source = """
        // This is a comment
        func test() : void = {
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_inline_comments(self):
        """Test inline comments at end of lines"""
        source = """
        func test() : void = {  // Function comment
            mut x : i32 = 42    // Variable comment
            x = 100             // Assignment comment
            return              // Return comment
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_comments_between_statements(self):
        """Test comments between statements"""
        source = """
        func test() : void = {
            // First comment
            mut x : i32 = 42
            // Second comment
            x = 100
            // Third comment
            return
            // Final comment
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_multiple_functions_with_comments(self):
        """Test comments with multiple functions"""
        source = """
        // First function
        func first() : void = {
            mut x : i32 = 42  // Local variable
            return
        }
        
        // Second function  
        func second() : i32 = {
            val result = 100  // Return value
            return result
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestCommentsInBlocks:
    """Test comments in different block contexts"""

    def test_comments_in_statement_blocks(self):
        """Test comments in statement blocks"""
        source = """
        func test() : void = {
            mut x : i32 = 42
            {
                // Inside statement block
                mut y : i32 = 100  // Local variable
                x = y              // Assignment
            }
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_comments_in_nested_blocks(self):
        """Test comments in nested blocks"""
        source = """
        func test() : void = {
            // Outer level
            mut x : i32 = 42
            {
                // First nesting level
                mut y : i32 = 100
                {
                    // Second nesting level
                    x = y  // Assignment across scopes
                }
            }
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestCommentsWithAllFeatures:
    """Test comments with all language features"""

    def test_comments_with_assignments(self):
        """Test comments with assignment statements"""
        source = """
        func test() : void = {
            // Variable declarations
            mut counter : i32 = 0        // Initial value
            mut message : string = "hi"  // String variable
            
            // Assignments
            counter = 10         // First assignment
            counter = 20         // Second assignment
            message = "hello"    // String assignment
            
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_comments_with_type_annotations(self):
        """Test comments with explicit type annotations"""
        source = """
        func test() : void = {
            // Explicit types
            mut number : i32 = 42      // Integer type
            mut text : string = "hi"   // String type
            mut big : i32 = 100        // Integer type
            
            // Type assignments
            number = 100               // Same type assignment
            text = "world"             // String reassignment
            
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_comments_with_returns(self):
        """Test comments with return statements"""
        source = """
        func test_void() : void = {
            mut x : i32 = 42  // Setup
            return            // Bare return
        }
        
        func test_value() : i32 = {
            mut result : i32 = 100  // Calculate result
            return result           // Return the value
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []


class TestCommentEdgeCases:
    """Test edge cases for comments"""

    def test_empty_comments(self):
        """Test empty comments (just //)"""
        source = """
        func test() : void = {
            //
            mut x : i32 = 42  //
            //
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_comments_with_special_characters(self):
        """Test comments with special characters"""
        source = """
        func test() : void = {
            // Comment with symbols: !@#$%^&*()
            mut x : i32 = 42  // Numbers: 123456789
            // Unicode: café naïve résumé
            return
        }
        """

        parser = HexenParser()
        ast = parser.parse(source)

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        assert errors == []

    def test_comments_do_not_affect_semantics(self):
        """Test that comments don't affect semantic analysis"""
        # Same program with and without comments should have same semantics
        source_with_comments = """
        // Function with comments
        func test() : void = {
            // Declare variable
            mut x : i32 = 42  // Initial value
            // Assign new value  
            x = 100           // Updated value
            return            // Exit
        }
        """

        source_without_comments = """
        func test() : void = {
            mut x : i32 = 42
            x = 100
            return
        }
        """

        parser = HexenParser()

        ast_with = parser.parse(source_with_comments)
        ast_without = parser.parse(source_without_comments)

        analyzer = SemanticAnalyzer()
        errors_with = analyzer.analyze(ast_with)
        errors_without = analyzer.analyze(ast_without)

        # Both should have no errors and same semantic behavior
        assert errors_with == []
        assert errors_without == []
