# Development vs Production - How to Avoid Confusion

## The Problem
Both development and production installations have the same command name: `signalhire-agent`

## How to Tell Which Version You Have

### Method 1: Check Installation Info
```bash
# For pipx installations
pipx list | grep signalhire-agent

# Shows something like:
# signalhire-agent 1.1.2 (signalhire-agent)
#   - signalhire-agent
#   installed from: git+https://github.com/...  <- GitHub install
#   OR
#   installed from: /home/user/signalhireagent  <- Local dev install
```

### Method 2: Check Version Details
```bash
# Production (from GitHub) will show:
signalhire-agent --version
# Output: signalhire-agent, version 1.1.2

# Development (editable) would show the same BUT
# you can check if it's editable:
pip list | grep signalhire-agent
# Editable install shows: signalhire-agent 1.1.2 /path/to/local/repo
```

## Recommended Setup to Avoid Confusion

### Option 1: Use Different Names (BEST)

#### For Development:
```bash
# In development directory
cd /home/vanman2025/signalhireagent

# Create a dev wrapper script
cat > signalhire-dev << 'EOF'
#!/bin/bash
echo "🔧 DEVELOPMENT VERSION"
python -m src.cli.main "$@"
EOF

chmod +x signalhire-dev
sudo ln -sf $(pwd)/signalhire-dev /usr/local/bin/signalhire-dev

# Now use:
signalhire-dev --version  # Development
signalhire-agent --version # Production
```

### Option 2: Use Virtual Environments

#### Production (Global):
```bash
# Install globally with pipx
pipx install git+https://github.com/vanman2024/signalhireagent.git
signalhire-agent --version  # Always production
```

#### Development (Local venv):
```bash
cd /home/vanman2025/signalhireagent
python -m venv .venv
source .venv/bin/activate
pip install -e .
signalhire-agent --version  # Development when venv active
deactivate  # Back to production
```

### Option 3: Use Aliases

Add to your `~/.bashrc`:
```bash
# Production version (from GitHub)
alias sha-prod='pipx run --spec git+https://github.com/vanman2024/signalhireagent.git signalhire-agent'

# Development version (local)
alias sha-dev='cd /home/vanman2025/signalhireagent && python -m src.cli.main'

# Check which is which
alias sha-which='echo "Production:" && pipx list | grep signalhire-agent'
```

## Quick Version Check Script

Create `~/.local/bin/check-signalhire`:
```bash
#!/bin/bash
echo "=== SignalHire Agent Version Info ==="
echo ""
echo "Installed via pipx:"
pipx list 2>/dev/null | grep -A2 signalhire-agent || echo "  Not installed via pipx"
echo ""
echo "Python packages:"
pip list 2>/dev/null | grep signalhire-agent || echo "  Not in current Python env"
echo ""
echo "Command location:"
which -a signalhire-agent 2>/dev/null || echo "  Command not found"
echo ""
echo "Version test:"
signalhire-agent --version 2>/dev/null || echo "  Version command failed"
```

## Current Status

You have **PRODUCTION** version installed from GitHub because:
1. You used `pipx install --force git+https://github.com/...`
2. It's NOT an editable install
3. It's version 1.1.2 from the GitHub repo

## Best Practice Going Forward

1. **Always use pipx for production**: `pipx install --force git+...`
2. **Use venv for development**: `source .venv/bin/activate` when developing
3. **Create dev alias**: So you can run `sha-dev` for development
4. **Check before running**: `pipx list | grep signalhire` to see what's installed