#!/bin/bash
# Automatic Release Tag Manager
#
# PURPOSE: Automatically detects changes and creates release tags with semantic versioning
# USAGE: ./auto-release-manager.sh [check|create|bump] [major|minor|patch]
# PART OF: Build and deployment system  
# CONNECTS TO: GitHub Actions workflow, auto-sync-config.sh, production builds
#
# This script automatically manages release versioning by:
# - Detecting significant changes that warrant new releases
# - Creating semantic version tags automatically
# - Triggering production builds and GitHub Actions
# - Coordinating with auto-sync system for immediate deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

print_status() {
    echo -e "${BLUE}[RELEASE]${NC} $1"
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

# Ensure we're in the repo root
cd "$REPO_ROOT"

# Function to get the latest version tag
get_latest_version() {
    git describe --tags --abbrev=0 2>/dev/null | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' || echo "v0.0.0"
}

# Function to parse version components
parse_version() {
    local version="$1"
    # Remove 'v' prefix and split into components
    version="${version#v}"
    echo "$version" | tr '.' ' '
}

# Function to increment version
increment_version() {
    local current_version="$1"
    local bump_type="$2"
    
    read -r major minor patch <<< "$(parse_version "$current_version")"
    
    case "$bump_type" in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid bump type: $bump_type (use: major, minor, patch)"
            exit 1
            ;;
    esac
    
    echo "v${major}.${minor}.${patch}"
}

# Function to analyze commits since last release to determine bump type
analyze_commits() {
    local last_version="$1"
    local commit_range
    
    if [[ "$last_version" == "v0.0.0" ]]; then
        # No previous tags, analyze all commits
        commit_range="$(git rev-list --max-parents=0 HEAD)..HEAD"
    else
        # Analyze commits since last tag
        commit_range="${last_version}..HEAD"
    fi
    
    # Get commit messages
    local commits=$(git log --pretty=format:"%s" "$commit_range" 2>/dev/null || echo "")
    
    if [[ -z "$commits" ]]; then
        echo "none"
        return 0
    fi
    
    # Analyze commit patterns for semantic versioning
    local has_breaking=false
    local has_features=false
    local has_fixes=false
    
    while IFS= read -r commit_msg; do
        if [[ -n "$commit_msg" ]]; then
            # Check for breaking changes
            if echo "$commit_msg" | grep -qE "(BREAKING|breaking|!)"; then
                has_breaking=true
            # Check for new features
            elif echo "$commit_msg" | grep -qE "^(feat|feature)(\(.*\))?:"; then
                has_features=true
            # Check for fixes
            elif echo "$commit_msg" | grep -qE "^(fix|bugfix)(\(.*\))?:"; then
                has_fixes=true
            fi
        fi
    done <<< "$commits"
    
    # Determine bump type based on analysis
    if [[ "$has_breaking" == true ]]; then
        echo "major"
    elif [[ "$has_features" == true ]]; then
        echo "minor"
    elif [[ "$has_fixes" == true ]]; then
        echo "patch"
    else
        # Default to patch for any other changes
        echo "patch"
    fi
}

# Function to check if a new release should be created
check_release_needed() {
    local last_version=$(get_latest_version)
    local last_release_file="$REPO_ROOT/.last-release-check"
    local current_commit=$(git rev-parse HEAD)
    
    # Check if we have any commits since last version tag
    if [[ "$last_version" != "v0.0.0" ]]; then
        local commits_since=$(git rev-list "${last_version}..HEAD" --count 2>/dev/null || echo "0")
        if [[ "$commits_since" -eq 0 ]]; then
            print_status "No commits since last release ($last_version)"
            return 1
        fi
    fi
    
    # Check if we've already checked this commit
    if [[ -f "$last_release_file" ]]; then
        local last_checked_commit=$(cat "$last_release_file")
        if [[ "$current_commit" == "$last_checked_commit" ]]; then
            print_status "Already checked current commit for releases"
            return 1
        fi
    fi
    
    local suggested_bump=$(analyze_commits "$last_version")
    
    if [[ "$suggested_bump" == "none" ]]; then
        print_status "No significant changes detected for release"
        echo "$current_commit" > "$last_release_file"
        return 1
    fi
    
    local new_version=$(increment_version "$last_version" "$suggested_bump")
    
    print_status "Release recommended:"
    echo "  Current version: $last_version"
    echo "  Suggested bump:  $suggested_bump"
    echo "  New version:     $new_version"
    
    return 0
}

# Function to create a new release tag
create_release() {
    local bump_type="$1"
    local current_version=$(get_latest_version)
    
    if [[ -z "$bump_type" ]]; then
        # Auto-detect bump type
        bump_type=$(analyze_commits "$current_version")
        if [[ "$bump_type" == "none" ]]; then
            print_warning "No significant changes detected. Use explicit bump type if needed."
            return 1
        fi
    fi
    
    local new_version=$(increment_version "$current_version" "$bump_type")
    
    print_status "Creating release $new_version (bump: $bump_type)"
    
    # Generate release notes from commit messages
    local commit_range
    if [[ "$current_version" == "v0.0.0" ]]; then
        commit_range="$(git rev-list --max-parents=0 HEAD)..HEAD"
    else
        commit_range="${current_version}..HEAD"
    fi
    
    local release_notes_file=$(mktemp)
    {
        echo "# Release $new_version"
        echo ""
        echo "## Changes since $current_version"
        echo ""
        
        # Categorize commits
        local features=$(git log --pretty=format:"- %s" "$commit_range" | grep -E "^- (feat|feature)(\(.*\))?:" || true)
        local fixes=$(git log --pretty=format:"- %s" "$commit_range" | grep -E "^- (fix|bugfix)(\(.*\))?:" || true)
        local others=$(git log --pretty=format:"- %s" "$commit_range" | grep -vE "^- (feat|feature|fix|bugfix)(\(.*\))?:" || true)
        
        if [[ -n "$features" ]]; then
            echo "### ✨ New Features"
            echo "$features"
            echo ""
        fi
        
        if [[ -n "$fixes" ]]; then
            echo "### 🐛 Bug Fixes"
            echo "$fixes"
            echo ""
        fi
        
        if [[ -n "$others" ]]; then
            echo "### 🔧 Other Changes"
            echo "$others"
            echo ""
        fi
        
        echo "**Full Changelog**: https://github.com/$(git remote get-url origin | sed 's/.*github.com[/:]\([^/]*\/[^/]*\)\.git.*/\1/')/compare/${current_version}...${new_version}"
    } > "$release_notes_file"
    
    # Create and push the tag
    git tag -a "$new_version" -F "$release_notes_file"
    
    print_success "Created release tag: $new_version"
    
    # Push the tag to trigger GitHub Actions
    if git remote get-url origin >/dev/null 2>&1; then
        print_status "Pushing tag to remote repository..."
        git push origin "$new_version"
        print_success "Tag pushed to remote. GitHub Actions will build and release."
    else
        print_warning "No remote repository configured. Tag created locally only."
    fi
    
    # Update last release check
    echo "$(git rev-parse HEAD)" > "$REPO_ROOT/.last-release-check"
    
    # Trigger auto-sync if configured
    if [[ -f "$SCRIPT_DIR/auto-sync-config.sh" ]]; then
        print_status "Triggering auto-sync for new release..."
        "$SCRIPT_DIR/auto-sync-config.sh" sync
    fi
    
    # Clean up
    rm -f "$release_notes_file"
    
    return 0
}

# Function to setup automatic release checking
setup_auto_releases() {
    local hook_file="$REPO_ROOT/.git/hooks/post-commit"
    
    print_status "Setting up automatic release detection..."
    
    # Check if hook already exists
    if [[ -f "$hook_file" ]]; then
        # Append to existing hook
        if ! grep -q "auto-release-manager.sh" "$hook_file"; then
            cat >> "$hook_file" << 'EOF'

# Auto-release detection after commits
if [[ -f "$REPO_ROOT/scripts/build/auto-release-manager.sh" ]]; then
    "$REPO_ROOT/scripts/build/auto-release-manager.sh" check
fi
EOF
        fi
    else
        # Create new hook
        cat > "$hook_file" << 'EOF'
#!/bin/bash
# Auto-release detection after commits
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ -f "$REPO_ROOT/scripts/build/auto-release-manager.sh" ]]; then
    "$REPO_ROOT/scripts/build/auto-release-manager.sh" check
