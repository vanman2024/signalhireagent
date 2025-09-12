# Stagehand Browser Automation Contract

## Core Integration

### Initialization
```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
  provider: "openai", // or "anthropic"
  model: "gpt-4-turbo", // or "computer-use-preview"
  headless: true,
  browserOptions: {
    timeout: 30000,
    viewport: { width: 1920, height: 1080 }
  }
});

await stagehand.init();
const page = stagehand.page;
```

## SignalHire Navigation Pattern

### Login Flow
```typescript
// Navigate to SignalHire
await page.goto("https://app.signalhire.com/login");

// AI-driven login
await page.act("click on email field");
await page.type("input[type='email']", process.env.SIGNALHIRE_EMAIL);
await page.act("click on password field");  
await page.type("input[type='password']", process.env.SIGNALHIRE_PASSWORD);
await page.act("click the login button");

// Wait for successful login
await page.waitForSelector(".dashboard", { timeout: 10000 });

// IMPORTANT: Enable new UI if not already enabled
await page.act("look for the UI toggle icon on the right side of the page");
const newUIEnabled = await page.evaluate(() => {
  // Check if new UI is already active
  return document.body.classList.contains('new-ui') || 
         document.querySelector('[data-new-ui="true"]') !== null;
});

if (!newUIEnabled) {
  await page.act("click the UI toggle icon to enable the new cleaner interface");
  await page.waitForTimeout(2000); // Wait for UI to update
  console.log("✅ New SignalHire UI enabled - cleaner interface for better automation");
}
```

### Search Automation
```typescript
// Navigate to search page
await page.act("go to the people search page");

// Fill search criteria using AI actions
await page.act("click on job title filter");
await page.act(`enter "${searchCriteria.title}" in the job title field`);

await page.act("click on location filter");
await page.act(`enter "${searchCriteria.location}" in the location field`);

if (searchCriteria.company) {
  await page.act("click on company filter");
  await page.act(`enter "${searchCriteria.company}" in company field`);
}

// Execute search
await page.act("click the search button");
await page.waitForSelector(".search-results", { timeout: 15000 });
```

### Bulk Selection and Reveal
```typescript
// Select all prospects on current page
await page.act("click select all checkbox");

// Or select specific number
const agent = stagehand.agent({
  provider: "openai",
  model: "computer-use-preview"
});

await agent.execute(`
  Select the first ${bulkSize} prospects from the search results.
  Look for checkboxes next to each prospect and click them.
`);

// Bulk reveal contacts
await page.act("click the bulk reveal contacts button");

// Handle confirmation dialog
await page.act("confirm the bulk reveal action");

// Wait for reveal to complete
await page.waitForSelector(".reveal-complete", { timeout: 300000 });
```

### Data Extraction
```typescript
// Extract prospect data using structured extraction
const prospects = await page.extract({
  instruction: "extract all prospect information from the results",
  schema: z.array(z.object({
    uid: z.string(),
    fullName: z.string(),
    currentTitle: z.string().optional(),
    currentCompany: z.string().optional(),
    location: z.string().optional(),
    email: z.string().optional(),
    phone: z.string().optional(),
    linkedinUrl: z.string().optional(),
    skills: z.array(z.string()).optional()
  }))
});

return prospects;
```

### Native Export Utilization
```typescript
// Use SignalHire's native export feature
await page.act("click the export button");
await page.act("select CSV format from export options");
await page.act("click download to start export");

// Wait for download to complete
const downloadPath = await page.waitForDownload({
  timeout: 60000
});

return downloadPath;
```

## Error Handling Patterns

### Rate Limit Detection
```typescript
// Monitor for rate limit warnings
const isRateLimited = await page.evaluate(() => {
  return document.querySelector('.rate-limit-warning') !== null;
});

if (isRateLimited) {
  await page.act("close the rate limit dialog");
  throw new RateLimitError("SignalHire rate limit reached");
}
```

