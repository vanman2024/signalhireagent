# Testing Strategy (API-Only)

## The Testing Challenge

SignalHire Agent now operates in API-only mode. Legacy notes on browser automation remain below for historical reference.

1. **External Dependencies**: Web interfaces change unpredictably
2. **Rate Limits**: APIs and websites limit testing frequency  
3. **Authentication**: Requires real credentials for meaningful tests
4. **Dynamic Content**: Web pages load differently each time
5. **Timing Issues**: Network delays, rendering delays, etc.

## Multi-Layer Testing Framework

### Layer 1: Unit Tests (Isolated Logic)
**What**: Test pure functions and business logic without external dependencies
**How**: Mock all external calls, focus on data processing and validation
**Example**:
```python
# Test credential validation
def test_validate_email():
    assert validate_email("user@example.com").is_valid == True
    assert validate_email("invalid-email").is_valid == False

# Test data parsing
def test_parse_prospect_data():
    raw_data = {"name": "John Doe", "title": "Engineer"}
    prospect = parse_prospect(raw_data)
    assert prospect.name == "John Doe"
```

### Layer 2: Integration Tests (Service Layer)
**What**: Test service interactions with mocked external dependencies
**How**: Mock browser/API calls, test error handling and data flow
**Example**:
```python
@patch('src.services.signalhire_client.SignalHireClient')
async def test_search_service(mock_client):
    # Mock successful search
    mock_client.search_prospects.return_value = APIResponse(success=True, data={"total": 100})
    # service = SearchService(mock_client)  # adapt to your layer
    # result = await service.perform_search(criteria)
    # assert result.total_found == 100
```

### Layer 3: Contract Tests (API/UI Contracts)
**What**: Test that external interfaces work as expected
**How**: Real calls to APIs/websites with minimal data
**Example**:
```python
@pytest.mark.contract
async def test_credits_api_contract():
    """Test that the credits API contract is stable"""
    client = SignalHireClient(api_key="test")
    resp = await client.check_credits()
    assert hasattr(resp, 'success')
```

### Layer 4: End-to-End Tests (Production-like)
**What**: Full workflow tests with real credentials and data
**How**: Limited runs with test accounts, careful cleanup
**Example**:
```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_full_search_workflow_api():
    """Full workflow: search -> partial reveal (API)"""
    client = SignalHireClient(api_key="test")
    result = await client.search_prospects({"title": "Engineer"}, limit=5)
    assert hasattr(result, 'success')
```

## Testing Environment Strategy

### Local Development
```bash
# Quick smoke tests
pytest tests/unit/ -v

# Contract tests (requires internet)
pytest tests/contract/ -v --slow

# Skip expensive tests
pytest -m "not slow and not e2e"
```

### Continuous Integration
```yaml
# GitHub Actions example
test-matrix:
  - Unit Tests: Fast, no external deps
  - Contract Tests: Check API/UI changes daily
  - Integration Tests: Mock all external calls
  
# E2E tests: Run weekly with test account
```

### Production Monitoring
```python
# Health check endpoint (API-only)
@app.get("/health")
async def health_check():
    return {
        "signalhire_reachable": await ping_signalhire_api(),
        "credentials_valid": await validate_api_credentials()
    }
```

## Test Data Management

### Test Account Strategy
- **Dedicated test account**: Separate from production
- **Limited operations**: Avoid burning real credits
- **Cleanup procedures**: Remove test data after runs
- **Rate limit awareness**: Space out tests appropriately

### Mock Data Patterns
```python
# Realistic test data
@pytest.fixture
def sample_prospects():
    return [
        Prospect(
            name="Test Engineer",
            title="Software Engineer", 
            company="Test Corp",
            location="San Francisco, CA"
        )
    ]

# Mock external responses
@pytest.fixture  
def mock_signalhire_search_response():
    return {
        "total_count": 1250,
        "prospects": [...],
        "credits_remaining": 500
    }
```

## Browser Automation Testing Patterns

### Reliable Element Selection
```python
# Bad: Fragile selectors
await page.click("#login-btn-v2-new")

# Good: Multiple fallback strategies  
login_selectors = [
    'button:has-text("Log in")',
    'input[type="submit"][value*="login" i]',
    '[data-testid="login-button"]'
]

for selector in login_selectors:
    try:
        await page.click(selector, timeout=5000)
        break
    except TimeoutError:
        continue
```

