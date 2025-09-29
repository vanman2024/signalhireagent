#!/usr/bin/env python3
"""
Session Manager for Browserbase
Handles session lifecycle and cleanup
"""

import asyncio
import os
import time
import requests
from typing import Optional
from stagehand import Stagehand
from dotenv import load_dotenv

load_dotenv()

class BrowserbaseSessionManager:
    """Manages Browserbase sessions with proper cleanup"""
    
    def __init__(self):
        self.api_key = os.environ.get("BROWSERBASE_API_KEY")
        self.project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.current_session = None
        
    async def create_session_with_retry(self, max_retries=3, retry_delay=30):
        """Create a session with retry logic for concurrent limits"""
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Session creation attempt {attempt + 1}/{max_retries}")
                
                stagehand = Stagehand(
                    env="BROWSERBASE",
                    api_key=self.openai_key,
                    browserbase_api_key=self.api_key,
                    browserbase_project_id=self.project_id,
                )
                
                await stagehand.init()
                self.current_session = stagehand
                print("✅ Session created successfully!")
                return stagehand
                
            except Exception as e:
                if "429" in str(e) or "concurrent" in str(e).lower():
                    print(f"⏳ Concurrent limit reached, waiting {retry_delay}s before retry {attempt + 1}...")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        print("❌ Max retries reached, switching to LOCAL mode")
                        return await self.create_local_session()
                else:
                    raise e
        
        return None
    
    async def create_local_session(self):
        """Fallback to local session"""
        print("🏠 Creating LOCAL session as fallback...")
        
        stagehand = Stagehand(
            env="LOCAL",
            api_key=self.openai_key,
            headless=False,  # Show browser for debugging
        )
        
        await stagehand.init()
        self.current_session = stagehand
        print("✅ Local session created!")
        return stagehand
    
    async def cleanup(self):
        """Clean up current session"""
        if self.current_session:
            try:
                await self.current_session.close()
                print("✅ Session cleaned up")
            except Exception as e:
                print(f"⚠️ Session cleanup warning: {e}")
            finally:
                self.current_session = None

async def test_session_manager():
    """Test the session manager"""
    manager = BrowserbaseSessionManager()
    
    try:
        # Try to create a session
        stagehand = await manager.create_session_with_retry()
        
        if stagehand:
            print("🌐 Testing navigation...")
            await stagehand.page.goto("https://www.signalhire.com")
            await stagehand.page.wait_for_timeout(3000)
            print(f"📍 Current URL: {stagehand.page.url}")
            
    finally:
        await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test_session_manager())
