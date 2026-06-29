---
description: "Comprehensive PR review review using specialized agents with flexible scope selection"
argument-hint: "[scope] [review-aspects]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Comprehensive Review with Flexible Scope

Run a comprehensive code review using multiple specialized agents, with flexible scope selection for what changes to review.

**Arguments (optional):** "$ARGUMENTS"

## Review Workflow:

1. **Select Review Scope**

   Parse the first argument to determine what changes to review:

   **Available Scopes:**
   - **pr [number]** - Review a remote PR (uses GitHub CLI)
   - **committed** - Review committed changes on current branch vs main/master
   - **staged** - Review only staged changes (git add)
   - **unstaged** - Review only unstaged working directory changes
   - **working** - Review all uncommitted changes (staged + unstaged)
   - **all** - Review all changes (committed + uncommitted) on current branch

   **If no scope provided:** Prompt the user to select from the available scopes.

   **If `pr` without number:** Prompt the user for the PR number.

2. **Identify Changed Files by Scope**

   Based on selected scope, run the appropriate git command:

   | Scope | Command |
   |-------|---------|
   | `pr <number>` | `gh pr diff <number> --name-only` |
   | `committed` | `git diff --name-only main...HEAD` (fallback: `master...HEAD`) |
   | `staged` | `git diff --staged --name-only` |
   | `unstaged` | `git diff --name-only` |
   | `working` | `git diff --name-only HEAD` |
   | `all` | `git diff --name-only main...HEAD` + `git diff --name-only HEAD` (combined, deduplicated) |

   Store the list of changed files for review.

3. **Select Review Aspects**

   **If review aspects provided in arguments:** Use the specified aspects.

   **If no review aspects provided:** Prompt the user with a multi-select checklist. First, analyze the changed files to determine recommendations, then display:

   **Available Aspects:**
   | Aspect | Agent | Description |
   |--------|-------|-------------|
   | **`all`** | **(all agents)** | **Runs ALL aspects below** |
   | `comments` | comment-analyzer | Verifies comment accuracy, identifies rot |
   | `tests` | pr-test-analyzer | Reviews test coverage and quality |
   | `errors` | silent-failure-hunter | Finds silent failures, reviews catch blocks |
   | `types` | type-design-analyzer | Analyzes type encapsulation and invariants |
   | `code` | code-reviewer | Checks guidelines compliance, detects bugs |
   | `simplify` | code-simplifier | Simplifies code, improves clarity |

   Display a multi-select checklist showing aspects with ⭐ recommendations based on:
   - **code** - Always recommended
   - **tests** - If `test_*.py`, `*_test.py`, or `tests/` files changed
   - **comments** - If `.md`, `.rst`, or docstring-heavy files changed
   - **errors** - If exception handling patterns detected in diff
   - **types** - If new classes, TypedDict, or type aliases added
   - **simplify** - For large diffs or complex logic changes

   **Default:** If user presses Enter without selection, run `all` applicable aspects.

4. **Determine Applicable Reviews**

   User-selected aspects take precedence. If `all` selected, apply all agents relevant to changed files.

5. **Verify Agent Availability**

   Before launching reviews, verify that all required agents for the selected aspects are installed.

   **Aspect to Agent Mapping:**
   | Aspect | Required Agent |
   |--------|----------------|
   | `comments` | `comment-analyzer` |
   | `tests` | `pr-test-analyzer` |
   | `errors` | `silent-failure-hunter` |
   | `types` | `type-design-analyzer` |
   | `code` | `code-reviewer` |
   | `simplify` | `code-simplifier` |

   **Verification:** Check if each required agent is available in the `/agents` list.

   **If any agents are missing, STOP the review immediately and display:**
   ```
   ❌ Required agent(s) not found: [list-all-missing-agents]

   The pr-review-toolkit plugin is required for deep reviews.

   Install from one of these sources:
   • https://github.com/anthropics/claude-code/tree/main/plugins/pr-review-toolkit
   • https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pr-review-toolkit

   After installation, verify agents are available by checking the /agents list.
   ```

   **Do not proceed with the review until all required agents are installed.**

6. **Launch Review Agents**

   Launch all selected review agents **in parallel**:
   - All agents run simultaneously for faster reviews
   - Results are collected and aggregated when all complete
   - Each agent focuses on its specialty for deep analysis

