# Literal Parsing Enhancement Plan

## Overview

This document outlines a comprehensive plan to enhance Hexen's literal parsing capabilities by adding support for scientific notation and hexadecimal literals while implementing proper overflow behavior as specified in `LITERAL_OVERFLOW_BEHAVIOR.md`.

## Current State Analysis

### Current Grammar (hexen.lark:69)
```lark
NUMBER: /-?[0-9]+(\.[0-9]+)?/
```

### Current Parser Implementation (parser.py:320-330)
```python
def NUMBER(self, token):
    token_str = str(token)
    if "." in token_str:
        # Float literal → comptime_float
        return {"type": NodeType.COMPTIME_FLOAT.value, "value": float(token_str)}
    else:
        # Integer literal → comptime_int
        return {"type": NodeType.COMPTIME_INT.value, "value": int(token_str)}
```

### Limitations Identified
1. **No scientific notation support** (e.g., `1.23e-4`, `6.02E23`)
2. **No hexadecimal literal support** (e.g., `0xFF`, `0x1A2B`)
3. **No binary literal support** (e.g., `0b1010`, `0B1111`)
4. **Missing overflow detection** during parsing
5. **Basic float parsing** without precision validation

## Enhancement Goals

### 1. Scientific Notation Support
- **Float scientific notation**: `1.23e-4`, `6.02E+23`, `3.14E-2`
- **Integer scientific notation**: `1e6` (represents 1,000,000)
- **Case insensitive exponent**: Both `e` and `E` supported
- **Optional signs**: `+` and `-` in exponents

### 2. Hexadecimal Literal Support
- **Standard hex format**: `0x1A2B`, `0X1a2b`
- **Case insensitive**: Both `0x` and `0X` prefixes
- **Mixed case digits**: `0xAbCd`, `0X1a2B3c`
- **Signed hex literals**: `-0xFF`, `+0x123`

### 3. Binary Literal Support
- **Standard binary format**: `0b1010`, `0B1111`
- **Case insensitive**: Both `0b` and `0B` prefixes
- **Signed binary literals**: `-0b1010`, `+0B1111`

### 4. Overflow Detection Integration
- **Compile-time range validation** per `LITERAL_OVERFLOW_BEHAVIOR.md`
- **Clear error messages** with value range information
- **Consistent with comptime type system** 

## Detailed Implementation Plan

### Phase 1: Grammar Enhancement

#### 1.1 Update Lark Grammar Rules

**Replace existing NUMBER rule with comprehensive literal rules:**

```lark
// Enhanced number literals with all formats
NUMBER: scientific_number | hex_number | binary_number | decimal_number

// Scientific notation (highest priority for complex patterns)
scientific_number: DECIMAL_PART EXPONENT_PART
                 | INTEGER_PART EXPONENT_PART

// Hexadecimal literals  
hex_number: HEX_PREFIX HEX_DIGITS

// Binary literals
binary_number: BIN_PREFIX BIN_DIGITS

// Standard decimal numbers (fallback)
decimal_number: DECIMAL_PART | INTEGER_PART

// Component definitions
DECIMAL_PART: SIGN? DIGITS "." DIGITS
INTEGER_PART: SIGN? DIGITS
EXPONENT_PART: ("e"|"E") SIGN? DIGITS
HEX_PREFIX: "0" ("x"|"X")
BIN_PREFIX: "0" ("b"|"B")
HEX_DIGITS: /[0-9a-fA-F]+/
BIN_DIGITS: /[01]+/
DIGITS: /[0-9]+/
SIGN: "+"|"-"
```

#### 1.2 Alternative Simplified Approach (Recommended)

**Single comprehensive NUMBER rule that captures all formats:**

```lark
// All-in-one number pattern (easier to maintain)
NUMBER: SIGN? (SCIENTIFIC | HEXADECIMAL | BINARY | DECIMAL | INTEGER)

SCIENTIFIC: (DIGITS "." DIGITS | DIGITS) ("e"|"E") SIGN? DIGITS
HEXADECIMAL: "0" ("x"|"X") /[0-9a-fA-F]+/
BINARY: "0" ("b"|"B") /[01]+/
DECIMAL: DIGITS "." DIGITS
INTEGER: DIGITS

DIGITS: /[0-9]+/
SIGN: /[+-]/
```

### Phase 2: Parser Enhancement

#### 2.1 Enhanced NUMBER Handler

**Replace current NUMBER method with comprehensive parser:**

