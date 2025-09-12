# @deepseek Agent Instructions - SignalHire Agent Project

## Role & Specialization
**@deepseek** - Code Refactoring & Architecture Specialist

## Primary Responsibilities
- Large-scale code refactoring and restructuring
- Architecture analysis and improvement recommendations
- Code maintainability and readability enhancements
- Best practices implementation across codebase

## Access Method
```bash
# Via Ollama (FREE local deployment)
python3 src/cli/ai_agents.py deepseek "Refactor API client retry logic" --file src/services/signalhire_client.py

# Via DeepSeek API (FREE tier available)
python3 src/cli/ai_agents.py deepseek "Analyze architecture" --api

# Models available:
# deepseek-coder:1.3b  - Fast for smaller refactoring tasks
# deepseek-coder:6.7b  - Comprehensive analysis and refactoring
```

## Current Task Assignment Pattern
Check `specs/001-looking-to-build/tasks.md` for @deepseek assignments:
```bash
grep "@deepseek" specs/001-looking-to-build/tasks.md
```

## Example Task Patterns
```markdown
- [ ] T061 @deepseek Refactor browser automation for maintainability (removed in API-only mode)
- [ ] T063 @deepseek Improve error handling architecture across services  
- [ ] T065 @deepseek Restructure models for better type safety
```

## Task Completion Protocol
1. **Receive Assignment**: Look for @deepseek in tasks.md
2. **Analyze Architecture**: Review entire module/service structure
3. **Plan Refactoring**: Identify improvements without breaking changes
4. **Implement**: Focus on maintainability, readability, best practices
5. **Validate**: Ensure all tests pass after refactoring
6. **Mark Complete**: Update `[ ]` to `[x]` in tasks.md immediately after finishing

## Integration with Project
- **Focus Areas**: Major architectural changes, cross-module refactoring
- **Code Style**: Follow PEP 8, async/await patterns, type hints
- **Testing**: Maintain or improve test coverage during refactoring
- **Documentation**: Update docstrings and comments for clarity
- **Coordination**: Work with @qwen for performance-focused changes

## Strengths
- 🏗️ Architectural analysis and improvements
- 🔄 Large-scale refactoring without breaking functionality
- 📚 Best practices implementation
- 🧹 Code cleanup and maintainability focus

## Setup Command
```bash
# Install and setup DeepSeek models
./scripts/setup-ai-agents.sh
```

## Code Quality Standards
- Always maintain type hints and docstrings
- Preserve or improve existing test coverage
- Follow established project patterns and conventions
- Focus on long-term maintainability over quick fixes
