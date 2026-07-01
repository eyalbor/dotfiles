---
description: Check and update reference documentation for recent code changes. Use when syncing docs with code modifications, generating new documentation, tracing code flows from entry points, or auditing doc coverage.
---

# Update Reference Documentation

Ensure reference documentation stays in sync with code changes. Auto-discovers documentation structure and works across different projects.

## Workflow

### Step 1: Determine Scope

Use AskUserQuestion to ask:

**Question**: "How thorough should this documentation review be?"

**Options**:
1. **Quick** - Check only modified files, suggest minimal targeted updates
2. **Comprehensive** - Analyze related code paths, check for gaps, suggest thorough improvements

Store the choice for use throughout the workflow.

### Step 2: Gather Context

Use AskUserQuestion to understand what to check:

**Question**: "What code area should I review for documentation?"

**Options**:
1. **Recent changes** - Check uncommitted changes and recent commits
2. **Specific path** - Let me specify a directory or file
3. **Generate new** - Create documentation for an undocumented area
4. **Trace flow** - Document a feature by tracing from an entry point

If user selects "Specific path" or "Generate new", follow up to get the path.

If user selects "Trace flow", follow up to get the entry point (file path and function/method name).

### Step 3: Discover Documentation Structure

Use Glob to find where reference docs live:

```
Patterns to try:
- reference/**/*.md
- docs/**/*.md
- documentation/**/*.md
- doc/**/*.md
- *.md (root level)
```

Check for project-specific mappings:
- Use Read on `CLAUDE.md` - look for "Reference Documentation" or "Documentation Mappings" sections
- Use Read on `.reference-doc-mappings.yaml` or `.claude/reference-mappings.yaml` if they exist

**Mapping format** (if config exists):
```yaml
doc_directories:
  - reference/
  - docs/

mappings:
  - code: "src/api/"
    doc: "docs/API.md"
```

**Branch based on user's choice in Step 2:**
- If **Recent changes** → Continue to Step 4
- If **Specific path** or **Generate new** → Skip to Step 5
- If **Trace flow** → Skip to Step 4a

### Step 4: Identify Changed Code

For "Recent changes" scope, use Bash to get modified files:

```bash
# Detect main branch (main or master)
main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# Get current branch
current_branch=$(git branch --show-current)

# Get committed changes on this branch
if [ "$current_branch" = "$main_branch" ]; then
  # On main branch - show recent commits
  git diff --name-only HEAD~5..HEAD 2>/dev/null
else
  # On feature branch - show all commits compared to main
  git diff --name-only $(git merge-base $main_branch HEAD)..HEAD 2>/dev/null
fi

# Also get uncommitted changes (staged and unstaged)
git diff --name-only
git diff --name-only --cached
```

Group changes by directory/feature area.

### Step 4a: Trace Flow

For "Trace flow" scope, follow these sub-steps in order:

**4a.1** Get the entry point details from the user:
- File path (e.g., `src/api/auth.py`)
- Function/method name (e.g., `handle_login`)
- A name for this flow (e.g., "Authentication Flow", "Secret Rotation Flow")

**4a.2** Use AskUserQuestion to ask about external library handling:

**Question**: "How should I handle external libraries (code outside this project)?"

**Options**:
1. **Summarize only** - Note external library calls with a brief description of their purpose
2. **Explore deeply** - Trace into external library code when relevant to understand the full flow

**4a.3** Use the Agent tool with `subagent_type=Explore` to trace the flow:

Prompt the agent with (substitute `{placeholders}` with actual values):
```
Trace the complete code flow for "{flow_name}" starting from {file}:{function}.

Map out:
1. **Entry point** - The function signature, parameters, and purpose
2. **Direct calls** - Functions/methods called directly from the entry point
3. **Dependency chain** - Follow each call to understand the full execution path
4. **External interactions** - Database calls, API requests, file I/O, message queues
5. **Error handling** - How errors are caught, propagated, or transformed
6. **Side effects** - State changes, logging, metrics, events emitted
7. **Return flow** - What data flows back and how it's transformed

For each component discovered, note:
- File location
- Purpose/responsibility
- Key logic or business rules
- Configuration that affects behavior

Stop tracing when you reach:
- Standard library calls
- External service boundaries (note the interface)

External library handling: {summarize_only|explore_deeply}
- If "summarize_only": Note library calls with a brief description (e.g., "requests.post - HTTP POST to external API"), do not trace into internal implementation
- If "explore_deeply": Trace into external library code when it contains relevant business logic, skip standard library and low-level framework internals
```

