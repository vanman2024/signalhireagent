"""Debug test to see exactly what's happening with SignalHire login fields."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from stagehand import Stagehand


async def debug_signalhire_login():
    """Debug SignalHire login to see what's happening with the form fields."""
    
    # Manually set credentials to avoid env issues
    email = "ryan@skilledtradesjobhub.ca"
    password = "jPdpd1a893pCLjkj"
    model_api_key = "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"
    browserbase_api_key = "bb_live_yo6BbY7HohjZxFIesSiOAL6Z4R0"
    browserbase_project_id = "6fda0deb-cff8-42ee-b361-3613d202e199"
    
    try:
        print("🚀 Starting SignalHire LOGIN DEBUG with Browserbase...")
        print("🎯 Goal: Fill email and password fields correctly")
        
        # Use Browserbase for reliable cloud browser
        stagehand = Stagehand(
            env="BROWSERBASE",
            model_api_key=model_api_key,
            verbose=2
        )
        
        print("🔧 Initializing browser...")
        await stagehand.init()
        print("✅ Browser initialized!")
        
        page = stagehand.page
        
        print("\n📱 Step 1: Navigate to SignalHire login...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(5000)  # Give page time to fully load
        print("✅ Login page loaded")
        
        print("\n🔍 Step 2: Observe the page to see what login elements are available...")
        observation = await page.observe()
        print("✅ Page observed - checking for login form elements")
        
        print("\n📝 Step 3: Try to fill email field with multiple approaches...")
        
        # Approach 1: Generic email field
        try:
            await page.act(f'Click on the email input field and type "{email}"')
            await page.wait_for_timeout(2000)
            print("✅ Approach 1: Email filled using generic 'email input field'")
        except Exception as e:
            print(f"❌ Approach 1 failed: {e}")
            
            # Approach 2: More specific
            try:
                await page.act(f'Find the email field or username field and enter "{email}"')
                await page.wait_for_timeout(2000)
                print("✅ Approach 2: Email filled using 'email or username field'")
            except Exception as e2:
                print(f"❌ Approach 2 failed: {e2}")
                
                # Approach 3: Even more specific
                try:
                    await page.act(f'Look for input field with placeholder "Email" or "Username" and click it, then type "{email}"')
                    await page.wait_for_timeout(2000)
                    print("✅ Approach 3: Email filled using placeholder-based search")
                except Exception as e3:
                    print(f"❌ Approach 3 failed: {e3}")
        
        print("\n🔐 Step 4: Try to fill password field with multiple approaches...")
        
        # Approach 1: Generic password field
        try:
            await page.act(f'Click on the password input field and type "{password}"')
            await page.wait_for_timeout(2000)
            print("✅ Approach 1: Password filled using generic 'password input field'")
        except Exception as e:
            print(f"❌ Approach 1 failed: {e}")
            
            # Approach 2: More specific
            try:
                await page.act(f'Find the password field and enter "{password}"')
                await page.wait_for_timeout(2000)
                print("✅ Approach 2: Password filled using 'password field'")
            except Exception as e2:
                print(f"❌ Approach 2 failed: {e2}")
                
                # Approach 3: Even more specific
                try:
                    await page.act(f'Look for input field with type "password" or placeholder "Password" and click it, then type "{password}"')
                    await page.wait_for_timeout(2000)
                    print("✅ Approach 3: Password filled using type/placeholder-based search")
                except Exception as e3:
                    print(f"❌ Approach 3 failed: {e3}")
        
        print("\n🔍 Step 5: Check if form fields were filled...")
        try:
            form_status = await page.extract({
                "instruction": "Check if the login form has been filled with email and password",
                "schema": {
                    "email_filled": {"type": "boolean", "description": "whether email field has content"},
                    "password_filled": {"type": "boolean", "description": "whether password field has content"},
                    "form_ready": {"type": "boolean", "description": "whether form is ready to submit"},
                    "visible_text": {"type": "string", "description": "any visible text or error messages"}
                }
            })
            
            print(f"📊 Form Status:")
            print(f"   Email filled: {getattr(form_status, 'email_filled', 'Unknown')}")
            print(f"   Password filled: {getattr(form_status, 'password_filled', 'Unknown')}")
            print(f"   Form ready: {getattr(form_status, 'form_ready', 'Unknown')}")
            print(f"   Visible text: {getattr(form_status, 'visible_text', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️ Could not extract form status: {e}")
        
        print("\n🎯 Step 6: Try to submit the login form...")
        try:
            await page.act('Click the login button or sign in button to submit the form')
            await page.wait_for_timeout(5000)
            print("✅ Login form submitted")
            
            # Check if login was successful
            current_url = page.url
            print(f"📍 Current URL after login attempt: {current_url}")
            
            if 'dashboard' in current_url or 'search' in current_url or 'app' in current_url:
                print("🎉 LOGIN SUCCESSFUL! Redirected to authenticated area")
            else:
                print("⚠️ Login may not have succeeded - still on login page")
                
        except Exception as e:
            print(f"❌ Login submission failed: {e}")
        
        print("\n⏰ Keeping session open for 10 seconds to see results...")
        await page.wait_for_timeout(10000)
        
        await stagehand.close()
        print("🔒 Browser session ended")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 SignalHire Login Debug Test")
    print("=" * 50)
    print("This will test multiple approaches to fill the login form")
    print("=" * 50)
    
    result = asyncio.run(debug_signalhire_login())
    
    if result:
        print("\n🎉 DEBUG TEST COMPLETED!")
    else:
        print("\n💥 DEBUG TEST FAILED!")
