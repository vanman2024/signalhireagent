#!/bin/bash
# Intelligent Auto-Deploy Script for SignalHire Agent
# Syncs SignalHire agent to signalhiretest2 directory while excluding development/test files

set -e

# Configuration
TEMPLATE_REPO_DIR="$1"
SOURCE_DIR="$2"
TARGET_DIR="signalhiretest2"

if [ -z "$TEMPLATE_REPO_DIR" ] || [ -z "$SOURCE_DIR" ]; then
    echo "Usage: $0 <template-repo-dir> <source-dir>"
    echo "Example: $0 /home/vanman2025 /home/vanman2025/signalhireagent"
    exit 1
fi

echo "🚀 Starting intelligent SignalHire auto-deploy sync..."
echo "   Source: $SOURCE_DIR"
echo "   Target: $TEMPLATE_REPO_DIR/$TARGET_DIR/"

# Ensure target directory exists
mkdir -p "$TEMPLATE_REPO_DIR/$TARGET_DIR"

# Remove existing signalhiretest2 directory content
echo "🧹 Cleaning existing deployment..."
rm -rf "$TEMPLATE_REPO_DIR/$TARGET_DIR"/* 2>/dev/null || true

# Define exclusion patterns for development/test files
EXCLUDE_PATTERNS=(
    # Test directories and files
    "tests" 
    "tests/"
    "test"
    "test/"
    "__tests__"
    "__tests__/"
    "spec"
    "spec/"
    "test_*.py"
    "*_test.py"
    "*.test.js"
    "*.spec.js"
    "*.test.ts"
    "*.spec.ts"
    
    # Development directories
    ".pytest_cache"
    ".pytest_cache/"
    "*/.pytest_cache/*"
    "*/node_modules/*"
    "node_modules"
    "node_modules/"
    "*/venv/*"
    "*/.venv/*"
    "*/env/*"
    "*/.env/*"
    "__pycache__"
    "__pycache__/"
    "*/__pycache__/*"
    "*/coverage/*"
    "*/.coverage"
    "*/dist/*"
    "*/build/*"
    "*/tmp/*"
    "*/temp/*"
    
    # Git and version control
    "*/.git/*"
    "*/.github/*"
    ".gitignore"
    ".gitattributes"
    
    # IDE and editor files
    "*/.vscode/*"
    "*/.idea/*"
    "*.swp"
    "*.swo"
    "*~"
    ".DS_Store"
    "Thumbs.db"
    
    # Documentation directories and files  
    "docs"
    "docs/"
    "documentation"
    "documentation/"
    "examples"
    "examples/"
    "samples" 
    "samples/"
    
    # Development-specific documentation (exclude)
    "DEVELOPMENT.md"
    "BUILD.md"
    "TESTING.md"
    "DEPLOYMENT.md"
    "ARCHITECTURE.md"
    
    # Lock files and logs
    "package-lock.json"
    "yarn.lock"
    "poetry.lock"
    "Pipfile.lock"
    "*.log"
    "*.log.*"
    
    # Cache and temporary files
    "*.pyc"
    "*.pyo"
    "*.pyd"
    "*.cache"
    "*/.cache/*"
    "*.tmp"
    
    # Development configs
    ".env.local"
    ".env.development"
    ".env.test"
    "docker-compose.yml"
    "docker-compose.*.yml"
    "Dockerfile.dev"
    "Dockerfile.test"
    
    # SignalHire-specific exclusions
    "archive"
    "archive/"
    "backup"
    "backup/"
    "__init__.py"
    "pytest.ini"
    ".github"
    ".github/"
    
    # Workflow-generated directories
    "template-repo"
    "template-repo/"
)

# Build rsync exclude arguments
RSYNC_EXCLUDES=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    RSYNC_EXCLUDES="$RSYNC_EXCLUDES --exclude='$pattern'"
done

echo "📋 Exclusion patterns configured: ${#EXCLUDE_PATTERNS[@]} patterns"

# Perform intelligent sync using rsync
echo "🔄 Syncing application files (excluding dev/test files)..."
eval rsync -av \
    --delete \
    $RSYNC_EXCLUDES \
    "$SOURCE_DIR"/ "$TEMPLATE_REPO_DIR/$TARGET_DIR"/ \
    --exclude=".*" \
    --include="README.md" \
    --include="VERSION" \
    --include="requirements.txt" \
    --include="pyproject.toml" \
    --include="setup.py"

# Special handling for VERSION file
echo "📝 Updating VERSION file..."
if [ -f "$SOURCE_DIR/VERSION" ]; then
    cp "$SOURCE_DIR/VERSION" "$TEMPLATE_REPO_DIR/$TARGET_DIR/VERSION"
    echo "   ✅ VERSION file updated"
else
    echo "   ⚠️  No VERSION file found in source"
fi

# Verify sync results
echo "📊 Sync results:"
echo "   Directories synced: $(find "$TEMPLATE_REPO_DIR/$TARGET_DIR"/ -type d | wc -l)"
echo "   Files synced: $(find "$TEMPLATE_REPO_DIR/$TARGET_DIR"/ -type f | wc -l)"

# Show what was synced (first level directories only)
echo "📁 Top-level directories synced:"
find "$TEMPLATE_REPO_DIR/$TARGET_DIR"/ -maxdepth 1 -type d | sort | sed "s|$TEMPLATE_REPO_DIR/$TARGET_DIR/|   ✅ |"

# Show what was excluded (common development files if they existed)
echo "🚫 Development files excluded (sampling):"
excluded_count=0
for pattern in "*/tests/*" "*/__pycache__/*" "*/.git/*" "*/node_modules/*"; do
    if find "$SOURCE_DIR" -path "$pattern" 2>/dev/null | head -1 | grep -q . 2>/dev/null; then
        echo "   🚫 $pattern"
        excluded_count=$((excluded_count + 1))
    fi
done

if [ $excluded_count -eq 0 ]; then
    echo "   ✅ No common development files found to exclude"
fi

echo "✅ Intelligent auto-deploy sync completed successfully!"
echo "🎯 Target: All application code synced to $TARGET_DIR/ directory"
echo "🛡️  Safety: Development and test files excluded"