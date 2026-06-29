---
name: sandbox-snyk-scan-fix
description: Scans the sandbox for Node and Python projects, runs Snyk test on each, analyzes reports, and suggests or applies fixes. Use when the user asks to scan/fix Snyk issues in the sandbox, run Snyk across repos, or fix vulnerabilities in sandbox projects.
---

# Sandbox Snyk Scan & Fix

## When to Use

- User asks to scan the sandbox for Snyk issues, fix vulnerabilities in sandbox repos, or run Snyk across all projects
- User wants to discover Node/Python projects in the sandbox and run Snyk test on each
- Bulk security scan and remediation across cloned repos

---

## 1. Ensure Snyk CLI Is Available

**Check first** (no install if already present):

```bash
snyk --version
```

If the command fails or is not found:

```bash
npm install -g snyk
```

**Authenticate** (required for `snyk test` to use Snyk’s vulnerability DB):

```bash
snyk auth
```

Follow the browser/link flow if prompted. If `snyk test` fails with API/auth errors (e.g. SNYK-0003, 400 Bad Request), ask the user to run `snyk auth` again.

---

## 2. Discover Projects in the Sandbox

**Sandbox location**: Default is `./sandbox` at project root (same as clone-repos-sandbox). Each repo is at `sandbox/<repo-name>/`.

**Run the discovery script** from the project root:

```bash
python .claude/skills/sandbox-snyk-scan-fix/scripts/discover-projects.py [--sandbox ./sandbox]
```

Output is JSON: array of `{"path": "sandbox/repo-name/...", "type": "node"|"python", "manifest": "package.json"|"requirements.txt"|...}`. Each entry is a **project root** (directory where the manifest lives).

**Project detection rules** (used by the script):

- **Node**: Any directory containing `package.json` (including nested, e.g. `sandbox/repo/packages/app/package.json`).
- **Python**: Any directory containing one of: `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`. Treat that directory as the project root for Snyk.

**Manual discovery** (if the script is unavailable): For each repo dir under `sandbox/`, search recursively for `package.json` (Node) or `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` (Python). Treat each manifest’s directory as a project root.

---

## 3. Run Snyk Test per Project

For **each** discovered project:

1. **Node** (directory with `package.json`):
   ```bash
   cd <project_path> && snyk test --json
   ```
   Save JSON to a temp file or variable for analysis. For human-readable output: `cd <project_path> && snyk test`.

2. **Python** (directory with `requirements.txt`, `pyproject.toml`, `setup.py`, or `Pipfile`):
   ```bash
   cd <project_path> && snyk test --json
   ```
   Snyk auto-detects the manifest. To force a file: `snyk test --file=requirements.txt --json` (or `--file=pyproject.toml` etc.).

Run from the **project root** (the directory that contains the manifest). One repo can have multiple projects; run Snyk once per project root.

---

## 4. Analyzing the Report

Snyk JSON reports contain:

- **`vulnerabilities`**: For each issue use: `moduleName`, `version`, `severity`, `cvssScore`, `fixedIn`, `from`, `isUpgradable`, `isPatchable`, `description`.
- **`remediation`**: May include `upgrade`, `patch`, `pin`, `ignore` hints.
- **`path`** / **`displayTargetFile`**: Which lockfile/manifest the finding applies to.

**Dependency path (`from`)**:

- Two elements (e.g. `["my-app@1.0.0", "lodash@4.17.15"]`) → **direct** dependency.
- More than two → **transitive**. Prefer upgrading a direct dependency that pulls in a fixed version; otherwise use overrides (Node) or constraint files (Python).

Apply remediation in the **same project root** where you ran `snyk test` (the `path` in the report is relative to that directory). For patterns see [reference.md](reference.md).

---

## 5. Suggesting and Applying Fixes

For each vulnerability, give a **short, actionable** suggestion:

1. **Direct dependency, fix available**: Upgrade the package to a version in `fixedIn` in the project’s manifest (`package.json`, `requirements.txt`, `pyproject.toml`, etc.).
2. **Transitive (Node), no direct upgrade path**: Add **npm overrides** in that project’s `package.json`:
   ```json
   "overrides": {
     "vulnerable-package-name": ">=fixed.version"
   }
   ```
   Or upgrade the parent dependency if a newer version brings in the fix.
3. **Transitive (Python)**: Upgrade the direct dependency that pulls in the vulnerable package, or add a constraint in `requirements.txt` / use `pip-tools` constraints.
4. **Patch available** (`isPatchable: true`): Mention `snyk fix` or applying Snyk’s patch.

Then **apply** the changes (edit manifest/lockfile in the project root), run install, and re-run Snyk (see step 6).

---

## 6. After Applying Fixes

- **Node**: Run `npm install` in the project root. If the project has `npm run verify` (or `lint`/`format`), run it.
- **Python**: Run `pip install -r requirements.txt` (or the appropriate install command for that project). Run project tests/linters if present.
- **Re-scan**: Run `snyk test` (and optionally `snyk test --json`) again from the same project root and confirm the issue is gone. Repeat until no new issues or no further fixes are feasible.

---

## Quick Checklist

- [ ] Snyk CLI present (`snyk --version`); if not, `npm install -g snyk`
- [ ] Authenticated if running `snyk test` (`snyk auth`)
- [ ] Sandbox path clear (default `./sandbox`); discover projects via script or manual search
- [ ] For each project root: run `snyk test --json` from that directory
- [ ] Each vulnerability mapped to the **correct project root** and manifest
- [ ] Remediation: upgrade direct dep, overrides/constraints for transitive, or patch
- [ ] After edits: install deps, run project verify/lint if any, re-run `snyk test`

---

## Optional: Generate Report Files

To save a report per project for later analysis:

```bash
cd <project_path> && snyk test --json > snyk-report.json
```

Use the same project root as for `snyk test`. Paths in the report are relative to that root.
