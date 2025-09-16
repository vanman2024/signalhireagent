#!/bin/bash
# Add SignalHire Automation System to Any Project (with auto-updates)
#
# Usage: ./add-automation-to-project.sh <target-project-path>

set -e

TARGET_PROJECT="$1"

if [[ -z "$TARGET_PROJECT" ]]; then
    echo "Usage: $0 <target-project-path>"
    echo ""
    echo "Examples:"
    echo "  $0 ~/multi-agent-claude-code"
    echo "  $0 ~/my-other-project"
    exit 1
fi

if [[ ! -d "$TARGET_PROJECT" ]]; then
    echo "❌ Target directory does not exist: $TARGET_PROJECT"
    exit 1
fi

cd "$TARGET_PROJECT"

echo "🚀 Adding SignalHire Automation System to $(basename "$TARGET_PROJECT")..."

# Add this repo as remote (ignore if already exists)
git remote add signalhire-automation https://github.com/vanman2024/signalhireagent.git 2>/dev/null || true

# Add automation as subtree
echo "📁 Adding automation system as git subtree..."
git subtree add --prefix=automation-system signalhire-automation main --squash

# Copy the ops script to the standard location
echo "🔧 Setting up ops command..."
mkdir -p scripts
cp automation-system/scripts/ops scripts/
chmod +x scripts/ops

# Create project config
echo "⚙️ Creating project configuration..."
mkdir -p .automation
cat > .automation/config.yml << EOF
# Automation Config for $(basename "$TARGET_PROJECT")
versioning:
  strategy: conventional_commits
  source: pyproject.toml

targets:
  - $(basename "$TARGET_PROJECT")-deploy

release:
  changelog: true
  tag_prefix: v
  
qa:
  lint: true
  typecheck: true
  tests: "not slow"
  
env:
  wsl_check: true
  
hooks:
  auto_sync: false
EOF

# Update .gitignore
if [[ -f ".gitignore" ]]; then
    if ! grep -q ".automation/state" ".gitignore"; then
        echo "" >> .gitignore
        echo "# SignalHire Automation" >> .gitignore
        echo ".automation/state/" >> .gitignore
        echo ".automation/config/auto-sync-targets" >> .gitignore
        echo ".automation/config/continuous-deployment" >> .gitignore
    fi
fi

# Create update script
cat > update-automation.sh << 'EOF'
#!/bin/bash
# Update automation system from SignalHire repo
echo "🔄 Updating automation system..."
git subtree pull --prefix=automation-system signalhire-automation main --squash
cp automation-system/scripts/ops scripts/
echo "✅ Automation system updated!"
EOF
chmod +x update-automation.sh

echo "✅ Installation complete!"
echo ""
echo "🎯 Available commands:"
echo "  ./scripts/ops setup      # Initial setup"
echo "  ./scripts/ops qa         # Quality checks"
echo "  ./scripts/ops build      # Production builds"
echo "  ./scripts/ops release    # Create releases"
echo "  ./scripts/ops status     # Show status"
echo ""
echo "🔄 To update automation system:"
echo "  ./update-automation.sh"
echo ""
echo "🚀 Quick start: ./scripts/ops help"