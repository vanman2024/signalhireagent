#!/usr/bin/env python3
"""
Production SignalHire to Airtable automation using MCP tools.
This script automatically processes revealed contacts and pushes them to Airtable.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import existing SignalHire client
from src.services.signalhire_client import SignalHireClient
from src.lib.contact_cache import ContactCache

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
AIRTABLE_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table


def generate_signalhire_profile_url(uid: str) -> str:
    """Generate SignalHire profile URL from UID."""
    return f"https://app.signalhire.com/profile/{uid}"


def format_contact_for_airtable(contact_data: dict, source_search: str = "Automated") -> dict:
    """Format contact data for Airtable insertion."""
    
    # Handle cache format (revealed contacts)
    if 'profile' in contact_data:
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
        # API format (search results) - basic info only
        uid = contact_data.get('uid', '')
        full_name = contact_data.get('fullName', '')
        location = contact_data.get('location', '')
        
        # Get current title and company from experience
        experience = contact_data.get('experience', [])
        current_title = experience[0].get('title', '') if experience else ''
        current_company = experience[0].get('company', '') if experience else ''
        
        # API format doesn't have revealed contacts
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


def load_revealed_heavy_equipment_contacts() -> List[dict]:
    """Load heavy equipment contacts from SignalHire cache."""
    cache_path = Path("/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json")
    
    if not cache_path.exists():
        print("No cache file found")
        return []
    
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        
        heavy_equipment_contacts = []
        
        for uid, cached_contact in cache_data.items():
            if not cached_contact.get('profile'):
                continue
                
            profile = cached_contact['profile']
            location = profile.get('location', '').lower()
            
            # Only Canada
            if 'canada' not in location:
                continue
                
            # Check title for heavy equipment
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
                contact_with_uid = {'uid': uid, **cached_contact}
                heavy_equipment_contacts.append(contact_with_uid)
        
        return heavy_equipment_contacts
        
    except Exception as e:
        print(f"Error loading cache: {e}")
        return []


async def main():
    """Main automation function."""
    print("SignalHire to Airtable Automation")
    print("=" * 40)
    
    # Load revealed heavy equipment contacts
    print("Loading revealed heavy equipment contacts from cache...")
    revealed_contacts = load_revealed_heavy_equipment_contacts()
    print(f"Found {len(revealed_contacts)} heavy equipment professionals")
    
    if not revealed_contacts:
        print("No contacts found to process")
        return
    
    # Check existing contacts in Airtable for deduplication
    print("Checking existing contacts in Airtable...")
    try:
        existing_records = await mcp__airtable__list_records(
            baseId=AIRTABLE_BASE_ID,
            tableId=AIRTABLE_TABLE_ID
        )
        
        existing_signalhire_ids = set()
        for record in existing_records:
            signalhire_id = record.get('fields', {}).get('SignalHire ID')
            if signalhire_id:
                existing_signalhire_ids.add(signalhire_id)
        
        print(f"Found {len(existing_signalhire_ids)} existing contacts in Airtable")
        
    except Exception as e:
        print(f"Error checking existing contacts: {e}")
        existing_signalhire_ids = set()
    
    # Filter out duplicates
    new_contacts = []
    skipped_count = 0
    
    for contact in revealed_contacts:
        uid = contact.get('uid')
        if uid in existing_signalhire_ids:
            skipped_count += 1
            continue
        new_contacts.append(contact)
    
    print(f"Processing {len(new_contacts)} new contacts (skipping {skipped_count} duplicates)")
    
    if not new_contacts:
        print("All contacts already exist in Airtable")
        return
    
    # Push contacts to Airtable
    print("Pushing contacts to Airtable...")
    success_count = 0
    error_count = 0
    
    for i, contact in enumerate(new_contacts, 1):
        try:
            # Format contact for Airtable
            airtable_record = format_contact_for_airtable(contact, "Cache - Heavy Equipment")
            
            # Create record in Airtable
            created_record = await mcp__airtable__create_record(
                baseId=AIRTABLE_BASE_ID,
                tableId=AIRTABLE_TABLE_ID,
                fields=airtable_record
            )
            
            success_count += 1
            print(f"{i:2d}. {airtable_record['Full Name']} - {airtable_record['Job Title']} at {airtable_record['Company']}")
            
            # Add a small delay to avoid rate limiting
            await asyncio.sleep(0.1)
            
        except Exception as e:
            error_count += 1
            print(f"Error creating record for {contact.get('uid', 'unknown')}: {e}")
    
    print(f"\nAutomation Complete!")
    print(f"Successfully added: {success_count} contacts")
    print(f"Errors: {error_count} contacts")
    print(f"Total processed: {len(new_contacts)} contacts")
    print(f"View in Airtable: https://airtable.com/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}")


if __name__ == "__main__":
    asyncio.run(main())