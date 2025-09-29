#!/usr/bin/env python3
"""
Test fetching contacts from Airtable
"""

import asyncio
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv(override=True)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

async def test_airtable_fetch():
    """Test fetching contacts from Airtable."""
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("📂 Fetching first page from Airtable...")
            url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
            params = {'pageSize': 5}  # Just get 5 records to test
            
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
            print(f"📡 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"📊 Got {len(records)} records")
                
                # Check for contacts with SignalHire IDs
                contacts_with_ids = []
                for record in records:
                    fields = record['fields']
                    signalhire_id = fields.get('SignalHire ID')
                    has_email = fields.get('Primary Email') or fields.get('Secondary Email')
                    has_phone = fields.get('Phone Number')
                    full_name = fields.get('Full Name', '')
                    
                    print(f"👤 {full_name}: SH_ID={signalhire_id}, Email={bool(has_email)}, Phone={bool(has_phone)}")
                    
                    if signalhire_id and not has_email and not has_phone:
                        contacts_with_ids.append({
                            'airtable_id': record['id'],
                            'signalhire_id': signalhire_id,
                            'full_name': full_name
                        })
                
                print(f"✅ Found {len(contacts_with_ids)} contacts needing revelation")
                return contacts_with_ids
            else:
                print(f"❌ Error: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(test_airtable_fetch())