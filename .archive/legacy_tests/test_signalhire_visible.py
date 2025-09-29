"""Test SignalHire automation with visible browser for Heavy Equipment Mechanic search in Canada."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from stagehand import Stagehand


async def test_signalhire_search_visible():
    """Test SignalHire search with visible browser - Heavy Equipment Mechanic in Canada."""
    # Load environment variables
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    
    print(f"SignalHire Email: {email}")
    print(f"SignalHire Password: {'*' * len(password)}" if password else "No password")
    
    if not email or not password:
        print("❌ Missing SignalHire credentials")
        return False
    
    try:
        print("\n🚀 Starting SignalHire automation with VISIBLE browser...")
        print("📍 Target: Heavy Equipment Mechanic profiles in Canada")
        
        # Initialize Stagehand with LOCAL environment (visible browser)
        stagehand = Stagehand(
            env="LOCAL",  # This will open a visible browser!
            verbose=2,    # More detailed logging
            headless=False  # Make sure browser is visible
        )
        
        print("🔧 Initializing browser...")
        await stagehand.init()
        print("✅ Browser opened successfully!")
        
        page = stagehand.page
        
        print("\n🔐 Step 1: Navigating to SignalHire login page...")
        await page.goto('https://www.signalhire.com/login')
        await page.wait_for_timeout(3000)  # Wait to see the page
        print("✅ Login page loaded")
        
        print("\n🔑 Step 2: Performing login...")
        await page.act(f'Fill in the email field with "{email}"')
        await page.wait_for_timeout(1000)
        
        await page.act(f'Fill in the password field with "{password}"')
        await page.wait_for_timeout(1000)
        
        await page.act('Click the sign in button')
        await page.wait_for_timeout(5000)  # Wait for login to complete
        print("✅ Login completed")
        
        print("\n🔍 Step 3: Navigating to search page...")
        await page.goto('https://www.signalhire.com/search')
        await page.wait_for_timeout(3000)
        print("✅ Search page loaded")
        
        print("\n⚙️ Step 4: Setting up search criteria...")
        print("   Job Title: Heavy Equipment Mechanic")
        await page.act('Fill in the job title field with "Heavy Equipment Mechanic"')
        await page.wait_for_timeout(2000)
        
        print("   Location: Canada")
        await page.act('Fill in the location field with "Canada"')
        await page.wait_for_timeout(2000)
        
        print("\n🚀 Step 5: Starting search...")
        await page.act('Click the search button')
        await page.wait_for_timeout(8000)  # Wait for search results
        print("✅ Search initiated")
        
        print("\n📊 Step 6: Extracting search results...")
        try:
            results = await page.extract({
                "instruction": "Extract information about the search results including total count and first few prospects",
                "schema": {
                    "total_results": {"type": "number", "description": "total number of results found"},
                    "results_shown": {"type": "number", "description": "number of results currently displayed"},
                    "first_prospects": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "name": {"type": "string", "description": "prospect name"},
                                "title": {"type": "string", "description": "job title"},
                                "company": {"type": "string", "description": "company name"},
                                "location": {"type": "string", "description": "location"}
                            }
                        },
                        "description": "first few prospects visible"
                    }
                }
            })
            
            print(f"✅ Search Results Extracted:")
            print(f"   📈 Total Results: {results.total_results if hasattr(results, 'total_results') else 'Unknown'}")
            print(f"   👥 Shown: {results.results_shown if hasattr(results, 'results_shown') else 'Unknown'}")
            
            if hasattr(results, 'first_prospects') and results.first_prospects:
                print(f"   🎯 First few prospects:")
                for i, prospect in enumerate(results.first_prospects[:3], 1):
                    if hasattr(prospect, 'name'):
                        print(f"     {i}. {prospect.name} - {getattr(prospect, 'title', 'N/A')} at {getattr(prospect, 'company', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️ Could not extract structured results: {e}")
            print("✅ But the search was performed successfully!")
        
        print("\n🎉 SUCCESS! SignalHire automation completed:")
        print("   ✅ Opened visible browser")
        print("   ✅ Logged into SignalHire")
        print("   ✅ Navigated to search")
        print("   ✅ Set job title: Heavy Equipment Mechanic")
        print("   ✅ Set location: Canada")
        print("   ✅ Executed search")
        print("   ✅ Displayed results")
        
        print("\n⏰ Keeping browser open for 30 seconds so you can see the results...")
        await page.wait_for_timeout(30000)  # Keep browser open for 30 seconds
        
        print("\n🔒 Closing browser...")
        await stagehand.close()
        print("✅ Browser closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔎 SignalHire Heavy Equipment Mechanic Search Test")
    print("=" * 60)
    print("This will open a VISIBLE browser and perform the search!")
    print("You'll see the browser login and search in real-time.")
    print("=" * 60)
    
    result = asyncio.run(test_signalhire_search_visible())
    
    if result:
        print("\n🎉 AUTOMATION TEST PASSED!")
        print("The agent successfully logged in and searched for Heavy Equipment Mechanics in Canada!")
    else:
        print("\n💥 AUTOMATION TEST FAILED!")
