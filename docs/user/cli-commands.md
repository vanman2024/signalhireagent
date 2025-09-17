# CLI Command Reference

This document provides a comprehensive reference for all available CLI commands in the SignalHire Agent.

## 🤖 AI Agent Quick Reference

When working with natural language requests, use these command mappings:

### Common User Requests → CLI Commands

**Search Requests:**
- "Find software engineers in California" → `signalhire search --title "Software Engineer" --location "California"`
- "Search for heavy equipment mechanics in Canada with 5+ years experience" → `signalhire search --title "Heavy Equipment Mechanic" --location "Canada" --experience-from 5`
- "Look for senior developers at tech companies" → `signalhire search --title "Senior Developer" --company "Tech"`

**Deduplication Requests:**
- "Merge these contact files and remove duplicates" → `signalhire dedupe merge --input "file1.json,file2.json" --output merged.json`
- "Combine all JSON files in this directory" → `signalhire dedupe merge --input /path/to/directory --output combined.json`

**Analysis Requests:**
- "Analyze job titles in these contacts" → `signalhire analyze job-titles --input contacts.json`
- "Check geographic coverage" → `signalhire analyze geography --input contacts.json`
- "Show me search templates for heavy equipment" → `signalhire search templates`

**Filtering Requests:**
- "Remove operators and drivers from contacts" → `signalhire filter job-title --input contacts.json --output filtered.json --exclude-job-titles "operator,driver"`

**Status/Credits Requests:**
- "Check my API limits" or "How many credits do I have?" → `signalhire status --credits`
- "Show daily usage" → `signalhire status --daily-usage`

### Best Practices for AI Agents:
1. **Always check credits first** with `signalhire status --credits` for large operations
2. **Use --dry-run** for searches to validate parameters before execution
3. **Recommend file naming** with timestamps: `contacts_2024-09-15.json`
4. **Chain commands logically**: search → dedupe → analyze → filter → reveal
5. **Monitor rate limits**: Search profiles (5000/day), Contact reveals (5000/day)
6. **Use Boolean operators** for complex searches: `AND`, `OR`, `NOT`, `()`

## `signalhire search`

Search for prospects using various criteria. **Includes automatic 5000/day search profile limit tracking.**

**Usage:**

```bash
signalhire search [OPTIONS]
```

**Options:**

*   `--title TEXT`               Job title or role to search for (supports Boolean queries)
*   `--location TEXT`            Geographic location (city, state, country)
*   `--company TEXT`             Company name (supports Boolean queries)
*   `--industry TEXT`            Industry category
*   `--keywords TEXT`            Skills and attributes (supports Boolean queries)  
*   `--name TEXT`                Full name to search for
*   `--experience-from INTEGER`  Minimum years of experience
*   `--experience-to INTEGER`    Maximum years of experience
*   `--open-to-work`             Filter for job seekers only
*   `--size INTEGER`             Results per page [1-100, default: 10]
*   `--output PATH`              Save results to file
*   `--continue-search`          Continue previous search using pagination
*   `--scroll-id TEXT`           Scroll ID for pagination  
*   `--all-pages`                Fetch all pages using scroll pagination
*   `--max-pages INTEGER`        Maximum pages to fetch with --all-pages [default: 20]
*   `--dry-run`                  Show search criteria without executing

**Boolean Operators:**
*   `AND` - Both terms must appear: `"PHP AND HTML"`
*   `OR` - Either term can appear: `"Python OR Java"`  
*   `NOT` - Exclude term: `"Manager NOT Assistant"`
*   `()` - Group terms: `"(Java AND Spring) OR Python"`
*   `""` - Exact phrases: `"Software Engineer"`

**Examples:**

*   **Basic Search:**
    ```bash
    signalhire search --title "Software Engineer" --location "New York" --size 25
    ```
*   **Advanced Boolean Search:**
    ```bash
    signalhire search --title "(Python OR JavaScript) AND Senior" --company "Google OR Microsoft"
    ```
*   **Heavy Equipment Mechanics with experience:**
    ```bash
    signalhire search --title "Heavy Equipment Mechanic" --location "Canada" --experience-from 5 --size 50
    ```
*   **Large paginated search:**
    ```bash
    signalhire search --title "Engineer" --all-pages --max-pages 10 --output engineers.json
    ```
*   **Test search criteria:**
    ```bash
    signalhire search --title "Product Manager" --dry-run
    ```

## `signalhire reveal`

Reveal contact information for prospects.

**Usage:**

```bash
signalhire reveal [OPTIONS] [PROSPECT_UIDS]...
```

**Options:**

*   `--search-file TEXT`  Input file with prospect UIDs (e.g., `prospects.json`).
*   `--output TEXT`       File to save revealed contacts (e.g., `contacts.csv`).
*   `--api-only`          Force API mode and disable browser fallback.

**Examples:**

