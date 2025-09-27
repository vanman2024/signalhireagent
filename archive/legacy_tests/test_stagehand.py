"""Test script to validate Stagehand integration."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from src.models.browser_config import BrowserConfig
from src.services.browser_client import BrowserClient


async def test_stagehand():
    """Test basic Stagehand functionality."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    email = os.getenv('SIGNALHIRE_EMAIL')
    password = os.getenv('SIGNALHIRE_PASSWORD')
    
    print(f"Email loaded: {email[:10]}..." if email else "No email")
    print(f"Password loaded: {'*' * len(password) if password else 'No password'}")
    
    if not email or not password:
        print("❌ Missing SignalHire credentials in .env file")
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
        print("🚀 Testing Stagehand initialization...")
        async with BrowserClient(config) as browser:
            print("✅ Stagehand initialized successfully")
            
            # Test authentication 
            print("🔐 Testing SignalHire authentication...")
            auth_result = await browser.authenticate()
            
            if auth_result:
                print("✅ Authentication successful!")
                return True
            else:
                print("❌ Authentication failed")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_stagehand())
    if result:
        print("\n🎉 Stagehand integration test PASSED!")
    else:
        print("\n💥 Stagehand integration test FAILED!")
