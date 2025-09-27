# Task Coordination in Worktree Workflow

## 🎯 The Coordination Challenge

### Problem: Isolated Worktree Communication
With each agent working in isolated worktrees, coordinating tasks becomes complex:

```
Main repo: tasks.md shows [ ] T001, [ ] T002, [ ] T003
    ↓
Agent creates worktree → ../project-agent
    ↓  
Agent updates: tasks.md to [x] T001 ✅
    ↓
OTHER AGENTS CAN'T SEE THIS UPDATE!
Main repo still shows T001 as incomplete
```

### Solution: Dual Tracking System
Combine **internal tracking** (TodoWrite) with **external coordination** (tasks.md + GitHub).

## Dual Tracking Architecture

### Internal Tracking: TodoWrite Tool
Each agent tracks their work session internally:
```json
{
  "content": "Implement user authentication (T015)",
  "status": "in_progress",
  "activeForm": "Implementing user authentication"
}
```

**Benefits:**
- Real-time progress within agent session
- Detailed task breakdown
- Session-specific organization
- No external conflicts

### External Tracking: tasks.md + GitHub Integration  
Team coordination through shared visibility:
```markdown
- [x] T015 @copilot Implement user authentication ✅
```

**Benefits:**
- Team-wide visibility
- Dependency tracking
- Historical record
- Integration with GitHub automation

## 6-Phase Coordination Workflow

### Phase 1: Setup & Context Reading
**All agents simultaneously:**
```bash
# Each agent finds their assignments
grep "@claude" specs/*/tasks.md
grep "@qwen" specs/*/tasks.md  
grep "@gemini" specs/*/tasks.md
grep "@codex" specs/*/tasks.md
grep "@copilot" specs/*/tasks.md
```

### Phase 2: Worktree Setup & Planning
**Each agent in their worktree:**
```bash
cd ../project-[agent]

# Set up TodoWrite tracking
TodoWrite: [
  {"content": "Feature X (T001)", "status": "pending", "activeForm": "Implementing feature X"},
  {"content": "Tests for X (T002)", "status": "pending", "activeForm": "Adding tests for X"}
]
```

### Phase 3: Task Dependencies Analysis
**Check coordination points:**
```markdown
# Example dependency chain:
- [x] T001 @claude Design auth architecture ✅     ← Foundation
- [ ] T002 @copilot Implement auth backend (depends on T001)  ← Core
- [ ] T003 @qwen Optimize auth queries (depends on T002)      ← Performance  
- [ ] T004 @codex Create auth UI (depends on T002)            ← Frontend
- [ ] T005 @gemini Document auth API (depends on T002)        ← Documentation
```

### Phase 4: Parallel Implementation with Coordination
**Work commits (no external updates):**
```bash
# Each agent works in isolation
git commit -m "[WORKING] feat: Implement auth @copilot"

# Internal tracking updates
TodoWrite: {"content": "Implement auth (T002)", "status": "completed"}
```

### Phase 5: PR Creation with External Updates
**Final integration with team visibility:**
```bash
# 1. Final commit triggers review
git commit -m "[COMPLETE] feat: Implementation complete @claude"

# 2. Update external tracking in main repo
cd /home/vanman2025/Projects/multiagent-core
# Edit tasks.md: - [x] T002 @copilot Implement auth backend ✅

# 3. Create PR with task references
gh pr create --title "feat: [copilot] Auth backend implementation" \
  --body "## Tasks Completed
- [x] T002 @copilot Implement auth backend ✅

Closes #T002"
```

### Phase 6: Post-Merge Coordination
**Update dependencies:**
```bash
# After @copilot's PR merges, dependent agents sync
cd ../project-qwen
git fetch origin main && git merge origin/main  # Gets auth backend

cd ../project-codex  
git fetch origin main && git merge origin/main  # Gets auth backend

# Both can now work on their dependent tasks
```

## Task Status Communication Mechanisms

### 1. GitHub Issues Integration (RECOMMENDED)
```bash
# Convert tasks to GitHub issues (one time setup)
for task in T001 T002 T003; do
  gh issue create --title "$task: Description" --assignee "@agent" --label "task"
done

# Agents check assigned issues
gh issue list --assignee @me --state open

# Auto-close via PR
gh pr create --body "Closes #T002" # Issue closes when PR merges
```

### 2. Task Branch Updates (ALTERNATIVE)
```bash
# Quick task status updates to main
git checkout main
git pull origin main
# Update tasks.md: [x] T002 @copilot Complete ✅
git add specs/tasks.md
git commit -m "task: Mark T002 complete (@copilot)"
git push origin main

# Other agents sync periodically
git pull origin main  # Gets latest task updates
```

### 3. PR-Based Task Coordination (CURRENT)
```bash
# Include task updates in feature PR
- [x] T002 @copilot Implement auth backend ✅

# Other agents see completion when PR merges
# Dependency chain becomes visible
```

## Agent Coordination Patterns

### Sequential Dependencies
```markdown
# Architecture → Implementation → Optimization
- [x] T001 @claude Design system architecture ✅
    ↓ (architecture complete - backends can start)
- [ ] T002 @copilot Implement API endpoints (depends on T001)
- [ ] T003 @copilot Implement data models (depends on T001)
    ↓ (implementation complete - optimization can start)  
- [ ] T004 @qwen Optimize database queries (depends on T002, T003)
```

### Parallel Development
```markdown
# After architecture, multiple agents can work simultaneously:
- [x] T001 @claude Design auth architecture ✅
    ↓ (enables parallel work)
- [ ] T002 @copilot Auth backend     } Parallel
- [ ] T003 @codex Auth frontend      } Development  
- [ ] T004 @gemini Auth documentation} Phase
```

