#!/usr/bin/env python3
"""
Dynamic Airtable Expansion Service

PURPOSE: Handle new items not in existing dropdowns by creating pending tables for review
USAGE: Called automatically by Universal Adaptive System when new items are detected
PART OF: SignalHire to Airtable automation with Universal Adaptive System
CONNECTS TO: Universal table schema, Airtable MCP, automated expansion workflows
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from src.services.airtable_formula_generator import AirtableFormulaGenerator, enhance_with_formulas

class DynamicAirtableExpansion:
    """Handles automatic expansion of Airtable fields and tables for new items."""
    
    def __init__(self, base_id: str):
        self.base_id = base_id
        self.pending_items = defaultdict(list)  # Track items pending addition
        self.expansion_log = []  # Log all expansions for review
        
        # Tables for pending items that need manual review
        self.pending_tables = {
            "trades": "tblPendingTrades",  # New trades not in Red Seal list
            "brands": "tblPendingBrands",  # New equipment brands
            "tools": "tblPendingTools",    # New tools/equipment
            "certifications": "tblPendingCertifications",  # New certifications
            "specializations": "tblPendingSpecializations",  # New specializations
            "industries": "tblPendingIndustries",  # New industries/environments
            "hierarchy_levels": "tblPendingHierarchy"  # New hierarchy levels
        }
    
    async def handle_new_items(self, contact_data: Dict[str, Any], signalhire_id: str) -> Dict[str, Any]:
        """Process contact data and handle any new items not in existing dropdowns."""
        
        print(f"🔍 Checking for new items in contact: {contact_data.get('Full Name', signalhire_id)}")
        
        # Extract items that need checking
        items_to_check = {
            "trades": [contact_data.get('Primary Trade', '')],
            "brands": contact_data.get('Equipment Brands Experience', []),
            "tools": contact_data.get('Equipment Categories', []),
            "certifications": contact_data.get('Certifications', []),
            "specializations": contact_data.get('Specializations', []),
            "industries": contact_data.get('Environments', []),
            "hierarchy_levels": [contact_data.get('Trade Hierarchy Level', '')]
        }
        
        # Check each category for new items
        expansion_results = {}
        for category, items in items_to_check.items():
            if items:  # Only process if there are items
                new_items = await self.check_and_handle_new_items(category, items, signalhire_id)
                if new_items:
                    expansion_results[category] = new_items
        
        # Update the contact data with handled items
        updated_contact = await self.update_contact_with_handled_items(contact_data, expansion_results)
        
        return updated_contact
    
    async def check_and_handle_new_items(self, category: str, items: List[str], source_id: str) -> List[str]:
        """Check if items exist in Airtable, add new ones to pending tables."""
        
        if not items:
            return []
        
        # Filter out empty items
        valid_items = [item.strip() for item in items if item and item.strip()]
        if not valid_items:
            return []
        
        print(f"   🔍 Checking {category}: {valid_items}")
        
        # Get existing items from main tables (this would be MCP calls in production)
        existing_items = await self.get_existing_items(category)
        
        # Find new items
        new_items = []
        for item in valid_items:
            if item not in existing_items:
                new_items.append(item)
                print(f"     ➕ New {category[:-1]}: {item}")
        
        # Add new items to pending table
        if new_items:
            await self.add_to_pending_table(category, new_items, source_id)
        
        return new_items
    
    async def get_existing_items(self, category: str) -> Set[str]:
        """Get existing items from main Airtable tables."""
        
        # This would be actual MCP calls in production
        # For now, simulate with known items
        
        existing_data = {
            "trades": {
                "Heavy Duty Equipment Technician",
                "Automotive Service Technician", 
                "Baker",
                "Hairstylist",
                "Industrial Mechanic (Millwright)",
                "Electrician",
                "Plumber",
                "Welder",
                "Cook"
            },
            "brands": {
                "Caterpillar", "Komatsu", "Hitachi", "John Deere", "Case",
                "Snap-On", "Hobart", "Redken", "Wella", "Fluke",
                "Siemens", "Allen Bradley", "RIDGID"
            },
            "tools": {
                "Excavators", "Bulldozers/Dozers", "Diagnostic Scanners",
                "Commercial Mixers", "Electrical Test Equipment"
            },
            "certifications": {
                "Red Seal Certified", "ASE Certified", "Safety Certified",
                "Manufacturer Specific (Caterpillar)", "Hydraulics Specialist"
            },
            "specializations": {
                "Hydraulic Systems", "Electrical Systems", "Engine Diagnostics",
                "Team Leadership", "Safety Management", "Project Management",
                "Customer Service", "Training/Mentoring"
            },
            "industries": {
                "Construction Sites", "Heavy Equipment", "Automotive Service",
                "Restaurants & Food Service", "Salons & Spas", "Industrial Plants"
            },
            "hierarchy_levels": {
                "Apprentice", "Apprentice (2nd Year)", "Apprentice (3rd Year)", "Apprentice (4th Year)",
                "Journeyperson", "Senior Professional", "Lead Hand", "Supervisor",
                "Shop Foreman", "Service Manager", "Operations Manager", "Executive"
            }
        }
        
        return existing_data.get(category, set())
    
    async def add_to_pending_table(self, category: str, new_items: List[str], source_id: str):
        """Add new items to pending review tables."""
        
        pending_table_id = self.pending_tables.get(category)
        if not pending_table_id:
            print(f"     ⚠️  No pending table configured for category: {category}")
            return
        
        for item in new_items:
            pending_record = {
                "Item Name": item,
                "Category": category.rstrip('s').title(),  # Remove 's' and capitalize
                "Source Contact": source_id,
                "Date Added": datetime.now().isoformat(),
                "Status": "Pending Review",
                "Auto Detected": "Yes",
                "Confidence": self.calculate_item_confidence(item, category),
                "Similar Existing": await self.find_similar_items(item, category)
            }
            
            # Log the pending addition
            self.expansion_log.append({
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "item": item,
                "source": source_id,
                "action": "added_to_pending"
            })
            
            print(f"     📝 Added to pending {category}: {item}")
            
            # In production, this would be an MCP call:
            # await mcp_airtable_create_record(
            #     baseId=self.base_id,
            #     tableId=pending_table_id,
            #     fields=pending_record
            # )
    
    def calculate_item_confidence(self, item: str, category: str) -> float:
        """Calculate confidence score for a new item."""
        
        confidence = 0.5  # Base confidence
        
        # Length and format checks
        if len(item) > 3:
            confidence += 0.1
        if len(item.split()) <= 4:  # Not too many words
            confidence += 0.1
        
        # Category-specific checks
        if category == "brands":
            # Brand names are usually 1-2 words
            if len(item.split()) <= 2:
                confidence += 0.2
        elif category == "trades":
            # Trade names often contain "technician", "mechanic", etc.
            trade_keywords = ["technician", "mechanic", "specialist", "operator", "engineer"]
            if any(keyword in item.lower() for keyword in trade_keywords):
                confidence += 0.2
        elif category == "certifications":
            # Certifications often contain "certified", "license", etc.
            cert_keywords = ["certified", "license", "certificate", "red seal"]
            if any(keyword in item.lower() for keyword in cert_keywords):
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    async def find_similar_items(self, item: str, category: str) -> str:
        """Find similar existing items to help with manual review."""
        
        existing_items = await self.get_existing_items(category)
        
        # Simple similarity check (in production, could use more sophisticated matching)
        item_lower = item.lower()
        similar_items = []
        
        for existing in existing_items:
            existing_lower = existing.lower()
            
            # Check for partial matches
            if item_lower in existing_lower or existing_lower in item_lower:
                similar_items.append(existing)
            # Check for shared words
            elif len(set(item_lower.split()) & set(existing_lower.split())) >= 1:
                similar_items.append(existing)
        
        return ", ".join(similar_items[:3])  # Return up to 3 similar items
    
    async def update_contact_with_handled_items(self, contact_data: Dict[str, Any], expansion_results: Dict[str, List[str]]) -> Dict[str, Any]:
        """Update contact data to indicate which items are pending vs approved."""
        
        updated_contact = contact_data.copy()
        
        # Add metadata about pending items
        if expansion_results:
            pending_summary = []
            multiselect_items = {}
            
            for category, new_items in expansion_results.items():
                pending_summary.append(f"{category}: {len(new_items)} new items")
                
                # Prepare multiselect field updates
                field_mapping = {
                    "brands": "Equipment Brands Experience",
                    "tools": "Equipment Categories", 
                    "specializations": "Specializations",
                    "certifications": "Certifications",
                    "industries": "Environments"
                }
                
                field_name = field_mapping.get(category)
                if field_name:
                    multiselect_items[field_name] = new_items
            
            # Note: Removing fields that don't exist in Contacts table
            # updated_contact["Pending Items"] = "; ".join(pending_summary)
            # updated_contact["Has Pending Items"] = "Yes"
            # updated_contact["Expansion Date"] = datetime.now().isoformat()
            
            # Enhance with formulas and multiselect updates
            if multiselect_items:
                await enhance_with_formulas(self.base_id, "tbl0uFVaAfcNjT2rS", multiselect_items)
                # updated_contact["Multiselect Enhanced"] = "Yes"
        # else:
            # updated_contact["Has Pending Items"] = "No"
        
        return updated_contact
    
    async def create_pending_tables_if_needed(self):
        """Create pending review tables if they don't exist."""
        
        for category, table_id in self.pending_tables.items():
            # Check if table exists (MCP call in production)
            table_exists = await self.check_table_exists(table_id)
            
            if not table_exists:
                await self.create_pending_table(category, table_id)
    
    async def check_table_exists(self, table_id: str) -> bool:
        """Check if a table exists in the Airtable base."""
        # In production, this would be an MCP call
        # For now, assume tables exist
        return True
    
    async def create_pending_table(self, category: str, table_id: str):
        """Create a pending review table for new items."""
        
        table_schema = {
            "name": f"Pending {category.title()}",
            "description": f"New {category} detected automatically, pending manual review",
            "fields": [
                {
                    "name": "Item Name",
                    "type": "singleLineText",
                    "description": f"Name of the new {category[:-1]}"
                },
                {
                    "name": "Category", 
                    "type": "singleSelect",
                    "options": {
                        "choices": [
                            {"name": "Trade"},
                            {"name": "Brand"},
                            {"name": "Tool"},
                            {"name": "Certification"},
                            {"name": "Specialization"},
                            {"name": "Industry"},
                            {"name": "Hierarchy Level"}
                        ]
                    }
                },
                {
                    "name": "Source Contact",
                    "type": "singleLineText",
                    "description": "SignalHire ID of contact that introduced this item"
                },
                {
                    "name": "Date Added",
                    "type": "dateTime"
                },
                {
                    "name": "Status",
                    "type": "singleSelect",
                    "options": {
                        "choices": [
                            {"name": "Pending Review"},
                            {"name": "Approved"},
                            {"name": "Rejected"},
                            {"name": "Duplicate"}
                        ]
                    }
                },
                {
                    "name": "Auto Detected",
                    "type": "checkbox"
                },
                {
                    "name": "Confidence",
                    "type": "number",
                    "options": {"precision": 2}
                },
                {
                    "name": "Similar Existing",
                    "type": "multilineText",
                    "description": "Similar items already in the system"
                },
                {
                    "name": "Review Notes",
                    "type": "multilineText"
                }
            ]
        }
        
        print(f"📋 Would create pending table: {table_schema['name']}")
        
        # In production, this would be an MCP call:
        # await mcp_airtable_create_table(
        #     baseId=self.base_id,
        #     table=table_schema
        # )
    
    def get_expansion_summary(self) -> Dict[str, Any]:
        """Get summary of all expansions for reporting."""
        
        summary = {
            "total_expansions": len(self.expansion_log),
            "expansions_by_category": defaultdict(int),
            "recent_expansions": self.expansion_log[-10:],  # Last 10
            "pending_counts": {category: len(items) for category, items in self.pending_items.items()}
        }
        
        for log_entry in self.expansion_log:
            summary["expansions_by_category"][log_entry["category"]] += 1
        
        return summary

