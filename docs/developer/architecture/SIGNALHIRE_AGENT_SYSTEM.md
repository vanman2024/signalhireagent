# SignalHire Agent Architecture

Summary of the services that power the SignalHire → Airtable automation and how data flows between them (state as of September 2025).

## Runtime Components

| Layer      | Component / Location                                      | Purpose |
| ---------- | --------------------------------------------------------- | ------- |
| Operator   | Local workstation running `signalhire-agent` (Python 3.11+) | Issues searches and reveal jobs, monitors credits |
| Runtime    | Project virtual environment (`.venv`) with editable install | Provides CLI entry points backed by `src/` modules |
| External   | SignalHire REST API (`/candidate/searchByQuery`, `/candidate/search`, `/credits`) | Supplies prospect data, accepts reveal requests |
| Automation | DigitalOcean droplet (`http://157.245.213.190/signalhire/callback`) | FastAPI webhook receiver that patches Airtable statuses and contact fields |
| Data store | Airtable base `appQoYINM992nBZ50` — Contacts `tbl0uFVaAfcNjT2rS`, Search Sessions `tblqmpcDHfG5pZCWh` | Source of truth for the prospect lifecycle |
| Observability | Local CLI output, droplet logs (`/opt/signalhire/callback.log`) | Minimal telemetry for troubleshooting |

## Data Flow & Execution Paths

```
┌──────────────────────────┐        searchByQuery         ┌─────────────────────────┐
│ Local operator CLI       │ ───────────────────────────▶ │ SignalHire API          │
│ (search / reveal commands│                             └─────────────────────────┘
│  + helper scripts)       │                                      │
│                          │                                      │ reveal (POST /candidate/search)
│                          │                                      ▼
│                          │                          ┌─────────────────────────┐
│                          │  updates via REST        │ DigitalOcean Droplet    │
│                          └────────────────────────▶ │ FastAPI callback server │
│                                                     └──────────┬──────────────┘
│                                                                │ Airtable REST API
│                                                                ▼
┌──────────────────────────┐        patch/status update         ┌─────────────────────────┐
│ Airtable Contacts table  │ ◀───────────────────────────────── │ Airtable API            │
│ (status, emails, phones) │                                    └─────────────────────────┘
└──────────────────────────┘
```

### Primary Steps
1. **Search & Stage** — `signalhire-agent search … --to-airtable` (or `scripts/run_signalhire_job.py`) hits SignalHire, enriches the local response with Airtable state (to avoid duplicates), and inserts/updates records in the Contacts table with `Status = New`.
2. **Reveal** — CLI submits reveal jobs. SignalHire pushes Person API results to the droplet callback, which immediately patches Airtable with emails/phones and flips status to `Revealed` or `No Contacts`.
3. **Direct Sync** — `signalhire-agent airtable sync-direct` can pull fresh Person API payloads for any Airtable records still marked `New`.

All authoritative contact data now lives in Airtable; the CLI only reads from there for deduplication/skip logic.

## Infrastructure Notes
- **DigitalOcean droplet** hosts the FastAPI server; health endpoint is `GET /health`.
- **Secrets**: exported via `.env` / environment (`SIGNALHIRE_API_KEY`, `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_ID`, `SIGNALHIRE_CALLBACK_URL`).
- **Credits**: `signalhire-agent status --credits` proxies the `/credits` endpoint; each reveal consumes one credit.

## Future Enhancements
Roadmap items (remote MCP servers, richer observability, AI categorization) are tracked in [docs/planning/ENHANCEMENTS.md](../../planning/ENHANCEMENTS.md).

For deeper implementation details, see:
- `src/services/signalhire_client.py`
- `scripts/run_signalhire_job.py`
- `src/cli/search_commands.py` and `src/cli/reveal_commands.py`