**Compile the flow map** into a structured summary:
```
Entry Point: src/api/auth.py:handle_login

Flow:
1. handle_login(request) - Validates credentials, initiates auth flow
   ├── validators/credentials.py:validate_user_input - Input sanitization
   ├── services/auth_service.py:authenticate - Core auth logic
   │   ├── repositories/user_repo.py:find_by_email - DB lookup
   │   ├── utils/password.py:verify_hash - Password verification
   │   └── services/token_service.py:generate_tokens - JWT creation
   └── middleware/audit.py:log_auth_attempt - Audit logging

External interactions:
- PostgreSQL: User lookup, session storage
- Redis: Token caching, rate limiting

Side effects:
- Audit log entry created
- Login metrics incremented
- Session cookie set
```

Proceed to Step 5 with the traced components as the "code area".

### Step 5: Match Code to Documentation

For each changed code area, find relevant docs using:

1. **Explicit mapping** - Use config if found in Step 3
2. **Name matching** - Use Glob to find docs with similar names:
   - `logic/authentication/` -> `*auth*.md`, `*authentication*.md`
3. **Content search** - Use Grep to find docs referencing the changed paths

### Step 6: Understand the Feature

**Before suggesting any documentation changes, thoroughly understand the code:**

- Use Read to examine all relevant source files (not just the diff)
- Trace the code flow: entry points, dependencies, side effects
- Understand the *why* behind the implementation, not just the *what*
- If the feature interacts with other components, read those too
- Look for edge cases, error handling, and configuration options

**If Comprehensive mode**: Use the Agent tool with `subagent_type=Explore` to deeply analyze the code area and its dependencies.

**If anything is unclear**, ask the user for clarification before proceeding. Never document what you don't fully understand.

### Step 7: Present Findings

**If matching doc(s) found:**
- Use Read on the existing doc
- Compare your understanding of the code against what the doc describes
- Identify sections needing updates
- Present summary:

```
Found relevant documentation for your changes:

Code Area: logic/authentication/
Documentation: reference/AUTH_FLOW.md

Sections that may need updating:
- "## Login Flow" - you modified login_handler.py
- "## Token Validation" - you added new validation logic
```

**If flow trace (Step 4a)**, present a terminal summary:

```
Flow traced: src/api/auth.py:handle_login

Summary: Handles user authentication by validating credentials against the
database and generating JWT tokens for session management.

Components found: 6
  - validators/credentials.py
  - services/auth_service.py
  - repositories/user_repo.py
  - utils/password.py
  - services/token_service.py
  ... and 1 more

External dependencies: PostgreSQL, Redis
Documentation: docs/AUTH_FLOW.md (will be created)
```

The summary should be 1-2 sentences explaining what the flow accomplishes from a user/business perspective. Show only the first 5 components if there are 5 or more.

**If Comprehensive mode**, also check:
- Are there code paths not covered in the doc?
- Are examples/diagrams still accurate?
- Use Grep to find broken internal doc links

**If NO matching doc found**, use AskUserQuestion:

**Question**: "No documentation found for code area: {area}. What would you like to do?"

**Options**:
1. **Provide path** - Specify path to existing documentation
2. **Generate new** - Create new reference documentation
3. **Skip** - No documentation needed for this change

### Step 8: Update or Generate Documentation

Only proceed once you have a solid understanding of the feature from Step 6.

**Updating existing doc:**
- Suggest specific edits with before/after snippets based on your understanding
- Explain *why* each change is needed
- Confirm with user before applying Edit

**Generating new doc:**
- Use Read on existing docs to match project style
- Use template from [references/doc-template.md](references/doc-template.md)
- Write documentation that captures your understanding: Overview, Architecture, Components, Flow, Usage
- Focus on the *why* and *how*, not just listing functions
- Ask user to confirm filename and location before Write

**Generating doc from flow trace (Step 4a):**
- Use template from [references/doc-template.md](references/doc-template.md)
- Use the flow map as the documentation skeleton
- Structure the doc to follow the execution path
- Include:
  - **Overview** - What the flow accomplishes and when it's triggered
  - **Flow diagram** - ASCII or Mermaid diagram of the traced flow
  - **Components** - Each component's responsibility and key logic
  - **Data flow** - What data enters, transforms, and exits
  - **External dependencies** - Services, databases, APIs involved
  - **Error scenarios** - What can fail and how it's handled
  - **Configuration** - Settings that affect the flow behavior

## Setup for Your Project (Optional)

To add explicit mappings, create `.reference-doc-mappings.yaml` in project root:

```yaml
doc_directories:
  - reference/
  - docs/

mappings:
  - code: "src/api/"
    doc: "docs/API.md"
  - code: "src/auth/"
    doc: "docs/AUTHENTICATION.md"
```

This is optional - the command auto-discovers docs without configuration.
