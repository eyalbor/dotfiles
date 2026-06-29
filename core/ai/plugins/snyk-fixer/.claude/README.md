# Claude/Cursor Compatibility Setup

This directory contains skills, agents, and rules that work with both **Claude AI** and **Cursor IDE**.

## Directory Structure

- `.claude/` - Primary directory (works with both Claude and Cursor)

## Compatibility

Both **Claude** and **Cursor** read from `.claude/` directories:
- **Skills**: `.claude/skills/`
- **Rules**: `.claude/rules/`
- **Agents**: `.claude/agents/` (Cursor-specific, but stored here for compatibility)

Cursor IDE automatically loads from `.claude/` directories for compatibility with Claude.

## Path References

All files reference `.claude/` paths. Both Cursor and Claude will resolve them correctly.
