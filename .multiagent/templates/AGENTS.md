# Agent Development Instructions

## 🔄 AGENT WORKFLOW: Phase-by-Phase Operation

### Phase 1: Setup & Context Reading
1. **Read your specific agent MD file** - Open and study your agent file (CLAUDE.md, QWEN.md, GEMINI.md, etc.)
2. **Read this general agent file completely** - Understand overall workflow and coordination patterns
3. **Study worktree documentation** - Review Git Worktree Management protocols
4. **Read referenced documentation** - Study the workflow guides:
   - Git Worktree Guide (.multiagent/docs/agent-workflows/GIT_WORKTREE_GUIDE.md)
   - Agent Branch Protocol (.multiagent/docs/agent-workflows/AGENT_BRANCH_PROTOCOL.md) 
   - Parallel Agent Strategy (.multiagent/docs/agent-workflows/PARALLEL_AGENT_STRATEGY.md)
   - Task Coordination (.multiagent/docs/agent-workflows/TASK_COORDINATION_WORKTREE.md)
5. **Check current assignments** - `grep "@[your-agent]" specs/*/tasks.md`
6. **Configure safe git behavior** - Run mandatory configs to prevent rebases:
   ```bash
   git config --local pull.rebase false
   git config --local pull.ff only
   ```

### Phase 2: Worktree Setup & Environment Preparation  
7. **Verify current branch and location** - `git branch --show-current` (should be main)
8. **Create your dedicated worktree** - Isolate your work environment:
   ```bash
   git worktree add -b agent-[name]-[feature] ../project-[name] main
   ```
9. **Navigate to your worktree directory** - `cd ../project-[name]` - Work in isolated environment
10. **Verify worktree setup** - `git branch --show-current` (should show your agent branch)
11. **Sync with latest main** - `git fetch origin main && git merge origin/main`

### Phase 3: Task Discovery & Planning
12. **Find your tasks** - `grep "@[your-agent]" specs/*/tasks.md` 
    ```markdown
    # Example tasks.md showing YOUR tasks:
    - [ ] T015 @[your-agent] Create responsive dashboard component
    - [ ] T045 @[your-agent] Implement user login form
    - [ ] T055 @[your-agent] Add responsive navigation menu
    ```
13. **Use TodoWrite tool** - Track your tasks internally: 
    ```json
    [
      {"content": "Create responsive dashboard component (T015)", "status": "pending", "activeForm": "Creating responsive dashboard component"},
      {"content": "Implement user login form (T045)", "status": "pending", "activeForm": "Implementing user login form"}, 
      {"content": "Add responsive navigation menu (T055)", "status": "pending", "activeForm": "Adding responsive navigation menu"}
    ]
    ```
14. **Analyze task dependencies** - Check if tasks depend on other agents' work
15. **Review existing folder structure** - MANDATORY before coding:
    ```bash
    find . -name "test*" -type d  # See existing test directories
    ls -la tests/                 # Review test organization
    ls -la src/ backend/ frontend/ # Check main code structure
    ```
16. **Plan implementation approach** - Consider architecture, patterns, and integration points

### Phase 4: Implementation & Development Work
17. **Start first task** - Mark `in_progress` in TodoWrite, then implement
18. **Make regular work commits** - Use normal commit format (NO @claude during work):
    ```bash
    git commit -m "[WORKING] feat: Implement component
    
    @[agent] working in isolated worktree"
    ```
19. **Complete tasks with dual tracking** - Update BOTH places:
    - **Internal**: TodoWrite `{"status": "completed"}`
    - **External**: tasks.md `- [x] T015 @agent Create component ✅`
20. **Basic smoke test** - Verify implementation works locally
21. **DO NOT create scattered test files** - Use existing `/tests/` structure, don't create new test folders
22. **Let GitHub Actions handle quality** - Automated lint/typecheck/integration tests run on PR

### Phase 5: PR Creation & Review Integration
23. **Complete final implementation** - Ensure all assigned work is done
24. **Final TodoWrite cleanup** - Mark all internal tasks as completed
25. **Make final commit with @claude** - This triggers review integration:
    ```bash
    git commit -m "[COMPLETE] feat: Implementation complete @claude
    
    All tasks completed and ready for automated review."
    ```
26. **Push and create PR** - `git push origin agent-[name]-[feature] && gh pr create`
27. **Review system handles feedback routing** - Claude reviews and routes feedback automatically

