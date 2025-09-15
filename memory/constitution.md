# AI Agent Development Constitution

## Current Project Status (Auto-Generated)
- **Active Branch**: 002-create-a-professional  
- **Last Commit**: 7264255 docs: Update CLAUDE.md [from Gemini]
- **Active Specification**: 002-create-a-professional
- **Task Progress**: 0/41 completed (0%)
- **Current Phase**: Starting
- **Implementation Status**: 11 models, 6 services, 9 CLI files, 14 libraries
- **Test Coverage**: 6 contract, 5 integration, 14 unit tests
- **Last Updated**: 2025-09-11 21:43:27

## Agent Task Distribution (Current)
- **@claude**: 8 pending tasks (integration & architecture)
- **@copilot**: 15 pending tasks (implementation & models)  
- **@codex**: 9 pending tasks (testing & debugging)
- **@gemini**: 0 pending tasks (documentation & research)

## Active Technology Stack
  Language Version    Python 3.11 (confirmed in pyproject.toml)   Primary Dependencies    httpx (API client), Click (CLI), pandas (CSV export), Stagehand (optional browser automation)   Storage    In-memory session storage, CSV file exports (no database)     Testing    pytest with contract tests (tests contract ), unit tests, integration tests   Target Platform    Linux servers, local development environments   Project Type    single (CLI application with API integration)   

## Current Implementation Structure
```
src/
├── .
├── ..
├── cli
├── lib
├── models
├── services
├── signalhire_agent

tests/  
├── .
├── ..
├── README.md
├── __pycache__
├── browser
```

## Core Development Principles

### I. Spec-Driven Development (ACTIVE)
- ✅ Specifications become executable and drive implementation
- ✅ Follow the spec-kit methodology for all new features  
- ✅ Reference specs/${ACTIVE_SPEC:-current}/ for current feature requirements
- ✅ Use contracts/ directory for API and interface specifications
- **Status**: Coordination system pending

### II. Multi-Agent Coordination (IMPLEMENTED)
- ✅ Use @ assignments in tasks.md for agent coordination
- ✅ Coordinator Claude manages programmatic agent execution (scripts/agent-coordinator.py)
- ✅ Worker Claude handles complex integration tasks  
- ✅ Respect agent capabilities and limitations
- **Status**: Agent coordinator pending

### III. Test-First Development (ACTIVE)
- ✅ All contract and integration tests must be written first
- ✅ Tests must fail before implementation begins
- ✅ Follow TDD red-green-refactor cycle strictly
- ✅ Use Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: pydantic-settings in c:\users\user\appdata\roaming\python\python312\site-packages (2.10.1)
Requirement already satisfied: pydantic>=2.7.0 in c:\users\user\appdata\roaming\python\python312\site-packages (from pydantic-settings) (2.9.2)
Requirement already satisfied: python-dotenv>=0.21.0 in c:\users\user\appdata\roaming\python\python312\site-packages (from pydantic-settings) (1.0.1)
Requirement already satisfied: typing-inspection>=0.4.0 in c:\users\user\appdata\roaming\python\python312\site-packages (from pydantic-settings) (0.4.1)
Requirement already satisfied: annotated-types>=0.6.0 in c:\users\user\appdata\roaming\python\python312\site-packages (from pydantic>=2.7.0->pydantic-settings) (0.7.0)
Requirement already satisfied: pydantic-core==2.23.4 in c:\users\user\appdata\roaming\python\python312\site-packages (from pydantic>=2.7.0->pydantic-settings) (2.23.4)
Requirement already satisfied: typing-extensions>=4.6.1 in c:\users\user\appdata\roaming\python\python312\site-packages (from pydantic>=2.7.0->pydantic-settings) (4.12.2)

=================================== ERRORS ====================================
_____________ ERROR collecting tests/browser/test_live_browser.py _____________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\browser\test_live_browser.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\browser\test_live_browser.py:17: in <module>
    from services.browser_client import StagehandClient, BrowserConfig, LoginCredentials
src\services\browser_client.py:11: in <module>
    from ..models.browser_config import BrowserConfig
E   ImportError: attempted relative import beyond top-level package
____________ ERROR collecting tests/contract/test_cli_interface.py ____________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\contract\test_cli_interface.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\contract\test_cli_interface.py:17: in <module>
    from src.cli.export_commands import export_data
E   ImportError: cannot import name 'export_data' from 'src.cli.export_commands' (\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\cli\export_commands.py)
__________ ERROR collecting tests/contract/test_scroll_search_api.py __________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\contract\test_scroll_search_api.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\contract\test_scroll_search_api.py:14: in <module>
    from src.models.search_result import SearchResult, PaginationState
E   ModuleNotFoundError: No module named 'src.models.search_result'
________ ERROR collecting tests/contract/test_stagehand_automation.py _________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\contract\test_stagehand_automation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\contract\test_stagehand_automation.py:14: in <module>
    from src.lib.browser_manager import BrowserManager
