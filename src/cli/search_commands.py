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

# ContactCache removed - using Airtable as source of truth
from ..models.search_criteria import SearchCriteria
from ..services.airtable_client import AirtableClientError, AirtableContactIndex
from ..services.search_analysis_service import create_heavy_equipment_search_templates
from ..services.signalhire_client import SignalHireClient
from .reveal_commands import handle_api_error

# Import validation utilities
from ..lib.validation import (
    ValidationResult,
    ValidatorChain,
    validate_string_length,
    validate_integer_range,
    validate_email,
    validate_phone,
    validate_signalhire_uid,
)


def validate_boolean_query(query: str | None, field_name: str = "Query") -> ValidationResult:
    """
    Validate Boolean search query syntax.

    Args:
        query: The query string to validate
        field_name: Name of the field for error messages

    Returns:
        ValidationResult with validation status and cleaned query
    """
    if not query:
        return ValidationResult(True, cleaned_value=query)  # Optional field

    # Check for balanced parentheses
    open_parens = query.count('(')
    close_parens = query.count(')')

    if open_parens != close_parens:
        return ValidationResult(
            False,
            f"{field_name} has unbalanced parentheses: {open_parens} opening, {close_parens} closing"
        )

    # Check for valid Boolean operators
    valid_operators = ['AND', 'OR', 'NOT']
    words = query.split()

    # Check for adjacent operators
    for i in range(len(words) - 1):
        if words[i] in valid_operators and words[i+1] in valid_operators:
            return ValidationResult(
                False,
                f"{field_name} has adjacent Boolean operators: {words[i]} {words[i+1]}"
            )

    # Check for operators at start/end (except NOT at start)
    if words and words[0] in ['AND', 'OR']:
        return ValidationResult(
            False,
            f"{field_name} cannot start with {words[0]} operator"
        )

    if words and words[-1] in valid_operators:
        return ValidationResult(
            False,
            f"{field_name} cannot end with {words[-1]} operator"
        )

    return ValidationResult(True, cleaned_value=query)


