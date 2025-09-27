import glob
import os

import click

from ..services.deduplication_service import (
    create_backup_files,
    deduplicate_contacts,
    load_contacts_from_files,
    save_contacts_to_file,
)


@click.group()
def dedupe():
    """Deduplication operations for SignalHire contacts."""


@dedupe.command()
@click.option(
    '--input',
    required=True,
    help='Input JSON file(s) or directory (comma-separated or dir)',
)
@click.option('--output', required=True, help='Output deduplicated JSON file')
@click.option('--no-backup', is_flag=True, help='Skip creating backup files')
def merge(input, output, no_backup):
    """Merge and deduplicate contacts from multiple JSON files."""
    # Support comma-separated files or directory
    input_files = []
    if os.path.isdir(input):
        input_files = glob.glob(os.path.join(input, '*.json'))
    else:
        input_files = [f.strip() for f in input.split(',') if f.strip()]
    if not input_files:
        click.echo("No input files found.")
        return

    # Create backups unless disabled
    if not no_backup:
        backup_paths = create_backup_files(input_files)
        if backup_paths:
            click.echo(f"Created {len(backup_paths)} backup files.")

    contacts = load_contacts_from_files(input_files)
    if not contacts:
        click.echo("No contacts found in input files.")
        return

    deduped = deduplicate_contacts(contacts)
    save_contacts_to_file(deduped, output)
    duplicates_removed = len(contacts) - len(deduped)
    click.echo(
        f"Deduplicated {len(contacts)} contacts to {len(deduped)} unique contacts ({duplicates_removed} duplicates removed). Output: {output}"
    )
