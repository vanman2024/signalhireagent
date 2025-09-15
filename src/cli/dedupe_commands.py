import os
import glob
import click
from src.services.deduplication_service import load_contacts_from_files, deduplicate_contacts, save_contacts_to_file

@click.group()
def dedupe():
    """Deduplication operations for SignalHire contacts."""
    pass

@dedupe.command()
@click.option('--input', required=True, help='Input JSON file(s) or directory (comma-separated or dir)')
@click.option('--output', required=True, help='Output deduplicated JSON file')
def merge(input, output):
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
    contacts = load_contacts_from_files(input_files)
    deduped = deduplicate_contacts(contacts)
    save_contacts_to_file(deduped, output)
    click.echo(f"Deduplicated {len(contacts)} contacts to {len(deduped)} unique contacts. Output: {output}")
