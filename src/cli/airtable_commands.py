"""
Airtable integration commands for SignalHire Agent CLI.

This module provides commands for syncing revealed contacts to Airtable
through the Universal Adaptive System with intelligent categorization.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import click
import httpx
from click import echo, style

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@click.group()
def airtable():
    """Airtable integration and sync operations."""
    pass


@click.command()
@click.option('--reveal-contacts', is_flag=True, help='Reveal contact information for contacts without details')
@click.option('--force', is_flag=True, help='Force processing even if no contacts have revealed info')
@click.option('--max-reveals', type=int, default=5, help='Maximum number of contacts to reveal (default: 5)')
@click.option('--base-id', type=str, help='Airtable base ID (optional - uses default from config)')
@click.option('--table-name', type=str, default='Contacts', help='Airtable table name (default: Contacts)')
@click.option('--trade-focus', type=str, help='Focus on specific trade for categorization')
def sync(reveal_contacts, force, max_reveals, base_id, table_name, trade_focus):
    """
    Sync revealed contacts to Airtable through Universal Adaptive System.
    
    This command processes cached contacts through the Universal Categorization Engine
    and syncs them to Airtable with intelligent categorization and dynamic field expansion.
    
    Examples:
    
        # Basic sync of existing revealed contacts
        signalhire-agent airtable sync
        
        # Reveal new contacts and sync
        signalhire-agent airtable sync --reveal-contacts --max-reveals 10
        
        # Force sync even without revealed contacts
        signalhire-agent airtable sync --force
        
        # Focus on specific trade
        signalhire-agent airtable sync --trade-focus heavy-equipment
    """
    try:
        echo(f"🚀 {style('SignalHire to Airtable Sync', fg='cyan', bold=True)}")
        echo("=" * 50)
        
        # Build arguments for automation
        automation_args = []
        
        if reveal_contacts:
            automation_args.append('--reveal-contacts')
            
        if force:
            automation_args.append('--force')
            
        if max_reveals != 5:
            automation_args.extend(['--max-reveals', str(max_reveals)])
        
        # Additional options for future enhancement
        if base_id:
            echo(f"📋 Target Airtable Base: {base_id}")
            
        if table_name != 'Contacts':
            echo(f"📊 Target Table: {table_name}")
            
        if trade_focus:
            echo(f"🔧 Trade Focus: {trade_focus}")
        
        # Run the automation
        echo(f"\n📡 Starting automation process...")
        
        # Import and run the automation script functionality
        import subprocess
        import os
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        # Build command
        cmd = [
            sys.executable,
            str(project_root / 'src' / 'services' / 'signalhire_to_airtable_automation.py')
        ] + automation_args
        
        # Run automation
        result = subprocess.run(cmd, env=env, capture_output=False)
        
        if result.returncode == 0:
            echo(f"\n✅ {style('Airtable sync completed successfully!', fg='green')}")
        else:
            echo(f"\n❌ {style('Airtable sync failed', fg='red')}")
            sys.exit(result.returncode)
            
    except ImportError as e:
        echo(f"❌ {style(f'Import error: {e}', fg='red')}")
        echo("Make sure all dependencies are installed and PYTHONPATH is set correctly.")
        sys.exit(1)
    except Exception as e:
        echo(f"❌ {style(f'Sync failed: {e}', fg='red')}")
        sys.exit(1)


@click.command()
def status():
    """Check Airtable integration status and configuration."""
    echo(f"📊 {style('Airtable Integration Status', fg='cyan', bold=True)}")
    echo("=" * 40)
    
    # Check environment variables
    import os
    
    airtable_token = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_TOKEN')
    airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
    
    echo(f"🔑 Airtable API Key: {'✅ Set' if airtable_token else '❌ Not set'}")
    echo(f"📋 Airtable Base ID: {'✅ Set' if airtable_base_id else '❌ Not set'}")
    
    if not airtable_token:
        echo(f"\n💡 {style('Set your Airtable API key:', fg='yellow')}")
        echo("   export AIRTABLE_API_KEY='your-api-key-here'")
        echo("   # Legacy support: export AIRTABLE_TOKEN='your-token-here'")
        
    if not airtable_base_id:
        echo(f"\n💡 {style('Set your Airtable base ID:', fg='yellow')}")
        echo("   export AIRTABLE_BASE_ID='your-base-id-here'")
    
    # Check Airtable integration status
    if airtable_token and airtable_base_id:
        try:
            import httpx
            echo(f"\n📋 Airtable Integration:")
            
            # Test connection to Airtable
            base_id = airtable_base_id
            table_id = os.getenv('AIRTABLE_TABLE_ID', 'tbl0uFVaAfcNjT2rS')
            
            url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
            headers = {"Authorization": f"Bearer {airtable_token}"}
            params = {"maxRecords": 3, "fields": ["Full Name", "Status"]}
            
            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('records', [])
                    echo(f"   🟢 Connection: ✅ Active")
                    echo(f"   📊 Table ID: {table_id}")
                    echo(f"   📝 Sample Records: {len(records)} found")
                    
                    # Count by status if available
                    if records:
                        statuses = {}
                        for record in records:
                            status = record.get('fields', {}).get('Status', 'Unknown')
                            statuses[status] = statuses.get(status, 0) + 1
                        echo(f"   📈 Status Distribution: {dict(statuses)}")
                else:
                    echo(f"   🔴 Connection: ❌ Failed (HTTP {response.status_code})")
                    
        except Exception as e:
            echo(f"   ⚠️  Airtable check failed: {e}")
    else:
        echo(f"\n📋 Airtable Integration: ⚠️  Not configured")
    
    # Show modern workflow steps
    echo(f"\n🚀 Modern Workflow:")
    echo(f"   1. Search → Airtable: signalhire-agent search --to-airtable")
    echo(f"   2. Reveal Contacts: signalhire-agent airtable sync-direct")
    echo(f"   3. Check Status: signalhire-agent airtable status")


@click.command()
@click.option('--signalhire-ids', type=str, help='Comma-separated SignalHire IDs to sync')
@click.option('--max-contacts', type=int, default=10, help='Maximum number of contacts to sync (default: 10)')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without executing')
@click.pass_context
def sync_direct(ctx, signalhire_ids, max_contacts, dry_run):
    """
    Sync contacts directly from SignalHire Person API to Airtable.
    
    This command acts as middleware - it fetches contact data directly from 
    SignalHire's Person API and pushes it to Airtable REST API, bypassing 
    the cache system entirely for a truly cache-free workflow.
    
    Examples:
    
        # Sync specific contacts by SignalHire ID
        signalhire-agent airtable sync-direct --signalhire-ids "abc123,def456"
        
        # Sync up to 20 already-revealed contacts from Airtable
        signalhire-agent airtable sync-direct --max-contacts 20
        
        # Dry run to see what would be synced
        signalhire-agent airtable sync-direct --dry-run
    """
    try:
        echo(f"🔄 {style('Direct SignalHire to Airtable Sync', fg='cyan', bold=True)}")
        echo("=" * 50)
        
        config = ctx.obj['config']
        
        # Validate API keys
        if not config.api_key:
            echo(style("Error: SignalHire API key is required", fg='red'), err=True)
            echo("Set SIGNALHIRE_API_KEY environment variable", err=True)
            ctx.exit(1)
            
        import os
        airtable_api_key = os.getenv('AIRTABLE_API_KEY')
        airtable_base_id = os.getenv('AIRTABLE_BASE_ID', 'appQoYINM992nBZ50')
        airtable_table_id = os.getenv('AIRTABLE_TABLE_ID', 'tbl0uFVaAfcNjT2rS')
        
        if not airtable_api_key:
            echo(style("Error: Airtable API key is required", fg='red'), err=True) 
            echo("Set AIRTABLE_API_KEY environment variable", err=True)
            ctx.exit(1)
        
        echo(f"📡 SignalHire API: {'✅ Ready' if config.api_key else '❌ Missing'}")
        echo(f"📋 Airtable API: {'✅ Ready' if airtable_api_key else '❌ Missing'}")
        echo(f"🎯 Base ID: {airtable_base_id}")
        echo(f"📊 Table ID: {airtable_table_id}")
        
        if dry_run:
            echo(f"\n🧪 {style('DRY RUN MODE - No actual changes will be made', fg='yellow')}")
        
        # Run the sync operation
        asyncio.run(_execute_direct_sync(
            config.api_key,
            airtable_api_key, 
            airtable_base_id,
            airtable_table_id,
            signalhire_ids,
            max_contacts,
            dry_run
        ))
        
    except Exception as e:
        echo(f"❌ {style(f'Sync failed: {e}', fg='red')}")
        if config.debug:
            import traceback
            echo(traceback.format_exc())
        ctx.exit(1)


async def _execute_direct_sync(signalhire_api_key: str, airtable_api_key: str, 
                              airtable_base_id: str, airtable_table_id: str,
                              signalhire_ids: str, max_contacts: int, dry_run: bool):
    """Execute the direct sync operation."""
    import json
    
    echo(f"\n🔍 Starting direct sync operation...")
    
    # Parse SignalHire IDs if provided
    ids_to_sync = []
    if signalhire_ids:
        ids_to_sync = [uid.strip() for uid in signalhire_ids.split(',') if uid.strip()]
        echo(f"📝 Specific IDs to sync: {len(ids_to_sync)}")
    else:
        # Find contacts in Airtable that have SignalHire IDs but no contact info
        echo(f"🔍 Finding contacts in Airtable to sync...")
        ids_to_sync = await _find_airtable_contacts_to_sync(
            airtable_api_key, airtable_base_id, airtable_table_id, max_contacts
        )
        echo(f"📋 Found {len(ids_to_sync)} contacts to sync from Airtable")
    
    if not ids_to_sync:
        echo(f"ℹ️  No contacts found to sync")
        return
    
    if dry_run:
        echo(f"\n🧪 Would sync {len(ids_to_sync)} contacts:")
        for uid in ids_to_sync[:5]:  # Show first 5
            echo(f"   • {uid}")
        if len(ids_to_sync) > 5:
            echo(f"   ... and {len(ids_to_sync) - 5} more")
        return
    
    # Sync each contact
    successful_syncs = 0
    failed_syncs = 0
    
    async with httpx.AsyncClient() as client:
        for uid in ids_to_sync:
            try:
                echo(f"🔄 Syncing contact {uid}...")
                
                # Fetch from SignalHire Person API
                contact_data = await _fetch_signalhire_contact(client, signalhire_api_key, uid)
                
                if contact_data:
                    # Push to Airtable
                    await _update_airtable_contact(
                        client, airtable_api_key, airtable_base_id, 
                        airtable_table_id, uid, contact_data
                    )
                    successful_syncs += 1
                    echo(f"   ✅ Successfully synced {contact_data.get('fullName', uid)}")
                else:
                    failed_syncs += 1
                    echo(f"   ⚠️  No contact data available for {uid}")
                    
            except Exception as e:
                failed_syncs += 1
                echo(f"   ❌ Failed to sync {uid}: {e}")
    
    echo(f"\n📊 Sync Results:")
    echo(f"   ✅ Successful: {successful_syncs}")
    echo(f"   ❌ Failed: {failed_syncs}")
    echo(f"   📋 Total: {len(ids_to_sync)}")


async def _find_airtable_contacts_to_sync(airtable_api_key: str, airtable_base_id: str, 
                                         airtable_table_id: str, max_contacts: int) -> list[str]:
    """Find contacts in Airtable that have SignalHire IDs but missing contact info."""
    
    async with httpx.AsyncClient() as client:
        # Search for records with SignalHire ID but no Primary Email
        url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_id}"
        headers = {"Authorization": f"Bearer {airtable_api_key}"}
        
        params = {
            "filterByFormula": "AND(NOT({SignalHire ID} = ''), OR({Primary Email} = '', {Primary Email} = BLANK()))",
            "maxRecords": max_contacts,
            "fields": ["SignalHire ID", "Full Name"]
        }
        
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        records = data.get('records', [])
        
        signalhire_ids = []
        for record in records:
            fields = record.get('fields', {})
            signalhire_id = fields.get('SignalHire ID')
            if signalhire_id:
                signalhire_ids.append(signalhire_id)
        
        return signalhire_ids


async def _fetch_signalhire_contact(client: httpx.AsyncClient, api_key: str, uid: str) -> dict | None:
    """Fetch contact data from SignalHire Person API."""
    url = f"https://www.signalhire.com/api/v1/candidate/{uid}"
    headers = {"apikey": api_key}
    
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        
        return data
    except httpx.HTTPError as e:
        echo(f"   ⚠️  SignalHire API error for {uid}: {e}")
        return None


async def _update_airtable_contact(client: httpx.AsyncClient, api_key: str, base_id: str,
                                  table_id: str, signalhire_id: str, contact_data: dict):
    """Update or create contact in Airtable with improved deduplication."""
    # First, find existing record by SignalHire ID
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Enhanced search for existing record with better filtering
    search_params = {
        "filterByFormula": f"{{SignalHire ID}} = '{signalhire_id}'",
        "maxRecords": 10  # Get more records to catch all duplicates
    }
    
    response = await client.get(url, headers=headers, params=search_params)
    response.raise_for_status()
    
    existing_records = response.json().get('records', [])
    
    # If multiple records found, log warning about duplicates
    if len(existing_records) > 1:
        echo(f"   ⚠️  Found {len(existing_records)} existing records for {signalhire_id}")
        # Sort by creation date to keep the oldest/most complete
        existing_records.sort(key=lambda r: r.get('createdTime', ''))
        echo(f"   🔄 Will update the first record: {existing_records[0]['id']}")
        
        # Log duplicate record IDs for manual cleanup
        duplicate_ids = [r['id'] for r in existing_records[1:]]
        if duplicate_ids:
            echo(f"   📝 Duplicate records found: {duplicate_ids}")
            # Could add automatic cleanup here later
    
    # Prepare update fields from SignalHire data
    update_fields = _format_signalhire_data_for_airtable(contact_data)
    update_fields['SignalHire ID'] = signalhire_id
    
    # Debug logging for field data
    echo(f"   📋 Formatted fields for {signalhire_id}: {list(update_fields.keys())}")
    
    try:
        if existing_records:
            # Update existing record
            record_id = existing_records[0]['id']
            update_url = f"{url}/{record_id}"
            payload = {"fields": update_fields}
            
            echo(f"   🔄 Updating existing record {record_id}")
            response = await client.patch(update_url, headers=headers, json=payload)
            response.raise_for_status()
        else:
            # Create new record
            payload = {"fields": update_fields}
            echo(f"   ➕ Creating new record for {signalhire_id}")
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        echo(f"   ❌ Airtable API error for {signalhire_id}: HTTP {e.response.status_code}")
        echo(f"   📄 Response body: {e.response.text}")
        echo(f"   📤 Payload sent: {payload}")
        raise


def _format_signalhire_data_for_airtable(contact_data: dict) -> dict:
    """Format SignalHire contact data for Airtable fields."""
    fields = {}
    
    # Basic info
    if contact_data.get('fullName'):
        fields['Full Name'] = contact_data['fullName']
    if contact_data.get('title'):
        fields['Job Title'] = contact_data['title']
    if contact_data.get('company'):
        fields['Company'] = contact_data['company']
    
    # Contact info - extract from contacts array
    contacts = contact_data.get('contacts', [])
    emails = []
    phones = []
    
    for contact in contacts:
        if contact.get('type') == 'email':
            emails.append(contact.get('value'))
        elif contact.get('type') == 'phone':
            phones.append(contact.get('value'))
    
    if emails:
        fields['Primary Email'] = emails[0]
        if len(emails) > 1:
            fields['Secondary Email'] = emails[1]
    
    if phones:
        fields['Phone Number'] = phones[0]
    
    # Location
    location_parts = []
    if contact_data.get('city'):
        location_parts.append(contact_data['city'])
    if contact_data.get('country'):
        location_parts.append(contact_data['country'])
    if location_parts:
        fields['Location'] = ', '.join(location_parts)
    
    # SignalHire Profile URL
    if contact_data.get('uid'):
        fields['SignalHire Profile'] = f"https://www.signalhire.com/candidates/{contact_data['uid']}"
    
    # Social profiles - extract from social array
    social = contact_data.get('social', [])
    for social_profile in social:
        if social_profile.get('type') == 'li':  # LinkedIn
            fields['LinkedIn URL'] = social_profile.get('link')
        elif social_profile.get('type') == 'fb':  # Facebook
            fields['Facebook URL'] = social_profile.get('link')
    
    # Extract all profile types dynamically
    profiles = contact_data.get('profiles', [])
    if profiles:
        profile_field_mapping = {
            'linkedin': 'LinkedIn URL',
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
            
            if profile_url and profile_type in profile_field_mapping:
                field_name = profile_field_mapping[profile_type]
                fields[field_name] = profile_url
    
    # Skills
    skills = contact_data.get('skills', [])
    if skills:
        skill_names = []
        for skill in skills:
            if isinstance(skill, dict):
                skill_names.append(skill.get('name', str(skill)))
            else:
                skill_names.append(str(skill))
        fields['Skills'] = ', '.join(skill_names)
    
    # Status based on contact revelation state using Airtable dropdown option IDs
    # Revelation workflow statuses:
    # "New" = "selHuOMFb98Q1nSpA" - Contact added but no revelation request made yet
    # "Contacted" = "selCdUR2ADvZG8SbI" - Revelation request sent, waiting for results  
    # "Revealed" = "selJfOFUDHriiWSMs" - Has actual contact info (email/phone)
    # "No Contacts" = "selu4tmP79JA16PHe" - Revelation completed but only LinkedIn found
    # NOTE: "Not Interested" should be removed from dropdown (not used in revelation workflow)
    
    # Check revelation results
    has_linkedin = fields.get('LinkedIn URL') is not None
    has_contact_info = emails or phones
    
    if has_contact_info:
        fields['Status'] = 'selJfOFUDHriiWSMs'  # "Revealed" - Has actual contact info (email/phone)
    elif has_linkedin:
        fields['Status'] = 'selu4tmP79JA16PHe'  # "No Contacts" - Only LinkedIn found, no email/phone
    else:
        fields['Status'] = 'selHuOMFb98Q1nSpA'  # "New" - No revelation data available
    
    return fields


# Add commands to the airtable group
airtable.add_command(sync)
airtable.add_command(status)
airtable.add_command(sync_direct)