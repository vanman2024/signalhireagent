#!/bin/bash
# Simple test script for signalhireagent
set -e

cd "$(dirname "$0")/.."

echo "🧪 Running tests for signalhireagent..."

# Run all tests with coverage
echo "🏃 Running unit tests..."
python3 run.py -m pytest tests/unit/ -v

echo "🔗 Running integration tests..."
python3 run.py -m pytest tests/integration/ -v

echo "🐌 Running all tests with coverage..."
python3 run.py -m pytest --cov=src --cov-report=term-missing

echo "✅ All tests passed!"