#!/usr/bin/env python3
"""
Process SignalHire contacts and create Airtable records for heavy equipment professionals.
Excludes operators and focuses on technicians/mechanics.
"""

import json
from datetime import datetime

def parse_name(full_name):
    """Parse full name into first and last name."""
    if not full_name:
        return "", "", full_name or ""
    
    # Clean up Unicode characters
    clean_name = full_name.encode('ascii', 'ignore').decode('ascii')
    if not clean_name.strip():
        clean_name = full_name  # Keep original if ASCII conversion fails
    
    # Split name
    parts = clean_name.strip().split()
    if len(parts) == 0:
        return "", "", clean_name
    elif len(parts) == 1:
        return parts[0], "", clean_name
    else:
        first_name = parts[0]
        last_name = " ".join(parts[1:])
        return first_name, last_name, clean_name

def should_include_contact(profile):
    """Determine if contact should be included based on job titles."""
    if not profile.get('experience'):
        return False
    
    # Get the most recent job title
    recent_title = profile['experience'][0].get('title', '').lower()
    
    # Exclude operators, drivers, coordinators, supervisors, sales
    exclude_keywords = [
        'operator', 'driver', 'coordinator', 'supervisor', 
        'sales', 'manager', 'foreman', 'superintendent'
    ]
    
    # Include technicians, mechanics
    include_keywords = [
        'technician', 'mechanic', 'tech'
    ]
    
    # Check if title contains any exclude keywords
    for keyword in exclude_keywords:
        if keyword in recent_title:
            return False
    
    # Check if title contains any include keywords
    for keyword in include_keywords:
        if keyword in recent_title:
            return True
    
    return False

def format_contact_for_airtable(uid, contact_data):
    """Format contact data for Airtable record creation."""
    profile = contact_data['profile']
    
    # Parse name
    first_name, last_name, full_name = parse_name(profile.get('fullName', ''))
    
    # Get job info
    experience = profile.get('experience', [])
    job_title = experience[0].get('title', '') if experience else ''
    company = experience[0].get('company', '') if experience else ''
    
    # Format skills
    skills = ', '.join(profile.get('skills', []))
    
    # Current ISO timestamp
    current_time = datetime.now().isoformat()
    
    record = {
        'SignalHire ID': uid,
        'First Name': first_name,
        'Last Name': last_name,
        'Full Name': full_name,
        'Job Title': job_title,
        'Company': company,
        'Location': profile.get('location', ''),
        'SignalHire Profile': f"https://app.signalhire.com/profile/{uid}",
        'Skills': skills,
        'Status': 'New',
        'Date Added': current_time,
        'Source Search': 'Cache - Heavy Equipment'
    }
    
    return record

def main():
    """Main processing function."""
    # Load contacts
    with open('revealed_contacts.json', 'r') as f:
        contacts = json.load(f)
    
    print(f"Loaded {len(contacts)} total contacts")
    
    # Filter and process contacts
    qualified_contacts = []
    
    for uid, contact_data in contacts.items():
        profile = contact_data['profile']
        
        if should_include_contact(profile):
            record = format_contact_for_airtable(uid, contact_data)
            qualified_contacts.append(record)
            print(f"✓ {record['Full Name']} - {record['Job Title']}")
        else:
            recent_title = profile['experience'][0].get('title', '') if profile.get('experience') else ''
            print(f"✗ {profile.get('fullName', 'Unknown')} - {recent_title} (excluded)")
    
    print(f"\nQualified contacts: {len(qualified_contacts)}")
    
    # Save processed data for review
    with open('qualified_contacts.json', 'w') as f:
        json.dump(qualified_contacts, f, indent=2)
    
    return qualified_contacts

if __name__ == "__main__":
    qualified = main()