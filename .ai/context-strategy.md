# Context Management Strategy

**Version:** 1.0
**Purpose:** Token optimization and tiered loading for AI agents
**Audience:** AI agents working in this repository

---

## Overview

This repository uses a **three-tier context loading strategy** (Progressive Disclosure of Abstractions - PDA) to optimize token usage while ensuring AI agents have necessary information at the right time.

**Token Budget:** 200k tokens total
- System + tools: ~16k tokens (8%)
- Target for messages: ~100k tokens (50%)
- Reserved buffer: ~84k tokens (42%)

**Problem:** Loading all documentation upfront wastes tokens on information not needed for current task.

**Solution:** Tiered loading - start minimal, drill down as needed.

---

## Three-Tier Loading Strategy

### Tier 1: Always Load First (~500-1000 tokens)

**Purpose:** Quick orientation, navigation to deeper context

**Load these first:**
1. **Repository `llms.txt`**
   - Repository overview and purpose
   - Core exports and API surface
   - Common workflows summary
   - Pointers to Tier 2 documentation

2. **README.md** (if quick start needed)
   - Installation instructions
   - Basic usage examples

**What you get:**
- High-level architecture
- Where to find detailed info (pointers to Tier 2)
- Common questions answered immediately
- Decision tree for what to load next

**Example - Starting work:**
```
AI Agent loads:
1. llms.txt (~500 tokens) → "This library provides X, exports Y, integrates with Z"
2. README.md (~300 tokens) → "Install with pip, basic usage example"

AI Agent knows:
- What this library does
- Core API surface
- How to get started
- Where to find detailed documentation
```

---

### Tier 2: Load When Designing/Integrating (~2000-5000 tokens)

**Purpose:** Deep context for specific domains, design patterns, integration

**Load these when:**
- Designing new code using this library
- Understanding architecture patterns
- Debugging integration issues
- Working with library internals

**Tier 2 Documents:**

1. **DETAILS.md**
   - Complete design guide
   - Integration patterns
   - Design rationale
   - Development workflows

2. **Specialized guides** (if they exist)
   - Architecture deep dives
   - Testing strategies
   - Contributing guidelines

**What you get:**
- Design rationale (why these patterns?)
- Integration patterns (how to use with other libraries)
- Complete workflows (step-by-step guides)
- Common pitfalls and solutions

**Example - Designing integration:**
```
AI Agent already loaded Tier 1.

User: "How do I integrate this library with another platform?"

AI Agent loads Tier 2:
1. DETAILS.md → "Integration patterns section, platform compatibility notes"

AI Agent now has:
- Integration best practices
- Platform constraints
- Example integration patterns
```

---

### Tier 3: Load For Implementation (~5000+ tokens)

**Purpose:** Source code, implementation details, debugging

**Load these when:**
- Actually writing/editing code
- Debugging specific errors
- Understanding implementation internals
- Fixing bugs in library code

**Tier 3 Sources:**

1. **Source code files**
   - Core implementation modules
   - Internal utilities
   - Type definitions

2. **Test files** (when debugging)
   - Unit tests
   - Integration tests
   - Test fixtures

**What you get:**
- Actual implementation code
- Line-by-line logic
- Test examples
- Internal implementation details

**Example - Debugging issue:**
```
AI Agent already loaded Tier 1 & 2.

User: "The validation function is rejecting valid input"

AI Agent loads Tier 3:
1. src/module/validation.py → "Implementation of validation logic"
2. tests/test_validation.py → "Test cases to understand expected behavior"

AI Agent can now:
- Trace validation logic
- Identify bug in implementation
- Verify with test cases
```

---

## Decision Tree: What to Load When

### Starting a New Task

```
User request arrives
    ↓
Load Tier 1 (always)
    ↓
Is this a quick question? (API lookup, usage example, etc.)
    ↓ Yes → Answer from Tier 1
    ↓ No
    ↓
Does this involve design/integration?
    ↓ Yes → Load Tier 2 (DETAILS.md, specialized guides)
    ↓ No
    ↓
Does this involve implementation/debugging?
    ↓ Yes → Load Tier 3 (source code, tests)
```

### Examples by Question Type

**Quick Questions (Tier 1 only):**
- "What does this library do?"
  - Answer from llms.txt → Core purpose and exports

- "How do I install this?"
  - Answer from README.md → Installation instructions

