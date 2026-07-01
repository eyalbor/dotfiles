![Claude Sauce Logo](docs/spicey_logo.jpeg)

A collection of Claude Code **skills** and **commands** for <ORG> that extend Claude's capabilities with specialized knowledge, workflows, and integrations.

## Skills vs Commands

This project contains two types of extensions:

| Type | Purpose | Trigger | Location |
|------|---------|---------|----------|
| **Skills** | Provide domain expertise, workflows, and tool integrations | Automatically triggered based on context | `skills/` |
| **Commands** | User-invocable actions via slash commands (e.g., `/bedrock-usage`) | Explicitly invoked by user | `commands/` |

### Skills

Skills are modular packages that provide Claude with:
- Specialized workflows for specific domains
- Tool integrations and scripts
- Domain expertise and company-specific knowledge
- Bundled resources for complex tasks

Skills are triggered automatically when Claude detects relevant context.

### Commands

Commands are user-invocable actions that:
- Execute specific tasks on demand
- Are triggered via slash commands (e.g., `/bedrock-usage`)
- Provide focused functionality for common operations

## Configuration

Most plugins require external service credentials stored in `~/.claude-sauce.json`. When you first use a plugin that needs credentials, Claude will automatically guide you through setup via the credential-setup skill.

### Plugins and Configuration

| Plugin            | Needs Setup | Configuration | Documentation                                                               |
|-------------------|-------------|---------------|-----------------------------------------------------------------------------|
| atlassian   | Yes | `~/.claude-sauce.json` (Jira + Confluence) | [Setup Guide](plugins/atlassian/README.md)                            |
| jenkins           | Yes | `~/.claude-sauce.json` | [Setup Guide](plugins/jenkins/README.md)                                    |
| codacy            | Yes | `~/.claude-sauce.json` (Codacy + GitHub) | [Setup Guide](plugins/codacy/README.md)                                     |
| github-enterprise | Yes | `gh` CLI authentication | [Setup Guide](plugins/github-enterprise/README.md)                          |
| bedrock-usage     | Yes | AWS credentials (environment/config) | [Usage Guide](plugins/bedrock-usage/README.md)                              |
| code-assist       | Optional | `gh` CLI + pr-review-toolkit plugin | [Usage Guide](plugins/code-assist/README.md)                                |
| test-manager      | No | - | -                                                                           |
| prompt-boost      | No | - | -                                                                           |
| sauce-statusline  | No | - | -                                                                           |
| reference-manager | No | - | - |

### Automated Credential Setup

Plugins using `~/.claude-sauce.json` (atlassian, jenkins, codacy) support automated credential setup:

1. Use the plugin command (e.g., `/jira search "PROJ-123"`)
2. Claude detects missing credentials and offers to help
3. Opens token generation page in your browser (when available)
4. Collects credentials securely via masked input
5. Saves to `~/.claude-sauce.json` automatically
6. Retries your command

For detailed setup instructions, see each plugin's README linked above.

## How to install locally?

### Option 1: Clone and Add Locally

1. Clone the project locally
2. From the Claude Sauce folder, run the following in Claude to add the plugin:

   ```text
   /plugins marketplace add ./
   ```

The plugin will read `.claude-plugin/marketplace.json` file and will load it as a consumable skill/command set.

### Option 2: Install via SSH (Git URL)

You can install directly using the SSH Git URL:

```text
/plugins marketplace add git@<GITHUB_HOST>:<ORG>/claude-sauce.git
```

**Prerequisites - SSH Key Setup:**

1. Generate an SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Copy the public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. Add the public key (`.pub` file contents) to your GitHub account:
   - Go to <https://<GITHUB_HOST>/settings/keys> → New SSH key
   - Paste the public key and save

## Cursor IDE Support

Install skills directly into your Cursor project - no need to clone the repository!

### Quick Install

**Important:** Run this command from your project root directory (where your `.cursor` folder is located).

```bash
cd /path/to/your/project

npx -y tiged --disable-cache --force git@<GITHUB_HOST>:<ORG>/claude-sauce.git/scripts temp-skills-scripts && \
python3 temp-skills-scripts/sync-to-cursor.py && \
rm -rf temp-skills-scripts/sync-to-cursor.py
```

The script will:
1. Download the scripts directory to `temp-skills-scripts/`
2. Show you all available skills/commands
3. Let you choose which ones to install
4. If existing items are found, prompt you to clean them up (or use `--force` to auto-clean)
5. Copy them to `.cursor/skills/<ORG>/` or `.cursor/commands/` in your project
6. Clean up the temporary `temp-skills-scripts/` directory automatically

### What Gets Installed?

Skills are installed to `.cursor/skills/<ORG>/` in your project (namespaced to avoid conflicts):

```
.cursor/skills/
└── <ORG>/
    ├── jira/
    │   ├── SKILL.md
    │   ├── scripts/
    │   └── references/
    ├── confluence/
    │   ├── SKILL.md
    │   └── scripts/
    └── ... (other skills)
```

### Options

**Install all skills automatically:**
```bash
npx -y tiged --disable-cache --force git@<GITHUB_HOST>:<ORG>/claude-sauce.git/scripts temp-skills-scripts && \
python3 temp-skills-scripts/sync-to-cursor.py --all && \
rm -rf temp-skills-scripts
```

**Sync commands instead of skills:**
```bash
npx -y tiged --disable-cache --force git@<GITHUB_HOST>:<ORG>/claude-sauce.git/scripts temp-skills-scripts && \
python3 temp-skills-scripts/sync-to-cursor.py --commands && \
rm -rf temp-skills-scripts
```

