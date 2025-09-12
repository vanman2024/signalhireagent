#!/usr/bin/env python3
"""
Test different authentication formats for SignalHire API.
"""

import asyncio
import httpx
from src.lib.config import get_config

async def test_auth_format(base_url: str, endpoint: str, headers: dict, description: str):
    """Test a specific auth format."""
    print(f"\n🔐 Testing {description}")
    url = f"{base_url.rstrip('/')}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"  📡 URL: {url}")
            print(f"  📋 Headers: {headers}")
            response = await client.get(url, headers=headers)
            
            print(f"  📊 Status: {response.status_code}")
            if response.status_code < 400:
                print(f"  ✅ Success! Response: {response.text[:300]}...")
                return True
            else:
                print(f"  ❌ Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  💥 Exception: {e}")
    
    return False

async def main():
    """Test different authentication formats."""
    print("🔐 SignalHire API Authentication Test")
    print("=" * 50)
    
    config = get_config()
    api_key = config.signalhire.api_key
    email = config.signalhire.email
    password = config.signalhire.password
    
    base_url = "https://www.signalhire.com"
    endpoint = "/api/v1/credits"
    
    # Test different authentication methods
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}),
        ("API Key Header", {"X-API-Key": api_key, "Content-Type": "application/json"}),
        ("API Key in Auth", {"Authorization": f"ApiKey {api_key}", "Content-Type": "application/json"}),
        ("Basic Auth with API Key", {"Authorization": f"Basic {api_key}", "Content-Type": "application/json"}),
        ("Token Header", {"Token": api_key, "Content-Type": "application/json"}),
        ("API Key Param", {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}),
    ]
    
    if email and password:
        import base64
        credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
        auth_methods.append(("Basic Auth Email/Password", {"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}))
    
    # Add common headers
    common_headers = {
        "User-Agent": "SignalHire-Agent/1.0.0",
        "Accept": "application/json",
    }
    
    for description, auth_headers in auth_methods:
        headers = {**common_headers, **auth_headers}
        success = await test_auth_format(base_url, endpoint, headers, description)
        if success:
            print(f"\n🎉 Working authentication method: {description}")
            break
    else:
        print("\n❌ No working authentication method found")
        
        # Try a simpler endpoint
        print("\n🔍 Trying simpler endpoints...")
        simple_endpoints = ["/api/v1/user", "/api/v1/me", "/api/v1/status"]
        
        for simple_endpoint in simple_endpoints:
            bearer_headers = {
                **common_headers,
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            success = await test_auth_format(base_url, simple_endpoint, bearer_headers, f"Bearer token on {simple_endpoint}")
            if success:
                break

if __name__ == "__main__":
    asyncio.run(main())