#!/usr/bin/env python3
"""
Direct contact fetching using SignalHire API without callbacks.
Attempts to get contact information synchronously or through polling.
"""

import asyncio
import json
import os
import time
from dotenv import load_dotenv
from src.services.signalhire_client import SignalHireClient
from pyairtable import Api

load_dotenv()

# Airtable configuration from environment
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

async def check_contact_status(client, request_id):
    """Check if a contact revelation request has completed"""
    try:
        # Try to get the status from SignalHire API
        # This might be available through a status endpoint
        result = await client._make_request("GET", f"/api/v1/person/status/{request_id}")
        return result
    except Exception as e:
        print(f"Status check failed for {request_id}: {e}")
        return None

async def try_direct_contact_fetch(contact_id):
    """Try to get contact info directly without callbacks"""
    client = SignalHireClient()
    
    try:
        # Method 1: Try the Search API with include_contacts=true
        search_params = {
            "ids": [contact_id],
            "include_contacts": True,
            "limit": 1
        }
        
        result = await client._make_request("POST", "/api/v1/search", json=search_params)
        
        if result.data and result.data.get('results'):
            person = result.data['results'][0]
            if person.get('contacts'):
                print(f"✅ Found contacts directly for {contact_id}")
                return person
        
        # Method 2: Try getting person profile with contacts
        profile_result = await client._make_request("GET", f"/api/v1/person/{contact_id}")
        
        if profile_result.data and profile_result.data.get('contacts'):
            print(f"✅ Found contacts in profile for {contact_id}")
            return profile_result.data
            
        print(f"⏸️ No direct contacts found for {contact_id}")
        return None
        
    except Exception as e:
        print(f"❌ Direct fetch failed for {contact_id}: {e}")
        return None
    finally:
        await client.close()

async def add_to_airtable(contact_data, contact_id):
    """Add contact to Airtable"""
    try:
        api = Api(os.getenv('AIRTABLE_API_KEY'))
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
        
        name = contact_data.get('fullName', 'Unknown')
        contacts = contact_data.get('contacts', [])
        experience = contact_data.get('experience', [])
        current_job = experience[0] if experience else {}
        
        # Extract contact info
        emails = [c.get('value') for c in contacts if c.get('type') == 'email']
        phones = [c.get('value') for c in contacts if c.get('type') == 'phone']
        
        # Parse location into components
        location = contact_data.get('location', '')
        location_parts = location.split(', ') if location else []
        city = location_parts[0] if len(location_parts) > 0 else ''
        province_state = location_parts[1] if len(location_parts) > 1 else ''
        country = location_parts[2] if len(location_parts) > 2 else location_parts[1] if len(location_parts) == 2 else ''
        
        record = {
            "Full Name": name,
            "Primary Email": emails[0] if emails else "",
            "Phone Number": phones[0] if phones else "",
            "Job Title": current_job.get('title', ''),
            "Company": current_job.get('company', ''),
            "Location": location,
            "City": city,
            "Province/State": province_state,
            "Country": country,
            "Status": "New",
            "Skills": ", ".join(contact_data.get('skills', [])[:5]),
            "SignalHire ID": contact_id,
            "Source Search": "SignalHire Agent - Direct Fetch",
            "Primary Trade": "Heavy Equipment Technician",
            "Trade Category": "Construction",
            "Date Added": "2025-09-28T22:00:00.000Z"
        }
        
        created_record = table.create(record)
        print(f"✅ {name} added to Airtable! Record ID: {created_record['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add {name} to Airtable: {e}")
        return False

async def main():
    print("🔍 Direct Contact Fetching - No Callbacks Required")
    
    # Load cached contacts
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        all_contacts = json.load(f)
    
    contact_ids = list(all_contacts.keys())
    print(f"📂 Found {len(contact_ids)} total contacts")
    
    # Try with first 5 contacts
    test_contacts = contact_ids[:5]
    print(f"🧪 Testing with {len(test_contacts)} contacts")
    
    success_count = 0
    for i, contact_id in enumerate(test_contacts):
        print(f"\n--- {i+1}/{len(test_contacts)}: {contact_id} ---")
        
        # Try direct fetch
        contact_data = await try_direct_contact_fetch(contact_id)
        
        if contact_data and contact_data.get('contacts'):
            # Add to Airtable
            if await add_to_airtable(contact_data, contact_id):
                success_count += 1
        else:
            # Fall back to cached profile data (no contacts but still useful)
            cached_profile = all_contacts[contact_id]['profile']
            print(f"📋 Using cached profile for {cached_profile.get('fullName', 'Unknown')}")
            if await add_to_airtable(cached_profile, contact_id):
                success_count += 1
        
        # Small delay to be respectful
        await asyncio.sleep(0.5)
    
    print(f"\n📊 Results: {success_count}/{len(test_contacts)} contacts processed")

if __name__ == "__main__":
    asyncio.run(main())