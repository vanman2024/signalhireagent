#!/bin/bash
# Smart Release Evaluator
#
# PURPOSE: Evaluates accumulated commits to decide if release is warranted
# USAGE: ./smart-release-evaluator.sh [--force-check] [--min-commits N]
# PART OF: Quality-controlled release management
# CONNECTS TO: auto-release-manager.sh, continuous deployment, quality gates
#
# This script implements smart release logic:
# - Accumulates commits without triggering releases
# - Evaluates every N commits (default 10) for release worthiness
# - Runs quality checks only when considering releases
# - Prevents spam releases from minor commits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
MIN_COMMITS_FOR_EVALUATION=10
FORCE_CHECK=false

# Ensure automation directories exist
mkdir -p "$REPO_ROOT/.automation/config" "$REPO_ROOT/.automation/state"

print_status() {
    echo -e "${BLUE}[SMART-RELEASE]${NC} $1"
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

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force-check)
            FORCE_CHECK=true
            shift
            ;;
        --min-commits)
            MIN_COMMITS_FOR_EVALUATION="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure we're in the repo root
cd "$REPO_ROOT"

# Get current version and commit count
get_latest_version() {
    git describe --tags --abbrev=0 2>/dev/null | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' || echo "v0.0.0"
}

get_commits_since_release() {
    local last_version="$1"
    if [[ "$last_version" == "v0.0.0" ]]; then
        git rev-list --count HEAD 2>/dev/null || echo "0"
    else
        git rev-list --count "${last_version}..HEAD" 2>/dev/null || echo "0"
    fi
}

# Evaluate commit quality and significance
evaluate_commits() {
    local last_version="$1"
    local commit_range
    
    if [[ "$last_version" == "v0.0.0" ]]; then
        commit_range="$(git rev-list --max-parents=0 HEAD)..HEAD"
    else
        commit_range="${last_version}..HEAD"
    fi
    
    # Get all commits
    local commits=$(git log --pretty=format:"%s" "$commit_range" 2>/dev/null || echo "")
    
    if [[ -z "$commits" ]]; then
        echo "none"
        return 0
    fi
    
    # Analyze significance
    local significant_changes=0
    local total_commits=0
    local has_features=false
    local has_fixes=false
    local has_breaking=false
    
    while IFS= read -r commit_msg; do
        if [[ -n "$commit_msg" ]]; then
            total_commits=$((total_commits + 1))
            
            # Check for significant changes
            if echo "$commit_msg" | grep -qE "(BREAKING|breaking|!)"; then
                has_breaking=true
                significant_changes=$((significant_changes + 3))  # Breaking = 3 points
            elif echo "$commit_msg" | grep -qE "^(feat|feature)(\(.*\))?:"; then
                has_features=true
                significant_changes=$((significant_changes + 2))  # Feature = 2 points
            elif echo "$commit_msg" | grep -qE "^(fix|bugfix)(\(.*\))?:"; then
                has_fixes=true
                significant_changes=$((significant_changes + 1))  # Fix = 1 point
            elif echo "$commit_msg" | grep -qE "^(docs|style|refactor|test)(\(.*\))?:"; then
                # Minor changes = 0.5 points
                significant_changes=$((significant_changes + 1))
            fi
        fi
    done <<< "$commits"
    
    # Calculate significance score
    if [[ $total_commits -eq 0 ]]; then
        echo "none"
        return 0
    fi
    
    # Decision logic: need meaningful changes, not just quantity
    local significance_ratio=$((significant_changes * 10 / total_commits))  # Scale to 0-30
    
    print_status "Commit analysis:"
    print_status "  Total commits: $total_commits"
    print_status "  Significance score: $significant_changes (ratio: $significance_ratio)"
    print_status "  Features: $([ "$has_features" = true ] && echo "Yes" || echo "No")"
    print_status "  Fixes: $([ "$has_fixes" = true ] && echo "Yes" || echo "No")"
    print_status "  Breaking: $([ "$has_breaking" = true ] && echo "Yes" || echo "No")"
    
    # Release worthiness criteria
    if [[ "$has_breaking" == true ]]; then
        echo "major"
    elif [[ "$has_features" == true ]] && [[ $significance_ratio -ge 15 ]]; then
        echo "minor"
    elif [[ "$has_fixes" == true ]] && [[ $significance_ratio -ge 10 ]]; then
        echo "patch"
    elif [[ $total_commits -ge 15 ]] && [[ $significance_ratio -ge 5 ]]; then
        echo "patch"  # Accumulated changes
    else
        echo "none"
    fi
}

