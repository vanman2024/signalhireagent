#!/bin/bash
# Auto-Sync Configuration Manager
#
# PURPOSE: Manages automatic synchronization targets for production builds
# USAGE: ./auto-sync-config.sh [add|remove|list|sync] [target_directory]
# PART OF: Build and deployment system
# CONNECTS TO: build-production.sh, continuous deployment automation
#
# This script manages a list of target directories that should be automatically
# synchronized whenever the codebase changes, ensuring deployments stay current.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration file for sync targets
CONFIG_FILE=".auto-sync-targets"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_PATH="$REPO_ROOT/$CONFIG_FILE"

print_status() {
    echo -e "${BLUE}[AUTO-SYNC]${NC} $1"
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

# Ensure we're in the right directory
cd "$REPO_ROOT"

# Function to add a sync target
add_target() {
    local target_dir="$1"
    
    if [[ -z "$target_dir" ]]; then
        print_error "Target directory is required"
        echo "Usage: $0 add <target_directory>"
        exit 1
    fi
    
    # Convert to absolute path
    target_dir="$(realpath "$target_dir")"
    
    # Check if target already exists in config
    if [[ -f "$CONFIG_PATH" ]] && grep -q "^$target_dir$" "$CONFIG_PATH"; then
        print_warning "Target directory already configured: $target_dir"
        return 0
    fi
    
    # Add to config file
    echo "$target_dir" >> "$CONFIG_PATH"
    print_success "Added sync target: $target_dir"
    
    # Perform initial sync
    print_status "Performing initial sync..."
    sync_target "$target_dir"
}

# Function to remove a sync target
remove_target() {
    local target_dir="$1"
    
    if [[ -z "$target_dir" ]]; then
        print_error "Target directory is required"
        echo "Usage: $0 remove <target_directory>"
        exit 1
    fi
    
    # Convert to absolute path
    target_dir="$(realpath "$target_dir")"
    
    if [[ ! -f "$CONFIG_PATH" ]]; then
        print_error "No sync targets configured"
        exit 1
    fi
    
    # Remove from config file
    grep -v "^$target_dir$" "$CONFIG_PATH" > "$CONFIG_PATH.tmp" || true
    mv "$CONFIG_PATH.tmp" "$CONFIG_PATH"
    
    print_success "Removed sync target: $target_dir"
}

# Function to list sync targets
list_targets() {
    if [[ ! -f "$CONFIG_PATH" ]] || [[ ! -s "$CONFIG_PATH" ]]; then
        print_status "No sync targets configured"
        echo ""
        echo "Add targets with: $0 add <directory>"
        return 0
    fi
    
    print_status "Configured sync targets:"
    while IFS= read -r target_dir; do
        if [[ -n "$target_dir" ]]; then
            if [[ -d "$target_dir" ]]; then
                echo "  ✅ $target_dir"
            else
                echo "  ❌ $target_dir (directory does not exist)"
            fi
        fi
    done < "$CONFIG_PATH"
}

# Function to sync a single target
sync_target() {
    local target_dir="$1"
    
    print_status "Syncing to: $target_dir"
    
    # Use the build-production script for consistent builds
    "$SCRIPT_DIR/build-production.sh" "$target_dir" --latest --force
    
    if [[ $? -eq 0 ]]; then
        print_success "Sync completed: $target_dir"
        return 0
    else
        print_error "Sync failed: $target_dir"
        return 1
    fi
}

# Function to sync all configured targets
sync_all() {
    if [[ ! -f "$CONFIG_PATH" ]] || [[ ! -s "$CONFIG_PATH" ]]; then
        print_warning "No sync targets configured"
        return 0
    fi
    
    local failed_count=0
    local total_count=0
    
    print_status "Syncing all configured targets..."
    
    while IFS= read -r target_dir; do
        if [[ -n "$target_dir" ]]; then
            total_count=$((total_count + 1))
            if ! sync_target "$target_dir"; then
                failed_count=$((failed_count + 1))
            fi
        fi
    done < "$CONFIG_PATH"
    
    if [[ $failed_count -eq 0 ]]; then
        print_success "All $total_count targets synced successfully"
    else
        print_error "$failed_count of $total_count targets failed to sync"
        exit 1
    fi
}

# Function to check if auto-sync is needed (based on git changes)
check_auto_sync() {
    if [[ ! -f "$CONFIG_PATH" ]] || [[ ! -s "$CONFIG_PATH" ]]; then
        return 0  # No targets configured
    fi
    
    # Check if there are uncommitted changes or new commits since last sync
    local last_sync_file="$REPO_ROOT/.last-auto-sync"
    local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "no-git")
    
    if [[ -f "$last_sync_file" ]]; then
        local last_synced_commit=$(cat "$last_sync_file")
        if [[ "$current_commit" == "$last_synced_commit" ]]; then
            print_status "No changes since last sync"
            return 0
        fi
    fi
    
    print_status "Changes detected, auto-syncing..."
    if sync_all; then
        echo "$current_commit" > "$last_sync_file"
    fi
}

