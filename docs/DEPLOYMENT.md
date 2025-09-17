# SignalHire Agent Deployment Guide

## Systematic Deployment Cycle

### 1. Development → Release Process

```bash
# 1. Make changes and test thoroughly
./scripts/test.sh

# 2. Deploy new version (auto-increments version, creates tag, triggers CI/CD)
./scripts/deploy.sh patch   # or minor, major

# 3. GitHub Actions automatically:
#    - Runs tests
#    - Creates production build using scripts/build/build-production.sh
#    - Creates GitHub release with downloadable artifacts
#    - Uploads build artifacts
```

### 2. Production Deployment

```bash
# Deploy latest release to production
./scripts/deploy-to-production.sh /path/to/production

# Deploy specific version
./scripts/deploy-to-production.sh /path/to/production v0.4.5
```

## Version Control System

### Version Bumping
- **Patch**: Bug fixes, small improvements (`0.4.5` → `0.4.6`)
- **Minor**: New features, backward compatible (`0.4.5` → `0.5.0`)
- **Major**: Breaking changes (`0.4.5` → `1.0.0`)

### Git Flow
1. All changes happen in feature branches
2. Merge to `main` branch
3. Deploy script:
   - Updates `pyproject.toml` version
   - Commits version bump
   - Creates git tag `vX.Y.Z`
   - Pushes to origin
4. GitHub Actions triggers on tag push
5. Production build created automatically

## CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/release.yml`)
1. **Trigger**: Git tag push (`v*`)
2. **Quality Checks**: Linting, type checking, unit tests
3. **Production Build**: Uses `scripts/build/build-production.sh`
4. **Verification**: Tests the built package
5. **Release**: Creates GitHub release with downloadable artifacts
6. **Artifacts**: Stores build for 30 days

### Production Build Process
- **Input**: Full development repository
- **Output**: Clean production package with only runtime files
- **Includes**: `src/`, `requirements.txt`, `install.sh`, CLI wrapper
- **Excludes**: `tests/`, `specs/`, dev dependencies, cache files

## Production Environment

### Directory Structure
```
/production/signalhireagent/
├── src/                 # Application code
├── requirements.txt     # Production dependencies
├── install.sh          # Setup script
├── signalhire-agent    # CLI wrapper
├── .env                # Environment configuration
├── VERSION             # Version metadata
└── docs/               # Essential documentation
```

### Installation Process
1. Extract production build
2. Run `./install.sh` (creates venv, installs deps)
3. Configure `.env` file
4. Test with `./signalhire-agent --help`

## Deployment Commands

### For Developers
```bash
# Release new version
./scripts/deploy.sh patch

# Manual production deployment
./scripts/deploy-to-production.sh /path/to/prod

# Build production package locally
./scripts/build/build-production.sh ./dist --version v1.0.0
```

### For Production Ops
```bash
# Deploy specific version to production
curl -L https://github.com/user/repo/releases/download/v1.0.0/signalhire-agent-v1.0.0-production.tar.gz | tar -xz
cd signalhireagent
./install.sh
```

## Version Tracking

### Development
- Version in `pyproject.toml`
- Git tags (`vX.Y.Z`)
- Commit history with version bumps

### Production
- `VERSION` file with JSON metadata
- Git tag reference
- Build timestamp
- GitHub release link

## Rollback Process

```bash
# List available backups
ls -la /production/*.backup.*

# Rollback to previous version
mv /production/signalhireagent /production/signalhireagent.failed
mv /production/signalhireagent.backup.YYYYMMDD_HHMMSS /production/signalhireagent

# Or deploy specific older version
./scripts/deploy-to-production.sh /production/signalhireagent v0.4.4
```

## Monitoring & Health Checks

### Post-Deployment Verification
```bash
cd /production/signalhireagent
./signalhire-agent --help                    # Basic functionality
./signalhire-agent status --credits         # API connectivity
./signalhire-agent doctor                   # Full system check
```

### Version Verification
```bash
# Check deployed version
cat VERSION

# Compare with latest release
curl -s https://api.github.com/repos/user/repo/releases/latest | jq .tag_name
```

## Security Considerations

- `.env` files are preserved during deployment
- Backups are created automatically
- Production builds exclude development secrets
- Virtual environments isolate dependencies
- File permissions are set correctly

## Troubleshooting

### Common Issues
1. **Permission errors**: Run `chmod +x install.sh signalhire-agent`
2. **Missing .env**: Copy from backup or recreate from template
3. **Import errors**: Ensure virtual environment is activated
4. **API issues**: Check credentials and network connectivity

### Recovery
1. Check backup directories
2. Redeploy from known good version
3. Verify .env configuration
4. Run full system diagnostics with `./signalhire-agent doctor`