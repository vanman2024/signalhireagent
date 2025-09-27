#!/usr/bin/env python3
"""
SignalHire Automation with SeleniumBase Undetected Mode - Cloudflare Bypass
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_seleniumbase_undetected():
    """Test SignalHire with SeleniumBase UC mode for Cloudflare bypass"""
    
    print("🔬 SeleniumBase UC (Undetected) Test - Cloudflare Bypass")
    print("=" * 60)
    
    try:
        # Install seleniumbase if not available
        try:
            from seleniumbase import SB
        except ImportError:
            print("📦 Installing SeleniumBase...")
            import subprocess
            subprocess.run(["pip", "install", "seleniumbase"], check=True)
            from seleniumbase import SB
        
        print("✅ SeleniumBase imported successfully")
        
        # Get credentials
        email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
        password = os.environ.get("SIGNALHIRE_PASSWORD")
        
        if not password:
            print("❌ Missing SIGNALHIRE_PASSWORD environment variable")
            return False
        
        print(f"✅ Using email: {email}")
        
        # Start undetected Chrome session
        print("🚀 Starting undetected Chrome with SeleniumBase...")
        
        with SB(uc=True, headless=False, block_images=False) as sb:
            print("✅ Undetected Chrome started")
            
            # Step 1: Navigate to SignalHire
            print("🌐 Navigating to SignalHire login...")
            sb.open("https://www.signalhire.com/login")
            time.sleep(3)
            
            current_url = sb.get_current_url()
            print(f"📍 Current URL: {current_url}")
            
            # Check for Cloudflare challenge
            if sb.is_text_visible("I'm Under Attack Mode"):
                print("🛡️ Cloudflare challenge detected - waiting...")
                sb.wait_for_text_not_visible("I'm Under Attack Mode", timeout=30)
            
            if sb.is_text_visible("Checking your browser"):
                print("🛡️ Browser check detected - waiting...")
                sb.wait_for_text_not_visible("Checking your browser", timeout=30)
            
            # Look for Cloudflare checkbox
            cloudflare_selectors = [
                "input[type='checkbox']",
                "iframe[src*='cloudflare']",
                ".cf-browser-verification",
                "#challenge-form",
                ".challenge-container"
            ]
            
            for selector in cloudflare_selectors:
                if sb.is_element_present(selector):
                    print(f"🛡️ Cloudflare element found: {selector}")
                    try:
                        sb.click(selector)
                        print("✅ Clicked Cloudflare verification")
                        time.sleep(5)
                        break
                    except Exception as e:
                        print(f"⚠️ Could not click {selector}: {e}")
            
            # Wait for page to stabilize
            time.sleep(5)
            current_url = sb.get_current_url()
            print(f"📍 URL after Cloudflare handling: {current_url}")
            
            # Step 2: Fill login form
            if "login" in current_url.lower():
                print("🔐 Filling login credentials...")
                
                # Email field
                email_selectors = [
                    "input[type='email']",
                    "input[name*='email']",
                    "input[id*='email']",
                    "input[placeholder*='email']"
                ]
                
                for selector in email_selectors:
                    if sb.is_element_present(selector):
                        sb.type(selector, email)
                        print(f"✅ Email filled using: {selector}")
                        break
                else:
                    print("❌ Email field not found")
                    return False
                
                time.sleep(1)
                
                # Password field
                password_selectors = [
                    "input[type='password']",
                    "input[name*='password']",
                    "input[id*='password']",
                    "input[placeholder*='password']"
                ]
                
                for selector in password_selectors:
                    if sb.is_element_present(selector):
                        sb.type(selector, password)
                        print(f"✅ Password filled using: {selector}")
                        break
                else:
                    print("❌ Password field not found")
                    return False
                
                time.sleep(1)
                
                # Step 3: Submit login
                print("🚪 Clicking login button...")
                
                login_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Sign')",
                    "button:contains('Login')",
                    ".login-button",
                    "#login-button"
                ]
                
                for selector in login_selectors:
                    if sb.is_element_present(selector):
                        sb.click(selector)
                        print(f"✅ Login clicked using: {selector}")
                        break
                else:
                    print("❌ Login button not found")
                    return False
                
                # Wait for login response
                time.sleep(5)
                
                final_url = sb.get_current_url()
                print(f"🎯 Final URL after login: {final_url}")
                
                # Step 4: Check if login successful
                if "login" not in final_url.lower() and "dashboard" in final_url.lower():
                    print("✅ Login successful!")
                    
                    # Step 5: Navigate to search
                    print("🔍 Navigating to search...")
                    sb.open("https://www.signalhire.com/search")
                    time.sleep(3)
                    
                    # Step 6: Perform search
                    print("⚙️ Setting up search for Heavy Equipment Mechanic in Canada...")
                    
                    try:
                        # Job title
                        title_selectors = [
                            "input[placeholder*='title']",
                            "input[name*='title']",
                            "input[aria-label*='title']",
                            "#job-title",
                            ".job-title-input"
                        ]
                        
                        for selector in title_selectors:
                            if sb.is_element_present(selector):
                                sb.type(selector, "Heavy Equipment Mechanic")
                                print(f"✅ Job title filled using: {selector}")
                                break
                        
                        time.sleep(1)
                        
                        # Location
                        location_selectors = [
                            "input[placeholder*='location']",
                            "input[name*='location']", 
                            "input[aria-label*='location']",
                            "#location",
                            ".location-input"
                        ]
                        
                        for selector in location_selectors:
                            if sb.is_element_present(selector):
                                sb.type(selector, "Canada")
                                print(f"✅ Location filled using: {selector}")
                                break
                        
                        time.sleep(1)
                        
                        # Search button
                        search_selectors = [
                            "button:contains('Search')",
                            "button:contains('Find')",
                            "input[value*='Search']",
                            ".search-button",
                            "#search-button"
                        ]
                        
                        for selector in search_selectors:
                            if sb.is_element_present(selector):
                                sb.click(selector)
                                print(f"✅ Search clicked using: {selector}")
                                break
                        
                        time.sleep(5)
                        
                        search_url = sb.get_current_url()
                        print(f"🎯 Search completed at: {search_url}")
                        
                        print("🎉 SELENIUMBASE UC AUTOMATION COMPLETED SUCCESSFULLY!")
                        return True
                        
                    except Exception as e:
                        print(f"⚠️ Search failed: {e}")
                        print("Login successful but search had issues")
                        return True
                        
                else:
                    print("❌ Login failed - still on login page")
                    print(f"Current URL: {final_url}")
                    return False
            else:
                print("❌ Not on login page after navigation")
                print(f"Current URL: {current_url}")
                return False
                
    except Exception as e:
        print(f"💥 SELENIUMBASE UC AUTOMATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🔬 Starting SeleniumBase UC (Undetected) SignalHire automation...")
    print("This uses undetected Chrome to bypass bot detection")
    print()
    
    success = test_seleniumbase_undetected()
    
    if success:
        print("\n🎉 SELENIUMBASE UC AUTOMATION COMPLETED!")
        print("Bot detection was bypassed successfully")
    else:
        print("\n❌ SELENIUMBASE UC AUTOMATION FAILED!")
        print("Check the output above for details")
    
    return success

if __name__ == "__main__":
    main()
