---
name: prompt-boost
description: Enhance basic prompts into production-grade optimized prompts using comprehensive prompt engineering methodology. Use when user asks to enhance, improve, optimize, or boost a prompt.
---

# Prompt Boost

Transform basic prompts into production-grade, optimized prompts.

## When to Use

Trigger when user:
- Asks to "enhance", "improve", "optimize", or "boost" a prompt
- Mentions "prompt engineering" or wants better prompting
- Wants to transform a simple instruction into a comprehensive prompt

## Process

1. **Ask which mode** using AskUserQuestion:
   - **Light Mode** (~200-400 tokens): Quick enhancement with core sections
   - **Advance Mode** (~500-1000 tokens): Comprehensive production-grade enhancement

2. **Read methodology**:
   - Light → [METHODOLOGY-LIGHT.md](METHODOLOGY-LIGHT.md)
   - Advance → [METHODOLOGY.md](METHODOLOGY.md)

3. **Apply methodology** and return enhanced prompt (no prefixes or meta-commentary)

## Enhancement Modes

**Light Mode** (~200-400 tokens):
- Role & task (1-2 sentences)
- Context sections (XML tags)
- Instructions (3-7 steps)
- 1+ examples
- Hallucination prevention (4 rules)
- Critical repetition (2-3 reminders)

**Advance Mode** (~500-1000 tokens):
All Light features plus:
- Constraints & boundaries
- Output format specs
- 2+ examples with edge cases
- Reasoning patterns
- Validation checklist
- Token optimization

## See Also

- **[EXAMPLES.md](EXAMPLES.md)**: Before/after examples demonstrating enhancements
