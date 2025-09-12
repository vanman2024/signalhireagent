# GitHub Copilot Instructions for signalhireagent

Auto-generated from all feature plans. Last updated: 2025-09-11

## Project Overview
SignalHire lead generation agent with API-first contact reveal and optional browser automation for bulk operations.

## Active Technologies
- Python 3.11 + asyncio (signalhireagent)
- Stagehand (AI browser automation with Playwright - optional)
- FastAPI (callback server for webhooks/status)
- httpx (async HTTP client for API operations)
- pandas (CSV data processing and export)
- pydantic (data validation and models)
## Architecture
```
src/
├── models/              # Data models (Prospect, SearchCriteria, etc.)
├── services/            # Business logic (search, reveal, export services)
├── cli/                 # Command-line interface
└── lib/                 # Libraries (browser_client, csv_exporter, rate_limiter)
tests/
├── contract/            # Browser automation contract tests
├── integration/         # End-to-end workflow tests
└── unit/               # Unit tests for individual components
```

## Key Commands
```bash
# Search and reveal prospects via API (recommended - 100/day limit)
signalhire search --title "Software Engineer" --location "San Francisco" --company "Tech Corp" --limit 50
signalhire reveal --input search_results.csv --limit 10 --output contacts.csv

# Bulk reveal using browser automation (1000+ contacts - optional)
signalhire reveal --input large_prospect_list.csv --browser --bulk-size 1000

# Monitor credits via API
signalhire credits --check
```

## Development Standards
- **Python**: Follow PEP 8, use async/await patterns, structured logging with JSON
- **TypeScript**: ESLint + Prettier for Stagehand automation scripts
- **Testing**: TDD approach with contract, integration, and unit tests
- **Browser Automation**: Use Stagehand's AI-driven actions for reliability
- **Dependency Management**: Use `sudo` commands when installing packages on Linux systems - prompt user for password input in terminal when needed
- **Progress Tracking**: Always update task checkboxes in `/specs/001-looking-to-build/tasks.md` immediately after completing each task

## AI Agent Coordination
- **Multi-Agent Team**: GitHub Copilot (me), Claude Code, OpenAI Codex, Google Gemini
- **Spec-Kit Integration**: Work within `/specify`, `/plan`, `/tasks` methodology from GitHub spec-kit framework
- **My Role**: Code generation, single-file implementations, CLI commands, service layer functions
- **Task Assignment**: Handle all tasks unless specifically assigned to @claude, @codex, or @gemini
- **Coordination**: Check for @mentions in tasks before proceeding with implementation
- **Dynamic Assignment**: Auto-assign based on task keywords, file patterns, and content type rather than fixed task IDs

## Important Notes
- **API-First Approach**: Use API-based contact reveal for reliability (100 contacts/day limit)
- **Browser Automation**: Optional capability for bulk operations (1000+ contacts) when needed
- **Hybrid Strategy**: API for daily operations, browser automation for high-volume scenarios
- **Rate Limiting**: Respect 100 contacts/day API limit with built-in rate limiter
- Environment variables: SIGNALHIRE_EMAIL, SIGNALHIRE_PASSWORD
- **Dependency Installation**: Automatically handle missing dependencies with `run.py` script - will use sudo when needed and prompt for password
- **Task Management & Completion Protocol**: 
  - ✅ **ALWAYS commit code changes** when completing tasks
  - ✅ **ALWAYS mark tasks as complete** with `[x]` symbol in tasks.md immediately after finishing
  - ✅ **Use completion symbols** to show you have committed your work  
  - ❌ **NEVER leave uncommitted work** when marking tasks complete

## Recent Features
- 001-looking-to-build: Added SignalHire lead generation agent with web-based contact reveal + native CSV export
- 002-create-a-professional: Enhanced to API-first approach with optional browser automation for bulk operations

<!-- MANUAL ADDITIONS START -->

## WSL Environment Notes
- When reading screenshots or working with Windows paths, always use WSL-compatible paths (e.g., `/mnt/c/` instead of `C:\`)
- Screenshots saved by Windows applications should be accessed via WSL path format

- Always use absolute paths when reading files

## Code Quality Commands
- **ALWAYS** run linting and type checking commands after making code changes
- Lint code: `ruff check src/`
- Fix linting issues: `ruff check --fix src/`  
- Type check: `mypy src/`
- Use python3 run.py instead of direct pytest commands for consistent environment setup
- Test message for consistent behavior
- Always validate input parameters in all functions
- Never commit secrets or API keys - always use environment variables and .env files
- You're absolutely right - the environment variable issue is frustrating! The problem is that we're running Python from Windows but the .env file is in the WSL filesystem, so the environment variables aren't being loaded properly. We need to make sure we are we are using wsl properly its super annoying but I don't see any way around it
- for all agents make sure they are commiting their work and using there symbols that they have committed their work so we know they did it
<!-- MANUAL ADDITIONS END -->
