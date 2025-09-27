"""
End-to-End Workflow Tests for SignalHire Agent

This test suite simulates complete user workflows:
1. Search -> Reveal -> Export workflow 
2. Credit monitoring throughout the process
3. Error handling and recovery
4. Real file I/O and data persistence

Run with real API key to test against live API:
    SIGNALHIRE_API_KEY=your_key python3 run.py -m pytest tests/backend/integration/test_end_to_end_workflow.py -v

Run without API key for offline testing:
    python3 run.py -m pytest tests/backend/integration/test_end_to_end_workflow.py -v
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import pandas as pd

from src.services.signalhire_client import SignalHireClient, APIResponse
from src.services.csv_exporter import CSVExporter
from src.lib.callback_server import CallbackServer
from src.services.progress_service import ProgressService


pytestmark = pytest.mark.integration


class TestCompleteUserWorkflows:
    """Test complete user workflows from start to finish."""

    @pytest.fixture
    def api_key(self):
        """Get API key or use test key."""
        return os.getenv("SIGNALHIRE_API_KEY", "test_api_key_workflow")

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for workflow tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Create subdirectories
            (workspace / "searches").mkdir()
            (workspace / "reveals").mkdir() 
            (workspace / "exports").mkdir()
            (workspace / "logs").mkdir()
            
            yield workspace

    @pytest.fixture
    def sample_search_results(self):
        """Sample search results for testing."""
        return {
            "profiles": [
                {
                    "uid": "engineer_001",
                    "fullName": "Alice Johnson",
                    "currentTitle": "Senior Software Engineer", 
                    "currentCompany": "TechStartup Inc",
                    "location": "San Francisco, CA, United States",
                    "linkedinUrl": "https://linkedin.com/in/alice-johnson-tech",
                    "contactStatus": "available",
                    "experience": [
                        {
                            "title": "Senior Software Engineer",
                            "company": "TechStartup Inc", 
                            "startDate": "2022-01",
                            "current": True
                        },
                        {
                            "title": "Software Engineer",
                            "company": "BigTech Corp",
                            "startDate": "2020-01",
                            "endDate": "2021-12"
                        }
                    ],
                    "skills": ["Python", "React", "AWS", "Docker"]
                },
                {
                    "uid": "engineer_002", 
                    "fullName": "Bob Chen",
                    "currentTitle": "Full Stack Developer",
                    "currentCompany": "InnovateNow LLC",
                    "location": "Austin, TX, United States", 
                    "linkedinUrl": "https://linkedin.com/in/bob-chen-dev",
                    "contactStatus": "available",
                    "experience": [
                        {
                            "title": "Full Stack Developer",
                            "company": "InnovateNow LLC",
                            "startDate": "2021-06",
                            "current": True
                        }
                    ],
                    "skills": ["JavaScript", "Node.js", "MongoDB", "Vue.js"]
                },
                {
                    "uid": "engineer_003",
                    "fullName": "Carol Davis", 
                    "currentTitle": "DevOps Engineer",
                    "currentCompany": "CloudFirst Solutions",
                    "location": "Seattle, WA, United States",
                    "linkedinUrl": "https://linkedin.com/in/carol-davis-devops",
                    "contactStatus": "available", 
                    "experience": [
                        {
                            "title": "DevOps Engineer",
                            "company": "CloudFirst Solutions",
                            "startDate": "2021-09",
                            "current": True
                        }
                    ],
                    "skills": ["Kubernetes", "Jenkins", "Terraform", "AWS"]
                }
            ],
            "totalResults": 3,
            "scrollId": "workflow_test_scroll_123"
        }

    @pytest.fixture
    def sample_revealed_contacts(self):
        """Sample revealed contact information."""
        return [
            {
                "uid": "engineer_001",
                "fullName": "Alice Johnson",
                "currentTitle": "Senior Software Engineer",
                "currentCompany": "TechStartup Inc", 
                "location": "San Francisco, CA, United States",
                "linkedinUrl": "https://linkedin.com/in/alice-johnson-tech",
                "email_work": "alice.johnson@techstartup.com",
                "email_personal": "alice.j.dev@gmail.com",
                "phone_work": "+1-415-555-0123",
                "phone_mobile": "+1-415-555-0124"
            },
            {
                "uid": "engineer_002",
                "fullName": "Bob Chen", 
                "currentTitle": "Full Stack Developer",
                "currentCompany": "InnovateNow LLC",
                "location": "Austin, TX, United States",
                "linkedinUrl": "https://linkedin.com/in/bob-chen-dev",
                "email_work": "bob.chen@innovatenow.com",
                "phone_work": "+1-512-555-0456"
            },
            {
                "uid": "engineer_003",
                "fullName": "Carol Davis",
                "currentTitle": "DevOps Engineer", 
                "currentCompany": "CloudFirst Solutions",
                "location": "Seattle, WA, United States",
                "linkedinUrl": "https://linkedin.com/in/carol-davis-devops",
                "email_work": "carol.davis@cloudfirst.com",
                "email_personal": "carol.devops@outlook.com",
                "phone_work": "+1-206-555-0789"
            }
        ]

    @pytest.mark.asyncio
    async def test_search_to_export_workflow(self, api_key, temp_workspace, sample_search_results):
        """Test complete search to export workflow."""
        client = SignalHireClient(api_key=api_key)
        
        # Step 1: Search for prospects
        search_criteria = {
            "currentTitle": "Software Engineer",
            "location": "United States", 
            "keywords": "Python OR React"
        }
        
        if api_key == "test_api_key_workflow":
            # Mock search response
            search_response = APIResponse(
                success=True,
                status_code=200,
                data=sample_search_results,
                credits_used=3,
                credits_remaining=4997
            )
            with patch.object(client, 'search_prospects', return_value=search_response):
                response = await client.search_prospects(search_criteria, size=25)
        else:
            # Real API call
            response = await client.search_prospects(search_criteria, size=25)
        
        assert response.success is True
        profiles = response.data.get("profiles", [])
        
        # Step 2: Save search results
        search_file = temp_workspace / "searches" / "software_engineers.json"
        with open(search_file, 'w') as f:
            json.dump(response.data, f, indent=2)
        
        assert search_file.exists()
        print(f"✅ Step 1: Saved {len(profiles)} profiles to {search_file}")
        
        # Step 3: Export to CSV
        csv_file = temp_workspace / "exports" / "software_engineers.csv"
        exporter = CSVExporter()
        exporter.export_to_csv(profiles, str(csv_file))
        
        assert csv_file.exists()
        
        # Step 4: Validate CSV content
        df = pd.read_csv(csv_file)
        assert len(df) == len(profiles)
        
        if len(df) > 0:
            # Check essential columns exist
            essential_cols = ["fullName", "currentTitle", "uid"]
            available_cols = df.columns.tolist()
            
            found_cols = [col for col in essential_cols if col in available_cols]
            assert len(found_cols) >= 2, f"Missing essential columns. Found: {found_cols}"
            
            print(f"✅ Step 2: Exported {len(df)} profiles to CSV with columns: {available_cols}")
        
        # Step 5: Generate summary report
        summary_file = temp_workspace / "logs" / "workflow_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Search Workflow Summary\n")
            f.write(f"======================\n")
            f.write(f"Search Criteria: {search_criteria}\n")
            f.write(f"Profiles Found: {len(profiles)}\n")
            f.write(f"CSV File: {csv_file}\n")
            f.write(f"Credits Used: {response.credits_used}\n")
            f.write(f"Credits Remaining: {response.credits_remaining}\n")
        
        assert summary_file.exists()
        print(f"✅ Step 3: Generated summary report at {summary_file}")

    @pytest.mark.asyncio
    async def test_reveal_to_export_workflow(self, api_key, temp_workspace, sample_search_results, sample_revealed_contacts):
        """Test reveal contacts to export workflow."""
        client = SignalHireClient(api_key=api_key)
        
        # Step 1: Start with search results
        search_data = sample_search_results
        profiles = search_data["profiles"]
        
        # Step 2: Extract identifiers for reveal
        identifiers = []
        for profile in profiles:
            if "linkedinUrl" in profile:
                identifiers.append(profile["linkedinUrl"])
            elif "uid" in profile:
                identifiers.append(profile["uid"])
        
        assert len(identifiers) > 0, "No identifiers found for reveal"
        
        # Step 3: Reveal contacts (mocked or real)
        callback_url = "http://localhost:8000/callback"
        
        if api_key == "test_api_key_workflow":
            # Mock reveal response
            reveal_response = APIResponse(
                success=True, 
                status_code=200,
                data={
                    "requestId": "reveal_workflow_123",
                    "status": "processing", 
                    "identifiers": identifiers,
                    "callbackUrl": callback_url
                },
                credits_used=len(identifiers),
                credits_remaining=5000 - len(identifiers)
            )
            
            with patch.object(client, 'reveal_contacts', return_value=reveal_response):
                response = await client.reveal_contacts(identifiers, callback_url)
        else:
            # Real API call - be careful with credits!
            response = await client.reveal_contacts(identifiers[:1], callback_url)  # Only test 1 to save credits
        
        assert response.success is True
        print(f"✅ Step 1: Submitted reveal request for {len(identifiers)} contacts")
        
        # Step 4: Simulate received revealed contacts (in real workflow, these come via callback)
        revealed_data = sample_revealed_contacts
        
        # Step 5: Export revealed contacts to CSV
        csv_file = temp_workspace / "exports" / "revealed_contacts.csv"
        exporter = CSVExporter()
        exporter.export_to_csv(revealed_data, str(csv_file))
        
        assert csv_file.exists()
        
        # Step 6: Validate CSV content
        df = pd.read_csv(csv_file)
        assert len(df) == len(revealed_data)
        
        # Check for contact information columns
        contact_cols = ["email_work", "phone_work", "email_personal", "phone_mobile"]
        available_cols = df.columns.tolist()
        
        found_contact_cols = [col for col in contact_cols if col in available_cols]
        assert len(found_contact_cols) >= 1, f"No contact columns found. Available: {available_cols}"
        
        print(f"✅ Step 2: Exported revealed contacts with contact fields: {found_contact_cols}")
        
        # Step 7: Generate contact summary
        summary_file = temp_workspace / "logs" / "reveal_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Contact Reveal Summary\n")
            f.write(f"====================\n")
            f.write(f"Contacts Requested: {len(identifiers)}\n")
            f.write(f"Contacts Received: {len(revealed_data)}\n")
            f.write(f"CSV File: {csv_file}\n")
            f.write(f"Contact Fields: {found_contact_cols}\n")
            
            # Contact statistics
            if len(df) > 0:
                email_count = df['email_work'].notna().sum() if 'email_work' in df.columns else 0
                phone_count = df['phone_work'].notna().sum() if 'phone_work' in df.columns else 0
                f.write(f"Work Emails Found: {email_count}\n")
                f.write(f"Work Phones Found: {phone_count}\n")
        
        assert summary_file.exists()
        print(f"✅ Step 3: Generated reveal summary report")

    @pytest.mark.asyncio
    async def test_credit_monitoring_workflow(self, api_key, temp_workspace):
        """Test credit monitoring throughout workflow."""
        client = SignalHireClient(api_key=api_key)
        
        # Step 1: Check initial credits
        if api_key == "test_api_key_workflow":
            initial_credits_response = APIResponse(
                success=True,
                status_code=200,
                data={
                    "availableCredits": 5000,
                    "usedCredits": 0,
                    "dailyLimit": 5000,
                    "resetTime": "2025-09-28T00:00:00Z"
                }
            )
            with patch.object(client, 'check_credits', return_value=initial_credits_response):
                initial_response = await client.check_credits()
        else:
            initial_response = await client.check_credits()
        
        assert initial_response.success is True
        initial_data = initial_response.data
        
        print(f"✅ Initial Credits Check: {initial_data}")
        
        # Step 2: Simulate some API usage
        usage_log = []
        
        # Mock search operation
        search_credits_used = 10
        usage_log.append({"operation": "search", "credits_used": search_credits_used})
        
        # Mock reveal operations
        reveal_credits_used = 5
        usage_log.append({"operation": "reveal", "credits_used": reveal_credits_used})
        
        # Step 3: Check credits after usage
        if api_key == "test_api_key_workflow":
            # Calculate remaining credits
            initial_available = initial_data.get("availableCredits", 5000)
            total_used = sum(entry["credits_used"] for entry in usage_log)
            remaining = initial_available - total_used
            
            final_credits_response = APIResponse(
                success=True,
                status_code=200,
                data={
                    "availableCredits": remaining,
                    "usedCredits": total_used,
                    "dailyLimit": 5000,
                    "resetTime": "2025-09-28T00:00:00Z"
                }
            )
            with patch.object(client, 'check_credits', return_value=final_credits_response):
                final_response = await client.check_credits()
        else:
            final_response = await client.check_credits()
        
        assert final_response.success is True
        final_data = final_response.data
        
        # Step 4: Generate usage report
        report_file = temp_workspace / "logs" / "credit_usage_report.txt"
        with open(report_file, 'w') as f:
            f.write(f"Credit Usage Report\n")
            f.write(f"==================\n")
            f.write(f"Initial Credits: {initial_data}\n")
            f.write(f"Final Credits: {final_data}\n")
            f.write(f"\nUsage Log:\n")
            for entry in usage_log:
                f.write(f"  {entry['operation']}: {entry['credits_used']} credits\n")
            
            total_used = sum(entry["credits_used"] for entry in usage_log)
            f.write(f"\nTotal Credits Used: {total_used}\n")
        
        assert report_file.exists()
        print(f"✅ Credit monitoring report generated: {report_file}")

    def test_error_handling_workflow(self, temp_workspace):
        """Test error handling in workflows.""" 
        # Test file handling errors
        invalid_file = temp_workspace / "nonexistent" / "invalid.json"
        
        # Test graceful handling of missing directories
        try:
            with open(invalid_file, 'w') as f:
                json.dump({"test": "data"}, f)
            assert False, "Should have failed due to missing directory"
        except FileNotFoundError:
            print("✅ Correctly handles missing directory error")
        
        # Test CSV export with invalid data
        exporter = CSVExporter()
        invalid_data = [
            {"name": "Test", "value": 123},
            {"name": "Test2", "different_field": "data"}  # Inconsistent structure
        ]
        
        csv_file = temp_workspace / "exports" / "error_test.csv"
        
        try:
            exporter.export_to_csv(invalid_data, str(csv_file))
            # Should handle inconsistent data gracefully
            if csv_file.exists():
                df = pd.read_csv(csv_file)
                print(f"✅ Handled inconsistent data: {len(df)} rows, {df.columns.tolist()}")
        except Exception as e:
            print(f"✅ Error handling test: {e}")

    @pytest.mark.asyncio
    async def test_large_dataset_workflow(self, api_key, temp_workspace):
        """Test workflow with larger datasets."""
        # Generate large mock dataset
        large_profiles = []
        for i in range(500):
            large_profiles.append({
                "uid": f"bulk_{i:03d}",
                "fullName": f"Professional {i}",
                "currentTitle": f"Engineer {i % 10}",
                "currentCompany": f"Company {i % 50}",
                "location": f"City {i % 20}, State, Country",
                "linkedinUrl": f"https://linkedin.com/in/professional{i}"
            })
        
        # Test CSV export performance
        start_time = time.time()
        
        csv_file = temp_workspace / "exports" / "large_dataset.csv"
        exporter = CSVExporter()
        exporter.export_to_csv(large_profiles, str(csv_file))
        
        export_time = time.time() - start_time
        
        # Validate export
        assert csv_file.exists()
        df = pd.read_csv(csv_file)
        assert len(df) == 500
        
        # Performance check
        assert export_time < 10, f"Export took too long: {export_time:.2f}s"
        
        file_size_mb = csv_file.stat().st_size / (1024 * 1024)
        assert file_size_mb < 5, f"File too large: {file_size_mb:.2f}MB"
        
        print(f"✅ Large dataset test: 500 records in {export_time:.2f}s, {file_size_mb:.2f}MB")

    def test_file_format_compatibility(self, temp_workspace, sample_revealed_contacts):
        """Test compatibility with different file formats."""
        exporter = CSVExporter()
        data = sample_revealed_contacts
        
        # Test CSV export
        csv_file = temp_workspace / "exports" / "test.csv"
        exporter.export_to_csv(data, str(csv_file))
        assert csv_file.exists()
        
        # Verify CSV can be read back
        df_csv = pd.read_csv(csv_file)
        assert len(df_csv) == len(data)
        
        # Test Excel export (if supported)
        excel_file = temp_workspace / "exports" / "test.xlsx"
        try:
            df_csv.to_excel(excel_file, index=False)
            if excel_file.exists():
                df_excel = pd.read_excel(excel_file)
                assert len(df_excel) == len(data)
                print(f"✅ Excel format supported")
        except Exception as e:
            print(f"Excel format not available: {e}")
        
        # Test JSON export
        json_file = temp_workspace / "exports" / "test.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        assert json_file.exists()
        
        # Verify JSON can be read back
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        assert len(json_data) == len(data)
        print(f"✅ File format compatibility test completed")


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.fixture
    def realistic_search_scenarios(self):
        """Realistic search scenarios users might run."""
        return [
            {
                "name": "Software Engineers in Bay Area",
                "criteria": {
                    "currentTitle": "Software Engineer", 
                    "location": "San Francisco Bay Area",
                    "keywords": "Python OR JavaScript"
                },
                "expected_size": 25
            },
            {
                "name": "Product Managers in Tech",
                "criteria": {
                    "currentTitle": "Product Manager",
                    "company": "Tech OR Technology",
                    "location": "United States"
                },
                "expected_size": 50
            },
            {
                "name": "DevOps Engineers Remote",
                "criteria": {
                    "currentTitle": "DevOps Engineer",
                    "keywords": "AWS OR Azure OR Kubernetes", 
                    "location": "Remote"
                },
                "expected_size": 30
            }
        ]

    @pytest.mark.asyncio
    async def test_realistic_search_scenarios(self, realistic_search_scenarios, temp_workspace):
        """Test realistic search scenarios."""
        api_key = os.getenv("SIGNALHIRE_API_KEY", "test_scenario_key")
        client = SignalHireClient(api_key=api_key)
        
        results_summary = []
        
        for scenario in realistic_search_scenarios:
            scenario_name = scenario["name"]
            criteria = scenario["criteria"]
            expected_size = scenario["expected_size"]
            
            print(f"\n🔍 Testing scenario: {scenario_name}")
            
            if api_key == "test_scenario_key":
                # Mock response for testing
                mock_profiles = [
                    {
                        "uid": f"scenario_{i}",
                        "fullName": f"Professional {i}",
                        "currentTitle": criteria.get("currentTitle", "Engineer"),
                        "currentCompany": "Test Company",
                        "location": criteria.get("location", "Test Location")
                    }
                    for i in range(min(expected_size, 10))  # Limit to 10 for testing
                ]
                
                response = APIResponse(
                    success=True,
                    status_code=200,
                    data={"profiles": mock_profiles, "totalResults": len(mock_profiles)},
                    credits_used=len(mock_profiles),
                    credits_remaining=5000 - len(mock_profiles)
                )
                
                with patch.object(client, 'search_prospects', return_value=response):
                    result = await client.search_prospects(criteria, size=expected_size)
            else:
                # Real API call
                result = await client.search_prospects(criteria, size=expected_size)
            
            # Record results
            scenario_result = {
                "scenario": scenario_name,
                "success": result.success,
                "profiles_found": len(result.data.get("profiles", [])) if result.data else 0,
                "credits_used": result.credits_used,
                "total_available": result.data.get("totalResults", 0) if result.data else 0
            }
            
            results_summary.append(scenario_result)
            
            # Save scenario results
            scenario_file = temp_workspace / "searches" / f"{scenario_name.lower().replace(' ', '_')}.json"
            scenario_file.parent.mkdir(exist_ok=True)
            
            with open(scenario_file, 'w') as f:
                json.dump({
                    "scenario": scenario_name,
                    "criteria": criteria,
                    "result": result.data if result.success else {"error": result.error}
                }, f, indent=2)
            
            print(f"  ✅ Found {scenario_result['profiles_found']} profiles")
        
        # Generate summary report
        summary_file = temp_workspace / "logs" / "scenario_summary.txt"
        summary_file.parent.mkdir(exist_ok=True)
        
        with open(summary_file, 'w') as f:
            f.write("Realistic Search Scenarios Summary\n")
            f.write("==================================\n\n")
            
            total_profiles = sum(r["profiles_found"] for r in results_summary)
            total_credits = sum(r["credits_used"] for r in results_summary)
            
            f.write(f"Total Scenarios Tested: {len(results_summary)}\n")
            f.write(f"Total Profiles Found: {total_profiles}\n") 
            f.write(f"Total Credits Used: {total_credits}\n\n")
            
            for result in results_summary:
                f.write(f"Scenario: {result['scenario']}\n")
                f.write(f"  Success: {result['success']}\n")
                f.write(f"  Profiles: {result['profiles_found']}\n")
                f.write(f"  Credits: {result['credits_used']}\n")
                f.write(f"  Total Available: {result['total_available']}\n\n")
        
        print(f"\n✅ Realistic scenarios test completed. Summary: {summary_file}")
        assert len(results_summary) == len(realistic_search_scenarios)
        assert all(r["success"] for r in results_summary)

    def test_csv_upload_to_google_drive_preparation(self, temp_workspace, sample_revealed_contacts):
        """Test preparing CSV for Google Drive upload."""
        # This test prepares CSV in optimal format for Google Drive upload
        exporter = CSVExporter()
        
        # Add timestamp and clean data for Google Sheets compatibility
        processed_data = []
        for contact in sample_revealed_contacts:
            clean_contact = {}
            for key, value in contact.items():
                # Clean up field names for Google Sheets
                clean_key = key.replace("_", " ").title()
                # Handle None values
                clean_value = value if value is not None else ""
                # Handle phone number formatting
                if "phone" in key.lower() and value:
                    clean_value = str(value).replace("+1-", "").replace("-", "")
                clean_contact[clean_key] = clean_value
            
            # Add metadata
            clean_contact["Export Date"] = "2025-09-27"
            clean_contact["Source"] = "SignalHire Agent"
            
            processed_data.append(clean_contact)
        
        # Export with Google Drive friendly filename
        timestamp = "20250927_120000"
        csv_file = temp_workspace / "exports" / f"signalhire_contacts_{timestamp}.csv"
        
        exporter.export_to_csv(processed_data, str(csv_file))
        
        # Validate Google Drive ready format
        assert csv_file.exists()
        df = pd.read_csv(csv_file)
        
        # Check Google Sheets friendly columns
        assert "Full Name" in df.columns
        assert "Current Title" in df.columns
        assert "Email Work" in df.columns
        assert "Export Date" in df.columns
        assert "Source" in df.columns
        
        # Check file size is reasonable for Google Drive
        file_size_kb = csv_file.stat().st_size / 1024
        assert file_size_kb < 1024, f"File too large for easy Google Drive upload: {file_size_kb:.1f}KB"
        
        print(f"✅ Google Drive ready CSV: {csv_file.name} ({file_size_kb:.1f}KB)")
        print(f"   Columns: {df.columns.tolist()}")
        print(f"   Records: {len(df)}")
        
        # Generate upload instructions
        instructions_file = temp_workspace / "logs" / "google_drive_upload_instructions.txt"
        with open(instructions_file, 'w') as f:
            f.write("Google Drive Upload Instructions\n")
            f.write("===============================\n\n")
            f.write(f"File: {csv_file.name}\n")
            f.write(f"Size: {file_size_kb:.1f}KB\n")
            f.write(f"Records: {len(df)}\n\n")
            f.write("Steps:\n")
            f.write("1. Go to drive.google.com\n")
            f.write("2. Click 'New' > 'File upload'\n")
            f.write(f"3. Select {csv_file.name}\n")
            f.write("4. Right-click uploaded file > 'Open with' > 'Google Sheets'\n")
            f.write("5. File will automatically convert to Google Sheets format\n\n")
            f.write("Available columns:\n")
            for col in df.columns:
                f.write(f"  - {col}\n")
        
        print(f"✅ Upload instructions: {instructions_file}")
        return str(csv_file)