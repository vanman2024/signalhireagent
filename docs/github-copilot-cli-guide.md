# 🚀 GitHub Copilot CLI Complete Guide

A comprehensive guide to setting up and using GitHub Copilot CLI for AI-powered command line assistance.

## 📋 Prerequisites

- **GitHub Account** with Copilot subscription
- **GitHub CLI** installed (`gh`)
- **Terminal access** (Linux/macOS/WSL)

## 🛠️ Installation & Setup

### 1. Install GitHub CLI

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install gh
```

#### macOS
```bash
brew install gh
```

#### Windows (WSL)
```bash
sudo apt install gh
```

### 2. Authenticate with GitHub
```bash
gh auth login
```
Follow the prompts to authenticate via browser.

### 3. Install Copilot Extension
```bash
gh extension install github/gh-copilot
```

### 4. Verify Installation
```bash
gh copilot --version
gh copilot --help
```

## 🎯 Core Commands

### Command Suggestions

Generate shell commands from natural language:

```bash
# Basic syntax
gh copilot suggest -t <target> "<description>"

# Targets: shell, git, gh
```

#### Shell Commands
```bash
gh copilot suggest -t shell "find large files over 100MB"
gh copilot suggest -t shell "batch rename files with timestamp"
gh copilot suggest -t shell "compress all JSON files in directory"
gh copilot suggest -t shell "convert CSV to JSON using Python"
gh copilot suggest -t shell "monitor system resources in real-time"
```

#### Git Commands
```bash
gh copilot suggest -t git "undo last commit but keep changes"
gh copilot suggest -t git "create branch from specific commit"
gh copilot suggest -t git "squash last 3 commits"
gh copilot suggest -t git "cherry pick commit to another branch"
```

#### GitHub CLI Commands
```bash
gh copilot suggest -t gh "create pull request with specific title"
gh copilot suggest -t gh "list my open issues"
gh copilot suggest -t gh "clone repository and create new branch"
```

### Command Explanations

Understand complex commands:

```bash
gh copilot explain "<command>"
```

#### Examples
```bash
gh copilot explain "signalhire search --title 'Heavy Equipment'"
gh copilot explain "grep -r 'contactsFetched' src/ | head -10"
gh copilot explain "git log --oneline --graph --all --decorate"
gh copilot explain "docker run -d -p 8080:80 nginx"
```

## 🔧 Configuration

### Set Preferences
```bash
gh copilot config
```

Options:
- **Usage Analytics**: Allow GitHub to collect usage data
- **Command Execution**: Default confirmation behavior

### Create Convenient Aliases
```bash
gh copilot alias
```

This generates shell aliases:
```bash
alias '??'='gh copilot suggest -t shell'
alias 'git?'='gh copilot suggest -t git'
alias 'gh?'='gh copilot suggest -t gh'
```

Add to your `.bashrc` or `.zshrc`:
```bash
echo 'alias "??"="gh copilot suggest -t shell"' >> ~/.bashrc
echo 'alias "git?"="gh copilot suggest -t git"' >> ~/.bashrc
echo 'alias "gh?"="gh copilot suggest -t gh"' >> ~/.bashrc
source ~/.bashrc
```

## 💡 Real-World Examples

### Data Processing & Analysis

```bash
# JSON/CSV manipulation
gh copilot suggest -t shell "merge multiple JSON files removing duplicates by UID"
gh copilot suggest -t shell "convert JSON to CSV with specific columns"
gh copilot suggest -t shell "find differences between two CSV files"

# File operations
gh copilot suggest -t shell "batch convert images from PNG to JPG"
gh copilot suggest -t shell "find and delete empty directories"
gh copilot suggest -t shell "backup files modified in last 7 days"
```

### Development Workflows

```bash
# Python development
gh copilot suggest -t shell "create virtual environment and install requirements"
gh copilot suggest -t shell "run Python tests with coverage report"
gh copilot suggest -t shell "format Python code with black and isort"

