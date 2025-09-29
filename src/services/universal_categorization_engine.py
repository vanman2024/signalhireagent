#!/usr/bin/env python3
"""
Universal Categorization Engine - Adaptive Learning System

PURPOSE: Self-learning categorization engine that adapts to ALL Red Seal trades and beyond
USAGE: Automatically categorizes contacts using pattern recognition and SignalHire data
PART OF: Universal Red Seal system with infinite scalability
CONNECTS TO: SignalHire API, Airtable, pattern learning algorithms
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import asyncio

logger = logging.getLogger(__name__)

class UniversalCategorizationEngine:
    """Self-learning categorization engine that adapts to any trade or industry."""
    
    def __init__(self):
        self.learned_patterns = defaultdict(list)
        self.industry_patterns = defaultdict(set)
        self.brand_patterns = defaultdict(set)
        self.skill_patterns = defaultdict(set)
        self.confidence_scores = defaultdict(float)
        self.processing_stats = {
            "total_processed": 0,
            "patterns_learned": 0,
            "auto_categorizations": 0,
            "confidence_improvements": 0
        }
        
        # Initialize with foundational patterns
        self._initialize_foundational_patterns()
    
    def _initialize_foundational_patterns(self):
        """Initialize with basic patterns that will expand through learning."""
        
        # Core trade categories (will auto-expand)
        self.foundational_trades = {
            "Heavy Equipment & Construction": {
                "keywords": ["heavy", "equipment", "construction", "excavator", "dozer", "crane"],
                "environments": ["construction", "site", "building", "infrastructure"],
                "brands": ["caterpillar", "komatsu", "volvo", "liebherr", "hitachi"],
                "tools": ["excavator", "bulldozer", "loader", "grader", "compactor"]
            },
            "Automotive & Transportation": {
                "keywords": ["automotive", "auto", "vehicle", "truck", "transport", "mechanic"],
                "environments": ["dealership", "garage", "service center", "fleet"],
                "brands": ["honda", "toyota", "ford", "gm", "snap-on", "matco"],
                "tools": ["diagnostic", "scanner", "lift", "tools", "engine"]
            },
            "Food Service & Hospitality": {
                "keywords": ["cook", "chef", "baker", "food", "kitchen", "culinary"],
                "environments": ["restaurant", "hotel", "kitchen", "bakery", "cafe"],
                "brands": ["hobart", "vulcan", "true", "rational", "viking"],
                "tools": ["oven", "mixer", "slicer", "grill", "fryer"]
            },
            "Industrial & Manufacturing": {
                "keywords": ["industrial", "manufacturing", "production", "factory", "plant"],
                "environments": ["factory", "plant", "manufacturing", "production", "assembly"],
                "brands": ["siemens", "allen bradley", "schneider", "abb", "rockwell"],
                "tools": ["plc", "cnc", "robot", "conveyor", "machinery"]
            },
            "Electrical & Energy": {
                "keywords": ["electrical", "electrician", "power", "energy", "wiring"],
                "environments": ["electrical", "power plant", "utility", "industrial"],
                "brands": ["fluke", "klein", "ideal", "greenlee", "milwaukee"],
                "tools": ["multimeter", "tester", "conduit", "wire", "panel"]
            },
            "Beauty & Personal Services": {
                "keywords": ["hair", "beauty", "salon", "spa", "stylist", "barber"],
                "environments": ["salon", "spa", "barbershop", "beauty"],
                "brands": ["redken", "loreal", "wella", "schwarzkopf", "matrix"],
                "tools": ["shears", "dryer", "chair", "steamer", "color"]
            },
            "Gas & Plumbing": {
                "keywords": ["gas", "plumbing", "pipe", "plumber", "gasfitter"],
                "environments": ["residential", "commercial", "industrial", "municipal"],
                "brands": ["ridgid", "milwaukee", "dewalt", "viega", "uponor"],
                "tools": ["pipe", "wrench", "snake", "torch", "meter"]
            }
        }
    
    async def analyze_and_categorize(self, signalhire_id: str, profile_data: Dict) -> Dict[str, Any]:
        """Main analysis function that learns and categorizes."""
        logger.info(f"🤖 Universal analysis starting for: {profile_data.get('fullName', 'Unknown')}")
        
        # Extract comprehensive data
        analysis_data = self._extract_comprehensive_data(profile_data)
        
        # Perform multi-dimensional analysis
        categorization = await self._perform_universal_analysis(analysis_data)
        
        # Learn from this analysis
        self._learn_from_analysis(analysis_data, categorization)
        
        # Format for Airtable
        airtable_record = self._format_universal_record(signalhire_id, profile_data, categorization)
        
        self.processing_stats["total_processed"] += 1
        
        logger.info(f"   🎯 Categorized as: {categorization.get('primary_category', 'Unknown')}")
        logger.info(f"   📊 Confidence: {categorization.get('confidence_score', 0):.2f}")
        
        return airtable_record
    
    def _extract_comprehensive_data(self, profile_data: Dict) -> Dict[str, Any]:
        """Extract all available data from SignalHire profile."""
        
        # Basic information
        job_title = profile_data.get('title', '')
        company = profile_data.get('company', '')
        location = f"{profile_data.get('city', '')} {profile_data.get('country', '')}"
        
        # Skills extraction
        skills = []
        if hasattr(profile_data, 'skills') and profile_data.skills:
            for skill in profile_data.skills:
                if hasattr(skill, 'name'):
                    skills.append(skill.name)
                else:
                    skills.append(str(skill))
        elif profile_data.get('skills'):
            skills = profile_data['skills']
        
        # Experience extraction (if available)
        experience_text = ""
        if hasattr(profile_data, 'experience') and profile_data.experience:
            for exp in profile_data.experience:
                if hasattr(exp, 'title'):
                    experience_text += f" {exp.title}"
                if hasattr(exp, 'company'):
                    experience_text += f" {exp.company}"
                if hasattr(exp, 'description'):
                    experience_text += f" {exp.description}"
        
        # Education extraction (if available)
        education_text = ""
        if hasattr(profile_data, 'education') and profile_data.education:
            for edu in profile_data.education:
                if hasattr(edu, 'school'):
                    education_text += f" {edu.school}"
                if hasattr(edu, 'degree'):
                    education_text += f" {edu.degree}"
                if hasattr(edu, 'field'):
                    education_text += f" {edu.field}"
        
        # Combine all text for analysis
        combined_text = f"{job_title} {company} {' '.join(skills)} {experience_text} {education_text}".lower()
        
        return {
            "job_title": job_title,
            "company": company,
            "location": location,
            "skills": skills,
            "experience_text": experience_text,
            "education_text": education_text,
            "combined_text": combined_text,
            "profile_richness": len(combined_text.split())
        }
    
    async def _perform_universal_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive multi-dimensional analysis."""
        
        categorization = {
            "confidence_score": 0.0,
            "detected_patterns": [],
            "learning_opportunities": []
        }
        
        # 1. Trade Category Detection
        trade_analysis = self._analyze_trade_category(data)
        categorization.update(trade_analysis)
        
        # 2. Hierarchy and Leadership Detection
        hierarchy_analysis = self._analyze_hierarchy_and_leadership(data)
        categorization.update(hierarchy_analysis)
        
        # 3. Brand and Tool Detection
        brand_analysis = self._analyze_brands_and_tools(data)
        categorization.update(brand_analysis)
        
        # 4. Environment and Industry Detection
        environment_analysis = self._analyze_work_environment(data)
        categorization.update(environment_analysis)
        
        # 5. Specialization Detection
        specialization_analysis = self._analyze_specializations(data)
        categorization.update(specialization_analysis)
        
        # 6. Regional and Certification Analysis
        regional_analysis = self._analyze_regional_and_certifications(data)
        categorization.update(regional_analysis)
        
        # 7. Calculate overall confidence
        categorization["confidence_score"] = self._calculate_confidence_score(categorization)
        
        return categorization
    
    def _analyze_trade_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and determine trade category with learning."""
        
        combined_text = data["combined_text"]
        job_title = data["job_title"].lower()
        
        category_scores = defaultdict(float)
        detected_trades = []
        
        # Score against foundational patterns
        for category, patterns in self.foundational_trades.items():
            score = 0.0
            
            # Keyword matching
            for keyword in patterns["keywords"]:
                if keyword in combined_text:
                    score += 1.0
                if keyword in job_title:
                    score += 2.0  # Job title matches are more important
            
            # Environment matching
            for env in patterns["environments"]:
                if env in combined_text:
                    score += 0.5
            
            # Brand matching
            for brand in patterns["brands"]:
                if brand in combined_text:
                    score += 0.7
            
            # Tool matching
            for tool in patterns["tools"]:
                if tool in combined_text:
                    score += 0.5
            
            category_scores[category] = score
        
        # Score against learned patterns
        for category, learned_patterns in self.learned_patterns.items():
            for pattern in learned_patterns:
                if pattern["pattern"] in combined_text:
                    category_scores[category] += pattern["confidence"]
        
        # Determine primary category
        if category_scores:
            primary_category = max(category_scores.items(), key=lambda x: x[1])
            primary_trade = self._detect_specific_trade(data, primary_category[0])
            
            return {
                "primary_category": primary_category[0],
                "category_confidence": primary_category[1],
                "primary_trade": primary_trade,
                "category_scores": dict(category_scores),
                "detected_trades": detected_trades
            }
        
        return {
            "primary_category": "Unknown/Emerging",
            "category_confidence": 0.0,
            "primary_trade": None,
            "category_scores": {},
            "detected_trades": [],
            "learning_opportunity": "New trade pattern detected"
        }
    
    def _detect_specific_trade(self, data: Dict[str, Any], category: str) -> Optional[str]:
        """Detect specific Red Seal trade within category."""
        
        combined_text = data["combined_text"]
        job_title = data["job_title"].lower()
        
        # Red Seal trade patterns (expandable)
        trade_patterns = {
            "Heavy Equipment & Construction": {
                "Heavy Duty Equipment Technician": ["heavy duty", "equipment technician", "heavy equipment"],
                "Heavy Equipment Operator (Excavator)": ["excavator operator", "excavator", "digger operator"],
                "Heavy Equipment Operator (Dozer)": ["dozer operator", "bulldozer operator", "dozer"],
                "Mobile Crane Operator": ["crane operator", "mobile crane", "crane"],
                "Construction Electrician": ["construction electrician", "electrical", "electrician"]
            },
            "Automotive & Transportation": {
                "Automotive Service Technician": ["automotive technician", "auto technician", "service technician"],
                "Truck and Transport Mechanic": ["truck mechanic", "transport mechanic", "diesel mechanic"],
                "Agricultural Equipment Technician": ["agricultural technician", "farm equipment", "ag tech"]
            },
            "Food Service & Hospitality": {
                "Cook": ["cook", "line cook", "prep cook"],
                "Baker": ["baker", "pastry chef", "baking"],
                "Hairstylist": ["hairstylist", "hair stylist", "salon"]
            },
            "Industrial & Manufacturing": {
                "Industrial Mechanic (Millwright)": ["millwright", "industrial mechanic", "industrial maintenance"],
                "Machinist": ["machinist", "cnc", "machine operator"],
                "Welder": ["welder", "welding", "fabricator"]
            },
            "Electrical & Energy": {
                "Construction Electrician": ["electrician", "electrical", "wiring"],
                "Industrial Electrician": ["industrial electrician", "plant electrician"],
                "Powerline Technician": ["powerline", "lineman", "power technician"]
            },
            "Beauty & Personal Services": {
                "Hairstylist": ["hairstylist", "hair stylist", "cosmetologist"]
            },
            "Gas & Plumbing": {
                "Plumber": ["plumber", "plumbing", "pipefitter"],
                "Gasfitter — Class A": ["gasfitter", "gas technician", "gas fitter"],
                "Steamfitter-Pipefitter": ["steamfitter", "pipefitter", "pipe fitter"]
            }
        }
        
        category_trades = trade_patterns.get(category, {})
        
        # Score trades within category
        trade_scores = {}
        for trade, keywords in category_trades.items():
            score = 0
            for keyword in keywords:
                if keyword in job_title:
                    score += 3  # Strong match in job title
                elif keyword in combined_text:
                    score += 1  # General match
            trade_scores[trade] = score
        
        # Return highest scoring trade
        if trade_scores:
            best_trade = max(trade_scores.items(), key=lambda x: x[1])
            if best_trade[1] > 0:
                return best_trade[0]
        
        return None
    
    def _analyze_hierarchy_and_leadership(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career hierarchy and leadership level."""
        
        job_title = data["job_title"].lower()
        combined_text = data["combined_text"]
        
        # Hierarchy patterns (universal across all trades)
        hierarchy_patterns = {
            "Executive": ["ceo", "president", "executive", "director", "vice president"],
            "Senior Manager": ["general manager", "operations manager", "regional manager"],
            "Manager": ["manager", "service manager", "shop manager", "department manager"],
            "Assistant Manager": ["assistant manager", "deputy manager", "associate manager"],
            "Supervisor": ["supervisor", "foreman", "team leader", "crew leader"],
            "Lead Hand": ["lead hand", "team lead", "senior lead", "lead technician"],
            "Senior Professional": ["senior", "sr.", "principal", "specialist"],
            "Professional": ["technician", "mechanic", "specialist", "analyst"],
            "Apprentice": ["apprentice", "trainee", "student", "intern"]
        }
        
        hierarchy_level = "Professional"  # Default
        leadership_role = "Individual Contributor"  # Default
        years_experience = "Unknown"
        
        # Detect hierarchy level
        for level, keywords in hierarchy_patterns.items():
            if any(keyword in job_title for keyword in keywords):
                hierarchy_level = level
                break
        
        # Detect leadership role
        leadership_keywords = {
            "Senior Executive": ["ceo", "president", "executive"],
            "Senior Management": ["director", "general manager", "operations manager"],
            "Manager": ["manager", "service manager", "shop manager"],
            "Supervisor/Foreman": ["supervisor", "foreman", "crew leader"],
            "Team Lead": ["team lead", "lead hand", "senior lead"],
            "Individual Contributor": []  # Default
        }
        
        for role, keywords in leadership_keywords.items():
            if role == "Individual Contributor":
                continue
            if any(keyword in job_title for keyword in keywords):
                leadership_role = role
                break
        
        # Estimate experience based on hierarchy
        experience_mapping = {
            "Apprentice": "0-4 years",
            "Professional": "4-8 years",
            "Senior Professional": "8-12 years",
            "Lead Hand": "8-15 years",
            "Supervisor": "12-20 years",
            "Manager": "15-25 years",
            "Senior Manager": "20+ years",
            "Executive": "25+ years"
        }
        
        years_experience = experience_mapping.get(hierarchy_level, "Unknown")
        
        return {
            "hierarchy_level": hierarchy_level,
            "leadership_role": leadership_role,
            "estimated_experience": years_experience
        }
    
    def _analyze_brands_and_tools(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Universal brand and tool detection across all industries."""
        
        combined_text = data["combined_text"]
        detected_brands = []
        detected_tools = []
        
        # Universal brand patterns (expandable)
        universal_brands = {
            # Heavy Equipment
            "caterpillar": "Caterpillar", "cat": "Caterpillar", "komatsu": "Komatsu",
            "volvo": "Volvo", "liebherr": "Liebherr", "hitachi": "Hitachi",
            
            # Automotive
            "snap-on": "Snap-On", "matco": "Matco", "mac tools": "Mac Tools",
            "honda": "Honda", "toyota": "Toyota", "ford": "Ford",
            
            # Food Service  
            "hobart": "Hobart", "vulcan": "Vulcan", "true": "True Refrigeration",
            "rational": "Rational", "viking": "Viking",
            
            # Industrial
            "siemens": "Siemens", "allen bradley": "Allen Bradley", "schneider": "Schneider Electric",
            "abb": "ABB", "rockwell": "Rockwell Automation",
            
            # Electrical
            "fluke": "Fluke", "klein": "Klein Tools", "ideal": "Ideal Industries",
            "greenlee": "Greenlee", "milwaukee": "Milwaukee Tool",
            
            # Beauty
            "redken": "Redken", "loreal": "L'Oreal", "wella": "Wella",
            "schwarzkopf": "Schwarzkopf", "matrix": "Matrix",
            
            # Plumbing/Gas
            "ridgid": "RIDGID", "dewalt": "DeWalt", "viega": "Viega", "uponor": "Uponor"
        }
        
        # Detect brands
        for brand_key, brand_name in universal_brands.items():
            if brand_key in combined_text:
                detected_brands.append(brand_name)
        
        # Universal tool patterns (expandable)
        universal_tools = {
            # Physical tools
            "excavator": "Excavators", "bulldozer": "Bulldozers", "crane": "Cranes",
            "oven": "Commercial Ovens", "mixer": "Commercial Mixers", "grill": "Commercial Grills",
            "multimeter": "Electrical Testing Equipment", "scanner": "Diagnostic Scanners",
            "shears": "Professional Shears", "dryer": "Professional Hair Dryers",
            
            # Software tools
            "autocad": "CAD Software", "solidworks": "3D Design Software",
            "pos": "Point of Sale Systems", "diagnostic software": "Diagnostic Software"
        }
        
        # Detect tools
        for tool_key, tool_name in universal_tools.items():
            if tool_key in combined_text:
                detected_tools.append(tool_name)
        
        return {
            "detected_brands": detected_brands,
            "detected_tools": detected_tools,
            "primary_brand": detected_brands[0] if detected_brands else None
        }
    
    def _analyze_work_environment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze work environment and industry context."""
        
        combined_text = data["combined_text"]
        company = data["company"].lower()
        
        # Universal environment patterns
        environment_patterns = {
            "Construction Sites": ["construction", "building", "site", "contractor"],
            "Manufacturing Facilities": ["manufacturing", "factory", "plant", "production"],
            "Restaurants & Food Service": ["restaurant", "hotel", "kitchen", "food service"],
            "Automotive Facilities": ["dealership", "garage", "auto shop", "service center"],
            "Salons & Spas": ["salon", "spa", "beauty", "barbershop"],
            "Industrial Plants": ["industrial", "chemical", "refinery", "processing"],
            "Healthcare Facilities": ["hospital", "clinic", "medical", "healthcare"],
            "Educational Institutions": ["school", "university", "college", "training"],
            "Government & Municipal": ["government", "municipal", "city", "public works"],
            "Mining Operations": ["mining", "mine", "extraction", "quarry"],
            "Agricultural Operations": ["farm", "agricultural", "ranch", "farming"],
            "Transportation & Logistics": ["transportation", "logistics", "shipping", "freight"]
        }
        
        detected_environments = []
        for environment, keywords in environment_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_environments.append(environment)
        
        primary_environment = detected_environments[0] if detected_environments else "General Commercial"
        
        return {
            "work_environments": detected_environments,
            "primary_environment": primary_environment
        }
    
    def _analyze_specializations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect technical specializations."""
        
        combined_text = data["combined_text"]
        
        # Universal specialization patterns
        specialization_patterns = {
            "Hydraulic Systems": ["hydraulic", "hydraulics", "fluid power"],
            "Electrical Systems": ["electrical", "electronics", "wiring", "circuits"],
            "Diesel Engines": ["diesel", "engine", "motor", "powerplant"],
            "Computer Systems": ["computer", "software", "digital", "programming"],
            "Safety & Compliance": ["safety", "osha", "compliance", "regulations"],
            "Quality Control": ["quality", "inspection", "testing", "standards"],
            "Training & Development": ["training", "teaching", "mentoring", "education"],
            "Customer Service": ["customer", "client", "service", "relations"],
            "Project Management": ["project", "planning", "coordination", "management"],
            "Maintenance & Repair": ["maintenance", "repair", "service", "preventive"]
        }
        
        detected_specializations = []
        for specialization, keywords in specialization_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_specializations.append(specialization)
        
        return {
            "specializations": detected_specializations[:5]  # Top 5
        }
    
    def _analyze_regional_and_certifications(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze regional location and certifications."""
        
        location = data["location"].lower()
        combined_text = data["combined_text"]
        
        # Canadian regions
        regional_mapping = {
            "British Columbia": ["vancouver", "victoria", "burnaby", "british columbia", "bc"],
            "Alberta": ["calgary", "edmonton", "alberta", "ab"],
            "Saskatchewan": ["saskatoon", "regina", "saskatchewan", "sk"],
            "Manitoba": ["winnipeg", "manitoba", "mb"],
            "Ontario": ["toronto", "ottawa", "hamilton", "ontario", "on"],
            "Quebec": ["montreal", "quebec", "laval", "qc"],
            "Atlantic Canada": ["halifax", "saint john", "charlottetown", "newfoundland"]
        }
        
        region = "Unknown"
        for region_name, locations in regional_mapping.items():
            if any(loc in location for loc in locations):
                region = region_name
                break
        
        # Certification detection
        certification_patterns = {
            "Red Seal Certified": ["red seal", "interprovincial", "certified"],
            "Manufacturer Certified": ["certified", "factory trained", "authorized"],
            "Safety Certified": ["safety", "whmis", "first aid", "cpr"],
            "Trade Licensed": ["licensed", "journeyman", "apprentice"],
            "Professional Designation": ["professional", "designation", "chartered"]
        }
        
        detected_certifications = []
        for cert, keywords in certification_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_certifications.append(cert)
        
        return {
            "region": region,
            "certifications": detected_certifications
        }
    
    def _calculate_confidence_score(self, categorization: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the categorization."""
        
        score = 0.0
        
        # Category confidence
        score += categorization.get("category_confidence", 0) * 0.3
        
        # Trade detection
        if categorization.get("primary_trade"):
            score += 0.2
        
        # Brand detection
        if categorization.get("detected_brands"):
            score += len(categorization["detected_brands"]) * 0.1
        
        # Tool detection  
        if categorization.get("detected_tools"):
            score += len(categorization["detected_tools"]) * 0.05
        
        # Hierarchy confidence
        if categorization.get("hierarchy_level") != "Professional":
            score += 0.15
        
        # Specialization depth
        if categorization.get("specializations"):
            score += len(categorization["specializations"]) * 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _learn_from_analysis(self, data: Dict[str, Any], categorization: Dict[str, Any]):
        """Learn from this analysis to improve future categorizations."""
        
        primary_category = categorization.get("primary_category")
        confidence = categorization.get("confidence_score", 0)
        
        if primary_category and confidence > 0.5:
            # Extract patterns that led to this categorization
            job_title = data["job_title"].lower()
            company = data["company"].lower()
            
            # Learn job title patterns
            if job_title:
                pattern = {
                    "pattern": job_title,
                    "confidence": confidence,
                    "source": "job_title",
                    "learned_at": datetime.now().isoformat()
                }
                self.learned_patterns[primary_category].append(pattern)
            
            # Learn company patterns
            if company:
                pattern = {
                    "pattern": company,
                    "confidence": confidence * 0.7,  # Company patterns are less reliable
                    "source": "company",
                    "learned_at": datetime.now().isoformat()
                }
                self.learned_patterns[primary_category].append(pattern)
            
            # Learn brand associations
            brands = categorization.get("detected_brands", [])
            for brand in brands:
                self.brand_patterns[primary_category].add(brand.lower())
            
            # Learn skill associations
            skills = data.get("skills", [])
            for skill in skills:
                self.skill_patterns[primary_category].add(skill.lower())
            
            self.processing_stats["patterns_learned"] += 1
    
    def _format_universal_record(self, signalhire_id: str, profile_data: Dict, categorization: Dict[str, Any]) -> Dict[str, Any]:
        """Format the analysis results for Airtable."""
        
        # Basic contact information
        record = {
            "Full Name": profile_data.get('fullName', ''),
            "SignalHire ID": signalhire_id,
            "Job Title": profile_data.get('title', ''),
            "Company": profile_data.get('company', ''),
            "Location": f"{profile_data.get('city', '')} {profile_data.get('country', '')}".strip(),
            "Primary Email": profile_data.get('emails', [''])[0] if profile_data.get('emails') else '',
            "Phone Number": profile_data.get('phones', [''])[0] if profile_data.get('phones') else '',
            "LinkedIn URL": profile_data.get('linkedinUrl', ''),
            "Status": "New",
            "Date Added": datetime.now().isoformat(),
            "Source Search": "Universal Categorization Engine"
        }
        
        # Add categorization results
        record.update({
            "Primary Trade": categorization.get("primary_trade"),
            "Trade Category": categorization.get("primary_category"),
            "Trade Hierarchy Level": categorization.get("hierarchy_level"),
            "Leadership Role": categorization.get("leadership_role"),
            "Estimated Experience": categorization.get("estimated_experience"),
            "Specializations": categorization.get("specializations", []),
            "Equipment Brands Used": categorization.get("detected_brands", []),
            "Primary Equipment Brand": categorization.get("primary_brand"),
            "Equipment Types Used": categorization.get("detected_tools", []),
            "Industries": categorization.get("work_environments", []),
            "Primary Work Environment": categorization.get("primary_environment"),
            "Certifications": categorization.get("certifications", []),
            "Region": categorization.get("region"),
            "Confidence Score": round(categorization.get("confidence_score", 0), 2),
            "Auto Categorized": "Yes"
        })
        
        return record
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning engine."""
        return {
            "processing_stats": self.processing_stats.copy(),
            "learned_patterns_count": sum(len(patterns) for patterns in self.learned_patterns.values()),
            "brand_associations": len(self.brand_patterns),
            "skill_associations": len(self.skill_patterns),
            "categories_learned": len(self.learned_patterns)
        }
    
    def export_learned_patterns(self) -> Dict[str, Any]:
        """Export learned patterns for backup/analysis."""
        return {
            "learned_patterns": dict(self.learned_patterns),
            "brand_patterns": {k: list(v) for k, v in self.brand_patterns.items()},
            "skill_patterns": {k: list(v) for k, v in self.skill_patterns.items()},
            "exported_at": datetime.now().isoformat()
        }

# Global instance for use across the application
universal_engine = UniversalCategorizationEngine()