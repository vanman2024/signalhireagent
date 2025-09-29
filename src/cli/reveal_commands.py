"""
Reveal command implementation for SignalHire Agent CLI

This module provides the reveal command functionality, allowing users to
reveal contact information for prospects using bulk operations.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import click
import httpx
from click import echo, style
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from ..lib.contact_cache import CachedContact, ContactCache
from ..models.operations import RevealOp
from ..services.signalhire_client import SignalHireClient


async def update_airtable_contacts_status(signalhire_ids: List[str], status_field_id: str, 
                                        airtable_api_key: str = None, 
                                        airtable_base_id: str = "appQoYINM992nBZ50",
                                        airtable_table_id: str = "tbl0uFVaAfcNjT2rS"):
    """
    Update status for contacts in Airtable based on SignalHire IDs.
    
    Args:
        signalhire_ids: List of SignalHire IDs to update
        status_field_id: Airtable field ID for the status (e.g., 'selCdUR2ADvZG8SbI' for 'Contacted')
        airtable_api_key: Airtable API key (optional, uses environment if not provided)
        airtable_base_id: Airtable base ID
        airtable_table_id: Airtable table ID for contacts
    """
    if not airtable_api_key:
        airtable_api_key = os.getenv('AIRTABLE_API_KEY')
        
    if not airtable_api_key:
        echo(style("⚠️  Airtable API key not found - skipping status updates", fg='yellow'))
        return
    
    if not signalhire_ids:
        return
        
    echo(f"📋 Updating Airtable status for {len(signalhire_ids)} contacts...")
    
    successful_updates = 0
    failed_updates = 0
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {airtable_api_key}"}
        
        for signalhire_id in signalhire_ids:
            try:
                # Find existing record by SignalHire ID
                search_url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_id}"
                search_params = {
                    "filterByFormula": f"{{SignalHire ID}} = '{signalhire_id}'",
                    "maxRecords": 1,
                    "fields": ["Full Name", "Status"]
                }
                
                response = await client.get(search_url, headers=headers, params=search_params)
                response.raise_for_status()
                
                records = response.json().get('records', [])
                
                if records:
                    record_id = records[0]['id']
                    contact_name = records[0].get('fields', {}).get('Full Name', signalhire_id)
                    
                    # Update status using field ID
                    update_url = f"{search_url}/{record_id}"
                    payload = {
                        "fields": {
                            "Status": status_field_id  # Use Airtable field ID directly
                        }
                    }
                    
                    response = await client.patch(update_url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    successful_updates += 1
                    echo(f"   ✅ Updated status for {contact_name}")
                else:
                    echo(f"   ⚠️  Contact not found in Airtable: {signalhire_id}")
                    failed_updates += 1
                    
            except httpx.HTTPError as e:
                failed_updates += 1
                echo(f"   ❌ Failed to update {signalhire_id}: {e}")
            except Exception as e:
                failed_updates += 1
                echo(f"   ❌ Error updating {signalhire_id}: {e}")
    
    if successful_updates > 0:
        echo(f"📊 Airtable status updates: {successful_updates} successful, {failed_updates} failed")


def handle_api_error(error: str, status_code: int | None = None, logger=None) -> None:
    """
    Handle API errors with user-friendly messages and suggestions.
    Provides specific guidance for different types of API errors.
    """
    if logger:
        logger.error("API error occurred", error=error, status_code=status_code)

    # Rate limit errors (429)
    if status_code == 429 or "rate limit" in error.lower():
        echo(style("🚦 Rate Limit Exceeded!", fg='yellow', bold=True))
        echo(
            "The SignalHire API has temporarily blocked requests due to high frequency."
        )
        echo()
        echo("💡 Solutions:")
        echo("  • Wait a few minutes before retrying")
        echo("  • Reduce the number of prospects per batch")
        echo("  • Pause briefly before resuming high-volume jobs")
        echo("  • Check your current usage: signalhire status --credits")
        echo("  • Monitor daily usage: signalhire status --daily-usage")
        echo()
        echo("📊 API Quotas:")
        echo("  • 600 search requests per minute")
        echo("  • 5,000 contact reveals per day (API mode)")
        echo("  • 5,000 search profile views per day")

    # Insufficient credits (402)
    elif (
        status_code == 402
        or "insufficient credits" in error.lower()
        or "credits" in error.lower()
    ):
        echo(style("💰 Insufficient Credits!", fg='red', bold=True))
        echo("Your account doesn't have enough credits for this operation.")
        echo()
        echo("💡 Solutions:")
        echo("  • Check your current balance: signalhire status --credits")
        echo("  • Review usage trends: signalhire status --daily-usage")
        echo("  • Purchase additional credits at: https://signalhire.com/credits")
        echo("  • Split the job into smaller batches and retry after the daily reset")

    # Authentication errors (401, 403)
    elif (
        status_code in [401, 403]
        or "unauthorized" in error.lower()
        or "forbidden" in error.lower()
    ):
        echo(style("🔐 Authentication Error!", fg='red', bold=True))
        echo("Unable to authenticate with SignalHire API.")
        echo()
        echo("💡 Solutions:")
        echo("  • Check your API key: export SIGNALHIRE_API_KEY='your-key'")
        echo("  • Verify your credentials are correct")
        echo("  • Regenerate your API key if needed")
        echo("  • Contact support if issues persist after regenerating the API key")

    # Network errors
    elif (
        "timeout" in error.lower()
        or "connection" in error.lower()
        or status_code == 408
    ):
        echo(style("🌐 Network Error!", fg='yellow', bold=True))
        echo("Unable to connect to SignalHire servers.")
        echo()
        echo("💡 Solutions:")
        echo("  • Check your internet connection")
        echo("  • Try again in a few moments")
        echo("  • If the problem persists, contact SignalHire support")

    # Server errors (5xx)
    elif status_code and status_code >= 500:
        echo(style("🛠️  Server Error!", fg='yellow', bold=True))
        echo("SignalHire servers are experiencing issues.")
        echo()
        echo("💡 Solutions:")
        echo("  • This is usually temporary - try again later")
        echo("  • Check SignalHire status page for outages")

    # Not found errors (404)
    elif status_code == 404:
        echo(style("🔍 Resource Not Found!", fg='yellow', bold=True))
        echo("The requested prospect or resource could not be found.")
        echo()
        echo("💡 Solutions:")
        echo("  • Verify the prospect IDs are correct")
        echo("  • Check if the prospects still exist in SignalHire")
        echo("  • Try searching for the prospects again")

    # Generic API error
    else:
        echo(style("❌ API Error!", fg='red', bold=True))
        echo(f"Error: {error}")
        if status_code:
            echo(f"Status Code: {status_code}")
        echo()
        echo("💡 Solutions:")
        echo("  • Check your internet connection")
        echo("  • Verify your API credentials")
        echo("  • Try again later")
        echo("  • Contact SignalHire support if the problem persists")


def format_prospect_uids(prospect_uids: list[str], format_type: str = "human") -> str:
    """Format prospect UIDs for output display."""
    if format_type == "json":
        return json.dumps(prospect_uids, indent=2)

    # Human-readable format
    output = []
    output.append(f"📋 Prospect UIDs ({len(prospect_uids)} total):")
    for i, uid in enumerate(prospect_uids[:10], 1):  # Show first 10
        output.append(f"  {i}. {uid}")

    if len(prospect_uids) > 10:
        output.append(f"  ... and {len(prospect_uids) - 10} more")

    return "\n".join(output)


def format_reveal_results(results: dict[str, Any], format_type: str = "human") -> str:
    """Format reveal results for output display."""
    if format_type == "json":
        return json.dumps(results, indent=2)

    # Human-readable format
    operation_id = results.get('operation_id', 'N/A')
    total_prospects = results.get('total_prospects', 0)
    revealed_count = results.get('revealed_count', 0)
    cached_count = results.get('cached_reused_count', 0)
    needs_refresh_count = results.get('needs_refresh_count', 0)
    failed_count = results.get('failed_count', 0)
    credits_used = results.get('credits_used', 0)

    output = []
    output.append("🔓 Contact Reveal Results")
    output.append(f"Operation ID: {style(operation_id, fg='blue')}")
    output.append(f"Total prospects: {total_prospects}")
    output.append(
        f"Newly revealed: {style(str(revealed_count), fg='green', bold=True)}"
    )

    if cached_count:
        output.append(
            f"Reused from local cache: {style(str(cached_count), fg='cyan', bold=True)}"
        )

    if needs_refresh_count > 0:
        output.append(
            f"Needs refresh (no local contacts cached): {style(str(needs_refresh_count), fg='yellow')}"
        )

    if failed_count > 0:
        output.append(f"Failed: {style(str(failed_count), fg='red')}")

    output.append(f"Credits used: {style(str(credits_used), fg='yellow')}")

    # Success rate counts cached contacts as successful reuse
    total_success = revealed_count + cached_count
    success_rate = (total_success / total_prospects * 100) if total_prospects > 0 else 0
    output.append(f"Success rate: {success_rate:.1f}% (including cached contacts)")

    # Show sample revealed contacts
    prospects = results.get('prospects', [])
    revealed_prospects = [
        p
        for p in prospects
        if p.get('contacts') and p.get('status') in {'success', 'cached'}
    ]

    if revealed_prospects:
        output.append("\n📧 Sample revealed contacts:")
        for prospect in revealed_prospects[:3]:  # Show first 3
            name = (
                prospect.get('full_name')
                or prospect.get('profile', {}).get('full_name')
                or prospect.get('profile', {}).get('fullName')
                or 'Unknown'
            )
            contacts = prospect.get('contacts', [])
            emails = [c['value'] for c in contacts if c.get('type') == 'email']

            if emails:
                output.append(f"  • {style(name, bold=True)}: {emails[0]}")

        if len(revealed_prospects) > 3:
            output.append(f"  ... and {len(revealed_prospects) - 3} more")

    return "\n".join(output)


@dataclass
class ProspectWorkItem:
    """Prospect metadata used to decide whether to reveal or reuse cached data."""

    uid: str
    profile: Optional[Dict[str, Any]] = None
    contacts_fetched: bool = False
    source: str = "input"


def load_prospects_from_file(
    file_path: str, skip_existing_contacts: bool = True
) -> List[ProspectWorkItem]:
    """
    Load prospect UIDs from a search results file.

    Args:
        file_path: Path to the search results file
        skip_existing_contacts: If True, skip prospects that already have contactsFetched

    Returns:
        List of prospect UIDs that need contact reveals
    """
    path = Path(file_path)

    if not path.exists():
        raise click.ClickException(f"File not found: {file_path}")

    try:
        with open(path) as f:
            data = json.load(f)

        # Handle different file formats
        work_items: List[ProspectWorkItem] = []
        _ = skip_existing_contacts  # Retained for backwards compatibility

        def _make_item(entry: Dict[str, Any]) -> Optional[ProspectWorkItem]:
            uid_value = entry.get('uid') or entry.get('id') or entry.get('prospect_uid')
            if not uid_value:
                return None

            contacts_flag = bool(
                entry.get('contactsFetched')
                or entry.get('contacts_fetched')
                or entry.get('contactsFetchedAt')
            )
            return ProspectWorkItem(
                uid=str(uid_value),
                profile=entry,
                contacts_fetched=contacts_flag,
                source='file',
            )

        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    work_items.append(ProspectWorkItem(uid=item, source='file'))
                elif isinstance(item, dict):
                    prospect_item = _make_item(item)
                    if prospect_item:
                        work_items.append(prospect_item)
        elif isinstance(data, dict):
            if 'profiles' in data and isinstance(data['profiles'], list):
                for profile in data['profiles']:
                    if not isinstance(profile, dict):
                        continue
                    prospect_item = _make_item(profile)
                    if prospect_item:
                        work_items.append(prospect_item)
            elif 'prospects' in data and isinstance(data['prospects'], list):
                for profile in data['prospects']:
                    if not isinstance(profile, dict):
                        continue
                    prospect_item = _make_item(profile)
                    if prospect_item:
                        work_items.append(prospect_item)
            elif 'prospect_uids' in data and isinstance(data['prospect_uids'], list):
                for uid_value in data['prospect_uids']:
                    if isinstance(uid_value, str):
                        work_items.append(
                            ProspectWorkItem(uid=uid_value, source='file')
                        )
            else:
                raise click.ClickException(
                    f"Unrecognized file format in {file_path}"
                )
        else:
            raise click.ClickException(f"Invalid JSON format in {file_path}")

        return work_items

    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in {file_path}: {e}") from e
    except OSError as e:
        raise click.ClickException(f"Error reading {file_path}: {e}") from e


def deduplicate_work_items(items: Iterable[ProspectWorkItem]) -> List[ProspectWorkItem]:
    """Deduplicate work items, preferring entries that include profile data."""

    deduped: Dict[str, ProspectWorkItem] = {}
    for item in items:
        if not item.uid:
            continue
        existing = deduped.get(item.uid)
        if not existing:
            deduped[item.uid] = item
            continue

        # Prefer entries that include profile details over bare UIDs
        if existing.profile and not item.profile:
            continue
        if not existing.profile and item.profile:
            deduped[item.uid] = item
            continue

        # Prefer file-sourced data (typically richer) over CLI args
        if existing.source == 'input' and item.source == 'file':
            deduped[item.uid] = item

    return list(deduped.values())


def partition_prospects(
    items: Iterable[ProspectWorkItem],
    cache: ContactCache,
    skip_existing: bool,
) -> Tuple[
    List[ProspectWorkItem],
    List[Tuple[ProspectWorkItem, CachedContact]],
    List[ProspectWorkItem],
]:
    """Split prospects into pending reveals, cached results, and needs-refresh lists."""

    pending: List[ProspectWorkItem] = []
    cached: List[Tuple[ProspectWorkItem, CachedContact]] = []
    needs_refresh: List[ProspectWorkItem] = []

    for item in items:
        cached_entry = cache.get(item.uid)
        if cached_entry:
            cached.append((item, cached_entry))
            continue

        if skip_existing and item.contacts_fetched:
            needs_refresh.append(item)
            continue

        pending.append(item)

    return pending, cached, needs_refresh


def save_reveal_results(
    results: dict[str, Any], output_file: str, format_type: str = "json"
):
    """Save reveal results to a file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format_type == "json" or output_file.endswith('.json'):
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        # Save as human-readable text
        with open(output_path, 'w') as f:
            f.write(format_reveal_results(results, "human"))


