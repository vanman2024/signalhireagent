# Testing and Release Workflow Guide

**Simplified workflow for solo development with AI CLI agents.**

## 🎯 Simplified Approach

This guide covers the **simplified workflow** using the `ops` command for:
- Quality assurance (linting, testing, formatting)
- Local production builds
- Version management and releases
- Environment troubleshooting

## 📋 Daily Development Workflow

### Quality Assurance
```bash
# Run all quality checks (lint, test, format)
ops qa

# This runs:
# - ruff check src/ --fix (linting)
# - black src/ (formatting)
# - mypy src/ (type checking)
# - python3 run.py -m pytest -m "not slow" (tests)
```

### Local Production Testing
```bash
# Build production version
ops build --target ~/Projects/signalhireagenttests2/signalhireagent/

# Test the production build
ops verify-prod --target ~/Projects/signalhireagenttests2/signalhireagent/

# This validates:
# - install.sh works
# - signalhire-agent --help runs
# - Basic CLI functionality
```

### Check System Status
```bash
# See current state
ops status

# Shows:
# - Current version (from pyproject.toml)
# - Git status
# - Configured targets
# - Environment info
```

## 🚀 Release Process

### When to Create Releases

**✅ CREATE RELEASE (Version Tag Required):**
- New CLI commands or features
- Bug fixes in actual functionality
- API endpoint changes
- Performance improvements
- Security fixes
- Breaking changes

**🚫 NO RELEASE NEEDED (Regular Commit Only):**
- Documentation updates
- Code formatting/linting fixes
- Test improvements (internal only)
- Configuration file updates
- Minor refactoring without user-facing changes

### Release Commands

```bash
# For bug fixes and patches
ops release patch    # v0.3.0 → v0.3.1

# For new features
ops release minor    # v0.3.0 → v0.4.0

# For breaking changes
ops release major    # v0.3.0 → v1.0.0
```

### What Release Does

The `ops release` command:
1. **Updates pyproject.toml** with new version
2. **Creates git tag** with proper semantic versioning
3. **Generates changelog** from conventional commits
4. **Pushes to remote** (if configured)
5. **Creates GitHub release** (if enabled in config)

## 🔧 Configuration

All settings in `.automation/config.yml`:

```yaml
versioning:
  strategy: conventional_commits
  source: pyproject.toml  # Single source of truth

targets:
  - ~/Projects/signalhireagenttests2/signalhireagent/

release:
  changelog: true
  tag_prefix: v
  auto_push: true

qa:
  lint: true
  typecheck: true
  tests: "not slow"
```

## 🐛 Troubleshooting

### WSL/Windows Environment Issues
```bash
# Diagnose environment problems
ops env doctor

# This checks:
# - Python path issues between WSL and Windows
# - .env file accessibility
# - Virtual environment setup
# - Path conflicts
```

### Build Problems
```bash
# Test build in temporary directory
ops build --target /tmp/test-build
cd /tmp/test-build
./install.sh
./signalhire-agent --help
```

### Version Sync Issues
```bash
# Check version consistency
ops status

# Shows version in:
# - pyproject.toml
# - Git tags
# - Current git describe
```

## 📊 Current Version Status

- **Current Version**: `0.3.0` (synced in pyproject.toml)
- **Latest Git Tag**: `v0.3.0`
- **Git Status**: 4 commits ahead of v0.3.0

### Next Release Decision

**Ask yourself**: "Did these 4 commits add user-visible functionality?"

- **If YES** → `ops release patch` (→ v0.3.1)
- **If NO** → Stay on v0.3.0 until functional changes

## 🔄 Migration from Old System

### Old Complex Workflow
```bash
# Multiple manual steps
./scripts/build/build-production.sh target --latest --force
cd target
./install.sh
./signalhire-agent --help
git tag -a v0.3.1 -m "Release v0.3.1"
git push origin main
git push origin v0.3.1
```

### New Simplified Workflow
```bash
# Single command
ops release patch
```

## 📈 Best Practices

### 1. Commit Often, Release When Ready
```bash
# Daily commits for work-in-progress
git add .
git commit -m "feat: implement new CLI command"

# Release only when feature is complete and tested
ops release minor
```

