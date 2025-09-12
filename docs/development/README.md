# Development Documentation  

Development processes, guidelines, and testing strategies.

## 🛠️ Development Resources

### Core Guidelines
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Comprehensive development standards
  - Code style and conventions
  - Environment setup and configuration  
  - Tool usage and best practices
  - WSL/cross-platform considerations

### Testing Framework
- **[testing_strategy.md](./testing_strategy.md)** - Multi-layer testing approach
  - Unit tests for individual components
  - Integration tests for end-to-end workflows
  - Contract tests for API client and CLI
  - Performance and reliability testing

## 🔧 Development Workflow

### Environment Setup
```bash
# Main entry point with dependency management
python3 run.py -m pytest tests/unit/

# Code quality checks
ruff check src/
mypy src/

# Docker development environment  
docker-compose up -d
```

### Agent Integration Testing
```bash
# Test AI agents CLI
python3 src/cli/ai_agents.py qwen 'Create a function to validate emails'
python3 src/cli/ai_agents.py deepseek 'Improve retry logic' --file src/services/signalhire_client.py
```

## 📋 Quality Standards

### Code Quality
- **PEP 8 compliance** with ruff linting
- **Type hints** with mypy validation  
- **Async/await patterns** for concurrency
- **Structured logging** with JSON format

### Testing Requirements
- **Test coverage** maintained for critical paths
- **Contract testing** for API reliability
- **Environment testing** across WSL/Linux/Docker

## 🎯 @Symbol Integration

Development workflow integrates with the @symbol coordination system:

```markdown
# Development tasks using @symbol coordination:
- [ ] T063 @qwen Optimize test execution performance
- [ ] T064 @deepseek Refactor test suite architecture  
- [ ] T065 @gemini Document testing best practices
```

The development process supports the multi-agent approach with clear handoffs and quality gates.
