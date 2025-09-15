# Script Header Standard

All scripts in the SignalHire Agent project MUST include a standardized header following this format.

## Required Header Format

```bash
#!/bin/bash  # or #!/usr/bin/env python3 for Python
# Script Name
#
# PURPOSE: One-line description of what this script does
# USAGE: ./script-name.sh [arguments] [flags]
# PART OF: Which system/workflow this script belongs to
# CONNECTS TO: What other scripts, workflows, or systems this interacts with
#
# Detailed description explaining:
# - What this script accomplishes
# - Key operations it performs
# - Important notes about usage or dependencies
```

## Examples

### Shell Script Example
```bash
#!/bin/bash
# Production Build Script for SignalHire Agent
#
# PURPOSE: Creates clean production deployment with version tracking
# USAGE: ./build-production.sh <target_directory> [--version TAG] [--latest] [--force]
# PART OF: Build and deployment system
# CONNECTS TO: GitHub Actions workflow (.github/workflows/release.yml)
#
# This script creates production-ready deployments by:
# - Copying only essential application files (src/, docs/, agent instructions)
# - Auto-creating .env with development credentials
# - Removing development files (tests/, specs/, version.py)
# - Creating install.sh with virtual environment support
# - Generating CLI wrapper for easy execution
```

### Python Script Example
```python
#!/usr/bin/env python3
"""
Agent Coordinator Script

PURPOSE: Orchestrates multi-agent workflows and task coordination
USAGE: python agent-coordinator.py [--config file] [--mode interactive]
PART OF: AI agent coordination system
CONNECTS TO: Task management system, agent instruction files (CLAUDE.md, AGENTS.md)

This script manages communication and task distribution between multiple AI agents
working on the SignalHire Agent project, ensuring proper task completion protocols
and coordination.
"""
```

## Required Fields

### ✅ MANDATORY Fields
- **PURPOSE**: One-line explanation of what the script does
- **USAGE**: How to run the script with arguments and flags
- **PART OF**: Which larger system or workflow this belongs to
- **CONNECTS TO**: Dependencies, related scripts, or systems it interacts with

### ✅ RECOMMENDED Fields
- **Detailed description**: Multi-line explanation of key operations
- **Dependencies**: Required environment variables, tools, or files
- **Notes**: Important warnings, limitations, or special considerations

## Guidelines for AI Agents

When creating any script file, ALL agents must:

1. **Always include the full header** before any code
2. **Be specific in PURPOSE** - explain exactly what the script accomplishes
3. **Show clear USAGE** - include all arguments and common usage patterns
4. **Identify PART OF** - which system/workflow this script serves
5. **Document CONNECTS TO** - what other parts of the project this interacts with
6. **Explain complex operations** in the detailed description

## Enforcement

- All new scripts MUST include proper headers
- Existing scripts missing headers should be updated when modified
- Code reviews should check for proper headers
- Automated tools may validate header presence

## Why This Matters

- **Maintenance**: Future developers understand what scripts do
- **Integration**: Clear connections between scripts and systems
- **Documentation**: Headers serve as inline documentation
- **Onboarding**: New team members can quickly understand script purposes
- **Debugging**: Clear context when scripts fail or behave unexpectedly