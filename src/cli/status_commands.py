"""
Status command implementation for SignalHire Agent CLI

This module provides status monitoring functionality including credit checking,
operation status tracking, and system health monitoring.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import click
from click import echo, style

from services.signalhire_client import SignalHireClient


def format_credits_info(
    credits_data: dict[str, Any], format_type: str = "human"
) -> str:
    """Format credits information for output display."""
    if format_type == "json":
        return json.dumps(credits_data, indent=2)

    # Human-readable format
    output = ["💳 Credit Status"]

    def _coerce_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _first_non_null(data: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
        return None

    regular_credits = _coerce_int(
        _first_non_null(
            credits_data,
            'credits',
            'available_credits',
            'credits_remaining',
        )
    )

    if regular_credits is not None:
        credit_color = 'green' if regular_credits > 1000 else 'yellow'
        if regular_credits <= 100:
            credit_color = 'red'
        output.append(
            f"Available credits: {style(f'{regular_credits:,}', fg=credit_color, bold=True)}"
        )
    else:
        raw_credits = _first_non_null(
            credits_data,
            'credits',
            'available_credits',
            'credits_remaining',
        )
        output.append(f"Available credits: {raw_credits or 'unknown'}")

    without_contacts = _coerce_int(
        _first_non_null(
            credits_data,
            'without_contacts_credits',
            'withoutContactsCredits',
        )
    )
    if without_contacts is not None:
        output.append(
            f"Without contacts credits: {style(f'{without_contacts:,}', fg='green', bold=True)}"
        )

    plan_type = _first_non_null(credits_data, 'plan_type', 'planType')
    if plan_type:
        output.append(f"Plan: {plan_type}")

    daily_limit = (
        _coerce_int(
            _first_non_null(
                credits_data,
                'daily_limit',
                'dailyLimit',
                'daily_quota',
                'dailyQuota',
            )
        )
        or 5000
    )
    used_today = _coerce_int(
        _first_non_null(
            credits_data,
            'used_today',
            'daily_used',
            'credits_used_today',
            'creditsUsedToday',
        )
    )
    remaining_today = daily_limit - used_today if used_today is not None else None
    percentage_used = (
        (used_today / daily_limit) * 100
        if used_today is not None and daily_limit > 0
        else None
    )

    search_limit = (
        _coerce_int(
            _first_non_null(
                credits_data,
                'search_profile_limit',
                'searchProfileLimit',
            )
        )
        or 5000
    )
    search_usage = _coerce_int(
        _first_non_null(
            credits_data,
            'search_profiles_used',
            'searchProfilesUsed',
        )
    )
    if search_usage is None:
        usage_details = credits_data.get('usageDetails') or {}
        search_usage = _coerce_int(usage_details.get('searches'))

    reset_time = _first_non_null(
        credits_data,
        'reset_time',
        'resetTime',
        'resetDate',
    )
    reset_seconds = _coerce_int(
        _first_non_null(
            credits_data,
            'reset_in_seconds',
            'resetInSeconds',
        )
    )

    output.append("")
    output.append("📊 Daily Quotas")
    if used_today is not None:
        percentage_display = (
            f"{percentage_used:.1f}%" if percentage_used is not None else ""
        )
        usage_line = f"  • Contact reveals: {used_today:,}/{daily_limit:,}"
        if percentage_display:
            usage_line += f" ({percentage_display} used)"
        output.append(usage_line)
        if remaining_today is not None:
            output.append(f"  • Remaining today: {max(remaining_today, 0):,} credits")
    else:
        output.append(f"  • Contact reveals: {daily_limit:,} credits/day")

    if search_usage is not None:
        search_pct = (search_usage / search_limit) * 100 if search_limit > 0 else 0
        output.append(
            f"  • Search profiles: {search_usage:,}/{search_limit:,} ({search_pct:.1f}% used)"
        )
    else:
        output.append(f"  • Search profiles: {search_limit:,} per day")

    if reset_time:
        output.append(f"  • Resets at: {reset_time}")
    elif reset_seconds is not None:
        hours = max(reset_seconds, 0) // 3600
        minutes = (max(reset_seconds, 0) % 3600) // 60
        output.append(f"  • Resets in: {hours}h {minutes}m")

    if percentage_used is not None:
        if percentage_used >= 90:
            output.append(
                f"\n🚨 {style('Critical: Daily reveal quota nearly exhausted!', fg='red', bold=True)}"
            )
            output.append("   • Pause large jobs until the daily reset completes")
        elif percentage_used >= 75:
            output.append(
                f"\n⚠️  {style('Warning: Daily usage above 75%', fg='yellow', bold=True)}"
            )
            output.append("   • Split remaining work into smaller batches")
        elif percentage_used >= 50:
            output.append(f"\nℹ️  {style('Notice: Daily usage above 50%', fg='blue')}")
            output.append("   • Monitor credits closely during bulk operations")

    output.append("")
    output.append("💡 Tips")
    output.append("  • Run signalhire status --credits before large workflows")
    output.append("  • Use --dry-run to confirm costs before revealing contacts")
    output.append("  • Credits reset nightly; plan multi-day campaigns accordingly")

    return "\n".join(output)


def format_operation_status(
    operation_data: dict[str, Any], format_type: str = "human"
) -> str:
    """Format operation status for output display."""
    if format_type == "json":
        return json.dumps(operation_data, indent=2)

    # Human-readable format
    operation_id = operation_data.get('operation_id', 'N/A')
    status = operation_data.get('status', 'unknown')
    operation_type = operation_data.get('type', 'unknown')

    # Status colors
    status_color = {
        'completed': 'green',
        'running': 'blue',
        'pending': 'yellow',
        'failed': 'red',
        'cancelled': 'red',
    }.get(status, 'white')

    output = []
    output.append("🔄 Operation Status")
    output.append(f"ID: {style(operation_id, fg='blue')}")
    output.append(f"Type: {operation_type}")
    output.append(f"Status: {style(status.upper(), fg=status_color, bold=True)}")

    # Timing information
    if operation_data.get('created_at'):
        output.append(f"Created: {operation_data['created_at']}")
    if operation_data.get('started_at'):
        output.append(f"Started: {operation_data['started_at']}")
    if operation_data.get('completed_at'):
        output.append(f"Completed: {operation_data['completed_at']}")

    # Progress information
    if operation_data.get('progress'):
        progress = operation_data['progress']
        output.append(
            f"Progress: {progress.get('current', 0)}/{progress.get('total', 0)}"
        )

    # Results summary
    if status == 'completed' and operation_data.get('results'):
        results = operation_data['results']
        if operation_type == 'search':
            total_found = results.get('total_count', 0)
            output.append(f"Results: {total_found} prospects found")
        elif operation_type == 'reveal':
            revealed = results.get('revealed_count', 0)
            credits_used = results.get('credits_used', 0)
            output.append(
                f"Results: {revealed} contacts revealed ({credits_used} credits)"
            )

    # Error information
    if status == 'failed' and operation_data.get('error'):
        output.append(f"Error: {style(operation_data['error'], fg='red')}")

    return "\n".join(output)


def format_operations_list(
    operations: list[dict[str, Any]], format_type: str = "human"
) -> str:
    """Format list of operations for output display."""
    if format_type == "json":
        return json.dumps(operations, indent=2)

    if not operations:
        return "📋 No recent operations found"

    # Human-readable format
    output = []
    output.append(f"📋 Recent Operations ({len(operations)} total)")
    output.append("")

    for i, op in enumerate(operations[:10], 1):  # Show last 10
        operation_id = op.get('operation_id', 'N/A')[:12]  # Truncate ID
        status = op.get('status', 'unknown')
        operation_type = op.get('type', 'unknown')
        created_at = op.get('created_at', '')

        # Parse datetime for relative time
        try:
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_ago = datetime.now() - created_time.replace(tzinfo=None)

            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600}h ago"
            elif time_ago.seconds > 60:
                time_str = f"{time_ago.seconds // 60}m ago"
            else:
                time_str = "just now"
        except ValueError:
            time_str = "unknown"

        # Status icon
        status_icon = {
            'completed': '✅',
            'running': '🔄',
            'pending': '⏳',
            'failed': '❌',
            'cancelled': '🛑',
        }.get(status, '❓')

        output.append(
            f"{i:2}. {status_icon} {operation_id} | {operation_type:12} | {time_str:8} | {status}"
        )

    if len(operations) > 10:
        output.append(f"\n... and {len(operations) - 10} more operations")

    return "\n".join(output)


def format_system_status(
    system_data: dict[str, Any], format_type: str = "human"
) -> str:
    """Format system status information for output display."""
    if format_type == "json":
        return json.dumps(system_data, indent=2)

    # Human-readable format
    output = []
    output.append("🖥️  System Status")

    # API connectivity
    api_status = system_data.get('api_status', 'unknown')
    api_icon = '✅' if api_status == 'connected' else '❌'
    output.append(f"API Connection: {api_icon} {api_status}")

    # Authentication status
    auth_status = system_data.get('auth_status', 'unknown')
    auth_icon = '✅' if auth_status == 'valid' else '❌'
    output.append(f"Authentication: {auth_icon} {auth_status}")

    # Browser automation status
    browser_status = system_data.get('browser_status', 'disabled')
    browser_icon = '❌'
    output.append(f"Browser Automation: {browser_icon} {browser_status}")

    # Configuration
    config_status = system_data.get('config_status', 'unknown')
    config_icon = '✅' if config_status == 'valid' else '⚠️'
    output.append(f"Configuration: {config_icon} {config_status}")

    # Recent activity
    if system_data.get('last_activity'):
        output.append(f"Last Activity: {system_data['last_activity']}")

    return "\n".join(output)


async def check_credits(config) -> dict[str, Any]:
    """Check available credits."""
    if config.api_key:
        # Use API to check credits
        api_client = SignalHireClient(api_key=config.api_key)

        try:
            # Check regular credits
            credits_response = await api_client.check_credits()

            if not credits_response.success:
                return {
                    'error': credits_response.error or 'Failed to check credits',
                    'credits': 0,
                }

            credits_data = credits_response.data or {}

            # Also check without-contacts credits if supported
            try:
                without_contacts_response = await api_client.check_credits(
                    without_contacts=True
                )
                if without_contacts_response.success and without_contacts_response.data:
                    credits_data['without_contacts_credits'] = (
                        without_contacts_response.data.get('credits', 0)
                    )
            except Exception:  # noqa: BLE001
                # Some accounts may not support this
                pass

            return credits_data

        except Exception as e:  # noqa: BLE001
            return {'error': f"Failed to check credits: {e}", 'credits': 0}

    else:
        # Browser mode - estimate from recent usage
        return {'credits': 'unknown', 'note': 'Credit checking requires API key'}


async def check_operation_status(operation_id: str, config) -> dict[str, Any]:
    """Check status of a specific operation."""
    # Try to load from local operation tracking first
    operation_file = (
        Path.home() / '.signalhire-agent' / 'operations' / f"{operation_id}.json"
    )

    if operation_file.exists():
        try:
            with open(operation_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    # Fallback to API if available
    if config.api_key:
        api_client = SignalHireClient(api_key=config.api_key)
        try:
            return await api_client.get_operation_status(operation_id)
        except Exception as e:  # noqa: BLE001
            return {'operation_id': operation_id, 'status': 'unknown', 'error': str(e)}

    return {
        'operation_id': operation_id,
        'status': 'not_found',
        'error': 'Operation not found',
    }


async def list_recent_operations(limit: int = 20) -> list[dict[str, Any]]:
    """List recent operations."""
    operations = []

    # Load from local operation tracking
    operations_dir = Path.home() / '.signalhire-agent' / 'operations'

    if operations_dir.exists():
        operation_files = sorted(
            operations_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True
        )

        for op_file in operation_files[:limit]:
            try:
                with open(op_file) as f:
                    operations.append(json.load(f))
            except (OSError, json.JSONDecodeError):
                continue

    return operations


async def check_system_status(config) -> dict[str, Any]:
    """Check overall system status."""
    status = {
        'api_status': 'unknown',
        'auth_status': 'unknown',
        'browser_status': 'disabled',
        'config_status': 'unknown',
    }

    # Check API connectivity
    if config.api_key:
        try:
            api_client = SignalHireClient(api_key=config.api_key)
            await api_client.check_credits()
            status['api_status'] = 'connected'
            status['auth_status'] = 'valid'
        except Exception:  # noqa: BLE001
            status['api_status'] = 'error'
            status['auth_status'] = 'invalid'
    else:
        status['api_status'] = 'not_configured'

    # Browser automation status is fixed (disabled)
    # Browser automation disabled in API-first build
    status['browser_status'] = 'disabled'

    # Check configuration
    if config.api_key or (config.email and config.password):
        status['config_status'] = 'valid'
    else:
        status['config_status'] = 'incomplete'

    # Add timestamp
    status['checked_at'] = datetime.now().isoformat()

    return status


def format_daily_usage(usage_data: dict[str, Any], format_type: str = "human") -> str:
    """Format daily usage information for output display."""
    if format_type == "json":
        return json.dumps(usage_data, indent=2)

    credits_used = usage_data.get("credits_used", 0)
    reveals = usage_data.get("reveals", 0)
    searches = usage_data.get("searches", 0)
    daily_limit = usage_data.get("daily_limit", 5000)
    percentage_used = (credits_used / daily_limit) * 100 if daily_limit else 0

    output = []
    output.append("📊 Daily Usage (Last 24 Hours)")
    output.append(f"Credits Used: {style(str(credits_used), fg='blue', bold=True)}")
    output.append(f"Contacts Revealed: {reveals}")
    output.append(f"Searches Performed: {searches}")
    output.append(
        f"Usage vs quota: {percentage_used:.1f}% of {daily_limit:,} daily credits"
    )

    # Enhanced usage warnings with actionable guidance
    if percentage_used >= 90:
        output.append(
            f"\n🚨 {style('CRITICAL: Daily quota above 90%', fg='red', bold=True)}"
        )
        output.append("   • Pause reveals until credits reset at midnight UTC")
        output.append("   • Schedule remaining work for tomorrow")
        output.append("   • Notify stakeholders about quota exhaustion")
    elif percentage_used >= 75:
        output.append(
            f"\n⚠️  {style('WARNING: Daily usage above 75%', fg='yellow', bold=True)}"
        )
        output.append("   • Plan remaining reveals carefully")
        output.append("   • Split bulk jobs into smaller batches")
        output.append("   • Communicate expected completion timelines")
    elif percentage_used >= 50:
        output.append(f"\nℹ️  {style('NOTICE: Daily usage above 50%', fg='blue')}")
        output.append("   • Stay alert for approaching warning thresholds")
        output.append("   • Review upcoming campaign schedule")

    # Usage efficiency metrics
    if reveals > 0:
        avg_credits_per_reveal = credits_used / reveals
        if avg_credits_per_reveal > 1.2:
            output.append(f"\n⚡ {style('EFFICIENCY TIP:', fg='cyan')}")
            output.append("   • Some reveals may have failed")
            output.append("   • Check operation status for details")
            output.append("   • Consider retrying failed operations")

    # Time-based guidance
    current_hour = datetime.now().hour
    if percentage_used >= 50 and current_hour < 18:
        output.append(f"\n⏰ {style('TIMING SUGGESTION:', fg='green')}")
        output.append("   • Consider pausing reveals until tomorrow")
        output.append("   • Daily API limit resets at midnight UTC")

    return "\n".join(output)


def format_credit_warnings(
    credits_data: dict[str, Any], planned_reveals: int = 0, format_type: str = "human"
) -> str:
    """Format proactive credit warnings for planned operations."""
    if format_type == "json":
        return json.dumps(credits_data, indent=2)

    daily_limit = credits_data.get('daily_limit', 5000)
    remaining_credits = max(0, daily_limit - credits_data.get('daily_used', 0))

    output = []
    output.append("⚠️  Credit Pre-Check")

    if planned_reveals > 0:
        if planned_reveals > remaining_credits:
            output.append(f"🚨 {style('INSUFFICIENT CREDITS!', fg='red', bold=True)}")
            output.append(f"   • Planned: {planned_reveals} reveals")
            output.append(f"   • Available: {remaining_credits} credits")
            output.append(
                f"   • Shortfall: {planned_reveals - remaining_credits} credits"
            )
            output.append(
                "   • SOLUTION: Reduce batch size or resume after the daily reset"
            )
        elif remaining_credits and planned_reveals > remaining_credits * 0.8:
            output.append(
                f"⚠️  {style('HIGH RISK: Close to daily limit', fg='yellow', bold=True)}"
            )
            output.append(f"   • Planned: {planned_reveals} reveals")
            output.append(f"   • Available: {remaining_credits} credits")
            output.append("   • RECOMMENDATION: Consider smaller batches")
        else:
            output.append(f"✅ {style('SUFFICIENT CREDITS', fg='green')}")
            output.append(f"   • Planned: {planned_reveals} reveals")
            output.append(f"   • Available: {remaining_credits} credits")
            output.append(
                f"   • Remaining after: {remaining_credits - planned_reveals} credits"
            )

    return "\n".join(output)


async def check_credit_sufficiency(config, planned_reveals: int = 0) -> dict[str, Any]:
    """Check if there are sufficient credits for planned reveals."""
    credits_data = await check_credits(config)
    daily_usage = await check_daily_usage()

    credits_data['daily_used'] = daily_usage.get('credits_used', 0)
    credits_data['daily_limit'] = daily_usage.get('daily_limit', 5000)
    credits_data['planned_reveals'] = planned_reveals
    credits_data['sufficient'] = planned_reveals <= max(
        0, credits_data['daily_limit'] - credits_data.get('daily_used', 0)
    )

    return credits_data


async def check_daily_usage() -> dict[str, Any]:
    """Check API and browser usage for the last 24 hours."""
    operations = await list_recent_operations(
        limit=1000
    )  # Get a large number of recent operations

    usage_data = {
        "credits_used": 0,
        "reveals": 0,
        "searches": 0,
        "from_time": (datetime.now() - timedelta(days=1)).isoformat(),
        "to_time": datetime.now().isoformat(),
        "daily_limit": 5000,
    }

    one_day_ago = datetime.now() - timedelta(days=1)

    for op in operations:
        try:
            created_time = datetime.fromisoformat(
                op.get('created_at', '').replace('Z', '+00:00')
            )
            if created_time.replace(tzinfo=None) < one_day_ago:
                continue
        except ValueError:
            continue

        op_type = op.get("type")
        if op_type == "reveal":
            usage_data["reveals"] += 1
            if op.get("status") == "completed" and op.get("results"):
                usage_data["credits_used"] += op["results"].get("credits_used", 0)
        elif op_type == "search":
            usage_data["searches"] += 1

    return usage_data


@click.command()
@click.option('--operation-id', help='Check specific operation status')
@click.option('--credits', 'show_credits', is_flag=True, help='Show remaining credits')
@click.option('--operations', is_flag=True, help='List recent operations')
@click.option(
    '--daily-usage', is_flag=True, help='Show API and browser usage for today'
)
@click.option('--logs', is_flag=True, help='Show recent log entries')
@click.option('--system', is_flag=True, help='Show system status')
@click.option('--all', 'show_all', is_flag=True, help='Show all status information')
@click.pass_context
def status(
    ctx, operation_id, show_credits, operations, daily_usage, logs, system, show_all
):
    """
    Check operation status and account information.
    Monitor your SignalHire agent operations, check remaining credits,
    and view system health status. Use various options to focus on
    specific information or get a complete overview.

    \b
    Examples:
      # Check account credits
      signalhire-agent status --credits
      # Show daily usage
      signalhire-agent status --daily-usage
      # Check specific operation
      signalhire-agent status --operation-id abc123
      # View recent operations
      signalhire-agent status --operations
      # Complete status overview
      signalhire-agent status --all
    """

    config = ctx.obj['config']

    # If no specific option is provided, show a summary
    if not any(
        [operation_id, show_credits, operations, daily_usage, logs, system, show_all]
    ):
        show_all = True

    try:
        # Check specific operation
        if operation_id:
            echo("🔍 Checking operation status...")
            operation_data = asyncio.run(check_operation_status(operation_id, config))

            if config.output_format == 'json':
                echo(json.dumps(operation_data, indent=2))
            else:
                echo(format_operation_status(operation_data, config.output_format))
            return

        # Show credits information
        if show_credits or show_all:
            echo("💳 Checking credits...")
            credits_data = asyncio.run(check_credits(config))

            if config.output_format == 'json':
                echo(json.dumps(credits_data, indent=2))
            else:
                echo(format_credits_info(credits_data, config.output_format))

            if show_all:
                echo("")  # Add spacing for multiple sections

        # Show daily usage
        if daily_usage or show_all:
            echo("📊 Checking daily usage...")
            usage_data = asyncio.run(check_daily_usage())

            if config.output_format == 'json':
                echo(json.dumps(usage_data, indent=2))
            else:
                echo(format_daily_usage(usage_data, config.output_format))

            if show_all:
                echo("")

        # Show recent operations
        if operations or show_all:
            echo("📋 Loading recent operations...")
            operations_list = asyncio.run(list_recent_operations())

            if config.output_format == 'json':
                echo(json.dumps(operations_list, indent=2))
            else:
                echo(format_operations_list(operations_list, config.output_format))

            if show_all:
                echo("")  # Add spacing for multiple sections

        # Show system status
        if system or show_all:
            echo("🖥️  Checking system status...")
            system_data = asyncio.run(check_system_status(config))

            if config.output_format == 'json':
                echo(json.dumps(system_data, indent=2))
            else:
                echo(format_system_status(system_data, config.output_format))

        # Show logs
        if logs:
            echo("📄 Recent logs:")
            log_file = Path.home() / '.signalhire-agent' / 'logs' / 'agent.log'

            if log_file.exists():
                try:
                    with open(log_file) as f:
                        lines = f.readlines()
                        # Show last 20 lines
                        recent_lines = lines[-20:] if len(lines) > 20 else lines

                        for line in recent_lines:
                            echo(line.rstrip())

                        if len(lines) > 20:
                            echo(f"\n... ({len(lines) - 20} more lines in {log_file})")
                except OSError as e:
                    echo(style(f"Error reading log file: {e}", fg='red'))
            else:
                echo("No log file found")

    except KeyboardInterrupt:
        echo("\n🛑 Status check cancelled by user", err=True)
        ctx.exit(1)
    except Exception as e:  # noqa: BLE001
        echo(style(f"❌ Status check failed: {e}", fg='red'), err=True)
        if config.debug:
            import traceback

            echo(traceback.format_exc(), err=True)
        ctx.exit(1)