class RevealProgressCallback:
    """
    Progress callback for reveal operations using Rich progress bars.
    """

    def __init__(self, total_prospects: int, description: str = "Revealing contacts"):
        self.console = Console()
        self.total_prospects = total_prospects
        self.description = description
        self.progress = None
        self.task = None
        self.start_time = datetime.now()

        # Progress statistics
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.credits_used = 0

    def __enter__(self):
        """Start the progress bar."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TextColumn("•"),
            TextColumn("[green]{task.fields[successful]:d}✓[/green]"),
            TextColumn("[red]{task.fields[failed]:d}✗[/red]"),
            TextColumn("•"),
            TextColumn("[yellow]{task.fields[credits_used]:d}💰[/yellow]"),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console,
            refresh_per_second=2,
        )

        self.progress.start()
        self.task = self.progress.add_task(
            self.description,
            total=self.total_prospects,
            completed=0,
            successful=0,
            failed=0,
            credits_used=0,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the progress bar."""
        if self.progress:
            self.progress.stop()

    async def update_progress(self, progress_data: dict[str, Any]):
        """
        Update progress bar with new data.
        Expected progress_data format:
        {
            "current": int,
            "total": int,
            "successful": int,
            "failed": int,
            "success_rate": float,
            "elapsed_seconds": float,
            "avg_time_per_contact": float,
            "estimated_completion": str (ISO format),
            "remaining_contacts": int,
            "batch_size": int,
            "recent_errors": list,
            "credits_used": int,
            "credits_remaining": int
        }
        """
        if not self.progress or not self.task:
            return

        # Update statistics
        self.processed = progress_data.get("current", self.processed)
        self.successful = progress_data.get("successful", self.successful)
        self.failed = progress_data.get("failed", self.failed)
        self.credits_used = progress_data.get("credits_used", self.credits_used)

        # Update progress bar
        self.progress.update(
            self.task,
            completed=self.processed,
            successful=self.successful,
            failed=self.failed,
            credits_used=self.credits_used,
        )

        # Update description with additional info
        success_rate = progress_data.get("success_rate", 0)
        remaining = progress_data.get("remaining_contacts", 0)

        if remaining > 0:
            description = f"{self.description} • {success_rate:.1f}% success • {remaining} remaining"
        else:
            description = (
                f"{self.description} • {success_rate:.1f}% success • Complete!"
            )

        self.progress.update(self.task, description=description)

        # Show recent errors if any
        recent_errors = progress_data.get("recent_errors", [])
        if recent_errors and len(recent_errors) > 0:
            # Only show the most recent error to avoid cluttering
            latest_error = recent_errors[-1]
            if isinstance(latest_error, dict) and "error" in latest_error:
                error_msg = latest_error["error"]
                if len(error_msg) > 60:
                    error_msg = error_msg[:57] + "..."
                # Update description to show error
                self.progress.update(
                    self.task, description=f"{description} • ⚠️ {error_msg}"
                )


