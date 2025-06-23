"""
Test context framework for semantic analysis

Phase 1 Semantic Tests - Context Framework
Tests the enhanced _analyze_expression method with target_type context parameter.
"""

from src.hexen.semantic import SemanticAnalyzer, HexenType


class TestContextFrameworkBasics:
    """Test basic context framework functionality"""

    def setup_method(self):
        self.analyzer = SemanticAnalyzer()

    def test_context_parameter_exists(self):
        """Test that _analyze_expression accepts target_type parameter"""
        # Create a simple literal node
        node = {"type": "literal", "value": 42}

        # Test without context (should work)
        result1 = self.analyzer._analyze_expression(node)
        assert result1 == HexenType.COMPTIME_INT

        # Test with context (should work)
        result2 = self.analyzer._analyze_expression(node, HexenType.I32)
        assert result2 == HexenType.COMPTIME_INT

    def test_context_propagation_to_variable_declarations(self):
        """Test that context is propagated to variable declarations"""

        # Parse the AST manually to create the expected structure
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "explicit",
                                "type_annotation": "i64",
                                "value": {"type": "literal", "value": 42},
                            }
                        ],
                    },
                }
            ],
        }

        # Should not produce errors - the comptime_int can coerce to i64
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_context_propagation_to_assignments(self):
        """Test that context is propagated to assignment statements"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "mut_declaration",
                                "name": "flexible",
                                "type_annotation": "f64",
                                "value": {"type": "literal", "value": 0.0},
                            },
                            {
                                "type": "assignment_statement",
                                "target": "flexible",
                                "value": {"type": "literal", "value": 42},
                            },
                        ],
                    },
                }
            ],
        }

        # Should not produce errors - comptime_int can coerce to f64
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_context_propagation_to_returns(self):
        """Test that context is propagated to return statements"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "f32",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "return_statement",
                                "value": {"type": "literal", "value": 42},
                            }
                        ],
                    },
                }
            ],
        }

        # Should not produce errors - comptime_int can coerce to f32
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestContextFrameworkWithParentheses:
    """Test context framework works correctly with parentheses"""

    def setup_method(self):
        self.analyzer = SemanticAnalyzer()

    def test_parenthesized_expression_with_context(self):
        """Test that parenthesized expressions receive context correctly"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "result",
                                "type_annotation": "i64",
                                "value": {
                                    "type": "literal",  # This represents (42) after parsing
                                    "value": 42,
                                },
                            }
                        ],
                    },
                }
            ],
        }

        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_nested_parentheses_with_context(self):
        """Test nested parentheses with context propagation"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "nested",
                                "type_annotation": "f32",
                                "value": {
                                    "type": "literal",  # This represents (((3.14))) after parsing
                                    "value": 3.14,
                                },
                            }
                        ],
                    },
                }
            ],
        }

        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_parenthesized_identifiers_with_context(self):
        """Test parenthesized identifiers work with context"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "source",
                                "type_annotation": "i32",
                                "value": {"type": "literal", "value": 42},
                            },
                            {
                                "type": "mut_declaration",
                                "name": "target",
                                "type_annotation": "i64",
                                "value": {
                                    "type": "identifier",  # This represents (source) after parsing
                                    "name": "source",
                                },
                            },
                        ],
                    },
                }
            ],
        }

        # Should not produce errors - i32 can coerce to i64
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestContextFrameworkWithBlocks:
    """Test context framework with block expressions"""

    def setup_method(self):
        self.analyzer = SemanticAnalyzer()

    def test_expression_block_with_return_context(self):
        """Test expression blocks receive return type context"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "i64",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "result",
                                "type_annotation": None,
                                "value": {
                                    "type": "block",
                                    "statements": [
                                        {
                                            "type": "val_declaration",
                                            "name": "computed",
                                            "type_annotation": None,
                                            "value": {"type": "literal", "value": 42},
                                        },
                                        {
                                            "type": "return_statement",
                                            "value": {
                                                "type": "identifier",
                                                "name": "computed",
                                            },
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "return_statement",
                                "value": {"type": "identifier", "name": "result"},
                            },
                        ],
                    },
                }
            ],
        }

        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0

    def test_nested_blocks_with_context(self):
        """Test nested blocks propagate context correctly"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "f64",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "return_statement",
                                "value": {
                                    "type": "block",
                                    "statements": [
                                        {
                                            "type": "return_statement",
                                            "value": {"type": "literal", "value": 3.14},
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                }
            ],
        }

        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestContextFrameworkCoercion:
    """Test context framework enables correct coercion"""

    def setup_method(self):
        self.analyzer = SemanticAnalyzer()

    def test_regular_type_coercion_with_context(self):
        """Test regular type coercion works with context"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "source_i32",
                                "type_annotation": "i32",
                                "value": {"type": "literal", "value": 42},
                            },
                            {
                                "type": "mut_declaration",
                                "name": "target_i64",
                                "type_annotation": "i64",
                                "value": {"type": "identifier", "name": "source_i32"},
                            },
                        ],
                    },
                }
            ],
        }

        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0


class TestContextFrameworkErrorHandling:
    """Test context framework error handling"""

    def setup_method(self):
        self.analyzer = SemanticAnalyzer()

    def test_invalid_coercion_with_context(self):
        """Test that invalid coercion still produces errors even with context"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "val_declaration",
                                "name": "invalid",
                                "type_annotation": "string",
                                "value": {"type": "literal", "value": 42},
                            }
                        ],
                    },
                }
            ],
        }

        # Should produce error - comptime_int cannot coerce to string
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Type mismatch" in errors[0].message

    def test_context_preserves_existing_error_detection(self):
        """Test that context framework doesn't break existing error detection"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "assignment_statement",
                                "target": "undefined_var",
                                "value": {"type": "literal", "value": 42},
                            }
                        ],
                    },
                }
            ],
        }

        # Should produce error - undefined variable
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Undefined variable" in errors[0].message

    def test_context_with_uninitialized_variables(self):
        """Test context framework with undef variables"""
        ast = {
            "type": "program",
            "functions": [
                {
                    "type": "function",
                    "name": "test",
                    "return_type": "void",
                    "body": {
                        "type": "block",
                        "statements": [
                            {
                                "type": "mut_declaration",
                                "name": "pending",
                                "type_annotation": "i32",
                                "value": {"type": "identifier", "name": "undef"},
                            },
                            {
                                "type": "assignment_statement",
                                "target": "pending",
                                "value": {"type": "literal", "value": 42},
                            },
                        ],
                    },
                }
            ],
        }

        # Should not produce errors - assignment to undef variable with context
        errors = self.analyzer.analyze(ast)
        assert len(errors) == 0
