#!/bin/bash

# Production Build Script for SignalHire Agent
# This script builds the production wheel and tarball

set -e

# Get arguments
OUTPUT_DIR="${1:-dist}"
VERSION_FLAG="${2:-}"
VERSION="${3:-}"
FORCE_FLAG="${4:-}"

echo "🚀 Building SignalHire Agent Production Release"
echo "============================================="

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Install build requirements
pip install build

# Build the package
echo "Building wheel and source distribution..."
python -m build --outdir "$OUTPUT_DIR"

echo "✅ Production build complete!"
echo "Files created in $OUTPUT_DIR:"
ls -la "$OUTPUT_DIR"/*.whl "$OUTPUT_DIR"/*.tar.gz 2>/dev/null || echo "Build artifacts:"
ls -la "$OUTPUT_DIR"