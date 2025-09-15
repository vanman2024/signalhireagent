# AI Agents Documentation

Agent-specific instructions and context files for the @symbol coordination system.

## 🤖 Active Agents

### Premium Agents
- **[COPILOT_SUMMARY.md](./COPILOT_SUMMARY.md)** - GitHub Copilot integration and task assignments

### Free Local Agents  
- **[QWEN.md](./QWEN.md)** - @qwen code optimization & performance specialist
- **[DEEPSEEK.md](./DEEPSEEK.md)** - @deepseek refactoring & architecture specialist  
- **[GEMINI.md](./GEMINI.md)** - @gemini research & performance analysis specialist

## 📋 Agent Coordination

Each agent file contains:
- **Role & Specialization** - What the agent excels at
- **Access Method** - How to invoke the agent
- **Current Assignments** - Active tasks from `specs/tasks.md`
- **Task Patterns** - Examples of @agent task assignments
- **Completion Protocol** - How agents mark tasks complete

## 🔄 Task Assignment Workflow

1. **Check Assignments**: `grep "@agentname" specs/001-looking-to-build/tasks.md`
2. **Complete Task**: Follow agent-specific instructions  
3. **Mark Complete**: Change `[ ]` to `[x]` in tasks.md immediately
4. **Coordinate**: Hand off to other agents if needed

## 🎯 @Symbol Coordination

All agents work within the revolutionary @symbol system using simple markdown task assignment:
```markdown
- [ ] T060 @qwen Optimize search performance
- [ ] T061 @deepseek Refactor for maintainability  
- [ ] T062 @gemini Analyze and document results
```