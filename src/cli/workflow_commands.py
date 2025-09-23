"""
Workflow command implementation for SignalHire Agent CLI

This module provides workflow commands that combine multiple operations
like search, reveal, and export in automated sequences.
"""

import asyncio
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from click import echo, style

from models.search_criteria import SearchCriteria
from services.export_service import ExportService
from services.signalhire_client import SignalHireClient
from .reveal_commands import handle_api_error


class WorkflowRunner:
    """Handles the execution of complete workflows."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.export_service = ExportService()

    async def run_lead_generation(
        self,
        search_criteria: SearchCriteria,
        output_dir: Path,
        list_name: str | None = None,
        max_prospects: int = 10000,
    ) -> dict[str, Any]:
        """Run complete lead generation workflow: search → reveal → export."""

        workflow_start = datetime.now()
        workflow_id = f"workflow_{int(workflow_start.timestamp())}"

        self.logger.info(
            "Starting lead generation workflow",
            workflow_id=workflow_id,
            max_prospects=max_prospects,
        )

        results = {
            'workflow_id': workflow_id,
            'workflow_type': 'lead-generation',
            'started_at': workflow_start.isoformat(),
            'search_results': None,
            'reveal_results': None,
            'export_results': None,
            'total_prospects_found': 0,
            'total_contacts_revealed': 0,
            'credits_used': 0,
            'output_files': [],
        }

        try:
            # Step 1: Search for prospects
            echo("🔍 Step 1: Searching for prospects...")
            search_results = await self._execute_search(search_criteria, max_prospects)
            results['search_results'] = search_results
            results['total_prospects_found'] = search_results.get('total_count', 0)

            prospects = search_results.get('prospects', [])
            prospect_uids = [
                p.get('uid') or p.get('id')
                for p in prospects
                if p.get('uid') or p.get('id')
            ]

            if not prospect_uids:
                echo(style("⚠️  No prospects found to reveal", fg='yellow'))
                return results

            echo(f"✅ Found {len(prospect_uids)} prospects")

            # Step 2: Reveal contacts
            echo("🔓 Step 2: Revealing contact information...")
            reveal_results = await self._execute_reveal(prospect_uids, list_name)
            results['reveal_results'] = reveal_results
            results['total_contacts_revealed'] = reveal_results.get('revealed_count', 0)
            results['credits_used'] = reveal_results.get('credits_used', 0)

            echo(
                f"✅ Revealed {results['total_contacts_revealed']} contacts using {results['credits_used']} credits"
            )

            # Step 3: Export data
            echo("📁 Step 3: Exporting data...")
            export_results = await self._execute_export(
                search_results, reveal_results, output_dir, workflow_id
            )
            results['export_results'] = export_results
            results['output_files'] = export_results.get('files', [])

            echo(f"✅ Exported data to {len(results['output_files'])} files")

            results['status'] = 'completed'
            results['completed_at'] = datetime.now().isoformat()

            return results

        except Exception as e:
            self.logger.error("Workflow failed", error=str(e), workflow_id=workflow_id)
            results['status'] = 'failed'
            results['error'] = str(e)
            results['completed_at'] = datetime.now().isoformat()
            raise

    async def run_prospect_enrichment(
        self, prospect_list_file: str, output_dir: Path
    ) -> dict[str, Any]:
        """Enrich existing prospect list with contact information."""

        workflow_start = datetime.now()
        workflow_id = f"enrichment_{int(workflow_start.timestamp())}"

        self.logger.info(
            "Starting prospect enrichment workflow",
            workflow_id=workflow_id,
            prospect_file=prospect_list_file,
        )

        results = {
            'workflow_id': workflow_id,
            'workflow_type': 'prospect-enrichment',
            'started_at': workflow_start.isoformat(),
            'input_file': prospect_list_file,
            'prospects_loaded': 0,
            'contacts_revealed': 0,
            'credits_used': 0,
            'output_files': [],
        }

        try:
            # Load existing prospects
            echo(f"📂 Loading prospects from {prospect_list_file}...")
            prospect_uids = await self._load_prospect_list(prospect_list_file)
            results['prospects_loaded'] = len(prospect_uids)

            if not prospect_uids:
                echo(style("⚠️  No valid prospect UIDs found in file", fg='yellow'))
                return results

            echo(f"✅ Loaded {len(prospect_uids)} prospects")

            # Reveal contacts for existing prospects
            echo("🔓 Enriching prospects with contact information...")
            reveal_results = await self._execute_reveal(prospect_uids)
            results['contacts_revealed'] = reveal_results.get('revealed_count', 0)
            results['credits_used'] = reveal_results.get('credits_used', 0)

            # Export enriched data
            echo("📁 Exporting enriched data...")
            export_results = await self._execute_export(
                None, reveal_results, output_dir, workflow_id
            )
            results['output_files'] = export_results.get('files', [])

            results['status'] = 'completed'
            results['completed_at'] = datetime.now().isoformat()

            return results

        except Exception as e:
            self.logger.error(
                "Enrichment workflow failed", error=str(e), workflow_id=workflow_id
            )
            results['status'] = 'failed'
            results['error'] = str(e)
            results['completed_at'] = datetime.now().isoformat()
            raise

    async def run_bulk_export(self, list_name: str, output_dir: Path) -> dict[str, Any]:
        """Export existing SignalHire list/project."""

        workflow_start = datetime.now()
        workflow_id = f"export_{int(workflow_start.timestamp())}"

        self.logger.info(
            "Starting bulk export workflow",
            workflow_id=workflow_id,
            list_name=list_name,
        )

        results = {
            'workflow_id': workflow_id,
            'workflow_type': 'bulk-export',
            'started_at': workflow_start.isoformat(),
            'list_name': list_name,
            'records_exported': 0,
            'output_files': [],
        }

        try:
            # In API-only mode, bulk export via UI is not supported
            raise click.ClickException(
                "Bulk export of existing UI lists is not supported in API-only mode."
            )

            results['status'] = 'completed'
            results['completed_at'] = datetime.now().isoformat()

            return results

        except Exception as e:
            self.logger.error(
                "Bulk export workflow failed", error=str(e), workflow_id=workflow_id
            )
            results['status'] = 'failed'
            results['error'] = str(e)
            results['completed_at'] = datetime.now().isoformat()
            raise

    async def _execute_search(
        self, search_criteria: SearchCriteria, max_prospects: int
    ) -> dict[str, Any]:
        """Execute search operation (API-only)."""
        api_client = SignalHireClient(api_key=self.config.api_key)
        # Convert SearchCriteria to dict for API call
        search_dict = {
            "title": search_criteria.title,
            "location": search_criteria.location,
            "company": search_criteria.company,
            "industry": getattr(search_criteria, 'industry', None),
            "keywords": getattr(search_criteria, 'keywords', None),
            "name": getattr(search_criteria, 'name', None),
            "experience_from": getattr(search_criteria, 'experience_from', None),
            "experience_to": getattr(search_criteria, 'experience_to', None),
            "open_to_work": getattr(search_criteria, 'open_to_work', None),
        }
        search_dict = {k: v for k, v in search_dict.items() if v is not None}

        api_response = await api_client.search_prospects(
            search_dict, page=1, limit=getattr(search_criteria, 'size', 50)
        )
        if api_response.success:
            return api_response.data
        raise Exception(f"API search failed: {api_response.error}")

        if api_response.success:
            return api_response.data
        raise Exception(f"API search failed: {api_response.error}")

    async def _execute_reveal(
        self, prospect_uids: list[str], list_name: str | None = None
    ) -> dict[str, Any]:
        """Execute reveal operation."""
        api_client = SignalHireClient(api_key=self.config.api_key)
        from models.operations import RevealOp

        operation = RevealOp(prospect_ids=prospect_uids, batch_size=100)
        return await api_client.bulk_reveal(operation)

    async def _execute_export(
        self,
        search_results: dict,
        reveal_results: dict,
        output_dir: Path,
        workflow_id: str,
    ) -> dict[str, Any]:
        """Execute export operation."""
        output_dir.mkdir(parents=True, exist_ok=True)
        files = []

        # Export search results if available
        if search_results:
            search_file = output_dir / f"{workflow_id}_search_results.json"
            with open(search_file, 'w') as f:
                json.dump(search_results, f, indent=2)
            files.append(str(search_file))

        # Export reveal results
        if reveal_results and reveal_results.get('prospects'):
            reveal_file = output_dir / f"{workflow_id}_contacts.csv"
            await self.export_service.export_prospects_to_csv(
                reveal_results['prospects'], str(reveal_file)
            )
            files.append(str(reveal_file))

        # Create summary file
        summary_file = output_dir / f"{workflow_id}_summary.json"
        summary = {
            'workflow_id': workflow_id,
            'total_prospects': (
                len(search_results.get('prospects', [])) if search_results else 0
            ),
            'revealed_contacts': (
                reveal_results.get('revealed_count', 0) if reveal_results else 0
            ),
            'credits_used': (
                reveal_results.get('credits_used', 0) if reveal_results else 0
            ),
            'files': files,
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        files.append(str(summary_file))

        return {'files': files, 'record_count': summary['revealed_contacts']}

    async def _load_prospect_list(self, file_path: str) -> list[str]:
        """Load prospect UIDs from various file formats."""
        path = Path(file_path)

        if not path.exists():
            raise click.ClickException(f"File not found: {file_path}")

        if file_path.endswith('.json'):
            with open(path) as f:
                data = json.load(f)

            if isinstance(data, list):
                return data
            if isinstance(data, dict) and 'prospects' in data:
                return [
                    p.get('uid') or p.get('id')
                    for p in data['prospects']
                    if p.get('uid') or p.get('id')
                ]

        elif file_path.endswith('.csv'):
            uids = []
            with open(path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uid = row.get('uid') or row.get('id') or row.get('prospect_id')
                    if uid:
                        uids.append(uid)
            return uids

        raise click.ClickException(f"Unsupported file format: {file_path}")


def format_workflow_results(results: dict[str, Any], format_type: str = "human") -> str:
    """Format workflow results for output display."""
    if format_type == "json":
        return json.dumps(results, indent=2)

    # Human-readable format
    workflow_id = results.get('workflow_id', 'N/A')
    workflow_type = results.get('workflow_type', 'unknown')
    status = results.get('status', 'unknown')

    output = []
    output.append("🔄 Workflow Results")
    output.append(f"ID: {style(workflow_id, fg='blue')}")
    output.append(f"Type: {workflow_type}")
    output.append(
        f"Status: {style(status, fg='green' if status == 'completed' else 'red')}"
    )

    if workflow_type == 'lead-generation':
        prospects_found = results.get('total_prospects_found', 0)
        contacts_revealed = results.get('total_contacts_revealed', 0)
        credits_used = results.get('credits_used', 0)

        output.append(f"Prospects found: {style(str(prospects_found), bold=True)}")
        output.append(
            f"Contacts revealed: {style(str(contacts_revealed), fg='green', bold=True)}"
        )
        output.append(f"Credits used: {style(str(credits_used), fg='yellow')}")

    elif workflow_type == 'prospect-enrichment':
        prospects_loaded = results.get('prospects_loaded', 0)
        contacts_revealed = results.get('contacts_revealed', 0)
        credits_used = results.get('credits_used', 0)

        output.append(f"Prospects loaded: {style(str(prospects_loaded), bold=True)}")
        output.append(
            f"Contacts revealed: {style(str(contacts_revealed), fg='green', bold=True)}"
        )
        output.append(f"Credits used: {style(str(credits_used), fg='yellow')}")

    elif workflow_type == 'bulk-export':
        records_exported = results.get('records_exported', 0)
        list_name = results.get('list_name', 'N/A')

        output.append(f"List: {list_name}")
        output.append(
            f"Records exported: {style(str(records_exported), fg='green', bold=True)}"
        )

    # Output files
    output_files = results.get('output_files', [])
    if output_files:
        output.append("\n📁 Output files:")
        for file_path in output_files:
            output.append(f"  • {Path(file_path).name}")

    # Error details
    if status == 'failed' and results.get('error'):
        output.append(f"\n❌ Error: {results['error']}")

    return "\n".join(output)


@click.group()
def workflow():
    """Complete lead generation workflows (API-first by default).

    Execute end-to-end workflows that combine search and contact revelation.
    Uses API mode by default for reliability, with browser fallback for large volumes.
    Perfect for automated lead generation pipelines.
    """


@workflow.command('lead-generation')
@click.option(
    '--search-criteria',
    type=click.Path(exists=True),
    help='JSON file with search parameters',
)
@click.option('--title', help='Job title (alternative to search criteria file)')
@click.option('--location', help='Location (alternative to search criteria file)')
@click.option('--company', help='Company (alternative to search criteria file)')
@click.option('--keywords', help='Keywords (alternative to search criteria file)')
@click.option(
    '--output-dir',
    type=click.Path(),
    default='./output',
    help='Directory for output files [default: ./output]',
)
@click.option('--list-name', help='Name for SignalHire lead list')
@click.option(
    '--max-prospects',
    type=int,
    default=10000,
    help='Maximum prospects to process [default: 10000]',
)
@click.pass_context
def lead_generation(
    ctx,
    search_criteria,
    title,
    location,
    company,
    keywords,
    output_dir,
    list_name,
    max_prospects,
):
    """
    Complete lead generation workflow: search → reveal → export.

    Executes a full lead generation workflow including prospect search,
    contact revelation, and data export. Results are saved to the specified
    output directory with organized file structure.

    \b
    Examples:
      # Using search criteria file
      signalhire-agent workflow lead-generation --search-criteria search.json --list-name "Q4 Leads"

      # Using inline search parameters
      signalhire-agent workflow lead-generation --title "Product Manager" --location "New York" --company "Tech"
    """

    config = ctx.obj['config']
    logger = ctx.obj.get('logger')

    # Build search criteria
    if search_criteria:
        with open(search_criteria) as f:
            criteria_data = json.load(f)
        search_criteria_obj = SearchCriteria(**criteria_data)
    elif any([title, location, company, keywords]):
        search_criteria_obj = SearchCriteria(
            title=title, location=location, company=company, keywords=keywords
        )
    else:
        echo(
            style(
                "Error: Either --search-criteria file or search parameters required",
                fg='red',
            ),
            err=True,
        )
        ctx.exit(1)

    # Validate credentials
    if not config.api_key:
        echo(style("Error: API key is required in API-only mode", fg='red'), err=True)
        ctx.exit(1)

    output_path = Path(output_dir)

    try:
        echo("🚀 Starting lead generation workflow...")

        runner = WorkflowRunner(config, logger)
        results = asyncio.run(
            runner.run_lead_generation(
                search_criteria_obj, output_path, list_name, max_prospects
            )
        )

        # Display results
        if config.output_format == 'json':
            echo(json.dumps(results, indent=2))
        else:
            echo(format_workflow_results(results, config.output_format))

        echo("\n✅ Workflow completed successfully!")
        echo(f"📁 Results saved to: {output_path.absolute()}")

    except KeyboardInterrupt:
        echo("\n🛑 Workflow cancelled by user", err=True)
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
        logger = logging.getLogger(__name__)
        handle_api_error(error_message, status_code, logger)

        if config.debug:
            import traceback

            echo("\n🔧 Debug information:")
            echo(traceback.format_exc())

        ctx.exit(1)


@workflow.command('prospect-enrichment')
@click.option(
    '--prospect-list',
    required=True,
    type=click.Path(exists=True),
    help='Existing prospect list file (CSV or JSON)',
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default='./enriched',
    help='Directory for output files [default: ./enriched]',
)
@click.pass_context
def prospect_enrichment(ctx, prospect_list, output_dir):
    """
    Enrich existing prospect list with contact information.

    Takes an existing list of prospects and enriches them with contact
    information using SignalHire's database.

    \b
    Examples:
      signalhire-agent workflow prospect-enrichment --prospect-list leads.csv --output-dir ./enriched
    """

    config = ctx.obj['config']
    logger = ctx.obj.get('logger')

    # Validate credentials (API-only)
    if config.browser_mode:
        echo(
            style(
                "Error: Browser automation is disabled. Use API credentials only.",
                fg='red',
            ),
            err=True,
        )
        ctx.exit(1)

    if not config.api_key:
        echo(
            style("Error: SIGNALHIRE_API_KEY is required for this workflow.", fg='red'),
            err=True,
        )
        ctx.exit(1)

    output_path = Path(output_dir)

    try:
        echo("🔄 Starting prospect enrichment workflow...")

        runner = WorkflowRunner(config, logger)
        results = asyncio.run(
            runner.run_prospect_enrichment(prospect_list, output_path)
        )

        # Display results
        if config.output_format == 'json':
            echo(json.dumps(results, indent=2))
        else:
            echo(format_workflow_results(results, config.output_format))

        echo("\n✅ Enrichment completed successfully!")
        echo(f"📁 Results saved to: {output_path.absolute()}")

    except KeyboardInterrupt:
        echo("\n🛑 Enrichment cancelled by user", err=True)
        ctx.exit(1)
    except Exception as e:  # noqa: BLE001
        echo(style(f"❌ Enrichment failed: {e}", fg='red'), err=True)
        if config.debug:
            import traceback

            echo(traceback.format_exc(), err=True)
        ctx.exit(1)


@workflow.command('bulk-export')
@click.option(
    '--export-existing',
    required=True,
    help='Name of existing SignalHire list to export',
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default='./exports',
    help='Directory for output files [default: ./exports]',
)
@click.pass_context
def bulk_export(ctx, export_existing, output_dir):
    """
    Export existing SignalHire lists/projects.

    Browser automation is disabled in this release, so the workflow
    exits immediately with guidance to use the API export tools instead.

    \b
    Examples:
      signalhire-agent workflow bulk-export --export-existing "Q3 Campaign Results" --output-dir ./exports
    """

    config = ctx.obj['config']
    logger = ctx.obj.get('logger')

    echo(
        style(
            "Error: Bulk export requires browser automation, which is currently disabled.",
            fg='red',
        ),
        err=True,
    )
    echo("Use signalhire export commands backed by the API instead.", err=True)
    ctx.exit(1)
