# Data Model: SignalHire Lead Generation Agent

## Future Data Models

### Multi-Platform Extensions
**Purpose**: Support expansion to multiple lead generation platforms

```python
class PlatformCredentials:
    platform: Literal["signalhire", "linkedin", "apollo", "zoominfo"]
    api_key: str | None
    username: str | None 
    password: str | None
    session_token: str | None
    expires_at: datetime | None

class UnifiedSearchCriteria:
    platforms: list[str]  # ["signalhire", "apollo", "linkedin"]
    search_criteria: SearchCriteria
    dedupe_strategy: Literal["email", "linkedin_url", "full_name_company"]
    max_results_per_platform: int

class PlatformProspect(Prospect):
    source_platform: str
    platform_specific_data: dict[str, Any]
    confidence_score: float  # AI matching confidence for deduplication
```

### Team Collaboration Models
**Purpose**: Support multi-user workflows and team management

```python
class User:
    user_id: str
    email: str
    full_name: str
    role: Literal["admin", "manager", "searcher", "revealer", "viewer"]
    credit_limit: int | None
    created_at: datetime
    last_active: datetime

class Team:
    team_id: str
    name: str
    description: str
    owner_user_id: str
    members: list[User]
    credit_pool: int
    monthly_usage: int

class SharedSearchOperation:
    operation_id: str
    created_by: str
    shared_with: list[str]
    assigned_to: str | None
    status: Literal["draft", "running", "completed", "failed"]
    visibility: Literal["private", "team", "public"]
```

### Enterprise & Agency Models
**Purpose**: Support white-label and enterprise features

```python
class Organization:
    org_id: str
    name: str
    subdomain: str | None  # agency.leadgen-platform.com
    custom_branding: BrandingConfig | None
    billing_plan: Literal["free", "professional", "business", "enterprise"]
    monthly_credit_limit: int
    api_access_enabled: bool

class BrandingConfig:
    logo_url: str | None
    primary_color: str | None
    secondary_color: str | None
    custom_domain: str | None
    email_signature: str | None

class CrmIntegration:
    integration_id: str
    platform: Literal["salesforce", "hubspot", "pipedrive"]
    api_credentials: dict[str, str]
    field_mappings: dict[str, str]
    auto_sync_enabled: bool
    last_sync: datetime | None
```

### Analytics & Reporting Models
**Purpose**: Track usage, performance, and business metrics

```python
class UsageAnalytics:
    date: date
    organization_id: str
    user_id: str | None
    searches_performed: int
    prospects_found: int
    contacts_revealed: int
    credits_consumed: int
    platform_breakdown: dict[str, int]

class PerformanceMetrics:
    operation_id: str
    operation_type: Literal["search", "reveal", "export"]
    start_time: datetime
    end_time: datetime
    success_rate: float
    error_count: int
    throughput: float  # operations per minute

class BusinessMetrics:
    date: date
    new_signups: int
    active_users: int
    revenue: float
    churn_rate: float
    upgrade_conversions: int
    platform_usage: dict[str, int]
```

---

## Core Entities

### SearchCriteria
**Purpose**: Encapsulates user-defined search parameters for SignalHire API

**Fields**:
- `current_title: str | None` - Job title filter with Boolean query support
- `location: str | None` - Geographic location (city, state, country)
- `current_company: str | None` - Company name filter with Boolean query support
- `industry: str | None` - Industry category from SignalHire's allowed values
- `keywords: str | None` - Skills and attributes filter with Boolean query support
- `full_name: str | None` - Search by specific person name
- `years_experience_from: int | None` - Minimum years of experience
- `years_experience_to: int | None` - Maximum years of experience
- `open_to_work: bool | None` - Filter by job seeking status
- `size: int` - Number of results per batch (1-100, default 10)

**Validation Rules**:
- At least one search field must be provided
- size must be between 1 and 100
- Boolean queries must use valid operators (AND, OR, NOT, (), "")
- Experience ranges must be logical (from <= to)

**Relationships**:
- Used by SearchOperation to execute searches
- Serialized to JSON for SignalHire Search API requests

### Prospect
**Purpose**: Represents an individual prospect found through search

**Fields**:
- `uid: str` - SignalHire unique identifier (32 characters)
- `full_name: str` - Complete name of the prospect
- `location: str | None` - Current location
- `current_title: str | None` - Current job title
- `current_company: str | None` - Current employer
- `skills: list[str]` - List of skills and competencies
- `experience: list[ExperienceEntry]` - Work history
- `education: list[EducationEntry]` - Educational background
- `contacts_fetched: datetime | None` - When contact info was last retrieved
- `open_to_work: bool` - Job seeking status
- `contacts: list[ContactInfo] | None` - Revealed contact information

**Validation Rules**:
- uid must be exactly 32 characters
- full_name is required
- contacts can only be populated after Person API call
- contacts_fetched timestamp updated when contacts revealed

**Relationships**:
- Contains ExperienceEntry and EducationEntry objects
- Contains ContactInfo objects when contacts revealed
- Used by RevealOperation to track contact revelation progress

### ExperienceEntry
**Purpose**: Represents a single work experience entry

