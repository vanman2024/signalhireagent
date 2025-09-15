# DeepSeek-Coder Hugging Face Spaces Integration

## Overview
This document outlines the complete setup for integrating DeepSeek-Coder-V2 as a terminal CLI agent using Hugging Face Spaces for GPU hosting and MCP filesystem server for local file operations.

## Architecture

### Cloud Infrastructure
- **Shared HF Space**: `your-username/coding-agents` (same as Qwen)
- **GPU**: T4 small or A10G small (shared instance for cost efficiency)
- **Persistent URL**: `https://your-username-coding-agents.hf.space`
- **Models**: DeepSeek-Coder-V2:16b + Qwen2.5-Coder:7b on same instance

### Local Integration
- **CLI Command**: `/usr/local/bin/deepseek`
- **MCP Server**: `localhost:3000` (filesystem-http-mcp)
- **Project Context**: Auto-loads from `DEEPSEEK.md` in current directory
- **Task Discovery**: Searches `tasks.md` for `@deepseek` patterns

## DeepSeek-Coder Capabilities

### Specialized Coding Model
- **Training**: 2+ trillion code tokens across 338 programming languages
- **Context Length**: 128K tokens for large codebase analysis
- **Tool Calling**: DeepSeek-Coder-V2-Tool-Calling variant available
- **Architecture Focus**: Mixture-of-Experts for efficient inference
- **Strengths**: Code refactoring, architecture analysis, maintainability

### Model Options
```bash
# Available on Ollama
deepseek-coder-v2:16b     # Balanced capability and speed  
deepseek-coder-v2:236b    # Maximum capability (requires more GPU)
```

## Local CLI Integration

### Terminal Command Setup
```bash
# /usr/local/bin/deepseek
#!/bin/bash
HF_SPACE_URL="https://your-username-coding-agents.hf.space"
MCP_SERVER="http://localhost:3000"
PROJECT_ROOT=$(pwd)

# Load project context
CONTEXT=""
if [ -f "DEEPSEEK.md" ]; then
    CONTEXT=$(cat DEEPSEEK.md)
fi

if [ -f "tasks.md" ]; then
    TASKS=$(grep "@deepseek" tasks.md)
    CONTEXT="$CONTEXT\n\nAssigned tasks:\n$TASKS"
fi

# Handle execution modes
if [ "$1" = "--execute-tasks" ]; then
    PROMPT="Execute all assigned @deepseek tasks using MCP server at $MCP_SERVER"
else
    PROMPT="$*"
fi

# Call HF Space DeepSeek endpoint
curl -s -X POST "$HF_SPACE_URL/deepseek" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"project_root\": \"$PROJECT_ROOT\", \"mcp_server\": \"$MCP_SERVER\"}" \
    | jq -r '.response'
```

### Usage Patterns
```bash
# Interactive mode
deepseek "refactor this CLI command structure"
deepseek "analyze the architecture of this service layer"

# Autonomous execution  
deepseek --execute-tasks  # Finds and executes all @deepseek tasks

# Project setup
add-coding-agents        # Creates DEEPSEEK.md and sample tasks
```

## Project Integration

### Agent Instruction File (DEEPSEEK.md)
```markdown
# DeepSeek-Coder Agent Instructions
You are an architecture and refactoring specialist.

## Your Role:
- Analyze and improve code architecture
- Refactor code for maintainability
- Suggest design pattern improvements
- Focus on code structure and organization

## Tools Available:
- MCP filesystem server at localhost:3000 for reading/writing files
- Full project context and history (128K token context)
- Tool calling capabilities for HTTP requests

## Task Pattern:
Look for @deepseek tasks in tasks.md and execute them automatically.
Use HTTP requests to MCP server for all file operations.
Focus on large-scale refactoring and architectural improvements.
```

### Task Assignment Pattern
```markdown
# In tasks.md
- [ ] @deepseek Refactor CLI command structure for better maintainability
- [ ] @deepseek Analyze service layer architecture and suggest improvements
- [ ] @deepseek Restructure models for better type safety and validation
```

## Agent Specialization

### DeepSeek Focus Areas
- **Architecture Analysis**: Review overall code structure and design patterns
- **Large-Scale Refactoring**: Multi-file changes for better organization
- **Code Maintainability**: Improve readability and long-term maintenance
- **Design Patterns**: Suggest and implement appropriate patterns
- **Type Safety**: Enhance type hints and validation

