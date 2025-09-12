# SignalHire Agent - Quick Start Guide

Get up and running with SignalHire Agent in 5 minutes!

## 🚀 1-Minute Setup

```bash
# 1. Clone and install
git clone https://github.com/your-username/signalhire-agent.git
cd signalhire-agent
sudo apt install python3-pydantic python3-click python3-httpx python3-pandas python3-structlog python3-dotenv python3-email-validator

# 2. Set credentials
export SIGNALHIRE_EMAIL="your@email.com"
export SIGNALHIRE_PASSWORD="your-password"

# 3. Test installation
python3 -m src.cli.main doctor
```

## ⚡ 3-Minute Lead Generation

### Option 1: Quick Search & Reveal
```bash
# Search for prospects
python3 -m src.cli.main search \
  --title "Software Engineer" \
  --location "San Francisco" \
  --output prospects.json

# Reveal contacts
python3 -m src.cli.main reveal \
  --search-file prospects.json \
  --output contacts.csv
```

### Option 2: Complete Workflow (Recommended)
```bash
# One command does it all: search → reveal → export
python3 -m src.cli.main workflow lead-generation \
  --title "Software Engineer" \
  --location "San Francisco" \
  --company "Startup" \
  --max-prospects 1000 \
  --output-dir ./my-leads
```

## 🎯 Common Use Cases

### Tech Recruiting
```bash
python3 -m src.cli.main workflow lead-generation \
  --title "Software Engineer, Full Stack Developer" \
  --location "San Francisco, Seattle, Austin" \
  --keywords "Python, React, Node.js" \
  --max-prospects 2000 \
  --output-dir ./tech-candidates
```

### Sales Prospecting
```bash
python3 -m src.cli.main workflow lead-generation \
  --title "VP Engineering, CTO, Engineering Manager" \
  --company "SaaS, Technology" \
  --keywords "B2B, Enterprise" \
  --max-prospects 500 \
  --output-dir ./sales-prospects
```

### Enriching Existing Lists
```bash
python3 -m src.cli.main workflow prospect-enrichment \
  --prospect-list my_leads.csv \
  --output-dir ./enriched
```

## 📊 Monitor Your Usage

```bash
# Check credits and status
python3 -m src.cli.main status --credits

# View recent operations
python3 -m src.cli.main status --operations
```

## ⚙️ Configuration

```bash
# View current settings
python3 -m src.cli.main config list

# Configure for your needs
python3 -m src.cli.main config set browser_headless false  # See browser
python3 -m src.cli.main config set rate_limit_reveal_per_hour 200  # Faster reveals
```

## 🆘 Need Help?

```bash
# Get help for any command
python3 -m src.cli.main --help
python3 -m src.cli.main workflow --help
python3 -m src.cli.main search --help

# Run diagnostics
python3 -m src.cli.main doctor

# List all available export columns
python3 -m src.cli.main export operation --list-columns
```

## 🎉 You're Ready!

That's it! You now have a powerful lead generation tool that can:
- Search SignalHire's database
- Reveal contact information in bulk
- Export to multiple formats
- Run complete automated workflows

Check the full [README.md](README.md) for advanced features and detailed documentation.