# Function to set up automated sync on git hooks
setup_git_hooks() {
    local hook_file="$REPO_ROOT/.git/hooks/post-commit"
    
    print_status "Setting up automatic sync on git commits..."
    
    # Create post-commit hook
    cat > "$hook_file" << 'EOF'
#!/bin/bash
# Auto-sync production builds after commits
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run auto-sync if configured
if [[ -f "$REPO_ROOT/scripts/build/auto-sync-config.sh" ]]; then
    "$REPO_ROOT/scripts/build/auto-sync-config.sh" check
fi
EOF
    
    chmod +x "$hook_file"
    print_success "Git post-commit hook installed"
}

# Function to show usage
show_usage() {
    echo "Auto-Sync Configuration Manager"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  add <directory>     Add a directory for automatic syncing"
    echo "  remove <directory>  Remove a directory from automatic syncing"
    echo "  list               List all configured sync targets"
    echo "  sync               Sync all configured targets now"
    echo "  check              Check if auto-sync is needed (for automation)"
    echo "  setup-hooks        Install git hooks for automatic syncing"
    echo "  status             Show sync status and configuration"
    echo ""
    echo "Examples:"
    echo "  $0 add ~/deployments/signalhire-staging"
    echo "  $0 add /var/www/signalhire-production"
    echo "  $0 list"
    echo "  $0 sync"
    echo "  $0 setup-hooks"
}

# Function to show status
show_status() {
    print_status "Auto-Sync Status"
    echo ""
    
    # Show git hook status
    local hook_file="$REPO_ROOT/.git/hooks/post-commit"
    if [[ -x "$hook_file" ]]; then
        echo "  Git Hooks: ✅ Installed (auto-sync on commit)"
    else
        echo "  Git Hooks: ❌ Not installed (run: $0 setup-hooks)"
    fi
    
    # Show last sync info
    local last_sync_file="$REPO_ROOT/.last-auto-sync"
    if [[ -f "$last_sync_file" ]]; then
        local last_commit=$(cat "$last_sync_file")
        local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "no-git")
        if [[ "$current_commit" == "$last_commit" ]]; then
            echo "  Last Sync: ✅ Current ($(echo "$last_commit" | cut -c1-8))"
        else
            echo "  Last Sync: ⚠️  Behind (last: $(echo "$last_commit" | cut -c1-8), current: $(echo "$current_commit" | cut -c1-8))"
        fi
    else
        echo "  Last Sync: ❌ Never synced"
    fi
    
    echo ""
    list_targets
}

# Main command handling
case "${1:-}" in
    "add")
        add_target "$2"
        ;;
    "remove")
        remove_target "$2"
        ;;
    "list")
        list_targets
        ;;
    "sync")
        sync_all
        ;;
    "check")
        check_auto_sync
        ;;
    "setup-hooks")
        setup_git_hooks
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac