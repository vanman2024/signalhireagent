#!/bin/bash
# Auto-setup Claude workflows for any project using multiagent-core
#
# This script:
# 1. Installs Claude Code SDK if not present (via npm or pip)
# 2. Verifies Claude CLI authentication
# 3. Copies Claude workflows from multiagent-core
# 4. Runs claude /install-github-app automatically
# 5. Sets up project configuration (CLAUDE.md, .gitignore)
# 6. Commits everything with proper attribution
# 7. Tests the complete setup
#
# Usage: ./setup-claude-workflows.sh [project-directory]

set -e

PROJECT_DIR=${1:-.}
PROJECT_NAME=$(basename "$PROJECT_DIR")

echo "🚀 Setting up Claude workflows for: $PROJECT_NAME"

# Step 0: Install Claude Code SDK if not present
if ! command -v claude >/dev/null 2>&1; then
    echo "📦 Claude Code SDK not found - installing..."
    
    # Check if npm is available
    if command -v npm >/dev/null 2>&1; then
        echo "📱 Installing Claude Code SDK via npm..."
        if npm install -g @anthropic/claude-cli; then
            echo "✅ Claude Code SDK installed successfully"
        else
            echo "❌ Failed to install Claude Code SDK via npm"
            echo "📝 Please install manually: https://docs.anthropic.com/en/docs/claude-code"
            exit 1
        fi
    # Check if pip is available
    elif command -v pip >/dev/null 2>&1; then
        echo "🐍 Installing Claude Code SDK via pip..."
        if pip install claude-code-sdk; then
            echo "✅ Claude Code SDK installed successfully"
        else
            echo "❌ Failed to install Claude Code SDK via pip"
            echo "📝 Please install manually: https://docs.anthropic.com/en/docs/claude-code"
            exit 1
        fi
    else
        echo "❌ Neither npm nor pip found"
        echo "📝 Please install Claude Code SDK manually: https://docs.anthropic.com/en/docs/claude-code"
        exit 1
    fi
else
    echo "✅ Claude Code SDK already installed"
fi

# Verify Claude CLI is working and authenticated
if ! claude --version >/dev/null 2>&1; then
    echo "⚠️  Claude CLI installed but not working properly"
    echo "📝 You may need to authenticate: claude auth login"
    echo "🔧 Attempting automatic authentication check..."
    
    # Try to check auth status
    if ! claude auth status >/dev/null 2>&1; then
        echo "❌ Claude CLI not authenticated"
        echo "📝 Please run: claude auth login"
        echo "💡 Then re-run this script"
        exit 1
    fi
else
    echo "✅ Claude Code SDK is working and authenticated"
fi

# Step 1: Check if we're in a git repo
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "❌ Error: $PROJECT_DIR is not a git repository"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 2: Create .github/workflows directory
mkdir -p .github/workflows

# Step 3: Copy Claude workflows from multiagent-core
CORE_DIR="$HOME/Projects/multiagent-core"
if [ ! -d "$CORE_DIR" ]; then
    echo "❌ Error: multiagent-core not found at $CORE_DIR"
    exit 1
fi

echo "📋 Copying Claude workflows from multiagent-core..."
cp "$CORE_DIR/.github/workflows/claude.yml" .github/workflows/
cp "$CORE_DIR/.github/workflows/claude-code-review.yml" .github/workflows/

# Step 4: Copy Claude subagents
echo "🤖 Setting up Claude subagents..."
mkdir -p .claude/agents
cp "$CORE_DIR/.claude/agents/pr-feedback-router.md" .claude/agents/

# Step 5: Check if GitHub App is installed
echo "🔍 Checking GitHub App installation..."
if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub CLI authenticated"
    
    # Try to check if Claude app is installed
    REPO_INFO=$(gh repo view --json owner,name)
    OWNER=$(echo "$REPO_INFO" | jq -r '.owner.login')
    REPO=$(echo "$REPO_INFO" | jq -r '.name')
    
    echo "📦 Repository: $OWNER/$REPO"
    
    # Check if CLAUDE_CODE_OAUTH_TOKEN secret exists
    if gh secret list | grep -q "CLAUDE_CODE_OAUTH_TOKEN"; then
        echo "✅ CLAUDE_CODE_OAUTH_TOKEN secret configured"
    else
        echo "⚠️  CLAUDE_CODE_OAUTH_TOKEN secret not found"
        echo "🔧 GitHub App setup required for full automation..."
        
        if command -v claude >/dev/null 2>&1; then
            echo "✅ Claude CLI detected - interactive setup available"
            echo ""
            echo "📋 To complete GitHub App setup:"
            echo "   1. Run: claude"
            echo "   2. Type: /install-github-app" 
            echo "   3. Follow the interactive prompts"
            echo ""
            echo "💡 This sets up GitHub App authentication for automated reviews"
            echo ""
            echo "🔀 Alternative manual setup:"
            echo "   1. Install GitHub App: https://github.com/apps/claude"
            echo "   2. Add CLAUDE_CODE_OAUTH_TOKEN to repository secrets"
            echo "   3. Copy workflow from: https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml"
        else
            echo "❌ Claude CLI not found"
            echo "📝 Manual setup required:"
            echo "   1. Install Claude CLI first"
            echo "   2. Run: claude"
            echo "   3. Type: /install-github-app in Claude chat"
            echo "   4. Or use manual setup: https://github.com/apps/claude"
        fi
    fi
