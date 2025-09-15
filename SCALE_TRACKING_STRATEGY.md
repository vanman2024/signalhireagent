# Large-Scale Tracking & Deduplication Strategy

This document outlines how to efficiently handle large datasets (7,000+ contacts) while avoiding duplicate reveals and managing API quotas.

## The Challenge: 7,000+ Heavy Equipment Mechanics

**Scenario:**
- Target: 7,000+ Heavy Equipment Mechanics
- API Limits: 200 searches/day, 5,000 reveals/day
- Need: Efficient tracking, no duplicate charges, scalable workflow

**Key Problems:**
1. **Search Pagination**: Must split into multiple searches (200 query limit)
2. **Duplicate Prevention**: Don't re-reveal already processed contacts
3. **Progress Tracking**: Know which contacts have been processed
4. **Credit Optimization**: Maximize reveals within daily limits

## SignalHire's Unique Identifier System

### What SignalHire Provides
```json
{
  "uid": "12345678",           // SignalHire's unique person ID
  "linkedin_url": "linkedin.com/in/johndoe",
  "email": "john@company.com", // If already revealed
  "phone": "+1-555-123-4567"   // If already revealed
}
```

**Key Insight:** SignalHire's `uid` is the primary deduplication key. Same person = same `uid` across all searches.

## Proposed Tracking Database Schema

### Local SQLite Database: `signalhire_tracking.db`

```sql
-- Main contacts table
CREATE TABLE contacts (
    uid TEXT PRIMARY KEY,                    -- SignalHire unique ID
    linkedin_url TEXT UNIQUE,               -- LinkedIn profile URL
    full_name TEXT,                         -- Full name
    current_title TEXT,                     -- Job title
    current_company TEXT,                   -- Company name
    location TEXT,                          -- Location
    first_seen_date DATE,                   -- When first discovered
    last_updated DATE,                      -- Last data update
    search_keywords TEXT,                   -- What search found them
    status TEXT DEFAULT 'discovered'        -- discovered, revealed, failed
);

-- Contact reveal tracking
CREATE TABLE reveals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT REFERENCES contacts(uid),
    reveal_date DATE,
    credits_used INTEGER DEFAULT 1,
    email TEXT,
    phone TEXT,
    request_id TEXT,                        -- SignalHire request ID
    success BOOLEAN,
    error_message TEXT
);

-- Search session tracking
CREATE TABLE search_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_date DATE,
    search_query TEXT,
    total_found INTEGER,
    new_contacts INTEGER,                   -- Contacts not seen before
    duplicate_contacts INTEGER,             -- Contacts already in DB
    scroll_id TEXT,                         -- For pagination
    completed BOOLEAN DEFAULT FALSE
);
```

## Implementation Strategy

### Phase 1: Search & Collect (0 credits used)
```bash
# Search in chunks to stay within 200 query limit
# Day 1: Search #1
signalhire search \
  --title "Heavy Equipment Mechanic" \
  --location "Canada" \
  --size 100 --all-pages --max-pages 20 \
  --output mechanics_batch_1.json

# Day 2: Search #2 (different location filter)
signalhire search \
  --title "Heavy Equipment Mechanic" \
  --location "United States" \
  --size 100 --all-pages --max-pages 20 \
  --output mechanics_batch_2.json

# Day 3: Search #3 (different keywords)
signalhire search \
  --title "Equipment Technician OR Machinery Mechanic" \
  --location "Canada OR United States" \
  --size 100 --all-pages --max-pages 20 \
  --output mechanics_batch_3.json
```

### Phase 2: Database Import & Deduplication
```bash
# Import all search results into tracking database
signalhire import-contacts mechanics_batch_1.json --session-name "canada-search"
signalhire import-contacts mechanics_batch_2.json --session-name "usa-search"  
signalhire import-contacts mechanics_batch_3.json --session-name "expanded-search"

# Check deduplication results
signalhire stats --contacts

# Expected output:
# 📊 Contact Statistics:
# Total unique contacts: 7,234
# New from batch 1: 2,500
# New from batch 2: 3,100 (1,400 duplicates skipped)
# New from batch 3: 1,634 (1,866 duplicates skipped)
# Ready for reveal: 7,234
# Already revealed: 0
```

### Phase 3: Intelligent Reveal Strategy
```bash
# Reveal in priority order (save highest value for later)
# Day 1: Reveal 4,000 contacts (within 5,000 daily limit)
signalhire reveal-from-db \
  --limit 4000 \
  --priority "current_company NOT LIKE '%unemployed%'" \
  --output revealed_batch_1.csv

# Day 2: Reveal remaining 3,234 contacts  
signalhire reveal-from-db \
  --limit 5000 \
  --skip-revealed \
  --output revealed_batch_2.csv
```

## Advanced Deduplication Logic

