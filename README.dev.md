# SignalHire Agent - Development Guide

## 🚧 Development Setup

This document is for developers working on SignalHire Agent. For end-user documentation, see README.md.

## Package Architecture

### What Gets Packaged vs What Stays in Development

```
signalhireagent/                  # Full repo (21MB)
├── src/                          # ✅ PACKAGED (544KB) - Only this goes to users
│   ├── cli/                     # Command-line interface
│   ├── lib/                     # Core libraries
│   ├── models/                  # Data models
│   └── services/                # Business logic
├── tests/                        # ❌ NOT PACKAGED - Development only
├── docs/                         # ❌ NOT PACKAGED - Development only
├── specs/                        # ❌ NOT PACKAGED - Development only
├── scripts/                      # ❌ NOT PACKAGED - Development only
├── .github/                      # ❌ NOT PACKAGED - CI/CD workflows
├── README.md                     # ✅ PACKAGED - User-facing docs
├── README.dev.md                 # ❌ NOT PACKAGED - This file
├── VERSION                       # ✅ PACKAGED - Version info
└── pyproject.toml               # ✅ PACKAGED - Package metadata
```

## Installation Methods During Development

### 1. GitHub Installation (Current Method)
```bash
# Install latest from main branch
pipx install git+https://github.com/vanman2024/signalhireagent.git

# Install specific version/tag
pipx install git+https://github.com/vanman2024/signalhireagent.git@v2.0.0

# Install from feature branch
pipx install git+https://github.com/vanman2024/signalhireagent.git@feature-branch

# Force reinstall to get updates
pipx install --force git+https://github.com/vanman2024/signalhireagent.git
```

### 2. Local Development Installation
```bash
# Editable install for development
pip install -e .

# Or with pipx for isolation
pipx install --editable .
```

### 3. Wheel Building (Test Packaging)
```bash
# Build wheel locally
python -m build

# Install from local wheel
pipx install dist/signalhire_agent-*.whl
```

## Version Management

### Current State
- **NOT on PyPI yet** - Intentionally staying on GitHub during active development
- **Version source**: `pyproject.toml` (single source of truth)
- **Version format**: Semantic versioning (MAJOR.MINOR.PATCH)

### Version Bumping Rules
```bash
# DON'T manually edit version in:
# - pyproject.toml
# - VERSION file

# DO use git tags or CI/CD:
git tag v2.1.0
git push origin v2.1.0
# GitHub Actions will handle version updates
```

### Why Not PyPI Yet?

**Benefits of GitHub-only during development:**
1. **Instant updates** - No PyPI publish delay
2. **Branch testing** - Install any branch/commit
3. **No version pollution** - PyPI versions are forever
4. **Private repos** - Can stay private if needed
5. **Simpler workflow** - One less step in deployment

**When to publish to PyPI:**
- [ ] API is stable (no more breaking changes)
- [ ] Documentation is complete
- [ ] Major version milestone (v2.0.0, v3.0.0)
- [ ] Ready for public/production use
- [ ] Have PYPI_API_TOKEN configured

## Import Structure

All imports are now absolute from package root (no `src.` prefix):
```python
# ✅ CORRECT (works when installed)
from cli.main import main
from models.prospect import Prospect
from services.export_service import ExportService

# ❌ WRONG (will fail when pip-installed)
from src.cli.main import main       # No src prefix!
from ..models.prospect import Prospect  # No relative imports!
```

## Build Process Explained

When someone runs `pipx install git+https://github.com/vanman2024/signalhireagent.git`:

1. **Clone** - Git clones entire 21MB repo to temp directory
2. **Build** - Runs `python -m build` which:
   - Reads `pyproject.toml`
   - Finds `[tool.setuptools.packages.find] where = ["src"]`
   - Creates wheel with ONLY `src/` contents (544KB)
3. **Install** - Installs wheel into virtualenv
4. **Cleanup** - Deletes temp clone

## Testing Installation

```bash
# Test what gets packaged
python -m build
unzip -l dist/*.whl | head -50

# Test GitHub installation
pipx uninstall signalhire-agent
pipx install git+https://github.com/vanman2024/signalhireagent.git
signalhire-agent --version

# Test specific branch
pipx install --force git+https://github.com/vanman2024/signalhireagent.git@main
```

## CI/CD Workflow

### Current GitHub Actions
- **On Push to main**: Builds and tests
- **On Tag (v*)**: Creates GitHub release with artifacts
- **PyPI Publishing**: Ready but not active (needs PYPI_API_TOKEN secret)

### To Enable PyPI Publishing
1. Create account on https://pypi.org
2. Generate API token
3. Add as GitHub secret: `PYPI_API_TOKEN`
4. Tag a release: `git tag v2.0.0 && git push origin v2.0.0`

## Development Dependencies

The package has different dependency sets:
- **Core** (`dependencies`): What users get
- **Dev** (`[project.optional-dependencies] dev`): Testing, linting
- **Enterprise** (`[project.optional-dependencies] enterprise`): Future SaaS features

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install everything
pip install -e ".[all]"
```

## Common Issues

### Import Errors After Installation
- Check for `from src.` imports (remove `src.`)
- Check for relative imports `from ..` (make absolute)
- Rebuild and reinstall after fixing

### Version Not Updating
- VERSION file is NOT the source of truth
- Check `pyproject.toml` version field
- Use git tags for version management

### Package Not Found on PyPI
- We're NOT on PyPI yet (intentionally)
- Use GitHub URL for installation
- Will publish when v2.0+ is stable

## Release Strategy

### Phase 1: GitHub Only (Current)
- Rapid iteration
- Breaking changes allowed
- Version via git tags
- Install via `pipx install git+...`

### Phase 2: Beta on PyPI (Future)
- Publish as `signalhire-agent-beta`
- Semantic versioning enforced
- Deprecation warnings for breaking changes

### Phase 3: Stable on PyPI (Later)
- Publish as `signalhire-agent`
- Full documentation
- Backward compatibility commitment
- Regular release cycle

## Contributing

1. Clone the repo
2. Install in editable mode: `pip install -e ".[dev]"`
3. Make changes in `src/` only
4. Run tests: `python -m pytest`
5. Push to feature branch
6. Test installation: `pipx install git+...@your-branch`
7. Create PR when ready

## Questions?

- **Why 21MB clone for 544KB package?** Git history (13MB) + dev files. Only src/ gets packaged.
- **When will PyPI release happen?** When API stabilizes around v2.0 or v3.0
- **Can I test packaging locally?** Yes: `python -m build` then check `dist/`
- **Why no src. imports?** Package installs without src/ parent directory