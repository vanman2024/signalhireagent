#!/usr/bin/env python3
"""
Test adding a few contacts with correct field values
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Airtable configuration from environment
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

async def test_few_contacts():
    """Test adding just 3 contacts with correct field structure"""
    
    # Load cached contacts
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        all_contacts = json.load(f)
    
    api = Api(os.getenv('AIRTABLE_API_KEY'))
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
    
    # Test with just 3 contacts
    test_contacts = list(all_contacts.items())[:3]
    print(f"🧪 Testing with {len(test_contacts)} contacts...")
    
    for i, (contact_id, contact_data) in enumerate(test_contacts):
        profile = contact_data.get('profile', {})
        name = profile.get('fullName', 'Unknown')
        experience = profile.get('experience', [])
        current_job = experience[0] if experience else {}
        
        # Parse location into components
        location = profile.get('location', '')
        location_parts = location.split(', ') if location else []
        city = location_parts[0] if len(location_parts) > 0 else ''
        province_state = location_parts[1] if len(location_parts) > 1 else ''
        country = location_parts[2] if len(location_parts) > 2 else location_parts[1] if len(location_parts) == 2 else ''
        
        try:
            record = {
                "Full Name": name,
                "Job Title": current_job.get('title', ''),
                "Company": current_job.get('company', ''),
                "Location": location,
                "City": city,
                "Province/State": province_state,
                "Country": country,
                "Status": "New",
                "Skills": ", ".join(profile.get('skills', [])[:5]),
                "SignalHire ID": contact_id,
                "Source Search": "SignalHire Agent - Test Import",
                "Primary Trade": "Heavy Duty Equipment Technician",
                "Trade Category": "Heavy Equipment"
            }
            
            created_record = table.create(record)
            print(f"✅ {i+1}/{len(test_contacts)}: {name} -> {created_record['id']}")
            
        except Exception as e:
            print(f"❌ {i+1}/{len(test_contacts)}: {name} failed: {e}")
        
        await asyncio.sleep(0.2)  # Small delay
    
    print("🧪 Test complete!")

if __name__ == "__main__":
    asyncio.run(test_few_contacts())