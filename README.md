# SignalHire Agent

Automation that keeps a SignalHire search-and-reveal loop wired directly into Airtable. Run the CLI from your terminal, let the DigitalOcean callback server ingest reveal webhooks, and watch Airtable status fields progress from `New` to `Revealed` or `No Contacts`.

## Quick Links
- [System Architecture](docs/developer/architecture/SIGNALHIRE_AGENT_SYSTEM.md)
- [Future Enhancements & Roadmap](docs/planning/ENHANCEMENTS.md)

## System Overview
- **Search:** `signalhire-agent search …` hits the SignalHire API and (optionally) pushes results into Airtable `Contacts` with `Status = New` and dedupe checks.
- **Reveal:** `signalhire-agent reveal …` or `scripts/run_signalhire_job.py` submits reveal batches. SignalHire webhooks land on the DigitalOcean callback server (`http://157.245.213.190/signalhire/callback`), which patches Airtable with emails/phones and updates status to `Revealed` or `No Contacts`.
- **Direct Sync:** `signalhire-agent airtable sync-direct` re-fetches Person API details for any lingering `New` records.
- **Credits & Health:** `signalhire-agent status --credits` and `signalhire-agent doctor` keep an eye on API limits and configuration.

### End-to-End Workflow (current production path)
```
┌────────────┐    search API     ┌────────────────┐
│ Operator   │ ────────────────▶ │ SignalHire API │
│ CLI        │                  └────────────────┘
│            │                       │
│            │  (optional)           │ reveal batches
│            ├──────────────────────▶│
│            │                       ▼
│            │                DigitalOcean Droplet
│            │                FastAPI callback server
│            │                       │ Airtable REST
│            ▼                       ▼
│ Airtable (Contacts / Search Sessions)
└────────────┘
     │
     ▼
Downstream sales & outreach tools
```

## Core CLI Commands
```bash
# Check environment and dependencies
signalhire-agent doctor

# Search for prospects
signalhire-agent search \
  --title "Heavy Equipment Technician" \
  --location "Canada" \
  --size 25 \
  --to-airtable \
  --check-duplicates

# Submit reveals for pending SignalHire IDs
signalhire-agent reveal \
  --search-file technicians.json \
  --skip-revealed \
  --bulk-size 10

# Force-sync remaining Airtable records directly from SignalHire Person API
signalhire-agent airtable sync-direct --max-contacts 25

# Review SignalHire credit balance
signalhire-agent status --credits
```
For templated searches, run `signalhire-agent search templates` to see curated Boolean queries.

## Complete Workflow
1. **Stage prospects** – run a targeted search and push matches into Airtable with `Status = New`.
   ```bash
   signalhire-agent search \n     --title "Heavy Equipment Technician" \n     --location "Canada" \n     --size 25 \n     --to-airtable \n     --check-duplicates
   ```
2. **Queue reveals** – submit SignalHire reveal requests (the callback server will handle updates).
   ```bash
   signalhire-agent reveal \n     --search-file technicians.json \n     --skip-revealed \n     --bulk-size 10
   ```
   *Shortcut:* `python scripts/run_signalhire_job.py --title ... --location ... --max-prospects 25 --wait-for-callbacks 60` performs both steps in one go.
3. **Let webhooks update Airtable** – the droplet receives callbacks at `http://157.245.213.190/signalhire/callback` and sets statuses to `Revealed` or `No Contacts`.
4. **Optional direct sync** – fill any stragglers via Person API.
   ```bash
   signalhire-agent airtable sync-direct --max-contacts 25
   ```
5. **Monitor & verify** – check Airtable and SignalHire credits.
   ```bash
   python check_airtable_status.py
   signalhire-agent status --credits
   ```

## Setup

## Command Reference
| Command | Description | Example |
| ------- | ----------- | ------- |
| `signalhire-agent doctor` | Environment & dependency diagnostics | `signalhire-agent doctor` |
| `signalhire-agent search` | Query SignalHire (supports Boolean filters, Airtable dedupe) | `signalhire-agent search --title "Heavy Equipment Technician" --location "Canada" --to-airtable` |
| `signalhire-agent reveal` | Submit reveal jobs from a list of SignalHire IDs | `signalhire-agent reveal --search-file technicians.json --bulk-size 10` |
| `signalhire-agent airtable sync-direct` | Pull contact data straight from Person API into Airtable | `signalhire-agent airtable sync-direct --max-contacts 20` |
| `signalhire-agent status --credits` | Show remaining SignalHire credits & usage | `signalhire-agent status --credits` |
| `signalhire-agent workflow lead-generation` | Guided end-to-end workflow (search → reveal → export) | `signalhire-agent workflow lead-generation --title "Diesel Mechanic" --location "Alberta"` |
| `scripts/run_signalhire_job.py` | One-shot automation (search + reveal + wait) | `python scripts/run_signalhire_job.py --title "Heavy Equipment Technician" --location "Canada" --max-prospects 25` |

```bash
# Clone & enter the repo
git clone https://github.com/vanman2024/signalhireagent.git
cd signalhireagent

# Create / activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the CLI locally
pip install -e .

# Configure environment (minimum variables)
cat <<'ENV' > .env
SIGNALHIRE_API_KEY=replace-me
AIRTABLE_API_KEY=replace-me
AIRTABLE_BASE_ID=appQoYINM992nBZ50
AIRTABLE_TABLE_ID=tbl0uFVaAfcNjT2rS
SIGNALHIRE_CALLBACK_URL=http://157.245.213.190/signalhire/callback
ENV

# Load env vars for the current shell
set -a; source .env; set +a

# Quick health check
signalhire-agent doctor
```

## Operating the Pipeline

### Option A — All-in-one automation
`scripts/run_signalhire_job.py` performs a search, queues reveals, and waits for webhooks.
```bash
source .venv/bin/activate
set -a; source .env; set +a

python scripts/run_signalhire_job.py \
  --title "Heavy Equipment Technician" \
  --location "Canada" \
  --size 50 \
  --max-prospects 25 \
  --wait-for-callbacks 60
```
The script saves the raw API payload under `automation_runs/` and leaves Airtable with updated statuses once callbacks arrive.

### Option B — Manual control
1. **Search:** `signalhire-agent search … --output technicians.json`
2. **Reveal:** `signalhire-agent reveal --search-file technicians.json --skip-revealed`
3. **Direct Fix-ups:** `signalhire-agent airtable sync-direct --max-contacts 10`
4. **Inspect Airtable:** `python check_airtable_status.py`

## Monitoring & Troubleshooting
- Callback server health: `curl http://157.245.213.190/health`
- Droplet logs: `ssh … tail -f /opt/signalhire/callback.log`
- Credits: `signalhire-agent status --credits`
- Airtable contact snapshot: `python check_airtable_status.py`

## Architecture & Roadmap
- Detailed component breakdown, data flow, and infrastructure expectations: `docs/developer/architecture/SIGNALHIRE_AGENT_SYSTEM.md`
- Upcoming work (remote MCP servers, AI categorization, automation hardening): `docs/planning/ENHANCEMENTS.md`

## Support & Contribution
- Inline CLI help: `signalhire-agent --help`
- Issues / PRs welcome on GitHub.

Everything in the live pipeline now persists directly to Airtable—no local JSON cache is written or read during normal CLI execution.
