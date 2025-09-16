#!/bin/bash
# Simple build script for signalhireagent
set -e

cd "$(dirname "$0")/.."

echo "🔨 Building signalhireagent..."

# Install/update dependencies
echo "📦 Installing dependencies..."
if command -v python3 >/dev/null && python3 -c "import sys; print('Virtual environment' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'System environment')" | grep -q "Virtual environment"; then
    pip install -e .[dev]
else
    echo "Using system environment - dependencies assumed installed"
    echo "Run: python3 -m pip install -e .[dev] --break-system-packages (if needed)"
fi

# Lint and fix issues
echo "🧹 Linting code..."
ruff check src/ --fix || true

# Type check
echo "🔍 Type checking..."
mypy src/ || true

# Basic import test
echo "✅ Testing imports..."
python3 -c "import sys; sys.path.append('src'); import cli.main"

echo "✅ Build complete!"