#!/usr/bin/env python3
"""
SignalHire Candidate Extraction Script

This script demonstrates how to use the SignalHire API to:
1. Search for candidates 
2. Extract their information
3. Export to CSV format for Google Drive upload

Usage:
    python3 scripts/extract_candidates_to_csv.py

Prerequisites:
    - Set SIGNALHIRE_API_KEY environment variable
    - Or create .env file with SIGNALHIRE_API_KEY=your_key_here

The script will:
- Search for candidates based on your criteria
- Extract available contact information
- Create a CSV file ready for Google Drive upload
- Show credit usage summary
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from dotenv import load_dotenv

from services.signalhire_client import SignalHireClient

# Load environment variables
load_dotenv()


class CandidateExtractor:
    """Extract candidates from SignalHire and prepare for Google Drive upload."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.client = SignalHireClient(api_key=api_key)
        self.results = {
            "search_results": [],
            "revealed_contacts": [],
            "credits_used": 0,
            "credits_remaining": None
        }
        
    async def check_credits(self) -> dict:
        """Check available credits before starting."""
        print("🔍 Checking available credits...")
        
        response = await self.client.check_credits()
        
        if response.success:
            credits_data = response.data
            print(f"✅ Credits check successful")
            print(f"   Available credits: {credits_data.get('availableCredits', 'Unknown')}")
            print(f"   Daily limit: {credits_data.get('dailyLimit', 'Unknown')}")
            return credits_data
        else:
            print(f"❌ Credits check failed: {response.error}")
            return {}
    
    async def search_candidates(self, search_criteria: dict, limit: int = 50) -> list:
        """Search for candidates using SignalHire API."""
        print(f"🔍 Searching for candidates...")
        print(f"   Criteria: {search_criteria}")
        print(f"   Limit: {limit}")
        
        response = await self.client.search_prospects(search_criteria, size=limit)
        
        if response.success:
            profiles = response.data.get("profiles", [])
            total_results = response.data.get("totalResults", len(profiles))
            
            print(f"✅ Search successful!")
            print(f"   Found: {len(profiles)} profiles")
            print(f"   Total available: {total_results}")
            print(f"   Credits used: {response.credits_used}")
            
            self.results["search_results"] = profiles
            self.results["credits_used"] += response.credits_used
            self.results["credits_remaining"] = response.credits_remaining
            
            return profiles
        else:
            print(f"❌ Search failed: {response.error}")
            return []
    
    async def reveal_contacts(self, profiles: list, callback_url: str = None) -> list:
        """Reveal contact information for profiles."""
        if not profiles:
            print("⚠️  No profiles to reveal contacts for")
            return []
            
        print(f"📞 Attempting to reveal contacts for {len(profiles)} profiles...")
        
        # Extract identifiers (LinkedIn URLs or UIDs)
        identifiers = []
        for profile in profiles:
            if "linkedinUrl" in profile and profile["linkedinUrl"]:
                identifiers.append(profile["linkedinUrl"])
            elif "uid" in profile:
                identifiers.append(profile["uid"])
                
        if not identifiers:
            print("⚠️  No valid identifiers found for contact reveal")
            return profiles
            
        # For testing, we'll only try to reveal a few to save credits
        test_identifiers = identifiers[:3]  # Only reveal first 3 to save credits
        
        print(f"   Using {len(test_identifiers)} identifiers (saving credits)")
        
        if not callback_url:
            callback_url = "http://localhost:8000/callback"  # Default test URL
            
        response = await self.client.reveal_contacts(test_identifiers, callback_url)
        
        if response.success:
            print(f"✅ Contact reveal request submitted")
            print(f"   Request ID: {response.data.get('requestId', 'Unknown')}")
            print(f"   Credits used: {response.credits_used}")
            
            self.results["credits_used"] += response.credits_used
            self.results["credits_remaining"] = response.credits_remaining
            
            # In a real scenario, contacts would come via callback
            # For testing, we'll add mock contact data to demonstrate
            enhanced_profiles = self._add_mock_contact_data(profiles[:3])
            self.results["revealed_contacts"] = enhanced_profiles
            
            return enhanced_profiles
        else:
            print(f"❌ Contact reveal failed: {response.error}")
            return profiles
    
    def _add_mock_contact_data(self, profiles: list) -> list:
        """Add mock contact data for demonstration."""
        enhanced = []
        for i, profile in enumerate(profiles):
            enhanced_profile = profile.copy()
            # Add mock contact data (in real scenario, this comes from callback)
            enhanced_profile.update({
                "email_work": f"contact{i+1}@{enhanced_profile.get('currentCompany', 'company').lower().replace(' ', '')}.com",
                "phone_work": f"+1-555-{1000 + i:04d}",
                "contact_revealed": True,
                "reveal_timestamp": datetime.now().isoformat()
            })
            enhanced.append(enhanced_profile)
        return enhanced
    
    def export_to_csv(self, profiles: list, output_file: str = None) -> str:
        """Export profiles to CSV format optimized for Google Drive."""
        if not profiles:
            print("⚠️  No profiles to export")
            return ""
            
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"signalhire_candidates_{timestamp}.csv"
            
        print(f"📋 Exporting {len(profiles)} profiles to CSV...")
        
        # Convert to DataFrame
        df = pd.DataFrame(profiles)
        
        # Rename columns for Google Sheets compatibility
        column_mapping = {
            "fullName": "Full Name",
            "currentTitle": "Current Title", 
            "currentCompany": "Current Company",
            "location": "Location",
            "linkedinUrl": "LinkedIn Profile",
            "email_work": "Work Email",
            "phone_work": "Work Phone",
            "uid": "SignalHire ID"
        }
        
        # Only rename columns that exist
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)
        
        # Add metadata columns
        df["Export Date"] = datetime.now().strftime("%Y-%m-%d")
        df["Source"] = "SignalHire Agent"
        df["Credits Used"] = self.results["credits_used"]
        df["Status"] = "New Lead"
        df["Notes"] = ""  # Empty for user notes
        df["Next Action"] = ""  # Empty for user action items
        
        # Reorder columns for better readability
        priority_columns = ["Full Name", "Current Title", "Current Company", "Location", "Work Email", "Work Phone"]
        other_columns = [col for col in df.columns if col not in priority_columns]
        ordered_columns = [col for col in priority_columns if col in df.columns] + other_columns
        df = df[ordered_columns]
        
        # Export to CSV
        df.to_csv(output_file, index=False)
        
        # Validate export
        file_size_kb = Path(output_file).stat().st_size / 1024
        
        print(f"✅ Export successful!")
        print(f"   File: {output_file}")
        print(f"   Records: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Size: {file_size_kb:.1f}KB")
        
        return output_file
    
    def generate_summary_report(self, csv_file: str = None):
        """Generate a summary report of the extraction process."""
        print(f"\n📊 Extraction Summary Report")
        print(f"=" * 50)
        print(f"Search Results: {len(self.results['search_results'])}")
        print(f"Contact Reveals: {len(self.results['revealed_contacts'])}")
        print(f"Credits Used: {self.results['credits_used']}")
        print(f"Credits Remaining: {self.results['credits_remaining']}")
        
        if csv_file and Path(csv_file).exists():
            df = pd.read_csv(csv_file)
            print(f"CSV Records: {len(df)}")
            print(f"CSV Columns: {df.columns.tolist()}")
            print(f"CSV File: {csv_file}")
            
            # Google Drive upload instructions
            print(f"\n📤 Google Drive Upload Instructions:")
            print(f"1. Go to drive.google.com")
            print(f"2. Click 'New' > 'File upload'")
            print(f"3. Select {Path(csv_file).name}")
            print(f"4. Right-click uploaded file > 'Open with' > 'Google Sheets'")
            print(f"5. File will convert to Google Sheets format automatically")
            
            # Sample data preview
            if len(df) > 0:
                print(f"\n👀 Sample Data Preview:")
                for i, row in df.head(2).iterrows():
                    name = row.get("Full Name", "Unknown")
                    title = row.get("Current Title", "Unknown")
                    company = row.get("Current Company", "Unknown")
                    print(f"   {i+1}. {name} - {title} at {company}")


