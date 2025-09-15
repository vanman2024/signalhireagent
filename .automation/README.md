# Automation Directory

This directory contains configuration and state files for the continuous deployment and auto-sync systems.

## Directory Structure

```
.automation/
├── config/          # User configuration files (gitignored)
│   ├── auto-sync-targets       # List of deployment directories
│   └── continuous-deployment   # CD system configuration
├── state/           # Runtime state files (gitignored)
│   ├── last-auto-sync         # Last commit that was synced
│   └── last-release-check     # Last commit checked for releases
└── README.md        # This documentation (tracked in git)
```

## File Descriptions

### Configuration Files (`config/`)
- **`auto-sync-targets`**: List of absolute paths to deployment directories that should be automatically synchronized on every commit
- **`continuous-deployment`**: Main configuration for the continuous deployment system including setup date and options

### State Files (`state/`)
- **`last-auto-sync`**: Git commit hash of the last commit that was successfully synced to deployment targets
- **`last-release-check`**: Git commit hash of the last commit that was checked for potential release creation

## Git Handling

- **Config and state files are gitignored** - these are user-specific and environment-specific
- **Only this README is tracked** - provides documentation without cluttering the repository
- **Directory structure is created automatically** by automation scripts

## Usage

These files are managed automatically by the automation scripts:
- `scripts/build/auto-sync-config.sh` - manages sync targets and state
- `scripts/build/auto-release-manager.sh` - manages release state
- `scripts/build/continuous-deployment.sh` - manages overall configuration

Users typically don't need to edit these files manually - use the provided scripts instead.

## Migration

This directory was created to move automation files out of the repository root for better organization:
- Old location: `.auto-sync-targets`, `.continuous-deployment`, etc. in repo root
- New location: Organized in `.automation/config/` and `.automation/state/`