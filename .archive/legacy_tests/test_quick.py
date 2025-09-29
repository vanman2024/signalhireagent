"""Simple test with manual environment loading to fix env issues."""

import asyncio
import os
from stagehand import Stagehand


# Manually set environment variables from your .env file
os.environ['SIGNALHIRE_EMAIL'] = 'ryan@skilledtradesjobhub.ca'
os.environ['SIGNALHIRE_PASSWORD'] = 'jPdpd1a893pCLjkj'
os.environ['OPENAI_API_KEY'] = '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'


async def test_signalhire_quick():
    """Quick test of SignalHire automation with manual credentials."""
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)}")
    
    try:
        print("\n🚀 Opening browser for SignalHire test...")
        
        # Use LOCAL environment with visible browser
        stagehand = Stagehand(
            env="LOCAL",
            verbose=1,
            headless=False  # Visible browser
        )
        
        await stagehand.init()
        page = stagehand.page
        
        print("🔐 Going to SignalHire login...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(3000)
        
        print("📧 Filling email...")
        await page.act(f'Fill in the email field with "{email}"')
        await page.wait_for_timeout(1000)
        
        print("🔑 Filling password...")
        await page.act(f'Fill in the password field with "{password}"')
        await page.wait_for_timeout(1000)
        
        print("🚀 Clicking login...")
        await page.act('Click the login button or sign in button')
        await page.wait_for_timeout(5000)
        
        print("✅ Login completed! Check the browser window.")
        
        print("\n🔍 Navigating to search...")
        await page.goto('https://www.signalhire.com/search')
        await page.wait_for_timeout(3000)
        
        print("⚙️ Setting up search for Heavy Equipment Mechanic in Canada...")
        await page.act('Fill in the job title field with "Heavy Equipment Mechanic"')
        await page.wait_for_timeout(2000)
        
        await page.act('Fill in the location field with "Canada"')
        await page.wait_for_timeout(2000)
        
        print("🔍 Starting search...")
        await page.act('Click the search button')
        await page.wait_for_timeout(8000)
        
        print("🎉 SUCCESS! Check the browser - you should see Heavy Equipment Mechanic results in Canada!")
        print("Keeping browser open for 60 seconds so you can see the results...")
        
        await page.wait_for_timeout(60000)  # Keep open for 1 minute
        
        await stagehand.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 SignalHire Quick Test - Heavy Equipment Mechanic in Canada")
    print("=" * 65)
    
    result = asyncio.run(test_signalhire_quick())
    
    if result:
        print("\n🎉 SUCCESS! The automation worked!")
    else:
        print("\n💥 Failed!")
