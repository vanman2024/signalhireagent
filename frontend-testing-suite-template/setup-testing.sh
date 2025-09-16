#!/bin/bash
# Frontend Testing Suite Setup Script
#
# PURPOSE: Scaffold a fast, agent‑friendly Playwright testing suite for local development
# USAGE: ./frontend-testing-suite-template/setup-testing.sh [--yes] [--skip-install] [--skip-browsers] [--pm npm|pnpm|yarn] [--force]
# PART OF: Frontend testing template for solo/local development
# CONNECTS TO: playwright.config.ts, tests/, GitHub Actions workflow (frontend tests)

set -euo pipefail

echo "🚀 Setting up Frontend Testing Suite..."

# Flags
YES=${YES:-0}
SKIP_INSTALL=0
SKIP_BROWSERS=0
PM=""
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y) YES=1; shift ;;
    --skip-install) SKIP_INSTALL=1; shift ;;
    --skip-browsers) SKIP_BROWSERS=1; shift ;;
    --pm) PM="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help)
      grep -E '^# (PURPOSE|USAGE|PART OF|CONNECTS TO):' "$0" | sed 's/^# //'
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Guard: project root
if [ ! -f "package.json" ]; then
    echo "❌ Error: No package.json found. Run from your project root."
    exit 1
fi

# Detect package manager if not specified
if [ -z "$PM" ]; then
  if [ -f "pnpm-lock.yaml" ]; then PM=pnpm; elif [ -f "yarn.lock" ]; then PM=yarn; else PM=npm; fi
fi

run_pm() {
  case "$PM" in
    npm) npm "$@" ;;
    pnpm) pnpm "$@" ;;
    yarn) yarn "$@" ;;
    *) echo "❌ Unknown package manager: $PM"; exit 1 ;;
  esac
}

# Backup existing tests unless --force
if [ -d "tests" ] && [ "$FORCE" -ne 1 ]; then
  echo "⚠️  Tests directory exists. Creating backup..."
  mv tests "tests.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy the testing suite
echo "📋 Copying testing suite template..."
mkdir -p tests
cp -r frontend-testing-suite-template/tests/* ./tests/

# Copy GitHub Actions workflow
mkdir -p .github/workflows
cp -f frontend-testing-suite-template/.github/workflows/ci.yml .github/workflows/

# Ensure .gitignore entries
{ echo "playwright-report/"; echo "test-results/"; echo "tests/screenshots/"; } | while read -r line; do
  grep -qxF "$line" .gitignore 2>/dev/null || echo "$line" >> .gitignore
done

# Update package.json scripts using jq (safer than sed)
echo "📦 Updating package.json scripts..."
if ! command -v jq >/dev/null 2>&1; then
  echo "⚠️  jq not found; installing via $PM to modify package.json safely"
  run_pm add -D jq || true
fi

tmp_pkg=$(mktemp)
jq '.scripts = (.scripts // {}) + {
  "test": "playwright test",
  "test:headed": "playwright test --headed",
  "test:debug": "playwright test --debug",
  "test:ui": "playwright test --ui",
  "test:e2e": "playwright test tests/e2e/",
  "test:api": "playwright test tests/api/",
  "test:visual": "playwright test tests/visual/",
  "test:accessibility": "playwright test tests/accessibility/",
  "test:smoke": "playwright test --grep @smoke",
  "test:regression": "playwright test --grep @regression",
  "report": "playwright show-report",
  "install:browsers": "playwright install",
  "install:deps": "playwright install-deps",
  "codegen": "playwright codegen",
  "lint": "eslint . --ext .js,.ts",
  "lint:fix": "eslint . --ext .js,.ts --fix",
  "type-check": "tsc --noEmit",
  "setup": "npm run install:browsers && npm run install:deps",
  "ci": "npm run lint && npm run type-check && npm run test",
  "test:parallel": "playwright test --workers=4",
  "test:shard": "playwright test --shard=1/4"
}' package.json > "$tmp_pkg" && mv "$tmp_pkg" package.json

# Create playwright config if it doesn't exist
if [ ! -f "playwright.config.ts" ]; then
    echo "⚙️  Creating Playwright configuration..."
    cp frontend-testing-suite-template/playwright.config.ts ./
fi

# Create smoke runner script
cp -f frontend-testing-suite-template/tests/run-smoke.sh ./tests/
chmod +x ./tests/run-smoke.sh

# Create screenshots directory
mkdir -p tests/screenshots

# Create .env.example for test configuration
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# Test Configuration
BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:3001
API_TOKEN=your-api-token-here

# Test Data Setup
SETUP_TEST_DB=false
SETUP_TEST_DATA=false
CLEANUP_TEST_DB=false
CLEANUP_TEST_DATA=false
CLEANUP_TEMP_FILES=false

# Browser Installation
INSTALL_BROWSERS=false
EOF
fi

if [ "$SKIP_INSTALL" -eq 0 ]; then
  echo "📥 Installing testing dependencies via $PM..."
  case "$PM" in
    npm) npm install --save-dev @playwright/test @types/node eslint typescript @typescript-eslint/eslint-plugin @typescript-eslint/parser prettier axe-playwright playwright-visual-regression ;;
    pnpm) pnpm add -D @playwright/test @types/node eslint typescript @typescript-eslint/eslint-plugin @typescript-eslint/parser prettier axe-playwright playwright-visual-regression ;;
    yarn) yarn add -D @playwright/test @types/node eslint typescript @typescript-eslint/eslint-plugin @typescript-eslint/parser prettier axe-playwright playwright-visual-regression ;;
  esac

  if [ "$SKIP_BROWSERS" -eq 0 ]; then
    echo "🌐 Installing Playwright browsers..."
    npx playwright install
    if [[ "${OSTYPE:-}" == linux* ]]; then
      echo "🐧 Installing system dependencies..."
      npx playwright install-deps chromium || true
    fi
  else
    echo "⏭️  Skipping browser installation (use later with: npx playwright install)"
  fi
else
  echo "⏭️  Skipping dependency installation per flag"
fi

echo ""
echo "✅ Frontend Testing Suite setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Update playwright.config.ts baseURL (or set BASE_URL in .env)"
echo "2. Run tests: ./tests/run-smoke.sh or $PM run test:smoke"
echo "3. Install browsers when ready: npx playwright install"
echo "4. Open the test UI: $PM run test:ui"
echo ""
echo "🎯 Happy testing!"
