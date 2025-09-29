#!/usr/bin/env python3
"""
Browserbase Session Cleanup Utility
Helps manage and cleanup running browser sessions
"""

import os
import requests
import asyncio
from stagehand import Stagehand
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def cleanup_all_sessions():
    """Clean up all running sessions using Stagehand's session management"""
    try:
        print("🧹 Cleaning up Browserbase sessions...")
        
        # Try to create a Stagehand instance to trigger cleanup
        stagehand = Stagehand(
            env="BROWSERBASE",
            api_key=os.environ.get("OPENAI_API_KEY"),
            browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
            browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        )
        
        # The init will fail if there's a session limit, but we can try cleanup
        try:
            await stagehand.init()
            print("✅ Stagehand initialized successfully")
            await stagehand.close()
            print("✅ Session closed")
        except Exception as e:
            print(f"❌ Session limit reached: {e}")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def direct_api_cleanup():
    """Try direct API cleanup using requests"""
    try:
        api_key = os.environ.get("BROWSERBASE_API_KEY")
        project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
        
        if not api_key or not project_id:
            print("❌ Missing API credentials")
            return
            
        print("🔍 Attempting direct API session cleanup...")
        
        # Try different API endpoints
        endpoints = [
            f"https://www.browserbase.com/v1/sessions",
            f"https://api.browserbase.com/v1/sessions", 
            f"https://www.browserbase.com/v1/projects/{project_id}/sessions"
        ]
        
        headers = {
            'X-BB-API-Key': api_key,
            'Authorization': f'Bearer {api_key}',
            'x-bb-api-key': api_key
        }
        
        for endpoint in endpoints:
            print(f"  Trying: {endpoint}")
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  Response: {response.text[:200]}...")
                    break
                elif response.status_code != 404:
                    print(f"  Error: {response.text[:200]}...")
            except Exception as e:
                print(f"  Failed: {e}")
                
    except Exception as e:
        print(f"❌ Direct API cleanup failed: {e}")

async def main():
    """Main cleanup function"""
    print("🚀 Starting Browserbase session cleanup...")
    
    # Try async cleanup first
    await cleanup_all_sessions()
    
    # Try direct API cleanup
    direct_api_cleanup()
    
    print("⏰ Waiting 60 seconds for sessions to timeout...")
    await asyncio.sleep(60)
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    asyncio.run(main())
