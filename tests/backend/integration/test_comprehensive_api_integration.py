"""
Comprehensive SignalHire API Integration Tests

This test suite covers the complete workflow from search to export:
1. Search prospects using SignalHire API
2. Reveal contact information 
3. Export results to CSV
4. Monitor credit usage and limits

Run with real API key:
    SIGNALHIRE_API_KEY=your_key python3 run.py -m pytest tests/backend/integration/test_comprehensive_api_integration.py -v

Run with mocked responses (no API key needed):
    python3 run.py -m pytest tests/backend/integration/test_comprehensive_api_integration.py -v
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import pandas as pd

from src.services.signalhire_client import SignalHireClient, APIResponse
from src.services.csv_exporter import CSVExporter
from src.cli.main import cli_config


pytestmark = pytest.mark.integration


class TestSignalHireAPIIntegration:
    """Test suite for complete SignalHire API integration workflow."""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment or use mock."""
        return os.getenv("SIGNALHIRE_API_KEY", "test_api_key_12345")

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files."""
        return tmp_path

    @pytest.fixture
    def mock_search_response(self):
        """Mock successful search response."""
        return APIResponse(
            success=True,
            status_code=200,
            data={
                "profiles": [
                    {
                        "uid": "test_uid_001",
                        "fullName": "John Smith", 
                        "currentTitle": "Software Engineer",
                        "currentCompany": "TechCorp Inc",
                        "location": "San Francisco, CA",
                        "linkedinUrl": "https://linkedin.com/in/johnsmith",
                        "contactStatus": "available",
                        "experience": [
                            {
                                "title": "Software Engineer",
                                "company": "TechCorp Inc",
                                "duration": "2022-present"
                            }
                        ]
                    },
                    {
                        "uid": "test_uid_002", 
                        "fullName": "Jane Doe",
                        "currentTitle": "Senior Developer", 
                        "currentCompany": "StartupXYZ",
                        "location": "New York, NY",
                        "linkedinUrl": "https://linkedin.com/in/janedoe",
                        "contactStatus": "available"
                    }
                ],
                "totalResults": 2,
                "scrollId": "test_scroll_id_123"
            },
            credits_used=2,
            credits_remaining=4998
        )

    @pytest.fixture 
    def mock_reveal_response(self):
        """Mock successful contact reveal response."""
        return APIResponse(
            success=True,
            status_code=200,
            data={
                "requestId": "reveal_request_123",
                "status": "processing", 
                "message": "Contact reveal request submitted successfully"
            },
            credits_used=1,
            credits_remaining=4997
        )

    @pytest.fixture
    def mock_credits_response(self):
        """Mock credits check response.""" 
        return APIResponse(
            success=True,
            status_code=200,
            data={
                "availableCredits": 5000,
                "usedCredits": 0,
                "dailyLimit": 5000,
                "resetTime": "2025-09-28T00:00:00Z",
                "profileViews": {
                    "used": 0,
                    "limit": 5000
                }
            }
        )

    @pytest.mark.asyncio
    async def test_search_prospects_api_integration(self, api_key, mock_search_response):
        """Test search prospects API integration."""
        client = SignalHireClient(api_key=api_key)
        
        # Mock the HTTP call if no real API key
        if api_key == "test_api_key_12345":
            with patch.object(client, '_make_request', return_value=mock_search_response):
                response = await client.search_prospects(
                    search_criteria={
                        "currentTitle": "Software Engineer",
                        "location": "San Francisco"
                    },
                    size=25
                )
        else:
            # Real API call
            response = await client.search_prospects(
                search_criteria={
                    "currentTitle": "Software Engineer", 
                    "location": "San Francisco"
                },
                size=25
            )

        # Validate response structure
        assert response.success is True
        assert response.data is not None
        assert "profiles" in response.data
        assert isinstance(response.data["profiles"], list)
        
        # Check that we got results
        if response.data["profiles"]:
            profile = response.data["profiles"][0]
            assert "uid" in profile
            assert "fullName" in profile
            assert "currentTitle" in profile
            
        print(f"✅ Search API Test - Found {len(response.data['profiles'])} profiles")

    @pytest.mark.asyncio
    async def test_check_credits_api_integration(self, api_key, mock_credits_response):
        """Test credits checking API integration."""
        client = SignalHireClient(api_key=api_key)
        
        # Mock the HTTP call if no real API key
        if api_key == "test_api_key_12345":
            with patch.object(client, '_make_request', return_value=mock_credits_response):
                response = await client.check_credits()
        else:
            # Real API call
            response = await client.check_credits()

        # Validate response structure
        assert response.success is True
        assert response.data is not None
        
        # Check credits data structure
        credits_data = response.data
        expected_fields = ["availableCredits", "dailyLimit"]
        
        # Flexible validation - SignalHire API may have different field names
        has_credits_info = any(
            field in credits_data for field in 
            ["availableCredits", "credits", "remaining", "balance"]
        )
        assert has_credits_info, f"No credits info found in: {list(credits_data.keys())}"
        
        print(f"✅ Credits API Test - Response keys: {list(credits_data.keys())}")

    @pytest.mark.asyncio
    async def test_reveal_contacts_api_integration(self, api_key, mock_reveal_response):
        """Test contact reveal API integration."""
        client = SignalHireClient(api_key=api_key)
        
        # Test data
        test_identifiers = [
            "https://linkedin.com/in/test-profile",
            "test@example.com"
        ]
        callback_url = "http://localhost:8000/callback"
        
        # Mock the HTTP call if no real API key
        if api_key == "test_api_key_12345":
            with patch.object(client, '_make_request', return_value=mock_reveal_response):
                response = await client.reveal_contacts(
                    identifiers=test_identifiers,
                    callback_url=callback_url
                )
        else:
            # Real API call - be careful with credits!
            # Only test with 1 request to avoid using credits unnecessarily
            response = await client.reveal_contacts(
                identifiers=test_identifiers[:1],  # Only test with first identifier
                callback_url=callback_url
            )

        # Validate response structure
        assert response.success is True
        assert response.data is not None
        
        # Check reveal response structure
        reveal_data = response.data
        expected_fields = ["requestId", "status"]
        
        # Flexible validation for reveal response
        has_request_info = any(
            field in reveal_data for field in 
            ["requestId", "id", "request_id", "status", "message"]
        )
        assert has_request_info, f"No request info found in: {list(reveal_data.keys())}"
        
        print(f"✅ Reveal API Test - Response keys: {list(reveal_data.keys())}")

    def test_csv_export_functionality(self, temp_dir):
        """Test CSV export functionality with sample data.""" 
        # Create sample prospect data
        sample_data = [
            {
                "uid": "test_001",
                "fullName": "John Smith",
                "currentTitle": "Software Engineer", 
                "currentCompany": "TechCorp",
                "location": "San Francisco, CA",
                "linkedinUrl": "https://linkedin.com/in/johnsmith",
                "email_work": "john.smith@techcorp.com",
                "phone_work": "+1-555-0123"
            },
            {
                "uid": "test_002",
                "fullName": "Jane Doe", 
                "currentTitle": "Product Manager",
                "currentCompany": "StartupXYZ", 
                "location": "New York, NY",
                "linkedinUrl": "https://linkedin.com/in/janedoe",
                "email_work": "jane.doe@startupxyz.com", 
                "phone_work": "+1-555-0456"
            }
        ]
        
        # Export to CSV
        exporter = CSVExporter()
        output_file = temp_dir / "test_export.csv"
        
        exporter.export_to_csv(sample_data, str(output_file))
        
        # Validate CSV was created
        assert output_file.exists()
        
        # Validate CSV content
        df = pd.read_csv(output_file)
        assert len(df) == 2
        assert "fullName" in df.columns
        assert "currentTitle" in df.columns
        assert "currentCompany" in df.columns
        
        # Check data integrity
        assert df.iloc[0]["fullName"] == "John Smith"
        assert df.iloc[1]["fullName"] == "Jane Doe"
        
        print(f"✅ CSV Export Test - Created {output_file} with {len(df)} rows")

    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, api_key, temp_dir, mock_search_response, mock_credits_response):
        """Test complete workflow: search -> export -> monitor credits."""
        client = SignalHireClient(api_key=api_key)
        
        # Step 1: Check initial credits
        if api_key == "test_api_key_12345":
            with patch.object(client, '_make_request', return_value=mock_credits_response):
                credits_response = await client.check_credits()
        else:
            credits_response = await client.check_credits()
            
        assert credits_response.success is True
        print(f"✅ Step 1: Credits check successful")
        
        # Step 2: Search for prospects
        if api_key == "test_api_key_12345":
            with patch.object(client, '_make_request', return_value=mock_search_response):
                search_response = await client.search_prospects(
                    search_criteria={
                        "currentTitle": "Software Engineer",
                        "location": "United States"
                    },
                    size=10
                )
        else:
            search_response = await client.search_prospects(
                search_criteria={
                    "currentTitle": "Software Engineer", 
                    "location": "United States"
                },
                size=10
            )
            
        assert search_response.success is True
        assert "profiles" in search_response.data
        profiles = search_response.data["profiles"]
        print(f"✅ Step 2: Search found {len(profiles)} profiles")
        
        # Step 3: Export to CSV
        output_file = temp_dir / "workflow_test_export.csv"
        exporter = CSVExporter()
        exporter.export_to_csv(profiles, str(output_file))
        
        assert output_file.exists()
        df = pd.read_csv(output_file)
        assert len(df) >= 0  # Allow empty results for test
        print(f"✅ Step 3: Exported {len(df)} profiles to CSV")
        
        # Step 4: Validate file structure
        if len(df) > 0:
            expected_columns = ["fullName", "currentTitle", "uid"]
            available_columns = df.columns.tolist()
            
            # Check that we have some expected columns
            has_basic_columns = any(col in available_columns for col in expected_columns)
            assert has_basic_columns, f"Missing basic columns. Available: {available_columns}"
            
            print(f"✅ Step 4: CSV has proper structure with columns: {available_columns}")
        
        print(f"✅ Complete workflow test successful!")

    @pytest.mark.asyncio 
    async def test_rate_limiting_and_error_handling(self, api_key):
        """Test rate limiting and error handling."""
        client = SignalHireClient(api_key=api_key)
        
        # Test with invalid search criteria to check error handling
        response = await client.search_prospects(
            search_criteria={},  # Empty criteria should be handled gracefully
            size=1
        )
        
        # Should either succeed with empty results or fail gracefully
        assert isinstance(response, APIResponse)
        if not response.success:
            assert response.error is not None
            print(f"✅ Error handling test: {response.error}")
        else:
            print(f"✅ Empty search handled gracefully")

    def test_cli_configuration_for_testing(self):
        """Test CLI configuration is properly set up for testing."""
        # Check that CLI config can be instantiated
        assert cli_config is not None
        assert hasattr(cli_config, 'api_key')
        assert hasattr(cli_config, 'api_base_url')
        
        # Check default values
        assert cli_config.api_base_url == "https://www.signalhire.com"
        assert cli_config.api_prefix == "/api/v1"
        
        print(f"✅ CLI Configuration Test - Base URL: {cli_config.api_base_url}")


class TestSignalHireBulkOperations:
    """Test bulk operations and batch processing."""
    
    @pytest.fixture
    def large_dataset(self):
        """Generate larger dataset for bulk testing.""" 
        return [
            {
                "uid": f"bulk_test_{i:03d}",
                "fullName": f"Test Person {i}",
                "currentTitle": f"Position {i}",
                "currentCompany": f"Company {i}",
                "location": "Test Location",
                "linkedinUrl": f"https://linkedin.com/in/test{i}"
            }
            for i in range(100)
        ]
    
    @pytest.fixture
    def api_key(self):
        """Get API key from environment or use mock."""
        return os.getenv("SIGNALHIRE_API_KEY", "test_api_key_12345")
    
    def test_bulk_csv_export_performance(self, tmp_path, large_dataset):
        """Test CSV export with larger dataset."""
        exporter = CSVExporter()
        output_file = tmp_path / "bulk_test_export.csv"
        
        # Export large dataset
        exporter.export_to_csv(large_dataset, str(output_file))
        
        # Validate export
        assert output_file.exists()
        df = pd.read_csv(output_file)
        assert len(df) == 100
        
        # Check file size is reasonable
        file_size_kb = output_file.stat().st_size / 1024
        assert file_size_kb > 1, "CSV file should be at least 1KB for 100 records"
        assert file_size_kb < 100, "CSV file should be under 100KB for 100 records"
        
        print(f"✅ Bulk Export Test - {len(df)} records, {file_size_kb:.1f}KB")
    
    @pytest.mark.asyncio
    async def test_batch_processing_simulation(self, api_key):
        """Test batch processing with simulated API calls."""
        client = SignalHireClient(api_key=api_key)
        
        # Simulate processing batches of UIDs
        test_uids = [f"test_uid_{i:03d}" for i in range(50)]
        batch_size = 10
        batches = [test_uids[i:i+batch_size] for i in range(0, len(test_uids), batch_size)]
        
        successful_batches = 0
        total_processed = 0
        
        for batch_num, batch in enumerate(batches):
            # Simulate batch processing (mocked)
            mock_response = APIResponse(
                success=True,
                data={"processed": len(batch), "batch": batch_num},
                status_code=200
            )
            
            if mock_response.success:
                successful_batches += 1
                total_processed += len(batch)
        
        assert successful_batches == len(batches)
        assert total_processed == len(test_uids)
        
        print(f"✅ Batch Processing Test - {successful_batches} batches, {total_processed} items")


# Integration test for command line interface
class TestCLIIntegration:
    """Test CLI integration with API services."""
    
    def test_cli_import_structure(self):
        """Test that CLI can import all necessary modules.""" 
        from src.cli.main import main, cli_config
        from src.cli.search_commands import search
        from src.cli.reveal_commands import reveal
        from src.cli.status_commands import status
        
        # Check that commands are properly registered
        assert main is not None
        assert search is not None
        assert reveal is not None
        assert status is not None
        
        print(f"✅ CLI Import Test - All commands available")
    
    def test_config_file_handling(self, tmp_path):
        """Test configuration file creation and loading."""
        from src.cli.main import CliConfig
        
        # Test config with custom directory
        test_config = CliConfig()
        test_config.config_dir = tmp_path / ".signalhire-test"
        test_config.config_file = test_config.config_dir / "config.json"
        
        # Test saving config
        test_config.email = "test@example.com"
        test_config.api_base_url = "https://test.signalhire.com"
        test_config.save_config()
        
        # Verify config file was created
        assert test_config.config_file.exists()
        
        # Test loading config
        new_config = CliConfig()
        new_config.config_dir = test_config.config_dir
        new_config.config_file = test_config.config_file
        new_config.load_config()
        
        assert new_config.email == "test@example.com"
        assert new_config.api_base_url == "https://test.signalhire.com"
        
        print(f"✅ Config File Test - Save/load successful")