#!/usr/bin/env python3
"""
Find and analyze duplicate contacts in Airtable
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

async def find_duplicates():
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = 'appQoYINM992nBZ50'
    table_id = 'tbl0uFVaAfcNjT2rS'
    
    headers = {'Authorization': f'Bearer {api_key}'}
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}?fields=SignalHire%20ID,Name,Email,LinkedIn%20URL'
    
    all_records = []
    offset = None
    
    async with httpx.AsyncClient() as client:
        while True:
            params = {}
            if offset:
                params['offset'] = offset
                
            response = await client.get(url, headers=headers, params=params)
            data = response.json()
            
            records = data.get('records', [])
            all_records.extend(records)
            
            offset = data.get('offset')
            if not offset:
                break
    
    print(f'📊 Total records found: {len(all_records)}')
    print('=' * 60)
    
    # Group by SignalHire ID
    by_signalhire_id = defaultdict(list)
    # Group by Name 
    by_name = defaultdict(list)
    # Group by Email
    by_email = defaultdict(list)
    
    for record in all_records:
        fields = record.get('fields', {})
        record_id = record.get('id')
        
        signalhire_id = fields.get('SignalHire ID', '')
        name = fields.get('Name', '')
        email = fields.get('Email', '')
        
        if signalhire_id:
            by_signalhire_id[signalhire_id].append((record_id, fields))
        if name:
            by_name[name].append((record_id, fields))
        if email:
            by_email[email].append((record_id, fields))
    
    # Find duplicates
    print("🔍 DUPLICATE ANALYSIS:")
    print()
    
    signalhire_duplicates = {k: v for k, v in by_signalhire_id.items() if len(v) > 1}
    name_duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
    email_duplicates = {k: v for k, v in by_email.items() if len(v) > 1}
    
    if signalhire_duplicates:
        print(f"🆔 SignalHire ID Duplicates: {len(signalhire_duplicates)} sets")
        for signalhire_id, records in signalhire_duplicates.items():
            print(f"   ID: {signalhire_id} - {len(records)} records:")
            for record_id, fields in records:
                print(f"     • {record_id}: {fields.get('Name', 'No Name')}")
        print()
    
    if name_duplicates:
        print(f"👤 Name Duplicates: {len(name_duplicates)} sets")
        for name, records in name_duplicates.items():
            print(f"   Name: {name} - {len(records)} records:")
            for record_id, fields in records:
                print(f"     • {record_id}: SH_ID={fields.get('SignalHire ID', 'N/A')}")
        print()
    
    if email_duplicates:
        print(f"📧 Email Duplicates: {len(email_duplicates)} sets")
        for email, records in email_duplicates.items():
            print(f"   Email: {email} - {len(records)} records:")
            for record_id, fields in records:
                print(f"     • {record_id}: {fields.get('Name', 'No Name')}")
        print()
    
    if not (signalhire_duplicates or name_duplicates or email_duplicates):
        print("✅ No duplicates found!")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Records: {len(all_records)}")
    print(f"   SignalHire ID Duplicates: {sum(len(v) for v in signalhire_duplicates.values())}")
    print(f"   Name Duplicates: {sum(len(v) for v in name_duplicates.values())}")
    print(f"   Email Duplicates: {sum(len(v) for v in email_duplicates.values())}")

if __name__ == "__main__":
    asyncio.run(find_duplicates())