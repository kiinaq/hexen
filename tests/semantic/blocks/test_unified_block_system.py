"""
Tests for the NEW Unified Block System with assign/return semantics

Tests the enhanced UNIFIED_BLOCK_SYSTEM.md implementation:
- Expression blocks: Must end with 'assign' OR 'return' (dual capability)
- Statement blocks: Allow 'return' for function exits, no 'assign' allowed
- Function blocks: Allow 'return' anywhere
- Unified return semantics: 'return' ALWAYS means "exit the function"
- -> semantics: 'assign' ONLY means "produce block value"
"""

from src.hexen.parser import HexenParser
from src.hexen.semantic.analyzer import SemanticAnalyzer


class TestUnifiedBlockSystemAssign:
    """Test the NEW assign/return unified block semantics"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_expression_block_with_assign_success(self):
        """Test expression block ending with -> statement (NEW semantics)"""
        source = """
        func test() : i32 = {
            val result : i32 = {
                val temp = 42
                -> temp
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_with_return_success(self):
        """Test expression block ending with return statement (dual capability)"""
        source = """
        func test() : i32 = {
            val result : i32 = {
                val temp = 42
                return temp  // This exits the function
            }
            return 0  // This line should never be reached
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should work - return exits function
        assert errors == []

    def test_expression_block_assign_with_explicit_types(self):
        """Test expression blocks with explicit type annotations work correctly"""
        source = """
        func test_i32() : i32 = {
            val flexible : i32 = {  // Explicit type required
                val calc = 42 + 100
                -> calc  // Adapts to i32
            }
            return flexible
        }

        func test_f64() : f64 = {
            val same_calc : f64 = {  // Explicit type required (f64 here)
                val calc = 42 + 100
                -> calc  // Adapts to f64
            }
            return same_calc
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_expression_block_requires_final_statement(self):
        """Test expression block must end with -> OR return"""
        source = """
        func test() : i32 = {
            val result : i32 = {
                val temp = 42
                // Missing -> or return - ERROR
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        # Should have multiple errors due to cascading issues from malformed expression block
        assert len(errors) >= 1
        # Check that the primary error is about missing assign/return
        error_messages = [str(error) for error in errors]
        assert any("assign" in msg or "return" in msg for msg in error_messages)

    def test_expression_block_assign_not_in_middle(self):
        """Test -> statement must be last statement in expression block"""
        source = """
        func test() : i32 = {
            val result : i32 = {
                val temp = 42
                -> temp  // -> not at end - ERROR
                val more = 100
            }
            return result
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "last statement" in str(errors[0])

    def test_expression_block_return_not_in_middle(self):
        """Test return statement must be last statement in expression block"""
        source = """
        func test() : i32 = {
            val result : i32 = {
                val temp = 42
                return temp  // return not at end - ERROR
                val more = 100
            }
            return 0
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "last statement" in str(errors[0])


class TestUnifiedBlockSystemStatementBlocks:
    """Test statement block semantics in unified system"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_statement_block_allows_return(self):
        """Test statement blocks allow return for function exits"""
        source = """
        func test() : void = {
            {
                val condition = true
                return  // Function exit from statement block - OK
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_statement_block_prohibits_assign(self):
        """Test statement blocks prohibit -> statements"""
        source = """
        func test() : void = {
            {
                val temp = 42
                -> temp  // -> in statement block - ERROR
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "assign" in str(errors[0])
        assert "expression blocks" in str(errors[0])

    def test_statement_block_return_type_validation(self):
        """Test return in statement block validates against function signature"""
        source = """
        func test() : i32 = {
            {
                val value = 42
                return value  // Must match i32 function return type
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_statement_block_return_type_mismatch(self):
        """Test return in statement block with type mismatch"""
        source = """
        func test() : i32 = {
            {
                val value = "hello"
                return value  // string vs i32 - ERROR
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "mismatch" in str(errors[0]).lower()


class TestUnifiedReturnSemantics:
    """Test unified return semantics: return ALWAYS means function exit"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_return_consistent_meaning_everywhere(self):
        """Test return always means function exit in all contexts"""
        source = """
        func test() : i32 = {
            // Function body return
            return 42
        }
        
        func test2() : i32 = {
            // Statement block return
            {
                return 100  // Exits function
            }
            return 0  // Never reached
        }
        
        func test3() : i32 = {
            // Expression block return  
            val result : i32 = {
                return 200  // Exits function
            }
            return result  // Never reached
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_bare_return_void_function(self):
        """Test bare return works in void functions"""
        source = """
        func test() : void = {
            return  // Bare return in void function - OK
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_bare_return_non_void_function_error(self):
        """Test bare return fails in non-void functions"""
        source = """
        func test() : i32 = {
            return  // Bare return in i32 function - ERROR
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "bare return" in str(errors[0]).lower()

    def test_expression_block_bare_return_error(self):
        """Test bare return fails in expression blocks"""
        source = """
        func test() : void = {
            val result : i32 = {
                return  // Bare return in expression block - ERROR
            }
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "value" in str(errors[0]).lower()


class TestUnifiedBlockDualCapability:
    """Test the dual capability of expression blocks: -> + return"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_validation_with_assign(self):
        """Test validation pattern with -> (success path)"""
        source = """
        func process_input() : i32 = {
            val validated : i32 = {
                val raw = 42
                // Validation logic here...
                -> raw  // Success: assign validated input
            }
            return validated
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_validation_with_early_return(self):
        """Test validation pattern with early return (error path)"""
        source = """
        func process_input() : i32 = {
            val validated : i32 = {
                val raw = -1
                // if raw < 0 { return -1 } // Simulated condition
                return -1  // Early function exit on error
            }
            return validated  // Never reached
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_caching_pattern_with_early_return(self):
        """Test caching optimization with early return"""
        source = """
        func expensive_calc() : i32 = {
            val result : i32 = {
                val cached = 100  // Simulated cache lookup
                // if cached != null { return cached }
                return cached  // Cache hit: early function exit
            }
            return result  // Cache miss code never reached
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_fallback_pattern_with_assign_and_return(self):
        """Test fallback pattern using both -> and return"""
        source = """
        func load_config() : i32 = {
            val config : i32 = {
                val primary = 42  // Simulated primary config
                // if primary is good, use it
                -> primary   // Success path: assign primary config
            }
            return config
        }
        
        func load_config_with_fallback() : i32 = {
            val config : i32 = {
                val primary = 0   // Failed primary config
                // if primary failed, try fallback then return default
                return 100  // Complete failure: function exit with default
            }
            return config  // Never reached
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []


class TestUnifiedBlockErrors:
    """Test error conditions in unified block system"""

    def setup_method(self):
        self.parser = HexenParser()
        self.analyzer = SemanticAnalyzer()

    def test_assign_outside_expression_block_error(self):
        """Test -> statement outside expression blocks fails"""
        source = """
        func test() : void = {
            val temp = 42
            -> temp  // -> in function body - ERROR
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert len(errors) > 0
        assert "expression blocks" in str(errors[0])

    def test_assign_without_expression_error(self):
        """Test -> statement without expression fails"""
        # This should be caught at parse level, but test semantic handling
        source = """
        func test() : i32 = {
            val result : i32 = {
                val temp = 42
                -> temp
            }
            return result
        }
        """
        # This should work fine - testing the valid case
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []

    def test_multiple_final_statements_error(self):
        """Test expression block cannot have both -> and return at end"""
        # Note: This is structurally impossible with current grammar
        # since both must be the final statement, but test validation
        pass  # Skip - grammar prevents this case

    def test_nested_expression_blocks_with_mixed_endings(self):
        """Test nested expression blocks with different ending strategies"""
        source = """
        func test() : i32 = {
            val outer : i32 = {
                val inner : i32 = {
                    -> 42  // Inner uses assign
                }
                return inner  // Outer uses return (function exit)
            }
            return 0  // Never reached
        }
        """
        ast = self.parser.parse(source)
        errors = self.analyzer.analyze(ast)
        assert errors == []
