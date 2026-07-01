---
description: Moderately-comprehensive and quick code review with actionable feedback
argument-hint: "[PR number or branch name]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Write", "AskUserQuestion"]
---

# Quick Code Review for PR or Branch

Perform moderately-comprehensive and quick code reviews with structured, actionable feedback on code changes in Git branches or pull requests.

## Review Workflow

1. **Understand the change**
   - Read diffs or files from the target branch
   - Identify the purpose of changes (features, refactors, fixes)
   - Assess whether implementation matches intent

2. **Detect potential issues across categories**
   - ⚠️ **Bugs** — logic errors, incorrect conditions, missing edge cases, wrong data types
   - 🔐 **Security** — unvalidated input, unsafe operations, sensitive data exposure
   - ⚡ **Performance** — unnecessary computations, poor data structures, N+1 queries
   - 🧱 **Architecture/Design** — unclear abstractions, tight coupling, missing modularity
   - 🎨 **Style/Readability** — naming, indentation, documentation, consistency

3. **Provide actionable suggestions**
   - Include **why** something is an issue
   - Explain **how** to fix it
   - Suggest clear, realistic improvements

## Review Criteria

Focus on issues in this priority order:

1. **Correctness** — Does the code do what it's supposed to do?
2. **Security** — Are there vulnerabilities or risks?
3. **Performance** — Will this scale or cause bottlenecks?
4. **Architecture** — Is the design sound and maintainable?
5. **Style** — Is the code readable and consistent?

## Output Format

For each finding, use this exact structure:

```
## Issue #<number>: <short title>
**Location:** <file path + line range>
**Category:** Bug | Security | Performance | Style | Design
**Severity:** High | Medium | Low

**Description:**
<Explain the issue clearly and concisely.>

**Impact:**
<Describe the risk or consequence if not fixed.>

**Suggestion:**
<Explain or show how to fix or improve the code.>
```

After listing all issues, provide a **summary**:

```
## Summary
✅ What was done well
⚠️ Key issues found
🛠️ Overall recommendation: (Approve | Request changes | Needs minor edits)
```

After the summary, include a **token usage breakdown**:

```
## 📊 Token Usage Summary

| Component | Input Tokens | Output Tokens | Total | Est. Cost |
|-----------|-------------|---------------|-------|-----------|
| pr-assist-review-quick | 15,200 | 3,450 | 18,650 | $0.26 |
| **Total** | **15,200** | **3,450** | **18,650** | **$0.26** |

### Tool Calls
| Tool | Invocations | Avg Tokens/Call |
|------|-------------|-----------------|
| read_file | 18 | 1,650 |
| grep_search | 8 | 280 |
| git diff | 3 | 2,100 |

### Model Pricing Reference (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| Claude Opus 4.5 | $15.00 | $75.00 |
| Claude Sonnet 4.5 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $1.00 | $5.00 |

💰 *Costs depend on active model. See pricing table above.*

⏱️ **Total Review Time:** 32s
```

After the token usage, include a **metadata section**:

```
---

## Review Metadata

**Generated:** 2026-01-30 14:15:00 (local time)
**Review Type:** Quick Code Review
**Scope:** All committed changes on feature-auth branch vs main
**Tools Used:** Grep, Read, git diff
**Token Usage:** ~18,650 tokens
**Estimated Cost:** ~$0.26 (Claude Sonnet 4.5)
**Execution Time:** ~32s
```

## Review Style

- Be **concise**, **specific**, and **professional**
- Use neutral tone — never judgmental or overly formal
- Avoid over-explaining basic syntax; assume experienced developers
- Focus first on correctness and security before minor style issues

## Usage Workflow

When invoked to review code:

1. **Ask the user** what to review using AskUserQuestion:
   ```
   Question: "What would you like me to review?"
   Header: "Review type"
   Options:
     1. "Committed changes" - "Review committed changes on current branch vs main/master"
     2. "All changes" - "Review all changes (committed + uncommitted) on current branch"
     3. "PR by number" - "Review a specific pull request (will ask for PR number)"
     4. "Specific file(s)" - "Review specific files (will ask for file paths)"
   ```
   - If "PR by number" selected, follow up asking for PR number
   - If "Specific file(s)" selected, follow up asking for file paths

2. **Fetch changes** based on selection:
   - **Committed changes**: `git diff main...HEAD` (fallback: `master...HEAD`)
   - **All changes**: Combine `git diff main...HEAD` + `git diff HEAD` (deduplicated)
   - **PR review**: `gh pr view <number>` and `gh pr diff <number>`
   - **Specific file(s)**: Read files directly

3. Analyze code against review criteria
4. Generate structured output with all findings
5. Provide summary with recommendation
6. **Save the review** to a markdown file and inform the user

## Saving Reviews

**Always save the review to a markdown file.** After completing the code review:

1. **Save the review** to a markdown file in the project root:
   - For PRs: `PR-<number>-code-review.md` (e.g., `PR-123-code-review.md`)
   - For branches: `<branch-name>-code-review.md` (e.g., `feature-auth-code-review.md`)
   - For files: `code-review-<date>.md` (e.g., `code-review-2026-01-30.md`)

2. **Inform the user** after displaying the review:
   ```
   ✅ Saved the code review to `<filename>` in the project root.
   📄 You can share this file with the PR author or reference it later.
   ```

## Examples

Review a specific PR:
```
/pr-assist-review-quick 123
```

Review a specific branch:
```
/pr-assist-review-quick feature/user-authentication
```

Review current branch:
```
/pr-assist-review-quick
```

**Focused review:**
```
User: "Check for security issues in auth.js"
→ Focus analysis on security category only
→ Review specified file
→ Generate findings for security concerns
```

## Best Practices

- Provide full diff or contextual files for accurate review
- Review smaller, focused commits for precision
- For large PRs, consider reviewing by module or commit
- Always explain the reasoning behind each finding
- Review findings should be validated before making changes
- Critical security issues should be addressed immediately
