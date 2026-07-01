# Codacy Plugin

Fetch code quality issues from Codacy and get actionable insights for improving code quality in pull requests.

## Overview

This plugin provides integration with Codacy code quality platform to:
- Fetch code quality issues from pull requests
- Extract Codacy analysis URLs from GitHub PR status checks
- Filter issues by severity, category, and files changed in PR
- Get actionable recommendations for resolving issues
- Support both Codacy Cloud and self-hosted instances

## Prerequisites

- Python 3.7+
- Git repository with Codacy integration enabled
- Network access to Codacy API (Cloud or self-hosted)

## Authentication/Setup

Credentials are stored in `~/.claude-sauce.json`:

```json
{
  "codacy": {
    "API_TOKEN": "your-codacy-api-token",
    "API_URL": "https://api.codacy.com"
  },
  "github": {
    "TOKEN": "your-github-token"
  }
}
```

**Configuration notes:**
- `API_URL` is optional and defaults to `https://api.codacy.com` (Codacy Cloud)
- For self-hosted Codacy instances, set `API_URL` to your instance URL (e.g., `https://<CODACY_HOST>`)
- GitHub `TOKEN` is required for extracting Codacy URLs from PR status checks

### Automated Credential Setup

The first time you use the Codacy integration, Claude will automatically guide you through credential setup:

1. Claude detects missing credentials and offers to help
2. Opens token generation pages in your browser:
   - **Codacy API token**: https://app.codacy.com/account/apiTokens (or your self-hosted instance)
   - **GitHub token**: https://github.com/settings/tokens (or your GitHub Enterprise instance)
3. Collects your tokens securely via masked input
4. Saves credentials to `~/.claude-sauce.json` automatically
5. Retries your analysis

No manual file editing required!

### Manual Setup

If you prefer to set up credentials manually:

1. **Generate Codacy API token**:
   - Cloud: https://app.codacy.com/account/apiTokens
   - Self-hosted: `https://<your-codacy-instance>/account/apiTokens`
   - Create a token with "Read" permissions

2. **Generate GitHub token**:
   - GitHub.com: https://github.com/settings/tokens
   - GitHub Enterprise: `https://<your-github-instance>/settings/tokens`
   - Required scopes: `repo` (for private repos) or `public_repo` (for public repos)

3. Create or edit `~/.claude-sauce.json` with the structure shown above
4. Set appropriate file permissions: `chmod 600 ~/.claude-sauce.json`

## Skills

### codacy-integration

Automatically triggered when you ask to fetch Codacy issues or analyze code quality for a PR.

**Capabilities:**
- Auto-detects current PR from git branch
- Extracts Codacy analysis URL from GitHub PR status checks
- Fetches code quality issues with filtering options
- Groups issues by file with severity and category
- Filters to only files changed in PR (optional)
- Supports Codacy Cloud and self-hosted instances

**Example triggers:**
```
"Fetch Codacy issues for this PR"
"Get code quality issues from Codacy"
"What are the Codacy findings for PR 123?"
"Show me Security issues from Codacy"
```

For detailed skill documentation, see [skills/codacy-integration/SKILL.md](skills/codacy-integration/SKILL.md).

## Usage Patterns

### Analyzing Current PR

```
1. Checkout your PR branch
2. Ask: "Get Codacy issues for this PR"
3. Claude auto-detects the PR and fetches issues
```

### Analyzing Specific PR

```
"Fetch Codacy issues for PR 123"
or
"Get Codacy issues from https://github.com/org/repo/pull/123"
```

### Filtering by Severity

```
"Show me only Error-level issues from Codacy"
or
"Get Codacy warnings and errors"
```

### Filtering by Category

```
"Get Security issues from Codacy"
or
"Show ErrorProne and Security issues from Codacy"
```

Valid categories:
- Security
- ErrorProne
- CodeStyle
- Performance
- Complexity
- UnusedCode
- Documentation
- Compatibility

### Filtering to PR Files Only

```
"Get Codacy issues for files changed in this PR"
```

This shows only issues in files that were modified in the PR, ignoring existing issues in untouched files.

## Issue Resolution Workflow

When Codacy issues are found:

1. **Review the issues** - Understand severity and impact
2. **Prioritize by severity**:
   - **Error**: Fix immediately (blocks quality gates)
   - **Warning**: Fix before merging
   - **Info**: Consider addressing
3. **Group by category** - Address similar issues together
4. **Fix in code** - Make necessary changes
5. **Re-check** - Fetch issues again to verify fixes

## Troubleshooting

### "GitHub token not found"

**Symptoms**: Cannot extract Codacy URL from PR

**Solutions**:
1. Add GitHub token to `~/.claude-sauce.json` under `github.TOKEN`
2. Generate token at: https://github.com/settings/tokens (or your GitHub Enterprise)
3. Required scopes: `repo` or `public_repo`
4. For GitHub Enterprise, ensure token has access to the instance

### "Codacy API token not found"

**Symptoms**: Cannot fetch issues from Codacy

**Solutions**:
1. Add Codacy token to `~/.claude-sauce.json` under `codacy.API_TOKEN`
2. Generate token at: https://app.codacy.com/account/apiTokens
3. For self-hosted instances, ensure `codacy.API_URL` is set correctly

### "No Codacy status check found"

**Symptoms**: Cannot find Codacy analysis URL in PR

**Solutions**:
1. Verify Codacy is configured for the repository
2. Check that PR has been analyzed by Codacy (may take a few minutes)
3. Ensure repository is connected to Codacy
4. Manually provide Codacy URL using `--url` parameter

### "Repository not found"

**Symptoms**: Codacy API returns 404

**Solutions**:
1. Verify provider, organization, and repository names are correct
2. Check that repository exists in Codacy
3. For self-hosted instances, ensure `codacy.API_URL` is set correctly
4. For GitHub Enterprise, use `ghe` as the provider value

### SSL Certificate Errors (Self-hosted)

**Symptoms**: SSL verification failed

**Solutions**:
1. Verify `codacy.API_URL` in `~/.claude-sauce.json` is correct
2. Check with Codacy administrator about certificate setup
3. For self-signed certificates, may need to add certificate to system trust store

### "Could not auto-detect PR number"

**Symptoms**: Cannot determine PR from git branch

**Solutions**:
1. Ensure you're in a git repository (`.git` directory exists)
2. Provide explicit PR number or URL
3. Check that branch has an associated PR

## Self-Hosted Codacy Instances

For self-hosted Codacy instances:

1. Set `codacy.API_URL` in `~/.claude-sauce.json`:
   ```json
   {
     "codacy": {
       "API_TOKEN": "your-token",
       "API_URL": "https://<CODACY_HOST>"
     }
   }
   ```

2. Use provider `ghe` for GitHub Enterprise repositories:
   ```
   "Get Codacy issues for this GHE repository"
   ```

3. Token generation URL will be at your instance:
   `https://<your-codacy-instance>/account/apiTokens`

## Plugin Details

**Name**: codacy
**Version**: 1.0.0
**Author**: <AUTHOR_NAME>

---

**Quick Start**: Run "Fetch Codacy issues for this PR" to analyze code quality!
