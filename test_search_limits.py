#!/usr/bin/env python3
"""Test script to verify search profile limit tracking."""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.signalhire_client import SignalHireClient


async def test_search_profile_limits():
    """Test search profile limit tracking and warnings."""
    print("🧪 Testing search profile limit tracking...")
    
    # Create client
    client = SignalHireClient()
    
    # Test the rate limiter's search profile limit tracking
    rate_limiter = client.rate_limiter
    print(f"📊 Search Profile Limit: {rate_limiter.search_profile_limit}")
    print(f"📊 Daily Reveal Limit: {rate_limiter.daily_limit}")
    
    # Check current daily limits
    daily_status = await rate_limiter.check_daily_limits()
    print(f"\n📈 Current Usage Status:")
    print(f"  Credits Used: {daily_status['current_usage']}/{daily_status['daily_limit']}")
    print(f"  Search Profiles Used: {daily_status['search_profiles_used']}/{daily_status['search_profile_limit']}")
    print(f"  Credits Remaining: {daily_status['remaining']}")
    print(f"  Search Profiles Remaining: {daily_status['search_profiles_remaining']}")
    print(f"  Warning Level: {daily_status['warning_level']}")
    print(f"  Can Proceed (Credits): {daily_status['can_proceed']}")
    print(f"  Can Search (Profiles): {daily_status['can_search']}")
    
    # Test wait_if_needed with search profiles
    try:
        print(f"\n🔄 Testing rate limiter with 10 search profiles needed...")
        status = await rate_limiter.wait_if_needed(credits_needed=0, search_profiles_needed=10)
        print(f"✅ Rate limiter check passed")
        print(f"   Search profiles usage: {status['search_percentage_used']:.1f}%")
    except Exception as e:
        print(f"❌ Rate limiter check failed: {e}")
    
    print(f"\n✅ Search profile limit tracking test completed!")


if __name__ == "__main__":
    asyncio.run(test_search_profile_limits())