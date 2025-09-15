#!/bin/bash
# Production Build Script for SignalHire Agent
# Creates clean production deployment with version tracking

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[BUILD]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "CLAUDE.md" ]]; then
    print_error "Must run from signalhireagent repository root"
    exit 1
fi

# Parse command line arguments
TARGET_DIR=""
VERSION_TAG=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION_TAG="$2"
            shift 2
            ;;
        --latest)
            VERSION_TAG="latest"
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 <target_directory> [options]"
            echo ""
            echo "Options:"
            echo "  --version TAG    Deploy specific version tag (e.g., v0.2.1)"
            echo "  --latest         Deploy latest version tag"
            echo "  --force          Overwrite existing target directory"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 ~/Projects/signalhireagenttests2/signalhireagent/"
            echo "  $0 /path/to/staging --version v0.2.1"
            echo "  $0 /path/to/staging --latest --force"
            exit 0
            ;;
        *)
            if [[ -z "$TARGET_DIR" ]]; then
                TARGET_DIR="$1"
            else
                print_error "Unknown option: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate target directory
if [[ -z "$TARGET_DIR" ]]; then
    print_error "Target directory is required"
    echo "Usage: $0 <target_directory> [--version TAG] [--latest] [--force]"
    exit 1
fi

# Get version information
if [[ "$VERSION_TAG" == "latest" ]]; then
    VERSION_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0-dev")
    print_status "Using latest version tag: $VERSION_TAG"
elif [[ -n "$VERSION_TAG" ]]; then
    # Validate that the version tag exists
    if ! git rev-parse "$VERSION_TAG" >/dev/null 2>&1; then
        print_error "Version tag '$VERSION_TAG' does not exist"
        exit 1
    fi
    print_status "Using specified version: $VERSION_TAG"
else
    # Get current version based on latest tag + commits
    VERSION_TAG=$(git describe --tags --dirty 2>/dev/null || echo "v0.0.0-dev-$(git rev-parse --short HEAD)")
    print_status "Using current version: $VERSION_TAG"
fi

# Get commit hash for version tracking
COMMIT_HASH=$(git rev-parse HEAD)
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

print_status "Building production deployment..."
print_status "  Version: $VERSION_TAG"
print_status "  Commit:  $COMMIT_HASH"
print_status "  Target:  $TARGET_DIR"

# Check if target directory exists
if [[ -d "$TARGET_DIR" ]]; then
    if [[ "$FORCE" == "true" ]]; then
        print_warning "Removing existing target directory"
        rm -rf "$TARGET_DIR"
    else
        print_error "Target directory already exists. Use --force to overwrite."
        exit 1
    fi
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy essential application files
print_status "Copying application files..."

# Core application code
cp -r src/ "$TARGET_DIR/"

# Essential configuration and documentation
cp README.md "$TARGET_DIR/" 2>/dev/null || true
cp QUICKSTART.md "$TARGET_DIR/" 2>/dev/null || true
cp LICENSE "$TARGET_DIR/" 2>/dev/null || true

# Create production requirements.txt (without dev dependencies)
print_status "Creating production requirements.txt..."
cat > "$TARGET_DIR/requirements.txt" << EOF
# SignalHire Agent Production Dependencies
# Generated on $BUILD_DATE

# Core dependencies
click>=8.0.0
httpx>=0.24.0
pandas>=1.5.0
pydantic>=2.0.0
structlog>=22.0.0
python-dotenv>=1.0.0

# Email validation
email-validator>=2.0.0

# Optional: Remove if not using async features
anyio>=3.6.0
EOF

# Create version information file
print_status "Creating version information..."
cat > "$TARGET_DIR/VERSION" << EOF
{
  "version": "$VERSION_TAG",
  "commit": "$COMMIT_HASH", 
  "build_date": "$BUILD_DATE",
  "build_type": "production"
}
EOF

# Create production .env template
print_status "Creating .env template..."
cat > "$TARGET_DIR/.env.example" << EOF
# SignalHire Agent Configuration
# Copy this to .env and add your actual values

# Required: SignalHire API Key
SIGNALHIRE_API_KEY=your_api_key_here

# Optional: API Configuration
SIGNALHIRE_API_BASE_URL=https://www.signalhire.com
SIGNALHIRE_API_PREFIX=/api/v1

