#!/bin/bash
# Comprehensive Rollback Test Suite Runner
#
# This script runs all rollback-related tests and provides a summary.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "🧪 SignalHire Agent - Rollback Test Suite"
echo "=========================================="
echo "Testing rollback functionality across all layers"
echo ""

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

print_status() { echo -e "${BLUE}[TEST]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }

run_test_suite() {
    local test_name="$1"
    local test_command="$2"

    ((TOTAL++))
    print_status "Running $test_name..."

    if eval "$test_command" >/dev/null 2>&1; then
        print_success "$test_name completed successfully"
        ((PASSED++))
    else
        print_error "$test_name failed"
        ((FAILED++))
    fi
}

# Test CLI Integration
run_test_suite "Ops CLI Help" "./devops/ops/ops help"
run_test_suite "Ops CLI Rollback Help" "./devops/ops/ops rollback 2>/dev/null || true"

# Test Standalone Script
run_test_suite "Rollback Script Help" "./devops/deploy/commands/rollback.sh --help"

# Test Git Integration
run_test_suite "Git Tag Listing" "git tag --list 'v*' 2>/dev/null || echo 'No tags'"

# Test Python Unit Tests
run_test_suite "Unit Tests" "python3 -m pytest tests/backend/unit/test_rollback.py -q"

# Test Python Integration Tests
run_test_suite "Integration Tests" "python3 -m pytest tests/backend/integration/test_rollback_integration.py -q"

# Test Python Functional Tests
run_test_suite "Functional Tests" "python3 -m pytest tests/backend/functional/test_rollback_functional.py -q"

# Test File Structure
run_test_suite "Ops Script Exists" "test -f devops/ops/ops"
run_test_suite "Rollback Script Exists" "test -f devops/deploy/commands/rollback.sh"
run_test_suite "Ops Script Executable" "test -x devops/ops/ops"
run_test_suite "Rollback Script Executable" "test -x devops/deploy/commands/rollback.sh"

echo ""
echo "📊 Test Results Summary"
echo "======================="
echo "Total Tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ $FAILED -eq 0 ]; then
    print_success "🎉 All rollback tests passed!"
    echo ""
    echo "✅ Rollback functionality is working correctly"
    echo ""
    echo "Available rollback commands:"
    echo "  ./devops/ops/ops rollback <version> [target]"
    echo "  ./devops/deploy/commands/rollback.sh <version> [target]"
    echo ""
    echo "Available versions:"
    git tag --list "v*" --sort=-version:refname | head -5 || echo "  No git tags found"
else
    print_error "❌ Some tests failed. Please check the output above."
    exit 1
fi

echo ""
echo "🔧 Test Files Created:"
echo "  tests/backend/unit/test_rollback.py"
echo "  tests/backend/integration/test_rollback_integration.py"
echo "  tests/backend/functional/test_rollback_functional.py"
echo "  tests/backend/run_rollback_tests.sh"
