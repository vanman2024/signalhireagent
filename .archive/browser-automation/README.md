# Archived Browser Automation Files

This directory contains browser automation files that were removed when transitioning to the autonomous lead generation system (003-autonomous-lead-generation).

## Contents

- **Python Files:**
  - `stagehand_automation.py` - Main browser automation wrapper
  - `stagehand_wrapper.py` - Stagehand integration layer 
  - `browser_manager.py` - Browser instance management
  - `browser_errors.py` - Browser-specific error handling
  - `fake_stagehand.py` - Test helper for mocking

- **JavaScript Files:**
  - `stagehand_bridge.js` - Node.js bridge for Stagehand
  - `signalhire_automation.js` - SignalHire web automation scripts

- **Node.js Dependencies:**
  - `package.json` / `package-lock.json` - Node.js project config
  - `node_modules/` - Node.js dependencies (including @browserbasehq/stagehand)

- **Tests:**
  - `tests-browser/` - Browser automation test suite

- **Old CLI Package:**
  - `signalhire_agent-old-cli/` - Original package-based CLI structure (minimal doctor command only)
  - `signalhire_agent.egg-info/` - Python package metadata for old CLI (pip install -e . artifacts)

## Reason for Archival

These files implemented web browser automation using Stagehand/Playwright to interact with SignalHire's web interface. The autonomous lead generation system (003) uses direct API integration instead, making browser automation unnecessary.

## Restoration

If browser automation is needed again, these files can be restored to their original locations:
- `src/lib/` - Python automation files
- `scripts/` - JavaScript files  
- `tests/browser/` - Test directory
- Root directory - Node.js config files