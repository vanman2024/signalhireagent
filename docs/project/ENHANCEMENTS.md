# Future Enhancements

## 🚀 Future Architecture (Terminal + Cloud Automation)

### Current: Local MCP Server
```
Terminal (you) → Local CLI → Local MCP → Airtable API
```

### Future: Remote HTTP MCP Servers
```
Terminal (you) → Local CLI → Remote HTTP MCP (Railway/Vercel) → Airtable API
                                   ↓
                              Webhook Automation
```

**Benefits of Remote Architecture:**
- ✅ **Keep terminal workflow** - no UI needed
- ✅ **24/7 automation** - webhooks and background jobs
- ✅ **Scalable processing** - handle large data volumes
- ✅ **Real-time sync** - immediate SignalHire → Airtable updates

**Planned Commands (Future):**
```bash
# Deploy automation to cloud
signalhire-agent deploy automation --platform railway

# Use remote processing
signalhire-agent workflow red-seal-automation --remote

# Monitor cloud jobs
signalhire-agent status --remote-jobs --live
```

## 🤖 AI/ML Enhancement Roadmap

**Current Categorization System:**
- ✅ Rule-based pattern matching with hardcoded keywords
- ✅ Works for basic trade categorization 
- ❌ Limited scalability and accuracy

**Future AI/ML Integration:**
```bash
# Train ML model on existing contact data
signalhire-agent ai train --dataset revealed-contacts.json --model trade-classifier

# Use AI for intelligent categorization
signalhire-agent categorize --ai-powered --confidence-threshold 0.85

# Export training data for RedAI system integration
signalhire-agent ai export-training-data --format redai-compatible
```

**Planned AI Features:**
- 🧠 **Machine Learning Models**: Train on job title, company, skills data
- 📊 **Confidence Scoring**: AI-powered accuracy ratings for categorizations
- 🔄 **Active Learning**: Improve model accuracy with user feedback
- 🎯 **RedAI Integration**: Export structured training data for future AI systems
- 📈 **Predictive Analytics**: Forecast hiring trends and skill demands

**Technology Stack (Future):**
- **Models**: scikit-learn, TensorFlow, or Hugging Face transformers
- **Features**: Job title NLP, company industry mapping, skills extraction
- **Training Data**: 1000+ categorized contacts from SignalHire reveals
- **Integration**: RESTful AI endpoints for real-time classification

## ⏱️ Scheduling Daily Runs

### Option A: Cron on a server (e.g., DigitalOcean Droplet)
1. Ensure SIGNALHIRE_API_KEY is set for the cron environment.
2. Add a cron entry:
```
0 8 * * * cd /path/to/signalhireagent && SIGNALHIRE_API_KEY=... ./scripts/daily_job.sh >> logs/cron.log 2>&1
```

### Option B: DigitalOcean App Platform Worker
- Use the Dockerfile in this repo.
- Create a Worker with command `./scripts/daily_job.sh`.
- Set env vars (SIGNALHIRE_API_KEY, optional SIGNALHIRE_API_BASE_URL and SIGNALHIRE_API_PREFIX).
- Add an App Platform Scheduled Job for daily execution.

### Option C: Vercel Cron
- Add to vercel.json:
```
{
  "crons": [
    { "path": "/api/daily", "schedule": "0 8 * * *" }
  ]
}
```
- Create a small serverless function at /api/daily that triggers a small search (and writes results to remote storage like S3/Blob). For heavier reveals, prefer a Worker/VM as above.

## 🧪 Validation Features

The user mentioned validation features and linked records in the Contacts table that aren't being used yet, originally built for the cache system. These need to be adapted from cache-based to Airtable-based:

- Validation system for contact data quality
- Linked record functionality 
- Quality control for new categorizations
- Advanced contact verification workflows

## Future CLI Improvements

- Direct MCP Airtable integration (currently using REST API)
- Enhanced search-to-Airtable commands
- Batch reveal processing from Airtable Status fields
- Advanced Status workflow management
- Real-time progress monitoring for large batches