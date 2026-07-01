---
name: jenkins-console-analyzer
description: Fetches Jenkins build console text and analyzes root causes of issues sorted by severity. Use when given a Jenkins job URL to debug builds, test runs, CI/CD pipelines, or deployments. The AI will analyze the console output to identify errors, warnings, and issues - prioritizing them by severity (critical, high, medium, low).
---

# Jenkins Console Analyzer

Fetch console text from Jenkins jobs and analyze root causes of issues, sorted by severity.

## Usage

```bash
python3 scripts/console_analyzer.py --url "<JENKINS_URL>" [OPTIONS]
```

## How to Setup Credentials

For detailed authentication setup, see the [jenkins plugin README](../../README.md#authenticationsetup).

Quick reference: Credentials in `~/.claude-sauce.json` (`USER`+`TOKEN` or `COOKIE` for SSO instances) or use CLI args `--user USERNAME --token TOKEN --cookie VALUE`

## Key Options

| Option | Description |
|--------|-------------|
| `--url URL` | Jenkins job URL (required) |
| `--user USER` | Username (overrides config) |
| `--token TOKEN` | API token (overrides config) |
| `--from-curl` | Extract auth from browser cURL (for SSO) |
| `--tail N` | Only last N lines (0=all) |
| `--force` | Force re-download (ignore cache) |
| `--no-verify-ssl` | Disable SSL verification |
| `--quiet, -q` | Only console text, no status messages |

## Analysis Output

The AI analyzes console output and provides:

**Job Summary**: Status (SUCCESS/FAILURE/etc), duration, build number

**Issues by Severity**: Critical → High → Medium → Low

**Issue Types**: Test failures, infrastructure problems, build errors, deployment issues, security problems

**Root Cause Summary**: Most likely cause, code vs infrastructure issue, actionable next steps

Output format:
```
Test Failures:
- test_name - What failed

Infrastructure Failures:
- Error message - Context

Summary: Root cause explanation and whether it's code or infrastructure/environment issue.
```
