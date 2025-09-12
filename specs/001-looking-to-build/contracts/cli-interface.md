# CLI Interface Contract

## Command: signalhire-agent

### Global Options
```bash
--api-key TEXT          SignalHire API key [env: SIGNALHIRE_API_KEY]
--email TEXT            SignalHire login email [env: SIGNALHIRE_EMAIL]
--password TEXT         SignalHire login password [env: SIGNALHIRE_PASSWORD]
--browser-mode          Use browser automation instead of API [default: auto]
--headless             Run browser in headless mode [default: true]
--config FILE           Configuration file path [default: ~/.signalhire-agent/config.json]
--log-level LEVEL       Log level [default: INFO]
--format FORMAT         Output format [default: human] [choices: human, json]
--help                  Show help message
--version               Show version information
```

## Command: search

Search for prospects using SignalHire database.

```bash
signalhire-agent search [OPTIONS]
```

### Options
```bash
--title TEXT                Current job title (supports Boolean queries)
--location TEXT             Geographic location (city, state, country)
--company TEXT              Current company name (supports Boolean queries)
--industry TEXT             Industry category
--keywords TEXT             Skills and attributes (supports Boolean queries)
--name TEXT                 Full name to search for
--experience-from INTEGER   Minimum years of experience
--experience-to INTEGER     Maximum years of experience
--open-to-work             Filter for job seekers only
--size INTEGER              Results per page [default: 10] [range: 1-100]
--output FILE               Save results to file [default: stdout]
--continue-search           Continue previous search using pagination
```

### Examples
```bash
# Basic search
signalhire-agent search --title "Software Engineer" --location "New York"

# Advanced Boolean search
signalhire-agent search --title "(Python OR JavaScript) AND Senior" --company "Google OR Microsoft"

# Save results to file
signalhire-agent search --title "Product Manager" --output prospects.json

# Paginated search
signalhire-agent search --title "Designer" --size 50 --continue-search
```

### Future CLI Enhancements
```bash
# Multi-platform search (future)
signalhire-agent search multi-platform \
  --platforms "signalhire,apollo,linkedin" \
  --title "VP Sales" \
  --dedupe \
  --output unified_results.json

# Team collaboration (future)
signalhire-agent search --title "DevOps" \
  --share-with-team \
  --assign-to john@company.com \
  --tags "q4-hiring,remote-ok"

# Workflow scheduling (future)
signalhire-agent search --title "Product Manager" \
  --schedule "weekly" \
  --webhook "https://company.com/leads-webhook" \
  --auto-reveal

# Agency/white-label mode (future)
signalhire-agent search --title "CTO" \
  --client-workspace "techcorp" \
  --branded-export \
  --custom-fields "client:techcorp,campaign:leadership"
```

### Output Format
```json
{
  "operation_id": "uuid",
  "total_results": 150,
  "current_batch": 20,
  "scroll_id": "abc123",
  "prospects": [
    {
      "uid": "string",
      "full_name": "string", 
      "location": "string",
      "current_title": "string",
      "current_company": "string",
      "skills": ["string"],
      "open_to_work": true,
      "contacts_available": false
    }
  ]
}
```

## Command: reveal

Reveal contact information for prospects using bulk operations.

```bash
signalhire-agent reveal [OPTIONS] PROSPECT_UIDS...
```

### Options
```bash
--search-file FILE          Load prospect UIDs from search results file
--bulk-size INTEGER         Prospects per bulk operation [default: 1000] [range: 1-1000]
--use-native-export        Use SignalHire's native CSV export feature
--export-format FORMAT     Native export format [choices: csv, xlsx] [default: csv]
--timeout INTEGER           Timeout for reveal operation [default: 600]
--output FILE               Save revealed contacts to file [default: stdout]
--dry-run                   Check credits and show what would be revealed
--save-to-list TEXT         Save results to SignalHire lead list
--browser-wait INTEGER      Wait time between browser actions [default: 2]
```

### Examples
```bash
# Bulk reveal with native export
signalhire-agent reveal --search-file prospects.json --use-native-export

# Large bulk operation
signalhire-agent reveal --search-file prospects.json --bulk-size 1000 --export-format xlsx

# Save to SignalHire lead list
signalhire-agent reveal --search-file prospects.json --save-to-list "Q4 Sales Leads"

# Check costs before large operation
signalhire-agent reveal --search-file prospects.json --dry-run
```

