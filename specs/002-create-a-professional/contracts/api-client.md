# SignalHire API Client Contract

## Interface Contract

### SignalHireClient
```python
class SignalHireClient:
    """API-only client for all SignalHire operations"""
    
    def __init__(self, config: ClientConfig):
        """Initialize client with configuration"""
        pass
    
    async def authenticate(self) -> bool:
        """Authenticate with SignalHire API"""
        pass
    
    async def search_prospects(self, criteria: SearchCriteria) -> SearchResponse:
        """Search for prospects using given criteria"""
        pass
    
    async def reveal_contact(self, prospect_uid: str) -> RevealResponse:
        """Reveal contact information for a single prospect"""
        pass
    
    async def batch_reveal_contacts(self, prospect_uids: List[str]) -> List[RevealResponse]:
        """Reveal contact information for multiple prospects"""
        pass
    
    async def get_credits_remaining(self) -> int:
        """Get remaining API credits"""
        pass
    
    async def get_daily_usage(self) -> DailyUsage:
        """Get current day's API usage statistics"""
        pass
    
    async def queue_reveal_operation(self, prospect_uids: List[str]) -> str:
        """Queue a bulk reveal operation, returns operation_id"""
        pass
    
    async def check_operation_status(self, operation_id: str) -> OperationStatus:
        """Check status of a queued operation"""
        pass
```

## API Endpoints

### Authentication
- **Endpoint**: `POST /auth/login`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"email": "user@example.com", "password": "password"}`
- **Success**: `200 OK` with auth token
- **Failure**: `401 Unauthorized`

### Search API
- **Endpoint**: `POST /search/prospects`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: SearchCriteria JSON
- **Success**: `200 OK` with SearchResponse
- **Rate Limit**: No rate limit for search operations

### Person API (Contact Reveal)
- **Endpoint**: `POST /person/reveal`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: `{"prospect_uid": "string"}`
- **Success**: `200 OK` with contact information
- **Rate Limit**: 100 requests per day per account

### Credits API
- **Endpoint**: `GET /credits/remaining`
- **Headers**: `Authorization: Bearer {token}`
- **Success**: `200 OK` with `{"credits": int, "daily_limit": int, "used_today": int}`

### Batch Operations API
- **Endpoint**: `POST /operations/bulk-reveal`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: `{"prospect_uids": ["uid1", "uid2", ...]}`
- **Success**: `202 Accepted` with `{"operation_id": "string"}`
- **Batch Limit**: Maximum 10 prospects per request

### Operation Status API
- **Endpoint**: `GET /operations/{operation_id}/status`
- **Headers**: `Authorization: Bearer {token}`
- **Success**: `200 OK` with OperationStatus

## Error Handling Contract

### Standard Error Response
```json
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Daily limit of 100 reveals exceeded",
        "details": {
            "daily_limit": 100,
            "used_today": 100,
            "reset_time": "2025-01-12T00:00:00Z"
        }
    }
}
```

### Error Codes
- `RATE_LIMIT_EXCEEDED`: Daily API limit reached
- `INSUFFICIENT_CREDITS`: Not enough credits for operation
- `INVALID_PROSPECT_UID`: Prospect UID not found or invalid
- `AUTHENTICATION_FAILED`: Invalid or expired token
- `VALIDATION_ERROR`: Request data validation failed
- `OPERATION_NOT_FOUND`: Operation ID not found
- `BATCH_SIZE_EXCEEDED`: Too many prospects in batch request

## Rate Limiting Contract

### Daily Limits
- **Contact Reveals**: 100 per day per account
- **Search Operations**: Unlimited
- **Credit Checks**: Unlimited
- **Operation Status**: Unlimited

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1641945600
X-RateLimit-Window: 24h
```

## Data Format Contract

### Request Validation
- All UIDs must be 32-character alphanumeric strings
- Email validation follows RFC 5322
- Phone numbers must be in international format
- Search criteria must have at least one non-empty field

### Response Format
- All timestamps in ISO 8601 format (UTC)
- All monetary values as integers (cents)
- All boolean values as true/false (not 1/0)
- All arrays return empty [] if no data, never null

## Authentication Contract

### Token Management
- Tokens expire after 24 hours
- Refresh required before expiration
- Failed requests with 401 should trigger re-authentication
- Maximum 3 concurrent sessions per account

### Security Requirements
- All requests must use HTTPS
- API keys must not be logged or exposed
- Rate limiting based on account, not IP
- Request signing for sensitive operations

## SLA Contract

### Response Times
- Search operations: < 2 seconds
- Single contact reveal: < 1 second
- Batch operations: < 5 seconds (queuing)
- Credit checks: < 500ms
- Operation status: < 500ms

### Availability
- 99.9% uptime SLA
- Planned maintenance windows announced 48 hours in advance
- Graceful degradation during peak usage

### Data Consistency
- Contact reveals are idempotent (same result for same UID)
- Credit deductions are atomic
- Search results consistent within 5-minute window
