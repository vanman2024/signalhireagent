#!/usr/bin/env python3
"""
Test reveal with 2 contacts using DigitalOcean droplet callback URL.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import httpx
import json
from typing import List, Dict

# Load environment variables (allow .env to override shell exports)
load_dotenv(override=True)

# Airtable and SignalHire configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
SIGNALHIRE_API_KEY = os.getenv('SIGNALHIRE_API_KEY')
base_callback_url = (os.getenv('SIGNALHIRE_CALLBACK_URL') or '').strip()

if base_callback_url:
    if not base_callback_url.startswith(('http://', 'https://')):
        base_callback_url = f"https://{base_callback_url.lstrip('/')}"
    base_callback_url = base_callback_url.rstrip('/')
    if base_callback_url.endswith('/signalhire/callback'):
        CALLBACK_URL = base_callback_url
    else:
        CALLBACK_URL = f"{base_callback_url}/signalhire/callback"
else:
    CALLBACK_URL = 'http://localhost:8000/signalhire/callback'

print(f"🔗 Using callback URL: {CALLBACK_URL}")

async def get_test_contacts() -> List[Dict]:
    """Get 2 test contacts from Airtable with SignalHire IDs but no email/phone."""
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
        params = {'pageSize': 50}
        
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        records = data.get('records', [])
    
    # Filter for contacts that have SignalHire ID but no email/phone
    contacts_to_reveal = []
    for record in records:
        fields = record['fields']
        signalhire_id = fields.get('SignalHire ID')
        has_email = fields.get('Primary Email') or fields.get('Secondary Email')
        has_phone = fields.get('Phone Number')
        
        # Skip test contacts
        full_name = fields.get('Full Name', '')
        if 'test' in full_name.lower() or 'callback' in full_name.lower():
            continue
            
        if signalhire_id and not has_email and not has_phone:
            contacts_to_reveal.append({
                'airtable_id': record['id'],
                'signalhire_id': signalhire_id,
                'full_name': full_name
            })
            
        # Only get 2 for testing
        if len(contacts_to_reveal) >= 2:
            break
    
    return contacts_to_reveal

async def reveal_contact(contact_id: str) -> Dict:
    """Submit revelation request for a single contact."""
    headers = {
        'apikey': SIGNALHIRE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'https://www.signalhire.com/api/v1/candidate/search',
                headers=headers,
                json={'items': [contact_id], 'callbackUrl': CALLBACK_URL},
                timeout=30.0
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'contact_id': contact_id,
                    'status': 'success',
                    'request_id': result.get('request_id')
                }
            else:
                return {
                    'contact_id': contact_id,
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {
                'contact_id': contact_id,
                'status': 'error',
                'error': str(e)
            }

async def main():
    """Test reveal with 2 contacts using droplet callback."""
    print("🧪 TESTING REVEAL WITH DIGITALOCEAN DROPLET")
    print("=" * 50)
    
    # Get 2 test contacts
    print("📂 Fetching 2 test contacts from Airtable...")
    contacts = await get_test_contacts()
    
    print(f"📊 Found {len(contacts)} test contacts")
    
    if not contacts:
        print("❌ No contacts available for testing!")
        return
    
    # Display test contacts
    print("\\n🎯 Test contacts:")
    for contact in contacts:
        print(f"  • {contact['full_name']} (ID: {contact['signalhire_id']})")
    
    print(f"\\n🔗 Callback URL: {CALLBACK_URL}")
    print("\\n🚀 Submitting reveal requests...")
    
    # Submit revelation requests
    tasks = [reveal_contact(contact['signalhire_id']) for contact in contacts]
    results = await asyncio.gather(*tasks)
    
    # Process results
    successful_requests = []
    for contact, result in zip(contacts, results):
        if result['status'] == 'success':
            successful_requests.append({
                'airtable_id': contact['airtable_id'],
                'signalhire_id': contact['signalhire_id'],
                'full_name': contact['full_name'],
                'request_id': result['request_id']
            })
            print(f"  ✅ {contact['full_name']}: Request {result['request_id']}")
        else:
            print(f"  ❌ {contact['full_name']}: {result['error']}")
    
    if successful_requests:
        print(f"\\n📊 RESULTS:")
        print(f"   ✅ Successful requests: {len(successful_requests)}")
        print(f"   🎯 Callback URL: {CALLBACK_URL}")
        print("\\n⏳ Waiting 30 seconds for callbacks to arrive...")
        print("   (Watch the DigitalOcean droplet for incoming callbacks)")
        
        await asyncio.sleep(30)
        print("✅ Test complete! Check Airtable for Status updates.")
    else:
        print("❌ No successful requests.")

if __name__ == "__main__":
    asyncio.run(main())