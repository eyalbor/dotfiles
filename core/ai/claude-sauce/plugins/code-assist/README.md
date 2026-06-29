# Code Assist Plugin

A comprehensive collection of tools for code assistance, including pull request reviews, code summaries, and detailed code analysis with structured, actionable feedback.

## Overview

This plugin provides powerful commands and skills for reviewing code changes, generating PR summaries, and performing comprehensive code analysis. It integrates with Git and GitHub to analyze branches, pull requests, and local changes.

## Prerequisites

Before using this plugin, ensure the following tools are installed and configured:

| Requirement | Purpose | Installation |
|-------------|---------|-------------|
| **Git** | Version control operations | Pre-installed on most systems |
| **GitHub CLI (`gh`)** | Required for reviewing or summarizing remote PRs by number | `brew install gh` (macOS) or [gh.io/installation](https://cli.github.com/manual/installation) |
| **pr-review-toolkit** | Specialized review agents for deep reviews | See links below |

### GitHub CLI Authentication

The GitHub CLI is **only required** when reviewing or summarizing a remote PR by providing its number (e.g., `/pr-assist-review-deep pr 123` or `/pr-assist-summary` with "PR by number" option). For local operations like reviewing committed, staged, or unstaged changes, the GitHub CLI is not needed.

After installing `gh`, authenticate with your GitHub account:
```bash
gh auth login
```

### pr-review-toolkit Plugin (Required for Deep Reviews)

The `/pr-assist-review-deep` command uses specialized agents from the **pr-review-toolkit** plugin.

Install from one of these sources:
- https://github.com/anthropics/claude-code/tree/main/plugins/pr-review-toolkit
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pr-review-toolkit

**Verification**: After installation, verify agents are available by checking the `/agents` list.

> **Note**: The quick review (`/pr-assist-review-quick`) and summary (`/pr-assist-summary`) commands work without the pr-review-toolkit plugin.

## Commands

### 1. pr-assist-review-deep
**Focus**: Comprehensive PR review with flexible scope selection

> **Dependency**: This command relies on the **pr-review-toolkit** plugin for specialized review agents.
> Install from:
> - https://github.com/anthropics/claude-code/tree/main/plugins/pr-review-toolkit
> - https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pr-review-toolkit

**Capabilities:**
- Review PRs, committed changes, staged/unstaged files
- Multi-agent parallel analysis
- Flexible scope and aspect selection

**Available Scopes:**
| Scope | Description |
|-------|-------------|
| `pr [number]` | Review a remote PR via GitHub CLI |
| `committed` | Review committed changes vs main/master |
| `staged` | Review only staged changes |
| `unstaged` | Review only working directory changes |
| `working` | Review all uncommitted changes |
| `all` | Review all changes (committed + uncommitted) |

**Available Review Aspects:**
| Aspect | Agent | Description |
|--------|-------|-------------|
| `all` | All agents | Runs ALL aspects below |
| `comments` | comment-analyzer | Verifies comment accuracy |
| `tests` | pr-test-analyzer | Reviews test coverage |
| `errors` | silent-failure-hunter | Finds silent failures |
| `types` | type-design-analyzer | Analyzes type design |
| `code` | code-reviewer | Checks guidelines, detects bugs |
| `simplify` | code-simplifier | Improves clarity |

**Usage:**
```
/pr-assist-review-deep pr 123
/pr-assist-review-deep committed tests errors
/pr-assist-review-deep staged code
```

---

### 2. pr-assist-review-quick
**Focus**: Detailed code reviews with structured feedback

**Analyzes:**
- ⚠️ **Bugs** — logic errors, incorrect conditions, edge cases
- 🔐 **Security** — unvalidated input, unsafe operations
- ⚡ **Performance** — unnecessary computations, N+1 queries
- 🧱 **Architecture** — unclear abstractions, tight coupling
- 🎨 **Style** — naming, documentation, consistency

**Review Priority:**
1. Correctness
2. Security
3. Performance
4. Architecture
5. Style

**Output Format:**
Each finding includes:
- Issue number and title
- Location (file path + line range)
- Category and Severity
- Description, Impact, and Suggestion

**When to use:**
- Quick validation before creating a PR
- Fast feedback on current branch
- Reviewing specific PRs without deep analysis

**Triggers:**
```
"Review my current branch"
"Check my PR"
"Review branch feature/auth"
"Look for issues in my code"
```

**Usage:**
```
/pr-assist-review-quick 123          # Review PR #123
/pr-assist-review-quick feature/auth # Review specific branch
/pr-assist-review-quick              # Review current branch
```

---

### 3. pr-assist-summary
**Focus**: Generate concise PR summaries for descriptions

**Capabilities:**
- Creates clear, actionable summaries of code changes
- Supports committed, unstaged, or PR-based changes
- Saves output to markdown files

**Summary Options:**
- **Committed changes**: Compare current branch vs main/master
- **Unstaged changes**: Summarize local uncommitted changes
- **PR by number**: Summarize a specific pull request

**Output Structure:**
- **Title**: One concise sentence capturing the change
- **Overview**: Primary purpose and intent
- **Key Changes**: Most important logic modifications
- **Testing**: Summary of test-related changes

**Usage:**
```
/pr-assist-summary
```
Then select the scope when prompted.

---

## Usage Patterns

### Quick Review Workflow

For fast feedback before committing:
```
/pr-assist-review-quick
```

### Comprehensive Review Workflow

For thorough PR analysis:
```
/pr-assist-review-deep all
```
Or with specific scope:
```
/pr-assist-review-deep pr 123 tests errors code
```

### PR Summary Generation

Before creating a PR:
```
/pr-assist-summary
```
Select "Committed changes" to generate a summary for your PR description.

### Natural Language Triggers

Simply ask questions to trigger the appropriate review:
```
"Review my code before I commit"
→ Triggers pr-assist-review-quick

"Check for security issues in auth.js"
→ Focused security review

"Summarize changes on this branch"
→ Triggers pr-assist-summary
```

---

## Output & Reporting

### Review Reports Include:

- **Issue Findings**: Categorized by Bug, Security, Performance, Style, Design
- **Severity Levels**: High, Medium, Low
- **Summary**: What was done well, key issues, recommendation
- **Token Usage**: Detailed breakdown of tokens and estimated costs
- **Metadata**: Timestamp, scope, agents used, execution time

### Saved Files:

Reviews and summaries are automatically saved:
- **PR Reviews**: `PR-<number>-code-review.md`
- **Branch Reviews**: `<branch-name>-code-review.md`
- **PR Summaries**: `PR-<number>-pr-summary.md` or `<branch-name>-pr-summary.md`

---

## Best Practices

### When to Use Each Command

| Scenario                | Command |
|-------------------------|---------|
| Quick review            | `/pr-assist-review-quick` |
| Thorough PR review      | `/pr-assist-review-deep all` |
| Review specific aspects | `/pr-assist-review-deep committed tests errors` |
| Generate PR description | `/pr-assist-summary` |
| Review remote PR        | `/pr-assist-review-deep pr 123` |

### Recommended Workflow

**Before Committing:**
```
1. Write code
2. Run: /pr-assist-review-quick
3. Fix critical issues
4. Commit
```

**Before Creating PR:**
```
1. Stage all changes
2. Run: /pr-assist-review-deep committed all
3. Address critical and important issues
4. Run: /pr-assist-summary
5. Create PR with generated summary
```

**After PR Feedback:**
```
1. Make requested changes
2. Run targeted reviews based on feedback
3. Verify issues are resolved
4. Push updates
```

---

## Tips

- **Run early**: Review before creating PRs, not after
- **Focus on changes**: Reviews analyze git diff by default
- **Address critical first**: Fix high-priority issues before lower priority
- **Re-run after fixes**: Verify issues are resolved
- **Use specific aspects**: Target specific reviews when you know the concern
- **Parallel execution**: Use `all parallel` for faster comprehensive reviews

---

## Troubleshooting

### Review Not Finding Changes

**Issue**: Review returns no findings

**Solution**:
- Ensure changes are committed or staged as expected
- Check you're on the correct branch
- Verify the comparison base (main/master)

### GitHub CLI Required

**Issue**: PR review fails

**Solution**:
- Install GitHub CLI: `brew install gh`
- Authenticate: `gh auth login`
- Ensure you have access to the repository

### Large Diffs

**Issue**: Review takes too long or times out

**Solution**:
- Use specific aspects instead of `all`
- Review in smaller batches
- Focus on critical files first

---

## Plugin Details

**Name**: code-assist
**Version**: 2.0.0
**Author**: <AUTHOR_NAME> (<AUTHOR_EMAIL>)

---

## License

MIT

---

**Quick Start**: Run `/pr-assist-review-quick` for instant feedback on your code!
