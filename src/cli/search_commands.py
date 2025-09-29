"""
Search command implementation for SignalHire Agent CLI

This module provides the search command functionality, allowing users to
search for prospects using various criteria and filters.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import httpx
from click import echo, style

from ..lib.contact_cache import ContactCache
from ..models.search_criteria import SearchCriteria
from ..services.search_analysis_service import create_heavy_equipment_search_templates
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
    cached_count = results.get('cached_contacts_count', 0)
    skipped_cached = results.get('skipped_revealed_count', 0)

    output = []
    output.append("🔍 Search Results")
    output.append(f"Request ID: {style(str(request_id), fg='blue')}")
    output.append(
        f"Total prospects found: {style(str(total_count), fg='green', bold=True)}"
    )
    output.append(f"Current batch: {current_batch} prospects")

    if cached_count:
        output.append(
            f"Cached contacts available: {style(str(cached_count), fg='cyan')}"
        )
    if skipped_cached:
        output.append(
            f"Skipped (already revealed & cached): {style(str(skipped_cached), fg='yellow')}"
        )

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


def _show_search_templates() -> None:
    """Display available Boolean search templates for quick search setup."""
    templates = create_heavy_equipment_search_templates()

    echo("\n🔍 Heavy Equipment Mechanic Search Templates")
    echo(
        "Use these with: signalhire search --title \"[TITLE]\" "
        '--keywords "[KEYWORDS]"'
    )

    for name, template in templates.items():
        echo(f"\n📋 {name.replace('_', ' ').title()}:")
        echo(f"  Title: {template['title']}")
        echo(f"  Keywords: {template['keywords']}")
        echo(f"  Description: {template['description']}")
        echo(
            "  Command: signalhire search --title "
            f'"{template["title"]}" --keywords "{template["keywords"]}"'
        )

    echo("\n💡 Pro Tips:")
    echo("  • Use AND NOT to exclude operators and drivers")
    echo("  • Combine equipment brands (CAT, Komatsu, John Deere)")
    echo("  • Focus on repair/maintenance skills vs operations")


async def _get_airtable_schema(client: httpx.AsyncClient, api_key: str, base_id: str, table_id: str) -> set:
    """Get the available field names from Airtable table schema."""
    try:
        # Get a single record to see what fields exist
        url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"maxRecords": 1}
        
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        records = data.get('records', [])
        
        if records:
            # Get field names from the first record
            return set(records[0].get('fields', {}).keys())
        else:
            # If no records exist, return common field names
            return {'Full Name', 'SignalHire ID', 'Status', 'Job Title', 'Company', 'Location'}
            
    except Exception as e:
        echo(f"   ⚠️  Could not fetch schema, using default fields: {e}")
        return {'Full Name', 'SignalHire ID', 'Status'}


async def _handle_airtable_integration(results: dict[str, Any], config, check_duplicates: bool, ctx):
    """Handle adding search results to Airtable with deduplication."""
    echo(f"\n📋 Adding search results to Airtable...")
    
    # Get environment variables
    airtable_api_key = os.getenv('AIRTABLE_API_KEY')
    airtable_base_id = os.getenv('AIRTABLE_BASE_ID', 'appQoYINM992nBZ50')
    airtable_table_id = os.getenv('AIRTABLE_TABLE_ID', 'tbl0uFVaAfcNjT2rS')
    
    if not airtable_api_key:
        echo(style("Error: AIRTABLE_API_KEY environment variable required", fg='red'), err=True)
        ctx.exit(1)
    
    # Extract prospects from results
    profile_key = 'profiles' if results.get('profiles') else 'prospects'
    prospects = results.get(profile_key, [])
    
    if not prospects:
        echo("ℹ️  No prospects to add to Airtable")
        return
    
    successful_adds = 0
    duplicates_skipped = 0
    failures = 0
    
    async with httpx.AsyncClient() as client:
        # Get table schema first to avoid validation errors
        echo(f"   🔍 Detecting Airtable schema...")
        available_fields = await _get_airtable_schema(client, airtable_api_key, airtable_base_id, airtable_table_id)
        echo(f"   📋 Available fields: {sorted(available_fields)}")
        
        for prospect in prospects:
            try:
                # Extract SignalHire ID
                signalhire_id = prospect.get('uid') or prospect.get('id')
                if not signalhire_id:
                    echo(f"   ⚠️  Skipping prospect - no SignalHire ID")
                    failures += 1
                    continue
                
                # Check for duplicates if requested
                if check_duplicates:
                    existing = await _check_airtable_duplicate(
                        client, airtable_api_key, airtable_base_id, airtable_table_id, signalhire_id
                    )
                    if existing:
                        echo(f"   🔄 Skipping duplicate: {prospect.get('full_name', signalhire_id)}")
                        duplicates_skipped += 1
                        continue
                
                # Format prospect data for Airtable with schema validation
                airtable_fields = _format_prospect_for_airtable(prospect, available_fields)
                
                # Add to Airtable with Status=New
                await _add_prospect_to_airtable(
                    client, airtable_api_key, airtable_base_id, airtable_table_id, airtable_fields
                )
                
                successful_adds += 1
                echo(f"   ✅ Added: {airtable_fields.get('Full Name', signalhire_id)}")
                
            except Exception as e:
                failures += 1
                echo(f"   ❌ Failed to add prospect: {e}")
    
    echo(f"\n📊 Airtable Results:")
    echo(f"   ✅ Successfully added: {successful_adds}")
    if check_duplicates:
        echo(f"   🔄 Duplicates skipped: {duplicates_skipped}")
    echo(f"   ❌ Failed: {failures}")


async def _check_airtable_duplicate(client: httpx.AsyncClient, api_key: str, base_id: str, 
                                   table_id: str, signalhire_id: str) -> bool:
    """Check if a contact already exists in Airtable by SignalHire ID."""
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    params = {
        "filterByFormula": f"{{SignalHire ID}} = '{signalhire_id}'",
        "maxRecords": 1
    }
    
    response = await client.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return len(data.get('records', [])) > 0


def _format_prospect_for_airtable(prospect: dict[str, Any], available_fields: set = None) -> dict:
    """Format a search prospect for Airtable insertion with schema validation."""
    # Extract basic info - handle different API response formats
    name = prospect.get('full_name') or prospect.get('fullName') or 'Unknown'
    title = prospect.get('current_title') or prospect.get('currentTitle') or prospect.get('title')
    company = prospect.get('current_company') or prospect.get('currentCompany') or prospect.get('company')
    location = prospect.get('location', 'Unknown Location')
    
    # Fallback: derive title/company from experience if missing
    if (not title or not company) and isinstance(prospect.get('experience'), list) and prospect['experience']:
        exp0 = prospect['experience'][0]
        title = title or exp0.get('title')
        company = company or exp0.get('company')
    
    # SignalHire ID
    signalhire_id = prospect.get('uid') or prospect.get('id')
    
    # Build complete field mapping
    all_fields = {
        "Full Name": name,
        "SignalHire ID": signalhire_id,
        "Status": "New",
        "Job Title": title,
        "Company": company,
        "Location": location
    }
    
    # Filter based on available schema if provided
    if available_fields:
        # Only include fields that exist in the Airtable schema
        fields = {}
        for field_name, value in all_fields.items():
            if field_name in available_fields and value:
                fields[field_name] = value
        
        # Ensure we always have the minimum required fields
        if "Full Name" in available_fields:
            fields["Full Name"] = name
        if "SignalHire ID" in available_fields:
            fields["SignalHire ID"] = signalhire_id
        if "Status" in available_fields:
            fields["Status"] = "New"
    else:
        # Fallback to old behavior - minimal fields with values
        fields = {
            "Full Name": name,
            "SignalHire ID": signalhire_id,
            "Status": "New"
        }
        
        # Add optional fields only if they have values
        if title:
            fields["Job Title"] = title
        if company:
            fields["Company"] = company
        if location and location != 'Unknown Location':
            fields["Location"] = location
    
    return fields


async def _add_prospect_to_airtable(client: httpx.AsyncClient, api_key: str, base_id: str,
                                   table_id: str, fields: dict):
    """Add a new prospect to Airtable."""
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {"fields": fields}
    response = await client.post(url, headers=headers, json=payload)
    response.raise_for_status()


async def execute_search(
    search_criteria: SearchCriteria, config, logger, exclude_revealed: bool = False
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
    
    # Add contactsFetched filter when excluding already-revealed prospects
    if exclude_revealed:
        search_dict["contactsFetched"] = False
    
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
    '--skip-revealed/--include-revealed',
    default=False,
    help='Skip prospects whose contacts are already cached locally',
)
@click.option(
    '--exclude-revealed',
    is_flag=True,
    help='Exclude already-revealed prospects from SignalHire API search (preserves search quota)',
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
@click.option(
    '--to-airtable', is_flag=True, help='Add search results directly to Airtable with Status=New'
)
@click.option(
    '--check-duplicates', is_flag=True, help='Check Airtable for existing contacts before adding'
)
@click.argument('preset', required=False)
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
    skip_revealed,
    exclude_revealed,
    continue_search,
    scroll_id,
    request_id,
    dry_run,
    all_pages,
    max_pages,
    to_airtable,
    check_duplicates,
    preset,
):
    """
    Search SignalHire database for prospects (API-powered).

    🔍 Search for prospects using SignalHire's comprehensive database with advanced
    filtering options. Uses API for fast, reliable results with pagination support
    for large datasets. Perfect for targeted lead generation campaigns.

    \b
    EXAMPLES:
      # 🔧 HEAVY EQUIPMENT TECHNICIANS (Recommended workflow)
      signalhire-agent search --title "(Heavy Equipment Technician) OR (Heavy Equipment Mechanic)" --keywords "(technician OR mechanic OR maintenance OR repair) NOT (operator OR driver OR supervisor)" --location "Canada" --size 10 --to-airtable --check-duplicates

      # Basic search
      signalhire-agent search --title "Software Engineer" --location "San Francisco"

      # Advanced Boolean search with Airtable
      signalhire-agent search --title "(Python OR JavaScript) AND Senior" --company "Google OR Microsoft" --to-airtable

      # Show built-in Boolean templates
      signalhire-agent search templates

      # Continue previous search
      signalhire-agent search --continue-search

      # Large paginated search without duplicates
      signalhire-agent search --title "Designer" --size 100 --check-duplicates --to-airtable

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

    if preset:
        normalized = preset.replace('-', '_').lower()
        if normalized in {'template', 'templates'}:
            _show_search_templates()
            ctx.exit(0)
        raise click.UsageError(
            f"Unexpected argument '{preset}'. Did you mean 'signalhire search templates'?"
        )

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
        echo(f"  Exclude revealed: {exclude_revealed}")
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
        results = asyncio.run(execute_search(search_criteria, config, logger, exclude_revealed))

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

        # Merge cached contacts and optionally skip already revealed prospects
        contact_cache = ContactCache()
        cached_contacts = 0
        skipped_cached = 0
        cached_uids: list[str] = []

        profile_key = None
        if isinstance(results.get('profiles'), list):
            profile_key = 'profiles'
        elif isinstance(results.get('prospects'), list):
            profile_key = 'prospects'

        original_profiles = results.get(profile_key, []) if profile_key else []
        filtered_profiles = []

        for profile in original_profiles:
            if not isinstance(profile, dict):
                filtered_profiles.append(profile)
                continue

            uid = profile.get('uid') or profile.get('id')
            cached_entry = contact_cache.get(uid) if uid else None

            if uid:
                # Persist latest profile metadata for future reveals/cache usage
                contact_cache.upsert(uid, profile=profile)

            if cached_entry and cached_entry.contacts:
                profile['contacts'] = cached_entry.contacts
                profile['contact_source'] = 'cache'
                cached_contacts += 1
                cached_uids.append(uid)

                if cached_entry.profile:
                    profile.setdefault(
                        'full_name',
                        cached_entry.profile.get('full_name')
                        or cached_entry.profile.get('fullName'),
                    )

            if cached_entry and cached_entry.contacts and skip_revealed:
                skipped_cached += 1
                continue

            filtered_profiles.append(profile)

        if profile_key:
            results[profile_key] = filtered_profiles

        results['cached_contacts_count'] = cached_contacts
        results['skipped_revealed_count'] = skipped_cached
        results['returned_count'] = len(filtered_profiles)
        if cached_uids:
            results['cached_uids'] = cached_uids

        contact_cache.save()

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

        # Handle Airtable integration
        if to_airtable:
            asyncio.run(_handle_airtable_integration(
                results, config, check_duplicates, ctx
            ))

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