async def main():
    """Main extraction workflow."""
    print("🚀 SignalHire Candidate Extraction Tool")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("SIGNALHIRE_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        print("   Set SIGNALHIRE_API_KEY environment variable")
        print("   Or create .env file with SIGNALHIRE_API_KEY=your_key")
        return
    
    # Initialize extractor
    extractor = CandidateExtractor(api_key)
    
    try:
        # Step 1: Check credits
        credits_info = await extractor.check_credits()
        
        # Step 2: Define search criteria - Heavy Equipment in Canada
        search_criteria = {
            "currentTitle": '"Heavy Equipment Technician" OR "Heavy Duty Technician" OR "Heavy Equipment Mechanic" OR "Heavy Duty Mechanic" OR "Diesel Mechanic" OR "Equipment Technician" OR "Construction Equipment Technician" OR "Mining Equipment Technician" OR "Heavy Machinery Technician" OR "Heavy Machinery Mechanic" OR "Equipment Mechanic" OR "Industrial Mechanic"',
            "location": "Canada",
            "exclude": "NOT driver NOT operator NOT sales NOT coordinator NOT supervisor"
        }
        
        # Ask user for confirmation
        print(f"\n⚠️  About to search with criteria: {search_criteria}")
        print(f"   This will use approximately 25-50 credits for search")
        
        # For automated testing, we'll proceed. In interactive mode, you might want:
        # confirm = input("Continue? (y/N): ")
        # if confirm.lower() != 'y':
        #     print("Cancelled by user")
        #     return
        
        # Step 3: Search for candidates  
        profiles = await extractor.search_candidates(search_criteria, limit=10)
        
        if not profiles:
            print("❌ No candidates found. Try different search criteria.")
            return
        
        # Step 4: Export to CSV (without revealing contacts to save credits)
        print(f"\n📋 Exporting search results to CSV...")
        csv_file = extractor.export_to_csv(profiles)
        
        # Step 5: Optional - reveal contacts for a few profiles (costs credits!)
        # Uncomment the next lines if you want to test contact reveal
        # print(f"\n📞 Revealing contacts for sample profiles...")
        # revealed_profiles = await extractor.reveal_contacts(profiles[:3])
        # if revealed_profiles:
        #     csv_with_contacts = extractor.export_to_csv(revealed_profiles, "candidates_with_contacts.csv")
        
        # Step 6: Generate summary
        extractor.generate_summary_report(csv_file)
        
        print(f"\n✅ Extraction complete! Check {csv_file} for results.")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the extraction
    asyncio.run(main())