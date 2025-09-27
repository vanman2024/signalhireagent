#!/bin/bash
# Create GitHub Release with just the wheel file (not entire repo)

set -e

echo "🚀 Creating Efficient GitHub Release"
echo "===================================="
echo ""

# Get version from pyproject.toml
VERSION=$(grep "^version" pyproject.toml | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
echo "Version: $VERSION"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Build the wheel (just 600KB, not 9MB!)
echo "Building wheel package..."
python -m pip install --quiet build
python -m build --wheel

# Show what we built
echo ""
echo "=== Built Package ==="
ls -lh dist/
WHEEL_SIZE=$(du -sh dist/*.whl | cut -f1)
echo "Wheel size: $WHEEL_SIZE (vs 9.1MB full repo!)"

# Create GitHub release
echo ""
echo "=== Creating GitHub Release ==="
echo "Tag: v$VERSION"

# Check if tag exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Tag v$VERSION already exists"
else
    echo "Creating tag v$VERSION"
    git tag -a "v$VERSION" -m "Release $VERSION"
    git push origin "v$VERSION"
fi

# Upload wheel to release using gh CLI
if command -v gh &> /dev/null; then
    echo "Uploading wheel to GitHub release..."
    
    # Create release if it doesn't exist
    gh release create "v$VERSION" \
        --title "v$VERSION" \
        --notes "## Installation

### Direct wheel install (fast - only 600KB):
\`\`\`bash
# This downloads ONLY the wheel, not the entire repo!
pipx install https://github.com/vanman2024/signalhireagent/releases/download/v$VERSION/signalhire_agent-$VERSION-py3-none-any.whl
\`\`\`

### Old way (slow - downloads 9MB repo):
\`\`\`bash
pipx install git+https://github.com/vanman2024/signalhireagent.git@v$VERSION
\`\`\`

## What's New
- See [CHANGELOG.md](https://github.com/vanman2024/signalhireagent/blob/main/CHANGELOG.md)

## Package Size
- Wheel: $WHEEL_SIZE (what you download)
- Full repo: 9.1MB (what you DON'T need)
" \
        dist/*.whl || \
    gh release upload "v$VERSION" dist/*.whl --clobber
    
    echo ""
    echo "✅ Release created!"
    echo ""
    echo "Users can now install efficiently:"
    echo "pipx install https://github.com/vanman2024/signalhireagent/releases/download/v$VERSION/signalhire_agent-$VERSION-py3-none-any.whl"
else
    echo "⚠️  GitHub CLI (gh) not installed"
    echo "Install with: sudo apt install gh"
    echo ""
    echo "Manual steps:"
    echo "1. Go to https://github.com/vanman2024/signalhireagent/releases/new"
    echo "2. Create release for tag v$VERSION"
    echo "3. Upload dist/signalhire_agent-$VERSION-py3-none-any.whl"
    echo "4. Users can then download just the wheel (600KB) instead of full repo (9MB)"
fi

echo ""
echo "=== Efficiency Comparison ==="
echo "Old way (git install): Downloads 9.1MB repo, uses 600KB"
echo "New way (wheel install): Downloads 600KB wheel, uses 600KB"
echo "Savings: 93% bandwidth reduction! 🎉"