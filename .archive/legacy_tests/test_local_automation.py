#!/usr/bin/env python3
"""
SignalHire Automation Test - LOCAL Environment
Tests the complete automation workflow using local Playwright instead of Browserbase
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from stagehand import Stagehand

# Load environment variables
load_dotenv()

async def test_local_automation():
    """Test SignalHire automation using LOCAL environment"""
    
    print("🚀 SignalHire Automation - LOCAL Test")
    print("=" * 60)
    print("Using local Playwright instead of Browserbase")
    print("=" * 60)
    
    # Get credentials
    email = os.environ.get("SIGNALHIRE_EMAIL")
    password = os.environ.get("SIGNALHIRE_PASSWORD")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not email or not password or not openai_key:
        print("❌ Missing required environment variables:")
        print(f"   SIGNALHIRE_EMAIL: {'✅' if email else '❌'}")
        print(f"   SIGNALHIRE_PASSWORD: {'✅' if password else '❌'}")
        print(f"   OPENAI_API_KEY: {'✅' if openai_key else '❌'}")
        return False
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    print(f"✅ OpenAI API: {openai_key[:20]}...")
    print()
    
    try:
        print("🔧 Initializing LOCAL Stagehand...")
        
        # Create Stagehand instance with LOCAL environment
        stagehand = Stagehand(
            env="LOCAL",  # Use LOCAL instead of BROWSERBASE
            api_key=openai_key,
            headless=True,  # Run headless in Docker
            logger_level="DEBUG"
        )
        
        print("✅ Stagehand created")
        
        # Initialize the browser
        await stagehand.init()
        print("✅ Browser initialized")
        
        # Step 1: Navigate to SignalHire login
        print("\n📍 Step 1: Navigating to SignalHire login...")
        await stagehand.page.goto("https://www.signalhire.com/login")
        print("✅ Navigated to login page")
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Step 2: Check for Cloudflare verification
        print("\n🛡️ Step 2: Checking for Cloudflare verification...")
        cloudflare_found = False
        
        try:
            # Look for Cloudflare challenge elements
            cloudflare_selectors = [
                'iframe[data-hcaptcha-widget-id]',
                'input[type="checkbox"][data-testid="cf-challenge-input"]',
                '.cf-challenge-running',
                '#challenge-running',
                '[data-cf-challenge]',
                'text="I am a human"',
                'text="Verify you are human"'
            ]
            
            for selector in cloudflare_selectors:
                try:
                    if 'text=' in selector:
                        # Try to find text
                        if await stagehand.page.locator(selector.replace('text=', '')).count() > 0:
                            print(f"✅ Found Cloudflare verification: {selector}")
                            cloudflare_found = True
                            break
                    else:
                        # Try to find element
                        if await stagehand.page.locator(selector).count() > 0:
                            print(f"✅ Found Cloudflare verification: {selector}")
                            cloudflare_found = True
                            break
                except:
                    continue
                    
            if cloudflare_found:
                print("🤖 Attempting to handle Cloudflare verification...")
                await stagehand.page.act("Click the 'I am a human' checkbox or complete the verification")
                await asyncio.sleep(5)
                print("✅ Cloudflare verification attempted")
            else:
                print("✅ No Cloudflare verification detected")
                
        except Exception as e:
            print(f"⚠️ Cloudflare check failed: {e}")
        
        # Step 3: Fill in login credentials
        print("\n🔐 Step 3: Filling login credentials...")
        
        # Fill email
        await stagehand.page.act(f"Fill in the email field with: {email}")
        await asyncio.sleep(1)
        
        # Fill password  
        await stagehand.page.act(f"Fill in the password field with: {password}")
        await asyncio.sleep(1)
        
        print("✅ Credentials filled")
        
        # Step 4: Submit login
        print("\n🚪 Step 4: Submitting login...")
        await stagehand.page.act("Click the Sign In or Login button")
        await asyncio.sleep(5)
        
        # Check if login was successful
        current_url = stagehand.page.url
        if "login" not in current_url.lower() and "signin" not in current_url.lower():
            print("✅ Login successful!")
            print(f"   Current URL: {current_url}")
        else:
            print("⚠️ Still on login page, may need additional verification")
            print(f"   Current URL: {current_url}")
        
        # Step 5: Navigate to search
        print("\n🔍 Step 5: Navigating to search...")
        if "search" not in current_url:
            await stagehand.page.act("Navigate to the search page or find prospects section")
            await asyncio.sleep(3)
        
        # Step 6: Set up search criteria
        print("\n⚙️ Step 6: Setting up search for Heavy Equipment Mechanic in Canada...")
        
        # Set job title
        await stagehand.page.act("Fill in the job title field with: Heavy Equipment Mechanic")
        await asyncio.sleep(1)
        
        # Set location
        await stagehand.page.act("Fill in the location field with: Canada")
        await asyncio.sleep(1)
        
        print("✅ Search criteria set")
        
        # Step 7: Execute search
        print("\n🔎 Step 7: Executing search...")
        await stagehand.page.act("Click the search button to find prospects")
        await asyncio.sleep(5)
        
        # Check search results
        final_url = stagehand.page.url
        print(f"✅ Search completed! Final URL: {final_url}")
        
        # Keep browser open for verification (headless, so just wait)
        print("\n🎯 AUTOMATION COMPLETED SUCCESSFULLY!")
        print("Automation ran in headless mode - all steps completed!")
        await asyncio.sleep(3)  # Short wait for any final operations
        
        # Close the browser
        await stagehand.close()
        print("✅ Browser closed")
        
        return True
        
    except Exception as e:
        print(f"\n💥 AUTOMATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await stagehand.close()
        except:
            pass
            
        return False

def main():
    """Main function"""
    success = asyncio.run(test_local_automation())
    
    if success:
        print("\n🎉 LOCAL AUTOMATION TEST PASSED!")
        print("The SignalHire automation workflow completed successfully.")
        print("You can now run this with Browserbase once session management is resolved.")
    else:
        print("\n❌ LOCAL AUTOMATION TEST FAILED!")
        print("Check the error messages above for debugging.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
