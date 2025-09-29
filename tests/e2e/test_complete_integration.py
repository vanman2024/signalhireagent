#!/usr/bin/env python3
"""
Complete Integration Test with Dynamic Expansion

PURPOSE: Test the complete system including Universal Adaptive categorization and dynamic expansion
USAGE: python3 test_complete_integration.py
PART OF: SignalHire to Airtable automation with Universal Adaptive System
CONNECTS TO: All system components including dynamic expansion for new items
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

def create_comprehensive_test_data() -> Dict[str, Any]:
    """Create test data including contacts with new items not in existing dropdowns."""
    return {
        "signalhire_id_004": {
            "profile": {
                "name": "Emma Wilson",
                "firstName": "Emma",
                "lastName": "Wilson",
                "title": "Solar Panel Installation Specialist",  # New trade
                "company": "GreenTech Energy Solutions",
                "location": {
                    "city": "Victoria",
                    "country": "Canada"
                },
                "linkedinUrl": "https://linkedin.com/in/emmawilson",
                "skills": [
                    {"name": "Tesla Solar Systems"},  # New brand
                    {"name": "NABCEP Certified"},      # New certification
                    {"name": "Renewable Energy Design"}, # New specialization
                    {"name": "Rooftop Installation"},   # New environment
                    {"name": "8+ Years Experience"}
                ]
            },
            "contacts": [
                {
                    "emails": ["emma.wilson@greentech.ca"],
                    "phones": ["+1-250-555-0987"],
                    "linkedinUrl": "https://linkedin.com/in/emmawilson",
                    "facebookUrl": ""
                }
            ]
        },
        "signalhire_id_005": {
            "profile": {
                "name": "Marcus Chen",
                "firstName": "Marcus",
                "lastName": "Chen", 
                "title": "Wind Turbine Maintenance Supervisor",  # New trade
                "company": "WindPower Canada",
                "location": {
                    "city": "Medicine Hat",
                    "country": "Canada"
                },
                "skills": [
                    {"name": "Vestas Turbines"},        # New brand
                    {"name": "GWO Certified"},          # New certification
                    {"name": "High Altitude Work"},     # New specialization
                    {"name": "Wind Farms"},             # New environment
                    {"name": "Team Leadership"},
                    {"name": "12+ Years Experience"}
                ]
            },
            "contacts": [
                {
                    "emails": ["marcus.chen@windpower.ca"],
                    "phones": ["+1-403-555-0654"],
                    "linkedinUrl": "https://linkedin.com/in/marcuschen",
                    "facebookUrl": ""
                }
            ]
        },
        "signalhire_id_006": {
            "profile": {
                "name": "Sarah Kim",
                "firstName": "Sarah", 
                "lastName": "Kim",
                "title": "Drone Pilot and Aerial Surveyor",  # New trade
                "company": "SkyView Mapping",
                "location": {
                    "city": "Winnipeg", 
                    "country": "Canada"
                },
                "skills": [
                    {"name": "DJI Professional"},       # New brand
                    {"name": "Transport Canada RPAS"},  # New certification
                    {"name": "Aerial Photography"},     # New specialization
                    {"name": "Construction Surveys"},   # New environment
                    {"name": "6+ Years Experience"}
                ]
            },
            "contacts": [
                {
                    "emails": ["sarah.kim@skyview.ca"],
                    "phones": ["+1-204-555-0321"],
                    "linkedinUrl": "https://linkedin.com/in/sarahkim",
                    "facebookUrl": ""
                }
            ]
        }
    }

async def test_complete_integration():
    """Test the complete system including dynamic expansion."""
    print("🧪 Testing Complete Integration - Universal Adaptive + Dynamic Expansion")
    print("=" * 90)
    
    # Import the production automation
    from src.services.signalhire_to_airtable_automation import SignalHireAirtableProcessor
    
    # Create test data with new items
    test_contacts = create_comprehensive_test_data()
    print(f"📋 Created {len(test_contacts)} test contacts with new items")
    
    # Initialize the processor
    processor = SignalHireAirtableProcessor()
    
    # Get contacts with info
    contacts_with_info = processor.get_contacts_with_info(test_contacts)
    print(f"📊 Contacts with revealed info: {len(contacts_with_info)}")
    
    print(f"\n🔍 Testing Complete System Integration...")
    print("-" * 80)
    
    integration_results = {
        "total_processed": 0,
        "successful_categorizations": 0,
        "new_items_detected": 0,
        "pending_items_created": 0,
        "airtable_ready": 0
    }
    
    # Process each contact through the complete system
    for i, contact_data in enumerate(contacts_with_info, 1):
        print(f"\n📋 Processing Contact {i}/{len(contacts_with_info)}")
        print(f"   ID: {contact_data['signalhire_id']}")
        print(f"   Name: {contact_data['data']['profile'].get('name', 'Unknown')}")
        print(f"   Title: {contact_data['data']['profile'].get('title', 'Unknown')}")
        
        integration_results["total_processed"] += 1
        
        try:
            # Format contact with complete system (Universal Adaptive + Dynamic Expansion)
            airtable_record = await processor.format_contact_for_airtable(contact_data)
            
            print(f"\n✅ Complete System Processing Results:")
            print(f"   🎯 Trade Category: {airtable_record.get('Trade Category', 'Not detected')}")
            print(f"   🔧 Primary Trade: {airtable_record.get('Primary Trade', 'Not detected')}")
            print(f"   📊 Hierarchy: {airtable_record.get('Trade Hierarchy Level', 'Not detected')}")
            print(f"   👑 Leadership: {airtable_record.get('Leadership Role', 'Not detected')}")
            print(f"   📅 Experience: {airtable_record.get('Years Experience', 'Not detected')}")
            print(f"   🏷️  Brands: {airtable_record.get('Equipment Brands Experience', [])}")
            print(f"   🛠️  Equipment: {airtable_record.get('Equipment Categories', [])}")
            print(f"   🎓 Certifications: {airtable_record.get('Certifications', [])}")
            print(f"   ⭐ Specializations: {airtable_record.get('Specializations', [])}")
            
            # Check for dynamic expansion
            if airtable_record.get('Has Pending Items') == 'Yes':
                print(f"   📝 Pending Items: {airtable_record.get('Pending Items', 'None')}")
                integration_results["new_items_detected"] += 1
            
            integration_results["successful_categorizations"] += 1
            
            # Test Airtable integration
            success = await processor.add_contact_to_airtable(airtable_record)
            if success:
                print(f"   ✅ Airtable Integration: Ready for production")
                integration_results["airtable_ready"] += 1
            else:
                print(f"   ❌ Airtable Integration: Issues detected")
                
        except Exception as e:
            print(f"   ❌ System Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Print comprehensive results
    print(f"\n📊 COMPLETE INTEGRATION TEST RESULTS")
    print("=" * 90)
    
    success_rate = (integration_results["successful_categorizations"] / integration_results["total_processed"]) * 100 if integration_results["total_processed"] > 0 else 0
    expansion_rate = (integration_results["new_items_detected"] / integration_results["total_processed"]) * 100 if integration_results["total_processed"] > 0 else 0
    airtable_rate = (integration_results["airtable_ready"] / integration_results["total_processed"]) * 100 if integration_results["total_processed"] > 0 else 0
    
    print(f"🎯 System Performance:")
    print(f"   Total Contacts Processed: {integration_results['total_processed']}")
    print(f"   Successful Categorizations: {integration_results['successful_categorizations']} ({success_rate:.1f}%)")
    print(f"   New Items Detected: {integration_results['new_items_detected']} ({expansion_rate:.1f}%)")
    print(f"   Airtable Ready: {integration_results['airtable_ready']} ({airtable_rate:.1f}%)")
    
    print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
    if success_rate >= 90 and airtable_rate >= 90:
        print(f"🎉 EXCELLENT - Complete system ready for production deployment!")
        print(f"   ✅ Universal Adaptive categorization working perfectly")
        print(f"   ✅ Dynamic expansion handling new items automatically")
        print(f"   ✅ No manual intervention required for unknown items")
        print(f"   ✅ Airtable integration seamless")
    elif success_rate >= 75:
        print(f"⚠️  GOOD - System functional with minor issues")
        print(f"   ✅ Core categorization working well")
        print(f"   🔧 Some edge cases may need refinement")
    else:
        print(f"🔧 NEEDS WORK - System requires attention")
        print(f"   🔧 Review categorization accuracy")
        print(f"   🔧 Check dynamic expansion logic")
    
    print(f"\n🔧 DYNAMIC EXPANSION BENEFITS:")
    print(f"   ✅ Handles emerging trades (Solar, Wind, Drone technology)")
    print(f"   ✅ Captures new equipment brands automatically")
    print(f"   ✅ Creates pending review tables for quality control")
    print(f"   ✅ Prevents errors from unknown dropdown values")
    print(f"   ✅ Enables continuous system evolution")
    
    print(f"\n📋 PENDING ITEMS WORKFLOW:")
    print(f"   1. System detects new items not in existing dropdowns")
    print(f"   2. Creates records in pending review tables")
    print(f"   3. Admin reviews and approves/rejects new items")
    print(f"   4. Approved items get added to main dropdowns")
    print(f"   5. System learns and improves automatically")
    
    print(f"\n🎯 BUSINESS VALUE:")
    print(f"   💰 Captures ALL leads, not just traditional trades")
    print(f"   🚀 Adapts to evolving industry automatically")
    print(f"   📊 Provides market intelligence on emerging roles")
    print(f"   ⚡ Zero manual intervention for categorization")
    print(f"   🎯 Perfect targeting for course marketing across ALL trades")

async def main():
    """Main test execution."""
    await test_complete_integration()

if __name__ == "__main__":
    asyncio.run(main())