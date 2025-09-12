# Data Model: API-Focused Architecture

## Core Data Models
*These remain unchanged as they're already API-optimized*

### Prospect
```python
@dataclass
class Prospect:
    uid: str  # 32-character unique identifier
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    contact_info: Optional[ContactInfo] = None
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    revealed: bool = False
    reveal_timestamp: Optional[datetime] = None
```

### ContactInfo
```python
@dataclass
class ContactInfo:
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    verified: bool = False
    confidence_score: Optional[float] = None
```

### SearchCriteria
```python
@dataclass
class SearchCriteria:
    keywords: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    seniority: Optional[str] = None
    limit: int = 50
```

## Service Layer Architecture

### SignalHireClient (Enhanced)
```python
class SignalHireClient:
    """API-only client for SignalHire operations"""
    
    # Core API operations
    async def search_prospects(self, criteria: SearchCriteria) -> List[Prospect]
    async def reveal_contact(self, prospect_uid: str) -> ContactInfo
    async def get_credits_remaining() -> int
    async def batch_reveal_contacts(self, prospect_uids: List[str]) -> Dict[str, ContactInfo]
    
    # Enhanced for API-only approach
    async def queue_reveal_operation(self, prospect_uids: List[str]) -> str  # Returns operation_id
    async def check_operation_status(self, operation_id: str) -> OperationStatus
    async def get_daily_usage() -> DailyUsage
```

### RateLimiter (Enhanced)
```python
class RateLimiter:
    """Enhanced rate limiting for API operations"""
    
    def __init__(self, daily_limit: int = 100):
        self.daily_limit = daily_limit
        self.daily_usage = 0
        self.reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    async def can_reveal(self, count: int = 1) -> bool
    async def record_usage(self, count: int)
    async def get_remaining_capacity() -> int
    async def time_until_reset() -> timedelta
```

## Data Flow Architecture

### Search Flow
```
User Input (SearchCriteria) 
→ SignalHireClient.search_prospects()
→ API Request to SignalHire Search API
→ Parse JSON Response
→ Convert to List[Prospect]
→ Return to CLI/User
```

### Reveal Flow
```
Prospect UIDs
→ RateLimiter.can_reveal() check
→ SignalHireClient.reveal_contact() or batch_reveal_contacts()
→ API Request to SignalHire Person API
→ Parse JSON Response
→ Update Prospect.contact_info
→ Record usage in RateLimiter
→ Return ContactInfo
```

### Export Flow
```
List[Prospect] with revealed contacts
→ CSVExporter.export_prospects()
→ pandas DataFrame conversion
→ CSV file generation
→ Return file path
```

## Data Persistence

### In-Memory Storage
```python
class ProspectStore:
    """In-memory storage for current session"""
    
    def __init__(self):
        self.prospects: Dict[str, Prospect] = {}
        self.search_history: List[SearchCriteria] = []
        self.operations: Dict[str, Operation] = {}
    
    def add_prospects(self, prospects: List[Prospect])
    def get_prospect(self, uid: str) -> Optional[Prospect]
    def update_contact_info(self, uid: str, contact_info: ContactInfo)
    def get_revealed_prospects() -> List[Prospect]
```

### Session Data (No Database Required)
- **Search Results**: Stored in memory for current session
- **Revealed Contacts**: Updated in Prospect objects
- **Rate Limit State**: Tracked in RateLimiter instance
- **Export Queue**: Managed in CSVExporter

## API Response Models

### SearchResponse
```python
@dataclass
class SearchResponse:
    prospects: List[Prospect]
    total_count: int
    page: int
    has_more: bool
    search_id: str
```

### RevealResponse
```python
@dataclass
class RevealResponse:
    prospect_uid: str
    contact_info: ContactInfo
    credits_used: int
    success: bool
    error_message: Optional[str] = None
```

### OperationStatus
```python
@dataclass
class OperationStatus:
    operation_id: str
    status: str  # "pending", "processing", "completed", "failed"
    completed_count: int
    total_count: int
    results: List[RevealResponse]
    created_at: datetime
    updated_at: datetime
```

## Error Handling Models

### APIError
```python
@dataclass
class APIError(Exception):
    status_code: int
    message: str
    error_code: Optional[str] = None
    retry_after: Optional[int] = None
```

### RateLimitError
```python
@dataclass
class RateLimitError(APIError):
    daily_limit: int
    current_usage: int
    reset_time: datetime
```

## Configuration Models

### ClientConfig
```python
@dataclass
class ClientConfig:
    api_key: str
    base_url: str = "https://api.signalhire.com"
    timeout: int = 30
    max_retries: int = 3
    daily_limit: int = 100
    batch_size: int = 10
```

## Data Validation Rules

1. **Prospect UID**: Must be 32 characters, alphanumeric
2. **Email Validation**: RFC 5322 compliant when provided
3. **Phone Validation**: International format when provided
4. **Search Criteria**: At least one field must be provided
5. **Rate Limits**: Cannot exceed daily API limits
6. **Batch Operations**: Maximum 10 prospects per batch request

## Memory Optimization

- **Lazy Loading**: Load contact details only when needed
- **Weak References**: Use weak references for large prospect lists
- **Data Cleanup**: Clear old search results after export
- **Batch Processing**: Process reveals in configurable batch sizes
- **Streaming Export**: Stream large datasets to CSV without loading all in memory