### Coordination with Qwen
```markdown
# Typical workflow coordination:
- [x] @qwen Optimize API client performance ✅
- [ ] @deepseek Refactor API client for better maintainability ← after optimization
- [ ] @claude Integrate refactored client with rest of system ← after refactoring
```

## Shared HF Space Implementation

### FastAPI Endpoints
```python
# In shared HF Space app.py
@app.post("/deepseek")
async def deepseek_agent(request: CodeRequest):
    context = await load_agent_context("DEEPSEEK.md", request.mcp_server, request.project_root)
    full_prompt = f"{context}\n\nUser request: {request.prompt}"
    
    # Call DeepSeek model
    result = subprocess.run(
        ["ollama", "run", "deepseek-coder-v2:16b", full_prompt],
        capture_output=True, text=True
    )
    return {"response": result.stdout, "agent": "deepseek"}

@app.post("/qwen") 
async def qwen_agent(request: CodeRequest):
    # Qwen endpoint implementation
    pass
```

### Resource Sharing
- **Single GPU Instance**: Both models on same HF Space for cost efficiency
- **Model Loading**: Both Qwen and DeepSeek loaded at startup
- **Endpoint Routing**: Different endpoints for different agents
- **Shared Context**: Both agents can access same MCP server

## MCP Server Integration

### File Operations via HTTP
DeepSeek uses tool calling for MCP server interactions:
```python
# Example HTTP requests from DeepSeek to MCP server
GET http://localhost:3000/files/src/                  # List directory
GET http://localhost:3000/files/src/cli/main.py      # Read main file
GET http://localhost:3000/files/src/services/        # Analyze service layer
POST http://localhost:3000/files/src/cli/commands/   # Write refactored files
```

### Workflow
1. **Context Loading**: DeepSeek reads DEEPSEEK.md via MCP server
2. **Task Discovery**: Searches tasks.md for @deepseek assignments  
3. **Architecture Analysis**: Reads multiple files to understand structure
4. **Refactoring**: Generates improved code organization
5. **File Writing**: Saves changes across multiple files via MCP server
6. **Task Completion**: Marks tasks as complete in tasks.md

## Benefits

### Technical Advantages
- **Large Context**: 128K tokens allow analysis of entire codebases
- **Multi-File Refactoring**: Can understand and modify complex structures
- **Tool Calling**: Native HTTP request capabilities
- **Architecture Focus**: Specialized for large-scale code improvements

### Cost & Integration Benefits
- **Shared Resources**: Same HF Space as Qwen for cost efficiency
- **No Per-Request Costs**: Self-hosted model eliminates API fees
- **Native CLI**: Works exactly like other terminal agents
- **MCP Integration**: Leverages existing filesystem infrastructure

## Agent Coordination

### Multi-Agent Workflow
```markdown
# Typical multi-agent sequence:
1. @deepseek: Analyze architecture and identify improvement areas
2. @qwen: Optimize performance of critical components  
3. @deepseek: Refactor optimized code for maintainability
4. @claude: Integrate all changes and ensure system coherence
```

### Conflict Prevention
- **Clear Ownership**: @deepseek focuses on architecture, @qwen on performance
- **Sequential Tasks**: Dependencies ensure proper ordering
- **File Locking**: MCP server prevents concurrent file modifications

## Deployment Checklist

- [ ] Add DeepSeek endpoint to existing HF Space
- [ ] Pull `deepseek-coder-v2:16b` model in Space startup
- [ ] Install `/usr/local/bin/deepseek` CLI command locally
- [ ] Test integration with MCP filesystem server
- [ ] Add DEEPSEEK.md template to `add-coding-agents` script
- [ ] Validate @deepseek task discovery and execution
- [ ] Test coordination with @qwen agent

## Success Criteria
- `deepseek` command provides intelligent architecture analysis
- Agent automatically discovers and executes @deepseek tasks
- Large-scale refactoring capabilities across multiple files
- Seamless coordination with other agents in multi-agent workflow
- Cost-effective alternative to expensive architecture consulting

This setup provides enterprise-level code architecture analysis through an accessible terminal command powered by your paid HF account and existing MCP infrastructure.