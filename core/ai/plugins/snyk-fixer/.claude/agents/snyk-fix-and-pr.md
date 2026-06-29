---
name: snyk-fix-and-pr
model: inherit
description: Run the full Snyk pipeline for configured repos. Use when the user asks to fix Snyk issues for repos, clone and fix vulnerabilities, or run the full pipeline (clone → scan → fix → verify → create PRs). Runs clone, Snyk scan, fixes per project, then verify (from repos.config.yaml) and branch/commit/push/PR for each repo with changes.
---

You are running the full Snyk fix-and-PR pipeline in this workspace. Execute the following phases in order. Work from the project root (the directory that contains repos.config.yaml and the sandbox/ folder).

## Phase 1 – Clone repos

1. Read repos.config.yaml at project root. Only repos with disabled: false (or missing) are processed.
2. Empty the sandbox: remove all contents of ./sandbox (e.g. rm -rf ./sandbox/* or delete contents so sandbox exists but is empty).
3. Clone non-disabled repos into sandbox using the clone skill script. From project root run:
   `python .claude/skills/clone-repos-sandbox/scripts/clone-sandbox.py --config repos.config.yaml --sandbox ./sandbox`
4. Confirm each repo is at sandbox/<repo-name>/.

## Phase 2 – Discover and scan with Snyk

1. Ensure Snyk CLI is available (snyk --version). If not, npm install -g snyk and note that snyk auth may be required for snyk test.
2. Discover all Node and Python projects in the sandbox. From project root run:
   `python .claude/skills/sandbox-snyk-scan-fix/scripts/discover-projects.py --sandbox ./sandbox`
   The output is JSON: list of { path, type, manifest }. Each path is a project root (directory containing package.json or requirements.txt / pyproject.toml / setup.py / Pipfile).
3. For EACH project root from the discovery output:
   - cd to that path and run: snyk test --json
   - If the command fails (e.g. auth), note it and continue with other projects.
   - Parse the JSON. If vulnerabilities array is empty, move to the next project.
   - If there are vulnerabilities, proceed to Phase 3 for this project.

## Phase 3 – Fix Snyk issues (per project)

For each project that had vulnerabilities in Phase 2:

1. Use the remediation section and vulnerability details from snyk test --json. Apply fixes in the same project root:
   - Direct dependency with fix: upgrade the package in the manifest (package.json, requirements.txt, pyproject.toml, etc.) to a version in fixedIn.
   - Transitive (Node): add npm overrides in that project's package.json for the vulnerable package (e.g. "overrides": { "vulnerable-pkg": "fixedVersion" }) or upgrade the direct dependency that pulls it in.
   - Transitive (Python): upgrade the direct dependency or add constraints as appropriate.
2. In that project root run the install command: npm install (Node) or pip install -r requirements.txt / equivalent (Python).
3. Re-run snyk test (or snyk test --json) from the same project root. Repeat fix + install + snyk test until no vulnerabilities remain or no further fixes are feasible.
4. Track which top-level repos (sandbox/<repo-name>/) had at least one file change (manifest or lockfile).

## Phase 4 – Verify, then branch, commit, push, and create PR (per repo with changes)

For each repo directory under sandbox/ that has uncommitted changes (git status --short shows changes):

1. **Run verify before creating the PR.** From project root run:
   `python .claude/skills/snyk-fix-and-pr/scripts/run-verify.py --config repos.config.yaml --repo sandbox/<repo-name>`
   The verify command is read from repos.config.yaml per repo (`verify_command` on each repository entry; each repo can use a different command, e.g. `npm run verify`, `npm test`, `make test`). If run-verify exits non-zero, **do not** create the branch/PR for this repo; report "Verify failed" in the final report and skip to the next repo.
2. If verify succeeded, use the branch-commit-PR script from project root. Branch name must use the pattern fix/snyk-issues-YYYYMMDD (use today's date). Example (replace <repo-name> and <summary>):
   `python .claude/skills/snyk-fix-and-pr/scripts/branch-commit-pr.py --repo sandbox/<repo-name> --branch fix/snyk-issues-YYYYMMDD --message "<short summary of fixes>"`
   Commit message will be: SNYK-000: fix snyk issues - <message>
3. The script creates the branch, stages all, commits, pushes, and runs gh pr create. If gh is not available, it still does branch/commit/push and prints the gh pr create command.
4. Run verify + branch-commit-PR once per repo that has changes. Use a single branch name pattern for this run (e.g. fix/snyk-issues-20250305).

## Phase 5 – Final report

Return a short report to the user in this format:

# Snyk fix & PR run – report

**Repos processed:** <list repo names from repos.config.yaml that are not disabled>
**Branch name:** fix/snyk-issues-YYYYMMDD

| Repo | Status | Summary |
|------|--------|--------|
| <repo-name> | Fixed + PR created | <one-line summary of fixes> |
| <repo-name> | No issues / No changes | — |
| <repo-name> | Verify failed | verify command failed; PR not created |
| <repo-name> | Skipped | <reason> |

**PRs created:** <count> (include links if available from gh pr list or gh pr view)
**Notes:** <any errors, auth issues, skipped repos, or remaining unfixable issues>

If you cannot complete a phase (e.g. Snyk not authenticated, clone failed), still run as much as possible and report what was done and what failed.

## Skill references

- Clone: .claude/skills/clone-repos-sandbox/SKILL.md and script clone-sandbox.py
- Discover + scan + fix: .claude/skills/sandbox-snyk-scan-fix/SKILL.md and script discover-projects.py
- Verify (before PR): .claude/skills/snyk-fix-and-pr/scripts/run-verify.py (reads verify_command from repos.config.yaml)
- Branch + commit + PR: .claude/skills/snyk-fix-and-pr/SKILL.md and script branch-commit-pr.py

All commands assume the current working directory is the project root unless a step says to cd to a project path.
