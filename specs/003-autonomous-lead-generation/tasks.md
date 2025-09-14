# Tasks: Autonomous Lead Generation System with Agentic MCP Server (Streamlined MVP)

**Input**: Design documents from `/specs/003-autonomous-lead-generation/`
**Prerequisites**: plan.md (required)

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Generate tasks by category: setup, tests, core, integration, polish
3. Apply task rules: tests before implementation, parallel where possible
4. Number tasks sequentially (T001, T002...)
5. Validate task completeness
```

## MVP Task List (Phase A: Backend-Only MVP)

- [ ] T001 [P] Refactor SignalHire API client, data models, and business logic into shared library `src/lib/signalhire_core.py` (extract SignalHireClient, SearchService, RevealService from CLI commands, keep Click interfaces separate) (@copilot)
- [ ] T002 [P] Add Supabase models for workflow rules, job state, audit logs in `src/models/workflow.py` (@claude)
- [ ] T003 [P] Add APScheduler and cost control dependencies to project (@copilot)
- [ ] T004 [P] Write contract test for MCP tool: `search_by_query()` in `tests/contract/test_mcp_search_by_query.py` (@codex)
- [ ] T005 [P] Write contract test for MCP tool: `scroll_search()` in `tests/contract/test_mcp_scroll_search.py` (@codex)
- [ ] T006 [P] Write contract test for MCP tool: `reveal_identifier()` in `tests/contract/test_mcp_reveal_identifier.py` (@codex)
- [ ] T007 [P] Write contract test for MCP tool: `get_credits()` in `tests/contract/test_mcp_get_credits.py` (@codex)
- [ ] T008 [P] Write contract test for MCP tool: `export_to_csv()` in `tests/contract/test_mcp_export_to_csv.py` (@codex)
- [ ] T009 [P] Write contract test for MCP tool: `add_rule()` in `tests/contract/test_mcp_add_rule.py` (@codex)
- [ ] T010 [P] Write contract test for MCP tool: `run_rule()` in `tests/contract/test_mcp_run_rule.py` (@codex)
- [ ] T011 [P] Write contract test for MCP tool: `get_run_status()` in `tests/contract/test_mcp_get_run_status.py` (@codex)
- [ ] T012 Implement FastAPI MCP server app in `src/services/mcp_server.py` (single service hosting MCP endpoints) (@copilot)
- [ ] T013 Implement `search_by_query()` MCP tool using shared library, with Pydantic models, rate limiting, and integrated cost estimation (@copilot)
- [ ] T014 Implement `scroll_search()` MCP tool using shared library, with pagination semantics and requestId/scrollId state management (@copilot)
- [ ] T015 Implement `reveal_identifier()` MCP tool using shared library, with integrated credit pre-checks, daily caps, and deduplication via UID tracking (@copilot)
- [ ] T016 Implement `get_credits()` MCP tool using shared library, with circuit breakers and credit threshold warnings (@copilot)
- [ ] T017 Implement `export_to_csv()` MCP tool using shared library, with integrated cost estimation and file size limits (@copilot)
- [ ] T021 Optimize MCP tool performance: analyze response times, memory usage, and API call efficiency (@qwen)
- [ ] T022 Optimize cost algorithms: improve credit estimation accuracy and reduce API calls through intelligent caching (@qwen)
- [ ] T018 Implement `add_rule()` MCP tool for workflow rule management with integrated safety limits and cost estimation per rule (@copilot)
- [ ] T019 Implement `run_rule()` MCP tool with APScheduler integration, state tracking, and integrated per-rule cost caps (@copilot)
- [ ] T020 Implement `get_run_status()` MCP tool with PENDING/RUNNING/COMPLETED/FAILED states and cost tracking (@copilot)
- [ ] T023 Integration test: httpx mocking for all MCP tools to avoid burning credits in `tests/integration/test_mcp_mocked.py` (@codex)
- [ ] T024 Single live E2E smoke test: tiny search with zero reveals in `tests/integration/test_live_smoke.py` (@codex)

## Phase B: Agent Integration

- [ ] T025 Implement agent abstraction layer in `src/lib/agent_interface.py` that enables agents to invoke MCP tools through structured API calls, supporting Claude Code SDK and Gemini CLI backends with consistent tool calling interface (@claude)
- [ ] T026 Implement session state management in Supabase for: workflow rules, execution history, pagination tokens (requestId/scrollId with TTL), credit usage tracking, and deduplication records by UID (@claude)
- [ ] T027 Integration test: agent workflow orchestration using MCP tools in `tests/integration/test_agent_workflow.py` (@claude)

## Phase C: Basic Monitoring

- [ ] T028 Implement simple monitoring dashboard FastAPI endpoints in `src/services/monitoring.py` (@copilot)
- [ ] T029 Add structured logging with request_id/workflow_id context throughout MCP server (@copilot)

## Polish

- [ ] T030 [P] Add unit tests for shared library functions in `tests/unit/test_signalhire_core.py` (@codex)
- [ ] T031 [P] Add unit tests for cost control systems in `tests/unit/test_cost_controls.py` (@codex)
- [ ] T032 [P] Optimize database queries and Supabase integration patterns for better performance (@claude)
- [ ] T033 [P] Update documentation for MCP server and agent workflows in `docs/mcp-server.md` (@gemini)
- [ ] T034 [P] Update quickstart for Supabase + Railway deployment in `specs/003-autonomous-lead-generation/quickstart.md` (@gemini)
## Parallel Execution Guidance
- Tasks marked [P] can be executed in parallel by different agents.
- Phase A (T001-T023) can be fully parallelized within categories.
- Implementation tasks follow TDD: contract tests must exist and fail before implementation.

## Agent Assignment
- @copilot: Project setup, MCP tool implementation, cost controls, monitoring
- @codex: Contract/unit/integration tests, mocking, live E2E testing
- @claude: Agent abstraction layer, session management, workflow orchestration, Supabase integration, deployments
- @qwen: Performance optimization, algorithm improvements, cost efficiency analysis
- @gemini: Documentation, quickstart updates, operational guides
