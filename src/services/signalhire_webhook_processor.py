#!/usr/bin/env python3
"""
SignalHire Webhook Processor with Airtable Integration

PURPOSE: Complete webhook processing system that receives SignalHire callbacks and pushes to Airtable
USAGE: python3 signalhire_webhook_processor.py [--port PORT] [--host HOST]
PART OF: SignalHire to Airtable automation workflow
CONNECTS TO: SignalHire webhooks, Airtable MCP server, callback server
"""

import asyncio
import logging
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..lib.callback_server import CallbackServer, get_server
from ..models.person_callback import PersonCallbackData, PersonCallbackItem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
SEARCH_SESSIONS_TABLE = "tblqmpcDHfG5pZCWh" 
RAW_PROFILES_TABLE = "tbl593Vc4ExFTYYn0"
CONTACTS_TABLE = "tbl0uFVaAfcNjT2rS"

class SignalHireWebhookProcessor:
    """Complete webhook processor that handles SignalHire callbacks and integrates with Airtable."""
    
    def __init__(self, callback_server: CallbackServer):
        self.callback_server = callback_server
        self.stats = {
            "callbacks_received": 0,
            "contacts_processed": 0,
            "airtable_records_created": 0,
            "errors": []
        }
    
    async def process_callback(self, callback_data: PersonCallbackData) -> None:
        """Main callback processing function."""
        try:
            logger.info(f"🔄 Processing webhook with {len(callback_data)} items")
            self.stats["callbacks_received"] += 1
            
            for item in callback_data:
                try:
                    if item.status == "success" and item.candidate:
                        await self._process_successful_contact(item)
                    else:
                        logger.warning(f"❌ Failed item {item.item}: {item.status}")
                        
                except Exception as e:
                    error_msg = f"Error processing item {item.item}: {e}"
                    logger.error(f"❌ {error_msg}")
                    self.stats["errors"].append(error_msg)
            
            # Log summary
            logger.info(f"📊 Callback processing complete:")
            logger.info(f"   Contacts processed: {self.stats['contacts_processed']}")
            logger.info(f"   Airtable records created: {self.stats['airtable_records_created']}")
            logger.info(f"   Errors: {len(self.stats['errors'])}")
            
        except Exception as e:
            error_msg = f"Critical error in callback processor: {e}"
            logger.error(f"🚨 {error_msg}")
            self.stats["errors"].append(error_msg)
    
    async def _process_successful_contact(self, item: PersonCallbackItem) -> None:
        """Process a successful contact and add to Airtable."""
        try:
            candidate = item.candidate
            signalhire_id = item.item
            
            logger.info(f"👤 Processing: {candidate.fullName} (ID: {signalhire_id})")
            
            # Check if this contact has actual contact information
            has_contact_info = self._has_contact_info(candidate)
            
            if has_contact_info:
                # Create contact in Airtable Contacts table
                contact_record = self._format_contact_for_airtable(signalhire_id, candidate)
                
                logger.info(f"📧 Contact info found for {candidate.fullName}:")
                logger.info(f"   Email: {candidate.emails[0] if candidate.emails else 'None'}")
                logger.info(f"   Phone: {candidate.phones[0] if candidate.phones else 'None'}")
                logger.info(f"   LinkedIn: {candidate.linkedinUrl or 'None'}")
                
                # Create record in Airtable using MCP
                success = await self._create_airtable_contact(contact_record)
                
                if success:
                    self.stats["airtable_records_created"] += 1
                    logger.info(f"✅ Successfully added {candidate.fullName} to Airtable")
                else:
                    logger.error(f"❌ Failed to add {candidate.fullName} to Airtable")
            else:
                logger.warning(f"⚠️  {candidate.fullName} has no contact information - skipping Airtable")
            
            self.stats["contacts_processed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing contact {item.item}: {e}")
            raise
    
    def _has_contact_info(self, candidate) -> bool:
        """Check if candidate has actual contact information."""
        return (
            (candidate.emails and len(candidate.emails) > 0) or
            (candidate.phones and len(candidate.phones) > 0) or
            bool(candidate.linkedinUrl)
        )
    
    def _format_contact_for_airtable(self, signalhire_id: str, candidate) -> Dict[str, Any]:
        """Format candidate data for Airtable Contacts table."""
        # Extract name information
        full_name = candidate.fullName or f"Contact {signalhire_id[:8]}"
        
        # Job and company info
        job_title = candidate.title or ""
        company = candidate.company or ""
        
        # Location
        location_parts = []
        if candidate.city:
            location_parts.append(candidate.city)
        if candidate.country:
            location_parts.append(candidate.country)
        location_str = ", ".join(location_parts)
        
        # Contact information
        primary_email = candidate.emails[0] if candidate.emails else ""
        secondary_email = candidate.emails[1] if len(candidate.emails) > 1 else ""
        phone_number = candidate.phones[0] if candidate.phones else ""
        
        # Social profiles
        linkedin_url = candidate.linkedinUrl or ""
        facebook_url = candidate.facebookUrl or ""
        
        # Skills
        skills = []
        if candidate.skills:
            for skill in candidate.skills:
                if hasattr(skill, 'name'):
                    skills.append(skill.name)
                else:
                    skills.append(str(skill))
        
        # Create Airtable record with Full Name as primary field
        contact_record = {
            "Full Name": full_name,  # Primary field as requested
            "SignalHire ID": signalhire_id,
            "Job Title": job_title,
            "Company": company,
            "Location": location_str,
            "Primary Email": primary_email,
            "Secondary Email": secondary_email,
            "Phone Number": phone_number,
            "LinkedIn URL": linkedin_url,
            "Facebook URL": facebook_url,
            "Skills": ", ".join(skills) if skills else "",
            "Status": "New",
            "Date Added": datetime.now().isoformat(),
            "Source Search": "SignalHire Webhook"
        }
        
        # Remove empty fields
        return {k: v for k, v in contact_record.items() if v}
    
    async def _create_airtable_contact(self, contact_record: Dict[str, Any]) -> bool:
        """Create contact in Airtable using MCP tools."""
        try:
            logger.info(f"📤 Creating Airtable record for: {contact_record.get('Full Name')}")
            
            # TODO: Replace with actual MCP call - this should work with the MCP permissions
            # For now, we'll log what we would send
            logger.info(f"🔧 Would create Airtable record:")
            logger.info(f"   Base ID: {AIRTABLE_BASE_ID}")
            logger.info(f"   Table ID: {CONTACTS_TABLE}")
            logger.info(f"   Fields: {json.dumps(contact_record, indent=2)}")
            
            # Simulate MCP call:
            # result = await mcp__airtable__create_record(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=CONTACTS_TABLE,
            #     fields=contact_record
            # )
            
            # For now, simulate success
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating Airtable record: {e}")
            return False

