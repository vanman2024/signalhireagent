# SignalHire Credits API Contract

## Endpoint
`GET https://www.signalhire.com/api/v1/credits`

## Request Schema

### Headers
```json
{
  "apikey": "string"
}
```

### Query Parameters
- `withoutContacts`: boolean (optional) - Check credits for profiles without contacts

## Response Schema

### Success Response (200)
```json
{
  "credits": "number"
}
```

### Error Responses
- `401`: Authentication failed (invalid API key)
- `403`: Account disabled
- `500`: Internal server error

## Usage
- Check remaining credits before expensive operations
- Monitor credit consumption during bulk reveals
- Separate credit pools for regular vs "without contacts" operations

## Example Request
```bash
# Check regular credits
curl -X GET \
  -H 'apikey: your_api_key' \
  https://www.signalhire.com/api/v1/credits

# Check "without contacts" credits  
curl -X GET \
  -H 'apikey: your_api_key' \
  https://www.signalhire.com/api/v1/credits?withoutContacts=true
```

## Example Response
```json
{
  "credits": 247
}
```
