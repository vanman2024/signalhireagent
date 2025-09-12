# QuickStart Guide: SignalHire Lead Generation Agent

## Future Platform Features

### Web UI Platform (Coming Soon)
Experience the same powerful automation through a modern web interface:

```bash
# Launch local web interface (development)
signalhire-agent serve --port 3000 --dev

# Access at: http://localhost:3000
# Features: Visual search builder, real-time progress tracking, team collaboration
```

**Upcoming Web Features:**
- 🎯 Visual search criteria builder with drag-and-drop filters
- 📊 Real-time dashboards with progress tracking and analytics
- 👥 Team collaboration with shared lead lists and assignments
- 📅 Workflow scheduling and automation
- 💳 Credit usage monitoring and alerts
- 📱 Mobile-responsive interface for on-the-go lead management

### Multi-Platform Expansion (Roadmap)
Transform your lead generation with unified cross-platform automation:

```bash
# Future: Search across multiple platforms
signalhire-agent search multi-platform \
  --platforms "signalhire,linkedin,apollo,zoominfo" \
  --title "VP of Sales" \
  --company-size "50-200" \
  --dedupe \
  --output master_leads.csv

# Future: LinkedIn Sales Navigator integration
signalhire-agent linkedin search \
  --title "CTO" --company "startups" \
  --connect-template warm_intro.txt

# Future: Apollo.io enrichment
signalhire-agent apollo enrich \
  --input-file leads.csv \
  --enrich-company-data \
  --output enriched_leads.csv
```

**Platform Roadmap:**
- 🔗 **LinkedIn Sales Navigator**: 1M+ users, advanced social selling
- 🚀 **Apollo.io**: 500K+ SMB users, excellent API ecosystem  
- 🏢 **ZoomInfo**: 20K+ enterprise customers, comprehensive B2B data
- 🎯 **Unified Workflows**: Search, enrich, and export across all platforms

### Enterprise & Agency Features (Future)
Scale your lead generation operations with advanced capabilities:

```bash
# Future: White-label agency configuration
signalhire-agent agency configure \
  --brand "Your Agency Name" \
  --logo agency_logo.png \
  --custom-domain leads.youragency.com

# Future: CRM integration
signalhire-agent crm sync \
  --platform salesforce \
  --mapping-file field_mapping.json \
  --auto-create-leads

# Future: Team management
signalhire-agent team add-user \
  --email user@company.com \
  --role "lead-generator" \
  --credits-limit 1000
```

**Enterprise Capabilities:**
- 🏢 **Multi-tenant Architecture**: Isolated data and configurations per organization
- 🎨 **White-label Customization**: Custom branding for agency services
- 🔐 **Role-based Access Control**: Granular permissions and user management
- 📈 **Advanced Analytics**: Detailed reporting and performance metrics
- 🔄 **CRM Integrations**: Salesforce, HubSpot, Pipedrive automatic sync
- 📧 **Email Automation**: Integrated outreach and follow-up sequences

---

## Prerequisites