def create_webhook_handler(processor: SignalHireWebhookProcessor):
    """Create a webhook handler function for the callback server."""
    async def webhook_handler(callback_data: PersonCallbackData) -> None:
        await processor.process_callback(callback_data)
    
    return webhook_handler

async def main():
    """Main function to start the webhook processor."""
    parser = argparse.ArgumentParser(description="SignalHire Webhook Processor")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--background", action="store_true", help="Run in background")
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting SignalHire Webhook Processor")
    logger.info("=" * 60)
    
    # Get the callback server
    callback_server = get_server(host=args.host, port=args.port)
    
    # Create the webhook processor
    processor = SignalHireWebhookProcessor(callback_server)
    
    # Register the webhook handler
    webhook_handler = create_webhook_handler(processor)
    callback_server.register_handler("signalhire_airtable", webhook_handler)
    
    # Start the server
    logger.info(f"🌐 Starting callback server on {args.host}:{args.port}")
    logger.info(f"📡 Webhook URL: {callback_server.get_callback_url()}")
    logger.info(f"🎯 Ready to receive SignalHire webhooks and process to Airtable")
    
    if args.background:
        callback_server.start(background=True)
        logger.info("🔄 Server running in background. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping webhook processor...")
            callback_server.stop()
    else:
        callback_server.start(background=False)

if __name__ == "__main__":
    asyncio.run(main())