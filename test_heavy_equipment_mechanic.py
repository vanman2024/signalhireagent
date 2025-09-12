#!/usr/bin/env python3
"""
Test SignalHire API with Heavy Equipment Mechanic search in Canada.
Uses the correct API format as documented.
"""

import asyncio
from src.services.signalhire_client import SignalHireClient
from src.lib.config import get_config

async def test_heavy_equipment_mechanic_search():
    """Test real Heavy Equipment Mechanic search in Canada."""
    print("🔍 Heavy Equipment Mechanic Search Test - Canada")
    print("=" * 60)
    
    config = get_config()
    api_key = config.signalhire.api_key
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"🔑 Using API Key: {api_key[:10]}...")
    
    # Create client with correct configuration
    client = SignalHireClient(api_key=api_key)
    
    try:
        # First check credits
        print("\n💳 Checking Credits...")
        credits_response = await client.check_credits()
        if credits_response.success:
            credits = credits_response.data.get('credits', 0)
            print(f"   Available Credits: {credits}")
            if credits < 10:
                print("⚠️  Low credits - search may be limited")
        else:
            print(f"❌ Credits check failed: {credits_response.error}")
            return
        
        # Test Heavy Equipment Mechanic search using correct API format
        print("\n🔍 Searching for Heavy Equipment Mechanics in Canada...")
        search_criteria = {
            "currentTitle": "Heavy Equipment Mechanic",
            "location": "Canada",
            # Using Boolean query format as documented
            "keywords": "machinery OR equipment OR hydraulic OR diesel"
        }
        
        print(f"   Search Criteria:")
        print(f"   - Current Title: {search_criteria['currentTitle']}")
        print(f"   - Location: {search_criteria['location']} ")
        print(f"   - Keywords: {search_criteria['keywords']}")
        
        search_response = await client.search_prospects(search_criteria, size=25)
        
        if search_response.success:
            data = search_response.data
            total = data.get('total', 0)
            profiles = data.get('profiles', [])
            request_id = data.get('requestId')
            scroll_id = data.get('scrollId')
            
            print(f"🎉 Search Successful!")
            print(f"   Total Results: {total}")
            print(f"   Profiles in This Batch: {len(profiles)}")
            print(f"   Request ID: {request_id}")
            if scroll_id:
                print(f"   Scroll ID Available: {scroll_id[:20]}...")
            
            # Analyze profile quality
            print(f"\n📊 Profile Analysis:")
            canada_locations = 0
            relevant_titles = 0
            
            for i, profile in enumerate(profiles[:5]):  # Analyze first 5
                full_name = profile.get('fullName', 'Unknown')
                location = profile.get('location', '')
                uid = profile.get('uid', '')
                
                # Check experience for relevant titles
                experience = profile.get('experience', [])
                current_title = ""
                if experience:
                    current_title = experience[0].get('title', '')
                
                # Check location relevance
                if any(keyword in location.lower() for keyword in ['canada', 'ontario', 'alberta', 'british columbia', 'quebec']):
                    canada_locations += 1
                
                # Check title relevance
                title_keywords = ['mechanic', 'technician', 'operator', 'maintenance', 'equipment', 'heavy']
                if any(keyword in current_title.lower() for keyword in title_keywords):
                    relevant_titles += 1
                
                print(f"   {i+1}. {full_name}")
                print(f"      Location: {location}")
                print(f"      Current Title: {current_title}")
                print(f"      UID: {uid}")
                
                # Check for contact fetch status
                contacts_fetched = profile.get('contactsFetched')
                if contacts_fetched:
                    print(f"      Contacts Available: {contacts_fetched}")
                
                print()
            
            # Quality metrics
            analyzed_count = min(len(profiles), 5)
            if analyzed_count > 0:
                canada_rate = (canada_locations / analyzed_count) * 100
                relevance_rate = (relevant_titles / analyzed_count) * 100
                
                print(f"📈 Quality Metrics (first {analyzed_count} profiles):")
                print(f"   Canada Location Accuracy: {canada_rate:.1f}%")
                print(f"   Title Relevance: {relevance_rate:.1f}%")
            
            # Test pagination if available
            if scroll_id:
                print(f"\n🔄 Pagination available - could fetch {total - len(profiles)} more results")
        
        elif search_response.status_code == 402:
            print("💰 Search failed - insufficient credits or quota exceeded")
        elif search_response.status_code == 403:
            print("🔐 Search failed - no access to Search API (contact support@signalhire.com)")
        else:
            print(f"❌ Search failed: {search_response.error}")
            print(f"   Status Code: {search_response.status_code}")
        
    except Exception as e:
        print(f"💥 Error during testing: {e}")
    finally:
        if client.session:
            await client.close_session()

if __name__ == "__main__":
    asyncio.run(test_heavy_equipment_mechanic_search())