### Phase 6: Post-Merge Cleanup - MANDATORY
28. **After PR is merged** - Clean up your worktree immediately:
    ```bash
    # Go to main project directory (not your worktree!)
    cd /home/vanman2025/Projects/multiagent-core
    
    # Update main branch
    git checkout main && git pull origin main
    
    # Remove your worktree (MANDATORY!)
    git worktree remove ../project-[name]
    
    # Clean up branch
    git branch -d agent-[name]-[feature]
    ```

---

## Git Worktree Management

**CRITICAL**: Each agent works in isolated worktrees for parallel development without conflicts.

### Worktree Setup
```bash
# Create your dedicated worktree from main
git worktree add -b agent-[name]-[feature] ../project-[name] main
cd ../project-[name]
git branch --show-current  # Verify: agent-[name]-[feature]
```

### Daily Sync & Commit
```bash
# Configure safe git behavior
git config --local pull.rebase false
git config --local pull.ff only

# Sync with main (NO REBASE - causes data loss)
git fetch origin main && git merge origin/main

# Regular commits
git commit -m "[WORKING] feat: Updates @[agent]"
```

### PR Workflow: Commit → Push → PR
```bash
# Final commit with @claude for review integration
git commit -m "[COMPLETE] feat: Implementation complete @claude"
git push origin agent-[name]-[feature]
gh pr create --title "feat: Updates from @[agent]"
```

## Agent Specializations

**Quick Reference & Direction-Following Capabilities:**
- **@claude**: CTO-level architecture, integration, security, strategic decisions ⭐ **Excellent at following directions**
- **@codex**: Full-stack development, React, UI/UX, interactive development ⭐ **Excellent at following directions**
- **@qwen**: Performance optimization, algorithms, efficiency improvements ⭐ **Excellent at following directions**
- **@copilot**: Backend implementation, API development, database operations ⭐ **Good at following directions**
- **@gemini**: Research, documentation, simple analysis ⚠️ **Use for simple tasks only**

### Permission Settings - AUTONOMOUS OPERATION

#### ✅ ALLOWED WITHOUT APPROVAL (Autonomous)
- **Reading files**: Read any file in the project
- **Editing files**: Edit, modify, update existing files
- **Creating new files**: Create new code, tests, documentation
- **Running commands**: Execute build, test, lint commands
- **Git operations**: Commit, branch, pull, status checks
- **Testing**: Run tests and validate functionality
- **Debugging**: Analyze logs, trace errors
- **Refactoring**: Improve code structure and organization

#### 🛑 REQUIRES APPROVAL (Ask First)
- **Deleting files**: Any file deletion needs explicit approval
- **Overwriting files**: Complete file replacement needs approval
- **Force operations**: Any `--force` flags or overwrites
- **System changes**: Modifying system files or global configs
- **Production deploys**: Any production deployment
- **Breaking changes**: Major API or interface changes

#### Operating Principle
**"Edit freely, delete carefully"** - Make all the changes needed to improve code, but always ask before removing or completely replacing anything.

### Commit Format
```bash
git commit -m "[WORKING] feat: Feature description

Related to #123

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: @qwen <noreply@anthropic.com>
Co-Authored-By: @gemini <noreply@anthropic.com>  
Co-Authored-By: @codex <noreply@anthropic.com>
Co-Authored-By: @copilot <noreply@anthropic.com>"
```

### Documentation References
For detailed information on worktree workflows, see:
- [Git Worktree Guide](.multiagent/docs/agent-workflows/GIT_WORKTREE_GUIDE.md)
- [Agent Branch Protocol](.multiagent/docs/agent-workflows/AGENT_BRANCH_PROTOCOL.md)
- [Parallel Agent Strategy](.multiagent/docs/agent-workflows/PARALLEL_AGENT_STRATEGY.md)
- [Task Coordination](.multiagent/docs/agent-workflows/TASK_COORDINATION_WORKTREE.md)

## Screenshot Handling (WSL)

When users provide screenshots in WSL environments, always use the correct path format:
```bash
# Correct WSL paths for reading screenshots
/mnt/c/Users/[username]/Pictures/Screenshots/[filename].png
/mnt/c/Users/[username]/Desktop/[filename].png
/mnt/c/Users/[username]/Downloads/[filename].png

# Example usage with Read tool:
Read: /mnt/c/Users/user/Pictures/Screenshots/Screenshot 2025-09-22.png
```

**Important**: Never use Windows-style paths (C:\Users\...) when working in WSL.