```python
def NUMBER(self, token):
    """Enhanced number parser supporting all literal formats with overflow detection"""
    token_str = str(token).strip()
    
    try:
        # Handle negative sign
        is_negative = token_str.startswith('-')
        if is_negative or token_str.startswith('+'):
            token_str = token_str[1:]
        
        # Determine literal type and parse
        if token_str.startswith(('0x', '0X')):
            # Hexadecimal literal
            value = self._parse_hex_literal(token_str[2:], is_negative)
            return self._create_comptime_int(value, f"{'-' if is_negative else ''}{token_str}")
            
        elif token_str.startswith(('0b', '0B')):
            # Binary literal  
            value = self._parse_binary_literal(token_str[2:], is_negative)
            return self._create_comptime_int(value, f"{'-' if is_negative else ''}{token_str}")
            
        elif 'e' in token_str.lower():
            # Scientific notation
            value = self._parse_scientific_literal(token_str, is_negative)
            return self._create_comptime_number(value, f"{'-' if is_negative else ''}{token_str}")
            
        elif '.' in token_str:
            # Decimal float
            value = float(f"{'-' if is_negative else ''}{token_str}")
            return self._create_comptime_float(value, f"{'-' if is_negative else ''}{token_str}")
            
        else:
            # Integer
            value = int(f"{'-' if is_negative else ''}{token_str}")
            return self._create_comptime_int(value, f"{'-' if is_negative else ''}{token_str}")
            
    except (ValueError, OverflowError) as e:
        raise SyntaxError(f"Invalid number literal '{str(token)}': {e}")
```

#### 2.2 Specialized Parsing Methods

```python
def _parse_hex_literal(self, hex_str: str, is_negative: bool) -> int:
    """Parse hexadecimal literal with validation"""
    try:
        value = int(hex_str, 16)
        if is_negative:
            value = -value
        return value
    except ValueError:
        raise SyntaxError(f"Invalid hexadecimal literal: 0x{hex_str}")

def _parse_binary_literal(self, bin_str: str, is_negative: bool) -> int:
    """Parse binary literal with validation"""
    try:
        value = int(bin_str, 2)
        if is_negative:
            value = -value
        return value
    except ValueError:
        raise SyntaxError(f"Invalid binary literal: 0b{bin_str}")

def _parse_scientific_literal(self, sci_str: str, is_negative: bool):
    """Parse scientific notation with validation"""
    try:
        value = float(f"{'-' if is_negative else ''}{sci_str}")
        # Determine if result should be comptime_int or comptime_float
        if value.is_integer() and abs(value) <= 2**63 - 1:
            return int(value)
        return value
    except (ValueError, OverflowError):
        raise SyntaxError(f"Invalid scientific literal: {sci_str}")
```

#### 2.3 Comptime Type Creation with Overflow Detection

```python
def _create_comptime_int(self, value: int, source_text: str) -> dict:
    """Create comptime_int with overflow detection"""
    # Check against absolute bounds for any integer type
    MAX_SAFE_INT = 2**63 - 1  # Largest safe integer (i64 max)
    MIN_SAFE_INT = -(2**63)   # Smallest safe integer (i64 min)
    
    if not (MIN_SAFE_INT <= value <= MAX_SAFE_INT):
        raise SyntaxError(f"Integer literal {source_text} exceeds maximum safe range for any integer type")
    
    return {
        "type": NodeType.COMPTIME_INT.value, 
        "value": value,
        "source_text": source_text  # Preserve original format for error messages
    }

def _create_comptime_float(self, value: float, source_text: str) -> dict:
    """Create comptime_float with overflow detection"""
    # Check against f64 bounds (largest float type)
    import sys
    if not (-sys.float_info.max <= value <= sys.float_info.max):
        raise SyntaxError(f"Float literal {source_text} exceeds maximum safe range for any float type")
    
    return {
        "type": NodeType.COMPTIME_FLOAT.value, 
        "value": value,
        "source_text": source_text  # Preserve original format for error messages
    }

def _create_comptime_number(self, value, source_text: str) -> dict:
    """Create appropriate comptime type for scientific notation"""
    if isinstance(value, int):
        return self._create_comptime_int(value, source_text)
    else:
        return self._create_comptime_float(value, source_text)
```

### Phase 3: Semantic Analyzer Integration

#### 3.1 Update Type Utilities (type_util.py)

**Enhance overflow detection in type coercion:**

```python
def validate_literal_range(value, target_type: str, source_text: str = None) -> bool:
    """Validate literal fits in target type range per LITERAL_OVERFLOW_BEHAVIOR.md"""
    
    type_ranges = {
        'i32': (-2147483648, 2147483647),
        'i64': (-9223372036854775808, 9223372036854775807),
        'f32': (-3.4028235e+38, 3.4028235e+38),
        'f64': (-1.7976931348623157e+308, 1.7976931348623157e+308)
    }
    
    if target_type not in type_ranges:
        return True  # Unknown type, let other validation handle it
    
    min_val, max_val = type_ranges[target_type]
    
    if not (min_val <= value <= max_val):
        display_text = source_text or str(value)
        raise TypeError(f"Literal {display_text} overflows {target_type} range\n"
                       f"  Expected: {min_val} to {max_val}\n"
                       f"  Suggestion: Use explicit conversion if truncation is intended: {display_text}:{target_type}")
    
    return True
```