async def execute_reveal_with_progress(
    prospect_uids: list[str], config, logger, **options
) -> dict[str, Any]:
    """
    Execute reveal operation with enhanced progress reporting.
    """
    bulk_size = options.get('bulk_size', 1000)

    total_prospects = len(prospect_uids)

    # Create progress callback
    progress_callback = RevealProgressCallback(
        total_prospects=total_prospects, description="🔓 Revealing contacts"
    )

    with progress_callback:
        # Update Airtable status to "Contacted" before sending revelation requests
        try:
            await update_airtable_contacts_status(
                signalhire_ids=prospect_uids,
                status_field_id="selCdUR2ADvZG8SbI"  # "Contacted" status field ID
            )
        except Exception as e:
            echo(style(f"⚠️  Failed to update Airtable status: {e}", fg='yellow'))
            logger.warning(f"Airtable status update failed: {e}")

        # API-only client
        api_client = SignalHireClient(api_key=config.api_key)
        logger.info(
            "Using API for reveal",
            has_api_key=bool(config.api_key),
            prospect_count=total_prospects,
        )
        echo("Using API for reveal")

        operation = RevealOp(prospect_ids=prospect_uids, batch_size=bulk_size)
        return await api_client.bulk_reveal(
            operation, progress_callback=progress_callback.update_progress
        )


