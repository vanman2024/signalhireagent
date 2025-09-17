# Quick Start: Frontend Testing Template

## 🚀 Get Started in 5 Minutes

### 1. Copy the Template
```bash
# Copy to your project
cp -r frontend-tests-template your-project/tests/

# Navigate to your project
cd your-project
```

### 2. Install Dependencies
```bash
# Install Playwright and testing dependencies
npm install --save-dev @playwright/test @types/node eslint typescript

# Install Playwright browsers
npx playwright install
```

### 3. Configure for Your App
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000', // ← Change this to your dev server
  },
  webServer: {
    command: 'npm run dev', // ← Change this to your dev command
    url: 'http://localhost:3000',
  },
});
```

### 4. Write Your First Test
```typescript
// tests/e2e/critical/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test('user can sign up and use app @critical', async ({ page }) => {
  // Visit your app
  await page.goto('/');

  // Click signup
  await page.click('[data-testid="signup-button"]');

  // Fill form
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="register-button"]');

  // Verify success
  await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
});
```

### 5. Run Your Tests
```bash
# Run all tests
npm test

# Run with browser visible
npm run test:headed

# Run specific test types
npm run test:e2e          # E2E tests only
npm run test:smoke        # Quick smoke tests
npm run test:critical     # Business-critical tests

# Debug tests
npm run test:debug        # Step through tests
npm run test:ui          # Interactive test UI
```

## 🎯 What Tests Should I Write First?

### Priority 1: Critical User Journeys (Start Here)
```typescript
test.describe('🔴 Critical Paths', () => {
  test('user can sign up and start using app @critical', async ({ page }) => {
    // Test: Landing → Signup → Email Verify → Dashboard
  });

  test('existing user can login and do main task @critical', async ({ page }) => {
    // Test: Login → Dashboard → Primary Feature → Success
  });
});
```

### Priority 2: Key Features
```typescript
test.describe('🟡 Key Features', () => {
  test('search works across the app', async ({ page }) => {
    // Test search functionality
  });

  test('settings save and persist', async ({ page }) => {
    // Test configuration changes
  });
});
```

### Priority 3: Smoke Tests
```typescript
test.describe('🟢 Smoke Tests @smoke', () => {
  test('homepage loads without errors', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });
});
```

## 📁 Project Structure

```
your-project/
├── tests/
│   ├── e2e/                    # End-to-end tests
│   │   ├── critical/          # @critical - business breakers
│   │   ├── journeys/          # User workflow tests
│   │   └── smoke/             # @smoke - quick checks
│   ├── integration/           # Component/API tests
│   ├── unit/                  # Logic tests
│   ├── visual/                # Screenshot tests
│   └── utils/                 # Shared utilities
│       ├── test-utils.ts      # Page objects & helpers
│       ├── factories.ts       # Test data factories
│       └── api-client.ts      # API testing utilities
├── playwright.config.ts       # Playwright configuration
├── package.json               # Test scripts
└── .github/workflows/ci.yml   # CI/CD pipeline
```

## 🛠️ Essential Commands

```bash
# Development
npm run test:headed     # See tests running
npm run test:debug      # Debug failing tests
npm run codegen         # Generate tests from interactions

# Quality Checks
npm run lint           # Code linting
npm run type-check     # TypeScript checks

# CI/CD
npm run test:smoke     # Quick checks (30s)
npm run test:critical  # Important tests (5-8 min)
npm run test           # Full suite (10-15 min)

# Reporting
npm run report         # View test results
```

## ⚙️ Common Configurations

### For React Apps
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### For Vue Apps
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:8080',
  },
  webServer: {
    command: 'npm run serve',
    url: 'http://localhost:8080',
  },
});
```

### For Next.js Apps
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
  },
});
```

## 🎯 Testing Strategy Summary

### What to Test
- ✅ **Critical user journeys** (5-8 E2E tests)
- ✅ **Key business features** (10-15 integration tests)
- ✅ **Business logic** (50+ unit tests)
- ✅ **Important static pages** (5-10 visual tests)

### What NOT to Test
- ❌ Every single page with E2E tests
- ❌ Admin panels (unless core business)
- ❌ Static content pages (use visual tests)
- ❌ Every form validation edge case

### Test Speed Goals
- **Smoke tests**: < 30 seconds
- **Critical E2E**: < 8 minutes
- **Full suite**: < 15 minutes

## 🚨 First Test Checklist

- [ ] Copied template to project
- [ ] Installed dependencies (`npm install`)
- [ ] Installed browsers (`npx playwright install`)
- [ ] Updated `playwright.config.ts` with your URLs
- [ ] Created first critical user journey test
- [ ] Ran test successfully (`npm run test:headed`)
- [ ] Added test to CI/CD pipeline

## 📚 Next Steps

1. **Read the docs**: Check `docs/TESTING_STRATEGY.md` for detailed guidance
2. **Customize utilities**: Update `tests/utils/test-utils.ts` for your app
3. **Add more tests**: Follow the priority order above
4. **Set up CI/CD**: Use the provided GitHub Actions workflow
5. **Monitor performance**: Keep tests fast and reliable

## 🆘 Need Help?

### Common Issues
```bash
# Tests failing? Try headed mode to see what's happening
npm run test:headed

# Element not found? Use codegen to find selectors
npm run codegen

# Tests slow? Check for unnecessary waits
# Remove page.waitForTimeout() calls
```

### Debug Tips
- Use `await page.pause()` to stop and inspect
- Add `console.log()` statements in tests
- Use `page.screenshot()` to capture state
- Check network tab for failed requests

---

**Happy Testing!** Start with one critical user journey, get it working reliably, then add more tests gradually. Quality over quantity! 🎯
