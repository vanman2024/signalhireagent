# 🔧 Integration Guide: Deployment Automation

Step-by-step guide to integrate deployment automation into any project.

## 🎯 Overview

This package provides complete deployment automation that can be added to any project in 5 minutes. Perfect for your multi-agent-claude-code template system.

## 📋 Prerequisites

- Git repository
- Python project (can be adapted for other languages)
- Optional: GitHub repository for automatic releases

## 🚀 Integration Steps

### Step 1: Copy Automation Package

```bash
# From the automation package directory
cp -r scripts/ /path/to/your/project/
cp -r .automation/ /path/to/your/project/
cp templates/quick-start.md /path/to/your/project/DEPLOYMENT.md
```

### Step 2: Update .gitignore

Add these lines to your project's `.gitignore`:

```gitignore
# Automation system files (state and user-specific configs)
.automation/state/
.automation/config/auto-sync-targets
.automation/config/continuous-deployment
```

### Step 3: Make Scripts Executable

```bash
chmod +x scripts/build/*.sh scripts/deploy scripts/setup-cd
```

### Step 4: Initial Setup

```bash
# Setup automation for your project
./scripts/build/continuous-deployment.sh setup --target ~/deployments/your-project --auto-release
```

### Step 5: Test the System

```bash
# Make a test change
echo "# Test" > test-automation.md
git add test-automation.md
git commit -m "feat: test deployment automation"

# Should automatically:
# ✅ Sync to deployment target
# ✅ Suggest/create release
# ✅ Trigger GitHub Actions (if configured)
```

## 🔧 Customization for Your Project

### For Multi-Agent Projects

Update the production build script to include agent instruction files:

```bash
# In scripts/build/build-production.sh, add your agent files
cp CLAUDE.md "$TARGET_DIR/" 2>/dev/null || true
cp GEMINI.md "$TARGET_DIR/" 2>/dev/null || true
cp AGENTS.md "$TARGET_DIR/" 2>/dev/null || true
cp -r .github/copilot-instructions.md "$TARGET_DIR/.github/" 2>/dev/null || true
```

### For Different Tech Stacks

Modify `scripts/build/build-production.sh`:

**Node.js projects:**
```bash
# Replace Python requirements with package.json
cp package.json "$TARGET_DIR/"
cp package-lock.json "$TARGET_DIR/" 2>/dev/null || true

# Create production install script
cat > "$TARGET_DIR/install.sh" << 'EOF'
#!/bin/bash
npm ci --production
EOF
```

**Go projects:**
```bash
# Copy Go files
cp go.mod go.sum "$TARGET_DIR/"
rsync -av --exclude='*_test.go' --exclude='.git' . "$TARGET_DIR/src/"
```

### Custom Release Patterns

Modify release detection in `scripts/build/auto-release-manager.sh`:

```bash
# Add your own commit patterns
elif echo "$commit_msg" | grep -qE "^(enhance|improve)(\(.*\))?:"; then
    has_features=true  # Treat enhance: as feature
```

## 🌐 GitHub Actions Integration

Create `.github/workflows/release.yml` in your project:

```yaml
name: Release
on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js  # or Python, Go, etc.
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Build Production
        run: |
          ./scripts/build/build-production.sh release-build --latest --force
          cd release-build && tar -czf ../release.tar.gz .
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: release.tar.gz
          generate_release_notes: true
```

## 📁 Integration with Your Sync Template

Add to your `sync-project-template.sh`:

```bash
# Add deployment automation
echo "🚀 Setting up deployment automation..."

# Copy automation scripts
if [[ -d "automation-template-package" ]]; then
    cp -r automation-template-package/scripts/ .
    mkdir -p .automation
    cp -r automation-template-package/.automation/README.md .automation/
    
    # Add to .gitignore if not present
    if ! grep -q ".automation/state/" .gitignore 2>/dev/null; then
        cat automation-template-package/.gitignore-additions >> .gitignore
    fi
    
    # Make scripts executable
    chmod +x scripts/build/*.sh scripts/deploy scripts/setup-cd
    
    echo "✅ Deployment automation installed"
    echo "📖 See DEPLOYMENT.md for usage instructions"
    
    # Create user guide
    cp automation-template-package/templates/quick-start.md DEPLOYMENT.md
else
    echo "⚠️  Automation package not found, skipping deployment setup"
fi
```

## 🎯 Project-Specific Configurations

### For AI Agent Projects

Add agent coordination to deployment:

```bash
# In your project's custom configuration
echo "AI_AGENT_COORDINATION=enabled" >> .automation/config/project.env
echo "CLAUDE_CODE_INTEGRATION=true" >> .automation/config/project.env
```

### For MCP (Master Control Program) Projects

```bash
# Include MCP server files in production builds
cp -r mcp/ "$TARGET_DIR/" 2>/dev/null || true
cp mcp.config.json "$TARGET_DIR/" 2>/dev/null || true
```

## 🔍 Verification

After integration, verify everything works:

```bash
# Check automation status
./scripts/build/continuous-deployment.sh status

# Test production build
./scripts/build/build-production.sh test-build --latest --force
cd test-build && ls -la

# Test convenience scripts
./scripts/deploy --help
./scripts/setup-cd --help
```

## 🛠️ Troubleshooting

### Common Issues

**Scripts not executable:**
```bash
find scripts/ -name "*.sh" -exec chmod +x {} \;
```

**Missing dependencies:**
```bash
# Install rsync if not available
sudo apt update && sudo apt install rsync
```

**Git hooks not working:**
```bash
# Reinstall git hooks
./scripts/build/auto-sync-config.sh setup-hooks
./scripts/build/auto-release-manager.sh setup
```

## 📚 Next Steps

1. **Configure deployment targets** for your environments
2. **Add GitHub Actions** for automated releases  
3. **Customize build process** for your tech stack
4. **Train team** on automated workflow
5. **Add to project template** for future projects

## 🎉 Result

After integration, your development workflow becomes:

```bash
git add .
git commit -m "feat: amazing new feature"
# → Everything else happens automatically! 🚀
```

Perfect for rapid development and professional deployment workflows.