**Sync both skills and commands:**
```bash
npx -y tiged --disable-cache --force git@<GITHUB_HOST>:<ORG>/claude-sauce.git/scripts temp-skills-scripts && \
python3 temp-skills-scripts/sync-to-cursor.py --skills --commands && \
rm -rf temp-skills-scripts
```

**Auto-overwrite existing skills/commands (no prompt):**
```bash
npx -y tiged --disable-cache --force git@<GITHUB_HOST>:<ORG>/claude-sauce.git/scripts temp-skills-scripts && \
python3 temp-skills-scripts/sync-to-cursor.py --force && \
rm -rf temp-skills-scripts
```

**Note:** Without `--force`, the script will prompt you before cleaning up existing items. With `--force`, it automatically cleans all existing items without asking.

**Use a custom repository:**
```bash
python3 sync-to-cursor.py --git-url git@<GITHUB_HOST>:<ORG>/claude-sauce.git
```

**Preview changes first:**
```bash
python3 sync-to-cursor.py --dry-run
```

### Interactive Behavior

When existing skills or commands are detected:

- **Without `--force`**: The script will show a warning listing existing items and prompt you: "Delete all existing items in <ORG> directory? [y/N]"
  - Answer `y` to clean up and proceed with installation
  - Answer `n` (or press Enter) to skip existing items

- **With `--force`**: The script automatically cleans all existing items without prompting

### Requirements

- Python 3
- Git (for cloning the repository)
- Cursor IDE (skills are automatically detected)

That's it! Once installed, Cursor will automatically use the skills when relevant.

## Adding a New Plugin

To contribute a new plugin to claude-sauce, follow these steps:

### 1. Create the Plugin Directory Structure

```
plugins/<your-plugin-name>/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata (required)
└── skills/
    └── <skill-name>/
        ├── SKILL.md          # Skill definition (required)
        ├── scripts/          # Python/Bash scripts (optional)
        └── references/       # Documentation files (optional)
```

> **Note:** Plugins can also include `commands/` for user-invocable slash commands. See [plugins/bedrock-usage/commands/](plugins/bedrock-usage/commands/) for an example.

### 2. Create Plugin Metadata

Create `.claude-plugin/plugin.json` with your plugin's metadata:

```json
{
  "name": "your-plugin-name",
  "description": "Brief description of what your plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "<AUTHOR_EMAIL>"
  }
}
```

### 3. Create the Skill Definition

Use the template at [templates/SKILL.md](templates/SKILL.md) to create your `SKILL.md` file. The YAML frontmatter with `name` and `description` is critical for Claude to determine when to trigger your skill.

### 4. Register in Root plugin.json

Add your plugin to the `plugins` array in [.claude-plugin/plugin.json](.claude-plugin/plugin.json):

```json
{
  "name": "your-plugin-name",
  "description": "Brief description of your plugin",
  "source": "./plugins/your-plugin-name",
  "strict": false
}
```

### References

- **Skill Template:** [templates/SKILL.md](templates/SKILL.md)
- **Contribution Workflow:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Skills & Commands Guide:** [CLAUDE.md](CLAUDE.md)
- **Official Specification:** https://agentskills.io/specification
- **Example Plugins:** [plugins/jenkins](plugins/jenkins), [plugins/codacy](plugins/codacy)

## Improving Skills Execution (Optional)

For more reliable skill activation, you can set up a hook that forces Claude to explicitly evaluate available skills before each prompt.

### Setup

1. **Copy the hook script** from this project to `.claude/hooks/` in your project (or globally to `~/.claude/hooks/`):

```bash
cp skill-forced-eval-hook.sh .claude/hooks/
chmod +x .claude/hooks/skill-forced-eval-hook.sh
```

> **Note:** When configuring the hook path in settings.json, use the full absolute path (e.g., `/Users/username/.claude/hooks/`) instead of `~/`. Claude does not expand the `~` shortcut.

2. **Add to `.claude/settings.json`**:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/skill-forced-eval-hook.sh"
          }
        ]
      }
    ]
  }
}
```

## Project Structure

```
claude-sauce/
├── .claude-plugin/      # Root plugin metadata
│   └── marketplace.json
├── plugins/             # Claude plugin structure
│   ├── atlassian/
│   │   └── skills/
│   │       ├── jira/
│   │       │   ├── SKILL.md      # Source of truth
│   │       │   ├── scripts/
│   │       │   └── references/
│   │       └── confluence/
│   └── ... (other plugins)
├── scripts/
│   └── sync-to-cursor.py  # Sync script for Cursor IDE installation
├── templates/           # Templates for creating new skills
│   └── SKILL.md         # Skill template structure
├── CLAUDE.md            # Guide for creating skills and commands
└── CONTRIBUTING.md      # Contribution guidelines
```

## Getting Started

See [CLAUDE.md](./CLAUDE.md) for a comprehensive guide on creating skills and commands.

### Quick Reference - Creating Skills

1. **Understand** the skill with concrete examples
2. **Plan** reusable skill contents (scripts, references, assets)
3. **Initialize** the skill structure
4. **Edit** the skill and implement resources
5. **Package** the skill for distribution
6. **Iterate** based on real usage

## Official Specification

The complete skill specification is available at: https://agentskills.io/specification

### Plugin Updates Not Reflecting

When updating skills or commands, changes may not take effect due to cached plugin data. To force a refresh:

1. Remove the plugin cache:
   ```bash
   rm -rf ~/.claude/plugins/cache
   ```

2. Remove the plugin from Claude:
   ```bash
   /plugins remove claude-sauce
   ```

3. Re-add the plugin:
   ```bash
   /plugins add /path/to/claude-sauce
   ```
