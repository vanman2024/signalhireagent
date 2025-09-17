# Deploy System

**Deployment and build management for SignalHire Agent.**

## 🎯 **Main Command**

```bash
./deploy/deploy <command> [options]
```

## 📋 **Commands**

```bash
# Production deployment
deploy production [target]    # Full production deployment
deploy simple [target]        # Simple file-based deployment  
deploy build [target]         # Build production version only
```

## 🚀 **Usage Examples**

```bash
# Deploy to production environment
deploy production ~/Projects/signalhireagenttests2/signalhireagent

# Simple deployment for testing
deploy simple ~/test-deploy

# Build only (no deployment)
deploy build ~/build-output --force
```

## 📁 **File Structure**

```
deploy/
├── README.md                           # This file
├── deploy                              # Main deploy command
├── commands/                           # Individual deployment scripts
│   ├── build-production.sh            # Production build script
│   ├── deploy-to-production.sh        # Main deployment script
│   └── deploy-to-production-simple.sh # Simple deployment script
└── docs/                              # Deploy documentation
    └── build-legacy-readme.md         # Legacy build system docs
```

## 🔧 **Deployment Features**

### Production Build (`build-production.sh`)
- Creates clean production deployment
- Copies only essential files (src/, docs/, configs)
- Auto-creates .env with development credentials
- Removes development files (tests/, specs/)
- Creates install.sh and CLI wrapper
- Handles WSL/Windows Python environment issues

### Production Deployment (`deploy-to-production.sh`)
- Uses production build system
- Preserves user files (CLAUDE.md, AGENTS.md, *.txt)
- Updates only system files (src/, VERSION, requirements.txt)
- Maintains existing configuration and data

### Simple Deployment (`deploy-to-production-simple.sh`)
- Lightweight file copying
- Whitelist approach for file updates
- Preserves all user-created content

## 🏷️ **Version Tracking**

- Reads version from `pyproject.toml`
- Auto-creates git tags for releases
- Updates VERSION file with build metadata
- Tracks commit hash and build date

## 🔗 **Integration**

- **Ops System**: Use `ops build` for workflow integration
- **GitHub Actions**: Triggered by version tags
- **Local Development**: Test builds locally before release

## 🚨 **File Preservation**

The deployment system preserves:
- ✅ User instruction files (CLAUDE.md, AGENTS.md)
- ✅ User data files (*.txt, *.json)
- ✅ Configuration directories (config/, data/)
- ✅ User-created documentation

System files that get updated:
- 📦 Application code (src/)
- 📦 Dependencies (requirements.txt)
- 📦 Version information (VERSION)
- 📦 Build documentation (BUILD_INFO.md)
- 📦 Installation scripts (install.sh, signalhire-agent)

## 🛠️ **WSL/Windows Compatibility**

- Forces WSL Python usage to avoid environment mixing
- Handles virtual environment creation properly
- Prevents Windows/WSL path conflicts
- Auto-detects and configures correct Python interpreter