fi
EOF
    fi
    
    chmod +x "$hook_file"
    print_success "Automatic release detection installed in git hooks"
}

# Function to show current release status
show_status() {
    local current_version=$(get_latest_version)
    local commits_since
    
    print_status "Release Status"
    echo ""
    
    echo "  Current Version: $current_version"
    
    if [[ "$current_version" != "v0.0.0" ]]; then
        commits_since=$(git rev-list "${current_version}..HEAD" --count 2>/dev/null || echo "0")
        echo "  Commits Since:   $commits_since"
        
        if [[ "$commits_since" -gt 0 ]]; then
            local suggested_bump=$(analyze_commits "$current_version")
            if [[ "$suggested_bump" != "none" ]]; then
                local next_version=$(increment_version "$current_version" "$suggested_bump")
                echo "  Suggested Next:  $next_version ($suggested_bump bump)"
            else
                echo "  Suggested Next:  No release needed"
            fi
        else
            echo "  Status:          Up to date"
        fi
    else
        echo "  Status:          No releases yet"
        local suggested_bump=$(analyze_commits "$current_version")
        if [[ "$suggested_bump" != "none" ]]; then
            local next_version=$(increment_version "$current_version" "$suggested_bump")
            echo "  First Release:   $next_version"
        fi
    fi
    
    # Check git hooks
    local hook_file="$REPO_ROOT/.git/hooks/post-commit"
    if [[ -f "$hook_file" ]] && grep -q "auto-release-manager.sh" "$hook_file"; then
        echo "  Auto-Release:    ✅ Enabled"
    else
        echo "  Auto-Release:    ❌ Disabled (run: $0 setup)"
    fi
}

# Function to show usage
show_usage() {
    echo "Automatic Release Tag Manager"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  check               Check if a new release is needed"
    echo "  create [bump_type]  Create a new release (major|minor|patch, auto-detected if omitted)"
    echo "  bump <bump_type>    Alias for create with explicit bump type"
    echo "  setup               Install automatic release detection in git hooks"
    echo "  status              Show current release status and suggestions"
    echo ""
    echo "Examples:"
    echo "  $0 check            # Check if release is needed"
    echo "  $0 create           # Auto-detect and create release"
    echo "  $0 create minor     # Force minor version bump"
    echo "  $0 setup            # Install git hooks"
    echo "  $0 status           # Show release status"
}

# Main command handling
case "${1:-}" in
    "check")
        if check_release_needed; then
            print_status "New release recommended. Run '$0 create' to create it."
            exit 2  # Special exit code to indicate release needed
        fi
        ;;
    "create")
        create_release "$2"
        ;;
    "bump")
        if [[ -z "$2" ]]; then
            print_error "Bump type required (major|minor|patch)"
            exit 1
        fi
        create_release "$2"
        ;;
    "setup")
        setup_auto_releases
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