# Implementation Plan: API-Focused Professional Agent

**Branch**: `002-create-a-professional` | **Date**: 2025-09-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-create-a-professional/spec.md`

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
**Primary Requirement**: Enhance existing SignalHire agent to prioritize API-based contact reveals while maintaining browser automation as optional capability for bulk operations (1000+ contacts).

**Technical Approach**: The agent already has comprehensive API integration (`SignalHireClient.reveal_contact()`, `batch_reveal_contacts()`) and CLI commands (`reveal_commands.py`) that support both API and browser modes. This refactoring will optimize the API-first workflow, improve documentation, and streamline the user experience while keeping browser automation available for high-volume scenarios.

## Technical Context
**Language/Version**: Python 3.11 (confirmed in pyproject.toml)
**Primary Dependencies**: httpx (API client), Click (CLI), pandas (CSV export), Stagehand (optional browser automation)
**Storage**: In-memory session storage, CSV file exports (no database)  
**Testing**: pytest with contract tests (tests/contract/), unit tests, integration tests
**Target Platform**: Linux servers, local development environments
**Project Type**: single (CLI application with API integration)  
**Performance Goals**: API responses <1 second, CSV exports <10 seconds for 1000 records
**Constraints**: 100 contacts/day API limit, memory usage <100MB for large exports
**Scale/Scope**: Single user CLI tool, up to 10,000 prospects per session

## Constitution Check

### Simplicity Requirements ✅
- **Single Purpose**: API-first contact reveal with clear 100/day limit
- **Minimal Dependencies**: Uses existing httpx, Click, pandas (no new deps)
- **Clear Interface**: Enhance existing CLI commands with better defaults

### Architecture Requirements ✅  
- **Layered Design**: CLI → Services → API Client → SignalHire API (existing)
- **Error Boundaries**: API errors handled at service layer with user-friendly messages
- **Async/Await**: Already implemented throughout the stack

### Testing Requirements ✅
- **Contract Tests**: Already exist in tests/contract/ for all APIs
- **Unit Tests**: Existing unit tests for individual components
- **Integration Tests**: End-to-end workflow tests already implemented

### Versioning Requirements ✅
- **Backward Compatibility**: All existing CLI commands continue to work
- **Feature Flags**: Browser mode remains available via --browser flag
- **Migration Path**: No breaking changes to existing workflows

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project) - Current structure already matches this pattern

## Phase 0: Research Complete ✅
*See [research.md](./research.md)*

The research phase identified that API-first approach is optimal for reliability and user experience, while browser automation remains available for bulk operations. All technical decisions are documented with rationale for the enhanced approach.

**Output**: ✅ research.md with API-first strategy and technology decisions

## Phase 1: Design & Contracts Complete ✅
*All artifacts created and validated*

1. **✅ Data Model**: [data-model.md](./data-model.md) - Enhanced API client architecture with queue management and rate limiting
2. **✅ API Contracts**: [contracts/](./contracts/) - Comprehensive API client, CLI interface, and CSV export contracts  
3. **✅ Quickstart Guide**: [quickstart.md](./quickstart.md) - Complete user guide emphasizing API-first workflow
4. **✅ Agent Context**: Ready for .github/copilot-instructions.md update

**Output**: ✅ All design artifacts complete and constitution-compliant

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy for API-First Enhancement**:

1. **Documentation Tasks** (High Priority):
   - Update CLI help text to emphasize API-first approach
   - Enhance README with API vs browser mode guidance
   - Update .github/copilot-instructions.md with enhanced context
   - Add rate limiting guidance to user documentation

2. **CLI Enhancement Tasks** (Medium Priority):
   - Set API mode as default in reveal commands
   - Add --api-only flag to disable browser fallback
   - Improve error messages for rate limit scenarios
   - Add daily usage warnings in CLI output

3. **API Client Optimization Tasks** (Medium Priority):
   - Enhance batch operation progress reporting
   - Add queue management for large batches within API limits
   - Improve retry logic for transient API failures
   - Add credit pre-check validation before batch operations

4. **User Experience Tasks** (Medium Priority):
   - Add interactive credit confirmation prompts
   - Implement better progress bars for API operations
   - Add daily usage tracking in status commands
   - Improve CSV export naming with timestamps

5. **Testing & Validation Tasks** (Low Priority):
   - Update integration tests to prioritize API mode
   - Add performance benchmarks for API vs browser modes
   - Validate quickstart guide with fresh installation
   - Test rate limiting behavior at boundaries

**Key Task Categories**:
- Documentation updates (5-7 tasks)
- CLI improvements (6-8 tasks) 
- API optimizations (4-6 tasks)
- UX enhancements (5-7 tasks)
- Testing updates (3-5 tasks)

**Ordering Strategy**:
- Priority order: Documentation → CLI → API → UX → Testing
- TDD approach: Update tests alongside implementation 
- Independence: Most tasks can run in parallel within categories

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations detected - all requirements met with existing architecture*

No complexity deviations required for this enhancement.


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
