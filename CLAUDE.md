# signalhireagent Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-16

## Active Technologies
- Python 3.11 + asyncio (signalhireagent)
- FastAPI (MCP server + autonomous workflows)
- Supabase (PostgreSQL database with real-time features)
- APScheduler (autonomous workflow scheduling)
- Railway (deployment platform with persistent processes)
- httpx (async HTTP client for SignalHire API)
- pandas (CSV data processing and export)
- pydantic (data validation and MCP tool models)
## Project Structure
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

## CLI Commands for AI Agents

**📖 Complete Reference**: See `/home/vanman2025/signalhireagent/docs/cli-commands.md`

When the user gives natural language requests, use the CLI command mappings in the reference file:

### Quick Examples:
- **"Find software engineers in California"** → `signalhire search --title "Software Engineer" --location "California"`
- **"Merge these contact files"** → `signalhire dedupe merge --input "file1.json,file2.json" --output merged.json`
- **"Check my daily limits"** → `signalhire status --credits`
- **"Remove operators from contacts"** → `signalhire filter job-title --input contacts.json --output filtered.json --exclude-job-titles "operator"`

### Key Features:
- Search with Boolean operators (AND, OR, NOT)
- Contact deduplication and filtering
- Geographic and job title analysis
- Automatic 5000/day limit tracking (search profiles + reveals)
- Progress tracking and resume capability

## 🚨 CRITICAL: Development vs Production Protocol

### Never Edit Production Directly
- ❌ **NEVER** make changes directly in production code
- ❌ **NEVER** edit files in `/path/to/production/` directory  
- ✅ **ALWAYS** make changes in development environment first
- ✅ **ALWAYS** test changes in development before deploying
- ✅ **ALWAYS** use deployment scripts to push changes to production

### Proper Development Workflow
1. **Make changes in development**: Edit files in main development directory
2. **Test with ops system**: Run `./ops/ops qa` to validate changes
3. **Commit changes**: Use git to commit changes to development repository
4. **Deploy to production**: Use `./ops/ops build` and deployment commands
5. **Verify in production**: Run `./ops/ops verify-prod` to test production build

### Why This Matters
- Production deployments overwrite ALL code changes
- Manual edits in production are lost when deployment script runs
- Development → Production flow ensures consistency and version control
- Ops/deploy systems handle proper file management and environment setup

## 🤝 Working with Users - Critical Guidelines

### User Communication Principles
- **Be Direct & Concise**: Users want solutions, not explanations. Answer in 1-3 sentences when possible.
- **Follow Instructions Exactly**: If user says "don't create backups", don't create backups. Period.
- **Ask for Clarification**: When unclear, ask specific questions rather than making assumptions.
- **Validate Understanding**: Repeat back critical requirements to confirm understanding.

### Common User Frustrations to Avoid
- ❌ **Over-explaining**: Don't explain what you're doing unless asked
- ❌ **Ignoring explicit instructions**: "I told you not to do X" means never do X
- ❌ **Making assumptions**: When in doubt, ask
- ❌ **Complex solutions**: Users prefer simple, reliable approaches
- ❌ **Defensive responses**: Accept feedback and fix issues quickly

### Deployment-Specific User Guidelines
- **Never edit production directly** - Users will be frustrated if you bypass their workflow
- **Preserve user files** - Any files users create in production must be preserved
- **Version control matters** - Users want to track changes via git tags and proper versioning
- **Simple is better** - Complex backup/restore systems confuse users

### Response Patterns
```
✅ Good: "Fixed. Files now preserved during deployment."
❌ Bad: "I've implemented a comprehensive backup and restoration system that..."

✅ Good: "Version now reads from pyproject.toml automatically."  
❌ Bad: "The issue was in the version detection logic where..."

✅ Good: "What specific behavior do you want when files exist?"
❌ Bad: "I think the best approach would be to..."
```

### When Users Give Critical Feedback
1. **Acknowledge immediately**: "You're right, that's not working"
2. **Identify root cause**: Get to the real problem quickly  
3. **Propose simple solution**: Offer the most direct fix
4. **Implement and verify**: Test the solution works as expected
5. **Confirm satisfaction**: "Is this working as you expected?"

## Code Style
Python: Follow PEP 8, use async/await patterns, structured logging with JSON
TypeScript: ESLint + Prettier for Stagehand automation scripts

