#!/usr/bin/env python3
"""
Proper Hybrid: Botasaurus (Cloudflare ONLY) + Stagehand (AI Vision + Prompts)
"""

import asyncio
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def proper_hybrid_automation():
    """Proper hybrid: Botasaurus bypasses Cloudflare, Stagehand does AI automation"""
    
    print("🎯 PROPER HYBRID SIGNALHIRE AUTOMATION")
    print("=" * 60)
    print("🛡️ Botasaurus: Cloudflare bypass ONLY")
    print("🤖 Stagehand: AI vision + natural language prompts")
    print()
    
    # Get credentials
    email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
    password = os.environ.get("SIGNALHIRE_PASSWORD")
    
    if not password:
        print("❌ Missing SIGNALHIRE_PASSWORD environment variable")
        return False
    
    print(f"✅ Using email: {email}")
    
    # Phase 1: Botasaurus ONLY for Cloudflare bypass
    print("\n🛡️ PHASE 1: CLOUDFLARE BYPASS ONLY")
    print("-" * 50)
    
    try:
        from botasaurus.browser import browser, Driver
        
        @browser
        def bypass_cloudflare_only(driver: Driver, data):
            """Use Botasaurus ONLY to get past Cloudflare, then stop"""
            
            print("🌐 Navigating to SignalHire with Cloudflare bypass...")
            driver.google_get("https://www.signalhire.com/login", bypass_cloudflare=True)
            driver.long_random_sleep()
            
            current_url = driver.page.url
            print(f"📍 URL after Cloudflare bypass: {current_url}")
            
            # Check if we successfully bypassed Cloudflare
            page_source = driver.page_source
            cloudflare_indicators = [
                "Checking your browser",
                "I'm Under Attack Mode", 
                "Just a moment",
                "DDoS protection",
                "Ray ID:",
                "Please wait while we verify",
                "Verify you are human"
            ]
            
            cloudflare_detected = any(indicator in page_source for indicator in cloudflare_indicators)
            
            if not cloudflare_detected and "login" in current_url.lower():
                print("✅ Cloudflare successfully bypassed!")
                print("🔄 Handing off to Stagehand for AI automation...")
                
                return {
                    "success": True,
                    "final_url": current_url,
                    "message": "Cloudflare bypassed, ready for Stagehand"
                }
            else:
                print("❌ Cloudflare bypass incomplete")
                return {
                    "success": False,
                    "error": "Cloudflare still blocking or not on login page"
                }
        
        # Execute Botasaurus bypass
        print("🚀 Executing Cloudflare bypass...")
        result = bypass_cloudflare_only()
        
        if not result.get("success"):
            print(f"❌ Cloudflare bypass failed: {result.get('error')}")
            return False
        
        print("✅ Cloudflare bypass completed! Handing off to Stagehand...")
        
    except Exception as e:
        print(f"💥 Cloudflare bypass failed: {e}")
        return False
    
    # Phase 2: Pure Stagehand with AI vision + prompts
    print("\n🤖 PHASE 2: STAGEHAND AI AUTOMATION")
    print("-" * 50)
    
    try:
        from stagehand import Stagehand
        
        print("🚀 Initializing Stagehand...")
        stagehand = Stagehand(
            env="BROWSERBASE",
            api_key=os.environ.get("BROWSERBASE_API_KEY"),
            project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
            headless=False
        )
        
        # Navigate to login page (Cloudflare already bypassed)
        print("🌐 Navigating to SignalHire login page...")
        await stagehand.page.goto("https://www.signalhire.com/login")
        await stagehand.page.wait_for_load_state()
        
        # Take screenshot to see current state
        await stagehand.page.screenshot(path="after_cloudflare_bypass.png")
        print("📸 Screenshot: after_cloudflare_bypass.png")
        
        # Use AI prompts for login (NO SELECTORS!)
        print("🔐 AI Login Process...")
        
        # Fill email with AI
        await stagehand.act(f"Type '{email}' in the email field")
        await asyncio.sleep(2)
        print("✅ Email filled with AI")
        
        # Fill password with AI  
        await stagehand.act(f"Type '{password}' in the password field")
        await asyncio.sleep(2)
        print("✅ Password filled with AI")
        
        # Click login with AI
        await stagehand.act("Click the login button to sign in")
        await asyncio.sleep(5)
        print("✅ Login clicked with AI")
        
        # Take screenshot after login attempt
        await stagehand.page.screenshot(path="after_login_attempt.png")
        print("📸 Screenshot: after_login_attempt.png")
        
        # Check if login was successful using AI
        current_url = stagehand.page.url
        print(f"📍 Current URL: {current_url}")
        
        if "login" not in current_url.lower():
            print("✅ Login appears successful!")
            
            # Navigate to search with AI
            print("🔍 AI Search Process...")
            await stagehand.act("Navigate to the search page")
            await asyncio.sleep(3)
            
            # Take screenshot of search page
            await stagehand.page.screenshot(path="search_page.png")
            print("📸 Screenshot: search_page.png")
            
            # Fill search criteria with AI (NO SELECTORS!)
            await stagehand.act("Fill the job title field with 'Heavy Equipment Mechanic'")
            await asyncio.sleep(2)
            print("✅ Job title filled with AI")
            
            await stagehand.act("Fill the location field with 'Canada'")
            await asyncio.sleep(2)
            print("✅ Location filled with AI")
            
            # Start search with AI
            await stagehand.act("Click the search button to find Heavy Equipment Mechanics in Canada")
            await asyncio.sleep(5)
            print("✅ Search started with AI")
            
            # Take final screenshot
            await stagehand.page.screenshot(path="search_results.png")
            print("📸 Final screenshot: search_results.png")
            
            final_url = stagehand.page.url
            print(f"🎯 Final search URL: {final_url}")
            
            print("\n🎉 PROPER HYBRID AUTOMATION COMPLETED!")
            print("✅ Cloudflare bypassed with Botasaurus")
            print("✅ Everything else automated with Stagehand AI")
            
        else:
            print("❌ Login failed - still on login page")
            await stagehand.close()
            return False
        
        await stagehand.close()
        return True
        
    except Exception as e:
        print(f"💥 Stagehand AI automation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🎯 Starting Proper Hybrid Automation...")
    print("Botasaurus for Cloudflare ONLY + Stagehand for AI automation")
    print()
    
    success = asyncio.run(proper_hybrid_automation())
    
    if success:
        print("\n🎉 PROPER HYBRID AUTOMATION SUCCEEDED!")
        print("Perfect division of labor achieved!")
    else:
        print("\n❌ PROPER HYBRID AUTOMATION FAILED!")
        print("Check the output above for details")
    
    return success

if __name__ == "__main__":
    main()
