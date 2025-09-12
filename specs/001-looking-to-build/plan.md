# Implementation Plan: SignalHire Lead Generation Agent

**Branch**: `001-looking-to-build` | **Date**: September 11, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/vanman2025/signalhireagent/specs/001-looking-to-build/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a comprehensive lead generation automation platform starting with SignalHire integration. **Phase 1 MVP**: CLI tool that accepts search criteria → searches SignalHire → reveals contacts via browser automation (1000+ capacity vs 100 API limit) → exports to CSV. **Future Vision**: Web UI platform for teams, multi-platform expansion (LinkedIn, Apollo, ZoomInfo), white-label SaaS for agencies. Market opportunity: $2B+ lead gen software market with no existing AI-powered multi-platform automation. Revenue model: $0-399/month freemium to enterprise with projected $486K+ ARR by Year 3.

## Technical Context
**Language/Version**: Python 3.11 + Stagehand (AI browser automation)  
**Primary Dependencies**: httpx (async HTTP), pydantic (data validation), fastapi (callback server + future web UI backend), pandas (CSV export), stagehand (browser automation)  
**Storage**: File system for CSV exports, in-memory for session state, future: PostgreSQL for multi-tenant SaaS  
**Testing**: pytest with httpx testing utilities + browser automation contract tests  
**Target Platform**: Linux server (containerizable), future: cloud-native SaaS architecture  
**Project Type**: CLI tool with embedded callback server → evolving to web platform with multi-tenant architecture  
**Performance Goals**: Handle 600 elements/minute (SignalHire limit), process 1000+ prospects per bulk reveal via browser automation  
**Constraints**: 15-second scrollId timeout for pagination, API rate limits, credit-based usage, browser automation reliability  
**Scale/Scope**: Phase 1: Thousands of prospects per search. Future: Multi-platform (LinkedIn, Apollo, ZoomInfo), team collaboration, enterprise white-label

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (signalhire-agent CLI tool)
- Using framework directly? Yes (FastAPI for callbacks, httpx for HTTP)
- Single data model? Yes (Prospect, SearchCriteria, ExportFile entities)
- Avoiding patterns? Yes (direct API calls, no unnecessary abstractions)

**Architecture**:
- EVERY feature as library? Yes (signalhire_client lib, csv_exporter lib, rate_limiter lib)
- Libraries listed: 
  * signalhire_client: API integration with Search/Person endpoints
  * browser_client: Stagehand-based browser automation for bulk operations
  * csv_exporter: Export prospect data to CSV format
  * rate_limiter: Handle API quotas and backoff strategies
  * platform_adapter: Extensible pattern for multi-platform expansion (LinkedIn, Apollo, ZoomInfo)
- CLI per library: signalhire-agent with --search, --reveal, --export commands + future multi-platform workflows
- Library docs: llms.txt format planned

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes
- Git commits show tests before implementation? Will be enforced
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual SignalHire API for integration tests)
- Integration tests for: API contracts, callback mechanisms, rate limiting
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes (JSON logs with request IDs)
- Frontend logs → backend? N/A (CLI tool)
- Error context sufficient? Yes (API errors, rate limit context, operation status)

**Versioning**:
- Version number assigned? 0.1.0
- BUILD increments on every change? Yes
- Breaking changes handled? Yes (CLI backward compatibility)

## Project Structure

### Documentation (this feature)
```
specs/001-looking-to-build/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Single project structure (CLI tool with libraries)
src/
├── models/              # Data models (Prospect, SearchCriteria, etc.)
├── services/            # Business logic (search, reveal, export services)
├── cli/                 # Command-line interface
└── lib/                 # Libraries (signalhire_client, csv_exporter, rate_limiter)

tests/
├── contract/            # API contract tests
├── integration/         # End-to-end workflow tests
└── unit/               # Unit tests for individual components
```

**Structure Decision**: Single project (Option 1) - CLI tool with embedded callback server

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|agents|copilot|all]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)  
**Phase 6+**: Future roadmap - Web UI development, multi-platform expansion, enterprise SaaS features

## Future Development Roadmap
*Beyond Phase 5 - Strategic expansion plan*

**Phase 6: Web UI Platform**
- React/Vue frontend with real-time dashboards
- Team collaboration and shared lead management
- Visual workflow builder and scheduling
- Credit usage analytics and reporting

**Phase 7: Multi-Platform Expansion**
- LinkedIn Sales Navigator integration (1M+ users, $20-50/month additional)
- Apollo.io integration (500K+ users, $15-30/month additional)  
- ZoomInfo integration (20K+ enterprise, $50-150/month additional)
- Unified multi-platform search workflows

**Phase 8: Enterprise SaaS**
- Multi-tenant architecture with RBAC
- White-label customization for agencies
- CRM integrations (Salesforce, HubSpot, Pipedrive)
- Advanced analytics and compliance features

**Business Model Evolution:**
- Stage 1: CLI tool for power users ($0-49/month)
- Stage 2: Web SaaS for sales teams ($49-149/month)
- Stage 3: Platform for agencies ($399-999/month) 
- Stage 4: Enterprise marketplace ($1000+/month)

**Market Opportunity:**
- Total Addressable Market: $2B+ lead generation software
- No existing AI-powered multi-platform automation
- Competitive advantage: SignalHire-native + AI adaptability

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
