# Tasks: API-Focused Professional Agent

**Input**: Design documents from `/specs/002-create-a-professional/`
**Prerequisites**: plan.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅), quickstart.md (✅)

## Execution Flow (main)
```
1. ✅ Load plan.md from feature directory
   → Tech stack: Python 3.11, httpx, Click, pandas, Stagehand (optional)
   → Structure: Single project (src/, tests/ at repository root)
2. ✅ Load design documents:
   → data-model.md: SignalHireClient, RateLimiter, ProspectStore entities
   → contracts/: api-client.md, cli-interface.md, csv-export.md
   → research.md: API-first strategy with browser fallback
   → quickstart.md: Integration test scenarios
3. ✅ Generate tasks by category: Setup → Tests → Core → Integration → Polish
4. ✅ Apply task rules: Different files [P], TDD approach
5. ✅ Number tasks sequentially (T001, T002...)
```

## Format: `[ID] [P?] @agent Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **@agent**: Assigned AI agent (@copilot, @claude, @codex, @gemini)
- Include exact file paths in descriptions

## Agent Assignments

### @copilot (GitHub Copilot) - 12 tasks
**Specialization**: CLI interfaces, configuration, user experience
- T001, T003: Configuration and setup files
- T010-T013: CLI command enhancements and defaults
- T018-T019: User experience improvements (CLI-focused)
- T022, T024: Error handling and rate limiting integration
- T027, T032: Testing and code cleanup

### @claude (Claude Code) - 8 tasks  
**Specialization**: Documentation, integration workflows, performance
- T002: README documentation
- T007-T009: Integration tests for workflows
- T020: CSV export improvements
- T025: Configuration management
- T028, T030: Performance benchmarks and validation

### @codex (OpenAI Codex) - 8 tasks
**Specialization**: API clients, contract testing, technical implementation
- T004-T006: Contract tests for APIs
- T014-T017: API client optimizations
- T023: Logging implementation
- T026: Unit tests for rate limiting

### @gemini (Google Gemini) - 4 tasks
**Specialization**: Documentation, validation, boundary testing
- T021: Daily usage tracking display
- T029: CLI command documentation with examples
- T031: Rate limiting boundary testing
- Alternative assignments available for load balancing

## Phase 3.1: Setup & Documentation

- [x] T001 @copilot Update .github/copilot-instructions.md with API-first approach context
- [x] T002 [P] @claude Update README.md with API vs browser mode guidance and rate limiting info
- [x] T003 [P] @copilot Configure ruff.toml and mypy configuration for enhanced code quality

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T004 [P] @codex Enhanced API client contract test in tests/contract/test_api_client_enhanced.py
- [x] T005 [P] @codex CLI interface contract test for API-first defaults in tests/contract/test_cli_api_first.py  
- [x] T006 [P] @codex CSV export contract test for enhanced formats in tests/contract/test_csv_export_enhanced.py
- [x] T007 [P] @claude Integration test for quickstart workflow in tests/integration/test_quickstart_workflow.py
- [x] T008 [P] @claude Integration test for credit management workflow in tests/integration/test_credit_management.py
- [x] T009 [P] @claude Integration test for API rate limiting behavior in tests/integration/test_rate_limiting.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### CLI Enhancements
- [x] T010 @copilot Set API mode as default in src/cli/reveal_commands.py
- [x] T011 @copilot Add --api-only flag to disable browser fallback in src/cli/reveal_commands.py  
- [x] T012 [P] @copilot Add daily usage warnings and credit checks in src/cli/status_commands.py
- [x] T013 [P] @copilot Improve CLI help text to emphasize API-first approach in src/cli/main.py

### API Client Optimizations  
- [x] T014 [P] @codex Enhance batch operation progress reporting in src/services/signalhire_client.py
- [x] T015 [P] @codex Add queue management for large batches within API limits in src/services/signalhire_client.py
- [x] T016 [P] @codex Improve retry logic for transient API failures in src/services/signalhire_client.py
- [x] T017 [P] @codex Add credit pre-check validation before batch operations in src/services/signalhire_client.py

### User Experience Improvements
- [x] T018 [P] @copilot Add interactive credit confirmation prompts in src/cli/reveal_commands.py
- [x] T019 [P] @copilot Implement better progress bars for API operations in src/cli/reveal_commands.py
- [x] T020 [P] @claude Improve CSV export naming with timestamps in src/services/csv_exporter.py
- [x] T021 [P] @gemini Add daily usage tracking display in src/cli/status_commands.py

## Phase 3.4: Integration & Error Handling

- [x] T022 @copilot Improve error messages for rate limit scenarios across CLI commands
- [x] T023 @codex Add comprehensive logging for API operations and user actions
- [x] T024 @copilot Integrate enhanced rate limiter with daily usage tracking
- [x] T025 @claude Add configuration management for API vs browser preferences

## Phase 3.5: Polish & Validation

