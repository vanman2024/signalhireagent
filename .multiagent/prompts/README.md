# AI Agent Startup Prompts

Simple paragraph-based prompts to get each AI CLI started on the right track.

## Usage

These prompts are designed to be used with AI CLIs in non-interactive mode:

```bash
# Claude
claude -p "$(cat .multiagent/prompts/claude-startup.txt)"

# Qwen
qwen -p "$(cat .multiagent/prompts/qwen-startup.txt)"

# Gemini  
gemini -p "$(cat .multiagent/prompts/gemini-startup.txt)"

# Codex
codex -p "$(cat .multiagent/prompts/codex-startup.txt)"

# Copilot
copilot -p "$(cat .multiagent/prompts/copilot-startup.txt)"
```

## Agent Specializations

- **claude-startup.txt** - Strategic architecture and integration lead
- **qwen-startup.txt** - Performance optimization specialist  
- **gemini-startup.txt** - Research and documentation specialist
- **codex-startup.txt** - Frontend development specialist
- **copilot-startup.txt** - Backend implementation specialist

Each prompt provides the essential context and commands needed to get the agent started with the 6-phase worktree workflow.