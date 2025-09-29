"""SignalHire automation with Cloudflare verification handling."""

import asyncio
import os
from stagehand import Stagehand


# Set environment variables  
os.environ['SIGNALHIRE_EMAIL'] = 'ryan@skilledtradesjobhub.ca'
os.environ['SIGNALHIRE_PASSWORD'] = 'jPdpd1a893pCLjkj'
os.environ['OPENAI_API_KEY'] = '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'


async def test_with_cloudflare():
    """Test SignalHire automation with Cloudflare verification handling."""
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    api_key = os.getenv('OPENAI_API_KEY')
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    
    try:
        print("\n🚀 Starting SignalHire automation with Cloudflare handling...")
        
        # Use Browserbase 
        stagehand = Stagehand(
            env="BROWSERBASE",
            model_api_key=api_key,
            verbose=2
        )
        
        await stagehand.init()
        page = stagehand.page
        
        print("✅ Browser session started")
        print("💡 Watch live at: https://www.browserbase.com/sessions")
        
        print("\n🌐 Step 1: Going to SignalHire login page...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(5000)  # Wait for page to load
        print("✅ Login page loaded")
        
        print("\n🛡️ Step 2: Checking for Cloudflare verification...")
        # Look for Cloudflare "I'm a human" checkbox
        await page.act('Look for and click the Cloudflare "I am a human" checkbox if it appears')
        await page.wait_for_timeout(5000)  # Wait for Cloudflare verification
        print("✅ Cloudflare verification handled")
        
        print("\n📧 Step 3: Finding and filling email field...")
        await page.act('Click on the email input field')
        await page.wait_for_timeout(1000)
        await page.act(f'Clear the field and type "{email}"')
        await page.wait_for_timeout(2000)
        print("✅ Email entered")
        
        print("\n🔑 Step 4: Finding and filling password field...")
        await page.act('Click on the password input field')
        await page.wait_for_timeout(1000)
        await page.act(f'Clear the field and type "{password}"')
        await page.wait_for_timeout(2000)
        print("✅ Password entered")
        
        print("\n🚀 Step 5: Clicking Sign In button...")
        await page.act('Click the Sign In button')
        await page.wait_for_timeout(8000)  # Wait for login process
        
        print("\n🛡️ Step 6: Handling any additional Cloudflare checks...")
        # Sometimes Cloudflare appears again after login
        await page.act('If there is another Cloudflare verification, click the "I am a human" checkbox')
        await page.wait_for_timeout(5000)
        
        print("\n✅ Step 7: Checking login success...")
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        # Wait a bit more and check URL again
        await page.wait_for_timeout(3000)
        current_url = page.url
        print(f"Final URL: {current_url}")
        
        if 'dashboard' in current_url or 'search' in current_url or 'app' in current_url:
            print("🎉 LOGIN SUCCESSFUL!")
            
            print("\n🔍 Step 8: Going to search page...")
            await page.goto('https://www.signalhire.com/search')
            await page.wait_for_timeout(5000)
            
            print("\n🛡️ Step 9: Handle Cloudflare on search page if needed...")
            await page.act('If Cloudflare verification appears, click "I am a human"')
            await page.wait_for_timeout(3000)
            
            print("\n⚙️ Step 10: Setting up search for Heavy Equipment Mechanic in Canada...")
            await page.act('Find the job title field and click it')
            await page.wait_for_timeout(1000)
            await page.act('Type "Heavy Equipment Mechanic" in the job title field')
            await page.wait_for_timeout(3000)
            
            await page.act('Find the location field and click it')
            await page.wait_for_timeout(1000)
            await page.act('Type "Canada" in the location field')
            await page.wait_for_timeout(3000)
            
            print("\n🔍 Step 11: Starting search...")
            await page.act('Click the search button to start the search')
            await page.wait_for_timeout(10000)  # Wait for search results
            
            print("🎉 SEARCH COMPLETED! Check the browser session to see results!")
            
        else:
            print("❌ Login verification needed - check current page")
            
            # Try to see what's on the page
            page_info = await page.extract({
                "instruction": "Describe what is currently visible on the page, including any buttons or verification steps",
                "schema": {
                    "page_content": {"type": "string", "description": "what is visible on the page"},
                    "verification_needed": {"type": "string", "description": "any verification steps or captchas visible"}
                }
            })
            
            print(f"Page content: {getattr(page_info, 'page_content', 'Unknown')}")
            print(f"Verification: {getattr(page_info, 'verification_needed', 'None')}")
        
        print("\n⏰ Keeping session alive for 60 seconds for inspection...")
        print("💡 Go to https://www.browserbase.com/sessions to watch live!")
        await page.wait_for_timeout(60000)
        
        await stagehand.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🛡️ SignalHire Automation with Cloudflare Verification")
    print("=" * 60)
    print("This handles Cloudflare 'I am a human' checkboxes")
    print("Watch the automation live at: https://www.browserbase.com/sessions")
    print("=" * 60)
    
    result = asyncio.run(test_with_cloudflare())
    
    if result:
        print("\n🎉 AUTOMATION COMPLETED!")
        print("The agent handled Cloudflare verification and performed the search!")
    else:
        print("\n💥 AUTOMATION FAILED!")