async def check_credits_and_confirm(config, total_prospects: int, logger) -> bool:
    """
    Check credit balance and daily usage, then get user confirmation for the operation.
    Returns True if user confirms to proceed, False otherwise.
    """
    if not config.api_key:
        echo(
            style(
                "❌ SIGNALHIRE_API_KEY is required. Browser automation is disabled in this release.",
                fg='red',
                bold=True,
            )
        )
        return False

    try:
        api_client = SignalHireClient(api_key=config.api_key)

        # Check current credits
        credits_response = await api_client.check_credits()

        if not credits_response.success:
            echo(
                style(
                    f"⚠️  Could not check credit balance: {credits_response.error}",
                    fg='yellow',
                )
            )
            return click.confirm("Continue without credit check?", default=True)

        credits_data = credits_response.data or {}
        current_credits = credits_data.get('credits_remaining', 0)
        estimated_cost = total_prospects  # Assume 1 credit per prospect

        # Check daily usage
        daily_status = await api_client.rate_limiter.check_daily_limits()

        echo("\n💰 Credit & Daily Usage Status:")
        echo(
            f"  Current balance: {style(str(current_credits), fg='green', bold=True)} credits"
        )
        echo(f"  Estimated cost: {style(str(estimated_cost), fg='yellow')} credits")
        echo(
            f"  Daily usage: {daily_status['current_usage']}/{daily_status['daily_limit']} credits ({daily_status['percentage_used']:.1f}%)"
        )

        # Daily limit warnings
        if daily_status['warning_level'] == 'critical':
            echo(
                style("  🚨 CRITICAL: Daily limit almost reached!", fg='red', bold=True)
            )
            echo(f"     Only {daily_status['remaining']} credits left for today")
            if not click.confirm(
                "Continue despite approaching daily limit?", default=False
            ):
                echo("Operation cancelled to avoid hitting daily limit.")
                return False
        elif daily_status['warning_level'] == 'high':
            echo(
                style(
                    f"  ⚠️  WARNING: High daily usage ({daily_status['percentage_used']:.1f}%)",
                    fg='yellow',
                    bold=True,
                )
            )
            echo(f"     {daily_status['remaining']} credits remaining today")
            if not click.confirm("Continue with high daily usage?", default=True):
                echo("Operation cancelled by user.")
                return False
        elif daily_status['warning_level'] == 'moderate':
            echo(
                f"  INFO: Moderate usage: {daily_status['percentage_used']:.1f}% of daily limit"
            )

        if current_credits < estimated_cost:
            shortfall = estimated_cost - current_credits
            echo(
                style(
                    f"  ❌ Insufficient credits! Shortfall: {shortfall} credits",
                    fg='red',
                    bold=True,
                )
            )

            if click.confirm(
                f"Purchase {shortfall} additional credits?", default=False
            ):
                echo("💳 Redirecting to SignalHire credit purchase...")
                echo("Please visit: https://signalhire.com/credits")
                return False
            echo("Operation cancelled due to insufficient credits.")
            return False

        remaining_after = current_credits - estimated_cost
        echo(f"  Remaining after: {style(str(remaining_after), fg='blue')} credits")

        # Combined credit + daily limit check
        if estimated_cost > daily_status['remaining']:
            echo(style("  ❌ Operation would exceed daily limit!", fg='red', bold=True))
            echo(
                f"     Need: {estimated_cost} credits, Available today: {daily_status['remaining']}"
            )
            echo("     💡 Try again tomorrow after the quota resets")
            return False

        # Cost warning for expensive operations
        if estimated_cost >= 50:
            echo(
                style(
                    f"\n⚠️  This is a large operation costing {estimated_cost} credits!",
                    fg='yellow',
                    bold=True,
                )
            )
            if not click.confirm(
                "Are you sure you want to proceed with this expensive operation?",
                default=False,
            ):
                return False

        # Always confirm for any credit-using operation
        if not click.confirm(
            f"Proceed with revealing {total_prospects} contacts for {estimated_cost} credits?",
            default=True,
        ):
            echo("Operation cancelled by user.")
            return False

        return True

    except Exception as e:  # noqa: BLE001
        logger.warning(f"Credit check failed: {e}")
        echo(style(f"⚠️  Credit check failed: {e}", fg='yellow'))
        return click.confirm("Continue without credit verification?", default=True)


