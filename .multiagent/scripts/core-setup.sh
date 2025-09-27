#!/bin/bash
# Core setup script for multiagent-core workflows

# Core multiagent-core setup
setup_multiagent_core() {
    echo "🚀 Setting up multiagent-core workflows..."
    
    # Copy all core workflows
    mkdir -p .github/workflows .claude/agents
    
    # Essential workflows
    cp "$MULTIAGENT_CORE_DIR/.github/workflows/claude.yml" .github/workflows/
    cp "$MULTIAGENT_CORE_DIR/.github/workflows/claude-code-review.yml" .github/workflows/
    
    # Core subagents
    cp "$MULTIAGENT_CORE_DIR/.claude/agents/pr-feedback-router.md" .claude/agents/
    
    # Project templates
    if [ ! -f "CLAUDE.md" ]; then
        cp "$MULTIAGENT_CORE_DIR/.multiagent/templates/CLAUDE.template.md" CLAUDE.md
    fi
    
    echo "✅ Core workflows installed"
}

# Add to any existing setup script
setup_multiagent_core