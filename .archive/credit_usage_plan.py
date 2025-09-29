#!/usr/bin/env python3
"""Plan optimal credit usage for extracting heavy equipment contacts."""

import json
from pathlib import Path
from datetime import datetime

def analyze_contact_pools():
    """Analyze available contact pools and plan credit usage."""
    
    print("Credit Usage Strategy for Heavy Equipment Contacts in Canada")
    print("=" * 60)
    
    # Current situation
    revealed_count = 23
    daily_limit = 5000
    remaining_credits = daily_limit - revealed_count
    
    print(f"Daily Credit Limit: {daily_limit}")
    print(f"Already Revealed: {revealed_count}")
    print(f"Remaining Credits: {remaining_credits}")
    print()
    
    # Available pools
    restrictive_total = 189  # From heavy_equipment_canada.json
    broader_total = 7365     # From heavy_equipment_broader.json
    
    print("Available Contact Pools:")
    print(f"1. Restrictive Search (exact titles): {restrictive_total} prospects")
    print(f"2. Broader Search (including variations): {broader_total} prospects")
    print()
    
    # Strategy recommendations
    print("Recommended Strategy:")
    print("-" * 20)
    
    # Phase 1: High-priority restrictive search
    phase1_target = min(restrictive_total - revealed_count, 200)  # Prioritize exact matches
    print(f"Phase 1: Extract remaining {phase1_target} from restrictive search")
    print(f"         (exact title matches, highest quality)")
    print(f"         Credits needed: {phase1_target}")
    
    # Phase 2: Broader search - highest value first
    remaining_after_phase1 = remaining_credits - phase1_target
    phase2_target = min(remaining_after_phase1, 1000)  # Focus on top prospects
    print(f"Phase 2: Extract top {phase2_target} from broader search")
    print(f"         (includes variations, good quality)")
    print(f"         Credits needed: {phase2_target}")
    
    # Phase 3: Continue broader search
    total_phase1_2 = phase1_target + phase2_target
    remaining_after_phase2 = remaining_credits - total_phase1_2
    
    if remaining_after_phase2 > 0:
        print(f"Phase 3: Extract additional {remaining_after_phase2} from broader search")
        print(f"         (remaining budget for maximum coverage)")
        print(f"         Credits needed: {remaining_after_phase2}")
    
    print()
    print("Priority Criteria:")
    print("- Current employees at known heavy equipment companies")
    print("- Recent experience with major equipment brands (Cat, Komatsu, etc.)")
    print("- Located in major industrial centers (Calgary, Edmonton, Toronto)")
    print("- Exclude operators, drivers, sales, coordinators, supervisors")
    print()
    
    # Calculate total extraction plan
    total_planned = phase1_target + phase2_target + remaining_after_phase2
    grand_total = revealed_count + total_planned
    
    print("Summary:")
    print(f"Current revealed contacts: {revealed_count}")
    print(f"Planned new extractions: {total_planned}")
    print(f"Total contacts after extraction: {grand_total}")
    print(f"Credits remaining: {remaining_credits - total_planned}")
    print()
    
    # Daily continuation plan
    remaining_prospects = broader_total - grand_total
    print("Future Days Strategy:")
    print(f"Remaining prospects: {remaining_prospects}")
    print(f"Days needed to complete (at 5000/day): {remaining_prospects // 5000 + 1}")
    print()
    
    return {
        'current_revealed': revealed_count,
        'remaining_credits': remaining_credits,
        'phase1_target': phase1_target,
        'phase2_target': phase2_target,
        'phase3_target': remaining_after_phase2,
        'total_planned': total_planned,
        'grand_total': grand_total
    }

def main():
    plan = analyze_contact_pools()
    
    # Save plan as JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = f"credit_usage_plan_{timestamp}.json"
    
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"Plan saved to: {plan_file}")

if __name__ == "__main__":
    main()