"""Test script to validate Stagehand integration with Browserbase."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.models.browser_config import BrowserConfig
from src.services.browser_client import BrowserClient


async def test_stagehand():
    """Test basic Stagehand functionality with Browserbase."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    browserbase_api_key = os.getenv('BROWSERBASE_API_KEY')
    browserbase_project_id = os.getenv('BROWSERBASE_PROJECT_ID')
    model_api_key = os.getenv('MODEL_API_KEY') or os.getenv('OPENAI_API_KEY')
    
    print(f"Email: {email[:10]}..." if email else "No email")
    print(f"Password: {'*' * len(password)}" if password else "No password")
    print(f"Browserbase API Key: {browserbase_api_key[:10]}..." if browserbase_api_key else "No Browserbase API key")
    print(f"Browserbase Project ID: {browserbase_project_id[:10]}..." if browserbase_project_id else "No Browserbase Project ID")
    print(f"Model API Key: {model_api_key[:10]}..." if model_api_key else "No Model API key")
    
    if not all([email, password, browserbase_api_key, browserbase_project_id, model_api_key]):
        print("❌ Missing required credentials in .env file")
        return False
        
    # Create browser config
    config = BrowserConfig(
        email=email,
        password=password,
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        timeout=30000
    )
    
    try:
        # Test browser initialization
        print("\n🚀 Testing Stagehand initialization with Browserbase...")
        async with BrowserClient(config) as browser:
            print("✅ Stagehand initialized successfully with Browserbase!")
            
            # Test basic navigation
            print("🌐 Testing basic page navigation...")
            page = browser.stagehand.page
            await page.goto('https://example.com')
            print("✅ Page navigation successful!")
            
            # Test simple extraction
            print("📄 Testing data extraction...")
            result = await page.extract({
                "instruction": "Extract the page title",
                "schema": {
                    "title": {"type": "string", "description": "page title"}
                }
            })
            print(f"✅ Data extraction successful! Title: {result.get('title', 'N/A')}")
            
            return True
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_stagehand())
    if result:
        print("\n🎉 Stagehand + Browserbase integration test PASSED!")
        print("Ready to proceed with SignalHire automation!")
    else:
        print("\n💥 Stagehand integration test FAILED!")
