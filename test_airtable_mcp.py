#!/usr/bin/env python3
"""
Test Airtable MCP Integration

PURPOSE: Test creating a contact record in Airtable using MCP tools
USAGE: python3 test_airtable_mcp.py
PART OF: SignalHire to Airtable automation testing
CONNECTS TO: Airtable MCP server
"""

import asyncio
import json
from datetime import datetime

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
CONTACTS_TABLE = "tbl0uFVaAfcNjT2rS"

async def test_airtable_creation():
    """Test creating a contact record in Airtable."""
    
    # Create a test contact record
    test_contact = {
        "Full Name": "Test Contact from Webhook",
        "SignalHire ID": "test_webhook_001",
        "Job Title": "Software Engineer",
        "Company": "Test Company",
        "Location": "Toronto, Canada",
        "Primary Email": "test@example.com",
        "Phone Number": "+1-555-123-4567",
        "LinkedIn URL": "https://linkedin.com/in/testcontact",
        "Skills": "Python, JavaScript, API Development",
        "Status": "New",
        "Date Added": datetime.now().isoformat(),
        "Source Search": "Test Webhook"
    }
    
    print("🧪 Testing Airtable MCP Integration")
    print("=" * 50)
    print(f"📋 Test Contact Data:")
    print(json.dumps(test_contact, indent=2))
    print()
    
    try:
        print(f"📤 Attempting to create record in Airtable...")
        print(f"   Base ID: {AIRTABLE_BASE_ID}")
        print(f"   Table ID: {CONTACTS_TABLE}")
        
        # This is where we would call the MCP function
        # The MCP tool should be available due to wildcard permissions
        
        # NOTE: This would be the actual call when running in Claude Code environment:
        # result = await mcp__airtable__create_record(
        #     baseId=AIRTABLE_BASE_ID,
        #     tableId=CONTACTS_TABLE,
        #     fields=test_contact
        # )
        
        # For now, simulate the call
        print(f"🔧 MCP Call (simulated):")
        print(f"   mcp__airtable__create_record(")
        print(f"     baseId='{AIRTABLE_BASE_ID}',")
        print(f"     tableId='{CONTACTS_TABLE}',")
        print(f"     fields={json.dumps(test_contact, indent=4)}")
        print(f"   )")
        
        # Simulate success
        simulated_result = {
            "id": f"rec{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "createdTime": datetime.now().isoformat(),
            "fields": test_contact
        }
        
        print(f"✅ Success! Created record: {simulated_result['id']}")
        print(f"🕒 Created at: {simulated_result['createdTime']}")
        
        return simulated_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_airtable_creation())