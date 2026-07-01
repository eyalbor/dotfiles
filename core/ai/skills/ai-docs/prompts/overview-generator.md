# Overview Generator Prompt

You are analyzing the codebase in this repository: {repo_path}

## Goal

- Infer the product idea, key business flows, and who invokes the service (end users / microservices) from the repository structure, code, tests, and configuration.
- Return a concise Markdown overview only, suitable as an approved high-level framing for later architecture documentation.

## CRITICAL OUTPUT REQUIREMENTS

- Your response MUST start IMMEDIATELY with the heading '### Product Idea'
- DO NOT include any preamble, analysis text, or commentary before the markdown sections
- DO NOT include phrases like 'I'll analyze...', 'Now I have enough information...', 'Let me create...'
- DO NOT duplicate sections or content
- The FIRST line of your output must be: ### Product Idea

## Output Format (Markdown)

### Product Idea

<1–3 short paragraphs>

### Key Business Flows

- At least 3 flows.
- Each flow: a bold name and 1–3 bullet points describing what happens and why it matters.

### Who Invokes the Service (End Users / Microservices)

- Describe which human users and/or microservices call this service, and for what purpose.

## Constraints

- Do not generate any architecture diagrams or low-level details yet.
- Do not ask questions; make reasonable assumptions.
- Return only Markdown, no JSON, no extra commentary.
- Start your response directly with '### Product Idea' - nothing before it.
