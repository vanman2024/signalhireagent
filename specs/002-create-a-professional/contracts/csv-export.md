# CSV Export Contract

## Export Service Interface

### CSVExporter
```python
class CSVExporter:
    """CSV export service for prospect and contact data"""
    
    def __init__(self, config: ExportConfig):
        """Initialize exporter with configuration"""
        pass
    
    async def export_prospects(self, prospects: List[Prospect], output_path: str) -> str:
        """Export prospects to CSV file"""
        pass
    
    async def export_search_results(self, search_response: SearchResponse, output_path: str) -> str:
        """Export search results to CSV"""
        pass
    
    async def export_revealed_contacts(self, prospects: List[Prospect], output_path: str) -> str:
        """Export only prospects with revealed contact info"""
        pass
    
    async def stream_export(self, prospects: Iterator[Prospect], output_path: str) -> str:
        """Stream large datasets to CSV without loading all in memory"""
        pass
    
    def generate_filename(self, prefix: str = "signalhire", timestamp: bool = True) -> str:
        """Generate standardized filename"""
        pass
```

## CSV Format Specification

### Standard Prospect Export
```csv
uid,name,title,company,location,email,phone,linkedin_url,verified,confidence_score,revealed,reveal_timestamp,experience_count,education_count
abc123def456ghi789jkl012mno345pq,John Doe,Software Engineer,Google Inc,"San Francisco, CA",john.doe@example.com,+1-555-0123,https://linkedin.com/in/johndoe,true,0.95,true,2025-01-11T15:30:00Z,3,2
def456ghi789jkl012mno345pqabc123,Jane Smith,Product Manager,Microsoft,"Seattle, WA",,,,false,,false,,2,1
```

### Detailed Export with Experience
```csv
uid,name,title,company,location,email,phone,linkedin_url,current_position,previous_positions,total_experience_years,industries,skills
abc123...,John Doe,Software Engineer,Google Inc,"San Francisco, CA",john.doe@example.com,+1-555-0123,https://linkedin.com/in/johndoe,"Software Engineer at Google (2022-Present)","Backend Developer at Uber (2020-2022); Junior Developer at Startup (2018-2020)",5,"Technology; Software Development","Python; Django; PostgreSQL; AWS"
```

### Contact-Only Export  
```csv
uid,name,email,phone,linkedin_url,verified,confidence_score,reveal_timestamp
abc123...,John Doe,john.doe@example.com,+1-555-0123,https://linkedin.com/in/johndoe,true,0.95,2025-01-11T15:30:00Z
```

## Export Configuration

### ExportConfig
```python
@dataclass
class ExportConfig:
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: str = "\\"
    line_terminator: str = "\n"
    include_header: bool = True
    timestamp_format: str = "%Y-%m-%dT%H:%M:%SZ"
    filename_timestamp_format: str = "%Y%m%d_%H%M%S"
    max_field_length: int = 32767  # Excel limit
    handle_unicode: bool = True
    encoding: str = "utf-8"
```

### Field Mappings
```python
STANDARD_FIELDS = [
    "uid",
    "name", 
    "title",
    "company",
    "location",
    "email",
    "phone", 
    "linkedin_url",
    "verified",
    "confidence_score",
    "revealed",
    "reveal_timestamp"
]

DETAILED_FIELDS = STANDARD_FIELDS + [
    "experience_count",
    "education_count", 
    "current_position",
    "previous_positions",
    "total_experience_years",
    "industries",
    "skills"
]

CONTACT_ONLY_FIELDS = [
    "uid",
    "name",
    "email", 
    "phone",
    "linkedin_url",
    "verified",
    "confidence_score",
    "reveal_timestamp"
]
```

## Data Processing Rules

### Field Formatting
- **UIDs**: Always 32 characters, no formatting
- **Names**: Title case, trim whitespace
- **Emails**: Lowercase, validate format
- **Phones**: International format (+1-555-0123)
- **URLs**: Full URLs with protocol
- **Timestamps**: ISO 8601 format in UTC
- **Booleans**: "true"/"false" (lowercase)
- **Numbers**: No thousand separators
- **Null Values**: Empty string (not "null" or "None")

