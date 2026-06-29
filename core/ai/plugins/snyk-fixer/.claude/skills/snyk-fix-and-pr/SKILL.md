---
name: snyk-fix-and-pr
description: End-to-end workflow: read repos from repos.config.yaml, clone to sandbox, fix Snyk issues per repo, then open a new branch and create a pull request for each repo with fixes. Use when the user wants to fix Snyk vulnerabilities across configured repos and open PRs for each.
---

# Snyk Fix and Create PRs

## Purpose

Orchestrates the full pipeline for configured repos: clone, scan, fix, verify, branch, commit, push, and open a PR per repo with changes. This skill composes the clone and scan/fix skills and adds verify + PR creation on top.

## When to Use

- User asks to fix Snyk issues for repos in the config and create PRs
- User wants a workflow that clones, fixes, and opens a PR per repo

## Run via Cursor subagent (recommended)

This workflow runs as a **Cursor custom subagent** so it executes in an isolated context.

- **Subagent file:** `.claude/agents/snyk-fix-and-pr.md`
- **Invoke:** `/snyk-fix-and-pr` in chat, or say "Use the snyk-fix-and-pr subagent."

The subagent runs Phase 1 (clone) → Phase 2 (discover + scan) → Phase 3 (fix) → Phase 4 (verify + branch/PR) → Phase 5 (report). Delegate to the subagent; do not run pipeline steps in the main agent.

## Prerequisites

- **Snyk CLI**: `snyk --version`; if missing, `npm install -g snyk` and run `snyk auth`
- **Git**: Repos cloned and fixes applied in sandbox
- **GitHub CLI** (for PRs): `gh --version`; if missing, install and run `gh auth login`

## Commit Message Pattern

**Required format:** `SNYK-000: fix snyk issues - {message}`

Keep `SNYK-000` as the ticket prefix (or use the ticket ID the user provides). `{message}` is a short summary of what was fixed.

## Scripts (unique to this skill)

### run-verify.py

Runs the `verify_command` from `repos.config.yaml` in a given repo. Use before creating a PR.

```bash
python .claude/skills/snyk-fix-and-pr/scripts/run-verify.py \
  --config repos.config.yaml --repo sandbox/<repo-name> [--dry-run]
```

If this exits non-zero, **do not** create the PR for that repo.

### branch-commit-pr.py

Creates branch, stages all, commits, pushes, and runs `gh pr create` in one go.

```bash
python .claude/skills/snyk-fix-and-pr/scripts/branch-commit-pr.py \
  --repo sandbox/<repo-name> \
  --branch fix/snyk-issues-YYYYMMDD \
  --message "<short summary>" \
  [--ticket SNYK-000] [--no-pr] [--dry-run]
```

If `gh` is not on PATH, the script completes branch/commit/push and prints the `gh pr create` command for manual use.

## Composed skills

- **Clone:** [clone-repos-sandbox](../clone-repos-sandbox/SKILL.md) — clones non-disabled repos from config into `sandbox/`
- **Scan & fix:** [sandbox-snyk-scan-fix](../sandbox-snyk-scan-fix/SKILL.md) — discovers projects, runs `snyk test`, and applies fixes
