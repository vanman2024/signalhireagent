"""
Search command implementation for SignalHire Agent CLI

This module provides the search command functionality, allowing users to
search for prospects using various criteria and filters.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import click
from click import echo, style

from ..models.search_criteria import SearchCriteria
from ..services.signalhire_client import SignalHireClient
from .reveal_commands import handle_api_error


def format_prospect_output(prospect: dict[str, Any], format_type: str = "human") -> str:
    """Format a single prospect for output display."""
    if format_type == "json":
        return json.dumps(prospect, indent=2)

    # Human-readable format
    # Try multiple key styles from different API shapes
    name = prospect.get('full_name') or prospect.get('fullName') or 'Unknown'
    title = prospect.get('current_title') or prospect.get('currentTitle')
    company = prospect.get('current_company') or prospect.get('currentCompany')
    location = prospect.get('location', 'Unknown Location')

    # Fallback: derive title/company from experience if missing
    if (
        (not title or not company)
        and isinstance(prospect.get('experience'), list)
        and prospect['experience']
    ):
        exp0 = prospect['experience'][0]
        title = title or exp0.get('title')
        company = company or exp0.get('company')

    title = title or 'Unknown Title'
    company = company or 'Unknown Company'

    return f"  • {style(name, bold=True)} - {title} at {company} ({location})"


def format_search_results(results: dict[str, Any], format_type: str = "human") -> str:
    """Format search results for output display."""
    if format_type == "json":
        return json.dumps(results, indent=2)

    # Human-readable format
    # Support both legacy and new Search API shapes
    request_id = results.get('request_id') or results.get('requestId') or 'N/A'
    total_count = results.get('total_count') or results.get('total') or 0
    profiles = results.get('prospects') or results.get('profiles') or []
    current_batch = len(profiles)
    scroll_id = results.get('scroll_id') or results.get('scrollId')

    output = []
    output.append("🔍 Search Results")
    output.append(f"Request ID: {style(str(request_id), fg='blue')}")
    output.append(
        f"Total prospects found: {style(str(total_count), fg='green', bold=True)}"
    )
    output.append(f"Current batch: {current_batch} prospects")

    if scroll_id:
        output.append(f"Scroll ID: {scroll_id[:20]}... (use --continue-search)")

    # Display prospects
    if profiles:
        output.append("\n📋 Prospects in this batch:")
        for prospect in profiles:
            output.append(format_prospect_output(prospect, format_type))

    return "\n".join(output)


def save_search_results(
    results: dict[str, Any], output_file: str, format_type: str = "json"
):
    """Save search results to a file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format_type == "json" or output_file.endswith('.json'):
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        # Save as human-readable text
        with open(output_path, 'w') as f:
            f.write(format_search_results(results, "human"))


async def execute_search(
    search_criteria: SearchCriteria, config, logger
) -> dict[str, Any]:
    """Execute the search operation using appropriate client."""

    # API-only implementation
    api_client = SignalHireClient(api_key=config.api_key)

    logger.info("Using API for search", has_api_key=bool(config.api_key))

    # Build API payload using documented keys
    search_dict = {
        "currentTitle": search_criteria.title,
        "location": search_criteria.location,
        "currentCompany": search_criteria.company,
        "industry": search_criteria.industry,
        "keywords": search_criteria.keywords,
        "fullName": search_criteria.name,
        "yearsOfCurrentExperienceFrom": search_criteria.experience_from,
        "yearsOfCurrentExperienceTo": search_criteria.experience_to,
        "openToWork": search_criteria.open_to_work,
    }
    search_dict = {k: v for k, v in search_dict.items() if v is not None}

    # Scroll pagination support
    state_dir = Path.home() / '.signalhire-agent'
    state_file = state_dir / 'last_search.json'

    if search_criteria.continue_search or search_criteria.scroll_id:
        # Load requestId/scrollId
        req_id = None
        scr_id = search_criteria.scroll_id
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())
                req_id = state.get('requestId')
                scr_id = scr_id or state.get('scrollId')
            except Exception:
                pass
        if not (req_id and scr_id):
            raise Exception(
                "Missing requestId/scrollId to continue search. Provide --scroll-id or start a new search."
            )
        api_response = await api_client.scroll_search(int(req_id), scr_id)
    else:
        api_response = await api_client.search_prospects(
            search_dict, size=search_criteria.size
        )

    if api_response.success:
        # Persist requestId/scrollId for continuation
        try:
            state_dir.mkdir(parents=True, exist_ok=True)
            data = api_response.data or {}
            persist = {
                'requestId': data.get('requestId') or data.get('request_id'),
                'scrollId': data.get('scrollId') or data.get('scroll_id'),
            }
            (state_file).write_text(json.dumps(persist, indent=2))
        except Exception:
            pass
        return api_response.data
    raise Exception(f"API search failed: {api_response.error}")


