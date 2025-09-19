#!/bin/bash
# Auto-sync SignalHire to signalhiretest2 
# This script should be run by cron or triggered automatically

set -e

SIGNALHIRE_REPO="/home/vanman2025/signalhireagent"
TARGET_DIR="/home/vanman2025/Projects/signalhireagenttests2"
LOCKFILE="/tmp/signalhire-auto-sync.lock"

# Prevent multiple instances
if [ -f "$LOCKFILE" ]; then
    echo "Auto-sync already running (lockfile exists)"
    exit 0
fi

touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

echo "🔄 $(date): Starting SignalHire auto-sync..."

cd "$SIGNALHIRE_REPO"

# Check if there are new commits
BEFORE_COMMIT=$(git rev-parse HEAD)
git fetch origin main

AFTER_COMMIT=$(git rev-parse origin/main)

if [ "$BEFORE_COMMIT" != "$AFTER_COMMIT" ]; then
    echo "📥 New commits detected, pulling and deploying..."
    
    # Pull latest changes
    git pull origin main
    
    # Deploy to test directory
    ./scripts/intelligent-auto-deploy.sh /home/vanman2025 $(pwd)
    
    echo "✅ Auto-deployment completed: $(cat VERSION | jq -r .version 2>/dev/null || echo 'unknown')"
else
    echo "✅ No new commits, deployment up to date"
fi