E   ImportError: cannot import name 'BrowserManager' from 'src.lib.browser_manager' (\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\browser_manager.py)
________ ERROR collecting tests/integration/test_browser_automation.py ________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\integration\test_browser_automation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\test_browser_automation.py:14: in <module>
    from src.lib.browser_client import BrowserClient
E   ModuleNotFoundError: No module named 'src.lib.browser_client'
__________ ERROR collecting tests/integration/test_error_handling.py __________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\integration\test_error_handling.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\test_error_handling.py:14: in <module>
    from src.services.search_service import SearchService
E   ModuleNotFoundError: No module named 'src.services.search_service'
__________ ERROR collecting tests/integration/test_rate_limiting.py ___________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\integration\test_rate_limiting.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\test_rate_limiting.py:12: in <module>
    from src.lib.rate_limiter import RateLimiter
E   ImportError: cannot import name 'RateLimiter' from 'src.lib.rate_limiter' (\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\rate_limiter.py)
____ ERROR collecting tests/integration/test_search_to_export_workflow.py _____
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\integration\test_search_to_export_workflow.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\integration\test_search_to_export_workflow.py:14: in <module>
    from src.services.search_service import SearchService
E   ModuleNotFoundError: No module named 'src.services.search_service'
_________ ERROR collecting tests/unit/test_browser_errors_manager.py __________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\unit\test_browser_errors_manager.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\unit\test_browser_errors_manager.py:5: in <module>
    from signalhire_agent.lib.browser_errors import (
E   ModuleNotFoundError: No module named 'signalhire_agent.lib'
_______________ ERROR collecting tests/unit/test_debug_tools.py _______________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\unit\test_debug_tools.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\unit\test_debug_tools.py:5: in <module>
    from signalhire_agent.lib.debug_tools import dump_session_artifacts
E   ModuleNotFoundError: No module named 'signalhire_agent.lib'
_________________ ERROR collecting tests/unit/test_models.py __________________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\unit\test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\unit\test_models.py:4: in <module>
    from signalhire_agent.models.search_criteria import SearchCriteria
E   ModuleNotFoundError: No module named 'signalhire_agent.models'
__________ ERROR collecting tests/unit/test_service_rate_limiter.py ___________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\unit\test_service_rate_limiter.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\unit\test_service_rate_limiter.py:5: in <module>
    from signalhire_agent.services.rate_limiter import RateLimiterService
E   ModuleNotFoundError: No module named 'signalhire_agent.services'
________________ ERROR collecting tests/unit/test_services.py _________________
ImportError while importing test module '\\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\tests\unit\test_services.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\unit\test_services.py:6: in <module>
    from signalhire_agent.lib.rate_limiter import AsyncTokenBucket
E   ModuleNotFoundError: No module named 'signalhire_agent.lib'
============================== warnings summary ===============================
C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in AgentClientOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in AgentHandlerOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in ActOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_client_options" in ActOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in ObserveOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_client_options" in ObserveOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in ExtractOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_client_options" in ExtractOptions has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_api_key" in StagehandConfig has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_client_options" in StagehandConfig has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in StagehandConfig has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_config.py:291
C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_config.py:291
  C:\Users\user\AppData\Roaming\Python\Python312\site-packages\pydantic\_internal\_config.py:291: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

src\cli\config_commands.py:75
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\cli\config_commands.py:75: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @validator('log_level')

src\cli\config_commands.py:83
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\cli\config_commands.py:83: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @validator('default_export_format')

src\lib\config.py:57
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\config.py:57: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @validator('email')

src\lib\config.py:71
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\config.py:71: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @validator('port')

src\lib\config.py:103
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\config.py:103: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @validator('output_dir')

src\lib\config.py:139
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\config.py:139: PydanticDeprecatedSince20: Pydantic V1 style `@root_validator` validators are deprecated. You should migrate to Pydantic V2 style `@model_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @root_validator(pre=True)

src\lib\config.py:152
  \\wsl.localhost\Ubuntu\home\vanman2025\signalhireagent\src\lib\config.py:152: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.9/migration/
    @validator('environment', pre=True)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests/browser/test_live_browser.py
ERROR tests/contract/test_cli_interface.py
ERROR tests/contract/test_scroll_search_api.py
ERROR tests/contract/test_stagehand_automation.py
ERROR tests/integration/test_browser_automation.py
ERROR tests/integration/test_error_handling.py
ERROR tests/integration/test_rate_limiting.py
ERROR tests/integration/test_search_to_export_workflow.py
ERROR tests/unit/test_browser_errors_manager.py
ERROR tests/unit/test_debug_tools.py
ERROR tests/unit/test_models.py
ERROR tests/unit/test_service_rate_limiter.py
ERROR tests/unit/test_services.py
!!!!!!!!!!!!!!!!!! Interrupted: 13 errors during collection !!!!!!!!!!!!!!!!!!!
20 warnings, 13 errors in 12.17s
Using Python: /mnt/c/Python312/python.exe
✅ pandas available
✅ httpx available
✅ pydantic available
✅ fastapi available
✅ email-validator available
✅ structlog available
✅ click available
✅ python-dotenv available
✅ uvicorn available
❌ pydantic-settings missing
✅ playwright available

Missing packages: pydantic-settings
Installing missing packages: pydantic-settings
✅ All Python dependencies are available
✅ Stagehand already available
✅ All dependencies are available
Running: /mnt/c/Python312/python.exe -m pytest with appropriate markers (unit, integration, contract, browser, slow)
- **Current**: 6 contract tests, 5 integration tests implemented

### IV. Architecture & Integration Focus (IN PROGRESS)
- ✅ Prefer async/await patterns for I/O operations
- ✅ Use structured logging with JSON format  
- ✅ Implement proper error handling and rate limiting
- ✅ Follow existing code patterns and conventions
- **Current**: 6 services, 14 libraries implemented

### V. Script Documentation Standards (ENFORCED)
- ✅ **ALL script files MUST include standardized headers** (see `docs/developer/SCRIPT_HEADER_STANDARD.md`)
- ✅ **Required fields**: PURPOSE, USAGE, PART OF, CONNECTS TO
- ✅ **Headers serve as inline documentation** for maintenance and onboarding
- ✅ **Clear system connections** must be documented in every script
- ✅ **Enforcement**: New scripts must have headers, existing scripts updated when modified
- **Standard**: All agents must follow header format for maintainability

### VI. Local Deployment & Testing Standards (CRITICAL)
- ✅ **ALL production changes MUST be tested locally first** using production build system
- ✅ **Required local testing workflow**: Build → Install → Validate → Test CLI → Commit
- ✅ **Production build testing**: `./scripts/build/build-production.sh test-build --latest --force`
- ✅ **Environment isolation**: Virtual environments for production testing
- ✅ **End-user validation**: Test all CLI commands work in production environment
- ✅ **Deployment validation**: Verify .env configuration, dependencies, and functionality
- **Protocol**: Never release without local production build verification

### VII. Quality Assurance Pipeline (MANDATORY)
- ✅ **Code quality gates**: Lint (ruff), type-check (mypy), format (black) before commit
- ✅ **Test coverage requirements**: ≥80% coverage on new/changed code
- ✅ **Integration testing**: httpx mocking to avoid burning API credits during development
- ✅ **Contract testing**: Browser automation tests marked appropriately (slow/browser)
- ✅ **Production readiness**: Local deployment testing before any release
- **Standard**: All quality gates must pass before code integration

### VIII. Documentation & Shared Memory (ACTIVE)
- ✅ Keep agent context files synchronized (use /update-memory)
- ✅ Update constitution.md when processes change (auto-generated)
- ✅ Document coordination decisions in AI_COORDINATION_PLAN.md  
- ✅ Use memory/ directory for shared knowledge


## Spec-Kit Development Workflow

### What is Spec-Kit?
Spec-Kit is a toolkit for **Spec-Driven Development** - an approach where specifications become executable and drive the implementation process instead of being discarded after initial coding.

### Core Philosophy
- **"Specifications become executable"** - specs are living documents, not throwaway artifacts
- **Intent-driven development** - focus on "what" before "how"
- **Specifications drive implementation** - plans and contracts guide code generation

### Available Commands
```bash
# Check spec-kit installation and requirements
uvx --from git+https://github.com/github/spec-kit.git specify check

# Initialize new specification (if needed for new features)
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>

# Access spec-kit help
uvx --from git+https://github.com/github/spec-kit.git specify --help
```

### Project Structure (Already Generated)
This project was initialized with spec-kit and follows its structure:
```
specs/001-looking-to-build/    # Current feature specification
├── spec.md                    # Feature specification
├── plan.md                    # Technical implementation plan  
├── tasks.md                   # Detailed task breakdown (T001-T040)
├── quickstart.md             # User workflows
├── research.md               # Research and decisions
├── data-model.md             # Data entities and relationships
└── contracts/                # API and interface contracts
    ├── search-api.md
    ├── person-api.md
    ├── credits-api.md
    ├── cli-interface.md
    ├── stagehand-automation.md
    └── scroll-search-api.md

templates/                     # Spec-kit templates
memory/                       # Shared knowledge (this file)
```

### Development Phases (From Spec-Kit)
1. **0-to-1 Development**: Generate from scratch using specifications
2. **Creative Exploration**: Parallel implementations and experimentation  
3. **Iterative Enhancement**: Modernize and enhance existing systems

### Agent Usage Guidelines
**All AI agents should:**
- Reference `specs/001-looking-to-build/tasks.md` for current task breakdown
- Follow the contracts in `specs/001-looking-to-build/contracts/` 
- Implement according to `specs/001-looking-to-build/plan.md`
- Update task completion status in `tasks.md` as work progresses

**For new features:**
- Use spec-kit to generate new spec directories
- Follow the established spec-driven workflow
- Generate tasks, contracts, and implementation plans before coding

### Integration with AI Coordination
Spec-kit specifications work with our AI coordination strategy:
- **@claude**: Handles architecture and multi-component integration per specs
- **@copilot**: Implements individual components following contract specifications
- **@codex**: Develops tests based on contract specifications (TDD approach)
- **@gemini**: Creates documentation and researches implementation approaches

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->