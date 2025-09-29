#!/usr/bin/env python3
"""
Enhanced Contact Processor with Intelligent Categorization

PURPOSE: Process SignalHire contacts with automatic trade and equipment brand categorization
USAGE: Used by webhook automation to intelligently categorize contacts for Airtable
PART OF: SignalHire to Airtable automation with enhanced categorization
CONNECTS TO: Categorization schema, contact processing, Airtable integration
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .airtable_categorization_schema import (
    categorize_trade,
    detect_equipment_brands,
    suggest_certifications,
    get_flat_trades_list,
    get_flat_brands_list,
    RED_SEAL_TRADES,
    EQUIPMENT_BRANDS
)

logger = logging.getLogger(__name__)

class EnhancedContactProcessor:
    """Processes SignalHire contacts with intelligent categorization for trades and equipment."""
    
    def __init__(self):
        self.stats = {
            "contacts_processed": 0,
            "trades_detected": 0,
            "brands_detected": 0,
            "certifications_suggested": 0,
            "regions_identified": 0
        }
    
    def process_contact_with_categories(self, signalhire_id: str, candidate) -> Dict[str, Any]:
        """Process a contact and add intelligent categorization."""
        try:
            logger.info(f"🤖 Processing contact with AI categorization: {candidate.fullName}")
            
            # Start with basic contact record
            contact_record = self._format_basic_contact(signalhire_id, candidate)
            
            # Add intelligent categorization
            categorization = self._analyze_contact_for_categories(candidate)
            contact_record.update(categorization)
            
            # Update statistics
            self.stats["contacts_processed"] += 1
            if categorization.get("Primary Trade"):
                self.stats["trades_detected"] += 1
            if categorization.get("Equipment Brands Experience"):
                self.stats["brands_detected"] += 1
            if categorization.get("Certifications"):
                self.stats["certifications_suggested"] += 1
            if categorization.get("Region"):
                self.stats["regions_identified"] += 1
            
            logger.info(f"   🎯 Trade: {categorization.get('Primary Trade', 'Not detected')}")
            logger.info(f"   🏗️ Brands: {', '.join(categorization.get('Equipment Brands Experience', [])) or 'None detected'}")
            logger.info(f"   📍 Region: {categorization.get('Region', 'Not detected')}")
            
            return contact_record
            
        except Exception as e:
            logger.error(f"❌ Error processing contact categorization: {e}")
            # Fallback to basic contact record
            return self._format_basic_contact(signalhire_id, candidate)
    
    def _format_basic_contact(self, signalhire_id: str, candidate) -> Dict[str, Any]:
        """Format basic contact information without categorization."""
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
        
        return {
            "Full Name": full_name,
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
            "Source Search": "SignalHire Enhanced Automation"
        }
    
    def _analyze_contact_for_categories(self, candidate) -> Dict[str, Any]:
        """Analyze contact and determine appropriate categories."""
        categorization = {}
        
        # Gather all text for analysis
        analysis_text = self._gather_analysis_text(candidate)
        
        # 1. Detect Primary Trade
        primary_trade = self._detect_primary_trade(candidate.title, analysis_text)
        if primary_trade:
            categorization["Primary Trade"] = primary_trade
            categorization["Trade Category"] = categorize_trade(primary_trade)
        
        # 2. Detect Trade Hierarchy and Leadership
        hierarchy_info = self._detect_trade_hierarchy(candidate.title, analysis_text)
        if hierarchy_info:
            categorization.update(hierarchy_info)
        
        # 3. Detect Specializations
        specializations = self._detect_specializations(analysis_text)
        if specializations:
            categorization["Specializations"] = specializations
        
        # 4. Detect Equipment Brands
        equipment_brands = self._detect_equipment_brands(analysis_text)
        if equipment_brands:
            categorization["Equipment Brands Experience"] = equipment_brands
            categorization["Primary Equipment Brand"] = equipment_brands[0]  # Most prominent
        
        # 5. Detect Equipment Categories
        equipment_categories = self._detect_equipment_categories(analysis_text)
        if equipment_categories:
            categorization["Equipment Categories"] = equipment_categories
        
        # 6. Determine Work Environment
        work_environment = self._determine_work_environment(candidate.company, analysis_text)
        if work_environment:
            categorization["Work Environment"] = work_environment
        
        # 7. Assess Experience Level
        experience_level = self._assess_experience_level(analysis_text, candidate.title)
        if experience_level:
            categorization["Experience Level"] = experience_level
        
        # 8. Suggest Certifications
        certifications = self._suggest_certifications(candidate.title, analysis_text)
        if certifications:
            categorization["Certifications"] = certifications
        
        # 9. Identify Region
        region = self._identify_region(candidate.city, candidate.country)
        if region:
            categorization["Region"] = region
        
        return categorization
    
    def _gather_analysis_text(self, candidate) -> str:
        """Gather all relevant text for analysis."""
        text_parts = []
        
        # Job title and company
        if candidate.title:
            text_parts.append(candidate.title)
        if candidate.company:
            text_parts.append(candidate.company)
        
        # Skills
        if candidate.skills:
            for skill in candidate.skills:
                if hasattr(skill, 'name'):
                    text_parts.append(skill.name)
                else:
                    text_parts.append(str(skill))
        
        # Experience (if available)
        if hasattr(candidate, 'experience') and candidate.experience:
            for exp in candidate.experience:
                if hasattr(exp, 'title'):
                    text_parts.append(exp.title)
                if hasattr(exp, 'company'):
                    text_parts.append(exp.company)
                if hasattr(exp, 'description'):
                    text_parts.append(exp.description)
        
        return " ".join(text_parts).lower()
    
    def _detect_primary_trade(self, job_title: str, analysis_text: str) -> Optional[str]:
        """Detect the most likely Red Seal trade."""
        if not job_title:
            return None
        
        job_title_lower = job_title.lower()
        all_trades = get_flat_trades_list()
        
        # Direct matches first
        for trade in all_trades:
            trade_words = trade.lower().split()
            if all(word in job_title_lower for word in trade_words):
                return trade
        
        # Keyword-based matching
        trade_keywords = {
            "Automotive Service Technician": ["automotive", "service", "technician", "auto", "vehicle"],
            "Heavy Duty Equipment Technician": ["heavy", "duty", "equipment", "technician", "heavy equipment"],
            "Truck and Transport Mechanic": ["truck", "transport", "mechanic", "diesel"],
            "Heavy Equipment Operator (Excavator)": ["excavator", "operator", "heavy equipment"],
            "Heavy Equipment Operator (Dozer)": ["dozer", "bulldozer", "operator"],
            "Heavy Equipment Operator (Tractor-Loader-Backhoe)": ["backhoe", "loader", "tractor"],
            "Industrial Mechanic (Millwright)": ["industrial", "mechanic", "millwright"],
            "Welder": ["welder", "welding"],
            "Machinist": ["machinist", "machine", "shop"],
            "Agricultural Equipment Technician": ["agricultural", "farm", "equipment", "technician"]
        }
        
        for trade, keywords in trade_keywords.items():
            if any(keyword in job_title_lower for keyword in keywords):
                return trade
        
        return None
    
    def _detect_equipment_brands(self, analysis_text: str) -> List[str]:
        """Detect equipment brands mentioned in the text."""
        detected_brands = []
        all_brands = get_flat_brands_list()
        
        for brand in all_brands:
            brand_lower = brand.lower()
            
            # Direct brand name match
            if brand_lower in analysis_text:
                detected_brands.append(brand)
                continue
            
            # Check for common abbreviations/variations
            brand_variations = {
                "caterpillar": ["cat", "caterpillar"],
                "john deere": ["deere", "john deere", "jd"],
                "komatsu": ["komatsu", "komat"],
                "case construction": ["case", "case ih"],
                "new holland": ["new holland", "nh"],
                "jcb": ["jcb"],
                "bobcat": ["bobcat"],
                "volvo construction": ["volvo", "volvo ce"]
            }
            
            variations = brand_variations.get(brand_lower, [brand_lower])
            if any(var in analysis_text for var in variations):
                detected_brands.append(brand)
        
        # Remove duplicates and return top 5 most relevant
        unique_brands = list(dict.fromkeys(detected_brands))
        return unique_brands[:5]
    
    def _detect_equipment_categories(self, analysis_text: str) -> List[str]:
        """Detect equipment categories from text."""
        categories = []
        
        category_keywords = {
            "Excavators": ["excavator", "digger", "shovel"],
            "Bulldozers/Dozers": ["bulldozer", "dozer", "blade"],
            "Wheel Loaders": ["wheel loader", "front loader", "loader"],
            "Backhoe Loaders": ["backhoe", "backhoe loader"],
            "Skid Steer Loaders": ["skid steer", "bobcat", "compact loader"],
            "Dump Trucks": ["dump truck", "dumper", "tipper"],
            "Graders": ["grader", "motor grader"],
            "Compactors/Rollers": ["compactor", "roller", "vibrating"],
            "Cranes (Mobile)": ["mobile crane", "truck crane", "crane"],
            "Cranes (Tower)": ["tower crane", "construction crane"],
            "Mining Trucks": ["mining truck", "haul truck", "off highway"],
            "Agricultural Tractors": ["tractor", "farm equipment"],
            "Combines": ["combine", "harvester"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in analysis_text for keyword in keywords):
                categories.append(category)
        
        return categories[:3]  # Top 3 most relevant
    
    def _determine_work_environment(self, company: str, analysis_text: str) -> Optional[str]:
        """Determine work environment based on company and text analysis."""
        if not company and not analysis_text:
            return None
        
        combined_text = f"{company or ''} {analysis_text}".lower()
        
        environment_keywords = {
            "Construction Sites": ["construction", "contractor", "building", "site"],
            "Mining Operations": ["mining", "mine", "extraction", "quarry"],
            "Agricultural Operations": ["agricultural", "farm", "farming", "crop"],
            "Manufacturing Plants": ["manufacturing", "factory", "plant", "production"],
            "Automotive Dealerships/Shops": ["dealership", "auto shop", "service center", "garage"],
            "Transportation/Logistics": ["transportation", "logistics", "trucking", "freight"],
            "Municipal/Government": ["municipal", "city", "government", "public works"],
            "Oil & Gas": ["oil", "gas", "petroleum", "energy", "pipeline"],
            "Forestry": ["forestry", "logging", "timber", "forest"],
            "Utilities (Power/Water)": ["utility", "power", "water", "electric", "hydro"]
        }
        
        for environment, keywords in environment_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return environment
        
        return None
    
    def _assess_experience_level(self, analysis_text: str, job_title: str) -> Optional[str]:
        """Assess experience level based on title and text."""
        combined_text = f"{job_title or ''} {analysis_text}".lower()
        
        # Check for seniority indicators
        if any(word in combined_text for word in ["senior", "lead", "supervisor", "foreman"]):
            if "manager" in combined_text:
                return "Service Manager"
            elif "foreman" in combined_text:
                return "Shop Foreman"
            else:
                return "Senior Technician (10+ years)"
        
        if any(word in combined_text for word in ["manager", "management"]):
            return "Field Service Manager"
        
        if any(word in combined_text for word in ["apprentice", "trainee"]):
            return "Apprentice (2nd Year)"  # Default apprentice level
        
        if any(word in combined_text for word in ["journeyman", "journeyperson", "certified"]):
            return "Journeyperson (3-5 years)"  # Default journeyperson level
        
        # Default based on job title patterns
        if "technician" in combined_text:
            return "Journeyperson (3-5 years)"
        
        return None
    
    def _suggest_certifications(self, job_title: str, analysis_text: str) -> List[str]:
        """Suggest relevant certifications."""
        certifications = []
        combined_text = f"{job_title or ''} {analysis_text}".lower()
        
        # Red Seal for recognized trades
        if any(trade.lower() in combined_text for trade in get_flat_trades_list()):
            certifications.append("Red Seal Certified")
        
        # Brand-specific certifications
        if "caterpillar" in combined_text or "cat" in combined_text:
            certifications.append("Manufacturer Specific (Caterpillar)")
        if "komatsu" in combined_text:
            certifications.append("Manufacturer Specific (Komatsu)")
        if "john deere" in combined_text or "deere" in combined_text:
            certifications.append("Manufacturer Specific (John Deere)")
        if "volvo" in combined_text:
            certifications.append("Manufacturer Specific (Volvo)")
        if "hitachi" in combined_text:
            certifications.append("Manufacturer Specific (Hitachi)")
        
        # Skill-based certifications
        if "welding" in combined_text or "welder" in combined_text:
            certifications.append("Welding Certifications")
        if "hydraulic" in combined_text:
            certifications.append("Hydraulics Specialist")
        if "electrical" in combined_text:
            certifications.append("Electrical Systems Specialist")
        if "diesel" in combined_text:
            certifications.append("Diesel Engine Specialist")
        if "crane" in combined_text:
            certifications.append("Crane Operator License")
        
        return certifications[:5]  # Top 5 most relevant
    
    def _detect_trade_hierarchy(self, job_title: str, analysis_text: str) -> Dict[str, Any]:
        """Detect trade hierarchy level and leadership role."""
        if not job_title:
            return {}
        
        title_lower = job_title.lower()
        combined_text = f"{job_title} {analysis_text}".lower()
        hierarchy_info = {}
        
        # Leadership role detection
        leadership_keywords = {
            "Senior Management": ["operations manager", "general manager", "regional manager", "director"],
            "Manager": ["service manager", "field service manager", "shop manager", "parts manager"],
            "Supervisor/Foreman": ["foreman", "supervisor", "shop foreman", "lead foreman"],
            "Team Lead": ["lead hand", "team leader", "lead technician", "crew leader", "senior lead"],
            "Individual Contributor": []  # Default
        }
        
        leadership_role = "Individual Contributor"
        for role, keywords in leadership_keywords.items():
            if role == "Individual Contributor":
                continue
            if any(keyword in title_lower for keyword in keywords):
                leadership_role = role
                break
        
        hierarchy_info["Leadership Role"] = leadership_role
        
        # Trade hierarchy level detection
        hierarchy_keywords = {
            "Operations Manager": ["operations manager", "general manager"],
            "Service Manager": ["service manager", "field service manager"],
            "Assistant Manager": ["assistant manager", "deputy manager"],
            "Shop Foreman": ["shop foreman", "service foreman"],
            "Foreman": ["foreman", "crew foreman"],
            "Supervisor": ["supervisor"],
            "Team Leader": ["team leader", "crew leader"],
            "Lead Hand": ["lead hand", "lead technician", "senior lead"],
            "Senior Technician (8+ years)": ["senior technician", "senior tech"],
            "Experienced Technician (5+ years)": ["experienced technician", "technician ii", "tech ii"],
            "Journeyperson": ["journeyman", "journeyperson", "certified technician"],
            "Apprentice (4th Year)": ["4th year apprentice", "final year apprentice"],
            "Apprentice (3rd Year)": ["3rd year apprentice"],
            "Apprentice (2nd Year)": ["2nd year apprentice"],
            "Apprentice (1st Year)": ["1st year apprentice", "apprentice"]
        }
        
        hierarchy_level = None
        for level, keywords in hierarchy_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                hierarchy_level = level
                break
        
        # Default based on leadership role if no specific hierarchy detected
        if not hierarchy_level:
            if leadership_role == "Senior Management":
                hierarchy_level = "Operations Manager"
            elif leadership_role == "Manager":
                hierarchy_level = "Service Manager"
            elif leadership_role == "Supervisor/Foreman":
                hierarchy_level = "Foreman"
            elif leadership_role == "Team Lead":
                hierarchy_level = "Lead Hand"
            else:
                hierarchy_level = "Journeyperson"  # Default assumption
        
        hierarchy_info["Trade Hierarchy Level"] = hierarchy_level
        
        # Years experience estimation based on hierarchy
        experience_mapping = {
            "Apprentice (1st Year)": "0-1 years",
            "Apprentice (2nd Year)": "1-2 years", 
            "Apprentice (3rd Year)": "2-3 years",
            "Apprentice (4th Year)": "3-4 years",
            "Journeyperson": "4-5 years",
            "Experienced Technician (5+ years)": "5-8 years",
            "Senior Technician (8+ years)": "8-12 years",
            "Lead Hand": "8-12 years",
            "Team Leader": "8-12 years",
            "Supervisor": "12-15 years",
            "Foreman": "12-15 years",
            "Shop Foreman": "15-20 years",
            "Assistant Manager": "15-20 years",
            "Service Manager": "15-20 years",
            "Operations Manager": "20+ years"
        }
        
        if hierarchy_level in experience_mapping:
            hierarchy_info["Years Experience"] = experience_mapping[hierarchy_level]
        
        return hierarchy_info
    
    def _detect_specializations(self, analysis_text: str) -> List[str]:
        """Detect technical specializations from text."""
        specializations = []
        
        specialization_keywords = {
            "Hydraulic Systems": ["hydraulic", "hydraulics", "fluid power", "pressure systems"],
            "Diesel Engines": ["diesel", "engine", "motor", "powerplant", "caterpillar engine"],
            "Electrical Systems": ["electrical", "electronics", "wiring", "circuits", "computer systems"],
            "Transmission/Drivetrain": ["transmission", "drivetrain", "gearbox", "final drive"],
            "Undercarriage/Tracks": ["undercarriage", "tracks", "track chains", "sprockets"],
            "Attachments/Implements": ["attachments", "implements", "buckets", "blades"],
            "Engine Diagnostics": ["diagnostics", "troubleshooting", "computer diagnostics"],
            "Welding/Fabrication": ["welding", "fabrication", "metal work", "repair welding"],
            "Preventive Maintenance": ["preventive", "maintenance", "pm", "scheduled maintenance"],
            "Field Service": ["field service", "mobile service", "on-site", "customer site"],
            "Shop Operations": ["shop", "workshop", "facility", "indoor repair"],
            "Parts Management": ["parts", "inventory", "procurement", "ordering"],
            "Customer Service": ["customer", "client", "service", "communication"],
            "Training/Mentoring": ["training", "mentoring", "teaching", "apprentice supervision"],
            "Safety Systems": ["safety", "osha", "compliance", "safety systems"],
            "Air Conditioning/HVAC": ["air conditioning", "hvac", "climate control", "ac"],
            "Computerized Systems": ["computerized", "software", "diagnostic software", "telematics"],
            "Rebuild/Overhaul": ["rebuild", "overhaul", "remanufacturing", "major repair"],
            "Emergency Repair": ["emergency", "breakdown", "urgent repair", "24/7"],
            "Mobile Service": ["mobile", "truck service", "field service truck"]
        }
        
        for specialization, keywords in specialization_keywords.items():
            if any(keyword in analysis_text for keyword in keywords):
                specializations.append(specialization)
        
        return specializations[:8]  # Top 8 most relevant
    
    def _identify_region(self, city: str, country: str) -> Optional[str]:
        """Identify Canadian region based on location."""
        if country and country.lower() not in ["canada", "ca"]:
            return "Other/International"
        
        if not city:
            return None
        
        city_lower = city.lower()
        
        # Provincial mappings
        province_cities = {
            "British Columbia": ["vancouver", "victoria", "burnaby", "richmond", "surrey", "kelowna", "kamloops"],
            "Alberta": ["calgary", "edmonton", "red deer", "lethbridge", "medicine hat", "fort mcmurray"],
            "Saskatchewan": ["saskatoon", "regina", "prince albert", "moose jaw"],
            "Manitoba": ["winnipeg", "brandon", "steinbach"],
            "Ontario": ["toronto", "ottawa", "hamilton", "london", "kitchener", "windsor", "oshawa", "barrie"],
            "Quebec": ["montreal", "quebec city", "laval", "gatineau", "sherbrooke", "trois-rivières"],
            "New Brunswick": ["saint john", "moncton", "fredericton"],
            "Nova Scotia": ["halifax", "sydney", "truro"],
            "Prince Edward Island": ["charlottetown", "summerside"],
            "Newfoundland and Labrador": ["st. john's", "corner brook", "mount pearl"]
        }
        
        for province, cities in province_cities.items():
            if any(prov_city in city_lower for prov_city in cities):
                return province
        
        return None
    
    def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.stats.copy()

# Create a global instance for use in other modules
enhanced_processor = EnhancedContactProcessor()