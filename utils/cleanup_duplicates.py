#!/usr/bin/env python3
"""
Clean up duplicate contacts in Airtable based on SignalHire ID
Using direct HTTP calls to Airtable API
"""
import asyncio
import os
import httpx
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

async def cleanup_duplicates():
    """Find and remove duplicate contacts, keeping the most complete record."""
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = 'appQoYINM992nBZ50'
    table_id = 'tbl0uFVaAfcNjT2rS'
    
    if not api_key:
        print("❌ AIRTABLE_API_KEY not found in environment")
        return
    
    headers = {'Authorization': f'Bearer {api_key}'}
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
    
    print("🔍 Fetching all records...")
    
    all_records = []
    offset = None
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                params = {'maxRecords': 100}
                if offset:
                    params['offset'] = offset
                    
                response = await client.get(url, headers=headers, params=params)
                data = response.json()
                
                records = data.get('records', [])
                if not records:
                    break
                    
                all_records.extend(records)
                print(f"  Fetched {len(records)} records (total: {len(all_records)})")
                
                offset = data.get('offset')
                if not offset:
                    break
                    
            except Exception as e:
                print(f"Error fetching records: {e}")
                break
    
    print(f"\n📊 Total records: {len(all_records)}")
    
    # Group by SignalHire ID
    by_signalhire_id = defaultdict(list)
    
    for record in all_records:
        fields = record.get('fields', {})
        signalhire_id = fields.get('SignalHire ID', '')
        
        if signalhire_id:
            by_signalhire_id[signalhire_id].append(record)
    
    # Find duplicates
    duplicates = {k: v for k, v in by_signalhire_id.items() if len(v) > 1}
    
    print(f"🔍 Found {len(duplicates)} SignalHire IDs with duplicates")
    
    records_to_delete = []
    
    for signalhire_id, records in duplicates.items():
        print(f"\n🆔 SignalHire ID: {signalhire_id} ({len(records)} records)")
        
        # Score records by completeness
        scored_records = []
        for record in records:
            fields = record.get('fields', {})
            score = 0
            
            # Score based on field completeness
            if fields.get('Primary Email'): score += 5
            if fields.get('Secondary Email'): score += 3
            if fields.get('Phone Number'): score += 4
            if fields.get('LinkedIn URL'): score += 2
            if fields.get('SignalHire Profile'): score += 1
            if fields.get('Skills'): score += 2
            if len(fields.get('Skills', '')) > 100: score += 1  # More detailed skills
            
            scored_records.append((score, record))
        
        # Sort by score (highest first)
        scored_records.sort(key=lambda x: x[0], reverse=True)
        
        # Keep the best record, mark others for deletion
        best_record = scored_records[0][1]
        duplicates_to_delete = [r[1] for r in scored_records[1:]]
        
        print(f"  ✅ Keeping: {best_record['id']} (score: {scored_records[0][0]})")
        for dup in duplicates_to_delete:
            score = next(s for s, r in scored_records if r['id'] == dup['id'])
            print(f"  ❌ Deleting: {dup['id']} (score: {score})")
            records_to_delete.append(dup['id'])
    
        if records_to_delete:
            print(f"\n🗑️  Deleting {len(records_to_delete)} duplicate records...")
            
            # Delete in batches of 10 (Airtable limit)
            for i in range(0, len(records_to_delete), 10):
                batch = records_to_delete[i:i+10]
                try:
                    delete_url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
                    params = {'records[]': batch}
                    
                    response = await client.delete(delete_url, headers=headers, params=params)
                    if response.status_code == 200:
                        deleted_data = response.json()
                        deleted_count = len(deleted_data.get('records', []))
                        print(f"  ✅ Deleted batch {i//10 + 1}: {deleted_count} records")
                    else:
                        print(f"  ❌ Error deleting batch {i//10 + 1}: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"  ❌ Error deleting batch {i//10 + 1}: {e}")
        else:
            print("\n✅ No duplicates to delete!")
        
        print(f"\n🎉 Cleanup complete! Removed {len(records_to_delete)} duplicate records.")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())