async def execute_reveal(
    prospect_uids: list[str], config, logger, **options
) -> dict[str, Any]:
    """Execute the reveal operation using appropriate client."""

    bulk_size = options.get('bulk_size', 1000)

    # Update Airtable status to "Contacted" before sending revelation requests
    try:
        await update_airtable_contacts_status(
            signalhire_ids=prospect_uids,
            status_field_id="selCdUR2ADvZG8SbI"  # "Contacted" status field ID
        )
    except Exception as e:
        echo(style(f"⚠️  Failed to update Airtable status: {e}", fg='yellow'))
        logger.warning(f"Airtable status update failed: {e}")

    # API-only client
    api_client = SignalHireClient(api_key=config.api_key)
    logger.info(
        "Using API for reveal",
        has_api_key=bool(config.api_key),
        prospect_count=len(prospect_uids),
    )
    echo("Using API for reveal")
    operation = RevealOp(prospect_ids=prospect_uids, batch_size=bulk_size)
    return await api_client.bulk_reveal(operation)


@click.command()
@click.argument('prospect_uids', nargs=-1)
@click.option(
    '--search-file',
    type=click.Path(exists=True),
    help='Load prospect UIDs from search results file',
)
@click.option(
    '--bulk-size',
    type=click.IntRange(1, 1000),
    default=1000,
    help='Prospects per bulk operation [default: 1000] [range: 1-1000]',
)
@click.option(
    '--use-native-export',
    is_flag=True,
    help="Use SignalHire's native CSV export feature",
)
@click.option(
    '--export-format',
    type=click.Choice(['csv', 'xlsx']),
    default='csv',
    help='Native export format [default: csv]',
)
@click.option(
    '--timeout',
    type=int,
    default=600,
    help='Timeout for reveal operation in seconds [default: 600]',
)
@click.option(
    '--output',
    type=click.Path(),
    help='Save revealed contacts to file [default: stdout]',
)
@click.option(
    '--dry-run', is_flag=True, help='Check credits and show what would be revealed'
)
@click.option('--save-to-list', help='Save results to SignalHire lead list')
@click.option(
    '--browser-wait',
    type=int,
    default=2,
    help='(Deprecated) Browser automation disabled; option retained for compatibility',
)
@click.option(
    '--api-only',
    is_flag=True,
    help='Require API mode only - do not fallback to browser automation',
)
@click.option(
    '--skip-existing',
    is_flag=True,
    default=True,
    help='Skip prospects that already have contactsFetched (saves credits) [default: True]',
)
@click.pass_context
def reveal(
    ctx,
    prospect_uids,
    search_file,
    bulk_size,
    use_native_export,
    export_format,
    timeout,
    output,
    dry_run,
    save_to_list,
    browser_wait,
    api_only,
    skip_existing,
):
    """
    Reveal contact information (API-only in this release).
    🚀 API-FIRST: Uses SignalHire API by default (5,000 reveals/day quota)
    🚫 BROWSER MODE: Disabled; all operations run through the API layer
    💳 CREDIT AWARE: Warns at 50%, 75%, and 90% daily usage thresholds
    \b
    EXAMPLES:
      # API-first reveal (recommended for daily use)
      signalhire reveal --search-file prospects.csv --output contacts.csv
      # Force API-only mode
      signalhire reveal --search-file prospects.csv --api-only --output contacts.csv
      # Break large reveal lists into API-sized batches
      signalhire reveal --search-file large_list.csv --bulk-size 1000
      # Check costs before revealing
      signalhire reveal --search-file prospects.csv --dry-run
      # Save to SignalHire lead list
      signalhire reveal --search-file prospects.csv --save-to-list "Q4 Sales Leads"
      # Reveal specific prospects
      signalhire reveal uid1 uid2 uid3 --output specific_contacts.csv
    \b
    RATE LIMITS & COSTS:
    • API Mode: 5,000 contact reveals/day (1 credit per contact)
    • Search profiles: 5,000/day shared with prospect searches
    • Use --dry-run to estimate credits and confirm availability before revealing
    • Browser automation is not available in this build
    \b
    OUTPUT FORMATS:
    • CSV (default): Spreadsheet-compatible with all contact fields
    • JSON: Structured data for programmatic processing
    • XLSX: Excel format with formatting and multiple sheets
    """

    config = ctx.obj['config']
    logger = ctx.obj.get('logger')
    contact_cache = ContactCache()
    _ = api_only  # Browser mode is disabled; flag retained for CLI compatibility

    work_items: List[ProspectWorkItem] = [
        ProspectWorkItem(uid=str(uid), source='input')
        for uid in prospect_uids
        if uid
    ]

    if search_file:
        try:
            file_items = load_prospects_from_file(
                search_file, skip_existing_contacts=skip_existing
            )
            work_items.extend(file_items)
            if config.verbose:
                echo(f"📂 Loaded {len(file_items)} prospects from {search_file}")
        except (OSError, json.JSONDecodeError) as e:
            echo(style(f"Error loading prospects from file: {e}", fg='red'), err=True)
            ctx.exit(1)

    work_items = deduplicate_work_items(work_items)

    if not work_items:
        echo(style("Error: No prospect UIDs provided.", fg='red'), err=True)
        echo("Provide UIDs as arguments or use --search-file option", err=True)
        ctx.exit(1)

    profiles_by_uid = {
        item.uid: item.profile for item in work_items if item.profile
    }
    if profiles_by_uid:
        contact_cache.merge_profiles(
            {uid: profile for uid, profile in profiles_by_uid.items() if profile}
        )

    pending_items, cached_hits, needs_refresh_items = partition_prospects(
        work_items, contact_cache, skip_existing
    )

    total_unique = len(work_items)
    total_pending = len(pending_items)
    cached_count = len(cached_hits)
    needs_refresh_count = len(needs_refresh_items)

    if config.verbose:
        echo(f"📊 Total unique prospects: {total_unique}")
        echo(f"   Pending API reveals: {total_pending}")
        echo(f"   Cached contacts available: {cached_count}")
        if needs_refresh_count:
            echo(f"   Needs refresh (no local cache): {needs_refresh_count}")

    if config.browser_mode and total_pending > 0:
        echo(
            style(
                "Error: Browser automation is disabled. Run in API mode only.",
                fg='red',
            ),
            err=True,
        )
        ctx.exit(1)

    if total_pending > 0 and not config.api_key:
        echo(
            style(
                "Error: SIGNALHIRE_API_KEY is required for reveal operations.",
                fg='red',
            ),
            err=True,
        )
        echo("Set the environment variable or pass --api-key explicitly.", err=True)
        ctx.exit(1)

    pending_uids = [item.uid for item in pending_items]

    def render_dry_run() -> None:
        echo("🧪 Dry Run - Reveal operation summary:")
        echo(f"  Total prospects considered: {total_unique}")
        echo(f"  Pending API reveals: {total_pending}")
        echo(f"  Reusing cached contacts: {cached_count}")
        if needs_refresh_count:
            echo(
                "  Needs refresh (no cached contacts): "
                f"{needs_refresh_count}"
            )
        echo(f"  Skip already revealed flag: {skip_existing}")

        if total_pending > 0:
            echo(f"  Bulk size: {bulk_size}")
            echo(
                f"  Estimated batches: {(total_pending + bulk_size - 1) // bulk_size}"
            )
            echo(f"  Use native export: {use_native_export}")
            if use_native_export:
                echo(f"  Export format: {export_format}")
            if save_to_list:
                echo(f"  Save to list: {save_to_list}")
            echo(f"  Timeout: {timeout} seconds")
            if config.api_key:
                try:
                    api_client = SignalHireClient(api_key=config.api_key)
                    credits_response = asyncio.run(api_client.check_credits())
                    if credits_response.success:
                        credits_data = credits_response.data or {}
                        current_credits = credits_data.get('credits_remaining', 0)
                        estimated_cost = total_pending
                        daily_status = asyncio.run(
                            api_client.rate_limiter.check_daily_limits()
                        )

                        echo("\n💰 Credit & Daily Usage Analysis:")
                        echo(
                            f"  Current balance: {style(str(current_credits), fg='green', bold=True)} credits"
                        )
                        echo(
                            f"  Estimated cost: {style(str(estimated_cost), fg='yellow')} credits"
                        )
                        echo(
                            f"  Daily usage: {daily_status['current_usage']}/{daily_status['daily_limit']} credits ({daily_status['percentage_used']:.1f}%)"
                        )

                        if current_credits >= estimated_cost:
                            remaining = current_credits - estimated_cost
                            echo(
                                f"  ✅ Sufficient credits - {remaining} remaining after operation"
                            )
                            if estimated_cost <= daily_status['remaining']:
                                echo(
                                    f"  ✅ Within daily limit - {daily_status['remaining'] - estimated_cost} remaining today"
                                )
                            else:
                                echo(
                                    style(
                                        "  ❌ Would exceed daily limit! Need "
                                        f"{estimated_cost - daily_status['remaining']} more credits",
                                        fg='red',
                                        bold=True,
                                    )
                                )
                        else:
                            shortfall = estimated_cost - current_credits
                            echo(
                                style(
                                    f"  ❌ Insufficient credits - need {shortfall} more",
                                    fg='red',
                                    bold=True,
                                )
                            )
                            echo(
                                "  💡 Consider purchasing credits or reducing prospect count"
                            )

                        warning_level = daily_status.get('warning_level')
                        if warning_level == 'critical':
                            echo(
                                style(
                                    f"  🚨 CRITICAL: Daily limit almost reached ({daily_status['percentage_used']:.1f}%)",
                                    fg='red',
                                    bold=True,
                                )
                            )
                        elif warning_level == 'high':
                            echo(
                                style(
                                    f"  ⚠️  WARNING: High daily usage ({daily_status['percentage_used']:.1f}%)",
                                    fg='yellow',
                                    bold=True,
                                )
                            )
                        elif warning_level == 'moderate':
                            echo(
                                f"  INFO: Moderate usage: {daily_status['percentage_used']:.1f}% of daily limit"
                            )
                    else:
                        echo(
                            style(
                                f"  ⚠️  Could not check credits: {credits_response.error}",
                                fg='yellow',
                            )
                        )
                except Exception as exc:  # noqa: BLE001
                    echo(style(f"  ⚠️  Credit check failed: {exc}", fg='yellow'))
        else:
            echo("  No API calls required — all contacts available from cache")

        if cached_count:
            echo("\n📦 Cached prospects ready:")
            for idx, (item, _) in enumerate(cached_hits[:5], 1):
                echo(f"  {idx}. {item.uid} (cached)")

        if total_pending > 0:
            echo("\n📋 Sample prospect UIDs to reveal:")
            for idx, uid in enumerate(pending_uids[:5], 1):
                echo(f"  {idx}. {uid}")
            if total_pending > 5:
                echo(f"  ... and {total_pending - 5} more")
            echo(
                f"\n💰 Estimated cost: {total_pending} credits (1 per new reveal)"
            )

        if needs_refresh_count:
            echo(
                "\n⚠️  Some prospects have contactsFetched but no cached contacts. "
                "Run again with --no-skip-existing to refresh local data if needed."
            )

        echo("\n✅ Reveal parameters validated. Remove --dry-run to execute.")

    if dry_run:
        render_dry_run()
        return

    def compose_results(api_result: Optional[dict[str, Any]]) -> dict[str, Any]:
        final: dict[str, Any] = {
            "operation_id": (
                api_result.get('operation_id', 'op_unknown')
                if api_result
                else 'cache_only'
            ),
            "total_prospects": total_unique,
            "revealed_count": api_result.get('revealed_count', 0) if api_result else 0,
            "cached_reused_count": cached_count,
            "needs_refresh_count": needs_refresh_count,
            "failed_count": api_result.get('failed_count', 0) if api_result else 0,
            "credits_used": api_result.get('credits_used', 0) if api_result else 0,
            "prospects": [],
        }

        warnings: List[str] = []
        if api_result and api_result.get('warnings'):
            warnings.extend(api_result['warnings'])
        if needs_refresh_count:
            warnings.append(
                "Contacts previously revealed but not cached locally. "
                "Run with --no-skip-existing to refresh if you need those details."
            )
        final['warnings'] = warnings

        api_entries: Dict[str, Dict[str, Any]] = {}
        if api_result:
            for record in api_result.get('prospects', []):
                uid = record.get('uid') or record.get('id') or record.get('prospect_id')
                if not uid:
                    continue
                profile = record.get('profile') or profiles_by_uid.get(uid)
                contacts = record.get('contacts') or []
                if contacts:
                    contact_cache.upsert(uid, contacts=contacts, profile=profile, metadata={'source': 'api'})
                elif profile:
                    contact_cache.upsert(uid, profile=profile)
                entry = {
                    'uid': uid,
                    'status': record.get('status', 'success' if contacts else 'unknown'),
                    'contacts': contacts,
                    'profile': profile,
                    'source': 'api',
                    'error': record.get('error'),
                    'credits_used': record.get('credits_used', 0),
                }
                if profile:
                    entry['full_name'] = profile.get('full_name') or profile.get('fullName')
                api_entries[uid] = entry

        cached_map: Dict[str, Dict[str, Any]] = {}
        for item, cached_contact in cached_hits:
            contact_cache.upsert(item.uid, profile=item.profile)
            entry_profile = cached_contact.profile or item.profile
            entry = {
                'uid': item.uid,
                'status': 'success',
                'contacts': cached_contact.contacts,
                'profile': entry_profile,
                'source': 'cache',
                'first_revealed_at': cached_contact.first_revealed_at,
                'last_updated_at': cached_contact.last_updated_at,
            }
            if isinstance(entry_profile, dict):
                entry['full_name'] = entry_profile.get('full_name') or entry_profile.get('fullName')
            cached_map[item.uid] = entry

        needs_refresh_map: Dict[str, Dict[str, Any]] = {}
        for item in needs_refresh_items:
            entry = {
                'uid': item.uid,
                'status': 'needs_refresh',
                'contacts': [],
                'profile': item.profile,
                'source': 'skip',
                'warning': 'Contact data not cached locally. Re-run with --no-skip-existing to refresh.',
            }
            needs_refresh_map[item.uid] = entry

        for item in work_items:
            uid = item.uid
            if uid in api_entries:
                final['prospects'].append(api_entries[uid])
            elif uid in cached_map:
                final['prospects'].append(cached_map[uid])
            elif uid in needs_refresh_map:
                final['prospects'].append(needs_refresh_map[uid])
            else:
                final['prospects'].append(
                    {
                        'uid': uid,
                        'status': 'unknown',
                        'contacts': [],
                        'profile': item.profile,
                        'source': 'unknown',
                    }
                )

        if api_result and api_result.get('export_file_path'):
            final['export_file_path'] = api_result['export_file_path']

        return final

    if total_pending == 0:
        final_results = compose_results(None)
        contact_cache.save()

        if config.output_format == 'json':
            result_output = json.dumps(final_results, indent=2)
        else:
            result_output = format_reveal_results(final_results, config.output_format)

        if output:
            save_reveal_results(final_results, output, config.output_format)
            echo(f"✅ Results saved to: {output}")
            if config.output_format != 'json':
                echo(result_output)
        else:
            echo(result_output)

        if cached_count:
            echo(
                f"\n♻️  Reused {cached_count} contacts from local cache (no new credits used)"
            )
        if needs_refresh_count:
            echo(
                style(
                    "⚠️  Some contacts are missing locally. Run with --no-skip-existing to refresh.",
                    fg='yellow',
                )
            )
        return

    # Execute reveal for pending prospects
    echo("🔓 Revealing contact information...")

    if config.verbose:
        echo("Mode: API (recommended)")
        echo(f"Bulk size: {bulk_size}")
        echo(f"Native export: {use_native_export}")
        if config.debug:
            echo(f"First 10 UIDs: {pending_uids[:10]}")

    confirmed = asyncio.run(
        check_credits_and_confirm(config, total_pending, logger)
    )
    if not confirmed:
        echo("Operation cancelled.")
        return

    try:
        api_result = asyncio.run(
            execute_reveal_with_progress(
                pending_uids,
                config,
                logger,
                bulk_size=bulk_size,
                use_native_export=use_native_export,
                export_format=export_format,
                timeout=timeout,
                save_to_list=save_to_list,
                browser_wait=browser_wait,
            )
        )

        final_results = compose_results(api_result)
        contact_cache.save()

        if config.output_format == 'json':
            result_output = json.dumps(final_results, indent=2)
        else:
            result_output = format_reveal_results(final_results, config.output_format)

        if output:
            save_reveal_results(final_results, output, config.output_format)
            echo(f"✅ Results saved to: {output}")
            if config.output_format != 'json':
                echo(result_output)
        else:
            echo(result_output)

        revealed_count = final_results.get('revealed_count', 0)
        credits_used = final_results.get('credits_used', 0)
        if revealed_count > 0:
            echo(
                f"\n✅ Successfully revealed {revealed_count} contacts using {credits_used} credits"
            )
        if final_results.get('cached_reused_count'):
            echo(
                f"♻️  Reused {final_results['cached_reused_count']} contacts from local cache"
            )
        if final_results.get('needs_refresh_count'):
            echo(
                style(
                    "⚠️  Some contacts still need refresh. Run with --no-skip-existing to fetch them.",
                    fg='yellow',
                )
            )
        if final_results.get('failed_count'):
            echo(
                style(
                    f"⚠️  {final_results['failed_count']} contacts failed to reveal.",
                    fg='yellow',
                )
            )

        if use_native_export and final_results.get('export_file_path'):
            echo(f"📁 Native export file: {final_results['export_file_path']}")

    except KeyboardInterrupt:
        echo("\n🛑 Reveal operation cancelled by user", err=True)
        ctx.exit(1)
    except Exception as e:  # noqa: BLE001
        error_message = str(e)

        # Try to extract status code and provide better error handling
        status_code = None
        if hasattr(e, 'status_code'):
            status_code = e.status_code
        elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            status_code = e.response.status_code

        # Use enhanced error handling
        handle_api_error(error_message, status_code, logger)

        if config.debug:
            import traceback

            echo("\n🔧 Debug information:")
            echo(traceback.format_exc())

        ctx.exit(1)
