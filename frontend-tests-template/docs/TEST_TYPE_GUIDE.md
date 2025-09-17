# Testing Decision Tree: When to Use What

## 🚨 Quick Reference: Test Type Selection

### For a New Page/Component, Ask:

```
Does this affect a critical user journey?
├── YES → E2E Test (full workflow)
└── NO  → Does this have complex interactions?
    ├── YES → Integration Test
    └── NO  → Does this have logic?
        ├── YES → Unit Test
        └── NO  → Visual Test or Skip
```

## 📋 Test Type Cheat Sheet

### 🎯 E2E Tests (Playwright)
**When to use:**
- User registration/login flows
- Purchase/checkout processes
- Critical business workflows
- Multi-page interactions
- Authentication redirects

**When NOT to use:**
- Individual form validations
- Static content display
- Utility functions
- Component styling

### 🔧 Integration Tests
**When to use:**
- API calls with UI
- Component interactions
- Form submissions
- Data persistence
- Cross-component communication

**When NOT to use:**
- Full user journeys
- Pure UI styling
- Simple utility functions

### ⚡ Unit Tests (Jest/Vitest)
**When to use:**
- Business logic functions
- Data transformations
- Form validation logic
- Utility functions
- Component logic (not DOM)

**When NOT to use:**
- DOM interactions
- Network requests
- Full page rendering
- User workflows

### 👁️ Visual Tests
**When to use:**
- Static content pages
- Marketing pages
- Component styling
- Layout changes
- Design consistency

**When NOT to use:**
- Dynamic content
- User interactions
- Data-driven changes
- Functional behavior

## 🎪 Real Examples

### E-commerce App
```
Homepage (static)           → Visual Test
Product Search             → Integration Test
Add to Cart                → Integration Test
Checkout Flow              → E2E Test
Payment Processing         → E2E Test
Order Confirmation         → E2E Test
User Profile Edit          → Integration Test
Admin Dashboard            → Smoke Test Only
```

### SaaS Dashboard
```
Login Flow                 → E2E Test
Main Dashboard             → E2E Test
Create New Project         → E2E Test
Project Settings           → Integration Test
User Preferences           → Integration Test
Help Documentation         → Visual Test
Terms of Service           → Skip (static)
```

### Blog/Content Site
```
Homepage                   → Visual Test
Article Pages              → Visual Test
Search Functionality       → Integration Test
Comment System             → E2E Test
User Registration          → E2E Test
Author Dashboard           → Integration Test
Admin Panel                → Smoke Test Only
```

## ⚡ Speed vs Coverage Trade-offs

```
E2E Tests:     Slowest (5-30s each)    Highest confidence
Integration:  Medium (1-5s each)      Good confidence
Unit Tests:   Fastest (0.1-1s each)   Code confidence
Visual:       Fast (2-5s each)        UI confidence
```

## 🎯 Solo Founder Priorities

### Minimum Viable Test Suite
1. **3-5 E2E Tests** for critical journeys
2. **10-15 Integration Tests** for key features
3. **50+ Unit Tests** for business logic
4. **5-10 Visual Tests** for important pages

### Maintenance Time Allocation
- **E2E Tests**: 50% of maintenance time (most fragile)
- **Integration Tests**: 30% of maintenance time
- **Unit Tests**: 15% of maintenance time
- **Visual Tests**: 5% of maintenance time

## 🚩 Red Flags

### Too Many E2E Tests
- CI takes >15 minutes
- Tests fail randomly
- Hard to debug failures
- Team complains about test speed

### Too Few E2E Tests
- Production bugs slip through
- Critical journeys untested
- Low confidence in releases

### Missing Test Types
- No unit tests = Technical debt
- No integration tests = Integration bugs
- No visual tests = UI regressions
- No E2E tests = Critical journey bugs

---

**Remember:** Quality over quantity. Test *behaviors* that matter to users, not *pages* that exist. 🎯
