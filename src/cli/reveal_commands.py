"""
Reveal command implementation for SignalHire Agent CLI

This module provides the reveal command functionality, allowing users to
reveal contact information for prospects using bulk operations.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import click
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

from ..models.operations import RevealOp
from ..services.signalhire_client import SignalHireClient


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
        echo("The SignalHire API has temporarily blocked requests due to high frequency.")
        echo()
        echo("💡 Solutions:")
        echo("  • Wait a few minutes before retrying")
        echo("  • Reduce the number of prospects per batch")
        echo("  • Switch to browser mode for bulk operations:")
        echo("    signalhire reveal --browser --bulk-size 1000 [prospects]")
        echo("  • Check your current usage: signalhire status")
        echo()
        echo("📊 API Limits:")
        echo("  • 600 requests per minute")
        echo("  • 100 contact reveals per day (API mode)")
        echo("  • Unlimited reveals with browser mode")

    # Insufficient credits (402)
    elif status_code == 402 or "insufficient credits" in error.lower() or "credits" in error.lower():
        echo(style("💰 Insufficient Credits!", fg='red', bold=True))
        echo("Your account doesn't have enough credits for this operation.")
        echo()
        echo("💡 Solutions:")
        echo("  • Check your current balance: signalhire credits --check")
        echo("  • Purchase additional credits at: https://signalhire.com/credits")
        echo("  • Use browser mode for unlimited reveals (slower but no credit cost)")
        echo("  • Reduce the number of prospects to reveal")

    # Authentication errors (401, 403)
    elif status_code in [401, 403] or "unauthorized" in error.lower() or "forbidden" in error.lower():
        echo(style("🔐 Authentication Error!", fg='red', bold=True))
        echo("Unable to authenticate with SignalHire API.")
        echo()
        echo("💡 Solutions:")
        echo("  • Check your API key: export SIGNALHIRE_API_KEY='your-key'")
        echo("  • Verify your credentials are correct")
        echo("  • Regenerate your API key if needed")
        echo("  • Switch to browser mode: export SIGNALHIRE_EMAIL='your@email.com'")

    # Network errors
    elif "timeout" in error.lower() or "connection" in error.lower() or status_code == 408:
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
        echo("  • Switch to browser mode as a workaround")

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
    failed_count = results.get('failed_count', 0)
    credits_used = results.get('credits_used', 0)

    output = []
    output.append("🔓 Contact Reveal Results")
    output.append(f"Operation ID: {style(operation_id, fg='blue')}")
    output.append(f"Total prospects: {total_prospects}")
    output.append(f"Successfully revealed: {style(str(revealed_count), fg='green', bold=True)}")

    if failed_count > 0:
        output.append(f"Failed: {style(str(failed_count), fg='red')}")

    output.append(f"Credits used: {style(str(credits_used), fg='yellow')}")

    # Success rate
    success_rate = (revealed_count / total_prospects * 100) if total_prospects > 0 else 0
    output.append(f"Success rate: {success_rate:.1f}%")

    # Show sample revealed contacts
    prospects = results.get('prospects', [])
    revealed_prospects = [p for p in prospects if p.get('status') == 'success' and p.get('contacts')]

    if revealed_prospects:
        output.append("\n📧 Sample revealed contacts:")
        for prospect in revealed_prospects[:3]:  # Show first 3
            name = prospect.get('full_name', 'Unknown')
            contacts = prospect.get('contacts', [])
            emails = [c['value'] for c in contacts if c.get('type') == 'email']

            if emails:
                output.append(f"  • {style(name, bold=True)}: {emails[0]}")

        if len(revealed_prospects) > 3:
            output.append(f"  ... and {len(revealed_prospects) - 3} more")

    return "\n".join(output)


def load_prospects_from_file(file_path: str, skip_existing_contacts: bool = True) -> list[str]:
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
        if isinstance(data, list):
            # List of UIDs - assume all need revealing
            return data
        if isinstance(data, dict):
            # Search results format
            if 'profiles' in data:
                profiles = data['profiles']
                uids = []
                skipped_count = 0

                for p in profiles:
                    uid = p.get('uid') or p.get('id')
                    if not uid:
                        continue

                    # Check if contacts already exist
                    if skip_existing_contacts and p.get('contactsFetched'):
                        skipped_count += 1
                        continue

                    uids.append(uid)

                if skip_existing_contacts and skipped_count > 0:
                    click.echo(f"ℹ️  Skipped {skipped_count} prospects that already have contacts")
                    click.echo(f"🔍 Will reveal {len(uids)} prospects that need contacts")

                return uids
            if 'prospects' in data:
                prospects = data['prospects']
                return [p.get('uid') or p.get('id') for p in prospects if p.get('uid') or p.get('id')]
            if 'prospect_uids' in data:
                return data['prospect_uids']
            raise click.ClickException(f"Unrecognized file format in {file_path}")
        raise click.ClickException(f"Invalid JSON format in {file_path}")

    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in {file_path}: {e}") from e
    except OSError as e:
        raise click.ClickException(f"Error reading {file_path}: {e}") from e


def save_reveal_results(results: dict[str, Any], output_file: str, format_type: str = "json"):
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
            refresh_per_second=2
        )

        self.progress.start()
        self.task = self.progress.add_task(
            self.description,
            total=self.total_prospects,
            completed=0,
            successful=0,
            failed=0,
            credits_used=0
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
            credits_used=self.credits_used
        )

        # Update description with additional info
        success_rate = progress_data.get("success_rate", 0)
        remaining = progress_data.get("remaining_contacts", 0)

        if remaining > 0:
            description = f"{self.description} • {success_rate:.1f}% success • {remaining} remaining"
        else:
            description = f"{self.description} • {success_rate:.1f}% success • Complete!"

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
                    self.task,
                    description=f"{description} • ⚠️ {error_msg}"
                )


async def execute_reveal_with_progress(prospect_uids: list[str], config, logger, **options) -> dict[str, Any]:
    """
    Execute reveal operation with enhanced progress reporting.
    """
    bulk_size = options.get('bulk_size', 1000)

    total_prospects = len(prospect_uids)

    # Create progress callback
    progress_callback = RevealProgressCallback(
        total_prospects=total_prospects,
        description="🔓 Revealing contacts"
    )

    with progress_callback:
        # API-only client
        api_client = SignalHireClient(api_key=config.api_key)
        logger.info("Using API for reveal", has_api_key=bool(config.api_key), prospect_count=total_prospects)
        echo("Using API for reveal")

        operation = RevealOp(prospect_ids=prospect_uids, batch_size=bulk_size)
        return await api_client.bulk_reveal(operation, progress_callback=progress_callback.update_progress)


async def check_credits_and_confirm(config, total_prospects: int, logger) -> bool:
    """
    Check credit balance and daily usage, then get user confirmation for the operation.
    Returns True if user confirms to proceed, False otherwise.
    """
    if not config.api_key:
        # Skip credit check for browser mode
        return True

    try:
        api_client = SignalHireClient(api_key=config.api_key)

        # Check current credits
        credits_response = await api_client.check_credits()

        if not credits_response.success:
            echo(style(f"⚠️  Could not check credit balance: {credits_response.error}", fg='yellow'))
            return click.confirm("Continue without credit check?", default=True)

        credits_data = credits_response.data or {}
        current_credits = credits_data.get('credits_remaining', 0)
        estimated_cost = total_prospects  # Assume 1 credit per prospect

        # Check daily usage
        daily_status = await api_client.rate_limiter.check_daily_limits()

        echo("\n💰 Credit & Daily Usage Status:")
        echo(f"  Current balance: {style(str(current_credits), fg='green', bold=True)} credits")
        echo(f"  Estimated cost: {style(str(estimated_cost), fg='yellow')} credits")
        echo(f"  Daily usage: {daily_status['current_usage']}/{daily_status['daily_limit']} credits ({daily_status['percentage_used']:.1f}%)")

        # Daily limit warnings
        if daily_status['warning_level'] == 'critical':
            echo(style("  🚨 CRITICAL: Daily limit almost reached!", fg='red', bold=True))
            echo(f"     Only {daily_status['remaining']} credits left for today")
            if not click.confirm("Continue despite approaching daily limit?", default=False):
                echo("Operation cancelled to avoid hitting daily limit.")
                return False
        elif daily_status['warning_level'] == 'high':
            echo(style(f"  ⚠️  WARNING: High daily usage ({daily_status['percentage_used']:.1f}%)", fg='yellow', bold=True))
            echo(f"     {daily_status['remaining']} credits remaining today")
            if not click.confirm("Continue with high daily usage?", default=True):
                echo("Operation cancelled by user.")
                return False
        elif daily_status['warning_level'] == 'moderate':
            echo(f"  INFO: Moderate usage: {daily_status['percentage_used']:.1f}% of daily limit")

        if current_credits < estimated_cost:
            shortfall = estimated_cost - current_credits
            echo(style(f"  ❌ Insufficient credits! Shortfall: {shortfall} credits", fg='red', bold=True))

            if click.confirm(f"Purchase {shortfall} additional credits?", default=False):
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
            echo(f"     Need: {estimated_cost} credits, Available today: {daily_status['remaining']}")
            echo("     💡 Try again tomorrow or use browser mode for unlimited reveals")
            return False

        # Cost warning for expensive operations
        if estimated_cost >= 50:
            echo(style(f"\n⚠️  This is a large operation costing {estimated_cost} credits!", fg='yellow', bold=True))
            if not click.confirm("Are you sure you want to proceed with this expensive operation?", default=False):
                return False

        # Always confirm for any credit-using operation
        if not click.confirm(f"Proceed with revealing {total_prospects} contacts for {estimated_cost} credits?", default=True):
            echo("Operation cancelled by user.")
            return False

        return True

    except Exception as e:  # noqa: BLE001
        logger.warning(f"Credit check failed: {e}")
        echo(style(f"⚠️  Credit check failed: {e}", fg='yellow'))
        return click.confirm("Continue without credit verification?", default=True)


async def execute_reveal(prospect_uids: list[str], config, logger, **options) -> dict[str, Any]:
    """Execute the reveal operation using appropriate client."""

    bulk_size = options.get('bulk_size', 1000)

    # API-only client
    api_client = SignalHireClient(api_key=config.api_key)
    logger.info("Using API for reveal", has_api_key=bool(config.api_key), prospect_count=len(prospect_uids))
    echo("Using API for reveal")
    operation = RevealOp(prospect_ids=prospect_uids, batch_size=bulk_size)
    return await api_client.bulk_reveal(operation)


@click.command()
@click.argument('prospect_uids', nargs=-1)
@click.option(
    '--search-file',
    type=click.Path(exists=True),
    help='Load prospect UIDs from search results file'
)
@click.option(
    '--bulk-size',
    type=click.IntRange(1, 1000),
    default=1000,
    help='Prospects per bulk operation [default: 1000] [range: 1-1000]'
)
@click.option(
    '--use-native-export',
    is_flag=True,
    help="Use SignalHire's native CSV export feature"
)
@click.option(
    '--export-format',
    type=click.Choice(['csv', 'xlsx']),
    default='csv',
    help='Native export format [default: csv]'
)
@click.option(
    '--timeout',
    type=int,
    default=600,
    help='Timeout for reveal operation in seconds [default: 600]'
)
@click.option(
    '--output',
    type=click.Path(),
    help='Save revealed contacts to file [default: stdout]'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Check credits and show what would be revealed'
)
@click.option(
    '--save-to-list',
    help='Save results to SignalHire lead list'
)
@click.option(
    '--browser-wait',
    type=int,
    default=2,
    help='Wait time between browser actions in seconds [default: 2]'
)
@click.option(
    '--api-only',
    is_flag=True,
    help='Require API mode only - do not fallback to browser automation'
)
@click.option(
    '--skip-existing',
    is_flag=True,
    default=True,
    help='Skip prospects that already have contactsFetched (saves credits) [default: True]'
)
@click.pass_context
def reveal(ctx, prospect_uids, search_file, bulk_size, use_native_export,
          export_format, timeout, output, dry_run, save_to_list, browser_wait, api_only, skip_existing):
    """
    Reveal contact information (API-first with browser fallback).
    🚀 API-FIRST: Uses SignalHire API by default (100 contacts/day limit)
    🌐 BROWSER MODE: Automatic fallback for bulk operations or when API unavailable
    💰 CREDIT AWARE: Shows cost estimates and tracks daily usage
    \b
    EXAMPLES:
      # API-first reveal (recommended for daily use)
      signalhire reveal --search-file prospects.csv --output contacts.csv
      # Force API-only mode
      signalhire reveal --search-file prospects.csv --api-only --output contacts.csv
      # Large bulk operation (browser mode)
      signalhire reveal --search-file large_list.csv --bulk-size 1000 --browser-wait 3
      # Check costs before revealing
      signalhire reveal --search-file prospects.csv --dry-run
      # Save to SignalHire lead list
      signalhire reveal --search-file prospects.csv --save-to-list "Q4 Sales Leads"
      # Reveal specific prospects
      signalhire reveal uid1 uid2 uid3 --output specific_contacts.csv
    \b
    RATE LIMITS & COSTS:
    • API Mode: 100 contacts/day, ~$0.10-0.20 per contact
    • Browser Mode: No daily limit, higher cost per contact
    • Use --dry-run to estimate costs before proceeding
    \b
    OUTPUT FORMATS:
    • CSV (default): Spreadsheet-compatible with all contact fields
    • JSON: Structured data for programmatic processing
    • XLSX: Excel format with formatting and multiple sheets
    """

    config = ctx.obj['config']
    logger = ctx.obj.get('logger')

    # Collect prospect UIDs from arguments and file
    all_prospect_uids = list(prospect_uids)

    if search_file:
        try:
            file_uids = load_prospects_from_file(search_file, skip_existing_contacts=skip_existing)
            all_prospect_uids.extend(file_uids)

            if config.verbose:
                echo(f"📂 Loaded {len(file_uids)} prospect UIDs from {search_file}")

        except (OSError, json.JSONDecodeError) as e:
            echo(style(f"Error loading prospects from file: {e}", fg='red'), err=True)
            ctx.exit(1)

    # Validate we have prospects to reveal
    if not all_prospect_uids:
        echo(style("Error: No prospect UIDs provided.", fg='red'), err=True)
        echo("Provide UIDs as arguments or use --search-file option", err=True)
        ctx.exit(1)

    # Remove duplicates while preserving order
    unique_uids = []
    seen = set()
    for uid in all_prospect_uids:
        if uid and uid not in seen:
            unique_uids.append(uid)
            seen.add(uid)

    total_prospects = len(unique_uids)

    if config.verbose:
        echo(f"📊 Total unique prospects to reveal: {total_prospects}")
        if len(all_prospect_uids) != total_prospects:
            echo(f"   (Removed {len(all_prospect_uids) - total_prospects} duplicates)")

    # Validate credentials based on mode
    if config.browser_mode:
        # Browser mode explicitly requested
        if not config.email or not config.password:
            echo(style("Error: Browser mode requires email and password.", fg='red'), err=True)
            echo("Set SIGNALHIRE_EMAIL and SIGNALHIRE_PASSWORD environment variables", err=True)
            echo("or use --email and --password options", err=True)
            ctx.exit(1)
    else:
        # Default to API mode - check if we have API credentials
        if not config.api_key:
            if api_only:
                echo(style("Error: --api-only specified but no API key available.", fg='red'), err=True)
                echo("Set SIGNALHIRE_API_KEY environment variable for API-only mode", err=True)
                echo("Or remove --api-only to allow browser fallback", err=True)
                ctx.exit(1)
            else:
                echo(style("Warning: No API key provided, falling back to browser mode", fg='yellow'), err=True)
                echo("For better reliability, consider setting SIGNALHIRE_API_KEY environment variable", err=True)
                config.browser_mode = True
                if not config.email or not config.password:
                    echo(style("Error: No valid authentication method available.", fg='red'), err=True)
                    echo("Set SIGNALHIRE_API_KEY for API mode, or SIGNALHIRE_EMAIL/SIGNALHIRE_PASSWORD for browser mode", err=True)
                    ctx.exit(1)

    # Dry run mode
    if dry_run:
        echo("🧪 Dry Run - Reveal operation summary:")
        echo(f"  Total prospects: {total_prospects}")
        echo(f"  Bulk size: {bulk_size}")
        echo(f"  Estimated batches: {(total_prospects + bulk_size - 1) // bulk_size}")
        echo(f"  Use native export: {use_native_export}")
        if use_native_export:
            echo(f"  Export format: {export_format}")
        if save_to_list:
            echo(f"  Save to list: {save_to_list}")
        echo(f"  Mode: {'Browser automation' if config.browser_mode else 'API (recommended)'}")
        echo(f"  Timeout: {timeout} seconds")

        # Enhanced credit information for dry run
        if not config.browser_mode and config.api_key:
            try:
                api_client = SignalHireClient(api_key=config.api_key)
                credits_response = asyncio.run(api_client.check_credits())

                if credits_response.success:
                    credits_data = credits_response.data or {}
                    current_credits = credits_data.get('credits_remaining', 0)
                    estimated_cost = total_prospects

                    # Check daily usage
                    daily_status = asyncio.run(api_client.rate_limiter.check_daily_limits())

                    echo("\n💰 Credit & Daily Usage Analysis:")
                    echo(f"  Current balance: {style(str(current_credits), fg='green', bold=True)} credits")
                    echo(f"  Estimated cost: {style(str(estimated_cost), fg='yellow')} credits")
                    echo(f"  Daily usage: {daily_status['current_usage']}/{daily_status['daily_limit']} credits ({daily_status['percentage_used']:.1f}%)")

                    if current_credits >= estimated_cost:
                        remaining = current_credits - estimated_cost
                        echo(f"  ✅ Sufficient credits - {remaining} remaining after operation")

                        # Check daily limits
                        if estimated_cost <= daily_status['remaining']:
                            echo(f"  ✅ Within daily limit - {daily_status['remaining'] - estimated_cost} remaining today")
                        else:
                            echo(style(f"  ❌ Would exceed daily limit! Need {estimated_cost - daily_status['remaining']} more credits", fg='red', bold=True))
                    else:
                        shortfall = estimated_cost - current_credits
                        echo(style(f"  ❌ Insufficient credits - need {shortfall} more", fg='red', bold=True))
                        echo("  💡 Consider purchasing credits or reducing prospect count")

                    # Daily usage warnings
                    if daily_status['warning_level'] == 'critical':
                        echo(style(f"  🚨 CRITICAL: Daily limit almost reached ({daily_status['percentage_used']:.1f}%)", fg='red', bold=True))
                    elif daily_status['warning_level'] == 'high':
                        echo(style(f"  ⚠️  WARNING: High daily usage ({daily_status['percentage_used']:.1f}%)", fg='yellow', bold=True))
                    elif daily_status['warning_level'] == 'moderate':
                        echo(f"  INFO: Moderate usage: {daily_status['percentage_used']:.1f}% of daily limit")
                else:
                    echo(style(f"  ⚠️  Could not check credits: {credits_response.error}", fg='yellow'))

            except Exception as e:  # noqa: BLE001
                echo(style(f"  ⚠️  Credit check failed: {e}", fg='yellow'))
        elif config.browser_mode:
            echo("\n💰 Cost Estimate:")
            echo("  Browser mode: Variable costs (typically higher than API)")
            echo("  💡 Tip: Consider using API mode for better cost predictability")
        else:
            echo("\n💰 Cost Estimate:")
            echo("  No API key: Cannot estimate costs without authentication")
            echo("  💡 Set SIGNALHIRE_API_KEY for cost estimates and API mode")

        # Show sample UIDs
        echo("\n📋 Sample prospect UIDs:")
        for i, uid in enumerate(unique_uids[:5], 1):
            echo(f"  {i}. {uid}")
        if total_prospects > 5:
            echo(f"  ... and {total_prospects - 5} more")

        echo(f"\n💰 Estimated cost: {total_prospects} credits (1 per successful reveal)")
        echo("\n✅ Reveal parameters validated. Remove --dry-run to execute.")
        return

    # Execute reveal
    echo("🔓 Revealing contact information...")

    if config.verbose:
        echo(f"Mode: {'Browser automation' if config.browser_mode else 'API (recommended)'}")
        echo(f"Bulk size: {bulk_size}")
        echo(f"Native export: {use_native_export}")
        if config.debug:
            echo(f"First 10 UIDs: {unique_uids[:10]}")

    # Interactive credit confirmation (skip for dry-run which already showed estimates)
    if not config.browser_mode and not dry_run:
        confirmed = asyncio.run(check_credits_and_confirm(config, total_prospects, logger))
        if not confirmed:
            echo("Operation cancelled.")
            return

    try:
        # Run async reveal with progress bar
        results = asyncio.run(execute_reveal_with_progress(
            unique_uids, config, logger,
            bulk_size=bulk_size,
            use_native_export=use_native_export,
            export_format=export_format,
            timeout=timeout,
            save_to_list=save_to_list,
            browser_wait=browser_wait
        ))

        # Display results
        if config.output_format == 'json':
            result_output = json.dumps(results, indent=2)
        else:
            result_output = format_reveal_results(results, config.output_format)

        if output:
            save_reveal_results(results, output, config.output_format)
            echo(f"✅ Results saved to: {output}")

            if config.output_format != 'json':
                echo(result_output)
        else:
            echo(result_output)

        # Success metrics
        revealed_count = results.get('revealed_count', 0)
        credits_used = results.get('credits_used', 0)

        if revealed_count > 0:
            echo(f"\n✅ Successfully revealed {revealed_count} contacts using {credits_used} credits")
        else:
            echo("\n⚠️  No contacts revealed")

        # Show export file if native export was used
        if use_native_export and results.get('export_file_path'):
            echo(f"📁 Native export file: {results['export_file_path']}")

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
