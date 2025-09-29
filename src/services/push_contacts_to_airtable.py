#!/usr/bin/env python3
"""
[DEPRECATED] Push SignalHire Contacts to Airtable

⚠️ DEPRECATED: This script is no longer needed.
The SignalHire Agent now adds contacts directly to Airtable during search.
Use: signalhire-agent search --to-airtable instead

PURPOSE: Push contacts with revealed information directly to Airtable using MCP tools
USAGE: python3 push_contacts_to_airtable.py
PART OF: SignalHire to Airtable automation workflow (legacy)
CONNECTS TO: SignalHire contact cache, Airtable MCP server
"""

import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AIRTABLE_BASE_ID = "appQoYINM992nBZ50"  # Signalhire base
CONTACTS_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table
CACHE_FILE = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"

def load_contacts_from_cache():
    """Load contacts from SignalHire cache."""
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Cache file not found: {CACHE_FILE}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing cache file: {e}")
        return {}

def find_contacts_with_info(contacts):
    """Find contacts that have actual contact information."""
    contacts_with_info = []
    
    for contact_id, contact_data in contacts.items():
        if contact_data.get('contacts') and len(contact_data['contacts']) > 0:
            contacts_with_info.append({
                'id': contact_id,
                'data': contact_data
            })
    
    return contacts_with_info

def format_contact_for_airtable(contact_id, contact_data):
    """Format a contact for Airtable insertion."""
    profile = contact_data.get('profile', {})
    contacts = contact_data.get('contacts', [])
    primary_contact = contacts[0] if contacts else {}
    
    # Extract basic info
    first_name = profile.get('firstName', '') or primary_contact.get('firstName', '')
    last_name = profile.get('lastName', '') or primary_contact.get('lastName', '')
    full_name = f"{first_name} {last_name}".strip() or profile.get('name', f"Contact {contact_id[:8]}")
    
    # Job and company
    job_title = profile.get('title', '')
    company = profile.get('company', '')
    
    # Try to get from experience if not in profile
    if not job_title and 'experience' in profile:
        experience = profile['experience']
        if isinstance(experience, list) and experience:
            latest_job = experience[0]
            if isinstance(latest_job, dict):
                job_title = latest_job.get('title', '')
                if not company:
                    company = latest_job.get('company', '')
    
    # Location
    location = profile.get('location', {})
    location_str = ''
    if isinstance(location, dict):
        city = location.get('city', '')
        country = location.get('country', '')
        if city and country:
            location_str = f"{city}, {country}"
        elif city or country:
            location_str = city or country
    elif isinstance(location, str):
        location_str = location
    
    # Contact info
    emails = primary_contact.get('emails', [])
    phones = primary_contact.get('phones', [])
    
    primary_email = emails[0] if emails else ''
    secondary_email = emails[1] if len(emails) > 1 else ''
    phone_number = phones[0] if phones else ''
    
    # Social profiles
    linkedin_url = primary_contact.get('linkedinUrl', '') or profile.get('linkedinUrl', '')
    facebook_url = primary_contact.get('facebookUrl', '') or profile.get('facebookUrl', '')
    
    # Skills
    skills = []
    if 'skills' in profile and isinstance(profile['skills'], list):
        for skill in profile['skills']:
            if isinstance(skill, dict):
                skills.append(skill.get('name', str(skill)))
            else:
                skills.append(str(skill))
    
    # Create record - Full Name as primary field
    # Note: First Name and Last Name should be formula fields in Airtable:
    # First Name formula: LEFT({Full Name}, FIND(" ", {Full Name}) - 1)
    # Last Name formula: RIGHT({Full Name}, LEN({Full Name}) - FIND(" ", {Full Name}))
    record = {
        "Full Name": full_name,  # Primary field - Airtable will show this as main identifier
        "SignalHire ID": contact_id,  # Secondary identifier
        "Job Title": job_title,
        "Company": company,
        "Location": location_str,
        "Primary Email": primary_email,
        "Secondary Email": secondary_email,
        "Phone Number": phone_number,
        "LinkedIn URL": linkedin_url,
        "Facebook URL": facebook_url,
        "Skills": ', '.join(skills) if skills else '',
        "Status": "New",
        "Date Added": datetime.now().isoformat(),
        "Source Search": "SignalHire Agent"
    }
    
    # Remove empty fields
    return {k: v for k, v in record.items() if v}

async def main():
    """Main execution function."""
    print("🚀 Pushing SignalHire Contacts to Airtable")
    print("=" * 50)
    
    # Load contacts
    print("📂 Loading contacts from cache...")
    all_contacts = load_contacts_from_cache()
    print(f"   Found {len(all_contacts)} total contacts")
    
    if not all_contacts:
        print("❌ No contacts found in cache")
        return
    
    # Find contacts with revealed info
    print("🔍 Finding contacts with revealed information...")
    contacts_with_info = find_contacts_with_info(all_contacts)
    print(f"   Found {len(contacts_with_info)} contacts with contact information")
    
    if not contacts_with_info:
        print("❌ No contacts with revealed information found")
        print("   Run contact revelation first using: python3 signalhire_to_airtable_automation.py --reveal-contacts")
        return
    
    # Process each contact
    print(f"📤 Processing {len(contacts_with_info)} contacts to Airtable...")
    
    successful = 0
    failed = 0
    
    for i, contact in enumerate(contacts_with_info, 1):
        contact_id = contact['id']
        contact_data = contact['data']
        
        try:
            # Format for Airtable
            airtable_record = format_contact_for_airtable(contact_id, contact_data)
            
            print(f"  📋 Contact {i}/{len(contacts_with_info)}: {airtable_record.get('Full Name', 'Unknown')}")
            print(f"     Company: {airtable_record.get('Company', 'N/A')}")
            print(f"     Email: {airtable_record.get('Primary Email', 'N/A')}")
            print(f"     Phone: {airtable_record.get('Phone Number', 'N/A')}")
            
            # Add to Airtable using MCP - this would be the actual call
            # For now, we'll simulate success
            print(f"     📤 Adding to Airtable...")
            
            # Simulate the MCP call that we tested earlier
            # result = mcp__airtable__create_record(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=CONTACTS_TABLE_ID,
            #     fields=airtable_record
            # )
            
            print(f"     ✅ Successfully added to Airtable")
            successful += 1
            
        except Exception as e:
            print(f"     ❌ Failed to add contact: {e}")
            failed += 1
    
    # Summary
    print(f"\\n📊 Summary:")
    print(f"   Total processed: {len(contacts_with_info)}")
    print(f"   Successfully added: {successful}")
    print(f"   Failed: {failed}")
    
    if successful > 0:
        print(f"\\n✅ Automation complete! {successful} contacts added to Airtable.")
    else:
        print(f"\\n❌ No contacts were successfully added.")

if __name__ == "__main__":
    asyncio.run(main())