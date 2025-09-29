#!/usr/bin/env python3
"""
Import already revealed contact information from SignalHire to Airtable.
This script checks SignalHire for contacts that already have revealed information
and imports that data directly into Airtable.
"""

import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
SIGNALHIRE_API_KEY = os.getenv('SIGNALHIRE_API_KEY')

async def get_airtable_contacts():
    """Get all contacts from Airtable with SignalHire IDs."""
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
    
    # Get contacts with SignalHire IDs
    contacts_with_ids = []
    for record in all_records:
        fields = record['fields']
        signalhire_id = fields.get('SignalHire ID')
        full_name = fields.get('Full Name', '')
        
        if signalhire_id:
            contacts_with_ids.append({
                'airtable_id': record['id'],
                'signalhire_id': signalhire_id,
                'full_name': full_name,
                'current_fields': fields
            })
    
    return contacts_with_ids

async def get_signalhire_contact_info(contact_id):
    """Get contact information from SignalHire directly."""
    headers = {
        'apikey': SIGNALHIRE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Try to get the contact information directly
            response = await client.get(
                f'https://www.signalhire.com/api/v1/candidate/{contact_id}',
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ {contact_id}: HTTP {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ {contact_id}: {e}")
            return None

async def update_airtable_contact(airtable_id, contact_data, current_fields):
    """Update Airtable contact with revealed information."""
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    update_fields = {}
    
    # Extract emails
    emails = contact_data.get('emails', [])
    if emails and not current_fields.get('Primary Email'):
        primary_email = emails[0].get('email')
        if primary_email:
            update_fields['Primary Email'] = primary_email
    
    if len(emails) > 1 and not current_fields.get('Secondary Email'):
        secondary_email = emails[1].get('email')
        if secondary_email:
            update_fields['Secondary Email'] = secondary_email
    
    # Extract phone
    phones = contact_data.get('phones', [])
    if phones and not current_fields.get('Phone Number'):
        phone = phones[0].get('phone')
        if phone:
            update_fields['Phone Number'] = phone
    
    # Extract profile URLs
    profiles = contact_data.get('profiles', [])
    profile_mapping = {
        'linkedin': 'LinkedIn',
        'facebook': 'Facebook',
        'twitter': 'Twitter',
        'instagram': 'Instagram',
        'vimeo': 'Vimeo',
        'youtube': 'YouTube',
        'github': 'GitHub',
        'behance': 'Behance',
        'dribbble': 'Dribbble'
    }
    
    for profile in profiles:
        profile_type = profile.get('type', '').lower()
        profile_url = profile.get('url')
        field_name = profile_mapping.get(profile_type)
        
        if field_name and profile_url and not current_fields.get(field_name):
            update_fields[field_name] = profile_url
    
    if not update_fields:
        return False
    
    # Update Airtable
    async with httpx.AsyncClient() as client:
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}/{airtable_id}'
        update_data = {'fields': update_fields}
        
        response = await client.patch(url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            return update_fields
        else:
            print(f"❌ Failed to update Airtable: {response.text}")
            return False

async def main():
    """Main function to import revealed contact information."""
    print("🔍 IMPORTING ALREADY REVEALED CONTACT INFORMATION")
    print("=" * 60)
    
    # Get all Airtable contacts with SignalHire IDs
    print("📂 Fetching contacts from Airtable...")
    contacts = await get_airtable_contacts()
    
    print(f"📊 Found {len(contacts)} contacts with SignalHire IDs")
    
    updated_count = 0
    no_info_count = 0
    error_count = 0
    
    # Process contacts in batches
    for i, contact in enumerate(contacts, 1):
        print(f"\n[{i}/{len(contacts)}] 🔍 {contact['full_name']} ({contact['signalhire_id']})")
        
        # Get contact info from SignalHire
        contact_data = await get_signalhire_contact_info(contact['signalhire_id'])
        
        if contact_data:
            # Check if there's any contact information
            has_email = contact_data.get('emails')
            has_phone = contact_data.get('phones')
            has_profiles = contact_data.get('profiles')
            
            if has_email or has_phone or has_profiles:
                # Try to update Airtable
                updated_fields = await update_airtable_contact(
                    contact['airtable_id'], 
                    contact_data, 
                    contact['current_fields']
                )
                
                if updated_fields:
                    print(f"✅ Updated: {updated_fields}")
                    updated_count += 1
                else:
                    print("ℹ️  No new information to add")
            else:
                print("ℹ️  No contact information available")
                no_info_count += 1
        else:
            print("❌ Failed to get contact data")
            error_count += 1
        
        # Small delay to respect rate limits
        if i % 10 == 0:
            print("⏳ Pausing 5 seconds...")
            await asyncio.sleep(5)
    
    print(f"\n📊 IMPORT SUMMARY:")
    print(f"   ✅ Updated: {updated_count}")
    print(f"   ℹ️  No info: {no_info_count}")
    print(f"   ❌ Errors: {error_count}")

if __name__ == "__main__":
    asyncio.run(main())