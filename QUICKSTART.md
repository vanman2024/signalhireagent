# SignalHire Agent - Quick Start Guide

Get up and running with SignalHire Agent in 5 minutes!

## 🚀 1-Minute Setup

```bash
# 1. Clone and install
git clone https://github.com/your-username/signalhire-agent.git
cd signalhire-agent
sudo apt install python3-pydantic python3-click python3-httpx python3-pandas python3-structlog python3-dotenv python3-email-validator

# 2. Set credentials (API key required)
export SIGNALHIRE_API_KEY="your-api-key-here"

# 3. Test installation (runs slower due to checks)
signalhire doctor
```

## ⚡ 3-Minute Lead Generation

### Option 1: Quick Search & Reveal
```bash
# Search for prospects
signalhire search \
  --title "Software Engineer" \
  --location "San Francisco" \
  --output prospects.json

# Reveal contacts
signalhire reveal \
  --search-file prospects.json \
  --output contacts.csv
```

### Option 2: Complete Workflow (Recommended)
```bash
# One command does it all: search → reveal → export
signalhire workflow lead-generation \
  --title "Software Engineer" \
  --location "San Francisco" \
  --company "Startup" \
  --max-prospects 1000 \
  --output-dir ./my-leads
```

## 🎯 Common Use Cases

### Tech Recruiting
```bash
signalhire workflow lead-generation \
  --title "Software Engineer, Full Stack Developer" \
  --location "San Francisco, Seattle, Austin" \
  --keywords "Python, React, Node.js" \
  --max-prospects 2000 \
  --output-dir ./tech-candidates
```

### Sales Prospecting
```bash
signalhire workflow lead-generation \
  --title "VP Engineering, CTO, Engineering Manager" \
  --company "SaaS, Technology" \
  --keywords "B2B, Enterprise" \
  --max-prospects 500 \
  --output-dir ./sales-prospects
```

### Enriching Existing Lists
```bash
signalhire workflow prospect-enrichment \
  --prospect-list my_leads.csv \
  --output-dir ./enriched
```

## 📊 Monitor Your Usage & API Limits

```bash
# Check credits and status (fast) - Shows 5000/day limits
signalhire status --credits

# Example output:
# 👁️ Profile Views: 1,250/5,000 daily views used (25.0%)
# 📞 Contact Reveals: 23/5,000 daily reveals used (0.5%) 
# ⚠️  Warning Level: none

# View recent operations
signalhire status --operations
```

**New in v0.2.0**: Automatic API limit tracking prevents exceeding daily quotas
- 🔍 **Search Profiles**: 5,000/day automatically tracked
- 📞 **Contact Reveals**: 5,000/day automatically tracked  
- ⚠️ **Smart Warnings**: At 50%, 75%, 90% usage levels

## ⚙️ Configuration

```bash
# View current settings
signalhire config list

# Configure for your needs
signalhire config set browser_headless false  # See browser
signalhire config set rate_limit_reveal_per_hour 200  # Faster reveals
```

## 🆘 Need Help?

```bash
# Get help for any command
signalhire --help
signalhire workflow --help
signalhire search --help

# Run diagnostics (runs slower due to checks)
signalhire doctor

# List all available export columns
signalhire export operation --list-columns
```

## 🎉 You're Ready!

That's it! You now have a powerful lead generation tool that can:
- Search SignalHire's database
- Reveal contact information in bulk
- Export to multiple formats
- Run complete automated workflows

Check the full [README.md](README.md) for advanced features and detailed documentation.
