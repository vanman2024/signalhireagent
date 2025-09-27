#!/usr/bin/env python3
"""
CloudFlare Bypass Test Runner - Try Multiple Solutions
"""

import sys
import os
from pathlib import Path

def run_test(test_name, test_file):
    """Run a single test and return success status"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*80}")
    
    try:
        # Import and run the test
        sys.path.insert(0, str(Path(__file__).parent))
        
        if test_file == "botasaurus_test.py":
            from botasaurus_test import main
        elif test_file == "seleniumbase_uc_test.py":
            from seleniumbase_uc_test import main
        elif test_file == "undetected_chrome_test.py":
            from undetected_chrome_test import main
        else:
            print(f"❌ Unknown test file: {test_file}")
            return False
        
        result = main()
        
        if result:
            print(f"\n✅ {test_name} SUCCEEDED!")
            return True
        else:
            print(f"\n❌ {test_name} FAILED!")
            return False
            
    except Exception as e:
        print(f"\n💥 {test_name} CRASHED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Cloudflare bypass tests"""
    print("🚀 CLOUDFLARE BYPASS TEST SUITE")
    print("Testing multiple solutions for SignalHire automation")
    print()
    
    # Check environment
    email = os.environ.get("SIGNALHIRE_EMAIL")
    password = os.environ.get("SIGNALHIRE_PASSWORD")
    
    if not email or not password:
        print("❌ Missing environment variables!")
        print("Please set SIGNALHIRE_EMAIL and SIGNALHIRE_PASSWORD")
        return False
    
    print(f"✅ Using email: {email}")
    print(f"✅ Password configured: {'*' * len(password)}")
    print()
    
    # Test configurations in order of expected success
    tests = [
        ("Botasaurus (Best for Cloudflare)", "botasaurus_test.py"),
        ("SeleniumBase UC Mode", "seleniumbase_uc_test.py"), 
        ("Undetected ChromeDriver", "undetected_chrome_test.py"),
    ]
    
    results = {}
    
    for test_name, test_file in tests:
        print(f"\n⏳ Preparing to run: {test_name}")
        
        # Ask user if they want to run this test
        response = input(f"Run {test_name}? (y/n/q): ").lower().strip()
        
        if response == 'q':
            print("🛑 Test suite stopped by user")
            break
        elif response == 'n':
            print(f"⏭️ Skipping {test_name}")
            results[test_name] = "SKIPPED"
            continue
        
        # Run the test
        success = run_test(test_name, test_file)
        results[test_name] = "SUCCESS" if success else "FAILED"
        
        if success:
            print(f"\n🎉 {test_name} WORKED! No need to test further.")
            break
        else:
            print(f"\n💔 {test_name} didn't work, trying next solution...")
    
    # Final results
    print(f"\n{'='*80}")
    print("📊 FINAL RESULTS")
    print(f"{'='*80}")
    
    for test_name, result in results.items():
        status_emoji = "✅" if result == "SUCCESS" else "❌" if result == "FAILED" else "⏭️"
        print(f"{status_emoji} {test_name}: {result}")
    
    # Determine overall success
    successful_tests = [name for name, result in results.items() if result == "SUCCESS"]
    
    if successful_tests:
        print(f"\n🎉 SUCCESS! Working solution: {successful_tests[0]}")
        print("You can now use this method for SignalHire automation")
        return True
    else:
        print(f"\n😞 No working solutions found")
        print("All Cloudflare bypass methods failed")
        return False

if __name__ == "__main__":
    main()
