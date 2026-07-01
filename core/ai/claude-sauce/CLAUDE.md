# Skills & Commands Creator Guide

**Name:** skill-command-creator
**Description:** Guide for creating effective skills and commands. Use this when users want to create or update a skill (auto-triggered domain expertise) or a command (user-invocable slash command).
**License:** Complete terms in LICENSE.txt

---

## Configuration Management

**CRITICAL:** All credentials and tokens for Claude Sauce plugins MUST be stored in `~/.claude-sauce.json`. This is the **single source of truth** for all configuration.

### Configuration Rules

1. **Only use `~/.claude-sauce.json`** for configuration - no environment variables, no other files
2. **Never implement fallback mechanisms** to other config sources

**When creating new skills/commands that require credentials:**
- Read from `~/.claude-sauce.json` exclusively
- Never add fallback logic


## Skills vs Commands - Ask Before Creating

**IMPORTANT:** If a user asks to "create something" or "add a new feature" without explicitly using the words "skill", "skills", "command", or "commands", **always ask which type they want to create**:

| Type | Purpose | When to Use |
|------|---------|-------------|
| **Skill** | Domain expertise, workflows, tool integrations | Auto-triggered based on context (e.g., Jira, Confluence) |
| **Command** | User-invocable action via `/command-name` | Explicit user action (e.g., `/bedrock-usage`) |

**Decision guidance:**
- If the user says "skill" or "skills" → Create a skill in `skills/`
- If the user says "command" or "commands" → Create a command in `commands/`
- If unclear → Ask: "Would you like me to create a **skill** (auto-triggered based on context) or a **command** (user-invocable via slash command)?"

---

## Official Specification

The complete and authoritative skill specification is available at: **https://agentskills.io/specification**

Refer to this specification when you need detailed information about:
- Skill file format requirements
- Metadata standards
- Directory structure specifications
- Validation rules
- Packaging requirements

---

## About Commands

Commands are user-invocable actions triggered via slash commands (e.g., `/bedrock-usage`). They:
- Execute specific tasks on demand
- Are stored in `commands/<command-name>/`
- Contain a markdown file with YAML frontmatter (`description`) and instructions
- Can include embedded scripts or reference external scripts

### Command Structure

```
commands/
└── my-command/
    └── my-command.md    # Command definition with YAML frontmatter
```

### Command File Format

```markdown
---
description: Brief description of what the command does
---
# Command Name

Instructions for Claude on how to execute this command.

## Behavior
1. Step-by-step instructions
2. ...

## How to execute
```bash
command to run
```
```

---

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks—they transform Claude from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

- **Specialized workflows** - Multi-step procedures for specific domains
- **Tool integrations** - Instructions for working with specific file formats or APIs
- **Domain expertise** - Company-specific knowledge, schemas, business logic
- **Bundled resources** - Scripts, references, and assets for complex and repetitive tasks

---

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption:** Claude is already very smart. Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

- **High freedom (text-based instructions):** Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

- **Medium freedom (pseudocode or scripts with parameters):** Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

- **Low freedom (specific scripts, few parameters):** Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

---

## Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter (YAML):** Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body (Markdown):** Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

### Bundled Resources (optional)

#### Scripts (scripts/)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include:** When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example:** `scripts/format_json.py` for JSON formatting and validation tasks
- **Benefits:** Token efficient, deterministic, may be executed without loading into context
- **Note:** Scripts may still need to be read by Claude for patching or environment-specific adjustments

#### References (references/)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include:** For documentation that Claude should reference while working
- **Examples:** `references/schema-standards.md` for JSON Schema specifications, `references/transforms.md` for transformation patterns, `references/jsonpath-guide.md` for JSONPath syntax
- **Use cases:** Schema specifications, transformation patterns, query syntax guides, formatting rules, validation approaches
- **Benefits:** Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice:** If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication:** Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

#### Assets (assets/)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include:** When the skill needs files that will be used in the final output
- **Examples:** `assets/transform-templates/` for JSON transformation configs, `assets/schema-templates/` for common JSON schemas, `assets/sample-data/` for example JSON files
- **Use cases:** Configuration templates, schema templates, example data files, boilerplate structures that get copied or modified
- **Benefits:** Separates output resources from documentation, enables Claude to use files without loading them into context

### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

---

## Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

#### Pattern 1: High-level guide with references

```markdown
# JSON Formatter

## Quick start

Format JSON using the `scripts/format_json.py` script:
[code example]

## Advanced features

- **Schema validation**: See [VALIDATION.md](VALIDATION.md) for complete guide
- **Transformation rules**: See [TRANSFORMS.md](TRANSFORMS.md) for all transformation patterns
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common formatting scenarios
```

