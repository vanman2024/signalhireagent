# CLI Interface Contract

## Command Structure

### signalhire search
```bash
signalhire search [OPTIONS]

Options:
  --keywords TEXT          Search keywords (job titles, skills, etc.)
  --title TEXT            Job title filter
  --company TEXT          Company name filter  
  --location TEXT         Location filter (city, state, country)
  --industry TEXT         Industry filter
  --seniority TEXT        Seniority level filter
  --limit INTEGER         Maximum results (default: 50, max: 1000)
  --output PATH           Save results to CSV file
  --format [csv|json]     Output format (default: csv)
  --help                  Show this message and exit
```

**Example Usage:**
```bash
signalhire search --title "Software Engineer" --location "San Francisco" --limit 100
signalhire search --keywords "Python Django" --company "Google" --output results.csv
```

### signalhire reveal
```bash
signalhire reveal [OPTIONS] [PROSPECT_UIDS]...

Options:
  --input PATH            CSV file with prospect UIDs
  --batch-size INTEGER    Number of prospects per batch (default: 10, max: 10)
  --output PATH           Save revealed contacts to CSV
  --check-credits         Check credits before revealing
  --force                 Skip credit check confirmation
  --help                  Show this message and exit
```

**Example Usage:**
```bash
signalhire reveal abc123def456ghi789jkl012mno345pq
signalhire reveal --input prospects.csv --output contacts.csv
signalhire reveal uid1 uid2 uid3 --batch-size 3
```

### signalhire credits
```bash
signalhire credits [OPTIONS]

Options:
  --check                 Check remaining credits
  --usage                 Show daily usage statistics
  --history INTEGER       Show usage history (days)
  --help                  Show this message and exit
```

**Example Usage:**
```bash
signalhire credits --check
signalhire credits --usage
signalhire credits --history 7
```

### signalhire workflow
```bash
signalhire workflow [OPTIONS]

Options:
  --search TEXT           Search criteria (JSON or file path)
  --reveal-all            Reveal all search results
  --max-reveals INTEGER   Maximum reveals per workflow (default: 50)
  --output PATH           Final CSV output file
  --dry-run               Show what would be done without executing
  --help                  Show this message and exit
```

**Example Usage:**
```bash
signalhire workflow --search '{"title":"Engineer","location":"SF"}' --reveal-all
signalhire workflow --search criteria.json --max-reveals 25 --output final.csv
```

### signalhire status
```bash
signalhire status [OPTIONS] [OPERATION_ID]

Options:
  --list                  List all pending operations
  --wait                  Wait for operation completion
  --timeout INTEGER       Timeout in seconds for --wait
  --help                  Show this message and exit
```

**Example Usage:**
```bash
signalhire status op_abc123def456
signalhire status --list
signalhire status op_abc123def456 --wait --timeout 300
```

## Output Formats

### CSV Format (Default)
```csv
uid,name,title,company,location,email,phone,linkedin_url,revealed,reveal_timestamp
abc123...,John Doe,Software Engineer,Google Inc,San Francisco CA,john.doe@example.com,+1-555-0123,https://linkedin.com/in/johndoe,true,2025-01-11T15:30:00Z
```

### JSON Format
```json
{
  "prospects": [
    {
      "uid": "abc123def456ghi789jkl012mno345pq",
      "name": "John Doe", 
      "title": "Software Engineer",
      "company": "Google Inc",
      "location": "San Francisco, CA",
      "contact_info": {
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "verified": true,
        "confidence_score": 0.95
      },
      "revealed": true,
      "reveal_timestamp": "2025-01-11T15:30:00Z"
    }
  ],
  "total_count": 1,
  "credits_used": 1,
  "operation_id": "op_abc123def456"
}
```

## Error Handling

### Exit Codes
- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Authentication failed
- `4`: Rate limit exceeded
- `5`: Insufficient credits
- `6`: Network error
- `7`: API error

### Error Messages
```bash
# Rate limit exceeded
Error: Daily reveal limit exceeded (100/100 used). Resets at 2025-01-12 00:00:00 UTC.

# Insufficient credits  
Error: Insufficient credits for operation. Required: 10, Available: 5.

# Invalid prospect UID
Error: Invalid prospect UID format: 'invalid-uid'. Must be 32 alphanumeric characters.

# Authentication failed
Error: Authentication failed. Please check your credentials.

# Network error
Error: Network connection failed. Please check your internet connection.
```

## Progress Display

### Search Progress
```bash
Searching prospects...
Found 127 prospects matching criteria
Results saved to: search_results_20250111_153045.csv
```

### Reveal Progress
```bash
Revealing contacts... [##########] 100% (10/10)
Credits used: 10
Contacts revealed: 8 successful, 2 failed
Results saved to: revealed_contacts_20250111_153145.csv
```

### Batch Operation Progress
```bash
Queued batch operation: op_abc123def456
Checking status... [####------] 40% (4/10 completed)
Operation completed: 8 successful, 2 failed
Results downloaded to: batch_results_20250111_153245.csv
```

## Configuration

### Environment Variables
```bash
SIGNALHIRE_EMAIL=your-email@example.com
SIGNALHIRE_PASSWORD=your-password
SIGNALHIRE_API_KEY=your-api-key
SIGNALHIRE_BASE_URL=https://api.signalhire.com
SIGNALHIRE_DAILY_LIMIT=100
SIGNALHIRE_BATCH_SIZE=10
SIGNALHIRE_TIMEOUT=30
```

### Configuration File (~/.signalhire/config.yaml)
```yaml
auth:
  email: your-email@example.com
  password: your-password
  api_key: your-api-key

api:
  base_url: https://api.signalhire.com
  timeout: 30
  max_retries: 3

limits:
  daily_reveals: 100
  batch_size: 10
  max_search_results: 1000

output:
  default_format: csv
  timestamp_format: "%Y%m%d_%H%M%S"
  csv_delimiter: ","
```

## Interactive Features

### Credit Confirmation
```bash
$ signalhire reveal uid1 uid2 uid3
This operation will use 3 credits. You have 47 credits remaining.
Continue? [y/N]: y
```

### Search Result Preview
```bash
$ signalhire search --title "Engineer" --limit 5
Found 127 prospects. Showing first 5:

1. John Doe - Software Engineer at Google (San Francisco, CA)
2. Jane Smith - DevOps Engineer at Microsoft (Seattle, WA)  
3. Bob Johnson - Backend Engineer at Uber (New York, NY)
4. Alice Brown - Frontend Engineer at Netflix (Los Gatos, CA)
5. Charlie Wilson - ML Engineer at OpenAI (San Francisco, CA)

Save all 127 results to CSV? [y/N]: y
```

### Operation Monitoring
```bash
$ signalhire status op_abc123def456 --wait
Operation Status: Processing... [####------] 40% (4/10)
Estimated completion: 2 minutes
^C (Ctrl+C to stop monitoring, operation continues)
```

## Help System

### Command Help
```bash
$ signalhire --help
SignalHire Lead Generation Agent

Usage: signalhire [OPTIONS] COMMAND [ARGS]...

Commands:
  search     Search for prospects
  reveal     Reveal contact information
  credits    Check credits and usage
  workflow   Execute complete search-to-export workflow
  status     Check operation status
  config     Manage configuration

Global Options:
  --config PATH    Configuration file path
  --verbose        Enable verbose logging
  --quiet          Suppress all output except errors
  --version        Show version information
  --help           Show this message and exit
```

### Subcommand Help
Each command provides detailed help:
```bash
$ signalhire search --help
$ signalhire reveal --help
$ signalhire credits --help
```
