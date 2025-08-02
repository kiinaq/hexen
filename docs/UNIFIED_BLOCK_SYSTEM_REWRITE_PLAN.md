# UNIFIED_BLOCK_SYSTEM.md Complete Rewrite Plan 🦉

## 🚨 Critical Issues Identified

The current UNIFIED_BLOCK_SYSTEM.md document contains **fundamental errors** that misrepresent how expression blocks work with Hexen's comptime type system. The document needs a complete rewrite to align with our refined understanding of compile-time vs runtime expression block evaluation.

## 📋 Main Problems to Fix

### 1. **Incorrect Comptime Type Preservation Claims**
- Document claims all expression blocks can preserve comptime types
- 90% of examples show runtime operations falsely claiming comptime preservation
- No distinction between compile-time evaluable vs runtime evaluable blocks

### 2. **Missing Fundamental Distinction**
- No explanation of when expression blocks can preserve comptime types
- No explanation of when explicit context is required
- Missing the core insight: runtime blocks need explicit types

### 3. **Misleading Examples Throughout**
- Lines 67-73: Runtime function calls claiming comptime preservation
- Lines 309-321: Mixed runtime/comptime examples without proper context requirements
- Lines 431-448: Incorrect claims about `val` vs `mut` with runtime blocks

### 4. **Missing Solution to "Untyped Literal Problem"**
- No explanation of how our approach solves ambiguity concerns
- No demonstration of compile-time evaluation vs explicit context pattern

## 🎯 Rewrite Strategy

### **Session 1: Core Foundation** (This session)
**Goal**: Establish the fundamental compile-time vs runtime distinction

**Tasks**:
1. Add new major section: "Compile-Time vs Runtime Expression Blocks"
2. Define the two categories clearly
3. Provide basic examples of each
4. Update the "Block Types and Contexts" section to reflect this distinction

**Estimated Lines**: ~150-200 lines of new/revised content

### **Session 2: Expression Block Examples Overhaul**
**Goal**: Fix all the incorrect examples throughout the document

**Tasks**:
1. Fix Section 1 "Expression Blocks" examples (lines 41-83)
2. Update "Dual Capability" examples (lines 200-280)
3. Correct "Type System Integration" examples (lines 308-449)
4. Ensure all runtime examples show explicit context requirements

**Estimated Lines**: ~300+ lines of corrections

### **Session 3: Advanced Patterns & Integration**
**Goal**: Update advanced usage patterns and integration sections

**Tasks**:
1. Fix "Advanced Usage Patterns" (lines 569-659) 
2. Update all type system integration claims
3. Add section addressing "Untyped Literal Problem" solution
4. Ensure consistency with BINARY_OPS.md and TYPE_SYSTEM.md

**Estimated Lines**: ~200+ lines of updates

### **Session 4: Final Review & Polish**
**Goal**: Comprehensive review and documentation polish

**Tasks**:
1. Review entire document for consistency
2. Verify all examples are correct
3. Update error handling section
4. Add cross-references to other docs
5. Final proofreading

**Estimated Lines**: ~100+ lines of refinements

## 📐 Key Concepts to Establish

### **The Fundamental Rule**
Expression blocks fall into two categories:

1. **✅ Compile-Time Evaluable**: Can preserve comptime types
   - All conditions are compile-time constants
   - All operations involve only comptime types or constants
   - No runtime function calls (except pure comptime functions)

2. **❌ Runtime Evaluable**: Require explicit context
   - Contains runtime conditions or function calls
   - Cannot preserve comptime types
   - Must have explicit type annotation

### **The Ambiguity Solution**
This approach solves the "untyped literal problem":
- **Compile-time cases**: No ambiguity (compiler can evaluate everything)
- **Runtime cases**: Explicit context required (eliminates ambiguity)
- **No default types needed**: Context is always available when needed

## 🔧 Example Templates for Consistency

### **Compile-Time Block Template**
```hexen
// ✅ Compile-time evaluable (comptime type preservation)
val flexible_block = {
    val x = 42 + 100           // comptime_int + comptime_int → comptime_int
    val y = x * 3.14           // comptime_int * comptime_float → comptime_float
    assign y                   // Result: comptime_float (preserved!)
}

// Later usage adapts to different contexts
val as_f32 : f32 = flexible_block    // comptime_float → f32
val as_f64 : f64 = flexible_block    // Same source → f64
```

### **Runtime Block Template**
```hexen
// ❌ Runtime evaluable (explicit context required)
val result : i32 = {              // Context REQUIRED!
    val input = get_user_input()  // Runtime function call
    if input > 0 {                // Runtime condition  
        assign input              // All paths resolve to i32
    } else {
        assign 0                  // All paths resolve to i32
    }
}
```

### **Mixed Block Template**  
```hexen
// 🔄 Mixed (comptime + runtime = runtime, context required)
val mixed_result : f64 = {        // Context REQUIRED!
    val comptime_base = 42 * 3.14 // comptime operations
    val runtime_val = get_value()  // Runtime function call
    assign comptime_base + runtime_val:f64  // Mixed → explicit conversion needed
}
```

## 📚 Integration Points

### **References to Update**
- All references to TYPE_SYSTEM.md patterns
- All references to BINARY_OPS.md behavior  
- All claims about `val` vs `mut` variable behavior
- All examples of function parameter context

### **New Cross-References to Add**
- Link to COMPTIME_QUICK_REFERENCE.md for basic patterns
- Reference to the "untyped literal problem" blog post discussion
- Connection to compile-time execution benefits from BINARY_OPS.md

## 🎭 Session Boundaries

### **Why Split Into Sessions**
1. **Context Length**: Complete rewrite would exceed single session limits
2. **Quality Control**: Each session focuses on specific aspects for thoroughness  
3. **Iterative Refinement**: Earlier sessions inform later improvements
4. **Manageable Scope**: Prevents overwhelming changes in single commit

### **Session Coordination**
- Each session will update the TODO list to track progress
- Each session will commit changes independently  
- Final session will ensure overall document coherence
- Cross-references will be updated in final session

## 🎯 Success Criteria

### **Technical Accuracy**
- [ ] All examples correctly distinguish compile-time vs runtime blocks
- [ ] All comptime type preservation claims are accurate
- [ ] All explicit context requirements are properly documented

### **Conceptual Clarity**  
- [ ] Clear explanation of the fundamental distinction
- [ ] Solution to "untyped literal problem" is demonstrated
- [ ] Integration with type system is accurate and consistent

### **Documentation Quality**
- [ ] Examples are clear and correct
- [ ] Cross-references are accurate and helpful
- [ ] Document flows logically from basic to advanced concepts

## 🚀 Starting Point: Session 1

Begin with establishing the foundational "Compile-Time vs Runtime Expression Blocks" section, which will serve as the conceptual anchor for all subsequent corrections.

This section should come early in the document (after "Core Philosophy") to establish the framework that all other sections will reference.

---

**Next Step**: Begin Session 1 by adding the fundamental distinction section and updating the core block type definitions.