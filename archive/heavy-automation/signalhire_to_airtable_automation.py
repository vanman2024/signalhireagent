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
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

import httpx

from src.lib.contact_cache import ContactCache
from src.services.signalhire_client import SignalHireClient
from src.services.enhanced_contact_processor import enhanced_processor
from src.services.dynamic_airtable_expansion import process_contact_with_dynamic_expansion
from src.lib.callback_server import start_server, get_server

# Load environment variables (allow .env to override shell exports)
load_dotenv(override=True)

AIRTABLE_BASE_ID = "appQoYINM992nBZ50"  # Signalhire base
CONTACTS_TABLE_ID = "tbl0uFVaAfcNjT2rS"  # Contacts table
CACHE_FILE = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"

def sanitize_for_json(value):
    """Sanitize data to ensure valid JSON encoding."""
    if isinstance(value, str):
        # Remove or replace problematic Unicode characters
        value = value.encode('utf-8', errors='ignore').decode('utf-8')
        # Remove control characters except tabs, newlines, and carriage returns
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        # Handle Unicode surrogates
        value = value.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')
        return value
    elif isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    elif isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    else:
        return value

class SignalHireAirtableProcessor:
    """Main processor for SignalHire to Airtable automation."""
    
    def __init__(self):
        self.signalhire_client = None
        self.callback_server = None
        self.pending_requests = {}  # Track pending revelation requests
        self._equipment_brands_cache = {}  # Cache for brand name -> record ID lookup
        self._equipment_types_cache = {}   # Cache for equipment type -> record ID lookup
        self._industries_cache = {}        # Cache for industry -> record ID lookup
        self.contact_cache = ContactCache()
        
    async def __aenter__(self):
        """Async context manager entry."""
        # Start the callback server
        self.callback_server = start_server(host="0.0.0.0", port=8000, background=True)
        
        # Register our callback handler
        self.callback_server.register_handler("airtable_processor", self._handle_revelation_callback)
        
        callback_url = self._resolve_callback_url()
        print(f"🌐 Callback server running locally at: {self.callback_server.get_callback_url()}")
        print(f"🔁 SignalHire callback target: {callback_url}")

        self.signalhire_client = SignalHireClient(callback_url=callback_url)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.signalhire_client:
            await self.signalhire_client.close()
        if self.callback_server:
            self.callback_server.stop()
    
    def _resolve_callback_url(self) -> str:
        """Determine the externally accessible callback URL for SignalHire."""
        # Priority: explicit env vars -> config file -> active ngrok tunnel -> local default
        env_url = os.getenv("SIGNALHIRE_CALLBACK_URL") or os.getenv("PUBLIC_CALLBACK_URL")
        if env_url:
            resolved = self._normalize_callback_url(env_url)
            if resolved:
                print(f"🔧 Using callback URL from environment variables: {resolved}")
                return resolved

        config_url = self._load_config_callback_url()
        if config_url:
            resolved = self._normalize_callback_url(config_url)
            if resolved:
                print(f"🔧 Using callback URL from ~/.signalhire-agent/config.json: {resolved}")
                return resolved

        tunnel_url = self._detect_ngrok_tunnel()
        if tunnel_url:
            resolved = self._normalize_callback_url(tunnel_url)
            if resolved:
                print(f"🔧 Detected active ngrok tunnel and using it for callbacks: {resolved}")
                return resolved

        print("⚠️  Falling back to local callback URL (external services must reach this host)")
        return self.callback_server.get_callback_url()

    def _normalize_callback_url(self, url: str | None) -> Optional[str]:
        """Ensure callback URL ends with /signalhire/callback and has a scheme."""
        if not url:
            return None
        url = url.strip()
        if not url:
            return None
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url.lstrip('/')}"
        url = url.rstrip('/')
        if not url.endswith('/signalhire/callback'):
            url = f"{url}/signalhire/callback"
        return url

    def _load_config_callback_url(self) -> Optional[str]:
        """Read callback_url from the persisted agent config if available."""
        try:
            config_path = Path.home() / '.signalhire-agent' / 'config.json'
            if not config_path.exists():
                return None
            with open(config_path, 'r', encoding='utf-8') as cfg:
                data = json.load(cfg)
            return data.get('callback_url')
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Unable to read callback URL from config: {exc}")
            return None

    def _detect_ngrok_tunnel(self) -> Optional[str]:
        """Check for a running ngrok tunnel and return its public URL if present."""
        try:
            response = httpx.get('http://127.0.0.1:4040/api/tunnels', timeout=2.0)
            response.raise_for_status()
            tunnels = response.json().get('tunnels', [])
            https_tunnel = next(
                (t for t in tunnels if t.get('public_url', '').startswith('https://')),
                None,
            )
            if https_tunnel:
                return https_tunnel.get('public_url')
            if tunnels:
                return tunnels[0].get('public_url')
        except httpx.RequestError:
            pass
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Unable to auto-detect ngrok tunnel: {exc}")
        return None
    
    def _search_airtable_records(self, table_id: str, search_term: str):
        """Search for records in Airtable by name using MCP search."""
        try:
            # Use the mcp__airtable__search_records tool directly
            import subprocess
            import json
            
            # Simple lookup for known equipment brands
            if table_id == "tblQ45u548RjR7qwT":  # Equipment Brands table
                lookup = {
                    "caterpillar": "rec4SwdgQ8C8oT2kL",
                    "john deere": "recQD8xbTjVKK53lf", 
                    "komatsu": "rec42W76LTdagoBB4"
                }
                record_id = lookup.get(search_term.lower())
                if record_id:
                    return [{"id": record_id, "fields": {"Brand Name": search_term}}]
            return []
        except Exception:
            return []
    
    def _get_or_create_linked_record_ids(self, table_id: str, field_name: str, names: List[str], cache: Dict[str, str]) -> List[str]:
        """Get or create record IDs for linked fields."""
        if not names:
            return []
        
        record_ids = []
        for name in names:
            if name in cache:
                record_ids.append(cache[name])
            else:
                # Search for existing record
                try:
                    existing_records = self._search_airtable_records(table_id, name)
                    if existing_records:
                        record_id = existing_records[0]['id']
                        cache[name] = record_id
                        record_ids.append(record_id)
                        print(f"     ✅ Found existing {field_name}: {name}")
                    else:
                        # For now, skip creating new records and use fallback
                        print(f"     ⚠️ {field_name} '{name}' not found in linked table")
                except Exception as e:
                    print(f"     ⚠️ Could not resolve {field_name} '{name}': {e}")
        
        return record_ids
    
    async def _handle_revelation_callback(self, callback_data):
        """Handle SignalHire revelation callbacks."""
        print(f"🔔 Received revelation callback with {len(callback_data)} items")

        processing_queue: List[tuple[str, Dict[str, Any]]] = []

        def get_value(source: Any, key: str, default: Any = None) -> Any:
            if isinstance(source, dict):
                return source.get(key, default)
            return getattr(source, key, default)

        for item in callback_data:
            item_id = get_value(item, 'item')
            status = get_value(item, 'status')
            candidate = get_value(item, 'candidate')

            print(f"   📄 Item: {item_id}")
            print(f"   📊 Status: {status}")

            if status == "success" and candidate and item_id:
                full_name = get_value(candidate, 'fullName', 'Unknown')
                print(f"   ✅ Success: {full_name}")

                experience = get_value(candidate, 'experience', []) or []
                locations = get_value(candidate, 'locations', []) or []
                skills = get_value(candidate, 'skills', []) or []

                current_title = ''
                current_company = ''
                if isinstance(experience, list) and experience:
                    current_job = experience[0]
                    current_title = get_value(current_job, 'position') or get_value(current_job, 'title', '')
                    current_company = get_value(current_job, 'company', '')
                else:
                    current_title = get_value(candidate, 'title', '')
                    current_company = get_value(candidate, 'company', '')

                location_str = ''
                if isinstance(locations, list) and locations:
                    first_location = locations[0]
                    location_str = get_value(first_location, 'name', '')

                emails = set(self._collect_contact_values(get_value(candidate, 'emails')))
                phones = set(self._collect_contact_values(get_value(candidate, 'phones')))

                linkedin_url = get_value(candidate, 'linkedinUrl', '')
                facebook_url = get_value(candidate, 'facebookUrl', '')
                if isinstance(item_id, str) and item_id.startswith('https://linkedin') and not linkedin_url:
                    linkedin_url = item_id

                contacts_payload = get_value(candidate, 'contacts', [])
                for contact in contacts_payload or []:
                    contact_type = (get_value(contact, 'type', '') or '').lower()
                    contact_value = get_value(contact, 'value') or get_value(contact, 'contact')
                    if not contact_value:
                        continue
                    if contact_type == 'email':
                        emails.add(str(contact_value))
                    elif contact_type == 'phone':
                        phones.add(str(contact_value))
                    elif 'linkedin' in contact_type and not linkedin_url:
                        linkedin_url = str(contact_value)
                    elif 'facebook' in contact_type and not facebook_url:
                        facebook_url = str(contact_value)

                if not emails and not phones and not linkedin_url and not facebook_url:
                    print(f"   ⚠️  No direct contact info provided for {full_name}")

                contact_entry: Dict[str, Any] = {}
                if emails:
                    contact_entry['emails'] = sorted(emails)
                if phones:
                    contact_entry['phones'] = sorted(phones)
                if linkedin_url:
                    contact_entry['linkedinUrl'] = linkedin_url
                if facebook_url:
                    contact_entry['facebookUrl'] = facebook_url

                contact_data = {
                    'profile': {
                        'fullName': full_name,
                        'title': current_title,
                        'company': current_company,
                        'location': location_str,
                        'experience': experience,
                        'skills': skills,
                        'linkedinUrl': linkedin_url,
                        'facebookUrl': facebook_url,
                    },
                    'contacts': [contact_entry] if contact_entry else []
                }

                self._update_contact_cache(item_id, contact_data)

                print(f"   💾 Processing to Airtable: {contact_data['profile']['fullName']}")
                processing_queue.append(
                    (
                        item_id,
                        {
                            'signalhire_id': item_id,
                            'data': contact_data,
                        },
                    )
                )
            else:
                print(f"   ❌ Failed: {status}")
                error_message = get_value(item, 'error')
                if error_message:
                    print(f"       Error: {error_message}")
                self._mark_request_status(item_id, 'failed', error_message)

        for item_id, formatted_contact in processing_queue:
            try:
                await self._process_single_contact_to_airtable(formatted_contact)
                self._mark_request_status(item_id, 'completed')
            except Exception as exc:  # noqa: BLE001
                print(f"   ❌ Error processing contact {item_id} to Airtable: {exc}")
                self._mark_request_status(item_id, 'failed', str(exc))
    
    async def _process_single_contact_to_airtable(self, contact_data: Dict[str, Any]):
        """Process a single revealed contact to Airtable."""
        try:
            # Format the contact for Airtable
            airtable_record = await self.format_contact_for_airtable(contact_data)
            
            # Add to Airtable
            success = await self.add_contact_to_airtable(airtable_record)
            
            if success:
                full_name = airtable_record.get('Full Name', 'Unknown')
                print(f"   🎉 Successfully added {full_name} to Airtable!")
            else:
                print(f"   ❌ Failed to add contact to Airtable")
                
        except Exception as e:
            print(f"   ❌ Error processing contact to Airtable: {e}")
    
    def load_cached_contacts(self) -> Dict[str, Any]:
        """Load contacts from SignalHire cache with normalized structure."""
        try:
            contacts: Dict[str, Any] = {}
            for uid in self.contact_cache.list_cached_uids():
                cached = self.contact_cache.get(uid)
                if not cached:
                    continue
                contacts[uid] = {
                    'uid': uid,
                    'profile': cached.profile or {},
                    'contacts': self._convert_cached_contacts(cached.contacts),
                    'first_revealed_at': cached.first_revealed_at,
                    'last_updated_at': cached.last_updated_at,
                    'metadata': cached.metadata,
                }
            if contacts:
                return contacts

            # Fallback to legacy JSON structure if contact cache is empty
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    legacy_data = json.load(f)
                    if isinstance(legacy_data, dict):
                        return legacy_data
            return {}
        except FileNotFoundError:
            print(f"❌ Cache file not found: {CACHE_FILE}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing cache file: {e}")
            return {}
        except Exception as e:
            print(f"⚠️  Unexpected error loading cache: {e}")
            return {}
    
    def _collect_contact_values(self, raw_entries: Any) -> List[str]:
        """Normalize SignalHire contact structures into a simple list of strings."""
        values: List[str] = []
        if not raw_entries:
            return values

        if isinstance(raw_entries, (list, tuple, set)):
            entries = list(raw_entries)
        else:
            entries = [raw_entries]

        for entry in entries:
            candidate_value = None
            if isinstance(entry, str):
                candidate_value = entry
            elif isinstance(entry, dict):
                candidate_value = (
                    entry.get('value')
                    or entry.get('email')
                    or entry.get('address')
                    or entry.get('number')
                )
            else:
                candidate_value = (
                    getattr(entry, 'value', None)
                    or getattr(entry, 'email', None)
                    or getattr(entry, 'address', None)
                    or getattr(entry, 'number', None)
                )
            if candidate_value:
                values.append(str(candidate_value))
        return values

    def _convert_cached_contacts(self, cached_contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert cached contact entries into Airtable-ready structure."""
        emails: List[str] = []
        phones: List[str] = []
        linkedin_url: Optional[str] = None
        facebook_url: Optional[str] = None
        other_contacts: List[Dict[str, Any]] = []

        for entry in cached_contacts or []:
            if not isinstance(entry, dict):
                continue
            contact_type = (entry.get('type') or '').lower()
            value = entry.get('value')
            if not value:
                continue
            if contact_type in {'email', 'emails'}:
                if value not in emails:
                    emails.append(value)
            elif contact_type in {'phone', 'phones', 'mobile', 'mobile_phone', 'work_phone', 'cell'}:
                if value not in phones:
                    phones.append(value)
            elif 'linkedin' in contact_type:
                linkedin_url = linkedin_url or value
            elif 'facebook' in contact_type:
                facebook_url = facebook_url or value
            else:
                other_contacts.append({
                    'type': contact_type or 'other',
                    'value': value,
                    'label': entry.get('label'),
                })

        primary_contact: Dict[str, Any] = {}
        if emails:
            primary_contact['emails'] = emails
        if phones:
            primary_contact['phones'] = phones
        if linkedin_url:
            primary_contact['linkedinUrl'] = linkedin_url
        if facebook_url:
            primary_contact['facebookUrl'] = facebook_url

        contacts: List[Dict[str, Any]] = []
        if primary_contact:
            contacts.append(primary_contact)
        if other_contacts:
            contacts.append({'otherContacts': other_contacts})
        return contacts

    def _update_contact_cache(self, signalhire_id: str, contact_data: Dict[str, Any]) -> None:
        """Update the local contact cache with revealed data."""
        try:
            profile = contact_data.get('profile', {})
            cache_entries: List[Dict[str, Any]] = []
            for entry in contact_data.get('contacts', []):
                if not isinstance(entry, dict):
                    continue
                for email in entry.get('emails', []) or []:
                    cache_entries.append({'type': 'email', 'value': email, 'label': 'email'})
                for phone in entry.get('phones', []) or []:
                    cache_entries.append({'type': 'phone', 'value': phone, 'label': 'phone'})
                linkedin = entry.get('linkedinUrl') or entry.get('LinkedIn URL')
                if linkedin:
                    cache_entries.append({'type': 'linkedin', 'value': linkedin, 'label': 'linkedinUrl'})
                facebook = entry.get('facebookUrl') or entry.get('Facebook URL')
                if facebook:
                    cache_entries.append({'type': 'facebook', 'value': facebook, 'label': 'facebookUrl'})
            self.contact_cache.upsert(signalhire_id, contacts=cache_entries, profile=profile)
            self.contact_cache.save()
        except Exception as e:
            print(f"   ⚠️ Failed to update contact cache for {signalhire_id}: {e}")

    def _mark_request_status(self, contact_id: Optional[str], status: str, error: Optional[str] = None) -> None:
        """Update tracking for pending reveal requests."""
        if not contact_id:
            return
        for request_id, info in list(self.pending_requests.items()):
            if info.get('contact_id') == contact_id:
                info['status'] = status
                info['completed_at'] = datetime.now().isoformat()
                if error:
                    info['error'] = error
                if status == 'completed':
                    self.pending_requests.pop(request_id, None)
                else:
                    self.pending_requests[request_id] = info
                break

    def get_contacts_with_info(self, contacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get contacts that have revealed CONTACT information (emails/phones)."""
        contacts_with_info = []
        
        for contact_id, contact_data in contacts.items():
            # Check if we have actual contact details (emails or phones)
            contacts = contact_data.get('contacts', [])
            has_contact_info = False
            
            if contacts:
                for contact in contacts:
                    emails = contact.get('emails', [])
                    phones = contact.get('phones', [])
                    if emails or phones:
                        has_contact_info = True
                        break
            
            if has_contact_info:
                contacts_with_info.append({
                    'signalhire_id': contact_id,
                    'data': contact_data
                })
        
        return contacts_with_info
    
    def get_contacts_without_info(self, contacts: Dict[str, Any]) -> List[str]:
        """Get contact IDs that don't have revealed CONTACT information yet."""
        contacts_without_info = []
        
        for contact_id, contact_data in contacts.items():
            # Check if we have actual contact details (emails or phones)
            contacts_list = contact_data.get('contacts', [])
            has_contact_info = False
            
            if contacts_list:
                for contact in contacts_list:
                    emails = contact.get('emails', [])
                    phones = contact.get('phones', [])
                    if emails or phones:
                        has_contact_info = True
                        break
            
            # If no contact info, add to revelation list
            if not has_contact_info:
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
            "tracking_records": [],
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
                        
                        # Track this pending request
                        self.pending_requests[str(request_id)] = {
                            'contact_id': contact_id,
                            'requested_at': datetime.now().isoformat(),
                            'status': 'pending'
                        }
                        
                        # Store tracking record in Raw Profiles table
                        tracking_record = await self.store_revelation_tracking(contact_id, request_id)
                        if tracking_record:
                            results["tracking_records"].append(tracking_record)
                            print(f"    📝 Tracking stored for request {request_id}")
                        else:
                            print(f"    ⚠️  Failed to store tracking for request {request_id}")
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
    
    async def _get_contact_from_cache(self, signalhire_id: str) -> Optional[Dict[str, Any]]:
        """Get contact information from cache file."""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    contacts = json.load(f)
                return contacts.get(signalhire_id)
        except Exception as e:
            print(f"    ❌ Error reading cache: {e}")
        return None
    
    async def store_revelation_tracking(self, signalhire_id: str, request_id: str) -> Optional[str]:
        """Store revelation tracking information in Contacts table."""
        try:
            # Load contact details from cache
            contact_info = await self._get_contact_from_cache(signalhire_id)
            if not contact_info:
                print(f"    ⚠️  Contact {signalhire_id} not found in cache")
                return None
                
            profile = contact_info.get('profile', {})
            
            # Get the most recent experience for job title and company
            experience = profile.get('experience', [])
            latest_job = experience[0] if experience else {}
            
            # Create Contact record with REAL information from cache and categorization
            location = profile.get('location', '')
            city, province, country = self._parse_location(location)
            
            tracking_record = {
                "SignalHire ID": signalhire_id,
                "Full Name": profile.get('fullName', f"Contact {signalhire_id[:8]}"),
                "Job Title": latest_job.get('title', ''),
                "Company": latest_job.get('company', ''),
                "Location": location,
                "City": city,
                "Province/State": province,
                "Country": country,
                "Skills": ', '.join(profile.get('skills', [])),
                "Status": "New",
                "Date Added": datetime.now().isoformat(),
                "Source Search": "SignalHire Revelation Request"
            }
            
            # Apply Universal Adaptive categorization
            try:
                categorized_record = await process_contact_with_dynamic_expansion(
                    tracking_record, 
                    signalhire_id, 
                    AIRTABLE_BASE_ID
                )
                tracking_record.update(categorized_record)
                print(f"    🧠 Applied Universal Adaptive categorization")
            except Exception as e:
                print(f"    ⚠️  Categorization failed: {e}")
                # Continue without categorization
            
            # Use MCP Airtable to create the tracking record
            try:
                # Import MCP Airtable at function level to avoid import issues
                import subprocess
                import json
                
                # Use direct MCP call to create the record
                result = await self._create_airtable_record(CONTACTS_TABLE_ID, tracking_record)
                if result and result.get('id'):
                    print(f"    📝 Tracking stored: Record {result['id']} for Request ID {request_id}")
                    return result['id']
                else:
                    print(f"    ⚠️  No record ID returned for tracking")
                    return f"fallback_record_{request_id}"
                    
            except Exception as mcp_error:
                print(f"    ⚠️  MCP error, using fallback tracking: {mcp_error}")
                print(f"    📝 Fallback tracking: SignalHire ID {signalhire_id} -> Request ID {request_id}")
                return f"fallback_record_{request_id}"
            
        except Exception as e:
            print(f"    ❌ Error storing revelation tracking: {e}")
            return None
    
    async def _create_airtable_record(self, table_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper method to create Airtable record using direct Airtable API."""
        try:
            import httpx
            import os
            
            # Get Airtable API key from environment
            api_key = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_TOKEN')
            if not api_key:
                print(f"    ⚠️  No Airtable API key found in environment")
                print(f"    💡 Set AIRTABLE_API_KEY or AIRTABLE_TOKEN environment variable")
                return None
            
            print(f"    📝 Creating Airtable record in table {table_id}")
            
            # Use MCP Airtable tool for proper API handling
            print(f"    🔗 Using MCP Airtable tools")
            
            # Clean fields - remove empty values and handle data types properly
            clean_fields = {}
            for k, v in fields.items():
                if v not in [None, '', [], {}]:
                    clean_fields[k] = v
            
            # Since we can't call MCP tools directly from here, use simple HTTP call
            # but with better error handling
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_id}",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"fields": clean_fields},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"    ✅ Created record: {result['id']}")
                    return result
                else:
                    error_text = response.text
                    print(f"    ❌ Airtable API Error {response.status_code}: {error_text}")
                    return None
                
        except Exception as e:
            print(f"    ❌ Airtable API error: {e}")
            return None
    
    def _parse_location(self, location_str: str) -> tuple[str, str, str]:
        """Parse location string into City, Province, Country components."""
        if not location_str:
            return "", "", ""
        
        # Common patterns:
        # "Calgary, Canada" -> city="Calgary", province="", country="Canada" 
        # "Calgary, Alberta, Canada" -> city="Calgary", province="Alberta", country="Canada"
        # "Calgary, AB" -> city="Calgary", province="AB", country=""
        # "Toronto, Ontario" -> city="Toronto", province="Ontario", country=""
        # "Seattle, WA" -> city="Seattle", province="WA", country=""
        # "Seattle, Washington, USA" -> city="Seattle", province="Washington", country="USA"
        
        parts = [part.strip() for part in location_str.split(',')]
        
        if len(parts) == 1:
            # Just one part - could be city or country
            return parts[0], "", ""
        elif len(parts) == 2:
            # Two parts - check if second is a known country
            city, second = parts
            known_countries = {'Canada', 'USA', 'United States', 'US'}
            if second in known_countries:
                return city, "", second
            else:
                # Assume it's City, Province
                return city, second, ""
        elif len(parts) >= 3:
            # Three or more parts - City, Province, Country
            city = parts[0]
            province = parts[1] 
            country = parts[-1]  # Last part is usually country
            return city, province, country
        
        return "", "", ""
    
    async def format_contact_for_airtable(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format contact data for Airtable insertion with Universal Adaptive categorization."""
        signalhire_id = contact_data['signalhire_id']
        data = contact_data['data']
        profile = data.get('profile', {})
        
        # Get the primary contact info (first revealed contact)
        contacts = data.get('contacts', [])
        primary_contact = contacts[0] if contacts else {}
        
        # Create mock candidate object for enhanced processing
        class MockCandidate:
            def __init__(self, profile, primary_contact):
                self.fullName = profile.get('fullName', '')
                
                # Extract job title from experience (most recent job)
                experience = profile.get('experience', [])
                if experience and isinstance(experience, list) and len(experience) > 0:
                    latest_job = experience[0]  # First item is most recent
                    self.title = latest_job.get('title', '')
                    self.company = latest_job.get('company', '')
                else:
                    self.title = profile.get('title', '')
                    self.company = profile.get('company', '')
                
                # Location handling - location is a string like "Hamilton, Ontario, Canada"
                location = profile.get('location', '')
                if isinstance(location, str) and location:
                    parts = [part.strip() for part in location.split(',')]
                    if len(parts) >= 3:
                        self.city = parts[0]
                        self.province = parts[1] 
                        self.country = parts[2]
                    elif len(parts) == 2:
                        self.city = parts[0]
                        self.country = parts[1]
                        self.province = ''
                    elif len(parts) == 1:
                        self.city = parts[0]
                        self.country = ''
                        self.province = ''
                    else:
                        self.city = ''
                        self.country = ''
                        self.province = ''
                else:
                    self.city = ''
                    self.country = ''
                    self.province = ''
                
                # Contact info
                self.emails = primary_contact.get('emails', [])
                self.phones = primary_contact.get('phones', [])
                self.linkedinUrl = primary_contact.get('linkedinUrl', '') or profile.get('linkedinUrl', '')
                self.facebookUrl = primary_contact.get('facebookUrl', '') or profile.get('facebookUrl', '')
                
                # Skills
                skills = []
                if 'skills' in profile:
                    skill_data = profile['skills']
                    if isinstance(skill_data, list):
                        for skill in skill_data:
                            if isinstance(skill, dict):
                                skills.append(MockSkill(skill.get('name', str(skill))))
                            else:
                                skills.append(MockSkill(str(skill)))
                self.skills = skills
        
        class MockSkill:
            def __init__(self, skill_name: str):
                self.name = skill_name
        
        # Create mock candidate and process with Universal Adaptive System
        candidate = MockCandidate(profile, primary_contact)
        
        # Process with enhanced categorization
        processed_contact = enhanced_processor.process_contact_with_categories(
            signalhire_id, candidate
        )
        
        # Skip dynamic expansion for faster processing
        # processed_contact = await process_contact_with_dynamic_expansion(
        #     processed_contact, signalhire_id, AIRTABLE_BASE_ID
        # )
        print(f"   ⚡ Skipping dynamic expansion for speed")
        
        # Extract basic info with fallbacks
        full_name = processed_contact.get('Full Name', '')
        if not full_name:
            # Try direct fullName from profile
            full_name = profile.get('fullName', '')
        
        # Always extract first/last names for separate fields
        first_name = profile.get('firstName', '') or primary_contact.get('firstName', '')
        last_name = profile.get('lastName', '') or primary_contact.get('lastName', '')
        
        # If we don't have first/last but have full name, try to split it
        if not first_name and not last_name and full_name:
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])
            elif len(name_parts) == 1:
                first_name = name_parts[0]
                last_name = ''
        
        # Final fallback for full name
        if not full_name:
            full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = f"Contact {signalhire_id[:8]}"
        
        # Extract contact information
        emails = primary_contact.get('emails', [])
        phones = primary_contact.get('phones', [])
        
        primary_email = emails[0] if emails else ''
        secondary_email = emails[1] if len(emails) > 1 else ''
        phone_number = phones[0] if phones else ''
        
        # Parse location into City, Province, Country from profile data
        location_str = profile.get('location', '')
        city, province, country = self._parse_location(location_str)
        
        # Create comprehensive Airtable record with categorization
        airtable_record = {
            # Basic contact information
            "SignalHire ID": signalhire_id,
            "Full Name": full_name,
            "Job Title": processed_contact.get('Job Title', ''),
            "Company": processed_contact.get('Company', ''),
            "Location": processed_contact.get('Location', ''),
            "City": city,
            "Province/State": province,
            "Country": country,
            "Primary Email": primary_email,
            "Secondary Email": secondary_email,
            "Phone Number": phone_number,
            "LinkedIn URL": processed_contact.get('LinkedIn URL', ''),
            "Facebook URL": processed_contact.get('Facebook URL', ''),
            "Skills": processed_contact.get('Skills', ''),
            "Status": "New",
            "Date Added": datetime.now().isoformat(),
            "Source Search": "SignalHire Agent - Universal Adaptive System",
            
            # Universal Adaptive categorization fields
            "Primary Trade": processed_contact.get('Primary Trade', ''),
            "Trade Category": processed_contact.get('Trade Category', ''),
            "Trade Hierarchy Level": processed_contact.get('Trade Hierarchy Level', ''),
            "Leadership Role": processed_contact.get('Leadership Role', ''),
            "Years Experience": processed_contact.get('Years Experience', ''),
            "Specializations": processed_contact.get('Specializations', []),
            # Equipment brands - use proper linked record IDs
            "Equipment Brands Used": self._get_or_create_linked_record_ids(
                "tblQ45u548RjR7qwT", "Brand Name", 
                processed_contact.get('Equipment Brands Experience', []), 
                self._equipment_brands_cache
            ),
            "Certifications": processed_contact.get('Certifications', []),
            
            # System metadata
            "Categorization Confidence": processed_contact.get('Categorization Confidence', 0)
        }
        
        # Remove empty fields and sanitize data
        cleaned_record = {k: v for k, v in airtable_record.items() if v}
        return sanitize_for_json(cleaned_record)
    
    async def add_contact_to_airtable(self, contact_record: Dict[str, Any]) -> bool:
        """Add a single contact to Airtable using MCP tools."""
        try:
            print(f"  📤 Adding to Airtable: {contact_record.get('Full Name', 'Unknown')}")
            print(f"     Trade: {contact_record.get('Primary Trade', 'N/A')}")
            print(f"     Category: {contact_record.get('Trade Category', 'N/A')}")
            print(f"     Hierarchy: {contact_record.get('Trade Hierarchy Level', 'N/A')}")
            print(f"     Leadership: {contact_record.get('Leadership Role', 'N/A')}")
            print(f"     Email: {contact_record.get('Primary Email', 'N/A')}")
            print(f"     Phone: {contact_record.get('Phone Number', 'N/A')}")
            print(f"     Company: {contact_record.get('Company', 'N/A')}")
            print(f"     Brands: {contact_record.get('Equipment Brands Used', [])}")
            print(f"     Confidence: {contact_record.get('Categorization Confidence', 0)}")
            
            # Production Airtable API integration
            result = await self._create_airtable_record(CONTACTS_TABLE_ID, contact_record)
            
            if result and result.get('id'):
                print(f"     ✅ Airtable record created: {result['id']}")
                return True
            else:
                print(f"     ❌ Failed to create Airtable record")
                return False
            
        except Exception as e:
            print(f"    ❌ Failed to process contact: {e}")
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
                airtable_record = await self.format_contact_for_airtable(contact_data)
                
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
        
        # Automatically reveal contacts if none have contact info
        if contacts_without_info and not contacts_with_info:
            print(f"\\n🔍 No revealed contacts found. Starting automatic revelation...")
            print(f"   Revealing {len(contacts_without_info)} contacts...")
            
            reveal_results = await processor.reveal_contacts(
                contacts_without_info, 
                max_reveals=len(contacts_without_info)  # Reveal all contacts
            )
            
            print(f"\\n📊 Revelation Results:")
            print(f"   Requested: {reveal_results['requested']}")
            print(f"   Request IDs: {reveal_results['request_ids']}")
            
            if reveal_results['errors']:
                print(f"   Errors: {reveal_results['errors']}")
                
            print(f"\\n⏳ Revelation requests submitted. Waiting for callbacks...")
            print(f"   Results will be processed to Airtable automatically when received.")
            return  # Exit here - callback will handle Airtable processing
        
        # Manual reveal if requested
        elif args.reveal_contacts and contacts_without_info:
            print(f"\\n🔍 Manual revelation requested...")
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