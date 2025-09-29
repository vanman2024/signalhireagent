#!/usr/bin/env python3
"""Push SignalHire contacts to Airtable Contacts table."""

import json
from pathlib import Path
from datetime import datetime

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
AIRTABLE_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table

def generate_signalhire_profile_url(uid: str) -> str:
    """Generate SignalHire profile URL from UID."""
    return f"https://app.signalhire.com/profile/{uid}"

def format_contact_for_airtable(contact_data: dict, source_search: str = "Cache") -> dict:
    """Format contact data for Airtable insertion."""
    
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

def filter_heavy_equipment_contacts(contacts):
    """Filter for heavy equipment professionals in Canada."""
    heavy_equipment_contacts = []
    
    for contact in contacts:
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
    
    return heavy_equipment_contacts

def main():
    print("Pushing SignalHire contacts to Airtable")
    print("=" * 40)
    
    # Load revealed contacts from cache
    revealed_contacts = load_revealed_contacts()
    print(f"Found {len(revealed_contacts)} revealed contacts in cache")
    
    if not revealed_contacts:
        print("No contacts found to push")
        return
    
    # Filter for heavy equipment professionals in Canada
    heavy_equipment_contacts = filter_heavy_equipment_contacts(revealed_contacts)
    print(f"Found {len(heavy_equipment_contacts)} heavy equipment professionals in Canada")
    
    if not heavy_equipment_contacts:
        print("No heavy equipment contacts found")
        return
    
    # Format for Airtable and push
    print("\nPushing contacts to Airtable...")
    
    for i, contact in enumerate(heavy_equipment_contacts, 1):
        try:
            airtable_record = format_contact_for_airtable(contact, "Heavy Equipment Cache")
            
            print(f"{i}. {airtable_record['Full Name']} - {airtable_record['Job Title']} at {airtable_record['Company']}")
            print(f"   SignalHire Profile: {airtable_record['SignalHire Profile']}")
            
            # Show what will be inserted (for verification)
            if i == 1:
                print(f"   Sample record structure:")
                for key, value in airtable_record.items():
                    if value:  # Only show non-empty fields
                        print(f"     {key}: {value}")
                print()
            
        except Exception as e:
            print(f"Error formatting contact {i}: {e}")
    
    print(f"\nReady to push {len(heavy_equipment_contacts)} contacts to Airtable")
    print("Table: Contacts")
    print(f"Base ID: {AIRTABLE_BASE_ID}")
    print(f"Table ID: {AIRTABLE_TABLE_ID}")

if __name__ == "__main__":
    main()