# Snyk fix project

## What it does

Scans repos from the config file, finds Python and npm projects, clones them to a sandbox, checks for Snyk issues, fixes them, and creates a PR for each repo.

## Dependencies

- **gh (GitHub CLI)**
  - Install: `brew install gh`
  - Then: `gh auth login`

- **Snyk CLI**
  - Install: `npm install -g snyk`
  - Then: `snyk auth`

## How to use

1. Edit repos in `repos.config.yaml` (add/remove/disable repos, set `verify_command` if needed)
2. In Cursor/Claude chat, ask to fix Snyk issues and tag the agent: **@.claude/agents/snyk-fix-and-pr.md**