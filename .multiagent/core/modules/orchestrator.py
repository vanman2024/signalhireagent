"""Python implementation of the enhancement orchestrator."""

from __future__ import annotations

import json
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional

from .detectors import detect_tech_stack
from .fs_utils import create_fs_utils
from .logger import create_logger, Logger
try:
    from ..sync_project import ProjectSync
except ImportError:  # standalone execution
    import sys
    CURRENT_DIR = Path(__file__).resolve().parent
    sys.path.append(str(CURRENT_DIR.parent))
    from sync_project import ProjectSync  # type: ignore

MANIFEST_PATH = Path(__file__).with_name('manifest.json')
CONFIG_PATH = Path(__file__).resolve().parents[2] / 'config' / 'project-sync-config.template.json'


def _load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _resolve_modules(manifest: Dict[str, Any], flags: List[str]) -> List[Dict[str, Any]]:
    modules = [entry for entry in manifest.get('modules', []) if entry.get('enabled', True)]
    if '--security-only' in flags:
        allowed = set(manifest.get('flags', {}).get('--security-only', []))
        modules = [entry for entry in modules if entry['name'] in allowed]
    if '--minimal' in flags:
        allowed = set(manifest.get('flags', {}).get('--minimal', []))
        modules = [entry for entry in modules if entry['name'] in allowed]
    if '--no-testing' in flags:
        excluded = set(manifest.get('flags', {}).get('--no-testing', {}).get('exclude', []))
        modules = [entry for entry in modules if entry['name'] not in excluded]
    return modules


def _should_skip(entry: Dict[str, Any], results: List[Dict[str, Any]]) -> bool:
    prerequisites = entry.get('prerequisites') or []
    satisfied = {result['name'] for result in results if result.get('status') == 'ok'}
    return any(dep not in satisfied for dep in prerequisites)


def run(*, project_root: Optional[Path] = None, flags: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = True) -> Dict[str, Any]:
    project_root = Path(project_root or Path.cwd()).resolve()
    flags = list(flags or [])

    manifest = _load_json(MANIFEST_PATH, default={"modules": []})
    config = _load_json(CONFIG_PATH, default={})

    logger = create_logger(verbose=verbose)
    fs_utils = create_fs_utils(dry_run=dry_run, logger=logger)

    template_root = Path(__file__).resolve().parents[2]
    sync = ProjectSync(project_root)
    context = {
        'sync': sync,
        'project_root': project_root,
        'template_root': template_root,
        'logger': logger,
        'fs_utils': fs_utils,
        'config': config,
        'flags': flags,
        'dry_run': dry_run,
    }
    context['detected_tech_stack'] = detect_tech_stack(project_root, config)

    logger.section('🚀 Enhancement Orchestrator (Python)')
    logger.info(f'Project root: {project_root}')
    logger.info(f'Template root: {template_root}')
    logger.info(f'Flags: {", ".join(flags) or "none"}')

    module_entries = _resolve_modules(manifest, flags)
    results: List[Dict[str, Any]] = []

    for entry in module_entries:
        name = entry['name']
        module_module = name.replace('-', '_')
        module_path = Path(__file__).with_name(f'{module_module}.py')
        if not module_path.exists():
            logger.warn(f'Module {name} not implemented yet (expected {module_path}). Skipping.')
            results.append({'name': name, 'status': 'missing'})
            continue

        if _should_skip(entry, results):
            logger.warn(f'Skipping {name} because prerequisites were not satisfied.')
            results.append({'name': name, 'status': 'skipped:prerequisite'})
            continue

        if __package__:
            module = import_module(f'.{module_module}', package=__package__)
        else:
            module = import_module(module_module)

        if hasattr(module, 'detect') and not module.detect(context):
            logger.info(f'{name} reported no applicable work. Skipping.')
            results.append({'name': name, 'status': 'skipped:detect'})
            continue

        logger.section(f'▶ {name}')
        try:
            deploy_result = module.deploy(context)
            status = deploy_result.get('status', 'ok') if isinstance(deploy_result, dict) else 'ok'
            record = {'name': name, 'status': status, 'details': deploy_result}
            if hasattr(module, 'validate'):
                validation = module.validate(context)
                record['validation'] = validation
                if validation and validation.get('issues'):
                    logger.warn(f"{name} validation surfaced {len(validation['issues'])} issue(s).")
            results.append(record)
            logger.success(f'{name} completed')
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f'{name} failed: {exc}')
            results.append({'name': name, 'status': 'error', 'error': str(exc)})
            if getattr(exc, 'fatal', False):
                logger.error(f'{name} marked failure as fatal. Halting.')
                break

    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'project_root': str(project_root),
        'flags': flags,
        'detected_tech_stack': context['detected_tech_stack'],
        'modules': results,
    }
    report_path = project_root / '.enhancement' / 'reports' / 'latest.json'
    if not dry_run:
        fs_utils.ensure_dir(report_path.parent)
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        logger.info(f'Report written to {report_path}')

    context['report_path'] = report_path
    return {'context': context, 'results': results, 'report_path': report_path}
