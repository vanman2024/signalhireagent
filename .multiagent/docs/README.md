# AI Collaboration & Multi-Init System Documentation

This directory contains documentation **specifically for AI collaboration patterns** and the **multi-init system** that enables seamless multi-agent development across projects.

## 📁 Directory Structure

### `agent-workflows/`
**AI Agent Coordination Patterns** - How multiple AI agents collaborate on software projects:
- `GIT_WORKTREE_GUIDE.md` - Safe git practices for agent isolation
- `AGENT_BRANCH_PROTOCOL.md` - Agent branching and PR coordination  
- `PARALLEL_AGENT_STRATEGY.md` - Parallel multi-agent development strategy
- `TASK_COORDINATION_WORKTREE.md` - Task assignment and dependency coordination

## 🔗 Multi-Init System Documentation

For multi-init system architecture documentation, see `/docs/system-architecture/` in the project root:
- `HOW_UPDATES_WORK.md` - Auto-build and multi-project update system
- `COMPONENT_LINKING.md` - Symlink-based development workflow  
- `AI_CLIS_NON_INTERACTIVE.md` - AI CLI coordination patterns

## 🎯 Scope: AI Collaboration Only

This documentation focuses **exclusively** on:
- ✅ **Multi-agent workflows** - How AI agents coordinate work
- ✅ **Agent specialization** - @claude, @qwen, @gemini, @codex, @copilot roles
- ✅ **Worktree isolation** - Safe parallel development patterns
- ✅ **Task coordination** - Dependency tracking and assignment

## 📚 General Project Documentation

For general project documentation (not AI-specific), see `/docs/` in the project root:
- `/docs/architecture/` - General system architecture
- `/docs/development-guides/` - General development workflows  
- `/docs/system-design/` - System design documents
- `/docs/system-architecture/` - Multi-init system and component linking

## 🤖 Template Distribution

These docs are automatically distributed to all projects that run `multiagent init`, ensuring consistent AI collaboration patterns across your entire development ecosystem.

## 🔄 Auto-Update System

When you commit changes to this directory with semantic commit messages (feat:, fix:, docs:), the auto-build system:
1. Detects the commit type
2. Runs `python3 -m build` automatically
3. Updates ALL registered projects instantly
4. Ensures consistent AI collaboration patterns everywhere

## Quick Links

- **Start Here**: [Parallel Agent Strategy](agent-workflows/PARALLEL_AGENT_STRATEGY.md)
- **Git Safety**: [Git Worktree Guide](agent-workflows/GIT_WORKTREE_GUIDE.md)
- **Multi-Init System**: [How Updates Work](/docs/system-architecture/HOW_UPDATES_WORK.md)
- **Component Linking**: [Component Linking](/docs/system-architecture/COMPONENT_LINKING.md)

---

**Remember**: This documentation is for AI collaboration patterns only. General project docs belong in `/docs/` at the project root.