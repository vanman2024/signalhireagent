import click

from ..services.filter_service import (
    filter_contacts_by_job_title,
    load_contacts_from_file,
    save_contacts_to_file,
)


@click.group()
def filter():
    """Filter contacts by job title, company, or other criteria."""


@filter.command()
@click.option('--input', required=True, help='Input JSON file')
@click.option('--output', required=True, help='Output filtered JSON file')
@click.option(
    '--exclude-job-titles', help='Comma-separated list of job titles to exclude'
)
def job_title(input, output, exclude_job_titles):
    """Filter contacts by job title."""
    if not exclude_job_titles:
        click.echo("No job titles to exclude specified.")
        return
    exclude_list = [title.strip() for title in exclude_job_titles.split(',')]
    contacts = load_contacts_from_file(input)
    filtered = filter_contacts_by_job_title(contacts, exclude_list)
    save_contacts_to_file(filtered, output)
    click.echo(
        f"Filtered {len(contacts)} contacts to {len(filtered)} contacts. Output: {output}"
    )
