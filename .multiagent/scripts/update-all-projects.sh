#!/bin/bash

# Update all projects that use multiagent-core
# This script finds all projects with .multiagent directories and updates them

echo "🔄 Multi-Agent Core Auto-Updater"
echo "================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find all projects with .multiagent directories
PROJECTS_DIR="${PROJECTS_DIR:-/home/vanman2025/Projects}"
SKIP_DIRS=("multiagent-core" "multiagent-devops" "multiagent-testing" "multiagent-agentswarm")

# Counter for statistics
UPDATED=0
FAILED=0
SKIPPED=0

echo -e "${YELLOW}Searching for projects in: $PROJECTS_DIR${NC}"
echo ""

# Function to update a single project
update_project() {
    local project_path=$1
    local project_name=$(basename "$project_path")
    
    # Skip core multiagent repos
    for skip in "${SKIP_DIRS[@]}"; do
        if [[ "$project_name" == "$skip" ]]; then
            echo -e "${YELLOW}⏭️  Skipping core repo: $project_name${NC}"
            ((SKIPPED++))
            return
        fi
    done
    
    echo -e "${GREEN}📦 Updating: $project_name${NC}"
    echo "   Path: $project_path"
    
    # Change to project directory
    cd "$project_path" || {
        echo -e "${RED}   ❌ Failed to enter directory${NC}"
        ((FAILED++))
        return
    }
    
    # Run multiagent init with yes to all prompts
    echo "y" | multiagent init > /tmp/multiagent-update.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ Successfully updated${NC}"
        
        # Check if new docs were added
        if [ -d ".multiagent/docs" ]; then
            local doc_count=$(ls -1 .multiagent/docs/*.md 2>/dev/null | wc -l)
            echo "   📚 Documentation files: $doc_count"
        fi
        
        ((UPDATED++))
    else
        echo -e "${RED}   ❌ Update failed (see /tmp/multiagent-update.log)${NC}"
        ((FAILED++))
    fi
    
    echo ""
}

# Find all directories with .multiagent folder
while IFS= read -r -d '' project; do
    project_dir=$(dirname "$project")
    update_project "$project_dir"
done < <(find "$PROJECTS_DIR" -maxdepth 3 -type d -name ".multiagent" -print0 2>/dev/null)

# Summary
echo "================================"
echo "📊 Update Summary:"
echo -e "${GREEN}✅ Updated: $UPDATED projects${NC}"
echo -e "${YELLOW}⏭️  Skipped: $SKIPPED projects${NC}"
echo -e "${RED}❌ Failed: $FAILED projects${NC}"
echo ""
echo "💡 Tip: Add this to cron for automatic updates:"
echo "   0 2 * * * $0"