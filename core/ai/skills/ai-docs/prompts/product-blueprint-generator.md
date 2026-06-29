---
description: 'Product-level architecture blueprint generator that synthesizes documentation from multiple microservices to create a unified product architecture document. Analyzes inter-service relationships, end-to-end business flows, and system topology.'
mode: 'agent'
---

# Product-Level Architecture Blueprint Generator

## Generated Prompt

"Create a comprehensive PRODUCT-LEVEL architecture documentation suite that synthesizes the architectural patterns and relationships across all microservices. The output must consist of FOUR types of documents:

1. **index.md** — Elegant homepage / landing page for the documentation site
2. **Product_Architecture_Blueprint.md** — The main architecture document
3. **Microservices_Relationships.md** — Visual guide to inter-service interactions
4. **flows/*.md** — One file per end-to-end business flow that spans multiple services

IMPORTANT: This is a PRODUCT-LEVEL documentation suite. Your focus is on:
- How microservices interact with each other as a unified system
- End-to-end business flows that span multiple services
- The overall system topology, communication patterns, and data architecture
- Shared infrastructure and cross-cutting concerns

You must NOT document individual service internals — only their roles, interfaces, and relationships.

---

## STYLE AND QUALITY REQUIREMENTS

Apply these rules consistently across ALL generated documents:

1. **MkDocs Material Admonitions**: Use `!!!` admonitions liberally for callouts:
   - `!!! abstract \"Flow at a Glance\"` for flow summaries
   - `!!! info \"Why ...\"` for architectural rationale
   - `!!! tip \"...\"` for actionable guidance
   - `!!! warning \"...\"` for destructive operations or important caveats
   - `!!! success \"Core Capabilities\"` for feature highlights
   - `!!! note \"Decision Record\"` for ADRs

2. **Diagrams**:
   - Every Mermaid diagram MUST be followed by a **Legend** table explaining colors and arrow types
   - **Legend color format**: Do NOT show raw hex codes like `#1565C0` in legend tables. Instead,
     render the color name text in the actual color using an inline HTML span. Example:

     | Element | Meaning |
     |---------|---------|
     | <span style="color:#1565C0">**&#9632; Dark blue**</span> | Hub service (Session Data) |
     | <span style="color:#4A90E2">**&#9632; Blue**</span> | Core microservices |
     | <span style="color:#7ED321">**&#9632; Green**</span> | External actors / sources |
     | <span style="color:#F5A623">**&#9632; Orange**</span> | External dependent services |
     | <span style="color:#BD10E0">**&#9632; Purple**</span> | Messaging infrastructure |
     | <span style="color:#50E3C2">**&#9632; Teal**</span> | Databases / storage |
     | <span style="color:#D0021B">**&#9632; Red**</span> | Error / DLQ / critical |
     | Solid arrow `-->` | Direct invocation / data flow |
     | Dashed arrow `-.->` | Dependency / discovery |

     Use &#9632; (filled square) before the color name as a swatch. The table should have only
     two columns: **Element** and **Meaning** (no separate "Color" column with hex values).
   - Use `rect rgb(...)` blocks in sequence diagrams to group phases visually
   - Use `subgraph` in flowcharts to group related services
   - Use `par` blocks in sequence diagrams for parallel operations
   - Use `alt`/`else` blocks for conditional branching

3. **Tables over Paragraphs**: Present structured data as tables whenever possible:
   - Service inventories, communication matrices, operations matrices
   - Error handling scenarios, performance targets, configuration references

4. **Cross-References**: Every flow document must:
   - Link back to the main Product_Architecture_Blueprint.md
   - Link to related flows in a \"Related Flows\" table at the bottom
   - Link to Microservices_Relationships.md where relevant

5. **Consistent Terminology**: Use the exact service names from the approved overviews throughout.

6. **Scannable Structure**: Use short paragraphs, bullet lists starting with strong verbs/nouns, and clear heading hierarchy.

---

## C4 DIAGRAM STYLING RULES (MANDATORY)

**CRITICAL: Use Standard Flowchart Syntax — NOT C4 Extension Syntax**

FORBIDDEN — NEVER use these Mermaid C4 keywords:
- C4Context, C4Container, C4Component, C4Dynamic, C4Deployment
- Person, Person_Ext, System, System_Ext, SystemDb, SystemQueue
- Container, Container_Boundary, ContainerDb, ContainerQueue
- Rel, Rel_U, Rel_D, Rel_L, Rel_R, BiRel

REQUIRED: Always use standard Mermaid `graph` / `flowchart` syntax with inline `style` directives.

**Color Palette:**
- **Blue** (core microservices): `fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff`
- **Dark Blue** (hub service): `fill:#1565C0,stroke:#0D47A1,stroke-width:3px,color:#fff`
- **Green** (external actors/sources): `fill:#7ED321,stroke:#5FA019,stroke-width:2px,color:#000`
- **Orange** (external dependent services): `fill:#F5A623,stroke:#C4841D,stroke-width:2px`
- **Purple** (messaging/infrastructure): `fill:#BD10E0,stroke:#9012B0,stroke-width:2px,color:#fff`
- **Teal** (databases/storage): `fill:#50E3C2,stroke:#3AB09E,stroke-width:2px`
- **Red** (error handling/DLQ): `fill:#D0021B,stroke:#A00116,stroke-width:2px,color:#fff`

**Subgraph fill colors (for grouping):**
- `fill:#e3f2fd,stroke:#1565c0,stroke-width:2px` (blue tint)
- `fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px` (green tint)
- `fill:#fff3e0,stroke:#e65100,stroke-width:2px` (orange tint)
- `fill:#fce4ec,stroke:#c62828,stroke-width:2px` (red tint)
- `fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px` (purple tint)

**Arrow Styles:**
- Solid `-->` for direct invocations and main data flow
- Dashed `-.->` for dependency/discovery usage
- Edge labels `|\"label\"|` should be concise action phrases
- In diagrams with `<-->`, use for bidirectional REST

**Node Labels:**
- Use `<b>Service Name</b><br/><i>Brief role description</i>` for rich labels
- Keep to 2 lines maximum
- NO stereotype labels like <<system>>, [CONTAINER]

---

## DOCUMENT 0: index.md (Homepage)

This is the landing page for the GitHub Pages documentation site. It MUST feel polished and
visually appealing, using the custom CSS classes available in the theme.

**Required structure:**

1. **Hero Banner** — wrapped in `<div class="hero-banner" markdown>`:
   - `# <Product Name>` as the title
   - A one-line tagline describing the product's value proposition
   - `<p class="hero-subtitle">N Microservices &bull; <Architecture Pattern> &bull; <Key Traits></p>`

2. **Stat Pills** — wrapped in `<div class="stat-row">`:
   - 3-5 `<span class="stat-pill">` elements with key metrics (microservice count, flow count, protocols, infrastructure)
   - Example: `<span class="stat-pill"><strong>6</strong> Microservices</span>`

3. **Platform at a Glance** — `## Platform at a Glance`:
   - One paragraph summarizing the product's purpose and positioning
   - A `graph TB` Mermaid diagram showing the high-level system architecture:
     - Group nodes into subgraphs (External Actors, Core Services, Supporting Services, Infrastructure)
     - Use the C4 color palette from the styling rules
     - Use rich labels: `<b>Service Name</b><br/>Brief role`

4. **Key Capabilities** — `## Key Capabilities`:
   - Wrapped in `<div class="card-grid" markdown>`
   - 4-6 capability cards, each as `<div class="card" markdown>` containing:
     - `<span class="card-icon">EMOJI</span>`
     - `<span class="card-title">Capability Name</span>`
     - `<p class="card-desc">One-sentence description.</p>`

5. **Documentation Guide** — `## Documentation Guide`:
   - Wrapped in `<div class="card-grid" markdown>`
   - Two link cards for Architecture Blueprint and Microservices Relationships
   - Each wraps the content in `<a href=".../">` (note trailing slash for MkDocs)

6. **Business Flows** — `### Business Flows`:
   - Wrapped in `<div class="card-grid" markdown>`
   - One card per flow document with `<a href="flows/<flow-name>/">`
   - Each card title includes a flow badge: `<span class="flow-badge flow-badge--TYPE">LABEL</span>`
   - Badge types: `--sync`, `--async`, `--event`, `--critical`

7. **Lifecycle Overview** — an optional section with a `graph LR` Mermaid diagram showing the
   high-level lifecycle/journey through the platform (3 phases as subgraphs with colored nodes)

8. **Footer** — a technology stack blockquote and generation attribution:
   - `<div class="section-divider"><span>Built on ...</span></div>`
   - `> **Technology Stack**: ...`
   - Italicized attribution linking to the Architecture Blueprint

**Formatting rules:**
- Use `---` horizontal rules between major sections
- All `<div>` tags with markdown content MUST include the `markdown` attribute
- Links to other docs use trailing slash: `Product_Architecture_Blueprint/` not `.md`
- The page must render beautifully with MkDocs Material theme + the provided CSS

---

## DOCUMENT 1: Product_Architecture_Blueprint.md

Start with:
```
# Architecture Blueprint
```

Then a one-paragraph executive summary of the product (what it does, how many microservices, key value).

Then `## Blueprint Metadata` as a table:

| Parameter | Value |
|-----------|-------|
| Generation Timestamp | [exact value from prompt] |
| Agent | cursor-agent |
| LLM | [exact value from prompt] |
| Product Type | Microservices Platform |
| Architecture Pattern | [detected pattern, e.g., Event-Driven Serverless] |
| Microservices Count | [count] |

Then `## Table of Contents` with numbered links to all sections (1-12).

### Section Structure:

#### 1. Product Overview and Business Context
- Executive Summary paragraph
- Key Value Propositions (use `!!! success \"Core Capabilities\"` admonition with bullet list)
- Primary User Personas table (| Persona | Role | Primary Interactions |)
- Business Domain Context (regulatory, compliance, architectural context)

#### 2. Microservices Inventory
- Summary table: | Service Name | Purpose | Key Responsibilities | Primary Interfaces |
- Service Roles Diagram: A `graph TB` showing all services with subgroups (User Layer, Frontend, Core Services, Supporting Services, External Systems)

#### 3. System Topology Visualization
- **3.1 Context Diagram**: Product boundary with all external actors and internal services
- **3.2 Container Diagram**: All compute, messaging, data, and discovery tiers with subgraphs
- Each diagram followed by a Legend table

#### 4. Inter-Service Communication Patterns
- **4.1 Synchronous Communication**: Table with Source, Target, Protocol, Authentication, Purpose
- **4.2 Asynchronous Communication**: Table with Publisher, Topic/Queue, Subscribers, Event Types
- **4.3 Service Discovery**: Table and `!!! info` admonition explaining why
- **4.4 Communication Matrix**: A `graph LR` showing all REST connections between services

#### 5. End-to-End Business Flows
- Flow Summary table: | Flow Name | Services Involved | Entry Point | Document |
- Flow Overview Diagram: A `graph LR` showing flow phases as subgraphs

#### 6. Data Architecture Across Services
- **6.1 Data Ownership**: Table with Domain Entity, Owner, Storage, Consumers
- **6.2 Data Flow Patterns**: Diagram showing ingestion, risk propagation, query paths
- **6.3 Multi-Tenancy Data Isolation**: Table per service with isolation strategy + `!!! warning` admonition
- **6.4 Data Retention**: Table with retention policies

#### 7. Shared Infrastructure and Cross-Cutting Concerns
- **7.1 Infrastructure Components**: Table
- **7.2 Security Across Services**: Authentication sequence diagram + service-to-service auth table
- **7.3 Observability Stack**: Table (Logging, Tracing, Metrics, Alerting) + correlation ID diagram
- **7.4 Multi-Tenancy Architecture**: Layered diagram showing DNS → JWT → Data → API scoping

#### 8. Deployment Topology
- **8.1 Environment Architecture**: Table of environments
- **8.2 Multi-Region Deployment**: Diagram (if applicable)
- **8.3 CI/CD Pipeline**: Pipeline flow diagram

#### 9. Operational Considerations
- **9.1 Monitoring**: Key metrics table
- **9.2 Incident Response**: Scenario/Detection/Mitigation table
- **9.3 Scaling Strategies**: Per-service scaling table

#### 10. Evolution and Extension Patterns
- **10.1 Adding New Microservices**: Checklist as `!!! tip` admonition
- **10.2 Extending Existing Services**: Step-by-step patterns
- **10.3 Deprecation Patterns**: Steps to retire services

#### 11. Architecture Decision Records
- Multiple ADRs using `!!! note \"Decision Record\"` admonitions
- Each with Context, Decision, Consequences (+/-), Services Affected

#### 12. Quick Reference
- **12.1 Service Endpoints**: Table
- **12.2 Event Catalog**: Table (Event Name, Publisher, Subscribers, Purpose)
- **12.3 Key Configuration**: Environment variables, feature toggles, tenant configuration

End with Maintenance Notes section.

---

## DOCUMENT 2: Microservices_Relationships.md

This is a VISUAL GUIDE to service interactions. Structure:

1. **Title**: `# Microservices Relationships` with intro paragraph
2. **The N Services**: Diagram showing all services in a single platform subgraph with labeled edges
3. **Communication Matrix**: Table showing who calls whom (rows = callers, columns = targets, cells = \"REST ➜\" or empty) with `!!! note \"Reading the matrix\"` admonition
4. **Synchronous vs Asynchronous Communication**: Two-subgraph diagram listing all sync and async paths + Why Two Patterns table
5. **Data Ownership Map**: Diagram with subgraphs per owning service, showing data entities and their storage
6. **Cross-Flow Service Participation**: Matrix table (flows × services with ✅ and role labels)
7. **How Services Collaborate** — 3-5 key patterns, each with:
   - Pattern name and description
   - Mermaid sequence diagram with `rect` phase blocks
   - Examples: Event Ingestion Pipeline, Hub-and-Spoke Query, Cross-Service Action Dispatch, Tenant Orchestration Fan-Out
8. **Authentication Between Services**: Three-subgraph diagram (External→Platform, Service→Service, Service→DataStore)
9. **Service Discovery**: Table + diagram
10. **Multi-Tenancy Across Services**: Layered diagram + per-service isolation table
11. **Event Catalog**: Complete event table
12. **Further Reading**: Links to blueprint and all flows

---

## DOCUMENT 3: Per-Flow Documents (flows/*.md)

For each end-to-end business flow that spans 2+ microservices, create `flows/<flow-kebab-case>-flow.md`.

Each flow document must follow this structure:

1. **Title**: `# <Flow Name> Flow`
2. **Badge**: `<span class=\"flow-badge flow-badge--sync\">Synchronous</span>` or `--async`, `--event`, `--critical`
3. **Summary**: One paragraph describing business value
4. **Flow at a Glance**: `!!! abstract` admonition with Trigger, Path, Result, Latency
5. **Services Involved**: Table with Service, Role, Communication columns
6. **End-to-End Flow Diagram**: `graph LR` with subgraphs per phase, colored nodes
7. **Step-by-Step Flow**: Numbered steps organized in phases (### Phase N: Name)
8. **Detailed Sequence Diagram**: `sequenceDiagram` with `rect rgb(...)` phase blocks, `alt`/`par` where appropriate
9. **Error Handling**: Table with Error Scenario, Detection, Handling, Impact + `!!! tip` for resilience notes
10. **Performance**: Table with Path, Latency Target, Notes
11. **Related Flows**: Table linking to other flow documents with relationship description

Identify flows by looking at how multiple services collaborate based on the approved overviews.
Common patterns: event ingestion, user queries/investigation, action dispatch, lifecycle management, risk/security pipelines.

---

## FINAL CHECKLIST

Before finishing, verify:
- [ ] index.md has hero-banner, stat-row, card-grid, and flow-badge HTML classes
- [ ] index.md links use trailing slash (e.g. `Product_Architecture_Blueprint/`)
- [ ] Every Mermaid diagram has a Legend table below it (two columns: Element, Meaning)
- [ ] Legend tables use `<span style="color:...">` with &#9632; swatch — NO raw hex codes
- [ ] Every flow document has a sequence diagram with rect phase blocks
- [ ] All service names are consistent across all documents
- [ ] Cross-references between documents use correct relative paths
- [ ] Blueprint Metadata uses exact timestamp and LLM values from the prompt
- [ ] No C4 extension syntax used — only standard flowchart/sequenceDiagram
- [ ] Admonitions use MkDocs Material syntax (!!!)
- [ ] Flow badges use the correct CSS class names"
