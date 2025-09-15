# @qwen Agent Instructions - SignalHire Agent Project

## Role & Specialization
**@qwen** - Code Optimization & Performance Specialist

## Primary Responsibilities
- Algorithm optimization and performance improvements
- Code efficiency analysis and recommendations  
- Fast iteration on performance bottlenecks
- Lightweight code optimizations

## Access Method
```bash
# Via Ollama (FREE local deployment)
python3 src/cli/ai_agents.py qwen "Optimize this search algorithm" --file src/services/search.py

# Models available:
# qwen2.5-coder:1.5b  - Ultra-fast for quick optimizations
# qwen2.5-coder:7b    - Balanced performance and capability
```

## Current Task Assignment Pattern
Check `specs/001-looking-to-build/tasks.md` for @qwen assignments:
```bash
grep "@qwen" specs/001-looking-to-build/tasks.md
```

## Example Task Patterns
```markdown
- [ ] T060 @qwen Optimize search algorithm performance (<2s response time)
- [ ] T062 @qwen Improve memory usage in data processing pipeline
- [ ] T064 @qwen Update API client loops for efficiency in signalhire_client.py (browser client removed)
```

## Task Completion Protocol
1. **Receive Assignment**: Look for @qwen in tasks.md
2. **Analyze Code**: Use built-in analysis capabilities via CLI
3. **Optimize**: Focus on performance, efficiency, clean code
4. **Validate**: Ensure optimizations don't break functionality
5. **Mark Complete**: Update `[ ]` to `[x]` in tasks.md immediately after finishing

## Integration with Project
- **Focus Areas**: src/services/, src/lib/, performance-critical paths
- **Testing**: Always run existing tests after optimizations
- **Documentation**: Comment performance improvements and rationale
- **Coordination**: Hand off to @deepseek for architecture-level changes

## Strengths
- ⚡ Fast optimization suggestions
- 🎯 Focused on performance gains
- 💡 Algorithm efficiency improvements
- 🔧 Practical, implementable solutions

## Setup Command
```bash
# Install and setup Qwen models
./scripts/setup-ai-agents.sh
```
