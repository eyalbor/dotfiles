---
name: credential-setup
description: Handles credential setup for Claude Sauce plugins. Use when bash stderr contains "MISSING CREDENTIALS: [SERVICE]" - guides token generation, collects credentials, updates ~/.claude-sauce.json, and retries the command.
---

# Credential Setup Handler

## Overview

When Claude Sauce plugins detect missing credentials, they print structured error messages to stderr. This skill detects those patterns and automates the complete setup process without requiring manual file editing.

## Detection Pattern

Monitor for bash command failures containing these patterns in stderr:

```
================================================================================
MISSING CREDENTIALS: [SERVICE]
================================================================================

The [service] integration requires credentials in ~/.claude-sauce.json

Required configuration keys:
  - [KEY1]: [description]
  - [KEY2]: [description]

Token generation URL: [URL]

================================================================================
```

**Key indicators:**
- Line contains "MISSING CREDENTIALS: " followed by service name in ALL CAPS
- "Required configuration keys:" section lists needed keys
- Optional "Token generation URL:" provides link to token generation page

## Automated Setup Workflow

### Step 1: Detect and Parse Error

When you see this error pattern:
1. Extract the service name (text after "MISSING CREDENTIALS:")
2. Extract required keys from the "Required configuration keys:" section
3. Extract the token generation URL if present

### Step 2: Offer to Open Token Generation URL

If a token generation URL is provided, offer to open it:

```text
I see you need [service] credentials. Let me help you set this up.

I can open the token generation page for you. Would you like me to open:
[token_generation_url]
```

If the user agrees:
- **macOS**: Run `open "[URL]"`
- **Linux**: Run `xdg-open "[URL]"`
- **Windows**: Run `start "[URL]"`

### Step 3: Collect Credentials

Use AskUserQuestion to collect each required credential:

For each key listed in "Required configuration keys:":
- For URL fields: Ask "What's your [service] [key name]?" (e.g., "What's your Jira URL?")
- For token/password fields: Ask "Please paste your [service] [key name]:" (e.g., "Please paste your Jira API token:")

**Important security notes:**
- Credentials will be masked in AskUserQuestion by default
- Never echo credentials to stdout
- Never include credentials in command history
- Store credentials securely in config file only

### Step 4: Update Configuration File

1. **Read existing config** (or create new if doesn't exist):
   ```bash
   ~/.claude-sauce.json
   ```

2. **Parse JSON** from existing file (if present)

3. **Merge new credentials**:
   - Extract service name from error pattern
   - Create new service section if doesn't exist
   - Update config with collected credentials
   - Preserve existing credentials for other services

4. **Validate JSON** before writing:
   - Ensure proper syntax
   - Test `json.loads()` to verify

5. **Write updated config** using Write tool:
   ```json
   {
     "jira": {
       "URL": "https://jira.example.com",
       "API_TOKEN": "token_from_user"
     },
     "confluence": {
       "URL": "https://confluence.example.com",
       "API_TOKEN": "token_from_user"
     }
   }
   ```

### Step 5: Retry Original Command

After credentials are saved:
1. Re-run the exact command that failed
2. Command should now succeed with credentials present
3. If still fails, check error message for other issues (validation, permissions, etc.)

## Supported Services

The following Claude Sauce plugins support this automated credential setup:

- **Jira** (atlassian plugin)
- **Confluence** (atlassian plugin)
- **Jenkins** (jenkins plugin)
- **AWS Bedrock** (bedrock-usage plugin)

## Error Handling

### User Cancels AskUserQuestion

If user exits AskUserQuestion without providing credentials:
1. Print: "Credential setup cancelled. You can try again later."
2. Do not attempt to proceed
3. Do not make file changes

### Invalid Credentials (Script Validation Fails)

If the script validates the provided credentials and they're invalid:
1. Script will fail with validation error
2. Offer to retry setup: "Would you like to try different credentials?"
3. Start over at Step 2 (open token URL again)

### File Permission Errors

If Write tool cannot save config:
1. Print clear error: "Cannot write to ~/.claude-sauce.json. Check file permissions."
2. Guide user: "Try running: `chmod 644 ~/.claude-sauce.json`"
3. Do not attempt workarounds

### Missing URL Opener (Headless System)

If `open`/`xdg-open`/`start` commands fail:
1. Print the token generation URL as text
2. Tell user: "Please open this URL in your browser: [URL]"
3. Continue to credential collection step

## Configuration File Structure

### Expected Format

```json
{
  "jira": {
    "URL": "https://your-jira-instance.com",
    "API_TOKEN": "your-token-here"
  },
  "confluence": {
    "URL": "https://your-confluence-instance.com",
    "API_TOKEN": "your-token-here"
  },
  "jenkins": {
    "USER": "username",
    "TOKEN": "api-token-here"
  }
}
```

### Preservation Rules

When updating config:
- Always preserve existing services and keys
- Only add/update credentials for the service being setup
- Do not delete any existing config
- Maintain JSON formatting with 2-space indentation

## Example Workflow

**User runs:**
```bash
/jira search "assignee = me"
```

**Script outputs (to stderr):**
```
================================================================================
MISSING CREDENTIALS: JIRA
================================================================================

The jira integration requires credentials in ~/.claude-sauce.json

Required configuration keys:
  - URL: your-jira-instance-url
  - API_TOKEN: your-api-token-here

Token generation URL: https://ca-il-jira.il.cyber-ark.com:8443/plugins/servlet/de.resolution.apitokenauth/admin

================================================================================
```

**Claude detects pattern and:**

1. Announces: "I see you need Jira credentials. Let me help you set this up."

2. Offers to open URL:
   ```text
   I can open the token generation page for you:
   https://ca-il-jira.il.cyber-ark.com:8443/plugins/servlet/de.resolution.apitokenauth/admin

   Would you like me to open it?
   ```

3. Opens browser with `open "[URL]"` on macOS

4. Collects credentials:
   - "What's your Jira URL?"
   - "Please paste your Jira API token:"

5. Updates config file:
   ```json
   {
     "jira": {
       "URL": "https://ca-il-jira.il.cyber-ark.com:8443",
       "API_TOKEN": "[user_token_masked]"
     }
   }
   ```

6. Retries command:
   ```bash
   /jira search "assignee = me"
   ```

7. Success! Jira search returns results.

## Security Considerations

- Credentials are never echoed to stdout or bash history
- AskUserQuestion masks sensitive input automatically
- Config file is created with standard permissions
- Sensitive keys are protected in `~/.claude-sauce.json`
- No credentials stored in environment variables
- No credentials stored in temporary files

## Troubleshooting

### Config file keeps getting overwritten

Check if another process is updating `~/.claude-sauce.json`. Configuration should be merged, not replaced.

### "Cannot open browser" error on headless system

This is expected. The URL will be printed as text - user can copy/paste into browser manually.

### Credentials not saved after setup

Check:
1. File permissions on `~/.claude-sauce.json` (should be readable/writable)
2. Disk space available in home directory
3. Any file locking software that might block writes

### Script still fails after setup

Verify:
1. Credentials are correct by testing manually
2. Service URL is accessible (not firewall blocked)
3. API token hasn't expired
4. Required permissions exist for the account
