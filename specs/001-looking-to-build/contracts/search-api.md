# SignalHire Search API Contract

## Endpoint
`POST https://www.signalhire.com/api/v1/candidate/searchByQuery`

## Request Schema

### Headers
```json
{
  "apikey": "string",
  "Content-Type": "application/json"
}
```

### Body Schema
```json
{
  "currentTitle": "string | null",
  "currentPastTitle": "string | null", 
  "location": "string | null",
  "currentCompany": "string | null",
  "currentPastCompany": "string | null",
  "fullName": "string | null",
  "keywords": "string | null",
  "industry": "string | null",
  "yearsOfCurrentExperienceFrom": "number | null",
  "yearsOfCurrentExperienceTo": "number | null",
  "yearsOfCurrentPastExperienceFrom": "number | null",
  "yearsOfCurrentPastExperienceTo": "number | null",
  "openToWork": "boolean | null",
  "size": "number"
}
```

### Validation Rules
- At least one search parameter must be provided
- `size` must be between 1 and 100
- Boolean queries support AND, OR, NOT, (), "" operators
- Experience ranges: from ≤ to

## Response Schema

### Success Response (200)
```json
{
  "requestId": "number",
  "total": "number", 
  "scrollId": "string | null",
  "profiles": [
    {
      "uid": "string",
      "fullName": "string",
      "location": "string | null",
      "experience": [
        {
          "company": "string",
          "title": "string"
        }
      ],
      "skills": ["string"],
      "contactsFetched": "string | null",
      "openToWork": "boolean"
    }
  ]
}
```

### Error Responses
- `401`: Authentication failed (invalid API key)
- `402`: Daily search quota exceeded  
- `406`: Requested more than 100 items
- `422`: Invalid request parameters
- `429`: Rate limit exceeded (only 3 concurrent requests)
- `500`: Internal server error

## Rate Limits
- Maximum 3 concurrent search requests
- Daily quota limits (varies by account)
- ScrollId expires after 15 seconds

## Example Request
```bash
curl -X POST \
  -H 'apikey: your_api_key' \
  -H 'Content-Type: application/json' \
  https://www.signalhire.com/api/v1/candidate/searchByQuery \
  --data '{
    "currentTitle": "(Software AND Engineer) OR Developer",
    "location": "New York, New York, United States", 
    "keywords": "PHP AND JavaScript",
    "size": 20
  }'
```

## Example Response
```json
{
  "requestId": 12345,
  "total": 150,
  "scrollId": "abc123xyz",
  "profiles": [
    {
      "uid": "10000000000000000000000000001006",
      "fullName": "John Smith", 
      "location": "New York, NY, United States",
      "experience": [
        {
          "company": "Tech Corp",
          "title": "Software Engineer"
        }
      ],
      "skills": ["JavaScript", "Python", "React"],
      "contactsFetched": null,
      "openToWork": true
    }
  ]
}
```
