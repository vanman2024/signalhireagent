# Testing and Release Workflow Guide

This guide covers how to work with multiple directories, git branches, and testing workflows for the SignalHire Agent project.

## Understanding Git States

### What Happened During Development
1. **Detached HEAD State**: When you checkout a tag (`git checkout v0.1.1`), you're in "detached HEAD" - frozen at that version
2. **Pull Behavior**: `git pull origin main` fetches commits but can't update working files when detached
3. **Checkout Updates**: `git checkout main` moves to latest branch and updates all files

### Key Commands to Check Your State
```bash
# See current branch/state
git branch -v
git status

# See what version you have
git describe --tags
git log --oneline -3
```

## Multi-Directory Development Workflow

### Directory Structure
```
~/signalhireagent/                          # Main development
~/Projects/signalhireagenttests2/signalhireagent/  # Testing directory
```

### Daily Startup Routine
```bash
# Main development directory
cd ~/signalhireagent
git checkout main
git pull origin main

# Testing directory  
cd ~/Projects/signalhireagenttests2/signalhireagent
git checkout main
git pull origin main

# Verify both are in sync
git log --oneline -1  # Should show same commit in both directories
```

### Before Starting Any Work
```bash
# Always run this sequence:
pwd                   # Know where you are
git branch -v         # See current branch/state  
git status            # Check for uncommitted changes
git pull origin main  # Get latest (if on main branch)
```

## Best Practices

### 1. Stay on `main` Branch
- **Default state**: Always work on `main` unless testing specific versions
- **Avoid detached HEAD**: Don't `git checkout v1.2.0` directly

### 2. Safe Version Testing
```bash
# ❌ Don't do this (creates detached HEAD):
git checkout v0.1.1

# ✅ Do this instead:
git checkout -b test-old-version v0.1.1  # Creates branch from tag
# Work with old version...
git checkout main  # Return to main when done
git branch -d test-old-version  # Clean up test branch
```

### 3. Quick Sync Commands
```bash
# Set up git alias for speed:
git config --global alias.sync '!git checkout main && git pull origin main'

# Then just run:
git sync
```

### 4. Directory Sync Check
```bash
# Compare both directories are on same version:
cd ~/signalhireagent && git log --oneline -1
cd ~/Projects/signalhireagenttests2/signalhireagent && git log --oneline -1
# Both should show identical commit hash
```

## Testing Workflow

### Performance Testing
```bash
# Test that commands start fast (should show "Using Python: ..." only)
./signalhire-agent search --help | head -5

# Test that doctor command still checks dependencies
./signalhire-agent doctor
```

### Version Verification
```bash
# Check current version:
git describe --tags  # Should show v0.2.0 or newer

# Test the latest features working:
./signalhire-agent search --title "Engineer" --dry-run
# Should start instantly with search profile limit tracking

# Test contact deduplication (latest feature):
./signalhire-agent dedupe --help
# Should show deduplication commands
```

### Cross-Directory Testing
```bash
# Test both directories behave identically:
cd ~/signalhireagent && ./signalhire-agent search --help | head -3
cd ~/Projects/signalhireagenttests2/signalhireagent && ./signalhire-agent search --help | head -3
# Output should be identical
```

## Release Process

### Semantic Versioning Strategy
Follow semantic versioning format: `v0.0.1`, `v0.0.2`, `v0.0.3`, etc.

**Version Increment Rules:**
- **Patch (0.0.X)**: Bug fixes, minor improvements, documentation updates
- **Minor (0.X.0)**: New features, significant enhancements (when patch reaches .10+)  
- **Major (X.0.0)**: Breaking changes, major rewrites (when minor reaches .10+)

### Current Version Status
- **Latest Release**: `v0.2.0` (Contact Deduplication & Search Limit Tracking)
- **Next Release**: `v0.2.1` (for next bug fix/improvement)
- **Next Minor**: `v0.3.0` (for next major feature)

### Changes Since v0.2.0 (Pending for v0.2.1)
**📝 Documentation Improvements (No Release Required):**
- ✅ Updated CLI commands reference with AI agent guidance  
- ✅ Enhanced testing and release guide with semantic versioning
- ✅ Added comprehensive command mapping for natural language requests
- ✅ Improved Boolean search operator documentation
- ✅ Added reminder to always push commits to remote

**🔧 Code Changes (Will Trigger v0.2.1 When Accumulated):**
- ✅ Added production build script with version tracking
- ✅ Added GitHub Actions workflow for automated releases
- ✅ Created clean development/production separation

**Release Readiness:** Ready for v0.2.1 - includes production build system

### When to Create Releases vs Regular Commits

**🚫 NO RELEASE NEEDED (Regular Commit Only):**
- Documentation updates (README, CLI docs, guides)
- Comment additions or improvements
- Code formatting/linting fixes
- Test improvements (without functionality changes)
- Configuration file updates
- Minor refactoring without user-facing changes

**✅ CREATE RELEASE (Version Tag Required):**
- New CLI commands or features
- Bug fixes in actual functionality
- API endpoint changes
- Performance improvements
- Security fixes
- Breaking changes

### Standard Workflow Examples

**Documentation/Minor Changes (No Release):**
```bash
# 1. Make changes and commit
git add .
git commit -m "docs: update CLI reference with AI agent guidance

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# 2. Push to main (no tag needed)
git push origin main

# Status: Still on v0.2.0 + improvements
```