### Contact Matching Rules
```python
def is_duplicate_contact(new_contact, existing_contacts):
    """Multi-level deduplication strategy."""
    
    # Level 1: SignalHire UID (most reliable)
    if new_contact.uid in [c.uid for c in existing_contacts]:
        return True
    
    # Level 2: LinkedIn URL (very reliable)
    if new_contact.linkedin_url in [c.linkedin_url for c in existing_contacts]:
        return True
    
    # Level 3: Name + Company combination (good reliability)
    name_company_pairs = [(c.full_name, c.current_company) for c in existing_contacts]
    if (new_contact.full_name, new_contact.current_company) in name_company_pairs:
        return True
    
    # Level 4: Email match (if available from previous reveals)
    if new_contact.email and new_contact.email in [c.email for c in existing_contacts]:
        return True
        
    return False
```

### Credit Savings Calculation
```bash
# Estimated savings from deduplication
# Original approach: 3 separate reveals × 7,000 = 21,000 credits
# Smart approach: 1 reveal × 7,234 unique = 7,234 credits
# Savings: 13,766 credits = $2,753 saved (at $0.20/credit)
```

## Recommended CLI Enhancements

### New Commands Needed

```bash
# Database management
signalhire db init                          # Create tracking database
signalhire db stats                         # Show contact/reveal statistics
signalhire db cleanup --older-than 30d     # Remove old data

# Import and deduplication
signalhire import-contacts <file.json> --session-name "batch1"
signalhire dedupe-contacts --dry-run       # Show what would be deduplicated
signalhire dedupe-contacts --apply         # Apply deduplication

# Smart reveal management
signalhire reveal-from-db --limit 4000 --priority "employed"
signalhire reveal-status                   # Show reveal progress
signalhire reveal-resume                   # Continue failed reveals

# Reporting
signalhire export-unique --format csv      # Export all unique contacts
signalhire export-revealed --format csv    # Export only revealed contacts
signalhire campaign-report --session-name "mechanics-campaign"
```

### Enhanced Tracking Features

```bash
# Progress tracking during large operations
signalhire reveal-from-db --limit 5000 --progress

# Output:
# 🔄 Revealing contacts from database...
# Progress: 1,250/5,000 (25%) | Credits used: 1,250 | ETA: 12 min
# ✅ Skipped 47 already revealed contacts (saved 47 credits)
# ⚡ Rate limit: 580/600 requests this minute
# 📊 Daily usage: 1,250/5,000 reveals used
```

## Production Workflow Example

### Complete 7,000+ Contact Campaign

```bash
# Week 1: Data Collection (0 credits used)
Day 1: signalhire search --title "Heavy Equipment Mechanic" --location "Alberta, Canada" --output ab_mechanics.json
Day 2: signalhire search --title "Heavy Equipment Mechanic" --location "Ontario, Canada" --output on_mechanics.json  
Day 3: signalhire search --title "Heavy Equipment Mechanic" --location "Texas, USA" --output tx_mechanics.json
Day 4: signalhire search --title "Equipment Technician" --location "Canada OR USA" --output technicians.json

# Week 2: Database Setup & Import
signalhire db init
signalhire import-contacts ab_mechanics.json --session-name "alberta"
signalhire import-contacts on_mechanics.json --session-name "ontario"
signalhire import-contacts tx_mechanics.json --session-name "texas"  
signalhire import-contacts technicians.json --session-name "technicians"

# Check results
signalhire db stats
# Output: 7,234 unique contacts ready for reveal

# Week 3: Strategic Reveals (within daily limits)
Day 1: signalhire reveal-from-db --limit 4000 --priority "senior" --output day1_reveals.csv
Day 2: signalhire reveal-from-db --limit 3234 --skip-revealed --output day2_reveals.csv

# Final export
signalhire export-revealed --format csv --output final_heavy_equipment_mechanics.csv
```

**Result:**
- ✅ **7,234 unique contacts** (instead of 21,000 duplicates)
- ✅ **$2,753 saved** in reveal credits
- ✅ **Complete tracking** of all operations
- ✅ **Resumable process** if interrupted
- ✅ **Professional export** ready for CRM import

## ROI Analysis

### Cost Comparison

**Without Deduplication Tracking:**
- 3 searches × ~7,000 contacts = ~21,000 reveals
- Cost: 21,000 × $0.20 = $4,200
- Time: 21,000 ÷ 5,000 daily limit = 5 days

**With Smart Deduplication:**
- 3 searches → 7,234 unique contacts
- Cost: 7,234 × $0.20 = $1,447
- Savings: $2,753 (66% reduction)
- Time: 2 days (within daily limits)

**Implementation Cost:**
- Development time: ~8 hours
- Savings per campaign: $2,753
- Break-even: First campaign

## Next Steps

1. **Implement tracking database** with SQLite backend
2. **Add CLI commands** for import/dedupe/reveal-from-db
3. **Create progress monitoring** with real-time statistics
4. **Add resume functionality** for interrupted operations
5. **Build campaign reporting** for ROI analysis

This strategy ensures maximum efficiency at scale while staying within SignalHire's API limits and minimizing credit waste.