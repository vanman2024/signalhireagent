"""CLI entry for the enhancement orchestrator."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .modules.orchestrator import run
except ImportError:  # running as direct script
    import sys
    CURRENT_DIR = Path(__file__).resolve().parent
    sys.path.append(str(CURRENT_DIR))
    from modules.orchestrator import run  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Run enhancement modules")
    parser.add_argument('project_root', nargs='?', help="Project root (defaults to CWD)")
    parser.add_argument('--dry-run', action='store_true', help="Show actions without writing")
    parser.add_argument('--quiet', action='store_true', help="Reduce log noise")
    args, unknown = parser.parse_known_args()

    flags = unknown
    run(
        project_root=Path(args.project_root).resolve() if args.project_root else None,
        dry_run=args.dry_run,
        verbose=not args.quiet,
        flags=flags,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
