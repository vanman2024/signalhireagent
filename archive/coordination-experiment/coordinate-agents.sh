#!/usr/bin/env bash
# Multi-Agent Coordinator Wrapper Script
#
# Usage:
#   ./scripts/coordinate-agents.sh           # Run once in dry-run mode
#   ./scripts/coordinate-agents.sh --live    # Run once and execute tasks
#   ./scripts/coordinate-agents.sh --loop    # Run continuously (live mode)
#   ./scripts/coordinate-agents.sh --help    # Show help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COORDINATOR="$SCRIPT_DIR/agent-coordinator.py"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

usage() {
    echo "Multi-Agent Coordinator for SignalHire Agent Development"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --live      Execute tasks (default is dry-run)"
    echo "  --loop      Run continuously instead of once"
    echo "  --interval N  Loop interval in seconds (default: 60)"
    echo "  --help      Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                    # Check what would be executed (dry-run)"
    echo "  $0 --live            # Execute ready tasks once"
    echo "  $0 --live --loop     # Run coordinator continuously"
    echo ""
    echo "Agent Assignment Status:"
    echo "  @codex     - Can be called programmatically ✓"
    echo "  @gemini    - Can be called programmatically ✓" 
    echo "  @copilot   - Requires manual execution in VS Code"
    echo "  @claude    - Handled by Worker Claude instance"
}

check_prerequisites() {
    # Check if we're in the right directory
    if [[ ! -f "$COORDINATOR" ]]; then
        echo -e "${RED}ERROR: Coordinator script not found at $COORDINATOR${NC}"
        exit 1
    fi
    
    # Check if tasks.md exists
    if [[ ! -f "$REPO_ROOT/specs/001-looking-to-build/tasks.md" ]]; then
        echo -e "${RED}ERROR: tasks.md not found${NC}"
        exit 1
    fi
    
    # Check for python3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: python3 not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Prerequisites check passed"
}

show_agent_status() {
    echo -e "${BLUE}=== Agent Status ===${NC}"
    
    # Check if agents are available
    if command -v codex &> /dev/null; then
        echo -e "${GREEN}✓${NC} Codex CLI available"
    else
        echo -e "${YELLOW}!${NC} Codex CLI not found (tasks will be skipped)"
    fi
    
    if command -v gemini &> /dev/null; then
        echo -e "${GREEN}✓${NC} Gemini CLI available"
    else
        echo -e "${YELLOW}!${NC} Gemini CLI not found (tasks will be skipped)"
    fi
    
    echo -e "${BLUE}ℹ${NC} Copilot requires manual execution in VS Code"
    echo -e "${BLUE}ℹ${NC} Worker Claude should handle @claude tasks separately"
    echo ""
}

run_coordinator() {
    local dry_run_flag=""
    local loop_flag=""
    local interval_flag=""
    
    if [[ "$1" == "dry-run" ]]; then
        dry_run_flag="--dry-run"
    fi
    
    if [[ "$2" == "loop" ]]; then
        loop_flag=""  # Default is loop mode
        interval_flag="--interval ${3:-60}"
    else
        loop_flag="--once"
    fi
    
    echo -e "${BLUE}=== Running Coordinator ===${NC}"
    echo "Command: python3 $COORDINATOR $dry_run_flag $loop_flag $interval_flag"
    echo ""
    
    python3 "$COORDINATOR" $dry_run_flag $loop_flag $interval_flag
}

# Parse arguments
MODE="dry-run"
LOOP_MODE="once"
INTERVAL=60

while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            MODE="live"
            shift
            ;;
        --loop)
            LOOP_MODE="loop"
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}ERROR: Unknown option $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Main execution
echo -e "${BLUE}🤖 Multi-Agent Coordinator${NC}"
echo -e "${BLUE}===========================${NC}"

check_prerequisites
show_agent_status

if [[ "$MODE" == "dry-run" ]]; then
    echo -e "${YELLOW}Running in DRY-RUN mode (no tasks will be executed)${NC}"
else
    echo -e "${GREEN}Running in LIVE mode (tasks will be executed)${NC}"
fi

echo ""
run_coordinator "$MODE" "$LOOP_MODE" "$INTERVAL"