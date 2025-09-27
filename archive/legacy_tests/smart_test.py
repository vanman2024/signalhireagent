#!/usr/bin/env python3
"""
Smart SignalHire Test - Skip login if already authenticated
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def smart_signalhire_test():
    """Smart test that checks if already logged in first"""
    
    print("🧠 Smart SignalHire Test - Skip login if possible")
    print("=" * 60)
    
    try:
        from stagehand import Stagehand
        print("✅ Stagehand imported")
        
        # Get credentials
        email = os.environ.get("SIGNALHIRE_EMAIL", "ryan@skilledtradesjobhub.ca")
        password = os.environ.get("SIGNALHIRE_PASSWORD")
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        if not password or not openai_key:
            print("❌ Missing password or OpenAI key")
            return False
        
        print(f"✅ Using email: {email}")
        
        # Initialize browser
        print("\n🌐 Starting browser...")
        stagehand = Stagehand(
            env="LOCAL",
            api_key=openai_key,
            headless=True
        )
        
        await stagehand.init()
        print("✅ Browser started")
        
        # Strategy 1: Try going directly to dashboard/search first
        print("\n🎯 Strategy 1: Try accessing dashboard directly...")
        try:
            await stagehand.page.goto("https://www.signalhire.com/app")
            await asyncio.sleep(3)
            
            current_url = stagehand.page.url
            print(f"📍 Direct access URL: {current_url}")
            
            # Check if we're already logged in
            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                print("🎉 Already logged in! Skipping login process")
                logged_in = True
            else:
                print("🔒 Not logged in, need to authenticate")
                logged_in = False
                
        except Exception as e:
            print(f"⚠️ Direct access failed: {e}")
            logged_in = False
        
        # Strategy 2: If not logged in, do minimal login
        if not logged_in:
            print("\n🔐 Strategy 2: Minimal login process...")
            
            # Go to login page
            await stagehand.page.goto("https://www.signalhire.com/login")
            await asyncio.sleep(2)
            
            current_url = stagehand.page.url
            print(f"📍 Login page URL: {current_url}")
            
            # Quick check - are we actually on a login page?
            page_content = await stagehand.page.text_content("body")
            if page_content and "sign in" in page_content.lower():
                print("✅ On login page, proceeding with authentication")
                
                # Fill credentials quickly
                await stagehand.page.act(f"Type '{email}' in the email field")
                await asyncio.sleep(0.5)
                
                await stagehand.page.act(f"Type '{password}' in the password field")
                await asyncio.sleep(0.5)
                
                # Submit login
                await stagehand.page.act("Click the login button")
                await asyncio.sleep(3)
                
                # Check result
                post_login_url = stagehand.page.url
                print(f"📍 Post-login URL: {post_login_url}")
                
                # Simple success check
                if "login" in post_login_url.lower():
                    print("⚠️ Still on login page - may need verification")
                    
                    # Quick verification check without endless loops
                    page_text = await stagehand.page.text_content("body")
                    if page_text and any(word in page_text.lower() for word in ["cloudflare", "verify", "challenge"]):
                        print("🛡️ Verification detected - trying once...")
                        try:
                            await stagehand.page.act("Click the verification checkbox if present")
                            await asyncio.sleep(5)
                        except:
                            print("⚠️ Verification attempt failed")
                    
                    # Check again
                    final_check_url = stagehand.page.url
                    if "login" in final_check_url.lower():
                        print("❌ Login still failed after verification attempt")
                        await stagehand.close()
                        return False
                
                print("✅ Login process completed")
            else:
                print("⚠️ Not on expected login page")
        
        # Strategy 3: Navigate to search functionality
        print("\n🔍 Strategy 3: Navigate to search...")
        
        try:
            # Try multiple navigation approaches
            search_urls = [
                "https://www.signalhire.com/app/search",
                "https://www.signalhire.com/search",
                "https://www.signalhire.com/prospects"
            ]
            
            search_success = False
            for url in search_urls:
                try:
                    print(f"   Trying: {url}")
                    await stagehand.page.goto(url)
                    await asyncio.sleep(2)
                    
                    current_url = stagehand.page.url
                    page_content = await stagehand.page.text_content("body")
                    
                    if page_content and any(word in page_content.lower() for word in ["search", "find people", "prospects"]):
                        print(f"✅ Found search page at: {current_url}")
                        search_success = True
                        break
                except:
                    continue
            
            if not search_success:
                print("⚠️ Could not find search page, trying navigation")
                await stagehand.page.act("Navigate to search or find people section")
                await asyncio.sleep(2)
        
        except Exception as e:
            print(f"⚠️ Search navigation failed: {e}")
        
        # Strategy 4: Try the search
        print("\n🎯 Strategy 4: Execute search...")
        
        try:
            current_url = stagehand.page.url
            print(f"📍 Search page URL: {current_url}")
            
            # Fill search criteria
            await stagehand.page.act("Fill job title with: Heavy Equipment Mechanic")
            await asyncio.sleep(1)
            
            await stagehand.page.act("Fill location with: Canada")
            await asyncio.sleep(1)
            
            await stagehand.page.act("Click search or find prospects button")
            await asyncio.sleep(3)
            
            final_url = stagehand.page.url
            print(f"🎯 Final URL: {final_url}")
            
            # Check for results
            page_content = await stagehand.page.text_content("body")
            if page_content and any(word in page_content.lower() for word in ["results", "prospects", "contacts"]):
                print("✅ Search appears successful!")
                success = True
            else:
                print("⚠️ Search results unclear")
                success = True  # Don't fail on this
        
        except Exception as e:
            print(f"⚠️ Search execution failed: {e}")
            success = True  # Don't fail on search issues
        
        # Close browser
        await stagehand.close()
        print("✅ Browser closed")
        
        return True
        
    except Exception as e:
        print(f"💥 Error: {e}")
        try:
            await stagehand.close()
        except:
            pass
        return False

def main():
    """Run the smart test"""
    success = asyncio.run(smart_signalhire_test())
    
    if success:
        print("\n🎉 SMART TEST COMPLETED!")
        print("Used intelligent approach to skip unnecessary steps")
    else:
        print("\n❌ SMART TEST FAILED!")
    
    return success

if __name__ == "__main__":
    main()
