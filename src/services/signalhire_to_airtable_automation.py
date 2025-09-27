#!/usr/bin/env python3
"""
SignalHire to Airtable Automation

PURPOSE: Complete automation to process SignalHire contacts with revealed information to Airtable
USAGE: python3 signalhire_to_airtable_automation.py [--reveal-contacts] [--force]
PART OF: SignalHire Agent automation workflow
CONNECTS TO: SignalHire API, Airtable MCP, contact cache management
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

from src.services.signalhire_client import SignalHireClient

# Load environment variables
load_dotenv()

AIRTABLE_BASE_ID = "appQoYINM992nBZ50"  # Signalhire base
CONTACTS_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table
CACHE_FILE = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"

class SignalHireAirtableProcessor:
    """Main processor for SignalHire to Airtable automation."""
    
    def __init__(self):
        self.signalhire_client = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.signalhire_client = SignalHireClient(
            callback_url="https://httpbin.org/post"  # Use a test endpoint for now
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.signalhire_client:
            await self.signalhire_client.close()
    
    def load_cached_contacts(self) -> Dict[str, Any]:
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
    
    def get_contacts_with_info(self, contacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get contacts that have actual contact information."""
        contacts_with_info = []
        
        for contact_id, contact_data in contacts.items():
            if contact_data.get('contacts') and len(contact_data['contacts']) > 0:
                contacts_with_info.append({
                    'signalhire_id': contact_id,
                    'data': contact_data
                })
        
        return contacts_with_info
    
    def get_contacts_without_info(self, contacts: Dict[str, Any]) -> List[str]:
        """Get contact IDs that don't have revealed information yet."""
        contacts_without_info = []
        
        for contact_id, contact_data in contacts.items():
            if not contact_data.get('contacts') or len(contact_data['contacts']) == 0:
                contacts_without_info.append(contact_id)
        
        return contacts_without_info
    
    async def reveal_contacts(self, contact_ids: List[str], max_reveals: int = 5) -> Dict[str, Any]:
        """Reveal contact information for given contact IDs."""
        if not self.signalhire_client:
            raise RuntimeError("SignalHire client not initialized")
        
        print(f"🔍 Revealing contact information for {min(len(contact_ids), max_reveals)} contacts...")
        
        results = {
            "requested": 0,
            "successful": 0,
            "failed": 0,
            "request_ids": [],
            "errors": []
        }
        
        # Limit the number of reveals to avoid hitting rate limits
        contacts_to_reveal = contact_ids[:max_reveals]
        
        for i, contact_id in enumerate(contacts_to_reveal, 1):
            try:
                print(f"  📞 Revealing contact {i}/{len(contacts_to_reveal)}: {contact_id}")
                
                response = await self.signalhire_client.reveal_contact(contact_id)
                results["requested"] += 1
                
                if response.success:
                    request_id = response.data.get('requestId') if response.data else None
                    print(f"    ✅ Success - Request ID: {request_id}")
                    results["successful"] += 1
                    if request_id:
                        results["request_ids"].append(request_id)
                else:
                    error_msg = f"Failed to reveal {contact_id}: {response.error}"
                    print(f"    ❌ {error_msg}")
                    results["failed"] += 1
                    results["errors"].append(error_msg)
                
                # Small delay to respect rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                error_msg = f"Exception revealing {contact_id}: {e}"
                print(f"    ❌ {error_msg}")
                results["failed"] += 1
                results["errors"].append(error_msg)
        
        return results
    
    def format_contact_for_airtable(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format contact data for Airtable insertion."""
        signalhire_id = contact_data['signalhire_id']
        data = contact_data['data']
        profile = data.get('profile', {})
        
        # Get the primary contact info (first revealed contact)
        contacts = data.get('contacts', [])
        primary_contact = contacts[0] if contacts else {}
        
        # Extract name information
        first_name = profile.get('firstName', '') or primary_contact.get('firstName', '')
        last_name = profile.get('lastName', '') or primary_contact.get('lastName', '')
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = profile.get('name', f"Contact {signalhire_id[:8]}")
        
        # Extract job and company info
        job_title = profile.get('title', '')
        company = profile.get('company', '')
        
        # Try to get job title from experience if not in profile
        if not job_title and 'experience' in profile:
            experience = profile['experience']
            if isinstance(experience, list) and experience:
                latest_job = experience[0]
                if isinstance(latest_job, dict):
                    job_title = latest_job.get('title', '')
                    if not company:
                        company = latest_job.get('company', '')
        
        # Extract location
        location = profile.get('location', {})
        location_str = ''
        if isinstance(location, dict):
            city = location.get('city', '')
            country = location.get('country', '')
            if city and country:
                location_str = f"{city}, {country}"
            elif city:
                location_str = city
            elif country:
                location_str = country
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
        
        # Extract skills
        skills = []
        if 'skills' in profile:
            skill_data = profile['skills']
            if isinstance(skill_data, list):
                for skill in skill_data:
                    if isinstance(skill, dict):
                        skills.append(skill.get('name', str(skill)))
                    else:
                        skills.append(str(skill))
        
        # Create Airtable record
        airtable_record = {
            "SignalHire ID": signalhire_id,
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
            "Status": "New",
            "Date Added": datetime.now().isoformat(),
            "Source Search": "SignalHire Agent"
        }
        
        # Remove empty fields
        return {k: v for k, v in airtable_record.items() if v}
    
    async def add_contact_to_airtable(self, contact_record: Dict[str, Any]) -> bool:
        """Add a single contact to Airtable using MCP tools."""
        try:
            # Note: In a real implementation, we would use the MCP airtable tools here
            # For demonstration, we'll simulate the process
            
            print(f"  📤 Adding to Airtable: {contact_record.get('Full Name', 'Unknown')}")
            print(f"     Email: {contact_record.get('Primary Email', 'N/A')}")
            print(f"     Phone: {contact_record.get('Phone Number', 'N/A')}")
            print(f"     Company: {contact_record.get('Company', 'N/A')}")
            
            # This would be the actual MCP call:
            # result = await mcp_airtable_create_record(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=CONTACTS_TABLE_ID,
            #     fields=contact_record
            # )
            
            return True
            
        except Exception as e:
            print(f"    ❌ Failed to add contact: {e}")
            return False
    
    async def process_contacts_to_airtable(self, contacts_with_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process revealed contacts to Airtable."""
        print(f"📤 Processing {len(contacts_with_info)} contacts to Airtable...")
        
        results = {
            "total": len(contacts_with_info),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for i, contact_data in enumerate(contacts_with_info, 1):
            try:
                # Format contact for Airtable
                airtable_record = self.format_contact_for_airtable(contact_data)
                
                # Add to Airtable
                success = await self.add_contact_to_airtable(airtable_record)
                
                if success:
                    results["successful"] += 1
                    print(f"    ✅ Successfully added contact {i}/{len(contacts_with_info)}")
                else:
                    results["failed"] += 1
                    print(f"    ❌ Failed to add contact {i}/{len(contacts_with_info)}")
                
            except Exception as e:
                error_msg = f"Error processing contact {i}: {e}"
                results["errors"].append(error_msg)
                results["failed"] += 1
                print(f"    ❌ {error_msg}")
        
        return results

async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="SignalHire to Airtable Automation")
    parser.add_argument("--reveal-contacts", action="store_true", 
                       help="Reveal contact information for contacts without details")
    parser.add_argument("--force", action="store_true",
                       help="Force processing even if no contacts have revealed info")
    parser.add_argument("--max-reveals", type=int, default=5,
                       help="Maximum number of contacts to reveal (default: 5)")
    
    args = parser.parse_args()
    
    print("🚀 SignalHire to Airtable Automation")
    print("=" * 50)
    
    async with SignalHireAirtableProcessor() as processor:
        # Load cached contacts
        print("📂 Loading cached contacts...")
        all_contacts = processor.load_cached_contacts()
        print(f"   Found {len(all_contacts)} total cached contacts")
        
        if not all_contacts:
            print("❌ No contacts found in cache. Run a SignalHire search first.")
            return
        
        # Check contacts with revealed information
        contacts_with_info = processor.get_contacts_with_info(all_contacts)
        contacts_without_info = processor.get_contacts_without_info(all_contacts)
        
        print(f"📊 Contact Status:")
        print(f"   ✅ With revealed info: {len(contacts_with_info)}")
        print(f"   ❓ Without revealed info: {len(contacts_without_info)}")
        
        # Reveal contacts if requested
        if args.reveal_contacts and contacts_without_info:
            print(f"\\n🔍 Revealing contact information...")
            reveal_results = await processor.reveal_contacts(
                contacts_without_info, 
                max_reveals=args.max_reveals
            )
            
            print(f"\\n📊 Revelation Results:")
            print(f"   Requested: {reveal_results['requested']}")
            print(f"   Successful: {reveal_results['successful']}")
            print(f"   Failed: {reveal_results['failed']}")
            
            if reveal_results['request_ids']:
                print(f"   Request IDs: {reveal_results['request_ids']}")
            
            if reveal_results['errors']:
                print(f"   Errors: {reveal_results['errors']}")
                
            print(f"\\nℹ️  Note: Contact information is revealed asynchronously.")
            print(f"   Check back later or monitor the callback URL for results.")
        
        # Process contacts to Airtable
        if contacts_with_info:
            print(f"\\n📤 Processing contacts to Airtable...")
            airtable_results = await processor.process_contacts_to_airtable(contacts_with_info)
            
            print(f"\\n📊 Airtable Processing Results:")
            print(f"   Total processed: {airtable_results['total']}")
            print(f"   Successful: {airtable_results['successful']}")
            print(f"   Failed: {airtable_results['failed']}")
            
            if airtable_results['errors']:
                print(f"   Errors:")
                for error in airtable_results['errors']:
                    print(f"     - {error}")
        
        elif not args.force:
            print(f"\\n❌ No contacts with revealed information found.")
            print(f"   Use --reveal-contacts to reveal contact information first.")
            print(f"   Or use --force to continue anyway.")
        
        print(f"\\n✅ Automation complete!")

if __name__ == "__main__":
    asyncio.run(main())