"""Placeholder performance check module."""

from __future__ import annotations

from typing import Any, Dict


def detect(context: Dict[str, Any]) -> bool:
    return False


def deploy(context: Dict[str, Any]) -> Dict[str, Any]:
    return {'status': 'skipped'}
