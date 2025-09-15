"""
Main CLI application for SignalHire Agent

This module provides the main CLI interface and global configuration
for the SignalHire agent application.
"""

import json
import os
import sys
from pathlib import Path

import click
import structlog
from click import Context, echo, style
from dotenv import load_dotenv

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class CliConfig:
    """Configuration class for CLI application."""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Authentication
        self.email: str | None = os.getenv('SIGNALHIRE_EMAIL')
        self.password: str | None = os.getenv('SIGNALHIRE_PASSWORD')
        self.api_key: str | None = os.getenv('SIGNALHIRE_API_KEY')
        # API endpoint configuration
        self.api_base_url: str = os.getenv('SIGNALHIRE_API_BASE_URL', 'https://api.signalhire.com')
        self.api_prefix: str = os.getenv('SIGNALHIRE_API_PREFIX', '/api/v1')

        # Browser configuration
        self.browser_mode: bool = False  # Will auto-detect if API key not available
        self.headless: bool = True

        # Output configuration
        self.output_format: str = "human"  # human, json
        self.verbose: bool = False
        self.debug: bool = False

        # File paths
        self.config_dir = Path.home() / '.signalhire-agent'
        self.config_file = self.config_dir / 'config.json'

        # Load saved configuration
        self.load_config()

    def load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    saved_config = json.load(f)

                # Update configuration with saved values (don't override env vars)
                if not self.email and saved_config.get('email'):
                    self.email = saved_config['email']

                self.headless = saved_config.get('headless', self.headless)
                self.output_format = saved_config.get('output_format', self.output_format)

            except (json.JSONDecodeError, IOError) as e:
                logger.warning("Could not load saved configuration", error=str(e))

    def save_config(self):
        """Save current configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        config_data = {
            'email': self.email,
            'headless': self.headless,
            'output_format': self.output_format,
            'api_base_url': self.api_base_url,
            'api_prefix': self.api_prefix,
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            logger.warning("Could not save configuration", error=str(e))

    def auto_detect_mode(self):
        """Auto-detect whether to use browser or API mode."""
        if self.api_key:
            self.browser_mode = False
        elif self.email and self.password:
            self.browser_mode = True
        else:
            # Default to browser mode, will show error if credentials missing
            self.browser_mode = True


# Global configuration instance
cli_config = CliConfig()


@click.group()
@click.option(
    '--email',
    envvar='SIGNALHIRE_EMAIL',
    help='SignalHire login email'
)
@click.option(
    '--password',
    envvar='SIGNALHIRE_PASSWORD',
    help='SignalHire login password'
)
@click.option(
    '--api-key',
    envvar='SIGNALHIRE_API_KEY',
    help='SignalHire API key (alternative to email/password)'
)
@click.option(
    '--api-base-url',
    envvar='SIGNALHIRE_API_BASE_URL',
    help='Override API base URL (default: https://api.signalhire.com)'
)
@click.option(
    '--api-prefix',
    envvar='SIGNALHIRE_API_PREFIX',
    help='Override API path prefix (default: /api/v1)'
)
@click.option(
    '--api-only',
    is_flag=True,
    help='Force API-only mode and disable any browser fallback'
)
@click.option(
    '--output-format',
    type=click.Choice(['human', 'json']),
    default='human',
    help='Output format [default: human]'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug output'
)
@click.pass_context
def main(ctx: Context, email, password, api_key, api_base_url, api_prefix, api_only, output_format, verbose, debug):
    """
    SignalHire Agent - API-First Lead Generation & Contact Revelation
    🚀 API-FIRST APPROACH: Uses SignalHire's API by default for reliable, fast contact reveals
    📊 Rate limits: 600 elements/minute search, separate daily reveal quotas
    🌐 BROWSER MODE: Optional browser automation for bulk operations (1000+ contacts)
    
    QUICK START:
      # Set credentials (choose one method)
      export SIGNALHIRE_EMAIL="your@email.com"
      export SIGNALHIRE_PASSWORD="your_password"
      # OR
      export SIGNALHIRE_API_KEY="your_api_key"

      # Search for prospects
      signalhire search --title "Software Engineer" --location "San Francisco"

      # Reveal contacts (API-first by default)
      signalhire reveal --input prospects.csv --output contacts.csv

      # Force browser mode for bulk operations
      signalhire reveal --input large_list.csv --browser --bulk-size 1000
    
    MODES:
      • API Mode (Default): Fast, reliable, daily reveal quotas
      • Browser Mode: Slower but handles large volumes, bypasses API limits
      • Auto Mode: Automatically chooses best method based on volume
    
    EXAMPLES:
      # Basic search and reveal (API-first)
      signalhire search --title "VP Engineering" --company "Tech Startup"
      signalhire reveal --search-id abc123 --output vps.csv

      # Large-scale operation (browser mode)
      signalhire reveal --input 5000_prospects.csv --browser --bulk-size 2000

      # Check credits and status
      signalhire credits --check
      signalhire status --detailed

      # Workflow with progress tracking
      signalhire workflow --title "CTO" --location "Silicon Valley" --limit 50
    """

    # Ensure context dict exists
    ctx.ensure_object(dict)

    # Update configuration with CLI options
    if email:
        cli_config.email = email
    if password:
        cli_config.password = password
    if api_key:
        cli_config.api_key = api_key
    if api_base_url:
        cli_config.api_base_url = api_base_url
    if api_prefix is not None and api_prefix != "":
        cli_config.api_prefix = api_prefix
    if api_only:
        cli_config.browser_mode = False
    # API-only mode
    cli_config.browser_mode = False
    cli_config.output_format = output_format
    cli_config.verbose = verbose
    cli_config.debug = debug

    # Auto-detect no longer toggles browser; API-only

    # Configure logging level
    if debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        import logging
        logging.getLogger().setLevel(logging.INFO)

    # Store configuration in context
    ctx.obj['config'] = cli_config
    ctx.obj['logger'] = logger

    # Save configuration for next run
    cli_config.save_config()


@main.command()
@click.option('--ping', is_flag=True, help='Perform live API ping checks to /credits and /search')
@click.pass_context
def doctor(ctx, ping):
    """
    Run diagnostics to check system health and configuration.
    This command verifies that all dependencies are installed,
    credentials are configured, and the system is ready to use.
    """

    config = ctx.obj['config']

    echo("🔍 SignalHire Agent Diagnostics\n")

    # Check Python version
    echo(f"Python Version: {style(sys.version.split()[0], fg='green')}")

    # Check dependencies
    echo("\n📦 Dependencies:")
    # Map package names to import names
    required_packages = {
        'click': 'click',
        'httpx': 'httpx',
        'pandas': 'pandas',
        'pydantic': 'pydantic',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'structlog': 'structlog',
        'python-dotenv': 'dotenv',
        'email-validator': 'email_validator'
    }

    missing_packages = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            echo(f"  ✅ {package_name}")
        except ImportError:
            echo(f"  ❌ {package_name} - {style('MISSING', fg='red')}")
            missing_packages.append(package_name)

    if missing_packages:
        echo(f"\n⚠️  Install missing packages: pip install {' '.join(missing_packages)}")

    # Check authentication (API-only)
    echo("\n🔐 Authentication:")
    if config.api_key:
        echo(f"  ✅ API Key: {config.api_key[:8]}...")
        echo("  📡 Mode: API")
    else:
        echo("  ❌ No API key configured")
        echo("     Set SIGNALHIRE_API_KEY or pass --api-key")

    # Check configuration
    echo("\n⚙️  Configuration:")
    echo(f"  Output Format: {config.output_format}")
    echo(f"  API Base URL: {config.api_base_url}")
    echo(f"  API Prefix: {config.api_prefix}")
    try:
        sample_credits = f"{config.api_base_url.rstrip('/')}/{config.api_prefix.strip('/')}/credits"
        sample_search = f"{config.api_base_url.rstrip('/')}/{config.api_prefix.strip('/')}/candidate/searchByQuery"
    except TypeError:
        sample_credits = sample_search = "(could not build sample URL)"
    echo(f"  Sample credits URL: {sample_credits}")
    echo(f"  Sample search URL:  {sample_search}")

    # Optional live ping checks
    if ping:
        echo("\n🔎 Live API Ping:")
        if not config.api_key:
            echo(style("  ❌ Cannot ping without SIGNALHIRE_API_KEY", fg='red'))
        else:
            try:
                # Import lazily to avoid circulars
                import asyncio as _asyncio

                from ..services.signalhire_client import SignalHireClient

                async def _do_ping():
                    client = SignalHireClient(
                        api_key=config.api_key,
                        base_url=config.api_base_url,
                        api_prefix=config.api_prefix,
                    )
                    credits_response = await client.check_credits()
                    echo(f"  Credits: success={credits_response.success} status={credits_response.status_code} data={credits_response.data or credits_response.error}")
                    search = await client.search_prospects({"title": "Engineer"}, limit=1)
                    echo(f"  Search: success={search.success} status={search.status_code} keys={list((search.data or {}).keys())}")

                _asyncio.run(_do_ping())
            except Exception as e:  # noqa: BLE001
                echo(style(f"  ❌ Ping failed: {e}", fg='red'))
    echo(f"  Config File: {config.config_file}")

    # Check file system
    echo("\n📁 File System:")
    echo(f"  Config Directory: {config.config_dir}")
    echo(f"  Directory Exists: {config.config_dir.exists()}")
    echo(f"  Directory Writable: {os.access(config.config_dir.parent, os.W_OK)}")

    # Overall status
    if missing_packages:
        echo(f"\n❌ Status: {style('Issues found - install missing packages', fg='red')}")
        ctx.exit(1)
    elif not (config.api_key or (config.email and config.password)):
        echo(f"\n⚠️  Status: {style('Ready, but no credentials configured', fg='yellow')}")
    else:
        echo(f"\n✅ Status: {style('All systems ready', fg='green')}")


# Import and register commands after main is defined
from .config_commands import config  # noqa: E402
from .export_commands import export  # noqa: E402
from .reveal_commands import reveal  # noqa: E402
from .search_commands import search  # noqa: E402
from .status_commands import status  # noqa: E402
from .workflow_commands import workflow  # noqa: E402
from .dedupe_commands import dedupe  # noqa: E402
from .analyze_commands import analyze  # noqa: E402
from .filter_commands import filter as filter_contacts  # noqa: E402

main.add_command(search)
main.add_command(reveal)
main.add_command(workflow)
main.add_command(status)
main.add_command(config)
main.add_command(export)
main.add_command(dedupe)
main.add_command(analyze)
main.add_command(filter_contacts)


if __name__ == '__main__':
    main()
