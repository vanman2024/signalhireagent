# SignalHire Agent Documentation

This directory contains comprehensive documentation for the SignalHire lead generation agent project and its revolutionary **@symbol coordination system**.

## 📁 Documentation Structure

### 🤖 [`agents/`](./agents/)
Agent-specific instructions and context files:
- **[COPILOT_SUMMARY.md](./agents/COPILOT_SUMMARY.md)** - GitHub Copilot integration and tasks
- **[DEEPSEEK.md](./agents/DEEPSEEK.md)** - @deepseek refactoring & architecture specialist  
- **[GEMINI.md](./agents/GEMINI.md)** - @gemini research & performance specialist
- **[QWEN.md](./agents/QWEN.md)** - @qwen optimization & performance specialist

### 🏗️ [`architecture/`](./architecture/)
System design and coordination documentation:
- **[AI_COORDINATION_PLAN.md](./architecture/AI_COORDINATION_PLAN.md)** - Revolutionary @symbol coordination system
- **[api.md](./architecture/api.md)** - API documentation and specifications
- **[CLI_FIRST_PATTERN.md](./CLI_FIRST_PATTERN.md)** - CLI-first development pattern for API connectors

### 🛠️ [`development/`](./development/)
Development processes and guidelines:
- **[DEVELOPMENT.md](./development/DEVELOPMENT.md)** - Development guidelines and standards
- **[testing_strategy.md](./development/testing_strategy.md)** - Comprehensive testing framework

## 🎯 Quick Navigation

### For AI Agents
Each agent has specific context files with their role, responsibilities, and task patterns:
```bash
# Agent instructions are in agents/ directory
grep "@qwen" agents/QWEN.md     # Check @qwen tasks
grep "@deepseek" agents/DEEPSEEK.md  # Check @deepseek tasks
```

### For Developers
- **Start here**: [DEVELOPMENT.md](./development/DEVELOPMENT.md)
- **Testing**: [testing_strategy.md](./development/testing_strategy.md)
- **API Reference**: [api.md](./architecture/api.md)

### For Project Coordination
- **@Symbol System**: [AI_COORDINATION_PLAN.md](./architecture/AI_COORDINATION_PLAN.md)
- **Multi-Agent Workflow**: See breakthrough coordination approach

## 🚀 Key Innovations

### @Symbol Coordination System

This project pioneered the **@symbol coordination system** - a simple, scalable approach to multi-agent development using familiar @mention syntax in markdown files. This system outperforms complex orchestration frameworks through:

- **Universal Pattern**: Uses GitHub/social media @mention syntax
- **Zero Infrastructure**: Just markdown files - works anywhere  
- **Self-Documenting**: The system explains itself
- **Tool Agnostic**: Works with any agent or human
- **Instantly Scalable**: Add new agents by just using @newagent

### CLI-First Architecture Pattern

This project demonstrates the **CLI-First Pattern** for API connector projects - a proven strategy for building on top of existing services:

- **Rapid API Validation**: Test integrations without frontend complexity
- **Technical Early Adopters**: Serve power users first, expand to broader audiences later
- **Future-Proof Foundation**: CLI logic becomes the backbone for web UIs, mobile apps, and integrations
- **Real-World Success**: Pattern used by Terraform, Docker, Stripe, and other major tools

See [CLI_FIRST_PATTERN.md](./CLI_FIRST_PATTERN.md) for the complete guide.

## 📊 Agent Ecosystem

| Agent | Role | Access | Specialization |
|-------|------|--------|----------------|
| @claude | Architecture & Integration | Claude Code | Complex system design, multi-file changes |
| @copilot | Implementation & Code Gen | GitHub Copilot | Single-file implementations, patterns |
| @codex | Interactive Development | OpenAI | TDD, interactive debugging |
| @gemini | Research & Performance | Google Gemini | Documentation, optimization |
| @qwen | Code Optimization | FREE (Ollama) | Algorithm performance, efficiency |
| @deepseek | Refactoring & Architecture | FREE (Ollama/API) | Large-scale refactoring, maintainability |

## 💡 Usage Examples

```markdown
# Example task assignments using @symbol coordination:
- [ ] T060 @qwen Optimize search algorithm performance (<2s response time)
- [ ] T061 @deepseek Refactor browser automation for maintainability (removed in API-only mode)
- [ ] T062 @gemini Create performance benchmarks and analysis
```

This documentation structure supports the scalable, self-organizing nature of the @symbol coordination breakthrough.
