# Qwen2.5-Coder Hugging Face Spaces Integration

## Overview
This document outlines the complete setup for integrating Qwen2.5-Coder as a terminal CLI agent using Hugging Face Spaces for GPU hosting and MCP filesystem server for local file operations.

## Architecture

### Cloud Infrastructure
- **Hugging Face Space**: `your-username/coding-agents`
- **GPU**: T4 small or A10G small (paid tier benefits)
- **Persistent URL**: `https://your-username-coding-agents.hf.space`
- **Models**: Qwen2.5-Coder:7b + DeepSeek-Coder-V2:16b on same instance

### Local Integration
- **CLI Command**: `/usr/local/bin/qwen`
- **MCP Server**: `localhost:3000` (filesystem-http-mcp)
- **Project Context**: Auto-loads from `QWEN.md` in current directory
- **Task Discovery**: Searches `tasks.md` for `@qwen` patterns

## Hugging Face Space Setup

### Space Configuration
```yaml
title: Multi-Agent Coding System
sdk: gradio
hardware: t4-small  # or a10g-small for paid tier
visibility: public
persistent_storage: true
```

### Application Structure
```
coding-agents-space/
├── app.py                 # FastAPI server with Ollama
├── requirements.txt       # Dependencies  
├── Dockerfile            # Container setup
├── startup.sh           # Model loading script
└── README.md           # Space documentation
```

### Key Features
- **Permanent URL**: No tunneling or dynamic URLs needed
- **Paid Tier Benefits**: Better GPUs, longer runtime, priority access
- **Always Available**: Space stays warm with paid account
- **Tool Calling**: Qwen2.5-Coder supports HTTP requests to MCP server
- **Multi-Model**: Both Qwen and DeepSeek on same instance

## Local CLI Integration

### Terminal Command Setup
```bash
# /usr/local/bin/qwen
#!/bin/bash
HF_SPACE_URL="https://your-username-coding-agents.hf.space"
MCP_SERVER="http://localhost:3000"
PROJECT_ROOT=$(pwd)

# Load project context
CONTEXT=""
if [ -f "QWEN.md" ]; then
    CONTEXT=$(cat QWEN.md)
fi

if [ -f "tasks.md" ]; then
    TASKS=$(grep "@qwen" tasks.md)
    CONTEXT="$CONTEXT\n\nAssigned tasks:\n$TASKS"
fi

# Handle execution modes
if [ "$1" = "--execute-tasks" ]; then
    PROMPT="Execute all assigned @qwen tasks using MCP server at $MCP_SERVER"
else
    PROMPT="$*"
fi

# Call HF Space
curl -s -X POST "$HF_SPACE_URL/qwen" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"project_root\": \"$PROJECT_ROOT\", \"mcp_server\": \"$MCP_SERVER\"}" \
    | jq -r '.response'
```

### Usage Patterns
```bash
# Interactive mode
qwen "optimize this API client function"
qwen "analyze performance bottlenecks in search.py"

# Autonomous execution
qwen --execute-tasks  # Finds and executes all @qwen tasks

# Project setup
add-coding-agents     # Creates QWEN.md and sample tasks
```

## Project Integration

### Agent Instruction File (QWEN.md)
```markdown
# Qwen2.5-Coder Agent Instructions
You are a code optimization and performance specialist.

## Your Role:
- Optimize algorithms and data structures
- Improve code performance and efficiency  
- Suggest better implementations
- Focus on speed and memory usage

## Tools Available:
- MCP filesystem server at localhost:3000 for reading/writing files
- Full project context and history
- Tool calling capabilities for HTTP requests

## Task Pattern:
Look for @qwen tasks in tasks.md and execute them automatically.
Use HTTP requests to MCP server for all file operations.
```

### Task Assignment Pattern
```markdown
# In tasks.md
- [ ] @qwen Optimize search algorithm performance (<2s response time)
- [ ] @qwen Improve memory usage in data processing pipeline  
- [ ] @qwen Analyze and optimize API client request patterns
```

## MCP Server Integration

### File Operations via HTTP
Qwen2.5-Coder uses tool calling to interact with MCP server:
```python
# Example HTTP requests from Qwen to MCP server
GET http://localhost:3000/files/src/services/api.py    # Read file
POST http://localhost:3000/files/src/services/api.py   # Write file
GET http://localhost:3000/files/tasks.md               # Read tasks
```

### Workflow
1. **Context Loading**: Qwen reads QWEN.md via MCP server
2. **Task Discovery**: Searches tasks.md for @qwen assignments
3. **File Analysis**: Reads source files via HTTP requests
4. **Optimization**: Generates improved code
5. **File Writing**: Saves changes via MCP server
6. **Task Completion**: Marks tasks as complete in tasks.md

## Benefits of This Approach

### Cost Effectiveness
- **No API Costs**: Self-hosted models eliminate per-request fees
- **Paid HF Benefits**: Better GPU access through subscription
- **On-Demand Usage**: Only pay for HF subscription, not per-use

### Integration Advantages
- **Native CLI Feel**: `qwen` command works like `gemini` or `claude`
- **Project Awareness**: Auto-loads context from current directory
- **MCP Integration**: Leverages existing filesystem-http-mcp server
- **Multi-Agent Ready**: Works alongside other agents seamlessly

### Technical Benefits
- **Tool Calling**: Qwen2.5-Coder supports HTTP requests natively
- **Persistent Models**: HF Space keeps models loaded and warm
- **Reliable Infrastructure**: HF Spaces provide stable hosting
- **Version Control**: Space code is git-managed

## Deployment Steps

1. **Create HF Space** with FastAPI + Ollama setup
2. **Deploy models** (Qwen2.5-Coder:7b + DeepSeek-Coder-V2:16b)
3. **Install CLI commands** (`qwen`, `deepseek`) locally
4. **Test integration** with MCP filesystem server
5. **Deploy to projects** using `add-coding-agents` script

## Success Criteria
- Typing `qwen` in any terminal provides intelligent coding assistance
- Agent automatically discovers and executes @qwen tasks
- Seamless integration with existing multi-agent development workflow
- Cost-effective alternative to API-based coding assistants
- Works alongside existing CLI agents (gemini, copilot, claude)

This setup transforms expensive cloud AI into accessible terminal commands powered by your paid HF account and existing MCP infrastructure.