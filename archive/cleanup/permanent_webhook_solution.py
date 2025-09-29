#!/usr/bin/env python3
"""
Permanent webhook solution for SignalHire callbacks.
Addresses the 1-hour tunnel limitation with persistent alternatives.
"""

import asyncio
import json
import os
import time
from dotenv import load_dotenv
from src.services.signalhire_client import SignalHireClient
from pyairtable import Api

load_dotenv()

# Airtable configuration from environment
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

class PermanentWebhookSolution:
    """Solutions for permanent webhook handling"""
    
    def __init__(self):
        self.solutions = {
            "webhook_site": "https://webhook.site - Free permanent URLs",
            "ngrok_auth": "ngrok with authenticated account - Persistent subdomains",
            "railway_deploy": "Deploy callback server to Railway - Public URL",
            "polling_approach": "Poll SignalHire API for completed requests"
        }
    
    def show_solutions(self):
        print("🔧 PERMANENT WEBHOOK SOLUTIONS:")
        print("=" * 50)
        
        print("\n1. 🌐 Webhook.site (Immediate Solution)")
        print("   - Go to https://webhook.site")
        print("   - Get permanent URL like: https://webhook.site/unique-id")
        print("   - No setup required, works immediately")
        print("   - Can view/download webhook data from web interface")
        
        print("\n2. 🚀 Railway Deployment (Recommended)")
        print("   - Deploy our callback server to Railway")
        print("   - Get permanent public URL")
        print("   - Automated Airtable integration")
        print("   - Scale automatically")
        
        print("\n3. 📡 Ngrok with Authentication")
        print("   - Sign up at https://dashboard.ngrok.com/signup")
        print("   - Get persistent subdomain")
        print("   - More reliable than localhost.run")
        
        print("\n4. 🔄 API Polling Approach")
        print("   - Submit revelation requests")
        print("   - Poll SignalHire API for completion status")
        print("   - No webhook needed")
        
    async def test_webhook_site_approach(self):
        """Test using webhook.site for immediate solution"""
        print("\n🧪 WEBHOOK.SITE APPROACH:")
        print("1. Go to https://webhook.site")
        print("2. Copy the unique URL (e.g., https://webhook.site/abc123)")
        print("3. Use that URL as your callback URL")
        print("4. Check the webhook.site page to see incoming data")
        print("5. Download the JSON data manually")
        
        webhook_url = input("Enter your webhook.site URL (or press Enter to skip): ").strip()
        
        if webhook_url and webhook_url.startswith("https://webhook.site/"):
            print(f"✅ Using webhook URL: {webhook_url}")
            await self.submit_test_revelations(webhook_url)
            print("📱 Check your webhook.site page for incoming callbacks!")
        else:
            print("⏭️ Skipping webhook.site test")
    
    async def submit_test_revelations(self, callback_url):
        """Submit test revelations with given callback URL"""
        # Load cached contacts
        cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
        with open(cache_file, 'r') as f:
            all_contacts = json.load(f)
        
        contact_ids = list(all_contacts.keys())[:3]  # Just 3 for testing
        
        client = SignalHireClient(callback_url=callback_url)
        
        print(f"🔍 Submitting {len(contact_ids)} revelation requests...")
        success_count = 0
        
        for i, contact_id in enumerate(contact_ids):
            try:
                result = await client.reveal_contact(contact_id)
                request_id = result.data.get('requestId') if result.data else None
                print(f"✅ {i+1}/{len(contact_ids)}: {contact_id} -> {request_id}")
                success_count += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ {i+1}/{len(contact_ids)}: {contact_id} failed: {e}")
        
        await client.close()
        print(f"📊 Submitted {success_count}/{len(contact_ids)} revelation requests")
        
        if success_count > 0:
            print(f"\n⏳ Callbacks should arrive at: {callback_url}")
            print("📥 Check the webhook.site page to see the contact data")
    
    def suggest_railway_deployment(self):
        """Suggest Railway deployment for permanent solution"""
        print("\n🚀 RAILWAY DEPLOYMENT SOLUTION:")
        print("=" * 40)
        
        print("Benefits:")
        print("✅ Permanent public URL")
        print("✅ Automatic Airtable integration")  
        print("✅ No tunnel limitations")
        print("✅ Scales automatically")
        print("✅ Free tier available")
        
        print("\nQuick Setup:")
        print("1. Push code to GitHub")
        print("2. Connect Railway to GitHub")
        print("3. Deploy callback server")
        print("4. Use Railway URL for SignalHire callbacks")
        
        print("\nFiles needed:")
        print("- src/lib/callback_server.py (✅ already exists)")
        print("- production_automation.py (✅ already exists)")
        print("- requirements.txt")
        print("- Procfile or railway.json")
        
    async def test_polling_approach(self):
        """Test polling approach as alternative to webhooks"""
        print("\n🔄 POLLING APPROACH (Experimental):")
        print("=" * 40)
        
        print("This approach:")
        print("1. Submit revelation requests")
        print("2. Store request IDs")
        print("3. Poll SignalHire API for completion")
        print("4. Process completed revelations")
        
        # This would require finding a status endpoint in SignalHire API
        print("\n❓ Need to investigate SignalHire API for status endpoints")
        print("📚 Check API documentation for request status checking")

