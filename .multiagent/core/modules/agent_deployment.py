"""Agent deployment module (Python port)."""

from __future__ import annotations

from typing import Any, Dict


def detect(context: Dict[str, Any]) -> bool:  # always applicable
    return True


def deploy(context: Dict[str, Any]) -> Dict[str, Any]:
    if context.get('dry_run'):
        return {'status': "skipped:dry-run"}
    sync = context['sync']
    sync.syncAgentFiles()
    sync.syncClaudeDirectory()
    sync.updateAgentContexts()
    return {'status': 'ok'}
