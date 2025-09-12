# SignalHire Scroll Search API Contract

## Endpoint
`POST https://www.signalhire.com/api/v1/candidate/scrollSearch/{requestId}`

## Request Schema

### Headers
```json
{
  "apikey": "string",
  "Content-Type": "application/json"
}
```

### URL Parameters
- `requestId`: Number from initial searchByQuery response

### Body Schema
```json
{
  "scrollId": "string"
}
```

### Validation Rules
- `requestId` must match a valid search request
- `scrollId` must be from previous search response
- `scrollId` expires after 15 seconds

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
- `402`: Daily search quota exceeded
- `404`: Invalid or expired scrollId
- `429`: Only three requests allowed at the same time

## Pagination Logic
- Each response includes `scrollId` if more results available
- `scrollId` is `null` when no more results
- `total` field always shows complete result count
- `profiles` contains current batch only

## Example Request
```bash
curl -X POST \
  -H 'apikey: your_api_key' \
  -H 'Content-Type: application/json' \
  https://www.signalhire.com/api/v1/candidate/scrollSearch/12345 \
  --data '{
    "scrollId": "abc123xyz"
  }'
```

## Example Response
```json
{
  "requestId": 12345,
  "total": 150,
  "scrollId": "def456uvw",
  "profiles": [
    {
      "uid": "10000000000000000000000000001007",
      "fullName": "Jane Smith",
      "location": "San Francisco, CA, United States", 
      "experience": [
        {
          "company": "Startup Inc",
          "title": "Product Manager"
        }
      ],
      "skills": ["Product Management", "Analytics"],
      "contactsFetched": null,
      "openToWork": false
    }
  ]
}
```
