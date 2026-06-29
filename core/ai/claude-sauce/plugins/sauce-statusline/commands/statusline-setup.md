---
description: Install the Claude Code custom statusline that shows model, cost, tokens, context usage, and git branch
allowed-tools: ["Bash", "Read"]
---
# Statusline Setup

Install a custom statusline for Claude Code that displays real-time session metrics.

## How to execute

Run these steps in order using the Bash tool:

### 1. Install jq (if missing)
```bash
command -v jq || brew install jq
```

### 2. Copy the statusline script
```bash
cp "${CLAUDE_PLUGIN_ROOT}/commands/scripts/statusline.sh" ~/.claude/statusline.sh && chmod +x ~/.claude/statusline.sh
```

### 3. Update settings.json
Use the `statusline-setup` agent to add the following to `~/.claude/settings.json`:
```json
{
	"statusLine": {
		"type": "command",
		"command": "~/.claude/statusline.sh"
	}
}
```

## User output
After successful installation, inform the user to restart Claude Code to see the new statusline.
