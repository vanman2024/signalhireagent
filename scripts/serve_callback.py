#!/usr/bin/env python3
"""Entry point to run the SignalHire callback server in production.

The script wires up the FastAPI callback server with the Airtable handler so
that every webhook received from SignalHire is processed immediately. It is
meant to be deployed on a long-lived compute target (e.g. DigitalOcean App
Platform or Droplet) and kept running under a process supervisor.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from typing import NoReturn

from dotenv import load_dotenv

from src.lib.callback_server import get_server
from src.services.airtable_callback_handler import register_airtable_handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the SignalHire webhook callback server"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Interface to bind the FastAPI server on [default: 0.0.0.0]",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on for SignalHire callbacks [default: 8000]",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR) [default: INFO]",
    )
    return parser.parse_args()


def run_server(host: str, port: int) -> NoReturn:
    """Start the callback server and block until interrupted."""
    server = get_server(host=host, port=port)
    register_airtable_handler(server)

    # Ensure the FastAPI application is instantiated before starting uvicorn
    if server.app is None:
        server.create_app()

    logging.info("Starting SignalHire callback server", extra={"host": host, "port": port})
    server.start(background=False)


def main() -> None:
    args = parse_args()

    load_dotenv()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    # Allow graceful shutdown with Ctrl+C or SIGTERM
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: sys.exit(0))

    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
