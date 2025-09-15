# Scripts Directory

Organized automation scripts for the SignalHire Agent project.

## Directory Structure

### 📦 `build/`
Production build and deployment scripts
- `build-production.sh` - Creates clean production deployments

### 🛠️ `development/`
Development automation and setup scripts
- `setup-ai-agents.sh` - AI agent coordination setup
- `create-new-feature.sh` - Feature development scaffolding
- `run-real-api-tests.sh` - Live API testing
- `validate_docs.py` - Documentation validation
- `daily_job.sh` - Scheduled maintenance tasks
- `common.sh` - Shared utility functions

### 🤖 `agents/`
AI agent coordination and management scripts
- `agent-coordinator.py` - Multi-agent workflow orchestration
- `update-agent-context.sh` - Agent context synchronization
- `update-shared-memory.sh` - Shared memory management

### 🔧 `git/`
Git and version control automation
- `git-commit-helper.sh` - Standardized commit message creation

### 📊 `data-processing/`
Data manipulation and processing tools
- `check_existing_contacts.py` - Contact deduplication utilities
- `convert_to_csv.py` - Data format conversion
- `create_test_sample.py` - Test data generation

### 🧪 `testing/`
Testing utilities and helpers
- `test_reveal_api.py` - API testing scripts
- `run_tests.py` - Test execution automation
- `simple_callback_server.py` - Testing callback server

## Usage

Most scripts are executable and include help information:
```bash
./scripts/build/build-production.sh --help
./scripts/development/setup-ai-agents.sh --help
```

## Development

When adding new scripts:
1. Place in appropriate subdirectory based on purpose
2. Make executable: `chmod +x script-name.sh`
3. Include usage documentation in script header
4. Update this README if creating new categories