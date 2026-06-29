---
name: clone-repos-sandbox
description: Clones non-disabled repositories from repos.config.yaml into a sandbox directory for automated changes. Use when preparing a sandbox of repos, syncing clones from the config, or when the user asks to clone repos or set up the sandbox.
---

# Clone Repos to Sandbox

## Purpose

Clone only **non-disabled** repositories from `repos.config.yaml` into a dedicated sandbox directory so the agent (or future automation) can make changes across them.

## When to Use

- User asks to clone repos, set up sandbox, or sync repos from config
- Preparing the workspace for bulk/automatic changes across configured repos
- Refreshing or (re)creating the sandbox from the current config

## Config Format

Expect `repos.config.yaml` at project root (or path given to the script):

```yaml
repositories:
  - name: project-name
    repository: git@host:org/repo.git
    disabled: true   # when true, skip this repo
```

Only entries with `disabled: false` or missing `disabled` are cloned.

## Workflow

1. **Run the clone script** from the project root (or with explicit config path):
   ```bash
   python .claude/skills/clone-repos-sandbox/scripts/clone-sandbox.py
   ```
   Or with custom config and sandbox:
   ```bash
   python .claude/skills/clone-repos-sandbox/scripts/clone-sandbox.py \
     --config path/to/repos.config.yaml \
     --sandbox ./my-sandbox
   ```

2. **Sandbox layout**: Repos are cloned into `sandbox/<name>/` (using the `name` field from config). Default sandbox directory is `./sandbox` at project root.

3. **Idempotency**: The script clones missing repos and optionally updates existing clones (`--pull`). It does not delete or force-reset by default.

## Script Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to repos config YAML (default: `repos.config.yaml` in cwd) |
| `--sandbox DIR` | Sandbox directory for clones (default: `./sandbox`) |
| `--pull` | Run `git pull` in existing clones to update |
| `--shallow` | Clone with `--depth 1` |

## After Cloning

- Use the sandbox paths (e.g. `sandbox/renaissance/`) when applying automated changes.
- Re-run the script after adding or enabling repos in `repos.config.yaml` to add new clones.