async def main():
    print("🔧 PERMANENT WEBHOOK SOLUTION")
    print("=" * 50)
    
    solution = PermanentWebhookSolution()
    solution.show_solutions()
    
    print("\nWhich solution would you like to try?")
    print("1. Test webhook.site approach (immediate)")
    print("2. Show Railway deployment guide")
    print("3. Test polling approach (experimental)")
    print("4. Just add all profiles to Airtable (no contacts)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        await solution.test_webhook_site_approach()
    elif choice == "2":
        solution.suggest_railway_deployment()
    elif choice == "3":
        await solution.test_polling_approach()
    elif choice == "4":
        print("\n📋 Adding all cached profiles to Airtable...")
        await add_all_profiles_to_airtable()
    else:
        print("❌ Invalid choice")

async def add_all_profiles_to_airtable():
    """Add all cached profiles to Airtable (without contact info)"""
    cache_file = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"
    with open(cache_file, 'r') as f:
        all_contacts = json.load(f)
    
    api = Api(os.getenv('AIRTABLE_API_KEY'))
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
    
    print(f"📂 Processing {len(all_contacts)} cached profiles...")
    success_count = 0
    
    for i, (contact_id, contact_data) in enumerate(all_contacts.items()):
        profile = contact_data.get('profile', {})
        name = profile.get('fullName', 'Unknown')
        experience = profile.get('experience', [])
        current_job = experience[0] if experience else {}
        
        try:
            # Parse location into components
            location = profile.get('location', '')
            location_parts = location.split(', ') if location else []
            city = location_parts[0] if len(location_parts) > 0 else ''
            province_state = location_parts[1] if len(location_parts) > 1 else ''
            country = location_parts[2] if len(location_parts) > 2 else location_parts[1] if len(location_parts) == 2 else ''
            
            record = {
                "Full Name": name,
                "Job Title": current_job.get('title', ''),
                "Company": current_job.get('company', ''),
                "Location": location,
                "City": city,
                "Province/State": province_state,
                "Country": country,
                "Status": "New",
                "Skills": ", ".join(profile.get('skills', [])[:5]),
                "SignalHire ID": contact_id,
                "Source Search": "SignalHire Agent - Complete Import",
                "Primary Trade": "Heavy Duty Equipment Technician",
                "Trade Category": "Heavy Equipment"
            }
            
            created_record = table.create(record)
            print(f"✅ {i+1}/{len(all_contacts)}: {name} -> {created_record['id']}")
            success_count += 1
            
            # Small delay to be respectful to Airtable API
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"❌ {i+1}/{len(all_contacts)}: {name} failed: {e}")
    
    print(f"\n📊 Added {success_count}/{len(all_contacts)} profiles to Airtable")
    print("📧 Contact information can be added later when revelation process works")

if __name__ == "__main__":
    asyncio.run(main())