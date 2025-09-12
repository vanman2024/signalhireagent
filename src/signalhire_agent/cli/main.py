from __future__ import annotations

import os

import click
from dotenv import load_dotenv

from .. import __version__

load_dotenv()  # Load variables from .env if present


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="signalhire-agent")
def cli() -> None:
    """SignalHire Agent CLI."""


@cli.command()
def doctor() -> None:
    """Check environment and print status."""
    email = os.getenv("SIGNALHIRE_EMAIL")
    password = os.getenv("SIGNALHIRE_PASSWORD")

    click.echo("Environment check:")
    click.echo(f"- SIGNALHIRE_EMAIL: {'set' if email else 'missing'}")
    click.echo(f"- SIGNALHIRE_PASSWORD: {'set' if password else 'missing'}")


def main() -> None:
    cli(prog_name="signalhire-agent")


if __name__ == "__main__":  # pragma: no cover
    main()