### Integration Coordination  
```markdown
# Final integration after parallel work:
- [x] T002 @copilot Auth backend ✅
- [x] T003 @codex Auth frontend ✅
- [ ] T005 @claude Integration testing (depends on T002, T003)
- [ ] T006 @qwen Performance testing (depends on T005)
```

## Communication Channels

### 1. tasks.md Files
- **Purpose**: Task assignment and dependency tracking
- **Update**: Via PR merge (external visibility)
- **Format**: `- [x] T001 @agent Description ✅`

### 2. TodoWrite Tool
- **Purpose**: Internal session tracking
- **Update**: Real-time during work
- **Format**: `{"content": "Task X", "status": "completed"}`

### 3. PR Descriptions
- **Purpose**: Document integration points and dependencies
- **Update**: During PR creation
- **Format**: Reference task numbers and dependent work

### 4. Git Commit Messages
- **Purpose**: Progress tracking and attribution
- **Update**: Regular during work
- **Format**: `[WORKING] feat: Description @agent`

## Coordination Monitoring

### Central Status Dashboard
```bash
# From main repo, check all agent progress
cd /home/vanman2025/Projects/multiagent-core

# Check task completion across all specs
grep -r "\[x\]" specs/*/tasks.md | grep -E "@(claude|qwen|gemini|codex|copilot)"

# See active worktrees and their status
git worktree list

# Check recent commits from all agents
git log --oneline --grep="@" -10
```

### Agent Status Checking
```bash
# Quick status of all active agents
for agent in claude qwen gemini codex copilot; do
  if [ -d "../project-$agent" ]; then
    echo "$agent: $(cd ../project-$agent && git log -1 --oneline)"
  fi
done
```

### Dependency Validation
```bash
# Check if dependencies are met before starting
check_dependencies() {
  local task=$1
  # Parse tasks.md for dependencies
  # Verify prerequisite tasks are complete
  # Alert if dependencies not ready
}
```

## Conflict Resolution Strategies

### Task Assignment Conflicts
```markdown
# WRONG: Multiple agents assigned same task
- [ ] T001 @copilot @codex Implement auth ❌

# CORRECT: Single agent responsibility  
- [ ] T001 @copilot Implement auth backend
- [ ] T002 @codex Implement auth frontend
```

### Dependency Conflicts
```bash
# If agent tries to work without prerequisites
if ! grep -q "\[x\] T001" specs/tasks.md; then
  echo "ERROR: T001 must be complete before starting T002"
  exit 1
fi
```

### Integration Conflicts
```bash
# When multiple agents' work conflicts
# 1. Later agent syncs with main to get earlier work
cd ../project-codex
git fetch origin main && git merge origin/main

# 2. Resolve conflicts understanding both implementations
# 3. Escalate complex conflicts to @claude
git commit -m "[COMPLETE] feat: Work complete @claude

Integration conflicts resolved."
```

## Best Practices

### 1. Clear Task Assignment
- **One task = one agent**
- **Clear dependencies in tasks.md**
- **Specific, actionable descriptions**

### 2. Regular Synchronization
```bash
# Daily sync routine for all agents
cd ../project-[agent]
git fetch origin main && git merge origin/main
```

### 3. Proactive Communication
```bash
# Update status before blocking others
git commit -m "[PROGRESS] feat: Auth 80% complete @copilot

Backend endpoints implemented, testing in progress."
```

### 4. Dependency Management
- **Check prerequisites before starting**
- **Update dependents when complete**  
- **Document integration requirements**

### 5. Escalation Protocol
```bash
# When stuck, escalate to @claude
git commit -m "[BLOCKED] feat: Need architecture decision @claude

Database schema unclear for user roles."
```

## GitHub Integration Automation

### Issue Templates
```yaml
# .github/ISSUE_TEMPLATE/task.yml
name: Agent Task
about: Create a task for an agent
labels: task
assignees: ''
body:
  - type: input
    attributes:
      label: Task ID
      placeholder: T001
  - type: dropdown
    attributes:
      label: Assigned Agent
      options:
        - @claude
        - @qwen  
        - @gemini
        - @codex
        - @copilot
```

### Automation Workflows
```yaml
# .github/workflows/task-coordination.yml
name: Task Coordination
on:
  pull_request:
    types: [merged]

jobs:
  update-task-status:
    runs-on: ubuntu-latest
    steps:
      - name: Extract completed tasks from PR
        run: |
          # Parse PR body for task completions
          # Update project board
          # Notify dependent agents
```

## Quick Reference

### For Agents Starting Work
```bash
# 1. Find your tasks
grep "@[agent]" specs/*/tasks.md

# 2. Check dependencies  
grep -B5 -A5 "T00X" specs/tasks.md

# 3. Set up tracking
TodoWrite: [{"content": "Task X", "status": "pending"}]

# 4. Start work in worktree
cd ../project-[agent]
```

### For Agents Completing Work
```bash
# 1. Mark internal tracking complete
TodoWrite: [{"content": "Task X", "status": "completed"}]

# 2. Final commit with @claude
git commit -m "[COMPLETE] feat: Work complete @claude"

# 3. Update tasks.md in main repo (via PR)
# 4. Notify dependent agents (via PR merge)
```

### For Monitoring Progress
```bash
# Check all agent status
git worktree list
grep -r "\[x\]" specs/*/tasks.md

# See dependency chain
grep -A10 -B10 "@agent" specs/tasks.md
```

## Success Metrics

- **Task Visibility**: All agents can see current status
- **Dependency Tracking**: Clear prerequisite relationships  
- **Attribution**: Easy to identify who did what
- **Conflict Rate**: Minimal integration issues
- **Coordination Overhead**: < 10% of development time

**Remember: Good coordination enables great parallel development!**