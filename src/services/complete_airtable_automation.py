#!/usr/bin/env python3
"""
Complete SignalHire to Airtable Automation

PURPOSE: End-to-end automation that starts webhook server, reveals contacts, and processes to Airtable
USAGE: python3 complete_airtable_automation.py [--max-reveals 5] [--webhook-port 8000]
PART OF: SignalHire to Airtable automation workflow
CONNECTS TO: SignalHire API, callback server, Airtable MCP server
"""

import asyncio
import json
import logging
import argparse
import signal
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..services.signalhire_client import SignalHireClient
from ..lib.callback_server import get_server, CallbackServer
from ..models.person_callback import PersonCallbackData, PersonCallbackItem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
CONTACTS_TABLE = "tbl0uFVaAfcNjT2rS"
CACHE_FILE = "/home/vanman2025/.signalhire-agent/cache/revealed_contacts.json"

class CompleteAirtableAutomation:
    """Complete automation that handles the entire workflow from revelation to Airtable."""
    
    def __init__(self, webhook_port: int = 8000):
        self.webhook_port = webhook_port
        self.callback_server: Optional[CallbackServer] = None
        self.signalhire_client: Optional[SignalHireClient] = None
        self.webhook_url = f"http://localhost:{webhook_port}/signalhire/callback"
        self.stats = {
            "contacts_revealed": 0,
            "webhook_callbacks_processed": 0,
            "airtable_records_created": 0,
            "errors": []
        }
        self.is_running = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_services()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_services()
    
    async def start_services(self):
        """Start all required services."""
        logger.info("🚀 Starting Complete Airtable Automation")
        logger.info("=" * 60)
        
        # Start callback server
        self.callback_server = get_server(host="0.0.0.0", port=self.webhook_port)
        self.callback_server.register_handler("airtable_processor", self._process_webhook)
        
        if not self.callback_server.is_running:
            self.callback_server.start(background=True)
            # Give the server a moment to start
            await asyncio.sleep(2)
        
        # Initialize SignalHire client with callback URL
        self.signalhire_client = SignalHireClient(callback_url=self.webhook_url)
        
        logger.info(f"🌐 Webhook server running at: {self.webhook_url}")
        logger.info(f"🔗 SignalHire client configured with callback URL")
        
        self.is_running = True
    
    async def stop_services(self):
        """Stop all services."""
        logger.info("🛑 Stopping services...")
        
        if self.signalhire_client:
            await self.signalhire_client.close()
        
        if self.callback_server:
            self.callback_server.stop()
        
        self.is_running = False
        logger.info("✅ Services stopped")
    
    async def _process_webhook(self, callback_data: PersonCallbackData) -> None:
        """Process incoming webhook data from SignalHire."""
        try:
            logger.info(f"📨 Received webhook with {len(callback_data)} items")
            self.stats["webhook_callbacks_processed"] += 1
            
            for item in callback_data:
                if item.status == "success" and item.candidate:
                    await self._process_successful_contact(item)
                else:
                    logger.warning(f"❌ Failed revelation: {item.item} - {item.status}")
            
        except Exception as e:
            error_msg = f"Error processing webhook: {e}"
            logger.error(f"❌ {error_msg}")
            self.stats["errors"].append(error_msg)
    
    async def _process_successful_contact(self, item: PersonCallbackItem) -> None:
        """Process a successfully revealed contact."""
        try:
            candidate = item.candidate
            signalhire_id = item.item
            
            logger.info(f"👤 Processing revealed contact: {candidate.fullName}")
            
            # Check if contact has actual contact information
            if not self._has_contact_info(candidate):
                logger.warning(f"⚠️  {candidate.fullName} has no contact information - skipping")
                return
            
            # Format for Airtable
            contact_record = self._format_contact_for_airtable(signalhire_id, candidate)
            
            # Log contact info found
            logger.info(f"📧 Contact details for {candidate.fullName}:")
            if candidate.emails:
                logger.info(f"   📧 Email: {candidate.emails[0]}")
            if candidate.phones:
                logger.info(f"   📞 Phone: {candidate.phones[0]}")
            if candidate.linkedinUrl:
                logger.info(f"   🔗 LinkedIn: {candidate.linkedinUrl}")
            
            # Create in Airtable using MCP tools
            success = await self._create_airtable_contact(contact_record)
            
            if success:
                self.stats["airtable_records_created"] += 1
                logger.info(f"✅ Successfully added {candidate.fullName} to Airtable!")
            else:
                logger.error(f"❌ Failed to add {candidate.fullName} to Airtable")
                
        except Exception as e:
            error_msg = f"Error processing contact {item.item}: {e}"
            logger.error(f"❌ {error_msg}")
            self.stats["errors"].append(error_msg)
    
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
        
        # Create record with Full Name as primary field
        return {
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
            "Source Search": "SignalHire Automation"
        }
    
    async def _create_airtable_contact(self, contact_record: Dict[str, Any]) -> bool:
        """Create contact in Airtable using MCP tools."""
        try:
            logger.info(f"📤 Creating Airtable record for: {contact_record.get('Full Name')}")
            
            # Remove empty fields before sending to Airtable
            fields = {k: v for k, v in contact_record.items() if v}
            
            logger.info(f"📧 Contact: {fields.get('Primary Email', 'No email')}")
            logger.info(f"📞 Phone: {fields.get('Phone Number', 'No phone')}")
            logger.info(f"🔗 LinkedIn: {fields.get('LinkedIn URL', 'No LinkedIn')}")
            
            # Call the actual MCP airtable create function
            # This should work with the wildcard permissions we set up
            result = await self._mcp_create_record(AIRTABLE_BASE_ID, CONTACTS_TABLE, fields)
            
            if result:
                logger.info(f"✅ Successfully created Airtable record: {result.get('id', 'Unknown ID')}")
                return True
            else:
                logger.error(f"❌ Failed to create Airtable record")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error creating Airtable record: {e}")
            return False
    
    async def _mcp_create_record(self, base_id: str, table_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call MCP Airtable create record function."""
        try:
            logger.info(f"📋 Creating Airtable record via MCP:")
            logger.info(f"   Base: {base_id}")
            logger.info(f"   Table: {table_id}")
            logger.info(f"   Contact: {fields.get('Full Name', 'Unknown')}")
            
            # Note: This function is designed to work when called from Claude Code environment
            # where MCP tools are available. When run as a standalone script, it will use
            # the subprocess approach to call through Claude Code
            
            # Try to determine if we're running in Claude Code environment
            import os
            import subprocess
            
            # Create a temporary file with the MCP call
            import tempfile
            
            mcp_call_script = f'''
import asyncio
from mcp__airtable import create_record

async def main():
    result = await create_record(
        baseId="{base_id}",
        tableId="{table_id}",
        fields={json.dumps(fields)}
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
'''
            
            # Write to temp file and execute
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(mcp_call_script)
                temp_script = f.name
            
            try:
                # Execute the MCP call script
                result = subprocess.run([
                    'python3', temp_script
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # Parse the result
                    import ast
                    mcp_result = ast.literal_eval(result.stdout.strip())
                    logger.info(f"✅ Successfully created Airtable record: {mcp_result.get('id', 'Unknown ID')}")
                    return mcp_result
                else:
                    logger.error(f"❌ MCP call failed: {result.stderr}")
                    return None
                    
            finally:
                # Clean up temp file
                os.unlink(temp_script)
            
        except Exception as e:
            logger.error(f"❌ MCP Airtable call failed: {e}")
            # Fallback: log what we would create
            logger.info(f"📋 Would create in Airtable: {fields.get('Full Name')} - {fields.get('Primary Email', 'No email')}")
            return None
    
    def load_contacts_cache(self) -> Dict[str, Any]:
        """Load contacts from cache file."""
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ Cache file not found: {CACHE_FILE}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing cache file: {e}")
            return {}
    
    def get_unrevealed_contacts(self, contacts: Dict[str, Any]) -> List[str]:
        """Get contact IDs that haven't been revealed yet."""
        unrevealed = []
        for contact_id, contact_data in contacts.items():
            if not contact_data.get('contacts') or len(contact_data['contacts']) == 0:
                unrevealed.append(contact_id)
        return unrevealed
    
    async def reveal_contacts(self, contact_ids: List[str], max_reveals: int = 5) -> Dict[str, Any]:
        """Reveal contact information for given contact IDs."""
        if not self.signalhire_client:
            raise RuntimeError("SignalHire client not initialized")
        
        logger.info(f"🔍 Revealing {min(len(contact_ids), max_reveals)} contacts...")
        
        results = {
            "requested": 0,
            "successful": 0,
            "failed": 0,
            "request_ids": []
        }
        
        # Limit reveals to avoid rate limits
        contacts_to_reveal = contact_ids[:max_reveals]
        
        for i, contact_id in enumerate(contacts_to_reveal, 1):
            try:
                logger.info(f"📞 Revealing contact {i}/{len(contacts_to_reveal)}: {contact_id}")
                
                response = await self.signalhire_client.reveal_contact(contact_id)
                results["requested"] += 1
                
                if response.success:
                    request_id = response.data.get('requestId') if response.data else None
                    logger.info(f"✅ Success - Request ID: {request_id}")
                    results["successful"] += 1
                    if request_id:
                        results["request_ids"].append(request_id)
                else:
                    logger.error(f"❌ Failed to reveal {contact_id}: {response.error}")
                    results["failed"] += 1
                
                # Small delay to respect rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Exception revealing {contact_id}: {e}")
                results["failed"] += 1
        
        self.stats["contacts_revealed"] += results["successful"]
        return results
    
    async def run_automation(self, max_reveals: int = 5):
        """Run the complete automation workflow."""
        logger.info("🎯 Starting Complete Automation Workflow")
        
        # Load contacts from cache
        logger.info("📂 Loading contacts from cache...")
        contacts = self.load_contacts_cache()
        
        if not contacts:
            logger.error("❌ No contacts found in cache")
            return
        
        logger.info(f"📊 Found {len(contacts)} total contacts in cache")
        
        # Find unrevealed contacts
        unrevealed_contacts = self.get_unrevealed_contacts(contacts)
        logger.info(f"🔍 Found {len(unrevealed_contacts)} unrevealed contacts")
        
        if unrevealed_contacts:
            # Reveal contacts
            logger.info(f"📞 Revealing up to {max_reveals} contacts...")
            reveal_results = await self.reveal_contacts(unrevealed_contacts, max_reveals)
            
            logger.info(f"📊 Revelation Results:")
            logger.info(f"   Requested: {reveal_results['requested']}")
            logger.info(f"   Successful: {reveal_results['successful']}")
            logger.info(f"   Failed: {reveal_results['failed']}")
            logger.info(f"   Request IDs: {reveal_results['request_ids']}")
            
            if reveal_results['successful'] > 0:
                logger.info(f"⏳ Waiting for webhook callbacks...")
                logger.info(f"   Webhook URL: {self.webhook_url}")
                logger.info(f"   Callbacks will be processed automatically")
            else:
                logger.warning("❌ No contacts were successfully revealed")
        else:
            logger.info("ℹ️  No unrevealed contacts found")
        
        # Print current stats
        logger.info(f"📊 Current Automation Stats:")
        logger.info(f"   Contacts revealed: {self.stats['contacts_revealed']}")
        logger.info(f"   Webhook callbacks: {self.stats['webhook_callbacks_processed']}")
        logger.info(f"   Airtable records: {self.stats['airtable_records_created']}")
        logger.info(f"   Errors: {len(self.stats['errors'])}")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Complete SignalHire to Airtable Automation")
    parser.add_argument("--max-reveals", type=int, default=5, 
                       help="Maximum number of contacts to reveal")
    parser.add_argument("--webhook-port", type=int, default=8000,
                       help="Port for webhook server")
    parser.add_argument("--keep-running", action="store_true",
                       help="Keep webhook server running after automation")
    
    args = parser.parse_args()
    
    automation = CompleteAirtableAutomation(webhook_port=args.webhook_port)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("🛑 Received shutdown signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        async with automation:
            # Run the automation workflow
            await automation.run_automation(max_reveals=args.max_reveals)
            
            if args.keep_running:
                logger.info("🔄 Keeping webhook server running. Press Ctrl+C to stop.")
                logger.info(f"🌐 Webhook URL: {automation.webhook_url}")
                
                # Keep running and processing webhooks
                while automation.is_running:
                    await asyncio.sleep(5)
                    
                    # Print stats every 30 seconds
                    if hasattr(automation, '_last_stats_time'):
                        if datetime.now().timestamp() - automation._last_stats_time > 30:
                            logger.info(f"📊 Stats: {automation.stats}")
                            automation._last_stats_time = datetime.now().timestamp()
                    else:
                        automation._last_stats_time = datetime.now().timestamp()
            else:
                logger.info("✅ Automation complete. Webhook server will stop.")
                
    except KeyboardInterrupt:
        logger.info("🛑 Automation stopped by user")
    except Exception as e:
        logger.error(f"❌ Automation error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())