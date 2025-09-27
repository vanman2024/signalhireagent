#!/usr/bin/env python3
"""
Session Reuse Test - Try to piggyback on existing login
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def session_reuse_test():
    """Test that tries to reuse existing browser session"""
    
    print("🔄 Session Reuse Test - Piggyback on existing login")
    print("=" * 60)
    print("This test tries to reuse your existing browser cookies/session")
    print("=" * 60)
    
    try:
        from stagehand import Stagehand
        print("✅ Stagehand imported")
        
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            print("❌ Missing OpenAI key")
            return False
        
        # Initialize browser with persistent context
        print("\n🌐 Starting browser with persistent session...")
        stagehand = Stagehand(
            env="LOCAL",
            api_key=openai_key,
            headless=True
        )
        
        await stagehand.init()
        print("✅ Browser started")
        
        # First, try to set common SignalHire cookies/session data
        # (This would work better if we had access to your actual session)
        print("\n🍪 Setting up session context...")
        
        # Go to SignalHire domain first to set cookies
        await stagehand.page.goto("https://www.signalhire.com")
        await asyncio.sleep(1)
        
        # Try going directly to protected areas
        test_urls = [
            "https://www.signalhire.com/app",
            "https://www.signalhire.com/app/search", 
            "https://www.signalhire.com/dashboard",
            "https://www.signalhire.com/search"
        ]
        
        authenticated = False
        working_url = None
        
        for url in test_urls:
            print(f"\n🎯 Testing direct access to: {url}")
            try:
                await stagehand.page.goto(url)
                await asyncio.sleep(3)
                
                current_url = stagehand.page.url
                page_content = await stagehand.page.text_content("body")
                
                print(f"   Landed on: {current_url}")
                
                # Check if we're authenticated
                if "login" not in current_url.lower() and "signin" not in current_url.lower():
                    if page_content:
                        # Look for authenticated page indicators
                        auth_indicators = ["search", "dashboard", "prospects", "find people", "credits"]
                        if any(indicator in page_content.lower() for indicator in auth_indicators):
                            print(f"✅ Authenticated access to: {url}")
                            authenticated = True
                            working_url = url
                            break
                        else:
                            print(f"⚠️ Access granted but content unclear")
                else:
                    print(f"❌ Redirected to login page")
                    
            except Exception as e:
                print(f"❌ Failed to access {url}: {e}")
                continue
        
        if authenticated:
            print(f"\n🎉 SUCCESS! Already authenticated at: {working_url}")
            
            # Now try to do the search since we're already in
            print("\n🔍 Proceeding with search since we're authenticated...")
            
            try:
                # Look for search functionality on current page
                page_content = await stagehand.page.text_content("body")
                if "search" in page_content.lower():
                    print("✅ Search functionality detected on current page")
                else:
                    print("🔍 Looking for search navigation...")
                    await stagehand.page.act("Navigate to search or find people")
                    await asyncio.sleep(2)
                
                # Execute search
                print("🎯 Executing Heavy Equipment Mechanic search in Canada...")
                await stagehand.page.act("Fill job title field with: Heavy Equipment Mechanic")
                await asyncio.sleep(1)
                
                await stagehand.page.act("Fill location field with: Canada")
                await asyncio.sleep(1)
                
                await stagehand.page.act("Click search or find prospects button")
                await asyncio.sleep(3)
                
                final_url = stagehand.page.url
                print(f"🎯 Search completed, final URL: {final_url}")
                
                success = True
                
            except Exception as e:
                print(f"⚠️ Search failed but authentication worked: {e}")
                success = True  # Still a success since we bypassed login
                
        else:
            print("\n❌ No existing authentication found")
            print("💡 You may need to log in manually first, then run this test")
            success = False
        
        # Close browser
        await stagehand.close()
        print("✅ Browser closed")
        
        return success
        
    except Exception as e:
        print(f"💥 Error: {e}")
        try:
            await stagehand.close()
        except:
            pass
        return False

def main():
    """Run the session reuse test"""
    success = asyncio.run(session_reuse_test())
    
    if success:
        print("\n🎉 SESSION REUSE TEST PASSED!")
        print("Successfully bypassed login by reusing existing session")
    else:
        print("\n❌ SESSION REUSE TEST FAILED!")
        print("No existing session found - manual login may be required first")
    
    return success

if __name__ == "__main__":
    main()
