#!/usr/bin/env python3
"""
Fix missing fields in Airtable records that were imported without complete data.
Adds Date Added field and ensures all records have consistent field mapping.
"""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Airtable configuration from environment
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

async def fix_airtable_records():
    """Fix all records in Airtable that are missing required fields"""
    
    api = Api(os.getenv('AIRTABLE_API_KEY'))
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
    
    # Get all records
    print("📋 Fetching all records from Airtable...")
    all_records = table.all()
    print(f"📊 Found {len(all_records)} records to check")
    
    # Load cached contacts for SignalHire ID mapping
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        cached_contacts = json.load(f)
    
    # Current date for Date Added field
    current_date = datetime.now().isoformat()
    
    updates_needed = []
    fixed_count = 0
    
    for record in all_records:
        record_id = record['id']
        fields = record['fields']
        full_name = fields.get('Full Name', '')
        
        # Check what fields are missing
        missing_fields = {}
        
        # Add Date Added if missing
        if 'Date Added' not in fields:
            missing_fields['Date Added'] = current_date
        
        # Add Source Search if missing
        if 'Source Search' not in fields:
            missing_fields['Source Search'] = "SignalHire Agent - Complete Import"
        
        # Add Primary Trade if missing
        if 'Primary Trade' not in fields:
            missing_fields['Primary Trade'] = "Heavy Duty Equipment Technician"
        
        # Add Trade Category if missing
        if 'Trade Category' not in fields:
            missing_fields['Trade Category'] = "Heavy Equipment"
        
        # Try to find and add SignalHire ID if missing
        if 'SignalHire ID' not in fields:
            # Try to match by full name in cached contacts
            for contact_id, contact_data in cached_contacts.items():
                profile = contact_data.get('profile', {})
                cached_name = profile.get('fullName', '')
                if cached_name == full_name:
                    missing_fields['SignalHire ID'] = contact_id
                    break
        
        # If we found missing fields, prepare update
        if missing_fields:
            updates_needed.append({
                'id': record_id,
                'fields': missing_fields
            })
            print(f"🔧 {full_name}: Adding {len(missing_fields)} missing fields")
            fixed_count += 1
    
    # Batch update records (Airtable allows up to 10 records per batch)
    if updates_needed:
        print(f"\n📝 Updating {len(updates_needed)} records with missing fields...")
        
        # Process in batches of 10
        for i in range(0, len(updates_needed), 10):
            batch = updates_needed[i:i+10]
            try:
                table.batch_update(batch)
                print(f"✅ Updated batch {i//10 + 1}: {len(batch)} records")
                await asyncio.sleep(0.2)  # Small delay between batches
            except Exception as e:
                print(f"❌ Failed to update batch {i//10 + 1}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total records: {len(all_records)}")
    print(f"   Records fixed: {fixed_count}")
    print(f"   Records updated: {len(updates_needed)}")
    
    # Show sample of updated record
    if updates_needed:
        print(f"\n📋 Sample fixed record fields:")
        sample_fields = updates_needed[0]['fields']
        for field_name, field_value in sample_fields.items():
            print(f"   + {field_name}: {field_value}")

if __name__ == "__main__":
    asyncio.run(fix_airtable_records())