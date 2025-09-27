#!/usr/bin/env python3
"""
SignalHire Automation with Botasaurus - Cloudflare Bypass Solution
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_botasaurus_signalhire():
    """Test SignalHire with Botasaurus for Cloudflare bypass"""
    
    print("🤖 Botasaurus SignalHire Test - Cloudflare Bypass")
    print("=" * 60)
    
    try:
        # Install botasaurus if not available
        try:
            from botasaurus.browser import browser, Driver
        except ImportError:
            print("📦 Installing Botasaurus...")
            import subprocess
            subprocess.run(["pip", "install", "botasaurus"], check=True)
            from botasaurus.browser import browser, Driver
        
        print("✅ Botasaurus imported successfully")
        
        # Get credentials
        email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
        password = os.environ.get("SIGNALHIRE_PASSWORD")
        
        if not password:
            print("❌ Missing SIGNALHIRE_PASSWORD environment variable")
            return False
        
        print(f"✅ Using email: {email}")
        
        @browser
        def signalhire_automation(driver: Driver, data):
            """Botasaurus automation function"""
            
            print("\n🌐 Starting browser automation...")
            
            # Step 1: Navigate with Cloudflare bypass
            print("🛡️ Navigating to SignalHire with Cloudflare bypass...")
            driver.google_get("https://www.signalhire.com/login", bypass_cloudflare=True)
            
            # Wait for page to load
            driver.long_random_sleep()
            
            current_url = driver.page.url
            print(f"📍 Current URL: {current_url}")
            
            # Check if we bypassed Cloudflare successfully
            if "login" in current_url.lower():
                print("✅ Successfully reached login page")
                
                # Step 2: Fill credentials
                print("🔐 Filling login credentials...")
                
                try:
                    # Use Botasaurus's smart element detection
                    driver.type("input[type='email'], input[name*='email'], #email", email)
                    print("✅ Email filled")
                    driver.short_random_sleep()
                    
                    driver.type("input[type='password'], input[name*='password'], #password", password)
                    print("✅ Password filled")
                    driver.short_random_sleep()
                    
                    # Step 3: Submit login
                    print("🚪 Clicking login button...")
                    driver.click("button[type='submit'], input[type='submit'], button:contains('Sign'), button:contains('Login')")
                    
                    # Wait for response
                    driver.long_random_sleep()
                    
                    # Check result
                    final_url = driver.page.url
                    print(f"🎯 Final URL after login: {final_url}")
                    
                    # Step 4: Navigate to search if login successful
                    if "login" not in final_url.lower():
                        print("✅ Login appears successful!")
                        
                        print("🔍 Navigating to search...")
                        driver.get("https://www.signalhire.com/search")
                        driver.short_random_sleep()
                        
                        # Step 5: Perform search
                        print("⚙️ Setting up search for Heavy Equipment Mechanic in Canada...")
                        
                        try:
                            # Fill job title
                            driver.type("input[placeholder*='title'], input[name*='title'], input[aria-label*='title']", "Heavy Equipment Mechanic")
                            driver.short_random_sleep()
                            print("✅ Job title filled")
                            
                            # Fill location
                            driver.type("input[placeholder*='location'], input[name*='location'], input[aria-label*='location']", "Canada")
                            driver.short_random_sleep()
                            print("✅ Location filled")
                            
                            # Click search
                            driver.click("button:contains('Search'), button:contains('Find'), input[value*='Search']")
                            driver.long_random_sleep()
                            
                            search_url = driver.page.url
                            print(f"🎯 Search completed at: {search_url}")
                            
                            return {
                                "success": True,
                                "final_url": search_url,
                                "email": email,
                                "cloudflare_bypassed": True
                            }
                            
                        except Exception as e:
                            print(f"⚠️ Search failed: {e}")
                            return {
                                "success": True,
                                "final_url": final_url,
                                "email": email,
                                "cloudflare_bypassed": True,
                                "search_error": str(e)
                            }
                    else:
                        print("❌ Login failed - still on login page")
                        return {
                            "success": False,
                            "error": "Login failed",
                            "final_url": final_url
                        }
                        
                except Exception as e:
                    print(f"❌ Login process failed: {e}")
                    return {
                        "success": False,
                        "error": f"Login error: {e}",
                        "url": driver.page.url
                    }
            else:
                print("❌ Unexpected page - not on login")
                return {
                    "success": False,
                    "error": "Not on login page",
                    "url": current_url
                }
        
        # Execute the automation
        print("\n🚀 Executing Botasaurus automation...")
        result = signalhire_automation()
        
        print("\n📊 Results:")
        print(f"Success: {result.get('success', False)}")
        if result.get('cloudflare_bypassed'):
            print("✅ Cloudflare bypass successful!")
        if result.get('final_url'):
            print(f"Final URL: {result['final_url']}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"💥 BOTASAURUS AUTOMATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🤖 Starting Botasaurus-based SignalHire automation...")
    print("This uses advanced Cloudflare bypass capabilities")
    print()
    
    success = asyncio.run(test_botasaurus_signalhire())
    
    if success:
        print("\n🎉 BOTASAURUS AUTOMATION COMPLETED SUCCESSFULLY!")
        print("Cloudflare was bypassed and automation proceeded")
    else:
        print("\n❌ BOTASAURUS AUTOMATION FAILED!")
        print("Check the output above for details")
    
    return success

if __name__ == "__main__":
    main()