### Text Cleaning
- Remove newlines and tabs from fields
- Escape quote characters in text fields
- Truncate fields exceeding max_field_length
- Handle unicode characters properly
- Remove leading/trailing whitespace

### List Field Handling
```python
# Experience positions: semicolon-separated
"Software Engineer at Google (2022-Present); Backend Developer at Uber (2020-2022)"

# Skills: semicolon-separated
"Python; Django; PostgreSQL; AWS; Docker"

# Industries: semicolon-separated  
"Technology; Software Development; Cloud Computing"
```

## File Management

### Filename Generation
```python
def generate_filename(prefix: str, suffix: str = "", timestamp: bool = True) -> str:
    """
    Examples:
    - signalhire_search_20250111_153045.csv
    - signalhire_contacts_revealed_20250111_153045.csv
    - signalhire_workflow_results_20250111_153045.csv
    """
    pass
```

### File Operations
- **Atomic Writes**: Write to temporary file, then rename
- **Backup Existing**: Rename existing files with .backup suffix
- **Compression**: Optional gzip compression for large files
- **Validation**: Verify CSV format after writing
- **Permissions**: Set appropriate file permissions (644)

## Export Types

### 1. Search Results Export
```python
await exporter.export_search_results(search_response, "search_results.csv")
```
- Includes all prospects from search
- No contact information (not revealed yet)
- Basic prospect information only

### 2. Revealed Contacts Export
```python
await exporter.export_revealed_contacts(prospects, "contacts.csv") 
```
- Only prospects with revealed contact info
- Includes email, phone, LinkedIn URL
- Includes verification status and confidence scores

### 3. Full Prospect Export
```python
await exporter.export_prospects(prospects, "full_export.csv")
```
- All prospect data including experience and education
- Contact info if revealed
- Complete profile information

### 4. Streaming Export (Large Datasets)
```python
async def prospect_generator():
    for batch in get_prospect_batches():
        for prospect in batch:
            yield prospect

await exporter.stream_export(prospect_generator(), "large_export.csv")
```

## Performance Specifications

### Memory Usage
- **Batch Processing**: Process in chunks of 1,000 records
- **Streaming**: Use generators for datasets > 10,000 records
- **Memory Limit**: Never load more than 100MB of data at once
- **Cleanup**: Release memory after each batch

### Speed Requirements
- **Small Files** (<1,000 records): < 1 second
- **Medium Files** (1,000-10,000 records): < 10 seconds  
- **Large Files** (10,000+ records): < 60 seconds
- **Streaming**: 500+ records per second sustained

### File Size Limits
- **Maximum Records**: 1,000,000 per file
- **Maximum File Size**: 500MB uncompressed
- **Split Large Files**: Automatically split if exceeding limits
- **Compression**: Optional gzip for files > 10MB

## Error Handling

### Export Errors
```python
class ExportError(Exception):
    """Base export error"""
    pass

class InvalidDataError(ExportError):
    """Invalid data format error"""
    pass

class FilesystemError(ExportError):
    """File system operation error"""
    pass

class CompressionError(ExportError):
    """Compression operation error"""
    pass
```

### Validation Rules
- Validate all prospect data before export
- Check file permissions before writing
- Verify CSV format after generation
- Validate required fields are present
- Check for data consistency

## Integration Contract

### CLI Integration
```bash
# Export search results
signalhire search --title "Engineer" --output results.csv

# Export revealed contacts only
signalhire reveal --input prospects.csv --output contacts.csv

# Full workflow export  
signalhire workflow --search criteria.json --output final.csv
```

### API Integration
```python
# Use with SignalHireClient
prospects = await client.search_prospects(criteria)
export_path = await exporter.export_prospects(prospects, "output.csv")

# Chain operations
search_response = await client.search_prospects(criteria) 
revealed_prospects = await client.batch_reveal_contacts(search_response.prospect_uids)
final_path = await exporter.export_revealed_contacts(revealed_prospects, "final.csv")
```
