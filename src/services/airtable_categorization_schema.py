#!/usr/bin/env python3
"""
Airtable Categorization Schema for SignalHire Contacts

PURPOSE: Define comprehensive categorization fields with dropdown options for trades and equipment brands
USAGE: Used by Airtable integration to create properly categorized contact records
PART OF: SignalHire to Airtable automation workflow with categorization
CONNECTS TO: Canadian Red Seal trades, heavy equipment manufacturers, contact processing
"""

# Canadian Red Seal Trades - Complete Official List
RED_SEAL_TRADES = {
    # Automotive and Transportation Trades
    "automotive_transportation": [
        "Agricultural Equipment Technician",
        "Auto Body and Collision Technician", 
        "Automotive Refinishing Technician",
        "Automotive Service Technician",
        "Motorcycle Technician",
        "Parts Technician",
        "Recreation Vehicle Service Technician",
        "Transport Trailer Technician",
        "Truck and Transport Mechanic"
    ],
    
    # Heavy Equipment and Mobile Equipment Trades
    "heavy_equipment": [
        "Heavy Duty Equipment Technician",
        "Heavy Equipment Operator (Dozer)",
        "Heavy Equipment Operator (Excavator)", 
        "Heavy Equipment Operator (Tractor-Loader-Backhoe)",
        "Mobile Crane Operator",
        "Tower Crane Operator"
    ],
    
    # Industrial and Manufacturing Trades
    "industrial_manufacturing": [
        "Industrial Mechanic (Millwright)",
        "Instrumentation and Control Technician",
        "Machinist",
        "Metal Fabricator (Fitter)",
        "Tool and Die Maker",
        "Welder"
    ],
    
    # Construction Trades
    "construction": [
        "Boilermaker",
        "Bricklayer", 
        "Cabinetmaker",
        "Carpenter",
        "Concrete Finisher",
        "Construction Craft Worker",
        "Construction Electrician",
        "Drywall Finisher and Plasterer",
        "Floorcovering Installer",
        "Glazier",
        "Insulator (Heat and Frost)",
        "Ironworker",
        "Painter and Decorator",
        "Plasterer",
        "Plumber",
        "Refrigeration and Air Conditioning Mechanic",
        "Roofer",
        "Sheet Metal Worker",
        "Steamfitter-Pipefitter",
        "Stonemason",
        "Tilesetter"
    ],
    
    # Electrical Trades
    "electrical": [
        "Construction Electrician",
        "Industrial Electrician",
        "Powerline Technician"
    ],
    
    # Food and Service Trades
    "food_service": [
        "Baker",
        "Cook",
        "Hairstylist"
    ],
    
    # Gas and Energy Trades
    "gas_energy": [
        "Gasfitter — Class A",
        "Gasfitter — Class B"
    ]
}

# Heavy Equipment and Machinery Brands
EQUIPMENT_BRANDS = {
    # Top Global Manufacturers (by market share)
    "tier_1_global": [
        "Caterpillar",           # 16.8% market share, $41B sales
        "Komatsu",               # 10.7% market share, $25.3B sales  
        "XCMG",                  # 5.8% market share, $13.4B sales
        "John Deere",            # 5.4% market share, $12.5B sales
        "Sany",                  # $11.9B sales
        "Volvo Construction",    # 4.3% market share, $9.8B sales
        "Liebherr",              # 4.3% market share, $9.9B sales
        "Hitachi Construction"   # 4% market share, $9.1B sales
    ],
    
    # Major Regional and Specialty Manufacturers
    "tier_2_major": [
        "JCB",
        "Zoomlion", 
        "Sandvik",
        "Doosan",
        "Hyundai Construction",
        "Kubota",
        "Terex",
        "CNH Industrial",
        "Manitou",
        "Tadano"
    ],
    
    # North American Specialists
    "north_american": [
        "Case Construction",
        "New Holland Construction", 
        "Bobcat",
        "Gehl",
        "Takeuchi",
        "Wacker Neuson",
        "Gradall",
        "Link-Belt",
        "Manitowoc"
    ],
    
    # Mining Equipment Specialists
    "mining_specialists": [
        "Sandvik Mining",
        "Epiroc",
        "Atlas Copco",
        "Metso Outotec",
        "Joy Global (Komatsu Mining)",
        "Bucyrus (Caterpillar)",
        "P&H Mining Equipment"
    ],
    
    # Agricultural Equipment (overlap with construction)
    "agricultural": [
        "John Deere",
        "Case IH", 
        "New Holland Agriculture",
        "Massey Ferguson",
        "Kubota",
        "Fendt",
        "Claas",
        "AGCO"
    ]
}

