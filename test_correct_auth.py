#!/usr/bin/env python3
"""
Test SignalHire API with correct apikey header format.
"""

import asyncio
import httpx
from src.lib.config import get_config

async def test_signalhire_api():
    """Test SignalHire API with correct authentication."""
    print("🔐 Testing SignalHire API with 'apikey' header")
    print("=" * 50)
    
    config = get_config()
    api_key = config.signalhire.api_key
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"🔑 Using API Key: {api_key[:10]}...")
    
    # Correct headers format based on documentation
    headers = {
        "apikey": api_key,  # Custom header format for SignalHire
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "SignalHire-Agent/1.0.0"
    }
    
    base_url = "https://www.signalhire.com"
    
    # Test credits endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            url = f"{base_url}/api/v1/credits"
            print(f"📡 Testing credits endpoint: {url}")
            print(f"📋 Headers: {headers}")
            
            response = await client.get(url, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ Credits API working!")
                
                # Now test search endpoint
                print(f"\n🔍 Testing search endpoint...")
                search_url = f"{base_url}/api/v1/search"
                search_data = {
                    "title": "Heavy Equipment Mechanic",
                    "location": "Canada",
                    "limit": 5
                }
                
                search_response = await client.post(search_url, headers=headers, json=search_data)
                print(f"📊 Search Status: {search_response.status_code}")
                print(f"📄 Search Response: {search_response.text[:500]}...")
                
                if search_response.status_code == 200:
                    print("🎉 Search API working! We can now run our real tests!")
                else:
                    print("⚠️ Search failed, but authentication is working")
            
            elif response.status_code == 401:
                print("❌ Still authentication error - API key may be invalid")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"💥 Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_signalhire_api())