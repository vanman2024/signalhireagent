# SignalHire Agent User Guide

**Professional lead generation with SignalHire's official API.**

## 🚀 Getting Started

### Quick Setup
```bash
# 1. Get your SignalHire API key from https://signalhire.com
# 2. Set your credentials
export SIGNALHIRE_API_KEY="your-api-key-here"

# 3. Test the connection
signalhire doctor
```

### First Search
```bash
# Search for software engineers in San Francisco
signalhire search \
  --title "Software Engineer" \
  --location "San Francisco" \
  --output prospects.json
```

## 📋 Core Features

### 🔍 **Advanced Search**
- Boolean search operators: `AND`, `OR`, `NOT`, `()`
- Multiple criteria: title, location, company, experience
- Automatic pagination and rate limit handling
- Real-time credit monitoring

### 📞 **Contact Reveal**
- LinkedIn URL, email, or phone-based lookups
- Async processing with callback tracking
- Automatic duplicate skipping
- CSV and JSON export formats

### 🧹 **Data Management**
- **Deduplication**: Remove duplicates by uid/LinkedIn URL
- **Filtering**: Exclude unwanted job titles
- **Analysis**: Job title and geographic analysis
- **Merging**: Combine multiple contact files

## 🎯 Common Workflows

### Complete Lead Generation Pipeline
```bash
# 1. Search for prospects
signalhire search \
  --title "(Senior Developer) OR (Software Engineer)" \
  --location "United States" \
  --size 100 \
  --output prospects.json

# 2. Reveal contacts
signalhire reveal \
  --search-file prospects.json \
  --output contacts.csv

# 3. Clean and analyze data
signalhire dedupe merge \
  --input "contacts.csv" \
  --output clean_contacts.json

signalhire analyze job-titles \
  --input clean_contacts.json
```

### Data Cleaning Workflow
```bash
# Remove duplicates from multiple files
signalhire dedupe merge \
  --input "file1.json,file2.json,file3.json" \
  --output merged_clean.json

# Filter out unwanted job titles
signalhire filter job-title \
  --input merged_clean.json \
  --exclude-job-titles "operator,driver,manager" \
  --output filtered_contacts.json
```

## 📊 API Limits & Monitoring

### Daily Limits
- **Search Profiles**: 5,000 per day
- **Contact Reveals**: 5,000 per day
- **Rate Limit**: 600 requests per minute

### Monitoring Usage
```bash
# Check current usage
signalhire status --credits

# Monitor during operations
signalhire search --title "Engineer" --monitor-usage
```

## 📁 File Formats

### Search Results (JSON)
```json
{
  "prospects": [
    {
      "name": "John Smith",
      "title": "Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "linkedin_url": "https://linkedin.com/in/johnsmith",
      "email": "john@techcorp.com"
    }
  ],
  "metadata": {
    "total_found": 2300,
    "credits_used": 0,
    "search_id": "abc123"
  }
}
```

### Contact Data (CSV)
```csv
name,title,company,location,linkedin_url,email,phone,reveal_date
John Smith,Software Engineer,Tech Corp,"San Francisco, CA",https://linkedin.com/in/johnsmith,john@techcorp.com,+1-555-0123,2024-09-15
```

## 🛠️ Advanced Usage

### Boolean Search Examples
```bash
# Complex title combinations
signalhire search \
  --title "((Senior OR Lead) AND (Developer OR Engineer)) OR Architect" \
  --location "California"

# Exclude certain companies
signalhire search \
  --title "Software Engineer" \
  --company "NOT (Google OR Microsoft OR Amazon)" \
  --location "Silicon Valley"
```

### Bulk Operations
```bash
# Process large datasets with progress tracking
signalhire reveal \
  --search-file large_prospects.json \
  --output results.csv \
  --batch-size 50 \
  --max-reveals 1000
```

### Data Analysis
```bash
# Analyze job title distribution
signalhire analyze job-titles --input contacts.json

# Geographic analysis
signalhire analyze geography --input contacts.json

# Check data quality
signalhire analyze duplicates --input contacts.json
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
SIGNALHIRE_API_KEY=your_api_key_here

# Optional
SIGNALHIRE_API_BASE_URL=https://www.signalhire.com
SIGNALHIRE_API_PREFIX=/api/v1
RATE_LIMIT_REQUESTS_PER_MINUTE=600
DAILY_REVEAL_LIMIT=5000
DAILY_SEARCH_PROFILE_LIMIT=5000
```

### CLI Configuration
```bash
# View current settings
signalhire config show

# Update settings
signalhire config set rate_limit 300
```

## 📚 Documentation Index

### User Guides
- **[CLI Commands](./cli-commands.md)** - Complete command reference
- **[API Reference](../developer/architecture/api.md)** - Technical API details
- **[Troubleshooting](../developer/TESTING_AND_RELEASE.md)** - Common issues and solutions

### Developer Resources
- **[Architecture](../developer/architecture/)** - System design docs
- **[Development](../developer/development/)** - Contributing guidelines
- **[Testing](../developer/TESTING_AND_RELEASE.md)** - Testing and release process

## 🎯 Best Practices

### Search Optimization
1. **Use Boolean operators** for complex queries
2. **Monitor credits** before large operations
3. **Use --dry-run** to test search parameters
4. **Save results** with descriptive filenames

### Data Management
1. **Deduplicate regularly** to avoid wasting credits
2. **Filter unwanted titles** early in the process
3. **Use consistent naming** for file organization
4. **Backup important data** before bulk operations

### Performance
1. **Batch operations** for better rate limit management
2. **Use --skip-existing** to avoid duplicate reveals
3. **Monitor usage** during long-running operations
4. **Schedule large jobs** during off-peak hours

## 🆘 Support

### Common Issues
- **API Key Issues**: Verify your key at https://signalhire.com
- **Rate Limits**: Wait 1 minute between batches
- **Connection Errors**: Check network and retry
- **Data Quality**: Use analysis commands to check data

### Getting Help
```bash
# Check system status
signalhire doctor

# View help for any command
signalhire search --help
signalhire reveal --help
signalhire dedupe --help
```

---

**Version**: v0.4.2 | **Last Updated**: September 15, 2025
