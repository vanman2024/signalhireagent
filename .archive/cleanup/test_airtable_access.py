#!/usr/bin/env python3
"""
Test Airtable access to diagnose permissions issues
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

def test_airtable_access():
    """Test various Airtable operations to diagnose permissions"""
    
    # Configuration from environment
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    print(f"API Key starts with: {api_key[:10] if api_key else 'N/A'}...")
    
    try:
        # Initialize API
        api = Api(api_key)
        print("✅ API initialized successfully")
        
        # Test 1: List bases
        try:
            bases = list(api.bases())
            print(f"✅ Can list bases: {len(bases)} found")
            for base in bases[:3]:  # Show first 3
                print(f"   - {base.name} ({base.id})")
        except Exception as e:
            print(f"❌ Cannot list bases: {e}")
        
        # Test 2: Access specific base
        try:
            base = api.base(AIRTABLE_BASE_ID)
            print(f"✅ Can access base: {AIRTABLE_BASE_ID}")
            
            # List tables in this base
            schema = base.schema()
            print(f"✅ Base schema accessed, {len(schema.tables)} tables found:")
            for table in schema.tables:
                print(f"   - {table.name} ({table.id})")
                
        except Exception as e:
            print(f"❌ Cannot access base: {e}")
        
        # Test 3: Access specific table
        try:
            table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
            print(f"✅ Can access table: {AIRTABLE_TABLE_ID}")
            
            # Try to read a few records
            records = table.all(max_records=3)
            print(f"✅ Can read records: {len(records)} found")
            
            if records:
                print("Sample record fields:")
                for field_name, field_value in list(records[0]['fields'].items())[:10]:
                    print(f"   - {field_name}: {field_value}")
            
        except Exception as e:
            print(f"❌ Cannot access table: {e}")
        
        # Test 4: Try to create a test record
        try:
            test_record = {
                "Test Field": "Test Value",
                "Status": "Test"
            }
            
            # Try minimal record first
            created = table.create({"Status": "Test Entry"})
            print(f"✅ Can create records: {created['id']}")
            
            # Clean up test record
            table.delete(created['id'])
            print("✅ Test record cleaned up")
            
        except Exception as e:
            print(f"❌ Cannot create records: {e}")
            
    except Exception as e:
        print(f"❌ API initialization failed: {e}")

if __name__ == "__main__":
    test_airtable_access()