## Testing Commands
- Run tests: `python3 run.py -m pytest`
- Tests with coverage: `python3 run.py -m pytest --cov=src --cov-report=term-missing`
- Test selection: `python3 run.py -m pytest -m unit`, `python3 run.py -m pytest -m "integration and not slow"`
- Check dependencies: `signalhire doctor` (dependency checking only runs for doctor command now for fast startup)

## Task Assignment & Coordination

### My Responsibilities (@claude - Worker Claude)
**Check current spec's tasks.md for @claude assignments:**
- Agent abstraction layer and workflow orchestration
- Supabase database integration and session state management
- Railway deployment configuration and infrastructure
- Cross-service integration and MCP tool coordination
- System architecture and autonomous workflow design

### Task Workflow & Completion Requirements
1. **Check for assignments**: Look for `@claude` in tasks.md
2. **Plan the implementation**: Consider multi-file impacts and integration points
3. **Implement with tests**: Create comprehensive implementation with proper testing
4. **COMMIT YOUR WORK**: All agents MUST commit their code changes when tasks are complete
5. **Mark completion**: Change `[ ]` to `[x]` in tasks.md immediately after finishing - this is your commitment symbol
6. **Document patterns**: Update shared context if new patterns are established

### Critical Completion Protocol
- ✅ **ALWAYS commit code changes** when completing tasks
- ✅ **ALWAYS push commits to remote** immediately after committing (`git push origin main`)
- ✅ **ALWAYS mark tasks as complete** with `[x]` symbol in tasks.md
- ✅ **Use completion symbols** to show you have committed your work
- ✅ **VERIFY 100% FR COMPLIANCE** before merging - all Functional Requirements must be implemented
- ✅ **TEST ALL EDGE CASES** before merging - must handle gracefully, not crash
- ❌ **NEVER forget to push commits** - other developers/directories won't see changes until pushed
- ❌ **NEVER delete feature branch** until 100% FR compliance verified
- ❌ **NEVER leave uncommitted work** when marking tasks complete

### Commit Message Requirements for ALL AGENTS
**MANDATORY**: Every agent must include their identity and task reference in commits:

```bash
# Template for all agents:
git commit -m "$(cat <<'EOF'
[AGENT_ACTION]: Brief description of changes

- Specific change 1
- Specific change 2
- Reference to task numbers completed (e.g., T025, T030)

[AGENT_NAME] completed: T### Task description
Supports: [Project specification reference]

🤖 Generated by [AGENT_NAME] with Claude Code

Co-Authored-By: [AGENT_NAME] <noreply@anthropic.com>
EOF
)"
```

**Examples by Agent:**
```bash
# @claude commits:
🤖 Generated by Claude with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
Claude completed: T025 Add configuration management for API vs browser preferences

# @copilot commits:
🤖 Generated by Copilot with Claude Code
Co-Authored-By: Copilot <noreply@anthropic.com>
Copilot completed: T010 CLI improvements for user experience

# @gemini commits:
🤖 Generated by Gemini with Claude Code
Co-Authored-By: Gemini <noreply@anthropic.com>
Gemini completed: T029 Update CLI command documentation

# @codex commits:
🤖 Generated by Codex with Claude Code
Co-Authored-By: Codex <noreply@anthropic.com>
Codex completed: T004 Enhanced API client contract test
```

### Current @claude Tasks
```bash
# Check my current assignments:
grep "@claude" [current-spec]/tasks.md
```


### Key Focus Areas
- **Supabase Integration**: Database models, session state, real-time features
- **Agent Orchestration**: Multi-agent workflow coordination and tool calling
- **Deployment**: Railway configuration, environment management, production setup
- **Architecture**: MCP server design, autonomous workflow patterns

### Example Task Pattern
```
- [ ] T031 @claude FastAPI callback server for Person API in src/lib/callback_server.py
```
**After completion:**
```
- [x] T031 @claude FastAPI callback server for Person API in src/lib/callback_server.py
```

## Recent Changes
- 004-enterprise-contact-deduplication: Complete contact deduplication and filtering system
- Consolidated ops and deploy systems into dedicated folders (ops/, deploy/)
- Fixed WSL Python environment dependency issues in production builds
- Standardized semantic versioning workflow with ops system
- Eliminated deployment file preservation issues

