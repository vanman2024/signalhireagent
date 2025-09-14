# Data Model: Autonomous Lead Generation System

## Entities

### WorkflowRule
- id: UUID
- name: str
- description: str
- schedule: cron/rrule/iso8601
- search_criteria: JSON
- exclusions: JSON
- owner_id: UUID
- status: enum (active, paused, archived)
- created_at: datetime
- updated_at: datetime

### AgentToolInvocation
- id: UUID
- workflow_rule_id: UUID (FK)
- tool_name: str (e.g., search_prospects, reveal_contacts)
- input_params: JSON
- output_data: JSON
- status: enum (pending, running, success, error)
- started_at: datetime
- finished_at: datetime
- error_message: str (nullable)

### PerformanceMetric
- id: UUID
- workflow_rule_id: UUID (FK)
- metric_name: str (e.g., leads_generated, conversion_rate)
- value: float
- recorded_at: datetime

### User
- id: UUID
- email: str
- name: str
- role: enum (admin, manager, user)
- team_id: UUID (nullable)
- created_at: datetime

### Team
- id: UUID
- name: str
- created_at: datetime

### AuditLog
- id: UUID
- user_id: UUID (FK)
- action: str
- target_type: str
- target_id: UUID
- timestamp: datetime
- details: JSON
