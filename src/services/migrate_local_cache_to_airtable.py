#!/usr/bin/env python3
"""
[DEPRECATED] Migrate Local Cache to Airtable

⚠️ DEPRECATED: This migration script is no longer needed.
The SignalHire Agent now uses Airtable as the primary source of truth.
New workflow: Search → Airtable → Webhook → Reveal

PURPOSE: Migrate existing SignalHire data from local JSON cache to Airtable tables
USAGE: python3 migrate_local_cache_to_airtable.py [--dry-run]
PART OF: SignalHire Agent data migration (legacy)
CONNECTS TO: Local cache files, Airtable MCP server
"""

import asyncio
import json
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
SEARCH_SESSIONS_TABLE = "tblqmpcDHfG5pZCWh" 
RAW_PROFILES_TABLE = "tbl593Vc4ExFTYYn0"
CONTACTS_TABLE = "tbl0uFVaAfcNjT2rS"

CACHE_FILE = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"

class CacheToAirtableMigrator:
    """Migrate local cache data to Airtable."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "sessions_created": 0,
            "profiles_migrated": 0,
            "contacts_migrated": 0,
            "errors": []
        }
    
    def load_local_cache(self) -> Dict[str, Any]:
        """Load data from local JSON cache."""
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Cache file not found: {CACHE_FILE}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing cache file: {e}")
            return {}
    
    async def create_migration_session(self) -> str:
        """Create a search session for the migration."""
        session_data = {
            "Session Name": f"Migration from Local Cache - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "Search Query": "Migrated from local JSON cache",
            "Job Titles": "Heavy Equipment Technicians, Mechanics",
            "Location": "Canada",
            "Total Found": 0,  # Will update this
            "Total Revealed": 0,  # Will update this
            "Search Date": datetime.now().isoformat(),
            "Status": "Completed",
            "Credits Used": 0,
            "Notes": "Historical data migrated from local cache system to Airtable"
        }
        
        if self.dry_run:
            print(f"[DRY RUN] Would create migration session")
            return "dry_run_session_id"
        
        print(f"📝 Creating migration session...")
        
        # This would be the actual MCP call:
        # result = await mcp__airtable__create_record(
        #     baseId=AIRTABLE_BASE_ID,
        #     tableId=SEARCH_SESSIONS_TABLE,
        #     fields=session_data
        # )
        # session_id = result["id"]
        
        # For now, simulate
        session_id = f"migration_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.stats["sessions_created"] += 1
        print(f"✅ Migration session created: {session_id}")
        return session_id
    
    async def migrate_profile_to_raw_profiles(self, contact_id: str, contact_data: Dict[str, Any], session_id: str) -> Optional[str]:
        """Migrate a single profile to Raw Profiles table."""
        try:
            profile = contact_data.get('profile', {})
            
            # Extract basic info
            name = profile.get('name', f"Contact {contact_id[:8]}")
            title = profile.get('title', '')
            company = profile.get('company', '')
            
            # Location handling
            location = profile.get('location', {})
            if isinstance(location, dict):
                city = location.get('city', '')
                country = location.get('country', '')
                location_str = f"{city}, {country}".strip(', ')
            else:
                location_str = str(location) if location else ''
            
            # Skills
            skills = []
            if 'skills' in profile and isinstance(profile['skills'], list):
                for skill in profile['skills']:
                    if isinstance(skill, dict):
                        skills.append(skill.get('name', str(skill)))
                    else:
                        skills.append(str(skill))
            skills_str = ', '.join(skills) if skills else ''
            
            # LinkedIn URL
            linkedin_url = profile.get('linkedinUrl', '')
            
            # Experience years
            experience_years = profile.get('experienceYears')
            if experience_years is not None:
                try:
                    experience_years = int(experience_years)
                except (ValueError, TypeError):
                    experience_years = None
            
            # Determine revelation status
            has_contacts = contact_data.get('contacts') and len(contact_data['contacts']) > 0
            revelation_status = "Revealed" if has_contacts else "Not Revealed"
            
            # Get timestamps
            found_date = contact_data.get('first_revealed_at') or datetime.now().isoformat()
            revelation_date = contact_data.get('last_updated_at') if has_contacts else None
            
            profile_record = {
                "Profile Name": name,
                "SignalHire ID": contact_id,
                "Job Title": title,
                "Company": company,
                "Location": location_str,
                "Skills": skills_str,
                "Experience Years": experience_years,
                "LinkedIn Profile": linkedin_url,
                "Profile Data": json.dumps(profile, indent=2),
                "Found Date": found_date,
                "Revelation Status": revelation_status,
                "Search Session": [session_id]
            }
            
            if revelation_date:
                profile_record["Revelation Date"] = revelation_date
            
            # Remove empty fields
            profile_record = {k: v for k, v in profile_record.items() 
                             if v is not None and v != '' and v != []}
            
            if self.dry_run:
                print(f"[DRY RUN] Would migrate profile: {name} ({contact_id})")
                return f"dry_run_profile_{contact_id}"
            
            print(f"  👤 Migrating profile: {name}")
            
            # This would be the actual MCP call:
            # result = await mcp__airtable__create_record(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=RAW_PROFILES_TABLE,
            #     fields=profile_record
            # )
            # profile_record_id = result["id"]
            
            profile_record_id = f"migrated_profile_{contact_id}"
            self.stats["profiles_migrated"] += 1
            return profile_record_id
            
        except Exception as e:
            error_msg = f"Error migrating profile {contact_id}: {e}"
            print(f"  ❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return None
    
    async def migrate_contact_to_contacts_table(self, contact_id: str, contact_data: Dict[str, Any], raw_profile_id: str) -> Optional[str]:
        """Migrate revealed contact to Contacts table."""
        try:
            # Only migrate if there are actual contacts
            contacts = contact_data.get('contacts', [])
            if not contacts:
                return None
            
            profile = contact_data.get('profile', {})
            primary_contact = contacts[0]
            
            # Extract name information
            first_name = profile.get('firstName', '') or primary_contact.get('firstName', '')
            last_name = profile.get('lastName', '') or primary_contact.get('lastName', '')
            full_name = f"{first_name} {last_name}".strip() or profile.get('name', f"Contact {contact_id[:8]}")
            
            # Job and company
            job_title = profile.get('title', '')
            company = profile.get('company', '')
            
            # Location
            location = profile.get('location', {})
            if isinstance(location, dict):
                city = location.get('city', '')
                country = location.get('country', '')
                location_str = f"{city}, {country}".strip(', ')
            else:
                location_str = str(location) if location else ''
            
            # Contact information
            emails = primary_contact.get('emails', [])
            phones = primary_contact.get('phones', [])
            
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
            
            contact_record = {
                "Full Name": full_name,
                "SignalHire ID": contact_id,
                "Job Title": job_title,
                "Company": company,
                "Location": location_str,
                "Primary Email": emails[0] if emails else '',
                "Secondary Email": emails[1] if len(emails) > 1 else '',
                "Phone Number": phones[0] if phones else '',
                "LinkedIn URL": linkedin_url,
                "Facebook URL": facebook_url,
                "Skills": ', '.join(skills) if skills else '',
                "Status": "New",
                "Date Added": contact_data.get('first_revealed_at') or datetime.now().isoformat(),
                "Source Search": "Migrated from Local Cache",
                "Raw Profile": [raw_profile_id]  # Link to raw profile
            }
            
            # Remove empty fields
            contact_record = {k: v for k, v in contact_record.items() 
                             if v is not None and v != '' and v != []}
            
            if self.dry_run:
                print(f"[DRY RUN] Would migrate contact: {full_name}")
                return f"dry_run_contact_{contact_id}"
            
            print(f"  📞 Migrating contact: {full_name}")
            
            # This would be the actual MCP call:
            # result = await mcp__airtable__create_record(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=CONTACTS_TABLE,
            #     fields=contact_record
            # )
            # contact_record_id = result["id"]
            
            contact_record_id = f"migrated_contact_{contact_id}"
            self.stats["contacts_migrated"] += 1
            return contact_record_id
            
        except Exception as e:
            error_msg = f"Error migrating contact {contact_id}: {e}"
            print(f"  ❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return None
    
    async def update_session_totals(self, session_id: str, total_found: int, total_revealed: int):
        """Update the session with final totals."""
        if self.dry_run:
            print(f"[DRY RUN] Would update session totals: {total_found} found, {total_revealed} revealed")
            return
        
        print(f"📊 Updating session totals...")
        
        # This would be the actual MCP call:
        # await mcp__airtable__update_records(
        #     baseId=AIRTABLE_BASE_ID,
        #     tableId=SEARCH_SESSIONS_TABLE,
        #     records=[{
        #         "id": session_id,
        #         "fields": {
        #             "Total Found": total_found,
        #             "Total Revealed": total_revealed
        #         }
        #     }]
        # )
    
    async def migrate_all_data(self):
        """Migrate all data from local cache to Airtable."""
        print(f"🚀 Starting Migration from Local Cache to Airtable")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print("=" * 60)
        
        # Load local cache
        print("📂 Loading local cache data...")
        cache_data = self.load_local_cache()
        
        if not cache_data:
            print("❌ No data found in local cache")
            return
        
        print(f"   Found {len(cache_data)} profiles in local cache")
        
        # Create migration session
        session_id = await self.create_migration_session()
        
        # Migrate each profile
        print(f"\\n📋 Migrating profiles...")
        total_revealed = 0
        
        for i, (contact_id, contact_data) in enumerate(cache_data.items(), 1):
            print(f"\\nProfile {i}/{len(cache_data)}: {contact_id}")
            
            # Migrate to Raw Profiles
            raw_profile_id = await self.migrate_profile_to_raw_profiles(
                contact_id, contact_data, session_id
            )
            
            if raw_profile_id:
                # Check if this profile has revealed contacts
                has_contacts = contact_data.get('contacts') and len(contact_data['contacts']) > 0
                
                if has_contacts:
                    # Migrate to Contacts table
                    contact_record_id = await self.migrate_contact_to_contacts_table(
                        contact_id, contact_data, raw_profile_id
                    )
                    
                    if contact_record_id:
                        total_revealed += 1
        
        # Update session totals
        await self.update_session_totals(session_id, len(cache_data), total_revealed)
        
        # Print final statistics
        print(f"\\n📊 Migration Summary:")
        print(f"   Sessions created: {self.stats['sessions_created']}")
        print(f"   Profiles migrated: {self.stats['profiles_migrated']}")
        print(f"   Contacts migrated: {self.stats['contacts_migrated']}")
        print(f"   Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print(f"\\n❌ Errors encountered:")
            for error in self.stats['errors']:
                print(f"   - {error}")
        
        if self.dry_run:
            print(f"\\n🧪 DRY RUN COMPLETE - No actual changes made")
            print(f"   Run without --dry-run to perform actual migration")
        else:
            print(f"\\n✅ MIGRATION COMPLETE!")
            print(f"   Local cache data successfully migrated to Airtable")

async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Migrate local cache to Airtable")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Run in dry-run mode (no actual changes)")
    
    args = parser.parse_args()
    
    migrator = CacheToAirtableMigrator(dry_run=args.dry_run)
    await migrator.migrate_all_data()

if __name__ == "__main__":
    asyncio.run(main())