"""Thin Airtable REST helpers used by the CLI.

Provides a lightweight read-only index of existing SignalHire contacts so
commands can make decisions without falling back to the legacy local cache.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


class AirtableClientError(RuntimeError):
    """Raised when Airtable API calls fail."""


@dataclass
class AirtableContactRecord:
    """Projection of an Airtable contact record."""

    record_id: str
    has_contact_info: bool
    status: Optional[str]


class AirtableContactIndex:
    """Caches Airtable contact metadata in memory."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_id: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        self.base_id = base_id or os.getenv("AIRTABLE_BASE_ID")
        self.table_id = table_id or os.getenv("AIRTABLE_TABLE_ID", "tbl0uFVaAfcNjT2rS")
        self._records: Dict[str, AirtableContactRecord] = {}

    @property
    def ready(self) -> bool:
        return bool(self.api_key and self.base_id and self.table_id)

    @property
    def signalhire_ids(self) -> frozenset[str]:
        return frozenset(self._records.keys())

    def entry_for(self, signalhire_id: str) -> Optional[AirtableContactRecord]:
        return self._records.get(signalhire_id)

    def has_contact_info(self, signalhire_id: str) -> bool:
        record = self.entry_for(signalhire_id)
        return bool(record and record.has_contact_info)

    async def _fetch_all(self) -> None:
        if not self.ready:
            raise AirtableClientError(
                "Airtable credentials are not configured (AIRTABLE_API_KEY / AIRTABLE_BASE_ID)."
            )

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params: Dict[str, Any] = {
            "pageSize": 100,
            "fields": [
                "SignalHire ID",
                "Primary Email",
                "Secondary Email",
                "Phone Number",
                "Status",
            ],
        }
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"

        async with httpx.AsyncClient() as client:
            next_offset: Optional[str] = None
            while True:
                if next_offset:
                    params["offset"] = next_offset
                elif "offset" in params:
                    params.pop("offset")

                response = await client.get(url, headers=headers, params=params)
                try:
                    response.raise_for_status()
                except httpx.HTTPError as exc:  # pragma: no cover - network failure path
                    raise AirtableClientError(f"Airtable request failed: {exc}") from exc

                payload = response.json()
                for record in payload.get("records", []):
                    fields = record.get("fields", {})
                    signalhire_id = fields.get("SignalHire ID")
                    if not signalhire_id:
                        continue
                    has_contact = bool(
                        fields.get("Primary Email")
                        or fields.get("Secondary Email")
                        or fields.get("Phone Number")
                    )
                    status = fields.get("Status")
                    self._records[signalhire_id] = AirtableContactRecord(
                        record_id=record.get("id", ""),
                        has_contact_info=has_contact,
                        status=status,
                    )

                next_offset = payload.get("offset")
                if not next_offset:
                    break

    @classmethod
    def build_sync(
        cls,
        *,
        api_key: Optional[str] = None,
        base_id: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> "AirtableContactIndex":
        index = cls(api_key=api_key, base_id=base_id, table_id=table_id)
        if not index.ready:
            return index
        asyncio.run(index._fetch_all())
        return index
