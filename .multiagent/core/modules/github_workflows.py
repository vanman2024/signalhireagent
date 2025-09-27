"""GitHub workflow synchronization module."""

from __future__ import annotations

from typing import Any, Dict


def detect(context: Dict[str, Any]) -> bool:
    return True


def deploy(context: Dict[str, Any]) -> Dict[str, Any]:
    if context.get('dry_run'):
        return {'status': "skipped:dry-run"}
    context['sync'].syncGitHubWorkflows()
    context['sync'].syncGitHubIssueTemplates()
    return {'status': 'ok'}
