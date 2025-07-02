# Hexen Examples 🦉

This directory contains comprehensive examples demonstrating every Hexen language feature. The examples are organized by learning progression and feature categories.

## 📚 Learning Path

> **🚀 Quick Reference**: Before diving into examples, check out the **[Comptime Types Quick Reference →](../docs/COMPTIME_QUICK_REFERENCE.md)** for essential patterns and mental models!

### 01. Getting Started
Perfect for newcomers to Hexen - covers the absolute basics:

- **`hello_world.hxn`** - The simplest possible Hexen program
- **`basic_variables.hxn`** - Introduction to `val` and `mut` variables  
- **`functions.hxn`** - Function basics with return types and void functions

### 02. Types
Comprehensive coverage of Hexen's type system:

- **`all_types.hxn`** - Complete type system showcase (`i32`, `i64`, `f64`, `string`, `bool`, `void`)
- **`comptime_types.hxn`** - Comptime type system demonstration with elegant coercion
- **`comptime_quick_patterns.hxn`** - ⚡ Practical demonstration of quick reference patterns
- **`i64_numbers.hxn`** - 64-bit integer handling with seamless coercion
- **`booleans.hxn`** - Deep dive into boolean types and patterns

### 03. Blocks
Hexen's powerful unified block system:

- **`expression_blocks.hxn`** - Blocks that compute and return values
- **`statement_blocks.hxn`** - Blocks for scoped execution and organization

### 04. Advanced
Advanced language features and patterns:

- **`assignments.hxn`** - Comprehensive assignment patterns and type safety

### 05. Complete
Real-world usage examples:

- **`comprehensive_demo.hxn`** - All features working together in a realistic program

## 🎯 Quick Start

```bash
# Parse any example to see its AST
uv run hexen parse examples/01_getting_started/hello_world.hxn

# Try the comprehensive demo
uv run hexen parse examples/05_complete/comprehensive_demo.hxn
```

## ✨ Featured Concepts

Each example demonstrates specific Hexen features:

### Core Language Features
- **Type Inference**: `val x = 42` (automatically `i32`)
- **Explicit Types**: `val x : i64 = 42` (when you need control)
- **Immutable by Default**: `val` variables prevent accidental changes
- **Opt-in Mutability**: `mut` variables when you need reassignment
- **Unified Blocks**: Same `{}` syntax for expressions, statements, and functions

### Type System
- **Five Core Types**: `i32`, `i64`, `f64`, `string`, `bool` 
- **Void Functions**: `func setup() : void = { return }`
- **Type Safety**: Compile-time prevention of type mismatches
- **Uninitialized Variables**: `val x : i32 = undef` for later initialization

### Advanced Features
- **Expression Blocks**: `val result = { return 42 }` - blocks that produce values
- **Statement Blocks**: `{ val temp = 100 }` - scoped execution without return
- **Variable Shadowing**: Inner scopes can redefine outer variables
- **Lexical Scoping**: Inner scopes access outer scope variables

## 🧪 Testing Examples

All examples are valid Hexen code and pass semantic analysis:

```bash
# Test that all examples parse correctly
find examples -name "*.hxn" -exec uv run hexen parse {} \;
```

## 📖 Design Philosophy

These examples embody Hexen's core principles:

- **🎯 Ergonomic**: Easy to read and understand
- **🧹 Clean**: One clear way to do each thing  
- **🧠 Logical**: Features build upon each other naturally
- **⚡ Pragmatic**: Focus on what works best

## 🗂️ Legacy Files

The old example files have been reorganized:
- `hello.hxn` → `05_complete/comprehensive_demo.hxn` (enhanced)
- `variables.hxn` → `01_getting_started/basic_variables.hxn` (fixed syntax)
- `bool_test.hxn` → `02_types/booleans.hxn` (enhanced)
- `assignment_demo.hxn` → `04_advanced/assignments.hxn` (reorganized)
- `comment_showcase.hxn` → (comments work everywhere now, no dedicated example needed)

---

*Start with `01_getting_started/hello_world.hxn` and work your way through! 🚀* 