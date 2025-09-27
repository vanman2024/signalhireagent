#!/usr/bin/env python3
"""
SignalHire Automation with Undetected ChromeDriver - Cloudflare Bypass
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_undetected_chromedriver():
    """Test SignalHire with undetected-chromedriver for Cloudflare bypass"""
    
    print("🕵️ Undetected ChromeDriver Test - Cloudflare Bypass")
    print("=" * 60)
    
    try:
        # Install undetected-chromedriver if not available
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            print("📦 Installing undetected-chromedriver and selenium...")
            import subprocess
            subprocess.run(["pip", "install", "undetected-chromedriver", "selenium"], check=True)
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        
        print("✅ Undetected ChromeDriver imported successfully")
        
        # Get credentials
        email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
        password = os.environ.get("SIGNALHIRE_PASSWORD")
        
        if not password:
            print("❌ Missing SIGNALHIRE_PASSWORD environment variable")
            return False
        
        print(f"✅ Using email: {email}")
        
        # Configure undetected Chrome options
        options = uc.ChromeOptions()
        
        # Add stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Start undetected Chrome
        print("🚀 Starting undetected Chrome...")
        driver = uc.Chrome(options=options, version_main=None)
        
        try:
            # Execute script to hide webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Undetected Chrome started")
            
            # Step 1: Navigate to SignalHire
            print("🌐 Navigating to SignalHire login...")
            driver.get("https://www.signalhire.com/login")
            
            # Wait for initial page load
            wait = WebDriverWait(driver, 20)
            time.sleep(5)
            
            current_url = driver.current_url
            print(f"📍 Current URL: {current_url}")
            
            # Check for and handle Cloudflare challenges
            print("🛡️ Checking for Cloudflare challenges...")
            
            # Look for common Cloudflare indicators
            cloudflare_indicators = [
                "Checking your browser",
                "I'm Under Attack Mode", 
                "Just a moment",
                "DDoS protection",
                "Ray ID:",
                "Please wait while we verify",
                "Verify you are human"
            ]
            
            page_source = driver.page_source
            cloudflare_detected = any(indicator in page_source for indicator in cloudflare_indicators)
            
            if cloudflare_detected:
                print("🛡️ Cloudflare challenge detected - waiting for bypass...")
                
                # Wait for Cloudflare to resolve (undetected-chromedriver should handle this)
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    current_url = driver.current_url
                    page_source = driver.page_source
                    
                    # Check if still on Cloudflare
                    still_cloudflare = any(indicator in page_source for indicator in cloudflare_indicators)
                    
                    if not still_cloudflare and "login" in current_url.lower():
                        print(f"✅ Cloudflare bypassed after {i+1} seconds")
                        break
                    
                    if i % 5 == 0:
                        print(f"⏳ Still waiting for Cloudflare bypass... ({i+1}s)")
                else:
                    print("⚠️ Cloudflare bypass took longer than expected, proceeding anyway...")
            else:
                print("✅ No Cloudflare challenge detected")
            
            # Refresh current state
            time.sleep(2)
            current_url = driver.current_url
            print(f"📍 URL after Cloudflare handling: {current_url}")
            
            # Step 2: Fill login form
            if "login" in current_url.lower():
                print("🔐 Filling login credentials...")
                
                # Find and fill email
                email_selectors = [
                    "input[type='email']",
                    "input[name*='email']",
                    "input[id*='email']",
                    "input[placeholder*='email']"
                ]
                
                email_filled = False
                for selector in email_selectors:
                    try:
                        email_field = driver.find_element(By.CSS_SELECTOR, selector)
                        email_field.clear()
                        email_field.send_keys(email)
                        print(f"✅ Email filled using: {selector}")
                        email_filled = True
                        break
                    except:
                        continue
                
                if not email_filled:
                    print("❌ Email field not found")
                    return False
                
                time.sleep(1)
                
                # Find and fill password
                password_selectors = [
                    "input[type='password']",
                    "input[name*='password']",
                    "input[id*='password']",
                    "input[placeholder*='password']"
                ]
                
                password_filled = False
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, selector)
                        password_field.clear()
                        password_field.send_keys(password)
                        print(f"✅ Password filled using: {selector}")
                        password_filled = True
                        break
                    except:
                        continue
                
                if not password_filled:
                    print("❌ Password field not found")
                    return False
                
                time.sleep(1)
                
                # Step 3: Submit login
                print("🚪 Clicking login button...")
                
                login_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "//button[contains(text(), 'Sign')]",
                    "//button[contains(text(), 'Login')]",
                    ".login-button",
                    "#login-button"
                ]
                
                login_clicked = False
                for selector in login_selectors:
                    try:
                        if selector.startswith("//"):
                            login_button = driver.find_element(By.XPATH, selector)
                        else:
                            login_button = driver.find_element(By.CSS_SELECTOR, selector)
                        
                        login_button.click()
                        print(f"✅ Login clicked using: {selector}")
                        login_clicked = True
                        break
                    except:
                        continue
                
                if not login_clicked:
                    print("❌ Login button not found")
                    return False
                
                # Wait for login response
                time.sleep(10)
                
                final_url = driver.current_url
                print(f"🎯 Final URL after login: {final_url}")
                
                # Step 4: Check if login successful
                if "login" not in final_url.lower():
                    print("✅ Login appears successful!")
                    
                    # Step 5: Navigate to search
                    print("🔍 Navigating to search...")
                    driver.get("https://www.signalhire.com/search")
                    time.sleep(5)
                    
                    # Step 6: Perform search
                    print("⚙️ Setting up search for Heavy Equipment Mechanic in Canada...")
                    
                    try:
                        # Job title
                        title_selectors = [
                            "input[placeholder*='title']",
                            "input[name*='title']",
                            "input[aria-label*='title']"
                        ]
                        
                        for selector in title_selectors:
                            try:
                                title_field = driver.find_element(By.CSS_SELECTOR, selector)
                                title_field.clear()
                                title_field.send_keys("Heavy Equipment Mechanic")
                                print(f"✅ Job title filled using: {selector}")
                                break
                            except:
                                continue
                        
                        time.sleep(1)
                        
                        # Location
                        location_selectors = [
                            "input[placeholder*='location']", 
                            "input[name*='location']",
                            "input[aria-label*='location']"
                        ]
                        
                        for selector in location_selectors:
                            try:
                                location_field = driver.find_element(By.CSS_SELECTOR, selector)
                                location_field.clear()
                                location_field.send_keys("Canada")
                                print(f"✅ Location filled using: {selector}")
                                break
                            except:
                                continue
                        
                        time.sleep(1)
                        
                        # Search button
                        search_selectors = [
                            "//button[contains(text(), 'Search')]",
                            "//button[contains(text(), 'Find')]",
                            "input[value*='Search']"
                        ]
                        
                        for selector in search_selectors:
                            try:
                                if selector.startswith("//"):
                                    search_button = driver.find_element(By.XPATH, selector)
                                else:
                                    search_button = driver.find_element(By.CSS_SELECTOR, selector)
                                
                                search_button.click()
                                print(f"✅ Search clicked using: {selector}")
                                break
                            except:
                                continue
                        
                        time.sleep(10)
                        
                        search_url = driver.current_url
                        print(f"🎯 Search completed at: {search_url}")
                        
                        print("🎉 UNDETECTED CHROMEDRIVER AUTOMATION COMPLETED!")
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
                
        finally:
            # Keep browser open for inspection
            print("\n⏸️ Keeping browser open for 30 seconds for inspection...")
            time.sleep(30)
            driver.quit()
                
    except Exception as e:
        print(f"💥 UNDETECTED CHROMEDRIVER AUTOMATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🕵️ Starting Undetected ChromeDriver SignalHire automation...")
    print("This uses advanced stealth mode to bypass bot detection")
    print()
    
    success = test_undetected_chromedriver()
    
    if success:
        print("\n🎉 UNDETECTED CHROMEDRIVER AUTOMATION COMPLETED!")
        print("Bot detection was bypassed successfully")
    else:
        print("\n❌ UNDETECTED CHROMEDRIVER AUTOMATION FAILED!")
        print("Check the output above for details")
    
    return success

if __name__ == "__main__":
    main()
