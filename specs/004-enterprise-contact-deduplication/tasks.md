# Tasks: Contact Deduplication and Search Optimi- [x] T014 Performance test: process 7,000+ contacts in under 5 minutes in `tests/performance/test_large_file.py` [P]ation

**Input**: Design documents from `/specs/004-enterprise-contact-deduplication/`
**Prerequisites**: plan.md (required), research.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: tech stack, libraries, structure
2. Load research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: integration tests for deduplication, filtering, resume
   → Core: deduplication logic, filtering logic, CLI commands
   → Integration: logging, progress tracking, CSV export
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---


### Tasks

- [x] T001 Setup Python environment and install dependencies (Click, pandas, pytest) [P]
- [x] T002 Add linting and type checking (ruff, mypy) [P]
- [x] T003 Create CLI command skeleton for `signalhire dedupe`, `analyze`, and `filter` in `src/cli/` [P]
- [x] T004 Write integration test for deduplication (merging JSON files, removing duplicates by uid/LinkedIn URL) in `tests/integration/test_deduplication.py` [P]
- [x] T005 Implement deduplication logic in `src/services/deduplication_service.py`
- [x] T006 Write integration test for job title filtering in `tests/integration/test_filtering.py` [P]
- [x] T007 Implement filtering logic in `src/services/filter_service.py`
- [x] T008 Write integration test for resume/reveal progress in `tests/integration/test_resume.py` [P]
- [x] T009 Implement progress tracking and resume logic in `src/services/progress_service.py`
- [x] T010 Add logging and error handling in `src/lib/logging.py` [P]
- [x] T011 Implement CSV export with deduplication metadata in `src/lib/csv_exporter.py` [P]
- [x] T012 Write unit tests for deduplication, filtering, and progress tracking in `tests/unit/` [P]
- [x] T013 Add CLI help text, usage examples, and polish docs in `docs/cli-commands.md` [P]
- [x] T014 Performance test: process 100 + contacts in under 1 minutes in `tests/performance/test_large_file.py` [P]
- [x] T015 Final review: validate requirements coverage and update documentation [P]

---

## Parallel Execution Examples
- T001, T002, T003, T004, T006, T008, T010, T011, T012, T013, T014, T015 can run in parallel
- T005 depends on T004
- T007 depends on T006
- T009 depends on T008

---

## Dependency Notes
- Setup and test tasks can run in parallel
- Core logic tasks depend on corresponding tests (TDD)
- Integration and polish tasks can run after core logic is implemented

---

# END
