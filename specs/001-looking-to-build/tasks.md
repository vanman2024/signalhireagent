# Tasks: SignalHire Lead Generation Agent

**Input**: Design doc### Data Model### Core Services (Sequential - Shared Dependencies)
- [x] T020 @copilot SignalHire API client service in src/services/signalhire_client.py
- [x] T021 @claude Browser automation service using Stagehand in src/services/browser_client.py
- [x] T022 @copilot CSV export service with pandas in src/services/csv_exporter.py
- [x] T023 @copilot Rate limiting and credit management service in src/services/rate_limiter.pyrallel - Independent Files)
- [x] T014 [P] SearchCriteria model with validation in src/models/search_criteria.py
- [x] T015 [P] Prospect model with relationships in src/models/prospect.py
- [x] T016 [P] ContactInfo model with types in src/models/contact_info.py
- [x] T017 [P] ExperienceEntry model in src/models/experience.py
- [x] T018 [P] EducationEntry model in src/models/education.py
- [x] T019 [P] Operation models (SearchOp, RevealOp) in src/models/operations.pyfrom `/home/vanman2025/signalhireagent/specs/001-looking-to-build/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11, httpx, pydantic, fastapi, pandas, Stagehand
   → Structure: Single project (CLI tool with embedded callback server)
2. Load design documents:
   → data-model.md: 6 entities (SearchCriteria, Prospect, ContactInfo, etc.)
   → contracts/: 6 contracts (search-api, person-api, credits-api, cli-interface, stagehand-automation, scroll-search-api)
   → research.md: Browser automation + API hybrid approach
   → quickstart.md: Search → reveal → export workflows
3. Generate tasks by category:
   → Setup: project structure, dependencies, linting
   → Tests: 6 contract tests, 4 integration tests
   → Core: 6 data models, 4 services, 7 CLI commands
   → Integration: browser automation, callback server, logging
   → Polish: unit tests, performance validation, documentation
4. Apply task rules:
   → Contract tests [P] (different files)
   → Models [P] (independent entities)
   → Services sequential (shared dependencies)
   → CLI commands sequential (shared click app)
5. Number tasks sequentially (T001-T030)
6. Generate dependency graph: Tests → Models → Services → CLI → Integration
7. Validate completeness: All contracts tested, all entities modeled, all commands implemented
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project structure**: `src/`, `tests/` at repository root
- **Source**: `src/models/`, `src/services/`, `src/cli/`, `src/lib/`
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`

## Phase 3.1: Setup
- [x] T001 Create project structure per implementation plan: src/{models,services,cli,lib}/, tests/{contract,integration,unit}/
- [x] T002 Initialize Python project with pyproject.toml: httpx, pydantic, fastapi, pandas, click, stagehand dependencies
- [x] T003 [P] Configure linting and formatting: ruff, mypy, pytest configuration

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API and Browser Automation)
- [x] T004 [P] Contract test Search API in tests/contract/test_search_api.py
- [x] T005 [P] Contract test Person API with callbacks in tests/contract/test_person_api.py
- [x] T006 [P] Contract test Credits API in tests/contract/test_credits_api.py
- [x] T007 [P] Contract test Scroll Search pagination in tests/contract/test_scroll_search_api.py
- [x] T008 [P] Contract test Stagehand automation workflows in tests/contract/test_stagehand_automation.py
- [x] T009 [P] Contract test CLI interface commands in tests/contract/test_cli_interface.py

### Integration Tests (End-to-End Workflows)
- [x] T010 [P] Integration test search → reveal → export workflow in tests/integration/test_search_reveal_export.py
- [x] T011 [P] Integration test browser automation login and search in tests/integration/test_browser_workflows.py
- [x] T012 [P] Integration test API rate limiting and credit management in tests/integration/test_rate_limiting.py
- [x] T013 [P] Integration test CSV export and data validation in tests/integration/test_csv_export.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (Parallel - Independent Files)
- [x] T014 [P] SearchCriteria model with validation in src/models/search_criteria.py
- [x] T015 [P] Prospect model with relationships in src/models/prospect.py
- [x] T016 [P] ContactInfo model with types in src/models/contact_info.py
- [x] T017 [P] ExperienceEntry model in src/models/experience.py
- [x] T018 [P] EducationEntry model in src/models/education.py
- [x] T019 [P] @copilot Operation models (SearchOp, RevealOp) in src/models/operations.py

