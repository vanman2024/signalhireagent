#!/usr/bin/env python3
"""
Cleanup Root Directory

PURPOSE: Organize and clean up the root directory by moving files to appropriate locations
USAGE: python3 cleanup_root_directory.py [--dry-run]
PART OF: SignalHire Agent project organization
CONNECTS TO: File system organization
"""

import os
import shutil
import argparse
from pathlib import Path

def cleanup_root_directory(dry_run=False):
    """Clean up the root directory by organizing files."""
    
    root_dir = Path("/home/vanman2025/signalhireagent")
    
    # Create archive directory for old files
    archive_dir = root_dir / "archive"
    if not dry_run:
        archive_dir.mkdir(exist_ok=True)
    
    # Files to move to archive (old/obsolete scripts)
    archive_files = [
        "automated_signalhire_airtable.py",
        "claude_automated_integration.py", 
        "credit_usage_plan.py",
        "extract_revealed_heavy_equipment.py",
        "process_contacts_to_airtable.py",
        "process_revealed_contacts_to_airtable.py",
        "push_to_airtable.py",
        "add_sample_contact_to_airtable.py",
        "signalhire_to_airtable.py",           # Old version
        "signalhire_airtable_integration.py"  # Old version
    ]
    
    # CSV/JSON data files to move to data directory
    data_dir = root_dir / "data" / "archive"
    if not dry_run:
        data_dir.mkdir(parents=True, exist_ok=True)
    
    data_files = [
        "heavy_equipment_canada.csv",
        "heavy_equipment_canada_20250927_132833.csv", 
        "heavy_equipment_canada_comprehensive_20250927_131817.csv",
        "revealed_heavy_equipment_canada_20250927_133716.csv",
        "heavy_equipment_canada.json",
        "heavy_equipment_broader.json",
        "heavy_equipment_search_templates.json",
        "revealed_contacts.json",
        "credit_usage_plan_20250927_133812.json"
    ]
    
    # Keep in root (current automation scripts)
    keep_in_root = [
        "signalhire_to_airtable_automation.py",  # Main automation
        "push_contacts_to_airtable.py",          # Current contact processing  
        "migrate_local_cache_to_airtable.py",    # Migration script
        "cleanup_root_directory.py",             # This script
        "run.py"                                 # Keep the main runner
    ]
    
    print("🧹 Root Directory Cleanup")
    print("=" * 40)
    
    # Move old scripts to archive
    print(f"📦 Moving obsolete scripts to archive/...")
    for filename in archive_files:
        file_path = root_dir / filename
        if file_path.exists():
            target_path = archive_dir / filename
            if dry_run:
                print(f"  [DRY RUN] Would move: {filename} → archive/")
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"  ✅ Moved: {filename} → archive/")
        else:
            print(f"  ⚠️  Not found: {filename}")
    
    # Move data files
    print(f"\\n📁 Moving data files to data/archive/...")
    for filename in data_files:
        file_path = root_dir / filename
        if file_path.exists():
            target_path = data_dir / filename
            if dry_run:
                print(f"  [DRY RUN] Would move: {filename} → data/archive/")
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"  ✅ Moved: {filename} → data/archive/")
        else:
            print(f"  ⚠️  Not found: {filename}")
    
    # List what stays in root
    print(f"\\n📋 Keeping in root:")
    for filename in keep_in_root:
        file_path = root_dir / filename
        if file_path.exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ Missing: {filename}")
    
    # Check for any other Python files
    print(f"\\n🔍 Other Python files in root:")
    other_py_files = []
    for file_path in root_dir.glob("*.py"):
        if file_path.name not in archive_files and file_path.name not in keep_in_root:
            other_py_files.append(file_path.name)
            print(f"  ⚠️  Unhandled: {file_path.name}")
    
    if not other_py_files:
        print(f"  ✅ No unhandled Python files")
    
    # Summary
    print(f"\\n📊 Cleanup Summary:")
    archived_count = len([f for f in archive_files if (root_dir / f).exists()])
    data_moved_count = len([f for f in data_files if (root_dir / f).exists()])
    
    print(f"  Scripts archived: {archived_count}")
    print(f"  Data files moved: {data_moved_count}")
    print(f"  Files kept in root: {len(keep_in_root)}")
    print(f"  Unhandled files: {len(other_py_files)}")
    
    if dry_run:
        print(f"\\n🧪 DRY RUN COMPLETE - No files were actually moved")
        print(f"   Run without --dry-run to perform actual cleanup")
    else:
        print(f"\\n✅ CLEANUP COMPLETE")

def main():
    parser = argparse.ArgumentParser(description="Clean up root directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()
    
    cleanup_root_directory(dry_run=args.dry_run)

if __name__ == "__main__":
    main()