**Production Build & Testing (New Workflow):**
```bash
# 1. Create production build locally
./scripts/build-production.sh ~/Projects/signalhireagenttests2/signalhireagent/ --latest --force

# 2. Test in production-like environment
cd ~/Projects/signalhireagenttests2/signalhireagent/
./install.sh
cp .env.example .env
# Add SIGNALHIRE_API_KEY to .env
./signalhire-agent search --title "Engineer" --dry-run

# 3. Verify version info
python3 version.py
```

**Feature/Bug Fix Changes (Create Release):**
```bash
# 1. Update version in documentation first (if user-facing)
# Update README.md, QUICKSTART.md version references

# 2. Commit all changes
git add .
git commit -m "feat: add new search filter options

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. Create annotated tag with proper increment
git tag -a v0.2.1 -m "Release v0.2.1: Enhanced Search Filters

## ✨ New Features
- Added company size filter
- Added remote work filter

## 🐛 Bug Fixes  
- Fixed pagination issue in large searches
- Improved error handling for invalid locations

## 🛠 Technical Improvements
- Enhanced search parameter validation
- Improved logging for debug mode

🤖 Generated with Claude Code"

# 4. Push commit and tag
git push origin main
git push origin v0.2.1
```

### Version Examples by Change Type
```bash
# Bug fixes, documentation updates
v0.2.0 → v0.2.1 → v0.2.2 → v0.2.3

# New features (after reaching v0.2.10 or significant feature)
v0.2.10 → v0.3.0 → v0.3.1 → v0.3.2

# Breaking changes (after reaching v0.10.0 or major rewrite)  
v0.9.10 → v1.0.0 → v1.0.1 → v1.0.2
```

### Documentation Updates
1. Always update docs BEFORE releasing
2. Test commands in documentation actually work
3. Verify both directories have identical documentation

### Release Decision Tree

**Ask yourself: "Did I change any actual code functionality?"**

```
┌─ Documentation only? ──────────────────┐
│  (README, guides, comments, help text) │
└─────────────────────────┬──────────────┘
                          │
                          ▼
                    ✅ Just commit & push
                    📝 No release needed
                    🏷️  Stay on current version

┌─ Code changes? ────────────────────────┐
│  (CLI commands, bug fixes, features)   │  
└─────────────────────────┬──────────────┘
                          │
                          ▼
                   ✅ Commit, tag & push  
                   🏷️  Create new version
                   📋 Update release notes
```

### Pre-Release Checklist (Only for Code Changes)
- [ ] Both directories on `main` branch
- [ ] Both directories have identical `git log --oneline -1`
- [ ] Performance tests pass in both directories  
- [ ] Documentation updated with correct version number
- [ ] Version incremented properly (0.0.X format)
- [ ] All new features tested with live API calls
- [ ] Documentation matches actual command behavior
- [ ] All workarounds removed, clean solution implemented
- [ ] Release notes written with clear changelog

## Common Issues and Solutions

### Issue: Files Not Updating After `git pull`
**Cause**: Detached HEAD state
**Solution**:
```bash
git checkout main
git pull origin main
```

### Issue: Different Content in Multiple Directories
**Cause**: Directories on different branches/commits
**Solution**:
```bash
# In each directory:
git checkout main
git pull origin main
git describe --tags  # Verify same version
```

### Issue: Old Commands in Documentation
**Cause**: Documentation not updated in commit
**Solution**:
```bash
# Check if docs were actually updated:
git log -1 --name-only | grep -E "\.(md|txt)$"

# If missing, update manually and commit
```

## Quick Reference

### Health Check Commands
```bash
# Full status check
git status && git branch -v && git describe --tags

# Sync both directories
cd ~/signalhireagent && git sync
cd ~/Projects/signalhireagenttests2/signalhireagent && git sync

# Performance test
./signalhire-agent search --title "test" --dry-run
```

### Version Quick Reference
```bash
# Current version format: v0.2.0

# Next patch release (bug fixes):
v0.2.1, v0.2.2, v0.2.3, etc.

# Next minor release (new features):  
v0.3.0, v0.4.0, v0.5.0, etc.

# Next major release (breaking changes):
v1.0.0, v2.0.0, v3.0.0, etc.

# Check latest tag:
git tag --list | sort -V | tail -1

# Create next patch version:
NEXT_VERSION=$(git tag --list | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+$" | sort -V | tail -1 | awk -F. '{print $1"."$2"."$3+1}')
echo "Next version: $NEXT_VERSION"
```

### Emergency Recovery
```bash
# If completely confused about git state:
git checkout main
git reset --hard origin/main  # ⚠️  Loses local changes
git pull origin main
```

---

## Recent Feature Releases

### 004-enterprise-contact-deduplication (Latest)
**Released**: September 15, 2025  
**Status**: ✅ Complete - Merged to main

**Features Added**:
- Multi-file JSON deduplication with uid-based merging
- Job title filtering with configurable exclusion lists  
- Progress tracking for large operations with resume capability
- CLI commands: `signalhire-agent dedupe`, `analyze`, `filter`
- Full test coverage: integration, unit, and performance tests

**Testing Performed**:
- ✅ All existing tests pass (12 passed, 2 skipped)
- ✅ Integration testing with real workflows validated
- ✅ Performance test for 7,000+ contacts completed
- ✅ Bug fixes applied and validated

**CLI Validation**:
```bash
# Validated working commands:
signalhire-agent dedupe merge --input "file1,file2" --output result.json
signalhire-agent filter job-title --input data.json --exclude-job-titles "operator,driver"
signalhire-agent analyze job-titles --input contacts.json
```

## Notes
- Keep this file updated as workflows evolve
- Add new testing patterns as you discover them
- Document any recurring issues and their solutions