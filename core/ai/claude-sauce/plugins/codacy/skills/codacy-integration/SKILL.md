---
name: codacy-integration
description: Comprehensive Codacy code quality integration for fetching issues from pull requests, analyzing code quality metrics, and resolving code quality issues. Use when Claude needs to interact with Codacy for: (1) Fetching code quality issues from a PR, (2) Getting Codacy analysis URL from GitHub PR, (3) Analyzing and resolving Codacy issues, (4) Checking code quality status, or any other Codacy-related tasks.
---

# Codacy Integration

Fetch code quality issues from Codacy API and resolve them. Supports auto-detection of PRs by reading git information directly from `.git/HEAD` and `.git/config` files (no git CLI required), and extraction of Codacy URLs from GitHub status checks.

## Quick Start

### Get Codacy URL from Current PR

```bash
python3 scripts/get_codacy_url.py
```

### Fetch Issues from Codacy

```bash
python3 scripts/fetch_issues.py --provider gh --organization myorg --repository myrepo --branch feature-branch
```

### Complete Workflow (Auto-detect PR)

```bash
CODACY_URL=$(python3 scripts/get_codacy_url.py)
python3 scripts/fetch_issues.py --url "$CODACY_URL"
```

### Complete Workflow (Filter by PR Files)

To get only issues in files changed by the PR:

```bash
CODACY_URL=$(python3 scripts/get_codacy_url.py --url https://github.com/org/repo/pull/123 --quiet)
PR_URL=$(python3 scripts/get_codacy_url.py --url https://github.com/org/repo/pull/123 --json | python3 -c "import sys, json; print(json.load(sys.stdin)['pr_url'])")
python3 scripts/fetch_issues.py --url "$CODACY_URL" --pr-url "$PR_URL"
```

Or more simply, if you have the PR URL:

```bash
CODACY_URL=$(python3 scripts/get_codacy_url.py --url https://github.com/org/repo/pull/123 --quiet)
python3 scripts/fetch_issues.py --url "$CODACY_URL" --pr-url "https://github.com/org/repo/pull/123"
```

## Configuration