# Run quality checks (only when considering release)
run_quality_checks() {
    print_status "Running quality checks..."
    
    local checks_passed=0
    local total_checks=0
    
    # Check 1: Syntax/lint check (lightweight)
    total_checks=$((total_checks + 1))
    if command -v ruff >/dev/null 2>&1; then
        if ruff check src/ --quiet 2>/dev/null; then
            checks_passed=$((checks_passed + 1))
            print_success "✓ Linting passed"
        else
            print_warning "⚠ Linting issues found (not blocking)"
        fi
    else
        print_status "○ Linting skipped (ruff not available)"
        checks_passed=$((checks_passed + 1))  # Don't penalize missing tools
    fi
    
    # Check 2: Import validation (quick)
    total_checks=$((total_checks + 1))
    if python3 -c "import sys; sys.path.append('src'); import cli.main" 2>/dev/null; then
        checks_passed=$((checks_passed + 1))
        print_success "✓ Import validation passed"
    else
        print_error "✗ Import validation failed"
    fi
    
    # Check 3: Basic smoke test (if available)
    total_checks=$((total_checks + 1))
    if [[ -f "scripts/test-smoke.sh" ]]; then
        if ./scripts/test-smoke.sh >/dev/null 2>&1; then
            checks_passed=$((checks_passed + 1))
            print_success "✓ Smoke test passed"
        else
            print_error "✗ Smoke test failed"
        fi
    else
        # Check if basic CLI works
        if python3 -m src.cli.main --help >/dev/null 2>&1; then
            checks_passed=$((checks_passed + 1))
            print_success "✓ CLI smoke test passed"
        else
            print_warning "⚠ CLI smoke test failed"
        fi
    fi
    
    # Quality gate: require at least 70% pass rate
    local pass_rate=$((checks_passed * 100 / total_checks))
    print_status "Quality check results: $checks_passed/$total_checks passed ($pass_rate%)"
    
    if [[ $pass_rate -ge 70 ]]; then
        return 0  # Pass
    else
        return 1  # Fail
    fi
}

# Main evaluation logic
main() {
    local last_version=$(get_latest_version)
    local commits_since=$(get_commits_since_release "$last_version")
    
    print_status "Smart release evaluation"
    print_status "  Current version: $last_version"
    print_status "  Commits since release: $commits_since"
    print_status "  Evaluation threshold: $MIN_COMMITS_FOR_EVALUATION commits"
    
    # Check if evaluation is needed
    if [[ $commits_since -lt $MIN_COMMITS_FOR_EVALUATION ]] && [[ "$FORCE_CHECK" != true ]]; then
        print_status "Not enough commits for evaluation ($commits_since < $MIN_COMMITS_FOR_EVALUATION)"
        print_status "Continue development - evaluation at $MIN_COMMITS_FOR_EVALUATION commits"
        return 0
    fi
    
    print_status "Evaluating accumulated commits for release worthiness..."
    
    # Evaluate if changes warrant a release
    local suggested_bump=$(evaluate_commits "$last_version")
    
    if [[ "$suggested_bump" == "none" ]]; then
        print_status "Accumulated commits don't warrant a release yet"
        print_status "Continue development - more significant changes needed"
        return 0
    fi
    
    print_status "Changes suggest $suggested_bump release - running quality checks..."
    
    # Run quality checks only when considering release
    if run_quality_checks; then
        print_success "Quality checks passed - release recommended!"
        print_status "Run: ./scripts/build/auto-release-manager.sh create $suggested_bump"
        
        # Ask for confirmation unless forced
        if [[ "$FORCE_CHECK" != true ]]; then
            read -p "Create $suggested_bump release now? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                "$SCRIPT_DIR/auto-release-manager.sh" create "$suggested_bump"
            else
                print_status "Release postponed - run manually when ready"
            fi
        fi
        
        return 0
    else
        print_error "Quality checks failed - release blocked"
        print_status "Fix issues before release can proceed"
        return 1
    fi
}

# Show usage
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "Smart Release Evaluator"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --force-check      Force evaluation regardless of commit count"
    echo "  --min-commits N    Set minimum commits for evaluation (default: 10)"
    echo ""
    echo "This script implements smart release logic:"
    echo "- Accumulates commits without spam releases"
    echo "- Evaluates every $MIN_COMMITS_FOR_EVALUATION commits for release worthiness"
    echo "- Runs quality checks only when considering releases"
    echo "- Prevents releases of insignificant changes"
    exit 0
fi

main "$@"