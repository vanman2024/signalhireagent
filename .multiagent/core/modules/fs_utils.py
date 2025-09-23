"""Filesystem helper utilities used by the orchestrator modules."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .logger import Logger


class FsUtils:
    def __init__(self, *, dry_run: bool = False, logger: Optional[Logger] = None) -> None:
        self.dry_run = dry_run
        self.logger = logger or Logger()

    def ensure_dir(self, path: Path) -> None:
        if self.dry_run:
            return
        Path(path).mkdir(parents=True, exist_ok=True)

    def _exists(self, path: Path) -> bool:
        try:
            return Path(path).exists()
        except OSError as exc:
            self.logger.warn(f"Unable to stat {path}: {exc}")
            return False

    def copy_file(self, *, source: Path, target: Path, overwrite: bool = False, mode: Optional[int] = None) -> Dict[str, Any]:
        source = Path(source)
        target = Path(target)
        if not self._exists(source):
            return {"status": "missing", "source": str(source)}
        if not overwrite and self._exists(target):
            return {"status": "skipped", "target": str(target)}
        if self.dry_run:
            return {"status": "copied", "source": str(source), "target": str(target)}
        self.ensure_dir(target.parent)
        shutil.copy2(source, target)
        if mode is not None:
            os.chmod(target, mode)
        return {"status": "copied", "source": str(source), "target": str(target)}

    def copy_dir(self, *, source: Path, target: Path, overwrite: bool = False, filter: Optional[Callable[[str, Path], bool]] = None) -> Dict[str, Any]:
        source = Path(source)
        target = Path(target)
        if not self._exists(source):
            return {"status": "missing", "source": str(source)}
        if self.dry_run:
            return {"status": "copied", "source": str(source), "target": str(target)}
        for root, dirs, files in os.walk(source):
            rel = Path(root).relative_to(source)
            dest_root = target / rel
            self.ensure_dir(dest_root)
            for name in files:
                src_file = Path(root) / name
                if filter and not filter(name, src_file):
                    continue
                dest_file = dest_root / name
                self.copy_file(source=src_file, target=dest_file, overwrite=overwrite)
        return {"status": "copied", "source": str(source), "target": str(target)}

    def read_json(self, path: Path, default: Any = None) -> Any:
        path = Path(path)
        if not self._exists(path):
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default

    def write_json(self, path: Path, data: Any, *, indent: int = 2) -> None:
        if self.dry_run:
            return
        path = Path(path)
        self.ensure_dir(path.parent)
        path.write_text(json.dumps(data, indent=indent), encoding="utf-8")

    def make_executable(self, path: Path, mode: int = 0o755) -> None:
        if self.dry_run:
            return
        try:
            os.chmod(path, mode)
        except FileNotFoundError:
            self.logger.warn(f"Cannot chmod missing file {path}")


def create_fs_utils(*, dry_run: bool = False, logger: Optional[Logger] = None) -> FsUtils:
    return FsUtils(dry_run=dry_run, logger=logger)
