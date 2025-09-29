#!/usr/bin/env python3
"""
Test script to reveal one contact at a time.
"""

import asyncio
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv(override=True)

SIGNALHIRE_API_KEY = os.getenv('SIGNALHIRE_API_KEY')
CALLBACK_URL = "https://8e359ac0f467f6.lhr.life/signalhire/callback"

async def test_single_contact():
    """Test revealing a single contact."""
    contact_id = "c8920e73c84f4e62955fd0142d2a5a19"
    
    headers = {
        'apikey': SIGNALHIRE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'items': [contact_id],
        'callbackUrl': CALLBACK_URL
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"🔍 Revealing contact: {contact_id}")
            response = await client.post(
                'https://www.signalhire.com/api/v1/candidate/search',
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            print(f"📡 Status: {response.status_code}")
            result = response.json()
            print(f"📧 Response: {result}")
            
            if response.status_code == 200:
                request_id = result.get('requestId')
                print(f"✅ Success! Request ID: {request_id}")
                print("⏳ Waiting 30 seconds for callback...")
                await asyncio.sleep(30)
                print("✅ Done waiting")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_contact())