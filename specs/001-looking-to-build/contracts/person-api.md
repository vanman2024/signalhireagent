# SignalHire Person API Contract

## Endpoint
`POST https://www.signalhire.com/api/v1/candidate/search`

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
  "items": ["string"],
  "callbackUrl": "string",
  "withoutContacts": "boolean | null"
}
```

### Validation Rules
- `items` array can contain up to 100 elements
- Each item can be: LinkedIn URL, email, phone, or 32-character UID
- `callbackUrl` must be accessible from SignalHire servers
- `withoutContacts` defaults to false

## Response Schema

### Success Response (201)
```json
{
  "requestId": "number"
}
```

### Error Responses
- `401`: Authentication failed (invalid API key)
- `402`: Out of credits
- `403`: Account disabled or unauthorized request
- `404`: Invalid JSON data or non-existing request
- `406`: More than 100 items requested
- `422`: Malformed request parameters
- `429`: Rate limit exceeded (600 items per minute)
- `500`: Internal server error

## Callback Schema

The callback will be sent to the provided `callbackUrl` via POST request.

### Callback Headers
```json
{
  "Request-Id": "string",
  "Content-Type": "application/json"
}
```

### Callback Body Schema
```json
[
  {
    "status": "success | failed | credits_are_over | timeout_exceeded | duplicate_query",
    "item": "string",
    "candidate": {
      "uid": "string",
      "fullName": "string",
      "gender": "string | null",
      "photo": {
        "url": "string"
      },
      "locations": [
        {
          "name": "string"
        }
      ],
      "skills": ["string"],
      "education": [
        {
          "faculty": "string | null",
          "university": "string",
          "url": "string | null", 
          "startedYear": "number | null",
          "endedYear": "number | null",
          "degree": ["string"]
        }
      ],
      "experience": [
        {
          "position": "string",
          "location": "string | null",
          "current": "boolean",
          "started": "string | null",
          "ended": "string | null", 
          "company": "string",
          "summary": "string | null",
          "companyUrl": "string | null",
          "companySize": "string | null",
          "staffCount": "number | null",
          "industry": "string | null",
          "website": "string | null"
        }
      ],
      "contacts": [
        {
          "type": "email | phone",
          "value": "string",
          "rating": "string",
          "subType": "work | personal | work_phone | etc",
          "info": "string | null"
        }
      ],
      "social": [
        {
          "type": "li | fb | tw | etc",
          "link": "string", 
          "rating": "string"
        }
      ],
      "headLine": "string | null",
      "summary": "string | null",
      "language": [
        {
          "name": "string",
          "proficiency": "string"
        }
      ]
    }
  }
]
```

## Rate Limits
- Maximum 600 elements per minute
- Maximum 100 elements per request
- No strict limit on parallel requests (but throttling may occur)

## Callback Requirements
- Callback URL must respond with HTTP 200 status
- 10-second timeout for callback responses
- 3 retry attempts on failure
- Callback URL must be accessible from internet

## Example Request
```bash
curl -X POST \
  -H 'apikey: your_api_key' \
  -H 'Content-Type: application/json' \
  https://www.signalhire.com/api/v1/candidate/search \
  --data '{
    "items": [
      "https://www.linkedin.com/in/john-doe",
      "john.doe@example.com",
      "+1-555-123-4567",
      "10000000000000000000000000001006"
    ],
    "callbackUrl": "https://yourdomain.com/signalhire/callback"
  }'
```

## Example Response
```json
{
  "requestId": 67890
}
```

## Example Callback
```json
[
  {
    "status": "success",
    "item": "10000000000000000000000000001006",
    "candidate": {
      "uid": "10000000000000000000000000001006",
      "fullName": "John Doe",
      "locations": [
        {
          "name": "New York, NY, United States"
        }
      ],
      "contacts": [
        {
          "type": "email",
          "value": "john.doe@company.com",
          "rating": "100",
          "subType": "work"
        },
        {
          "type": "phone", 
          "value": "+1-555-123-4567",
          "rating": "95",
          "subType": "work_phone"
        }
      ]
    }
  }
]
```
