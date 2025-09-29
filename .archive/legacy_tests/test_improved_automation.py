#!/usr/bin/env python3
"""
SignalHire Automation Test - Improved with Screenshots and Better Detection
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from stagehand import Stagehand

# Load environment variables
load_dotenv()

async def take_screenshot(stagehand, step_name):
    """Take a screenshot for debugging"""
    try:
        # Save to host-accessible location
        screenshot_path = f"/home/vanman2025/signalhireagent/screenshots/{step_name}_{int(asyncio.get_event_loop().time())}.png"
        await stagehand.page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"⚠️ Screenshot failed: {e}")
        return None

async def check_page_content(stagehand, step_name):
    """Check page content for debugging"""
    try:
        url = stagehand.page.url
        title = await stagehand.page.title()
        
        # Get page text content
        page_text = await stagehand.page.text_content("body")
        
        print(f"\n🔍 Page Analysis - {step_name}:")
        print(f"   URL: {url}")
        print(f"   Title: {title}")
        print(f"   Content sample: {page_text[:200] if page_text else 'No content'}...")
        
        # Check for specific indicators
        indicators = {
            "cloudflare": ["cloudflare", "challenge", "checking your browser", "i am a human", "verify you are human"],
            "login_failed": ["invalid", "incorrect", "error", "try again", "login failed"],
            "logged_in": ["dashboard", "search", "prospects", "find people", "welcome"],
            "captcha": ["captcha", "recaptcha", "verify", "robot"]
        }
        
        page_lower = page_text.lower() if page_text else ""
        
        detected = []
        for category, keywords in indicators.items():
            if any(keyword in page_lower for keyword in keywords):
                detected.append(category)
        
        if detected:
            print(f"   Detected: {', '.join(detected)}")
        else:
            print("   No specific indicators detected")
            
        return {
            "url": url,
            "title": title,
            "content": page_text,
            "detected": detected
        }
        
    except Exception as e:
        print(f"⚠️ Page analysis failed: {e}")
        return None

async def handle_cloudflare_verification(stagehand):
    """Enhanced Cloudflare detection and handling"""
    print("🛡️ Enhanced Cloudflare verification check...")
    
    try:
        # Wait a bit for any dynamic content to load
        await asyncio.sleep(3)
        
        # Take screenshot first
        await take_screenshot(stagehand, "cloudflare_check")
        
        # Multiple detection methods
        cloudflare_detected = False
        
        # Method 1: Check page title
        title = await stagehand.page.title()
        if any(word in title.lower() for word in ["cloudflare", "challenge", "verify"]):
            print("✅ Cloudflare detected via page title")
            cloudflare_detected = True
        
        # Method 2: Check for common Cloudflare elements
        cloudflare_selectors = [
            'iframe[src*="cloudflare"]',
            'iframe[src*="challenges.cloudflare"]',
            '[data-cf-challenge]',
            '.cf-challenge-running',
            '#challenge-running',
            'input[name="cf_challenge"]',
            'div[class*="cloudflare"]'
        ]
        
        for selector in cloudflare_selectors:
            try:
                elements = await stagehand.page.locator(selector).count()
                if elements > 0:
                    print(f"✅ Cloudflare detected via selector: {selector}")
                    cloudflare_detected = True
                    break
            except:
                continue
        
        # Method 3: Check page content
        page_content = await stagehand.page.text_content("body")
        if page_content:
            cloudflare_keywords = [
                "checking your browser",
                "cloudflare",
                "i am a human",
                "verify you are human", 
                "challenge",
                "ray id"
            ]
            
            content_lower = page_content.lower()
            for keyword in cloudflare_keywords:
                if keyword in content_lower:
                    print(f"✅ Cloudflare detected via content: '{keyword}'")
                    cloudflare_detected = True
                    break
        
        if cloudflare_detected:
            print("🤖 Attempting to handle Cloudflare verification...")
            
            # Try multiple approaches
            verification_attempts = [
                "Click the 'I am a human' checkbox",
                "Complete the verification challenge",
                "Click the verification button",
                "Wait for verification to complete"
            ]
            
            for attempt in verification_attempts:
                try:
                    print(f"   Trying: {attempt}")
                    await stagehand.page.act(attempt)
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"   Failed: {e}")
                    continue
            
            # Wait for verification to complete
            print("⏳ Waiting for Cloudflare verification to complete...")
            await asyncio.sleep(10)
            
            # Take screenshot after verification attempt
            await take_screenshot(stagehand, "after_cloudflare")
            
            return True
        else:
            print("✅ No Cloudflare verification detected")
            return False
            
    except Exception as e:
        print(f"❌ Cloudflare handling failed: {e}")
        return False

async def verify_login_success(stagehand):
    """Verify if login was actually successful"""
    print("🔍 Verifying login success...")
    
    current_url = stagehand.page.url
    print(f"   Current URL: {current_url}")
    
    # Take screenshot
    await take_screenshot(stagehand, "login_verification")
    
    # Check URL patterns that indicate success/failure
    success_patterns = ["dashboard", "search", "prospects", "home", "app"]
    failure_patterns = ["login", "signin", "auth", "challenge", "error"]
    
    url_lower = current_url.lower()
    
    # Check for success indicators
    if any(pattern in url_lower for pattern in success_patterns):
        print("✅ Login appears successful based on URL")
        return True
    
    # Check for failure indicators
    if any(pattern in url_lower for pattern in failure_patterns):
        print("❌ Login appears to have failed based on URL")
        return False
    
    # Check page content for indicators
    try:
        page_content = await stagehand.page.text_content("body")
        if page_content:
            content_lower = page_content.lower()
            
            success_keywords = ["welcome", "dashboard", "search prospects", "find people", "logout"]
            failure_keywords = ["login", "sign in", "invalid", "incorrect", "error"]
            
            success_found = any(keyword in content_lower for keyword in success_keywords)
            failure_found = any(keyword in content_lower for keyword in failure_keywords)
            
            if success_found and not failure_found:
                print("✅ Login appears successful based on page content")
                return True
            elif failure_found:
                print("❌ Login appears to have failed based on page content")
                return False
    except Exception as e:
        print(f"⚠️ Could not analyze page content: {e}")
    
    print("⚠️ Login status unclear - proceeding cautiously")
    return None

async def test_improved_automation():
    """Test SignalHire automation with improved detection"""
    
    print("🚀 SignalHire Automation - IMPROVED Test")
    print("=" * 60)
    print("Enhanced with screenshots, better detection, and error handling")
    print("=" * 60)
    
    # Get credentials
    email = os.environ.get("SIGNALHIRE_EMAIL")
    password = os.environ.get("SIGNALHIRE_PASSWORD")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not email or not password or not openai_key:
        print("❌ Missing required environment variables")
        return False
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    print()
    
    # Create screenshots directory
    os.makedirs("/home/vanman2025/signalhireagent/screenshots", exist_ok=True)
    
    try:
        print("🔧 Initializing Stagehand...")
        stagehand = Stagehand(
            env="LOCAL",
            api_key=openai_key,
            headless=True,
            logger_level="INFO"
        )
        
        await stagehand.init()
        print("✅ Browser initialized")
        
        # Step 1: Navigate to login
        print("\n📍 Step 1: Navigating to SignalHire login...")
        await stagehand.page.goto("https://www.signalhire.com/login")
        await asyncio.sleep(3)
        
        # Take initial screenshot
        await take_screenshot(stagehand, "01_initial_login_page")
        await check_page_content(stagehand, "Initial Login Page")
        
        # Step 2: Enhanced Cloudflare check
        print("\n🛡️ Step 2: Enhanced Cloudflare verification check...")
        cloudflare_handled = await handle_cloudflare_verification(stagehand)
        
        if cloudflare_handled:
            await check_page_content(stagehand, "After Cloudflare")
        
        # Step 3: Fill credentials
        print("\n🔐 Step 3: Filling login credentials...")
        
        try:
            await stagehand.page.act(f"Fill in the email field with: {email}")
            print("✅ Email filled")
            await asyncio.sleep(1)
            
            await stagehand.page.act(f"Fill in the password field with: {password}")
            print("✅ Password filled")
            await asyncio.sleep(1)
            
            # Take screenshot after filling
            await take_screenshot(stagehand, "02_credentials_filled")
            
        except Exception as e:
            print(f"❌ Failed to fill credentials: {e}")
            await take_screenshot(stagehand, "02_credential_fill_failed")
            return False
        
        # Step 4: Submit login
        print("\n🚪 Step 4: Submitting login...")
        try:
            await stagehand.page.act("Click the Sign In or Login button")
            print("✅ Login button clicked")
            
            # Wait for response
            await asyncio.sleep(5)
            
            # Take screenshot after login attempt
            await take_screenshot(stagehand, "03_after_login_attempt")
            
        except Exception as e:
            print(f"❌ Failed to click login button: {e}")
            await take_screenshot(stagehand, "03_login_click_failed")
            return False
        
        # Step 5: Verify login success
        print("\n🔍 Step 5: Verifying login success...")
        login_success = await verify_login_success(stagehand)
        
        if login_success is False:
            print("❌ Login verification failed - stopping automation")
            await check_page_content(stagehand, "Login Failed")
            
            # Check if we need additional verification
            current_url = stagehand.page.url
            if "login_check" in current_url or "challenge" in current_url:
                print("🛡️ Additional verification may be required...")
                await handle_cloudflare_verification(stagehand)
                
                # Re-verify after handling verification
                login_success = await verify_login_success(stagehand)
                
        if login_success is not True:
            print("❌ Cannot proceed without successful login")
            return False
        
        print("✅ Login verified successful!")
        
        # Step 6: Navigate to search
        print("\n🔍 Step 6: Navigating to search...")
        try:
            await stagehand.page.act("Navigate to the search page or find prospects section")
            await asyncio.sleep(3)
            await take_screenshot(stagehand, "04_search_page")
            
        except Exception as e:
            print(f"⚠️ Navigation to search failed: {e}")
            await take_screenshot(stagehand, "04_search_nav_failed")
        
        # Step 7: Set up search
        print("\n⚙️ Step 7: Setting up search for Heavy Equipment Mechanic in Canada...")
        
        try:
            await stagehand.page.act("Fill in the job title field with: Heavy Equipment Mechanic")
            await asyncio.sleep(1)
            print("✅ Job title filled")
            
            await stagehand.page.act("Fill in the location field with: Canada")
            await asyncio.sleep(1)
            print("✅ Location filled")
            
            await take_screenshot(stagehand, "05_search_criteria_filled")
            
        except Exception as e:
            print(f"⚠️ Failed to fill search criteria: {e}")
            await take_screenshot(stagehand, "05_search_fill_failed")
        
        # Step 8: Execute search
        print("\n🔎 Step 8: Executing search...")
        try:
            await stagehand.page.act("Click the search button to find prospects")
            await asyncio.sleep(5)
            
            await take_screenshot(stagehand, "06_search_results")
            await check_page_content(stagehand, "Search Results")
            
            print("✅ Search executed!")
            
        except Exception as e:
            print(f"⚠️ Search execution failed: {e}")
            await take_screenshot(stagehand, "06_search_failed")
        
        # Final status
        final_url = stagehand.page.url
        print(f"\n🎯 Final URL: {final_url}")
        
        await take_screenshot(stagehand, "07_final_state")
        
        await stagehand.close()
        print("✅ Browser closed")
        
        return True
        
    except Exception as e:
        print(f"\n💥 AUTOMATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await take_screenshot(stagehand, "99_error_state")
            await stagehand.close()
        except:
            pass
            
        return False

def main():
    """Main function"""
    success = asyncio.run(test_improved_automation())
    
    if success:
        print("\n🎉 IMPROVED AUTOMATION TEST COMPLETED!")
        print("Check the screenshots in /home/vanman2025/signalhireagent/screenshots/ for detailed analysis")
    else:
        print("\n❌ IMPROVED AUTOMATION TEST FAILED!")
        print("Check the screenshots and logs for debugging")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