### Credit Monitoring
```typescript
// Extract remaining credits
const credits = await page.extract({
  instruction: "find the remaining credits display",
  schema: z.object({
    remaining: z.number(),
    total: z.number().optional()
  })
});

if (credits.remaining < 10) {
  throw new InsufficientCreditsError(`Only ${credits.remaining} credits remaining`);
}
```

### Session Management
```typescript
// Check if still logged in
const isLoggedIn = await page.evaluate(() => {
  return !document.querySelector('.login-form');
});

if (!isLoggedIn) {
  throw new AuthenticationError("Session expired, need to re-login");
}
```

## Advanced Workflows

### Pagination Handling
```typescript
async function processAllPages(searchCriteria: SearchCriteria) {
  const allProspects = [];
  let hasNextPage = true;
  let pageNum = 1;

  while (hasNextPage && pageNum <= maxPages) {
    // Process current page
    const pageProspects = await extractCurrentPage();
    allProspects.push(...pageProspects);

    // Check for next page
    hasNextPage = await page.evaluate(() => {
      const nextBtn = document.querySelector('.pagination .next:not(.disabled)');
      return nextBtn !== null;
    });

    if (hasNextPage) {
      await page.act("click the next page button");
      await page.waitForSelector(".search-results", { timeout: 10000 });
      pageNum++;
    }
  }

  return allProspects;
}
```

### List Management
```typescript
// Save prospects to SignalHire list
await page.act("click the save to list button");
await page.act(`create new list named "${listName}"`);
await page.act("confirm list creation");

// Or add to existing list
await page.act("click add to existing list");
await page.act(`select the list named "${existingListName}"`);
await page.act("confirm adding to list");
```

## Configuration Options

### Browser Settings
```typescript
const stagehandConfig = {
  provider: "openai",
  model: "gpt-4-turbo",
  headless: process.env.NODE_ENV === "production",
  browserOptions: {
    timeout: 30000,
    viewport: { width: 1920, height: 1080 },
    userAgent: "Mozilla/5.0 (compatible; SignalHireAgent/1.0)"
  },
  retries: 3,
  retryDelay: 2000
};
```

### Action Timing
```typescript
// Configure wait times between actions
const actionConfig = {
  defaultWait: 2000,
  searchWait: 5000,
  revealWait: 10000,
  exportWait: 30000
};

// Apply delays between actions
await page.act("click search button");
await page.waitForTimeout(actionConfig.searchWait);
```

## Performance Optimization

### Caching Actions
```typescript
// Cache common UI actions for reuse
const cachedActions = {
  goToSearch: () => page.act("navigate to people search"),
  selectAll: () => page.act("click select all checkbox"),
  bulkReveal: () => page.act("click bulk reveal button")
};

// Use cached actions for better performance
await cachedActions.goToSearch();
await cachedActions.selectAll();
await cachedActions.bulkReveal();
```

### Parallel Processing
```typescript
// Process multiple search criteria in parallel
const searchPromises = searchCriteriaList.map(async (criteria) => {
  const stagehand = new Stagehand(config);
  await stagehand.init();
  return await processSearchCriteria(criteria, stagehand);
});

const results = await Promise.allSettled(searchPromises);
```

## Error Recovery

### Retry Logic
```typescript
async function withRetry<T>(action: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await action();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      await page.waitForTimeout(2000 * (i + 1)); // Exponential backoff
      
      // Try to recover from common errors
      if (error.message.includes("rate limit")) {
        await page.waitForTimeout(60000); // Wait 1 minute
      } else if (error.message.includes("session")) {
        await reLogin();
      }
    }
  }
}
```

### Cleanup and Resource Management
```typescript
// Always cleanup Stagehand instances
try {
  await performAutomation();
} finally {
  await stagehand.close();
}

// Handle process termination gracefully
process.on('SIGINT', async () => {
  await stagehand.close();
  process.exit(0);
});
```

