#!/usr/bin/env python3
"""
Reveal contact information for existing Airtable contacts.
This script takes the SignalHire IDs from Airtable and reveals their contact info.
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
base_callback_url = (os.getenv('SIGNALHIRE_CALLBACK_URL') or os.getenv('PUBLIC_CALLBACK_URL') or '').strip()
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

async def get_airtable_contacts() -> List[Dict]:
    """Get all contacts from Airtable with SignalHire IDs but no email/phone."""
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    all_records = []
    offset = None
    
    async with httpx.AsyncClient() as client:
        while True:
            url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
            params = {'pageSize': 100}
            if offset:
                params['offset'] = offset
            
            response = await client.get(url, headers=headers, params=params)
            data = response.json()
            
            records = data.get('records', [])
            all_records.extend(records)
            
            offset = data.get('offset')
            if not offset:
                break
    
    # Filter for contacts that have SignalHire ID but no email/phone
    contacts_to_reveal = []
    for record in all_records:
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
    
    return contacts_to_reveal

async def reveal_contact(contact_id: str) -> Dict:
    """Submit revelation request for a single contact."""
    headers = {
        'apikey': SIGNALHIRE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'callback_url': CALLBACK_URL,
        'item': contact_id
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
    """Main function to reveal contact information."""
    print("🔍 REVEALING CONTACT INFORMATION FOR EXISTING AIRTABLE CONTACTS")
    print("=" * 70)
    
    # Get contacts that need revelation
    print("📂 Fetching contacts from Airtable...")
    contacts = await get_airtable_contacts()
    
    print(f"📊 Found {len(contacts)} contacts that need contact information")
    
    if not contacts:
        print("✅ All contacts already have contact information!")
        return
    
    # Process in batches of 10 to respect rate limits
    batch_size = 10
    successful_requests = []
    failed_requests = []
    
    for i in range(0, len(contacts), batch_size):
        batch = contacts[i:i + batch_size]
        print(f"\\n🚀 Processing batch {i//batch_size + 1} ({len(batch)} contacts)...")
        
        # Submit revelation requests for this batch
        tasks = [reveal_contact(contact['signalhire_id']) for contact in batch]
        results = await asyncio.gather(*tasks)
        
        # Process results
        for contact, result in zip(batch, results):
            if result['status'] == 'success':
                successful_requests.append({
                    'airtable_id': contact['airtable_id'],
                    'signalhire_id': contact['signalhire_id'],
                    'full_name': contact['full_name'],
                    'request_id': result['request_id']
                })
                print(f"  ✅ {contact['full_name']}: Request {result['request_id']}")
            else:
                failed_requests.append({
                    'contact': contact,
                    'error': result['error']
                })
                print(f"  ❌ {contact['full_name']}: {result['error']}")
        
        # Wait between batches to respect rate limits
        if i + batch_size < len(contacts):
            print("   ⏳ Waiting 10 seconds between batches...")
            await asyncio.sleep(10)
    
    print(f"\\n📊 REVELATION SUMMARY:")
    print(f"   ✅ Successful requests: {len(successful_requests)}")
    print(f"   ❌ Failed requests: {len(failed_requests)}")
    
    if successful_requests:
        print(f"\\n🎯 Callback URL: {CALLBACK_URL}")
        print("⏳ Waiting 30 seconds for callbacks to arrive...")
        print("   (Contact information will be automatically added to Airtable)")
        
        # Save the request mapping for callback processing
        with open('/tmp/signalhire_requests.json', 'w') as f:
            json.dump(successful_requests, f, indent=2)
        
        await asyncio.sleep(30)
        print("✅ Revelation process complete! Check Airtable for updated contact info.")
    else:
        print("❌ No successful revelation requests submitted.")

if __name__ == "__main__":
    asyncio.run(main())