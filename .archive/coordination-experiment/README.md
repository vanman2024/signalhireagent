# Archived: Multi-Agent Coordination Experiment

This directory contains the experimental automated coordination system that was developed but ultimately replaced with a simpler direct CLI approach.

## What was built

### 1. Agent Coordinator (`agent-coordinator.py`)
- **Purpose**: Automatically parse @ assignments from tasks.md and call agents programmatically
- **Features**: 
  - Task dependency resolution
  - Agent calling (Codex, Gemini)
  - Automatic checkbox updates
  - Dry-run mode
- **Why archived**: Complex parsing issues and over-engineering for the use case

### 2. Coordination Wrapper (`coordinate-agents.sh`) 
- **Purpose**: User-friendly interface for the coordinator
- **Features**:
  - Dry-run and live modes
  - Continuous loop operation
  - Agent status checking
- **Why archived**: Dependency on the main coordinator script

### 3. Debug Tools (`debug-coordinator.py`)
- **Purpose**: Debug task parsing and dependency issues
- **Why archived**: No longer needed with direct CLI approach

## Lessons Learned

1. **Automated coordination is complex**: Parsing @ assignments, handling dependencies, and calling agents programmatically introduced many edge cases
2. **Direct CLI is simpler**: Just tell each agent what to work on directly
3. **Shared context still valuable**: The `/update-memory` command for synchronizing agent context remains useful
4. **Over-engineering trap**: Sometimes the simple solution is better

## What we kept

- **`/update-memory` slash command**: Still useful for synchronizing agent context and constitution
- **@ assignments in tasks.md**: Clear task ownership remains valuable for organization
- **AI_COORDINATION_PLAN.md**: Documentation of the approach and architecture decisions

## Final approach

**Coordination**: `/update-memory` keeps agents synchronized  
**Execution**: Direct CLI calls like `codex exec "task description" --sandbox workspace-write`  
**Organization**: @ assignments in tasks.md for clarity

This provides the benefits of coordinated context without the complexity of automated orchestration.

---
*Archived on: $(date)*  
*Reason: Replaced with simpler direct CLI approach*