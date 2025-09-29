#!/bin/bash
# Clean CLI Workflow Automation
#
# PURPOSE: Demonstrate the clean CLI-first approach for SignalHire lead generation
# USAGE: ./clean_workflow.sh [title] [location] [size]
# PART OF: SignalHire Agent clean architecture
# CONNECTS TO: signalhire-agent CLI, simple_callback_server.py, Airtable
#
# This script orchestrates the clean CLI workflow:
# 1. Search for prospects
# 2. Reveal contact information 
# 3. Export to CSV
# 4. Webhook automatically pushes to Airtable

set -e  # Exit on any error

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default parameters
TITLE="${1:-Diesel Mechanic}"
LOCATION="${2:-Calgary}"
SIZE="${3:-5}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="$HOME/leads"
BASE_NAME="${LOCATION,,}_${TITLE// /_}_${TIMESTAMP}"

echo "🚀 SignalHire Clean CLI Workflow"
echo "================================="
echo "📋 Target: $TITLE in $LOCATION"
echo "🎯 Size: $SIZE prospects"
echo "📁 Output: $OUTPUT_DIR/$BASE_NAME"
echo ""

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Step 1: Search for prospects
echo "🔍 Step 1: Searching for prospects..."
signalhire-agent search \
  --title "$TITLE" \
  --location "$LOCATION" \
  --size "$SIZE" \
  --output "$OUTPUT_DIR/${BASE_NAME}_search.json"

echo ""

# Step 2: Check how many credits would be used
echo "🧪 Step 2: Checking credit requirements..."
signalhire-agent reveal \
  --search-file "$OUTPUT_DIR/${BASE_NAME}_search.json" \
  --dry-run

echo ""

# Step 3: Reveal contact information
echo "🔓 Step 3: Revealing contact information..."
signalhire-agent reveal \
  --search-file "$OUTPUT_DIR/${BASE_NAME}_search.json" \
  --output "$OUTPUT_DIR/${BASE_NAME}_revealed.json"

echo ""

# Step 4: Export to CSV
echo "📊 Step 4: Exporting to CSV..."
signalhire-agent export operation "$OUTPUT_DIR/${BASE_NAME}_revealed.json" \
  --format csv \
  --output "$OUTPUT_DIR/${BASE_NAME}_contacts.csv"

echo ""
echo "✅ Workflow Complete!"
echo "================================="
echo "📁 Files created:"
echo "   Search results: $OUTPUT_DIR/${BASE_NAME}_search.json"
echo "   Revealed data:  $OUTPUT_DIR/${BASE_NAME}_revealed.json"
echo "   CSV export:     $OUTPUT_DIR/${BASE_NAME}_contacts.csv"
echo ""
echo "🔄 Webhook Integration:"
echo "   Contacts with emails automatically pushed to Airtable"
echo "   via callback server at: $(grep SIGNALHIRE_CALLBACK_URL .env | cut -d'=' -f2)"
echo ""
echo "💡 Next steps:"
echo "   1. Check Airtable for new contacts"
echo "   2. Review CSV file for all prospect data"
echo "   3. Use files for further processing or CRM import"