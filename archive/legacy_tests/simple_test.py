#!/usr/bin/env python3
"""
Simple SignalHire Test - Just make it work!
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def simple_signalhire_test():
    """Dead simple test - no fancy stuff"""
    
    print("🚀 Simple SignalHire Test")
    print("=" * 40)
    
    try:
        # Import stagehand
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
        print(f"✅ Password: {'*' * 8}")
        
        # Initialize browser
        print("\n🌐 Starting browser...")
        stagehand = Stagehand(
            env="LOCAL",
            api_key=openai_key,
            headless=True
        )
        
        await stagehand.init()
        print("✅ Browser started")
        
        # Go to login page
        print("\n🔗 Going to login page...")
        await stagehand.page.goto("https://www.signalhire.com/login")
        await asyncio.sleep(3)
        
        current_url = stagehand.page.url
        print(f"✅ At: {current_url}")
        
        # Fill email
        print("\n📧 Filling email...")
        await stagehand.page.act(f"Type '{email}' in the email input field")
        await asyncio.sleep(1)
        print("✅ Email filled")
        
        # Fill password  
        print("\n🔒 Filling password...")
        await stagehand.page.act(f"Type '{password}' in the password input field")
        await asyncio.sleep(1)
        print("✅ Password filled")
        
        # Click login
        print("\n🚪 Clicking login...")
        await stagehand.page.act("Click the login button or sign in button")
        await asyncio.sleep(5)
        
        # Check where we are
        final_url = stagehand.page.url
        print(f"\n🎯 Final URL: {final_url}")
        
        # Simple success check
        if "login" in final_url.lower():
            print("❌ Still on login page - login failed")
            success = False
        else:
            print("✅ Redirected away from login - likely successful")
            success = True
        
        # Close browser
        await stagehand.close()
        print("✅ Browser closed")
        
        return success
        
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def main():
    """Run the simple test"""
    success = asyncio.run(simple_signalhire_test())
    
    if success:
        print("\n🎉 SIMPLE TEST PASSED!")
    else:
        print("\n❌ SIMPLE TEST FAILED!")
    
    return success

if __name__ == "__main__":
    main()
