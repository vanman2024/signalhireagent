#!/usr/bin/env python3
"""
Quick test script to check SignalHire API connectivity.
Tests different base URLs and authentication methods.
"""

import asyncio
import httpx
import os
from src.lib.config import get_config

async def test_api_endpoint(base_url: str, api_key: str, name: str):
    """Test a specific API endpoint."""
    print(f"\n🔍 Testing {name}: {base_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "SignalHire-Agent/1.0.0"
    }
    
    # Test different possible endpoints
    endpoints_to_try = [
        "/api/v1/credits",
        "/api/credits", 
        "/credits",
        "/api/v1/health",
        "/api/health",
        "/health"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints_to_try:
            url = f"{base_url.rstrip('/')}{endpoint}"
            try:
                print(f"  📡 Trying: {url}")
                response = await client.get(url, headers=headers)
                
                print(f"     Status: {response.status_code}")
                if response.status_code < 400:
                    print(f"     Success! Response: {response.text[:200]}...")
                    return True
                elif response.status_code == 401:
                    print(f"     Authentication failed - check API key")
                elif response.status_code == 404:
                    print(f"     Endpoint not found")
                else:
                    print(f"     Error: {response.text[:100]}...")
                    
            except httpx.ConnectError as e:
                print(f"     Connection Error: {e}")
            except httpx.TimeoutException:
                print(f"     Timeout")
            except Exception as e:
                print(f"     Exception: {e}")
    
    return False

async def main():
    """Test different SignalHire API endpoints."""
    print("🌐 SignalHire API Connection Test")
    print("=" * 50)
    
    config = get_config()
    api_key = config.signalhire.api_key
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"🔑 Using API Key: {api_key[:10]}...")
    
    # Test different base URLs
    base_urls = [
        ("Official API URL", "https://api.signalhire.com"),
        ("Web API URL", "https://www.signalhire.com/api"),
        ("Direct Web URL", "https://www.signalhire.com"),
        ("Alternative API", "https://signalhire.com/api"),
    ]
    
    for name, base_url in base_urls:
        success = await test_api_endpoint(base_url, api_key, name)
        if success:
            print(f"✅ Found working endpoint: {base_url}")
            break
    else:
        print("❌ No working endpoints found")
        
        # Additional diagnostics
        print("\n🔍 Additional Diagnostics:")
        print("- Try checking SignalHire documentation")
        print("- Verify API key is valid and active")
        print("- Check if account has necessary permissions")

if __name__ == "__main__":
    asyncio.run(main())