@click.command()
@click.option(
    '--title',
    help='Current job title (supports Boolean queries like "Senior AND (Python OR JavaScript)")',
)
@click.option('--location', help='Geographic location (city, state, country)')
@click.option('--company', help='Current company name (supports Boolean queries)')
@click.option('--industry', help='Industry category')
@click.option('--keywords', help='Skills and attributes (supports Boolean queries)')
@click.option('--name', help='Full name to search for')
@click.option('--experience-from', type=int, help='Minimum years of experience')
@click.option('--experience-to', type=int, help='Maximum years of experience')
@click.option('--open-to-work', is_flag=True, help='Filter for job seekers only')
@click.option(
    '--size',
    type=click.IntRange(1, 100),
    default=10,
    help='Results per page [default: 10] [range: 1-100]',
)
@click.option(
    '--output', type=click.Path(), help='Save results to file [default: stdout]'
)
@click.option(
    '--continue-search', is_flag=True, help='Continue previous search using pagination'
)
@click.option(
    '--scroll-id', help='Scroll ID for pagination (usually loaded automatically)'
)
@click.option(
    '--request-id',
    type=int,
    help='Optional: Request ID for scroll pagination (loaded automatically if omitted)',
)
@click.option(
    '--all-pages',
    is_flag=True,
    help='Fetch all pages using scroll pagination (up to --max-pages)',
)
@click.option(
    '--max-pages',
    type=click.IntRange(1, 1000),
    default=20,
    help='Maximum number of pages to fetch when using --all-pages [default: 20]',
)
@click.option(
    '--dry-run', is_flag=True, help='Show what would be searched without executing'
)
@click.pass_context
def search(
    ctx,
    title,
    location,
    company,
    industry,
    keywords,
    name,
    experience_from,
    experience_to,
    open_to_work,
    size,
    output,
    continue_search,
    scroll_id,
    request_id,
    dry_run,
    all_pages,
    max_pages,
):
    """
    Search SignalHire database for prospects (API-powered).

    🔍 Search for prospects using SignalHire's comprehensive database with advanced
    filtering options. Uses API for fast, reliable results with pagination support
    for large datasets. Perfect for targeted lead generation campaigns.

    \b
    EXAMPLES:
      # Basic search
      signalhire search --title "Software Engineer" --location "San Francisco"

      # Advanced Boolean search
      signalhire search --title "(Python OR JavaScript) AND Senior" --company "Google OR Microsoft"

      # Industry-specific search
      signalhire search --title "VP Engineering" --industry "Technology" --experience-from 10

      # Save results for later reveal
      signalhire search --title "Product Manager" --company "Startup" --output prospects.csv

      # Large paginated search
      signalhire search --title "Designer" --size 100 --continue-search

    \b
    BOOLEAN OPERATORS:
    Use AND, OR, NOT, and parentheses in title, company, and keywords fields:
    • "Python AND JavaScript"
    • "(Senior OR Lead) AND Engineer"
    • "NOT Intern"

    \b
    PAGINATION:
    Large searches are automatically paginated. Use --continue-search to get
    the next page of results from a previous search.
    """

    config = ctx.obj['config']
    logger = ctx.obj.get('logger')

    # Validate search criteria
    if (
        not any([title, location, company, industry, keywords, name])
        and not continue_search
    ):
        echo(
            style("Error: At least one search criterion is required.", fg='red'),
            err=True,
        )
        echo(
            "Use --title, --location, --company, --industry, --keywords, or --name",
            err=True,
        )
        ctx.exit(1)

    # API-only: require API key
    if not config.api_key:
        echo(style("Error: API key is required in API-only mode.", fg='red'), err=True)
        echo("Set SIGNALHIRE_API_KEY environment variable or pass --api-key", err=True)
        ctx.exit(1)

    # Build search criteria
    try:
        search_criteria = SearchCriteria(
            title=title,
            location=location,
            company=company,
            industry=industry,
            keywords=keywords,
            name=name,
            experience_from=experience_from,
            experience_to=experience_to,
            open_to_work=open_to_work,
            size=size,
            continue_search=continue_search,
            scroll_id=scroll_id,
        )
    except ValueError as e:
        echo(style(f"Error: Invalid search criteria: {e}", fg='red'), err=True)
        ctx.exit(1)

    # Dry run mode
    if dry_run:
        echo("🧪 Dry Run - Search criteria:")
        echo(f"  Title: {title or 'Not specified'}")
        echo(f"  Location: {location or 'Not specified'}")
        echo(f"  Company: {company or 'Not specified'}")
        echo(f"  Industry: {industry or 'Not specified'}")
        echo(f"  Keywords: {keywords or 'Not specified'}")
        echo(f"  Name: {name or 'Not specified'}")
        echo(
            f"  Experience: {experience_from or 'Any'} - {experience_to or 'Any'} years"
        )
        echo(f"  Open to work: {open_to_work}")
        echo(f"  Results per page: {size}")
        echo("  Mode: API")
        echo(f"  Continue search: {continue_search}")
        if scroll_id:
            echo(f"  Scroll ID: {scroll_id[:20]}...")

        echo("\n✅ Search criteria validated. Remove --dry-run to execute.")
        return

    # Load previous search state if continuing
    search_state_file = Path.home() / '.signalhire-agent' / 'last_search.json'

    if continue_search and search_state_file.exists():
        try:
            with open(search_state_file) as f:
                previous_state = json.load(f)
                if not scroll_id and previous_state.get('scroll_id'):
                    scroll_id = previous_state['scroll_id']
                    search_criteria.scroll_id = scroll_id
                    echo(
                        f"📄 Loaded scroll ID from previous search: {scroll_id[:20]}..."
                    )
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("Could not load previous search state", error=str(e))

    # Execute search
    echo("🔍 Searching for prospects...")

    if config.verbose:
        echo(f"Mode: {'Browser automation' if config.browser_mode else 'API'}")
        if config.debug:
            echo(f"Search criteria: {search_criteria.dict()}")

    try:
        # Run async search
        results = asyncio.run(execute_search(search_criteria, config, logger))

        # If requested, fetch all remaining pages via scroll
        if all_pages:
            req_id = results.get('requestId') or results.get('request_id')
            scr_id = results.get('scrollId') or results.get('scroll_id')
            profiles = list(results.get('profiles') or results.get('prospects') or [])

            if scr_id and req_id:

                async def _fetch_all():
                    client = SignalHireClient(api_key=config.api_key)
                    pages = 0
                    nonlocal scr_id
                    while scr_id and pages < max_pages:
                        resp = await client.scroll_search(int(req_id), scr_id)
                        if not resp.success:
                            break
                        data = resp.data or {}
                        new_profiles = (
                            data.get('profiles') or data.get('prospects') or []
                        )
                        profiles.extend(new_profiles)
                        scr_id = data.get('scrollId') or data.get('scroll_id')
                        pages += 1

                asyncio.run(_fetch_all())
                # Merge results
                results = dict(results)
                results['profiles'] = profiles
                results['total'] = (
                    results.get('total') or results.get('total_count') or len(profiles)
                )
                results.pop('prospects', None)
                results['scrollId'] = scr_id

        # Save search state for pagination
        if results.get('scroll_id') or results.get('scrollId'):
            search_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(search_state_file, 'w') as f:
                json.dump(
                    {
                        'scroll_id': results.get('scroll_id')
                        or results.get('scrollId'),
                        'request_id': results.get('request_id')
                        or results.get('requestId'),
                        'search_criteria': search_criteria.dict(),
                    },
                    f,
                )

        # Display results
        if config.output_format == 'json':
            result_output = json.dumps(results, indent=2)
        else:
            result_output = format_search_results(results, config.output_format)

        if output:
            save_search_results(results, output, config.output_format)
            echo(f"✅ Results saved to: {output}")

            if config.output_format != 'json':
                echo(result_output)
        else:
            echo(result_output)

        # Show pagination info
        total = results.get('total_count') or results.get('total') or 0
        batch = len(results.get('prospects', []) or results.get('profiles', []) or [])
        if results.get('scroll_id') or results.get('scrollId'):
            remaining = max(0, total - batch)
            echo(
                f"\n📄 {remaining} more prospects available. Use --continue-search to get next batch."
            )

        # Success metrics
        prospects_found = len(
            results.get('prospects', []) or results.get('profiles', []) or []
        )
        if prospects_found > 0:
            echo(f"\n✅ Found {prospects_found} prospects in this batch")
        else:
            echo("\n⚠️  No prospects found matching your criteria")

    except KeyboardInterrupt:
        echo("\n🛑 Search cancelled by user", err=True)
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