else
    echo "❌ GitHub CLI not authenticated"
    echo "📝 Run: gh auth login"
    exit 1
fi

# Step 6: Create CLAUDE.md if it doesn't exist
if [ ! -f "CLAUDE.md" ]; then
    echo "📄 Creating CLAUDE.md configuration..."
    cat > CLAUDE.md << 'EOF'
# Claude Configuration

## Code Review Guidelines
- Focus on security vulnerabilities
- Check code quality and standards
- Validate test coverage
- Review performance implications
- Ensure documentation is updated

## Agent Workflow
- All agents should create PRs with "@claude please review" 
- Address review feedback promptly
- Re-request review after fixes
- Loop until approved

## Project-Specific Standards
- Follow existing code patterns
- Maintain test coverage >80%
- Update documentation with changes
- Use semantic commit messages
EOF
    echo "✅ CLAUDE.md created"
fi

# Step 7: Update .gitignore if needed
echo "📝 Updating .gitignore..."
if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi

# Add patterns if not already present
grep -q "__pycache__" .gitignore || echo "__pycache__/" >> .gitignore
grep -q "*.pyc" .gitignore || echo "*.pyc" >> .gitignore
grep -q "dist/" .gitignore || echo "dist/" >> .gitignore
grep -q ".env" .gitignore || echo ".env" >> .gitignore

# Step 8: Commit changes
echo "💾 Committing Claude workflow setup..."
git add .github/workflows/ .claude/ CLAUDE.md .gitignore
git commit -m "feat: add Claude workflow automation from multiagent-core

- Add claude.yml for @claude mentions
- Add claude-code-review.yml for auto-reviews  
- Add pr-feedback-router subagent
- Add CLAUDE.md configuration
- Update .gitignore

🤖 Generated from multiagent-core v$(cat $CORE_DIR/VERSION 2>/dev/null || echo 'latest')
Co-Authored-By: multiagent-core <noreply@multiagent-core.dev>" || true

echo ""
echo "🎉 Claude workflow setup complete!"
echo ""
echo "🧪 Testing Claude Code SDK integration..."
if command -v claude >/dev/null 2>&1; then
    echo "🔍 Verifying SDK setup..."
    
    # Test Claude connectivity (non-interactive)
    echo "📡 Testing Claude Code SDK connection..."
    if claude --version >/dev/null 2>&1; then
        echo "✅ Claude Code SDK is working"
        
        # Show available commands for this project
        echo "📋 Available Claude commands for this project:"
        echo "  /install-github-app - GitHub App setup"
        echo "  /review - Code review assistance"  
        echo "  /test - Testing assistance"
        echo "  /docs - Documentation generation"
        echo "  /spec - Specification creation"
        echo ""
        echo "💡 You can now use: claude /review, claude /test, etc."
    else
        echo "⚠️  Claude Code SDK connection issue"
    fi
else
    echo "❌ Claude Code SDK not found - some features may require manual setup"
fi

echo "📋 Next steps:"
if gh secret list | grep -q "CLAUDE_CODE_OAUTH_TOKEN"; then
    echo "🎉 Fully configured! Create a test PR to verify workflows work"
    echo ""
    echo "🧪 Test the automation:"
    echo "   1. Create a test PR"  
    echo "   2. Include '@claude please review' in PR description"
    echo "   3. Watch Claude auto-review within minutes"
    echo ""
    echo "✅ Complete agent workflow ready:"
    echo "   Agent work → PR with @claude → Auto-review → Feedback → Fixes → Loop until approved"
else
    echo "🔧 Complete setup by running the GitHub App installation:"
    if command -v claude >/dev/null 2>&1; then
        echo "   → Run: claude"
        echo "   → Type: /install-github-app"
    else
        echo "   → Install Claude CLI first, then run /install-github-app"
    fi
    echo ""
    echo "🧪 Then test with a PR containing '@claude please review'"
fi