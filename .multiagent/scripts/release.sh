#!/bin/bash

# Universal Release Script for Python Projects
# Works with any project that has pyproject.toml and VERSION file

set -e

echo "🚀 Universal Python Package Release Script"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check requirements
check_requirement() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}✗ $1 is required but not installed${NC}"
        echo "  Install with: $2"
        exit 1
    fi
    echo -e "${GREEN}✓ $1 found${NC}"
}

echo -e "\n${YELLOW}Checking requirements...${NC}"
check_requirement "git" "apt install git"
check_requirement "python3" "apt install python3"
check_requirement "pip3" "apt install python3-pip"

# Parse arguments
VERSION_BUMP=${1:-patch}  # Default to patch
PYPI_UPLOAD=${2:-no}      # Default to no PyPI upload

echo -e "\n${YELLOW}Release configuration:${NC}"
echo "  Version bump: $VERSION_BUMP (major/minor/patch)"
echo "  PyPI upload: $PYPI_UPLOAD (yes/no)"

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo -e "\n${YELLOW}Current version: $CURRENT_VERSION${NC}"

# Calculate new version
IFS='.' read -r -a version_parts <<< "$CURRENT_VERSION"
MAJOR="${version_parts[0]}"
MINOR="${version_parts[1]}"
PATCH="${version_parts[2]}"

case $VERSION_BUMP in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo -e "${RED}Invalid version bump: $VERSION_BUMP${NC}"
        echo "Use: major, minor, or patch"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo -e "${GREEN}New version: $NEW_VERSION${NC}"

# Step 1: Update pyproject.toml
echo -e "\n${YELLOW}Step 1: Updating pyproject.toml...${NC}"
sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo -e "${GREEN}✓ Updated to $NEW_VERSION${NC}"

# Step 2: Update VERSION file if it exists
if [ -f "VERSION" ]; then
    echo -e "\n${YELLOW}Step 2: Updating VERSION file...${NC}"
    
    # Handle JSON format
    if grep -q '{' VERSION; then
        cat > VERSION <<EOF
{
  "version": "$NEW_VERSION",
  "commit": "$(git rev-parse HEAD)",
  "build_date": "$(date -Iseconds)",
  "build_type": "production"
}
EOF
    else
        # Simple text format
        echo "$NEW_VERSION" > VERSION
    fi
    echo -e "${GREEN}✓ VERSION file updated${NC}"
else
    echo -e "\n${YELLOW}Step 2: No VERSION file found, skipping...${NC}"
fi

# Step 3: Build the package
echo -e "\n${YELLOW}Step 3: Building package...${NC}"
pip3 install build --break-system-packages 2>/dev/null || pip3 install build
python3 -m build
echo -e "${GREEN}✓ Package built${NC}"

# Step 4: Git operations
echo -e "\n${YELLOW}Step 4: Committing changes...${NC}"
git add pyproject.toml
[ -f VERSION ] && git add VERSION
git commit -m "chore(release): $NEW_VERSION

- Bumped version from $CURRENT_VERSION to $NEW_VERSION
- Type: $VERSION_BUMP release"
echo -e "${GREEN}✓ Changes committed${NC}"

# Step 5: Create git tag
echo -e "\n${YELLOW}Step 5: Creating git tag...${NC}"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
echo -e "${GREEN}✓ Tag v$NEW_VERSION created${NC}"

# Step 6: Push to remote
echo -e "\n${YELLOW}Step 6: Pushing to remote...${NC}"
echo "Run these commands to push:"
echo -e "${YELLOW}  git push origin main${NC}"
echo -e "${YELLOW}  git push origin v$NEW_VERSION${NC}"

# Step 7: PyPI upload (optional)
if [ "$PYPI_UPLOAD" = "yes" ]; then
    echo -e "\n${YELLOW}Step 7: Uploading to PyPI...${NC}"
    pip3 install twine --break-system-packages 2>/dev/null || pip3 install twine
    python3 -m twine upload dist/*
    echo -e "${GREEN}✓ Package uploaded to PyPI${NC}"
else
    echo -e "\n${YELLOW}Step 7: PyPI upload skipped${NC}"
    echo "To upload manually later:"
    echo -e "${YELLOW}  python3 -m twine upload dist/*${NC}"
fi

# Step 8: Local installation
echo -e "\n${YELLOW}Step 8: Install locally with pipx:${NC}"
echo -e "${YELLOW}  pipx install dist/*.whl --force${NC}"

echo -e "\n${GREEN}🎉 Release $NEW_VERSION complete!${NC}"
echo ""
echo "Summary:"
echo "  • Version: $CURRENT_VERSION → $NEW_VERSION"
echo "  • Git tag: v$NEW_VERSION"
echo "  • Package: dist/$(ls -1 dist/*.whl | tail -1 | basename)"
echo ""
echo "Next steps:"
echo "  1. Push to remote (see commands above)"
echo "  2. Create GitHub release"
echo "  3. Announce to users"