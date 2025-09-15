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
# Check you have the latest performance fixes:
git describe --tags  # Should show v1.2.0-fast-cli or newer

# Test the fix is working:
./signalhire-agent search --title "Engineer" --dry-run
# Should start instantly without dependency installation
```

### Cross-Directory Testing
```bash
# Test both directories behave identically:
cd ~/signalhireagent && ./signalhire-agent search --help | head -3
cd ~/Projects/signalhireagenttests2/signalhireagent && ./signalhire-agent search --help | head -3
# Output should be identical
```

## Release Process

### Tagging Strategy
```bash
# Create version tags for major improvements:
git tag -a v1.3.0-feature-name -m "Description of changes"
git push origin main --tags
```

### Documentation Updates
1. Always update docs BEFORE releasing
2. Test commands in documentation actually work
3. Verify both directories have identical documentation

### Pre-Release Checklist
- [ ] Both directories on `main` branch
- [ ] Both directories have identical `git log --oneline -1`
- [ ] Performance tests pass in both directories
- [ ] Documentation matches actual command behavior
- [ ] All workarounds removed, clean solution implemented

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