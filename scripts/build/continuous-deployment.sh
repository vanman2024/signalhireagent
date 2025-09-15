#!/bin/bash
# Continuous Deployment Automation
#
# PURPOSE: Orchestrates complete automated deployment pipeline from code changes to production
# USAGE: ./continuous-deployment.sh [setup|deploy|status|watch] [--target DIR] [--auto-release]
# PART OF: Build and deployment system
# CONNECTS TO: auto-sync-config.sh, auto-release-manager.sh, build-production.sh, GitHub Actions
#
# This script provides complete automation by:
# - Setting up continuous deployment for specified targets
# - Automatically syncing code changes to deployment directories
# - Managing release versioning and GitHub releases
# - Coordinating all deployment components for seamless updates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

print_status() {
    echo -e "${BLUE}[CD]${NC} $1"
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

print_header() {
    echo -e "${PURPLE}[CONTINUOUS DEPLOYMENT]${NC} $1"
}

# Ensure we're in the repo root
cd "$REPO_ROOT"

# Configuration
AUTO_RELEASE=false
TARGET_DIR=""
WATCH_MODE=false

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --target)
                TARGET_DIR="$2"
                shift 2
                ;;
            --auto-release)
                AUTO_RELEASE=true
                shift
                ;;
            --watch)
                WATCH_MODE=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done
}

# Function to setup complete continuous deployment
setup_continuous_deployment() {
    print_header "Setting up Continuous Deployment"
    echo ""
    
    # Setup auto-sync system
    print_status "Installing auto-sync system..."
    "$SCRIPT_DIR/auto-sync-config.sh" setup-hooks
    
    # Setup auto-release system
    if [[ "$AUTO_RELEASE" == true ]]; then
        print_status "Installing auto-release system..."
        "$SCRIPT_DIR/auto-release-manager.sh" setup
    fi
    
    # Add target directory if specified
    if [[ -n "$TARGET_DIR" ]]; then
        print_status "Adding deployment target: $TARGET_DIR"
        "$SCRIPT_DIR/auto-sync-config.sh" add "$TARGET_DIR"
    fi
    
    # Create continuous deployment configuration
    local config_file="$REPO_ROOT/.continuous-deployment"
    cat > "$config_file" << EOF
# Continuous Deployment Configuration
# Generated on $(date)

AUTO_RELEASE=$AUTO_RELEASE
LAST_SETUP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VERSION=1.0.0
EOF
    
    print_success "Continuous deployment setup complete!"
    echo ""
    echo "Configuration:"
    echo "  Auto-Sync:     ✅ Enabled (syncs on every commit)"
    echo "  Auto-Release:  $([ "$AUTO_RELEASE" == true ] && echo "✅ Enabled" || echo "❌ Disabled")"
    echo "  Git Hooks:     ✅ Installed"
    if [[ -n "$TARGET_DIR" ]]; then
        echo "  Target:        $TARGET_DIR"
    fi
    echo ""
    echo "Next steps:"
    echo "  1. Make any code changes"
    echo "  2. Commit your changes: git add . && git commit -m 'feat: your changes'"
    echo "  3. Watch automatic deployment happen!"
    if [[ "$AUTO_RELEASE" == true ]]; then
        echo "  4. Automatic releases will be created for significant changes"
    fi
}

# Function to manually trigger deployment
trigger_deployment() {
    print_header "Manual Deployment Trigger"
    echo ""
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes. Consider committing them first."
        echo ""
    fi
    
    # Sync all targets
    print_status "Syncing all deployment targets..."
    "$SCRIPT_DIR/auto-sync-config.sh" sync
    
    # Check for potential release
    if [[ "$AUTO_RELEASE" == true ]]; then
        print_status "Checking for potential release..."
        if "$SCRIPT_DIR/auto-release-manager.sh" check; then
            # Exit code 2 means release is recommended
            if [[ $? -eq 2 ]]; then
                read -p "Create recommended release? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    "$SCRIPT_DIR/auto-release-manager.sh" create
                fi
            fi
        fi
    fi
    
    print_success "Deployment completed!"
}

