#!/usr/bin/env python3
"""
Hybrid Cloudflare Bypass + Stagehand Automation
- Botasaurus: Handle Cloudflare bypass and login
- Stagehand: Handle search automation (the part that works well)
"""

import asyncio
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def hybrid_signalhire_automation():
    """Hybrid approach: Botasaurus for Cloudflare, Stagehand for automation"""
    
    print("🔄 HYBRID SIGNALHIRE AUTOMATION")
    print("=" * 60)
    print("Phase 1: Botasaurus (Cloudflare bypass + login)")
    print("Phase 2: Stagehand (search automation)")
    print()
    
    # Get credentials
    email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
    password = os.environ.get("SIGNALHIRE_PASSWORD")
    
    if not password:
        print("❌ Missing SIGNALHIRE_PASSWORD environment variable")
        return False
    
    print(f"✅ Using email: {email}")
    
    # Phase 1: Botasaurus for Cloudflare bypass and login
    print("\n🛡️ PHASE 1: BOTASAURUS CLOUDFLARE BYPASS")
    print("-" * 50)
    
    try:
        from botasaurus.browser import browser, Driver
        
        @browser
        def cloudflare_bypass_and_login(driver: Driver, data):
            """Use Botasaurus only for Cloudflare bypass and login"""
            
            print("🌐 Navigating to SignalHire with Cloudflare bypass...")
            driver.google_get("https://www.signalhire.com/login", bypass_cloudflare=True)
            driver.long_random_sleep()
            
            current_url = driver.page.url
            print(f"📍 Current URL: {current_url}")
            
            if "login" in current_url.lower():
                print("✅ Successfully bypassed Cloudflare, on login page")
                
                # Fill credentials with Botasaurus
                print("🔐 Filling login credentials...")
                
                try:
                    driver.type("input[type='email'], input[name*='email'], #email", email)
                    print("✅ Email filled")
                    driver.short_random_sleep()
                    
                    driver.type("input[type='password'], input[name*='password'], #password", password)
                    print("✅ Password filled")
                    driver.short_random_sleep()
                    
                    # Submit login
                    print("🚪 Clicking login button...")
                    driver.click("button[type='submit'], input[type='submit'], button:contains('Sign'), button:contains('Login')")
                    driver.long_random_sleep()
                    
                    # Check if login successful
                    final_url = driver.page.url
                    print(f"🎯 Final URL after login: {final_url}")
                    
                    if "login" not in final_url.lower():
                        print("✅ Login successful! Botasaurus phase complete")
                        
                        # Extract session cookies for Stagehand
                        cookies = driver.get_cookies()
                        print(f"🍪 Extracted {len(cookies)} cookies for Stagehand")
                        
                        return {
                            "success": True,
                            "final_url": final_url,
                            "cookies": cookies,
                            "user_agent": driver.execute_script("return navigator.userAgent")
                        }
                    else:
                        print("❌ Login failed - still on login page")
                        return {"success": False, "error": "Login failed"}
                        
                except Exception as e:
                    print(f"❌ Login process failed: {e}")
                    return {"success": False, "error": f"Login error: {e}"}
            else:
                print("❌ Unexpected page after Cloudflare bypass")
                return {"success": False, "error": "Not on login page"}
        
        # Execute Botasaurus phase
        print("🚀 Executing Botasaurus bypass...")
        result = cloudflare_bypass_and_login()
        
        if not result.get("success"):
            print(f"❌ Botasaurus phase failed: {result.get('error')}")
            return False
        
        print("✅ Botasaurus phase completed successfully!")
        
    except Exception as e:
        print(f"💥 Botasaurus phase failed: {e}")
        return False
    
    # Phase 2: Stagehand for search automation
    print("\n🎯 PHASE 2: STAGEHAND SEARCH AUTOMATION")
    print("-" * 50)
    
    try:
        from stagehand import Stagehand
        
        # Initialize Stagehand with session from Botasaurus
        print("🚀 Initializing Stagehand with authenticated session...")
        
        stagehand = Stagehand(
            env="BROWSERBASE",
            api_key=os.environ.get("BROWSERBASE_API_KEY"),
            project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
            headless=False  # Keep visible for verification
        )
        
        # Set cookies from Botasaurus session
        cookies = result.get("cookies", [])
        if cookies:
            print(f"🍪 Setting {len(cookies)} cookies from Botasaurus session...")
            for cookie in cookies:
                await stagehand.page.context.add_cookies([cookie])
        
        # Navigate to search page (should already be authenticated)
        print("🔍 Navigating to search page...")
        await stagehand.page.goto("https://www.signalhire.com/search")
        await stagehand.page.wait_for_load_state()
        
        # Take screenshot to verify we're authenticated
        await stagehand.page.screenshot(path="authenticated_search.png")
        print("📸 Screenshot saved: authenticated_search.png")
        
        # Use Stagehand for search automation (this works well)
        print("⚙️ Setting up search with Stagehand...")
        
        # Fill job title
        await stagehand.act("Fill in the job title field with 'Heavy Equipment Mechanic'")
        await asyncio.sleep(2)
        print("✅ Job title filled")
        
        # Fill location
        await stagehand.act("Fill in the location field with 'Canada'")
        await asyncio.sleep(2)
        print("✅ Location filled")
        
        # Click search
        await stagehand.act("Click the search button to start the search")
        await asyncio.sleep(5)
        print("✅ Search initiated")
        
        # Take final screenshot
        await stagehand.page.screenshot(path="search_results.png")
        print("📸 Final screenshot saved: search_results.png")
        
        current_url = stagehand.page.url
        print(f"🎯 Final search URL: {current_url}")
        
        print("\n🎉 HYBRID AUTOMATION COMPLETED SUCCESSFULLY!")
        print("✅ Cloudflare bypassed with Botasaurus")
        print("✅ Search automated with Stagehand")
        
        await stagehand.close()
        return True
        
    except Exception as e:
        print(f"💥 Stagehand phase failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🔄 Starting Hybrid SignalHire Automation...")
    print("Combining Botasaurus (Cloudflare bypass) + Stagehand (search automation)")
    print()
    
    success = asyncio.run(hybrid_signalhire_automation())
    
    if success:
        print("\n🎉 HYBRID AUTOMATION SUCCEEDED!")
        print("Best of both worlds: Cloudflare bypass + reliable automation")
    else:
        print("\n❌ HYBRID AUTOMATION FAILED!")
        print("Check the output above for details")
    
    return success

if __name__ == "__main__":
    main()
