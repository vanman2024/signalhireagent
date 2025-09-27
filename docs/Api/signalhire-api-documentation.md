# SignalHire API Complete Documentation

## Overview

The SignalHire API provides two main services:
1. **Person API** - Retrieve detailed contact information for specific individuals
2. **Search API** - Search for prospects in the database using filters

## Authentication

- **Method**: API Key in header
- **Header**: `apikey: your_secret_api_key`
- **API Key Location**: Available in SignalHire account under "Integrations & API"

## Base URLs and Endpoints

### Person API
- **Base URL**: `https://www.signalhire.com/api/v1`
- **Main Endpoint**: `POST /candidate/search`
- **Credits Check**: `GET /credits`

### Search API
- **Search Endpoint**: `POST /candidate/searchByQuery` 
- **Scroll Search**: `POST /candidate/scrollSearch/{requestId}`

## Person API - Contact Revelation

### Endpoint: POST /candidate/search

**Purpose**: Retrieve detailed contact information (emails, phones, LinkedIn) for specific individuals.

**Request Format**:
```json
{
  "items": [
    "https://www.linkedin.com/in/profile1",
    "email@example.com", 
    "+44 0 123 456 789",
    "10000000000000000000000000000001"
  ],
  "callbackUrl": "https://yourdomain.com/callback"
}
```

**Headers**:
```
apikey: your_secret_api_key
Content-Type: application/json
```

**Response** (HTTP 201):
```json
{
  "requestId": 1
}
```

**Callback Response** (sent to your callback URL):
```json
[
  {
    "item": "https://www.linkedin.com/in/profile1",
    "status": "success",
    "candidate": {
      "uid": "abc123def456gh789ijk012lmn345op6",
      "fullName": "John Doe",
      "contacts": [
        {
          "type": "email",
          "value": "john.doe@company.com",
          "rating": "100",
          "subType": "work"
        },
        {
          "type": "phone", 
          "value": "+1 555-123-4567",
          "rating": "100",
          "subType": "work_phone"
        }
      ],
      "experience": [...],
      "skills": [...],
      "education": [...]
    }
  }
]
```

### Status Values:
- `success` - Contact information retrieved
- `failed` - Person not found or processing failed
- `credits_are_over` - No credits remaining
- `timeout_exceeded` - Request timed out
- `duplicate_query` - Duplicate request detected

### Rate Limits:
- **Maximum per request**: 100 items
- **Rate limit**: 600 items per minute
- **Parallel requests**: No strict limit but may be throttled

## Search API - Finding Prospects

### Endpoint: POST /candidate/searchByQuery

**Purpose**: Search for prospects using filters. Returns profile data WITHOUT contact information.

**Request Format**:
```json
{
  "currentTitle": "(Software AND Engineer) OR Developer",
  "location": "New York, New York, United States", 
  "keywords": "PHP AND JavaScript",
  "excludeRevealed": true,
  "size": 50
}
```

**Key Filters**:
- `currentTitle` - Current job title (Boolean query)
- `currentPastTitle` - Current or past job titles
- `location` - Geographic location(s) 
- `currentCompany` - Current company name
- `currentPastCompany` - Current or past companies
- `keywords` - Skills, education, description keywords
- `excludeRevealed` - Exclude already revealed contacts
- `excludeWatched` - Exclude already viewed profiles
- `size` - Number of results (1-100, default 10)

**Response**:
```json
{
  "requestId": 3,
  "total": 500,
  "scrollId": "abc123",
  "profiles": [
    {
      "uid": "10000000000000000000000000001006",
      "fullName": "Aaron Smith", 
      "location": "London, United Kingdom",
      "experience": [
        {
          "company": "Tech Corp",
          "title": "Software Engineer"
        }
      ],
      "skills": ["JavaScript", "Python"],
      "contactsFetched": null,
      "openToWork": false
    }
  ]
}
```

### Pagination with Scroll Search

**Endpoint**: `POST /candidate/scrollSearch/{requestId}`

**Request**:
```json
{
  "scrollId": "abc123"
}
```

**Important Notes**:
- `scrollId` expires after 15 seconds
- Must use `requestId` from original search in URL
- Up to 3 concurrent search requests allowed

## Credits Management

### Check Remaining Credits

**Endpoint**: `GET /credits`

**Response**:
```json
{
  "credits": 27
}
```

**Alternative**: Check `X-Credits-Left` header in any API response.

## Error Codes

- **200** - Success, data retrieved
- **201** - Request accepted, processing started
- **204** - Request in progress
- **401** - Authentication failed (bad API key)
- **402** - No credits remaining
- **403** - Account disabled or unauthorized access
- **404** - Invalid request or endpoint not found
- **406** - Too many items in request (>100)
- **422** - Malformed request parameters
- **429** - Rate limit exceeded (600/min for Person API, 3 concurrent for Search API)
- **500** - Internal server error

## Key Insights for Our Integration

### Why Our Cached Contacts Are Empty

1. **Search vs Reveal**: Our cached contacts are from Search API calls, which return profiles WITHOUT contact information
2. **Contact Revelation Required**: To get actual emails/phones, we need to use Person API `/candidate/search` endpoint
3. **Callback Required**: Person API requires a callback URL - results are sent asynchronously
4. **Credit Cost**: Each contact revelation costs credits

### Correct Integration Flow

1. **Search for prospects**: Use Search API to find candidates
2. **Filter results**: Apply business logic to select relevant prospects  
3. **Reveal contacts**: Use Person API to get contact details for selected prospects
4. **Handle callbacks**: Set up server to receive contact data
5. **Cache revealed data**: Store complete contact information
6. **Export to Airtable**: Process only contacts with actual contact information

### excludeRevealed Parameter

The Search API has an `excludeRevealed: true` parameter that excludes profiles for which the user has already requested contact details. This is perfect for avoiding duplicate revelations.

## Implementation Requirements

1. **Callback Server**: Must implement HTTP server to receive Person API results
2. **Async Processing**: Person API is asynchronous - results come via callback
3. **Error Handling**: Handle various status codes and retry logic
4. **Rate Limiting**: Respect 600 items/minute limit
5. **Credit Management**: Monitor remaining credits before making requests

## Fixed API Client Requirements

The current SignalHire client needs these corrections:

1. **Base URL**: Change from `https://www.signalhire.com` to `https://www.signalhire.com/api/v1`
2. **Endpoints**: Use correct endpoint paths:
   - Reveal: `POST /candidate/search` (not `/prospects/{id}/reveal`)
   - Credits: `GET /credits` (not `/account`)
   - Search: `POST /candidate/searchByQuery`
3. **Headers**: Use `apikey` header (not `Authorization: Bearer`)
4. **Callback Pattern**: Implement callback URL handling for Person API
5. **Async Results**: Handle asynchronous response pattern correctly