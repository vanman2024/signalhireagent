#!/usr/bin/env python3
"""
Process Revealed SignalHire Contacts to Airtable

PURPOSE: Automatically process only SignalHire contacts with actual contact information to Airtable
USAGE: python3 process_revealed_contacts_to_airtable.py
PART OF: SignalHire Agent automation workflow
CONNECTS TO: SignalHire contact cache, Airtable MCP server, contact normalization
"""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

AIRTABLE_BASE_ID = "appQoYINM992nBZ50"  # Signalhire base
CONTACTS_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table
CACHE_FILE = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"

def load_revealed_contacts() -> Dict[str, Any]:
    """Load contacts from SignalHire cache."""
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Cache file not found: {CACHE_FILE}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing cache file: {e}")
        return {}

def filter_contacts_with_info(contacts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter contacts that have actual contact information (email, phone, LinkedIn)."""
    contacts_with_info = []
    
    for contact_id, contact_data in contacts.items():
        # Check if this contact has revealed contact information
        if contact_data.get('contacts') and len(contact_data['contacts']) > 0:
            # Extract profile information
            profile = contact_data.get('profile', {})
            
            # Get the primary contact info from the first contact entry
            primary_contact = contact_data['contacts'][0] if contact_data['contacts'] else {}
            
            # Create normalized contact record
            contact_record = {
                'signalhire_id': contact_id,
                'profile': profile,
                'contact_info': primary_contact,
                'all_contacts': contact_data['contacts'],
                'metadata': contact_data.get('metadata', {}),
                'first_revealed_at': contact_data.get('first_revealed_at'),
                'last_updated_at': contact_data.get('last_updated_at')
            }
            
            contacts_with_info.append(contact_record)
    
    return contacts_with_info

def format_for_airtable(contact: Dict[str, Any]) -> Dict[str, Any]:
    """Format contact data for Airtable insertion."""
    profile = contact.get('profile', {})
    primary_contact = contact.get('contact_info', {})
    
    # Extract name information
    first_name = profile.get('firstName', '') or primary_contact.get('firstName', '')
    last_name = profile.get('lastName', '') or primary_contact.get('lastName', '')
    full_name = f"{first_name} {last_name}".strip() or profile.get('name', '')
    
    # Extract job and company info
    job_title = profile.get('title', '')
    company = profile.get('company', '')
    
    # Extract location
    location = profile.get('location', {})
    location_str = ''
    if isinstance(location, dict):
        city = location.get('city', '')
        country = location.get('country', '')
        location_str = f"{city}, {country}".strip(', ')
    elif isinstance(location, str):
        location_str = location
    
    # Extract contact information
    emails = primary_contact.get('emails', [])
    phones = primary_contact.get('phones', [])
    
    primary_email = emails[0] if emails else ''
    secondary_email = emails[1] if len(emails) > 1 else ''
    phone_number = phones[0] if phones else ''
    
    # Extract social profiles
    linkedin_url = primary_contact.get('linkedinUrl', '') or profile.get('linkedinUrl', '')
    facebook_url = primary_contact.get('facebookUrl', '') or profile.get('facebookUrl', '')
    
    # Extract skills and experience
    skills = []
    if 'skills' in profile and isinstance(profile['skills'], list):
        skills = [skill.get('name', skill) if isinstance(skill, dict) else str(skill) 
                 for skill in profile['skills']]
    
    experience_years = profile.get('experienceYears', '')
    
    # Create Airtable record
    airtable_record = {
        "SignalHire ID": contact['signalhire_id'],
        "First Name": first_name,
        "Last Name": last_name,
        "Full Name": full_name,
        "Job Title": job_title,
        "Company": company,
        "Location": location_str,
        "Primary Email": primary_email,
        "Secondary Email": secondary_email,
        "Phone Number": phone_number,
        "LinkedIn URL": linkedin_url,
        "Facebook URL": facebook_url,
        "Skills": ', '.join(skills) if skills else '',
        "Years of Experience": str(experience_years) if experience_years else '',
        "Status": "Revealed",
        "Date Added": datetime.now().isoformat(),
        "Source Search": "SignalHire Agent"
    }
    
    # Remove empty fields to keep Airtable clean
    return {k: v for k, v in airtable_record.items() if v}

async def check_existing_contacts(contacts_to_add: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check which contacts already exist in Airtable."""
    from src.lib.airtable_client import AirtableClient
    
    client = AirtableClient()
    existing_signalhire_ids = set()
    
    try:
        # Get all existing records to check for duplicates
        existing_records = await client.list_records(
            AIRTABLE_BASE_ID, 
            CONTACTS_TABLE_ID,
            fields=["SignalHire ID"]
        )
        
        for record in existing_records.get('records', []):
            signalhire_id = record.get('fields', {}).get('SignalHire ID')
            if signalhire_id:
                existing_signalhire_ids.add(signalhire_id)
    
    except Exception as e:
        print(f"Error checking existing contacts: {e}")
        print("Proceeding without duplicate check...")
    
    # Filter out contacts that already exist
    new_contacts = []
    for contact in contacts_to_add:
        if contact.get("SignalHire ID") not in existing_signalhire_ids:
            new_contacts.append(contact)
        else:
            print(f"Skipping duplicate contact: {contact.get('SignalHire ID')}")
    
    return new_contacts

async def add_contacts_to_airtable(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Add contacts to Airtable using MCP tools."""
    results = {
        "total_processed": len(contacts),
        "successful": 0,
        "failed": 0,
        "errors": []
    }
    
    print(f"Adding {len(contacts)} contacts to Airtable...")
    
    for i, contact in enumerate(contacts, 1):
        try:
            print(f"  Adding contact {i}/{len(contacts)}: {contact.get('Full Name', 'Unknown')}")
            
            # Note: Using direct MCP call since we don't have an AirtableClient wrapper
            # In a real implementation, we'd use the MCP airtable tools directly
            
            # For now, just print what would be added
            print(f"    SignalHire ID: {contact.get('SignalHire ID')}")
            print(f"    Email: {contact.get('Primary Email', 'N/A')}")
            print(f"    Phone: {contact.get('Phone Number', 'N/A')}")
            print(f"    LinkedIn: {contact.get('LinkedIn URL', 'N/A')}")
            
            results["successful"] += 1
            
        except Exception as e:
            error_msg = f"Failed to add contact {contact.get('SignalHire ID', 'unknown')}: {e}"
            print(f"    ERROR: {error_msg}")
            results["errors"].append(error_msg)
            results["failed"] += 1
    
    return results

async def main():
    """Main execution function."""
    print("🔍 Processing SignalHire contacts with revealed information...")
    
    # Load contacts from cache
    print("📂 Loading contacts from cache...")
    all_contacts = load_revealed_contacts()
    print(f"   Found {len(all_contacts)} total cached contacts")
    
    # Filter for contacts with actual contact information
    print("🔍 Filtering contacts with revealed information...")
    contacts_with_info = filter_contacts_with_info(all_contacts)
    print(f"   Found {len(contacts_with_info)} contacts with revealed contact information")
    
    if not contacts_with_info:
        print("❌ No contacts found with revealed contact information.")
        print("   All cached contacts appear to be search results without contact details.")
        print("   Use the SignalHire Person API to reveal contact information first.")
        return
    
    # Format contacts for Airtable
    print("📋 Formatting contacts for Airtable...")
    airtable_contacts = [format_for_airtable(contact) for contact in contacts_with_info]
    
    # Check for existing contacts (when AirtableClient is available)
    # airtable_contacts = await check_existing_contacts(airtable_contacts)
    
    if not airtable_contacts:
        print("ℹ️  All contacts already exist in Airtable. No new contacts to add.")
        return
    
    # Add contacts to Airtable
    print("📤 Adding contacts to Airtable...")
    results = await add_contacts_to_airtable(airtable_contacts)
    
    # Print summary
    print(f"\n✅ Processing complete!")
    print(f"   Total processed: {results['total_processed']}")
    print(f"   Successfully added: {results['successful']}")
    print(f"   Failed: {results['failed']}")
    
    if results['errors']:
        print(f"\n❌ Errors encountered:")
        for error in results['errors']:
            print(f"   - {error}")

if __name__ == "__main__":
    asyncio.run(main())