# Docker operations
gh copilot suggest -t shell "build Docker image and run container"
gh copilot suggest -t shell "clean up unused Docker images"
```

### Git & GitHub Workflows

```bash
# Advanced Git operations
gh copilot suggest -t git "interactive rebase to edit commit messages"
gh copilot suggest -t git "stash changes with descriptive message"
gh copilot suggest -t git "merge feature branch with no fast-forward"

# GitHub collaboration
gh copilot suggest -t gh "create issue from template"
gh copilot suggest -t gh "review pull request and add comments"
```

## 🚀 SignalHire Project Examples

### Project-Specific Commands

```bash
# Data analysis for our Heavy Equipment project
gh copilot suggest -t shell "count prospects by province in JSON file"
gh copilot suggest -t shell "extract LinkedIn URLs from SignalHire export"
gh copilot suggest -t shell "merge search results and remove duplicates by UID"

# API testing
gh copilot suggest -t shell "test SignalHire API endpoints with curl"
gh copilot suggest -t shell "monitor API rate limits and usage"

# File organization
gh copilot suggest -t shell "organize SignalHire results by date and region"
```

### Command Explanations for Our CLI

```bash
# Explain our complex search commands
gh copilot explain "signalhire search --title '(Heavy Equipment Mechanic) OR (Heavy Equipment Technician)' --location Canada --size 100 --all-pages"

# Explain reveal operations
gh copilot explain "signalhire reveal --search-file prospects.json --skip-existing --output contacts.csv"

# Explain our commit patterns
gh copilot explain "git commit -m 'feat: improve CLI to handle existing contacts and save credits'"
```

## 📊 Interactive Mode

For guided assistance, run commands without parameters:

```bash
# Interactive suggestion
gh copilot suggest

# Interactive explanation
gh copilot explain
```

The CLI will prompt you to:
1. Choose command type (shell/git/gh)
2. Provide your description
3. Select from suggested actions

## ⚠️ Best Practices

### Security & Safety
- **Always review** generated commands before execution
- **Test on sample data** before running on production files
- **Understand the command** - use `gh copilot explain` if unsure
- **Backup important data** before running destructive operations

### Optimization Tips
- **Be specific** in your descriptions for better suggestions
- **Use context** - run from relevant directories
- **Iterate** - refine your requests if first suggestion isn't perfect
- **Combine with domain knowledge** - Copilot + your expertise = best results

### Integration Workflow
1. **Describe what you need** in natural language
2. **Review the suggestion** carefully
3. **Test with safe data** first
4. **Execute and verify** results
5. **Save useful commands** as aliases or scripts

## 🔍 Troubleshooting

### Common Issues

#### Authentication Problems
```bash
# Re-authenticate if needed
gh auth logout
gh auth login
```

#### Extension Not Found
```bash
# Reinstall extension
gh extension remove github/gh-copilot
gh extension install github/gh-copilot
```

#### Interactive Mode Issues
```bash
# Use explicit flags instead
gh copilot suggest -t shell "your request"
# Instead of just: gh copilot suggest
```

### Getting Help
```bash
gh copilot --help
gh copilot suggest --help
gh copilot explain --help
```

## 🎯 Advanced Usage

### Chaining with Other Tools

```bash
# Generate command and save to file
gh copilot suggest -t shell "backup database" -s backup_script.sh

# Explain piped commands
ps aux | grep python | gh copilot explain
```

### Custom Workflows

Create project-specific aliases:
```bash
# .bashrc additions for SignalHire project
alias signalhire-search='gh copilot suggest -t shell "SignalHire search command"'
alias api-explain='gh copilot explain'
```

## 📚 Resources

- **Official Documentation**: [GitHub Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli)
- **GitHub CLI**: [cli.github.com](https://cli.github.com/)
- **Copilot Subscription**: [GitHub Copilot Plans](https://github.com/features/copilot)

---

## 🚀 Quick Start Checklist

- [ ] Install GitHub CLI
- [ ] Authenticate with `gh auth login`
- [ ] Install extension: `gh extension install github/gh-copilot`
- [ ] Test: `gh copilot suggest -t shell "list files"`
- [ ] Set up aliases: `gh copilot alias`
- [ ] Add aliases to shell config
- [ ] Start using with your projects!

**Happy coding with AI assistance!** 🤖✨
