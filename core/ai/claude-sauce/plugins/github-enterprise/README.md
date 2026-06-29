# GitHub Enterprise Plugin

Integration with GitHub Enterprise Server for accessing GitHub API functionality in enterprise environments.

## Overview

This plugin provides skills for:
- Authenticating with GitHub Enterprise instances
- Accessing GitHub Enterprise API via `gh` CLI
- Supporting enterprise-specific workflows
- Working with private repositories in enterprise environments

## Prerequisites

| Requirement | Purpose | Installation |
|-------------|---------|--------------|
| **GitHub CLI (`gh`)** | GitHub Enterprise API access | `brew install gh` (macOS) or [cli.github.com](https://cli.github.com/manual/installation) |
| **Network access** | GitHub Enterprise instance | VPN if required |

## Authentication/Setup

**IMPORTANT**: This plugin uses GitHub CLI (`gh`) authentication. It does **NOT** use `~/.claude-sauce.json`.

### Configure GitHub CLI

Authenticate with your GitHub Enterprise instance:

```bash
gh auth login
```

**Follow the prompts:**
1. Select "GitHub Enterprise Server"
2. Enter your GitHub Enterprise instance URL (e.g., `https://<GITHUB_HOST>`)
3. Choose authentication method:
   - **Token**: Paste a personal access token
   - **Browser**: Authenticate via web browser
4. Select preferred protocol (HTTPS recommended)
5. Authenticate with Git credentials when prompted

### Verify Authentication

Check authentication status:

```bash
gh auth status
```

Should show your GitHub Enterprise instance and authentication status.

### Generate Personal Access Token (if needed)

If using token authentication:

1. Navigate to your GitHub Enterprise instance
2. Go to Settings → Developer settings → Personal access tokens
3. Click "Generate new token"
4. Select required scopes:
   - `repo` - Full control of private repositories
   - `read:org` - Read org and team membership
   - `workflow` - Update GitHub Action workflows (if needed)
5. Generate token and copy immediately (shown only once)
6. Use token with `gh auth login`

### GitHub Enterprise Instance URL

For <ORG> environments:
```
https://<GITHUB_HOST>
```

For other organizations, use your organization's GitHub Enterprise URL.

## Skills

### github-enterprise

Automatically triggered when you need to access GitHub Enterprise APIs or work with enterprise repositories.

**Capabilities:**
- Authenticate with GitHub Enterprise Server
- Access private enterprise repositories
- Use all `gh` CLI commands with enterprise context
- Support for enterprise-specific API endpoints

**Example triggers:**
```
"Get pull requests from our enterprise GitHub"
"Access repository on <GITHUB_HOST>"
"Use gh CLI with enterprise instance"
```

For detailed skill documentation, see [skills/github-enterprise/SKILL.md](skills/github-enterprise/SKILL.md).

## Usage Patterns

### Working with Enterprise Pull Requests

```
gh pr list --repo org/repo
gh pr view 123 --repo org/repo
gh pr checkout 123
```

### Accessing Enterprise Repositories

```
gh repo view org/repo
gh repo clone org/repo
```

### Enterprise API Access

```
gh api /repos/org/repo/pulls
gh api /orgs/your-org/teams
```

### Switching Between Instances

If you have multiple GitHub instances configured:

```
gh auth switch
```

Select the GitHub Enterprise instance you want to use.

## Common Use Cases

### Code Reviews

```
1. List open PRs:
   gh pr list --repo org/repo

2. Review a specific PR:
   gh pr view 123 --repo org/repo

3. Check out PR for local testing:
   gh pr checkout 123
```

### Repository Management

```
1. View repository details:
   gh repo view org/repo

2. List organization repositories:
   gh repo list your-org

3. Clone enterprise repository:
   gh repo clone org/repo
```

### CI/CD Workflows

```
1. List workflow runs:
   gh run list --repo org/repo

2. View workflow run details:
   gh run view 123456 --repo org/repo

3. Trigger workflow:
   gh workflow run workflow-name --repo org/repo
```

## Troubleshooting

### "Not logged in to any GitHub hosts"

**Symptoms**: `gh` commands fail with authentication error

**Solutions**:
1. Run `gh auth login` and follow prompts
2. Select "GitHub Enterprise Server"
3. Enter your enterprise instance URL
4. Complete authentication flow

### "Could not resolve host"

**Symptoms**: Cannot connect to GitHub Enterprise instance

**Solutions**:
1. Verify GitHub Enterprise URL is correct
2. Check VPN connection if instance is internal
3. Test URL in browser first
4. Verify DNS resolution: `nslookup <GITHUB_HOST>`

### "Token expired" / "Bad credentials"

**Symptoms**: Previously working authentication now fails

**Solutions**:
1. Re-authenticate: `gh auth login`
2. Generate new personal access token
3. Check token hasn't been revoked in GitHub Enterprise settings
4. Verify token has required scopes

### "Resource not accessible by integration"

**Symptoms**: Specific API calls fail with permission error

**Solutions**:
1. Check personal access token has required scopes
2. Re-generate token with additional scopes if needed
3. Verify you have repository access in GitHub Enterprise
4. Contact GitHub Enterprise administrator for org-level permissions

### Multiple GitHub Instances

**Symptoms**: Confused about which GitHub instance is active

**Solutions**:
1. Check current auth status: `gh auth status`
2. List all authenticated instances: `gh auth status --show-token`
3. Switch instances: `gh auth switch`
4. Explicitly specify host: `gh pr list --repo org/repo --hostname <GITHUB_HOST>`

### SSL Certificate Errors

**Symptoms**: SSL verification failed when connecting

**Solutions**:
1. Check GitHub Enterprise instance has valid SSL certificate
2. Verify certificate trust chain is installed
3. Contact GitHub Enterprise administrator
4. For self-signed certificates (not recommended): check `gh` documentation for workarounds

## GitHub CLI Tips

### Useful Commands

```bash
# View all gh commands
gh help

# Get help for specific command
gh pr help

# Use JSON output for automation
gh pr list --json number,title,author

# Use JQ for advanced filtering
gh pr list --json number,state | jq '.[] | select(.state=="OPEN")'
```

### Configuration

GitHub CLI configuration is stored in:
- Credentials: `~/.config/gh/hosts.yml`
- Config: `~/.config/gh/config.yml`

### Extensions

Install `gh` extensions for additional functionality:
```bash
gh extension install owner/extension-name
```

## Plugin Details

**Name**: github-enterprise
**Version**: 1.0.0
**Author**: <AUTHOR_NAME>

---

**Quick Start**: Run `gh auth login` to connect to GitHub Enterprise!
