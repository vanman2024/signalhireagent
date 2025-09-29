#!/usr/bin/env python3
"""
Simple script to reveal contacts using the working tunnel URL
"""

import asyncio
import json
from dotenv import load_dotenv
from src.services.signalhire_client import SignalHireClient

# Load environment variables
load_dotenv()

# New working tunnel URL
CALLBACK_URL = "https://82b4afcaf4f376.lhr.life/signalhire/callback"

async def main():
    # Load cached contacts
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        all_contacts = json.load(f)
    
    contact_ids = list(all_contacts.keys())
    print(f"📂 Found {len(contact_ids)} total contacts")
    
    # Test with 5 contacts
    test_contacts = contact_ids[:5]
    print(f"🔍 Revealing {len(test_contacts)} contacts with callback: {CALLBACK_URL}")
    
    client = SignalHireClient(callback_url=CALLBACK_URL)
    
    success_count = 0
    for i, contact_id in enumerate(test_contacts):
        try:
            result = await client.reveal_contact(contact_id)
            request_id = result.data.get('requestId') if result.data else None
            print(f"✅ {i+1}/{len(test_contacts)}: {contact_id} -> {request_id}")
            success_count += 1
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"❌ {i+1}/{len(test_contacts)}: {contact_id} failed: {e}")
    
    await client.close()
    print(f"📊 Submitted {success_count}/{len(test_contacts)} revelations")
    print("⏳ Check server logs for incoming callbacks...")

if __name__ == "__main__":
    asyncio.run(main())