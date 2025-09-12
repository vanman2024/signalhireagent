# CLI Command Reference

This document provides a comprehensive reference for all available CLI commands in the SignalHire Agent.

## `signalhire search`

Search for prospects using various criteria.

**Usage:**

```bash
signalhire search [OPTIONS]
```

**Options:**

*   `--title TEXT`      Job title or role to search for.
*   `--location TEXT`   Location filter.
*   `--company TEXT`    Company filter.
*   `--industry TEXT`   Industry category.
*   `--keywords TEXT`   Skills and attributes.
*   `--name TEXT`       Full name to search for.
*   `--output TEXT`     File to save search results (e.g., `prospects.json`).

**Examples:**

*   **Basic Search:**
    ```bash
    signalhire search --title "Software Engineer" --location "New York"
    ```
*   **Advanced Boolean Search:**
    ```bash
    signalhire search --title "(Python OR JavaScript) AND Senior" --company "Google OR Microsoft"
    ```
*   **Save results to file:**
    ```bash
    signalhire search --title "Product Manager" --output prospects.json
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

Check operation status and account information.

**Usage:**

```bash
signalhire status [OPTIONS]
```

**Options:**

*   `--credits`       Show remaining credits.
*   `--daily-usage`   Show API and browser usage for today.
*   `--operation-id TEXT` Check specific operation status.
*   `--operations`    List recent operations.
*   `--all`           Show all status information.

**Examples:**

*   **Check account credits:**
    ```bash
    signalhire status --credits
    ```
*   **Show daily usage:**
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
