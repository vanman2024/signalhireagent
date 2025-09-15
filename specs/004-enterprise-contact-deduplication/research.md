# Research: Contact Deduplication and Search Optimization

**Feature**: 004-enterprise-contact-deduplication
**Phase**: 0 - Research and Investigation
**Date**: September 15, 2025

## Technical Decisions

### File-Based vs Database Approach
**Decision**: File-based processing with JSON input/output and CSV exports
**Rationale**:
- Avoids database setup complexity mentioned in user requirements
- Maintains simplicity for initial implementation
- Enables easy backup and versioning of contact data
- Compatible with existing CLI architecture patterns
- Provides clear data lineage from search results to final exports

**Alternatives considered**:
- SQLite embedded database: Rejected due to complexity requirement
- In-memory only: Rejected due to resume capability requirement
- Cloud database: Rejected due to local-first approach

### Deduplication Strategy
**Decision**: Multi-level deduplication using uid as primary key, LinkedIn URL as secondary
**Rationale**:
- SignalHire uid is most reliable unique identifier
- LinkedIn URL provides fallback for uid mismatches or missing data
- Handles edge cases where same person has different names but same LinkedIn profile
- Provides clear audit trail of which deduplication method was used

**Alternatives considered**:
- Name + company matching: Rejected due to unreliability (name variations, company changes)
- Email-based: Rejected as emails not available until after reveal
- Fuzzy string matching: Rejected due to complexity and false positives

### Memory Management for Large Datasets
**Decision**: Streaming JSON processing with chunked operations
**Rationale**:
- Handles 7,000+ contacts without memory issues
- Enables progress tracking and resume capability
- Maintains performance under 5-minute target for processing
- Allows for memory-efficient filtering and analysis

**Alternatives considered**:
- Load entire dataset: Rejected due to memory constraints at scale
- Database streaming: Rejected due to no-database requirement
- External sorting: Rejected as overkill for expected dataset size

### Progress Tracking and Resume Capability
**Decision**: Simple JSON state files with operation checkpoints
**Rationale**:
- Enables resume of large reveal operations
- Provides clear audit trail of processing steps
- Compatible with existing CLI patterns
- Easy to implement and debug

**Alternatives considered**:
- In-memory tracking only: Rejected due to resume requirement
- Database state tracking: Rejected due to no-database constraint
- Complex checkpoint system: Rejected due to simplicity requirement

### Quality Filtering Strategy
**Decision**: Configurable exclusion lists with job title pattern matching
**Rationale**:
- Addresses core user need to filter Heavy Equipment Operators
- Provides flexibility for different role types and campaigns
- Enables quality scoring before expensive reveal operations
- Reduces credit waste on unwanted contacts

**Alternatives considered**:
- Machine learning classification: Rejected due to complexity
- Manual review process: Rejected due to scale (7,000+ contacts)
- Simple keyword blacklist: Enhanced to pattern matching for better accuracy

## Integration Points

### Existing CLI Integration
**Approach**: Extend existing CLI with new command groups
- `signalhire dedupe` - Deduplication operations
- `signalhire analyze` - Quality analysis and reporting
- `signalhire filter` - Contact filtering operations

### SignalHire API Compatibility
**Approach**: Process SignalHire JSON format as-is
- Maintain compatibility with existing search result format
- Preserve all original data for audit purposes
- Add metadata fields for tracking deduplication decisions

### Export Integration
**Approach**: Leverage existing CSV export functionality
- Extend with deduplication metadata
- Maintain backward compatibility with current reveal workflows
- Add progress tracking for large exports

## Performance Considerations

### Processing Speed Targets
- Deduplication: Under 30 seconds for 7,000 contacts
- Quality analysis: Under 1 minute for job title distribution
- File operations: Under 5 minutes for complete workflow
- Memory usage: Under 1GB for 100,000 contact processing

### Scalability Approach
- Stream processing for memory efficiency
- Chunked operations for progress tracking
- Parallel processing for independent operations
- Optimized data structures for deduplication lookups

## Risk Assessment

### Data Integrity Risks
- **Risk**: Loss of original search data during processing
- **Mitigation**: Automatic backup creation before any modification

### Performance Risks
- **Risk**: Memory exhaustion with very large datasets
- **Mitigation**: Streaming processing and memory monitoring

### Usability Risks
- **Risk**: Complex command structure confusing users
- **Mitigation**: Clear help text and example workflows in quickstart

### Compatibility Risks
- **Risk**: Breaking existing CLI workflows
- **Mitigation**: Additive approach - new commands don't modify existing behavior

## Success Metrics

### Functional Success
- Successfully merge 5+ JSON files with 7,000+ total contacts
- Achieve >95% deduplication accuracy using uid + LinkedIn URL
- Filter >90% of unwanted job titles (operators, drivers)
- Resume interrupted operations without data loss

### Performance Success
- Complete deduplication in <5 minutes for 7,000 contacts
- Process files up to 100MB without memory issues
- Generate analysis reports in <30 seconds

### User Experience Success
- Clear command structure following existing CLI patterns
- Comprehensive help and error messages
- Workflow completion within 10 CLI commands maximum

---

**Research Status**: Complete
**Next Phase**: Design & Contracts (Phase 1)
