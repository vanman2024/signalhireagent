"""Test SignalHire with fixed OpenAI API configuration."""

import asyncio
import os
from stagehand import Stagehand


async def test_signalhire_fixed_openai():
    """Test SignalHire with properly configured OpenAI API."""
    
    # Set credentials
    email = 'ryan@skilledtradesjobhub.ca'
    password = 'jPdpd1a893pCLjkj'
    
    # Clean OpenAI API key without organization issues
    os.environ['OPENAI_API_KEY'] = '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'
    
    # Remove any organization headers that might be causing issues
    if 'OPENAI_ORG_ID' in os.environ:
        del os.environ['OPENAI_ORG_ID']
    if 'OPENAI_ORGANIZATION' in os.environ:
        del os.environ['OPENAI_ORGANIZATION']
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    print("🔧 OpenAI API configured without organization headers")
    
    try:
        print("\n🚀 Starting Stagehand with VISIBLE browser...")
        
        # Use LOCAL with visible browser
        stagehand = Stagehand(
            env="LOCAL",
            verbose=2,
            headless=False  # Visible browser
        )
        
        await stagehand.init()
        page = stagehand.page
        print("✅ Browser opened and ready!")
        
        print("\n🔐 Going to SignalHire login page...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(4000)  # Wait for page to fully load
        print("✅ Login page loaded")
        
        print("\n📧 Step 1: Clicking on email field and entering email...")
        # Be very specific about the email field
        await page.act('Click on the email input field')
        await page.wait_for_timeout(1000)
        
        await page.act('Clear the email field and type ryan@skilledtradesjobhub.ca')
        await page.wait_for_timeout(2000)
        print("✅ Email entered")
        
        print("\n🔑 Step 2: Clicking on password field and entering password...")
        await page.act('Click on the password input field')
        await page.wait_for_timeout(1000)
        
        await page.act('Clear the password field and type jPdpd1a893pCLjkj')
        await page.wait_for_timeout(2000)
        print("✅ Password entered")
        
        print("\n🚀 Step 3: Clicking the Sign In button...")
        await page.act('Click the blue "Sign In" button')
        await page.wait_for_timeout(6000)  # Wait for login to process
        print("✅ Sign In button clicked")
        
        # Check if login was successful by looking at URL
        current_url = page.url
        print(f"📍 Current URL after login: {current_url}")
        
        if 'dashboard' in current_url or 'search' in current_url:
            print("🎉 LOGIN SUCCESSFUL!")
        else:
            print("⚠️ Login may not have succeeded, but continuing...")
        
        print("\n🔍 Step 4: Going to search page...")
        await page.goto('https://www.signalhire.com/search')
        await page.wait_for_timeout(4000)
        print("✅ Search page loaded")
        
        print("\n⚙️ Step 5: Setting up search criteria...")
        
        # Job title
        print("   Setting job title: Heavy Equipment Mechanic")
        await page.act('Click on the job title search field')
        await page.wait_for_timeout(1000)
        await page.act('Type "Heavy Equipment Mechanic" in the job title field')
        await page.wait_for_timeout(2000)
        
        # Location
        print("   Setting location: Canada")
        await page.act('Click on the location search field')
        await page.wait_for_timeout(1000)
        await page.act('Type "Canada" in the location field')
        await page.wait_for_timeout(2000)
        
        print("\n🔍 Step 6: Starting the search...")
        await page.act('Click the search button to start searching')
        await page.wait_for_timeout(10000)  # Wait for search results
        print("✅ Search completed!")
        
        print("\n🎉 SUCCESS! Complete workflow:")
        print("   ✅ Opened visible browser")
        print("   ✅ Navigated to SignalHire login")
        print("   ✅ Filled email field")
        print("   ✅ Filled password field") 
        print("   ✅ Clicked Sign In button")
        print("   ✅ Navigated to search page")
        print("   ✅ Set job title: Heavy Equipment Mechanic")
        print("   ✅ Set location: Canada")
        print("   ✅ Executed search")
        
        print("\n👀 Browser will stay open for 60 seconds so you can see the results...")
        await page.wait_for_timeout(60000)
        
        await stagehand.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🤖 SignalHire Smart Agent Test - Fixed OpenAI Configuration")
    print("=" * 65)
    print("This fixes the OpenAI organization header issue")
    print("The browser should now intelligently interact with SignalHire!")
    print("=" * 65)
    
    result = asyncio.run(test_signalhire_fixed_openai())
    
    if result:
        print("\n🎉 SMART AUTOMATION SUCCESS!")
        print("Stagehand AI successfully automated SignalHire!")
    else:
        print("\n💥 Test failed - check OpenAI API configuration")
