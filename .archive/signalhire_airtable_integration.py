#!/usr/bin/env python3
"""
Automated SignalHire to Airtable integration using direct API calls.
This directly integrates both APIs for automated workflow.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import existing SignalHire client
from src.services.signalhire_client import SignalHireClient
from src.lib.contact_cache import ContactCache


# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
AIRTABLE_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table


def generate_signalhire_profile_url(uid: str) -> str:
    """Generate SignalHire profile URL from UID."""
    return f"https://app.signalhire.com/profile/{uid}"


def format_contact_for_airtable(contact_data: dict, source_search: str = "SDK Integration") -> dict:
    """Format contact data for Airtable insertion."""
    
    # Handle both cache format and API format
    if 'profile' in contact_data:
        # Cache format (revealed contacts)
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
        # API format (search results)
        uid = contact_data.get('uid', '')
        full_name = contact_data.get('fullName', '')
        location = contact_data.get('location', '')
        
        # Get current title and company from experience
        experience = contact_data.get('experience', [])
        current_title = experience[0].get('title', '') if experience else ''
        current_company = experience[0].get('company', '') if experience else ''
        
        # For API format, contacts need to be revealed separately
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


class SignalHireAirtableIntegration:
    """Automated integration between SignalHire and Airtable."""
    
    def __init__(self):
        self.signalhire_client = SignalHireClient()
        self.contact_cache = ContactCache()
        
    async def get_existing_airtable_contacts(self) -> List[str]:
        """Get list of SignalHire IDs already in Airtable for deduplication."""
        print("Checking existing contacts in Airtable...")
        # For now return empty list, will implement with MCP call
        return []
    
    async def search_signalhire_heavy_equipment(self, limit: int = 25) -> List[dict]:
        """Search for heavy equipment professionals in Canada using SignalHire API."""
        search_criteria = {
            "currentTitle": '"Heavy Equipment Technician" OR "Heavy Duty Technician" OR "Heavy Equipment Mechanic" OR "Heavy Duty Mechanic" OR "Diesel Mechanic" OR "Equipment Technician" OR "Construction Equipment Technician" OR "Mining Equipment Technician" OR "Heavy Machinery Technician" OR "Heavy Machinery Mechanic" OR "Equipment Mechanic" OR "Industrial Mechanic"',
            "location": "Canada",
            "exclude": "NOT driver NOT operator NOT sales NOT coordinator NOT supervisor"
        }
        
        try:
            response = await self.signalhire_client.search_prospects(search_criteria, size=limit)
            if response.success and response.data:
                return response.data.get('results', [])
            return []
        except Exception as e:
            print(f"Error searching SignalHire: {e}")
            return []
    
    async def get_revealed_heavy_equipment_from_cache(self) -> List[dict]:
        """Get already revealed heavy equipment contacts from cache."""
        cache_path = Path("/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json")
        
        if not cache_path.exists():
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
    
    async def push_contacts_to_airtable(self, contacts: List[dict], source_search: str) -> int:
        """Push contacts to Airtable with deduplication."""
        if not contacts:
            return 0
        
        print(f"Processing {len(contacts)} contacts for Airtable...")
        
        # Get existing IDs for deduplication
        existing_ids = await self.get_existing_airtable_contacts()
        existing_ids_set = set(existing_ids)
        
        new_contacts = []
        skipped_count = 0
        
        for contact in contacts:
            uid = contact.get('uid') or contact.get('SignalHire ID')
            
            if uid in existing_ids_set:
                skipped_count += 1
                continue
                
            airtable_record = format_contact_for_airtable(contact, source_search)
            new_contacts.append(airtable_record)
        
        print(f"Adding {len(new_contacts)} new contacts (skipped {skipped_count} duplicates)")
        
        # For now, show what would be pushed - will implement actual MCP calls
        for i, record in enumerate(new_contacts[:5], 1):  # Show first 5
            print(f"{i}. {record['Full Name']} - {record['Job Title']} at {record['Company']}")
        
        if len(new_contacts) > 5:
            print(f"   ... and {len(new_contacts) - 5} more contacts")
        
        return len(new_contacts)
    
    async def automated_signalhire_to_airtable_workflow(self, search_limit: int = 25) -> dict:
        """Complete automated workflow: search SignalHire -> dedupe -> push to Airtable."""
        results = {
            "revealed_contacts_pushed": 0,
            "new_search_contacts_pushed": 0,
            "total_contacts_pushed": 0,
            "credits_used": 0
        }
        
        print("Starting automated SignalHire to Airtable workflow")
        print("=" * 60)
        
        # Step 1: Push already revealed contacts from cache
        print("Step 1: Processing revealed contacts from cache...")
        revealed_contacts = await self.get_revealed_heavy_equipment_from_cache()
        print(f"Found {len(revealed_contacts)} revealed heavy equipment contacts")
        
        if revealed_contacts:
            pushed_revealed = await self.push_contacts_to_airtable(
                revealed_contacts, 
                "Cache - Revealed Contacts"
            )
            results["revealed_contacts_pushed"] = pushed_revealed
            print(f"Prepared {pushed_revealed} revealed contacts for Airtable")
        
        # Step 2: Search for new contacts (uses credits)
        print(f"\nStep 2: Searching for new contacts (limit: {search_limit})...")
        new_contacts = await self.search_signalhire_heavy_equipment(search_limit)
        print(f"Found {len(new_contacts)} new contacts from search")
        results["credits_used"] = len(new_contacts)
        
        if new_contacts:
            pushed_new = await self.push_contacts_to_airtable(
                new_contacts,
                "API Search - Heavy Equipment"
            )
            results["new_search_contacts_pushed"] = pushed_new
            print(f"Prepared {pushed_new} new search contacts for Airtable")
        
        results["total_contacts_pushed"] = results["revealed_contacts_pushed"] + results["new_search_contacts_pushed"]
        
        print(f"\nWorkflow Complete!")
        print(f"   Revealed contacts prepared: {results['revealed_contacts_pushed']}")
        print(f"   New search contacts prepared: {results['new_search_contacts_pushed']}")
        print(f"   Total contacts prepared: {results['total_contacts_pushed']}")
        print(f"   Credits used: {results['credits_used']}")
        
        return results


async def main():
    """Main function to run the automated integration."""
    integration = SignalHireAirtableIntegration()
    
    # Run the automated workflow directly
    try:
        result = await integration.automated_signalhire_to_airtable_workflow(search_limit=25)
        print(f"Workflow result: {result}")
    except Exception as e:
        print(f"Error running automated workflow: {e}")


if __name__ == "__main__":
    asyncio.run(main())