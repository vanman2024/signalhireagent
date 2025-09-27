#!/usr/bin/env python3
"""
Airtable Callback Handler for SignalHire Webhooks

PURPOSE: Process SignalHire callback data and push revealed contacts to Airtable
USAGE: Used by callback server to handle revealed contact information
PART OF: SignalHire to Airtable automation workflow
CONNECTS TO: SignalHire callback server, Airtable MCP server
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..models.person_callback import PersonCallbackData, PersonCallbackItem

logger = logging.getLogger(__name__)

# Airtable configuration
AIRTABLE_BASE_ID = "appQoYINM992nBZ50"
SEARCH_SESSIONS_TABLE = "tblqmpcDHfG5pZCWh" 
RAW_PROFILES_TABLE = "tbl593Vc4ExFTYYn0"
CONTACTS_TABLE = "tbl0uFVaAfcNjT2rS"

class AirtableCallbackHandler:
    """Handler that processes SignalHire callbacks and pushes contacts to Airtable."""
    
    def __init__(self):
        self.stats = {
            "callbacks_processed": 0,
            "contacts_created": 0,
            "profiles_updated": 0,
            "errors": []
        }
    
    async def handle_callback(self, callback_data: PersonCallbackData) -> None:
        """Process callback data and push successful contacts to Airtable."""
        try:
            logger.info(f"Processing callback with {len(callback_data)} items")
            self.stats["callbacks_processed"] += 1
            
            for item in callback_data:
                try:
                    if item.status == "success" and item.candidate:
                        # Process successful contact
                        await self._process_successful_contact(item)
                    else:
                        # Log failed items
                        logger.warning(f"Failed item {item.item}: {item.status}")
                        
                except Exception as e:
                    error_msg = f"Error processing item {item.item}: {e}"
                    logger.error(error_msg)
                    self.stats["errors"].append(error_msg)
            
            logger.info(f"Callback processing complete. Stats: {self.stats}")
            
        except Exception as e:
            error_msg = f"Error in callback handler: {e}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
    
    async def _process_successful_contact(self, item: PersonCallbackItem) -> None:
        """Process a successful contact item and add to Airtable."""
        try:
            candidate = item.candidate
            if not candidate:
                return
            
            logger.info(f"Processing successful contact: {candidate.fullName}")
            
            # Update Raw Profile with revelation status
            await self._update_raw_profile(item.item, candidate)
            
            # Create contact in Contacts table if we have contact info
            if self._has_contact_info(candidate):
                await self._create_airtable_contact(item.item, candidate)
            else:
                logger.warning(f"Contact {candidate.fullName} has no contact information")
                
        except Exception as e:
            logger.error(f"Error processing successful contact {item.item}: {e}")
            raise
    
    def _has_contact_info(self, candidate) -> bool:
        """Check if candidate has actual contact information."""
        return (
            (candidate.emails and len(candidate.emails) > 0) or
            (candidate.phones and len(candidate.phones) > 0) or
            bool(candidate.linkedinUrl)
        )
    
    async def _update_raw_profile(self, signalhire_id: str, candidate) -> None:
        """Update Raw Profile with revelation status and data."""
        try:
            # First, find the raw profile record by SignalHire ID
            search_result = await self._search_airtable_records(
                RAW_PROFILES_TABLE,
                f"{{SignalHire ID}} = '{signalhire_id}'"
            )
            
            if not search_result or len(search_result) == 0:
                logger.warning(f"Raw profile not found for SignalHire ID: {signalhire_id}")
                return
            
            profile_record_id = search_result[0]["id"]
            
            # Update the profile with revelation data
            update_fields = {
                "Revelation Status": "Revealed",
                "Revelation Date": datetime.now().isoformat(),
                "Profile Data": json.dumps(candidate.model_dump(), indent=2)
            }
            
            await self._update_airtable_record(
                RAW_PROFILES_TABLE,
                profile_record_id,
                update_fields
            )
            
            self.stats["profiles_updated"] += 1
            logger.info(f"Updated Raw Profile for {candidate.fullName}")
            
        except Exception as e:
            logger.error(f"Error updating raw profile for {signalhire_id}: {e}")
            raise
    
    async def _create_airtable_contact(self, signalhire_id: str, candidate) -> None:
        """Create a new contact record in Airtable."""
        try:
            # Format contact data for Airtable
            contact_record = self._format_contact_for_airtable(signalhire_id, candidate)
            
            # Create the contact record
            result = await self._create_airtable_record(
                CONTACTS_TABLE,
                contact_record
            )
            
            if result:
                self.stats["contacts_created"] += 1
                logger.info(f"Created Airtable contact: {contact_record.get('Full Name')}")
            else:
                logger.error(f"Failed to create Airtable contact for {signalhire_id}")
                
        except Exception as e:
            logger.error(f"Error creating Airtable contact for {signalhire_id}: {e}")
            raise
    
    def _format_contact_for_airtable(self, signalhire_id: str, candidate) -> Dict[str, Any]:
        """Format candidate data for Airtable Contacts table."""
        # Extract name information
        full_name = candidate.fullName or f"Contact {signalhire_id[:8]}"
        first_name = candidate.firstName or ""
        last_name = candidate.lastName or ""
        
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
        
        # Create Airtable record
        contact_record = {
            "Full Name": full_name,  # Primary field
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
    
    async def _search_airtable_records(self, table_id: str, formula: str) -> List[Dict[str, Any]]:
        """Search Airtable records using a formula."""
        try:
            # This would use the MCP Airtable search functionality
            # For now, we'll simulate this
            logger.info(f"Searching Airtable table {table_id} with formula: {formula}")
            
            # TODO: Implement actual MCP airtable search call
            # result = await mcp__airtable__list_records(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=table_id,
            #     filterByFormula=formula
            # )
            # return result.get("records", [])
            
            # For now, return empty to avoid errors
            return []
            
        except Exception as e:
            logger.error(f"Error searching Airtable records: {e}")
            return []
    
    async def _update_airtable_record(self, table_id: str, record_id: str, fields: Dict[str, Any]) -> bool:
        """Update an Airtable record."""
        try:
            logger.info(f"Updating Airtable record {record_id} in table {table_id}")
            
            # TODO: Implement actual MCP airtable update call
            # result = await mcp__airtable__update_records(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=table_id,
            #     records=[{
            #         "id": record_id,
            #         "fields": fields
            #     }]
            # )
            # return result is not None
            
            # For now, simulate success
            return True
            
        except Exception as e:
            logger.error(f"Error updating Airtable record: {e}")
            return False
    
    async def _create_airtable_record(self, table_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new Airtable record."""
        try:
            logger.info(f"Creating Airtable record in table {table_id}")
            logger.info(f"Record data: {json.dumps(fields, indent=2)}")
            
            # TODO: Implement actual MCP airtable create call
            # result = await mcp__airtable__create_record(
            #     baseId=AIRTABLE_BASE_ID,
            #     tableId=table_id,
            #     fields=fields
            # )
            # return result
            
            # For now, simulate success
            return {"id": f"simulated_record_{datetime.now().timestamp()}"}
            
        except Exception as e:
            logger.error(f"Error creating Airtable record: {e}")
            return None

# Handler instance for registration with callback server
airtable_handler = AirtableCallbackHandler()

def register_airtable_handler(callback_server):
    """Register the Airtable handler with a callback server."""
    callback_server.register_handler("airtable", airtable_handler.handle_callback)
    logger.info("Registered Airtable callback handler")

def get_handler_stats() -> Dict[str, Any]:
    """Get statistics from the Airtable handler."""
    return airtable_handler.stats.copy()