- "What's the basic usage?"
  - Answer from llms.txt → Quick usage example

**Design Questions (Tier 1 + 2):**
- "What are the design patterns used here?"
  - Tier 1: llms.txt → "See DETAILS.md for design patterns"
  - Tier 2: DETAILS.md → "Design Principles section"

- "How do I integrate with library X?"
  - Tier 1: llms.txt → "Integration notes section"
  - Tier 2: DETAILS.md → "Integration with Sibling Libraries"

**Implementation Questions (Tier 1 + 2 + 3):**
- "Why is function X behaving unexpectedly?"
  - Tier 1: llms.txt → "Core concepts"
  - Tier 2: DETAILS.md → "Implementation patterns"
  - Tier 3: src/module.py → "Actual implementation code"

---

## Token Budget Guidelines

### Conservative Approach (Recommended)

**Always load:**
- Tier 1: ~1k tokens (llms.txt + README.md)

**Load as needed:**
- Tier 2: Add ~2-5k tokens per DETAILS.md or specialized guide
- Tier 3: Add ~5-10k tokens per source file

**Example budget:**
```
Tier 1: 1k tokens (base)
Tier 2:
  - DETAILS.md: +3k
Total so far: 4k tokens (2% of budget)

Tier 3 (if needed):
  - src/core.py: +5k
  - tests/test_core.py: +3k
Total: 12k tokens (6% of budget)

Still have 188k tokens available (94%)
```

### Aggressive Approach (When Confident)

If you know exactly what's needed:
- Skip Tier 1 if already in context
- Load Tier 2/3 directly
- Useful for follow-up questions in same session

**Example:**
```
User: "Now look at the test file"

AI Agent (already in context):
- Skip Tier 1 (already loaded)
- Skip Tier 2 (already loaded)
- Load Tier 3 directly: tests/test_module.py

Saves reloading 4k tokens
```

---

## Anti-Patterns to Avoid

### ❌ Loading Everything Upfront
```
AI Agent: "Let me load all documentation and source code..."
Result: 50k+ tokens wasted, nothing left for conversation
```

**Instead:**
```
AI Agent: "Load llms.txt first. User asked about API → answer from Tier 1."
Result: 500 tokens used, 199.5k available
```

---

### ❌ Re-loading Same Content
```
User: "What about function A?"
AI Agent: Loads DETAILS.md (3k tokens)

User: "And function B?"
AI Agent: Loads DETAILS.md again (3k tokens wasted)
```

**Instead:**
```
AI Agent: "Already have DETAILS.md in context, reference it directly."
Result: 0 additional tokens
```

---

### ❌ Loading Source Code for Documentation Questions
```
User: "What's the API for this library?"
AI Agent: Loads src/module.py (5k tokens)
```

**Instead:**
```
AI Agent: "Check Tier 1: llms.txt has API documentation."
Result: 500 tokens vs 5k tokens
```

---

## Best Practices

### 1. Start Minimal
Always load Tier 1 first. Don't assume you need deeper context.

### 2. Load Just-In-Time
Load Tier 2/3 only when needed for current question.

### 3. Reuse Context
If already loaded, reference it. Don't reload.

### 4. Prefer Documentation Over Code
Tier 2 (DETAILS.md) is more concise than Tier 3 (source code).

### 5. Ask Before Deep Diving
If unclear whether Tier 3 is needed, check Tier 2 first.

---

## Meta-Strategy: When to Use This Document

**Load CONTEXT_MANAGEMENT.md when:**
- Starting work in this repository for the first time
- Unsure what documentation to load
- Optimizing token usage
- Debugging "context too large" issues

**Don't load when:**
- Simple single-file questions
- Already know exactly what to load
- Following established workflow from Tier 1

---

## Summary

**Three Tiers:**
1. **Tier 1** (~1k tokens) - Always load, quick orientation (llms.txt, README.md)
2. **Tier 2** (~2-5k tokens) - Load for design/integration (DETAILS.md, guides)
3. **Tier 3** (~5-10k tokens) - Load for implementation/debugging (source code, tests)

**Decision Tree:**
- Quick question? → Tier 1 only
- Design question? → Tier 1 + 2
- Implementation? → Tier 1 + 2 + 3

**Best Practice:**
Start minimal, load just-in-time, reuse context, prefer docs over code.

---

**Last Updated:** 2025-11-10
**Maintained By:** Repository maintainers
