#!/bin/bash
# Automated Project Integration Script for Deployment Automation
#
# PURPOSE: Integrates deployment automation into any project automatically
# USAGE: ./project-integration.sh [--target DEPLOY_DIR] [--auto-release]
# PART OF: Deployment automation template package
# CONNECTS TO: Multi-agent project sync system, continuous deployment
#
# This script safely integrates deployment automation into existing projects
# without overwriting existing configurations or breaking current workflows.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}[AUTOMATION INTEGRATION]${NC} $1"
}

print_status() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default options
DEPLOY_TARGET=""
AUTO_RELEASE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            DEPLOY_TARGET="$2"
            shift 2
            ;;
        --auto-release)
            AUTO_RELEASE=true
            shift
            ;;
        -h|--help)
            echo "Automated Project Integration for Deployment Automation"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --target DIR       Setup deployment target directory"
            echo "  --auto-release     Enable automatic release management"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --target ~/staging --auto-release"
            echo "  $0 --target /var/www/production"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "Integrating Deployment Automation"
echo ""

# Verify we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    print_error "This must be run in a git repository"
    exit 1
fi

# Check if automation is already installed
if [[ -d "scripts/build" ]]; then
    print_warning "Deployment automation appears to already be installed"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
fi

# Step 1: Copy automation scripts
print_status "Installing automation scripts..."
if [[ -d "$PROJECT_ROOT/scripts" ]]; then
    cp -r "$PROJECT_ROOT/scripts/"* scripts/ 2>/dev/null || true
    mkdir -p scripts/build
    cp -r "$PROJECT_ROOT/scripts/build/"* scripts/build/
    cp "$PROJECT_ROOT/scripts/deploy" "$PROJECT_ROOT/scripts/setup-cd" scripts/ 2>/dev/null || true
else
    print_error "Automation scripts not found in package"
    exit 1
fi

# Make scripts executable
find scripts/ -name "*.sh" -exec chmod +x {} \;
chmod +x scripts/deploy scripts/setup-cd 2>/dev/null || true

print_success "Automation scripts installed"

# Step 2: Setup automation directory structure
print_status "Creating automation directory structure..."
mkdir -p .automation/config .automation/state
if [[ -f "$PROJECT_ROOT/.automation/README.md" ]]; then
    cp "$PROJECT_ROOT/.automation/README.md" .automation/
fi

print_success "Automation directories created"

# Step 3: Update .gitignore
print_status "Updating .gitignore..."
if [[ -f ".gitignore" ]]; then
    # Check if automation rules already exist
    if ! grep -q ".automation/state/" .gitignore 2>/dev/null; then
        echo "" >> .gitignore
        echo "# Automation system files (state and user-specific configs)" >> .gitignore
        echo ".automation/state/" >> .gitignore
        echo ".automation/config/auto-sync-targets" >> .gitignore
        echo ".automation/config/continuous-deployment" >> .gitignore
        print_success "Added automation rules to .gitignore"
    else
        print_status "Automation rules already in .gitignore"
    fi
else
    # Create .gitignore with automation rules
    cat > .gitignore << 'EOF'
# Automation system files (state and user-specific configs)
.automation/state/
.automation/config/auto-sync-targets
.automation/config/continuous-deployment
EOF
    print_success "Created .gitignore with automation rules"
fi

# Step 4: Create user documentation
print_status "Creating deployment documentation..."
if [[ -f "$PROJECT_ROOT/templates/quick-start.md" ]]; then
    cp "$PROJECT_ROOT/templates/quick-start.md" DEPLOYMENT.md
    print_success "Created DEPLOYMENT.md user guide"
else
    # Create basic documentation
    cat > DEPLOYMENT.md << 'EOF'
# 🚀 Deployment Automation

This project includes automated deployment and release management.

## Quick Start

```bash
# Setup automation for your deployment
./scripts/build/continuous-deployment.sh setup --target ~/your-deployment --auto-release

# Daily workflow (everything else is automatic)
git add .
git commit -m "feat: your changes"
```

## Commands

- `./scripts/build/continuous-deployment.sh status` - Check automation status
- `./scripts/deploy [target]` - Quick deployment to any directory
- `./scripts/setup-cd <target>` - Setup new deployment target

## Automatic Features

- **Auto-sync** to deployment targets on every commit
- **Semantic versioning** based on commit patterns (`feat:`, `fix:`, etc.)
- **GitHub releases** with automatic changelogs
- **Clean production builds** excluding development files

See `scripts/build/README.md` for complete documentation.
EOF
    print_success "Created basic DEPLOYMENT.md guide"
fi

# Step 5: Setup automation system
if [[ -n "$DEPLOY_TARGET" ]]; then
    print_status "Setting up deployment automation..."
    
    # Setup the automation system
    local setup_args="--target $DEPLOY_TARGET"
    if [[ "$AUTO_RELEASE" == true ]]; then
        setup_args="$setup_args --auto-release"
    fi
    
    ./scripts/build/continuous-deployment.sh setup $setup_args
    print_success "Deployment automation configured"
else
    print_status "Installing git hooks for manual setup..."
    ./scripts/build/auto-sync-config.sh setup-hooks
    if [[ "$AUTO_RELEASE" == true ]]; then
        ./scripts/build/auto-release-manager.sh setup
    fi
    print_success "Git hooks installed"
fi

# Step 6: Create GitHub Actions template (optional)
if [[ -d ".github/workflows" ]] || [[ -n "$(git remote get-url origin 2>/dev/null | grep github)" ]]; then
    print_status "Creating GitHub Actions template..."
    mkdir -p .github/workflows
    
    # Detect project type for appropriate workflow
    if [[ -f "package.json" ]]; then
        PROJECT_TYPE="node"
    elif [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        PROJECT_TYPE="python"
    elif [[ -f "go.mod" ]]; then
        PROJECT_TYPE="go"
    else
        PROJECT_TYPE="generic"
    fi
    
    cat > .github/workflows/release.yml << EOF
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
      
      - name: Setup Environment
        run: |
          # Add your environment setup here
          echo "Setting up for $PROJECT_TYPE project"
      
      - name: Build Production
        run: |
          ./scripts/build/build-production.sh release-build --latest --force
          cd release-build && tar -czf ../release.tar.gz .
      
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: release.tar.gz
          generate_release_notes: true
EOF
    
    print_success "Created GitHub Actions workflow template"
fi

# Final summary
print_header "Integration Complete!"
echo ""
print_success "✅ Automation scripts installed in scripts/build/"
print_success "✅ Git hooks configured for automatic sync"
if [[ "$AUTO_RELEASE" == true ]]; then
    print_success "✅ Automatic release management enabled"
fi
if [[ -n "$DEPLOY_TARGET" ]]; then
    print_success "✅ Deployment target configured: $DEPLOY_TARGET"
fi
print_success "✅ Documentation created: DEPLOYMENT.md"

echo ""
print_status "Next steps:"
if [[ -z "$DEPLOY_TARGET" ]]; then
    echo "  1. Setup deployment: ./scripts/build/continuous-deployment.sh setup --target ~/your-deployment"
fi
echo "  2. Test the system: make a commit with 'feat:' or 'fix:' prefix"
echo "  3. Check status: ./scripts/build/continuous-deployment.sh status"
echo "  4. Read the guide: cat DEPLOYMENT.md"

echo ""
print_header "Deployment automation ready! 🚀"