def validate_search_parameters(
    title: str | None,
    keywords: str | None,
    company: str | None,
    location: str | None,
    size: int
) -> tuple[bool, list[str]]:
    """
    Validate all search parameters using the validation system.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate Boolean queries
    for field_name, value in [
        ("Title", title),
        ("Keywords", keywords),
        ("Company", company)
    ]:
        result = validate_boolean_query(value, field_name)
        if not result.is_valid:
            errors.append(result.error_message)

    # Validate location length if provided
    if location:
        result = validate_string_length(location, min_length=2, max_length=100, field_name="Location")
        if not result.is_valid:
            errors.append(result.error_message)

    # Validate size range
    result = validate_integer_range(size, min_value=1, max_value=100, field_name="Size")
    if not result.is_valid:
        errors.append(result.error_message)

    return len(errors) == 0, errors


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
    airtable_existing = results.get('airtable_existing_contacts', 0)
    skipped_existing = results.get('skipped_existing_contacts', 0)

    output = []
    output.append("🔍 Search Results")
    output.append(f"Request ID: {style(str(request_id), fg='blue')}")
    output.append(
        f"Total prospects found: {style(str(total_count), fg='green', bold=True)}"
    )
    output.append(f"Current batch: {current_batch} prospects")

    if airtable_existing:
        output.append(
            f"Existing contacts in Airtable: {style(str(airtable_existing), fg='cyan')}"
        )
    if skipped_existing:
        output.append(
            f"Skipped (already revealed in Airtable): {style(str(skipped_existing), fg='yellow')}"
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
    echo("📋 Complete workflow with Airtable integration")

    # Show primary recommended template first
    primary_template = templates.get('diesel_technician_focused', {})
    echo(f"\n🎯 RECOMMENDED: Heavy Equipment Technician (Complete Workflow)")
    echo(f"  Title: {primary_template.get('title', '')}")
    echo(f"  Keywords: {primary_template.get('keywords', '')}")
    echo(f"  Description: {primary_template.get('description', '')}")
    echo(style("\n  ✅ Full Command (Copy & Paste):", fg='green', bold=True))
    echo(
        f'  signalhire-agent search --title "{primary_template.get("title", "")}" '
        f'--keywords "{primary_template.get("keywords", "")}" '
        f'--location "Canada" --size 100 --to-airtable --check-duplicates'
    )

    # Show other templates
    echo("\n📚 Other Available Templates:")
    for name, template in templates.items():
        if name != 'diesel_technician_focused':  # Skip the primary one we already showed
            echo(f"\n📋 {name.replace('_', ' ').title()}:")
            echo(f"  Title: {template['title']}")
            echo(f"  Keywords: {template['keywords']}")
            echo(f"  Description: {template['description']}")
            echo(
                f'  Command: signalhire-agent search --title "{template["title"]}" '
                f'--keywords "{template["keywords"]}" --location "Canada" '
                f'--size 100 --to-airtable --check-duplicates'
            )

    echo("\n🚀 Complete Workflow Steps:")
    echo("  1. Search: Use template above with --to-airtable --check-duplicates")
    echo("  2. Reveal: signalhire-agent airtable sync-direct --max-contacts 100")
    echo("  3. Monitor: signalhire-agent status --credits")

    echo("\n💡 Pro Tips:")
    echo("  • Always use --to-airtable --check-duplicates for consistency")
    echo("  • Set --size 100 for larger result sets")
    echo("  • Add --location 'Canada' for regional targeting")
    echo("  • Monitor credits with status command (1200 available)")


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
                
                # Validate prospect data
                is_valid, warnings = validate_prospect_data(prospect)
                if warnings:
                    name = prospect.get('full_name') or prospect.get('fullName', 'Unknown')
                    echo(f"   ⚠️  Data quality issues for {name}:")
                    for warning in warnings:
                        echo(f"      • {warning}")

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


def _parse_location(location: str) -> tuple[str, str, str]:
    """Parse location string into city, province/state, and country components."""
    if not location or location == 'Unknown Location':
        return '', '', ''
    
    # Common location formats from SignalHire:
    # "City, Province, Country"
    # "City, State, Country" 
    # "City, Country"
    # "Province, Country"
    # "Country"
    
    parts = [part.strip() for part in location.split(',')]
    
    if len(parts) >= 3:
        # "City, Province/State, Country"
        city = parts[0]
        province_state = parts[1]
        country = parts[2]
    elif len(parts) == 2:
        # "City, Country" or "Province/State, Country"
        # Check if first part looks like a known province/state or city
        part1, part2 = parts[0], parts[1]
        
        # Known Canadian provinces and US states for better parsing
        provinces_states = {
            'ontario', 'quebec', 'british columbia', 'alberta', 'manitoba', 'saskatchewan',
            'nova scotia', 'new brunswick', 'newfoundland and labrador', 'prince edward island',
            'northwest territories', 'nunavut', 'yukon',
            'california', 'texas', 'florida', 'new york', 'pennsylvania', 'illinois', 'ohio',
            'georgia', 'north carolina', 'michigan', 'new jersey', 'virginia', 'washington',
            'arizona', 'massachusetts', 'tennessee', 'indiana', 'maryland', 'missouri',
            'wisconsin', 'colorado', 'minnesota', 'south carolina', 'alabama', 'louisiana'
        }
        
        if part1.lower() in provinces_states:
            # "Province/State, Country"
            city = ''
            province_state = part1
            country = part2
        else:
            # "City, Country"
            city = part1
            province_state = ''
            country = part2
    elif len(parts) == 1:
        # Just "Country" or a single location
        city = ''
        province_state = ''
        country = parts[0]
    else:
        city = ''
        province_state = ''
        country = ''
    
    return city, province_state, country


def validate_prospect_data(prospect: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate prospect data before adding to Airtable.

    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []

    # Validate SignalHire ID if present
    signalhire_id = prospect.get('uid') or prospect.get('id')
    if signalhire_id:
        result = validate_signalhire_uid(signalhire_id)
        if not result.is_valid:
            warnings.append(f"Invalid SignalHire ID format: {signalhire_id[:8]}...")

    # Validate email if present
    email = prospect.get('email')
    if email:
        result = validate_email(email)
        if not result.is_valid:
            warnings.append(f"Invalid email format: {email}")

    # Validate phones if present
    phones = prospect.get('phones', [])
    if isinstance(phones, list):
        for phone in phones[:3]:  # Check first 3 phones
            if isinstance(phone, str):
                result = validate_phone(phone)
                if not result.is_valid:
                    warnings.append(f"Invalid phone format: {phone}")

    # Check for required fields
    if not prospect.get('full_name') and not prospect.get('fullName'):
        warnings.append("Missing full name")

    return len(warnings) == 0, warnings


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
    
    # Parse location into separate components
    city, province_state, country = _parse_location(location)
    
    # Build complete field mapping
    all_fields = {
        "Full Name": name,
        "SignalHire ID": signalhire_id,
        "Status": "New",
        "Job Title": title,
        "Company": company,
        "Location": location,  # Keep original for fallback
        "City": city,
        "Province/State": province_state,
        "Country": country
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
    help='Skip prospects that already have contact info in Airtable',
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

    # Validate search parameters using validation system
    is_valid, validation_errors = validate_search_parameters(
        title, keywords, company, location, size
    )

    if not is_valid:
        echo(style("❌ Search Validation Failed:", fg='red', bold=True), err=True)
        for error in validation_errors:
            echo(style(f"  • {error}", fg='red'), err=True)
        echo("\n💡 Tips for Boolean queries:", err=True)
        echo("  • Use AND, OR, NOT operators in UPPERCASE", err=True)
        echo("  • Balance your parentheses", err=True)
        echo("  • Don't end queries with operators", err=True)
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

        # Process profiles for display with Airtable context
        profile_key = None
        if isinstance(results.get('profiles'), list):
            profile_key = 'profiles'
        elif isinstance(results.get('prospects'), list):
            profile_key = 'prospects'

        original_profiles = results.get(profile_key, []) if profile_key else []
        filtered_profiles: list[dict[str, Any]] = []

        airtable_index = None
        existing_contacts = 0
        skipped_existing = 0
        try:
            index_candidate = AirtableContactIndex.build_sync()
            if index_candidate.ready:
                airtable_index = index_candidate
            elif skip_revealed:
                echo(style('⚠️  AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set; cannot skip already revealed contacts.', fg='yellow'))
        except AirtableClientError as airtable_error:
            if skip_revealed:
                echo(style(f'⚠️  Airtable lookup failed: {airtable_error}', fg='yellow'))

        for profile in original_profiles:
            if not isinstance(profile, dict):
                filtered_profiles.append(profile)
                continue

            uid = profile.get('uid') or profile.get('id')
            airtable_entry = airtable_index.entry_for(uid) if airtable_index and uid else None
            if airtable_entry:
                profile['airtable_status'] = airtable_entry.status
                profile['airtable_has_contact'] = airtable_entry.has_contact_info
                if airtable_entry.has_contact_info:
                    existing_contacts += 1
                    if skip_revealed:
                        skipped_existing += 1
                        continue

            filtered_profiles.append(profile)

        if profile_key:
            results[profile_key] = filtered_profiles

        results['returned_count'] = len(filtered_profiles)
        if airtable_index:
            results['airtable_existing_contacts'] = existing_contacts
            results['skipped_existing_contacts'] = skipped_existing

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