# Equipment Categories for more granular classification
EQUIPMENT_CATEGORIES = [
    "Excavators",
    "Bulldozers/Dozers", 
    "Wheel Loaders",
    "Backhoe Loaders",
    "Skid Steer Loaders",
    "Dump Trucks",
    "Articulated Trucks",
    "Graders",
    "Compactors/Rollers",
    "Cranes (Mobile)",
    "Cranes (Tower)",
    "Scrapers",
    "Trenchers",
    "Paving Equipment",
    "Crushing Equipment",
    "Screening Equipment",
    "Mining Trucks",
    "Underground Equipment",
    "Agricultural Tractors",
    "Combines",
    "Harvesters"
]

# Work Environments for better categorization
WORK_ENVIRONMENTS = [
    "Construction Sites",
    "Mining Operations", 
    "Agricultural Operations",
    "Manufacturing Plants",
    "Automotive Dealerships/Shops",
    "Transportation/Logistics",
    "Municipal/Government",
    "Oil & Gas",
    "Forestry",
    "Marine/Shipping",
    "Aerospace",
    "Railway",
    "Emergency Services",
    "Utilities (Power/Water)",
    "Waste Management"
]

# Experience Levels
EXPERIENCE_LEVELS = [
    "Apprentice (1st Year)",
    "Apprentice (2nd Year)", 
    "Apprentice (3rd Year)",
    "Apprentice (4th Year)",
    "Journeyperson (0-2 years)",
    "Journeyperson (3-5 years)",
    "Journeyperson (6-10 years)", 
    "Senior Technician (10+ years)",
    "Lead Technician/Supervisor",
    "Shop Foreman",
    "Service Manager",
    "Field Service Manager"
]

# Certifications beyond Red Seal
ADDITIONAL_CERTIFICATIONS = [
    "Red Seal Certified",
    "Manufacturer Specific (Caterpillar)",
    "Manufacturer Specific (Komatsu)", 
    "Manufacturer Specific (John Deere)",
    "Manufacturer Specific (Volvo)",
    "Manufacturer Specific (Hitachi)",
    "ASE Certified",
    "Transport Canada Certified",
    "COR Safety Certified",
    "WHMIS Certified",
    "First Aid/CPR",
    "Crane Operator License",
    "Welding Certifications",
    "Hydraulics Specialist",
    "Electrical Systems Specialist",
    "Diesel Engine Specialist"
]

# Airtable Field Definitions
AIRTABLE_CATEGORIZATION_FIELDS = {
    # Primary Trade Classification
    "Primary Trade": {
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": trade} 
                for category in RED_SEAL_TRADES.values() 
                for trade in category
            ]
        }
    },
    
    # Trade Category (broader grouping)
    "Trade Category": {
        "type": "singleSelect", 
        "options": {
            "choices": [
                {"name": "Automotive & Transportation"},
                {"name": "Heavy Equipment"},
                {"name": "Industrial & Manufacturing"}, 
                {"name": "Construction"},
                {"name": "Electrical"},
                {"name": "Food & Service"},
                {"name": "Gas & Energy"},
                {"name": "Other/Mixed"}
            ]
        }
    },
    
    # Equipment Brands (multiple selection)
    "Equipment Brands Experience": {
        "type": "multipleSelects",
        "options": {
            "choices": [
                {"name": brand}
                for tier in EQUIPMENT_BRANDS.values()
                for brand in tier
            ]
        }
    },
    
    # Primary Equipment Brand (single most relevant)
    "Primary Equipment Brand": {
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": brand}
                for tier in EQUIPMENT_BRANDS.values() 
                for brand in tier
            ]
        }
    },
    
    # Equipment Categories
    "Equipment Categories": {
        "type": "multipleSelects",
        "options": {
            "choices": [
                {"name": category}
                for category in EQUIPMENT_CATEGORIES
            ]
        }
    },
    
    # Work Environment
    "Work Environment": {
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": environment}
                for environment in WORK_ENVIRONMENTS  
            ]
        }
    },
    
    # Experience Level
    "Experience Level": {
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": level}
                for level in EXPERIENCE_LEVELS
            ]
        }
    },
    
    # Certifications
    "Certifications": {
        "type": "multipleSelects", 
        "options": {
            "choices": [
                {"name": cert}
                for cert in ADDITIONAL_CERTIFICATIONS
            ]
        }
    },
    
    # Geographic Region (Canadian focus)
    "Region": {
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": "British Columbia"},
                {"name": "Alberta"}, 
                {"name": "Saskatchewan"},
                {"name": "Manitoba"},
                {"name": "Ontario"},
                {"name": "Quebec"},
                {"name": "New Brunswick"},
                {"name": "Nova Scotia"},
                {"name": "Prince Edward Island"},
                {"name": "Newfoundland and Labrador"},
                {"name": "Northwest Territories"},
                {"name": "Nunavut"},
                {"name": "Yukon"},
                {"name": "Other/International"}
            ]
        }
    }
}

