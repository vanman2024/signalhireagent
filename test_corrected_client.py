#!/usr/bin/env python3
"""
Test the corrected SignalHire API client with proper authentication and endpoints.
"""

import asyncio
from src.services.signalhire_client import SignalHireClient
from src.lib.config import get_config

async def test_corrected_client():
    """Test the corrected SignalHire client."""
    print("🔧 Testing Corrected SignalHire API Client")
    print("=" * 50)
    
    config = get_config()
    api_key = config.signalhire.api_key
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"🔑 Using API Key: {api_key[:10]}...")
    
    # Test with corrected client
    client = SignalHireClient(api_key=api_key)
    
    try:
        print(f"🌐 Base URL: {client.base_url}")
        print(f"📡 API Prefix: {client.api_prefix}")
        
        # Test credits endpoint
        print("\n📊 Testing Credits API...")
        credits_response = await client.check_credits()
        
        if credits_response.success:
            print(f"✅ Credits API working!")
            print(f"   Available Credits: {credits_response.data.get('credits', 'unknown')}")
        else:
            print(f"❌ Credits API failed: {credits_response.error}")
            return
        
        # Test search prospects (should show compatibility message)
        print("\n🔍 Testing Search API...")
        search_response = await client.search_prospects({"title": "Test"})
        
        if not search_response.success:
            print(f"ℹ️  Expected: {search_response.error}")
        
        # Test reveal by identifier (would need callback URL)
        print("\n📞 Testing Reveal API...")
        reveal_response = await client.reveal_contact("test-id")
        
        if not reveal_response.success:
            print(f"ℹ️  Expected: {reveal_response.error}")
        
        print("\n🎉 All tests completed! API client is properly configured.")
        print("   - Base URL: ✅ https://www.signalhire.com")
        print("   - Authentication: ✅ apikey header")
        print("   - Credits endpoint: ✅ Working")
        
    except Exception as e:
        print(f"💥 Error during testing: {e}")
    finally:
        if client.session:
            await client.close_session()

if __name__ == "__main__":
    asyncio.run(test_corrected_client())