#### 3.2 Update Expression Analyzer

**Integrate overflow checking in literal resolution:**

```python
def analyze_comptime_literal(self, node: dict) -> dict:
    """Analyze comptime literal with enhanced format support"""
    value = node["value"]
    source_text = node.get("source_text", str(value))
    
    if node["type"] == NodeType.COMPTIME_INT.value:
        return {
            "type": "comptime_int",
            "value": value,
            "source_text": source_text,
            "is_literal": True
        }
    elif node["type"] == NodeType.COMPTIME_FLOAT.value:
        return {
            "type": "comptime_float", 
            "value": value,
            "source_text": source_text,
            "is_literal": True
        }
```

### Phase 4: Test Coverage Enhancement

#### 4.1 Parser Test Additions

**Create comprehensive test coverage in `tests/parser/test_literals.py`:**

```python
class TestLiteralParsing:
    """Test enhanced literal parsing capabilities"""
    
    def test_scientific_notation_integers(self):
        """Test scientific notation that resolves to integers"""
        cases = [
            ("1e3", 1000),        # 1 * 10^3
            ("2E6", 2000000),     # 2 * 10^6  
            ("1e+2", 100),        # Explicit positive exponent
            ("5e-0", 5),          # Zero exponent
            ("-3e2", -300),       # Negative scientific
        ]
        # Test parsing and semantic analysis
    
    def test_scientific_notation_floats(self):
        """Test scientific notation that remains float"""
        cases = [
            ("1.23e-4", 0.000123),
            ("6.02E+23", 6.02e23),
            ("3.14e2", 314.0),
            ("-2.5E-3", -0.0025),
        ]
        # Test parsing and semantic analysis
        
    def test_hexadecimal_literals(self):
        """Test hexadecimal literal parsing"""
        cases = [
            ("0xFF", 255),
            ("0x1A2B", 6699),
            ("0X00", 0),
            ("-0xABC", -2748),
            ("0xDEADBEEF", 3735928559),
        ]
        # Test parsing and semantic analysis
        
    def test_binary_literals(self):
        """Test binary literal parsing"""
        cases = [
            ("0b1010", 10),
            ("0B1111", 15),
            ("0b00000000", 0),
            ("-0b1001", -9),
            ("0B11111111", 255),
        ]
        # Test parsing and semantic analysis
        
    def test_overflow_detection(self):
        """Test overflow detection per LITERAL_OVERFLOW_BEHAVIOR.md"""
        overflow_cases = [
            ("4294967296", "i32"),      # 2^32, too large for i32
            ("18446744073709551616", "i64"),  # 2^64, too large for i64
            ("3.5e+38", "f32"),         # Too large for f32
            ("0x100000000", "i32"),     # 2^32 in hex, too large for i32
            ("0b100000000000000000000000000000000", "i32"),  # 2^32 in binary
        ]
        # Test that each case produces clear overflow error
        
    def test_boundary_values(self):
        """Test exact boundary values work correctly"""
        boundary_cases = [
            ("2147483647", "i32"),      # Max i32
            ("-2147483648", "i32"),     # Min i32  
            ("9223372036854775807", "i64"),  # Max i64
            ("-9223372036854775808", "i64"), # Min i64
        ]
        # Test that boundary values parse correctly
```

#### 4.2 Semantic Test Additions

**Create overflow behavior tests in `tests/semantic/test_literal_overflow.py`:**

```python
class TestLiteralOverflowBehavior:
    """Test overflow behavior per LITERAL_OVERFLOW_BEHAVIOR.md"""
    
    def test_comptime_preservation_with_enhanced_literals(self):
        """Test that enhanced literals preserve comptime flexibility"""
        test_cases = [
            "val flexible = 0xFF",           # Hex comptime_int
            "val scientific = 1e6",          # Scientific comptime_int  
            "val binary = 0b1010",           # Binary comptime_int
            "val sci_float = 1.23e-4",       # Scientific comptime_float
        ]
        # Test that all cases preserve comptime types for flexibility
        
    def test_overflow_error_messages(self):
        """Test that overflow errors provide clear guidance"""
        error_cases = [
            ("val x:i32 = 4294967296", "i32 range"),
            ("val y:f32 = 3.5e+38", "f32 range"),
            ("val z:i32 = 0x100000000", "i32 range"),
        ]
        # Test error message format matches LITERAL_OVERFLOW_BEHAVIOR.md
```

