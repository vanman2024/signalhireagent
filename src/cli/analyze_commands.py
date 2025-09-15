from collections import Counter

import click

from src.services.filter_service import load_contacts_from_file
from src.services.search_analysis_service import (
    analyze_geographic_coverage,
    create_heavy_equipment_search_templates,
    identify_search_overlap,
)


@click.group()
def analyze():
    """Analyze contact quality and job title distribution."""

@analyze.command()
@click.option('--input', required=True, help='Input JSON file')
def job_titles(input):
    """Analyze job title distribution in contacts."""
    try:
        contacts = load_contacts_from_file(input)

        # Extract job titles
        job_titles = []
        for contact in contacts:
            title = contact.get('job_title', '').strip()
            if title:
                job_titles.append(title.lower())

        if not job_titles:
            click.echo("No job titles found in contacts.")
            return

        # Analyze distribution
        title_counts = Counter(job_titles)
        total_contacts = len(contacts)
        total_with_titles = len(job_titles)

        click.echo(f"\n📊 Job Title Analysis for {input}")
        click.echo(f"Total contacts: {total_contacts}")
        click.echo(f"Contacts with job titles: {total_with_titles} ({total_with_titles/total_contacts*100:.1f}%)")

        click.echo("\n🏆 Top Job Titles:")
        for title, count in title_counts.most_common(10):
            percentage = count / total_with_titles * 100
            click.echo(f"  {title}: {count} ({percentage:.1f}%)")

        # Quality metrics
        unique_titles = len(title_counts)
        click.echo("\n📈 Quality Metrics:")
        click.echo(f"Unique job titles: {unique_titles}")
        click.echo(f"Average contacts per title: {total_with_titles/unique_titles:.1f}")

        # Identify potential low-quality titles
        low_quality_keywords = ['operator', 'driver', 'foreman', 'laborer', 'helper']
        low_quality_count = sum(count for title, count in title_counts.items()
                               if any(keyword in title for keyword in low_quality_keywords))

        if low_quality_count > 0:
            click.echo("\n⚠️  Potential Low-Quality Contacts:")
            click.echo(f"Contacts with operator/driver/foreman titles: {low_quality_count} ({low_quality_count/total_with_titles*100:.1f}%)")
            click.echo("Consider filtering these before reveal to save credits.")

    except Exception as e:
        click.echo(f"Error analyzing job titles: {e}", err=True)

@analyze.command()
@click.option('--input', required=True, help='Input JSON file')
def geography(input):
    """Analyze geographic coverage and suggest areas for additional searches."""
    try:
        contacts = load_contacts_from_file(input)
        analysis = analyze_geographic_coverage(contacts)

        click.echo(f"\n🌍 Geographic Coverage Analysis for {input}")
        click.echo(f"Total unique locations: {analysis['total_locations']}")
        click.echo(f"Geographic diversity score: {analysis['geographic_diversity_score']:.1f}%")

        if analysis['top_states']:
            click.echo("\n🏛️ Top States/Regions:")
            for state, count in analysis['top_states'].items():
                click.echo(f"  {state}: {count} contacts")

        if analysis['top_cities']:
            click.echo("\n🏙️ Top Cities:")
            for city, count in list(analysis['top_cities'].items())[:5]:
                click.echo(f"  {city}: {count} contacts")

        if analysis['suggestions']:
            click.echo("\n💡 Optimization Suggestions:")
            for suggestion in analysis['suggestions']:
                click.echo(f"  • {suggestion}")

    except Exception as e:
        click.echo(f"Error analyzing geography: {e}", err=True)

@analyze.command()
@click.option('--files', required=True, help='Comma-separated list of JSON files to compare')
def overlap(files):
    """Identify search overlap between multiple contact files."""
    try:
        file_list = [f.strip() for f in files.split(',')]
        contact_sets = []

        for file_path in file_list:
            contacts = load_contacts_from_file(file_path)
            contact_sets.append(contacts)

        analysis = identify_search_overlap(contact_sets, file_list)

        if "error" in analysis:
            click.echo(f"Error: {analysis['error']}")
            return

        click.echo("\n🔄 Search Overlap Analysis")
        click.echo(f"Comparing {len(file_list)} contact sets:")
        for i, (name, size) in enumerate(zip(analysis['set_names'], analysis['set_sizes'], strict=False)):
            click.echo(f"  {i+1}. {name}: {size} contacts")

        if analysis['uid_overlaps']:
            click.echo("\n📊 Contact Overlaps:")
            for pair, overlap in analysis['uid_overlaps'].items():
                click.echo(f"  {pair}: {overlap} overlapping contacts")

        if analysis['recommendations']:
            click.echo("\n💡 Optimization Recommendations:")
            for rec in analysis['recommendations']:
                click.echo(f"  • {rec}")

    except Exception as e:
        click.echo(f"Error analyzing overlap: {e}", err=True)

@analyze.command()
def search_templates():
    """Show Boolean search templates for Heavy Equipment Mechanics."""
    templates = create_heavy_equipment_search_templates()

    click.echo("\n🔍 Heavy Equipment Mechanic Search Templates")
    click.echo("Use these with: signalhire search --title \"[TITLE]\" --keywords \"[KEYWORDS]\"")

    for name, template in templates.items():
        click.echo(f"\n📋 {name.replace('_', ' ').title()}:")
        click.echo(f"  Title: {template['title']}")
        click.echo(f"  Keywords: {template['keywords']}")
        click.echo(f"  Description: {template['description']}")
        click.echo(f"  Command: signalhire search --title \"{template['title']}\" --keywords \"{template['keywords']}\"")

    click.echo("\n💡 Pro Tips:")
    click.echo("  • Use AND NOT to exclude operators and drivers")
    click.echo("  • Combine equipment brands (CAT, Komatsu, John Deere)")
    click.echo("  • Focus on repair/maintenance skills vs operations")
