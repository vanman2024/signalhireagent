"""Test SignalHire automation with real search scenario."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from stagehand import Stagehand


async def test_signalhire_search():
    """Test searching for Heavy Equipment Mechanics in Canada."""
    # Load environment variables
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    
    if not email or not password:
        print("❌ Missing SignalHire credentials")
        return False
    
    try:
        print("🚀 Initializing Stagehand with Browserbase...")
        stagehand = Stagehand(
            env="BROWSERBASE",
            model_api_key=os.getenv('MODEL_API_KEY'),
            verbose=1
        )
        await stagehand.init()
        page = stagehand.page
        
        print("🌐 Navigating to SignalHire login...")
        await page.goto('https://www.signalhire.com/auth/signin')
        await page.wait_for_timeout(3000)
        
        print("🔐 Logging into SignalHire...")
        await page.act(f'Fill in the email field with "{email}"')
        await page.act(f'Fill in the password field with "{password}"')
        await page.act('Click the sign in button')
        
        # Wait for login to complete
        await page.wait_for_timeout(5000)
        
        print("🔍 Navigating to search page...")
        await page.goto('https://www.signalhire.com/search')
        await page.wait_for_timeout(3000)
        
        print("📋 Filling search criteria...")
        await page.act('Fill in the job title field with "Heavy Equipment Mechanic"')
        await page.wait_for_timeout(1000)
        
        await page.act('Fill in the location field with "Canada"')
        await page.wait_for_timeout(1000)
        
        print("🚀 Starting search...")
        await page.act('Click the search button')
        
        # Wait for search results to load
        await page.wait_for_timeout(8000)
        
        print("📊 Extracting search results...")
        results = await page.extract({
            "instruction": "Extract search results information including total count and prospect names",
            "schema": {
                "total_prospects": {"type": "number", "description": "total number of prospects found"},
                "prospects_visible": {"type": "number", "description": "number of prospects currently visible"},
                "sample_prospects": {
                    "type": "array",
                    "items": {
                        "type": "object", 
                        "properties": {
                            "name": {"type": "string"},
                            "title": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    },
                    "description": "first few prospects visible"
                }
            }
        })
        
        print(f"✅ Search completed!")
        print(f"📈 Total prospects found: {results.get('total_prospects', 'Unknown')}")
        print(f"👀 Prospects visible: {results.get('prospects_visible', 'Unknown')}")
        
        if results.get('sample_prospects'):
            print("\n👥 Sample prospects found:")
            for prospect in results.get('sample_prospects', [])[:3]:
                print(f"  • {prospect.get('name', 'N/A')} - {prospect.get('title', 'N/A')} - {prospect.get('location', 'N/A')}")
        
        print("\n🎯 Looking for bulk export options...")
        await page.act('Look for bulk actions or export options')
        await page.wait_for_timeout(2000)
        
        # Try to find export functionality
        export_info = await page.extract({
            "instruction": "Check if there are bulk action buttons, export options, or select all functionality visible",
            "schema": {
                "bulk_actions_available": {"type": "boolean", "description": "whether bulk action buttons are visible"},
                "export_options": {"type": "array", "items": {"type": "string"}, "description": "available export options like CSV, Excel, etc"},
                "select_all_available": {"type": "boolean", "description": "whether there's a select all checkbox"}
            }
        })
        
        print(f"\n📤 Export options available: {export_info}")
        
        await stagehand.close()
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'stagehand' in locals():
            await stagehand.close()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_signalhire_search())
    if result:
        print("\n✅ SignalHire search test PASSED!")
    else:
        print("\n💥 SignalHire search test FAILED!")