### 2. Test Locally Before Release
```bash
# Always test production build locally first
ops build --target ~/test-deploy
ops verify-prod --target ~/test-deploy
```

### 3. Use Conventional Commits
```bash
# These automatically generate changelogs
git commit -m "feat: add contact deduplication"
git commit -m "fix: resolve pagination issue"
git commit -m "docs: update CLI reference"
```

## 🚫 What We Removed

### No More Complex Multi-Directory Sync
- ❌ Manual directory syncing
- ❌ Detached HEAD state management
- ❌ Complex git branch workflows

### No More Hidden Automation
- ❌ Automatic git hooks
- ❌ Background sync processes
- ❌ Implicit deployments

### No More Fragmented Configuration
- ❌ Version scattered across multiple files
- ❌ Config split across directories
- ❌ Inconsistent settings

## ✅ What We Keep

### Simple, Explicit Commands
- ✅ `ops qa` - Quality assurance
- ✅ `ops build` - Production builds
- ✅ `ops release` - Version management
- ✅ `ops status` - System overview
- ✅ `ops env doctor` - Environment troubleshooting

### Local-First Development
- ✅ Everything works locally first
- ✅ No external dependencies for basic workflow
- ✅ Clear error messages and debugging

### Single Source of Truth
- ✅ pyproject.toml for version
- ✅ .automation/config.yml for settings
- ✅ Conventional commits for changelog

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

### GitHub Actions Workflow
The repository includes automated release builds via `.github/workflows/release.yml`:
- **Triggers**: Automatically on version tags (`v*`) or manual workflow dispatch
- **Builds**: Production deployment packages with clean dependencies
- **Tests**: Validates build integrity, install script, CLI wrapper, and auto-generated .env
- **Releases**: Creates GitHub releases with downloadable tar.gz and zip packages
- **Artifacts**: Stores production builds for 30 days

### Current Version Status
- **Latest Release**: `v0.2.0` (Contact Deduplication & Search Limit Tracking)
- **Next Release**: `v0.2.1` (for production build system improvements)
- **Next Minor**: `v0.3.0` (for next major feature)

### Changes Since v0.2.0 (Ready for v0.2.1)
**🚀 Production Build System (Major Infrastructure Improvement):**
- ✅ Complete production build script with version tracking and environment handling
- ✅ Automatic environment configuration (copies dev .env to production .env)
- ✅ Virtual environment support with fallback to system-wide installation
- ✅ Complete dependency specification including all required packages (rich, fastapi, etc.)
- ✅ Remove development files (tests, specs, version.py) from production deployment
- ✅ GitHub Actions workflow for automated release builds and packaging

**🤖 AI Agent Integration Enhancements:**
- ✅ Updated CLI commands reference with comprehensive AI agent guidance
- ✅ Enhanced agent instruction files (CLAUDE.md, AGENTS.md, copilot-instructions.md)
- ✅ Added natural language to CLI command mappings for all agents

**📝 Documentation Updates:**
- ✅ Enhanced testing and release guide with GitHub Actions workflow info
- ✅ Added comprehensive production deployment documentation
- ✅ Updated semantic versioning strategy and decision trees

**Release Readiness:** ✅ **READY FOR v0.2.1** - Complete production build system with robust environment handling

### Testing GitHub Actions Workflow

**To test the release workflow:**
```bash
# Method 1: Create and push a test tag (triggers automatic build)
git tag v0.2.1-test
git push origin v0.2.1-test

# Method 2: Manual workflow dispatch via GitHub UI
# Go to Actions tab → Release and Package → Run workflow

# Method 3: Test with gh CLI
gh workflow run release.yml
```

**Workflow Validation Checklist:**
- [ ] Build completes without errors
- [ ] Production deployment includes all required files
- [ ] install.sh is executable and works with virtual environments
- [ ] .env file is auto-created with proper credentials
- [ ] CLI wrapper (signalhire-agent) is executable
- [ ] Release artifacts (tar.gz, zip) are created
- [ ] GitHub release is published with correct version

**Production Build Testing:**
```bash
# Test locally before creating release
./scripts/build/build-production.sh test-build --latest --force
cd test-build
./install.sh
./signalhire-agent --help
```

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
