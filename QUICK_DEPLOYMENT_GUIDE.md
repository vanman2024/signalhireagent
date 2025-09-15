# 🚀 Quick Deployment Guide - 100% Automated

**Setup once, then everything is automatic!**

## ⚡ One-Command Setup

```bash
# Replace with your desired deployment directory
./scripts/build/continuous-deployment.sh setup --target ~/deployments/signalhire-staging --auto-release
```

**That's it!** Now every time you commit changes:
- ✅ Automatically syncs to your deployment directory
- ✅ Updates production build with latest code
- ✅ Installs dependencies in virtual environment
- ✅ Copies your .env configuration
- ✅ Creates releases for significant changes
- ✅ Triggers GitHub Actions

## 🔄 Daily Workflow (100% Automatic)

```bash
# 1. Make your changes (same as always)
vim src/cli/main.py

# 2. Commit your changes (same as always)
git add .
git commit -m "feat: add new search functionality"

# 3. Everything else happens automatically!
#    → Syncs to ~/deployments/signalhire-staging
#    → Creates production build
#    → Updates virtual environment
#    → Creates v0.x.x release tag (if significant changes)
#    → Triggers GitHub Actions workflow
```

## 📁 What Gets Created

After setup, you'll have:

```
~/deployments/signalhire-staging/
├── src/                    # Latest application code
├── .env                    # Your development credentials (auto-copied)
├── requirements.txt        # Production dependencies
├── install.sh             # Virtual environment setup
├── signalhire-agent       # CLI wrapper script
├── venv/                  # Virtual environment (auto-created)
├── VERSION                # Build information
└── BUILD_INFO.md          # Deployment details
```

## 🎯 Test Your Deployment

```bash
cd ~/deployments/signalhire-staging
./signalhire-agent --help              # Test CLI
./signalhire-agent status --credits    # Test API connection
```

## 🔧 Multiple Deployment Targets

```bash
# Add production deployment
./scripts/build/auto-sync-config.sh add /var/www/signalhire-production

# Add development environment
./scripts/build/auto-sync-config.sh add ~/dev/signalhire-test

# View all targets
./scripts/build/auto-sync-config.sh list
```

## 📊 Monitor Status

```bash
# Check overall deployment status
./scripts/build/continuous-deployment.sh status

# Check specific systems
./scripts/build/auto-sync-config.sh status
./scripts/build/auto-release-manager.sh status
```

## 🎮 Convenience Commands

After setup, these commands are available in the scripts directory:

```bash
# Quick deploy to any directory
./scripts/deploy ~/custom-deployment

# Setup new deployment target with full automation
./scripts/setup-cd ~/new-target
```

## 🏷️ Automatic Releases

The system automatically creates releases based on your commit messages:

| Commit Pattern | Version Bump | Example |
|----------------|--------------|---------|
| `feat:` or `feature:` | Minor (0.1.0 → 0.2.0) | `feat: add search filters` |
| `fix:` or `bugfix:` | Patch (0.1.0 → 0.1.1) | `fix: handle empty results` |
| `BREAKING` or `!` | Major (0.1.0 → 1.0.0) | `feat!: new API structure` |
| Other changes | Patch | `docs: update README` |

## 🚨 Troubleshooting

### Sync Not Working?
```bash
# Check sync status and targets
./scripts/build/auto-sync-config.sh status

# Manual sync to test
./scripts/build/auto-sync-config.sh sync

# Reinstall git hooks
./scripts/build/auto-sync-config.sh setup-hooks
```

### Want to Disable Automation?
```bash
# Remove deployment target
./scripts/build/auto-sync-config.sh remove ~/deployments/signalhire-staging

# Remove git hooks
rm .git/hooks/post-commit
```

## ✨ What Makes This Special

- **Zero maintenance** - setup once, works forever
- **Multiple targets** - sync to staging, production, dev environments
- **Smart releases** - only creates releases when needed
- **Environment sync** - your .env always copied correctly
- **GitHub integration** - triggers CI/CD automatically
- **Safe deployments** - virtual environments isolate dependencies
- **Instant updates** - changes appear immediately after commit

---

**Need help?** Check the detailed documentation at `scripts/build/README.md`