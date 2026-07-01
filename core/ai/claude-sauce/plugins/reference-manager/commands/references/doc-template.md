# Reference Documentation Template

When generating new docs, adapt this template to match the existing project style. Include sections relevant to your documentation type - not all sections are required.

```markdown
# {Feature/Flow Name}

{Brief description of what this feature/flow does.}

## Overview

{High-level explanation - what problem does this solve?}

<!-- For flow documentation, include: -->
**Entry Point**: `{file}:{function}`
**Trigger**: {What initiates this flow - API call, event, scheduled job, etc.}

### Key Capabilities

- **Capability 1**: Description
- **Capability 2**: Description

## Architecture / Flow Diagram

{Explain the design pattern or execution path, with ASCII diagram}

```
{entry_point}
├── {step_1}
│   ├── {sub_step_1a}
│   └── {sub_step_1b}
├── {step_2}
└── {step_3}
```

## Components

### {Component 1}

**File**: `path/to/file.py`
**Responsibility**: {What this component does}

Key logic:
- {Important business rule or decision}
- {Edge case handling}

## Data Flow

| Stage | Input | Output | Transformation |
|-------|-------|--------|----------------|
| Entry | {input} | {output} | {what happens} |

## External Dependencies

- **{Service/DB}**: {How it's used, what data is exchanged}

## Error Handling

| Error Scenario | Handling | User Impact |
|----------------|----------|-------------|
| {scenario} | {how handled} | {what user sees} |

## Configuration

| Setting | Default | Effect |
|---------|---------|--------|
| {config} | {value} | {what it controls} |

## Usage

{How to use this feature, with code examples}

## Related Documentation

- [Related Doc](./RELATED.md)
```

## Style Guidelines

- Match the tone and format of existing docs in the project
- Use ASCII diagrams for architecture when helpful
- Include code examples where applicable
- Link to related documentation
- Keep sections focused and scannable
- Only include sections relevant to your documentation type
