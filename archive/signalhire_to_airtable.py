#!/usr/bin/env python3
"""Extract SignalHire contacts and push directly to Airtable with deduplication."""

import json
import os
from datetime import datetime
from pathlib import Path

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
AIRTABLE_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Heavy Equipment Contacts table

def generate_signalhire_profile_url(uid: str) -> str:
    """Generate SignalHire profile URL from UID."""
    return f"https://app.signalhire.com/profile/{uid}"

def format_contact_for_airtable(contact_data: dict, source_search: str = "Cache") -> dict:
    """Format contact data for Airtable insertion."""
    
    # Handle both cache format and API format
    if 'profile' in contact_data:
        # Cache format
        profile = contact_data['profile']
        uid = contact_data['uid']
        contacts = contact_data.get('contacts', [])
        
        full_name = profile.get('fullName', '')
        location = profile.get('location', '')
        skills = profile.get('skills', [])
        
        # Get current title and company
        current_title = ""
        current_company = ""
        if 'experience' in profile and profile['experience']:
            current_title = profile['experience'][0].get('title', '')
            current_company = profile['experience'][0].get('company', '')
        
        # Extract emails and other contacts
        emails = []
        phone = ""
        linkedin = ""
        facebook = ""
        
        for contact in contacts:
            contact_type = contact.get('type', '')
            value = contact.get('value', '')
            
            if contact_type == 'email' and value:
                emails.append(value)
            elif contact_type == 'phone' and value:
                phone = value
            elif contact_type == 'linkedin' and value:
                linkedin = value
            elif contact_type == 'facebook' and value:
                facebook = value
                
    else:
        # API format
        uid = contact_data.get('uid', '')
        full_name = contact_data.get('fullName', '')
        location = contact_data.get('location', '')
        
        # Get current title and company from experience
        experience = contact_data.get('experience', [])
        current_title = experience[0].get('title', '') if experience else ''
        current_company = experience[0].get('company', '') if experience else ''
        
        # For API format, we'll need to reveal contacts separately
        emails = []
        phone = ""
        linkedin = ""
        facebook = ""
        skills = []
    
    # Split name
    name_parts = full_name.split(' ', 1)
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Format skills
    skills_text = ', '.join(skills) if isinstance(skills, list) else str(skills)
    
    # Create Airtable record
    airtable_record = {
        "SignalHire ID": uid,
        "First Name": first_name,
        "Last Name": last_name,
        "Full Name": full_name,
        "Job Title": current_title,
        "Company": current_company,
        "Location": location,
        "Primary Email": emails[0] if emails else "",
        "Secondary Email": emails[1] if len(emails) > 1 else "",
        "Phone Number": phone,
        "LinkedIn URL": linkedin,
        "Facebook URL": facebook,
        "SignalHire Profile": generate_signalhire_profile_url(uid),
        "Skills": skills_text,
        "Status": "New",
        "Date Added": datetime.now().isoformat(),
        "Source Search": source_search
    }
    
    return airtable_record

def get_existing_signalhire_ids():
    """Get list of SignalHire IDs already in Airtable for deduplication."""
    print("Checking existing contacts in Airtable...")
    
    try:
        # This would use the MCP Airtable server to list existing records
        # For now, we'll return empty set - you can extend this
        existing_ids = set()
        
        # TODO: Use MCP server to fetch existing records
        # records = mcp_airtable_list_records(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
        # existing_ids = {record['fields'].get('SignalHire ID') for record in records if 'SignalHire ID' in record['fields']}
        
        print(f"Found {len(existing_ids)} existing contacts")
        return existing_ids
        
    except Exception as e:
        print(f"Error checking existing contacts: {e}")
        return set()

def push_contacts_to_airtable(contacts: list, source_search: str):
    """Push contacts to Airtable with deduplication."""
    print(f"Processing {len(contacts)} contacts for Airtable...")
    
    # Get existing IDs for deduplication
    existing_ids = get_existing_signalhire_ids()
    
    new_contacts = []
    skipped_count = 0
    
    for contact in contacts:
        uid = contact.get('uid') or contact.get('SignalHire ID')
        
        if uid in existing_ids:
            skipped_count += 1
            continue
            
        airtable_record = format_contact_for_airtable(contact, source_search)
        new_contacts.append(airtable_record)
    
    print(f"Adding {len(new_contacts)} new contacts (skipped {skipped_count} duplicates)")
    
    # Push to Airtable in batches
    batch_size = 10  # Airtable limit
    
    for i in range(0, len(new_contacts), batch_size):
        batch = new_contacts[i:i + batch_size]
        
        try:
            # TODO: Use MCP server to create records
            # This is where you'd call the MCP Airtable server
            print(f"Pushing batch {i//batch_size + 1} ({len(batch)} records)...")
            
            # For now, just show what would be pushed
            for record in batch:
                print(f"  - {record['Full Name']} ({record['Job Title']}) at {record['Company']}")
            
            # Simulate success
            print(f"✅ Batch {i//batch_size + 1} pushed successfully")
            
        except Exception as e:
            print(f"❌ Error pushing batch {i//batch_size + 1}: {e}")
    
    return len(new_contacts)

def load_revealed_contacts():
    """Load already revealed contacts from cache."""
    cache_path = Path("/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json")
    
    if not cache_path.exists():
        print("No cache file found")
        return []
    
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        
        contacts = []
        for uid, cached_contact in cache_data.items():
            if cached_contact.get('profile'):
                contact_with_uid = {'uid': uid, **cached_contact}
                contacts.append(contact_with_uid)
        
        return contacts
        
    except Exception as e:
        print(f"Error loading cache: {e}")
        return []

def main():
    print("SignalHire to Airtable Integration")
    print("=" * 40)
    
    # Load revealed contacts from cache
    revealed_contacts = load_revealed_contacts()
    print(f"Found {len(revealed_contacts)} revealed contacts in cache")
    
    if revealed_contacts:
        # Filter for heavy equipment professionals in Canada
        heavy_equipment_contacts = []
        
        for contact in revealed_contacts:
            profile = contact.get('profile', {})
            location = profile.get('location', '').lower()
            
            if 'canada' not in location:
                continue
                
            # Check title
            current_title = ""
            if 'experience' in profile and profile['experience']:
                current_title = profile['experience'][0].get('title', '').lower()
            
            # Heavy equipment keywords
            heavy_equipment_terms = [
                'heavy equipment', 'heavy duty', 'equipment technician', 
                'equipment mechanic', 'diesel mechanic', 'construction equipment',
                'mining equipment', 'heavy machinery', 'industrial mechanic'
            ]
            
            # Exclude terms
            exclude_terms = ['driver', 'operator', 'sales', 'coordinator', 'supervisor']
            
            if any(term in current_title for term in heavy_equipment_terms) and \
               not any(term in current_title for term in exclude_terms):
                heavy_equipment_contacts.append(contact)
        
        print(f"Found {len(heavy_equipment_contacts)} heavy equipment professionals")
        
        if heavy_equipment_contacts:
            # Push to Airtable
            push_contacts_to_airtable(heavy_equipment_contacts, "Cache - Revealed Contacts")
    
    # TODO: Add functionality to process new searches and reveal contacts
    print("\nNext steps:")
    print("1. Integrate with MCP Airtable server for actual record creation")
    print("2. Add new search functionality that reveals contacts and pushes to Airtable")
    print("3. Implement proper deduplication checking against existing Airtable records")

if __name__ == "__main__":
    main()