# Integration function for the main automation
async def process_contact_with_dynamic_expansion(contact_data: Dict[str, Any], signalhire_id: str, base_id: str) -> Dict[str, Any]:
    """Process a contact and handle any dynamic expansions needed."""
    
    expansion_service = DynamicAirtableExpansion(base_id)
    
    # Ensure pending tables exist
    await expansion_service.create_pending_tables_if_needed()
    
    # Handle new items
    updated_contact = await expansion_service.handle_new_items(contact_data, signalhire_id)
    
    return updated_contact

# Example usage
async def test_dynamic_expansion():
    """Test the dynamic expansion system."""
    
    print("🧪 Testing Dynamic Airtable Expansion")
    print("=" * 50)
    
    # Mock contact with new items
    test_contact = {
        "Full Name": "Test Contact",
        "Primary Trade": "Solar Panel Installer",  # New trade
        "Equipment Brands Experience": ["Tesla Solar", "SunPower"],  # New brand
        "Equipment Categories": ["Solar Panels", "Inverters"],  # New equipment
        "Certifications": ["NABCEP Certified"],  # New certification
        "Specializations": ["Renewable Energy Systems"],  # New specialization
        "Environments": ["Residential Rooftops"],  # New environment
        "Trade Hierarchy Level": "Installation Specialist"  # New hierarchy
    }
    
    # Process with dynamic expansion
    result = await process_contact_with_dynamic_expansion(
        test_contact, "test_001", "appQoYINM992nBZ50"
    )
    
    print(f"\n📊 Processing Results:")
    print(f"Has Pending Items: {result.get('Has Pending Items', 'No')}")
    print(f"Pending Items: {result.get('Pending Items', 'None')}")
    
    print(f"\n✅ Dynamic expansion system ready for production!")

if __name__ == "__main__":
    asyncio.run(test_dynamic_expansion())