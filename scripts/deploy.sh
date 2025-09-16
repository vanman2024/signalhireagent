#!/bin/bash
# Simple deploy script for signalhireagent
set -e

cd "$(dirname "$0")/.."

VERSION_TYPE="${1:-patch}"  # major, minor, patch

echo "🚀 Deploying signalhireagent..."

# Activate virtual environment  
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
elif [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
else
    echo "❌ No virtual environment found - run ./scripts/build.sh first"
    exit 1
fi

# Run tests first
echo "🧪 Running tests before deploy..."
./scripts/test.sh

# Get current version
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/v//' || echo "0.0.0")
echo "📋 Current version: $CURRENT_VERSION"

# Calculate new version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]:-0}
MINOR=${VERSION_PARTS[1]:-0}
PATCH=${VERSION_PARTS[2]:-0}

case "$VERSION_TYPE" in
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
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "📈 New version: $NEW_VERSION"

# Create git tag
echo "🏷️  Creating release tag..."
git tag "v$NEW_VERSION"
git push origin "v$NEW_VERSION"

echo "✅ Deploy complete!"
echo "🌐 GitHub Actions will handle the rest automatically"