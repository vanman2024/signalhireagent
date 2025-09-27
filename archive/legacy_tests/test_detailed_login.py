"""Debug SignalHire login - detailed step-by-step with clicks and typing."""

import asyncio
import os
from stagehand import Stagehand


# Set environment variables
os.environ['SIGNALHIRE_EMAIL'] = 'ryan@skilledtradesjobhub.ca'
os.environ['SIGNALHIRE_PASSWORD'] = 'jPdpd1a893pCLjkj'
os.environ['MODEL_API_KEY'] = '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'


async def test_detailed_login():
    """Test detailed login steps with clicks and typing."""
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    model_api_key = os.getenv('MODEL_API_KEY')
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    
    try:
        print("\n🚀 Starting detailed login test...")
        
        # Use Browserbase 
        stagehand = Stagehand(
            env="BROWSERBASE",
            model_api_key=model_api_key,
            verbose=2
        )
        
        await stagehand.init()
        page = stagehand.page
        
        print("✅ Browser session started")
        print("💡 Watch live at: https://www.browserbase.com/sessions")
        
        print("\n🌐 Step 1: Going to SignalHire login page...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(5000)  # Wait longer for page to fully load
        print("✅ Login page loaded")
        
        print("\n🔍 Step 2: Looking for login form elements...")
        # First let's see what's on the page
        await page.act('Take a screenshot of the current page')
        await page.wait_for_timeout(2000)
        
        print("\n📧 Step 3: Finding and clicking email field...")
        # Be more specific about finding the email field
        await page.act('Find and click on the email input field or username field')
        await page.wait_for_timeout(2000)
        
        print("\n⌨️ Step 4: Typing email address...")
        await page.act(f'Type "{email}" in the currently focused field')
        await page.wait_for_timeout(2000)
        
        print("\n🔑 Step 5: Finding and clicking password field...")
        await page.act('Find and click on the password input field')
        await page.wait_for_timeout(2000)
        
        print("\n⌨️ Step 6: Typing password...")
        await page.act(f'Type "{password}" in the currently focused field')
        await page.wait_for_timeout(2000)
        
        print("\n🚀 Step 7: Finding and clicking sign in button...")
        await page.act('Find and click the Sign In button or Login button')
        await page.wait_for_timeout(8000)  # Wait longer for login to process
        
        print("\n✅ Step 8: Checking if login was successful...")
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if 'dashboard' in current_url or 'search' in current_url or 'profile' in current_url:
            print("🎉 LOGIN SUCCESSFUL! We're logged in!")
            
            print("\n🔍 Step 9: Going to search page...")
            await page.goto('https://www.signalhire.com/search')
            await page.wait_for_timeout(4000)
            
            print("\n⚙️ Step 10: Setting up search...")
            await page.act('Click on the job title field and type "Heavy Equipment Mechanic"')
            await page.wait_for_timeout(3000)
            
            await page.act('Click on the location field and type "Canada"')
            await page.wait_for_timeout(3000)
            
            await page.act('Click the search button to start searching')
            await page.wait_for_timeout(10000)
            
            print("🎉 SEARCH COMPLETED!")
            
        else:
            print("❌ Login may have failed - not redirected to expected page")
            print("Let's try to see what's on the current page...")
            
            # Try to extract page content to see what happened
            page_content = await page.extract({
                "instruction": "Describe what's currently visible on the page",
                "schema": {
                    "page_description": {"type": "string", "description": "what is visible on the page"},
                    "any_errors": {"type": "string", "description": "any error messages visible"}
                }
            })
            
            print(f"Page content: {getattr(page_content, 'page_description', 'Unknown')}")
            print(f"Any errors: {getattr(page_content, 'any_errors', 'None')}")
        
        print("\n⏰ Keeping session alive for 30 seconds so you can inspect...")
        await page.wait_for_timeout(30000)
        
        await stagehand.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 SignalHire Detailed Login Debug Test")
    print("=" * 50)
    print("This will show detailed steps of login process")
    print("Watch live at: https://www.browserbase.com/sessions")
    print("=" * 50)
    
    result = asyncio.run(test_detailed_login())
    
    if result:
        print("\n🎉 TEST COMPLETED!")
    else:
        print("\n💥 TEST FAILED!")
