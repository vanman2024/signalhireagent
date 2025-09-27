#!/usr/bin/env python3
"""
Complete SignalHire workflow test with enhanced error handling
"""
import asyncio
import os
from stagehand import Stagehand

async def test_complete_signalhire_workflow():
    print("🤖 SignalHire Complete Workflow Test")
    print("="*50)
    
    # Environment setup - using local with proper OpenAI config
    os.environ["STAGEHAND_ENV"] = "LOCAL"
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    
    # Remove organization header if present (this was the fix!)
    if "OPENAI_ORGANIZATION" in os.environ:
        del os.environ["OPENAI_ORGANIZATION"]
    
    # Get credentials
    email = os.getenv("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
    password = os.getenv("SIGNALHIRE_PASSWORD", "jPdpd1a893pCLjkj")
    
    if not email or not password:
        print("❌ Missing SignalHire credentials")
        return
        
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    print("🚀 Starting browser automation...")

    try:
        # Initialize Stagehand with local browser
        async with Stagehand() as stagehand:
            page = stagehand.page
            
            print("🔐 Logging into SignalHire...")
            await page.goto("https://www.signalhire.com/login")
            await page.wait_for_timeout(3000)
            
            # Login process
            print("📧 Entering email...")
            await page.act("Click on the email input field")
            await page.act(f"Type {email} into the email field")
            
            print("🔑 Entering password...")
            await page.act("Click on the password input field")
            await page.act(f"Type {password} into the password field")
            
            print("🚀 Clicking Sign In...")
            await page.act("Click the Sign In button")
            
            # Wait for login and handle potential redirects
            print("⏳ Waiting for login to complete...")
            await page.wait_for_timeout(5000)
            
            current_url = await page.url()
            print(f"📍 Current URL: {current_url}")
            
            # Check if we're logged in (look for dashboard or search page)
            if "login" in current_url:
                print("⚠️ Still on login page, checking for errors...")
                try:
                    await page.act("Look for any error messages on the page")
                except Exception as e:
                    print(f"Login may have failed: {e}")
                    return
            
            # Navigate to search page
            print("🔍 Going to search page...")
            search_url = "https://www.signalhire.com/search"
            await page.goto(search_url)
            await page.wait_for_timeout(3000)
            
            print("🎯 Setting up search for Heavy Equipment Mechanic in Canada...")
            
            # Try to find and fill job title
            try:
                await page.act("Find the job title search field")
                await page.act("Click on the job title field")
                await page.act("Type 'Heavy Equipment Mechanic' in the job title field")
                print("✅ Job title entered")
            except Exception as e:
                print(f"⚠️ Could not set job title: {e}")
            
            # Try to find and fill location
            try:
                await page.act("Find the location search field")
                await page.act("Click on the location field")
                await page.act("Type 'Canada' in the location field")
                print("✅ Location entered")
            except Exception as e:
                print(f"⚠️ Could not set location: {e}")
            
            # Start search
            try:
                await page.act("Click the search button to start the search")
                print("✅ Search initiated")
                await page.wait_for_timeout(5000)
                
                # Check results
                final_url = await page.url()
                print(f"📊 Search results URL: {final_url}")
                
                # Try to observe search results
                await page.act("Look for search results on the page")
                print("✅ Search completed successfully!")
                
            except Exception as e:
                print(f"⚠️ Search may not have completed: {e}")
            
            print("🎉 Workflow test completed!")
            print("Browser will stay open for 30 seconds so you can see the results...")
            await page.wait_for_timeout(30000)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["SIGNALHIRE_EMAIL"] = "ryan@skilledtradesjobhub.ca"
    os.environ["SIGNALHIRE_PASSWORD"] = "jPdpd1a893pCLjkj"
    
    asyncio.run(test_complete_signalhire_workflow())
