---
description: 'Comprehensive project architecture blueprint generator that analyzes codebases to create detailed architectural documentation. Automatically detects technology stacks and architectural patterns, generates visual diagrams, documents implementation patterns, and provides extensible blueprints for maintaining architectural consistency and guiding new development.'
mode: 'agent'
---

# Comprehensive Project Architecture Blueprint Generator

## Configuration Variables
${PROJECT_TYPE="Auto-detect|.NET|Java|React|Angular|Python|Node.js|Flutter|Other"} <!-- Primary technology -->
${ARCHITECTURE_PATTERN="Auto-detect|Clean Architecture|Microservices|Layered|MVVM|MVC|Hexagonal|Event-Driven|Serverless|Monolithic|Other"} <!-- Primary architectural pattern -->
${DIAGRAM_TYPE="C4|UML|Flow|Component|None"} <!-- Architecture diagram type -->
${DETAIL_LEVEL="High-level|Detailed|Comprehensive|Implementation-Ready"} <!-- Level of detail to include -->
${INCLUDES_CODE_EXAMPLES=true|false} <!-- Include sample code to illustrate patterns -->
${INCLUDES_IMPLEMENTATION_PATTERNS=true|false} <!-- Include detailed implementation patterns -->
${INCLUDES_DECISION_RECORDS=true|false} <!-- Include architectural decision records -->
${FOCUS_ON_EXTENSIBILITY=true|false} <!-- Emphasize extension points and patterns -->




## Generated Prompt

"Create a comprehensive architecture blueprint document that thoroughly analyzes the architectural patterns in the codebase to serve as a definitive reference for maintaining architectural consistency and elaborating on the key business flows that drive the system's functionality.

STYLE HIGHLIGHTS TO APPLY THROUGHOUT THE DOCUMENT:
1. Executive Summary: Begin with a one-paragraph high-impact summary of purpose, scope, and strategic value.
2. Table of Contents: Provide a numbered TOC matching section numbering (1–17) for quick navigation.
3. Scannable Bullets: Prefer concise bullet lists over dense paragraphs; each bullet should start with a strong noun or verb.
4. Consistent Terminology: Use standardized concise labels (e.g., "Layer Chain", "Entities", "Workflow", "Topology", "Pitfalls").
5. Rationale Phrases: Where beneficial, include short "Why This Matters" or "Impact" lines to contextualize architectural choices.
6. Streamlined Descriptions: Retain substance but remove filler wording; avoid repeating configuration details already covered.
7. Preservation: Keep original section structure and numbering (1–17) and include diagrams as specified.
8. Legends & Diagrams: For C4 diagrams, use multiple colors (green/blue/orange/purple by element type), keep labels to 2 lines max, NEVER include stereotype labels like <<system>>, [CONTAINER], etc. Add a legend explaining color coding and relationships.
9. Accessibility: Ensure legends and summary text make diagrams understandable; use both color and shape/position for clarity.
10. Cohesion: Maintain alignment between TOC, headings, and any cross-references in flow documents.
11. Inviting & Appealing Presentation: Use clear whitespace, consistent heading hierarchy, short paragraphs, and occasional callout lines (e.g., "Why This Matters") to make the document welcoming; avoid walls of text and overly technical tone in overview sections while retaining precision.

Follow these style rules while generating each section.

First, extract the project/service name from the codebase by examining:
- Repository name or root directory name
- Package.json, pyproject.toml, pom.xml, or similar configuration files
- Main application/service class names
- Docker compose service names
- README.md title or project descriptions

Name and store the document under the documentation directory: 'ai_docs/<Project_name>_Architecture_Blueprint.md' where <Project_name> is the extracted service/project name. If the ai_docs directory does not exist, create it. All generated flow markdown artifacts MUST also reside under 'ai_docs/flows/'.


