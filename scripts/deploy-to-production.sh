#!/bin/bash
# Deploy to production script for signalhireagent
# This script deploys a specific version to a production directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
PRODUCTION_DIR="${1:-/home/vanman2025/Projects/signalhireagenttests2/signalhireagent}"
VERSION="${2:-latest}"

echo "🚀 Deploying SignalHire Agent to Production..."
echo "📁 Production directory: $PRODUCTION_DIR"
echo "🏷️  Version: $VERSION"

cd "$PROJECT_ROOT"

# Validate we're in the right place
if [[ ! -f "CLAUDE.md" ]]; then
    echo "❌ Must run from signalhireagent repository root"
    exit 1
fi

# Get the latest version if not specified
if [[ "$VERSION" == "latest" ]]; then
    VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/v//' || echo "0.4.5")
    echo "📋 Using latest version: v$VERSION"
fi

# Create production build using our build script
echo "🔨 Creating production build..."
BUILD_DIR="$(mktemp -d)"
./scripts/build/build-production.sh "$BUILD_DIR/signalhireagent" --version "v$VERSION" --force

# Preserve user-created files before deployment
USER_FILES_BACKUP=""
if [[ -d "$PRODUCTION_DIR" && "$(ls -A "$PRODUCTION_DIR" 2>/dev/null)" ]]; then
    USER_FILES_BACKUP="$(mktemp -d)"
    echo "💾 Preserving user-created files..."
    
    # List of files/directories to preserve (user-created documentation, configs, logs, etc.)
    PRESERVE_PATTERNS=(
        "*.log"
        "*.notes"
        "*.md" # But exclude README.md, QUICKSTART.md, BUILD_INFO.md which come from deployment
        "issues/"
        "notes/"
        "docs/user/"
        "docs/issues/"
        "docs/notes/"
        "local/"
        "config/"
        "data/"
        "operations/"
        ".signalhire-agent/"
    )
    
    cd "$PRODUCTION_DIR"
    for pattern in "${PRESERVE_PATTERNS[@]}"; do
        # Skip CLAUDE.md and AGENTS.md as these are development files
        if [[ "$pattern" == "*.md" ]]; then
            # Only preserve user-created .md files, not development instruction files
            for file in *.md; do
                if [[ -f "$file" && ! "$file" =~ ^(README|QUICKSTART|BUILD_INFO|CLAUDE|AGENTS)\.md$ ]]; then
                    echo "  📄 Preserving: $file"
                    cp "$file" "$USER_FILES_BACKUP/" 2>/dev/null || true
                fi
            done
        else
            if ls $pattern 2>/dev/null >/dev/null 2>&1; then
                echo "  📄 Preserving: $pattern"
                cp -r $pattern "$USER_FILES_BACKUP/" 2>/dev/null || true
            fi
        fi
    done
    cd - >/dev/null
    
    # Full backup for safety
    BACKUP_DIR="$(dirname "$PRODUCTION_DIR")/backups/signalhireagent.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Creating full backup at: $BACKUP_DIR"
    mkdir -p "$(dirname "$BACKUP_DIR")"
    mv "$PRODUCTION_DIR" "$BACKUP_DIR"
fi

# Deploy the build
echo "📦 Deploying to production..."
mkdir -p "$(dirname "$PRODUCTION_DIR")"
mv "$BUILD_DIR/signalhireagent" "$PRODUCTION_DIR"

# Set up production environment
echo "⚙️  Setting up production environment..."
cd "$PRODUCTION_DIR"

# Ensure install script is executable
chmod +x install.sh
chmod +x signalhire-agent

# Copy environment file if it exists from backup
if [[ -f "${PRODUCTION_DIR}.backup."*"/.env" ]]; then
    LATEST_BACKUP=$(ls -td "${PRODUCTION_DIR}.backup."*/ 2>/dev/null | head -1)
    if [[ -f "${LATEST_BACKUP}.env" ]]; then
        echo "📋 Copying .env from backup..."
        cp "${LATEST_BACKUP}.env" ./.env
    fi
fi

# Run installation
echo "🔧 Running production installation..."
./install.sh

# Restore user-created files
if [[ -n "$USER_FILES_BACKUP" && -d "$USER_FILES_BACKUP" ]]; then
    echo "🔄 Restoring user-created files..."
    
    # Restore preserved files
    cd "$USER_FILES_BACKUP"
    if [[ -n "$(ls -A . 2>/dev/null)" ]]; then
        for item in *; do
            if [[ -e "$item" ]]; then
                echo "  📄 Restoring: $item"
                cp -r "$item" "$PRODUCTION_DIR/" 2>/dev/null || true
            fi
        done
    fi
    cd - >/dev/null
    
    # Clean up temporary backup
    rm -rf "$USER_FILES_BACKUP"
    echo "✅ User files restored"
fi

# Test the installation
echo "🧪 Testing production installation..."
if ./signalhire-agent --help >/dev/null 2>&1; then
    echo "✅ Production deployment successful!"
else
    echo "❌ Production test failed"
    exit 1
fi

# Show version info
echo ""
echo "📊 Production Status:"
echo "  Version: $(cat VERSION 2>/dev/null || echo 'unknown')"
echo "  Location: $PRODUCTION_DIR"
echo "  Test command: ./signalhire-agent status --credits"
echo ""
echo "🎉 Deployment complete!"

# Cleanup
rm -rf "$BUILD_DIR"