- Python 3.11 or higher
- SignalHire API key (obtain from [SignalHire Integrations](https://www.signalhire.com/integrations))
- Internet connectivity for API calls and callbacks

## Installation

### 1. Install the Package
```bash
pip install signalhire-agent
```

### 2. Set Up API Key
```bash
# Option 1: Environment variable
export SIGNALHIRE_API_KEY="your-api-key-here"

# Option 2: Configuration command
signalhire-agent config set api_key "your-api-key-here"

# Option 3: Pass as command line argument
signalhire-agent --api-key "your-api-key-here" status --credits
```

### 3. Verify Installation
```bash
signalhire-agent --version
signalhire-agent status --credits
```

Expected output:
```
SignalHire Agent v0.1.0
Credits remaining: 1,247
```

## Basic Usage Workflow

### Step 1: Search for Prospects
```bash
# Search for software engineers in New York
signalhire-agent search \
  --title "Software Engineer" \
  --location "New York, New York, United States" \
  --size 20 \
  --output prospects.json
```

Expected output:
```
Operation ID: abc123-def456-ghi789
Total results: 156 prospects found
Retrieved: 20 prospects in current batch
Results saved to: prospects.json

Use --continue-search to get more results
```

### Step 2: Review Search Results
```bash
# View the first few prospects (human-readable format)
signalhire-agent export prospects.json --format json | head -20

# Or view summary information
cat prospects.json | jq '.prospects[] | {name: .full_name, title: .current_title, company: .current_company}'
```

### Step 3: Reveal Contact Information
```bash
# Reveal contacts for all prospects from search
signalhire-agent reveal \
  --search-file prospects.json \
  --output revealed_contacts.json

# Or reveal specific prospects
signalhire-agent reveal uid1 uid2 uid3 --output contacts.json
```

Expected output:
```
Operation ID: xyz789-abc123-def456
Starting callback server on http://localhost:8080
Revealing contacts for 20 prospects...
Progress: 15/20 completed (3 failed, 2 pending)
Credits used: 15
Results saved to: revealed_contacts.json
```

### Step 4: Export to CSV
```bash
# Export all data to CSV
signalhire-agent export revealed_contacts.json \
  --format csv \
  --include-contacts \
  --output leads.csv
```

Expected output:
```
Exported 15 prospects with contact information to leads.csv
Columns: full_name, current_title, current_company, location, email_work, phone_work
```

## Advanced Usage Examples

### Complex Search with Boolean Queries
```bash
signalhire-agent search \
  --title "(Senior OR Lead) AND (Python OR JavaScript)" \
  --company "NOT (Facebook OR Meta)" \
  --keywords "machine learning AND (tensorflow OR pytorch)" \
  --location "San Francisco, California, United States" \
  --experience-from 5 \
  --experience-to 15 \
  --open-to-work \
  --size 50
```

### Batch Processing with Pagination
```bash
# Get first batch
signalhire-agent search --title "Product Manager" --size 100 --output pm_batch1.json

# Continue pagination
signalhire-agent search --continue-search --output pm_batch2.json

# Combine results and reveal all
cat pm_batch*.json | jq -s 'add' > all_pms.json
signalhire-agent reveal --search-file all_pms.json --batch-size 50
```

### Custom Export with Specific Columns
```bash
signalhire-agent export revealed_contacts.json \
  --format xlsx \
  --columns "full_name,email_work,current_company,linkedin_url" \
  --output "sales_leads.xlsx"
```

### Monitoring and Status Checking
```bash
# Check remaining credits before large operation
signalhire-agent status --credits

# Monitor specific operation
signalhire-agent status --operation-id abc123-def456

# View recent operations and logs
signalhire-agent status --operations --logs
```

### Browser Automation Mode (High-Volume Operations)
```bash
# Use browser automation for bulk reveals (1000+ prospects)
signalhire-agent reveal \
  --search-file large_search.json \
  --mode browser \
  --batch-size 500 \
  --output massive_reveal.csv

# Configure browser settings
signalhire-agent config set browser_headless true
signalhire-agent config set browser_timeout 30
signalhire-agent config set browser_retry_attempts 3
```

Expected output:
```
Browser automation mode enabled
Processing 1,247 prospects in batches of 500
Batch 1/3: 500 prospects - 12 minutes estimated
Using SignalHire native export functionality
Progress: 500/500 completed in 11m 23s
Batch 2/3: 500 prospects - 11 minutes estimated
...
Total: 1,247 prospects revealed and exported to massive_reveal.csv
```

### Rate Limiting and Credit Management
```bash
# Configure rate limiting for production usage
signalhire-agent config set rate_limit_requests_per_minute 580  # Below 600 limit
signalhire-agent config set rate_limit_delay_on_limit 300      # 5 minute backoff

# Set credit alerts
signalhire-agent config set credit_warning_threshold 100
signalhire-agent config set credit_stop_threshold 25

# Monitor usage patterns
signalhire-agent analytics credits --last-30-days
signalhire-agent analytics operations --summary
```

## Configuration Management

### Set Up Custom Callback URL (for production)
```bash
# If you have a public domain for callbacks
signalhire-agent config set callback_url "https://yourdomain.com/signalhire/callback"

# Configure callback server settings
signalhire-agent config set callback_host "0.0.0.0"
signalhire-agent config set callback_port "9000"
```

### Set Default Export Settings
```bash
signalhire-agent config set default_export_format "xlsx"
signalhire-agent config set default_columns "full_name,email_work,current_company,location"
```

### View All Configuration
```bash
signalhire-agent config list
```

## Troubleshooting

### Common Issues

**Authentication Error (Exit Code 3)**
```bash
# Check API key is set correctly
signalhire-agent status --credits

# If error, update API key
signalhire-agent config set api_key "your-correct-api-key"
```

**Rate Limit Exceeded (Exit Code 4)**
```bash
# Wait and retry with smaller batch sizes
signalhire-agent reveal --search-file prospects.json --batch-size 25 --timeout 900
```

**Insufficient Credits (Exit Code 5)**
```bash
# Check credit balance
signalhire-agent status --credits

# Use dry-run to estimate costs
signalhire-agent reveal --search-file prospects.json --dry-run
```

**Callback Server Issues**
```bash
# Use different port if 8080 is busy
signalhire-agent reveal --callback-port 8081 uid1 uid2 uid3

# Check firewall settings for callback URL access
```

### Logs and Debugging
```bash
# Enable verbose logging
signalhire-agent --log-level DEBUG search --title "Engineer"

# View recent logs
signalhire-agent status --logs

# Check specific operation logs
grep "operation-id-here" ~/.signalhire-agent/logs/agent.log
```

### Getting Help
```bash
# Command-specific help
signalhire-agent search --help
signalhire-agent reveal --help
signalhire-agent export --help

# General help
signalhire-agent --help
```

## Performance Tips

1. **Batch Size Optimization**: Use batch sizes of 50-100 for reveals to balance speed and reliability
2. **Credit Management**: Check credits before large operations to avoid interruptions
3. **Callback Stability**: Ensure callback URL is stable and accessible for duration of reveal operations
4. **Search Refinement**: Use specific search criteria to reduce unnecessary credit usage
5. **Pagination**: Use pagination for large search results rather than very large single requests

## Security Best Practices

1. **API Key Storage**: Never commit API keys to version control; use environment variables
2. **Callback URLs**: Use HTTPS for production callback URLs
3. **Data Handling**: Export files contain personal information; handle according to privacy requirements
4. **Network Security**: Ensure callback server is properly configured and secured

## Integration Examples

### CRM Integration
```bash
# Export in format compatible with Salesforce
signalhire-agent export prospects.json \
  --format csv \
  --columns "full_name,email_work,current_company,current_title,location" \
  --output salesforce_import.csv
```

### Analytics Pipeline
```bash
# Export to JSON for data analysis
signalhire-agent export prospects.json \
  --format json \
  --include-contacts > data/prospects_$(date +%Y%m%d).json
```

### Automated Workflow
```bash
#!/bin/bash
# Daily lead generation script

# Search for new prospects
signalhire-agent search \
  --title "Senior Software Engineer" \
  --location "Remote" \
  --open-to-work \
  --output daily_prospects.json

# Reveal contacts
signalhire-agent reveal \
  --search-file daily_prospects.json \
  --output daily_contacts.json

# Export to CRM format
signalhire-agent export daily_contacts.json \
  --format csv \
  --include-contacts \
  --output "leads_$(date +%Y%m%d).csv"

# Clean up temporary files
rm daily_prospects.json daily_contacts.json
```

## Business & Enterprise Scenarios

### Agency Workflow
Scale lead generation for multiple clients with advanced automation:

```bash
# Set up client-specific configurations
signalhire-agent workspace create --name "client-techcorp" 
signalhire-agent workspace activate "client-techcorp"

# Configure client branding and limits
signalhire-agent config set client_name "TechCorp Solutions"
signalhire-agent config set monthly_credit_limit 5000
signalhire-agent config set export_branding true

# Run client-specific searches with custom fields
signalhire-agent search \
  --title "DevOps Engineer" \
  --company-size "100-500" \
  --location "Remote" \
  --custom-tags "client:techcorp,campaign:q4-hiring" \
  --output techcorp_devops.json

# Export with client branding
signalhire-agent export techcorp_devops.json \
  --format csv \
  --header-logo client_logo.png \
  --footer-text "Prepared by Your Agency Name" \
  --output "TechCorp_DevOps_Leads_$(date +%Y%m%d).csv"
```

### Sales Team Collaboration
Enable team-based lead generation with role management:

```bash
# Set up team workspace
signalhire-agent team create --name "sales-team-q4"
signalhire-agent team add-member --email john@company.com --role "searcher"
signalhire-agent team add-member --email sarah@company.com --role "revealer" 
signalhire-agent team add-member --email mike@company.com --role "admin"

# Share search results with team
signalhire-agent search \
  --title "VP of Engineering" \
  --company "Series A startups" \
  --size 100 \
  --share-with-team \
  --assign-to john@company.com \
  --output vp_engineering_targets.json

# Track team performance
signalhire-agent team stats --last-30-days
signalhire-agent team quotas --show-usage
```

### CRM Integration Workflows
Seamlessly integrate lead generation with your existing sales stack:

```bash
# Configure CRM connection
signalhire-agent crm connect salesforce \
  --api-key "your-sf-api-key" \
  --instance "your-company.salesforce.com"

# Search and auto-create leads in CRM
signalhire-agent workflow crm-pipeline \
  --search-criteria search_config.json \
  --auto-create-leads \
  --lead-status "Prospecting" \
  --assign-to "sales@company.com" \
  --tags "signalhire,q4-outbound"

# Sync existing prospects to CRM
signalhire-agent crm sync \
  --input revealed_contacts.json \
  --match-field "email_work" \
  --update-existing \
  --create-missing
```

## Revenue & ROI Examples

### Individual User ROI
**Investment**: $49/month Professional plan  
**Value**: 2,000 prospects/month capacity
- Manual research: 2,000 prospects × 10 minutes = 333 hours
- Time savings: 333 hours × $50/hour = $16,650/month value
- **ROI**: 33,900% return on investment

### Agency Business Model
**Investment**: $399/month Enterprise plan  
**Capacity**: Unlimited prospects, white-label features
- Service 10 clients at $2,000/month each = $20,000 monthly revenue
- Platform cost: $399/month
- **Profit Margin**: 98% ($19,601 monthly profit)

### Enterprise Team Efficiency
**Investment**: $149/month Business plan  
**Team**: 5 sales reps using collaborative features
- Previous tool costs: $500/month per rep × 5 = $2,500/month
- Lead quality improvement: 40% better conversion rates
- Time savings: 15 hours/week per rep × 5 reps = 75 hours/week
- **Total Savings**: $2,351/month + improved conversion ROI

---
