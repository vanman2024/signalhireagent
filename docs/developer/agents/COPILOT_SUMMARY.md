# @copilot Browser Automation Implementation Guide

## 🎯 Critical Browser Automation Issue to Fix

The project has transitioned to **API-only mode** for increased reliability. Browser automation content below is preserved for historical context but is no longer applicable.

## 🚨 Current Problem
The API client in `src/services/signalhire_client.py` includes enhanced retry, concurrency, progress reporting, and credit checks.

## 🎯 Specific Workflow Needed

### Target Use Case: Heavy Equipment Mechanic Search
```
1. Login to SignalHire ✅ (browser opens, form filling works)
2. Navigate to search page ✅
3. Search for "Heavy Equipment Mechanic" in Canada 
4. Process ALL 2,334 results by:
   - Select bulk option (10 selections at a time limitation)
   - Move to next page automatically  
   - Repeat until all 2,334 people processed
   - Click export action button → CSV download
5. Save CSV with all email addresses
```

## 🔧 Files That Need Browser Logic Implementation

### 1. `src/services/signalhire_client.py` - PRIORITY 1
**Current Status**: Enhanced API client in place

**Need to Implement**:
```python
async def search_prospects(self, search_criteria, max_results=None):
    # SPECIFIC SignalHire UI interactions needed:
    
    # Navigate to search
    await self.bridge.goto("https://app.signalhire.com/search")
    
    # Fill job title field (find exact CSS selector)
    await self.bridge.act("Click job title field")
    await self.bridge.act("Type 'Heavy Equipment Mechanic'")
    
    # Fill location field  
    await self.bridge.act("Click location field")
    await self.bridge.act("Type 'Canada'")
    
    # Click search button
    await self.bridge.act("Click search button")
    
    # Wait for results to load
    await self.bridge.wait_for_load_state("networkidle")
```

### 2. Bulk Selection Logic - PRIORITY 1
```python
async def bulk_reveal_contacts(self, export_format="csv", max_contacts=None):
    # CRITICAL: Handle SignalHire's 10-at-a-time limitation
    
    page_number = 1
    total_processed = 0
    
    while total_processed < max_contacts:
        # Select bulk checkbox (top of page)
        await self.bridge.act("Click bulk select checkbox at top")
        
        # Process current page (max 10 selections)
        current_page_selections = min(10, max_contacts - total_processed)
        
        # Move to next page
        await self.bridge.act("Click next page button")
        page_number += 1
        total_processed += current_page_selections
        
        # Wait for page load
        await self.bridge.wait_for_load_state("networkidle")
    
    # After all selections, click export
    await self.bridge.act("Click export action button")
    
    # Download CSV
    export_file = await self._wait_for_download()
    return export_file
```

## 🔍 Browser Testing Environment Available

### Docker Environment Ready ✅
```bash
# Start development environment
docker-compose up -d signalhire-agent

# Run organized test suite
python3 run.py -m pytest tests/contract/test_api_client_enhanced.py -q
python3 run_tests.py quick           # Quick smoke + unit tests
python3 run_tests.py integration     # Integration tests

# API-first contract tests
pytest tests/contract/test_cli_api_first.py -q
pytest tests/contract/test_csv_export_enhanced.py -q
```

### Current Test Status:
- ✅ Browser opens successfully
- ✅ SignalHire website accessible  
- ✅ Login page structure detected
- ✅ Screenshot capture working
- ⏳ **NEED**: Specific UI element interactions

## 🎯 Immediate Action Items for @copilot

### 1. **Fix Browser Client Logic** - `src/services/browser_client.py`
Replace these placeholder functions with real SignalHire interactions:

```python
# CURRENT (doesn't work):
await self.stagehand.act("Enter job title in search field", text="Engineer")

# NEED (specific selectors):
await self.bridge.act("Click the job title input field with selector '[data-testid=job-title-input]'")
await self.bridge.act("Type 'Heavy Equipment Mechanic' in the focused field")
```

### 2. **Create SignalHire UI Mapping** - New file needed
Create `src/lib/signalhire_selectors.py`:
```python
# SignalHire UI element selectors and actions
SELECTORS = {
    "login": {
        "email_field": 'input[type="email"]',
        "password_field": 'input[type="password"]', 
        "login_button": 'button:contains("Log")'
    },
    "search": {
        "job_title_field": '[data-testid="job-title"]',  # Need actual selector
        "location_field": '[data-testid="location"]',     # Need actual selector  
        "search_button": 'button:contains("Search")',
        "bulk_select": '[data-testid="bulk-select"]'     # Need actual selector
    },
    "results": {
        "next_page": 'button:contains("Next")',
        "export_button": 'button:contains("Export")'
    }
}
```

### 3. **Create Stagehand Bridge** - `src/lib/stagehand_wrapper.py`
The browser client references a `StagehandBridge` class that doesn't exist yet. You need to create this Python-to-Node.js bridge.

## 🎯 Testing Strategy

### Step 1: Visual Browser Testing
```python
# In test_docker_browser.py, set headless=False to see what's happening:
browser = await p.chromium.launch(headless=False)  # Watch the browser work
```

### Step 2: Element Discovery  
```python
# Add to test to find the actual CSS selectors:
await page.goto("https://app.signalhire.com/search")
elements = await page.query_selector_all("input")
for element in elements:
    print(await element.get_attribute("data-testid"))
    print(await element.get_attribute("placeholder"))
```

### Step 3: Real Credential Testing
Set environment variables and test actual login:
```bash
export SIGNALHIRE_EMAIL="your-test-account@example.com"  
export SIGNALHIRE_PASSWORD="your-password"
```

## 🎯 Success Criteria

When this is working correctly, you should be able to:

1. **See the browser open** ✅ (already working)
2. **Watch agent login** (need to implement login sequence)
3. **Search for "Heavy Equipment Mechanic in Canada"** (need search logic)
4. **Bulk select 10 at a time through all 2,334 results** (need pagination logic)
5. **Export CSV with all emails** (need export button click)
6. **Download file automatically** (need download handling)

## 🛠 Development Workflow

1. **Use Docker environment** for consistent testing
2. **Set headless=False** to watch browser actions
3. **Take screenshots** at each step for debugging  
4. **Test with small batches first** (10-50 people) before full 2,334
5. **Add logging** at each step to track progress

The infrastructure is solid - now we just need the **specific SignalHire UI interaction logic**! 🚀