**Note**: After blueprint generation completes, a GitHub Pages documentation site will be automatically created using MkDocs with the Material theme. The system will:
- Create a `ai_docs/` directory structure with all documentation
- Generate `mkdocs.yml` configuration file
- Set up media assets (logo, favicon) and custom styling
- Create an index.md homepage linking to the blueprint and flows
- Deploy using `mkdocs gh-deploy` command
Focus on creating high-quality, well-structured Markdown content that will render beautifully in the generated documentation site.

Start the document with:
- Title: '# Project Architecture Blueprint'
- Blueprint Metadata section as a table showing the key analysis parameters:

| Parameter | Value |
|-----------|-------|
| Generation Timestamp | [Timestamp with minutes granularity, e.g., 2025-10-23 14:30] |
| Git Commit Hash | [Short git hash of the analyzed commit, e.g., a1b2c3d] |
| Agent | ${AGENT} |
| LLM | ${LLM} |
| Project Type | ${PROJECT_TYPE} |
| Architecture Pattern | ${ARCHITECTURE_PATTERN} |

Use the following approach for the analysis:

### 1. Architecture Detection and Analysis
- ${PROJECT_TYPE == "Auto-detect" ? "Analyze the project structure to identify all technology stacks and frameworks in use by examining:
  - Project and configuration files
  - Package dependencies and import statements
  - Framework-specific patterns and conventions
  - Build and deployment configurations" : "Focus on ${PROJECT_TYPE} specific patterns and practices"}
  
- ${ARCHITECTURE_PATTERN == "Auto-detect" ? "Determine the architectural pattern(s) by analyzing:
  - Folder organization and namespacing
  - Dependency flow and component boundaries
  - Interface segregation and abstraction patterns
  - Communication mechanisms between components" : "Document how the ${ARCHITECTURE_PATTERN} architecture is implemented"}

### 2. Architectural Overview
- Provide a clear, concise explanation of the overall architectural approach
- Document the guiding principles evident in the architectural choices
- Identify architectural boundaries and how they're enforced
- Note any hybrid architectural patterns or adaptations of standard patterns

### 3. Architecture Visualization
${DIAGRAM_TYPE != "None" ? `Create ${DIAGRAM_TYPE} diagrams at multiple levels of abstraction:
- High-level architectural overview showing major subsystems
- Component interaction diagrams showing relationships and dependencies
- Data flow diagrams showing how information moves through the system
- Ensure diagrams accurately reflect the actual implementation, not theoretical patterns
- Verify that all Mermaid diagrams have valid syntax and render correctly

#### C4 Diagram Styling Rules (MANDATORY)

**CRITICAL: Use Standard Flowchart Syntax - NOT C4 Extension Syntax**

⚠️ **FORBIDDEN SYNTAX** - NEVER use these Mermaid C4 extension keywords (they cause rendering errors and force ugly labels):
- `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`
- `Person`, `Person_Ext`, `System`, `System_Ext`, `SystemDb`, `SystemQueue`
- `Container`, `Container_Boundary`, `ContainerDb`, `ContainerQueue`
- `Component`, `Component_Ext`, `Boundary`
- `Rel`, `Rel_U`, `Rel_D`, `Rel_L`, `Rel_R`, `BiRel`
- `UpdateLayoutConfig`, `UpdateRelStyle`, `UpdateElementStyle`

✅ **REQUIRED**: Always use standard Mermaid `flowchart` syntax with `classDef` for styling. This is MORE RELIABLE and gives BETTER visual control.

**CRITICAL: Visual Appeal & Readability Requirements**

1. **Use Multiple Colors by Element Category** (NEVER all-blue diagrams):
   - Green (#228B22 or similar): External systems, entry points, message sources
   - Blue (#1E90FF or similar): Core/main system components being documented
   - Orange (#FF8C00 or similar): Downstream services, dependencies, APIs
   - Magenta/Purple (#9932CC or similar): Infrastructure services (service discovery, auth providers)
   - Yellow backgrounds (#FFFACD or similar): For grouping/boundary boxes (subgraphs)
   - Red (#DC143C or similar): Error handling, DLQs, failure paths

2. **NEVER Include Stereotype Labels** - These are FORBIDDEN:
   - NO \`<<system>>\`, \`<<container>>\`, \`<<component>>\`, \`<<person>>\`
   - NO \`[CONTAINER]\`, \`[ENTERPRISE]\`, \`[Software System]\`
   - NO \`[Lambda Python]\`, \`[API Gateway]\`, \`[AWS SQS]\` type annotations
   - Just use clean element names with optional brief description

3. **Text Clarity Rules**:
   - Element labels: Maximum 2 lines (Name + brief role)
   - Format: "Component Name" on line 1, "Brief Role" on line 2
   - NO long descriptions crammed inside shapes
   - Move detailed explanations to the legend or narrative sections

4. **Mermaid Syntax for C4 Diagrams** - Use `graph TB` with inline `style` directives:

**Color Palette to Use:**
- **Blue** (focus system): `fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff`
- **Green** (external sources): `fill:#7ED321,stroke:#5FA019,stroke-width:2px`
- **Orange** (downstream services): `fill:#F5A623,stroke:#C4841D,stroke-width:2px`
- **Purple** (infrastructure/utilities): `fill:#BD10E0,stroke:#9012B0,stroke-width:2px`
- **Red** (error handling/DLQ): `fill:#D0021B,stroke:#A00116,stroke-width:2px`
- **Teal** (queues/messaging): `fill:#50E3C2,stroke:#3AB09E,stroke-width:2px`
- **Violet** (decorators/middleware): `fill:#9013FE,stroke:#6A0FB0,stroke-width:2px`

**Context Diagram Example:**
\`\`\`mermaid
graph TB
    PubSub[PubSub System<br/>SNS Topics]
    MainService[Main Service<br/>Lambda Handler]
    DownstreamAPI[Downstream API<br/>Private Gateway]
    CloudMap[AWS CloudMap<br/>Service Discovery]
    
    PubSub -->|Events via SQS| MainService
    MainService -->|API calls| DownstreamAPI
    MainService -->|Discover endpoints| CloudMap
    
    style MainService fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style PubSub fill:#7ED321,stroke:#5FA019,stroke-width:2px
    style DownstreamAPI fill:#F5A623,stroke:#C4841D,stroke-width:2px
    style CloudMap fill:#BD10E0,stroke:#9012B0,stroke-width:2px
\`\`\`

5. **Container Diagram Example** (use subgraphs for system boundaries):
\`\`\`mermaid
graph TB
    subgraph PubSub["PubSub System"]
        Topic1[Recording Topic]
        Topic2[Command Topic]
    end
    
    subgraph MainSystem["Main System"]
        SQSQueue[SQS Consumer Queue]
        DLQ[Dead Letter Queue]
        Lambda[Events Listener Lambda]
    end
    
    subgraph Downstream["Downstream Services"]
        API1[Service A API]
        API2[Service B API]
    end
    
    Topic1 -->|SNS subscription| SQSQueue
    Topic2 -->|SNS subscription| SQSQueue
    SQSQueue -->|Triggers| Lambda
    Lambda -->|Failed events| DLQ
    Lambda -->|POST /api/resource| API1
    Lambda -->|PUT /api/other| API2
    
    style Lambda fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style SQSQueue fill:#50E3C2,stroke:#3AB09E,stroke-width:2px
    style DLQ fill:#D0021B,stroke:#A00116,stroke-width:2px
\`\`\`

6. **Component Diagram Example** (use subgraphs + dashed arrows for dependencies):
\`\`\`mermaid
graph TB
    subgraph Handler["handler.py"]
        Decorators[Decorators Chain:<br/>Tracer, Metrics, Logger,<br/>Error Handler]
        MainFunction[main_function]
    end
    
    subgraph Logic["Event Routing Logic"]
        Router1[router_a.py]
        Router2[router_b.py]
        Handler1[handler_a.py]
        Handler2[handler_b.py]
    end
    
    subgraph Integrations["Service Integrations"]
        Client1[Service A Client]
        Client2[Service B Client]
        Resolver[CloudMap Resolver]
        Auth[IAM Auth]
    end
    
    Decorators -->|Wraps| MainFunction
    MainFunction -->|Type A events| Router1
    MainFunction -->|Type B events| Router2
    Router1 -->|Process| Handler1
    Router2 -->|Process| Handler2
    Handler1 -->|Invoke| Client1
    Handler2 -->|Invoke| Client2
    Client1 -.->|Discover| Resolver
    Client2 -.->|Discover| Resolver
    Client1 -.->|Assume role| Auth
    Client2 -.->|Assume role| Auth
    
    style MainFunction fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style Decorators fill:#9013FE,stroke:#6A0FB0,stroke-width:2px
\`\`\`

7. **Arrow Styles**:
   - Solid arrows `-->` for direct invocations and main data flow
   - Dashed arrows `-.->` for dependency usage (discovery, auth, utilities)
   - Edge labels `|label|` should be concise action phrases

8. **Always Include a Legend** after each diagram explaining:
   - Color meanings (which category each color represents)
   - Arrow types (solid vs dashed meanings)
   - Key relationships

Diagram Style Guidelines (additional refinements):
- Remove verbose relationship labels; keep node rectangles clean
- Keep node labels concise (abbreviate where clarity is retained)
- Provide a Legend below each diagram explaining relationships and color coding
- Maintain consistent naming across Context, Container, and Component levels
- For flows (sequence/flowchart) retain minimal step labels with short verbs (init, enrich, persist)
- Validate that diagrams are visually appealing and accessible
` : "Describe the component relationships based on actual code dependencies, providing clear textual explanations of:
- Subsystem organization and boundaries
- Dependency directions and component interactions
- Data flow and process sequences"}

### 4. Business Flow Mapping (Onboarding Focus)
- Identify 3–7 primary business or operational flows critical for understanding the system (examples: Entity Search, Entity Lifecycle Creation, Notification Dispatch, Access Authorization, Configuration Retrieval). Avoid repository-specific naming; derive flow names from detected endpoints, scheduled jobs, event handlers, or CLI entry points.
- Create a summary table at the beginning of this section with the following structure:

| Flow Name | Entry Point | Document Link |
|-----------|-------------|---------------|
| [Flow 1 Name] | [Entry trigger details: HTTP method + endpoint, SNS→SQS→handler, scheduled job, etc.] | [flow document](flows/flow-1-name-flow.md) |
| [Flow 2 Name] | [Entry trigger details] | [flow document](flows/flow-2-name-flow.md) |
| ... | ... | ... |

  - **Flow Name**: Human-readable business flow name
  - **Entry Point**: Concise entry trigger (e.g., "GET /api/sessions/ui", "SNS → SQS → sessions_collection_handler.py", "POST /api/tenants, /api/tenants/{id}")
  - **Document Link**: Markdown link to the detailed flow document in the `ai_docs/flows/` directory with text "flow document"

- For each flow capture:
  - Entry trigger (HTTP endpoint, message/event, scheduled job, CLI invocation)
  - Entry component (handler/function/class) and immediate cross-cutting wrappers (auth, tracing, validation, logging)
  - Sequence of internal components/modules invoked (domain services, repositories, adapters)
  - External dependencies touched (datastores, third-party APIs, queues, caches)
  - Data transformations (validation, mapping, enrichment, serialization) at each major step
  - Decision & branching points (authorization checks, feature flag gates, fallback paths, error handling distinctions)
  - Output artifact (HTTP response, emitted event, persisted record, side-effect) and success/error variants
- Highlight multi-tenant or isolation mechanics if present (claim extraction, context injection, access scopes) in a technology-neutral fashion.
- **MANDATORY**: Each flow MUST include a Mermaid sequence diagram (`sequenceDiagram`) showing the runtime interaction between actors and components. This is a required element, not optional. Use generic actor/component naming; ensure diagrams reflect actual code calling order and have valid Mermaid syntax. If additional flow diagrams (flowchart) would aid understanding, include them as supplementary diagrams, but the sequence diagram is always required.
- Enumerate extension points per flow (where new filters, validations, integration calls, or feature flags can be introduced) and note stability vs. volatile sections.
- Provide performance & scalability notes (hot paths, expected data volume, latency-sensitive steps) if detectable.
- Security & compliance considerations (sensitive data boundaries, permission checks, encryption points) annotated inline.
- Optional resiliency annotations: timeouts, retries, circuit breakers, idempotency markers.

#### Per-Flow Markdown Artifact Generation
- Create a dedicated Markdown file for each detected flow under a `ai_docs/flows/` directory (create if absent).
- File naming convention: `ai_docs/flows/<flow-kebab-case>-flow.md` (e.g., `user-authentication-flow.md`).
- Minimum structure for each file:
  1. Title: `<Human Readable Flow Name>`
  2. Summary: One-paragraph overview of business value & scope.
  3. Trigger(s): Enumerated list (endpoints/events/jobs).
  4. Primary Actors / Roles (if applicable).
  5. Step-by-Step Control Flow (numbered) with component references.
  6. Data Flow: Key inputs/outputs, transformations, schemas (link to domain models).
  7. Dependencies: Internal modules + external services.
  8. Cross-Cutting Concerns Applied (auth, logging, tracing, validation, flags).
  9. Extension Points & Variation Mechanisms.
 10. Failure Modes & Error Handling Paths.
 11. Performance / Scalability Notes.
 12. Security & Compliance Considerations.
 13. **Diagram (REQUIRED)**: A Mermaid `sequenceDiagram` block showing the runtime interaction flow between actors, components, and external systems. This section is mandatory and must not be omitted. The diagram must have validated Mermaid syntax and accurately reflect the code calling order.
      
      **Sequence Diagram Styling Rules:**
      - Use clean participant aliases (NO stereotype labels like <<system>> or [Container])
      - Keep message labels concise: short verb phrases (e.g., "Request", "Validate", "Store")
      - Use participant aliases for readability: `participant API as API Gateway`
      
      Example structure:
      ```mermaid
      sequenceDiagram
          actor User
          participant API as API Gateway
          participant Service as Business Service
          participant DB as Database
          User->>API: Request
          API->>Service: Process
          Service->>DB: Query
          DB-->>Service: Result
          Service-->>API: Response
          API-->>User: Result
      ```
      
      **If adding a supplementary flowchart diagram**, apply C4 styling rules:
      - Use multiple colors by element type (green for external, blue for core, orange for downstream)
      - NO stereotype labels - clean names only
      - Keep node labels to 2 lines maximum
 14. Testing Strategy Summary (unit, integration, E2E coverage targets).
 15. Maintenance Guidance (how to safely modify / version the flow).
- Ensure each flow file links back to the main 'ai_docs/<Project_name>_Architecture_Blueprint.md' for global context.
- If a flow spans multiple bounded contexts or microservices, include an "Inter-Service Interactions" subsection referencing other flow files.

### 5. Core Architectural Components
For each architectural component discovered in the codebase:

- **Purpose and Responsibility**:
  - Primary function within the architecture
  - Business domains or technical concerns addressed
  - Boundaries and scope limitations

- **Internal Structure**:
  - Organization of classes/modules within the component
  - Key abstractions and their implementations
  - Design patterns utilized

- **Interaction Patterns**:
  - How the component communicates with others
  - Interfaces exposed and consumed
  - Dependency injection patterns
  - Event publishing/subscription mechanisms

- **Evolution Patterns**:
  - How the component can be extended
  - Variation points and plugin mechanisms
  - Configuration and customization approaches

### 6. Architectural Layers and Dependencies
- Map the layer structure as implemented in the codebase
- Document the dependency rules between layers
- Identify abstraction mechanisms that enable layer separation
- Note any circular dependencies or layer violations
- Document dependency injection patterns used to maintain separation

### 7. Data Architecture
- Document domain model structure and organization
- Map entity relationships and aggregation patterns
- Identify data access patterns (repositories, data mappers, etc.)
- Document data transformation and mapping approaches
- Note caching strategies and implementations
- Document data validation patterns

### 8. Cross-Cutting Concerns Implementation
Document implementation patterns for cross-cutting concerns:

- **Authentication & Authorization**:
  - Security model implementation
  - Permission enforcement patterns
  - Identity management approach
  - Security boundary patterns

- **Error Handling & Resilience**:
  - Exception handling patterns
  - Retry and circuit breaker implementations
  - Fallback and graceful degradation strategies
  - Error reporting and monitoring approaches

- **Logging & Monitoring**:
  - Instrumentation patterns
  - Observability implementation
  - Diagnostic information flow
  - Performance monitoring approach

- **Validation**:
  - Input validation strategies
  - Business rule validation implementation
  - Validation responsibility distribution
  - Error reporting patterns

- **Configuration Management**:
  - Configuration source patterns
  - Environment-specific configuration strategies
  - Secret management approach
  - Feature flag implementation

### 9. Service Communication Patterns
- Document service boundary definitions
- Identify communication protocols and formats
- Map synchronous vs. asynchronous communication patterns
- Document API versioning strategies
- Identify service discovery mechanisms
- Note resilience patterns in service communication

### 10. Technology-Specific Architectural Patterns
${PROJECT_TYPE == "Auto-detect" ? "For each detected technology stack, document specific architectural patterns:" : `Document ${PROJECT_TYPE}-specific architectural patterns:`}

${(PROJECT_TYPE == ".NET" || PROJECT_TYPE == "Auto-detect") ? 
"#### .NET Architectural Patterns (if detected)
- Host and application model implementation
- Middleware pipeline organization
- Framework service integration patterns
- ORM and data access approaches
- API implementation patterns (controllers, minimal APIs, etc.)
- Dependency injection container configuration" : ""}

${(PROJECT_TYPE == "Java" || PROJECT_TYPE == "Auto-detect") ? 
"#### Java Architectural Patterns (if detected)
- Application container and bootstrap process
- Dependency injection framework usage (Spring, CDI, etc.)
- AOP implementation patterns
- Transaction boundary management
- ORM configuration and usage patterns
- Service implementation patterns" : ""}

${(PROJECT_TYPE == "React" || PROJECT_TYPE == "Auto-detect") ? 
"#### React Architectural Patterns (if detected)
- Component composition and reuse strategies
- State management architecture
- Side effect handling patterns
- Routing and navigation approach
- Data fetching and caching patterns
- Rendering optimization strategies" : ""}

${(PROJECT_TYPE == "Angular" || PROJECT_TYPE == "Auto-detect") ? 
"#### Angular Architectural Patterns (if detected)
- Module organization strategy
- Component hierarchy design
- Service and dependency injection patterns
- State management approach
- Reactive programming patterns
- Route guard implementation" : ""}

${(PROJECT_TYPE == "Python" || PROJECT_TYPE == "Auto-detect") ? 
"#### Python Architectural Patterns (if detected)
- Module organization approach
- Dependency management strategy
- OOP vs. functional implementation patterns
- Framework integration patterns
- Asynchronous programming approach" : ""}

### 11. Implementation Patterns
${INCLUDES_IMPLEMENTATION_PATTERNS ? 
"Document concrete implementation patterns for key architectural components:

- **Interface Design Patterns**:
  - Interface segregation approaches
  - Abstraction level decisions
  - Generic vs. specific interface patterns
  - Default implementation patterns

- **Service Implementation Patterns**:
  - Service lifetime management
  - Service composition patterns
  - Operation implementation templates
  - Error handling within services

- **Repository Implementation Patterns**:
  - Query pattern implementations
  - Transaction management
  - Concurrency handling
  - Bulk operation patterns

- **Controller/API Implementation Patterns**:
  - Request handling patterns
  - Response formatting approaches
  - Parameter validation
  - API versioning implementation

- **Domain Model Implementation**:
  - Entity implementation patterns
  - Value object patterns
  - Domain event implementation
  - Business rule enforcement" : "Mention that detailed implementation patterns vary across the codebase."}

### 12. Testing Architecture
- Document testing strategies aligned with the architecture
- Identify test boundary patterns (unit, integration, system)
- Map test doubles and mocking approaches
- Document test data strategies
- Note testing tools and frameworks integration

### 13. Deployment Architecture
- Document deployment topology derived from configuration
- Identify environment-specific architectural adaptations
- Map runtime dependency resolution patterns
- Document configuration management across environments
- Identify containerization and orchestration approaches
- Note cloud service integration patterns

### 14. Extension and Evolution Patterns
${FOCUS_ON_EXTENSIBILITY ? 
"Provide detailed guidance for extending the architecture:

- **Feature Addition Patterns**:
  - How to add new features while preserving architectural integrity
  - Where to place new components by type
  - Dependency introduction guidelines
  - Configuration extension patterns

- **Modification Patterns**:
  - How to safely modify existing components
  - Strategies for maintaining backward compatibility
  - Deprecation patterns
  - Migration approaches

- **Integration Patterns**:
  - How to integrate new external systems
  - Adapter implementation patterns
  - Anti-corruption layer patterns
  - Service facade implementation" : "Document key extension points in the architecture."}

${INCLUDES_CODE_EXAMPLES ? 
"### 15. Architectural Pattern Examples
Extract representative code examples that illustrate key architectural patterns:

- **Layer Separation Examples**:
  - Interface definition and implementation separation
  - Cross-layer communication patterns
  - Dependency injection examples

- **Component Communication Examples**:
  - Service invocation patterns
  - Event publication and handling
  - Message passing implementation

- **Extension Point Examples**:
  - Plugin registration and discovery
  - Extension interface implementations
  - Configuration-driven extension patterns

Include enough context with each example to show the pattern clearly, but keep examples concise and focused on architectural concepts." : ""}

${INCLUDES_DECISION_RECORDS ? 
"### 16. Architectural Decision Records
Document key architectural decisions evident in the codebase:

- **Architectural Style Decisions**:
  - Why the current architectural pattern was chosen
  - Alternatives considered (based on code evolution)
  - Constraints that influenced the decision

- **Technology Selection Decisions**:
  - Key technology choices and their architectural impact
  - Framework selection rationales
  - Custom vs. off-the-shelf component decisions

- **Implementation Approach Decisions**:
  - Specific implementation patterns chosen
  - Standard pattern adaptations
  - Performance vs. maintainability tradeoffs

For each decision, note:
- Context that made the decision necessary
- Factors considered in making the decision
- Resulting consequences (positive and negative)
- Future flexibility or limitations introduced" : ""}

### ${INCLUDES_DECISION_RECORDS ? "17" : INCLUDES_CODE_EXAMPLES ? "16" : "15"}. Architecture Governance
- Document how architectural consistency is maintained
- Identify automated checks for architectural compliance
- Note architectural review processes evident in the codebase
- Document architectural documentation practices

### ${INCLUDES_DECISION_RECORDS ? "18" : INCLUDES_CODE_EXAMPLES ? "17" : "16"}. Blueprint for New Development
Create a clear architectural guide for implementing new features:

- **Development Workflow**:
  - Starting points for different feature types
  - Component creation sequence
  - Integration steps with existing architecture
  - Testing approach by architectural layer

- **Implementation Templates**:
  - Base class/interface templates for key architectural components
  - Standard file organization for new components
  - Dependency declaration patterns
  - Documentation requirements

- **Common Pitfalls**:
  - Architecture violations to avoid
  - Common architectural mistakes
  - Performance considerations
  - Testing blind spots

Include information about when this blueprint was generated and recommendations for keeping it updated as the architecture evolves."