# Optional: Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=600
DAILY_REVEAL_LIMIT=5000
DAILY_SEARCH_PROFILE_LIMIT=5000
EOF

# Create simple deployment script
print_status "Creating deployment utilities..."
cat > "$TARGET_DIR/install.sh" << 'EOF'
#!/bin/bash
# SignalHire Agent Installation Script

echo "Installing SignalHire Agent..."

# Check Python version
python3 --version | grep -E "3\.(9|10|11|12)" > /dev/null
if [ $? -ne 0 ]; then
    echo "Error: Python 3.9+ required"
    exit 1
fi

# Install dependencies
pip3 install -r requirements.txt

# Make CLI executable (if using direct execution)
chmod +x src/cli/main.py

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Add your SIGNALHIRE_API_KEY to .env"
echo "3. Run: python3 -m src.cli.main --help"

EOF

chmod +x "$TARGET_DIR/install.sh"

# Create version check utility
cat > "$TARGET_DIR/version.py" << 'EOF'
#!/usr/bin/env python3
"""Version information utility for SignalHire Agent."""

import json
import sys
from pathlib import Path

def get_version():
    """Get version information from VERSION file."""
    version_file = Path(__file__).parent / "VERSION"
    if not version_file.exists():
        return {"version": "unknown", "error": "VERSION file not found"}
    
    try:
        with open(version_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"version": "unknown", "error": str(e)}

def main():
    """Print version information."""
    version_info = get_version()
    
    if "error" in version_info:
        print(f"Error getting version: {version_info['error']}")
        sys.exit(1)
    
    print(f"SignalHire Agent {version_info['version']}")
    print(f"Build: {version_info['commit'][:8]} ({version_info['build_date']})")
    print(f"Type: {version_info['build_type']}")

if __name__ == "__main__":
    main()
EOF

chmod +x "$TARGET_DIR/version.py"

# Create simple CLI wrapper (optional)
cat > "$TARGET_DIR/signalhire-agent" << 'EOF'
#!/bin/bash
# SignalHire Agent CLI Wrapper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Load .env if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

# Run the CLI
python3 -m src.cli.main "$@"
EOF

chmod +x "$TARGET_DIR/signalhire-agent"

# Generate build manifest
print_status "Creating build manifest..."
cat > "$TARGET_DIR/BUILD_INFO.md" << EOF
# SignalHire Agent Production Build

**Version:** $VERSION_TAG  
**Commit:** $COMMIT_HASH  
**Built:** $BUILD_DATE  
**Build Type:** Production

## Files Included
- \`src/\` - Core application code
- \`requirements.txt\` - Production dependencies only
- \`VERSION\` - Version information (JSON)
- \`version.py\` - Version utility script
- \`install.sh\` - Installation script
- \`signalhire-agent\` - CLI wrapper script
- \`.env.example\` - Configuration template

## Files Excluded (Development Only)
- \`tests/\` - Test suite
- \`specs/\` - Development specifications  
- \`.pytest_cache/\` - Test cache
- \`pyproject.toml\` - Development configuration
- Development documentation and scripts

## Installation
1. Run \`./install.sh\`
2. Copy \`.env.example\` to \`.env\`
3. Add your SIGNALHIRE_API_KEY to \`.env\`
4. Test: \`./signalhire-agent --help\`

## Version Check
Run \`python3 version.py\` to see build information.
EOF

# Final verification
print_status "Verifying build..."

# Check that essential files exist
ESSENTIAL_FILES=(
    "src/cli/main.py"
    "src/services/signalhire_client.py" 
    "requirements.txt"
    "VERSION"
    "install.sh"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [[ ! -f "$TARGET_DIR/$file" ]]; then
        print_error "Missing essential file: $file"
        exit 1
    fi
done

# Get directory size
BUILD_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)

print_success "Production build completed successfully!"
print_success "  Location: $TARGET_DIR"
print_success "  Version:  $VERSION_TAG"
print_success "  Size:     $BUILD_SIZE"
print_success ""
print_success "Next steps:"
print_success "  cd $TARGET_DIR"
print_success "  ./install.sh"
print_success "  cp .env.example .env"
print_success "  # Add your SIGNALHIRE_API_KEY to .env"
print_success "  ./signalhire-agent --help"