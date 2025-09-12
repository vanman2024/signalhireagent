#!/usr/bin/env node
/**
 * Simple SignalHire automation using Stagehand
 * This script demonstrates proper Stagehand usage without complex bridges
 */

const { Stagehand } = require('@browserbasehq/stagehand');

async function signalhireAutomation(action, params = {}) {
    console.log(`Starting SignalHire automation: ${action}`);
    
    const stagehand = new Stagehand({
        env: "LOCAL", // Use local browser
        verbose: 1,
        debugDom: false
    });

    try {
        await stagehand.init();
        console.log("✅ Stagehand initialized successfully");
        
        const page = stagehand.page;
        
        switch (action) {
            case 'test':
                await testBasicFunctionality(page);
                break;
            case 'login':
                await loginToSignalHire(page, params);
                break;
            case 'search':
                await searchProspects(page, params);
                break;
            default:
                console.log(`Unknown action: ${action}`);
        }
        
        console.log("✅ Automation completed successfully");
        
    } catch (error) {
        console.error("❌ Automation failed:", error.message);
        process.exit(1);
    } finally {
        await stagehand.close();
    }
}

async function testBasicFunctionality(page) {
    console.log("🧪 Testing basic browser functionality...");
    
    // Test with a simple public site first
    await page.goto("https://httpbin.org/get");
    
    const result = await page.extract("Get the current URL and any visible text");
    console.log("Test result:", result);
}

async function loginToSignalHire(page, { email, password }) {
    console.log("🔐 Logging into SignalHire...");
    
    // Navigate to SignalHire
    await page.goto("https://www.signalhire.com/login");
    
    // Use Stagehand's natural language actions
    await page.act("Enter email address", { text: email });
    await page.act("Enter password", { text: password });
    await page.act("Click the login button");
    
    // Wait and verify login
    await page.waitForLoadState("networkidle");
    
    const loginStatus = await page.observe("Check if login was successful or if there are any error messages");
    console.log("Login status:", loginStatus);
}

async function searchProspects(page, { title, location, company }) {
    console.log("🔍 Searching for prospects...");
    
    // Navigate to search page
    await page.goto("https://app.signalhire.com/search");
    
    // Fill in search criteria
    if (title) {
        await page.act("Enter job title in the search field", { text: title });
    }
    
    if (location) {
        await page.act("Enter location in the location field", { text: location });
    }
    
    if (company) {
        await page.act("Enter company name", { text: company });
    }
    
    // Execute search
    await page.act("Click the search button");
    
    // Wait for results
    await page.waitForLoadState("networkidle");
    
    // Get search results info
    const results = await page.observe("How many search results were found?");
    console.log("Search results:", results);
    
    return { success: true, results };
}

// Handle command line arguments
const action = process.argv[2];
const paramsJson = process.argv[3];
const params = paramsJson ? JSON.parse(paramsJson) : {};

if (!action) {
    console.log("Usage: node signalhire_automation.js <action> [params]");
    console.log("Actions: test, login, search");
    console.log("Example: node signalhire_automation.js test");
    console.log('Example: node signalhire_automation.js search \'{"title":"Software Engineer","location":"San Francisco"}\'');
    process.exit(1);
}

signalhireAutomation(action, params);
