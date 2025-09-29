#!/usr/bin/env python3
"""
Test the callback processing fix.
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.complete_airtable_automation import CompleteAirtableAutomation
from lib.custom_logging import setup_error_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_error_logging()

async def test_callback_fix():
    """Test that callback processing is working."""
    print("🔧 Testing callback processing fix...")
    
    # Load some cached contacts to test
    cache_file = os.path.expanduser("~/.signalhire-agent/cache/revealed_contacts.json")
    
    if not os.path.exists(cache_file):
        print("❌ No cached contacts found. Please run the automation first.")
        return
    
    with open(cache_file, 'r') as f:
        contacts = json.load(f)
    
    print(f"📂 Found {len(contacts)} cached contacts")
    
    # Initialize automation
    automation = CompleteAirtableAutomation()
    
    # Start services
    await automation.start_services()
    
    print(f"🌐 Callback server URL: {automation.webhook_url}")
    print("✅ Services started successfully")
    
    # Test revealing just 2 contacts to see if callback processing works
    test_contacts = list(contacts.values())[:2]
    contact_ids = [contact['contact_id'] for contact in test_contacts]
    
    print(f"🧪 Testing callback fix with {len(contact_ids)} contacts: {contact_ids}")
    
    # Process contacts for revelation 
    results = await automation.process_contacts_for_revelation(contact_ids)
    
    print(f"📤 Submitted {len(results)} revelation requests")
    for result in results:
        if result['status'] == 'success':
            print(f"✅ Request {result['request_id']} submitted successfully")
        else:
            print(f"❌ Request failed: {result.get('error', 'Unknown error')}")
    
    # Wait for callbacks (should be very fast)
    print("⏳ Waiting 10 seconds for callbacks...")
    await asyncio.sleep(10)
    
    # Check stats
    print(f"📊 Automation stats: {automation.stats}")
    
    # Stop services
    await automation.stop_services()
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_callback_fix())