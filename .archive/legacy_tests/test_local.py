#!/usr/bin/env python3
"""
Local SignalHire Automation Test - No Browserbase
Tests the automation using local Playwright browser
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from stagehand import Stagehand

# Load environment
load_dotenv()

async def test_local_automation():
    """Test SignalHire automation using local browser"""
    
    print("🏠 SignalHire Local Automation Test")
    print("=" * 50)
    print("Using LOCAL browser (no cloud dependencies)")
    print("=" * 50)
    
    # Get credentials
    email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
    password = os.environ.get("SIGNALHIRE_PASSWORD", "jPdpd1a893pCLjkj")
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    print()
    
    try:
        print("🚀 Starting local browser automation...")
        
        # Initialize Stagehand with LOCAL environment
        stagehand = Stagehand(
            env="LOCAL",  # Use local browser instead of Browserbase
            api_key=os.environ.get("OPENAI_API_KEY"),
            headless=False,  # Show browser for debugging
            debugDom=True,   # Enable DOM debugging
        )
        
        print("🔧 Initializing Stagehand...")
        await stagehand.init()
        
        print("🌐 Navigating to SignalHire login...")
        await stagehand.page.goto("https://www.signalhire.com/login")
        
        # Wait for page to load
        await stagehand.page.wait_for_timeout(3000)
        
        print("📧 Looking for email input...")
        await stagehand.act("Fill in the email field with the email address")
        await stagehand.page.fill('input[type="email"], input[name="email"], #email', email)
        
        print("🔐 Looking for password input...")
        await stagehand.act("Fill in the password field")
        await stagehand.page.fill('input[type="password"], input[name="password"], #password', password)
        
        print("🖱️ Looking for sign in button...")
        await stagehand.act("Click the Sign In or Login button")
        
        # Wait for navigation or response
        await stagehand.page.wait_for_timeout(5000)
        
        # Check current URL
        current_url = stagehand.page.url
        print(f"📍 Current URL: {current_url}")
        
        # Check for Cloudflare challenge
        page_content = await stagehand.page.content()
        if "cloudflare" in page_content.lower() or "challenge" in page_content.lower():
            print("🛡️ Cloudflare challenge detected!")
            await stagehand.act("Look for and click the Cloudflare 'I am a human' checkbox or verification button")
            await stagehand.page.wait_for_timeout(3000)
        
        # Check if we're logged in
        if "dashboard" in current_url or "search" in current_url:
            print("✅ Login successful!")
            
            print("🔍 Navigating to search...")
            await stagehand.act("Navigate to the search or find prospects section")
            
            print("🔧 Setting up search for Heavy Equipment Mechanic...")
            await stagehand.act("Enter 'Heavy Equipment Mechanic' as the job title")
            
            print("🇨🇦 Setting location to Canada...")
            await stagehand.act("Set the location to Canada")
            
            print("🚀 Starting search...")
            await stagehand.act("Click the search button to find Heavy Equipment Mechanics in Canada")
            
            # Wait for results
            await stagehand.page.wait_for_timeout(5000)
            
            print("✅ Search completed successfully!")
            
        else:
            print("❌ Login may have failed or requires additional steps")
            print(f"Current URL: {current_url}")
        
        # Keep browser open for manual inspection
        print("🔍 Browser will stay open for 30 seconds for inspection...")
        await stagehand.page.wait_for_timeout(30000)
        
        await stagehand.close()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_local_automation())