### Output Format
```json
{
  "operation_id": "uuid",
  "total_prospects": 100,
  "revealed_count": 95,
  "failed_count": 5,
  "credits_used": 95,
  "prospects": [
    {
      "uid": "string",
      "full_name": "string",
      "status": "success",
      "contacts": [
        {
          "type": "email",
          "value": "email@domain.com",
          "rating": "100",
          "sub_type": "work"
        }
      ]
    }
  ]
}
```

## Command: workflow

Execute complete lead generation workflows using browser automation.

```bash
signalhire-agent workflow [OPTIONS] WORKFLOW_TYPE
```

### Workflow Types
```bash
lead-generation         Complete search → reveal → export workflow
prospect-enrichment     Enrich existing prospect list with contacts
list-management         Manage SignalHire lead lists and folders
bulk-export            Export existing SignalHire lists/projects
```

### Options
```bash
--search-criteria FILE     JSON file with search parameters
--prospect-list FILE       Existing prospect list to enrich
--output-dir DIR           Directory for output files [default: ./output]
--list-name TEXT           Name for SignalHire lead list
--export-existing TEXT     Export existing SignalHire list by name
--schedule CRON            Schedule workflow execution
--notification-email TEXT  Email for completion notifications
--max-prospects INTEGER    Maximum prospects to process [default: 10000]
```

### Examples
```bash
# Complete lead generation workflow
signalhire-agent workflow lead-generation \
  --search-criteria search_params.json \
  --list-name "Q4 Enterprise Leads" \
  --output-dir ./leads

# Enrich existing prospect list
signalhire-agent workflow prospect-enrichment \
  --prospect-list existing_leads.csv \
  --output-dir ./enriched

# Export existing SignalHire data
signalhire-agent workflow bulk-export \
  --export-existing "Previous Campaign Results" \
  --output-dir ./exports

# Scheduled lead generation
signalhire-agent workflow lead-generation \
  --search-criteria weekly_search.json \
  --schedule "0 9 * * 1" \
  --notification-email alerts@company.com
```

## Command: export

Export prospect data to various formats.

```bash
signalhire-agent export [OPTIONS] INPUT_FILE
```

### Options
```bash
--format FORMAT             Export format [choices: csv, xlsx, json] [default: csv]
--output FILE               Output file path [default: prospects.{format}]
--columns TEXT              Comma-separated list of columns to include
--include-contacts          Include revealed contact information
--template FILE             Custom export template file
```

### Available Columns
- `full_name`, `location`, `current_title`, `current_company`
- `skills`, `experience_years`, `open_to_work`
- `email_work`, `email_personal`, `phone_work`, `phone_personal`
- `linkedin_url`, `company_size`, `industry`

### Examples
```bash
# Basic CSV export
signalhire-agent export prospects.json

# Custom Excel export
signalhire-agent export prospects.json --format xlsx --output leads.xlsx

# Export specific columns only
signalhire-agent export prospects.json --columns "full_name,email_work,current_company"

# Include all contact information
signalhire-agent export prospects.json --include-contacts
```

## Command: status

Check operation status and account information.

```bash
signalhire-agent status [OPTIONS]
```

### Options
```bash
--operation-id TEXT         Check specific operation status
--credits                   Show remaining credits
--operations               List recent operations
--logs                     Show recent log entries
```

### Examples
```bash
# Check account status
signalhire-agent status --credits

# Check specific operation
signalhire-agent status --operation-id abc123

# View recent operations
signalhire-agent status --operations --logs
```

## Command: config

Manage configuration settings.

```bash
signalhire-agent config [OPTIONS] COMMAND
```

### Subcommands
```bash
set KEY VALUE              Set configuration value
get KEY                    Get configuration value  
list                       List all configuration
reset                      Reset to defaults
```

### Examples
```bash
# Set API key
signalhire-agent config set api_key "your-api-key"

# Set default callback URL
signalhire-agent config set callback_url "https://yourdomain.com/callback"

# View all settings
signalhire-agent config list
```

## Exit Codes
- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: API authentication error
- `4`: Rate limit exceeded
- `5`: Insufficient credits
- `6`: Network/connectivity error
