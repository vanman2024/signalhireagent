#!/bin/bash

# Update ALL projects including component sources
# This updates agentswarm, devops, testing, AND regular projects

echo "🔄 Multi-Agent Core Universal Updater"
echo "====================================="
echo "Updates ALL projects including component sources"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base directory
PROJECTS_DIR="${PROJECTS_DIR:-/home/vanman2025/Projects}"

# Counter for statistics
UPDATED=0
FAILED=0
TOTAL=0

# Function to update a project
update_project() {
    local project_path=$1
    local project_name=$(basename "$project_path")
    local project_type=$2
    
    ((TOTAL++))
    
    echo -e "${CYAN}[$TOTAL] ${project_type}: $project_name${NC}"
    echo "     Path: $project_path"
    
    # Change to project directory
    cd "$project_path" || {
        echo -e "${RED}     ❌ Failed to enter directory${NC}"
        ((FAILED++))
        return
    }
    
    # Run multiagent init with yes to all prompts
    echo "y" | multiagent init > /tmp/multiagent-update-$project_name.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}     ✅ Successfully updated${NC}"
        
        # Check what was updated
        if [ -d ".multiagent/docs" ]; then
            local doc_count=$(ls -1 .multiagent/docs/*.md 2>/dev/null | wc -l)
            echo "     📚 Documentation files: $doc_count"
        fi
        
        ((UPDATED++))
    else
        echo -e "${RED}     ❌ Update failed (see /tmp/multiagent-update-$project_name.log)${NC}"
        ((FAILED++))
    fi
    
    echo ""
}

echo -e "${YELLOW}📦 Updating Component Sources First${NC}"
echo "-------------------------------------"

# Update component sources FIRST (they provide to others)
[ -d "$PROJECTS_DIR/agentswarm" ] && update_project "$PROJECTS_DIR/agentswarm" "Component"
[ -d "$PROJECTS_DIR/devops" ] && update_project "$PROJECTS_DIR/devops" "Component"
[ -d "$PROJECTS_DIR/multiagent-testing" ] && update_project "$PROJECTS_DIR/multiagent-testing" "Component"

echo -e "${YELLOW}📂 Updating Regular Projects${NC}"
echo "------------------------------"

# Find and update all other projects with .multiagent directories
while IFS= read -r -d '' project; do
    project_dir=$(dirname "$project")
    project_name=$(basename "$project_dir")
    
    # Skip if already updated above or is multiagent-core
    if [[ "$project_name" != "agentswarm" && \
          "$project_name" != "devops" && \
          "$project_name" != "multiagent-testing" && \
          "$project_name" != "multiagent-core" ]]; then
        update_project "$project_dir" "Project"
    fi
done < <(find "$PROJECTS_DIR" -maxdepth 3 -type d -name ".multiagent" -print0 2>/dev/null)

# Summary
echo "====================================="
echo "📊 Update Summary:"
echo -e "${GREEN}✅ Updated: $UPDATED projects${NC}"
echo -e "${RED}❌ Failed: $FAILED projects${NC}"
echo "Total processed: $TOTAL"
echo ""

if [ $UPDATED -gt 0 ]; then
    echo "💡 All projects now have the latest:"
    echo "   - Documentation from multiagent-core"
    echo "   - Agent templates"
    echo "   - Component symlinks"
fi

echo ""
echo "🔗 Component Linking Note:"
echo "   Component sources (agentswarm, devops, testing) serve dual roles:"
echo "   1. They provide functionality to other projects (via symlinks)"
echo "   2. They receive docs/templates from multiagent-core (via init)"