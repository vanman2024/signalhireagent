# Documentation Directory

Comprehensive documentation for the SignalHire Agent project.

## Directory Structure

### 👥 `user/`
**End-user documentation** - for people using the SignalHire Agent CLI

- `cli-commands.md` - Complete CLI command reference with examples
- `README.md` - User-focused project overview and getting started guide

**Target Audience:** Users running the SignalHire Agent to search for prospects and reveal contacts

### 🔧 `developer/`
**Developer documentation** - for people contributing to or understanding the codebase

#### Core Development Docs:
- `CLI_FIRST_PATTERN.md` - CLI-first development pattern and architecture
- `TESTING_AND_RELEASE.md` - Testing workflows and release procedures

#### Subdirectories:
- `architecture/` - System architecture and design documents
- `development/` - Development setup, patterns, and guidelines
- `agents/` - AI agent coordination and workflow documentation

**Target Audience:** Developers working on the SignalHire Agent codebase

## Documentation Guidelines

### For User Documentation:
- Focus on **how to use** the application
- Include practical examples and common workflows
- Assume minimal technical background
- Prioritize clarity and ease of use

### For Developer Documentation:
- Focus on **how the system works** internally
- Include architectural decisions and patterns
- Assume technical background
- Prioritize completeness and technical accuracy

## Quick Navigation

**New User?** → Start with [`user/README.md`](user/README.md)  
**Using the CLI?** → See [`user/cli-commands.md`](user/cli-commands.md)  
**Contributing code?** → Start with [`developer/development/`](developer/development/)  
**Understanding architecture?** → See [`developer/architecture/`](developer/architecture/)

## Maintenance

- Keep user docs updated when CLI commands change
- Update developer docs when architecture or patterns change
- Maintain clear separation between user-facing and developer-facing content