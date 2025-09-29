#!/usr/bin/env python3
"""Extract all already revealed heavy equipment mechanics and technicians from contact cache."""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def get_cache_path():
    """Get the default cache path for revealed contacts."""
    # Use WSL path directly
    return Path("/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json")

def is_heavy_equipment_title(title: str) -> bool:
    """Check if title matches heavy equipment roles, excluding operators/drivers."""
    if not title:
        return False
    
    title_lower = title.lower()
    
    # Exclude drivers and operators
    exclude_terms = ['driver', 'operator', 'sales', 'coordinator', 'supervisor', 'manager']
    if any(term in title_lower for term in exclude_terms):
        return False
    
    # Include heavy equipment related roles
    include_terms = [
        'heavy equipment technician',
        'heavy duty technician', 
        'heavy equipment mechanic',
        'heavy duty mechanic',
        'equipment technician',
        'equipment mechanic',
        'diesel mechanic',
        'construction equipment',
        'mining equipment',
        'heavy machinery',
        'industrial mechanic'
    ]
    
    return any(term in title_lower for term in include_terms)

def main():
    print("Searching for revealed heavy equipment contacts in cache...")
    
    cache_path = get_cache_path()
    
    if not cache_path.exists():
        print(f"No cache file found at: {cache_path}")
        return
    
    # Load cache data
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        return
    
    print(f"Found {len(cache_data)} total cached contacts")
    
    heavy_equipment_contacts = []
    
    for uid, cached_contact in cache_data.items():
        profile = cached_contact.get('profile')
        if not profile:
            continue
            
        # Check if this is a heavy equipment professional
        current_title = ""
        current_company = ""
        
        if 'experience' in profile and profile['experience']:
            # Get most recent title and company
            current_title = profile['experience'][0].get('title', '')
            current_company = profile['experience'][0].get('company', '')
        
        # Also check other title fields
        if not current_title:
            current_title = profile.get('title', '') or profile.get('currentTitle', '')
        
        if is_heavy_equipment_title(current_title):
            # Extract contact info
            emails = []
            linkedin = ""
            
            contacts = cached_contact.get('contacts', [])
            for contact in contacts:
                if contact.get('type') == 'email':
                    emails.append(contact.get('value', ''))
                elif contact.get('type') == 'linkedin':
                    linkedin = contact.get('value', '')
            
            # Get location
            location = profile.get('location', '')
            
            # Check if location is in Canada
            if 'canada' in location.lower():
                contact_data = {
                    'uid': uid,
                    'fullName': profile.get('fullName', ''),
                    'location': location,
                    'currentTitle': current_title,
                    'company': current_company,
                    'emails': emails,
                    'linkedin': linkedin,
                    'first_revealed_at': cached_contact.get('first_revealed_at', ''),
                    'skills': profile.get('skills', [])
                }
                
                heavy_equipment_contacts.append(contact_data)
    
    print(f"Found {len(heavy_equipment_contacts)} revealed heavy equipment professionals in Canada")
    
    if heavy_equipment_contacts:
        # Convert to CSV format matching SignalHire export
        csv_data = []
        for contact in heavy_equipment_contacts:
            # Split name
            name_parts = contact['fullName'].split(' ', 1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Get primary email
            primary_email = contact['emails'][0] if contact['emails'] else ''
            secondary_email = contact['emails'][1] if len(contact['emails']) > 1 else ''
            
            # Format skills
            skills_str = ', '.join(contact['skills']) if contact['skills'] else ''
            
            csv_row = {
                'Id': contact['uid'],
                'First Name': first_name,
                'Last Name': last_name,
                'Position': contact['currentTitle'],
                'Company': contact['company'],
                'Location': contact['location'],
                'Summary': '',
                'Personal Email1': primary_email,
                'Personal Email2': secondary_email,
                'Years of Experience': '',
                'Skill': skills_str,
                'LinkedIn Link': contact['linkedin'],
                'Twitter Link': '',
                'Facebook Link': '',
                'Instagram Link': '',
                'Education Degree1': '',
                'Education Faculty1': '',
                'Education University1': '',
                'Education Started1': '',
                'Education Ended1': '',
                'Education Degree2': '',
                'Education Faculty2': '',
                'Education University2': '',
                'Education Started2': '',
                'Education Ended2': '',
                'Education Degree3': '',
                'Education Faculty3': '',
                'Education University3': '',
                'Education Started3': '',
                'Education Ended3': '',
                'Education Degree4': '',
                'Education Faculty4': '',
                'Education University4': '',
                'Education Started4': '',
                'Education Ended4': '',
                'Education Degree5': '',
                'Education Faculty5': '',
                'Education University5': '',
                'Education Started5': '',
                'Education Ended5': '',
                'Education Degree6': '',
                'Education Faculty6': '',
                'Education University6': '',
                'Education Started6': '',
                'Education Ended6': ''
            }
            csv_data.append(csv_row)
        
        # Export to CSV
        df = pd.DataFrame(csv_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"revealed_heavy_equipment_canada_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"Exported to: {filename}")
        
        # Show summary
        print("\nSummary of revealed contacts:")
        for i, contact in enumerate(heavy_equipment_contacts[:10], 1):
            emails_str = f" - {contact['emails'][0]}" if contact['emails'] else ""
            print(f"  {i}. {contact['fullName']} - {contact['currentTitle']} at {contact['company']} ({contact['location']}){emails_str}")
        
        if len(heavy_equipment_contacts) > 10:
            print(f"  ... and {len(heavy_equipment_contacts) - 10} more")
            
        print(f"\nThese {len(heavy_equipment_contacts)} contacts are already revealed - no credits used!")
        
        # Also save as JSON for reference
        json_filename = f"revealed_heavy_equipment_canada_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(heavy_equipment_contacts, f, indent=2)
        print(f"Also exported JSON to: {json_filename}")
        
    else:
        print("No revealed heavy equipment professionals found in cache")
        print("Checking cache file structure...")
        
        # Debug: show a sample of what's in the cache
        if cache_data:
            sample_uid = list(cache_data.keys())[0]
            sample_contact = cache_data[sample_uid]
            print(f"Sample contact structure: {json.dumps(sample_contact, indent=2)}")

if __name__ == "__main__":
    main()