7. **Aggregate Results**

   After agents complete, summarize:
   - **Critical Issues** (must fix before merge)
   - **Important Issues** (should fix)
   - **Suggestions** (nice to have)
   - **Positive Observations** (what's good)

8. **Provide Action Plan**

   Organize findings:
   ```markdown
   # Review Summary

   ## Critical Issues (X found)
   - [agent-name]: Issue description [file:line]

   ## Important Issues (X found)
   - [agent-name]: Issue description [file:line]

   ## Suggestions (X found)
   - [agent-name]: Suggestion [file:line]

   ## Strengths
   - What's well-done in this change

   ## Recommended Action
   1. Fix critical issues first
   2. Address important issues
   3. Consider suggestions
   4. Re-run review after fixes
   ```

9. **Token Usage Summary**

   After the review completes, display a summary of tokens consumed and estimated cost.

   **If per-agent token breakdown is available**, show detailed breakdown:
   ```markdown
   ## 📊 Token Usage Summary

   | Component | Input Tokens | Output Tokens | Total | Est. Cost |
   |-----------|-------------|---------------|-------|-----------|
   | code-reviewer | 12,450 | 2,340 | 14,790 | $0.21 |
   | pr-test-analyzer | 8,200 | 1,560 | 9,760 | $0.14 |
   | comment-analyzer | 5,120 | 890 | 6,010 | $0.08 |
   | silent-failure-hunter | 6,780 | 1,230 | 8,010 | $0.11 |
   | type-design-analyzer | 4,500 | 780 | 5,280 | $0.07 |
   | code-simplifier | 9,300 | 2,100 | 11,400 | $0.17 |
   | **Orchestration** | 3,200 | 450 | 3,650 | $0.05 |
   | **Total** | **49,550** | **9,350** | **58,900** | **$0.83** |
   ```

   **If per-agent breakdown is NOT available**, show overall totals only:
   ```markdown
   ## 📊 Token Usage Summary

   | Metric | Value |
   |--------|-------|
   | Input Tokens | ~49,550 |
   | Output Tokens | ~9,350 |
   | **Total Tokens** | **~58,900** |
   | **Estimated Cost** | **~$0.83** |

   *Note: Per-agent breakdown not available. Total based on main context usage.*
   ```

   **Model Pricing Reference (per 1M tokens):**

   | Model | Input | Output |
   |-------|-------|--------|
   | Claude Opus 4.5 | $15.00 | $75.00 |
   | Claude Sonnet 4.5 | $3.00 | $15.00 |
   | Claude Haiku 4.5 | $1.00 | $5.00 |

   💰 *Costs depend on active model. See pricing table above.*

   ⏱️ **Total Review Time:** 47s

   **Tracking includes (when available):**
   - **Subagent tokens**: Input/output tokens for each review agent
   - **Orchestration tokens**: Tokens used by the main review coordinator
   - **Cost estimates**: Based on the model's current pricing rates
   - **Total time**: Wall-clock time from review start to completion

10. **Save Review Results**

    **Always save the review to a markdown file.** After completing the code review:

    **File naming convention:**
    - For PRs: `PR-<number>-code-review.md` (e.g., `PR-123-code-review.md`)
    - For branches: `<branch-name>-code-review.md` (e.g., `feature-auth-code-review.md`)
    - For working/staged/unstaged: `code-review-<date>.md` (e.g., `code-review-2026-01-30.md`)

    **Saved file contents:**
    ```markdown
    # Code Review: [PR #123 | branch-name | Working Changes]

    **Date:** 2026-01-30
    **Scope:** [pr | committed | staged | unstaged | working]
    **Files Changed:** 12
    **Aspects Reviewed:** code, tests, errors, types

    ---

    ## Critical Issues (X found)
    ...

    ## Important Issues (X found)
    ...

    ## Suggestions (X found)
    ...

    ## Strengths
    ...

    ## Recommended Action
    ...

    ---

    ## 📊 Token Usage Summary
    *(Same format as displayed - see Token Usage Summary section above)*

    ---

    ## Review Metadata

    **Generated:** 2026-01-30 14:15:00 (local time)
    **Review Type:** Comprehensive Multi-Agent Parallel Review
    **Scope:** All committed changes on feature-auth branch vs main
    **Agents / Tools Used:** 5 specialized review agents
    **Token Usage:** ~58,900 tokens (29% of context window)
    **Estimated Cost:** ~$0.83 (Claude Sonnet 4.5)
    **Execution Time:** ~47s
    ```

    **Always save the review to an .md file and inform the user:**
    ```
    ✅ Saved the code review to `PR-123-code-review.md` in the project root.
    📄 You can share this file with the PR author or reference it later.
    ```

## Usage Examples:

**Interactive mode (prompts for scope and aspects):**
```
/pr-assist-review-deep
# 1. Prompts to select scope (pr, committed, staged, unstaged, working, all)
# 2. Identifies changed files
# 3. Shows multi-select checklist with recommended aspects highlighted
# 4. Runs selected reviews in parallel
# 5. Saves review to file and displays path
```

**Remote PR review:**
```
/pr-assist-review-deep pr 123
# Reviews PR #123, prompts for aspects with recommendations
# Saves to PR-123-code-review.md

/pr-assist-review-deep pr
# Prompts for PR number, then prompts for aspects

/pr-assist-review-deep pr 456 tests errors
# Reviews PR #456, focusing on tests and error handling (no aspect prompt)
```

**Committed changes (branch vs main):**
```
/pr-assist-review-deep committed
# Reviews all commits on current branch, prompts for aspects

/pr-assist-review-deep committed tests
# Reviews committed changes, focusing only on tests
```

**All changes (committed + uncommitted):**
```
/pr-assist-review-deep all
# Reviews both committed and uncommitted changes together

/pr-assist-review-deep all code tests
# Reviews all changes, focusing on code quality and tests
```

**Uncommitted changes:**
```
/pr-assist-review-deep staged
# Reviews only staged changes, prompts for aspects

/pr-assist-review-deep unstaged
# Reviews only unstaged changes, prompts for aspects

/pr-assist-review-deep working
# Reviews all uncommitted changes, prompts for aspects

/pr-assist-review-deep working code errors
# Reviews working changes, focusing on code quality and error handling
```

**Skip aspect prompt (specify aspects directly):**
```
/pr-assist-review-deep committed all
# Reviews committed changes with all applicable agents (no prompt)

/pr-assist-review-deep pr 123 code tests simplify
# Reviews PR #123 with specific aspects only
```

## Tips:

- **Choose the right scope**: Use `staged` to review before committing, `committed` before creating PR, `all` for complete branch review, `pr` for existing PRs
- **Trust the recommendations**: The ⭐ recommended aspects are based on actual file changes detected
- **Press Enter for comprehensive review**: When unsure, accept the default `all` to run all applicable agents
- **Specify aspects to skip prompt**: Add aspects as arguments (e.g., `committed code tests`) to skip the interactive selection
- **Run early**: Review before creating PR, not after
- **Focus on changes**: Agents analyze the diff from selected scope
- **Address critical first**: Fix high-priority issues before lower priority
- **Re-run after fixes**: Verify issues are resolved

## Workflow Integration:

**Before committing:**
```
1. Write code
2. Stage changes: git add <files>
3. Run: /pr-assist-review-deep staged
4. Select aspects from checklist (or press Enter for all)
5. Fix any critical issues
6. Commit
```

**Before creating PR:**
```
1. Commit all changes
2. Run: /pr-assist-review-deep committed
3. Review recommended aspects, select what to include
4. Address all critical and important issues
5. Run specific reviews again to verify
6. Create PR
```

**Review existing PR:**
```
1. Run: /pr-assist-review-deep pr <number>
2. Select aspects (recommendations based on PR changes)
3. Address findings
4. Push updates
5. Re-run to verify
```

**Quick review with specific aspects:**
```
1. Make changes
2. Run: /pr-assist-review-deep working code errors
3. Fix issues (skips aspect prompt since aspects specified)
4. Stage and commit
```

## Notes:

- Agents always run in parallel for faster reviews
- Each agent focuses on its specialty for deep analysis
- Results are actionable with specific file:line references
- Agents use appropriate models for their complexity
- All agents available in `/agents` list
- PR scope requires GitHub CLI (`gh`) to be installed and authenticated
- For `committed` scope, falls back to `master` if `main` branch doesn't exist
- Aspect recommendations are based on file patterns and diff content analysis
- Specifying aspects in arguments skips the interactive selection prompt