Claude loads VALIDATION.md, TRANSFORMS.md, or EXAMPLES.md only when needed.

#### Pattern 2: Domain-specific organization

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Claude only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Claude only reads aws.md.

#### Pattern 3: Conditional details

Show basic content, link to advanced content:

```markdown
# JSON Formatter

## Basic formatting

Use the `scripts/format_json.py` script for standard formatting with proper indentation.

## Advanced operations

For complex transformations, use the transformation engine.

**For schema validation**: See [VALIDATION.md](VALIDATION.md)
**For custom formatters**: See [CUSTOM_FORMATTERS.md](CUSTOM_FORMATTERS.md)
**For JSON Path queries**: See [JSONPATH.md](JSONPATH.md)
```

Claude reads VALIDATION.md, CUSTOM_FORMATTERS.md, or JSONPATH.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.

---

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Package the skill (run package_skill.py)
6. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

**For example**, when building a JSON formatter skill, relevant questions include:

- "What functionality should the JSON formatter skill support? Formatting, validation, transformation, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Format this JSON file' or 'Validate this JSON against a schema' or 'Minify this JSON'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

**Conclude this step** when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

**Example:** When building a JSON formatter skill to handle queries like "Format this JSON file with proper indentation," the analysis shows:
- Formatting JSON requires re-writing the same formatting code each time
- A `scripts/format_json.py` script would be helpful to store in the skill

**Example:** When handling queries like "Validate this JSON against a schema," the analysis shows:
- JSON schema validation requires understanding various schema standards (JSON Schema Draft 7, Draft 2020-12, etc.)
- A `references/schema-standards.md` file documenting different schema validation approaches would be helpful to store in the skill

**Example:** When handling queries like "Transform this JSON using these rules," the analysis shows:
- Common transformation patterns (flattening, nesting, renaming keys) are repeatedly needed
- An `assets/transform-templates/` directory containing template transformation configs would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

**Usage:**

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, customize or remove the generated SKILL.md and example files as needed.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes:** See `references/workflows.md` for sequential workflows and conditional logic
- **Specific output formats or quality standards:** See `references/output-patterns.md` for template and example patterns

These files contain established best practices for effective skill design.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a JSON formatter skill, the user may need to provide custom schema templates to store in `assets/schema-templates/`, or transformation pattern documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- **name:** The skill name
- **description:** This is the primary triggering mechanism for your skill, and helps Claude understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Claude.
  - **Example description for a JSON formatter skill:** "Comprehensive JSON formatting, validation, and transformation tool with support for pretty-printing, minification, schema validation, and structural transformations. Use when Claude needs to work with JSON data for: (1) Formatting or beautifying JSON, (2) Validating JSON against schemas, (3) Minifying JSON, (4) Transforming JSON structure, or any other JSON manipulation tasks"

Do not include any other fields in YAML frontmatter.

##### Body

Write instructions for using the skill and its bundled resources.

### Step 5: Packaging a Skill

Once development of the skill is complete, it must be packaged into a distributable `.skill` file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate the skill automatically**, checking:
   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package the skill** if validation passes, creating a `.skill` file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The `.skill` file is a zip file with a `.skill` extension.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

### Step 6: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

---

## Example: Creating a SKILL.md

Here's what a properly structured SKILL.md looks like for a JSON formatter skill:

```markdown
---
name: json-formatter
description: Comprehensive JSON formatting, validation, and transformation tool with support for pretty-printing, minification, schema validation, and structural transformations. Use when Claude needs to work with JSON data for: (1) Formatting or beautifying JSON, (2) Validating JSON against schemas, (3) Minifying JSON, (4) Transforming JSON structure, or any other JSON manipulation tasks.
---

# JSON Formatter

## Quick Start

### Format JSON

Use the `scripts/format_json.py` script for basic formatting:

```bash
python scripts/format_json.py --input data.json --indent 2
```

Options:
- `--indent N`: Set indentation level (default: 2)
- `--sort-keys`: Sort object keys alphabetically
- `--minify`: Minify JSON (remove whitespace)

### Validate JSON

Validate JSON against a schema:

```bash
python scripts/validate_json.py --input data.json --schema schema.json
```

## Advanced Operations

### Schema Validation

For detailed information on different schema standards and validation approaches, see [references/schema-standards.md](references/schema-standards.md).

### JSON Transformations

For common transformation patterns (flattening, nesting, key renaming), see [references/transforms.md](references/transforms.md).

### JSONPath Queries

For querying and extracting data from JSON using JSONPath, see [references/jsonpath-guide.md](references/jsonpath-guide.md).
```

---

## Next Steps

Now that you understand how to create skills, you're ready to build your first skill! Start by following the 6-step process outlined above, beginning with understanding the concrete use cases for your skill.
