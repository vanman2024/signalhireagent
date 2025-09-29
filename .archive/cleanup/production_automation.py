#!/usr/bin/env python3
"""
PRODUCTION VERSION: 
1. Keeps callback server running
2. Adds revealed contacts directly to Airtable
3. Can process all 114 contacts
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from src.lib.callback_server import CallbackServer
from pyairtable import Api

load_dotenv()

# Airtable configuration
AIRTABLE_BASE_ID = "appNLDGCRSp0J8lMF"
AIRTABLE_TABLE_ID = "tblkPGvvZGCJzYNZw"

def production_callback_handler(callback_data):
    """Production handler that adds contacts to Airtable"""
    print(f"\n🎯 CALLBACK RECEIVED - Processing {len(callback_data)} items")
    
    for i, item in enumerate(callback_data):
        if isinstance(item, dict) and item.get('status') == 'success' and 'candidate' in item:
            candidate = item['candidate']
            name = candidate.get('fullName', 'Unknown')
            contacts = candidate.get('contacts', [])
            
            # Extract contact info
            emails = []
            phones = []
            for contact in contacts:
                if contact.get('type') == 'email':
                    emails.append(contact.get('value'))
                elif contact.get('type') == 'phone':
                    phones.append(contact.get('value'))
            
            # Extract job info
            experience = candidate.get('experience', [])
            current_job = experience[0] if experience else {}
            
            print(f"📧 {name}: {len(emails)} emails, {len(phones)} phones")
            
            if emails or phones:
                # Create Airtable record
                record = {
                    "SignalHire ID": item.get('item', ''),
                    "Full Name": name,
                    "Primary Email": emails[0] if emails else "",
                    "Primary Phone": phones[0] if phones else "",
                    "Job Title": current_job.get('position', ''),
                    "Company": current_job.get('company', ''),
                    "Status": "Revealed",
                    "Source Search": "SignalHire Agent - Production",
                    "Primary Trade": "Heavy Equipment Technician",
                    "Trade Category": "Construction"
                }
                
                print(f"📝 Adding {name} to Airtable...")
                try:
                    # Initialize Airtable API
                    api = Api(os.getenv('AIRTABLE_API_KEY'))
                    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
                    
                    # Create record in Airtable
                    created_record = table.create(record)
                    print(f"✅ {name} added to Airtable! Record ID: {created_record['id']}")
                except Exception as e:
                    print(f"❌ Failed to add {name} to Airtable: {e}")
            else:
                print(f"❌ {name}: No contact info available")

async def reveal_contacts(contact_ids):
    """Reveal multiple contacts"""
    from src.services.signalhire_client import SignalHireClient
    
    client = SignalHireClient(callback_url="https://f59e9ab9847dd3.lhr.life/signalhire/callback")
    
    print(f"🔍 Revealing {len(contact_ids)} contacts...")
    success_count = 0
    
    for i, contact_id in enumerate(contact_ids):
        try:
            result = await client.reveal_contact(contact_id)
            request_id = result.data.get('requestId') if result.data else None
            print(f"✅ {i+1}/{len(contact_ids)}: {contact_id} -> {request_id}")
            success_count += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"❌ {i+1}/{len(contact_ids)}: {contact_id} failed: {e}")
    
    await client.close()
    print(f"📊 Submitted {success_count}/{len(contact_ids)} revelations")
    return success_count

async def main():
    print("🚀 PRODUCTION AUTOMATION - Persistent server + Airtable integration")
    
    # Start persistent callback server
    server = CallbackServer(port=8001)
    server.register_handler("production", production_callback_handler)
    server.start()
    
    print("✅ Persistent callback server running on port 8001")
    print("🌐 Tunnel: https://f59e9ab9847dd3.lhr.life")
    print("📞 Ready to receive callbacks and add to Airtable")
    
    # Load all cached contacts
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        all_contacts = json.load(f)
    
    contact_ids = list(all_contacts.keys())
    print(f"📂 Found {len(contact_ids)} total contacts")
    
    # Run in persistent mode
    print("\n🔄 PERSISTENT MODE: Server stays running")
    choice = "3"
    
    if choice == "1":
        test_contacts = contact_ids[:5]
        await reveal_contacts(test_contacts)
        print("⏳ Waiting for callbacks...")
        await asyncio.sleep(30)
        
    elif choice == "2":
        print("🚨 Processing ALL contacts - this will use credits!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            await reveal_contacts(contact_ids)
            print("⏳ Waiting for all callbacks (2 minutes)...")
            await asyncio.sleep(120)
        else:
            print("❌ Cancelled")
            
    else:
        print("🔄 Server running - use another terminal to make revelation calls")
        print("   Server will stay active until you stop it")
        
        # Keep running indefinitely
        try:
            while True:
                await asyncio.sleep(60)
                print("💓 Server still running...")
        except KeyboardInterrupt:
            print("👋 Stopping server...")
    
    print("✅ Done")

if __name__ == "__main__":
    asyncio.run(main())