## Prerequisites
- SignalHire API key (for MCP tool integration)
- Supabase account and project (for database and session state)
- Railway account (for deployment with persistent processes)
- Environment variables: SIGNALHIRE_API_KEY, SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY

<!-- MANUAL ADDITIONS START -->

## WSL Environment Notes
- When reading screenshots or working with Windows paths, always use WSL-compatible paths (e.g., `/mnt/c/` instead of `C:\`)
- Screenshots saved by Windows applications should be accessed via WSL path format

## Documentation Guidelines
- ALWAYS check if documentation files already exist before creating new ones
- Use Read tool to verify file existence and content before creating documentation
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested

- Always use absolute paths when reading files

## 🚀 Ops & Deploy Systems

Use the consolidated ops and deploy systems for all development and deployment tasks.

### Operations Workflow (ops/)
```bash
# Daily development workflow
./ops/ops qa                    # Quality checks (lint, format, typecheck, tests)
./ops/ops build                 # Build production to configured target
./ops/ops verify-prod          # Verify production build works
./ops/ops release patch         # Create patch release (bug fixes)
./ops/ops release minor         # Create minor release (new features)
./ops/ops release major         # Create major release (breaking changes)

# Setup and status
./ops/ops setup [target]        # One-time setup with target directory
./ops/ops status                # Show current config and versions
./ops/ops env doctor           # Diagnose environment issues
```

### Deployment Commands (deploy/)
```bash
# Production deployment
./deploy/deploy production [target]    # Full production deployment
./deploy/deploy simple [target]        # Simple file-based deployment
./deploy/deploy build [target]         # Build production version only
```

### Semantic Versioning
```
MAJOR.MINOR.PATCH format:
./ops/ops release patch    # 0.4.9 → 0.4.10 (bug fixes)
./ops/ops release minor    # 0.4.9 → 0.5.0  (new features)
./ops/ops release major    # 0.4.9 → 1.0.0  (breaking changes)
```

### Documentation
- **Complete ops workflow**: `ops/README.md`
- **Complete deploy system**: `deploy/README.md`
- **Legacy documentation**: `docs/developer/TESTING_AND_RELEASE.md`

## Code Quality Guidelines
- **Use ops system**: Run `./ops/ops qa` for complete quality checks (includes linting, formatting, type checking, tests)
- **Manual commands** (if needed):
  - Lint: `ruff check src/` (auto-fix: `ruff check --fix src/`)
  - Type check: `mypy src/`
  - Tests: `python3 run.py -m pytest`
- **Always validate input parameters** in all functions
- **Never commit secrets** - use environment variables and .env files
- **WSL compatibility**: Use WSL-native Python to avoid environment issues

## 🚨 CRITICAL: Script Documentation Standards
**MANDATORY for ALL AGENTS**: Every script file must include a standardized header.

### Required Header Format:
```bash
#!/bin/bash  # or #!/usr/bin/env python3 for Python
# Script Name
#
# PURPOSE: One-line description of what this script does
# USAGE: ./script-name.sh [arguments] [flags]
# PART OF: Which system/workflow this script belongs to
# CONNECTS TO: What other scripts, workflows, or systems this interacts with
#
# Detailed description explaining key operations and usage notes
```

### Mandatory Fields:
- **PURPOSE**: One-line explanation of what the script does
- **USAGE**: How to run the script with arguments and flags
- **PART OF**: Which larger system or workflow this belongs to
- **CONNECTS TO**: Dependencies, related scripts, or systems it interacts with

### Standards Enforcement:
- ✅ **ALL new scripts MUST include proper headers**
- ✅ **Existing scripts missing headers should be updated when modified**
- ✅ **Reference**: `docs/developer/SCRIPT_HEADER_STANDARD.md` for complete guidelines

## Agent Work Validation Protocol
When checking any agent's completed work, use this systematic validation approach:

### Agent Work Validation
Use the ops system for systematic validation:

```bash
# Complete validation workflow
./ops/ops qa                    # Run all quality checks
./ops/ops build                 # Test production build
./ops/ops verify-prod          # Verify production works
```

### Manual Validation (if needed)
```bash
# Check commits follow format
git log --grep="🤖 Generated by" --oneline -5

# Test CLI functionality  
signalhire --help
```

<!-- MANUAL ADDITIONS END -->
# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
ALWAYS check if documentation files already exist before creating new documentation.
Use Read tool to verify file existence and content before creating documentation.
