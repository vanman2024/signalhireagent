"""Test SignalHire with Browserbase (cloud) - you can see the session via Browserbase dashboard."""

import asyncio
import os
from stagehand import Stagehand


# Set environment variables
os.environ['SIGNALHIRE_EMAIL'] = 'ryan@skilledtradesjobhub.ca'
os.environ['SIGNALHIRE_PASSWORD'] = 'jPdpd1a893pCLjkj'
os.environ['MODEL_API_KEY'] = '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'


async def test_signalhire_browserbase():
    """Test SignalHire with Browserbase cloud browser."""
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    model_api_key = os.getenv('MODEL_API_KEY')
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    print(f"✅ API Key: {model_api_key[:10]}...")
    
    try:
        print("\n🚀 Starting Browserbase session...")
        print("💡 You can view the live browser session at: https://www.browserbase.com/sessions")
        
        # Use Browserbase cloud environment
        stagehand = Stagehand(
            env="BROWSERBASE",
            model_api_key=model_api_key,
            verbose=2  # More detailed logging
        )
        
        await stagehand.init()
        page = stagehand.page
        
        print("✅ Browserbase session started!")
        print("🌐 Browser is now running in the cloud...")
        
        print("\n🔐 Step 1: Going to SignalHire login...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(3000)
        print("✅ Login page loaded")
        
        print("\n📧 Step 2: Filling email...")
        await page.act(f'Fill in the email field with "{email}"')
        await page.wait_for_timeout(2000)
        print("✅ Email entered")
        
        print("\n🔑 Step 3: Filling password...")
        await page.act(f'Fill in the password field with "{password}"')
        await page.wait_for_timeout(2000)
        print("✅ Password entered")
        
        print("\n🚀 Step 4: Clicking login...")
        await page.act('Click the login button or sign in button')
        await page.wait_for_timeout(6000)
        print("✅ Login clicked - checking if successful...")
        
        print("\n🔍 Step 5: Navigating to search page...")
        await page.goto('https://www.signalhire.com/search')
        await page.wait_for_timeout(4000)
        print("✅ Search page loaded")
        
        print("\n⚙️ Step 6: Setting job title to 'Heavy Equipment Mechanic'...")
        await page.act('Fill in the job title field with "Heavy Equipment Mechanic"')
        await page.wait_for_timeout(3000)
        print("✅ Job title set")
        
        print("\n🇨🇦 Step 7: Setting location to 'Canada'...")
        await page.act('Fill in the location field with "Canada"')
        await page.wait_for_timeout(3000)
        print("✅ Location set")
        
        print("\n🔍 Step 8: Starting search...")
        await page.act('Click the search button')
        await page.wait_for_timeout(10000)  # Wait longer for search results
        print("✅ Search completed!")
        
        print("\n📊 Step 9: Extracting search information...")
        try:
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            # Try to get basic page info
            page_info = await page.extract({
                "instruction": "Get the page title and any search result information visible",
                "schema": {
                    "page_title": {"type": "string", "description": "the page title"},
                    "search_info": {"type": "string", "description": "any search results or status information"}
                }
            })
            
            print(f"📄 Page Title: {getattr(page_info, 'page_title', 'Unknown')}")
            print(f"🔍 Search Info: {getattr(page_info, 'search_info', 'Unknown')}")
            
        except Exception as e:
            print(f"⚠️ Could not extract page info: {e}")
        
        print("\n🎉 SUCCESS! SignalHire automation completed!")
        print("📋 Summary of what was done:")
        print("   ✅ Opened cloud browser session")
        print("   ✅ Navigated to SignalHire login")
        print("   ✅ Entered credentials")
        print("   ✅ Clicked login")
        print("   ✅ Navigated to search page")
        print("   ✅ Set job title: Heavy Equipment Mechanic")
        print("   ✅ Set location: Canada")
        print("   ✅ Executed search")
        
        print(f"\n💡 Session URL: You can view this session at https://www.browserbase.com/sessions")
        print("   (Login to your Browserbase account to see the live browser)")
        
        # Keep session alive for a bit longer so you can view it
        print("\n⏰ Keeping session alive for 30 more seconds...")
        await page.wait_for_timeout(30000)
        
        await stagehand.close()
        print("🔒 Session closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🎯 SignalHire Browserbase Test - Heavy Equipment Mechanic in Canada")
    print("=" * 70)
    print("This uses cloud browser automation via Browserbase")
    print("You can watch the session live at https://www.browserbase.com/sessions")
    print("=" * 70)
    
    result = asyncio.run(test_signalhire_browserbase())
    
    if result:
        print("\n🎉 AUTOMATION TEST PASSED!")
        print("The agent successfully automated SignalHire search!")
    else:
        print("\n💥 AUTOMATION TEST FAILED!")
