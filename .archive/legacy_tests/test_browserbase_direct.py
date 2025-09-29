"""Simple test script to validate Stagehand/Browserbase integration."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from stagehand import Stagehand


async def test_stagehand_direct():
    """Test Stagehand directly with Browserbase."""
    # Load environment variables
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    browserbase_api_key = os.getenv('BROWSERBASE_API_KEY')
    browserbase_project_id = os.getenv('BROWSERBASE_PROJECT_ID')
    model_api_key = os.getenv('MODEL_API_KEY') or os.getenv('OPENAI_API_KEY')
    
    print(f"Browserbase API Key: {browserbase_api_key[:10]}..." if browserbase_api_key else "❌ No Browserbase API key")
    print(f"Browserbase Project ID: {browserbase_project_id[:10]}..." if browserbase_project_id else "❌ No Browserbase Project ID")
    print(f"Model API Key: {model_api_key[:10]}..." if model_api_key else "❌ No Model API key")
    
    if not all([browserbase_api_key, browserbase_project_id, model_api_key]):
        print("\n❌ Missing required credentials in .env file")
        return False
    
    try:
        print("\n🚀 Testing Stagehand initialization with Browserbase...")
        
        # Initialize Stagehand with Browserbase
        stagehand = Stagehand(
            env="BROWSERBASE",
            model_api_key=model_api_key,
            verbose=1
        )
        
        print("🔧 Initializing Stagehand...")
        await stagehand.init()
        print("✅ Stagehand initialized successfully with Browserbase!")
        
        # Test basic navigation
        print("🌐 Testing basic page navigation...")
        page = stagehand.page
        await page.goto('https://example.com')
        print("✅ Page navigation successful!")
        
        # Test simple action
        print("🤖 Testing basic action...")
        await page.act('scroll down')
        print("✅ Action successful!")
        
        # Test data extraction
        print("📄 Testing data extraction...")
        result = await page.extract({
            "instruction": "Extract the page title and main heading",
            "schema": {
                "title": {"type": "string", "description": "page title"},
                "heading": {"type": "string", "description": "main heading text"}
            }
        })
        print(f"✅ Data extraction successful!")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Heading: {result.get('heading', 'N/A')}")
        
        # Close Stagehand
        await stagehand.close()
        print("🔒 Stagehand closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_stagehand_direct())
    if result:
        print("\n🎉 Stagehand + Browserbase integration test PASSED!")
        print("Ready to proceed with SignalHire automation!")
    else:
        print("\n💥 Stagehand integration test FAILED!")