## Multi-Platform Automation (Future)

### Platform Adapter Pattern
```typescript
interface PlatformAutomation {
  loginFlow(credentials: PlatformCredentials): Promise<void>;
  searchFlow(criteria: UnifiedSearchCriteria): Promise<Prospect[]>;
  revealFlow(prospects: Prospect[]): Promise<ContactInfo[]>;
  exportFlow(data: Prospect[], format: string): Promise<string>;
}

class LinkedInAutomation implements PlatformAutomation {
  async loginFlow(credentials: PlatformCredentials): Promise<void> {
    await page.goto("https://linkedin.com/login");
    await page.act("enter email and password for LinkedIn");
    await page.act("solve any CAPTCHA if present using AI vision");
    // LinkedIn-specific anti-detection measures
    await this.simulateHumanBehavior();
  }

  async searchFlow(criteria: UnifiedSearchCriteria): Promise<Prospect[]> {
    await page.act("navigate to Sales Navigator search");
    await page.act("configure advanced search filters");
    await page.act("execute search with human-like timing");
    return this.extractProspects();
  }

  private async simulateHumanBehavior(): Promise<void> {
    // Random delays, mouse movements, scrolling
    await page.act("scroll naturally and pause as a human would");
    await page.waitForTimeout(Math.random() * 3000 + 2000);
  }
}

class ApolloAutomation implements PlatformAutomation {
  async loginFlow(credentials: PlatformCredentials): Promise<void> {
    await page.goto("https://app.apollo.io/login");
    await page.act("login to Apollo using provided credentials");
  }

  async searchFlow(criteria: UnifiedSearchCriteria): Promise<Prospect[]> {
    await page.act("use Apollo's advanced search interface");
    await page.act("apply filters for company size, location, title");
    return this.extractApolloProspects();
  }
}
```

### AI-Enhanced Error Recovery
```typescript
class SmartErrorRecovery {
  async handleUIChanges(action: string, maxRetries: number = 3): Promise<void> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        await page.act(action);
        return; // Success
      } catch (error) {
        console.log(`Attempt ${attempt} failed: ${error.message}`);
        
        if (attempt < maxRetries) {
          // AI-powered error analysis and adaptation
          await page.act("analyze the current page and find alternative way to " + action);
          await page.waitForTimeout(2000 * attempt); // Exponential backoff
        } else {
          throw new Error(`Failed after ${maxRetries} attempts: ${action}`);
        }
      }
    }
  }

  async adaptToUIChanges(): Promise<void> {
    // Take screenshot for AI analysis
    const screenshot = await page.screenshot();
    
    // Use AI to analyze UI changes
    await page.act("observe the current interface and adapt to any layout changes");
    await page.act("find the equivalent functionality if buttons moved");
  }
}
```

### Enterprise Automation Features
```typescript
class EnterpriseAutomation {
  async teamWorkflowAutomation(workflow: TeamWorkflow): Promise<void> {
    // Assign different team members to different tasks
    for (const task of workflow.tasks) {
      switch (task.type) {
        case "search":
          await this.executeSearch(task.criteria, task.assignedTo);
          break;
        case "reveal":
          await this.executeReveal(task.prospects, task.assignedTo);
          break;
        case "export":
          await this.executeExport(task.data, task.format);
          break;
      }
    }
  }

  async whitelabelExport(data: Prospect[], branding: BrandingConfig): Promise<void> {
    await page.act("navigate to export options");
    await page.act("customize export with client branding");
    await page.act(`add custom logo and company name: ${branding.clientName}`);
    await page.act("generate branded CSV with custom headers");
  }

  async crmIntegration(prospects: Prospect[], crmConfig: CrmConfig): Promise<void> {
    // Real-time CRM sync during automation
    for (const prospect of prospects) {
      await this.syncToCRM(prospect, crmConfig);
    }
  }
}
```

---