def get_flat_trades_list():
    """Get a flat list of all Red Seal trades for dropdown creation."""
    trades = []
    for category in RED_SEAL_TRADES.values():
        trades.extend(category)
    return sorted(trades)

def get_flat_brands_list():
    """Get a flat list of all equipment brands for dropdown creation.""" 
    brands = []
    for tier in EQUIPMENT_BRANDS.values():
        brands.extend(tier)
    return sorted(list(set(brands)))  # Remove duplicates and sort

def categorize_trade(job_title):
    """Automatically categorize a job title into trade categories."""
    job_title_lower = job_title.lower()
    
    # Check automotive/transportation keywords
    auto_keywords = ['automotive', 'auto', 'vehicle', 'truck', 'transport', 'motorcycle', 'trailer']
    if any(keyword in job_title_lower for keyword in auto_keywords):
        return "Automotive & Transportation"
    
    # Check heavy equipment keywords  
    heavy_keywords = ['heavy', 'equipment', 'operator', 'crane', 'dozer', 'excavator']
    if any(keyword in job_title_lower for keyword in heavy_keywords):
        return "Heavy Equipment"
        
    # Check construction keywords
    construction_keywords = ['construction', 'carpenter', 'electrician', 'plumber', 'welder']
    if any(keyword in job_title_lower for keyword in construction_keywords):
        return "Construction"
        
    # Check industrial keywords
    industrial_keywords = ['industrial', 'mechanic', 'millwright', 'machinist', 'technician']
    if any(keyword in job_title_lower for keyword in industrial_keywords):
        return "Industrial & Manufacturing"
    
    return "Other/Mixed"

def detect_equipment_brands(profile_text):
    """Detect equipment brands mentioned in profile text, skills, or experience."""
    if not profile_text:
        return []
        
    profile_lower = profile_text.lower()
    detected_brands = []
    
    # Check all brands
    all_brands = get_flat_brands_list()
    for brand in all_brands:
        if brand.lower() in profile_lower:
            detected_brands.append(brand)
    
    return detected_brands

def suggest_certifications(job_title, skills_text=""):
    """Suggest relevant certifications based on job title and skills."""
    suggestions = []
    combined_text = f"{job_title} {skills_text}".lower()
    
    # Red Seal is relevant for most trades
    if any(trade.lower() in combined_text for trade in get_flat_trades_list()):
        suggestions.append("Red Seal Certified")
    
    # Brand-specific certifications
    if 'caterpillar' in combined_text or 'cat' in combined_text:
        suggestions.append("Manufacturer Specific (Caterpillar)")
    if 'komatsu' in combined_text:
        suggestions.append("Manufacturer Specific (Komatsu)")
    if 'john deere' in combined_text or 'deere' in combined_text:
        suggestions.append("Manufacturer Specific (John Deere)")
    
    # Skill-based certifications
    if 'welding' in combined_text or 'welder' in combined_text:
        suggestions.append("Welding Certifications")
    if 'hydraulic' in combined_text:
        suggestions.append("Hydraulics Specialist")
    if 'electrical' in combined_text:
        suggestions.append("Electrical Systems Specialist")
    if 'diesel' in combined_text:
        suggestions.append("Diesel Engine Specialist")
        
    return suggestions

# Export the main structures for use in other modules
__all__ = [
    'RED_SEAL_TRADES',
    'EQUIPMENT_BRANDS', 
    'EQUIPMENT_CATEGORIES',
    'WORK_ENVIRONMENTS',
    'EXPERIENCE_LEVELS',
    'ADDITIONAL_CERTIFICATIONS',
    'AIRTABLE_CATEGORIZATION_FIELDS',
    'get_flat_trades_list',
    'get_flat_brands_list', 
    'categorize_trade',
    'detect_equipment_brands',
    'suggest_certifications'
]