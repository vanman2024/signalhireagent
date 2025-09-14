# Research: Autonomous Lead Generation System MCP Server & Agentic Workflows

## MCP Server Architecture
- **Pattern**: FastAPI-based MCP server wraps existing SignalHire CLI commands as agent tools (search, reveal, export) using subprocess, returning structured JSON to agents.
- **Rationale**: Leverages proven CLI code for immediate agent functionality, minimizes risk, and accelerates validation. CLI remains ground truth for all MCP tool behavior.
- **Alternatives Considered**: Direct API integration for each tool (chosen for future optimization, not initial implementation).

## Claude Code SDK Patterns
- **Pattern**: Persistent Claude Code agent sessions orchestrate workflows by invoking MCP tools via structured API calls.
- **Rationale**: Enables 24/7 autonomous operation, supports natural language configuration, and allows agents to adapt workflows based on performance data.
- **Alternatives Considered**: Stateless agent invocations (rejected for lack of persistence and context).

## Autonomous Workflow Research
- **Pattern**: Workflows are defined in natural language, parsed into structured rules, and executed on a schedule or in response to business events.
- **Rationale**: Empowers "set it and forget it" operation, supports business intelligence, and enables continuous optimization.
- **Best Practices**: Use Celery/Redis for scheduling, PostgreSQL for workflow state, and WebSockets for real-time updates.
- **Open Questions**: How to best support multi-market coordination and advanced analytics in agent workflows?
