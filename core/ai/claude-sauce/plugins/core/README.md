# Core Plugin

Core Claude Sauce utilities and cross-plugin capabilities.

## Skills

### credential-setup

Automatically handles credential setup when Claude Sauce plugins report missing credentials.

**How it works:**
- Detects "MISSING CREDENTIALS" error patterns from any plugin
- Guides users through token generation
- Collects credentials via secure prompts
- Updates `~/.claude-sauce.json`
- Retries the original command

**Supported services:**
- Jira (atlassian plugin)
- Confluence (atlassian plugin)
- Jenkins (jenkins plugin)
- AWS Bedrock (bedrock-usage plugin)

This skill provides a unified credential management experience across all Claude Sauce plugins.
