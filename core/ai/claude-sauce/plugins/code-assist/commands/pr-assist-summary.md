---
description: Generate a concise summary of pull request changes for PR descriptions
argument-hint: "[scope]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Write", "AskUserQuestion"]
---

# PR Summary Generator

Generate a clear, actionable summary of code changes for use in pull request descriptions.

## Context

- Current branch: !`git branch --show-current`
- Base branch: !`git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "master"`

## Usage Workflow

When invoked, **always ask the user first** what changes to summarize using the AskUserQuestion tool with these options:

1. **Committed changes** (default/first option): Summarize committed changes on current branch compared to main/master
2. **Unstaged changes**: Summarize uncommitted local changes (staged + unstaged)
3. **PR by number**: Summarize a specific pull request by number (ask for PR number after selection)

### Initial Question

Always start by asking the user using the AskUserQuestion tool:

```
Question: "What changes would you like me to summarize?"
Header: "Summary scope"
Options:
  1. "Committed changes" - "Summarize committed changes on current branch vs main/master"
  2. "Unstaged changes" - "Summarize uncommitted local changes (staged + unstaged)"
  3. "PR by number" - "Summarize a specific pull request (will ask for PR number)"
```

If user selects "PR by number", follow up by asking for the PR number.

### Getting Changes Based on Selection

Based on the user's selection:
- **Committed changes**: Run `git diff main...HEAD` or `git diff master...HEAD` to get committed changes on current branch
- **Unstaged changes**: Run `git diff HEAD` to get all uncommitted changes
- **PR by number**: Use `gh pr view <number>` and `gh pr diff <number>` to fetch PR details

## Your Task

Analyze the code changes and create a concise PR summary following this methodology:

### Analysis Process

1. **Get Full Diff**: Run the appropriate git diff command based on user selection
2. **First Pass - Understand Scope**: Scan all changed files to understand the breadth of changes
3. **Second Pass - Deep Dive**: Examine the most significant files in detail
4. **Third Pass - Context**: Understand how changes interact across files and components
5. **Synthesis**: Distill findings into a clear narrative

### Summary Structure

Create a hierarchical summary with:

- **Title**: One concise sentence capturing the overall change
- **Overview (1-2 sentences)**: The primary purpose and intent of the changes
- **Key Changes**: Bullet points focusing on the most important logic modifications (1-2 sentences each)
- **Testing**: Summary of test-related changes to validate the implementation

### Focus Areas

Prioritize these types of changes:
- New functionality and features
- Modified business logic and algorithms
- Architectural or structural changes
- Bug fixes and their root causes
- Performance optimizations
- Security improvements
- Dependency updates
- Configuration changes

### Quality Requirements

- Keep all lines to a maximum of 120 characters
- Focus on the "what" and "why" rather than just the "where"
- Ensure someone unfamiliar with the changes could understand the summary
- Maximum 30 lines of output
- Do not repeat yourself or list all modified files

### Output

1. **Console**: Display the complete summary in the terminal (in markdown format)
2. **File**: Save as a markdown file (`.md`) with naming based on the selection:
   - For PRs: `PR-<number>-pr-summary.md` (e.g., `PR-123-pr-summary.md`)
   - For branches (committed changes): `<branch-name>-pr-summary.md` (e.g., `feature-auth-pr-summary.md`)
   - For unstaged changes: `pr-summary-<date>.md` (e.g., `pr-summary-2026-01-30.md`)

After generating, tell the user which file was created.
