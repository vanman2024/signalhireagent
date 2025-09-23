# SignalHire Agent - Cleanup Plan

## Scripts Directory Analysis & Recommendations

### 🗑️ TO DELETE (Redundant/Old)

#### `/scripts/` Root Level
- **auto-sync-to-test.sh** - OLD: Syncs to test directory that doesn't exist anymore
- **intelligent-auto-deploy.sh** - OLD: Complex deployment replaced by GitHub/pipx
- **setup-production-workspace.sh** - OLD: Production setup now handled by pip install
- **add-ops-only.sh** - UNCLEAR: Seems to add ops system which we're not using
- **setup-cd** - TINY: Just changes directory, not needed
- **test.sh** - REDUNDANT: We use pytest directly

#### `/scripts/agents/`
- **agent-coordinator.py** - OLD: Multi-agent stuff not relevant to SignalHire
- **update-agent-context*.sh** - OLD: Agent context management not needed
- **update-shared-memory.sh** - OLD: Not using shared memory pattern

#### `/scripts/development/`
- **Dockerfile**, **docker-compose.yml** - NOT USING: No Docker deployment
- **daily_job.sh** - UNCLEAR: Cron job we don't need
- **setup-ai-agents.sh** - OLD: AI agent setup not relevant
- **setup-plan.sh** - OLD: Planning system not used
- **check-task-prerequisites.sh** - OLD: Task system not used
- **get-feature-paths.sh** - OLD: Feature management not used

#### `/scripts/git/`
- **git-commit-helper.sh** - REDUNDANT: Just use git directly

#### `/scripts/data-processing/`
- Keep if contains SignalHire-specific data scripts

#### `/scripts/testing/`
- Check contents, likely redundant with pytest

### ✅ TO KEEP (Still Useful)

#### `/scripts/build/`
- **build-production.sh** - KEEP: Used by GitHub Actions workflow

#### Root Level
- **setup.sh** - MAYBE KEEP: Check if still relevant for initial setup
- **signalhire-agent** - KEEP: CLI wrapper script
- **run.py** - KEEP: Python runner with dependency management

### 📁 Hidden Directories to Clean

#### `.multiagent/`
- Contains universal release scripts that were meant for multi-project use
- Not needed for SignalHire specifically
- Can delete entire directory

#### `.specify/`
- Old specification system
- Not actively used
- Can delete

#### `.claude/`
- Check contents, might have useful context
- Keep if has project-specific guidelines

### 🎯 Proposed Clean Structure

```
signalhireagent/
├── src/                    # Source code (KEEP)
├── tests/                  # Tests (KEEP)
├── docs/                   # Documentation (KEEP)
├── .github/                # GitHub Actions (KEEP)
├── scripts/
│   └── build/
│       └── build-production.sh  # For GitHub Actions (KEEP)
├── README.md               # User docs (KEEP)
├── README.dev.md           # Dev docs (KEEP)
├── pyproject.toml          # Package config (KEEP)
├── MANIFEST.in             # Package manifest (KEEP)
├── requirements.txt        # Dependencies (KEEP)
├── .gitignore              # Git config (KEEP)
├── .env.example            # Config template (KEEP)
└── VERSION                 # Version file (KEEP)
```

### 🧹 Cleanup Commands

```bash
# Delete old scripts
rm -rf scripts/agents/
rm -rf scripts/development/
rm -rf scripts/git/
rm -f scripts/auto-sync-to-test.sh
rm -f scripts/intelligent-auto-deploy.sh
rm -f scripts/setup-production-workspace.sh
rm -f scripts/add-ops-only.sh
rm -f scripts/setup-cd
rm -f scripts/test.sh

# Delete hidden directories
rm -rf .multiagent/
rm -rf .specify/

# Delete old docs
rm -f MULTI_AGENT_INTEGRATION_SUMMARY.md
rm -f QUICKSTART.md
rm -f QUICK_DEPLOYMENT_GUIDE.md
rm -f ENVIRONMENT_SETUP.md

# Keep only essential root files
```

### 📊 Size Reduction

- **Before**: ~21MB repo with tons of scripts
- **After**: ~10MB focused on SignalHire functionality
- **Benefit**: Cleaner, easier to maintain, less confusing

## Why This Cleanup?

1. **We're using pip/pipx now** - Don't need complex deployment scripts
2. **Not a multi-agent system** - SignalHire is a focused tool
3. **GitHub Actions handles CI/CD** - Don't need manual build scripts
4. **Simpler is better** - Less to maintain, less to break