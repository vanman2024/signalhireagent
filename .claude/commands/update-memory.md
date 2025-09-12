# Update Shared Memory

Update agent context files and constitution.md to keep shared memory synchronized across all AI agents.

## Usage

```
/update-memory [message] [scope] [options]
```

## Parameters

- `message` (optional): Specific update message to apply across agent files
  - Example: "Update all pytest commands to use 'python3 run.py -m pytest'"
  - Example: "Add new testing requirements for async operations"
  
- `scope` (optional): What to update
  - `agent` - Update only agent context files (CLAUDE.md, GEMINI.md, AGENTS.md, etc.)
  - `constitution` - Update only constitution.md with current project status
  - `coordination` - Update coordination documentation 
  - `all` - Update everything (default)

- `options` (optional):
  - `--force` - Force update even if no changes detected
  - `--dry-run` - Show what would be updated without making changes

## Examples

```
/update-memory
/update-memory "Update pytest commands to use python3 run.py" agent
/update-memory constitution --force
/update-memory "Add new API endpoints documentation" all --dry-run
/update-memory "make sure to use wsl paths for reading screenshots"
```

## What it does

1. **Agent Context**: Runs `scripts/update-agent-context.sh all` to update:
   - CLAUDE.md with current feature and technology info
   - GEMINI.md with project context
   - AGENTS.md with repository guidelines
   - Any other agent context files

2. **Constitution**: Updates `memory/constitution.md` with:
   - Current project status and task progress
   - Active branch and last commit info
   - Core development principles
   - Spec-kit workflow documentation
   - AI coordination guidelines

3. **Coordination**: Updates coordination system documentation

This ensures all AI agents have synchronized context and understand the current project state, development principles, and coordination procedures.

## Implementation

When this slash command is executed, it runs:
```bash
./scripts/update-shared-memory.sh [scope] [options]
```

The script handles all the heavy lifting of updating agent context and constitution files.