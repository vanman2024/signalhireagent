"""Test SignalHire automation with visible browser - no env issues."""

import asyncio
from stagehand import Stagehand


async def test_signalhire_visible():
    """Test SignalHire with visible local browser."""
    
    # Hard-code credentials for testing (will work regardless of env issues)
    email = "ryan@skilledtradesjobhub.ca"
    password = "jPdpd1a893pCLjkj"
    openai_key = "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"
    
    print("🚀 Starting SignalHire automation test...")
    print("📍 Target: Heavy Equipment Mechanic in Canada")
    print("👀 Browser will be VISIBLE so you can see the automation!")
    
    try:
        # Use LOCAL environment with visible browser
        stagehand = Stagehand(
            env="LOCAL",
            model_api_key=openai_key,
            verbose=1,
            headless=False  # This makes the browser visible!
        )
        
        await stagehand.init()
        page = stagehand.page
        
        print("\n🔐 Step 1: Navigating to SignalHire login...")
        await page.goto('https://www.signalhire.com/auth/signin')
        await page.wait_for_timeout(3000)
        
        print("📝 Step 2: Filling in login credentials...")
        await page.act(f'Fill in the email field with "{email}"')
        await page.wait_for_timeout(1000)
        
        await page.act(f'Fill in the password field with "{password}"')
        await page.wait_for_timeout(1000)
        
        print("🔑 Step 3: Clicking sign in...")
        await page.act('Click the sign in button')
        await page.wait_for_timeout(5000)
        
        print("🔍 Step 4: Navigating to search...")
        await page.goto('https://www.signalhire.com/search')
        await page.wait_for_timeout(3000)
        
        print("🏗️ Step 5: Searching for Heavy Equipment Mechanic...")
        await page.act('Fill in the job title field with "Heavy Equipment Mechanic"')
        await page.wait_for_timeout(1000)
        
        await page.act('Fill in the location field with "Canada"')
        await page.wait_for_timeout(1000)
        
        print("🚀 Step 6: Starting search...")
        await page.act('Click the search button')
        await page.wait_for_timeout(10000)  # Wait for results to load
        
        print("📊 Step 7: Extracting search results...")
        results = await page.extract({
            "instruction": "Extract search results summary and first few prospects",
            "schema": {
                "total_results": {"type": "number", "description": "total number of results found"},
                "prospects": {
                    "type": "array",
                    "items": {
                        "type": "object", 
                        "properties": {
                            "name": {"type": "string"},
                            "title": {"type": "string"},
                            "company": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    }
                }
            }
        })
        
        print(f"\n✅ SUCCESS! Found results:")
        print(f"📈 Total Results: {results.get('total_results', 'Unknown')}")
        print(f"👥 First few prospects:")
        for i, prospect in enumerate(results.get('prospects', [])[:5]):
            print(f"  {i+1}. {prospect.get('name', 'N/A')} - {prospect.get('title', 'N/A')} at {prospect.get('company', 'N/A')}")
        
        print("\n⏸️  Browser will stay open for 30 seconds so you can see the results...")
        await page.wait_for_timeout(30000)
        
        await stagehand.close()
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_signalhire_visible())