# Function to show deployment status
show_status() {
    print_header "Continuous Deployment Status"
    echo ""
    
    # Check if CD is configured
    local config_file="$REPO_ROOT/.continuous-deployment"
    if [[ ! -f "$config_file" ]]; then
        print_warning "Continuous deployment not configured"
        echo "Run: $0 setup [--target DIR] [--auto-release]"
        return 1
    fi
    
    # Load configuration
    source "$config_file"
    
    echo "  Setup Date:    $LAST_SETUP"
    echo "  Auto-Release:  $([ "$AUTO_RELEASE" == true ] && echo "✅ Enabled" || echo "❌ Disabled")"
    echo ""
    
    # Show auto-sync status
    "$SCRIPT_DIR/auto-sync-config.sh" status
    echo ""
    
    # Show release status if auto-release is enabled
    if [[ "$AUTO_RELEASE" == true ]]; then
        "$SCRIPT_DIR/auto-release-manager.sh" status
    fi
}

# Function to watch for changes and auto-deploy
watch_deployment() {
    print_header "Watching for Changes (Ctrl+C to stop)"
    echo ""
    
    local last_commit=$(git rev-parse HEAD)
    
    while true; do
        sleep 5
        
        # Check for new commits
        local current_commit=$(git rev-parse HEAD)
        if [[ "$current_commit" != "$last_commit" ]]; then
            print_status "New commit detected: $(echo "$current_commit" | cut -c1-8)"
            
            # Trigger auto-sync
            "$SCRIPT_DIR/auto-sync-config.sh" check
            
            # Check for auto-release if enabled
            if [[ "$AUTO_RELEASE" == true ]]; then
                "$SCRIPT_DIR/auto-release-manager.sh" check
            fi
            
            last_commit="$current_commit"
        fi
    done
}

# Function to create development workflow integration
create_dev_workflow() {
    print_status "Creating development workflow integration..."
    
    # Create convenience script for developers
    cat > "$REPO_ROOT/deploy" << 'EOF'
#!/bin/bash
# Quick deployment helper
# Usage: ./deploy [target_directory]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "$1" ]]; then
    # Deploy to specific target
    "$SCRIPT_DIR/scripts/build/build-production.sh" "$1" --latest --force
else
    # Use continuous deployment system
    "$SCRIPT_DIR/scripts/build/continuous-deployment.sh" deploy
fi
EOF
    
    chmod +x "$REPO_ROOT/deploy"
    
    # Create setup helper
    cat > "$REPO_ROOT/setup-cd" << 'EOF'
#!/bin/bash
# Continuous deployment setup helper
# Usage: ./setup-cd [target_directory]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "$1" ]]; then
    "$SCRIPT_DIR/scripts/build/continuous-deployment.sh" setup --target "$1" --auto-release
else
    echo "Usage: $0 <target_directory>"
    echo "Example: $0 ~/deployments/signalhire-staging"
    exit 1
fi
EOF
    
    chmod +x "$REPO_ROOT/setup-cd"
    
    print_success "Development workflow helpers created:"
    echo "  ./deploy [target]     - Quick deployment"
    echo "  ./setup-cd <target>   - Setup continuous deployment"
}

# Function to show usage
show_usage() {
    echo "Continuous Deployment Automation"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  setup      Setup continuous deployment system"
    echo "  deploy     Trigger manual deployment"
    echo "  status     Show deployment status and configuration"
    echo "  watch      Watch for changes and auto-deploy (interactive)"
    echo ""
    echo "Options:"
    echo "  --target DIR       Add deployment target directory"
    echo "  --auto-release     Enable automatic release management"
    echo ""
    echo "Examples:"
    echo "  $0 setup --target ~/staging --auto-release"
    echo "  $0 deploy"
    echo "  $0 status"
    echo "  $0 watch"
    echo ""
    echo "Quick Setup:"
    echo "  # Full automation with staging deployment"
    echo "  $0 setup --target ~/deployments/signalhire-staging --auto-release"
    echo ""
    echo "  # Then make changes and commit - everything else is automatic!"
}

# Parse arguments first
parse_args "$@"

# Main command handling
case "${1:-}" in
    "setup")
        setup_continuous_deployment
        create_dev_workflow
        ;;
    "deploy")
        trigger_deployment
        ;;
    "status")
        show_status
        ;;
    "watch")
        watch_deployment
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_usage
        exit 1
        ;;
esac