*   **Reveal from search file:**
    ```bash
    signalhire reveal --search-file prospects.json --output contacts.csv
    ```
*   **Reveal specific UIDs:**
    ```bash
    signalhire reveal uid1 uid2 uid3 --output contacts.json
    ```

## `signalhire status`

Check operation status and account information. **Shows 5000/day limits for both reveals and search profiles.**

**Usage:**

```bash
signalhire status [OPTIONS]
```

**Options:**

*   `--credits`       Show remaining credits and daily usage
*   `--daily-usage`   Show detailed API usage for today  
*   `--operation-id TEXT` Check specific operation status
*   `--operations`    List recent operations
*   `--all`           Show all status information

**Examples:**

*   **Check account credits and daily limits:**
    ```bash
    signalhire status --credits
    # Output shows:
    # 👁️ Profile Views: 1,250/5,000 daily views used (25.0%)
    # 📞 Contact Reveals: 23/5,000 daily reveals used (0.5%)
    # ⚠️  Warning Level: none
    ```
*   **Show detailed daily usage:**
    ```bash
    signalhire status --daily-usage
    ```
*   **Check specific operation:**
    ```bash
    signalhire status --operation-id abc123
    ```

## `signalhire export`

Export search results and contact data.

**Usage:**

```bash
signalhire export [OPTIONS] COMMAND [ARGS]...
```

**Commands:**

*   `search`  Export search results to file.

**Examples:**

*   **Export search to CSV:**
    ```bash
    signalhire export search --search-id abc123 --format csv
    ```
*   **Export specific columns to Excel:**
    ```bash
    signalhire export search --search-id abc123 --format xlsx --columns "name,email,company"
    ```

## `signalhire dedupe`

Merge and deduplicate contacts from multiple JSON files.

**Usage:**

```bash
signalhire dedupe merge [OPTIONS]
```

**Options:**

*   `--input TEXT`      Input JSON file(s) or directory (comma-separated or dir) [required]
*   `--output TEXT`     Output deduplicated JSON file [required]

**Examples:**

*   **Merge multiple JSON files:**
    ```bash
    signalhire dedupe merge --input contacts1.json,contacts2.json --output deduped.json
    ```

*   **Merge all JSON files in a directory:**
    ```bash
    signalhire dedupe merge --input /path/to/search/results --output deduped.json
    ```

## `signalhire analyze`

Analyze contact quality and job title distribution.

**Usage:**

```bash
signalhire analyze [COMMAND] [OPTIONS]
```

**Commands:**

*   `job-titles`        Analyze job title distribution in contacts
*   `geography`         Analyze geographic coverage and suggest areas for additional searches  
*   `overlap`           Identify search overlap between multiple contact files
*   `search-templates`  Show Boolean search templates for Heavy Equipment Mechanics

**Options:**

*   `--input TEXT`      Input JSON file [required]

**Examples:**

*   **Analyze job title distribution:**
    ```bash
    signalhire analyze job-titles --input contacts.json
    ```
*   **Analyze geographic coverage:**
    ```bash
    signalhire analyze geography --input contacts.json
    ```
*   **Check overlap between contact sets:**
    ```bash
    signalhire analyze overlap --input contacts1.json,contacts2.json
    ```
*   **Show Heavy Equipment search templates:**
    ```bash
    signalhire search templates
    # Alias: signalhire analyze search-templates
    ```

## `signalhire filter`

Filter contacts by job title, company, or other criteria.

**Usage:**

```bash
signalhire filter job-title [OPTIONS]
```

**Options:**

*   `--input TEXT`                  Input JSON file [required]
*   `--output TEXT`                 Output filtered JSON file [required]
*   `--exclude-job-titles TEXT`     Comma-separated list of job titles to exclude

**Examples:**

*   **Filter out operators and drivers:**
    ```bash
    signalhire filter job-title --input contacts.json --output filtered.json --exclude-job-titles "operator,driver,foreman"
    ```

## Workflow Examples

### Complete Deduplication and Filtering Workflow

1. **Search for contacts:**
   ```bash
   signalhire search --title "Heavy Equipment Mechanic" --location "Texas" --limit 1000
   ```

2. **Merge and deduplicate multiple search results:**
   ```bash
   signalhire dedupe merge --input search_results/ --output deduped_contacts.json
   ```

3. **Analyze job title distribution:**
   ```bash
   signalhire analyze job-titles --input deduped_contacts.json
   ```

4. **Filter unwanted job titles:**
   ```bash
   signalhire filter job-title --input deduped_contacts.json --output filtered_contacts.json --exclude-job-titles "operator,driver,foreman"
   ```

5. **Export to CSV for reveal:**
   ```bash
   signalhire export search --search-id abc123 --format csv --output ready_for_reveal.csv
   ```

6. **Reveal contacts:**
   ```bash
   signalhire reveal --input ready_for_reveal.csv --output revealed_contacts.csv
   ```
