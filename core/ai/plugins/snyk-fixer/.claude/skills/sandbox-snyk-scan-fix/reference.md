# Snyk Report Structure & Remediation Patterns (Generic)

## Report JSON (high level)

- **`vulnerabilities[]`**: Each has `id`, `moduleName`, `version`, `severity`, `cvssScore`, `fixedIn[]`, `from[]`, `isUpgradable`, `isPatchable`, `description`, `references`.
- **`remediation`**: `upgrade`, `patch`, `pin`, `ignore` (often keyed by vulnerability id).
- **`summary`**: e.g. "2 vulnerable dependency paths".
- **`projectName`**, **`displayTargetFile`**, **`path`**: Which project and lockfile/manifest (paths relative to the directory where `snyk test` was run).

## Dependency path (`from`)

- `["my-app@1.0.0", "lodash@4.17.15"]` → **Direct** dependency (lodash).
- `["my-app@1.0.0", "aws-cdk-lib@2.239.0", "minimatch@3.1.2"]` → **Transitive** (minimatch via aws-cdk-lib).

## Remediation patterns

| Case | Action |
|------|--------|
| Direct dep, `fixedIn` set | Bump that package in the project’s manifest (`package.json`, `requirements.txt`, `pyproject.toml`) to a version in `fixedIn`. |
| Transitive (Node), parent has no update | Add npm `overrides` for the vulnerable package to a version in `fixedIn` in that project’s `package.json`. |
| Transitive (Node), parent has update | Prefer upgrading the parent; if it pulls in a fixed version, no override needed. |
| Transitive (Python) | Upgrade the direct dependency that brings in the vulnerable package, or add version constraints in `requirements.txt` / dependency spec. |
| `isPatchable: true` | Optionally use `snyk fix` or apply Snyk’s patch. |

## Project roots

- **Node**: Directory containing `package.json`. Apply fixes in that directory’s `package.json` (and run `npm install` there).
- **Python**: Directory containing `requirements.txt`, `pyproject.toml`, `setup.py`, or `Pipfile`. Apply fixes in the relevant manifest; reinstall and re-run Snyk from that directory.

Use `path` / `displayTargetFile` in the report to confirm which lockfile/manifest the finding applies to; it is relative to the project root where `snyk test` was executed.