- [x] T026 [P] @codex Unit tests for enhanced rate limiting in tests/unit/test_rate_limiter_enhanced.py
- [x] T027 [P] @copilot Unit tests for CLI user experience features in tests/unit/test_cli_ux.py
- [x] T028 [P] @claude Performance benchmarks for API vs browser modes in tests/performance/test_mode_comparison.py
- [x] T029 [P] @gemini Update CLI command documentation with examples in docs/cli-commands.md
- [x] T030 @claude Validate quickstart guide with fresh installation
- [x] T031 @gemini Test rate limiting behavior at daily boundaries
- [ ] T032 @copilot Remove code duplication and optimize imports

## Phase 3.6: Follow-up Enhancements (@codex)

- [ ] T033 @codex Add CLI scroll pagination support for Search API (search --continue-search uses requestId + scrollId)
- [ ] T034 @codex Add scheduling examples and scripts for daily runs (cron, DO App Platform, Vercel)
- [x] T035 @codex Preserve agent documentation in production build (devops/deploy/commands/build-production.sh)
- [x] T036 @codex Add search command shortcut for heavy equipment templates (src/cli/search_commands.py)
- [x] T037 @codex Normalize export path display for WSL outputs (src/lib/common.py, src/cli/export_commands.py)
- [x] T038 @codex Ensure production build bundles pydantic-settings and CLI wrapper uses venv python (devops/deploy/commands/build-production.sh, src/lib/validation.py)

## Dependencies

### Critical Path
- Setup (T001-T003) before everything
- Tests (T004-T009) before implementation (T010-T025)
- CLI enhancements (T010-T013) before UX improvements (T018-T021)
- API optimizations (T014-T017) before integration (T022-T025)
- Core implementation before polish (T026-T032)

### Specific Dependencies
- T010, T011 block T018, T019 (same file: reveal_commands.py)
- T014-T017 block T024 (signalhire_client.py enhancements before integration)
- T022 depends on T010-T021 (error handling needs CLI enhancements)
- T030 depends on T001-T002 (documentation must be updated first)

## Parallel Execution Examples

### Phase 3.2 (Tests) - All can run in parallel:
```bash
# Launch T004-T009 together:
@codex: "Enhanced API client contract test in tests/contract/test_api_client_enhanced.py"
@codex: "CLI interface contract test for API-first defaults in tests/contract/test_cli_api_first.py"
@codex: "CSV export contract test for enhanced formats in tests/contract/test_csv_export_enhanced.py"
@claude: "Integration test for quickstart workflow in tests/integration/test_quickstart_workflow.py"
@claude: "Integration test for credit management workflow in tests/integration/test_credit_management.py"
@claude: "Integration test for API rate limiting behavior in tests/integration/test_rate_limiting.py"
```

### Phase 3.3 (Independent Files) - Groups can run in parallel:
```bash
# Group 1: CLI files (@copilot specialization)
@copilot: "Add daily usage warnings and credit checks in src/cli/status_commands.py"
@copilot: "Improve CLI help text to emphasize API-first approach in src/cli/main.py"

# Group 2: API client optimizations (@codex specialization)
@codex: "Enhance batch operation progress reporting in src/services/signalhire_client.py"
@codex: "Add queue management for large batches within API limits in src/services/signalhire_client.py"

# Group 3: User experience (mixed assignments)
@claude: "Improve CSV export naming with timestamps in src/services/csv_exporter.py"
@gemini: "Add daily usage tracking display in src/cli/status_commands.py"
```

### Phase 3.5 (Polish) - Most can run in parallel:
```bash
# Launch T026-T029 together:
@codex: "Unit tests for enhanced rate limiting in tests/unit/test_rate_limiter_enhanced.py"
@copilot: "Unit tests for CLI user experience features in tests/unit/test_cli_ux.py"  
@claude: "Performance benchmarks for API vs browser modes in tests/performance/test_mode_comparison.py"
@gemini: "Update CLI command documentation with examples in docs/cli-commands.md"
```

## Task Details

### High Priority Tasks (Complete First)
- **T001-T003**: Documentation and setup for user guidance
- **T004-T009**: Test coverage for all new functionality
- **T010-T013**: CLI defaults to prioritize API approach
- **T014-T017**: API client reliability and performance

### Medium Priority Tasks  
- **T018-T021**: User experience improvements
- **T022-T025**: Integration and error handling
- **T026-T029**: Test coverage and documentation

### Low Priority Tasks
- **T030-T032**: Validation and cleanup

## Notes
- [P] tasks target different files with no dependencies
- Verify all tests fail before implementing features
- Commit after each task completion
- Focus on enhancing existing functionality rather than rewriting
- Maintain backward compatibility with browser automation mode

## Validation Checklist
*GATE: All items must be checked before considering tasks complete*

- [ ] All contracts (api-client, cli-interface, csv-export) have corresponding tests
- [ ] All entities (SignalHireClient, RateLimiter, ProspectStore) have enhancement tasks
- [ ] All tests come before implementation (T004-T009 before T010+)
- [ ] Parallel tasks truly target independent files
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
- [ ] Quickstart scenarios covered by integration tests
- [ ] API-first approach prioritized throughout task list
