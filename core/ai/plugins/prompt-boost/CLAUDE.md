# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multi-platform prompt enhancement tool that transforms basic prompts into production-grade optimized prompts. Available as:
- **Cursor Slash Command**: `/prompt-boost` in Cursor IDE
- **Claude Code Skill**: Agent skill in `.claude/skills/prompt-boost/`

Built with a comprehensive methodology based on prompt engineering best practices.

## Commands

### Methodology Management

```bash
npm run methodology:validate  # Validate methodology has all required sections
npm run methodology:generate  # Generate markdown docs from TypeScript source
```

## Architecture

### Core Enhancement Logic

The enhancement logic uses a **consolidated methodology module** as the single source of truth:

**Methodology Module** (`src/methodology/`):
- **Single Source of Truth**: All enhancement rules live in TypeScript
- `advance.ts` - Advance mode system instructions (~500-1000 tokens)
- `light.ts` - Light mode system instructions (~200-400 tokens)
- `types.ts` - TypeScript interfaces for methodology modes
- `validator.ts` - Validation utilities for methodology quality
- `index.ts` - Main exports

**Integration Points**:
1. **Auto-Generated Documentation**:
   - `.claude/skills/prompt-boost/METHODOLOGY.md` (generated from advance.ts)
   - `.claude/skills/prompt-boost/METHODOLOGY-LIGHT.md` (generated from light.ts)
   - `.cursor/commands/prompt-boost-advanced.md` (generated from advance.ts)
   - `.cursor/commands/prompt-boost-lite.md` (generated from light.ts)

**Benefits**:
- Zero duplication: methodology exists in one place only
- Type-safe: TypeScript compilation catches errors
- Auto-generation: documentation stays synchronized automatically
- Testable: validation ensures quality standards are met

### Cursor Integration

```
.cursor/
├── commands/
│   ├── prompt-boost-advanced.md  # Full methodology for Cursor slash command
│   └── prompt-boost-lite.md      # Light methodology (if exists)
└── prompts/                      # User can save enhanced prompts here
```

Slash commands in `.cursor/commands/*.md` are loaded by Cursor automatically. The command file contains the full methodology that Cursor applies when users type `/prompt-boost`.

### Claude Code Skill Structure

```
.claude/skills/prompt-boost/
├── SKILL.md                     # Skill entry point: when/how to use, quick start
├── METHODOLOGY.md               # Advance mode: comprehensive enhancement rules
├── METHODOLOGY-LIGHT.md         # Light mode: streamlined enhancement rules
└── EXAMPLES.md                  # Before/after examples
```

**Progressive Disclosure**: Claude Code loads files progressively based on what's needed (metadata → instructions → methodology → examples → scripts).

### TypeScript Configuration

- **`tsconfig.json`**: Main config (noEmit: true, targets ES2022, moduleResolution: bundler)

## Enhancement Methodology

### Two Modes

**Light Mode** (~200-400 tokens):
1. Role & Task (1-2 sentences)
2. Context sections with XML tags
3. Detailed instructions (3-7 steps)
4. 1+ concrete examples
5. Basic hallucination prevention (4 rules)
6. Critical repetition (2-3 reminders)

**Advance Mode** (~500-1000 tokens):
- All Light mode features plus:
- Constraints & boundaries, output format specification
- 2+ examples with edge cases
- Reasoning patterns, multi-step scaffolding
- Comprehensive validation checklist
- Token optimization, formatting standards

### Key Enhancement Principles

1. **Structural Foundation**: Role assignment, context sections (XML tags), detailed instructions, constraints, output format
2. **Content Requirements**: 2+ concrete examples, reasoning patterns, multi-step scaffolding
3. **Quality Assurance**: Hallucination prevention (uncertainty expression, source attribution, confidence scoring), validation rules
4. **Optimization**: Token efficiency, clarity principles, instruction prioritization
5. **Formatting Standards**: XML tag conventions, section delimiters, code block formatting
6. **Critical Repetition**: 3-5 most important instructions repeated at end

See `METHODOLOGY.md` for complete details.

## Development Workflow

### Making Enhancement Methodology Changes

**New Workflow (Single Source of Truth)**:

1. Edit the TypeScript source:
   ```bash
   # For Advance mode
   code src/methodology/advance.ts

   # For Light mode
   code src/methodology/light.ts
   ```

2. Validate the changes:
   ```bash
   npm run methodology:validate
   ```

3. Generate documentation for all integrations:
   ```bash
   npm run methodology:generate
   ```
   This auto-generates:
   - `.claude/skills/prompt-boost/METHODOLOGY.md`
   - `.claude/skills/prompt-boost/METHODOLOGY-LIGHT.md`
   - `.cursor/commands/prompt-boost-advanced.md`
   - `.cursor/commands/prompt-boost-lite.md`

4. Test integrations:
   ```bash
   # Test Claude Code skill
   # (manually trigger in Claude Code session)

   # Test Cursor command
   # (use /prompt-boost in Cursor)
   ```

5. Commit changes:
   ```bash
   git add .
   git commit -m "Update enhancement methodology: [description]"
   ```

**Old Workflow (DEPRECATED)**:
- DO NOT manually edit METHODOLOGY.md files - they are auto-generated
- DO NOT manually edit .cursor/commands/*.md files - they are auto-generated

## Key Constraints

- **Methodology is auto-generated**: Never manually edit METHODOLOGY.md or Cursor command files - edit src/methodology/*.ts instead
- **Single source of truth**: All methodology changes must go through src/methodology/ TypeScript files
- **Validation required**: Run `npm run methodology:validate` before generating docs
- **Build before commit**: Run `npm run methodology:generate` to update all integrations
- Node.js version requirement: >=22.13.0 for development