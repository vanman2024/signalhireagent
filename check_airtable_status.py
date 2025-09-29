#!/usr/bin/env python3
"""
Quick script to check current Airtable contacts and their statuses
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def check_airtable():
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = 'appQoYINM992nBZ50'
    table_id = 'tbl0uFVaAfcNjT2rS'
    
    headers = {'Authorization': f'Bearer {api_key}'}
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}?maxRecords=10&fields=SignalHire%20ID,Status,Email,LinkedIn%20URL,Name'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        
        print(f'📋 Found {len(data.get("records", []))} contacts in Airtable:')
        print('=' * 60)
        
        for i, record in enumerate(data.get('records', []), 1):
            fields = record.get('fields', {})
            signalhire_id = fields.get('SignalHire ID', 'N/A')
            status = fields.get('Status', 'N/A')
            email = fields.get('Email', 'N/A')
            linkedin = fields.get('LinkedIn URL', 'N/A')
            name = fields.get('Name', 'N/A')
            
            has_linkedin = "Yes" if linkedin != 'N/A' else "No"
            has_email = "Yes" if email != 'N/A' else "No"
            
            print(f'{i:2}. Name: {name}')
            print(f'    ID: {signalhire_id}')
            print(f'    Status: {status}')
            print(f'    Email: {has_email} | LinkedIn: {has_linkedin}')
            print()

if __name__ == "__main__":
    asyncio.run(check_airtable())