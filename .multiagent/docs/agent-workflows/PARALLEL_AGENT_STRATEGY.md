# Parallel Agent Development Strategy

## 🎯 Core Strategy: Isolated Worktree Development

### The Problem: Agent Coordination Chaos
Multiple agents working together creates conflicts:
- Mixed work in massive, unreviewable PRs
- Git conflicts from simultaneous edits  
- Lost work from overwrites and rebases
- Unclear attribution and responsibility
- Integration nightmares

### The Solution: 6-Phase Worktree Isolation
Each agent works in their own **completely isolated worktree** following a standardized 6-phase workflow.

## CRITICAL: Main Repository Safety

**GOLDEN RULE**: The primary repository at `/home/vanman2025/Projects/multiagent-core` MUST always remain on `main` branch.

This is your:
- **Command center** for monitoring all work
- **Stable base** that never loses context  
- **Coordination hub** between agents
- **Safe haven** for quick fixes

**Never switch branches in main repo - use worktrees for all agent work!**

## Worktree Isolation Architecture

### Directory Structure
```
/home/vanman2025/Projects/
├── multiagent-core/              # Main repo (ALWAYS on main)
│   ├── specs/                    # Task specifications  
│   ├── .multiagent/              # Agent templates & docs
│   └── [project files]           # Stable main branch
├── project-claude/               # Claude's isolated worktree
├── project-qwen/                 # Qwen's isolated worktree
├── project-gemini/               # Gemini's isolated worktree
├── project-codex/                # Codex's isolated worktree
└── project-copilot/              # Copilot's isolated worktree
```

### Viewing All Active Worktrees
```bash
# See all active worktrees and their branches
git worktree list -v

# Quick status of all agent work
for dir in ../project-*; do
  if [ -d "$dir" ]; then
    echo "$(basename $dir): $(cd $dir && git branch --show-current)"
  fi
done
```

## Agent Specialization Strategy

### Role-Based Agent Assignment
- **@claude**: CTO-level architecture, integration, security, strategic decisions
- **@qwen**: Performance optimization, algorithms, database efficiency
- **@gemini**: Documentation, research, analysis (simple tasks only)
- **@codex**: Frontend development, UI/UX, React components
- **@copilot**: Backend implementation, API development, database operations

### Task Dependencies & Coordination
```markdown
# Typical dependency flow:
- [x] T001 @claude Design authentication architecture ✅
- [ ] T002 @copilot Implement auth backend (depends on T001)
- [ ] T003 @qwen Optimize auth queries (depends on T002)
- [ ] T004 @codex Create auth UI components (depends on T002)
- [ ] T005 @gemini Document auth API (depends on T002)
```

## 6-Phase Parallel Workflow

### Phase 1: Setup & Context Reading (All Agents)
Each agent simultaneously:
1. **Read their agent MD file** - Understand role and specializations
2. **Configure git safety** - Prevent destructive rebases
3. **Check assignments** - `grep "@[agent]" specs/*/tasks.md`
4. **Review dependencies** - Identify coordination points

### Phase 2: Worktree Creation (Parallel Setup)
Each agent creates their isolation:
```bash
# @claude creates architecture workspace
git worktree add -b agent-claude-architecture ../project-claude main

# @qwen creates optimization workspace  
git worktree add -b agent-qwen-optimization ../project-qwen main

# @gemini creates documentation workspace
git worktree add -b agent-gemini-docs ../project-gemini main

# @codex creates frontend workspace
git worktree add -b agent-codex-frontend ../project-codex main

# @copilot creates backend workspace
git worktree add -b agent-copilot-backend ../project-copilot main
```

### Phase 3: Parallel Task Planning
Each agent in their worktree:
```bash
cd ../project-[agent]
# Use TodoWrite for internal tracking
# Plan implementation approach
# Review existing structure
```

### Phase 4: Parallel Implementation 
All agents work simultaneously in isolation:
```bash
# Each agent makes regular commits in their worktree
git commit -m "[WORKING] feat: Implement feature @[agent]"

# NO interference between agents
# NO shared branches or conflicts
```

### Phase 5: Sequential PR Integration
**Recommended merge order for dependencies:**
1. **@claude** - Architecture foundation first
2. **@copilot** - Core backend implementation
3. **@qwen** - Performance optimizations
4. **@codex** - Frontend implementation  
5. **@gemini** - Documentation polish

### Phase 6: Parallel Cleanup
After each PR merge, that agent cleans up:
```bash
cd /home/vanman2025/Projects/multiagent-core
git worktree remove ../project-[agent]
git branch -d agent-[agent]-feature
```

## Safe Git Configuration (All Agents)

### MANDATORY Safety Settings
```bash
# EVERY agent MUST configure this in their worktree:
cd ../project-[agent]
git config --local pull.rebase false  # Prevents data loss
git config --local pull.ff only       # Only safe operations
```