### Core Services (Sequential - Shared Dependencies)
- [x] T020 @copilot SignalHire API client service in src/services/signalhire_client.py
- [x] T021 @claude Browser automation service using Stagehand in src/services/browser_client.py
- [x] T022 @gemini CSV export service with pandas in src/services/csv_exporter.py
- [x] T023 @codex Rate limiting and credit management service in src/services/rate_limiter.py

### CLI Commands (Sequential - Shared Click App)
- [x] T024 @copilot CLI main application and global options in src/cli/main.py
- [x] T025: Implement search command (`src/cli/search_commands.py`) - Complete CLI search functionality with filtering options
- [x] T026: Implement reveal command (`src/cli/reveal_commands.py`) - Bulk contact revelation with native export support
- [x] T027: Implement workflow command (`src/cli/workflow_commands.py`) - Combined search+reveal+export workflows
- [x] T028: Status and credits commands in src/cli/status_commands.py
- [x] T029 @copilot Configuration management commands in src/cli/config_commands.py
- [x] T030 @copilot Export command with format options in src/cli/export_commands.py

## Phase 3.4: Integration
- [x] T031 @claude FastAPI callback server for Person API in src/lib/callback_server.py
- [x] T032 @codex Stagehand browser configuration and session management in src/lib/browser_manager.py
- [x] T033 @gemini Structured logging with JSON format in src/lib/logger.py
- [x] T034 @claude Environment configuration and secrets management in src/lib/config.py

## Phase 3.5: Polish
- [x] T035 [P] @codex Unit tests for data model validation in tests/unit/test_models.py
- [x] T036 [P] @codex Unit tests for service utilities in tests/unit/test_services.py
- [x] T037 [P] @gemini Performance tests for bulk operations (<600 elements/minute) in tests/performance/test_bulk_operations.py
- [x] T038 [P] @gemini Update README.md with installation and usage guide
- [x] T039 [P] @copilot Create requirements.txt and setup.py for distribution
- [x] T040 @claude Remove code duplication and refactor shared utilities
- [x] T041 @codex Comprehensive error handling and retry logic for browser automation
- [x] T042 @gemini API documentation generation and validation
- [x] T043 @codex Interactive debugging utilities for failed browser sessions
- [x] T044 @gemini Performance monitoring and metrics collection system
- [x] T045 @codex Async test utilities and fixtures for integration tests

## Dependencies
- **Setup** (T001-T003) before everything
- **Tests** (T004-T013) before implementation (T014-T040)
- **Models** (T014-T019) before services (T020-T023)
- **Services** (T020-T023) before CLI (T024-T030)
- **Core** (T014-T030) before integration (T031-T034)
- **Implementation** before polish (T035-T040)

## Parallel Execution Examples

### Phase 3.2 - Launch All Contract Tests Together:
```bash
# All contract tests can run in parallel (different files)
Task: "Contract test Search API in tests/contract/test_search_api.py"
Task: "Contract test Person API with callbacks in tests/contract/test_person_api.py"  
Task: "Contract test Credits API in tests/contract/test_credits_api.py"
Task: "Contract test Scroll Search pagination in tests/contract/test_scroll_search_api.py"
Task: "Contract test Stagehand automation workflows in tests/contract/test_stagehand_automation.py"
Task: "Contract test CLI interface commands in tests/contract/test_cli_interface.py"
```

### Phase 3.2 - Launch All Integration Tests Together:
```bash
# All integration tests can run in parallel (different files)
Task: "Integration test search → reveal → export workflow in tests/integration/test_search_reveal_export.py"
Task: "Integration test browser automation login and search in tests/integration/test_browser_workflows.py"
Task: "Integration test API rate limiting and credit management in tests/integration/test_rate_limiting.py"
Task: "Integration test CSV export and data validation in tests/integration/test_csv_export.py"
```

### Phase 3.3 - Launch All Data Models Together:
```bash
# All models can run in parallel (independent entities)
Task: "SearchCriteria model with validation in src/models/search_criteria.py"
Task: "Prospect model with relationships in src/models/prospect.py"
Task: "ContactInfo model with types in src/models/contact_info.py"
Task: "ExperienceEntry model in src/models/experience.py"
Task: "EducationEntry model in src/models/education.py"
Task: "Operation models (SearchOp, RevealOp) in src/models/operations.py"
```

