import json
import os
from typing import Any
import httpx


async def load_contacts_from_airtable() -> list[dict[str, Any]]:
    """Load contacts from Airtable instead of JSON files."""
    airtable_api_key = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_TOKEN')
    if not airtable_api_key:
        print("❌ AIRTABLE_API_KEY not found in environment")
        return []
    
    base_id = os.getenv('AIRTABLE_BASE_ID', 'appQoYINM992nBZ50')
    table_id = os.getenv('AIRTABLE_TABLE_ID', 'tbl0uFVaAfcNjT2rS')
    
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {airtable_api_key}"}
    
    contacts = []
    offset = None
    
    async with httpx.AsyncClient() as client:
        while True:
            params = {"pageSize": 100}
            if offset:
                params["offset"] = offset
                
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                records = data.get('records', [])
                for record in records:
                    fields = record.get('fields', {})
                    # Convert Airtable record to contact format
                    contact = {
                        'uid': fields.get('SignalHire ID', record.get('id')),
                        'name': fields.get('Full Name', ''),
                        'linkedin_url': fields.get('LinkedIn URL', ''),
                        'job_title': fields.get('Job Title', ''),
                        'company': fields.get('Company', ''),
                        'email': fields.get('Primary Email', ''),
                        'phone': fields.get('Phone Number', ''),
                        'location': fields.get('Location', ''),
                        'status': fields.get('Status', ''),
                        'airtable_id': record.get('id')
                    }
                    contacts.append(contact)
                
                offset = data.get('offset')
                if not offset:
                    break
                    
            except Exception as e:
                print(f"❌ Error loading contacts from Airtable: {e}")
                break
    
    return contacts


def load_contacts_from_files(file_paths: list[str]) -> list[dict[str, Any]]:
    contacts = []
    for path in file_paths:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                contacts.extend(data)
            elif isinstance(data, dict) and 'contacts' in data:
                contacts.extend(data['contacts'])
            elif isinstance(data, dict):
                # Try to find contact-like data in any array field
                for key, value in data.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        # Check if this looks like contact data (has name or uid or linkedin_url)
                        first_item = value[0]
                        if any(
                            field in first_item
                            for field in ['name', 'uid', 'linkedin_url', 'job_title']
                        ):
                            contacts.extend(value)
                            break
                else:
                    # No contact-like data found, log warning but continue
                    print(
                        f"Warning: No recognizable contact data found in {path}, skipping file"
                    )
            else:
                print(f"Warning: Unrecognized JSON format in {path}, skipping file")
    return contacts


def deduplicate_contacts(contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate contacts using uid, SignalHire ID, LinkedIn URL, or email."""
    seen_uids = set()
    seen_linkedin = set()
    seen_emails = set()
    deduped = []
    
    for c in contacts:
        # Check multiple UID fields (Airtable and legacy formats)
        uid = c.get('uid') or c.get('SignalHire ID') or c.get('airtable_id')
        linkedin = c.get('linkedin_url') or c.get('LinkedIn URL')
        email = c.get('email') or c.get('Primary Email')
        
        # Primary deduplication by UID
        if uid and uid not in seen_uids:
            seen_uids.add(uid)
            deduped.append(c)
        # Secondary deduplication by LinkedIn URL
        elif not uid and linkedin and linkedin not in seen_linkedin:
            seen_linkedin.add(linkedin)
            deduped.append(c)
        # Tertiary deduplication by email
        elif not uid and not linkedin and email and email not in seen_emails:
            seen_emails.add(email)
            deduped.append(c)
        # else: duplicate, skip
        
    return deduped


async def save_contacts_to_airtable(contacts: list[dict[str, Any]]) -> bool:
    """Save deduplicated contacts back to Airtable (updates existing records)."""
    airtable_api_key = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_TOKEN')
    if not airtable_api_key:
        print("❌ AIRTABLE_API_KEY not found in environment")
        return False
    
    base_id = os.getenv('AIRTABLE_BASE_ID', 'appQoYINM992nBZ50')
    table_id = os.getenv('AIRTABLE_TABLE_ID', 'tbl0uFVaAfcNjT2rS')
    
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {airtable_api_key}"}
    
    success_count = 0
    
    async with httpx.AsyncClient() as client:
        # Process in batches of 10 (Airtable limit)
        for i in range(0, len(contacts), 10):
            batch = contacts[i:i+10]
            records = []
            
            for contact in batch:
                airtable_id = contact.get('airtable_id')
                if not airtable_id:
                    continue  # Skip contacts without Airtable ID
                    
                # Convert back to Airtable format
                fields = {
                    'Full Name': contact.get('name', ''),
                    'SignalHire ID': contact.get('uid', ''),
                    'Job Title': contact.get('job_title', ''),
                    'Company': contact.get('company', ''),
                    'LinkedIn URL': contact.get('linkedin_url', ''),
                    'Primary Email': contact.get('email', ''),
                    'Phone Number': contact.get('phone', ''),
                    'Location': contact.get('location', ''),
                    'Status': contact.get('status', 'Deduplicated')
                }
                
                # Only include non-empty fields
                filtered_fields = {k: v for k, v in fields.items() if v}
                
                records.append({
                    'id': airtable_id,
                    'fields': filtered_fields
                })
            
            if not records:
                continue
                
            try:
                response = await client.patch(url, headers=headers, json={'records': records})
                response.raise_for_status()
                success_count += len(records)
                print(f"✅ Updated {len(records)} contacts in Airtable")
                
            except Exception as e:
                print(f"❌ Error updating batch to Airtable: {e}")
                
    print(f"📊 Successfully updated {success_count}/{len(contacts)} contacts")
    return success_count > 0


def save_contacts_to_file(contacts: list[dict[str, Any]], output_path: str):
    with open(output_path, 'w') as f:
        json.dump(contacts, f, indent=2)


def create_backup_files(file_paths: list[str]) -> list[str]:
    """Create backup copies of input files before processing."""
    import shutil
    from datetime import datetime

    backup_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for file_path in file_paths:
        if not file_path or not file_path.strip():
            continue

        # Create backup filename
        path_parts = file_path.rsplit('.', 1)
        if len(path_parts) == 2:
            backup_path = f"{path_parts[0]}_backup_{timestamp}.{path_parts[1]}"
        else:
            backup_path = f"{file_path}_backup_{timestamp}"

        try:
            shutil.copy2(file_path, backup_path)
            backup_paths.append(backup_path)
            print(f"Created backup: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup for {file_path}: {e}")

    return backup_paths
