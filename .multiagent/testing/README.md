# Multi-Agent Project Testing

This directory contains testing utilities for projects using the multi-agent framework.

## Quick Verification

After running `multiagent init` in your project:

```bash
# Make the test script executable
chmod +x .multiagent/testing/test_project_setup.sh

# Run the verification
./.multiagent/testing/test_project_setup.sh
```

This will verify:
- ✅ All required directories exist
- ✅ Essential configuration files are present
- ✅ AI CLI tools are available
- ✅ Component status

## Testing Your Multi-Agent Setup

### 1. Verify Structure
```bash
ls -la .multiagent/
ls -la .claude/
```

### 2. Check AI CLI Availability
```bash
specify --version   # spec-kit
gemini --version   # Gemini
qwen --version     # Qwen
claude --version   # Claude
```

### 3. Test Agent Workflows
Each agent in `.claude/agents/` can be tested:
- Review agent instructions
- Test with sample tasks
- Verify agent coordination

## Component Testing

If you've installed additional components:

### multiagent-testing
```bash
python -m multiagent_testing.cli verify
```

### multiagent-devops
```bash
python -m multiagent_devops.cli status
```

### multiagent-agentswarm
```bash
python -m multiagent_agentswarm.cli check
```

## Troubleshooting

### Missing directories/files
Re-run initialization:
```bash
multiagent init --no-interactive
```

### AI CLIs not found
Install the required CLIs:
```bash
# spec-kit (required)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Optional AI CLIs
pipx install gemini-cli
pipx install qwen-cli
```