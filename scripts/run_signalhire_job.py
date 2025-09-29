#!/usr/bin/env python3
"""Automation runner for SignalHire → Airtable workflow.

This script performs a focused search against the SignalHire API, queues
reveal requests for the resulting prospect UIDs, and leaves webhook-based
processing to the existing callback server + Airtable handler.

Example
-------
python scripts/run_signalhire_job.py \
    --title "Diesel Mechanic" \
    --location "Calgary, AB" \
    --size 50 \
    --max-prospects 40 \
    --output-dir automation_runs
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.lib.callback_server import CallbackServer, start_server
from src.services.airtable_callback_handler import (
    get_handler_stats,
    register_airtable_handler,
)
from src.services.signalhire_client import APIResponse, SignalHireAPIError, SignalHireClient


def _configure_logging(level: str) -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate SignalHire search + reveal flow")

    search_group = parser.add_argument_group("search criteria")
    search_group.add_argument("--title", help="Job title / role to target")
    search_group.add_argument("--location", help="Geographic filter (city, state, country)")
    search_group.add_argument("--company", help="Company filter (supports Boolean queries)")
    search_group.add_argument("--industry", help="Industry filter")
    search_group.add_argument("--keywords", help="Keyword or Boolean expression")
    search_group.add_argument("--name", help="Full name search")
    search_group.add_argument(
        "--size",
        type=int,
        default=25,
        help="Number of prospects to request from the API [default: 25]",
    )
    search_group.add_argument(
        "--exclude-revealed",
        dest="exclude_revealed",
        action="store_true",
        help="Ask SignalHire to skip already revealed contacts (contactsFetched=false)",
    )
    search_group.add_argument(
        "--include-revealed",
        dest="exclude_revealed",
        action="store_false",
        help="Allow already revealed contacts back into the search results",
    )
    parser.set_defaults(exclude_revealed=True)

    reveal_group = parser.add_argument_group("reveal options")
    reveal_group.add_argument(
        "--max-prospects",
        type=int,
        default=0,
        help="Limit how many of the found prospects to queue for reveal (0 = all)",
    )
    reveal_group.add_argument(
        "--chunk-size",
        type=int,
        default=75,
        help="Maximum number of prospects to send per API batch (<=100) [default: 75]",
    )
    reveal_group.add_argument(
        "--reveal-batch-size",
        type=int,
        default=10,
        help="Concurrent reveals within each batch [default: 10]",
    )
    reveal_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the search and print stats without issuing reveal requests",
    )

    output_group = parser.add_argument_group("output")
    output_group.add_argument(
        "--output-dir",
        default="automation_runs",
        help="Directory for search snapshots and logs [default: automation_runs]",
    )
    output_group.add_argument(
        "--no-save",
        action="store_true",
        help="Skip writing JSON snapshot of the search response",
    )

    callback_group = parser.add_argument_group("callback server")
    callback_group.add_argument(
        "--start-callback-server",
        action="store_true",
        help="Start the FastAPI callback server in-process before revealing contacts",
    )
    callback_group.add_argument(
        "--callback-host",
        default="0.0.0.0",
        help="Host for the callback server if started [default: 0.0.0.0]",
    )
    callback_group.add_argument(
        "--callback-port",
        type=int,
        default=8000,
        help="Port for callback server if started [default: 8000]",
    )
    callback_group.add_argument(
        "--wait-for-callbacks",
        type=int,
        default=20,
        help="Seconds to wait after reveals for callbacks to arrive [default: 20]",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR) [default: INFO]",
    )

    args = parser.parse_args()

    if not any([args.title, args.location, args.company, args.industry, args.keywords, args.name]):
        parser.error("At least one search criterion (title/location/company/industry/keywords/name) is required")

    if args.size < 1 or args.size > 100:
        parser.error("--size must be between 1 and 100 (SignalHire API limit)")

    if args.chunk_size < 1 or args.chunk_size > 100:
        parser.error("--chunk-size must be between 1 and 100 (SignalHire batch limit)")

    if args.reveal_batch_size < 1 or args.reveal_batch_size > 25:
        parser.error("--reveal-batch-size must be between 1 and 25")

    return args


def _build_search_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if args.title:
        payload["currentTitle"] = args.title
    if args.location:
        payload["location"] = args.location
    if args.company:
        payload["currentCompany"] = args.company
    if args.industry:
        payload["industry"] = args.industry
    if args.keywords:
        payload["keywords"] = args.keywords
    if args.name:
        payload["fullName"] = args.name
    if args.exclude_revealed:
        payload["contactsFetched"] = False
    return payload


async def _perform_search(client: SignalHireClient, payload: dict[str, Any], size: int) -> dict[str, Any]:
    response = await client.search_prospects(payload, size=size)
    if not response.success or not response.data:
        raise SignalHireAPIError(
            response.error or "Search failed", status_code=response.status_code, response_data=response.data
        )
    return response.data


def _extract_prospect_ids(search_data: dict[str, Any]) -> list[str]:
    profiles = search_data.get("profiles") or search_data.get("prospects") or []
    prospect_ids: list[str] = []
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        uid = profile.get("uid") or profile.get("id") or profile.get("prospect_uid")
        if uid:
            prospect_ids.append(str(uid))
    return prospect_ids


def _save_snapshot(output_dir: Path, search_data: dict[str, Any]) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"search_{timestamp}.json"
    path.write_text(json.dumps(search_data, indent=2))
    logging.info("Saved search snapshot -> %s", path)
    return path


async def _reveal_chunk(
    client: SignalHireClient,
    chunk: list[str],
    batch_size: int,
) -> list[APIResponse]:
    return await client.batch_reveal_contacts(chunk, batch_size=batch_size)


async def _run_workflow(args: argparse.Namespace) -> None:
    load_dotenv()

    api_key = os.getenv("SIGNALHIRE_API_KEY")
    if not api_key:
        raise RuntimeError("SIGNALHIRE_API_KEY is not set in the environment")

    configured_callback_url = os.getenv("SIGNALHIRE_CALLBACK_URL") or os.getenv(
        "PUBLIC_CALLBACK_URL"
    )
    callback_url = configured_callback_url
    callback_server: CallbackServer | None = None

    if args.start_callback_server:
        callback_server = start_server(host=args.callback_host, port=args.callback_port, background=True)
        register_airtable_handler(callback_server)
        inferred_url = f"http://{args.callback_host}:{args.callback_port}/signalhire/callback"
        callback_url = configured_callback_url or inferred_url
        logging.info("Callback server started at %s", inferred_url)
        if not configured_callback_url:
            logging.warning(
                "SIGNALHIRE_CALLBACK_URL/PUBLIC_CALLBACK_URL not set; using %s for outgoing reveal requests.\n"
                "Ensure this URL is reachable by SignalHire (e.g., via tunnel or public reverse proxy).",
                inferred_url,
            )
    else:
        if not configured_callback_url:
            raise RuntimeError(
                "SIGNALHIRE_CALLBACK_URL or PUBLIC_CALLBACK_URL is not set. Either export one of them or run with --start-callback-server."
            )

    async with SignalHireClient(api_key=api_key, callback_url=callback_url) as client:
        search_payload = _build_search_payload(args)
        logging.debug("Search payload: %s", search_payload)

        search_data = await _perform_search(client, search_payload, args.size)
        total_found = search_data.get("total") or search_data.get("total_count") or 0
        prospects = _extract_prospect_ids(search_data)
        logging.info("Search returned %s prospects (requested size=%s)", len(prospects), args.size)
        if total_found and total_found > len(prospects):
            logging.info("SignalHire reports %s total prospects available", total_found)

        if not args.no_save:
            output_dir = Path(args.output_dir)
            snapshot_path = _save_snapshot(output_dir, search_data)
        else:
            snapshot_path = None

        if not prospects:
            logging.warning("No prospect UIDs returned; nothing to reveal")
            return

        if args.max_prospects and args.max_prospects > 0:
            prospects = prospects[: args.max_prospects]
            logging.info("Limiting to first %s prospects for reveal", len(prospects))

        logging.info("Prospects queued for reveal: %s", len(prospects))
        logging.debug("Queued UIDs: %s", prospects)

        if args.dry_run:
            logging.info("Dry run complete. Reveal not requested. Snapshot=%s", snapshot_path)
            return

        successes: list[tuple[str, str | None]] = []
        failures: list[tuple[str, str | None]] = []

        for i in range(0, len(prospects), args.chunk_size):
            chunk = prospects[i : i + args.chunk_size]
            logging.info("Revealing chunk %s - %s", i + 1, i + len(chunk))

            responses = await _reveal_chunk(
                client,
                chunk,
                batch_size=min(args.reveal_batch_size, len(chunk)),
            )

            for prospect_id, response in zip(chunk, responses, strict=False):
                if response.success:
                    request_id = None
                    if response.data:
                        request_id = response.data.get("requestId") or response.data.get("request_id")
                    successes.append((prospect_id, request_id))
                else:
                    failures.append((prospect_id, response.error))

            logging.info(
                "Chunk complete: %s successes, %s failures", len(successes), len(failures)
            )

        logging.info(
            "Reveal requests submitted: %s succeeded, %s failed",
            len(successes),
            len(failures),
        )

        if failures:
            for prospect_id, error in failures[:5]:
                logging.error("Reveal failed for %s: %s", prospect_id, error)
            if len(failures) > 5:
                logging.error("%s additional failures not shown", len(failures) - 5)

        if args.wait_for_callbacks > 0:
            logging.info(
                "Waiting %s seconds for callbacks to arrive before exiting...",
                args.wait_for_callbacks,
            )
            end_time = time.time() + args.wait_for_callbacks
            while time.time() < end_time:
                stats = get_handler_stats()
                logging.debug("Callback stats: %s", stats)
                await asyncio.sleep(1)

        if callback_server:
            logging.info(
                "Callback server ran in-process for this job; the server ends when this script exits."
            )


def main() -> None:
    args = _parse_args()
    _configure_logging(args.log_level)

    try:
        asyncio.run(_run_workflow(args))
    except KeyboardInterrupt:
        logging.warning("Interrupted by user")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Automation run failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
