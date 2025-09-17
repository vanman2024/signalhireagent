# Frontend Unit Tests

**Component-level and function-level testing for frontend code.**

## 🎯 **Purpose**

Frontend unit tests focus on:
- **Component behavior**: Props, state, events
- **Pure functions**: Utilities, helpers, calculations  
- **Custom hooks**: React/Vue hooks in isolation
- **Business logic**: Frontend-specific algorithms

## 📁 **Structure**

```
unit/
├── components/          # Component testing
│   ├── Button.test.tsx
│   ├── Modal.test.tsx
│   └── Form.test.tsx
├── hooks/              # Custom hooks testing  
│   ├── useAuth.test.tsx
│   └── useApi.test.tsx
├── utils/              # Utility function testing
│   ├── formatters.test.ts
│   └── validators.test.ts
└── stores/             # State management testing
    ├── authStore.test.ts
    └── userStore.test.ts
```

## 🔧 **Testing Tools**

### **React Projects**
```bash
# Example component test
import { render, screen } from '@testing-library/react'
import { Button } from './Button'

test('renders button with text', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByText('Click me')).toBeInTheDocument()
})
```

### **Vue Projects**
```bash
# Example component test
import { mount } from '@vue/test-utils'
import Button from './Button.vue'

test('renders button with text', () => {
  const wrapper = mount(Button, {
    props: { text: 'Click me' }
  })
  expect(wrapper.text()).toBe('Click me')
})
```

## 🚀 **Running Unit Tests**

### **Via DevOps System**
```bash
# Run all frontend tests (includes unit)
./devops/ops/ops qa --frontend

# Or run just unit tests
npm run test:unit
```

### **Direct Commands**
```bash
# React with Jest
npm run test:unit
npm run test:unit:watch
npm run test:unit:coverage

# Vue with Vitest  
npm run test:unit
npm run test:unit:watch
npm run test:unit:coverage
```

## 📊 **Unit vs Integration vs E2E**

### **Frontend Unit Tests** (This folder)
- ✅ **Component props/state**: Test component behavior in isolation
- ✅ **Pure functions**: Test utilities, formatters, validators
- ✅ **Custom hooks**: Test hooks with mock dependencies
- ✅ **Fast**: Run in milliseconds, no browser needed

### **Frontend Integration Tests** (`../integration/`)
- ✅ **Component interaction**: Multiple components working together
- ✅ **API integration**: Components with real/mocked API calls
- ✅ **Route testing**: Navigation and routing behavior

### **Frontend E2E Tests** (`../e2e/`)
- ✅ **User journeys**: Complete workflows from user perspective
- ✅ **Cross-browser**: Real browser testing
- ✅ **Production-like**: Full application stack

## 🎨 **Examples**

### **Component Unit Test**
```typescript
// components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  test('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  test('renders with correct variant class', () => {
    render(<Button variant="primary">Primary Button</Button>)
    expect(screen.getByText('Primary Button')).toHaveClass('btn-primary')
  })
})
```

### **Utility Unit Test**
```typescript
// utils/formatters.test.ts
import { formatCurrency, formatDate } from './formatters'

describe('Formatters', () => {
  test('formatCurrency formats USD correctly', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56')
  })
  
  test('formatDate handles invalid dates', () => {
    expect(formatDate('invalid')).toBe('Invalid Date')
  })
})
```

### **Hook Unit Test**
```typescript
// hooks/useAuth.test.tsx
import { renderHook, act } from '@testing-library/react'
import { useAuth } from './useAuth'

describe('useAuth Hook', () => {
  test('login updates user state', async () => {
    const { result } = renderHook(() => useAuth())
    
    await act(async () => {
      await result.current.login('user@example.com', 'password')
    })
    
    expect(result.current.user).toBeTruthy()
    expect(result.current.isAuthenticated).toBe(true)
  })
})
```

---

**🎯 Template Note**: Frontend unit tests complement backend unit tests by focusing on UI components, user interactions, and frontend-specific business logic.