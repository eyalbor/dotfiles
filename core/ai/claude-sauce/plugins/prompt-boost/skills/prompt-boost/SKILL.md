---
name: prompt-boost
description: Enhance basic prompts into production-grade optimized prompts using comprehensive prompt engineering methodology. Use when user asks to enhance, improve, optimize, or boost a prompt.
---

# Prompt Boost

Transform basic prompts into production-grade, optimized prompts.

## Trigger

Use when user asks to: "enhance", "improve", "optimize", or "boost" a prompt, or mentions "prompt engineering".

## Process

1. **Ask which mode** (use AskUserQuestion):
   - **Light Mode** (~200-400 tokens): Quick enhancement with core sections
   - **Advance Mode** (~500-1000 tokens): Comprehensive production-grade enhancement

2. **Read methodology**:
   - Light → [METHODOLOGY-LIGHT.md](METHODOLOGY-LIGHT.md)
   - Advance → [METHODOLOGY.md](METHODOLOGY.md)

3. **Apply methodology** and return enhanced prompt (no prefixes or meta-commentary)

## Enhancement Modes

**Light Mode**: Role & task, context sections (XML), 3-7 instructions, 1+ examples, hallucination prevention (4 rules), critical repetition (2-3 reminders)

**Advance Mode**: All Light features + constraints & boundaries, output format specs, 2+ examples with edge cases, reasoning patterns, validation checklist, token optimization

See [EXAMPLES.md](EXAMPLES.md) for before/after demonstrations.
