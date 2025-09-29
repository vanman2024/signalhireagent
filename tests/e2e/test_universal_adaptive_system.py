#!/usr/bin/env python3
"""
Test Universal Adaptive System - Complete End-to-End Validation

PURPOSE: Test the complete universal system with auto-learning, schema expansion, and SignalHire integration
USAGE: python3 test_universal_adaptive_system.py
PART OF: Universal Red Seal system with infinite scalability
CONNECTS TO: Universal Categorization Engine, Universal Table Schema, SignalHire patterns
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Mock comprehensive SignalHire data
class ComprehensiveCandidate:
    """Enhanced candidate with rich SignalHire-style data."""
    def __init__(self, data: Dict[str, Any]):
        self.fullName = data.get('fullName', '')
        self.title = data.get('title', '')
        self.company = data.get('company', '')
        self.city = data.get('city', '')
        self.country = data.get('country', 'Canada')
        self.emails = data.get('emails', [])
        self.phones = data.get('phones', [])
        self.linkedinUrl = data.get('linkedinUrl', '')
        self.facebookUrl = data.get('facebookUrl', '')
        self.skills = [MockSkill(skill) for skill in data.get('skills', [])]
        
        # Rich SignalHire data
        self.experience = [MockExperience(exp) for exp in data.get('experience', [])]
        self.education = [MockEducation(edu) for edu in data.get('education', [])]
        self.certifications = data.get('certifications', [])
        self.summary = data.get('summary', '')

class MockSkill:
    def __init__(self, skill_name: str):
        self.name = skill_name

class MockExperience:
    def __init__(self, exp_data: Dict):
        self.title = exp_data.get('title', '')
        self.company = exp_data.get('company', '')
        self.description = exp_data.get('description', '')
        self.duration = exp_data.get('duration', '')

class MockEducation:
    def __init__(self, edu_data: Dict):
        self.school = edu_data.get('school', '')
        self.degree = edu_data.get('degree', '')
        self.field = edu_data.get('field', '')

async def test_universal_adaptive_system():
    """Test the complete universal adaptive system."""
    
    from src.services.universal_categorization_engine import universal_engine
    from src.services.universal_table_schema import universal_schema
    
    print("🚀 TESTING UNIVERSAL ADAPTIVE SYSTEM")
    print("=" * 80)
    print("🎯 Testing: Auto-learning, Schema expansion, Cross-industry categorization")
    print("📊 Coverage: ALL Red Seal trades + emerging patterns + SignalHire integration")
    print()
    
    # Comprehensive test dataset across ALL industries
    test_candidates = create_comprehensive_test_dataset()
    
    print(f"📋 Test Dataset: {len(test_candidates)} candidates across ALL trade categories")
    print("   Including: Traditional trades, emerging trades, hybrid roles, leadership levels")
    print()
    
    # Process all candidates and collect results
    results = []
    learning_progression = []
    
    for i, candidate_data in enumerate(test_candidates, 1):
        print(f"🔍 Processing {i}/{len(test_candidates)}: {candidate_data['name']}")
        print("-" * 60)
        
        # Create rich candidate profile
        candidate = ComprehensiveCandidate(candidate_data['profile'])
        signalhire_id = f"universal_{i:03d}"
        
        # Process with universal engine
        categorization_result = await universal_engine.analyze_and_categorize(
            signalhire_id, candidate_data['profile']
        )
        
        # Display results
        display_categorization_results(categorization_result, candidate_data)
        
        # Collect for analysis
        results.append({
            "candidate": candidate_data,
            "result": categorization_result,
            "learning_stats": universal_engine.get_learning_stats()
        })
        
        # Track learning progression
        learning_progression.append(universal_engine.get_learning_stats())
        
        print()
    
    # Analyze system learning and adaptation
    await analyze_system_learning(results, learning_progression)
    
    # Test schema expansion
    await test_schema_expansion(results)
    
    # Generate comprehensive report
    generate_system_report(results, learning_progression)

def create_comprehensive_test_dataset() -> List[Dict[str, Any]]:
    """Create comprehensive test dataset covering ALL scenarios."""
    
    return [
        # Traditional Heavy Equipment (Baseline)
        {
            "name": "Traditional Heavy Equipment Foreman",
            "expected_patterns": ["heavy equipment", "leadership", "caterpillar"],
            "profile": {
                "fullName": "Mike Henderson",
                "title": "Heavy Equipment Shop Foreman",
                "company": "Rocky Mountain Construction",
                "city": "Calgary",
                "emails": ["mike.henderson@rockymtn.ca"],
                "skills": ["Caterpillar Equipment", "Hydraulics", "Team Leadership", "Safety Management"],
                "experience": [
                    {"title": "Shop Foreman", "company": "Rocky Mountain Construction", 
                     "description": "Managing heavy equipment service operations, supervising 12 technicians"},
                    {"title": "Senior Technician", "company": "Finning International", 
                     "description": "Caterpillar equipment repair and maintenance"}
                ],
                "certifications": ["Red Seal Heavy Duty Equipment Technician", "Caterpillar Certified"],
                "summary": "15 years experience in heavy equipment service and repair"
            }
        },
        
        # Food Service - Head Chef (Non-equipment trade)
        {
            "name": "Executive Chef with Culinary Leadership",
            "expected_patterns": ["food service", "leadership", "commercial equipment"],
            "profile": {
                "fullName": "Isabella Martinez",
                "title": "Executive Chef",
                "company": "Four Seasons Hotel Vancouver",
                "city": "Vancouver",
                "skills": ["Culinary Arts", "Menu Development", "Hobart Equipment", "Team Management", "Food Cost Control"],
                "experience": [
                    {"title": "Executive Chef", "company": "Four Seasons Hotel Vancouver",
                     "description": "Leading culinary operations for 300+ seat restaurant, managing 25 kitchen staff"},
                    {"title": "Sous Chef", "company": "Fairmont Hotel",
                     "description": "Food preparation, Rational oven operation, kitchen management"}
                ],
                "certifications": ["Red Seal Cook", "ServSafe Certified", "HACCP"],
                "summary": "12 years culinary experience specializing in high-volume commercial kitchen operations"
            }
        },
        
        # Beauty Services - Salon Owner (Business + Trade)
        {
            "name": "Salon Owner with Business Operations",
            "expected_patterns": ["beauty services", "business owner", "product brands"],
            "profile": {
                "fullName": "Sarah Kim",
                "title": "Salon Owner and Master Stylist",
                "company": "Bella Vista Hair Studio",
                "city": "Toronto",
                "skills": ["Advanced Color Techniques", "Redken Products", "Wella", "Business Management", "Staff Training"],
                "experience": [
                    {"title": "Salon Owner", "company": "Bella Vista Hair Studio",
                     "description": "Operating full-service salon, managing 8 stylists, product inventory"},
                    {"title": "Senior Stylist", "company": "Chatters Hair Salon",
                     "description": "Hair cutting, coloring, chemical services, client consultation"}
                ],
                "certifications": ["Red Seal Hairstylist", "Redken Certified Colorist", "Business License"],
                "summary": "10 years experience, specialized in color correction and business operations"
            }
        },
        
        # Automotive - Diagnostic Specialist (Tech-heavy)
        {
            "name": "Automotive Diagnostic Technology Specialist",
            "expected_patterns": ["automotive", "technology", "diagnostic equipment"],
            "profile": {
                "fullName": "James Wang",
                "title": "Senior Automotive Diagnostic Technician",
                "company": "Mercedes-Benz Downtown",
                "city": "Montreal",
                "skills": ["Computer Diagnostics", "Snap-On Scanners", "Mercedes STAR Diagnostic", "CAN Bus Systems", "Hybrid Technology"],
                "experience": [
                    {"title": "Diagnostic Specialist", "company": "Mercedes-Benz Downtown",
                     "description": "Complex electrical diagnostics, STAR diagnostic system, hybrid vehicle service"},
                    {"title": "Automotive Technician", "company": "Canadian Tire",
                     "description": "General automotive repair, oil changes, brake service"}
                ],
                "certifications": ["Red Seal Automotive Service Technician", "ASE Master Certified", "Mercedes-Benz Certified"],
                "summary": "8 years automotive experience with specialization in advanced diagnostics"
            }
        },
        
        # Industrial - Automation Specialist (Emerging tech)
        {
            "name": "Industrial Automation and Robotics Specialist",
            "expected_patterns": ["industrial", "automation", "robotics", "emerging"],
            "profile": {
                "fullName": "Alex Chen",
                "title": "Industrial Automation Specialist",
                "company": "Bombardier Aerospace",
                "city": "Montreal",
                "skills": ["PLC Programming", "Siemens TIA Portal", "Robot Programming", "SCADA Systems", "Allen Bradley"],
                "experience": [
                    {"title": "Automation Specialist", "company": "Bombardier Aerospace",
                     "description": "Programming industrial robots, PLC maintenance, system integration"},
                    {"title": "Millwright", "company": "Steel Dynamics",
                     "description": "Mechanical equipment maintenance, conveyor systems, pneumatics"}
                ],
                "certifications": ["Red Seal Industrial Mechanic (Millwright)", "Siemens Certified", "Fanuc Robotics"],
                "summary": "6 years industrial experience transitioning into automation and robotics"
            }
        },
        
        # Electrical - Solar Energy (Emerging green tech)
        {
            "name": "Solar Energy Installation Supervisor",
            "expected_patterns": ["electrical", "solar", "green energy", "emerging"],
            "profile": {
                "fullName": "Maria Gonzalez",
                "title": "Solar Installation Supervisor",
                "company": "SunPower Energy Solutions",
                "city": "Calgary",
                "skills": ["Solar Panel Installation", "DC/AC Systems", "Fluke Testing", "Crew Leadership", "Green Energy"],
                "experience": [
                    {"title": "Solar Supervisor", "company": "SunPower Energy Solutions",
                     "description": "Leading solar installation crews, system commissioning, safety compliance"},
                    {"title": "Journeyman Electrician", "company": "IBEW Local 424",
                     "description": "Commercial electrical work, conduit installation, panel wiring"}
                ],
                "certifications": ["Red Seal Electrician", "Solar Installation Certified", "Working at Heights"],
                "summary": "12 years electrical experience with 4 years specializing in solar energy systems"
            }
        },
        
        # Gas Fitting - HVAC Specialist
        {
            "name": "HVAC and Gas Systems Specialist",
            "expected_patterns": ["gas systems", "hvac", "technical specialist"],
            "profile": {
                "fullName": "Robert Brown",
                "title": "HVAC Gas Systems Technician",
                "company": "Climate Control Systems",
                "city": "Edmonton",
                "skills": ["Natural Gas Systems", "HVAC Installation", "Carrier Equipment", "Trane Systems", "Gas Code"],
                "experience": [
                    {"title": "Gas Systems Technician", "company": "Climate Control Systems",
                     "description": "Commercial HVAC installation, gas line installation, system commissioning"},
                    {"title": "Apprentice Gasfitter", "company": "ATCO Gas",
                     "description": "Residential gas line installation, meter connections, safety inspections"}
                ],
                "certifications": ["Red Seal Gasfitter Class A", "HVAC Excellence", "Gas Code Certified"],
                "summary": "7 years experience in gas systems and commercial HVAC"
            }
        },
        
        # Hybrid Role - Operations Manager (Cross-trades)
        {
            "name": "Multi-Trade Operations Manager",
            "expected_patterns": ["management", "multi-trade", "operations"],
            "profile": {
                "fullName": "Jennifer Thompson",
                "title": "Operations Manager - Facilities",
                "company": "Alberta Health Services",
                "city": "Calgary",
                "skills": ["Facilities Management", "Budget Management", "Multi-Trade Coordination", "Project Management", "Vendor Relations"],
                "experience": [
                    {"title": "Operations Manager", "company": "Alberta Health Services",
                     "description": "Managing facilities maintenance across 12 hospitals, coordinating electrical, plumbing, HVAC trades"},
                    {"title": "Maintenance Supervisor", "company": "CBRE",
                     "description": "Supervising building maintenance staff, work order management"},
                    {"title": "Journeyman Electrician", "company": "Independent",
                     "description": "Commercial electrical work, industrial maintenance"}
                ],
                "certifications": ["Red Seal Electrician", "PMP Certified", "Facilities Management"],
                "summary": "18 years experience from trades to management, overseeing multi-million dollar facility operations"
            }
        },
        
        # Emerging Trade - Renewable Energy Technician
        {
            "name": "Wind Turbine Maintenance Technician",
            "expected_patterns": ["renewable energy", "emerging trade", "technical specialist"],
            "profile": {
                "fullName": "David Miller",
                "title": "Wind Turbine Technician",
                "company": "Vestas Wind Systems",
                "city": "Medicine Hat",
                "skills": ["Wind Turbine Maintenance", "High Voltage Systems", "Hydraulic Systems", "Working at Heights", "Vestas Equipment"],
                "experience": [
                    {"title": "Wind Technician", "company": "Vestas Wind Systems",
                     "description": "Preventive maintenance on wind turbines, troubleshooting electrical and mechanical systems"},
                    {"title": "Industrial Electrician", "company": "Suncor Energy",
                     "description": "Oil sands facility electrical maintenance, motor controls, instrumentation"}
                ],
                "certifications": ["Red Seal Industrial Electrician", "Vestas Certified", "Working at Heights", "High Voltage"],
                "summary": "5 years industrial electrical, 3 years specializing in renewable energy systems"
            }
        },
        
        # Apprentice - Learning Track
        {
            "name": "2nd Year Plumbing Apprentice",
            "expected_patterns": ["apprentice", "learning", "plumbing"],
            "profile": {
                "fullName": "Emily Johnson",
                "title": "2nd Year Plumbing Apprentice",
                "company": "Master Mechanical",
                "city": "Winnipeg",
                "skills": ["Pipe Installation", "Soldering", "RIDGID Tools", "Blueprint Reading", "Apprentice Program"],
                "experience": [
                    {"title": "Plumbing Apprentice", "company": "Master Mechanical",
                     "description": "Learning residential and commercial plumbing, pipe installation, fixture installation"},
                    {"title": "General Laborer", "company": "Construction Plus",
                     "description": "Construction site preparation, tool handling, basic carpentry"}
                ],
                "certifications": ["Plumbing Apprentice Registration", "First Aid/CPR", "WHMIS"],
                "summary": "18 months into plumbing apprenticeship, strong mechanical aptitude"
            }
        }
    ]

def display_categorization_results(result: Dict[str, Any], candidate_data: Dict[str, Any]):
    """Display comprehensive categorization results."""
    
    print(f"👤 {result.get('Full Name', 'Unknown')}")
    print(f"💼 {result.get('Job Title', 'Unknown')} at {result.get('Company', 'Unknown')}")
    print(f"📍 {result.get('Location', 'Unknown')}")
    print()
    
    print("🎯 Universal Categorization Results:")
    print(f"   Primary Category: {result.get('Trade Category', 'Not detected')}")
    print(f"   Specific Trade: {result.get('Primary Trade', 'Not detected')}")
    print(f"   Hierarchy Level: {result.get('Trade Hierarchy Level', 'Not detected')}")
    print(f"   Leadership Role: {result.get('Leadership Role', 'Not detected')}")
    print(f"   Experience: {result.get('Estimated Experience', 'Not detected')}")
    print(f"   Confidence Score: {result.get('Confidence Score', 0):.2f}")
    print()
    
    print("🔧 Detected Resources:")
    brands = result.get('Equipment Brands Used', [])
    print(f"   Brands: {', '.join(brands) if brands else 'None detected'}")
    
    tools = result.get('Equipment Types Used', [])
    print(f"   Tools/Equipment: {', '.join(tools) if tools else 'None detected'}")
    
    environments = result.get('Industries', [])
    print(f"   Environments: {', '.join(environments) if environments else 'None detected'}")
    
    specializations = result.get('Specializations', [])
    if specializations:
        print(f"   Specializations: {', '.join(specializations[:3])}")
    
    print(f"   Auto Categorized: {result.get('Auto Categorized', 'No')}")

async def analyze_system_learning(results: List[Dict], progression: List[Dict]):
    """Analyze how the system learned and improved over time."""
    
    print("🧠 SYSTEM LEARNING ANALYSIS")
    print("=" * 60)
    
    initial_stats = progression[0] if progression else {}
    final_stats = progression[-1] if progression else {}
    
    print(f"📊 Learning Progression:")
    print(f"   Contacts Processed: {final_stats.get('processing_stats', {}).get('total_processed', 0)}")
    print(f"   Patterns Learned: {final_stats.get('learned_patterns_count', 0)}")
    print(f"   Brand Associations: {final_stats.get('brand_associations', 0)}")
    print(f"   Skill Associations: {final_stats.get('skill_associations', 0)}")
    print(f"   Categories Learned: {final_stats.get('categories_learned', 0)}")
    print()
    
    # Analyze confidence improvements
    confidence_scores = [r['result'].get('Confidence Score', 0) for r in results]
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    print(f"🎯 Categorization Performance:")
    print(f"   Average Confidence: {avg_confidence:.2f}")
    print(f"   High Confidence (>0.7): {sum(1 for c in confidence_scores if c > 0.7)}/{len(confidence_scores)}")
    print(f"   Learning Opportunities: {sum(1 for r in results if 'learning_opportunity' in r['result'])}")
    print()
    
    # Detect new patterns discovered
    emerging_patterns = []
    for result in results:
        candidate = result['candidate']
        categorization = result['result']
        
        if categorization.get('Trade Category') == 'Unknown/Emerging':
            emerging_patterns.append(candidate['name'])
    
    if emerging_patterns:
        print(f"🔍 Emerging Patterns Detected:")
        for pattern in emerging_patterns:
            print(f"   • {pattern}")
    
    print()

async def test_schema_expansion(results: List[Dict]):
    """Test automatic schema expansion based on discovered patterns."""
    
    from src.services.universal_table_schema import universal_schema
    
    print("🚀 SCHEMA EXPANSION TESTING")
    print("=" * 60)
    
    # Extract categorization results for expansion analysis
    categorization_results = [r['result'] for r in results]
    
    # Identify expansion opportunities
    opportunities = universal_schema.get_expansion_opportunities(categorization_results)
    
    print(f"📋 Expansion Opportunities Detected: {len(opportunities)}")
    
    for i, opportunity in enumerate(opportunities, 1):
        print(f"   {i}. {opportunity['type'].title()}: {opportunity['action']}")
        print(f"      Items: {', '.join(opportunity['items'][:3])}...")
        print(f"      Priority: {opportunity['priority']}")
    print()
    
    # Test auto-expansion
    await universal_schema.auto_expand_schema(opportunities)
    
    # Show schema status
    schema_status = universal_schema.get_schema_status()
    print(f"📊 Schema Status:")
    for key, value in schema_status.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print()

def generate_system_report(results: List[Dict], progression: List[Dict]):
    """Generate comprehensive system performance report."""
    
    print("📋 UNIVERSAL ADAPTIVE SYSTEM REPORT")
    print("=" * 80)
    
    # Overall statistics
    total_processed = len(results)
    successful_categorizations = sum(1 for r in results if r['result'].get('Trade Category') != 'Unknown/Emerging')
    avg_confidence = sum(r['result'].get('Confidence Score', 0) for r in results) / total_processed
    
    print(f"🎯 Overall Performance:")
    print(f"   Total Contacts Processed: {total_processed}")
    print(f"   Successful Categorizations: {successful_categorizations}/{total_processed} ({successful_categorizations/total_processed*100:.1f}%)")
    print(f"   Average Confidence Score: {avg_confidence:.2f}")
    print()
    
    # Trade category coverage
    categories_detected = set()
    for result in results:
        category = result['result'].get('Trade Category')
        if category and category != 'Unknown/Emerging':
            categories_detected.add(category)
    
    print(f"📊 Trade Category Coverage:")
    print(f"   Categories Detected: {len(categories_detected)}")
    for category in sorted(categories_detected):
        count = sum(1 for r in results if r['result'].get('Trade Category') == category)
        print(f"   • {category}: {count} contacts")
    print()
    
    # Brand and tool coverage
    all_brands = set()
    all_tools = set()
    for result in results:
        brands = result['result'].get('Equipment Brands Used', [])
        tools = result['result'].get('Equipment Types Used', [])
        all_brands.update(brands)
        all_tools.update(tools)
    
    print(f"🔧 Resource Detection:")
    print(f"   Unique Brands Detected: {len(all_brands)}")
    print(f"   Unique Tools/Equipment: {len(all_tools)}")
    print()
    
    # Learning system performance
    final_stats = progression[-1] if progression else {}
    print(f"🧠 Learning System:")
    print(f"   Patterns Learned: {final_stats.get('learned_patterns_count', 0)}")
    print(f"   Auto-Expansions: {final_stats.get('schema_expansions', 0)}")
    print(f"   System Adaptivity: {'High' if avg_confidence > 0.6 else 'Medium' if avg_confidence > 0.4 else 'Developing'}")
    print()
    
    # Readiness assessment
    readiness_score = calculate_readiness_score(results, avg_confidence, successful_categorizations, total_processed)
    
    print(f"✅ SYSTEM READINESS ASSESSMENT:")
    print(f"   Overall Readiness Score: {readiness_score:.1f}/100")
    
    if readiness_score >= 80:
        print(f"   🎉 EXCELLENT - Ready for production automation!")
        print(f"      ✅ High accuracy across all trade categories")
        print(f"      ✅ Strong learning and adaptation capabilities")
        print(f"      ✅ Comprehensive resource detection")
        print(f"      ✅ Auto-expanding schema handles new patterns")
    elif readiness_score >= 60:
        print(f"   ⚠️ GOOD - Ready with monitoring")
        print(f"      ✅ Solid performance across most trades")
        print(f"      🔧 Some fine-tuning needed for edge cases")
        print(f"      ✅ Learning system is functional")
    else:
        print(f"   🔧 DEVELOPING - Needs improvement")
        print(f"      🔧 Expand training patterns")
        print(f"      🔧 Improve confidence scoring")
        print(f"      🔧 Add more diverse test cases")
    
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Deploy to production with real SignalHire data")
    print("   2. Monitor learning progression and accuracy")
    print("   3. Review auto-expansions for quality")
    print("   4. Integrate with course marketing segmentation")
    print("   5. Expand to additional Red Seal trades as needed")

def calculate_readiness_score(results: List[Dict], avg_confidence: float, successful: int, total: int) -> float:
    """Calculate overall system readiness score."""
    
    # Base scoring components
    accuracy_score = (successful / total) * 40  # 40% weight
    confidence_score = avg_confidence * 30      # 30% weight
    
    # Coverage scoring
    categories_covered = len(set(r['result'].get('Trade Category', '') for r in results if r['result'].get('Trade Category') != 'Unknown/Emerging'))
    coverage_score = min(categories_covered / 8, 1.0) * 20  # 20% weight (expect 8+ categories)
    
    # Learning scoring
    learning_indicators = sum(1 for r in results if r['result'].get('Auto Categorized') == 'Yes')
    learning_score = (learning_indicators / total) * 10  # 10% weight
    
    return accuracy_score + confidence_score + coverage_score + learning_score

async def main():
    """Main test function."""
    await test_universal_adaptive_system()

if __name__ == "__main__":
    asyncio.run(main())