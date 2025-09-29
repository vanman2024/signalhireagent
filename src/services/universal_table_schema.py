#!/usr/bin/env python3
"""
Universal Table Schema - Auto-Expanding Database Structure

PURPOSE: Define universal table structure that grows automatically without duplication
USAGE: Schema management for the adaptive categorization system
PART OF: Universal Red Seal system with infinite scalability
CONNECTS TO: Airtable MCP, Universal Categorization Engine, Pattern Learning
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UniversalTableSchema:
    """Manages universal table structure that adapts and expands automatically."""
    
    def __init__(self):
        self.base_id = "appQoYINM992nBZ50"  # SignalHire Contacts Base
        self.universal_schema = self._define_universal_schema()
        self.expansion_log = []
        
    def _define_universal_schema(self) -> Dict[str, Any]:
        """Define the core universal table structure."""
        
        return {
            # Core contact table - never changes, only links
            "contacts": {
                "table_name": "Contacts",
                "table_id": "tbl0uFVaAfcNjT2rS",
                "description": "Universal contact records with smart linking",
                "core_fields": [
                    {"name": "Full Name", "type": "singleLineText"},
                    {"name": "SignalHire ID", "type": "singleLineText"},
                    {"name": "Job Title", "type": "singleLineText"},
                    {"name": "Company", "type": "singleLineText"},
                    {"name": "Location", "type": "singleLineText"},
                    {"name": "Primary Email", "type": "email"},
                    {"name": "Phone Number", "type": "phoneNumber"},
                    {"name": "LinkedIn URL", "type": "url"},
                    {"name": "Status", "type": "singleSelect"},
                    {"name": "Date Added", "type": "dateTime"},
                    {"name": "Source Search", "type": "singleLineText"},
                    {"name": "Auto Categorized", "type": "checkbox"},
                    {"name": "Confidence Score", "type": "number"}
                ],
                "linking_fields": [
                    {"name": "Primary Trade", "links_to": "trades"},
                    {"name": "Trade Categories", "links_to": "trade_categories"},
                    {"name": "Items Used", "links_to": "items"},
                    {"name": "Brands Used", "links_to": "brands"},
                    {"name": "Work Environments", "links_to": "environments"},
                    {"name": "Skills & Certifications", "links_to": "skills"},
                    {"name": "Company Record", "links_to": "companies"}
                ]
            },
            
            # Universal Items table - tools, equipment, software, materials
            "items": {
                "table_name": "Items",
                "table_id": "tblcq5EvwlhBjnNpS",  # Reuse existing Tools & Equipment table
                "description": "Universal items: tools, equipment, software, materials, supplies",
                "core_fields": [
                    {"name": "Item Name", "type": "singleLineText"},
                    {"name": "Item Type", "type": "singleSelect", "options": [
                        "Hand Tool", "Power Tool", "Heavy Equipment", "Software", 
                        "Material", "Supply", "Service", "Digital Asset"
                    ]},
                    {"name": "Physical Category", "type": "singleSelect", "options": [
                        "Portable", "Bench/Counter", "Room Equipment", 
                        "Vehicle/Mobile", "Industrial/Large", "Digital/Virtual"
                    ]},
                    {"name": "Complexity Level", "type": "singleSelect", "options": [
                        "Basic", "Intermediate", "Advanced", "Expert"
                    ]},
                    {"name": "Cost Range", "type": "singleSelect", "options": [
                        "Under $100", "$100-$1K", "$1K-$10K", "$10K-$100K", "Over $100K"
                    ]},
                    {"name": "Learning Priority", "type": "singleSelect", "options": [
                        "Essential", "Important", "Optional", "Advanced"
                    ]}
                ],
                "linking_fields": [
                    {"name": "Trade Categories", "links_to": "trade_categories"},
                    {"name": "Primary Brands", "links_to": "brands"},
                    {"name": "Used By Contacts", "links_to": "contacts"},
                    {"name": "Common Environments", "links_to": "environments"}
                ],
                "auto_expand": True
            },
            
            # Universal Brands table - all manufacturers across all industries
            "brands": {
                "table_name": "Brands",
                "table_id": "tblQ45u548RjR7qwT",  # Reuse existing Brands & Manufacturers table
                "description": "Universal brands and manufacturers across all industries",
                "core_fields": [
                    {"name": "Brand Name", "type": "singleLineText"},
                    {"name": "Industry Focus", "type": "multipleSelects", "options": [
                        "Heavy Equipment", "Automotive", "Food Service", "Beauty", 
                        "Industrial", "Electrical", "Software", "Construction",
                        "Healthcare", "Education", "Agriculture", "Marine"
                    ]},
                    {"name": "Market Tier", "type": "singleSelect", "options": [
                        "Global Leader", "Major Player", "Regional", "Specialist", "Emerging"
                    ]},
                    {"name": "Founded Year", "type": "number"},
                    {"name": "Headquarters", "type": "singleLineText"},
                    {"name": "Website", "type": "url"},
                    {"name": "Annual Revenue", "type": "currency"},
                    {"name": "Employee Count", "type": "singleSelect", "options": [
                        "1-50", "51-500", "501-5K", "5K-50K", "50K+"
                    ]}
                ],
                "linking_fields": [
                    {"name": "Items Manufactured", "links_to": "items"},
                    {"name": "Trade Categories Served", "links_to": "trade_categories"},
                    {"name": "Used By Contacts", "links_to": "contacts"},
                    {"name": "Active In Environments", "links_to": "environments"}
                ],
                "auto_expand": True
            },
            
            # Universal Environments table - all work environments
            "environments": {
                "table_name": "Environments",
                "table_id": "tbl57DrLRhpqUo1Op",  # Reuse existing Industries table
                "description": "Universal work environments and industry contexts",
                "core_fields": [
                    {"name": "Environment Name", "type": "singleLineText"},
                    {"name": "Environment Type", "type": "singleSelect", "options": [
                        "Indoor Facility", "Outdoor Site", "Mobile/Vehicle", 
                        "Remote/Digital", "Hybrid", "Specialized"
                    ]},
                    {"name": "Safety Level", "type": "singleSelect", "options": [
                        "Low Risk", "Moderate Risk", "High Risk", "Extreme Risk"
                    ]},
                    {"name": "Employment Scale", "type": "singleSelect", "options": [
                        "Major Employer (1000+)", "Significant (100-999)", 
                        "Moderate (10-99)", "Small (1-9)", "Specialized"
                    ]},
                    {"name": "Growth Trend", "type": "singleSelect", "options": [
                        "Rapidly Growing", "Growing", "Stable", "Declining", "Transforming"
                    ]},
                    {"name": "Course Market Priority", "type": "singleSelect", "options": [
                        "High Priority", "Medium Priority", "Low Priority", "Future Opportunity"
                    ]}
                ],
                "linking_fields": [
                    {"name": "Common Trade Categories", "links_to": "trade_categories"},
                    {"name": "Typical Items Used", "links_to": "items"},
                    {"name": "Major Brands Present", "links_to": "brands"},
                    {"name": "Workers In Environment", "links_to": "contacts"}
                ],
                "auto_expand": True
            },
            
            # Universal Skills table - all skills and certifications
            "skills": {
                "table_name": "Skills & Certifications",
                "table_id": None,  # New table
                "description": "Universal skills, certifications, and competencies",
                "core_fields": [
                    {"name": "Skill Name", "type": "singleLineText"},
                    {"name": "Skill Type", "type": "singleSelect", "options": [
                        "Technical Skill", "Soft Skill", "Certification", 
                        "License", "Safety Training", "Software Proficiency"
                    ]},
                    {"name": "Difficulty Level", "type": "singleSelect", "options": [
                        "Beginner", "Intermediate", "Advanced", "Expert"
                    ]},
                    {"name": "Time to Learn", "type": "singleSelect", "options": [
                        "Days", "Weeks", "Months", "Years"
                    ]},
                    {"name": "Certification Body", "type": "singleLineText"},
                    {"name": "Renewal Required", "type": "checkbox"},
                    {"name": "Course Relevance", "type": "singleSelect", "options": [
                        "Core Curriculum", "Supplementary", "Advanced Module", "Optional"
                    ]}
                ],
                "linking_fields": [
                    {"name": "Relevant Trade Categories", "links_to": "trade_categories"},
                    {"name": "Associated Items", "links_to": "items"},
                    {"name": "Common In Environments", "links_to": "environments"},
                    {"name": "Contacts With Skill", "links_to": "contacts"}
                ],
                "auto_expand": True
            },
            
            # Trade Categories table - dynamic and expandable
            "trade_categories": {
                "table_name": "Trade Categories",
                "table_id": "tbljXYnOSXYisV1se",  # Reuse existing Red Seal Trades table
                "description": "Dynamic trade categories that expand automatically",
                "core_fields": [
                    {"name": "Category Name", "type": "singleLineText"},
                    {"name": "Official Trade Code", "type": "singleLineText"},
                    {"name": "Red Seal Status", "type": "singleSelect", "options": [
                        "Red Seal Trade", "Provincial Trade", "Emerging Trade", "Other"
                    ]},
                    {"name": "Apprenticeship Length", "type": "singleSelect", "options": [
                        "2 Years", "3 Years", "4 Years", "5+ Years", "No Formal Program"
                    ]},
                    {"name": "Market Size", "type": "singleSelect", "options": [
                        "Large (1000+ annually)", "Medium (100-999)", "Small (10-99)", "Niche (<10)"
                    ]},
                    {"name": "Course Priority", "type": "singleSelect", "options": [
                        "High Priority - Launch First", "Medium Priority - Phase 2", 
                        "Low Priority - Future", "Research Needed"
                    ]},
                    {"name": "Average Salary Range", "type": "singleLineText"},
                    {"name": "Job Growth Outlook", "type": "singleSelect", "options": [
                        "High Growth", "Moderate Growth", "Stable", "Declining"
                    ]}
                ],
                "linking_fields": [
                    {"name": "Common Items Used", "links_to": "items"},
                    {"name": "Major Brands", "links_to": "brands"},
                    {"name": "Work Environments", "links_to": "environments"},
                    {"name": "Required Skills", "links_to": "skills"},
                    {"name": "Workers In Category", "links_to": "contacts"}
                ],
                "auto_expand": True
            },
            
            # Companies table - for organizational context
            "companies": {
                "table_name": "Companies",
                "table_id": "tblBPNe19Pen0F1HW",  # Existing table
                "description": "Companies and organizations across all industries",
                "core_fields": [
                    {"name": "Company Name", "type": "singleLineText"},
                    {"name": "Company Size", "type": "singleSelect", "options": [
                        "1-10", "11-50", "51-200", "201-1000", "1000+"
                    ]},
                    {"name": "Industry Type", "type": "multipleSelects"},
                    {"name": "Headquarters", "type": "singleLineText"},
                    {"name": "Website", "type": "url"},
                    {"name": "Hiring Activity", "type": "singleSelect", "options": [
                        "Actively Hiring", "Selective Hiring", "Stable", "Reducing"
                    ]}
                ],
                "linking_fields": [
                    {"name": "Employees", "links_to": "contacts"},
                    {"name": "Primary Environments", "links_to": "environments"},
                    {"name": "Brands Used", "links_to": "brands"},
                    {"name": "Items/Equipment", "links_to": "items"}
                ],
                "auto_expand": True
            }
        }
    
    async def ensure_universal_structure(self):
        """Ensure all universal tables exist with proper structure."""
        logger.info("🏗️ Ensuring universal table structure exists...")
        
        for table_key, table_config in self.universal_schema.items():
            await self._ensure_table_exists(table_key, table_config)
            await self._ensure_linking_fields_exist(table_key, table_config)
    
    async def _ensure_table_exists(self, table_key: str, config: Dict[str, Any]):
        """Ensure a specific table exists."""
        # This would use MCP to check/create tables
        # For now, logging what would be done
        logger.info(f"   ✅ Table: {config['table_name']} ({table_key})")
        
        if config.get("table_id"):
            logger.info(f"      Using existing table: {config['table_id']}")
        else:
            logger.info(f"      Would create new table: {config['table_name']}")
            # await mcp__airtable__create_table(...)
    
    async def _ensure_linking_fields_exist(self, table_key: str, config: Dict[str, Any]):
        """Ensure linking fields exist between tables."""
        linking_fields = config.get("linking_fields", [])
        
        for link_field in linking_fields:
            logger.info(f"      🔗 Link: {link_field['name']} -> {link_field['links_to']}")
            # Would check/create linking fields using MCP
    
    def get_expansion_opportunities(self, categorization_results: List[Dict]) -> List[Dict[str, Any]]:
        """Identify opportunities to expand the schema based on new data."""
        
        opportunities = []
        
        # Analyze categorization results for new patterns
        new_trades = set()
        new_brands = set()
        new_tools = set()
        new_environments = set()
        
        for result in categorization_results:
            # Detect new trade categories
            category = result.get("primary_category")
            if category and category not in [t["Category Name"] for t in self._get_existing_trades()]:
                new_trades.add(category)
            
            # Detect new brands
            brands = result.get("detected_brands", [])
            for brand in brands:
                if brand not in self._get_existing_brands():
                    new_brands.add(brand)
            
            # Detect new tools/items
            tools = result.get("detected_tools", [])
            for tool in tools:
                if tool not in self._get_existing_items():
                    new_tools.add(tool)
            
            # Detect new environments
            environments = result.get("work_environments", [])
            for env in environments:
                if env not in self._get_existing_environments():
                    new_environments.add(env)
        
        # Create expansion opportunities
        if new_trades:
            opportunities.append({
                "type": "trade_categories",
                "action": "add_new_categories",
                "items": list(new_trades),
                "priority": "high"
            })
        
        if new_brands:
            opportunities.append({
                "type": "brands",
                "action": "add_new_brands",
                "items": list(new_brands),
                "priority": "medium"
            })
        
        if new_tools:
            opportunities.append({
                "type": "items",
                "action": "add_new_items",
                "items": list(new_tools),
                "priority": "medium"
            })
        
        if new_environments:
            opportunities.append({
                "type": "environments",
                "action": "add_new_environments",
                "items": list(new_environments),
                "priority": "low"
            })
        
        return opportunities
    
    async def auto_expand_schema(self, opportunities: List[Dict[str, Any]]):
        """Automatically expand the schema based on detected opportunities."""
        
        for opportunity in opportunities:
            if opportunity["priority"] == "high":
                await self._execute_expansion(opportunity)
                
                self.expansion_log.append({
                    "opportunity": opportunity,
                    "executed_at": datetime.now().isoformat(),
                    "status": "completed"
                })
    
    async def _execute_expansion(self, opportunity: Dict[str, Any]):
        """Execute a specific schema expansion."""
        
        table_type = opportunity["type"]
        action = opportunity["action"]
        items = opportunity["items"]
        
        logger.info(f"🚀 Auto-expanding schema: {action} for {table_type}")
        logger.info(f"   Adding {len(items)} new items: {', '.join(items[:3])}...")
        
        # This would use MCP to actually add the items
        # For now, logging what would be done
        
        if table_type == "trade_categories":
            # Add new trade categories
            for trade in items:
                logger.info(f"      ➕ New trade category: {trade}")
                # await mcp__airtable__create_record(trade_categories_table, {...})
        
        elif table_type == "brands":
            # Add new brands
            for brand in items:
                logger.info(f"      ➕ New brand: {brand}")
                # await mcp__airtable__create_record(brands_table, {...})
        
        # Continue for other types...
    
    def _get_existing_trades(self) -> List[str]:
        """Get existing trade categories (would query Airtable)."""
        # Placeholder - would actually query the table
        return ["Heavy Equipment & Construction", "Automotive & Transportation", 
                "Food Service & Hospitality", "Industrial & Manufacturing"]
    
    def _get_existing_brands(self) -> List[str]:
        """Get existing brands (would query Airtable)."""
        # Placeholder - would actually query the table
        return ["Caterpillar", "Komatsu", "Hobart", "Snap-On"]
    
    def _get_existing_items(self) -> List[str]:
        """Get existing items (would query Airtable)."""
        # Placeholder - would actually query the table
        return ["Excavators", "Commercial Ovens", "Diagnostic Scanners"]
    
    def _get_existing_environments(self) -> List[str]:
        """Get existing environments (would query Airtable)."""
        # Placeholder - would actually query the table
        return ["Construction Sites", "Restaurants", "Auto Shops"]
    
    def get_schema_status(self) -> Dict[str, Any]:
        """Get current schema status and statistics."""
        
        return {
            "total_tables": len(self.universal_schema),
            "auto_expanding_tables": len([t for t in self.universal_schema.values() if t.get("auto_expand")]),
            "total_linking_fields": sum(len(t.get("linking_fields", [])) for t in self.universal_schema.values()),
            "expansion_log_count": len(self.expansion_log),
            "last_expansion": self.expansion_log[-1] if self.expansion_log else None,
            "schema_health": "Optimal"
        }

# Global instance
universal_schema = UniversalTableSchema()