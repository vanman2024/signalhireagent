#!/usr/bin/env python3
"""
Simple SignalHire callback server on port 8000.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

app = FastAPI(title="SignalHire Callback Server", version="1.0.0")

async def update_airtable_contact(signalhire_id: str, email: str = None, phone: str = None, secondary_email: str = None, profile_urls: dict = None):
    """Update Airtable contact with revealed information."""
    import httpx
    
    # Find the record with this SignalHire ID
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        # Search for record with this SignalHire ID
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
        params = {'filterByFormula': f'{{SignalHire ID}} = "{signalhire_id}"'}
        
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        records = data.get('records', [])
        if not records:
            logger.warning(f"No Airtable record found for SignalHire ID: {signalhire_id}")
            return
        
        record = records[0]
        record_id = record['id']
        current_fields = record['fields']
        
        # Prepare update fields
        update_fields = {}
        
        if email and not current_fields.get('Primary Email'):
            update_fields['Primary Email'] = email
            
        if secondary_email and not current_fields.get('Secondary Email'):
            update_fields['Secondary Email'] = secondary_email
            
        if phone and not current_fields.get('Phone Number'):
            update_fields['Phone Number'] = phone
        
        # Handle profile URLs dynamically
        if profile_urls:
            # Map profile types to Airtable field names
            profile_field_mapping = {
                'linkedin': 'LinkedIn',
                'facebook': 'Facebook', 
                'twitter': 'Twitter',
                'instagram': 'Instagram',
                'vimeo': 'Vimeo',
                'youtube': 'YouTube',
                'github': 'GitHub',
                'behance': 'Behance',
                'dribbble': 'Dribbble'
            }
            
            for profile_type, profile_url in profile_urls.items():
                field_name = profile_field_mapping.get(profile_type.lower())
                if field_name and profile_url and not current_fields.get(field_name):
                    update_fields[field_name] = profile_url
        
        # Update Status field - set to "Revealed" if we have contact info, "No Contacts" if we don't
        if email or phone_number or secondary_email or profile_urls:
            update_fields['Status'] = 'Revealed'
        else:
            update_fields['Status'] = 'No Contacts'
        
        if not update_fields:
            logger.info(f"No new contact info to update for {signalhire_id}")
            return
        
        # Update the record
        update_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}/{record_id}'
        update_data = {'fields': update_fields}
        
        response = await client.patch(update_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            logger.info(f"✅ Updated {signalhire_id}: {update_fields}")
        else:
            logger.error(f"❌ Failed to update {signalhire_id}: {response.text}")

async def process_callback_data(request_id: str, callback_data: list):
    """Process SignalHire callback data."""
    logger.info(f"Processing callback {request_id} with {len(callback_data)} items")
    
    for item in callback_data:
        try:
            # Log the complete item structure to understand what's available
            logger.info(f"🔍 FULL CALLBACK ITEM: {json.dumps(item, indent=2)}")
            
            if item.get('status') != 'success':
                logger.warning(f"Item {item.get('item')} failed: {item.get('status')}")
                continue
                
            candidate = item.get('candidate', {})
            if not candidate:
                logger.warning(f"No candidate data for item {item.get('item')}")
                continue
            
            signalhire_id = item.get('item')
            emails = candidate.get('emails', [])
            phones = candidate.get('phones', [])
            profiles = candidate.get('profiles', [])
            
            # Extract email addresses
            primary_email = None
            secondary_email = None
            
            if emails:
                for email_obj in emails:
                    email_addr = email_obj.get('email')
                    if email_addr:
                        if not primary_email:
                            primary_email = email_addr
                        elif not secondary_email and email_addr != primary_email:
                            secondary_email = email_addr
            
            # Extract phone number
            phone_number = None
            if phones:
                for phone_obj in phones:
                    phone_num = phone_obj.get('phone')
                    if phone_num:
                        phone_number = phone_num
                        break
            
            # Extract profile URLs dynamically
            profile_urls = {}
            
            if profiles:
                for profile_obj in profiles:
                    profile_type = profile_obj.get('type', '').lower()
                    profile_url = profile_obj.get('url')
                    
                    if profile_url and profile_type:
                        profile_urls[profile_type] = profile_url
            
            # Update Airtable
            if primary_email or phone_number or secondary_email or profile_urls:
                await update_airtable_contact(
                    signalhire_id=signalhire_id,
                    email=primary_email,
                    phone=phone_number,
                    secondary_email=secondary_email,
                    profile_urls=profile_urls
                )
                
                # Create profile info display
                profiles_info = []
                profile_icons = {
                    'linkedin': '🔗 LinkedIn',
                    'facebook': '📘 Facebook', 
                    'twitter': '🐦 Twitter',
                    'instagram': '📷 Instagram',
                    'vimeo': '🎬 Vimeo',
                    'youtube': '📺 YouTube',
                    'github': '💻 GitHub',
                    'behance': '🎨 Behance',
                    'dribbble': '🏀 Dribbble'
                }
                
                for profile_type in profile_urls.keys():
                    icon = profile_icons.get(profile_type, f"🌐 {profile_type.title()}")
                    profiles_info.append(icon)
                
                logger.info(f"📧 {signalhire_id}: {primary_email or 'no email'} | 📞 {phone_number or 'no phone'} | {' | '.join(profiles_info) if profiles_info else 'no profiles'}")
            else:
                logger.warning(f"No contact info found for {signalhire_id}")
                
        except Exception as e:
            logger.error(f"Error processing item {item.get('item', 'unknown')}: {e}")

@app.post("/signalhire/callback")
async def handle_callback(request: Request, background_tasks: BackgroundTasks):
    """Handle SignalHire callback."""
    try:
        # Get request ID from headers
        request_id = request.headers.get("Request-Id")
        if not request_id:
            logger.warning("Callback received without Request-Id header")
            request_id = "unknown"
        
        # Parse callback data
        callback_data = await request.json()
        
        logger.info(f"🔔 Received callback {request_id} with {len(callback_data)} items")
        
        # Process in background
        background_tasks.add_task(process_callback_data, request_id, callback_data)
        
        return JSONResponse(
            status_code=200,
            content={"status": "accepted", "request_id": request_id}
        )
        
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "signalhire-callback"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "SignalHire Callback Server",
        "version": "1.0.0",
        "callback_endpoint": "/signalhire/callback"
    }

if __name__ == "__main__":
    print("🚀 Starting SignalHire callback server on port 8000...")
    print("📡 Callback URL: http://localhost:8000/signalhire/callback")
    print("✅ Ready to receive SignalHire callbacks")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")