For detailed authentication setup, see the [codacy plugin README](../../README.md#authenticationsetup).

Quick reference:
- Requires Codacy API token and GitHub token
- Stored in `~/.claude-sauce.json`
- Automated setup available on first use

## Getting Codacy URL

Use `scripts/get_codacy_url.py` to extract the Codacy analysis URL from a GitHub PR.

### Auto-detect Current PR

```bash
python3 scripts/get_codacy_url.py
```

Automatically detects the PR associated with the current git branch by reading `.git/HEAD` to get the branch name and `.git/config` to get the repository information. No git CLI required.

### Explicit PR Number

```bash
python3 scripts/get_codacy_url.py --pr 123
```

### Explicit PR URL

```bash
python3 scripts/get_codacy_url.py --url https://github.com/org/repo/pull/123
```

### JSON Output

```bash
python3 scripts/get_codacy_url.py --pr 123 --json
```

Outputs JSON with Codacy URL, PR number, provider, organization, and repository.

## Fetching Issues

Use `scripts/fetch_issues.py` to fetch code quality issues from Codacy API.

### Basic Usage

```bash
python3 scripts/fetch_issues.py --provider gh --organization myorg --repository myrepo
```

### Filter by Branch

```bash
python3 scripts/fetch_issues.py --provider gh --organization myorg --repository myrepo --branch feature-branch
```

### Filter by Severity Levels

```bash
python3 scripts/fetch_issues.py --provider gh --organization myorg --repository myrepo --levels Error,Warning
```

Valid levels: `Error`, `Warning`, `Info`

### Filter by Categories

```bash
python3 scripts/fetch_issues.py --provider gh --organization myorg --repository myrepo --categories Security,ErrorProne
```

Valid categories: `Security`, `CodeStyle`, `ErrorProne`, `Performance`, `Compatibility`, `UnusedCode`, `Complexity`, `Documentation`

### Extract Info from Codacy URL

```bash
python3 scripts/fetch_issues.py --url https://app.codacy.com/organizations/gh/myorg/myrepo/...
```

Automatically extracts provider, organization, and repository from the Codacy URL.

### Self-Hosted Codacy Instance

For self-hosted Codacy instances, configure `codacy.API_URL` in `~/.claude-sauce.json`:

```bash
python3 scripts/fetch_issues.py --url https://<CODACY_HOST>/ghe/myorg/myrepo/pullRequest?prid=123456
```

Or with explicit provider/org/repo:

```bash
python3 scripts/fetch_issues.py --provider ghe --organization myorg --repository myrepo --branch feature-branch
```

### JSON Output

```bash
python3 scripts/fetch_issues.py --provider gh --organization myorg --repository myrepo --json
```

Outputs raw JSON response from Codacy API.

## CLI Arguments

### get_codacy_url.py

| Argument | Description |
|----------|-------------|
| `--pr PR_NUMBER` | Explicit PR number (optional, auto-detects if not provided) |
| `--url PR_URL` | Explicit PR URL (optional) |
| `--json` | Output JSON format with all extracted info |
| `--quiet, -q` | Suppress status messages |

### fetch_issues.py

| Argument | Description |
|----------|-------------|
| `--provider PROVIDER` | Provider (`gh` for GitHub, `ghe` for GitHub Enterprise, `bb` for Bitbucket) - required unless `--url` provided |
| `--organization ORG` | Organization name - required unless `--url` provided |
| `--repository REPO` | Repository name - required unless `--url` provided |
| `--branch BRANCH` | Branch name (optional, for PR branch) |
| `--levels LEVELS` | Comma-separated levels (`Error,Warning,Info`) |
| `--categories CATEGORIES` | Comma-separated categories (see valid categories above) |
| `--url CODACY_URL` | Extract provider/org/repo from Codacy URL (alternative to explicit args) |
| `--pr-url PR_URL` | GitHub PR URL to filter issues to only files changed in the PR |
| `--json` | Output raw JSON |

## Workflow Examples

### Example 1: Check Issues for Current PR

```bash
CODACY_URL=$(python3 scripts/get_codacy_url.py --quiet)
python3 scripts/fetch_issues.py --url "$CODACY_URL"
```

The script automatically detects the branch from `.git/HEAD`, so no `--branch` argument is needed.

### Example 2: Get Only Security Issues

```bash
python3 scripts/fetch_issues.py \
  --provider gh \
  --organization myorg \
  --repository myrepo \
  --categories Security \
  --levels Error,Warning
```

### Example 3: Check Specific PR

```bash
PR_NUM=123
CODACY_URL=$(python3 scripts/get_codacy_url.py --pr $PR_NUM --quiet)
python3 scripts/fetch_issues.py --url "$CODACY_URL"
```

### Example 4: Self-Hosted Codacy Instance

```bash
python3 scripts/fetch_issues.py \
  --url "https://<CODACY_HOST>/ghe/myorg/myrepo/pullRequest?prid=123456"
```

**Note**: Configure `codacy.API_URL` in `~/.claude-sauce.json` for self-hosted instances.

### Example 5: GitHub Enterprise PR

```bash
python3 scripts/get_codacy_url.py \
  --url "https://<GITHUB_HOST>/myorg/myrepo/pull/123"
```

**Note**: Configure `github.TOKEN` in `~/.claude-sauce.json` for authentication.

## Issue Resolution

When fetching issues, the script outputs issues grouped by file with:
- File path and line number
- Severity level (Error, Warning, Info)
- Category (Security, CodeStyle, ErrorProne, etc.)
- Issue message
- Pattern ID

### Resolving Issues

1. **Review the issues** - Understand what each issue is about
2. **Prioritize by severity** - Fix Errors first, then Warnings
3. **Fix issues in code** - Make the necessary code changes
4. **Re-check** - Run the fetch script again to verify issues are resolved

### Common Issue Types

- **Security**: Potential security vulnerabilities (e.g., SQL injection, XSS)
- **ErrorProne**: Code patterns that may cause runtime errors
- **CodeStyle**: Style violations (e.g., formatting, naming conventions)
- **Performance**: Performance anti-patterns
- **Complexity**: Overly complex code that should be simplified
- **UnusedCode**: Dead code that can be removed
- **Documentation**: Missing or inadequate documentation

## Requirements

- Python 3.7+ (standard library only - no external dependencies)
- GitHub API token - Set in `~/.claude-sauce.json` under `github.TOKEN` (for `get_codacy_url.py`)
- Codacy API token - Set in `~/.claude-sauce.json` under `codacy.API_TOKEN`

**Note**: The scripts are dependency-free and use only Python standard library. They read git information directly from `.git/HEAD` and `.git/config` files.

## Provider Values

- `gh` - GitHub (github.com)
- `ghe` - GitHub Enterprise (e.g., <GITHUB_HOST>)
- `bb` - Bitbucket

## Troubleshooting

### "GitHub token not found"

- Add GitHub token to `~/.claude-sauce.json` under `github.TOKEN`
- Generate a token at: https://github.com/settings/tokens (or your GitHub Enterprise instance)
- For GitHub Enterprise, ensure the token has access to the enterprise instance

### "Authentication token not found" (Codacy)

- Add Codacy token to `~/.claude-sauce.json` under `codacy.API_TOKEN`
- For self-hosted instances, ensure `codacy.API_URL` is set correctly in config file

### "SSL certificate verify failed" (Self-hosted Codacy)

- Ensure you're using the correct `codacy.API_URL` in `~/.claude-sauce.json`
- Verify the Codacy instance URL is correct
- For self-signed certificates, contact your Codacy administrator

### "Could not auto-detect PR number"

- Ensure you're in a git repository (`.git` directory exists)
- The script reads git information from `.git/HEAD` and `.git/config`
- If auto-detection fails, provide explicit `--pr` or `--url` arguments

### "No Codacy status check found"

- Ensure Codacy is configured for the repository
- Check that the PR has been analyzed by Codacy
- Verify the repository is connected to Codacy
- Wait a few minutes after PR creation for Codacy to analyze

### "Repository not found"

- Verify provider, organization, and repository names are correct
- Check that the repository exists in Codacy
- For self-hosted instances, ensure `codacy.API_URL` is set correctly in config file
- For GitHub Enterprise, use `ghe` as the provider value
