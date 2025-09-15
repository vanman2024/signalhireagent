# Feature Specification: Contact Deduplication and Search Optimization

**Feature Branch**: `004-contact-deduplication`
**Created**: September 15, 2025
**Status**: Draft - Revised for Simplicity
**Input**: User description: "JSON-based contact deduplication system to optimize search quotas and filter quality before reveals. Start simple with file merging, avoid database complexity initially. Focus on core problem: managing 7,000+ contacts across multiple searches within daily limits."

## Execution Flow (main)
```
1. Parse user description from Input
   → Transform CLI from simple search tool to enterprise contact management
2. Extract key concepts from description
   → Actors: enterprise users, recruiters, sales teams
   → Actions: deduplication, campaign management, smart reveals
   → Data: contacts, campaigns, search sessions, reveal tracking
   → Constraints: credit costs, rate limits, data accuracy
3. For each unclear aspect:
   → All core requirements clearly specified
4. Fill User Scenarios & Testing section
   → Multi-search campaign management with deduplication
5. Generate Functional Requirements
   → 25 testable requirements covering all aspects
6. Identify Key Entities
   → 5 core entities: contacts, campaigns, search sessions, reveals, templates
7. Run Review Checklist
   → No [NEEDS CLARIFICATION] markers
   → Business-focused requirements
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a recruiter searching for 7,000+ Heavy Equipment Mechanics, I need to run multiple searches (due to 200 search/day quota limits) and merge the results without duplicate reveals. I want to filter out unwanted job titles (operators, drivers) before revealing contacts to maximize credit efficiency. SignalHire doesn't charge twice for already-revealed contacts, but I want to avoid revealing low-quality prospects.

### Acceptance Scenarios

1. **Given** I have multiple JSON search result files from different searches, **When** I merge them using the dedupe command, **Then** the system removes duplicates based on SignalHire uid and LinkedIn URL, showing how many were deduplicated.

2. **Given** I have merged search results with various job titles, **When** I filter the results to exclude operators and drivers, **Then** the system removes unwanted contacts and reports the filtering results.

3. **Given** I have a filtered list of 7,000+ unique contacts, **When** I start the reveal process, **Then** the system tracks progress and can resume if interrupted without re-revealing already processed contacts.

4. **Given** I'm working with JSON files containing SignalHire search results, **When** I analyze the contact quality, **Then** the system shows job title distribution and identifies potential low-quality contacts.

5. **Given** I want to optimize my search strategy, **When** I review deduplication reports, **Then** the system shows which geographic areas or search terms yielded the most unique contacts.

### Edge Cases
- What happens when two contacts have different names but same LinkedIn URL?
- How does system handle JSON files with different schemas or missing fields?
- What occurs when reveal quota is exceeded during a large batch reveal?
- How does system process contacts with missing uid or LinkedIn URL?
- What happens when a reveal fails - can it be retried or is it marked as attempted?
- How does system handle "LinkedIn-only" results (no email found) - does SignalHire charge for these?

## Requirements *(mandatory)*

### Functional Requirements

#### JSON File Management and Deduplication
- **FR-001**: System MUST merge multiple JSON search result files into a single deduplicated file
- **FR-002**: System MUST identify duplicate contacts using SignalHire uid as primary key
- **FR-003**: System MUST use LinkedIn URL as secondary deduplication method when uid is missing
- **FR-004**: System MUST report deduplication statistics (total contacts, duplicates removed, unique remaining)
- **FR-005**: System MUST handle JSON files with varying schemas and missing fields gracefully

#### Contact Quality Filtering
- **FR-006**: System MUST filter contacts by job title to exclude unwanted roles (operators, drivers, foremen)
- **FR-007**: System MUST analyze and report job title distribution in search results
- **FR-008**: System MUST support configurable exclusion lists for job titles and companies
- **FR-009**: System MUST maintain original search result data while creating filtered subsets

#### Reveal Process Management
- **FR-010**: System MUST track reveal progress for large contact lists (7,000+ contacts)
- **FR-011**: System MUST support resuming interrupted reveal processes without re-revealing completed contacts
- **FR-012**: System MUST handle reveal quota limits gracefully and report when limits are reached
- **FR-013**: System MUST distinguish between successful reveals, failed reveals, and LinkedIn-only results

#### Search Optimization
- **FR-014**: System MUST support Boolean search templates for Heavy Equipment Mechanics with operator exclusions
- **FR-015**: System MUST track which search parameters yield the most unique contacts
- **FR-016**: System MUST report geographic coverage and suggest areas for additional searches
- **FR-017**: System MUST identify search overlap and recommend optimization strategies

#### File Format Support
- **FR-018**: System MUST read SignalHire JSON search result format
- **FR-019**: System MUST export filtered and deduplicated results to CSV format
- **FR-020**: System MUST maintain backup copies of original search files
- **FR-021**: System MUST support batch processing of multiple JSON files in a directory

#### Performance and Reliability
- **FR-022**: System MUST process 7,000+ contacts within reasonable time limits (under 5 minutes for deduplication)
- **FR-023**: System MUST provide clear error messages for malformed JSON files
- **FR-024**: System MUST validate contact data integrity during processing
- **FR-025**: System MUST log all operations for troubleshooting and audit purposes

### Data Formats *(file-based, no database)*

- **Input**: SignalHire JSON search result files containing contact arrays with uid, LinkedIn URL, name, job title, company, location
- **Processing**: In-memory deduplication using uid as primary key, LinkedIn URL as fallback
- **Output**: Deduplicated JSON files and CSV exports for reveal operations
- **State**: Simple progress files for resume capability during large reveals
- **Reports**: Text-based statistics showing deduplication results and quality metrics

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
