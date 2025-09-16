# Build Scripts (Legacy - Use `ops` Command Instead)

**These scripts are now integrated into the simplified `ops` CLI system.**

## 🚀 Recommended: Use `ops` Command

Instead of these individual scripts, use the unified `ops` command:

```bash
# Quality assurance
ops qa

# Build production
ops build --target ~/deploy/signalhire

# Verify production build
ops verify-prod ~/deploy/signalhire

# Create release
ops release patch
```

## 📁 Legacy Scripts (Still Available)

These scripts are maintained for backward compatibility but the `ops` command is recommended:

| Script | Purpose | New `ops` Equivalent |
|--------|---------|---------------------|
| `build-production.sh` | Production builds | `ops build` |
| `auto-sync-config.sh` | Target management | `ops sync` |
| `auto-release-manager.sh` | Release management | `ops release` |
| `continuous-deployment.sh` | Full pipeline | `ops setup` |

## 🔄 Migration Guide

### Old Workflow:
```bash
# Complex multi-step process
./scripts/build/continuous-deployment.sh setup --target ~/deploy --auto-release
./scripts/build/auto-sync-config.sh add ~/deploy
./scripts/build/build-production.sh ~/deploy --latest --force
```

### New Workflow:
```bash
# Simple single command
ops setup ~/deploy
ops build --target ~/deploy
```

## 📚 Documentation

For the new simplified system, see:
- `.automation/README.md` - Complete workflow guide
- `docs/developer/TESTING_AND_RELEASE.md` - Updated release process
- `scripts/README.md` - `ops` command reference

## 🏷️ Auto-Release System

Automatically creates semantic version tags based on commit patterns.

```bash
# Check if release is needed
./scripts/build/auto-release-manager.sh check

# Create release (auto-detects version bump)
./scripts/build/auto-release-manager.sh create

# Force specific version bump
./scripts/build/auto-release-manager.sh create major|minor|patch

# Setup automatic release detection
./scripts/build/auto-release-manager.sh setup
```

### Semantic Versioning Rules:
- **Major**: Commits with `BREAKING` or `!` in message
- **Minor**: Commits starting with `feat:` or `feature:`
- **Patch**: Commits starting with `fix:` or `bugfix:`
- **Patch**: Any other changes (default)

### Release Process:
1. Analyzes commits since last release
2. Generates release notes automatically
3. Creates and pushes git tag
4. Triggers GitHub Actions workflow
5. Creates GitHub release with changelog

## 🚀 Continuous Deployment

Complete automation orchestrating all systems together.

```bash
# Setup everything for a deployment target
./scripts/build/continuous-deployment.sh setup --target ~/staging --auto-release

# Manual deployment trigger
./scripts/build/continuous-deployment.sh deploy

# Check status of all automation
./scripts/build/continuous-deployment.sh status

# Watch mode (live monitoring)
./scripts/build/continuous-deployment.sh watch
```

## 🛠️ Developer Convenience

After running the setup, these convenience scripts are created in the scripts directory:

```bash
# Quick deployment to any directory
./scripts/deploy ~/target-directory

# Setup continuous deployment for new target
./scripts/setup-cd ~/new-deployment-target
```

## 📋 Configuration Files

The automation system creates these configuration files:

- `.automation/config/auto-sync-targets` - List of directories to sync automatically
- `.automation/config/continuous-deployment` - Main CD configuration  
- `.automation/state/last-auto-sync` - Tracks last sync commit
- `.automation/state/last-release-check` - Tracks release checking state
- `.git/hooks/post-commit` - Automatic git hooks

## 🔍 Status & Monitoring

Check the status of all automation systems:

```bash
# Overall status
./scripts/build/continuous-deployment.sh status

# Auto-sync specific status
./scripts/build/auto-sync-config.sh status

# Release management status  
./scripts/build/auto-release-manager.sh status
```

## 🎯 Complete Workflow Example

1. **Initial Setup** (one-time):
   ```bash
   ./scripts/build/continuous-deployment.sh setup --target ~/staging --auto-release
   ```

2. **Daily Development** (automatic):
   ```bash
   # Make your changes
   git add .
   git commit -m "feat: add new search feature"
   # → Automatically syncs to ~/staging
   # → Automatically creates release if significant
   # → Automatically triggers GitHub Actions
   ```

3. **Production Deployment**:
   ```bash
   # Add production target
   ./scripts/build/auto-sync-config.sh add /var/www/production
   # Now production auto-updates too!
   ```

## 🔧 Troubleshooting

### Sync Not Working
```bash
# Check sync status
./scripts/build/auto-sync-config.sh status

# Manual sync to test
./scripts/build/auto-sync-config.sh sync

# Reinstall git hooks
./scripts/build/auto-sync-config.sh setup-hooks
```

### Releases Not Creating
```bash
# Check release status
./scripts/build/auto-release-manager.sh status

# Manual release check
./scripts/build/auto-release-manager.sh check

# Reinstall release hooks
./scripts/build/auto-release-manager.sh setup
```

### Production Build Issues
```bash
# Test production build manually
./scripts/build/build-production.sh test-build --latest --force
cd test-build && ./install.sh && ./signalhire-agent --help
```

## 📚 Integration with Existing Systems

- **GitHub Actions**: Automatically triggered by release tags
- **Production Build**: Uses existing `build-production.sh` 
- **Environment Config**: Automatically copies `.env` files
- **Virtual Environments**: Handles `venv` setup automatically
- **CI/CD**: Compatible with existing GitHub workflows

## 🚨 Important Notes

- **Git hooks are local** - each developer needs to run setup
- **Target directories should exist** or be creatable by the user
- **Remote git repository required** for GitHub Actions integration
- **Virtual environment support** requires `python3-venv` package