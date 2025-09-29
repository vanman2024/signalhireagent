#!/usr/bin/env python3
"""
Update Johnathon Scott Newton-slavin with his revealed contact information.
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

async def update_johnathon():
    """Update Johnathon's contact with revealed information."""
    signalhire_id = "c8920e73c84f4e62955fd0142d2a5a19"
    email = "scttnewton0@gmail.com"
    linkedin = "https://www.linkedin.com/in/johnathon-scott-newton-slavin-b09a17159"
    
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        # Find the record with this SignalHire ID
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
        params = {'filterByFormula': f'{{SignalHire ID}} = "{signalhire_id}"'}
        
        print(f"🔍 Searching for {signalhire_id}...")
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        records = data.get('records', [])
        if not records:
            print(f"❌ No Airtable record found for SignalHire ID: {signalhire_id}")
            return
        
        record = records[0]
        record_id = record['id']
        current_fields = record['fields']
        
        print(f"✅ Found record: {current_fields.get('Full Name')}")
        
        # Prepare update fields
        update_fields = {}
        
        if email and not current_fields.get('Primary Email'):
            update_fields['Primary Email'] = email
            
        if linkedin and not current_fields.get('LinkedIn URL'):
            update_fields['LinkedIn URL'] = linkedin
        
        if not update_fields:
            print("ℹ️  No new information to add")
            return
        
        # Update the record
        update_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}/{record_id}'
        update_data = {'fields': update_fields}
        
        print(f"📝 Updating with: {update_fields}")
        response = await client.patch(update_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            print(f"✅ Successfully updated {signalhire_id}: {update_fields}")
        else:
            print(f"❌ Failed to update {signalhire_id}: {response.text}")

if __name__ == "__main__":
    asyncio.run(update_johnathon())