### Safe Sync Pattern
```bash
# CORRECT: Safe sync with main
git fetch origin main && git merge origin/main

# WRONG: Dangerous rebase operations  
git rebase origin/main              # ❌ Can destroy work
git pull origin main --rebase      # ❌ Can reset tasks.md
```

## Task Coordination Mechanisms

### Dual Tracking System
**Internal Tracking (TodoWrite)** - Per agent session:
```json
{
  "content": "Implement auth middleware (T015)",
  "status": "in_progress", 
  "activeForm": "Implementing auth middleware"
}
```

**External Tracking (tasks.md)** - Team coordination:
```markdown
- [x] T015 @copilot Implement auth middleware ✅
```

### Inter-Agent Communication
- **Through tasks.md** - Mark dependencies and completion
- **Through PR descriptions** - Document integration points
- **Through main branch** - Sync completed work
- **Through @claude integration** - Final review coordination

## Review Integration Strategy

### @claude as Review Coordinator
- All agents include `@claude` in final commit
- Triggers automated review routing
- Claude coordinates integration conflicts
- Strategic decisions escalated to Claude

### PR Review Process
```bash
# Agent final commit triggers review
git commit -m "[COMPLETE] feat: Implementation complete @claude

All tasks completed and ready for review."

# Creates focused, manageable PR
gh pr create --title "feat: [agent] Description"
```

## Conflict Prevention

### Structural Conflicts
- **Agent specializations** prevent work overlap
- **Sequential dependencies** provide clear order
- **Isolated worktrees** eliminate file conflicts
- **One agent = one PR** keeps changes focused

### Integration Conflicts
- **Later agents sync with main** to get earlier work
- **Dependency tracking** in tasks.md shows requirements
- **@claude coordination** resolves complex integration issues
- **Small, focused PRs** make conflicts manageable

## Monitoring & Status

### Central Coordination View
```bash
# From main repo, check all agent status
cd /home/vanman2025/Projects/multiagent-core

# See all active worktrees
git worktree list

# Check task completion status
grep -r "@\(claude\|qwen\|gemini\|codex\|copilot\)" specs/*/tasks.md
```

### Agent Status Checking
```bash
# Quick status script for all agents
for agent in claude qwen gemini codex copilot; do
  if [ -d "../project-$agent" ]; then
    echo "$agent: $(cd ../project-$agent && git status --porcelain | wc -l) changes"
  fi
done
```

## Emergency Procedures

### Agent Workspace Recovery
```bash
# If agent worktree becomes corrupted
git worktree remove --force ../project-[agent]
git worktree prune
git worktree add -b agent-[agent]-recovery ../project-[agent] main
```

### Conflict Resolution
```bash
# If merge conflicts occur during sync
cd ../project-[agent]
git fetch origin main
git merge origin/main
# Resolve conflicts manually
git add .
git commit -m "resolve: Merge conflicts with main"
```

### Emergency Rollback
```bash
# Rollback individual agent PR if needed
gh pr revert <pr-number>
# Other agents unaffected due to isolation
```

## Benefits of Parallel Strategy

### 1. **Complete Isolation** 
- No interference between agents
- Safe parallel development
- Independent debugging and testing

### 2. **Clear Attribution**
- One agent = one worktree = one PR
- Easy to track contributions
- Clear responsibility boundaries

### 3. **Scalable Coordination**
- Add new agents without disruption
- Handle complex multi-agent projects
- Maintain code quality at scale

### 4. **Safe Operations**
- No destructive rebases
- Protected main branch
- Recoverable from failures

### 5. **Efficient Reviews**
- Focused, manageable PRs
- Agent-specific expertise
- Faster integration cycles

## Implementation Checklist

### Project Setup
- [ ] Main repo stays on main branch
- [ ] Agent templates configured
- [ ] Task specifications created
- [ ] Documentation links verified

### Agent Onboarding
- [ ] Each agent creates worktree
- [ ] Git safety configured
- [ ] TodoWrite tool available
- [ ] Agent MD file studied

### Coordination Setup
- [ ] Task dependencies mapped
- [ ] Review integration configured
- [ ] Cleanup procedures documented
- [ ] Emergency procedures tested

## Quick Reference Commands

```bash
# Create agent worktree
git worktree add -b agent-[name]-feature ../project-[name] main

# Safe sync in worktree
git fetch origin main && git merge origin/main

# Check all agent status
git worktree list

# Final commit with review integration
git commit -m "[COMPLETE] feat: Work complete @claude"

# Cleanup after merge
git worktree remove ../project-[name]
```

## Success Metrics

- **PR Size**: < 1,000 lines per agent PR
- **Review Time**: < 24 hours per focused PR
- **Conflict Rate**: Near zero due to isolation
- **Attribution**: 100% clear agent responsibility
- **Parallel Efficiency**: All agents work simultaneously
- **Integration Success**: Sequential dependency satisfaction

**Remember: Isolation enables parallelism, coordination ensures success!**