### Phase 5: Documentation Updates

#### 5.1 Update TYPE_SYSTEM.md

**Add section on enhanced literal formats:**

```markdown
### Enhanced Literal Formats

Hexen supports multiple literal formats for maximum flexibility:

#### Integer Literals
- **Decimal**: `42`, `-123`, `+456`
- **Hexadecimal**: `0xFF`, `0x1A2B`, `-0xABC`  
- **Binary**: `0b1010`, `0B1111`, `-0b1001`
- **Scientific (integer)**: `1e6`, `2E3`, `-5e2`

#### Float Literals  
- **Decimal**: `3.14`, `-2.5`, `+1.0`
- **Scientific**: `1.23e-4`, `6.02E+23`, `-2.5E-3`

#### Format Flexibility
```hexen
// Same value, different representations (all become comptime_int)
val decimal = 255
val hex = 0xFF  
val binary = 0b11111111
val scientific = 2.55e2

// All can adapt to any compatible type
val as_i32: i32 = decimal    // or hex, binary, scientific
val as_i64: i64 = hex        // or decimal, binary, scientific  
val as_f64: f64 = binary     // or decimal, hex, scientific
```
```

#### 5.2 Update LITERAL_OVERFLOW_BEHAVIOR.md

**Add enhanced literal format examples:**

```markdown
### Enhanced Literal Overflow Examples

#### Hexadecimal Overflow
```hexen
val valid_hex:i32 = 0x7FFFFFFF      // ✅ Max i32 in hex
val overflow_hex:i32 = 0x80000000   // ❌ Error: Overflows i32 range
```

#### Binary Overflow
```hexen  
val valid_bin:i32 = 0b01111111111111111111111111111111  // ✅ Max i32 in binary
val overflow_bin:i32 = 0b10000000000000000000000000000000 // ❌ Error: Overflows i32 range
```

#### Scientific Notation Overflow
```hexen
val valid_sci:i32 = 2e9           // ✅ 2 billion, fits in i32
val overflow_sci:i32 = 3e10       // ❌ Error: 30 billion, overflows i32
val float_sci:f32 = 1.5e20        // ✅ Scientific float, fits in f32
val overflow_float:f32 = 5e40     // ❌ Error: Overflows f32 range
```
```

## Implementation Timeline

### Week 1: Grammar and Basic Parsing
- [ ] Update `hexen.lark` with enhanced NUMBER rules
- [ ] Implement basic enhanced NUMBER handler in `parser.py`
- [ ] Create initial test cases for new literal formats
- [ ] Verify basic parsing functionality

### Week 2: Overflow Detection Integration  
- [ ] Implement overflow detection methods in parser
- [ ] Update type utilities with range validation
- [ ] Integrate with semantic analyzer
- [ ] Create overflow detection test suite

### Week 3: Comprehensive Testing
- [ ] Complete parser test coverage for all literal formats
- [ ] Complete semantic test coverage for overflow behavior
- [ ] Test integration with existing comptime type system
- [ ] Performance testing for complex literals

### Week 4: Documentation and Polish
- [ ] Update all relevant documentation files
- [ ] Create examples demonstrating new literal capabilities
- [ ] Error message refinement and consistency
- [ ] Final integration testing

## Risk Mitigation

### Grammar Complexity
- **Risk**: Complex grammar rules may cause parsing ambiguity
- **Mitigation**: Use simplified single NUMBER rule approach 
- **Testing**: Extensive parser test coverage with edge cases

### Backward Compatibility  
- **Risk**: Changes break existing literal parsing
- **Mitigation**: Ensure existing decimal literals continue working
- **Testing**: Regression test suite for existing functionality

### Performance Impact
- **Risk**: Enhanced parsing may slow compilation
- **Mitigation**: Profile parsing performance and optimize if needed
- **Testing**: Performance benchmarks with large literal datasets

### Error Message Quality
- **Risk**: Poor error messages for new literal formats  
- **Mitigation**: Follow LITERAL_OVERFLOW_BEHAVIOR.md error format
- **Testing**: Validate error messages match specification

## Success Criteria

1. **All literal formats parse correctly** (decimal, hex, binary, scientific)
2. **Overflow detection works per specification** with clear error messages
3. **Comptime type preservation maintained** for all literal formats
4. **100% test coverage** for new literal parsing capabilities
5. **Zero regression** in existing functionality
6. **Performance remains acceptable** (< 10% parsing overhead)
7. **Documentation updated** and examples provided

This plan provides a comprehensive roadmap for enhancing Hexen's literal parsing capabilities while maintaining compatibility with existing systems and adhering to the language's core design principles.