---
description: Show AWS Bedrock usage costs per user or organization on a given aws account (this relays on aws creds currently loaded on the user's bash/cmd profile)
---
# Bedrock Usage

## How to execute
1. Run the script using Bash tool
2. Capture stdout and stderr
3. Display the full output to the user verbatim (do not summarize or post-process)

### macOS/Linux
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/commands/scripts/bedrock_usage.py" $ARGUMENTS
```

### Windows
```cmd
python "%CLAUDE_PLUGIN_ROOT%\commands\scripts\bedrock_usage.py" %ARGUMENTS%
```

## Options
- `--days N` - Days to look back (default: 30)
- `--start-date YYYY-MM-DD` - Start date
- `--end-date YYYY-MM-DD` - End date
- `--all` - Show all users (default: current user only)
- `--user EMAIL` - Filter to specific user
- `--data-source {cost_explorer,price_list}` - Cost source (default: cost_explorer)
- `--json` - JSON output
- `--region REGION` - AWS region (default: us-east-1)
- `--profile PROFILE` - AWS profile

## Examples
```bash
# Current user, last 30 days
python3 bedrock_usage.py

# All users, last 7 days
python3 bedrock_usage.py --days 7 --all

# Date range
python3 bedrock_usage.py --start-date 2026-01-01 --end-date 2026-01-31 --all

# Specific user
python3 bedrock_usage.py --user john@example.com
```