### Robust Waiting Strategies
```python
# Wait for multiple conditions
async def wait_for_search_results(page):
    await page.wait_for_load_state("networkidle")
    await page.wait_for_selector(".search-results", timeout=10000)
    
    # Ensure results are actually loaded
    await page.wait_for_function("""
        () => document.querySelectorAll('.prospect-card').length > 0
    """)
```

### Error Recovery and Screenshots
```python
async def safe_browser_action(action_func, context):
    try:
        return await action_func()
    except Exception as e:
        # Capture state for debugging
        screenshot = await context.page.screenshot()
        html = await context.page.content()
        
        # Save debug info
        debug_dir = Path("debug_screenshots")
        debug_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(debug_dir / f"error_{timestamp}.png", "wb") as f:
            f.write(screenshot)
            
        raise BrowserActionError(f"Action failed: {e}", screenshot_path=screenshot_file)
```

## Monitoring and Alerting

### Change Detection
```python
# Monitor for UI changes
async def monitor_signalhire_ui():
    """Daily check for UI changes that could break automation"""
    
    async with playwright_browser() as page:
        await page.goto("https://app.signalhire.com/login")
        
        # Take screenshot
        screenshot = await page.screenshot()
        
        # Compare with baseline
        if visual_diff(screenshot, "baseline_login.png") > threshold:
            alert_team("SignalHire login page has changed significantly")
            
        # Check element structure
        expected_elements = [
            'input[type="email"]',
            'input[type="password"]', 
            'button:has-text("Log")'
        ]
        
        missing_elements = []
        for element in expected_elements:
            if await page.locator(element).count() == 0:
                missing_elements.append(element)
                
        if missing_elements:
            alert_team(f"Missing UI elements: {missing_elements}")
```

### Performance Monitoring
```python
# Track operation timing
async def monitored_search(criteria):
    start_time = time.time()
    
    try:
        result = await perform_search(criteria)
        duration = time.time() - start_time
        
        # Log performance metrics
        logger.info("search_completed", {
            "duration": duration,
            "results_count": result.total_found,
            "success": True
        })
        
        # Alert on slow operations
        if duration > 60:  # 1 minute threshold
            alert_team(f"Slow search operation: {duration}s")
            
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error("search_failed", {
            "duration": duration,
            "error": str(e),
            "success": False
        })
        raise
```

## Test Configuration

### Environment-Specific Testing
```python
# test_config.py
@dataclass 
class TestConfig:
    # Test account credentials
    test_email: str = os.getenv("TEST_SIGNALHIRE_EMAIL")
    test_password: str = os.getenv("TEST_SIGNALHIRE_PASSWORD") 
    
    # Test behavior
    run_e2e_tests: bool = os.getenv("RUN_E2E_TESTS", "false").lower() == "true"
    max_test_credits: int = int(os.getenv("MAX_TEST_CREDITS", "10"))
    
    # Browser settings for tests
    headless_browser: bool = os.getenv("HEADLESS", "true").lower() == "true"
    browser_timeout: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    @property
    def can_run_expensive_tests(self) -> bool:
        return self.test_email and self.test_password and self.run_e2e_tests
```

### Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
markers =
    unit: Unit tests (fast, no external deps)
    integration: Integration tests (mocked externals)
    contract: Contract tests (real external calls, minimal data)
    e2e: End-to-end tests (full workflow, uses credits)
    slow: Tests that take >30 seconds
    
addopts = 
    -v
    --tb=short
    --strict-markers
    -m "not slow"  # Skip slow tests by default
    
testpaths = tests/
```

## Key Principles for Browser Automation Testing

1. **Test Pyramid**: Many unit tests, fewer integration tests, minimal E2E tests
2. **Fail Fast**: Detect UI changes quickly with lightweight contract tests  
3. **Isolation**: Each test should be independent and cleanable
4. **Realistic Data**: Use production-like test data but in small quantities
5. **Graceful Degradation**: Tests should handle partial failures gracefully
6. **Documentation**: Every flaky test needs investigation notes
7. **Monitoring**: Treat test health as a production concern

This framework ensures reliable testing while minimizing costs and external dependencies, which is crucial for applications that interact with third-party services like SignalHire.