**Fields**:
- `company: str` - Company name
- `title: str` - Job title/position
- `location: str | None` - Work location
- `current: bool` - Whether this is current position
- `started: datetime | None` - Start date
- `ended: datetime | None` - End date (None if current)
- `summary: str | None` - Role description
- `company_size: str | None` - Company size category
- `industry: str | None` - Industry classification

**Validation Rules**:
- ended must be None if current is True
- started must be before ended if both provided
- company and title are required

### EducationEntry
**Purpose**: Represents educational background

**Fields**:
- `university: str` - Institution name
- `faculty: str | None` - School/department
- `degree: list[str]` - Degree types (e.g., ["Bachelor of Arts"])
- `started_year: int | None` - Start year
- `ended_year: int | None` - End year

**Validation Rules**:
- started_year must be before ended_year if both provided
- university is required

### ContactInfo
**Purpose**: Revealed contact information for prospects

**Fields**:
- `type: str` - Contact type ("email", "phone")
- `value: str` - Contact value (email address, phone number)
- `rating: str` - Confidence rating (0-100)
- `sub_type: str | None` - Specific type ("work", "personal", "work_phone")
- `info: str | None` - Additional context information

**Validation Rules**:
- type must be "email" or "phone"
- value must match format for type (email regex, phone format)
- rating must be numeric string 0-100

### SearchOperation
**Purpose**: Tracks a search operation and its results

**Fields**:
- `operation_id: str` - Unique identifier for this operation
- `criteria: SearchCriteria` - Search parameters used
- `request_id: int | None` - SignalHire request ID
- `total_results: int | None` - Total matching prospects
- `scroll_id: str | None` - Pagination token (15-second timeout)
- `prospects: list[Prospect]` - Retrieved prospects
- `status: OperationStatus` - Current operation status
- `created_at: datetime` - Operation start time
- `updated_at: datetime` - Last update time
- `error_message: str | None` - Error details if failed

**State Transitions**:
- PENDING → SEARCHING → COMPLETED/FAILED
- COMPLETED → REVEALING (when reveal operation starts)
- Can return to SEARCHING for pagination

### RevealOperation
**Purpose**: Tracks contact revelation for a set of prospects

**Fields**:
- `operation_id: str` - Unique identifier for this operation
- `search_operation_id: str` - Related search operation
- `prospect_uids: list[str]` - UIDs to reveal contacts for
- `callback_url: str` - URL for SignalHire callbacks
- `request_id: int | None` - SignalHire request ID
- `revealed_contacts: dict[str, list[ContactInfo]]` - UID → contacts mapping
- `status: OperationStatus` - Current operation status
- `credits_used: int` - Credits consumed for this operation
- `created_at: datetime` - Operation start time
- `updated_at: datetime` - Last update time
- `error_message: str | None` - Error details if failed

**State Transitions**:
- PENDING → REVEALING → COMPLETED/FAILED
- Can handle partial completion (some prospects successful, others failed)

### ExportFile
**Purpose**: Represents a generated CSV export file

**Fields**:
- `file_path: str` - Absolute path to generated file
- `prospect_count: int` - Number of prospects included
- `format: ExportFormat` - File format (CSV, XLSX, JSON)
- `columns: list[str]` - Included data columns
- `created_at: datetime` - File generation time
- `size_bytes: int` - File size in bytes

**Validation Rules**:
- file_path must be accessible and writable
- prospect_count must match actual file content
- format must be supported export format

### OperationLog
**Purpose**: Audit trail for all agent operations

**Fields**:
- `log_id: str` - Unique log entry identifier
- `operation_type: str` - Type of operation (SEARCH, REVEAL, EXPORT)
- `operation_id: str` - Related operation identifier
- `level: str` - Log level (INFO, WARN, ERROR)
- `message: str` - Human-readable log message
- `structured_data: dict` - Machine-readable context
- `timestamp: datetime` - When log entry was created

**Validation Rules**:
- level must be valid log level
- structured_data must be JSON serializable
- operation_id must reference valid operation

## Enumerations

### OperationStatus
- `PENDING` - Operation queued but not started
- `SEARCHING` - Actively searching SignalHire
- `REVEALING` - Revealing contact information
- `COMPLETED` - Operation finished successfully
- `FAILED` - Operation failed with error
- `CANCELLED` - Operation cancelled by user

### ExportFormat
- `CSV` - Comma-separated values
- `XLSX` - Excel format
- `JSON` - JSON format

## Entity Relationships

```
SearchCriteria
    ↓ (used by)
SearchOperation
    ↓ (produces)
Prospect[]
    ↓ (input to)
RevealOperation
    ↓ (populates)
Prospect.contacts[]
    ↓ (exported via)
ExportFile

OperationLog ← (tracks all operations)
```

## Validation Strategy

### Input Validation
- Pydantic models with custom validators
- API parameter validation before requests
- File path validation before export operations
- Configuration validation at startup

### Data Integrity
- Immutable operation IDs using UUID4
- Timestamp consistency (created_at ≤ updated_at)
- Status transition validation
- Credit usage tracking and limits

### Error Handling
- Structured error messages with context
- Operation rollback for critical failures
- Partial success handling for batch operations
- Clear user feedback for validation failures