## Notes
- **[P] tasks** = different files, no dependencies between them
- **TDD approach**: All tests must fail before implementing features
- **Browser automation**: Uses Stagehand for AI-powered web interaction
- **Hybrid strategy**: API for credits/monitoring + browser for bulk operations
- **Rate limiting**: Respect SignalHire's 600 elements/minute limit
- **CSV export**: Leverage SignalHire's native export (1000+ vs 100 API limit)
- **Commit after each task** to maintain clear progress tracking

## Task Generation Rules Applied
- ✅ Each contract file → contract test task marked [P]
- ✅ Each entity in data-model → model creation task marked [P]  
- ✅ Each CLI command → implementation task (sequential - shared click app)
- ✅ Each user story → integration test marked [P]
- ✅ Different files = parallel [P], same file = sequential
- ✅ Tests before implementation (TDD)
- ✅ Models before services before CLI
- ✅ Core before integration before polish

## Validation Checklist
- ✅ All 6 contracts have corresponding tests (T004-T009)
- ✅ All 6 entities have model creation tasks (T014-T019)
- ✅ All 7 CLI commands implemented (T024-T030)
- ✅ All 4 quickstart workflows have integration tests (T010-T013)
- ✅ Dependency ordering follows TDD principles
- ✅ Parallel tasks properly identified with [P] markers
- ✅ File paths are specific and absolute within project structure

## Future Enhancements & Business Expansion

### Phase 4: Web UI Development (Post-CLI MVP)
**Transition from CLI-first to UI-enabled platform**

**Foundation Ready:**
- ✅ FastAPI callback server (T031) provides web backend foundation
- ✅ Service layer architecture enables API endpoints for UI
- ✅ Structured data models ready for frontend consumption

**UI Development Tasks (Future):**
```
UI001 [P] React/Vue frontend application with dashboard
UI002 [P] REST API endpoints for all CLI commands
UI003 [P] User authentication and session management
UI004 [P] Visual search criteria builder with filters
UI005 [P] Real-time progress tracking for bulk operations  
UI006 [P] Interactive prospect management and selection
UI007 [P] Drag-and-drop CSV import/export interface
UI008 [P] Credit usage analytics and visualization
UI009 [P] Workflow scheduling and automation dashboard
UI010 [P] Team collaboration and shared lead lists
```

**UI Architecture:**
```
User → Web Interface → FastAPI Backend → Same Services → SignalHire
     ↓
- Dashboard for search management
- Visual workflow builder  
- Real-time operation monitoring
- Team collaboration tools
- Analytics and reporting
```

### Phase 5: Multi-Platform Expansion
**Expand beyond SignalHire to complete lead generation suite**

**Platform Integration Roadmap:**

**5.1 LinkedIn Sales Navigator Integration**
```bash
signalhire-agent linkedin search --title "CTO" --company "startups"
signalhire-agent linkedin connect --message-template warm_intro.txt
```
- **Market**: 1M+ Sales Navigator users
- **Challenge**: LinkedIn anti-automation measures
- **Advantage**: Stagehand AI harder to detect than traditional tools
- **Revenue**: $20-50/month additional per user

**5.2 Apollo.io Integration**
```bash
signalhire-agent apollo search --intent "hiring" --company-size "50-200"
signalhire-agent apollo enrich --prospect-file leads.csv
```
- **Market**: 500K+ Apollo users (growing SMB segment)
- **Advantage**: Good API + our automation layer
- **Revenue**: $15-30/month additional per user

**5.3 ZoomInfo Integration**
```bash
signalhire-agent zoominfo search --scoops "funding" --location "SF Bay Area"
signalhire-agent zoominfo export --format crm-ready
```
- **Market**: 20K+ enterprise customers
- **Challenge**: Expensive platform, complex integration
- **Revenue**: $50-150/month additional per user

**5.4 Multi-Platform Workflows**
```bash
# Ultimate workflow - search across platforms
signalhire-agent workflow multi-platform \
  --platforms "signalhire,apollo,zoominfo,linkedin" \
  --criteria search.json \
  --dedupe \
  --output master_leads.csv
```

