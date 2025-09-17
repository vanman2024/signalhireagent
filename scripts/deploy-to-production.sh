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

# Backup existing production if it exists
if [[ -d "$PRODUCTION_DIR" && "$(ls -A "$PRODUCTION_DIR" 2>/dev/null)" ]]; then
    BACKUP_DIR="$(dirname "$PRODUCTION_DIR")/backups/signalhireagent.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing production to: $BACKUP_DIR"
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