#!/bin/bash

# Version Sync Script
# Ensures VERSION file and pyproject.toml are in sync

set -e

echo "🔄 Version Sync Tool"
echo "==================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get version from pyproject.toml
if [ -f "pyproject.toml" ]; then
    PYPROJECT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    echo -e "pyproject.toml version: ${GREEN}$PYPROJECT_VERSION${NC}"
else
    echo -e "${RED}✗ pyproject.toml not found${NC}"
    exit 1
fi

# Check VERSION file
if [ -f "VERSION" ]; then
    # Check if it's JSON format
    if grep -q '{' VERSION; then
        VERSION_VALUE=$(grep '"version"' VERSION | cut -d'"' -f4)
        echo -e "VERSION file version:   ${GREEN}$VERSION_VALUE${NC}"
        
        if [ "$PYPROJECT_VERSION" != "$VERSION_VALUE" ]; then
            echo -e "\n${YELLOW}Versions are out of sync!${NC}"
            echo "Updating VERSION file to match pyproject.toml..."
            
            # Update JSON VERSION file
            cat > VERSION <<EOF
{
  "version": "$PYPROJECT_VERSION",
  "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "build_date": "$(date -Iseconds)",
  "build_type": "production"
}
EOF
            echo -e "${GREEN}✓ VERSION file updated${NC}"
        else
            echo -e "\n${GREEN}✓ Versions are in sync${NC}"
        fi
    else
        # Simple text format
        VERSION_VALUE=$(cat VERSION | tr -d '\n')
        echo -e "VERSION file version:   ${GREEN}$VERSION_VALUE${NC}"
        
        if [ "$PYPROJECT_VERSION" != "$VERSION_VALUE" ]; then
            echo -e "\n${YELLOW}Versions are out of sync!${NC}"
            echo "Updating VERSION file to match pyproject.toml..."
            echo "$PYPROJECT_VERSION" > VERSION
            echo -e "${GREEN}✓ VERSION file updated${NC}"
        else
            echo -e "\n${GREEN}✓ Versions are in sync${NC}"
        fi
    fi
else
    echo -e "${YELLOW}VERSION file not found, creating...${NC}"
    # Create JSON VERSION file
    cat > VERSION <<EOF
{
  "version": "$PYPROJECT_VERSION",
  "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "build_date": "$(date -Iseconds)",
  "build_type": "production"
}
EOF
    echo -e "${GREEN}✓ VERSION file created${NC}"
fi

# Check if __version__ is used in Python package
if [ -d "src" ] || [ -d "multiagent_core" ]; then
    echo -e "\n${YELLOW}Checking Python package version...${NC}"
    
    # Find the package directory
    if [ -d "src" ]; then
        PKG_DIRS=$(find src -name "__init__.py" -type f | head -1 | xargs dirname)
    else
        PKG_DIRS=$(find . -maxdepth 2 -name "__init__.py" -type f | grep -v test | head -1 | xargs dirname)
    fi
    
    if [ -n "$PKG_DIRS" ]; then
        INIT_FILE="$PKG_DIRS/__init__.py"
        if [ -f "$INIT_FILE" ]; then
            if grep -q "__version__" "$INIT_FILE"; then
                echo -e "${YELLOW}Found __version__ in $INIT_FILE${NC}"
                echo "Consider using importlib.metadata instead:"
                echo '  from importlib.metadata import version'
                echo '  __version__ = version("package-name")'
            else
                echo -e "${GREEN}✓ No hardcoded __version__ found (good!)${NC}"
            fi
        fi
    fi
fi

echo -e "\n${GREEN}Version sync complete!${NC}"