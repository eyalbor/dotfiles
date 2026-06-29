---
name: github-enterprise
description: |
  GitHub Enterprise integration for <GITHUB_HOST> ONLY. Use this skill ONLY when the user explicitly mentions "<GITHUB_HOST>" or "enterprise github". Do NOT use for general GitHub questions or github.com. If the user asks about GitHub without specifying which instance, ASK them: "Are you asking about <GITHUB_HOST> (enterprise) or github.com?"
---

# GitHub Enterprise Integration

Interact with GitHub Enterprise at `<GITHUB_HOST>` using the `gh` CLI.

## Important: When to Use

- **USE** when: `<GITHUB_HOST>`, `enterprise github`
- **ASK** if user says "GitHub" without specifying which instance
- **DO NOT USE** for general GitHub (github.com)

## Setup

Install: `brew install gh` (macOS) or see https://cli.github.com/

Authenticate:
```bash
gh auth login --hostname <GITHUB_HOST>
```

All commands use `-h <GITHUB_HOST>` (or `--hostname <GITHUB_HOST>`).

## Commands

```bash
# Search repos
gh search repos "query" -h <GITHUB_HOST> [--language python] [--owner ORG]

# Search code
gh search code "pattern" -h <GITHUB_HOST> [--repo owner/repo] [--language python]

# Fetch file contents
gh api repos/{owner}/{repo}/contents/{path} -h <GITHUB_HOST> --jq '.content' | base64 -d
gh api "repos/{owner}/{repo}/contents/{path}?ref={branch}" -h <GITHUB_HOST> --jq '.content' | base64 -d

# List PRs
gh pr list -R owner/repo -h <GITHUB_HOST> [--state open] [--author username]
gh pr view 123 -R owner/repo -h <GITHUB_HOST> [--comments]

# List issues
gh issue list -R owner/repo -h <GITHUB_HOST> [--state open] [--label "bug"]

# Repo info
gh repo view owner/repo -h <GITHUB_HOST> [--json name,description,defaultBranch]

# Commits
gh api repos/{owner}/{repo}/commits -h <GITHUB_HOST> --jq '.[].sha'
gh api repos/{owner}/{repo}/commits/{sha} -h <GITHUB_HOST>
```

## JSON Output

Add `--json field1,field2,...` to most commands for structured output. Use `--jq` to filter.
