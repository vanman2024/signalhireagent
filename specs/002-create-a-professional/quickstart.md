# QuickStart Guide: API-First SignalHire Agent

## Installation

```bash
# Clone repository
git clone https://github.com/your-repo/signalhireagent
cd signalhireagent

# Install dependencies
pip install -e .

# Set up environment variables
export SIGNALHIRE_EMAIL="your-email@example.com"
export SIGNALHIRE_PASSWORD="your-password"

# Or create .env file
echo "SIGNALHIRE_EMAIL=your-email@example.com" > .env
echo "SIGNALHIRE_PASSWORD=your-password" >> .env
```

## Quick Start (API Mode - Recommended)

### 1. Check Your Credits
```bash
signalhire credits --check
```
Expected output:
```
✅ Available credits: 85
📊 Daily usage: 15/100 contacts revealed
⏰ Resets at: 2025-09-12 00:00:00 UTC
```

### 2. Search for Prospects
```bash
signalhire search --title "Software Engineer" --location "San Francisco" --limit 20
```
Expected output:
```
🔍 Searching prospects...
✅ Found 127 prospects matching criteria
📄 Results saved to: search_results_20250911_153045.csv
```

### 3. Reveal Contact Information
```bash
# Reveal single contact (costs 1 credit)
signalhire reveal abc123def456ghi789jkl012mno345pq

# Reveal multiple contacts from CSV
signalhire reveal --input search_results_20250911_153045.csv --limit 10 --output contacts.csv
```
Expected output:
```
🔓 Revealing contacts... [██████████] 100% (10/10)
✅ Credits used: 10
📧 Contacts revealed: 8 successful, 2 failed
📄 Results saved to: contacts.csv
```

### 4. Complete Workflow
```bash
signalhire workflow --search '{"title":"Engineer","location":"SF"}' --reveal-all --max-reveals 25
```

## Advanced Usage

### Browser Mode (For Bulk Operations 1000+)
```bash
# Enable browser automation for high-volume reveals
signalhire reveal --input large_prospect_list.csv --browser --bulk-size 1000
```

### Configuration
```bash
# Set default preferences
signalhire config set default_format csv
signalhire config set batch_size 10
signalhire config set timeout 30

# View current configuration
signalhire config show
```

### Export Formats
```bash
# CSV export (default)
signalhire search --title "Engineer" --output results.csv

# JSON export
signalhire search --title "Engineer" --format json --output results.json

# Revealed contacts only
signalhire reveal --input all_prospects.csv --output contacts_only.csv
```

## Rate Limits & Best Practices

### API Limits
- **Contact Reveals**: 100 per day per account
- **Searches**: Unlimited
- **Credit Checks**: Unlimited

### Best Practices
1. **Check credits first**: Always run `signalhire credits --check` before bulk operations
2. **Use search filters**: Be specific to reduce irrelevant results
3. **Batch wisely**: Use `--batch-size 10` for optimal API performance
4. **Save intermediate results**: Use `--output` to avoid losing progress
5. **Monitor usage**: Check daily usage to avoid hitting limits

### When to Use Browser Mode
- Need more than 100 contact reveals per day
- Willing to handle potential Cloudflare challenges
- Have bulk operations (1000+ contacts)
- Using SignalHire's native export features

## Troubleshooting

### Authentication Issues
```bash
# Test your credentials
signalhire doctor

# Expected output:
# Environment check:
# - SIGNALHIRE_EMAIL: set
# - SIGNALHIRE_PASSWORD: set
```

### Rate Limit Exceeded
```bash
Error: Daily reveal limit exceeded (100/100 used). Resets at 2025-09-12 00:00:00 UTC.
```
**Solution**: Wait until reset time or use browser mode for additional reveals.

### Invalid Prospect UID
```bash
Error: Invalid prospect UID format: 'invalid-uid'. Must be 32 alphanumeric characters.
```
**Solution**: Verify UID format from search results.

### Network Issues
```bash
Error: Network connection failed. Please check your internet connection.
```
**Solution**: Check internet connection and SignalHire API status.

## File Formats

### Input Files
**Prospect UIDs (JSON)**:
```json
["abc123def456ghi789jkl012mno345pq", "def456ghi789jkl012mno345pqabc123"]
```

**Search Results (CSV)**:
```csv
uid,name,title,company,location
abc123...,John Doe,Software Engineer,Google Inc,"San Francisco, CA"
```

### Output Files
**Revealed Contacts (CSV)**:
```csv
uid,name,title,company,location,email,phone,linkedin_url,revealed,reveal_timestamp
abc123...,John Doe,Software Engineer,Google Inc,"San Francisco, CA",john.doe@example.com,+1-555-0123,https://linkedin.com/in/johndoe,true,2025-09-11T15:30:00Z
```

## Examples

### Example 1: Target Company Research
```bash
# Search for engineers at specific companies
signalhire search --company "Google" --title "Engineer" --limit 50 --output google_engineers.csv

# Reveal top 10 prospects
signalhire reveal --input google_engineers.csv --limit 10 --output google_contacts.csv
```

### Example 2: Location-Based Outreach
```bash
# Find prospects in multiple locations
signalhire search --title "Product Manager" --location "San Francisco OR Seattle" --limit 100

# Workflow approach
signalhire workflow --search 'search_criteria.json' --max-reveals 50 --output pm_contacts.csv
```

### Example 3: Skills-Based Search
```bash
# Search by keywords/skills
signalhire search --keywords "Python Django React" --title "Full Stack" --limit 30
```

## Integration

### API Usage (Python)
```python
import asyncio
from src.services.signalhire_client import SignalHireClient

async def main():
    async with SignalHireClient() as client:
        # Check credits
        credits = await client.check_credits()
        print(f"Credits: {credits.data}")
        
        # Search prospects
        search_result = await client.search_prospects({
            "title": "Software Engineer",
            "location": "San Francisco"
        })
        
        # Reveal contacts
        prospects = search_result.data["prospects"]
        prospect_ids = [p["id"] for p in prospects[:5]]
        results = await client.batch_reveal_contacts(prospect_ids)
        
        print(f"Revealed {len(results)} contacts")

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI Automation (Bash)
```bash
#!/bin/bash
# Automated daily prospect gathering

# Check if we have credits
if ! signalhire credits --check | grep -q "Available credits"; then
    echo "No credits available"
    exit 1
fi

# Search and reveal
signalhire search --title "Engineer" --company "Startup" --limit 50 --output daily_prospects.csv
signalhire reveal --input daily_prospects.csv --limit 25 --output daily_contacts.csv

echo "Daily prospect gathering complete: daily_contacts.csv"
```

## Next Steps

1. **Set up automation**: Create daily/weekly scripts for regular prospect gathering
2. **Configure CRM integration**: Export CSV files to your CRM system
3. **Monitor usage**: Set up alerts for credit usage and daily limits
4. **Optimize searches**: Refine search criteria based on results quality
5. **Scale operations**: Consider browser mode for high-volume needs
