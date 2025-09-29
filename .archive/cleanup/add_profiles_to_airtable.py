#!/usr/bin/env python3
"""
Add existing profile data to Airtable without waiting for contact revelations
"""

import json
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Airtable configuration
AIRTABLE_BASE_ID = "appNLDGCRSp0J8lMF"
AIRTABLE_TABLE_ID = "tblkPGvvZGCJzYNZw"

def main():
    # Load cached contacts
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        all_contacts = json.load(f)
    
    print(f"📂 Found {len(all_contacts)} total contacts")
    
    # Initialize Airtable API
    api = Api(os.getenv('AIRTABLE_API_KEY'))
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
    
    added_count = 0
    
    # Process all contacts (limit to first 10 for testing)
    contacts_to_process = list(all_contacts.items())[:10]
    
    for contact_id, contact_data in contacts_to_process:
        profile = contact_data.get('profile', {})
        name = profile.get('fullName', 'Unknown')
        location = profile.get('location', '')
        
        # Extract job info
        experience = profile.get('experience', [])
        current_job = experience[0] if experience else {}
        
        print(f"📝 Adding {name} to Airtable (profile only)...")
        
        try:
            # Create Airtable record with available profile data
            record = {
                "SignalHire ID": contact_id,
                "Full Name": name,
                "Primary Email": "",  # Empty until revealed
                "Primary Phone": "",  # Empty until revealed 
                "Job Title": current_job.get('title', ''),
                "Company": current_job.get('company', ''),
                "Location": location,
                "Status": "Profile Added - Contacts Pending",
                "Source Search": "SignalHire Agent - Profile Import",
                "Primary Trade": "Heavy Equipment Technician",
                "Trade Category": "Construction",
                "Skills": ", ".join(profile.get('skills', [])[:5])  # First 5 skills
            }
            
            created_record = table.create(record)
            print(f"✅ {name} added to Airtable! Record ID: {created_record['id']}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Failed to add {name} to Airtable: {e}")
    
    print(f"\n📊 Summary: Added {added_count}/{len(contacts_to_process)} profiles to Airtable")
    print("🔄 Contact information can be added later when revelations complete")

if __name__ == "__main__":
    main()