**Technical Architecture for Multi-Platform:**
```python
# Extensible platform adapter pattern
class PlatformAdapter:
    def login(self) -> bool
    def search(self, criteria: SearchCriteria) -> list[Prospect]
    def reveal_contacts(self, prospects: list[Prospect]) -> list[ContactInfo]
    def export_data(self, data: list[Prospect], format: str) -> str

# Platform implementations
SignalHireAdapter(PlatformAdapter)  # Current
LinkedInAdapter(PlatformAdapter)    # Phase 5.1
ApolloAdapter(PlatformAdapter)      # Phase 5.2
ZoomInfoAdapter(PlatformAdapter)    # Phase 5.3
```

### Phase 6: Enterprise & SaaS Features
**Scale to enterprise customers with advanced features**

**Enterprise Tasks (Future):**
```
ENT001 [P] Multi-tenant architecture with organization management
ENT002 [P] Role-based access control (RBAC) and permissions
ENT003 [P] White-label customization for agencies
ENT004 [P] Advanced analytics and reporting dashboard
ENT005 [P] CRM integrations (Salesforce, HubSpot, Pipedrive)
ENT006 [P] Workflow scheduling and automation engine
ENT007 [P] Email notification and alert system
ENT008 [P] Data backup and export capabilities
ENT009 [P] Audit logging and compliance features
ENT010 [P] Custom API endpoints for enterprise integrations
```

**Business Model Evolution:**
```
Stage 1: Tool for power users (CLI) - $0-49/month
Stage 2: SaaS for sales teams (Web UI) - $49-149/month  
Stage 3: Platform for agencies (White-label) - $399-999/month
Stage 4: Enterprise marketplace (Custom) - $1000+/month
```

### Revenue Projections & Market Analysis

**Pricing Strategy:**
```
Free Tier:         $0/month
- 100 prospects/month (SignalHire only)
- CLI access only
- Community support

Professional:      $49/month  
- 2,000 prospects/month
- CLI + Web UI
- SignalHire + 1 additional platform
- Email support

Business:          $149/month
- 10,000 prospects/month  
- All platform integrations
- Team collaboration features
- Priority support
- Custom workflows

Enterprise:        $399/month
- Unlimited prospects
- White-label option
- Custom integrations
- Dedicated support
- Advanced analytics
```

**Conservative Revenue Projections:**
```
Year 1 (SignalHire CLI):
- 100 free → 20 paid ($49) = $12K ARR
- 5 business ($149) = $9K ARR
- Total: ~$21K ARR

Year 2 (+ Web UI + LinkedIn):
- 500 free → 100 paid ($49) = $60K ARR
- 25 business ($149) = $45K ARR
- 3 enterprise ($399) = $14K ARR
- Total: ~$119K ARR

Year 3 (Multi-Platform):
- 2000 free → 400 paid ($49) = $235K ARR
- 100 business ($149) = $179K ARR  
- 15 enterprise ($399) = $72K ARR
- Total: ~$486K ARR

Aggressive Growth Potential: $2M+ ARR by Year 3
```

**Market Validation:**
- **Total Addressable Market**: $2B+ lead generation software
- **Immediate Market**: 50K+ SignalHire users
- **Expansion Market**: 1.5M+ across all platforms
- **Pain Points**: Time consumption, platform switching, credit inefficiency
- **Competitive Advantage**: First AI-powered multi-platform automation

### Technical Debt & Maintenance Considerations

**Ongoing Maintenance (Future):**
```
MAINT001 Platform UI change monitoring and Stagehand updates
MAINT002 API versioning and backward compatibility
MAINT003 Performance optimization for large-scale operations
MAINT004 Security audits and penetration testing
MAINT005 Database scaling and optimization
MAINT006 Monitoring and alerting infrastructure
MAINT007 Customer onboarding and success workflows
```

**Success Metrics:**
- **User Adoption**: Free-to-paid conversion >20%
- **Retention**: Monthly churn <5%
- **Performance**: <15min for 1000 prospect workflows
- **Reliability**: 99.5% uptime SLA
- **Customer Satisfaction**: NPS >50

### Open Source & Community Strategy

**Community Building:**
- **Open core model**: CLI tool open source, enterprise features paid
- **Developer ecosystem**: Plugin architecture for custom platforms
- **Community contributions**: Platform adapters, workflow templates
- **Documentation**: Comprehensive guides, video tutorials, API docs
- **Support**: Community forum, enterprise support tiers

This roadmap transforms our SignalHire CLI tool into a comprehensive lead generation automation platform, positioning us as the first AI-powered multi-platform solution in the market.
